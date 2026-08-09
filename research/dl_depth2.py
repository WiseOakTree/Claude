"""Laedt die fehlende bookDepth-Historie 2023-01 bis 2025-08."""
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

# direkt zu 5-Min-Features verdichten -- spart Speicher gegenueber 9 Mio. Rohzeilen
feats = []
days = pd.date_range("2023-01-01", "2025-08-31", freq="D").strftime("%Y-%m-%d")
for i, d in enumerate(days):
    df = one(d)
    if df is None: continue
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, format="mixed")
    piv = df.pivot_table(index="timestamp", columns="percentage", values="notional", aggfunc="sum")
    lv = sorted(piv.columns); neg = [c for c in lv if c < 0]; pos = [c for c in lv if c > 0]
    f = pd.DataFrame(index=piv.index)
    for tag, ns in (("1", 1), ("3", 3), ("5", 5)):
        b = piv[[c for c in neg if abs(c) <= ns]].sum(axis=1)
        a_ = piv[[c for c in pos if abs(c) <= ns]].sum(axis=1)
        f[f"imb{tag}"] = (b - a_) / (b + a_)
    f[f"liq"] = piv.sum(axis=1)
    feats.append(f.resample("5min").last())
    if i % 100 == 0: print(f"  {d} ({len(feats)} Tage)", flush=True)

all_ = pd.concat(feats).sort_index()
print("Punkte:", len(all_), all_.index.min(), "->", all_.index.max())
all_.to_csv(OUT + "depth_feat_hist.csv.gz", compression="gzip")
print("FERTIG")
