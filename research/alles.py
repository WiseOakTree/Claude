"""ALLE Befunde mit korrigierter Ueberlappungsstatistik neu gerechnet.

alt: n_eff = n / Haltedauer          (falsch, wenn Signale duenn gesaet sind)
neu: n_eff = Summe der Einzigartigkeit (Trade mit k gleichzeitigen zaehlt 1/k)
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/home/user/Claude/src")
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from prop_backtester import levels as LV
from msb import bars4h, signals, macd, stoch, boll
D="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC"); COST=8e-4

def n_eff(starts,hold,N):
    conc=np.zeros(N)
    for i in starts: conc[i:i+hold]+=1
    u=[]
    for i in starts:
        seg=conc[i:i+hold]; seg=seg[seg>0]
        u.append((1.0/seg).mean() if len(seg) else 0.0)
    return max(np.sum(u),2.0)

def zeile(label,zeit,starts,rets,hold,N,ref=None):
    x=np.asarray(rets,dtype=float)
    if len(x)<15:
        print(f"  {label:<34}{zeit:<14}{len(x):>5}{'zu wenige':>28}"); return None
    ne=n_eff(np.asarray(starts),hold,N)
    ta=x.mean()/(x.std(ddof=1)/np.sqrt(max(len(x)/hold,2)))
    tn=x.mean()/(x.std(ddof=1)/np.sqrt(ne))
    mk=""
    if ref is not None and np.sign(x.mean())!=np.sign(ref): mk="  KIPPT"
    print(f"  {label:<34}{zeit:<14}{len(x):>5}{x.mean()*1e4:>+9.1f} bp"
          f"{ta:>8.2f}{tn:>9.2f}{ne:>8.0f}{mk}")
    return x.mean()

KOPF=(f"  {'Befund':<34}{'Zeitraum':<14}{'n':>5}{'Effekt':>12}{'t ALT':>8}"
      f"{'t NEU':>9}{'n_eff':>8}")

# ============ 1) S/R-Ausbruch und die zehn Filter ============
h1=pd.read_csv(D+"btc_1h.csv",index_col=0,parse_dates=True)
by=LV.build_levels(h1)
c=h1.close.to_numpy(); H=48; N=len(c); idx=h1.index
f=np.full(N,np.nan); f[:-H]=c[H:]/c[:-H]-1
o,hi,lo=h1.open.to_numpy(),h1.high.to_numpy(),h1.low.to_numpy()
ha_c=(o+hi+lo+c)/4
er=pd.Series(c).diff().abs().rolling(48).sum()
eff=(pd.Series(c)-pd.Series(c).shift(48)).abs()/er.replace(0,np.nan)

def events(**kw):
    ev=LV.breakout_events(by,h1,min_touch=6,**kw)
    r=[(t,d,idx[t],d*f[t]-2*COST) for t,d,_,_ in ev if np.isfinite(f[t])]
    return pd.DataFrame(r,columns=["i","d","ts","ret"])

E=events()
print("="*104); print("1. S/R-AUSBRUCH UND DIE ZEHN FILTER (BTC 1h, 48 h halten)"); print("="*104)
print(KOPF)
basis={}
for nm,m in (("Suche 21-24",E.ts<SPLIT),("HOLDOUT 25-26",E.ts>=SPLIT),
             ("gesamt",pd.Series(True,index=E.index))):
    s=E[m]; basis[nm]=zeile("S/R ohne Filter",nm,s.i.to_numpy(),s.ret.to_numpy(),H,N)
print()

FILTER={
 "1 Mindest-Durchbruch 0,25 ATR": ("param",dict(min_pen_atr=0.25)),
 "2 Rollenlogik nach Kurslage":   ("param",dict(role="position")),
 "3 Cooldown 48 Bars":            ("param",dict(cooldown=48)),
 "5 Heikin-Ashi im Einklang":     ("maske",lambda e: (e.d.to_numpy()==1)==(ha_c[e.i]>ha_c[e.i-1])),
 "6 Session 08-20 UTC":           ("maske",lambda e: e.ts.dt.hour.between(8,20).to_numpy()),
 "7 Tagesbremse (Mo-Fr)":         ("maske",lambda e: (e.ts.dt.dayofweek<5).to_numpy()),
 "8 kein Wochenende":             ("maske",lambda e: (e.ts.dt.dayofweek<5).to_numpy()),
 "9 Marktphase Trend (ER>Median)":("maske",lambda e: (eff.to_numpy()[e.i]>np.nanmedian(eff)) ),
}
for lab,(art,arg) in FILTER.items():
    EE = events(**arg) if art=="param" else E[arg(E)]
    for nm,m in (("Suche 21-24",EE.ts<SPLIT),("HOLDOUT 25-26",EE.ts>=SPLIT)):
        s=EE[m]; zeile(lab,nm,s.i.to_numpy(),s.ret.to_numpy(),H,N,basis[nm])
    print()

# Filter 10: VWAP
tp=(h1.high+h1.low+h1.close)/3; pv=tp*h1.volume
vwd=(pv.groupby(idx.floor("1D")).cumsum()/h1.volume.groupby(idx.floor("1D")).cumsum()).to_numpy()
mk=(E.d.to_numpy()==1)==(c[E.i]>vwd[E.i])
EE=E[mk]
for nm,m in (("Suche 21-24",EE.ts<SPLIT),("HOLDOUT 25-26",EE.ts>=SPLIT)):
    s=EE[m]; zeile("10 VWAP im Einklang",nm,s.i.to_numpy(),s.ret.to_numpy(),H,N,basis[nm])

# ============ 2) S/R-Bounce ============
print("\n"+"="*104); print("2. S/R-BOUNCE (der Gegenentwurf zum Ausbruch)"); print("="*104)
print(KOPF)
bv=LV.bounce_events(by,h1,min_touch=6)
rb=[(t,d,idx[t],d*f[t]-2*COST) for t,d,_,_ in bv if np.isfinite(f[t])]
B=pd.DataFrame(rb,columns=["i","d","ts","ret"])
for nm,m in (("Suche 21-24",B.ts<SPLIT),("HOLDOUT 25-26",B.ts>=SPLIT),
             ("gesamt",pd.Series(True,index=B.index))):
    s=B[m]; zeile("S/R-Bounce",nm,s.i.to_numpy(),s.ret.to_numpy(),H,N)
