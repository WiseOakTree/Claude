"""Stops richtig gerechnet: Verlust bei Ausloesung MIT einbezogen.

Und die eigentliche Frage fuer eine Prop-Challenge: Ein Stop kann die
Erwartung senken und trotzdem helfen, wenn er den Drawdown kappt.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
full=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
df=full[full.index<pd.Timestamp("2025-01-01",tz="UTC")].copy()
c=df["close"].to_numpy(); h=df["high"].to_numpy(); l=df["low"].to_numpy(); n=len(df)
by=levels.build_levels(df, width=8, tol_atr=0.5, max_age=1000)
bo=levels.breakout_events(by, df, min_touch=6)
HOLD=24; COST=16e-4

print("="*80)
print("1) Erwartungswert je Trade -- Stop-Verlust EINGERECHNET")
print("="*80)
print(f"{'Stop':>8s} {'ausgeloest':>12s} {'E[Rendite]':>13s} {'ohne Stop':>12s}")
print("-"*50)
base=[]
for (t,d,_,_) in bo:
    if t+HOLD>=n: continue
    base.append((c[t+HOLD]/c[t]-1)*d*1e4)
base=np.array(base)
for stop_bp in (None,50,100,150,200,300,500,800):
    vals=[]
    for (t,d,_,_) in bo:
        if t+HOLD>=n: continue
        entry=c[t]
        if stop_bp is not None:
            lim = entry*(1-d*stop_bp/1e4)
            hit=False
            for j in range(t+1, t+HOLD+1):
                if (d>0 and l[j]<=lim) or (d<0 and h[j]>=lim):
                    vals.append(-stop_bp); hit=True; break
            if hit: continue
        vals.append((c[t+HOLD]/c[t]-1)*d*1e4)
    v=np.array(vals)
    lbl = "kein" if stop_bp is None else f"{stop_bp} bp"
    trig = "—" if stop_bp is None else f"{(v==-stop_bp).mean()*100:.0f}%"
    print(f"{lbl:>8s} {trig:>12s} {v.mean():+11.1f} bp {base.mean():+10.1f} bp")

print("\n"+"="*80)
print("2) Der Test, der zaehlt: Pass-Rate mit und ohne Stop")
print("="*80)
ret=pd.Series(c,index=df.index).pct_change().fillna(0)
def build_series(stop_bp, lev):
    pos=np.zeros(n)
    for (t,d,_,_) in bo:
        end=min(t+HOLD,n)
        if stop_bp is not None:
            entry=c[t]; lim=entry*(1-d*stop_bp/1e4)
            for j in range(t+1,end):
                if (d>0 and l[j]<=lim) or (d<0 and h[j]>=lim):
                    end=j; break
        pos[t:end]+=d
    w=pd.Series(np.clip(pos,-1,1),index=df.index).astype(float)*lev
    held=w.shift(1)
    return held*ret - COST*held.diff().abs().fillna(0)

def challenge(s):
    d=((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()
    p=f=cn=0
    for st in range(0,len(d)-1):
        eq=1.0; done=None
        for i in range(st,min(st+365,len(d))):
            r=d[i]
            if r<-.03: done="f";break
            eq*=(1+r)
            if eq<=.94: done="f";break
            if eq-1>=.10: done="p";break
        if done=="p": p+=1
        elif done=="f": f+=1
        else: cn+=1
    tot=p+f+cn
    return (p/(p+f)*100 if p+f else 0, p/tot*100)
print(f"{'Stop':>8s} {'Groesse':>9s} {'Quote':>9s} {'Untergrenze':>13s}")
print("-"*44)
for stop_bp in (None, 150, 300, 500):
    for lev in (1.0, 0.5):
        q,u = challenge(build_series(stop_bp, lev))
        lbl = "kein" if stop_bp is None else f"{stop_bp} bp"
        print(f"{lbl:>8s} {lev:8.2f}x {q:8.1f}% {u:12.1f}%")
