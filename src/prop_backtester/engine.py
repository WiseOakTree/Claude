"""Backtest-Engine: rechnet Signale in Trades, Kosten und eine Equity-Kurve um.

Die Engine laeuft ueber die *realen* OHLCV-Bars (nicht nur ueber Bricks), damit
die Equity-Kurve fuer die Prop-Regel-Pruefung realistisch ist:

  * Positionsgroesse per Risiko-%-vom-Kontostand (Stop = ``stop_bricks`` * Brick).
  * Realistische Kosten pro Fill: Gebuehr + halber Spread + fixe Slippage +
    **vola-abhaengige** Slippage (teurer in wilden Phasen).
  * **Funding-Kosten** auf offene Positionen (pro Einheit akkumuliert, damit
    Teilverkaeufe korrekt anteilig belastet werden).
  * Optionale **Teil-Gewinnmitnahmen** an TP-Leveln (``tp_take_fractions``);
    der Rest laeuft bis zum Gegensignal (Stop-and-Reverse).
  * Mark-to-Market inkl. **unrealisiertem** PnL -- Kraken Prop rechnet realized
    UND unrealized in Daily-Loss und Drawdown ein.
  * Fuer jede Bar werden zusaetzlich die intrabar Extrema (equity_low/high)
    geschaetzt (konservativ), damit Drawdown-Breaches nicht "durchrutschen".

Reihenfolge innerhalb einer Bar: Liegt auf dieser Bar ein Reversal-Signal, wird
**zuerst das Signal** verarbeitet (pessimistisch -- eine TP-Mitnahme derselben
Bar wird verworfen). Nur auf signalfreien Bars werden TPs geprueft.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from .config import BacktestConfig


@dataclass
class Position:
    side: int                  # +1 long, -1 short
    initial_size: float        # Groesse beim Einstieg
    size: float                # aktuell noch offene Groesse
    entry_fill: float          # tatsaechlicher Einstiegskurs (inkl. Slippage)
    entry_fee_per_unit: float  # Einstiegsgebuehr je Einheit
    entry_time: pd.Timestamp
    brick_size: float
    funding_per_unit: float = 0.0        # aufgelaufene Funding-Kosten je Einheit
    tp_prices: List[float] = field(default_factory=list)
    tp_fracs: List[float] = field(default_factory=list)
    tp_done: List[bool] = field(default_factory=list)
    realized: float = 0.0                # bereits realisierter PnL dieses Trades
    partials: int = 0                    # Anzahl Teilverkaeufe


@dataclass
class BacktestResult:
    equity: pd.DataFrame          # index=Zeit, Spalten: equity_close/low/high
    trades: pd.DataFrame          # ein Eintrag pro (vollstaendig) geschlossenem Trade
    initial_balance: float
    final_balance: float
    config: BacktestConfig


def _infer_dt_hours(index: pd.DatetimeIndex) -> float:
    """Bar-Dauer in Stunden aus dem Zeitindex (Median der Abstaende)."""
    if len(index) < 2:
        return 1.0
    deltas = np.diff(index.view("int64"))  # Nanosekunden
    med_ns = float(np.median(deltas))
    return max(med_ns / 3.6e12, 1e-6)  # ns -> Stunden


class Engine:
    def __init__(self, cfg: BacktestConfig):
        self.cfg = cfg.validate()
        c = cfg.costs
        self.fee = c.fee_pct
        self.slip = c.slippage_pct
        self.half_spread = c.half_spread_pct
        self.slip_vol = c.slippage_vol_mult
        self.funding_daily = c.funding_rate_daily_pct

    # --- Kosten ---------------------------------------------------------
    def _adverse(self, brick_size: float, price: float) -> float:
        """Adversariale Fill-Verschiebung als Anteil (Spread + Slippage + Vola)."""
        vol_component = self.slip_vol * (brick_size / price) if price > 0 else 0.0
        return self.slip + self.half_spread + vol_component

    # --- Bewertung ------------------------------------------------------
    def _unrealized(self, pos: Optional[Position], price: float) -> float:
        """Mark-to-Market der noch offenen Restposition (inkl. bereits Realisiertem)."""
        if pos is None:
            return 0.0
        if pos.size <= 0:
            return pos.realized
        per_unit_cost = pos.entry_fee_per_unit + pos.funding_per_unit + self.fee * price
        return pos.realized + (pos.side * (price - pos.entry_fill) - per_unit_cost) * pos.size

    def _close_units(self, pos: Position, price: float, units: float) -> float:
        """Schliesst ``units`` Einheiten zum Marktpreis und gibt den PnL zurueck."""
        units = min(units, pos.size)
        if units <= 0:
            return 0.0
        exit_fill = price * (1 - pos.side * self._adverse(pos.brick_size, price))
        per_unit = (pos.side * (exit_fill - pos.entry_fill)
                    - pos.entry_fee_per_unit - self.fee * exit_fill - pos.funding_per_unit)
        pnl = per_unit * units
        pos.size -= units
        pos.realized += pnl
        return pnl

    def _open(self, side: int, price: float, brick_size: float,
              balance: float, time: pd.Timestamp) -> Optional[Position]:
        """Oeffnet eine Position mit risiko-basierter Groesse; None wenn zu klein."""
        risk = self.cfg.risk
        stop_dist = risk.stop_bricks * brick_size
        if stop_dist <= 0:
            return None
        entry_fill = price * (1 + side * self._adverse(brick_size, price))
        size = (balance * risk.risk_per_trade_pct) / stop_dist
        max_size = (balance * risk.max_leverage) / entry_fill  # Hebelbegrenzung
        size = min(size, max_size)
        if size <= 0 or size * entry_fill < risk.min_notional:
            return None

        # TP-Level und Teilverkaufs-Anteile vorbereiten
        tp_prices: List[float] = []
        tp_fracs: List[float] = []
        for m, frac in zip(risk.tp_r_multiples, risk.tp_take_fractions):
            tp_prices.append(entry_fill + side * m * stop_dist)
            tp_fracs.append(float(frac))

        return Position(
            side=side, initial_size=size, size=size, entry_fill=entry_fill,
            entry_fee_per_unit=self.fee * entry_fill, entry_time=time,
            brick_size=brick_size, tp_prices=tp_prices, tp_fracs=tp_fracs,
            tp_done=[False] * len(tp_prices),
        )

    def _check_tps(self, pos: Position, high: float, low: float) -> float:
        """Prueft TP-Level gegen die Bar-Extrema und nimmt Teilgewinne mit."""
        realized = 0.0
        for i, (tp, frac) in enumerate(zip(pos.tp_prices, pos.tp_fracs)):
            if pos.tp_done[i] or pos.size <= 0:
                continue
            hit = high >= tp if pos.side == 1 else low <= tp
            if not hit:
                continue
            pos.tp_done[i] = True
            units = pos.initial_size * frac
            pnl = self._close_units(pos, tp, units)
            if pnl != 0.0 or units > 0:
                pos.partials += 1
            realized += pnl
        return realized

    # --- Hauptlauf ------------------------------------------------------
    def run(self, df: pd.DataFrame, signals: pd.DataFrame) -> BacktestResult:
        n = len(df)
        highs = df["high"].to_numpy(float)
        lows = df["low"].to_numpy(float)
        closes = df["close"].to_numpy(float)
        times = df.index
        dt_frac = _infer_dt_hours(times) / 24.0  # Bruchteil eines Tages je Bar

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

            # Funding auf die offene Restposition (je Einheit akkumuliert)
            if pos is not None and pos.size > 0 and self.funding_daily > 0:
                pos.funding_per_unit += self.funding_daily * dt_frac * cl

            lows_cand: List[float] = []
            highs_cand: List[float] = []

            def mark():
                if pos is not None:
                    lows_cand.extend([eq_at(lo), eq_at(hi)])
                    highs_cand.extend([eq_at(lo), eq_at(hi)])
                else:
                    lows_cand.append(balance)
                    highs_cand.append(balance)

            # 1) Bewertung mit dem Zustand zu Beginn der Bar
            mark()

            if i in sig_by_bar:
                # 2a) Reversal-Bar: Signal zuerst (pessimistisch, kein TP diese Bar)
                target, sig_price, bsize = sig_by_bar[i]
                if pos is not None and pos.side != target:
                    self._close_units(pos, sig_price, pos.size)
                    balance += pos.realized
                    trades.append(_trade_record(pos, sig_price, times[i]))
                    pos = None
                if pos is None and target != 0:
                    pos = self._open(target, sig_price, bsize, balance, times[i])
                mark()
            elif pos is not None and pos.size > 0 and pos.tp_prices:
                # 2b) Signalfreie Bar: Teil-Gewinnmitnahmen pruefen
                self._check_tps(pos, hi, lo)
                if pos.size <= 1e-12:
                    balance += pos.realized
                    trades.append(_trade_record(pos, cl, times[i]))
                    pos = None
                mark()

            eq_low[i] = min(lows_cand)
            eq_high[i] = max(highs_cand)
            eq_close[i] = eq_at(cl) if pos is not None else balance

        # Offene Position am Ende zum letzten Schlusskurs glattstellen
        if pos is not None:
            self._close_units(pos, closes[-1], pos.size)
            balance += pos.realized
            trades.append(_trade_record(pos, closes[-1], times[-1]))
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


def _trade_record(pos: Position, exit_price: float,
                  exit_time: pd.Timestamp) -> dict:
    notional = pos.entry_fill * pos.initial_size
    return {
        "entry_time": pos.entry_time,
        "exit_time": exit_time,
        "side": "long" if pos.side == 1 else "short",
        "size": pos.initial_size,
        "entry_price": pos.entry_fill,
        "exit_price": exit_price,
        "funding": pos.funding_per_unit * pos.initial_size,
        "partials": pos.partials,
        "pnl": pos.realized,
        "return_pct": pos.realized / notional if notional else 0.0,
    }


def run_backtest(df: pd.DataFrame, signals: pd.DataFrame,
                 cfg: BacktestConfig) -> BacktestResult:
    """Bequeme Top-Level-Funktion."""
    return Engine(cfg).run(df, signals)
