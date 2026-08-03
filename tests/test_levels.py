"""Tests fuer die S/R-Level-Konstruktion.

Der wichtigste ist ``test_levels_no_lookahead``: Der Level-Stand bis Bar N darf
sich nicht aendern, wenn spaetere Bars fehlen. Ein Pivot bei Bar i ist erst bei
i+width bekannt -- wer das verletzt, sieht in die Zukunft.
"""

import numpy as np
import pandas as pd
import pytest

from prop_backtester import data, levels


@pytest.fixture(scope="module")
def df():
    return data.generate_realistic(bars=1200, seed=7)


def _frame(highs, lows=None, closes=None):
    n = len(highs)
    lows = lows if lows is not None else [h - 1.0 for h in highs]
    closes = closes if closes is not None else [(h + l) / 2 for h, l in zip(highs, lows)]
    idx = pd.date_range("2025-01-01", periods=n, freq="1h", tz="UTC")
    return pd.DataFrame({"open": closes, "high": highs, "low": lows,
                         "close": closes, "volume": np.ones(n)}, index=idx)


def _baseline(n, high=101.0, low=99.0, slope=0.01):
    """Leicht fallende Grundlinie -- so entstehen KEINE Pivots ausser den
    absichtlich gesetzten Spitzen.

    Bei einer exakt flachen Reihe ist wegen der Gleichstand-Behandlung (``>=``)
    jeder Bar ein Pivot; das erzeugt Phantom-Level und macht die Tests wertlos.
    """
    highs = [high - slope * i for i in range(n)]
    lows = [low - slope * i for i in range(n)]
    closes = [(h + l) / 2 for h, l in zip(highs, lows)]
    return highs, lows, closes


# --------------------------------------------------------------- Zeitlogik

def test_pivot_confirmed_width_bars_later(df):
    for p in levels.find_pivots(df, width=8):
        assert p.confirmed_at == p.bar + 8


def test_pivot_is_local_extreme():
    highs, lows, closes = _baseline(21)
    highs[10] = 110.0                        # Spitze bei Index 10
    pv = levels.find_pivots(_frame(highs, lows, closes), width=5)
    tops = [p for p in pv if p.kind == levels.RESISTANCE and p.price == 110.0]
    assert len(tops) == 1
    assert tops[0].bar == 10
    assert tops[0].confirmed_at == 15


@pytest.mark.parametrize("width", [4, 8, 12])
def test_levels_no_lookahead(df, width):
    """Level bis Bar N muessen ohne die spaeteren Bars identisch sein."""
    cut = 900
    full = levels.build_levels(df, width=width)
    part = levels.build_levels(df.iloc[:cut], width=width)
    for t in range(cut):
        assert full[t] == part[t], f"Bar {t}: Level weichen ab -> Look-ahead"


def test_events_no_lookahead(df):
    cut = 900
    full_by = levels.build_levels(df)
    part_by = levels.build_levels(df.iloc[:cut])
    for fn in (levels.breakout_events, levels.bounce_events):
        f = [e for e in fn(full_by, df, min_touch=2) if e[0] < cut]
        p = [e for e in fn(part_by, df.iloc[:cut], min_touch=2) if e[0] < cut]
        assert f == p, f"{fn.__name__}: Ereignisse weichen ab -> Look-ahead"


# ------------------------------------------------------------ Level-Aufbau

def test_nearby_pivots_merge_into_one_level():
    """Zwei fast gleiche Hochs ergeben EIN Level mit zwei Beruehrungen."""
    highs, lows, closes = _baseline(60)
    highs[10] = 120.0
    highs[35] = 120.3          # innerhalb der Toleranz
    by = levels.build_levels(_frame(highs, lows, closes), width=5, tol_atr=1.0,
                             max_age=1000)
    res = [lv for lv in by[59] if lv[1] == levels.RESISTANCE and lv[2] >= 2]
    assert len(res) == 1
    assert res[0][2] == 2
    assert 120.0 <= res[0][0] <= 120.3


