"""Laedt On-Chain-Kennzahlen: CoinMetrics Community + Blockchain.com Charts."""
import json, time, urllib.request
import pandas as pd

OUT = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/oc/"
UA = {"User-Agent": "research/1.0"}

def get(url):
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return json.loads(r.read())
        except Exception as e:
            if a == 3: raise
            time.sleep(2 ** a)

# --- CoinMetrics (paginiert) ---
METRICS = "CapMVRVCur,CapMrktCurUSD,AdrActCnt,TxCnt,HashRate,IssTotUSD,FeeTotNtv"
rows, nxt = [], None
base = ("https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
        f"?assets=btc&metrics={METRICS}&start_time=2013-01-01&frequency=1d&page_size=10000")
url = base
while True:
    d = get(url)
    rows.extend(d.get("data", []))
    nxt = d.get("next_page_url")
    if not nxt: break
    url = nxt
cm = pd.DataFrame(rows)
cm["time"] = pd.to_datetime(cm["time"], utc=True).dt.normalize()
for c in cm.columns:
    if c not in ("asset", "time"): cm[c] = pd.to_numeric(cm[c], errors="coerce")
cm = cm.set_index("time").drop(columns=["asset"]).sort_index()
print("CoinMetrics:", len(cm), cm.index.min().date(), "->", cm.index.max().date())

# --- Blockchain.com: Transaktionsvolumen in USD (fuer NVT) ---
bc = {}
for chart in ("estimated-transaction-volume-usd", "n-unique-addresses", "miners-revenue"):
    d = get(f"https://api.blockchain.info/charts/{chart}?timespan=all&format=json")
    s = pd.Series({pd.to_datetime(p["x"], unit="s", utc=True).normalize(): p["y"]
                   for p in d["values"]})
    bc[chart] = s
    print(f"  {chart}: {len(s)} Punkte")
bc = pd.DataFrame(bc).sort_index()

df = cm.join(bc, how="outer")
df.to_csv(OUT + "onchain.csv")
print("\nGesamt:", len(df), "Zeilen |", list(df.columns))
print(df.tail(3).to_string())
