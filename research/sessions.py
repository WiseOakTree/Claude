"""Wo findet die Bewegung wirklich statt? Tageszeit-Analyse, vier Assets."""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
ASSETS=[("BTC","btc_1h.csv"),("ETH","eth_1h.csv"),("SOL","sol_1h.csv"),("XRP","xrp_1h.csv")]
SESS={"Asien":range(0,8),"Europa":range(8,13),"US":range(13,21),"vor Asien":range(21,24)}

frames={}
for nm,fn in ASSETS:
    d=pd.read_csv(V+fn,index_col=0,parse_dates=True)
    d["ret"]=d["close"].pct_change()
    d["absret"]=d["ret"].abs()*1e4
    d["hour"]=d.index.hour
    frames[nm]=d.dropna()

print("="*94)
print("1) Bewegungsstaerke je Stunde (mittlere absolute 1h-Rendite in bp)")
print("="*94)
print(f"{'UTC':>4s} " + "".join(f"{n:>9s}" for n,_ in ASSETS) + f"{'Mittel':>9s}  {'Session':<12s}")
print("-"*94)
means={}
for h in range(24):
    vals=[frames[n][frames[n].hour==h].absret.mean() for n,_ in ASSETS]
    means[h]=np.mean(vals)
    sess=next((s for s,r in SESS.items() if h in r),"")
    print(f"{h:4d} " + "".join(f"{v:9.1f}" for v in vals) + f"{np.mean(vals):9.1f}  {sess:<12s}")

overall=np.mean(list(means.values()))
print(f"\n  Tagesmittel: {overall:.1f} bp")
best=max(means,key=means.get); worst=min(means,key=means.get)
print(f"  staerkste Stunde: {best:02d}:00 UTC ({means[best]:.1f} bp, "
      f"{means[best]/overall-1:+.0%} gegen Mittel)")
print(f"  schwaechste:      {worst:02d}:00 UTC ({means[worst]:.1f} bp, "
      f"{means[worst]/overall-1:+.0%})")

print("\n"+"="*94)
print("2) Je Session zusammengefasst")
print("="*94)
print(f"{'Session':<14s} {'Stunden':>9s} " + "".join(f"{n:>9s}" for n,_ in ASSETS)
      + f"{'Mittel':>9s} {'vs Tag':>9s}")
print("-"*94)
for s,r in SESS.items():
    vals=[frames[n][frames[n].hour.isin(r)].absret.mean() for n,_ in ASSETS]
    m=np.mean(vals)
    print(f"{s:<14s} {f'{min(r):02d}-{max(r):02d}':>9s} "
          + "".join(f"{v:9.1f}" for v in vals) + f"{m:9.1f} {m/overall-1:+8.0%}")

print("\n"+"="*94)
print("3) Gerichtete Drift je Session (mittlere 1h-Rendite, nicht absolut)")
print("="*94)
print(f"{'Session':<14s} " + "".join(f"{n:>11s}" for n,_ in ASSETS) + f"{'Mittel':>10s} {'p (BTC)':>9s}")
print("-"*94)
for s,r in SESS.items():
    vals=[]; p=np.nan
    for i,(n,_) in enumerate(ASSETS):
        sub=frames[n][frames[n].hour.isin(r)].ret*1e4
        vals.append(sub.mean())
        if n=="BTC": _,p=stats.ttest_1samp(sub.dropna(),0)
    print(f"{s:<14s} " + "".join(f"{v:+11.2f}" for v in vals)
          + f"{np.mean(vals):+10.2f} {p:9.3f}")
print("\n  Bonferroni-Schwelle bei 4 Sessions: p < 0,0125")
