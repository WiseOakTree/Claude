"""Selbst gesetzte Tagesbremse: Bei X % Tagesverlust flach stellen, Feierabend.

Zielt direkt auf die gemessene Hauptausfallursache (95 % der Fehlschlaege
kommen vom 3-%-Tageslimit). Keine Prognose -- reine Risikokontrolle.
Geprueft auf allen vier Assets.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
ASSETS=[("BTC","btc_1h.csv"),("ETH","eth_1h.csv"),("SOL","sol_1h.csv"),("XRP","xrp_1h.csv")]
COST=16e-4

def stundenpnl(df, hold=48, lev=0.5):
    """Stuendliche Strategierendite ohne Bremse."""
    c=df["close"].to_numpy(); n=len(df)
    by=levels.build_levels(df,width=8,tol_atr=0.5,max_age=1000)
    ev=levels.breakout_events(by,df,min_touch=6)
    pos=np.zeros(n)
    for (t,d,_,_) in ev: pos[t:min(t+hold,n)]+=d
    w=pd.Series(np.clip(pos,-1,1),index=df.index).astype(float)*lev
    return w, pd.Series(c,index=df.index).pct_change().fillna(0)

def mit_bremse(w, ret, cutoff):
    """cutoff=None: keine Bremse. Sonst: ab -cutoff Tagesverlust flach bis Mitternacht."""
    held=w.shift(1).fillna(0).to_numpy()
    r=ret.to_numpy(); idx=ret.index
    n=len(r); out=np.zeros(n)
    tag=idx.normalize()
    cur=None; eq_tag=1.0; gesperrt=False; prev=0.0
    for i in range(n):
        if cur is None or tag[i]!=cur:
            cur=tag[i]; eq_tag=1.0; gesperrt=False
        h = 0.0 if gesperrt else held[i]
        pnl = h*r[i] - COST*abs(h-prev)
        out[i]=pnl; prev=h
        eq_tag*=(1+pnl)
        if cutoff is not None and eq_tag-1 <= -cutoff:
            gesperrt=True                      # Rest des Tages Pause
            if prev!=0.0:
                out[i]-=COST*abs(prev); prev=0.0
    return pd.Series(out,index=idx)

def passrate(s):
    d=((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()
    p=f=cn=0; tage=[]
    for st in range(0,len(d)-1):
        eq=1.0; done=None
        for i in range(st,min(st+365,len(d))):
            x=d[i]
            if x<-.03: done="f";break
            eq*=(1+x)
            if eq<=.94: done="f";break
            if eq-1>=.10: done="p";tage.append(i-st+1);break
        if done=="p": p+=1
        elif done=="f": f+=1
        else: cn+=1
    tot=p+f+cn
    return (p/tot*100 if tot else 0, np.median(tage) if tage else np.nan,
            cn/tot*100 if tot else 0)

CUTS=[None,0.025,0.02,0.015,0.01,0.0075]
res={}
for nm,fn in ASSETS:
    df=pd.read_csv(V+fn,index_col=0,parse_dates=True)
    w,ret=stundenpnl(df)
    res[nm]={c:passrate(mit_bremse(w,ret,c)) for c in CUTS}

print("="*86)
print("Selbst gesetzte Tagesbremse -- Pass-Rate (0,5x, Untergrenze, alle vier Assets)")
print("="*86)
print(f"{'Bremse bei':>12s} " + "".join(f"{n:>11s}" for n,_ in ASSETS) + f"{'Mittel':>10s}")
print("-"*86)
for c in CUTS:
    vals=[res[n][c][0] for n,_ in ASSETS]
    lab = "keine" if c is None else f"-{c*100:.2f} %"
    star = "  <<<" if c is not None and np.mean(vals)>np.mean([res[n][None][0] for n,_ in ASSETS]) else ""
    print(f"{lab:>12s} " + "".join(f"{v:10.1f}%" for v in vals) + f"{np.mean(vals):9.1f}%{star}")

print("\n"+"="*86)
print("Wie lange dauert es dann? (Median-Tage bis zum Ziel)")
print("="*86)
print(f"{'Bremse bei':>12s} " + "".join(f"{n:>11s}" for n,_ in ASSETS))
print("-"*60)
for c in CUTS:
    lab = "keine" if c is None else f"-{c*100:.2f} %"
    row=""
    for n,_ in ASSETS:
        d=res[n][c][1]
        row += f"{d:10.0f}T" if np.isfinite(d) else f"{'—':>11s}"
    print(f"{lab:>12s} " + row)

print("\n"+"="*86)
print("Wie oft wird das harte 3-%-Limit ueberhaupt noch erreicht?")
print("="*86)
for nm,fn in ASSETS:
    df=pd.read_csv(V+fn,index_col=0,parse_dates=True)
    w,ret=stundenpnl(df)
    line=f"  {nm:5s}"
    for c in (None,0.02,0.015,0.01):
        s=mit_bremse(w,ret,c)
        d=((1+s.dropna()).resample("1D").prod()-1).dropna()
        lab="ohne" if c is None else f"{c*100:.1f}%"
        line += f"   {lab}: {(d<-.03).mean()*100:5.2f}%"
    print(line)
