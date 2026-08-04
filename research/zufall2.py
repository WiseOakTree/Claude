"""Haelt "einfach halten bei 0,25x" der Pruefung stand?
Suchzeitraum/Holdout, alle vier Assets, direkter Vergleich mit S/R.
Plus: wie stark haengt es an der Aufwaertsdrift?
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from prop_backtester import levels

TGT,DD,DAY=.10,.06,.03
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC")

def pr(dd,cost_once=0.0,cap=365):
    p=f=c=0
    for st in range(0,len(dd)-30):
        e=1.0-cost_once; done=None
        for i in range(st,min(st+cap,len(dd))):
            x=dd[i]
            if x<-DAY: done="f";break
            e*=(1+x)
            if e<=1-DD: done="f";break
            if e>=1+TGT: done="p";break
        if done=="p":p+=1
        elif done=="f":f+=1
        else:c+=1
    t=p+f+c
    return (p/t*100 if t else 0),(c/t*100 if t else 0)

def series(asset):
    d=pd.read_csv(V+f"{asset}_1h.csv",index_col=0,parse_dates=True)
    h=pd.Series(d["close"].to_numpy(),index=d.index).pct_change().fillna(0)
    by=levels.build_levels(d,width=8,tol_atr=0.5,max_age=1000)
    ev=levels.breakout_events(by,d,min_touch=6)
    pos=np.zeros(len(d))
    for (t,dr,_,_) in ev: pos[t:t+48]+=dr
    w=pd.Series(np.clip(pos,-1,1),index=d.index).astype(float)*0.5
    held=w.shift(1); s=held*h-16e-4*held.diff().abs().fillna(0)
    return h, s

print("="*92)
print("A) HALTEN bei 0,25x gegen S/R bei 0,5x -- getrennt nach Zeitraum")
print("="*92)
print(f"  {'Asset':6s} {'Zeitraum':13s} {'Halten 0,25x':>13s} {'(unaufgel.)':>12s} "
      f"{'S/R 0,5x':>10s} {'Differenz':>10s}")
print("  "+"-"*72)
for a in ["btc","eth","sol","xrp"]:
    h,s=series(a)
    for lab,m in (("Suchzeitraum",h.index<SPLIT),("Holdout",h.index>=SPLIT),
                  ("gesamt",np.ones(len(h),bool))):
        hh=h[m]*0.25; ss=s[m]
        if len(hh)<2000: continue
        dh=((1+hh).resample("1D").prod()-1).dropna().to_numpy()
        ds=((1+ss.dropna()).resample("1D").prod()-1).dropna().to_numpy()
        ph,ch=pr(dh,cost_once=16e-4*0.25); ps,_=pr(ds)
        print(f"  {a.upper():6s} {lab:13s} {ph:>12.1f}% {ch:>11.1f}% "
              f"{ps:>9.1f}% {ph-ps:>+9.1f}")
    print()

print("="*92)
print("B) Woran haengt es? Drift-Sensitivitaet bei 15 % Jahresvol (Simulation)")
print("="*92)
rng=np.random.default_rng(3)
def sim(drift,vol=.15,n=30000,maxd=365):
    sd=vol/np.sqrt(365); mu=drift/365
    r=rng.normal(mu,sd,size=(n,maxd)); eq=np.ones(n); done=np.zeros(n,int)
    for i in range(maxd):
        if (done==0).sum()==0: break
        x=r[:,i]; live=done==0
        done[live&(x<-DAY)]=3; live=done==0
        eq[live]*=(1+x[live]); done[live&(eq<=1-DD)]=2; live=done==0
        done[live&(eq>=1+TGT)]=1
    return (done==1).mean()*100
print(f"  {'Jahresdrift':>12s} {'BESTANDEN':>11s}")
print("  "+"-"*26)
for dr in [-.20,-.10,0.0,.10,.20,.30,.50]:
    print(f"  {dr*100:>+11.0f}% {sim(dr):>10.1f}%")
btc=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
r=np.log(btc["close"]).diff().dropna()
print(f"\n  BTC 2021-03..2026-07 tatsaechlich: {r.mean()*24*365*100:>+.0f}% p.a. "
      f"(log), Vol {r.std()*np.sqrt(24*365)*100:.0f}%")
