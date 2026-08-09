"""Letzte Kontrollen am Gegen-Bounce: Richtungsverteilung, Drift-Kontrolle,
Pass-Rate unter Kraken-Regeln."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/home/user/Claude/src")
from prop_backtester import levels as LV
D="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC"); COST=8e-4; H=48

def n_eff(st,hold,N):
    conc=np.zeros(N)
    for i in st: conc[i:i+hold]+=1
    u=[]
    for i in st:
        s=conc[i:i+hold]; s=s[s>0]; u.append((1.0/s).mean() if len(s) else 0)
    return max(np.sum(u),2.0)

df=pd.read_csv(D+"btc_1h.csv",index_col=0,parse_dates=True)
by=LV.build_levels(df); c=df.close.to_numpy(); N=len(c)
f=np.full(N,np.nan); f[:-H]=c[H:]/c[:-H]-1
ev=LV.bounce_events(by,df,min_touch=6)
r=[(t,-d,df.index[t],-d*f[t]-2*COST) for t,d,_,_ in ev if np.isfinite(f[t])]
B=pd.DataFrame(r,columns=["i","d","ts","ret"])   # d = GEGEN-Richtung

print("="*92); print("A. RICHTUNGSVERTEILUNG -- reitet der Effekt nur den Aufwaertsdrift?")
print("="*92)
print(f"{'Zeitraum':<15}{'long':>7}{'short':>7}{'bp long':>11}{'bp short':>11}"
      f"{'t long':>9}{'t short':>9}")
for nm,m in (("Suche 21-24",B.ts<SPLIT),("HOLDOUT 25-26",B.ts>=SPLIT)):
    s=B[m]; out=[]
    for d in (1,-1):
        g=s[s.d==d]
        if len(g)<30: out.append((0,np.nan,np.nan)); continue
        ne=n_eff(g.i.to_numpy(),H,N)
        out.append((len(g),g.ret.mean()*1e4,g.ret.mean()/(g.ret.std(ddof=1)/np.sqrt(ne))))
    print(f"{nm:<15}{out[0][0]:>7}{out[1][0]:>7}{out[0][1]:>+10.1f}{out[1][1]:>+10.1f}"
          f"{out[0][2]:>9.2f}{out[1][2]:>9.2f}")

print(f"\n  BTC-Drift im Zeitraum: Suche "
      f"{(c[df.index<SPLIT][-1]/c[0]-1)*100:+.0f} %, Holdout "
      f"{(c[-1]/c[df.index<SPLIT].shape[0]-1)*100:+.0f} % (nur zur Einordnung)")

print("\n"+"="*92); print("B. DRIFT-KONTROLLE: gleiche Zeitpunkte, Richtung gewuerfelt (500x)")
print("="*92)
rng=np.random.default_rng(99)
for nm,m in (("Suche 21-24",B.ts<SPLIT),("HOLDOUT 25-26",B.ts>=SPLIT)):
    s=B[m]; ii=s.i.to_numpy(); echt=s.ret.mean()*1e4
    zs=[]
    for _ in range(500):
        d=rng.choice([1,-1],size=len(ii))
        zs.append((d*f[ii]-2*COST).mean()*1e4)
    zs=np.array(zs)
    print(f"  {nm:<15} echt {echt:>+7.1f} bp   Zufall Median {np.median(zs):>+6.1f} bp   "
          f"5-95 %: {np.percentile(zs,5):+.0f}..{np.percentile(zs,95):+.0f}   "
          f"p = {(zs>=echt).mean():.3f}")

print("\n"+"="*92); print("C. PASS-RATE UNTER KRAKEN-REGELN (10 % Ziel, 6 % statisch, 3 % Tag)")
print("="*92)
def passrate(size, quelle):
    pos=np.zeros(N); i=0
    d=np.zeros(N,dtype=int); d[quelle.i.to_numpy()]=quelle.d.to_numpy()
    while i<N:
        if d[i]!=0: pos[i:i+H]=d[i]*size; i+=H
        else: i+=1
    ret=np.diff(c)/c[:-1]; turn=np.abs(np.diff(np.concatenate([[0.0],pos])))[:-1]
    s=pos[:-1]*ret-COST*turn
    day=pd.Series(s,index=df.index[1:]).resample("1D").apply(lambda x:(1+x).prod()-1).to_numpy()
    ok=tot=0
    for st in range(0,len(day)-30,3):
        e=1.0
        for k in range(st,len(day)):
            e*=(1+day[k])
            if day[k]<-0.03 or e-1<=-0.06: h=False; break
            if e-1>=0.10: h=True; break
        else: continue
        ok+=h; tot+=1
    return ok/tot*100 if tot else 0
A_=LV.breakout_events(by,df,min_touch=6)
AB=pd.DataFrame([(t,d) for t,d,_,_ in A_],columns=["i","d"])
print(f"  {'Regel':<26}{'0,25x':>9}{'0,35x':>9}{'0,50x':>9}")
for lab,q in (("S/R-Ausbruch",AB),("Gegen-Bounce",B[["i","d"]])):
    print(f"  {lab:<26}"+"".join(f"{passrate(sz,q):>8.1f}%" for sz in (0.25,0.35,0.5)))
print("\n  Zufall bei diesen Regeln: 37,5 %")
