"""S/R-Ausbruch als handelbare Strategie -- mit Vol-Targeting fuer die Groesse."""
import numpy as np, pandas as pd
V = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
df = pd.read_csv(V+"btc_1h.csv", index_col=0, parse_dates=True)
o,h,l,c = (df[x].to_numpy() for x in ("open","high","low","close")); n=len(df)
atr = pd.Series(np.maximum.reduce([h-l,abs(h-np.roll(c,1)),abs(l-np.roll(c,1))])
                ).ewm(alpha=1/14,adjust=False).mean().to_numpy()
def pivots(w=8):
    out=[]
    for i in range(w,n-w):
        if h[i]==h[i-w:i+w+1].max(): out.append((i+w,h[i],"R"))
        if l[i]==l[i-w:i+w+1].min(): out.append((i+w,l[i],"S"))
    return sorted(out)
def build(pv,tol_atr=.5,max_age=1000):
    levels=[];by={};pi=0
    for t in range(n):
        while pi<len(pv) and pv[pi][0]<=t:
            _,p_,k=pv[pi];pi+=1;tol=tol_atr*atr[min(t,n-1)];hit=None
            for L in levels:
                if L[1]==k and abs(L[0]-p_)<=tol: hit=L;break
            if hit: hit[0]=(hit[0]*hit[2]+p_)/(hit[2]+1);hit[2]+=1;hit[3]=t
            else: levels.append([p_,k,1,t])
        levels=[L for L in levels if t-L[3]<=max_age]; by[t]=[tuple(L) for L in levels]
    return by
def breaks(by,mt):
    ev=[]
    for t in range(1,n):
        for (p_,k,tc,_) in by.get(t-1,[]):
            if tc<mt: continue
            if k=="R" and c[t-1]<=p_<c[t]: ev.append((t,+1))
            elif k=="S" and c[t-1]>=p_>c[t]: ev.append((t,-1))
    return ev
by=build(pivots(8))

COST=16e-4
px = pd.Series(c, index=df.index); ret = px.pct_change().fillna(0)
# stuendliche realisierte Vola -> Zielvola 15 % p.a. (Befund aus required_edge.md)
rv = np.log(px).diff().rolling(24*30).std()*np.sqrt(24*365)*100
size = (15.0/rv).clip(upper=2.0).fillna(0)

def challenge(r, split=None):
    d=(1+r.dropna()).resample("1D").prod()-1; a=d.dropna().to_numpy()
    if split=="a": a=a[:len(a)//2]
    if split=="b": a=a[len(a)//2:]
    passed=tot=0;R=[];DD=[]
    for s in range(0,len(a)-90):
        w=a[s:s+90];eq=np.cumprod(1+w);dd=(eq/np.maximum.accumulate(eq)-1).min()
        passed += (eq[-1]-1>=.10 and dd>=-.06 and w.min()>-.03); tot+=1
        R.append(eq[-1]-1);DD.append(-dd)
    return (passed/tot*100,np.median(R)*100,np.median(DD)*100) if tot else (0,0,0)

def strat(mt, hold, use_vt):
    ev=breaks(by,mt); pos=np.zeros(n)
    for (t,d) in ev: pos[t:min(t+hold,n)] += d
    w = pd.Series(np.clip(pos,-1,1), index=df.index).astype(float)
    if use_vt: w = w*size
    held = w.shift(1)
    return held*ret - COST*held.diff().abs().fillna(0)

print("="*82)
print("S/R-Ausbruch als Strategie -- mit und ohne Vol-Targeting")
print("="*82)
print(f"{'Variante':38s} {'Rendite':>9s} {'DD':>7s} {'R/DD':>6s} {'Pass':>7s}")
print("-"*72)
best=None
for mt in (4,5,6):
    for hold in (12,24,48,72):
        for vt in (False,True):
            r = strat(mt,hold,vt)
            p,m,dd = challenge(r)
            ratio = m/dd if dd>0 else 0
            tag = " +VT" if vt else "    "
            print(f"{f'>={mt} Ber., {hold}h halten{tag}':38s} {m:+8.1f}% {dd:6.1f}% "
                  f"{ratio:6.2f} {p:6.1f}%")
            if best is None or p>best[0]: best=(p,mt,hold,vt,m,dd)

p,mt,hold,vt,m,dd = best
print(f"\nBeste Variante: >={mt} Beruehrungen, {hold}h halten"
      f"{' mit Vol-Targeting' if vt else ''}")
print(f"  Pass-Rate {p:.1f} %   Rendite {m:+.1f} %   Drawdown {dd:.1f} %   "
      f"Verhaeltnis {m/dd if dd else 0:.2f} (noetig: 1,67)")

print("\n"+"="*82)
print("Out-of-Sample-Kontrolle der besten Variante")
print("="*82)
r = strat(mt,hold,vt)
for nm,sp in (("1. Haelfte","a"),("2. Haelfte","b"),("gesamt",None)):
    p2,m2,d2 = challenge(r, sp)
    print(f"  {nm:11s} Pass {p2:5.1f} %   Rendite {m2:+6.1f} %   Drawdown {d2:5.1f} %")
print("\nVergleich: reines Vol-Targeting ohne Signal")
held = size.shift(1)
r0 = held*ret - COST*held.diff().abs().fillna(0)
for nm,sp in (("1. Haelfte","a"),("2. Haelfte","b"),("gesamt",None)):
    p2,m2,d2 = challenge(r0, sp)
    print(f"  {nm:11s} Pass {p2:5.1f} %   Rendite {m2:+6.1f} %   Drawdown {d2:5.1f} %")
