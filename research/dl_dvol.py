"""Laedt DVOL (Deribit Volatility Index) Historie -- gechunkt, da die API limitiert."""
import json, time, urllib.request, datetime as dt
import pandas as pd

URL = ("https://www.deribit.com/api/v2/public/get_volatility_index_data"
       "?currency={cur}&start_timestamp={a}&end_timestamp={b}&resolution=43200")

def fetch(cur, a, b):
    req = urllib.request.Request(URL.format(cur=cur, a=a, b=b),
                                 headers={"User-Agent": "research/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["result"]["data"]

def history(cur, start="2021-01-01"):
    t0 = int(pd.Timestamp(start, tz="UTC").timestamp() * 1000)
    t1 = int(pd.Timestamp.utcnow().timestamp() * 1000)
    rows, cur_t = [], t0
    step = 90 * 86400 * 1000
    while cur_t < t1:
        end = min(cur_t + step, t1)
        for attempt in range(4):
            try:
                d = fetch(cur, cur_t, end)
                break
            except Exception as e:
                if attempt == 3:
                    print("  fail", e); d = []
                time.sleep(2 ** attempt)
        rows.extend(d)
        cur_t = end + 1
        time.sleep(0.25)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close"])
    df["time"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    df = df.drop_duplicates("ts").set_index("time").sort_index()
    return df[["open", "high", "low", "close"]]

for cur in ("BTC", "ETH"):
    h = history(cur)
    print(cur, len(h), h.index.min(), "->", h.index.max())
    h.to_csv(f"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/dvol_{cur}.csv")
