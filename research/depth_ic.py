"""Orderbuch-Ungleichgewicht (echte Tiefendaten) gegen kuenftige Renditen."""
import numpy as np, pandas as pd
from scipy import stats

OUT = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/of/"
d = pd.read_csv(OUT + "bookdepth.csv.gz")
d["timestamp"] = pd.to_datetime(d["timestamp"], utc=True, format="mixed")
print("Ebenen (% vom Mittelkurs):", sorted(d["percentage"].unique()))

# negative percentage = Bid-Seite, positive = Ask-Seite
piv = d.pivot_table(index="timestamp", columns="percentage", values="notional",
                    aggfunc="sum")
lv = sorted(piv.columns)
neg = [c for c in lv if c < 0]; pos = [c for c in lv if c > 0]

feat = pd.DataFrame(index=piv.index)
for tag, ns in (("1", 1), ("3", 3), ("5", 5)):
    b = piv[[c for c in neg if abs(c) <= ns]].sum(axis=1)
    a = piv[[c for c in pos if abs(c) <= ns]].sum(axis=1)
    feat[f"imb{tag}"] = (b - a) / (b + a)
    feat[f"liq{tag}"] = b + a
feat = feat.replace([np.inf, -np.inf], np.nan).dropna()

px = pd.read_csv(OUT + "flow_5m.csv.gz", index_col=0, parse_dates=True)["close"]
f5 = feat.resample("5min").last().dropna()
m = pd.concat([f5, px.rename("px")], axis=1).dropna()
m["liq3_z"] = (m["liq3"] - m["liq3"].rolling(288).mean()) / m["liq3"].rolling(288).std()

print(f"\n{'='*84}")
print(f"Orderbuch-Ungleichgewicht   n = {len(m):,} 5-Min-Punkte "
      f"({m.index.min().date()} .. {m.index.max().date()}, {len(feat)//1440} Tage)")
print("=" * 84)
print(f"{'Signal':28s} {'Horizont':>9s} {'IC':>8s} {'p':>10s} {'Q5-Q1':>11s} {'vs 16bp':>9s}")
print("-" * 84)
for nm, key in (("Imbalance +/-1 %", "imb1"), ("Imbalance +/-3 %", "imb3"),
                ("Imbalance +/-5 %", "imb5"), ("Liquiditaet z (3 %)", "liq3_z")):
    for bars, lbl in ((1, "5 min"), (3, "15 min"), (12, "1 h"), (48, "4 h")):
        fwd = m["px"].pct_change(bars).shift(-bars)
        s = pd.concat([m[key].rename("s"), fwd.rename("f")], axis=1).dropna()
        if len(s) < 500: continue
        ic, p = stats.spearmanr(s["s"], s["f"])
        q = pd.qcut(s["s"], 5, labels=False, duplicates="drop")
        spread = (s["f"][q == 4].mean() - s["f"][q == 0].mean()) * 1e4
        print(f"{nm:28s} {lbl:>9s} {ic:+8.3f} {p:10.2e} {spread:+8.2f} bp "
              f"{('handelbar' if abs(spread) > 16 else f'{abs(spread)/16:.2f}x'):>9s}")

print(f"\n{'='*84}\nOut-of-Sample-Kontrolle des staerksten Signals\n{'='*84}")
best_key, best_bars = None, None; best_ic = 0
for key in ("imb1", "imb3", "imb5"):
    for bars in (1, 3, 12, 48):
        fwd = m["px"].pct_change(bars).shift(-bars)
        s = pd.concat([m[key].rename("s"), fwd.rename("f")], axis=1).dropna()
        ic, _ = stats.spearmanr(s["s"], s["f"])
        if abs(ic) > abs(best_ic): best_ic, best_key, best_bars = ic, key, bars
print(f"  Staerkstes: {best_key}, {best_bars*5} min, IC {best_ic:+.3f}")
fwd = m["px"].pct_change(best_bars).shift(-best_bars)
s = pd.concat([m[best_key].rename("s"), fwd.rename("f")], axis=1).dropna()
h = len(s) // 2
for nm, part in (("1. Haelfte", s.iloc[:h]), ("2. Haelfte", s.iloc[h:])):
    ic, p = stats.spearmanr(part["s"], part["f"])
    print(f"  {nm}: IC {ic:+.3f} (p={p:.1e})")
