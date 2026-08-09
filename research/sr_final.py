"""S/R-Ausbruch: Ueberlappungskorrektur, starke Level, Out-of-Sample."""
import numpy as np, pandas as pd
from scipy import stats
V = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
df = pd.read_csv(V+"btc_1h.csv", index_col=0, parse_dates=True)
o,h,l,c = (df[x].to_numpy() for x in ("open","high","low","close")); n=len(df)
atr = pd.Series(np.maximum.reduce([h-l, abs(h-np.roll(c,1)), abs(l-np.roll(c,1))])
                ).ewm(alpha=1/14, adjust=False).mean().to_numpy()

def pivots(w=8):
    out=[]
    for i in range(w, n-w):
        if h[i]==h[i-w:i+w+1].max(): out.append((i+w,h[i],"R"))
        if l[i]==l[i-w:i+w+1].min(): out.append((i+w,l[i],"S"))
    return sorted(out)
def build(pv, tol_atr=.5, max_age=1000):
    levels=[]; by={}; pi=0
    for t in range(n):
        while pi<len(pv) and pv[pi][0]<=t:
            _,price,kind = pv[pi]; pi+=1
            tol=tol_atr*atr[min(t,n-1)]; hit=None
            for L in levels:
                if L[1]==kind and abs(L[0]-price)<=tol: hit=L; break
            if hit: hit[0]=(hit[0]*hit[2]+price)/(hit[2]+1); hit[2]+=1; hit[3]=t
            else: levels.append([price,kind,1,t])
        levels=[L for L in levels if t-L[3]<=max_age]
        by[t]=[tuple(L) for L in levels]
    return by
def breaks(by, mt):
    ev=[]
    for t in range(1,n):
        for (p,k,tc,_) in by.get(t-1,[]):
            if tc<mt: continue
            if k=="R" and c[t-1]<=p<c[t]: ev.append((t,+1))
            elif k=="S" and c[t-1]>=p>c[t]: ev.append((t,-1))
    return ev

by = build(pivots(8))
print("="*80)
print("1) Signifikanz MIT Ueberlappungskorrektur (Ereignisse ueberlappen stark)")
print("="*80)
print(f"{'Ber.':>5s} {'Ereign.':>8s} {'24h':>9s} {'p naiv':>9s} {'n_eff':>7s} {'p korr.':>9s} {'vs 16bp':>8s}")
print("-"*80)
for mt in (2,3,4,5,6,8):
    ev = breaks(by, mt)
    r = np.array([(c[t+24]/c[t]-1)*d for (t,d) in ev if t+24<n])*1e4
    if len(r)<30: continue
    t_,p = stats.ttest_1samp(r,0)
    # ueberlappungskorrigiert: unabhaengig sind hoechstens n/24 Beobachtungen
    n_eff = min(len(r), n/24)
    t_adj = r.mean()/(r.std()/np.sqrt(n_eff))
    p_adj = 2*(1-stats.t.cdf(abs(t_adj), max(n_eff-1,1)))
    print(f"{mt:5d} {len(ev):8d} {r.mean():+8.2f} {p:9.4f} {n_eff:7.0f} {p_adj:9.4f} "
          f"{abs(r.mean())/16:7.2f}x")

print("\n"+"="*80)
print("2) Out-of-Sample: haelt die Dosis-Wirkung in beiden Haelften?")
print("="*80)
half = n//2
print(f"{'Ber.':>5s} {'1. Haelfte (24h)':>20s} {'2. Haelfte (24h)':>20s}")
print("-"*50)
for mt in (2,3,4,5,6):
    ev = breaks(by, mt)
    a = np.array([(c[t+24]/c[t]-1)*d for (t,d) in ev if t+24<n and t<half])*1e4
    b = np.array([(c[t+24]/c[t]-1)*d for (t,d) in ev if t+24<n and t>=half])*1e4
    if len(a)<20 or len(b)<20: continue
    print(f"{mt:5d} {a.mean():+15.2f} bp {b.mean():+15.2f} bp")

print("\n"+"="*80)
print("3) Starke Level als Strategie (nur >=5 Beruehrungen, sauber gerechnet)")
print("="*80)
COST=16e-4
ret = pd.Series(c, index=df.index).pct_change().fillna(0)
def challenge(r):
    d=(1+r.dropna()).resample("1D").prod()-1; a=d.dropna().to_numpy()
    passed=tot=0; R=[];DD=[]
    for s in range(0,len(a)-90):
        w=a[s:s+90]; eq=np.cumprod(1+w); dd=(eq/np.maximum.accumulate(eq)-1).min()
        passed += (eq[-1]-1>=.10 and dd>=-.06 and w.min()>-.03); tot+=1
        R.append(eq[-1]-1); DD.append(-dd)
    return (passed/tot*100,np.median(R)*100,np.median(DD)*100) if tot else (0,0,0)
print(f"{'Variante':40s} {'Trades':>7s} {'Rendite':>9s} {'DD':>7s} {'Pass':>7s}")
print("-"*74)
for mt in (5,6,8):
    for hold in (24,72):
        ev = breaks(by, mt)
        pos=np.zeros(n)
        for (t,d) in ev: pos[t:min(t+hold,n)] += d
        w = pd.Series(np.sign(pos), index=df.index)     # nur Richtung, kein Stapeln
        r = w.shift(1)*ret - COST*w.shift(1).diff().abs().fillna(0)
        p,m,dd = challenge(r)
        turn = w.diff().abs().sum()
        print(f"{f'>={mt} Ber., {hold}h halten':40s} {len(ev):7d} {m:+8.1f}% {dd:6.1f}% {p:6.1f}%"
              + f"   Umsatz {turn:.0f}x")
