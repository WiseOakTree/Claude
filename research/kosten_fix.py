"""Korrektur: Der Backtest verrechnete 16 bp JE SEITE = 32 bp je Roundtrip.
Beabsichtigt waren 16 bp je Roundtrip (8 bp je Seite).
Wie viel aendert das?
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from prop_backtester import levels
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC"); TGT,DD,DAY=.10,.06,.03

def series(a, side_bp, lev, one=True, hold=48):
    d=pd.read_csv(V+f"{a}_1h.csv",index_col=0,parse_dates=True)
    h=pd.Series(d["close"].to_numpy(),index=d.index).pct_change().fillna(0)
    by=levels.build_levels(d,width=8,tol_atr=0.5,max_age=1000)
    ev=levels.breakout_events(by,d,min_touch=6)
    n=len(d); pos=np.zeros(n); busy=-1
    for (t,dr,_,_) in ev:
        if one and t<busy: continue
        pos[t:t+hold]=dr; busy=t+hold
    w=pd.Series(np.clip(pos,-1,1),index=d.index).astype(float)*lev
    held=w.shift(1)
    return (held*h-side_bp/1e4*held.diff().abs().fillna(0)).dropna()

def pr(s):
    dd=((1+s).resample("1D").prod()-1).dropna().to_numpy()
    p=f=c=0
    for st in range(0,len(dd)-30):
        e=1.0; done=None
        for i in range(st,min(st+365,len(dd))):
            x=dd[i]
            if x<-DAY: done="f";break
            e*=(1+x)
            if e<=1-DD: done="f";break
            if e>=1+TGT: done="p";break
        if done=="p":p+=1
        elif done=="f":f+=1
        else:c+=1
    t=p+f+c
    return p/t*100 if t else 0

print("="*88)
print("KORREKTUR: Pass-Rate bei tatsaechlich 16 bp je Roundtrip (statt 32 bp)")
print("="*88)
print(f"  {'Asset':6s} {'Groesse':>8s} {'32 bp/RT (berichtet)':>22s} "
      f"{'16 bp/RT (korrekt)':>20s} {'Differenz':>10s}")
print("  "+"-"*70)
for a in ["btc","eth","sol","xrp"]:
    for lev in [0.35,0.50]:
        old=pr(series(a,16.0,lev)); new=pr(series(a,8.0,lev))
        print(f"  {a.upper():6s} {lev:>7.2f}x {old:>21.1f}% {new:>19.1f}% {new-old:>+9.1f}")
print()
print("  Such/Holdout fuer BTC 0,35x bei korrigierten Kosten:")
s=series("btc",8.0,0.35)
print(f"    Suchzeitraum {pr(s[s.index<SPLIT]):.1f}%   Holdout {pr(s[s.index>=SPLIT]):.1f}%")
