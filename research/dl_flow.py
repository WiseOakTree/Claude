"""Laedt 5m-Klines inkl. Taker-Buy-Volumen -> Orderflow-Ungleichgewicht."""
import io, zipfile, urllib.request, time
import pandas as pd

COLS = ["open_time","open","high","low","close","volume","close_time",
        "quote_volume","count","taker_base","taker_quote","ignore"]
BASE = ("https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/5m/"
        "BTCUSDT-5m-{m}.zip")
OUT = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/of/"

def one(m):
    for a in range(4):
        try:
            req = urllib.request.Request(BASE.format(m=m), headers={"User-Agent":"research/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                z = zipfile.ZipFile(io.BytesIO(r.read()))
            df = pd.read_csv(z.open(z.namelist()[0]), header=None, names=COLS)
            if str(df.iloc[0,0]).lower().startswith("open"):   # manche Dateien haben Header
                df = df.iloc[1:]
            return df
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(2**a)
        except Exception:
            time.sleep(2**a)
    return None

months = pd.date_range("2022-01-01", "2026-06-01", freq="MS").strftime("%Y-%m")
fr = []
for i, m in enumerate(months):
    d = one(m)
    if d is not None: fr.append(d)
    if i % 12 == 0: print(f"  {m} ({len(fr)} Monate)", flush=True)
df = pd.concat(fr, ignore_index=True)
for c in ("open","high","low","close","volume","quote_volume","taker_base","count"):
    df[c] = pd.to_numeric(df[c], errors="coerce")
ot = pd.to_numeric(df["open_time"], errors="coerce")
unit = "us" if ot.max() > 1e15 else "ms"
df["time"] = pd.to_datetime(ot, unit=unit, utc=True)
df = df.dropna(subset=["time","close"]).set_index("time").sort_index()
keep = df[["open","high","low","close","volume","quote_volume","taker_base","count"]]
print("Zeilen:", len(keep), keep.index.min(), "->", keep.index.max())
keep.to_csv(OUT + "flow_5m.csv.gz", compression="gzip")
