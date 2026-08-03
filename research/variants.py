"""Varianten der Signallogik -- Suchzeitraum 2021-03..2024-12."""
import sys, itertools, warnings; sys.path.insert(0,"/home/user/Claude/src")
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
full=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
df=full[full.index<pd.Timestamp("2025-01-01",tz="UTC")].copy()
c=df["close"].to_numpy(); n=len(df)
ret=pd.Series(c,index=df.index).pct_change().fillna(0)
by=levels.build_levels(df,width=8,tol_atr=0.5,max_age=1000)
COST=16e-4; HZ=24

def effect(ev):
    seen={}
    for (t,d,_,_) in ev:
        b=t//HZ
        if b not in seen and t+HZ<n: seen[b]=(c[t+HZ]/c[t]-1)*d
    a=np.array(list(seen.values()))*1e4
    if len(a)<20: return np.nan, np.nan, len(a)
    _,p=stats.ttest_1samp(a,0)
    return a.mean(), p, len(a)

def passrate(ev, hold=24, lev=0.5):
    pos=np.zeros(n)
    for (t,d,_,_) in ev: pos[t:min(t+hold,n)]+=d
    w=pd.Series(np.clip(pos,-1,1),index=df.index).astype(float)*lev
    held=w.shift(1)
    s=held*ret-COST*held.diff().abs().fillna(0)
    d_=((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()
    p=f=cn=0
    for st in range(0,len(d_)-1):
        eq=1.0; done=None
        for i in range(st,min(st+365,len(d_))):
            r=d_[i]
            if r<-.03: done="f";break
            eq*=(1+r)
            if eq<=.94: done="f";break
            if eq-1>=.10: done="p";break
        if done=="p": p+=1
        elif done=="f": f+=1
        else: cn+=1
    tot=p+f+cn
    return (p/(p+f)*100 if p+f else 0, p/tot*100)

rows=[]
for pen, role, cd in itertools.product((0.0,0.1,0.25,0.5), ("fixed","position"), (0,24,48)):
    ev=levels.breakout_events(by,df,min_touch=6,min_pen_atr=pen,role=role,cooldown=cd)
    e,p,neff=effect(ev)
    q,u=passrate(ev)
    rows.append(dict(pen=pen,role=role,cd=cd,n=len(ev),eff=e,p=p,quote=q,unten=u))
r=pd.DataFrame(rows)
r.to_csv("/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/oc/variants.csv",index=False)

base = r[(r.pen==0.0)&(r.role=="fixed")&(r.cd==0)].iloc[0]
print("="*84)
print(f"Ausgangslage (heutige Logik): {base.n:.0f} Ereignisse, {base.eff:+.1f} bp, "
      f"Pass {base.unten:.1f} %")
print(f"Vereinbarte Grenze: Effektverlust > 20 % = unter {base.eff*0.8:+.1f} bp")
print("="*84)
print(f"{'Durchbr.':>9s} {'Rolle':>9s} {'Cooldown':>9s} {'Ereign.':>8s} {'Effekt':>10s} "
      f"{'p':>7s} {'Pass':>8s} {'Urteil':>10s}")
print("-"*84)
for _,x in r.iterrows():
    ok = "" if not np.isfinite(x.eff) else ("  ok" if x.eff >= base.eff*0.8 else "  -20%")
    star = " <<<" if (np.isfinite(x.eff) and x.eff>=base.eff*0.8 and x.unten>base.unten) else ""
    print(f"{x.pen:9.2f} {x.role:>9s} {x.cd:9.0f} {x.n:8.0f} {x.eff:+9.1f} bp "
          f"{x.p:7.3f} {x.unten:7.1f}% {ok:>7s}{star}")

print("\n"+"="*84)
print("Nur die Rollenkorrektur isoliert (ohne Durchbruch, ohne Cooldown)")
print("="*84)
for role in ("fixed","position"):
    x=r[(r.pen==0.0)&(r.role==role)&(r.cd==0)].iloc[0]
    print(f"  {role:9s}: {x.n:5.0f} Ereignisse, {x.eff:+7.1f} bp (p={x.p:.3f}), Pass {x.unten:5.1f} %")
d=r[(r.pen==0.0)&(r.cd==0)]
if len(d)==2:
    a=d[d.role=="fixed"].iloc[0]; b=d[d.role=="position"].iloc[0]
    print(f"\n  Zusaetzliche Ereignisse durch die Rollenkorrektur: {b.n-a.n:+.0f}")
    print(f"  Effektaenderung: {b.eff-a.eff:+.1f} bp ({(b.eff/a.eff-1)*100:+.0f} %)")
