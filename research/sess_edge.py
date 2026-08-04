"""Traegt der S/R-Ausbruch je nach Tageszeit unterschiedlich? Vier Assets."""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
ASSETS=[("BTC","btc_1h.csv"),("ETH","eth_1h.csv"),("SOL","sol_1h.csv"),("XRP","xrp_1h.csv")]
SESS={"Asien (00-07)":range(0,8),"Europa (08-12)":range(8,13),
      "US (13-20)":range(13,21),"vor Asien (21-23)":range(21,24)}
COST=16e-4

data={}
for nm,fn in ASSETS:
    df=pd.read_csv(V+fn,index_col=0,parse_dates=True)
    by=levels.build_levels(df,width=8,tol_atr=0.5,max_age=1000)
    ev=levels.breakout_events(by,df,min_touch=6)
    data[nm]=(df,ev)

def eff(ev, c, n, hours=None, idx=None, hz=24):
    seen={}
    for (t,d,_,_) in ev:
        if hours is not None and idx[t].hour not in hours: continue
        b=t//hz
        if b not in seen and t+hz<n: seen[b]=(c[t+hz]/c[t]-1)*d
    a=np.array(list(seen.values()))*1e4
    if len(a)<12: return np.nan,np.nan,len(a)
    _,p=stats.ttest_1samp(a,0); return a.mean(),p,len(a)

print("="*96)
print("Ausbruchs-Effekt nach Session der Signalstunde")
print("="*96)
print(f"{'Session':<20s} " + "".join(f"{n:>17s}" for n,_ in ASSETS))
print(f"{'':<20s} " + "".join(f"{'Effekt   n':>17s}" for _ in ASSETS))
print("-"*96)
rows={}
for s,r in SESS.items():
    line=f"{s:<20s} "; vals=[]
    for nm,_ in ASSETS:
        df,ev=data[nm]; c=df["close"].to_numpy(); n=len(df)
        e,p,cnt=eff(ev,c,n,hours=set(r),idx=df.index)
        vals.append(e)
        line += f"{e:+10.1f}{cnt:7d}" if np.isfinite(e) else f"{'—':>10s}{cnt:7d}"
    rows[s]=vals
    print(line)
print("-"*96)
line=f"{'ALLE Stunden':<20s} "
for nm,_ in ASSETS:
    df,ev=data[nm]; c=df["close"].to_numpy(); n=len(df)
    e,p,cnt=eff(ev,c,n)
    line += f"{e:+10.1f}{cnt:7d}"
print(line)

print("\n"+"="*96)
print("Konsistenz: In wie vielen Assets ist die Session besser als der Gesamtschnitt?")
print("="*96)
base=[]
for nm,_ in ASSETS:
    df,ev=data[nm]; c=df["close"].to_numpy(); n=len(df)
    base.append(eff(ev,c,n)[0])
for s in SESS:
    v=np.array(rows[s]); b=np.array(base)
    ok=np.isfinite(v)
    better=(v[ok]>b[ok]).sum()
    print(f"  {s:<20s} besser in {better}/{ok.sum()} Assets   "
          f"(Mittel {np.nanmean(v):+.1f} bp gegen {np.nanmean(b):+.1f} bp)")

print("\n"+"="*96)
print("Praktischer Test: nur in der besten Session handeln?")
print("="*96)
def passrate(ev, df, hours=None, hold=48, lev=0.5):
    c=df["close"].to_numpy(); n=len(df); idx=df.index
    ret=pd.Series(c,index=idx).pct_change().fillna(0)
    pos=np.zeros(n)
    for (t,d,_,_) in ev:
        if hours is not None and idx[t].hour not in hours: continue
        pos[t:min(t+hold,n)]+=d
    w=pd.Series(np.clip(pos,-1,1),index=idx).astype(float)*lev
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
    return p/tot*100 if tot else 0
print(f"{'Filter':<20s} " + "".join(f"{n:>10s}" for n,_ in ASSETS) + f"{'Mittel':>10s}")
print("-"*74)
for lab,hrs in [("keiner",None)]+[(s,set(r)) for s,r in SESS.items()]:
    vals=[passrate(data[n][1],data[n][0],hours=hrs) for n,_ in ASSETS]
    print(f"{lab:<20s} " + "".join(f"{v:9.1f}%" for v in vals) + f"{np.mean(vals):9.1f}%")
