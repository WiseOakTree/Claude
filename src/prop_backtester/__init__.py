"""Krypto-Prop-Backtester -- Renko-Reversal-Strategie fuer die Kraken-Prop-Challenge.

High-Level-API:

    from prop_backtester import backtest, data

    df = data.generate_synthetic()
    result, metrics, challenges = backtest(df)
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

import pandas as pd

from .config import BacktestConfig
from .renko import build_renko
from .strategy import generate_signals
from .engine import run_backtest, BacktestResult
from .prop import evaluate_all_presets, evaluate_challenge, PRESETS, ChallengeResult
from .report import compute_metrics
from .sweep import (run_sweep, synthetic_scenarios, walkforward_scenarios,
                    DEFAULT_GRID, SweepResult)
from . import data, kraken, binance

__all__ = [
    "backtest",
    "BacktestConfig",
    "BacktestResult",
    "PRESETS",
    "ChallengeResult",
    "build_renko",
    "generate_signals",
    "run_backtest",
    "evaluate_challenge",
    "evaluate_all_presets",
    "compute_metrics",
    "run_sweep",
    "synthetic_scenarios",
    "walkforward_scenarios",
    "DEFAULT_GRID",
    "SweepResult",
    "data",
    "kraken",
    "binance",
]

__version__ = "0.1.0"


def backtest(df: pd.DataFrame, cfg: Optional[BacktestConfig] = None
             ) -> Tuple[BacktestResult, dict, Dict[str, ChallengeResult]]:
    """Kompletter Durchlauf: Renko -> Signale -> Engine -> Kennzahlen + Prop-Check.

    Rueckgabe: (BacktestResult, metrics-dict, {preset_key: ChallengeResult}).
    """
    cfg = (cfg or BacktestConfig()).validate()
    bricks = build_renko(df, cfg.renko).bricks
    signals = generate_signals(bricks, cfg.strategy)
    result = run_backtest(df, signals, cfg)
    metrics = compute_metrics(result)
    challenges = evaluate_all_presets(result.equity, result.initial_balance)
    return result, metrics, challenges
