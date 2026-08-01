"""Tests fuer die Strategie-Familien -- vor allem: kein Look-ahead.

Der entscheidende Test ist ``test_no_lookahead``: Signale, die auf einer
abgeschnittenen Kursreihe berechnet werden, muessen mit denen aus der vollen
Reihe uebereinstimmen. Nutzt ein Generator zukuenftige Daten, weichen sie ab.
"""

import numpy as np
import pandas as pd
import pytest

from prop_backtester import data, strategies


@pytest.fixture(scope="module")
def df():
    return data.generate_realistic(bars=1500, seed=42)


@pytest.mark.parametrize("name", sorted(strategies.REGISTRY))
def test_signal_format(name, df):
    sig = strategies.REGISTRY[name](df)
    assert list(sig.columns) == ["time", "src_index", "price", "target", "brick_size"]
    if len(sig):
        assert set(sig["target"].unique()).issubset({-1, 0, 1})
        assert (sig["brick_size"] > 0).all()
        assert sig["src_index"].is_monotonic_increasing
        assert (sig["src_index"] < len(df)).all()


@pytest.mark.parametrize("name", sorted(strategies.REGISTRY))
def test_no_lookahead(name, df):
    """Signale bis Bar N duerfen sich nicht aendern, wenn spaetere Bars fehlen."""
    gen = strategies.REGISTRY[name]
    cut = 1000
    full = gen(df)
    part = gen(df.iloc[:cut])
    f = full[full["src_index"] < cut - 1].reset_index(drop=True)
    p = part[part["src_index"] < cut - 1].reset_index(drop=True)
    assert len(f) == len(p), f"{name}: unterschiedliche Signalanzahl -> Look-ahead"
    if len(f):
        assert (f["src_index"].to_numpy() == p["src_index"].to_numpy()).all()
        assert (f["target"].to_numpy() == p["target"].to_numpy()).all()


@pytest.mark.parametrize("name", sorted(strategies.REGISTRY))
def test_alternating_positions(name, df):
    """Aufeinanderfolgende Signale muessen die Position tatsaechlich aendern."""
    sig = strategies.REGISTRY[name](df)
    t = sig["target"].to_numpy()
    assert all(t[i] != t[i + 1] for i in range(len(t) - 1))


def test_donchian_uses_prior_bars_only():
    # Monoton steigend: der Ausbruch darf nicht am eigenen Hoch scheitern
    n = 300
    idx = pd.date_range("2025-01-01", periods=n, freq="1h", tz="UTC")
    p = np.linspace(100, 200, n)
    d = pd.DataFrame({"open": p, "high": p * 1.001, "low": p * 0.999,
                      "close": p, "volume": np.ones(n)}, index=idx)
    sig = strategies.donchian(d, lookback=20)
    assert len(sig) >= 1
    assert sig["target"].iloc[0] == 1
