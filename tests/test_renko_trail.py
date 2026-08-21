"""Tests fuer Renko-Trail: Einstiegs-Ereignisse, Gitter und die Management-Leiter."""

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from prop_backtester import data
from prop_backtester.config import BacktestConfig, CostConfig, RenkoConfig
from prop_backtester.renko import build_renko
from prop_backtester.renko_trail import (VARIANTS, brick_grid, entry_signals,
                                         run_variant, variant_config)


def _bricks(directions, sizes=None):
    n = len(directions)
    sizes = sizes or [1.0] * n
    return pd.DataFrame({
        "time": pd.date_range("2025-01-01", periods=n, freq="1h", tz="UTC"),
        "close": np.cumsum(np.asarray(directions, float)) + 100.0,
        "direction": directions,
        "brick_size": sizes,
        "src_index": list(range(n)),
    })


# --- Einstiegs-Ereignisse --------------------------------------------------

def test_signal_erst_beim_dritten_brick():
    sig = entry_signals(_bricks([1, 1, 1]), entry_bricks=3)
    assert len(sig) == 1
    assert sig["src_index"].iloc[0] == 2
    assert sig["target"].iloc[0] == 1


def test_kein_nachkaufen_bei_laengerer_serie():
    """Eine Serie aus sechs Bricks gibt genau ein Signal, nicht vier."""
    sig = entry_signals(_bricks([1] * 6), entry_bricks=3)
    assert len(sig) == 1


def test_serie_startet_nach_richtungswechsel_neu():
    sig = entry_signals(_bricks([1, 1, -1, -1, -1, 1, 1, 1]), entry_bricks=3)
    assert list(sig["target"]) == [-1, 1]
    assert list(sig["src_index"]) == [4, 7]


def test_zu_kurze_serie_gibt_kein_signal():
    sig = entry_signals(_bricks([1, 1, -1, 1, 1]), entry_bricks=3)
    assert len(sig) == 0
    assert list(sig.columns) == ["time", "src_index", "price", "target", "brick_size"]


def test_richtungsfilter():
    b = _bricks([1, 1, 1, -1, -1, -1])
    assert list(entry_signals(b, 3, allow_short=False)["target"]) == [1]
    assert list(entry_signals(b, 3, allow_long=False)["target"]) == [-1]


def test_ungueltige_parameter():
    with pytest.raises(ValueError):
        entry_signals(_bricks([1, 1]), entry_bricks=0)
    with pytest.raises(ValueError):
        entry_signals(_bricks([1, 1]), allow_long=False, allow_short=False)


# --- Brick-Gitter ----------------------------------------------------------

def test_gitter_haelt_den_letzten_brick():
    b = pd.DataFrame({
        "time": pd.date_range("2025-01-01", periods=2, freq="1h", tz="UTC"),
        "close": [101.0, 102.0], "direction": [1, 1],
        "brick_size": [1.0, 1.0], "src_index": [1, 3],
    })
    g = brick_grid(b, 6)
    assert np.isnan(g[0])                      # vor dem ersten Brick: unbekannt
    assert g[1] == 101.0 and g[2] == 101.0     # gilt bis zum naechsten Brick
    assert g[3] == 102.0 and g[5] == 102.0


def test_gitter_nimmt_den_letzten_brick_einer_bar():
    b = pd.DataFrame({
        "time": pd.date_range("2025-01-01", periods=2, freq="1h", tz="UTC"),
        "close": [101.0, 102.0], "direction": [1, 1],
        "brick_size": [1.0, 1.0], "src_index": [1, 1],
    })
    assert brick_grid(b, 3)[1] == 102.0


def test_leeres_gitter():
    b = pd.DataFrame(columns=["time", "close", "direction", "brick_size", "src_index"])
    assert np.isnan(brick_grid(b, 4)).all()


# --- Die Leiter ------------------------------------------------------------

def test_leiter_ist_vollstaendig_und_gueltig():
    assert list(VARIANTS) == ["V0", "V1", "V2", "V3", "V4", "V5", "V6"]
    for v in VARIANTS.values():
        variant_config(v).validate()


def test_leiter_baut_aufeinander_auf():
    m = {k: v.management for k, v in VARIANTS.items()}
    assert not m["V0"].hard_stop
    assert m["V1"].hard_stop
    assert m["V3"].breakeven_bricks == 2.0 and m["V2"].breakeven_bricks is None
    assert m["V4"].trail_bricks == 2.0 and m["V3"].trail_bricks is None
    assert VARIANTS["V5"].tp_take_fractions == [0.5] and not VARIANTS["V4"].tp_take_fractions
    assert m["V6"].time_stop_bars == 240 and m["V5"].time_stop_bars is None
    assert VARIANTS["V0"].mode == "reverse" and VARIANTS["V2"].mode == "entry"


def _demo_df():
    return data.generate_synthetic(bars=4000, seed=7)


def test_alle_stufen_laufen_durch():
    df = _demo_df()
    for key, v in VARIANTS.items():
        res = run_variant(df, v)
        assert len(res.trades) > 0, key
        assert res.trades["r_multiple"].notna().all()
        assert np.isfinite(res.final_balance)


def test_harter_stop_kappt_den_groessten_verlust():
    df = _demo_df()
    ohne = run_variant(df, VARIANTS["V0"]).trades["r_multiple"].min()
    mit = run_variant(df, VARIANTS["V1"]).trades["r_multiple"].min()
    assert mit > ohne


def test_diskrete_trades_sind_nicht_dauerhaft_im_markt():
    df = _demo_df()
    v0 = run_variant(df, VARIANTS["V0"]).trades
    v2 = run_variant(df, VARIANTS["V2"]).trades
    spanne = (df.index[-1] - df.index[0]).total_seconds()
    zeit_v0 = (v0["exit_time"] - v0["entry_time"]).dt.total_seconds().sum() / spanne
    zeit_v2 = (v2["exit_time"] - v2["entry_time"]).dt.total_seconds().sum() / spanne
    assert zeit_v0 > 0.95      # Stop-and-Reverse ist praktisch immer im Markt
    assert zeit_v2 < zeit_v0


def test_zeitstop_greift_wenn_er_bindet():
    """V6 hat einen Zeitstop bei 240 Bars -- neben dem Trailing bindet er selten.

    Deshalb hier mit kurzem Zeitstop geprueft, dass der Baustein wirkt.
    """
    df = _demo_df()
    v = replace(VARIANTS["V2"],
                management=replace(VARIANTS["V2"].management,
                                   time_stop_bars=24, time_stop_min_r=1.0))
    gruende = set(run_variant(df, v).trades["exit_reason"])
    assert "zeit" in gruende
    assert "stop" in gruende


def test_variant_config_veraendert_die_basis_nicht():
    base = BacktestConfig(costs=CostConfig(fee_pct=0.001),
                          renko=RenkoConfig(atr_period=20))
    cfg = variant_config(VARIANTS["V6"], base)
    assert cfg.renko.atr_period == 20 and cfg.costs.fee_pct == 0.001
    assert base.management.hard_stop is False        # Basis bleibt unberuehrt
    assert base.risk.tp_take_fractions == []
