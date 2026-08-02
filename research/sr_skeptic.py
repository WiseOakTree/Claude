"""Die Haerteprüfung des S/R-Befunds: ist es Drift, Auswahl oder echt?"""
import numpy as np, pandas as pd
from scipy import stats
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

print("="*80)
print("1) Long gegen Short -- ist der Effekt nur BTC-Aufwaertsdrift?")
print("="*80)
print(f"{'Ber.':>5s} {'Long n':>7s} {'Long 24h':>10s} {'Short n':>8s} {'Short 24h':>11s}")
print("-"*50)
for mt in (2,4,5,6):
    ev=breaks(by,mt)
    L=np.array([(c[t+24]/c[t]-1) for (t,d) in ev if d>0 and t+24<n])*1e4
    S=np.array([-(c[t+24]/c[t]-1) for (t,d) in ev if d<0 and t+24<n])*1e4
    print(f"{mt:5d} {len(L):7d} {L.mean():+9.2f} {len(S):8d} {S.mean():+10.2f}")
drift = (c[24:]/c[:-24]-1).mean()*1e4
print(f"\n  Mittlere 24h-Rendite von BTC insgesamt (Drift): {drift:+.2f} bp")

print("\n"+"="*80)
print("2) Korrekte n_eff: Ereignisse in 24h-Bloecke gruppieren")
print("="*80)
print(f"{'Ber.':>5s} {'Ereign.':>8s} {'unabh. Bloecke':>15s} {'24h':>9s} {'p korr.':>9s}")
print("-"*55)
for mt in (4,5,6):
    ev=breaks(by,mt)
    blocks={}
    for (t,d) in ev:
        b=t//24
        if b not in blocks: blocks[b]=[]
        blocks[b].append((t,d))
    # je Block eine Beobachtung (die erste)
    obs=[]
    for b,items in blocks.items():
        t,d=items[0]
        if t+24<n: obs.append((c[t+24]/c[t]-1)*d)
    a=np.array(obs)*1e4
    t_,p=stats.ttest_1samp(a,0)
    print(f"{mt:5d} {len(ev):8d} {len(a):15d} {a.mean():+8.2f} {p:9.4f}")

print("\n"+"="*80)
print("3) Jahresweise Stabilitaet (>=5 Beruehrungen, 24h)")
print("="*80)
ev=breaks(by,5)
idx=df.index
for yr in sorted(set(idx.year)):
    a=np.array([(c[t+24]/c[t]-1)*d for (t,d) in ev if t+24<n and idx[t].year==yr])*1e4
    if len(a)<20: continue
    print(f"  {yr}: n={len(a):4d}   {a.mean():+8.2f} bp"
          + ("   negativ!" if a.mean()<0 else ""))

print("\n"+"="*80)
print("4) Kontrolle: gleicher Bar, gleiche Richtung, ABER zufaelliger Zeitpunkt")
print("="*80)
rng=np.random.default_rng(4)
for mt in (5,6):
    ev=breaks(by,mt)
    real=np.array([(c[t+24]/c[t]-1)*d for (t,d) in ev if t+24<n])*1e4
    ctrl=[]
    for (t,d) in ev:
        tt=int(rng.integers(30,n-30))
        ctrl.append((c[tt+24]/c[tt]-1)*d)
    ctrl=np.array(ctrl)*1e4
    _,p=stats.ttest_ind(real,ctrl,equal_var=False)
    print(f"  >={mt} Ber.: echt {real.mean():+7.2f} bp | Kontrolle {ctrl.mean():+7.2f} bp"
          f" | Differenz {real.mean()-ctrl.mean():+7.2f} bp (p={p:.4f})")
