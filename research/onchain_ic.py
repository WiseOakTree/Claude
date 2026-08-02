"""On-Chain-Signale: Vorhersagekraft mit Ueberlappungskorrektur.

Die Lehre aus der Orderbuch-Analyse: Bei langen Horizonten schrumpft die Zahl
UNABHAENGIGER Fenster. n_eff wird hier immer mitgefuehrt.
"""
import json, urllib.request
import numpy as np, pandas as pd
from scipy import stats

OUT = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/oc/"
df = pd.read_csv(OUT + "onchain.csv", index_col=0, parse_dates=True)

with urllib.request.urlopen(urllib.request.Request(
        "https://api.blockchain.info/charts/market-price?timespan=all&format=json",
        headers={"User-Agent": "research/1.0"}), timeout=90) as r:
    d = json.loads(r.read())
px = pd.Series({pd.to_datetime(p["x"], unit="s", utc=True).normalize(): p["y"]
                for p in d["values"]}).sort_index()
px = px[px > 0]
df["px"] = px
# Marktkapitalisierung als Preis-Ersatz fuellen, wo blockchain.com Luecken hat
df["px"] = df["px"].where(df["px"].notna(), df["CapMrktCurUSD"] / 19.7e6)
df = df[df["px"].notna()].copy()

# --- klassische On-Chain-Indikatoren ---
df["mvrv"] = df["CapMVRVCur"]
df["mvrv_z"] = (df["mvrv"] - df["mvrv"].rolling(365).mean()) / df["mvrv"].rolling(365).std()
df["puell"] = df["IssTotUSD"] / df["IssTotUSD"].rolling(365).mean()      # Miner-Einnahmen
hr30 = df["HashRate"].rolling(30).mean(); hr60 = df["HashRate"].rolling(60).mean()
df["hash_ribbon"] = hr30 / hr60 - 1                                      # Miner-Kapitulation
df["nvt"] = df["CapMrktCurUSD"] / df["estimated-transaction-volume-usd"].rolling(28).mean()
df["nvt_z"] = -(df["nvt"] - df["nvt"].rolling(365).mean()) / df["nvt"].rolling(365).std()
df["adr_mom"] = df["AdrActCnt"].rolling(30).mean() / df["AdrActCnt"].rolling(180).mean() - 1
df["tx_mom"] = df["TxCnt"].rolling(30).mean() / df["TxCnt"].rolling(180).mean() - 1
# MVRV invertiert: niedrig = guenstig = Kaufsignal
df["mvrv_inv"] = -df["mvrv_z"]

SIGS = {"MVRV (invertiert)": "mvrv_inv", "MVRV Niveau (inv.)": None,
        "Puell (invertiert)": None, "Hash Ribbon": "hash_ribbon",
        "NVT (invertiert)": "nvt_z", "Adressen-Momentum": "adr_mom",
        "Transaktions-Momentum": "tx_mom"}
df["mvrv_lvl_inv"] = -df["mvrv"]
df["puell_inv"] = -df["puell"]
SIGS = {"MVRV z (invertiert)": "mvrv_inv", "MVRV Niveau (inv.)": "mvrv_lvl_inv",
        "Puell (invertiert)": "puell_inv", "Hash Ribbon": "hash_ribbon",
        "NVT (invertiert)": "nvt_z", "Adressen-Momentum": "adr_mom",
        "Transaktions-Momentum": "tx_mom"}

def cp(ic, n):
    t = ic * np.sqrt(max(n - 2, 1) / max(1 - ic ** 2, 1e-9))
    return 2 * (1 - stats.t.cdf(abs(t), max(n - 2, 1)))

print("=" * 96)
print(f"On-Chain-Signale gegen Folgerenditen   n = {len(df):,} Tage "
      f"({df.index.min().date()} .. {df.index.max().date()})")
print("=" * 96)
print(f"{'Signal':24s} {'Horiz.':>7s} {'IC':>7s} {'p naiv':>9s} {'p korr.':>9s} "
      f"{'n_eff':>6s} {'Q5-Q1':>9s}")
print("-" * 96)
hold = []
for nm, key in SIGS.items():
    for h in (30, 90, 180, 365):
        fwd = df["px"].pct_change(h).shift(-h)
        s = pd.concat([df[key].rename("s"), fwd.rename("f")], axis=1).dropna()
        s = s.replace([np.inf, -np.inf], np.nan).dropna()
        if len(s) < 400: continue
        ic, p = stats.spearmanr(s["s"], s["f"])
        n_eff = len(s) / h
        pa = cp(ic, n_eff)
        q = pd.qcut(s["s"], 5, labels=False, duplicates="drop")
        sp = (s["f"][q == 4].mean() - s["f"][q == 0].mean()) * 100
        mark = "  <<<" if pa < 0.05 else ""
        print(f"{nm:24s} {h:5d} T {ic:+7.3f} {p:9.1e} {pa:9.3f} {n_eff:6.0f} "
              f"{sp:+7.1f} %{mark}")
        if pa < 0.05: hold.append((nm, key, h, ic, pa, sp))

print(f"\nSignifikant nach Ueberlappungskorrektur: {len(hold)} von "
      f"{len(SIGS)*4} Kombinationen")
df.to_csv(OUT + "onchain_feat.csv")
