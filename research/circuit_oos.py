"""Out-of-Sample-Pruefung der Tagesbremse.

Hoehe wird auf dem BTC-Suchzeitraum gewaehlt, dann unveraendert angewandt auf
BTC-Holdout und die drei anderen Assets.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
COST=16e-4; SPLIT=pd.Timestamp("2025-01-01",tz="UTC")

def bahn(df, hold=48, lev=0.5):
    c=df["close"].to_numpy(); n=len(df)
    by=levels.build_levels(df,width=8,tol_atr=0.5,max_age=1000)
    ev=levels.breakout_events(by,df,min_touch=6)
    pos=np.zeros(n)
    for (t,d,_,_) in ev: pos[t:min(t+hold,n)]+=d
    w=pd.Series(np.clip(pos,-1,1),index=df.index).astype(float)*lev
    return w, pd.Series(c,index=df.index).pct_change().fillna(0)

def bremse(w, ret, cutoff):
    held=w.shift(1).fillna(0).to_numpy(); r=ret.to_numpy(); idx=ret.index
    n=len(r); out=np.zeros(n); tag=idx.normalize()
    cur=None; eq=1.0; sperr=False; prev=0.0
    for i in range(n):
        if cur is None or tag[i]!=cur: cur=tag[i]; eq=1.0; sperr=False
        h=0.0 if sperr else held[i]
        pnl=h*r[i]-COST*abs(h-prev); out[i]=pnl; prev=h; eq*=(1+pnl)
        if cutoff is not None and eq-1<=-cutoff:
            sperr=True
            if prev!=0.0: out[i]-=COST*abs(prev); prev=0.0
    return pd.Series(out,index=idx)

def pr(s):
    d=((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()
    p=f=cn=0
    for st in range(0,len(d)-1):
        eq=1.0; done=None
        for i in range(st,min(st+365,len(d))):
            x=d[i]
            if x<-.03: done="f";break
            eq*=(1+x)
            if eq<=.94: done="f";break
            if eq-1>=.10: done="p";break
        if done=="p": p+=1
        elif done=="f": f+=1
        else: cn+=1
    tot=p+f+cn
    return p/tot*100 if tot else 0

CUTS=[None,0.025,0.02,0.015,0.01,0.0075]
btc=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
w,ret=bahn(btc[btc.index<SPLIT])
such={c:pr(bremse(w,ret,c)) for c in CUTS}
print("="*74); print("1) Wahl auf dem BTC-SUCHZEITRAUM (2021-03..2024-12)"); print("="*74)
for c in CUTS:
    lab="keine" if c is None else f"-{c*100:.2f} %"
    print(f"  Bremse {lab:>9s}: {such[c]:5.1f} %")
best=max([c for c in CUTS if c is not None], key=lambda c: such[c])
print(f"\n  -> gewaehlt: {best*100:.2f} % (bestes im Suchzeitraum)")

print("\n"+"="*74); print("2) Unveraendert angewandt auf ungesehene Daten"); print("="*74)
print(f"  {'Datensatz':28s} {'ohne Bremse':>13s} {f'mit {best*100:.2f} %':>13s} {'Aenderung':>11s}")
print("  "+"-"*68)
w,ret=bahn(btc[btc.index>=SPLIT])
a,b=pr(bremse(w,ret,None)),pr(bremse(w,ret,best))
print(f"  {'BTC-Holdout 2025-01..':28s} {a:12.1f}% {b:12.1f}% {b-a:+10.1f} pp")
for nm,fn in (("ETH","eth_1h.csv"),("SOL","sol_1h.csv"),("XRP","xrp_1h.csv")):
    d=pd.read_csv(V+fn,index_col=0,parse_dates=True)
    w,ret=bahn(d)
    a,b=pr(bremse(w,ret,None)),pr(bremse(w,ret,best))
    print(f"  {nm+' (gesamt, ungesehen)':28s} {a:12.1f}% {b:12.1f}% {b-a:+10.1f} pp")

print("\n"+"="*74); print("3) Robustheit: gilt die Verbesserung ueber ALLE Bremsenhoehen?"); print("="*74)
print(f"  {'Bremse':>9s} " + "".join(f"{n:>11s}" for n in ("BTC-Hold","ETH","SOL","XRP")) + f"{'Mittel':>10s}")
print("  "+"-"*64)
sets=[("BTC-Hold",btc[btc.index>=SPLIT])]+[(n,pd.read_csv(V+f,index_col=0,parse_dates=True))
      for n,f in (("ETH","eth_1h.csv"),("SOL","sol_1h.csv"),("XRP","xrp_1h.csv"))]
bahnen=[(n,)+bahn(d) for n,d in sets]
base={n:pr(bremse(w,r,None)) for n,w,r in bahnen}
for c in CUTS:
    vals=[pr(bremse(w,r,c))-base[n] for n,w,r in bahnen]
    lab="keine" if c is None else f"-{c*100:.2f}%"
    print(f"  {lab:>9s} " + "".join(f"{v:+10.1f}" for v in vals) + f"{np.mean(vals):+9.1f} pp")
