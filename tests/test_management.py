"""Tests fuer das Handelsmanagement: harter Stop, Gap, Break-even, Trailing, Zeitstop."""

import numpy as np
import pandas as pd
import pytest

from prop_backtester.config import (BacktestConfig, CostConfig, ManagementConfig,
                                    RiskConfig)
from prop_backtester.engine import run_backtest


def _bars(rows):
    """rows: Liste von (open, high, low, close)."""
    idx = pd.date_range("2025-01-01", periods=len(rows), freq="1h", tz="UTC")
    arr = np.asarray(rows, float)
    return pd.DataFrame(
        {"open": arr[:, 0], "high": arr[:, 1], "low": arr[:, 2], "close": arr[:, 3],
         "volume": np.ones(len(rows))},
        index=idx,
    )


def _flat(prices):
    return _bars([(p, p, p, p) for p in prices])


def _zero_costs():
    return CostConfig(fee_pct=0.0, slippage_pct=0.0, half_spread_pct=0.0,
                      slippage_vol_mult=0.0, funding_rate_daily_pct=0.0)


def _sig(df, bar, target=1, brick=1.0):
    return pd.DataFrame({
        "time": [df.index[bar]], "src_index": [bar], "price": [df["close"].iloc[bar]],
        "target": [target], "brick_size": [brick],
    })


def _cfg(mgmt=None, stop_bricks=2.0, **kw):
    return BacktestConfig(
        costs=_zero_costs(),
        risk=RiskConfig(risk_per_trade_pct=0.005, stop_bricks=stop_bricks,
                        max_leverage=100.0),
        management=mgmt or ManagementConfig(),
        **kw,
    )


# --- Grundverhalten --------------------------------------------------------

def test_ohne_management_kein_stop():
    """Ohne hard_stop laeuft der Trade durch -- das war der Zustand vorher."""
    df = _flat([100, 100, 90, 80, 70])
    res = run_backtest(df, _sig(df, 0), _cfg())
    assert len(res.trades) == 1
    assert res.trades["exit_reason"].iloc[0] == "ende"
    # Verlust deutlich groesser als das geplante 1R
    assert res.trades["r_multiple"].iloc[0] < -5


def test_harter_stop_begrenzt_den_verlust():
    # Einstieg 100, Brick 1, Stop 2 Bricks -> 98. Bar 1 durchlaeuft den Stop.
    df = _bars([(100, 100, 100, 100), (100, 100, 90, 95), (95, 95, 90, 90)])
    res = run_backtest(df, _sig(df, 0), _cfg(ManagementConfig(hard_stop=True,
                                                             stop_slippage_pct=0.0)))
    t = res.trades.iloc[0]
    assert t["exit_reason"] == "stop"
    assert t["r_multiple"] == pytest.approx(-1.0, abs=1e-9)


def test_stop_wird_auf_der_einstiegsbar_nicht_geprueft():
    """Der Fill liegt auf dem Schlusskurs -- der Rest der Bar ist vorbei."""
    df = _bars([(100, 100, 90, 100), (100, 100, 100, 100)])
    res = run_backtest(df, _sig(df, 0), _cfg(ManagementConfig(hard_stop=True)))
    assert res.trades["exit_reason"].iloc[0] == "ende"


def test_gap_fuellt_zur_eroeffnung_nicht_am_stop():
    """Eroeffnet die Bar unter dem Stop, ist der Stop-Preis nicht erreichbar."""
    df = _bars([(100, 100, 100, 100), (90, 91, 89, 90)])
    mgmt = ManagementConfig(hard_stop=True, stop_slippage_pct=0.0)
    res = run_backtest(df, _sig(df, 0), _cfg(mgmt))
    t = res.trades.iloc[0]
    assert t["exit_reason"] == "stop"
    assert t["exit_price"] == pytest.approx(90.0)
    assert t["r_multiple"] < -4          # Luecke kostet mehr als 1R


def test_stop_slippage_verschlechtert_den_fill():
    df = _flat([100, 100, 97, 97])
    ohne = run_backtest(df, _sig(df, 0), _cfg(ManagementConfig(hard_stop=True,
                                                              stop_slippage_pct=0.0)))
    mit = run_backtest(df, _sig(df, 0), _cfg(ManagementConfig(hard_stop=True,
                                                             stop_slippage_pct=0.002)))
    assert mit.trades["pnl"].iloc[0] < ohne.trades["pnl"].iloc[0]


