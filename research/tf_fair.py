"""Fairer Timeframe-Vergleich: Parameter in WANDUHRZEIT konstant.

1h-Referenz: Pivot-Weite 8 Bars = 8 Stunden, Level-Alter 1000 Bars = 41,7 Tage.
Auf groeberen Bars werden die Bar-Zahlen entsprechend heruntergerechnet, damit
ueberall dieselbe Marktstruktur betrachtet wird.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
COST=16e-4
# (Stunden je Bar, Pivot-Weite, Level-Alter) -- Weite*h ~ 8h, Alter*h ~ 1000h
CFG=[("1h",1,8,1000),("2h",2,4,500),("4h",4,2,250),("4h·w4",4,4,250),("8h",8,2,125)]

def rs(df,h):
    return df if h==1 else df.resample(f"{h}h").agg(
        {"open":"first","high":"max","low":"min","close":"last","volume":"sum"}).dropna()

def evaluate(src, label, lo=None, hi=None):
    print("="*96); print(label); print("="*96)
    print(f"{'Variante':8s} {'Weite':>6s} {'Alter':>6s} {'Bars':>7s} {'Ereign.':>8s} "
          f"{'Effekt 24h':>12s} {'p':>7s} {'Pass 1,0x':>10s} {'Pass 0,5x':>10s}")
    print("-"*96)
    for tag,h,w,age in CFG:
        df=rs(src,h)
        if lo is not None: df=df[df.index>=lo]
        if hi is not None: df=df[df.index<hi]
        if len(df)<400: continue
        c=df["close"].to_numpy(); n=len(df)
        ret=pd.Series(c,index=df.index).pct_change().fillna(0)
        by=levels.build_levels(df,width=w,tol_atr=0.5,max_age=age)
        ev=levels.breakout_events(by,df,min_touch=6)
        hz=max(1,24//h); hold=max(1,48//h)
        seen={}
        for (t,d,_,_) in ev:
            b=t//max(hz,1)
            if b not in seen and t+hz<n: seen[b]=(c[t+hz]/c[t]-1)*d
        a=np.array(list(seen.values()))*1e4
        if len(ev)<25 or len(a)<15:
            print(f"{tag:8s} {w:6d} {age:6d} {len(df):7d} {len(ev):8d}   zu wenige"); continue
        _,p=stats.ttest_1samp(a,0)
        res=[]
        for lev in (1.0,0.5):
            pos=np.zeros(n)
            for (t,d,_,_) in ev: pos[t:min(t+hold,n)]+=d
            wser=pd.Series(np.clip(pos,-1,1),index=df.index).astype(float)*lev
            held=wser.shift(1); s=held*ret-COST*held.diff().abs().fillna(0)
            dd=((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()
            pp=ff=cn=0
            for st in range(0,len(dd)-1):
                eq=1.0; done=None
                for i in range(st,min(st+365,len(dd))):
                    r=dd[i]
                    if r<-.03: done="f";break
                    eq*=(1+r)
                    if eq<=.94: done="f";break
                    if eq-1>=.10: done="p";break
                if done=="p": pp+=1
                elif done=="f": ff+=1
                else: cn+=1
            res.append(pp/(pp+ff+cn)*100)
        print(f"{tag:8s} {w:6d} {age:6d} {len(df):7d} {len(ev):8d} {a.mean():+9.1f} bp "
              f"{p:7.3f} {res[0]:9.1f}% {res[1]:9.1f}%")
    print()

S=pd.Timestamp("2025-01-01",tz="UTC")
btc=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
eth=pd.read_csv(V+"eth_1h.csv",index_col=0,parse_dates=True)
evaluate(btc,"BTC — Suchzeitraum 2021-03..2024-12", hi=S)
evaluate(btc,"BTC — Holdout 2025-01..2026-06 (vierte Nutzung, entsprechend schwach)", lo=S)
evaluate(eth,"ETH — gesamt (anderes Asset)")
