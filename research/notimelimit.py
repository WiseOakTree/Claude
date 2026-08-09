"""Kraken OHNE Zeitlimit: Erstpassage-Problem statt 90-Tage-Fenster.

Frage: Wird +10 % erreicht, BEVOR -6 % (statisch vom Start) erreicht wird?
Wichtig: Versuche, die am Datenende noch offen sind, werden als ZENSIERT
ausgewiesen -- nicht als bestanden oder gescheitert gezaehlt.
"""
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
w=pd.Series(np.clip(pos,-1,1),index=df.index).astype(float).shift(1)
sr=w*ret-COST*w.diff().abs().fillna(0)
rv=np.log(px).diff().rolling(24*30).std()*np.sqrt(24*365)*100
sz=(15.0/rv).clip(upper=2.0).fillna(0).shift(1)
vtr=sz*ret-COST*sz.diff().abs().fillna(0)
def daily(s): return ((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()
CAND={"BTC einfach halten":daily(ret),"Vol-Targeting 15 %":daily(vtr),
      "S/R-Ausbruch (>=6, 48h)":daily(sr)}

def first_passage(d, target=.10, max_dd=.06, daily_lim=.03):
    """Ohne Zeitlimit. Gibt (Pass %, Fail %, offen %, Median-Dauer) zurueck."""
    p=f=cens=0; dur=[]
    for s in range(0, len(d)-1):
        eq=1.0; done=None
        for i in range(s, len(d)):
            r=d[i]
            if r < -daily_lim: done="f"; break
            eq*=(1+r)
            if eq <= 1-max_dd: done="f"; break
            if eq-1 >= target: done="p"; dur.append(i-s+1); break
        if done=="p": p+=1
        elif done=="f": f+=1
        else: cens+=1
    tot=p+f+cens
    resolved = p+f
    return (p/tot*100, f/tot*100, cens/tot*100,
            p/resolved*100 if resolved else 0, np.median(dur) if dur else np.nan)

print("="*90)
print("Kraken Starter OHNE Zeitlimit  (10 % Ziel, 6 % statischer DD, 3 % Tagesverlust)")
print("="*90)
print(f"{'Strategie':26s} {'bestanden':>10s} {'gescheitert':>12s} {'offen':>8s} "
      f"{'Quote*':>8s} {'Ø Dauer':>10s}")
print("-"*90)
for nm,d in CAND.items():
    p,f,cn,q,dur = first_passage(d)
    print(f"{nm:26s} {p:9.1f}% {f:11.1f}% {cn:7.1f}% {q:7.1f}% {dur:7.0f} Tage")
print("\n  * Quote = bestanden / (bestanden + gescheitert), also ohne die am")
print("    Datenende noch offenen Versuche. Das ist die belastbarere Zahl.")

print("\n"+"="*90)
print("Direktvergleich meiner Modellannahmen")
print("="*90)
def windowed(d, days, target=.10, max_dd=.06, daily_lim=.03):
    p=t=0
    for s in range(0,len(d)-days):
        eq=1.0; ok=None
        for i in range(s,s+days):
            r=d[i]
            if r<-daily_lim: ok=False;break
            eq*=(1+r)
            if eq<=1-max_dd: ok=False;break
            if eq-1>=target: ok=True;break
        if ok is None: ok=False
        p+=ok;t+=1
    return p/t*100 if t else 0
print(f"{'Strategie':26s} {'90 T (falsch)':>14s} {'180 T':>9s} {'365 T':>9s} {'ohne Limit*':>13s}")
print("-"*76)
for nm,d in CAND.items():
    _,_,_,q,_ = first_passage(d)
    print(f"{nm:26s} {windowed(d,90):13.1f}% {windowed(d,180):8.1f}% "
          f"{windowed(d,365):8.1f}% {q:12.1f}%")

print("\n"+"="*90)
print("Was scheitern laesst: Drawdown oder Tagesverlust?")
print("="*90)
for nm,d in CAND.items():
    dd_fail=dl_fail=0
    for s in range(0,len(d)-1):
        eq=1.0
        for i in range(s,len(d)):
            r=d[i]
            if r<-.03: dl_fail+=1; break
            eq*=(1+r)
            if eq<=.94: dd_fail+=1; break
            if eq-1>=.10: break
    tot=dd_fail+dl_fail
    if tot:
        print(f"  {nm:26s} 6 %-Drawdown {dd_fail/tot*100:5.1f} %   "
              f"3 %-Tagesverlust {dl_fail/tot*100:5.1f} %")
