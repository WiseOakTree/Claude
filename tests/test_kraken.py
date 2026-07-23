import numpy as np
import pandas as pd

from prop_backtester import kraken


def _make_fake(all_trades, page=1000):
    """Fake-Request-Fn: liefert Trades nach dem Cursor, seitenweise."""
    def fn(pair, since, session, timeout):
        since_s = since / 1e9
        nxt = [t for t in all_trades if t[2] > since_s][:page]
        if not nxt:
            return [], str(since)
        last_ns = int(round(nxt[-1][2] * 1e9))
        return nxt, str(last_ns)
    return fn


def _trade(price, vol, ts, side="b"):
    return [str(price), str(vol), float(ts), side, "l", "", 0]


def test_to_ns_variants():
    assert kraken._to_ns(0) == 0
    assert kraken._to_ns(1_600_000_000) == 1_600_000_000 * 10**9      # Sekunden
    assert kraken._to_ns(1_600_000_000_000) == 1_600_000_000_000 * 10**6  # ms
    ns = kraken._to_ns("2024-01-01")
    assert ns == int(pd.Timestamp("2024-01-01", tz="UTC").value)


def test_download_trades_paginates_all():
    base = 1_700_000_000.0
    trades = [_trade(100 + i, 1.0, base + i) for i in range(2500)]
    fn = _make_fake(trades, page=1000)
    df = kraken.download_trades("XBTUSD", since=0, sleep_s=0, progress=False,
                                request_fn=fn)
    assert len(df) == 2500
    assert df.index.is_monotonic_increasing
    assert df["price"].iloc[0] == 100
    assert df["price"].iloc[-1] == 100 + 2499


def test_download_until_stops_early():
    base = 1_700_000_000.0
    trades = [_trade(100 + i, 1.0, base + i) for i in range(1000)]
    fn = _make_fake(trades, page=1000)
    until = pd.to_datetime(base + 500, unit="s", utc=True)
    df = kraken.download_trades("XBTUSD", since=0, until=until, sleep_s=0,
                                progress=False, request_fn=fn)
    assert len(df) == 500  # nur Trades vor "until"


def test_max_trades_cap():
    base = 1_700_000_000.0
    trades = [_trade(100 + i, 1.0, base + i) for i in range(3000)]
    fn = _make_fake(trades, page=1000)
    df = kraken.download_trades("XBTUSD", since=0, max_trades=1500, sleep_s=0,
                                progress=False, request_fn=fn)
    assert len(df) == 1500


def test_trades_to_ohlc_aggregation():
    # Zwei Stunden mit bekannten Preisen -> pruefbare OHLC-Bars
    h0 = pd.Timestamp("2024-01-01T00:00:00Z").timestamp()
    h1 = pd.Timestamp("2024-01-01T01:00:00Z").timestamp()
    trades = [
        _trade(100, 1.0, h0 + 1),    # open h0
        _trade(110, 2.0, h0 + 100),  # high h0
        _trade(90, 1.0, h0 + 200),   # low h0
        _trade(105, 1.0, h0 + 3500), # close h0
        _trade(105, 1.0, h1 + 1),    # open h1
        _trade(107, 1.0, h1 + 10),   # close h1
    ]
    df = pd.DataFrame(
        {"price": [float(t[0]) for t in trades],
         "volume": [float(t[1]) for t in trades],
         "side": ["buy"] * len(trades)},
        index=pd.to_datetime([t[2] for t in trades], unit="s", utc=True),
    )
    ohlc = kraken.trades_to_ohlc(df, interval_minutes=60)
    assert len(ohlc) == 2
    b0 = ohlc.iloc[0]
    assert b0["open"] == 100 and b0["high"] == 110 and b0["low"] == 90 and b0["close"] == 105
    assert b0["volume"] == 5.0
    b1 = ohlc.iloc[1]
    assert b1["open"] == 105 and b1["close"] == 107


def test_download_ohlc_end_to_end_offline():
    base = pd.Timestamp("2024-01-01T00:00:00Z").timestamp()
    # 3 Stunden à 60 Trades, leicht schwankend
    trades = []
    for i in range(180):
        trades.append(_trade(100 + (i % 10), 0.5, base + i * 60))
    fn = _make_fake(trades, page=1000)
    ohlc = kraken.download_ohlc("XBTUSD", interval_minutes=60, since=0, sleep_s=0,
                                progress=False, request_fn=fn)
    assert list(ohlc.columns) == ["open", "high", "low", "close", "volume"]
    assert len(ohlc) == 3
    assert (ohlc["high"] >= ohlc["low"]).all()
