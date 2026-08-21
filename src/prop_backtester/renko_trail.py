"""Renko-Trail -- eine Renko-Strategie, deren Kern das Handelsmanagement ist.

Der Ausgangspunkt des Projekts (``strategy.generate_signals``) ist **immer im
Markt**: zwei Gegen-Bricks drehen die Position um. Der Einstieg ist damit
gleichzeitig der Ausstieg des vorherigen Trades -- es gibt kein Management, nur
Signalwechsel.

Renko-Trail macht das Gegenteil: **diskrete Trades mit definiertem Risiko.**

  * Einstieg nach ``entry_bricks`` gleichgerichteten Bricks.
  * Anfangsstop auf dem Gitter, ``risk.stop_bricks`` Bricks entfernt.
  * Danach uebernimmt das Management (``ManagementConfig``): Break-even,
    Brick-Trailing, Teilmitnahme, Zeitstop.
  * Nach dem Ausstieg ist die Position **flat**, bis ein neues Einstiegssignal
    steht. Kein Nachkaufen, keine Dauerposition.

Damit laesst sich die Frage sauber trennen, die im Alltag ununterscheidbar
vermischt wird: Was leistet das *Signal*, und was leistet das *Management*?

Die Leiter ``VARIANTS`` (V0 bis V6) baut das Management Baustein fuer Baustein
auf -- so ist jeder Effekt einzeln zurechenbar. Reihenfolge und Parameter sind
in ``docs/renko_trail_spec.md`` vor der Rechnung festgelegt worden.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from .config import BacktestConfig, ManagementConfig, RiskConfig, StrategyConfig
from .engine import BacktestResult, run_backtest
from .renko import build_renko
from .strategy import generate_signals as reversal_signals

SIGNAL_COLUMNS = ["time", "src_index", "price", "target", "brick_size"]


def entry_signals(bricks: pd.DataFrame, entry_bricks: int = 3,
                  allow_long: bool = True, allow_short: bool = True
                  ) -> pd.DataFrame:
    """Einstiegs-Ereignisse: der ``entry_bricks``-te Brick einer Serie.

    Anders als ``strategy.generate_signals`` wird hier **nicht** eine
    Zielposition fortgeschrieben, sondern ein Ereignis gemeldet: genau in dem
    Moment, in dem die Serie die geforderte Laenge erreicht. Laeuft die Serie
    weiter, kommt kein zweites Signal -- es wird nicht nachgekauft.

    Ist die Engine zu diesem Zeitpunkt bereits in derselben Richtung
    positioniert, ignoriert sie das Signal; steht sie gegen die Serie, dreht
    sie. Wurde vorher ausgestoppt, ist dies der Wiedereinstieg.
    """
    if entry_bricks < 1:
        raise ValueError("entry_bricks muss >= 1 sein")
    if not (allow_long or allow_short):
        raise ValueError("Mindestens eine Handelsrichtung muss erlaubt sein")

    directions = bricks["direction"].to_numpy()
    closes = bricks["close"].to_numpy()
    sizes = bricks["brick_size"].to_numpy()
    times = bricks["time"].to_numpy()
    src = bricks["src_index"].to_numpy()

    out_time, out_idx, out_price, out_target, out_size = [], [], [], [], []
    run_dir, run_len = 0, 0

    for k in range(len(directions)):
        d = int(directions[k])
        if d == run_dir:
            run_len += 1
        else:
            run_dir, run_len = d, 1
        if run_len != entry_bricks:
            continue          # nur der ausloesende Brick, nicht jeder weitere
        if run_dir == 1 and not allow_long:
            continue
        if run_dir == -1 and not allow_short:
            continue
        out_time.append(times[k])
        out_idx.append(int(src[k]))
        out_price.append(float(closes[k]))
        out_target.append(run_dir)
        out_size.append(float(sizes[k]))

    return pd.DataFrame({
        "time": out_time,
        "src_index": out_idx,
        "price": out_price,
        "target": out_target,
        "brick_size": out_size,
    }, columns=SIGNAL_COLUMNS)


def brick_grid(bricks: pd.DataFrame, n_bars: int) -> np.ndarray:
    """Je Bar der Schlusskurs des zuletzt bekannten Bricks (sonst NaN).

    Der Brick auf Bar ``i`` ist mit dem Schlusskurs von Bar ``i`` bekannt; die
    Engine benutzt den Wert erst ab Bar ``i+1`` zum Nachziehen des Stops. Kein
    Look-ahead.
    """
    grid = np.full(n_bars, np.nan)
    if len(bricks) == 0:
        return grid
    idx = bricks["src_index"].to_numpy(dtype=int)
    close = bricks["close"].to_numpy(dtype=float)
    inside = (idx >= 0) & (idx < n_bars)
    # Bei mehreren Bricks auf einer Bar gewinnt der letzte.
    grid[idx[inside]] = close[inside]
    return pd.Series(grid).ffill().to_numpy()


@dataclass
class Variant:
    """Eine Stufe der Management-Leiter."""

    key: str
    label: str
    mode: str                      # "reverse" (Dauerposition) oder "entry" (diskret)
    management: ManagementConfig = field(default_factory=ManagementConfig)
    tp_r_multiples: List[float] = field(default_factory=list)
    tp_take_fractions: List[float] = field(default_factory=list)
    entry_bricks: int = 3
    reversal_bricks: int = 2


#: Break-even heisst "Stop auf Einstieg + Kosten" -- ein Stop exakt auf dem
#: Einstiegskurs waere nach Gebuehren immer noch ein kleiner Verlust.
#: 16 bp = Roundtrip aus der Spezifikation.
BE_OFFSET = 0.0016


def _mgmt(**kw) -> ManagementConfig:
    return ManagementConfig(**kw)


#: Die in ``docs/renko_trail_spec.md`` festgelegte Leiter. Jede Stufe fuegt
#: genau einen Baustein hinzu.
VARIANTS: Dict[str, Variant] = {
    "V0": Variant("V0", "Stop-and-Reverse, kein echter Stop", "reverse"),
    "V1": Variant("V1", "+ harter Stop", "reverse",
                  management=_mgmt(hard_stop=True)),
    "V2": Variant("V2", "diskrete Trades + harter Stop", "entry",
                  management=_mgmt(hard_stop=True)),
    "V3": Variant("V3", "+ Break-even nach 2 Bricks", "entry",
                  management=_mgmt(hard_stop=True, breakeven_bricks=2.0,
                                   breakeven_offset_pct=BE_OFFSET)),
    "V4": Variant("V4", "+ Brick-Trailing", "entry",
                  management=_mgmt(hard_stop=True, breakeven_bricks=2.0,
                                   breakeven_offset_pct=BE_OFFSET,
                                   trail_bricks=2.0)),
    "V5": Variant("V5", "+ Teilmitnahme 50 % bei 2R", "entry",
                  management=_mgmt(hard_stop=True, breakeven_bricks=2.0,
                                   breakeven_offset_pct=BE_OFFSET,
                                   trail_bricks=2.0),
                  tp_r_multiples=[2.0], tp_take_fractions=[0.5]),
    "V6": Variant("V6", "+ Zeitstop (voller Renko-Trail)", "entry",
                  management=_mgmt(hard_stop=True, breakeven_bricks=2.0,
                                   breakeven_offset_pct=BE_OFFSET,
                                   trail_bricks=2.0, time_stop_bars=240,
                                   time_stop_min_r=1.0),
                  tp_r_multiples=[2.0], tp_take_fractions=[0.5]),
}


def variant_config(variant: Variant, base: Optional[BacktestConfig] = None
                   ) -> BacktestConfig:
    """Baut die vollstaendige Backtest-Konfiguration einer Leiter-Stufe."""
    cfg = base or BacktestConfig()
    risk = replace(cfg.risk,
                   tp_r_multiples=list(variant.tp_r_multiples),
                   tp_take_fractions=list(variant.tp_take_fractions))
    strategy = replace(cfg.strategy, reversal_bricks=variant.reversal_bricks)
    return replace(cfg, risk=risk, strategy=strategy,
                   management=replace(variant.management)).validate()


def variant_signals(variant: Variant, bricks: pd.DataFrame,
                    cfg: BacktestConfig) -> pd.DataFrame:
    """Signale der Stufe: Dauerposition (``reverse``) oder Einstiege (``entry``)."""
    if variant.mode == "reverse":
        return reversal_signals(bricks, cfg.strategy)
    if variant.mode == "entry":
        return entry_signals(bricks, entry_bricks=variant.entry_bricks,
                             allow_long=cfg.strategy.allow_long,
                             allow_short=cfg.strategy.allow_short)
    raise ValueError(f"unbekannter Variant-Modus: {variant.mode!r}")


def run_variant(df: pd.DataFrame, variant: Variant,
                base: Optional[BacktestConfig] = None) -> BacktestResult:
    """Kompletter Durchlauf einer Leiter-Stufe auf einem OHLCV-DataFrame."""
    cfg = variant_config(variant, base)
    bricks = build_renko(df, cfg.renko).bricks
    signals = variant_signals(variant, bricks, cfg)
    grid = brick_grid(bricks, len(df))
    return run_backtest(df, signals, cfg, grid=grid)
