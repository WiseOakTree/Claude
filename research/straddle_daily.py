"""Korrekte TAEGLICHE Marktbewertung des gehedgten Short-Straddle.
Vorher wurde die Praemie erst am Verfallstag gebucht -- das erzeugt einen
kuenstlichen Sprung und eine viel zu hohe Tagesvolatilitaet.
Richtig: taeglich mit Black-Scholes zum aktuellen IV neu bewerten.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy.stats import norm
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
px=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)["close"].resample("1D").last().dropna()
iv=pd.read_csv(V+"dvol_BTC.csv",index_col=0,parse_dates=True)["close"].resample("1D").last().dropna()
df=pd.DataFrame({"px":px,"iv":iv}).dropna()
def bs(S,K,T,s):
    if T<=1e-9: return abs(S-K),(1.0 if S>K else -1.0)
    d1=(np.log(S/K)+.5*s*s*T)/(s*np.sqrt(T)); d2=d1-s*np.sqrt(T)
    return (S*norm.cdf(d1)-K*norm.cdf(d2))+(K*norm.cdf(-d2)-S*norm.cdf(-d1)), norm.cdf(d1)-norm.cdf(-d1)

T0=30; daily=[]; dates=[]; i=0
while i+T0<len(df):
    S0=df["px"].iloc[i]; K=S0
    valp,hedge=bs(S0,K,T0/365,df["iv"].iloc[i]/100*0.98)   # Verkauf mit Spread
    valp-=S0*3/1e4                                          # Gebuehr beim Verkauf
    Sp=S0
    for j in range(1,T0+1):
        Sj=df["px"].iloc[i+j]; Tj=(T0-j)/365
        val,dn=bs(Sj,K,max(Tj,1e-9),df["iv"].iloc[i+j]/100)
        # short option: Wertanstieg = Verlust. Plus Hedge-PnL. Minus Hedge-Kosten.
        pnl=(valp-val)+hedge*(Sj-Sp)-abs(dn-hedge)*Sj*5/1e4
        daily.append(pnl/S0); dates.append(df.index[i+j])
        valp=val; hedge=dn; Sp=Sj
    i+=T0
ds=pd.Series(daily,index=dates)
print("="*84)
print("Short-Straddle: taegliche Marktbewertung (korrigiert)")
print("="*84)
print(f"  Tage {len(ds)}   Vol p.a. {ds.std()*np.sqrt(365)*100:.1f} %   "
      f"Rendite p.a. {((1+ds).prod()**(365/len(ds))-1)*100:+.1f} %")
print(f"  Sharpe {ds.mean()/ds.std()*np.sqrt(365):.2f}   "
      f"schlechtester Tag {ds.min()*100:+.2f} %   "
      f"Tage unter -3 %: {(ds<-.03).mean()*100:.2f} %")
eq=(1+ds).cumprod(); print(f"  groesster Drawdown {(eq/eq.cummax()-1).min()*100:.1f} %")
ds.to_csv("/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/oc/straddle_daily.csv")

def year(x,day_lim,dd):
    o=[]
    for st in range(0,len(x)-365):
        e=1.0; g=None
        for k in range(st,st+365):
            if day_lim is not None and x[k]<-day_lim: g="Tag";break
            e*=(1+x[k])
            if e<=1-dd: g="DD";break
        o.append((g is None,e-1,g or "-"))
    return o
x=ds.to_numpy()
print()
print(f"  {'Groesse':>8s} {'Vol p.a.':>9s} {'ueberlebt':>10s} {'Ø Rendite':>11s} "
      f"{'>=20 %':>8s} {'Tag':>6s} {'DD':>6s}")
print("  "+"-"*64)
for lev in [0.5,1.0,1.5,2.0,2.5]:
    r=year(x*lev,0.03,0.06)
    s=np.array([q[0] for q in r]); ret=np.array([q[1] for q in r])
    g=pd.Series([q[2] for q in r]).value_counts(normalize=True)*100
    print(f"  {lev:>7.2f}x {ds.std()*np.sqrt(365)*lev*100:>8.1f}% {s.mean()*100:>9.1f}% "
          f"{ret.mean()*100:>+10.1f}% {((s)&(ret>=.20)).mean()*100:>7.1f}% "
          f"{g.get('Tag',0):>5.1f}% {g.get('DD',0):>5.1f}%")
