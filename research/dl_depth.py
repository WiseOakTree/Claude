"""Laedt Binance-Futures bookDepth (Orderbuch-Tiefe, 60s-Snapshots)."""
import io, zipfile, urllib.request, time
import pandas as pd

BASE = "https://data.binance.vision/data/futures/um/daily/bookDepth/BTCUSDT/BTCUSDT-bookDepth-{d}.zip"
OUT = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/of/"

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

days = pd.date_range("2025-09-01", "2026-06-30", freq="D").strftime("%Y-%m-%d")
frames = []
for i, d in enumerate(days):
    df = one(d)
    if df is not None:
        frames.append(df)
    if i % 40 == 0:
        print(f"  {d}  ({len(frames)} Tage geladen)", flush=True)
all_ = pd.concat(frames, ignore_index=True)
print("Zeilen:", len(all_), "| Spalten:", list(all_.columns))
all_.to_csv(OUT + "bookdepth.csv.gz", index=False, compression="gzip")
