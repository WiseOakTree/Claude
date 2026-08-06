"""Kontrolle: Ist die hoehere Quote je Konto bei Versatz echt oder ein
Stichprobenartefakt? Gleiche Startfenster fuer alle Bauformen erzwingen.
Plus: optimaler Abstand."""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
exec(open("kraken_parallel.py").read().split('print("="*90)')[0])

btc=get("btc",0.35).to_numpy(); n=len(btc)
MAXOFF=240
starts=range(0,n-380-MAXOFF,3)      # identisches Fenster fuer ALLE Varianten

print("="*88)
print("KONTROLLE: identische Startfenster fuer alle Bauformen")
print("="*88)
print(f"  {'Versatz (Tage)':>22s} {'>=1 gefunded':>13s} {'Ø Konten':>10s} {'je Konto':>10s} {'$/Konto':>10s}")
print("  "+"-"*70)
for offs,lab in [((0,0,0),"0 / 0 / 0  (gleichzeitig)"),
                 ((0,30,60),"0 / 30 / 60"),
                 ((0,60,120),"0 / 60 / 120"),
                 ((0,90,180),"0 / 90 / 180"),
                 ((0,120,240),"0 / 120 / 240")]:
    res=[]
    for st in starts:
        o=[attempt(btc,st+k) for k in offs]
        if any(x is None for x in o): continue
        res.append(o)
    R=np.array(res); p=R.sum(axis=1)
    print(f"  {lab:>22s} {(p>=1).mean()*100:>12.1f}% {p.mean():>10.2f} "
          f"{p.mean()/3*100:>9.1f}% {255/max(p.mean(),1e-9):>9,.0f} $")

print()
print("="*88)
print("Und wie viele Konten lohnen sich?  (Versatz 60 Tage, BTC 0,35x)")
print("="*88)
print(f"  {'Anzahl':>8s} {'Einsatz':>9s} {'>=1 gefunded':>13s} {'Ø Konten':>10s} {'$/Konto':>10s}")
print("  "+"-"*56)
for N in [1,2,3,4,5]:
    offs=[60*k for k in range(N)]
    res=[]
    for st in starts:
        o=[attempt(btc,st+k) for k in offs]
        if any(x is None for x in o): continue
        res.append(o)
    R=np.array(res); p=R.sum(axis=1)
    print(f"  {N:>8d} {85*N:>8d}$ {(p>=1).mean()*100:>12.1f}% {p.mean():>10.2f} "
          f"{85*N/max(p.mean(),1e-9):>9,.0f} $")
