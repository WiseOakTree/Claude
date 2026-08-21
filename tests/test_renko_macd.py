"""Tests fuer die TradingView-Nachbildung: OHLC-Quelle, 2-Boxen-Umkehr, MACD auf Bricks."""

import numpy as np
import pandas as pd
import pytest

from prop_backtester.config import RenkoConfig
from prop_backtester.renko import build_renko
from prop_backtester.renko_macd import filter_signals, macd_lines, macd_signals


def _bars(rows):
    idx = pd.date_range("2025-01-01", periods=len(rows), freq="1h", tz="UTC")
    a = np.asarray(rows, float)
    return pd.DataFrame({"open": a[:, 0], "high": a[:, 1], "low": a[:, 2],
                         "close": a[:, 3], "volume": np.ones(len(rows))}, index=idx)


def _fix(**kw):
    return RenkoConfig(mode="fixed", fixed_brick=1.0, **kw)


# --- Quelle: close gegen ohlc ---------------------------------------------

def test_close_quelle_ignoriert_dochte():
    # Docht bis 110, Schluss zurueck auf 100 -> mit "close" passiert nichts
    df = _bars([(100, 100, 100, 100), (100, 110, 100, 100)])
    assert len(build_renko(df, _fix(source="close")).bricks) == 0


def test_ohlc_quelle_baut_bricks_aus_dochten():
    df = _bars([(100, 100, 100, 100), (100, 110, 100, 100)])
    b = build_renko(df, _fix(source="ohlc")).bricks
    assert len(b) > 0
    assert (b["direction"] == 1).sum() == 10        # Docht bis 110 = 10 Bricks


def test_ohlc_reihenfolge_gegenlaeufiges_extrem_zuerst():
    """Steigende Bar: erst das Tief, dann das Hoch -- pessimistisch."""
    df = _bars([(100, 100, 100, 100), (100, 103, 97, 103)])
    b = build_renko(df, _fix(source="ohlc")).bricks
    assert list(b["direction"])[:3] == [-1, -1, -1]   # Tief zuerst
    assert b["direction"].iloc[-1] == 1


def test_fallende_bar_verarbeitet_hoch_zuerst():
    df = _bars([(100, 100, 100, 100), (100, 103, 97, 97)])
    b = build_renko(df, _fix(source="ohlc")).bricks
    assert list(b["direction"])[:3] == [1, 1, 1]


# --- Umkehr: 1 Box gegen 2 Boxen ------------------------------------------

def test_gitter_dreht_nach_einer_box():
    df = _bars([(100, 100, 100, 100), (100, 102, 100, 102), (102, 102, 101, 101)])
    b = build_renko(df, _fix(source="close", reversal_boxes=1.0)).bricks
    assert list(b["direction"]) == [1, 1, -1]


def test_klassisches_renko_braucht_zwei_boxen():
    df = _bars([(100, 100, 100, 100), (100, 102, 100, 102), (102, 102, 101, 101)])
    b = build_renko(df, _fix(source="close", reversal_boxes=2.0)).bricks
    assert list(b["direction"]) == [1, 1]      # ein Punkt zurueck reicht nicht


def test_zwei_boxen_umkehr_springt_zwei_boxen_weit():
    df = _bars([(100, 100, 100, 100), (100, 102, 100, 102), (102, 102, 100, 100)])
    b = build_renko(df, _fix(source="close", reversal_boxes=2.0)).bricks
    assert list(b["direction"]) == [1, 1, -1]
    assert b["close"].iloc[-1] == pytest.approx(100.0)   # 102 - 2*1


def test_prozentuale_box_waechst_mit_dem_kurs():
    df = _bars([(100, 100, 100, 100), (200, 200, 200, 200), (204, 204, 204, 204)])
    cfg = RenkoConfig(mode="fixed", fixed_brick_pct=0.01, source="close")
    b = build_renko(df, cfg).bricks
    # Bei Kurs 200 ist die Box 2,00 -- nicht 1,00 wie bei Kurs 100
    assert b["brick_size"].iloc[-1] == pytest.approx(2.04)


def test_ungueltige_schalter():
    with pytest.raises(ValueError):
        RenkoConfig(source="hlc").validate()
    with pytest.raises(ValueError):
        RenkoConfig(reversal_boxes=0.5).validate()


# --- MACD auf Bricks -------------------------------------------------------

def _bricks(closes):
    n = len(closes)
    d = np.sign(np.diff(np.concatenate([[closes[0]], closes]))).astype(int)
    d[d == 0] = 1
    return pd.DataFrame({
        "time": pd.date_range("2025-01-01", periods=n, freq="1h", tz="UTC"),
        "close": closes, "direction": d,
        "brick_size": np.ones(n), "src_index": np.arange(n),
    })


def test_macd_linien_haben_brick_laenge():
    b = _bricks(np.linspace(100, 200, 300))
    lines = macd_lines(b)
    assert len(lines) == len(b)
    assert lines["macd"].iloc[-1] > 0           # Aufwaertsreihe -> MACD positiv


def test_kreuzung_wird_erkannt_und_richtung_stimmt():
    steigend = np.linspace(100, 200, 200)
    fallend = np.linspace(200, 100, 200)
    b = _bricks(np.concatenate([steigend, fallend]))
    sig = macd_signals(b)
    assert len(sig) >= 1
    assert sig["target"].iloc[0] == -1          # nach dem Umschwung: short
    assert set(sig["target"]) <= {-1, 1}


def test_warmup_unterdrueckt_scheinkreuzungen():
    b = _bricks(np.linspace(100, 200, 300))
    assert len(macd_signals(b, warmup=100)) <= len(macd_signals(b, warmup=0))


def test_richtungsfilter_und_leere_eingabe():
    b = _bricks(np.concatenate([np.linspace(100, 200, 200), np.linspace(200, 100, 200)]))
    assert set(macd_signals(b, allow_short=False)["target"]) <= {1}
    leer = pd.DataFrame(columns=["time", "close", "direction", "brick_size", "src_index"])
    assert len(macd_signals(leer)) == 0


def test_fast_muss_kleiner_als_slow_sein():
    with pytest.raises(ValueError):
        macd_lines(_bricks(np.linspace(100, 110, 50)), fast=26, slow=12)


def test_filter_wirkt_auf_der_ausloesebar():
    b = _bricks(np.concatenate([np.linspace(100, 200, 200), np.linspace(200, 100, 200)]))
    sig = macd_signals(b)
    ok = np.zeros(len(b), dtype=bool)
    ok[sig["src_index"].iloc[0]] = True
    gefiltert = filter_signals(sig, ok)
    assert len(gefiltert) == 1
    assert gefiltert["src_index"].iloc[0] == sig["src_index"].iloc[0]
