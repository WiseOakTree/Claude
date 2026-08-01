"""Tests fuer das Ausfuehrungsmodell -- Schutz gegen Look-ahead-Bias.

Hintergrund: Der urspruengliche Backtester hat den Fill-Preis vom Signal
uebernommen. Damit liess sich ein Preis fuellen, der zeitlich VOR der
signalausloesenden Information lag (Renko-Brick-Level mitten in der Kerze,
waehrend erst der Schlusskurs das Signal bestaetigte). Diese Tests stellen
sicher, dass das strukturell nicht mehr moeglich ist.
"""

import numpy as np
import pandas as pd
import pytest

from prop_backtester.config import BacktestConfig, CostConfig, ExecutionConfig
from prop_backtester.engine import run_backtest


def _bars(rows):
    """rows = Liste von (open, high, low, close)."""
    idx = pd.date_range("2025-01-01", periods=len(rows), freq="1h", tz="UTC")
    a = np.asarray(rows, float)
    return pd.DataFrame({"open": a[:, 0], "high": a[:, 1], "low": a[:, 2],
                         "close": a[:, 3], "volume": np.ones(len(rows))}, index=idx)


def _zero_costs():
    return CostConfig(fee_pct=0.0, slippage_pct=0.0, half_spread_pct=0.0,
                      slippage_vol_mult=0.0, funding_rate_daily_pct=0.0)


def _sig(bar, target=1, price=100.0, brick=1.0, **extra):
    d = {"time": [pd.Timestamp("2025-01-01", tz="UTC")], "src_index": [bar],
         "price": [price], "target": [target], "brick_size": [brick]}
    d.update({k: [v] for k, v in extra.items()})
    return pd.DataFrame(d)


def test_close_mode_ignores_signal_price():
    """Der alte Bug: ein guenstiger Signal-Preis darf NICHT gefuellt werden."""
    # Bar 1: Spanne 90..110, Schluss 100. Das Signal behauptet einen Fill zu 90.
    df = _bars([(100, 100, 100, 100), (100, 110, 90, 100), (100, 100, 100, 100)])
    cfg = BacktestConfig(costs=_zero_costs())
    cfg.execution = ExecutionConfig(mode="close")
    res = run_backtest(df, _sig(1, target=1, price=90.0), cfg)
    # Gefuellt wurde der Schlusskurs (100), nicht die geschenkten 90
    assert res.trades.iloc[0]["entry_price"] == pytest.approx(100.0)


def test_next_open_mode_uses_following_bar():
    df = _bars([(100, 100, 100, 100), (100, 110, 90, 100), (105, 106, 104, 105)])
    cfg = BacktestConfig(costs=_zero_costs())
    cfg.execution = ExecutionConfig(mode="next_open")
    res = run_backtest(df, _sig(1, target=1, price=90.0), cfg)
    assert res.trades.iloc[0]["entry_price"] == pytest.approx(105.0)


def test_next_open_signal_on_last_bar_expires():
    df = _bars([(100, 100, 100, 100), (100, 110, 90, 100)])
    cfg = BacktestConfig(costs=_zero_costs())
    cfg.execution = ExecutionConfig(mode="next_open")
    res = run_backtest(df, _sig(1, target=1), cfg)
    assert len(res.trades) == 0          # kein Folgebar -> kein Trade


def test_level_mode_requires_known_at():
    df = _bars([(100, 100, 100, 100), (100, 110, 90, 100)])
    cfg = BacktestConfig(costs=_zero_costs())
    cfg.execution = ExecutionConfig(mode="level")
    with pytest.raises(ValueError, match="known_at"):
        run_backtest(df, _sig(1, target=1, price=95.0), cfg)


def test_level_mode_rejects_lookahead():
    """Level, das erst auf der Fill-Bar bekannt wurde -> harter Fehler."""
    df = _bars([(100, 100, 100, 100), (100, 110, 90, 100)])
    cfg = BacktestConfig(costs=_zero_costs())
    cfg.execution = ExecutionConfig(mode="level", strict=True)
    sig = _sig(1, target=1, level=95.0, known_at=1)   # known_at == Fill-Bar
    with pytest.raises(ValueError, match="Look-ahead"):
        run_backtest(df, sig, cfg)


def test_level_mode_accepts_prior_knowledge():
    df = _bars([(100, 100, 100, 100), (100, 110, 90, 100)])
    cfg = BacktestConfig(costs=_zero_costs())
    cfg.execution = ExecutionConfig(mode="level")
    sig = _sig(1, target=1, level=95.0, known_at=0)   # vorher bekannt -> ok
    res = run_backtest(df, sig, cfg)
    assert res.trades.iloc[0]["entry_price"] == pytest.approx(95.0)


def test_level_outside_bar_range_rejected():
    """Ein Level, das die Bar nie erreicht hat, ist nicht ausfuehrbar."""
    df = _bars([(100, 100, 100, 100), (100, 110, 90, 100)])
    cfg = BacktestConfig(costs=_zero_costs())
    cfg.execution = ExecutionConfig(mode="level", strict=True)
    sig = _sig(1, target=1, level=150.0, known_at=0)
    with pytest.raises(ValueError, match="ausserhalb"):
        run_backtest(df, sig, cfg)


def test_non_strict_skips_instead_of_raising():
    df = _bars([(100, 100, 100, 100), (100, 110, 90, 100)])
    cfg = BacktestConfig(costs=_zero_costs())
    cfg.execution = ExecutionConfig(mode="level", strict=False)
    sig = _sig(1, target=1, level=150.0, known_at=0)
    res = run_backtest(df, sig, cfg)
    assert len(res.trades) == 0          # uebersprungen statt Ausnahme


def test_default_mode_is_close():
    """Der sichere Modus ist Default -- niemand faellt versehentlich zurueck."""
    assert BacktestConfig().execution.mode == "close"