# --- Nachziehen ------------------------------------------------------------

def test_breakeven_verhindert_verlust_nach_vorsprung():
    # +2 Bricks Vorsprung (Brick = 1, Stop 2 Bricks) -> Stop auf Einstieg
    df = _bars([(100, 100, 100, 100), (100, 102, 100, 102), (102, 102, 95, 96)])
    mgmt = ManagementConfig(hard_stop=True, breakeven_bricks=2.0,
                            stop_slippage_pct=0.0)
    res = run_backtest(df, _sig(df, 0), _cfg(mgmt))
    t = res.trades.iloc[0]
    assert t["exit_reason"] == "stop"
    assert t["exit_price"] == pytest.approx(100.0)
    assert t["stop_moves"] >= 1


def test_trailing_sichert_gewinn():
    df = _bars([(100, 100, 100, 100), (100, 110, 100, 110), (110, 110, 100, 100)])
    mgmt = ManagementConfig(hard_stop=True, trail_bricks=2.0, stop_slippage_pct=0.0)
    res = run_backtest(df, _sig(df, 0), _cfg(mgmt))
    t = res.trades.iloc[0]
    assert t["exit_reason"] == "stop"
    # Stop steht nach Bar 2 bei 110 - 2 = 108
    assert t["exit_price"] == pytest.approx(108.0)
    assert t["pnl"] > 0


def test_trailing_zieht_nie_zurueck():
    # Bar 1 setzt den Stop auf 110; der Rueckfall auf 111 darf ihn nicht senken.
    df = _bars([(100, 100, 100, 100), (100, 112, 100, 112),
                (112, 112, 111, 111), (111, 111, 105, 105)])
    mgmt = ManagementConfig(hard_stop=True, trail_bricks=2.0, stop_slippage_pct=0.0)
    res = run_backtest(df, _sig(df, 0), _cfg(mgmt))
    assert res.trades["exit_price"].iloc[0] == pytest.approx(110.0)


def test_trailing_am_brick_gitter_statt_am_bar_schluss():
    """Mit ``grid`` folgt der Stop den Bricks, nicht dem Schlusskurs."""
    df = _bars([(100, 100, 100, 100), (100, 105, 100, 105), (105, 105, 90, 95)])
    grid = np.array([100.0, 103.0, 103.0])   # Gitter hinkt dem Kurs nach
    mgmt = ManagementConfig(hard_stop=True, trail_bricks=2.0, stop_slippage_pct=0.0)
    res = run_backtest(df, _sig(df, 0), _cfg(mgmt), grid=grid)
    assert res.trades["exit_price"].iloc[0] == pytest.approx(101.0)


def test_grid_laenge_wird_geprueft():
    df = _flat([100, 101])
    with pytest.raises(ValueError):
        run_backtest(df, _sig(df, 0), _cfg(ManagementConfig(hard_stop=True)),
                     grid=np.array([100.0]))


# --- Zeitstop --------------------------------------------------------------

def test_zeitstop_schliesst_haengende_position():
    df = _flat([100, 100, 100, 100, 100, 100])
    mgmt = ManagementConfig(hard_stop=True, time_stop_bars=2, time_stop_min_r=1.0)
    res = run_backtest(df, _sig(df, 0), _cfg(mgmt))
    t = res.trades.iloc[0]
    assert t["exit_reason"] == "zeit"
    assert t["bars_held"] == 2


def test_zeitstop_laesst_laufer_laufen():
    # Nach 2 Bars deutlich ueber 1R -> Zeitstop greift nicht
    df = _flat([100, 110, 110, 110, 110])
    mgmt = ManagementConfig(hard_stop=True, time_stop_bars=2, time_stop_min_r=1.0)
    res = run_backtest(df, _sig(df, 0), _cfg(mgmt))
    assert res.trades["exit_reason"].iloc[0] == "ende"


# --- R-Abrechnung und Validierung -----------------------------------------

