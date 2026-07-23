"""Backtest-Engine: rechnet Signale in Trades, Kosten und eine Equity-Kurve um.

Die Engine laeuft ueber die *realen* OHLCV-Bars (nicht nur ueber Bricks), damit
die Equity-Kurve fuer die Prop-Regel-Pruefung realistisch ist:

  * Positionsgroesse per Risiko-%-vom-Kontostand (Stop = ``stop_bricks`` * Brick).
  * Gebuehren + Slippage pro Fill.
  * Mark-to-Market inkl. **unrealisiertem** PnL -- Kraken Prop rechnet realized
    UND unrealized in Daily-Loss und Drawdown ein.
  * Fuer jede Bar werden zusaetzlich die intrabar Extrema (equity_low/high)
    geschaetzt (konservativ), damit Drawdown-Breaches nicht "durchrutschen".
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

from .config import BacktestConfig


@dataclass
class Position:
    side: int          # +1 long, -1 short
    size: float        # Einheiten des Basiswerts
    entry_fill: float  # tatsaechlicher Einstiegskurs (inkl. Slippage)
    entry_fee: float   # bezahlte Einstiegsgebuehr (Kontowaehrung)
    entry_time: pd.Timestamp
    brick_size: float


@dataclass
class BacktestResult:
    equity: pd.DataFrame          # index=Zeit, Spalten: equity_close/low/high
    trades: pd.DataFrame          # ein Eintrag pro geschlossenem Trade
    initial_balance: float
    final_balance: float
    config: BacktestConfig


class Engine:
    def __init__(self, cfg: BacktestConfig):
        self.cfg = cfg.validate()
        self.fee = cfg.costs.fee_pct
        self.slip = cfg.costs.slippage_pct

    # --- Bewertung ------------------------------------------------------
    def _unrealized(self, pos: Optional[Position], price: float) -> float:
        """Unrealisierter PnL (Mark-to-Market, ohne Slippage, inkl. Gebuehren)."""
        if pos is None:
            return 0.0
        exit_fee_est = self.fee * price * pos.size
        return pos.side * (price - pos.entry_fill) * pos.size - pos.entry_fee - exit_fee_est

    def _realize(self, pos: Position, price: float) -> float:
        """Realisierter PnL beim Schliessen (inkl. Slippage + Exit-Gebuehr)."""
        exit_fill = price * (1 - pos.side * self.slip)
        exit_fee = self.fee * exit_fill * pos.size
        return pos.side * (exit_fill - pos.entry_fill) * pos.size - pos.entry_fee - exit_fee

    def _open(self, side: int, price: float, brick_size: float,
              balance: float, time: pd.Timestamp) -> Optional[Position]:
        """Oeffnet eine Position mit risiko-basierter Groesse; None wenn zu klein."""
        risk = self.cfg.risk
        stop_dist = risk.stop_bricks * brick_size
        if stop_dist <= 0:
            return None
        entry_fill = price * (1 + side * self.slip)
        size = (balance * risk.risk_per_trade_pct) / stop_dist
        # Hebelbegrenzung
        max_size = (balance * risk.max_leverage) / entry_fill
        size = min(size, max_size)
        if size <= 0 or size * entry_fill < risk.min_notional:
            return None
        entry_fee = self.fee * entry_fill * size
        return Position(side, size, entry_fill, entry_fee, time, brick_size)

    # --- Hauptlauf ------------------------------------------------------
    def run(self, df: pd.DataFrame, signals: pd.DataFrame) -> BacktestResult:
        n = len(df)
        opens = df["open"].to_numpy(float)
        highs = df["high"].to_numpy(float)
        lows = df["low"].to_numpy(float)
        closes = df["close"].to_numpy(float)
        times = df.index

        # Signale pro Bar buendeln (netto: letztes Ziel je Bar gewinnt)
        sig_by_bar: Dict[int, Tuple[int, float, float]] = {}
        for row in signals.itertuples(index=False):
            sig_by_bar[int(row.src_index)] = (int(row.target), float(row.price), float(row.brick_size))

        balance = self.cfg.initial_balance
        pos: Optional[Position] = None
        eq_close = np.empty(n)
        eq_low = np.empty(n)
        eq_high = np.empty(n)
        trades = []

        def eq_at(price: float) -> float:
            return balance + self._unrealized(pos, price)

        for i in range(n):
            hi, lo, cl = highs[i], lows[i], closes[i]
            lows_cand = []
            highs_cand = []

            # 1) Bewertung mit der Position, die zu Beginn der Bar gehalten wird
            if pos is not None:
                lows_cand += [eq_at(lo), eq_at(hi)]
                highs_cand += [eq_at(lo), eq_at(hi)]
            else:
                lows_cand.append(balance)
                highs_cand.append(balance)

            # 2) Signalverarbeitung (Fill am Gitter-Level des ausloesenden Bricks)
            if i in sig_by_bar:
                target, sig_price, bsize = sig_by_bar[i]
                if pos is not None and pos.side != target:
                    pnl = self._realize(pos, sig_price)
                    balance += pnl
                    trades.append(_trade_record(pos, sig_price, pnl, times[i]))
                    pos = None
                if pos is None and target != 0:
                    pos = self._open(target, sig_price, bsize, balance, times[i])

                # Bewertung mit der neuen Position ueber den Rest der Bar
                if pos is not None:
                    lows_cand += [eq_at(lo), eq_at(hi)]
                    highs_cand += [eq_at(lo), eq_at(hi)]
                else:
                    lows_cand.append(balance)
                    highs_cand.append(balance)

            eq_low[i] = min(lows_cand)
            eq_high[i] = max(highs_cand)
            eq_close[i] = eq_at(cl) if pos is not None else balance

        # Offene Position am Ende zum letzten Schlusskurs glattstellen
        if pos is not None:
            pnl = self._realize(pos, closes[-1])
            balance += pnl
            trades.append(_trade_record(pos, closes[-1], pnl, times[-1]))
            pos = None

        equity = pd.DataFrame(
            {"equity_close": eq_close, "equity_low": eq_low, "equity_high": eq_high},
            index=times,
        )
        trades_df = pd.DataFrame(trades)
        return BacktestResult(
            equity=equity,
            trades=trades_df,
            initial_balance=self.cfg.initial_balance,
            final_balance=float(balance),
            config=self.cfg,
        )


def _trade_record(pos: Position, exit_price: float, pnl: float,
                  exit_time: pd.Timestamp) -> dict:
    return {
        "entry_time": pos.entry_time,
        "exit_time": exit_time,
        "side": "long" if pos.side == 1 else "short",
        "size": pos.size,
        "entry_price": pos.entry_fill,
        "exit_price": exit_price,
        "pnl": pnl,
        "return_pct": pnl / (pos.entry_fill * pos.size) if pos.size else 0.0,
    }


def run_backtest(df: pd.DataFrame, signals: pd.DataFrame,
                 cfg: BacktestConfig) -> BacktestResult:
    """Bequeme Top-Level-Funktion."""
    return Engine(cfg).run(df, signals)
