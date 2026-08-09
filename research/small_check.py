"""Haerteprüfung: Zensierungs-Untergrenze und Out-of-Sample."""
import numpy as np, pandas as pd
V = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
df = pd.read_csv(V+"btc_1h.csv", index_col=0, parse_dates=True)
o,h,l,c=(df[x].to_numpy() for x in ("open","high","low","close")); n=len(df)
atr=pd.Series(np.maximum.reduce([h-l,abs(h-np.roll(c,1)),abs(l-np.roll(c,1))])
              ).ewm(alpha=1/14,adjust=False).mean().to_numpy()
def pivots(w=8):
    out=[]
    for i in range(w,n-w):
        if h[i]==h[i-w:i+w+1].max(): out.append((i+w,h[i],"R"))
        if l[i]==l[i-w:i+w+1].min(): out.append((i+w,l[i],"S"))
    return sorted(out)
def build(pv,tol=.5,age=1000):
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
by=build(pivots(8)); COST=16e-4
px=pd.Series(c,index=df.index); ret=px.pct_change().fillna(0)
ev=[]
for t in range(1,n):
    for (p_,k,tc,_) in by.get(t-1,[]):
        if tc<6: continue
        if k=="R" and c[t-1]<=p_<c[t]: ev.append((t,+1))
        elif k=="S" and c[t-1]>=p_>c[t]: ev.append((t,-1))
pos=np.zeros(n)
for (t,d) in ev: pos[t:min(t+48,n)] += d
base=pd.Series(np.clip(pos,-1,1),index=df.index).astype(float).shift(1)

def daily_of(lev):
    w=base*lev; s=w*ret-COST*w.diff().abs().fillna(0)
    return pd.Series(((1+s.dropna()).resample("1D").prod()-1).dropna())

def fp(d, cap=None):
    """cap = maximale Dauer in Tagen (None = bis Datenende)."""
    a=d.to_numpy(); p=f=cn=0; dur=[]
    for s in range(0,len(a)-1):
        eq=1.0; done=None
        end = len(a) if cap is None else min(s+cap, len(a))
        for i in range(s,end):
            r=a[i]
            if r<-.03: done="f";break
            eq*=(1+r)
            if eq<=.94: done="f";break
            if eq-1>=.10: done="p";dur.append(i-s+1);break
        if done=="p": p+=1
        elif done=="f": f+=1
        else: cn+=1
    tot=p+f+cn
    return dict(p=p,f=f,cn=cn, quote=p/(p+f)*100 if p+f else 0,
                unten=p/tot*100, dauer=np.median(dur) if dur else np.nan)

print("="*84)
print("1) Zensierung: obere und untere Schranke der Quote")
print("="*84)
print(f"{'Hebel':>7s} {'Quote (nur geloest)':>20s} {'UNTERGRENZE*':>14s} {'zensiert':>10s} {'Ø Dauer':>10s}")
print("-"*70)
for lev in (1.0,0.7,0.5,0.35,0.25,0.15):
    r=fp(daily_of(lev))
    dtxt=f"{r['dauer']:.0f} T" if np.isfinite(r['dauer']) else "—"
    print(f"{lev:6.2f}x {r['quote']:19.1f}% {r['unten']:13.1f}% {r['cn']/(r['p']+r['f']+r['cn'])*100:9.1f}% {dtxt:>10s}")
print("\n  * UNTERGRENZE: alle offenen Versuche als gescheitert gewertet.")
print("    Die Wahrheit liegt dazwischen; bei viel Zensierung ist die Quote unbrauchbar.")

print("\n"+"="*84)
print("2) Mit realistischer Obergrenze: max. 365 Tage Handelsdauer")
print("="*84)
print(f"{'Hebel':>7s} {'Quote':>9s} {'Untergrenze':>13s} {'zensiert':>10s}")
print("-"*44)
for lev in (1.0,0.7,0.5,0.35,0.25):
    r=fp(daily_of(lev), cap=365)
    print(f"{lev:6.2f}x {r['quote']:8.1f}% {r['unten']:12.1f}% {r['cn']/(r['p']+r['f']+r['cn'])*100:9.1f}%")

print("\n"+"="*84)
print("3) Out-of-Sample (365-Tage-Deckel, Untergrenze als Massstab)")
print("="*84)
d_all = daily_of(0.35); half=len(d_all)//2
print(f"{'Hebel':>7s} {'1. Haelfte':>12s} {'2. Haelfte':>12s}")
print("-"*34)
for lev in (1.0,0.5,0.35,0.25):
    d=daily_of(lev)
    a=fp(d.iloc[:half], cap=365); b=fp(d.iloc[half:], cap=365)
    print(f"{lev:6.2f}x {a['unten']:11.1f}% {b['unten']:11.1f}%")