def test_r_multiple_entspricht_pnl_durch_risiko():
    df = _flat([100, 104, 104])
    res = run_backtest(df, _sig(df, 0), _cfg())
    t = res.trades.iloc[0]
    assert t["r_multiple"] == pytest.approx(t["pnl"] / t["risk"])
    assert t["r_multiple"] == pytest.approx(2.0, abs=1e-6)


def test_short_stop_funktioniert_spiegelbildlich():
    df = _bars([(100, 100, 100, 100), (100, 103, 100, 101)])
    mgmt = ManagementConfig(hard_stop=True, stop_slippage_pct=0.0)
    res = run_backtest(df, _sig(df, 0, target=-1), _cfg(mgmt))
    t = res.trades.iloc[0]
    assert t["side"] == "short"
    assert t["exit_reason"] == "stop"
    assert t["r_multiple"] == pytest.approx(-1.0, abs=1e-9)


def test_nachziehen_ohne_harten_stop_ist_ungueltig():
    with pytest.raises(ValueError):
        ManagementConfig(hard_stop=False, trail_bricks=2.0).validate()
    with pytest.raises(ValueError):
        ManagementConfig(hard_stop=False, breakeven_bricks=2.0).validate()


def test_negative_parameter_werden_abgelehnt():
    with pytest.raises(ValueError):
        ManagementConfig(stop_slippage_pct=-0.1).validate()
    with pytest.raises(ValueError):
        ManagementConfig(hard_stop=True, trail_bricks=0.0).validate()
    with pytest.raises(ValueError):
        ManagementConfig(hard_stop=True, time_stop_bars=0).validate()


# --- Feste Klammer: nur Stop und Ziel beenden den Trade -------------------

def test_gegensignal_dreht_normalerweise():
    df = _flat([100, 100, 100, 100])
    sig = pd.concat([_sig(df, 0, target=1), _sig(df, 2, target=-1)])
    res = run_backtest(df, sig, _cfg())
    assert list(res.trades["side"]) == ["long", "short"]


def test_ignore_reverse_signals_haelt_die_position():
    df = _flat([100, 100, 100, 100])
    sig = pd.concat([_sig(df, 0, target=1), _sig(df, 2, target=-1)])
    mgmt = ManagementConfig(hard_stop=True, ignore_reverse_signals=True)
    res = run_backtest(df, sig, _cfg(mgmt))
    assert list(res.trades["side"]) == ["long"]


def test_klammer_schliesst_am_ziel():
    """SL 3 Bricks, TP 6 Bricks (2R): das Ziel beendet den Trade."""
    df = _bars([(100, 100, 100, 100), (100, 107, 100, 106), (106, 106, 106, 106)])
    cfg = BacktestConfig(
        costs=_zero_costs(),
        risk=RiskConfig(risk_per_trade_pct=0.01, stop_bricks=3.0, max_leverage=100.0,
                        tp_r_multiples=[2.0], tp_take_fractions=[1.0]),
        management=ManagementConfig(hard_stop=True, stop_slippage_pct=0.0,
                                    ignore_reverse_signals=True),
    )
    res = run_backtest(df, _sig(df, 0, brick=1.0), cfg)
    t = res.trades.iloc[0]
    assert t["exit_reason"] == "ziel"
    assert t["r_multiple"] == pytest.approx(2.0, abs=1e-9)


def test_klammer_stop_zaehlt_vor_dem_ziel():
    """Beruehrt eine Bar beide Seiten, gilt der Stop -- ohne Tickdaten pessimistisch."""
    df = _bars([(100, 100, 100, 100), (100, 107, 96, 106)])
    cfg = BacktestConfig(
        costs=_zero_costs(),
        risk=RiskConfig(risk_per_trade_pct=0.01, stop_bricks=3.0, max_leverage=100.0,
                        tp_r_multiples=[2.0], tp_take_fractions=[1.0]),
        management=ManagementConfig(hard_stop=True, stop_slippage_pct=0.0,
                                    ignore_reverse_signals=True),
    )
    res = run_backtest(df, _sig(df, 0, brick=1.0), cfg)
    assert res.trades["exit_reason"].iloc[0] == "stop"
    assert res.trades["r_multiple"].iloc[0] == pytest.approx(-1.0, abs=1e-9)
