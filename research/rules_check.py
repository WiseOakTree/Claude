"""Welche Regelauslegung ist richtig? Und was heisst das fuer alle Ergebnisse?"""
import numpy as np, pandas as pd
V = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
df = pd.read_csv(V+"btc_1h.csv", index_col=0, parse_dates=True)
c = df["close"].to_numpy(); n=len(df)
px = pd.Series(c, index=df.index); ret = px.pct_change().fillna(0)
COST=16e-4

# --- die drei Kandidaten als Tagesrenditen ---
o,h,l = (df[x].to_numpy() for x in ("open","high","low"))
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
by=build(pivots(8))
ev=[]
for t in range(1,n):
    for (p_,k,tc,_) in by.get(t-1,[]):
        if tc<6: continue
        if k=="R" and c[t-1]<=p_<c[t]: ev.append((t,+1))
        elif k=="S" and c[t-1]>=p_>c[t]: ev.append((t,-1))
pos=np.zeros(n)
for (t,d) in ev: pos[t:min(t+48,n)] += d
wsr=pd.Series(np.clip(pos,-1,1),index=df.index).astype(float).shift(1)
sr = wsr*ret - COST*wsr.diff().abs().fillna(0)

rv = np.log(px).diff().rolling(24*30).std()*np.sqrt(24*365)*100
sz = (15.0/rv).clip(upper=2.0).fillna(0).shift(1)
vtr = sz*ret - COST*sz.diff().abs().fillna(0)

def to_daily(s): return ((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()
CAND = {"BTC halten": to_daily(ret), "Vol-Targeting 15 %": to_daily(vtr),
        "S/R-Ausbruch (>=6, 48h)": to_daily(sr)}

def eval_rule(daily, target=.10, max_dd=.06, daily_lim=.03, days=90,
              stop_at_target=True, trailing_dd=False):
    passed=tot=0
    for s in range(0, len(daily)-days):
        eq=1.0; peak=1.0; ok=None
        for i in range(s, s+days):
            r=daily[i]
            if r < -daily_lim: ok=False; break
            eq*=(1+r); peak=max(peak,eq)
            if eq <= (peak if trailing_dd else 1.0)*(1-max_dd): ok=False; break
            if stop_at_target and eq-1>=target: ok=True; break
        if ok is None: ok = (eq-1>=target)
        passed+=ok; tot+=1
    return passed/tot*100 if tot else 0

print("="*86)
print("Welche Auslegung? Kraken: Drawdown STATISCH vom Startguthaben,")
print("Ziel gilt als erreicht, SOBALD es beruehrt wird.")
print("="*86)
print(f"{'Strategie':26s} {'streng (alt)':>14s} {'korrekt':>10s} {'Differenz':>11s}")
print(f"{'':26s} {'trailing+Ende':>14s} {'stat.+sofort':>10s}")
print("-"*66)
for nm, d in CAND.items():
    alt = eval_rule(d, stop_at_target=False, trailing_dd=True)
    neu = eval_rule(d, stop_at_target=True,  trailing_dd=False)
    print(f"{nm:26s} {alt:13.1f}% {neu:9.1f}% {neu-alt:+10.1f} pp")

print("\n"+"="*86)
print("Beide Aenderungen einzeln -- welche macht den Unterschied?")
print("="*86)
print(f"{'Strategie':26s} {'trail+Ende':>11s} {'stat+Ende':>11s} {'trail+sofort':>13s} {'stat+sofort':>12s}")
print("-"*78)
for nm, d in CAND.items():
    a=eval_rule(d,stop_at_target=False,trailing_dd=True)
    b=eval_rule(d,stop_at_target=False,trailing_dd=False)
    cc=eval_rule(d,stop_at_target=True, trailing_dd=True)
    e=eval_rule(d,stop_at_target=True, trailing_dd=False)
    print(f"{nm:26s} {a:10.1f}% {b:10.1f}% {cc:12.1f}% {e:11.1f}%")
