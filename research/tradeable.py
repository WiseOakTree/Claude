"""Was von der Vol-Praemie im Kraken-Prop-Konto uebrig bleibt (nur Spot/Futures)."""
import numpy as np, pandas as pd
from scipy import stats

D = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
px = pd.read_csv(D + "btc_1h.csv", index_col=0, parse_dates=True)["close"].resample("1D").last().dropna()
iv = pd.read_csv(D + "dvol_BTC.csv", index_col=0, parse_dates=True)["close"].resample("1D").last().dropna()
df = pd.DataFrame({"px": px, "iv": iv}).dropna()
df["ret"] = df["px"].pct_change()
df["trail"] = np.log(df["px"]).diff().rolling(30).std() * np.sqrt(365) * 100
df["vrp"] = df["iv"] - df["trail"]
df = df.dropna()

COST = 16e-4  # 16 bp je Roundtrip, proportional zum Umsatz

def challenge(eq_ret, win=90):
    """Pass-Rate ueber rollierende Fenster: +10 % Ziel, 6 % DD, 3 % Tagesverlust."""
    r = eq_ret.dropna().to_numpy()
    n, passed, tot, rets, dds = len(r), 0, 0, [], []
    for s in range(0, n - win):
        w = r[s:s + win]
        eq = np.cumprod(1 + w)
        dd = (eq / np.maximum.accumulate(eq) - 1).min()
        ok = eq[-1] - 1 >= 0.10 and dd >= -0.06 and w.min() > -0.03
        passed += ok; tot += 1
        rets.append(eq[-1] - 1); dds.append(-dd)
    return passed / tot * 100, np.median(rets) * 100, np.median(dds) * 100, tot

def vol_target(vol_est, target=20.0, cap=2.0):
    """Positionsgroesse = Zielvola / geschaetzte Vola, taeglich, look-ahead-frei."""
    w = (target / vol_est.shift(1)).clip(upper=cap).fillna(0)
    turn = w.diff().abs().fillna(w.abs())
    return w * df["ret"] - COST * turn

print("=" * 78)
print("A) Richtungs-Vorhersagekraft der Vol-Signale (Spearman-IC, look-ahead-frei)")
print("=" * 78)
print(f"{'Signal':26s} {'Horizont':>9s} {'IC':>8s} {'p':>8s}")
print("-" * 78)
for nm, sig in (("DVOL (Niveau)", df["iv"]),
                ("DVOL z-Score 90T", (df["iv"] - df["iv"].rolling(90).mean()) / df["iv"].rolling(90).std()),
                ("VRP = IV - trailing RV", df["vrp"]),
                ("DVOL-Aenderung 5T", df["iv"].diff(5))):
    for h in (5, 20):
        fwd = df["px"].pct_change(h).shift(-h)
        m = pd.concat([sig, fwd], axis=1).dropna()
        ic, p = stats.spearmanr(m.iloc[:, 0], m.iloc[:, 1])
        flag = "  <-- signifikant" if p < 0.01 else ""
        print(f"{nm:26s} {h:6d} T {ic:+8.3f} {p:8.3f}{flag}")

print()
print("=" * 78)
print("B) Vol-Targeting: implizite (DVOL) statt realisierter Vol als Schaetzer")
print("=" * 78)
print(f"{'Variante':34s} {'Rendite':>9s} {'DD':>7s} {'Pass':>7s}  n")
print("-" * 78)
bh = df["ret"].copy()
p, r, d, n = challenge(bh); print(f"{'BTC einfach halten':34s} {r:+8.1f}% {d:6.1f}% {p:6.1f}% {n:4d}")
for tgt in (15, 20, 25):
    for nm, est in (("trailing RV", df["trail"]), ("DVOL implizit", df["iv"])):
        s = vol_target(est, target=tgt)
        p, r, d, n = challenge(s)
        print(f"{f'Vol-Target {tgt}% / {nm}':34s} {r:+8.1f}% {d:6.1f}% {p:6.1f}% {n:4d}")
