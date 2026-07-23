import numpy as np
import pandas as pd

from prop_backtester.prop import (
    PRESETS,
    evaluate_challenge,
    evaluate_all_presets,
    _day_key,
)


def _equity(values, start="2025-01-01", freq="1h"):
    idx = pd.date_range(start, periods=len(values), freq=freq, tz="UTC")
    v = np.asarray(values, float)
    return pd.DataFrame({"equity_close": v, "equity_low": v, "equity_high": v}, index=idx)


def test_pass_when_target_reached():
    # Startet bei 100k, steigt monoton auf 110k -> 1step_classic (10%) bestanden
    eq = _equity(np.linspace(100_000, 111_000, 300))
    res = evaluate_challenge(eq, PRESETS["1step_classic"], initial_balance=100_000)
    assert res.passed
    assert res.phases[0].status == "passed"


def test_fail_on_max_drawdown():
    # -2% pro Tag: Daily Loss (3%) nie verletzt, aber Gesamt-Drawdown (6% statisch)
    # wird ueberschritten -> failed mit max_drawdown.
    eq = _equity([100_000, 98_000, 96_040, 94_119, 92_236], freq="1D")
    res = evaluate_challenge(eq, PRESETS["1step_classic"], initial_balance=100_000)
    assert not res.passed
    assert res.phases[0].fail_reason == "max_drawdown"


def test_fail_on_daily_loss():
    # -3% an einem Tag -> daily_loss (bevor der 6%-Gesamtdrawdown greift)
    eq = _equity([100_000, 99_000, 96_500])
    res = evaluate_challenge(eq, PRESETS["1step_classic"], initial_balance=100_000)
    assert not res.passed
    assert res.phases[0].fail_reason == "daily_loss"


def test_two_step_needs_both_phases():
    # Nur +10% erreicht -> Phase1 passt, Phase2 (weitere +5% frisch) unvollstaendig
    eq = _equity(np.linspace(100_000, 110_500, 200))
    res = evaluate_challenge(eq, PRESETS["2step_classic"], initial_balance=100_000)
    assert not res.passed
    assert res.phases[0].status == "passed"


def test_two_step_full_pass():
    # Genug Aufwaertsbewegung fuer +10% dann frisch +5%
    eq = _equity(np.linspace(100_000, 130_000, 600))
    res = evaluate_challenge(eq, PRESETS["2step_classic"], initial_balance=100_000)
    assert res.passed
    assert all(p.status == "passed" for p in res.phases)


def test_daily_reset_key_boundary():
    # 00:15 UTC gehoert noch zum Vortag (Reset 00:30)
    before = pd.Timestamp("2025-01-02T00:15:00Z")
    after = pd.Timestamp("2025-01-02T00:45:00Z")
    from datetime import time
    assert _day_key(before, time(0, 30)) != _day_key(after, time(0, 30))
    assert _day_key(before, time(0, 30)) == _day_key(pd.Timestamp("2025-01-01T12:00:00Z"), time(0, 30))


def test_evaluate_all_presets_keys():
    eq = _equity(np.linspace(100_000, 105_000, 100))
    out = evaluate_all_presets(eq, initial_balance=100_000)
    assert set(out) == set(PRESETS)
