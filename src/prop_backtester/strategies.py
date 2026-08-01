"""Weitere Strategie-Familien -- alle look-ahead-frei.

Jeder Generator liefert dasselbe Signal-Format wie ``strategy.generate_signals``:
Spalten ``time, src_index, price, target, brick_size``.

  * ``target``     -- Zielposition (+1 long, -1 short, 0 flat)
  * ``brick_size`` -- Risiko-Einheit; die Engine setzt den Stop auf
                      ``risk.stop_bricks * brick_size`` (Positionsgroesse)
  * ``price``      -- wird von der Engine im Modus ``close``/``next_open``
                      IGNORIERT (nur fuer Diagnose mitgefuehrt)

**Look-ahead-Regel:** Jede Entscheidung fuer Bar ``i`` darf ausschliesslich
Daten bis einschliesslich Bar ``i`` nutzen, und der Fill erfolgt fruehestens zum
Schlusskurs von Bar ``i``. Indikatoren, die den aktuellen Bar mitverwenden
duerfen (z.B. gleitende Durchschnitte), sind erlaubt -- Extremwerte wie
Donchian-Kanaele werden dagegen auf die VORHERIGEN Bars verschoben.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

from .renko import wilder_atr


def _emit(df: pd.DataFrame, target: pd.Series, unit: pd.Series) -> pd.DataFrame:
    """Wandelt eine Zielpositions-Reihe in Signale bei jedem Wechsel um."""
    tgt = target.fillna(0).astype(int).to_numpy()
    out_i, out_t = [], []
    pos = 0
    for i in range(len(tgt)):
        if tgt[i] != pos:
            pos = int(tgt[i])
            out_i.append(i)
            out_t.append(pos)
    if not out_i:
        return pd.DataFrame(columns=["time", "src_index", "price", "target", "brick_size"])
    idx = np.array(out_i)
    u = unit.to_numpy()[idx]
    ok = np.isfinite(u) & (u > 0)
    idx, tt, u = idx[ok], np.array(out_t)[ok], u[ok]
    return pd.DataFrame({
        "time": df.index.to_numpy()[idx],
        "src_index": idx,
        "price": df["close"].to_numpy()[idx],
        "target": tt,
        "brick_size": u,
    })


def _atr_unit(df: pd.DataFrame, period: int = 14, mult: float = 1.0) -> pd.Series:
    return wilder_atr(df, period) * mult


def donchian(df: pd.DataFrame, lookback: int = 20, atr_period: int = 14,
             atr_mult: float = 1.0, allow_short: bool = True) -> pd.DataFrame:
    """Donchian-Ausbruch: long ueber dem Hoch der letzten N Bars, short darunter.

    Die Kanalgrenzen nutzen ``shift(1)`` -- der aktuelle Bar zaehlt nicht mit,
    sonst waere der Ausbruch per Konstruktion immer erfuellt.
    """
    hi = df["high"].rolling(lookback).max().shift(1)
    lo = df["low"].rolling(lookback).min().shift(1)
    c = df["close"]
    target = pd.Series(np.nan, index=df.index)
    target[c > hi] = 1
    target[c < lo] = -1 if allow_short else 0
    target = target.ffill()
    return _emit(df, target, _atr_unit(df, atr_period, atr_mult))


def ma_cross(df: pd.DataFrame, fast: int = 20, slow: int = 100,
             atr_period: int = 14, atr_mult: float = 1.0,
             allow_short: bool = True) -> pd.DataFrame:
    """EMA-Kreuzung: long wenn schnelle ueber langsamer EMA liegt."""
    f = df["close"].ewm(span=fast, adjust=False).mean()
    s = df["close"].ewm(span=slow, adjust=False).mean()
    target = pd.Series(np.where(f > s, 1, -1 if allow_short else 0), index=df.index)
    target[s.isna()] = np.nan
    return _emit(df, target, _atr_unit(df, atr_period, atr_mult))


def momentum(df: pd.DataFrame, lookback: int = 100, atr_period: int = 14,
             atr_mult: float = 1.0, allow_short: bool = True) -> pd.DataFrame:
    """Zeitreihen-Momentum: long wenn die Rendite ueber N Bars positiv ist."""
    ret = df["close"].pct_change(lookback)
    target = pd.Series(np.where(ret > 0, 1, -1 if allow_short else 0), index=df.index)
    target[ret.isna()] = np.nan
    return _emit(df, target, _atr_unit(df, atr_period, atr_mult))


def bollinger_reversion(df: pd.DataFrame, period: int = 20, n_std: float = 2.0,
                        atr_period: int = 14, atr_mult: float = 1.0,
                        allow_short: bool = True) -> pd.DataFrame:
    """Mean-Reversion: kaufen unter dem unteren Band, flat an der Mitte."""
    mid = df["close"].rolling(period).mean()
    sd = df["close"].rolling(period).std()
    upper, lower = mid + n_std * sd, mid - n_std * sd
    c = df["close"]
    target = pd.Series(np.nan, index=df.index)
    target[c < lower] = 1
    if allow_short:
        target[c > upper] = -1
    # Rueckkehr zur Mitte schliesst die Position
    target[(c >= mid) & (target.isna())] = 0
    target = target.ffill()
    return _emit(df, target, _atr_unit(df, atr_period, atr_mult))


def breakout_with_trend_filter(df: pd.DataFrame, lookback: int = 20,
                               trend: int = 200, atr_period: int = 14,
                               atr_mult: float = 1.0) -> pd.DataFrame:
    """Donchian-Ausbruch, aber nur in Richtung des uebergeordneten Trends."""
    hi = df["high"].rolling(lookback).max().shift(1)
    lo = df["low"].rolling(lookback).min().shift(1)
    ma = df["close"].rolling(trend).mean()
    c = df["close"]
    target = pd.Series(np.nan, index=df.index)
    target[(c > hi) & (c > ma)] = 1
    target[(c < lo) & (c < ma)] = -1
    target[(c < ma) & (target.isna())] = target[(c < ma) & (target.isna())]
    target = target.ffill()
    return _emit(df, target, _atr_unit(df, atr_period, atr_mult))


REGISTRY = {
    "donchian": donchian,
    "ma_cross": ma_cross,
    "momentum": momentum,
    "bollinger": bollinger_reversion,
    "breakout_trend": breakout_with_trend_filter,
}
