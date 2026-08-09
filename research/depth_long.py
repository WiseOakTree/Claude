"""Orderbuch-Imbalance auf LANGEN Horizonten -- mit Ueberlappungskorrektur.

Der offene Faden: Der Effekt wuchs monoton mit dem Horizont. Hier bis 7 Tage
verlaengert. Entscheidend ist die Korrektur fuer ueberlappende Fenster -- genau
daran ist der DVOL-z-Score gescheitert.
"""
import numpy as np, pandas as pd
from scipy import stats

OUT = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/of/"
d = pd.read_csv(OUT + "bookdepth.csv.gz")
d["timestamp"] = pd.to_datetime(d["timestamp"], utc=True, format="mixed")
piv = d.pivot_table(index="timestamp", columns="percentage", values="notional", aggfunc="sum")
lv = sorted(piv.columns); neg = [c for c in lv if c < 0]; pos = [c for c in lv if c > 0]
feat = pd.DataFrame(index=piv.index)
for tag, ns in (("1", 1), ("3", 3), ("5", 5)):
    b = piv[[c for c in neg if abs(c) <= ns]].sum(axis=1)
    a = piv[[c for c in pos if abs(c) <= ns]].sum(axis=1)
    feat[f"imb{tag}"] = (b - a) / (b + a)
feat = feat.replace([np.inf, -np.inf], np.nan).dropna()

px = pd.read_csv(OUT + "flow_5m.csv.gz", index_col=0, parse_dates=True)["close"]
m = pd.concat([feat.resample("5min").last(), px.rename("px")], axis=1, sort=True).dropna()
BARS_PER_DAY = 288

print("=" * 88)
print(f"Orderbuch-Imbalance, lange Horizonte   n = {len(m):,} 5-Min-Punkte, "
      f"{len(m)/BARS_PER_DAY:.0f} Tage")
print("=" * 88)
print(f"{'Signal':16s} {'Horizont':>9s} {'IC':>7s} {'p naiv':>9s} {'p korr.':>8s} "
      f"{'Q5-Q1':>10s} {'vs 16bp':>8s} {'n_eff':>6s}")
print("-" * 88)
res = []
for key in ("imb1", "imb3", "imb5"):
    for bars, lbl in ((48, "4 h"), (96, "8 h"), (288, "1 T"), (576, "2 T"),
                      (864, "3 T"), (1440, "5 T"), (2016, "7 T")):
        fwd = m["px"].pct_change(bars).shift(-bars)
        s = pd.concat([m[key].rename("s"), fwd.rename("f")], axis=1).dropna()
        if len(s) < 2000: continue
        ic, p = stats.spearmanr(s["s"], s["f"])
        n_eff = len(s) / bars                       # unabhaengige, nicht ueberlappende Fenster
        if n_eff < 10: continue
        t = ic * np.sqrt(max(n_eff - 2, 1) / max(1 - ic ** 2, 1e-9))
        p_adj = 2 * (1 - stats.t.cdf(abs(t), max(n_eff - 2, 1)))
        q = pd.qcut(s["s"], 5, labels=False, duplicates="drop")
        spread = (s["f"][q == 4].mean() - s["f"][q == 0].mean()) * 1e4
        mark = " <<<" if abs(spread) > 16 and p_adj < 0.05 else ""
        print(f"{key:16s} {lbl:>9s} {ic:+7.3f} {p:9.1e} {p_adj:8.3f} "
              f"{spread:+7.1f} bp {abs(spread)/16:7.2f}x {n_eff:6.0f}{mark}")
        res.append((key, lbl, bars, ic, p_adj, spread))

print("\n" + "=" * 88)
print("Kontrolle: ist das nur BTC-Beta? (Imbalance gegen gleichzeitige Rendite)")
print("=" * 88)
for key in ("imb3", "imb5"):
    for bars, lbl in ((288, "1 T"), (864, "3 T")):
        past = m["px"].pct_change(bars)          # VERGANGENE Rendite
        s = pd.concat([m[key].rename("s"), past.rename("p")], axis=1).dropna()
        ic, _ = stats.spearmanr(s["s"], s["p"])
        print(f"  {key}, {lbl}: Korrelation mit der VERGANGENEN Rendite {ic:+.3f}"
              f"   ({'Trendfolge-Artefakt' if abs(ic) > 0.3 else 'unabhaengig'})")
