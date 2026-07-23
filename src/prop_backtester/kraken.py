"""Kraken-Downloader: tiefe Historie ueber den Trades-Endpoint -> OHLC.

Krakens OHLC-Endpoint liefert nur ~720 aktuelle Kerzen. Fuer echte tiefe
Historie nutzt dieses Modul ``/0/public/Trades`` und paginiert ueber den
``last``-Cursor (Nanosekunden), aggregiert die Trades dann zu OHLCV-Bars.

Verwendung (auf einem Rechner mit Kraken-Zugang):

    from prop_backtester import kraken
    df = kraken.download_ohlc("XBTUSD", interval_minutes=60,
                              since="2024-01-01", until="2024-04-01")
    df.to_csv("xbtusd_1h.csv")

Danach mit ``--csv`` in Backtest/Sweep einspeisen.

Der HTTP-Aufruf ist ueber ``request_fn`` injizierbar -- so laesst sich der
Downloader ohne Netzwerk testen.
"""

from __future__ import annotations

import time as _time
from typing import Callable, List, Optional, Tuple

import numpy as np
import pandas as pd

from .data import _finalize

TRADES_URL = "https://api.kraken.com/0/public/Trades"

# Kraken-Trade-Zeile: [price, volume, time, buy/sell, market/limit, misc, trade_id]
_TRADE_COLS = ["price", "volume", "time", "side", "ordertype", "misc", "trade_id"]


class KrakenAPIError(RuntimeError):
    pass


def _to_ns(value) -> int:
    """Normalisiert Start-/Endzeit auf Nanosekunden (Kraken-Cursor-Format)."""
    if value is None:
        return 0
    if isinstance(value, (int, np.integer)):
        v = int(value)
        if v < 10 ** 12:          # Sekunden
            return v * 1_000_000_000
        if v < 10 ** 15:          # Millisekunden
            return v * 1_000_000
        return v                   # bereits Nanosekunden
    if isinstance(value, float):
        return int(value * 1_000_000_000)
    ts = pd.Timestamp(value)       # ISO-String / datetime
    if ts.tz is None:
        ts = ts.tz_localize("UTC")
    return int(ts.value)           # ns seit Epoch


def _default_request(pair: str, since: int, session, timeout: float
                     ) -> Tuple[List[list], str]:
    """Ein Trades-API-Call -> (Liste von Trades, naechster Cursor)."""
    import requests

    sess = session or requests
    resp = sess.get(TRADES_URL, params={"pair": pair, "since": str(since)},
                    timeout=timeout)
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("error"):
        raise KrakenAPIError(str(payload["error"]))
    result = payload["result"]
    key = next(k for k in result if k != "last")
    return result[key], str(result["last"])


def download_trades(pair: str, since=0, until=None, max_trades: Optional[int] = None,
                    sleep_s: float = 1.6, session=None, timeout: float = 30.0,
                    request_fn: Optional[Callable] = None,
                    max_retries: int = 5, progress: bool = True) -> pd.DataFrame:
    """Laedt Trades von Kraken mit Cursor-Pagination.

    ``since``/``until`` akzeptieren Unix-Sekunden, ISO-Strings oder Timestamps.
    Gibt einen DataFrame (DatetimeIndex UTC) mit ``price, volume, side`` zurueck.
    """
    request_fn = request_fn or _default_request
    cursor = _to_ns(since)
    until_ns = _to_ns(until) if until is not None else None

    prices: List[float] = []
    volumes: List[float] = []
    times_ns: List[int] = []
    sides: List[str] = []
    seen_cursors = set()
    calls = 0

    while True:
        # Robust gegen Rate-Limits: exponentielles Backoff bei Fehlern
        for attempt in range(max_retries):
            try:
                trades, last = request_fn(pair, cursor, session, timeout)
                break
            except KrakenAPIError as exc:
                if "Rate limit" in str(exc) and attempt < max_retries - 1:
                    _time.sleep(sleep_s * (2 ** attempt))
                    continue
                raise
        else:  # pragma: no cover
            raise KrakenAPIError("Maximale Wiederholungen erreicht")

        calls += 1
        if not trades:
            break

        for t in trades:
            price = float(t[0]); vol = float(t[1]); ts = float(t[2])
            ts_ns = int(round(ts * 1_000_000_000))
            if until_ns is not None and ts_ns >= until_ns:
                until_reached = True
                break
            prices.append(price); volumes.append(vol); times_ns.append(ts_ns)
            sides.append("buy" if t[3] == "b" else "sell")
        else:
            until_reached = False

        if progress and calls % 10 == 0:
            last_dt = pd.to_datetime(times_ns[-1], unit="ns", utc=True) if times_ns else "-"
            print(f"  ... {len(prices)} Trades geladen (bis {last_dt})")

        if until_reached:
            break
        if max_trades is not None and len(prices) >= max_trades:
            break
        # Cursor-Fortschritt pruefen (Schutz gegen Endlosschleife)
        if last in seen_cursors or last == str(cursor):
            break
        seen_cursors.add(last)
        cursor = int(last)
        if sleep_s > 0:
            _time.sleep(sleep_s)

    if max_trades is not None and len(prices) > max_trades:
        prices = prices[:max_trades]; volumes = volumes[:max_trades]
        times_ns = times_ns[:max_trades]; sides = sides[:max_trades]

    idx = pd.to_datetime(times_ns, unit="ns", utc=True)
    df = pd.DataFrame({"price": prices, "volume": volumes, "side": sides}, index=idx)
    df.index.name = "time"
    return df.sort_index()


def trades_to_ohlc(trades: pd.DataFrame, interval_minutes: int = 60) -> pd.DataFrame:
    """Aggregiert einen Trades-DataFrame zu OHLCV-Bars."""
    if len(trades) == 0:
        raise ValueError("Keine Trades zum Aggregieren")
    rule = f"{interval_minutes}min"
    price = trades["price"]
    ohlc = price.resample(rule).ohlc()
    volume = trades["volume"].resample(rule).sum().rename("volume")
    df = ohlc.join(volume)
    df = df.dropna(subset=["open", "high", "low", "close"])
    return _finalize(df)


def download_ohlc(pair: str, interval_minutes: int = 60, since=0, until=None,
                  **kwargs) -> pd.DataFrame:
    """Bequemlichkeit: Trades laden und direkt zu OHLC aggregieren."""
    trades = download_trades(pair, since=since, until=until, **kwargs)
    if len(trades) == 0:
        raise KrakenAPIError("Keine Trades erhalten -- Pair/Zeitraum pruefen")
    return trades_to_ohlc(trades, interval_minutes=interval_minutes)
