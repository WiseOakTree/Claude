"""Wie einfach darf die Regel werden, ohne schlechter zu werden?

Die aktuelle Regel hat eine versteckte Komplikation: ueberlappende Signale
werden gestapelt (pos += dr, geklippt auf +-1). Von Hand ist das kaum
umsetzbar. Getestet werden radikale Vereinfachungen -- jede fuer sich.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC"); TGT,DD,DAY=.10,.06,.03; COST=16e-4

def pr(dd,cap=365):
    p=f=c=0
    for st in range(0,len(dd)-30):
        e=1.0; done=None
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
    return (p/t*100 if t else 0)

def build(asset, min_touch=6, hold=48, lev=0.5, long_only=False, one_at_a_time=False):
    d=pd.read_csv(V+f"{asset}_1h.csv",index_col=0,parse_dates=True)
    h=pd.Series(d["close"].to_numpy(),index=d.index).pct_change().fillna(0)
    by=levels.build_levels(d,width=8,tol_atr=0.5,max_age=1000)
    ev=levels.breakout_events(by,d,min_touch=min_touch)
    n=len(d); pos=np.zeros(n); ntr=0; busy=-1
    for (t,dr,_,_) in ev:
        if long_only and dr<0: continue
        if one_at_a_time:
            if t<busy: continue
            pos[t:t+hold]=dr; busy=t+hold; ntr+=1
        else:
            pos[t:t+hold]+=dr; ntr+=1
    w=pd.Series(np.clip(pos,-1,1),index=d.index).astype(float)*lev
    held=w.shift(1); s=held*h-COST*held.diff().abs().fillna(0)
    return s, ntr

def evaluate(s):
    out={}
    for lab,m in (("Such",s.index<SPLIT),("Hold",s.index>=SPLIT),
                  ("ges",np.ones(len(s),bool))):
        ss=s[m].dropna()
        if len(ss)<2000: out[lab]=float("nan"); continue
        out[lab]=pr(((1+ss).resample("1D").prod()-1).dropna().to_numpy())
    return out

VARIANTS=[
 ("BASIS  (stapelnd, long+short, 48h, >=6)", dict()),
 ("A  nur EINE Position gleichzeitig",       dict(one_at_a_time=True)),
 ("B  nur LONG (Shorts weglassen)",          dict(long_only=True)),
 ("C  eine Position UND nur long",           dict(one_at_a_time=True,long_only=True)),
 ("D  Halten 24h statt 48h",                 dict(hold=24)),
 ("E  nur starke Level >=10 Beruehrungen",   dict(min_touch=10)),
 ("F  MAXIMAL EINFACH: 1 Pos, long, >=10",   dict(one_at_a_time=True,long_only=True,min_touch=10)),
]
print("="*100)
print("Wie viel Vereinfachung vertraegt die Regel?   (Pass-Rate in %, 0,5x)")
print("="*100)
hdr=f"  {'Variante':40s}"
for a in ["BTC","ETH","SOL","XRP"]: hdr+=f" {a+' S/H':>12s}"
print(hdr+f" {'Ø ges':>7s} {'Trades':>7s}")
print("  "+"-"*96)
for name,kw in VARIANTS:
    row=f"  {name:40s}"; ges=[]; tr=0
    for a in ["btc","eth","sol","xrp"]:
        s,n=build(a,**kw); r=evaluate(s); tr+=n
        row+=f" {r['Such']:>5.1f}/{r['Hold']:>5.1f}"
        ges.append(r["ges"])
    print(row+f" {np.mean(ges):>6.1f}% {tr:>7d}")
