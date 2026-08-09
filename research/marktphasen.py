"""Behauptung: "Marktphasen zu verstehen ist das Wichtigste."

Staerkster moeglicher Test: ein PERFEKTES ORAKEL. Wenn du die Phase der
NAECHSTEN 48 Stunden im Voraus wuesstest -- wie viel waere das wert?
Wenn selbst das nichts bringt, ist die Behauptung erledigt.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import levels
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
d=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
c=d["close"].to_numpy(); h=d["high"].to_numpy(); l=d["low"].to_numpy(); n=len(d)
r=np.diff(np.log(c),prepend=np.log(c[0]))
by=levels.build_levels(d,width=8,tol_atr=0.5,max_age=1000)
tr=[]; busy=-1
for (t,dr,tc,lv) in levels.breakout_events(by,d,min_touch=6):
    if t<busy or t+48>=n: continue
    busy=t+48; tr.append((t,dr))
pnl=np.array([dr*(c[t+48]/c[t]-1) for t,dr in tr])*1e4 - 16.0
print("="*88)
print(f"Basis: {len(tr)} Trades, Ø {pnl.mean():+.1f} bp netto, {(pnl>0).mean()*100:.1f} % positiv")
print("="*88)

def eff(a,b):
    """Efficiency Ratio: |Nettobewegung| / Summe der Einzelbewegungen.
    Nahe 1 = sauberer Trend. Nahe 0 = Seitwaerts."""
    seg=r[a:b]
    return abs(seg.sum())/np.abs(seg).sum() if np.abs(seg).sum()>0 else 0

print("\n1) ORAKEL: die Phase der NAECHSTEN 48 h ist bekannt (Look-ahead!)")
print("="*88)
fwd=np.array([eff(t,t+48) for t,_ in tr])
print(f"  {'Phase (Orakel)':28s} {'n':>5s} {'Ø netto':>10s} {'positiv':>9s} {'p':>8s}")
print("  "+"-"*64)
q=np.asarray(pd.qcut(fwd,3,labels=["Seitwaerts","gemischt","Trend"]))
for lab in ["Seitwaerts","gemischt","Trend"]:
    m=(q==lab)
    t_,p_=stats.ttest_1samp(pnl[m],0)
    print(f"  {lab:28s} {m.sum():>5d} {pnl[m].mean():>+9.1f}bp {(pnl[m]>0).mean()*100:>8.1f}% {p_:>8.3f}")
best=pd.Series(pnl).groupby(pd.Series(q).astype(str)).mean().idxmax()
m=(q==best)
print(f"\n  Beste Phase: '{best}' mit {pnl[m].mean():+.1f} bp gegen {pnl.mean():+.1f} bp gesamt")
print(f"  Nur in dieser Phase handeln (mit ORAKEL): {pnl[m].mean():+.1f} bp,"
      f" aber nur {m.sum()} statt {len(tr)} Trades")
print(f"  Gesamtertrag: {pnl[m].sum():,.0f} bp gegen {pnl.sum():,.0f} bp -> "
      f"{'BESSER' if pnl[m].sum()>pnl.sum() else 'SCHLECHTER'}")

print("\n2) OHNE Orakel: Phase aus der VERGANGENHEIT (handelbar)")
print("="*88)
print(f"  {'Rueckblick':>12s} {'Korrelation mit Zukunftsphase':>32s} {'p':>9s}")
print("  "+"-"*58)
for lb in [24,48,96,168,336]:
    past=np.array([eff(max(0,t-lb),t) for t,_ in tr])
    cc=np.corrcoef(past,fwd)[0,1]
    t_,p_=stats.pearsonr(past,fwd)
    print(f"  {lb:>10d}h {cc:>31.3f} {p_:>9.3f}")

print("\n3) Und wenn man die vergangene Phase als Filter nimmt?")
print("="*88)
print(f"  {'Rueckblick':>10s} {'Phase':>12s} {'n':>5s} {'Ø netto':>10s} {'p':>8s}")
print("  "+"-"*50)
for lb in [48,168]:
    past=np.array([eff(max(0,t-lb),t) for t,_ in tr])
    qp=np.asarray(pd.qcut(past,3,labels=["Seitwaerts","gemischt","Trend"]))
    for lab in ["Seitwaerts","gemischt","Trend"]:
        m=(qp==lab)
        t_,p_=stats.ttest_1samp(pnl[m],0)
        print(f"  {lb:>9d}h {lab:>12s} {m.sum():>5d} {pnl[m].mean():>+9.1f}bp {p_:>8.3f}")