def test_distant_pivots_stay_separate():
    highs, lows, closes = _baseline(60)
    highs[10] = 120.0
    highs[35] = 160.0          # weit ausserhalb jeder Toleranz
    by = levels.build_levels(_frame(highs, lows, closes), width=5, tol_atr=0.5,
                             max_age=1000)
    prices = sorted(lv[0] for lv in by[59] if lv[1] == levels.RESISTANCE)
    assert 120.0 in prices and 160.0 in prices


def test_levels_expire(df):
    young = levels.build_levels(df, max_age=50)
    old = levels.build_levels(df, max_age=2000)
    last = len(df) - 1
    assert len(young[last]) < len(old[last])


# ---------------------------------------------------------------- Ereignisse

def test_breakout_direction():
    """Kurs bricht ueber einen zweifach getesteten Widerstand -> long."""
    n = 90
    highs, lows, closes = _baseline(n)
    for b in (10, 35):                       # zwei Pivot-Hochs auf 120
        highs[b] = 120.0
    closes[80] = 130.0                       # Ausbruch
    highs[80] = 131.0
    d = _frame(highs, lows, closes)
    by = levels.build_levels(d, width=5, tol_atr=1.0, max_age=1000)
    ev = levels.breakout_events(by, d, min_touch=2)
    assert any(t == 80 and direction == 1 for (t, direction, _, _) in ev)


def test_bounce_direction():
    """Kurs faellt auf eine zweifach getestete Unterstuetzung und haelt -> long."""
    n = 90
    highs, lows, closes = _baseline(n)
    for b in (10, 35):                       # zwei Pivot-Tiefs auf 80
        lows[b] = 80.0
    lows[80] = 80.2                          # Ruecklauf in die Zone
    closes[80] = 85.0                        # Schluss haelt darueber
    d = _frame(highs, lows, closes)
    by = levels.build_levels(d, width=5, tol_atr=1.0, max_age=1000)
    ev = levels.bounce_events(by, d, min_touch=2, zone_atr=2.0)
    assert any(t == 80 and direction == 1 for (t, direction, _, _) in ev)


def test_bounce_needs_prior_bar_outside_zone():
    """Eine Seitwaertsphase IM Level darf nicht dutzende Signale liefern."""
    n = 120
    highs, lows, closes = _baseline(n)
    for b in (10, 35):
        lows[b] = 95.0
    for b in range(70, 100):                 # dauerhaft an der Unterstuetzung
        lows[b] = 95.1
        closes[b] = 95.5
    d = _frame(highs, lows, closes)
    by = levels.build_levels(d, width=5, tol_atr=1.0, max_age=1000)
    ev = levels.bounce_events(by, d, min_touch=2, zone_atr=2.0)
    in_range = [e for e in ev if 70 <= e[0] < 100]
    assert len(in_range) <= 2, f"zu viele Signale in der Seitwaertsphase: {len(in_range)}"


def test_more_touches_is_subset():
    """Ereignisse mit hoher Schwelle sind eine Teilmenge der niedrigen."""
    d = data.generate_realistic(bars=900, seed=3)
    by = levels.build_levels(d)
    lo = set((t, x) for (t, x, _, _) in levels.breakout_events(by, d, min_touch=2))
    hi = set((t, x) for (t, x, _, _) in levels.breakout_events(by, d, min_touch=5))
    assert hi <= lo


def test_nearest_opposite_picks_closest():
    n = 120
    highs, lows, closes = _baseline(n)
    for b in (10, 30):
        highs[b] = 130.0
    for b in (50, 70):
        highs[b] = 160.0
    d = _frame(highs, lows, closes)
    by = levels.build_levels(d, width=5, tol_atr=1.0, max_age=1000)
    tgt = levels.nearest_opposite(by, n - 1, price=100.0, direction=1, min_touch=2)
    assert tgt == pytest.approx(130.0, abs=1.0)
