"""Marktdaten laden: CSV, Kraken Public API oder synthetische Demo-Daten.

Ein OHLCV-DataFrame hat immer:
  * einen ``DatetimeIndex`` in UTC (Bar-Oeffnungszeit)
  * die Spalten ``open, high, low, close, volume`` (float)

Der Backtester arbeitet ausschliesslich mit diesem Format.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = ["open", "high", "low", "close", "volume"]


def _finalize(df: pd.DataFrame) -> pd.DataFrame:
    """Normalisiert Spalten/Index und prueft die Konsistenz der Daten."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Fehlende Spalten in den Daten: {missing}")
    df = df[REQUIRED_COLUMNS].astype(float)
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("Index muss ein DatetimeIndex sein")
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    else:
        df.index = df.index.tz_convert("UTC")
    df = df[~df.index.duplicated(keep="last")].sort_index()
    # Grundlegende OHLC-Plausibilitaet
    bad = (df["high"] < df["low"]) | (df["high"] < df["open"]) | (df["high"] < df["close"]) \
        | (df["low"] > df["open"]) | (df["low"] > df["close"])
    if bool(bad.any()):
        raise ValueError(f"{int(bad.sum())} Bars mit inkonsistenten OHLC-Werten gefunden")
    return df


def load_csv(path: str, time_col: Optional[str] = None) -> pd.DataFrame:
    """Laedt OHLCV aus einer CSV.

    Erwartet eine Zeitspalte (auto-erkannt: ``time``/``timestamp``/``date``/erste
    Spalte). Unix-Sekunden oder ISO-Strings werden unterstuetzt.
    """
    df = pd.read_csv(path)
    df.columns = [str(c).strip().lower() for c in df.columns]
    if time_col is None:
        for cand in ("time", "timestamp", "date", "datetime", "open_time"):
            if cand in df.columns:
                time_col = cand
                break
        else:
            time_col = df.columns[0]
    ts = df[time_col]
    if np.issubdtype(ts.dtype, np.number):
        # Heuristik: Millisekunden vs. Sekunden
        unit = "ms" if ts.max() > 1e12 else "s"
        idx = pd.to_datetime(ts, unit=unit, utc=True)
    else:
        idx = pd.to_datetime(ts, utc=True)
    df = df.set_index(idx)
    return _finalize(df)


def fetch_kraken_ohlc(pair: str, interval_minutes: int = 60,
                      since: Optional[int] = None) -> pd.DataFrame:
    """Laedt OHLC-Daten von der oeffentlichen Kraken-REST-API.

    Hinweis: Kraken liefert pro Aufruf max. ~720 Kerzen. Fuer lange Historien
    mehrfach mit ``since`` (Unix-Sekunden) paginieren oder CSV nutzen.
    ``pair`` z.B. "XBTUSD", "ETHUSD".
    """
    import requests

    url = "https://api.kraken.com/0/public/OHLC"
    params = {"pair": pair, "interval": int(interval_minutes)}
    if since is not None:
        params["since"] = int(since)
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("error"):
        raise RuntimeError(f"Kraken-API-Fehler: {payload['error']}")
    result = payload["result"]
    key = next(k for k in result if k != "last")
    rows = result[key]
    df = pd.DataFrame(
        rows,
        columns=["time", "open", "high", "low", "close", "vwap", "volume", "count"],
    )
    df["time"] = pd.to_datetime(df["time"].astype(float), unit="s", utc=True)
    df = df.set_index("time")
    return _finalize(df)


def generate_synthetic(bars: int = 5000, start: str = "2025-01-01",
                       interval_minutes: int = 60, start_price: float = 40_000.0,
                       annual_drift: float = 0.20, annual_vol: float = 0.70,
                       seed: int = 42) -> pd.DataFrame:
    """Erzeugt realistische synthetische OHLCV-Daten (GBM) fuer Tests/Demos.

    Nutzt eine geometrische Brownsche Bewegung mit Trend + Volatilitaet, sodass
    der Backtester ohne Netzwerk lauffaehig ist.
    """
    rng = np.random.default_rng(seed)
    dt = interval_minutes / (60 * 24 * 365)  # Zeitschritt in Jahren
    mu, sigma = annual_drift, annual_vol
    shocks = rng.normal((mu - 0.5 * sigma**2) * dt, sigma * np.sqrt(dt), size=bars)
    close = start_price * np.exp(np.cumsum(shocks))
    open_ = np.empty(bars)
    open_[0] = start_price
    open_[1:] = close[:-1]
    # Intrabar-Range proportional zur Schrittvolatilitaet
    intrabar = np.abs(rng.normal(0, sigma * np.sqrt(dt), size=bars)) * close
    high = np.maximum(open_, close) + intrabar
    low = np.minimum(open_, close) - intrabar
    low = np.maximum(low, 1e-8)
    volume = rng.uniform(10, 200, size=bars)
    index = pd.date_range(start=start, periods=bars, freq=f"{interval_minutes}min", tz="UTC")
    df = pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=index,
    )
    return _finalize(df)
