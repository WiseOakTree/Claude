"""Welcher Timeframe traegt den S/R-Ausbruch?

Wanduhr-Horizont konstant bei 24 Stunden -- auf 1h sind das 24 Bars, auf 4h
nur 6. Sonst waeren die Zahlen nicht vergleichbar.
Nur Suchzeitraum. Holdout und ETH kommen danach.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
full=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
COST=16e-4
TFS={"1h":1,"2h":2,"4h":4,"8h":8,"1D":24}

def rs(df, hours):
    if hours==1: return df
    return df.resample(f"{hours}h").agg({"open":"first","high":"max","low":"min",
                                         "close":"last","volume":"sum"}).dropna()

def effect(ev, c, n, hz_bars):
    seen={}
    for (t,d,_,_) in ev:
        b=t//max(hz_bars,1)
        if b not in seen and t+hz_bars<n: seen[b]=(c[t+hz_bars]/c[t]-1)*d
    a=np.array(list(seen.values()))*1e4
    if len(a)<15: return np.nan,np.nan,len(a)
    _,p=stats.ttest_1samp(a,0); return a.mean(),p,len(a)

def passrate(ev, df, hold_bars, lev):
    c=df["close"].to_numpy(); n=len(df)
    ret=pd.Series(c,index=df.index).pct_change().fillna(0)
    pos=np.zeros(n)
    for (t,d,_,_) in ev: pos[t:min(t+hold_bars,n)]+=d
    w=pd.Series(np.clip(pos,-1,1),index=df.index).astype(float)*lev
    held=w.shift(1); s=held*ret-COST*held.diff().abs().fillna(0)
    dd=((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()
    p=f=cn=0
    for st in range(0,len(dd)-1):
        eq=1.0; done=None
        for i in range(st,min(st+365,len(dd))):
            r=dd[i]
            if r<-.03: done="f";break
            eq*=(1+r)
            if eq<=.94: done="f";break
            if eq-1>=.10: done="p";break
        if done=="p": p+=1
        elif done=="f": f+=1
        else: cn+=1
    tot=p+f+cn
    return (p/(p+f)*100 if p+f else 0, p/tot*100, cn/tot*100)

def run(src, label, split=None):
    print("="*92); print(label); print("="*92)
    print(f"{'TF':>4s} {'Bars':>7s} {'Ereign.':>8s} {'Effekt 24h':>12s} {'p':>7s} "
          f"{'Halten':>9s} {'Pass 1,0x':>10s} {'Pass 0,5x':>10s}")
    print("-"*92)
    for tf, hrs in TFS.items():
        df = rs(src, hrs)
        if split=="search": df=df[df.index<pd.Timestamp("2025-01-01",tz="UTC")]
        elif split=="holdout": df=df[df.index>=pd.Timestamp("2025-01-01",tz="UTC")]
        if len(df)<500: continue
        c=df["close"].to_numpy(); n=len(df)
        by=levels.build_levels(df,width=8,tol_atr=0.5,max_age=1000)
        ev=levels.breakout_events(by,df,min_touch=6)
        hz=max(1, 24//hrs)                      # 24 Stunden in Bars
        e,p,ne=effect(ev,c,n,hz)
        hold=max(1, 48//hrs)                    # 48 Stunden in Bars
        if len(ev)<20:
            print(f"{tf:>4s} {len(df):7d} {len(ev):8d}   zu wenige Ereignisse"); continue
        q1,u1,_=passrate(ev,df,hold,1.0); q5,u5,_=passrate(ev,df,hold,0.5)
        etxt=f"{e:+8.1f} bp" if np.isfinite(e) else "     —   "
        ptxt=f"{p:7.3f}" if np.isfinite(p) else "      —"
        print(f"{tf:>4s} {len(df):7d} {len(ev):8d} {etxt} {ptxt} {hold:6d} Bars "
              f"{u1:9.1f}% {u5:9.1f}%")
    print()

run(full, "BTC — SUCHZEITRAUM 2021-03..2024-12 (hier wird gesucht)", "search")
