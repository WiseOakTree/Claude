"""Binance-Downloader: tiefe OHLC-Historie via data.binance.vision.

Die offentliche Binance-REST-API ist teils geoblockt; die statischen
Daten-Dumps unter ``data.binance.vision`` sind es nicht. Dieses Modul laedt die
**monatlichen Klines-ZIPs** und aggregiert sie zu einem OHLCV-DataFrame im
Format des Backtesters.

Verwendung:
    from prop_backtester import binance
    df = binance.download_klines("BTCUSDT", "1h", "2022-07", "2026-06")
    df.to_csv("btcusdt_1h.csv")

Hinweis: BTCUSDT ist ein USDT-Paar -- fuer BTC-Strategietests praktisch
gleichwertig zu BTC/USD, aber nicht identisch mit Kraken-Daten.
"""

from __future__ import annotations

import io
import zipfile
from typing import List, Optional

import numpy as np
import pandas as pd

from .data import _finalize

VISION = "https://data.binance.vision/data/spot/monthly/klines"

# Binance-Kline-Spalten (ohne Header in den CSVs)
_COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time",
         "quote_volume", "count", "taker_base", "taker_quote", "ignore"]


def _month_range(start: str, end: str) -> List[str]:
    """Liste von 'YYYY-MM' von start bis end (inklusive)."""
    s = pd.Period(start, freq="M")
    e = pd.Period(end, freq="M")
    return [str(p) for p in pd.period_range(s, e, freq="M")]


def _parse_time(series: pd.Series) -> pd.DatetimeIndex:
    """Erkennt die Zeiteinheit (s/ms/us/ns) automatisch und konvertiert zu UTC."""
    v = float(series.iloc[0])
    if v >= 1e18:
        unit = "ns"
    elif v >= 1e15:
        unit = "us"
    elif v >= 1e12:
        unit = "ms"
    else:
        unit = "s"
    return pd.to_datetime(series.astype("int64"), unit=unit, utc=True)


def _read_month_zip(content: bytes) -> Optional[pd.DataFrame]:
    """Entpackt ein Monats-ZIP und liest die Kline-CSV."""
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        name = zf.namelist()[0]
        with zf.open(name) as fh:
            raw = fh.read()
    # Binance-CSVs haben teils (neuere) eine Kopfzeile -> automatisch erkennen
    first = raw[:64].lstrip()
    header = 0 if first[:9].lower() == b"open_time" else None
    df = pd.read_csv(io.BytesIO(raw), header=header, names=None if header == 0 else _COLS)
    df.columns = [str(c).strip().lower() for c in df.columns]
    if len(df) == 0:
        return None
    idx = _parse_time(df["open_time"])
    # .to_numpy(), damit pandas nicht am alten RangeIndex ausrichtet (sonst NaN)
    out = pd.DataFrame({
        "open": df["open"].astype(float).to_numpy(),
        "high": df["high"].astype(float).to_numpy(),
        "low": df["low"].astype(float).to_numpy(),
        "close": df["close"].astype(float).to_numpy(),
        "volume": df["volume"].astype(float).to_numpy(),
    }, index=idx)
    return out


def download_klines(symbol: str = "BTCUSDT", interval: str = "1h",
                    start: str = "2022-01", end: Optional[str] = None,
                    session=None, timeout: float = 60.0,
                    progress: bool = True) -> pd.DataFrame:
    """Laedt monatliche Klines von data.binance.vision und aggregiert zu OHLCV.

    ``start``/``end`` als 'YYYY-MM'. Fehlende Monate (404) werden uebersprungen.
    """
    import requests

    sess = session or requests
    if end is None:
        end = str(pd.Timestamp.utcnow().to_period("M") - 1)  # letzter voller Monat
    months = _month_range(start, end)
    frames: List[pd.DataFrame] = []
    missing = 0
    for m in months:
        url = f"{VISION}/{symbol}/{interval}/{symbol}-{interval}-{m}.zip"
        r = sess.get(url, timeout=timeout)
        if r.status_code == 404:
            missing += 1
            continue
        r.raise_for_status()
        part = _read_month_zip(r.content)
        if part is not None:
            frames.append(part)
        if progress and len(frames) % 6 == 0 and frames:
            print(f"  ... {m}: {sum(len(f) for f in frames)} Bars")
    if not frames:
        raise RuntimeError("Keine Daten geladen -- Symbol/Zeitraum/Netzwerk pruefen.")
    df = pd.concat(frames)
    df = df[~df.index.duplicated(keep="last")].sort_index()
    if progress:
        print(f"  fertig: {len(df)} Bars, {len(months)-missing}/{len(months)} Monate "
              f"({df.index[0].date()} -> {df.index[-1].date()})")
    return _finalize(df)
