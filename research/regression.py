"""Gegenprobe: levels.py muss dieselben Zahlen liefern wie research/sr_breakout.py."""
import sys; sys.path.insert(0,"/home/user/Claude/src")
import numpy as np, pandas as pd
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
df=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
c=df["close"].to_numpy(); n=len(df)

# ---- alte Referenzimplementierung (aus research/sr_breakout.py, wortgleich) ----
o,h,l=(df[x].to_numpy() for x in ("open","high","low"))
atr=pd.Series(np.maximum.reduce([h-l,abs(h-np.roll(c,1)),abs(l-np.roll(c,1))])
              ).ewm(alpha=1/14,adjust=False).mean().to_numpy()
def old_pivots(w=8):
    out=[]
    for i in range(w,n-w):
        if h[i]==h[i-w:i+w+1].max(): out.append((i+w,h[i],"R"))
        if l[i]==l[i-w:i+w+1].min(): out.append((i+w,l[i],"S"))
    return sorted(out)
def old_build(pv,tol=.5,age=1000):
    lv=[];by={};pi=0
    for t in range(n):
        while pi<len(pv) and pv[pi][0]<=t:
            _,p_,k=pv[pi];pi+=1;tl=tol*atr[min(t,n-1)];hit=None
            for L in lv:
                if L[1]==k and abs(L[0]-p_)<=tl: hit=L;break
            if hit: hit[0]=(hit[0]*hit[2]+p_)/(hit[2]+1);hit[2]+=1;hit[3]=t
            else: lv.append([p_,k,1,t])
        lv=[L for L in lv if t-L[3]<=age]; by[t]=[tuple(L) for L in lv]
    return by
def old_breaks(by,mt=6):
    ev=[]
    for t in range(1,n):
        for (p_,k,tc,_) in by.get(t-1,[]):
            if tc<mt: continue
            if k=="R" and c[t-1]<=p_<c[t]: ev.append((t,+1))
            elif k=="S" and c[t-1]>=p_>c[t]: ev.append((t,-1))
    return ev

old_ev = old_breaks(old_build(old_pivots()))
new_by = levels.build_levels(df, width=8, tol_atr=0.5, max_age=1000)
new_ev = [(t,d) for (t,d,_,_) in levels.breakout_events(new_by, df, min_touch=6)]

def eff(ev,hz=24):
    r=np.array([(c[t+hz]/c[t]-1)*d for (t,d) in ev if t+hz<n])*1e4
    return len(r), r.mean()

no,eo = eff(old_ev); nn,en = eff(new_ev)
print("="*66)
print("Gegenprobe: alte Referenz gegen src/prop_backtester/levels.py")
print("="*66)
print(f"  {'':22s} {'Ereignisse':>12s} {'Effekt 24h':>13s}")
print(f"  {'alt (research/)':22s} {len(old_ev):12d} {eo:+10.2f} bp")
print(f"  {'neu (levels.py)':22s} {len(new_ev):12d} {en:+10.2f} bp")
print()
same = old_ev == new_ev
print(f"  Signale identisch: {same}")
if not same:
    so,sn=set(old_ev),set(new_ev)
    print(f"    nur alt: {len(so-sn)}   nur neu: {len(sn-so)}   gemeinsam: {len(so&sn)}")
    print(f"    Beispiele nur neu: {sorted(sn-so)[:5]}")
    print(f"    Beispiele nur alt: {sorted(so-sn)[:5]}")
print(f"\n  Erwartet laut docs/sr_breakout.md: 775 Ereignisse, +42,88 bp")
