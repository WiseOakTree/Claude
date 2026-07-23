import numpy as np
import pandas as pd

from prop_backtester.config import RenkoConfig
from prop_backtester.renko import build_renko, wilder_atr
from prop_backtester import data


def _linear_df(prices):
    idx = pd.date_range("2025-01-01", periods=len(prices), freq="1h", tz="UTC")
    p = np.asarray(prices, float)
    return pd.DataFrame(
        {"open": p, "high": p, "low": p, "close": p, "volume": np.ones_like(p)},
        index=idx,
    )


def test_fixed_bricks_count_up_move():
    # Preis steigt von 100 auf 110 -> bei Brick 1 erwarten wir 10 Up-Bricks
    df = _linear_df(list(range(100, 111)))
    cfg = RenkoConfig(mode="fixed", fixed_brick=1.0)
    bricks = build_renko(df, cfg).bricks
    assert (bricks["direction"] == 1).all()
    assert len(bricks) == 10
    assert bricks["close"].iloc[-1] == 110


def test_fixed_bricks_reversal_direction():
    df = _linear_df([100, 101, 102, 103, 102, 101, 100])
    cfg = RenkoConfig(mode="fixed", fixed_brick=1.0)
    bricks = build_renko(df, cfg).bricks
    dirs = list(bricks["direction"])
    assert dirs[:3] == [1, 1, 1]
    assert dirs[-3:] == [-1, -1, -1]


def test_atr_bricks_form_on_trend():
    df = data.generate_synthetic(bars=1000, seed=1)
    cfg = RenkoConfig(mode="atr", atr_period=14, atr_multiplier=1.0)
    bricks = build_renko(df, cfg).bricks
    assert len(bricks) > 0
    assert set(bricks["direction"].unique()).issubset({-1, 1})
    assert (bricks["brick_size"] > 0).all()


def test_wilder_atr_positive():
    df = data.generate_synthetic(bars=200, seed=2)
    atr = wilder_atr(df, 14).dropna()
    assert (atr > 0).all()
    assert len(atr) > 0
