"""Ohne Zeitlimit: Wie klein muss man handeln, damit das Tageslimit nie greift?"""
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
base_sr=pd.Series(np.clip(pos,-1,1),index=df.index).astype(float).shift(1)
rv=np.log(px).diff().rolling(24*30).std()*np.sqrt(24*365)*100
base_vt=(15.0/rv).clip(upper=2.0).fillna(0).shift(1)

def daily_from(wser, lev):
    w = wser*lev
    s = w*ret - COST*w.diff().abs().fillna(0)
    return ((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()

def fp(d, target=.10, max_dd=.06, daily_lim=.03):
    p=f=cn=0; dur=[]
    for s in range(0,len(d)-1):
        eq=1.0; done=None
        for i in range(s,len(d)):
            r=d[i]
            if r<-daily_lim: done="f";break
            eq*=(1+r)
            if eq<=1-max_dd: done="f";break
            if eq-1>=target: done="p";dur.append(i-s+1);break
        if done=="p": p+=1
        elif done=="f": f+=1
        else: cn+=1
    res=p+f
    return (p/res*100 if res else 0, np.median(dur) if dur else np.nan, cn/(p+f+cn)*100)

print("="*88)
print("OHNE Zeitlimit: Positionsgroesse herunterskalieren")
print("(Kraken Starter: 10 % Ziel, 6 % statischer DD, 3 % Tagesverlust)")
print("="*88)
for nm, base in (("S/R-Ausbruch", base_sr), ("Vol-Targeting 15 %", base_vt),
                 ("BTC halten", pd.Series(1.0, index=df.index))):
    print(f"\n  {nm}")
    print(f"  {'Hebel':>7s} {'Quote':>8s} {'Ø Dauer':>11s} {'offen':>8s}")
    print("  " + "-"*38)
    for lev in (1.0, 0.7, 0.5, 0.35, 0.25, 0.15):
        q, dur, cn = fp(daily_from(base, lev))
        d_txt = f"{dur:.0f} Tage" if np.isfinite(dur) else "—"
        print(f"  {lev:6.2f}x {q:7.1f}% {d_txt:>11s} {cn:7.1f}%")

print("\n"+"="*88)
print("Warum das funktioniert: Haeufigkeit von Tagen unter -3 %")
print("="*88)
print(f"{'Hebel':>7s} {'S/R: Tage < -3 %':>18s} {'BTC: Tage < -3 %':>18s}")
print("-"*46)
for lev in (1.0,0.7,0.5,0.35,0.25,0.15):
    a=daily_from(base_sr,lev); b=daily_from(pd.Series(1.0,index=df.index),lev)
    print(f"{lev:6.2f}x {(a<-.03).mean()*100:17.2f}% {(b<-.03).mean()*100:17.2f}%")
