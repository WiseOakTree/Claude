"""Haerteprüfung des DVOL-z-Score-Signals ('Angst kaufen')."""
import numpy as np, pandas as pd
from scipy import stats

D = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
px = pd.read_csv(D + "btc_1h.csv", index_col=0, parse_dates=True)["close"].resample("1D").last().dropna()
iv = pd.read_csv(D + "dvol_BTC.csv", index_col=0, parse_dates=True)["close"].resample("1D").last().dropna()
df = pd.DataFrame({"px": px, "iv": iv}).dropna()
df["ret"] = df["px"].pct_change()
df["z"] = (df["iv"] - df["iv"].rolling(90).mean()) / df["iv"].rolling(90).std()
df = df.dropna()
H = 20
df["fwd"] = df["px"].pct_change(H).shift(-H)
m = df.dropna()

ic, p = stats.spearmanr(m["z"], m["fwd"])
n_eff = len(m) / H
t = ic * np.sqrt(max(n_eff - 2, 1) / max(1 - ic**2, 1e-9))
p_adj = 2 * (1 - stats.t.cdf(abs(t), n_eff - 2))
print("=" * 72)
print(f"1) Signifikanz mit Ueberlappungskorrektur   (n={len(m)}, n_eff={n_eff:.0f})")
print("=" * 72)
print(f"   IC {ic:+.3f}   naiv p={p:.2e}   ueberlappungskorrigiert p={p_adj:.4f}"
      + ("   -> haelt" if p_adj < 0.05 else "   -> faellt"))

print("\n" + "=" * 72)
print("2) Quintile: ist der Zusammenhang monoton?")
print("=" * 72)
m = m.copy(); m["q"] = pd.qcut(m["z"], 5, labels=False)
g = m.groupby("q")["fwd"].agg(["median", "mean", "count"])
for q in range(5):
    print(f"   Q{q+1} (z {'niedrig' if q==0 else 'hoch' if q==4 else '     '}) "
          f" Median {g.loc[q,'median']*100:+7.2f}%   Mittel {g.loc[q,'mean']*100:+7.2f}%   n={g.loc[q,'count']}")
print(f"   Spread Q5-Q1 (Mittel): {(g.loc[4,'mean']-g.loc[0,'mean'])*100:+.2f} %")

print("\n" + "=" * 72)
print("3) Out-of-Sample: erste vs. zweite Haelfte")
print("=" * 72)
half = len(m) // 2
for nm, s in (("1. Haelfte", m.iloc[:half]), ("2. Haelfte", m.iloc[half:])):
    i2, p2 = stats.spearmanr(s["z"], s["fwd"])
    ne = len(s) / H
    tt = i2 * np.sqrt(max(ne - 2, 1) / max(1 - i2**2, 1e-9))
    pa = 2 * (1 - stats.t.cdf(abs(tt), ne - 2))
    print(f"   {nm} ({s.index.min().date()}..{s.index.max().date()}): "
          f"IC {i2:+.3f}   korrigiert p={pa:.3f}" + ("  signifikant" if pa < 0.05 else "  nicht signifikant"))

print("\n" + "=" * 72)
print("4) Als Strategie gehandelt (long bei z > Schwelle, 16 bp Kosten)")
print("=" * 72)
COST = 16e-4
def challenge(r, win=90):
    r = r.dropna().to_numpy(); passed = tot = 0; R=[]; DD=[]
    for s in range(0, len(r) - win):
        w = r[s:s+win]; eq = np.cumprod(1+w)
        dd = (eq/np.maximum.accumulate(eq)-1).min()
        passed += (eq[-1]-1 >= .10 and dd >= -.06 and w.min() > -.03); tot += 1
        R.append(eq[-1]-1); DD.append(-dd)
    return passed/tot*100, np.median(R)*100, np.median(DD)*100
print(f"{'Variante':40s} {'Rendite':>9s} {'DD':>7s} {'Pass':>7s}")
print("-" * 72)
for thr in (-0.5, 0.0, 0.5, 1.0):
    for lev, tag in ((1.0, "1x"), (2.0, "2x")):
        w = (df["z"].shift(1) > thr).astype(float) * lev
        turn = w.diff().abs().fillna(w.abs())
        r = w * df["ret"] - COST * turn
        p_, rr, dd = challenge(r)
        print(f"{f'long wenn z > {thr:+.1f}  ({tag})':40s} {rr:+8.1f}% {dd:6.1f}% {p_:6.1f}%")
