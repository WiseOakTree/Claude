"""Teil 3: Der faire Kopf-an-Kopf-Vergleich.

Meine validierte Regel benutzt Level aus PIVOTS. Volume Profile liefert
Level aus VOLUMEN (POC frueherer Perioden). Gleiche Mechanik, gleiche
Auswertung, gleicher Zeitraum -- welche Levelart traegt mehr?
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/home/user/Claude/src")
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from vp import load, profile, value_area, SPLIT, COST
from prop_backtester import levels as LV
H=48

def poc_levels(df, periode="W", nb=100):
    """Je Periode ein POC + Value-Area-Grenzen. Ab der FOLGENDEN Periode gueltig."""
    g=df.groupby(df.index.to_period(periode))
    out=[]
    for per,sub in g:
        if len(sub)<24: continue
        lo,hi=sub.low.min(),sub.high.max()
        if hi<=lo: continue
        pr,ct=profile(sub.high.to_numpy(),sub.low.to_numpy(),sub.volume.to_numpy(),lo,hi,nb)
        p,a,b=value_area(pr,ct)
        out.append((per.end_time.tz_localize(sub.index.tz) if sub.index.tz else per.end_time, p,a,b))
    return out

def test_levels(df, lv_list, kind="poc", tol=0.0):
    """Bruch eines Levels -> Richtung = Kreuzungsrichtung. 48 h halten."""
    c=df.close.to_numpy(); idx=df.index
    f=np.full(len(c),np.nan); f[:-H]=c[H:]/c[:-H]-1
    ev=[]
    for i,(t_end,p,a,b) in enumerate(lv_list[:-1]):
        # gilt ab Periodenende bis zum naechsten
        t_next=lv_list[i+1][0]
        m=(idx>t_end)&(idx<=t_next)
        pos=np.where(m)[0]
        if len(pos)<2: continue
        prices={"poc":[p],"va":[a,b]}[kind]
        for price in prices:
            for k in range(1,len(pos)):
                t=pos[k]; t0=pos[k-1]
                if c[t0]<=price<c[t]:  d=1
                elif c[t0]>=price>c[t]: d=-1
                else: continue
                if not np.isfinite(f[t]): continue
                ev.append((idx[t], d*f[t]-2*COST))
    return pd.DataFrame(ev,columns=["ts","ret"])

def rep(name,E):
    for nm,m in (("Suche 21-24",E.ts<SPLIT),("HOLDOUT 25-26",E.ts>=SPLIT)):
        s=E[m]
        if len(s)<20: continue
        t=s.ret.mean()/(s.ret.std(ddof=1)/np.sqrt(max(len(s)/H,2)))
        print(f"  {name:<34}{nm:<16}{len(s):>6}{s.ret.mean()*1e4:>+9.1f} bp{t:>7.2f}")

print("="*88)
print("KOPF AN KOPF: Level aus Volumen gegen Level aus Pivots (BTC 1h, 48 h halten)")
print("="*88)
print(f"  {'Levelart':<34}{'Zeitraum':<16}{'n':>6}{'Effekt':>12}{'t':>7}")
df=load("btc")
for per,lab in (("W","POC der Vorwoche"),("M","POC des Vormonats")):
    lv=poc_levels(df,per)
    rep(lab, test_levels(df,lv,"poc"))
    rep(lab.replace("POC","Value-Area-Grenzen"), test_levels(df,lv,"va"))
    print()
# Referenz: die validierte Pivot-Regel
by=LV.build_levels(df); ev=LV.breakout_events(by,df,min_touch=6)
c=df.close.to_numpy(); f=np.full(len(c),np.nan); f[:-H]=c[H:]/c[:-H]-1
rows=[(df.index[t], d*f[t]-2*COST) for t,d,_,_ in ev if np.isfinite(f[t])]
rep("S/R aus Pivots (validiert)", pd.DataFrame(rows,columns=["ts","ret"]))
