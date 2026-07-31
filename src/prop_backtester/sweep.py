"""Parameter-Sweep + Robustheits-Bewertung.

Kernidee fuer "nachhaltig bestehen": Eine Strategie ist nicht gut, weil sie
*einmal* bestanden hat, sondern weil sie *ueber viele Marktphasen zuverlaessig*
besteht. Deshalb bewertet der Sweep jede Parameter-Kombination gegen ein ganzes
**Set von Szenarien** und misst die **Pass-Rate** (Anteil bestandener Versuche)
sowie den **Worst-Case-Drawdown**.

Szenarien-Quellen:
  * ``synthetic_scenarios`` -- viele realistische Zufallsmaerkte (Bull/Baer/Range).
  * ``walkforward_scenarios`` -- rollierende Fenster echter Daten (Walk-Forward).
"""

from __future__ import annotations

import copy
import itertools
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

from . import data
from .config import BacktestConfig
from .engine import run_backtest
from .renko import build_renko
from .strategy import generate_signals
from .prop import PRESETS, evaluate_challenge, resolve_preset
from .report import compute_metrics


# --- Parameter-Grid ----------------------------------------------------------
def build_grid(param_grid: Dict[str, Sequence]) -> List[dict]:
    """Kartesisches Produkt eines Parameter-Grids -> Liste von Kombinationen.

    Schluessel sind gepunktete Pfade in die Config, z.B.
    ``{"renko.atr_multiplier": [1.0, 1.5], "risk.risk_per_trade_pct": [0.003, 0.005]}``.
    """
    keys = list(param_grid)
    combos = []
    for values in itertools.product(*(param_grid[k] for k in keys)):
        combos.append(dict(zip(keys, values)))
    return combos


def apply_params(base: BacktestConfig, params: dict) -> BacktestConfig:
    """Kopiert die Basis-Config und setzt die gepunkteten Parameter-Pfade."""
    cfg = copy.deepcopy(base)
    for dotted, value in params.items():
        section, _, field = dotted.partition(".")
        if not field:
            setattr(cfg, section, value)
        else:
            setattr(getattr(cfg, section), field, value)
    return cfg.validate()


# --- Szenarien ---------------------------------------------------------------
def synthetic_scenarios(n: int = 12, bars: int = 6000, interval_minutes: int = 60,
                        base_seed: int = 1000) -> List[pd.DataFrame]:
    """Erzeugt n realistische Zufallsmaerkte mit variierenden Regimen.

    Drift und Volatilitaet werden pro Szenario gestreut, sodass das Set Bull-,
    Baer- und Seitwaerts-Phasen abdeckt -- ein fairer Robustheitstest.
    """
    rng = np.random.default_rng(base_seed)
    scenarios = []
    for i in range(n):
        drift = float(rng.uniform(-0.6, 0.6))    # Bull bis Baer
        vol = float(rng.uniform(0.45, 1.10))     # ruhig bis wild
        scenarios.append(
            data.generate_realistic(
                bars=bars, interval_minutes=interval_minutes,
                annual_drift=drift, annual_vol=vol, seed=base_seed + i + 1,
            )
        )
    return scenarios


def walkforward_scenarios(df: pd.DataFrame, window_bars: int,
                          step_bars: Optional[int] = None) -> List[pd.DataFrame]:
    """Zerlegt echte Daten in rollierende Fenster (Walk-Forward).

    Jedes Fenster ist ein eigenstaendiger "Challenge-Versuch". Die Pass-Rate ueber
    alle Fenster schaetzt, wie oft man die Challenge real bestehen wuerde.
    """
    if step_bars is None:
        step_bars = window_bars  # nicht ueberlappend
    scenarios = []
    i = 0
    while i + window_bars <= len(df):
        scenarios.append(df.iloc[i:i + window_bars])
        i += step_bars
    if not scenarios:
        raise ValueError("Daten zu kurz fuer die gewaehlte Fenstergroesse")
    return scenarios


# --- Sweep -------------------------------------------------------------------
@dataclass
class SweepResult:
    table: pd.DataFrame        # eine Zeile je Parameter-Kombination (sortiert)
    preset: str
    n_scenarios: int

    @property
    def best(self) -> dict:
        return self.table.iloc[0].to_dict()


def _run_one(df: pd.DataFrame, cfg: BacktestConfig, preset_key: str):
    """Ein Backtest auf einem Szenario -> (passed, return_pct, max_dd_pct)."""
    bricks = build_renko(df, cfg.renko).bricks
    signals = generate_signals(bricks, cfg.strategy)
    result = run_backtest(df, signals, cfg)
    metrics = compute_metrics(result)
    ch = evaluate_challenge(result.equity, PRESETS[preset_key], result.initial_balance)
    return bool(ch.passed), float(metrics["return_pct"]), float(metrics["max_drawdown_pct"])


def run_sweep(scenarios: Sequence[pd.DataFrame], param_grid: Dict[str, Sequence],
              preset_key: str = "1step_classic",
              base_cfg: Optional[BacktestConfig] = None,
              min_scenario_bars: int = 100) -> SweepResult:
    """Fuehrt den Sweep aus und rankt die Kombinationen nach Robustheit.

    Ranking: hoechste **Pass-Rate**, dann kleinster **Worst-Case-Drawdown**,
    dann hoechste Median-Rendite. So gewinnt die Einstellung, die am
    zuverlaessigsten *und* am schonendsten besteht.
    """
    preset_key = resolve_preset(preset_key)
    if preset_key not in PRESETS:
        raise ValueError(f"Unbekanntes Preset: {preset_key!r} (siehe PRESETS)")
    base = (base_cfg or BacktestConfig()).validate()
    scenarios = [s for s in scenarios if len(s) >= min_scenario_bars]
    if not scenarios:
        raise ValueError("Keine ausreichend langen Szenarien vorhanden")
    combos = build_grid(param_grid)

    rows = []
    for combo in combos:
        cfg = apply_params(base, combo)
        passes, rets, dds = 0, [], []
        for df in scenarios:
            ok, ret, dd = _run_one(df, cfg, preset_key)
            passes += int(ok)
            rets.append(ret)
            dds.append(dd)
        row = dict(combo)
        row["pass_rate"] = passes / len(scenarios)
        row["median_return"] = float(np.median(rets))
        row["median_maxdd"] = float(np.median(dds))
        row["worst_maxdd"] = float(np.max(dds))
        row["n_scenarios"] = len(scenarios)
        rows.append(row)

    table = pd.DataFrame(rows).sort_values(
        by=["pass_rate", "worst_maxdd", "median_return"],
        ascending=[False, True, False],
    ).reset_index(drop=True)
    return SweepResult(table=table, preset=preset_key, n_scenarios=len(scenarios))


# Sinnvolles Standard-Grid fuer den schnellen Einstieg
DEFAULT_GRID: Dict[str, Sequence] = {
    "renko.atr_multiplier": [0.75, 1.0, 1.5, 2.0],
    "renko.atr_period": [10, 14, 20],
    "risk.risk_per_trade_pct": [0.003, 0.005, 0.0075],
}
