"""Open Interest + Positionierungs-Ratios, 2023-01..2026-06, auf 1h verdichtet."""
import io, zipfile, urllib.request, time
import pandas as pd
BASE=("https://data.binance.vision/data/futures/um/daily/metrics/{s}/{s}-metrics-{d}.zip")
OUT="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/oc/"

def one(sym,d):
    for a in range(4):
        try:
            r=urllib.request.Request(BASE.format(s=sym,d=d),headers={"User-Agent":"research/1.0"})
            with urllib.request.urlopen(r,timeout=90) as f:
                z=zipfile.ZipFile(io.BytesIO(f.read()))
            return pd.read_csv(z.open(z.namelist()[0]))
        except urllib.error.HTTPError as e:
            if e.code==404: return None
            time.sleep(2**a)
        except Exception: time.sleep(2**a)
    return None

for sym in ("BTCUSDT","ETHUSDT"):
    parts=[]
    days=pd.date_range("2023-01-01","2026-06-30",freq="D").strftime("%Y-%m-%d")
    for i,d in enumerate(days):
        raw=one(sym,d)
        if raw is None: continue
        raw["t"]=pd.to_datetime(raw["create_time"],utc=True)
        g=raw.set_index("t").resample("1h").agg({
            "sum_open_interest":"last","sum_open_interest_value":"last",
            "count_toptrader_long_short_ratio":"mean",
            "sum_toptrader_long_short_ratio":"mean",
            "count_long_short_ratio":"mean",
            "sum_taker_long_short_vol_ratio":"mean"}).dropna(how="all")
        parts.append(g)
        if i%180==0: print(f"  {sym} {d} ({len(parts)} Tage)",flush=True)
    tab=pd.concat(parts).sort_index()
    tab=tab[~tab.index.duplicated(keep="last")]
    tab.to_csv(OUT+f"oi_{sym[:-4].lower()}.csv")
    print(f"{sym}: {len(tab)} Stunden, {tab.index.min()} .. {tab.index.max()}",flush=True)
print("FERTIG")
