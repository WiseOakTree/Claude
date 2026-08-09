"""Teil 2: Die restlichen Volume-Profile-Behauptungen.

B. Value-Area-Ausbruch als Signal
C. Low Volume Nodes: laeuft der Kurs dort schneller durch?
D. Profil als Risikomass (dort steckte bisher jede Information)
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, pickle, sys
from scipy.stats import spearmanr
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from vp import build, fwd, tstat, SPLIT, COST
H=48

res={}
for sym in ("btc","eth","sol"):
    A,raw=build(sym)
    A["fwd"]=fwd(A.close,H)
    r1=np.log(A.close).diff()
    A["volf"]=r1.shift(-H).rolling(H).std()*np.sqrt(24*365)
    A["dmin"]=r1.shift(-H).rolling(H).resample("1D").min().reindex(A.index).ffill() \
        if False else r1.shift(-H).rolling(H).min()
    res[sym]=A

print("="*90)
print("B. VALUE-AREA-AUSBRUCH: Kurs verlaesst die Value Area -> naechste 48 h")
print("="*90)
print(f"{'Markt':<6}{'Zeitraum':<16}{'Ausbrueche':>11}{'bp/Trade':>11}{'t':>7}{'Treffer':>9}")
for sym,A in res.items():
    up=(A.close>A.vah)&(A.close.shift(1)<=A.vah.shift(1))
    dn=(A.close<A.val)&(A.close.shift(1)>=A.val.shift(1))
    d=np.where(up,1,np.where(dn,-1,0))
    for nm,m in (("Suche 21-24",A.index<SPLIT),("HOLDOUT 25-26",A.index>=SPLIT)):
        msk=m&(d!=0)&np.isfinite(A.fwd.to_numpy())
        if msk.sum()<30: continue
        r=d[msk]*A.fwd.to_numpy()[msk]-2*COST
        print(f"{sym.upper():<6}{nm:<16}{msk.sum():>11}{r.mean()*1e4:>+10.1f}"
              f"{tstat(r,H):>7.2f}{(r>0).mean()*100:>8.1f}%")
    print()

print("="*90)
print("C. LOW VOLUME NODES: bewegt sich der Kurs dort schneller?")
print("="*90)
print(f"{'Markt':<6}{'Zeitraum':<16}{'LVN (unt. 20%)':>16}{'HVN (ob. 20%)':>15}{'Verhaeltnis':>13}")
for sym,A in res.items():
    A2=A.dropna(subset=["dens"]).copy()
    A2["absfwd"]=A2.fwd.abs()
    for nm,m in (("Suche 21-24",A2.index<SPLIT),("HOLDOUT 25-26",A2.index>=SPLIT)):
        g=A2[m].dropna(subset=["absfwd"])
        if len(g)<500: continue
        q=pd.qcut(g.dens,5,labels=False,duplicates="drop")
        lo=g.absfwd[q==0].mean()*100; hi=g.absfwd[q==4].mean()*100
        print(f"{sym.upper():<6}{nm:<16}{lo:>15.2f}%{hi:>14.2f}%{lo/hi:>13.2f}x")
    print()

print("="*90)
print("D. DAS PROFIL ALS RISIKOMASS (Rangkorrelation, 1h-Bars)")
print("="*90)
print(f"{'Markt':<6}{'Mass':<28}{'Vol 48h Suche':>15}{'Vol 48h HOLD':>14}{'-3%-Tag HOLD':>14}")
for sym,A in res.items():
    r1=np.log(A.close).diff()
    cand={
      "Value-Area-Breite": A.va_breite,
      "|Abstand zum POC|": A.dist_poc.abs(),
      "Volumendichte am Kurs": -A.dens,          # niedrige Dichte = LVN = riskant?
      "VWAP-Bandbreite (120h)": None,
      "Bollinger-Breite (120h)": 4*A.close.rolling(120).std()/A.close.rolling(120).mean(),
      "Abwaerts-Semivol (120h)": r1.where(r1<0,0).rolling(120).std()*np.sqrt(24*365),
    }
    del cand["VWAP-Bandbreite (120h)"]
    X=pd.DataFrame(cand); X["volf"]=A.volf
    X["neg"]=(r1.shift(-H).rolling(H).min()<=np.log(0.97)).astype(float)
    X=X.replace([np.inf,-np.inf],np.nan).dropna()
    tr=X.index<SPLIT; ho=X.index>=SPLIT
    for k in cand:
        a=spearmanr(X[k][tr],X.volf[tr]).statistic
        b=spearmanr(X[k][ho],X.volf[ho]).statistic
        c=spearmanr(X[k][ho],X.neg[ho]).statistic
        print(f"{sym.upper():<6}{k:<28}{a:>15.3f}{b:>14.3f}{c:>14.3f}")
    print()
