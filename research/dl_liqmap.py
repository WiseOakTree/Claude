"""Laedt bookDepth 2023-01..2025-08 und verdichtet direkt zur Liquiditaetskarte.

Die Rohdaten (9 Mio Zeilen je 300 Tage) werden nicht gespeichert -- pro Tag
entsteht sofort die Tageskarte (Preisraster x USD), das ist ~1000x kleiner.
"""
import io, zipfile, urllib.request, time, sys
sys.path.insert(0, "/home/user/Claude/src")
import pandas as pd
from prop_backtester import liquidity

BASE = "https://data.binance.vision/data/futures/um/daily/bookDepth/BTCUSDT/BTCUSDT-bookDepth-{d}.zip"
OUT = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/of/"

px = pd.read_csv(OUT + "flow_5m.csv.gz", index_col=0, parse_dates=True)["close"]

def one(d):
    for a in range(4):
        try:
            req = urllib.request.Request(BASE.format(d=d), headers={"User-Agent": "research/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                z = zipfile.ZipFile(io.BytesIO(r.read()))
            return pd.read_csv(z.open(z.namelist()[0]))
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(2 ** a)
        except Exception:
            time.sleep(2 ** a)
    return None

parts = []
days = pd.date_range("2023-01-01", "2025-08-31", freq="D").strftime("%Y-%m-%d")
for i, d in enumerate(days):
    raw = one(d)
    if raw is None: continue
    lo = pd.Timestamp(d, tz="UTC") - pd.Timedelta(hours=1)
    hi = pd.Timestamp(d, tz="UTC") + pd.Timedelta(days=1, hours=1)
    mid = px.loc[(px.index >= lo) & (px.index <= hi)]
    if len(mid) < 10: continue
    parts.append(liquidity.daily_map(raw, mid))
    if i % 90 == 0:
        print(f"  {d}  ({len(parts)} Tage)", flush=True)

tab = pd.concat(parts, ignore_index=True)
print("Zeilen:", len(tab), "| Tage:", tab['day'].nunique())
tab.to_csv(OUT + "liqmap_search.csv.gz", index=False, compression="gzip")
print("FERTIG")
