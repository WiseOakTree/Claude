"""Bringt das Orderbuch Information, die im Preis nicht schon steckt?

Die Imbalance korreliert -0,48 mit der vergangenen Rendite. Also: Ist sie mehr
als ein umetikettiertes 'Buy the Dip'?
"""
import numpy as np, pandas as pd
from scipy import stats

OUT = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/of/"
d = pd.read_csv(OUT + "bookdepth.csv.gz")
d["timestamp"] = pd.to_datetime(d["timestamp"], utc=True, format="mixed")
piv = d.pivot_table(index="timestamp", columns="percentage", values="notional", aggfunc="sum")
lv = sorted(piv.columns); neg=[c for c in lv if c<0]; pos=[c for c in lv if c>0]
f = pd.DataFrame(index=piv.index)
for tag, ns in (("3",3),("5",5)):
    b = piv[[c for c in neg if abs(c)<=ns]].sum(axis=1)
    a = piv[[c for c in pos if abs(c)<=ns]].sum(axis=1)
    f[f"imb{tag}"] = (b-a)/(b+a)
f = f.replace([np.inf,-np.inf], np.nan).dropna()
px = pd.read_csv(OUT+"flow_5m.csv.gz", index_col=0, parse_dates=True)["close"]
m = pd.concat([f.resample("5min").last(), px.rename("px")], axis=1, sort=True).dropna()

H = 864   # 3 Tage
m["fwd"] = m["px"].pct_change(H).shift(-H)
m["past"] = m["px"].pct_change(H)
m = m.dropna()

print("=" * 80)
print("A) Reine Preis-Mean-Reversion als Vergleichsmassstab (3-Tage-Horizont)")
print("=" * 80)
ic_p, _ = stats.spearmanr(-m["past"], m["fwd"])
q = pd.qcut(-m["past"], 5, labels=False, duplicates="drop")
sp_p = (m["fwd"][q==4].mean() - m["fwd"][q==0].mean())*1e4
print(f"  Nur Preis (negative Vergangenheitsrendite): IC {ic_p:+.3f}, Q5-Q1 {sp_p:+.1f} bp")
for key in ("imb3","imb5"):
    ic_i,_ = stats.spearmanr(m[key], m["fwd"])
    q = pd.qcut(m[key], 5, labels=False, duplicates="drop")
    sp_i = (m["fwd"][q==4].mean()-m["fwd"][q==0].mean())*1e4
    print(f"  Nur Orderbuch ({key}):                      IC {ic_i:+.3f}, Q5-Q1 {sp_i:+.1f} bp")

print("\n" + "=" * 80)
print("B) Der entscheidende Test: Orderbuch NACH Herausrechnen des Preises")
print("=" * 80)
print("   (Residuum der Imbalance gegen die vergangene Rendite)")
for key in ("imb3","imb5"):
    # Imbalance auf vergangene Rendite regressieren, Rest ist die reine Buchinformation
    x = m["past"].to_numpy(); y = m[key].to_numpy()
    beta = np.polyfit(x, y, 1)
    resid = y - np.polyval(beta, x)
    ic_r, p_r = stats.spearmanr(resid, m["fwd"])
    n_eff = len(m)/H
    t = ic_r*np.sqrt(max(n_eff-2,1)/max(1-ic_r**2,1e-9))
    p_adj = 2*(1-stats.t.cdf(abs(t), max(n_eff-2,1)))
    q = pd.qcut(pd.Series(resid, index=m.index), 5, labels=False, duplicates="drop")
    sp_r = (m["fwd"][q==4].mean()-m["fwd"][q==0].mean())*1e4
    print(f"  {key} bereinigt: IC {ic_r:+.3f}  Q5-Q1 {sp_r:+7.1f} bp  "
          f"p korrigiert {p_adj:.3f}  ({'haelt' if p_adj<0.05 else 'faellt'})")

print("\n" + "=" * 80)
print("C) Doppelsortierung: Orderbuch innerhalb gleicher Preisbewegung")
print("=" * 80)
m["pq"] = pd.qcut(m["past"], 3, labels=False, duplicates="drop")
print(f"  {'Preis-Terzil':16s} {'Buch niedrig':>14s} {'Buch hoch':>12s} {'Differenz':>12s}")
for pq in range(3):
    sub = m[m["pq"]==pq]
    iq = pd.qcut(sub["imb5"], 3, labels=False, duplicates="drop")
    lo, hi = sub["fwd"][iq==0].mean()*1e4, sub["fwd"][iq==2].mean()*1e4
    lbl = ["gefallen","seitwaerts","gestiegen"][pq]
    print(f"  {lbl:16s} {lo:+11.1f} bp {hi:+9.1f} bp {hi-lo:+9.1f} bp")
