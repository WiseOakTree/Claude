import io
import zipfile

import numpy as np
import pandas as pd

from prop_backtester import binance


def _make_zip(rows, header=False):
    """Baut ein Binance-Monats-ZIP im Speicher (rows = Liste von Zeilen-Strings)."""
    lines = []
    if header:
        lines.append(",".join(binance._COLS))
    lines.extend(rows)
    csv = "\n".join(lines).encode()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("BTCUSDT-1h-2024-01.csv", csv)
    return buf.getvalue()


def _row(ts_ms, o, h, l, c, v):
    return f"{ts_ms},{o},{h},{l},{c},{v},{ts_ms+3599999},0,10,0,0,0"


def test_read_month_zip_no_header_values_not_nan():
    # Regression: kein Index-Alignment-NaN (Series muessen .to_numpy() sein)
    base = 1704067200000  # 2024-01-01 00:00 UTC in ms
    rows = [_row(base + i * 3600000, 100 + i, 110 + i, 90 + i, 105 + i, 1.5) for i in range(5)]
    df = binance._read_month_zip(_make_zip(rows, header=False))
    assert len(df) == 5
    assert int(df.isna().sum().sum()) == 0
    assert df["close"].iloc[0] == 105
    assert df["high"].iloc[4] == 114
    assert df.index[0] == pd.Timestamp("2024-01-01T00:00:00Z")


def test_read_month_zip_with_header():
    base = 1704067200000
    rows = [_row(base, 100, 110, 90, 105, 2.0)]
    df = binance._read_month_zip(_make_zip(rows, header=True))
    assert len(df) == 1
    assert df["open"].iloc[0] == 100
    assert df["volume"].iloc[0] == 2.0


def test_parse_time_units():
    # Sekunden, Millisekunden, Mikrosekunden werden alle erkannt
    s = pd.Series([1704067200])
    ms = pd.Series([1704067200000])
    us = pd.Series([1704067200000000])
    for series in (s, ms, us):
        idx = binance._parse_time(series)
        assert idx[0] == pd.Timestamp("2024-01-01T00:00:00Z")


def test_month_range():
    months = binance._month_range("2023-11", "2024-02")
    assert months == ["2023-11", "2023-12", "2024-01", "2024-02"]
    assert len(binance._month_range("2024-01", "2024-01")) == 1
