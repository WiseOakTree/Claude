"""Wochenend-Effekt: Sind Ausbrueche bei duenner Liquiditaet Fehlausbrueche?

Fenster wie vorgeschlagen: Freitag 22:00 UTC bis Sonntag 22:00 UTC.
Vier Assets, Suchzeitraum und Holdout getrennt.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
ASSETS=["btc","eth","sol","xrp"]; SPLIT=pd.Timestamp("2025-01-01",tz="UTC"); COST=16e-4

def is_weekend(idx):
    """Fr 22:00 UTC .. So 22:00 UTC. Gibt immer ein numpy-Array zurueck."""
    dow=np.asarray(idx.dayofweek); hr=np.asarray(idx.hour)
    return ((dow==4)&(hr>=22)) | (dow==5) | ((dow==6)&(hr<22))

DATA={}
for s in ASSETS:
    d=pd.read_csv(V+f"{s}_1h.csv",index_col=0,parse_dates=True)
    by=levels.build_levels(d,width=8,tol_atr=0.5,max_age=1000)
    DATA[s]=(d, by, levels.breakout_events(by,d,min_touch=6))

print("="*92)
print("0) Stimmt die Praemisse? Liquiditaet und Bewegung am Wochenende")
print("="*92)
print(f"  {'Asset':6s} {'Volumen WE/Werktag':>20s} {'Bewegung WE/Werktag':>22s}")
print("  "+"-"*50)
for s in ASSETS:
    d=DATA[s][0]; we=is_weekend(d.index)
    vr=d["volume"][we].mean()/d["volume"][~we].mean()
    ar=(d["close"].pct_change().abs()[we].mean()/
        d["close"].pct_change().abs()[~we].mean())
    print(f"  {s.upper():6s} {vr:19.2f}x {ar:21.2f}x")

def eff(ev, d, mask=None, hz=24):
    c=d["close"].to_numpy(); n=len(d); idx=d.index
    seen={}
    for (t,dr,_,_) in ev:
        if mask is not None and not mask[t]: continue
        b=t//hz
        if b not in seen and t+hz<n: seen[b]=(c[t+hz]/c[t]-1)*dr
    a=np.array(list(seen.values()))*1e4
    if len(a)<10: return np.nan,np.nan,len(a)
    _,p=stats.ttest_1samp(a,0); return a.mean(),p,len(a)

for lab,filt in (("SUCHZEITRAUM (bis 2024-12)", lambda i: i<SPLIT),
                 ("HOLDOUT (ab 2025-01)",       lambda i: i>=SPLIT)):
    print(f"\n{'='*92}\n{lab}\n{'='*92}")
    print(f"  {'Asset':6s} {'Wochenende':>22s} {'Werktag':>22s} {'Differenz':>12s}")
    print(f"  {'':6s} {'Effekt    n      p':>22s} {'Effekt    n      p':>22s}")
    print("  "+"-"*66)
    for s in ASSETS:
        d,by,ev=DATA[s]
        keep=filt(d.index)
        sub=d[keep]; off=np.where(keep)[0]
        lo=off.min() if len(off) else 0
        ev2=[(t-lo,dr,tc,lv) for (t,dr,tc,lv) in ev if keep[t]]
        we=is_weekend(sub.index)
        ew,pw,nw=eff(ev2,sub,mask=we)
        ed,pd_,nd=eff(ev2,sub,mask=~we)
        diff = ew-ed if (np.isfinite(ew) and np.isfinite(ed)) else np.nan
        fm=lambda e,n,p: (f"{e:+8.1f}{n:5d}{p:7.3f}" if np.isfinite(e)
                          else f"{'zu wenige':>20s}")
        dtxt=f"{diff:+11.1f}" if np.isfinite(diff) else f"{'—':>11s}"
        print(f"  {s.upper():6s} {fm(ew,nw,pw):>22s} {fm(ed,nd,pd_):>22s} {dtxt}")

print("\n"+"="*92)
print("Als Filter: Pass-Rate mit und ohne Wochenend-Ausschluss (0,5x)")
print("="*92)
def passrate(ev,d,skip_we,hold=48,lev=0.5):
    c=d["close"].to_numpy(); n=len(d); idx=d.index
    we=is_weekend(idx)
    ret=pd.Series(c,index=idx).pct_change().fillna(0)
    pos=np.zeros(n)
    for (t,dr,_,_) in ev:
        if skip_we and we[t]: continue
        pos[t:min(t+hold,n)]+=dr
    w=pd.Series(np.clip(pos,-1,1),index=idx).astype(float)*lev
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
print(f"  {'Asset':6s} " + "".join(f"{x:>16s}" for x in ("gesamt ohne","gesamt mit","Aenderung")))
print("  "+"-"*54)
tot_a=[];tot_b=[]
for s in ASSETS:
    d,by,ev=DATA[s]
    a=passrate(ev,d,False); b=passrate(ev,d,True)
    tot_a.append(a); tot_b.append(b)
    print(f"  {s.upper():6s} {a:15.1f}% {b:15.1f}% {b-a:+15.1f}")
print(f"  {'Mittel':6s} {np.mean(tot_a):15.1f}% {np.mean(tot_b):15.1f}% "
      f"{np.mean(tot_b)-np.mean(tot_a):+15.1f}")
