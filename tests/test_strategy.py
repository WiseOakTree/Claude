import numpy as np
import pandas as pd

from prop_backtester.config import StrategyConfig
from prop_backtester.strategy import generate_signals


def _bricks(directions):
    n = len(directions)
    return pd.DataFrame({
        "time": pd.date_range("2025-01-01", periods=n, freq="1h", tz="UTC"),
        "close": np.arange(n, dtype=float) + 100,
        "direction": directions,
        "brick_size": np.ones(n),
        "src_index": np.arange(n),
    })


def test_two_brick_reversal_generates_long_then_short():
    # 2 up -> long, dann 2 down -> short
    bricks = _bricks([1, 1, -1, -1])
    sig = generate_signals(bricks, StrategyConfig(reversal_bricks=2))
    assert list(sig["target"]) == [1, -1]


def test_single_brick_does_not_trigger():
    bricks = _bricks([1, -1, 1, -1])  # nie 2 gleiche in Folge
    sig = generate_signals(bricks, StrategyConfig(reversal_bricks=2))
    assert len(sig) == 0


def test_long_only_exits_on_bearish_signal():
    # allow_short=False: Long, dann Gegensignal -> flach (0), dann wieder Long
    bricks = _bricks([1, 1, -1, -1, 1, 1])
    sig = generate_signals(bricks, StrategyConfig(reversal_bricks=2, allow_short=False))
    assert list(sig["target"]) == [1, 0, 1]


def test_no_duplicate_same_direction_signal():
    bricks = _bricks([1, 1, 1, 1])  # bleibt long
    sig = generate_signals(bricks, StrategyConfig(reversal_bricks=2))
    assert list(sig["target"]) == [1]
