"""Teil 5: Die entscheidende Kontrolle -- gleiche Zeitpunkte, verschobene
Signale. Und die Pass-Rate getrennt nach Suchzeitraum und Holdout."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from msb import bars4h, signals, SPLIT
COST=8e-4; btc=bars4h("btc")

def pr_of(df,pos):
    c=df.close.to_numpy(); ret=np.diff(c)/c[:-1]
    turn=np.abs(np.diff(np.concatenate([[0],pos])))[:-1]
    s=pos[:-1]*ret-COST*turn
    day=pd.Series(s,index=df.index[1:]).resample("1D").apply(lambda x:(1+x).prod()-1).to_numpy()
    n=len(day); ok=tot=0
    for st in range(0,n-30,5):
        e=1.0
        for k in range(st,n):
            e*=(1+day[k])
            if day[k]<-0.03 or e-1<=-0.06: hit=False; break
            if e-1>=0.10: hit=True; break
        else: continue
        ok+=hit; tot+=1
    return (ok/tot*100 if tot else 0), tot

def build(d,hold,size):
    pos=np.zeros(len(d)); i=0
    while i<len(d):
        if d[i]!=0: pos[i:i+hold]=d[i]*size; i+=hold
        else: i+=1
    return pos

print("="*70); print("Pass-Rate getrennt (0,35x, 5 Tage halten)"); print("="*70)
for name,seg in (("Suchzeitraum 2021-24",btc[btc.index<SPLIT]),
                 ("HOLDOUT 2025-26",btc[btc.index>=SPLIT]),
                 ("gesamt",btc)):
    L,S=signals(seg,"trend")
    d=np.where(L.to_numpy(),1,np.where(S.to_numpy(),-1,0))
    p,t=pr_of(seg,build(d,30,0.35)); print(f"  {name:<24} {p:>5.1f} %  ({t} Starts)")

print("\n"+"="*70)
print("Kontrolle: dieselben Zeitpunkte, Richtung gewuerfelt (500 Laeufe)")
print("="*70)
L,S=signals(btc,"trend")
d0=np.where(L.to_numpy(),1,np.where(S.to_numpy(),-1,0))
times=np.where(d0!=0)[0]
rng=np.random.default_rng(3); zs=[]
for _ in range(500):
    d=np.zeros(len(d0)); d[times]=rng.choice([1,-1],size=len(times))
    p,_=pr_of(btc,build(d,30,0.35)); zs.append(p)
real,_=pr_of(btc,build(d0,30,0.35))
zs=np.array(zs)
print(f"  echte Richtungen:            {real:>5.1f} %")
print(f"  gewuerfelte Richtungen:      Median {np.median(zs):>5.1f} %   "
      f"5-95 %: {np.percentile(zs,5):.1f} .. {np.percentile(zs,95):.1f} %")
print(f"  p-Wert (einseitig):          {(zs>=real).mean():.3f}")

print("\n"+"="*70)
print("Kontrolle: Signale um 1..500 Bars zirkulaer verschoben (500 Laeufe)")
print("="*70)
zs2=[]
for k in rng.choice(np.arange(30,len(d0)-30),size=500,replace=False):
    p,_=pr_of(btc,build(np.roll(d0,int(k)),30,0.35)); zs2.append(p)
zs2=np.array(zs2)
print(f"  echte Lage:                  {real:>5.1f} %")
print(f"  verschoben:                  Median {np.median(zs2):>5.1f} %   "
      f"5-95 %: {np.percentile(zs2,5):.1f} .. {np.percentile(zs2,95):.1f} %")
print(f"  p-Wert (einseitig):          {(zs2>=real).mean():.3f}")
