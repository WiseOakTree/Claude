import numpy as np
import pandas as pd

from prop_backtester import data
from prop_backtester.config import BacktestConfig
from prop_backtester.sweep import (
    build_grid,
    apply_params,
    synthetic_scenarios,
    walkforward_scenarios,
    run_sweep,
    DEFAULT_GRID,
)


def test_build_grid_cartesian():
    grid = {"a": [1, 2], "b": [3, 4, 5]}
    combos = build_grid(grid)
    assert len(combos) == 6
    assert {"a": 1, "b": 3} in combos
    assert {"a": 2, "b": 5} in combos


def test_apply_params_sets_dotted_paths():
    base = BacktestConfig()
    cfg = apply_params(base, {"renko.atr_multiplier": 2.5,
                              "risk.risk_per_trade_pct": 0.004})
    assert cfg.renko.atr_multiplier == 2.5
    assert cfg.risk.risk_per_trade_pct == 0.004
    # Basis bleibt unveraendert (deepcopy)
    assert base.renko.atr_multiplier == 1.0


def test_walkforward_scenarios_windows():
    df = data.generate_synthetic(bars=1000, seed=1)
    scen = walkforward_scenarios(df, window_bars=300, step_bars=300)
    assert len(scen) == 3
    assert all(len(s) == 300 for s in scen)


def test_walkforward_too_short_raises():
    df = data.generate_synthetic(bars=100, seed=1)
    try:
        walkforward_scenarios(df, window_bars=500)
        assert False, "sollte fehlschlagen"
    except ValueError:
        pass


def test_synthetic_scenarios_count_and_shape():
    scen = synthetic_scenarios(n=4, bars=500, base_seed=10)
    assert len(scen) == 4
    assert all(set(["open", "high", "low", "close", "volume"]).issubset(s.columns) for s in scen)


def test_run_sweep_ranks_and_reports():
    scen = synthetic_scenarios(n=4, bars=1500, base_seed=20)
    grid = {"renko.atr_multiplier": [1.0, 2.0], "risk.risk_per_trade_pct": [0.003, 0.006]}
    sweep = run_sweep(scen, grid, preset_key="1step_classic")
    # 2x2 Kombinationen
    assert len(sweep.table) == 4
    for col in ("pass_rate", "median_return", "worst_maxdd"):
        assert col in sweep.table.columns
    # nach pass_rate absteigend sortiert
    assert sweep.table["pass_rate"].is_monotonic_decreasing
    assert 0.0 <= sweep.best["pass_rate"] <= 1.0
