"""Teil 2: VWAP als RISIKOMASS (dort steckte die Information) und als
ZEHNTER FILTER auf das validierte S/R-Signal."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
from scipy.stats import spearmanr
sys.path.insert(0,"/home/user/Claude/src")
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from msb import bars4h, SPLIT
from vwap import build
COST=8e-4; HOLD=30

print("="*86)
print("A. VWAP-BAENDER ALS RISIKOMASS -- gegen die bestehende Rangliste")
print("="*86)
print(f"{'Markt':<6}{'Mass':<26}{'Vol 5T Suche':>14}{'Vol 5T HOLD':>13}{'Tag<=-3% HOLD':>15}")
for sym in ("btc","eth"):
    d=build(sym)
    r=np.log(d.close).diff(); AN=np.sqrt(6*365)
    cand={
      "VWAP-Bandbreite (20)": d.vwband,
      "|Abstand| zum Tages-VWAP": (d.close/d.vwap_d-1).abs(),
      "Volumen / Ø20": d.volume/d.volume.rolling(20).mean(),
      "Abwaerts-Semivol 20": r.where(r<0,0).rolling(20).std()*AN,
      "Bollinger-Breite (20,2)": 4*d.close.rolling(20).std()/d.close.rolling(20).mean(),
    }
    A=pd.DataFrame(cand); A["volf"]=d.volf
    A["neg"]=(d.dmin<=np.log(0.97)).astype(float)
    A=A.replace([np.inf,-np.inf],np.nan).dropna()
    tr=A.index<SPLIT; ho=A.index>=SPLIT
    for n in cand:
        a=spearmanr(A[n][tr],A.volf[tr]).statistic
        b=spearmanr(A[n][ho],A.volf[ho]).statistic
        c=spearmanr(A[n][ho],A.neg[ho]).statistic
        print(f"{sym.upper():<6}{n:<26}{a:>14.3f}{b:>13.3f}{c:>15.3f}")
    print()

print("="*86)
print("B. VWAP ALS ZEHNTER FILTER auf das S/R-Ausbruchssignal (BTC 1h)")
print("="*86)
from prop_backtester import levels as LV
D="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
h1=pd.read_csv(D+"btc_1h.csv",index_col=0,parse_dates=True)
by=LV.build_levels(h1)
ev=LV.breakout_events(by,h1,min_touch=6)
c=h1.close.to_numpy(); H=48
f=np.full(len(c),np.nan); f[:-H]=c[H:]/c[:-H]-1
tp=(h1.high+h1.low+h1.close)/3; pv=tp*h1.volume
day=h1.index.floor("1D")
vwd=(pv.groupby(day).cumsum()/h1.volume.groupby(day).cumsum()).to_numpy()
vwr=(pv.rolling(50).sum()/h1.volume.rolling(50).sum()).to_numpy()
idx=h1.index
rows=[]
for t,dirn,tou,px in ev:
    if not np.isfinite(f[t]): continue
    rows.append(dict(t=t,ts=idx[t],d=dirn,ret=dirn*f[t]-2*COST,
                     ok_d=(dirn==1)==(c[t]>vwd[t]),
                     ok_r=(dirn==1)==(c[t]>vwr[t]) if np.isfinite(vwr[t]) else None))
E=pd.DataFrame(rows).dropna()
tr=E.ts<SPLIT; ho=E.ts>=SPLIT
def rep(lab,sel):
    for nm,m in (("Suche",tr),("HOLDOUT",ho)):
        s=E[m & sel]
        if len(s)<15: continue
        t_=s.ret.mean()/(s.ret.std(ddof=1)/np.sqrt(max(len(s)/H,2)))
        print(f"  {lab:<34}{nm:<10}{len(s):>5}{s.ret.mean()*1e4:>+9.1f} bp{t_:>7.2f}")
print(f"  {'Variante':<34}{'Zeitraum':<10}{'n':>5}{'Effekt':>12}{'t':>7}")
rep("ohne Filter (Ausgangslage)", pd.Series(True,index=E.index))
rep("nur wenn im Einklang mit Tages-VWAP", E.ok_d.astype(bool))
rep("nur wenn im Einklang mit VWAP(50)", E.ok_r.astype(bool))
rep("GEGEN den Tages-VWAP", ~E.ok_d.astype(bool))
