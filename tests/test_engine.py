import numpy as np
import pandas as pd

from prop_backtester import backtest, data
from prop_backtester.config import BacktestConfig, CostConfig
from prop_backtester.engine import run_backtest


def _df(prices):
    idx = pd.date_range("2025-01-01", periods=len(prices), freq="1h", tz="UTC")
    p = np.asarray(prices, float)
    return pd.DataFrame(
        {"open": p, "high": p, "low": p, "close": p, "volume": np.ones_like(p)},
        index=idx,
    )


def test_profitable_long_trade_no_costs():
    # Long ab Signal, Preis steigt weiter -> Gewinn.
    df = _df([100, 101, 102, 103, 104, 105, 106, 107])
    signals = pd.DataFrame({
        "time": [df.index[2]],
        "src_index": [2],
        "price": [102.0],
        "target": [1],
        "brick_size": [1.0],
    })
    cfg = BacktestConfig(costs=CostConfig(fee_pct=0.0, slippage_pct=0.0))
    res = run_backtest(df, signals, cfg)
    assert res.final_balance > res.initial_balance
    assert len(res.trades) == 1
    assert res.trades["side"].iloc[0] == "long"


def test_costs_reduce_pnl():
    df = _df([100, 101, 102, 103, 104, 105])
    signals = pd.DataFrame({
        "time": [df.index[1]], "src_index": [1], "price": [101.0],
        "target": [1], "brick_size": [1.0],
    })
    no_cost = run_backtest(df, signals, BacktestConfig(costs=CostConfig(0.0, 0.0)))
    with_cost = run_backtest(df, signals, BacktestConfig(costs=CostConfig(0.001, 0.001)))
    assert with_cost.final_balance < no_cost.final_balance


def test_full_pipeline_runs_and_is_finite():
    df = data.generate_synthetic(bars=3000, seed=5)
    result, metrics, challenges = backtest(df)
    assert np.isfinite(result.final_balance)
    assert metrics["num_trades"] > 0
    assert 0.0 <= metrics["win_rate"] <= 1.0
    assert set(challenges) == {"1step_turbo", "1step_pro", "1step_classic", "2step_classic"}


def test_equity_curve_length_matches_data():
    df = data.generate_synthetic(bars=500, seed=6)
    result, _, _ = backtest(df)
    assert len(result.equity) == len(df)
    assert (result.equity["equity_low"] <= result.equity["equity_high"] + 1e-6).all()
