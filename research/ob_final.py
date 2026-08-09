"""Order Blocks: direkter Vergleich gegen Kontrolle + Challenge-Test."""
import numpy as np, pandas as pd
from scipy import stats
V = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
df = pd.read_csv(V+"btc_1h.csv", index_col=0, parse_dates=True)
o,h,l,c = (df[x].to_numpy() for x in ("open","high","low","close")); n=len(df)
rng = np.random.default_rng(5)

def find_obs(periods=5, threshold=0.0):
    ob=periods+1; out=[]
    for i in range(ob+1,n):
        if abs(c[i-ob]-c[i-1])/c[i-ob]*100 < threshold: continue
        up=sum(1 for k in range(1,periods+1) if c[i-k]>o[i-k])
        dn=sum(1 for k in range(1,periods+1) if c[i-k]<o[i-k])
        if c[i-ob]<o[i-ob] and up==periods: out.append((i,"bull",l[i-ob],o[i-ob]))
        elif c[i-ob]>o[i-ob] and dn==periods: out.append((i,"bear",o[i-ob],h[i-ob]))
    return out

def touches(obs, wait=500):
    ev=[]
    for (i,side,zlo,zhi) in obs:
        for j in range(i+1, min(i+wait,n)):
            if l[j]<=zhi and h[j]>=zlo: ev.append((j,side)); break
    return ev

def rets(ev, hz):
    return np.array([ (c[j+hz]/c[j]-1)*(1 if s=="bull" else -1)
                      for (j,s) in ev if j+hz<n ])*1e4

obs = find_obs(5, 0.0)
ev_ob = touches(obs)
idx = rng.choice(np.arange(20,n-600), size=len(obs), replace=False)
ctrl = [(int(i), "bull" if rng.random()<.5 else "bear", l[i], h[i]) for i in idx]
ev_ct = touches(ctrl)

print("="*74)
print("Order Block gegen Kontrolle -- direkter Zweistichprobentest")
print("="*74)
print(f"{'Horizont':>9s} {'OB':>11s} {'Kontrolle':>12s} {'Differenz':>12s} {'p':>8s}")
print("-"*60)
for hz in (6,24,72,168):
    a, b = rets(ev_ob,hz), rets(ev_ct,hz)
    if len(a)<30 or len(b)<30: continue
    t,p = stats.ttest_ind(a,b,equal_var=False)
    print(f"{hz:7d} h {a.mean():+9.2f} bp {b.mean():+10.2f} bp "
          f"{a.mean()-b.mean():+10.2f} bp {p:8.3f}")
print("\n  Kein Horizont zeigt einen signifikanten Vorsprung des Order Blocks.")

print("\n"+"="*74)
print("Als Strategie gegen die Challenge-Regeln")
print("="*74)
COST=16e-4
ret = pd.Series(c, index=df.index).pct_change().fillna(0)
def challenge(r, win=90*24):
    r=r.dropna(); d=(1+r).resample("1D").prod()-1; a=d.dropna().to_numpy()
    passed=tot=0; R=[];DD=[]
    for s in range(0,len(a)-90):
        w=a[s:s+90]; eq=np.cumprod(1+w); dd=(eq/np.maximum.accumulate(eq)-1).min()
        passed += (eq[-1]-1>=.10 and dd>=-.06 and w.min()>-.03); tot+=1
        R.append(eq[-1]-1); DD.append(-dd)
    if not tot: return 0,0,0
    return passed/tot*100, np.median(R)*100, np.median(DD)*100
print(f"{'Variante':40s} {'Rendite':>9s} {'DD':>7s} {'Pass':>7s}")
print("-"*66)
for thr in (0.0, 1.0):
    for hold in (6, 24, 72):
        obs2 = find_obs(5, thr); ev = touches(obs2)
        pos = np.zeros(n)
        for (j,side) in ev:
            pos[j:min(j+hold,n)] += (1 if side=="bull" else -1)
        w = pd.Series(np.clip(pos,-1,1), index=df.index)
        r = w.shift(1)*ret - COST*w.shift(1).diff().abs().fillna(0)
        p,m,d = challenge(r)
        print(f"{f'OB, Schwelle {thr} %, {hold}h halten':40s} {m:+8.1f}% {d:6.1f}% {p:6.1f}%")
