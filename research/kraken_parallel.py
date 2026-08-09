"""Mehrere Kraken-Challenges parallel -- 85 $ je Stueck.
Vier Bauformen: identisch, verschiedene Groessen, verschiedene Assets,
versetzte Startzeitpunkte.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from prop_backtester import levels
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
TGT,DD,DAY=.10,.06,.03

def daily(asset, lev, side_bp=8.0, hold=48):
    d=pd.read_csv(V+f"{asset}_1h.csv",index_col=0,parse_dates=True)
    h=pd.Series(d["close"].to_numpy(),index=d.index).pct_change().fillna(0)
    by=levels.build_levels(d,width=8,tol_atr=0.5,max_age=1000)
    n=len(d); pos=np.zeros(n); busy=-1
    for (t,dr,_,_) in levels.breakout_events(by,d,min_touch=6):
        if t<busy: continue
        pos[t:t+hold]=dr; busy=t+hold
    w=pd.Series(np.clip(pos,-1,1),index=d.index).astype(float)*lev
    held=w.shift(1)
    s=(held*h-side_bp/1e4*held.diff().abs().fillna(0)).dropna()
    return ((1+s).resample("1D").prod()-1).dropna()

def attempt(dd, st, cap=365):
    e=1.0
    for i in range(st,min(st+cap,len(dd))):
        r=dd[i]
        if r<-DAY: return 0
        e*=(1+r)
        if e<=1-DD: return 0
        if e-1>=TGT: return 1
    return None

CACHE={}
def get(a,l):
    k=(a,l)
    if k not in CACHE: CACHE[k]=daily(a,l)
    return CACHE[k]

print("="*90)
print("MEHRERE KRAKEN-CHALLENGES PARALLEL  (85 $ je Stueck, 10.000 $ Konto)")
print("="*90)

def evaluate(legs, name, offsets=None):
    """legs: Liste von (asset, lev). offsets: Startversatz in Tagen."""
    series=[get(a,l) for a,l in legs]
    idx=series[0].index
    for s in series[1:]: idx=idx.intersection(s.index)
    arr=[s.reindex(idx).to_numpy() for s in series]
    N=len(arr); off=offsets or [0]*N
    n=len(idx)
    res=[]
    for st in range(0,n-380,3):
        out=[attempt(arr[k], st+off[k]) for k in range(N)]
        if any(o is None for o in out): continue
        res.append(out)
    if not res: return
    R=np.array(res)
    passed=R.sum(axis=1)
    print(f"  {name:44s} {(passed>=1).mean()*100:>8.1f}% {passed.mean():>10.2f} "
          f"{passed.mean()/N*100:>10.1f}% {85*N/max(passed.mean(),1e-9):>11,.0f} $")

print(f"  {'Bauform':44s} {'>=1 fund.':>9s} {'Ø Konten':>10s} {'je Konto':>10s} {'$/Konto':>12s}")
print("  "+"-"*88)
evaluate([("btc",0.35)],"1 Challenge BTC 0,35x")
evaluate([("btc",0.35)]*3,"3x identisch (BTC 0,35x)")
evaluate([("btc",0.25),("btc",0.35),("btc",0.50)],"3x BTC, verschiedene Groessen")
evaluate([("btc",0.35),("eth",0.35),("sol",0.35)],"3x verschiedene Assets, 0,35x")
evaluate([("btc",0.35)]*3,"3x BTC 0,35x, Start versetzt 60/120 T",offsets=[0,60,120])
evaluate([("btc",0.25),("btc",0.35),("btc",0.50)],"3x Groessen UND versetzt",offsets=[0,60,120])
