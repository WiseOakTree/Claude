"""Prueft die VEREINFACHTE Pine-Logik gegen die getestete Backtest-Logik.

Pine: nur eine Position, neue Signale werden waehrend der Haltedauer ignoriert.
Backtest: ueberlappende Signale summiert und auf +/-1 begrenzt.
"""
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

def signals(mt=6):
    ev=[]
    for t in range(1,n):
        for (p_,k,tc,_) in by.get(t-1,[]):
            if tc<mt: continue
            if k=="R" and c[t-1]<=p_<c[t]: ev.append((t,+1)); break
            elif k=="S" and c[t-1]>=p_>c[t]: ev.append((t,-1)); break
    return ev
ev = signals(6)

# A) Backtest-Logik: ueberlappend, geclippt
posA=np.zeros(n)
for (t,d) in ev: posA[t:min(t+48,n)] += d
wA=pd.Series(np.clip(posA,-1,1),index=df.index).astype(float)

# B) Pine-Logik: eine Position, neue Signale waehrend Haltedauer ignoriert
posB=np.zeros(n); i=0; trades=0
ev_sorted=sorted(ev)
k=0
while k < len(ev_sorted):
    t,d = ev_sorted[k]
    posB[t:min(t+48,n)] = d
    trades += 1
    # alle Signale innerhalb der Haltedauer ueberspringen
    while k < len(ev_sorted) and ev_sorted[k][0] < t+48: k += 1
wB=pd.Series(posB,index=df.index).astype(float)

def daily(w, lev):
    ww=(w*lev).shift(1)
    s=ww*ret-COST*ww.diff().abs().fillna(0)
    return ((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()

def fp(d, cap=365):
    p=f=cn=0
    for s in range(0,len(d)-1):
        eq=1.0; done=None
        for i2 in range(s, min(s+cap,len(d))):
            r=d[i2]
            if r<-.03: done="f";break
            eq*=(1+r)
            if eq<=.94: done="f";break
            if eq-1>=.10: done="p";break
        if done=="p": p+=1
        elif done=="f": f+=1
        else: cn+=1
    tot=p+f+cn
    return p/(p+f)*100 if p+f else 0, p/tot*100, cn/tot*100

print("="*74)
print(f"Signale gesamt: {len(ev)}  |  davon in der Pine-Logik gehandelt: {trades}")
print("="*74)
print(f"{'Groesse':>9s} {'Backtest (ueberlappend)':>26s} {'Pine (eine Position)':>24s}")
print(f"{'':9s} {'Quote':>12s} {'Untergr.':>12s} {'Quote':>11s} {'Untergr.':>12s}")
print("-"*74)
for lev in (1.0, 0.5, 0.35):
    qa, ua, _ = fp(daily(wA, lev))
    qb, ub, _ = fp(daily(wB, lev))
    print(f"{lev:8.2f}x {qa:11.1f}% {ua:11.1f}% {qb:10.1f}% {ub:11.1f}%")

print("\n" + "="*74)
print("Wie oft ist man ueberhaupt im Markt?")
print("="*74)
print(f"  Backtest-Logik: {(wA!=0).mean()*100:5.1f} % der Zeit")
print(f"  Pine-Logik:     {(wB!=0).mean()*100:5.1f} % der Zeit")
print(f"\n  Handelstage je Jahr (Pine): {trades/4.5:.0f} Trades")
