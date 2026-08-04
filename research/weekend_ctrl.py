"""Die entscheidende Kontrolle: Wirkt der Wochenendfilter -- oder nur das
Weglassen von einem Viertel der Signale?

Vergleich gegen 200 Zufallsfilter, die exakt gleich viele Signale entfernen.
Zusaetzlich Suchzeitraum und Holdout getrennt.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
ASSETS=["btc","eth","sol","xrp"]; SPLIT=pd.Timestamp("2025-01-01",tz="UTC"); COST=16e-4

def is_weekend(idx):
    dow=np.asarray(idx.dayofweek); hr=np.asarray(idx.hour)
    return ((dow==4)&(hr>=22)) | (dow==5) | ((dow==6)&(hr<22))

def passrate(ev,d,drop,hold=48,lev=0.5):
    """drop: boolesches Array ueber die Ereignisse -- True = weglassen."""
    c=d["close"].to_numpy(); n=len(d)
    ret=pd.Series(c,index=d.index).pct_change().fillna(0)
    pos=np.zeros(n)
    for k,(t,dr,_,_) in enumerate(ev):
        if drop[k]: continue
        pos[t:min(t+hold,n)]+=dr
    w=pd.Series(np.clip(pos,-1,1),index=d.index).astype(float)*lev
    held=w.shift(1); s=held*ret-COST*held.diff().abs().fillna(0)
    dd=((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()
    p=f=cn=0
    for st in range(0,len(dd)-1):
        e=1.0; done=None
        for i in range(st,min(st+365,len(dd))):
            r=dd[i]
            if r<-.03: done="f";break
            e*=(1+r)
            if e<=.94: done="f";break
            if e-1>=.10: done="p";break
        if done=="p": p+=1
        elif done=="f": f+=1
        else: cn+=1
    tot=p+f+cn
    return p/tot*100 if tot else 0

print("="*92)
print("Wochenendfilter gegen 200 Zufallsfilter gleicher Groesse")
print("="*92)
print(f"  {'Asset':6s} {'Zeitraum':12s} {'ohne':>8s} {'Wochenende':>11s} "
      f"{'Zufall (Mittel)':>16s} {'Streuung':>9s} {'Perzentil':>10s}")
print("  "+"-"*76)
rng=np.random.default_rng(0)
summary={}
for s in ASSETS:
    full=pd.read_csv(V+f"{s}_1h.csv",index_col=0,parse_dates=True)
    by=levels.build_levels(full,width=8,tol_atr=0.5,max_age=1000)
    ev_all=levels.breakout_events(by,full,min_touch=6)
    for lab,keep in (("Suchzeitraum",full.index<SPLIT),("Holdout",full.index>=SPLIT)):
        d=full[keep]; off=np.where(keep)[0]
        if len(off)<2000: continue
        lo=off.min()
        ev=[(t-lo,dr,tc,lv) for (t,dr,tc,lv) in ev_all if keep[t]]
        if len(ev)<40: continue
        we=is_weekend(d.index)[[t for t,_,_,_ in ev]]
        base=passrate(ev,d,np.zeros(len(ev),bool))
        real=passrate(ev,d,we)
        k=int(we.sum())
        rand=[]
        for _ in range(200):
            m=np.zeros(len(ev),bool); m[rng.choice(len(ev),k,replace=False)]=True
            rand.append(passrate(ev,d,m))
        rand=np.array(rand)
        pct=(rand<real).mean()*100
        print(f"  {s.upper():6s} {lab:12s} {base:7.1f}% {real:10.1f}% "
              f"{rand.mean():15.1f}% {rand.std():8.1f} {pct:9.0f}%")
        summary[(s,lab)]=(base,real,rand.mean(),pct)

print("\n"+"="*92)
print("Zusammenfassung")
print("="*92)
for lab in ("Suchzeitraum","Holdout"):
    v=[(b,r,m,p) for (a,l),(b,r,m,p) in summary.items() if l==lab]
    if not v: continue
    b,r,m,p=map(np.mean,zip(*v))
    print(f"  {lab:14s} ohne {b:5.1f}%  Wochenendfilter {r:5.1f}%  "
          f"Zufallsfilter {m:5.1f}%  -> Vorsprung gegen Zufall {r-m:+.1f} pp")
    print(f"  {'':14s} mittleres Perzentil in der Zufallsverteilung: {p:.0f} %")
