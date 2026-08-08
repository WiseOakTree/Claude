"""Alle Kernbefunde des Projekts mit KORRIGIERTER Statistik neu gerechnet."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/home/user/Claude/src")
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from prop_backtester import levels as LV
from msb import bars4h, signals
D="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC"); COST=8e-4

def n_eff(starts,hold,N):
    conc=np.zeros(N)
    for i in starts: conc[i:i+hold]+=1
    u=[]
    for i in starts:
        seg=conc[i:i+hold]; seg=seg[seg>0]
        u.append((1.0/seg).mean() if len(seg) else 0.0)
    return max(np.sum(u),2.0)

def bewerte(starts,rets,hold,N,label,zeitraum):
    if len(starts)<15: return
    x=np.asarray(rets)
    ne=n_eff(np.asarray(starts),hold,N)
    t_alt=x.mean()/(x.std(ddof=1)/np.sqrt(max(len(x)/hold,2)))
    t_neu=x.mean()/(x.std(ddof=1)/np.sqrt(ne))
    print(f"  {label:<32}{zeitraum:<14}{len(x):>5}{x.mean()*1e4:>+9.1f} bp"
          f"{t_alt:>8.2f}{t_neu:>9.2f}{ne:>9.0f}")

print("="*96)
print("KERNBEFUNDE MIT KORRIGIERTER UEBERLAPPUNGSSTATISTIK")
print("="*96)
print(f"  {'Befund':<32}{'Zeitraum':<14}{'n':>5}{'Effekt':>12}{'t ALT':>8}"
      f"{'t NEU':>9}{'n_eff':>9}")

# 1) S/R-Ausbruch, der validierte Befund
h1=pd.read_csv(D+"btc_1h.csv",index_col=0,parse_dates=True)
by=LV.build_levels(h1); ev=LV.breakout_events(by,h1,min_touch=6)
c=h1.close.to_numpy(); H=48; N=len(c)
f=np.full(N,np.nan); f[:-H]=c[H:]/c[:-H]-1
rec=[(t,d,h1.index[t],d*f[t]-2*COST) for t,d,_,_ in ev if np.isfinite(f[t])]
E=pd.DataFrame(rec,columns=["i","d","ts","ret"])
for nm,m in (("Suche 21-24",E.ts<SPLIT),("HOLDOUT 25-26",E.ts>=SPLIT),
             ("gesamt",pd.Series(True,index=E.index))):
    s=E[m]; bewerte(s.i.to_numpy(),s.ret.to_numpy(),H,N,"S/R-Ausbruch (Pivots)",nm)
print()

# 2) Die 4h-Trendlesart MACD+Stoch+BB
for sym in ("btc","eth"):
    df=bars4h(sym); cc=df.close.to_numpy(); NN=len(cc); HH=30
    ff=np.full(NN,np.nan); ff[:-HH]=cc[HH:]/cc[:-HH]-1
    L,S=signals(df,"trend")
    d=np.where(L.to_numpy(),1,np.where(S.to_numpy(),-1,0))
    idx=np.where((d!=0)&np.isfinite(ff))[0]
    R=pd.DataFrame({"i":idx,"ts":df.index[idx],"ret":d[idx]*ff[idx]-2*COST})
    for nm,m in (("Suche 21-24",R.ts<SPLIT),("HOLDOUT 25-26",R.ts>=SPLIT)):
        s=R[m]; bewerte(s.i.to_numpy(),s.ret.to_numpy(),HH,NN,
                        f"MACD+Stoch+BB Trend {sym.upper()}",nm)
    print()

# 3) Wie gross muesste der S/R-Effekt sein, um beweisbar zu sein?
print("="*96)
print("WIE GROSS MUESSTE EIN EFFEKT SEIN, UM MIT DIESEN DATEN BEWEISBAR ZU SEIN?")
print("="*96)
s=E[E.ts>=SPLIT]
ne=n_eff(s.i.to_numpy(),H,N); sd=s.ret.std(ddof=1)
print(f"  S/R im Holdout: n = {len(s)}, n_eff = {ne:.0f}, "
      f"Streuung je Trade = {sd*1e4:.0f} bp")
print(f"  gemessener Effekt: {s.ret.mean()*1e4:+.1f} bp   ->   t = {s.ret.mean()/(sd/np.sqrt(ne)):.2f}")
print(f"  fuer t = 2 noetig: {2*sd/np.sqrt(ne)*1e4:+.1f} bp je Trade")
print(f"  fuer t = 2 bei gleichem Effekt noetig: n_eff = "
      f"{(2*sd/s.ret.mean())**2:.0f}  (also rund "
      f"{(2*sd/s.ret.mean())**2/ne*1.5:.1f} Jahre statt 1,5)")
