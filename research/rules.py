"""Welches Regelwerk wuerde die gefundene Strategie bestehen?

Statt die Strategie an Kraken anzupassen: die Regeln variieren und sehen,
welches Profil passt. Entscheidend und bisher ungetestet: das ZEITLIMIT.
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
COST=16e-4
px=pd.Series(c,index=df.index); ret=px.pct_change().fillna(0)
by=build(pivots(8)); ev=breaks(by,6)
pos=np.zeros(n)
for (t,d) in ev: pos[t:min(t+48,n)] += d
w=pd.Series(np.clip(pos,-1,1),index=df.index).astype(float)
held=w.shift(1)
strat=(held*ret - COST*held.diff().abs().fillna(0))
daily=((1+strat.dropna()).resample("1D").prod()-1).dropna().to_numpy()

def run(target, max_dd, daily_lim=0.03, limit_days=90, trailing=False):
    """Anteil der Versuche, die das Ziel VOR dem Drawdown erreichen."""
    passed=tot=0
    horizon = limit_days if limit_days else len(daily)
    for s in range(0, len(daily)-30):
        eq=1.0; peak=1.0; ok=None
        end = min(s+horizon, len(daily))
        for i in range(s, end):
            r=daily[i]
            if r < -daily_lim: ok=False; break
            eq *= (1+r); peak=max(peak,eq)
            floor = (peak if trailing else 1.0)*(1-max_dd)
            if eq <= floor: ok=False; break
            if eq-1 >= target: ok=True; break
        if ok is None: ok=False               # Zeit abgelaufen
        passed+=ok; tot+=1
    return passed/tot*100 if tot else 0

print("="*84)
print("Pass-Rate der S/R-Strategie je Regelwerk  (statischer Drawdown, 90 Tage)")
print("="*84)
dds=[0.05,0.06,0.08,0.10,0.12,0.15]
print(f"{'Ziel':>6s} |" + "".join(f"{d*100:7.0f}%" for d in dds) + "   <- max. Drawdown")
print("-"*84)
for tgt in (0.05,0.06,0.08,0.10,0.12):
    row="".join(f"{run(tgt,d):7.1f}" for d in dds)
    mark = "  <- Kraken Starter" if tgt==0.10 else ""
    print(f"{tgt*100:5.0f}% |{row}{mark}")

print("\n"+"="*84)
print("Die ungetestete Variable: ZEITLIMIT")
print("="*84)
print(f"{'Regelwerk':44s} {'30 T':>7s} {'60 T':>7s} {'90 T':>7s} {'180 T':>7s} {'ohne':>7s}")
print("-"*84)
for tgt, dd, nm in ((0.10,0.06,"Kraken Starter (10 % / 6 %)"),
                    (0.08,0.08,"8 % Ziel / 8 % DD"),
                    (0.08,0.10,"8 % Ziel / 10 % DD"),
                    (0.06,0.10,"6 % Ziel / 10 % DD"),
                    (0.10,0.10,"10 % Ziel / 10 % DD"),
                    (0.10,0.12,"10 % Ziel / 12 % DD")):
    vals="".join(f"{run(tgt,dd,limit_days=L):7.1f}" for L in (30,60,90,180,None))
    print(f"{nm:44s}{vals}")

print("\n"+"="*84)
print("Trailing- statt statischer Drawdown (viele Anbieter nutzen trailing)")
print("="*84)
print(f"{'Regelwerk':30s} {'statisch':>10s} {'trailing':>10s}")
print("-"*54)
for tgt,dd,nm in ((0.10,0.06,"10 % / 6 %"),(0.08,0.10,"8 % / 10 %"),(0.10,0.10,"10 % / 10 %")):
    print(f"{nm:30s} {run(tgt,dd,limit_days=None):9.1f}% {run(tgt,dd,limit_days=None,trailing=True):9.1f}%")

print("\n"+"="*84)
print("Auch die Tagesverlust-Grenze prueft mit")
print("="*84)
print(f"{'Tagesverlust-Limit':30s} {'Pass (10 %/10 %, ohne Zeitlimit)':>34s}")
print("-"*66)
for dl in (0.02,0.03,0.04,0.05,1.0):
    lbl = "keins" if dl>=1 else f"{dl*100:.0f} %"
    print(f"{lbl:30s} {run(0.10,0.10,daily_lim=dl,limit_days=None):33.1f}%")
