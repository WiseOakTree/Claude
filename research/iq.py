"""iqcapital Advanced 50k gegen Kraken Starter -- gleiche Strategien, andere Regeln."""
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
by=build(pivots(8))
COST=16e-4
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
sr = w*ret - COST*w.diff().abs().fillna(0)
rv = np.log(px).diff().rolling(24*30).std()*np.sqrt(24*365)*100
sz = (15.0/rv).clip(upper=2.0).fillna(0).shift(1)
vtr = sz*ret - COST*sz.diff().abs().fillna(0)
def daily(s): return ((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()
CAND={"BTC halten":daily(ret),"Vol-Targeting 15 %":daily(vtr),"S/R-Ausbruch":daily(sr)}

def ev_rule(d, target, max_dd, days, trailing_eod=False, daily_lim=None):
    passed=tot=0
    for s in range(0,len(d)-min(days,len(d)-1)):
        eq=1.0; peak=1.0; ok=None
        for i in range(s, min(s+days,len(d))):
            r=d[i]
            if daily_lim and r < -daily_lim: ok=False; break
            eq*=(1+r)
            floor = (peak if trailing_eod else 1.0)*(1-max_dd)
            if eq <= floor: ok=False; break
            peak=max(peak,eq)                     # EOD: Hoch erst zum Tagesschluss
            if eq-1>=target: ok=True; break
        if ok is None: ok=False
        passed+=ok; tot+=1
    return passed/tot*100 if tot else 0

print("="*84)
print("iqcapital 'Advanced' 50k  gegen  Kraken Starter")
print("="*84)
print(f"{'Strategie':22s} {'Kraken':>10s} {'iqcapital':>11s} {'iq mit 90 T':>13s} {'iq ohne Limit':>15s}")
print(f"{'':22s} {'10%/6%/90T':>10s} {'6%/6%/30T':>11s} {'(hypothetisch)':>13s}")
print("-"*84)
for nm,d in CAND.items():
    kr = ev_rule(d, .10, .06, 90, trailing_eod=False, daily_lim=.03)
    iq = ev_rule(d, .06, .06, 30, trailing_eod=True)
    iq90 = ev_rule(d, .06, .06, 90, trailing_eod=True)
    iqinf = ev_rule(d, .06, .06, len(d), trailing_eod=True)
    print(f"{nm:22s} {kr:9.1f}% {iq:10.1f}% {iq90:12.1f}% {iqinf:14.1f}%")

print("\n"+"="*84)
print("Woran liegt es? Die Regeln einzeln geaendert (S/R-Strategie)")
print("="*84)
d=CAND["S/R-Ausbruch"]
print(f"{'Regelwerk':52s} {'Pass':>8s}")
print("-"*62)
for nm,(tg,dd,dy,tr,dl) in {
    "Kraken: 10 % Ziel, 6 % statisch, 90 T, 3 % Tageslimit":(.10,.06,90,False,.03),
    "  -> Ziel auf 6 % gesenkt":                            (.06,.06,90,False,.03),
    "  -> zusaetzlich EOD-trailing statt statisch":         (.06,.06,90,True,.03),
    "  -> zusaetzlich kein Tageslimit":                     (.06,.06,90,True,None),
    "iqcapital: dazu Dauer auf 30 Tage":                    (.06,.06,30,True,None),
}.items():
    print(f"{nm:52s} {ev_rule(d,tg,dd,dy,tr,dl):7.1f}%")

print("\n"+"="*84)
print("Die Gebuehrenstruktur")
print("="*84)
iq_pass = ev_rule(CAND["S/R-Ausbruch"], .06,.06,30, trailing_eod=True)
kr_pass = ev_rule(CAND["S/R-Ausbruch"], .10,.06,90, trailing_eod=False, daily_lim=.03)
print(f"{'':34s} {'Kraken Starter':>16s} {'iqcapital Advanced':>20s}")
print("-"*74)
print(f"{'Kontogroesse':34s} {'10.000 $':>16s} {'50.000 $':>20s}")
print(f"{'Gewinnziel':34s} {'1.000 $ (10 %)':>16s} {'3.000 $ (6 %)':>20s}")
print(f"{'Pass-Rate (S/R-Strategie)':34s} {kr_pass:15.1f}% {iq_pass:19.1f}%")
print(f"{'Versuche bis Erfolg':34s} {100/max(kr_pass,.01):15.1f} {100/max(iq_pass,.01):19.1f}")
print(f"{'Gebuehr je Versuch':34s} {'85 $':>16s} {'53 $':>20s}")
print(f"{'erwartete Gebuehren bis Erfolg':34s} "
      f"{100/max(kr_pass,.01)*85:14.0f} $ {100/max(iq_pass,.01)*53:18.0f} $")
print(f"{'+ Aktivierungsgebuehr':34s} {'0 $':>16s} {'129 $':>20s}")
print(f"{'+ Monatsgebuehr':34s} {'0 $':>16s} {'19 $/Monat':>20s}")
print(f"\n{'GESAMT bis zum gefundeten Konto':34s} "
      f"{100/max(kr_pass,.01)*85:14.0f} $ {100/max(iq_pass,.01)*53+129:18.0f} $")
print(f"{'davon laufend':34s} {'-':>16s} {'228 $/Jahr':>20s}")
