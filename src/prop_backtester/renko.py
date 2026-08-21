"""Renko-Bricks aus OHLCV bauen (ATR-basiert oder fix).

Modell (bewusst simpel & konsistent):
  * Es gibt ein Gitter (``anchor`` = Schlusskurs des letzten Bricks).
  * Ein neuer Brick entsteht, sobald sich der Preis um mindestens eine
    Brick-Groesse vom ``anchor`` entfernt.
  * Innerhalb einer Bar koennen mehrere Bricks entstehen.

**Zwei Schalter, die die Brick-Reihe grundlegend aendern:**

``source``
    ``"close"`` -- nur der Schlusskurs jeder Bar wird gegen das Gitter geprueft.
    ``"ohlc"``  -- auch Hoch und Tief; damit erzeugen auch **Dochte** Bricks.
    Das entspricht der TradingView-Einstellung "OHLC" und liefert deutlich mehr
    (und mehr wechselnde) Bricks. Reihenfolge innerhalb der Bar: das
    **gegenlaeufige Extrem zuerst** (bei steigender Bar erst das Tief). Ohne
    Tickdaten ist die echte Reihenfolge unbekannt; diese Wahl erzeugt eher
    zusaetzliche Gegen-Bricks als zusaetzliche Trendbricks.

``reversal_boxes``
    Wie weit der Preis **gegen** die letzte Brick-Richtung laufen muss, damit
    ein Gegenbrick entsteht. ``1.0`` ist ein reines Gitter -- in Kombination mit
    der Strategie "Reversal nach 2 Gegen-Bricks" entspricht das exakt dem
    klassischen 2-Brick-Reversal. ``2.0`` ist klassisches Renko wie in
    TradingView ("Traditional"): ein Gegenbrick springt zwei Boxen weit.

Bei ``mode="atr"`` ist die Brick-Groesse dynamisch: es wird die (Wilder-)ATR am
ausloesenden Bar verwendet. Bei ``fixed_brick_pct`` waechst die Boxgroesse mit
dem Kurs mit (TradingView: Boxgroesse in Prozent).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd

from .config import RenkoConfig


def wilder_atr(df: pd.DataFrame, period: int) -> pd.Series:
    """Berechnet die Average True Range nach Wilder."""
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    # Wilder-Glaettung == EMA mit alpha = 1/period
    atr = tr.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    return atr


@dataclass
class RenkoResult:
    """Ergebnis des Renko-Aufbaus."""

    bricks: pd.DataFrame  # Spalten: time, close, direction, brick_size, src_index

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.bricks)


def build_renko(df: pd.DataFrame, cfg: RenkoConfig) -> RenkoResult:
    """Baut Renko-Bricks aus einem OHLCV-DataFrame.

    Jeder Brick traegt den Zeitstempel und den Bar-Index der Bar, die ihn
    ausgeloest hat -- das erlaubt spaeter die praezise Rueckabbildung auf die
    reale Zeitachse (Daily-Reset, Mark-to-Market).
    """
    cfg.validate()
    closes = df["close"].to_numpy(dtype=float)
    times = df.index

    if cfg.mode == "atr":
        atr = wilder_atr(df, cfg.atr_period).to_numpy(dtype=float)
        brick_of = lambda i: atr[i] * cfg.atr_multiplier
    else:
        def brick_of(i: int) -> float:
            if cfg.fixed_brick is not None:
                return cfg.fixed_brick
            return closes[i] * cfg.fixed_brick_pct

    times_out: List = []
    close_out: List[float] = []
    dir_out: List[int] = []
    size_out: List[float] = []
    idx_out: List[int] = []

    highs = df["high"].to_numpy(dtype=float) if cfg.source == "ohlc" else None
    lows = df["low"].to_numpy(dtype=float) if cfg.source == "ohlc" else None
    opens = df["open"].to_numpy(dtype=float) if cfg.source == "ohlc" else None

    anchor = np.nan  # Schlusskurs des letzten Bricks (Gitter-Anker)
    last_dir = 0     # Richtung des letzten Bricks (fuer reversal_boxes)

    for i in range(len(closes)):
        size = brick_of(i)
        if not np.isfinite(size) or size <= 0:
            continue  # ATR-Warmup noch nicht bereit
        if np.isnan(anchor):
            anchor = closes[i]  # erster gueltiger Bar setzt den Anker
            continue

        if cfg.source == "ohlc":
            # Gegenlaeufiges Extrem zuerst -- pessimistisch (siehe Modulkopf).
            path = ([lows[i], highs[i]] if closes[i] >= opens[i]
                    else [highs[i], lows[i]])
        else:
            path = [closes[i]]

        # Groesse wird pro Bar fixiert (dynamische ATR wirkt ab dem naechsten Bar).
        guard = 0
        for price in path:
            while True:
                auf = size * (cfg.reversal_boxes if last_dir == -1 else 1.0)
                ab = size * (cfg.reversal_boxes if last_dir == 1 else 1.0)
                if price >= anchor + auf:
                    anchor += auf
                    richtung = 1
                elif price <= anchor - ab:
                    anchor -= ab
                    richtung = -1
                else:
                    break
                times_out.append(times[i]); close_out.append(anchor)
                dir_out.append(richtung); size_out.append(size)
                idx_out.append(i)
                last_dir = richtung
                guard += 1
                if guard > 100000:  # Schutz gegen Endlosschleife bei Datenfehlern
                    raise RuntimeError("Renko-Aufbau: zu viele Bricks pro Bar")

    bricks = pd.DataFrame({
        "time": times_out,
        "close": close_out,
        "direction": dir_out,
        "brick_size": size_out,
        "src_index": idx_out,
    })
    return RenkoResult(bricks=bricks)
