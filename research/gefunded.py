"""Was killt das gefundete Konto -- und geht es mit dem Straddle besser?"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy.stats import norm
from prop_backtester import levels
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"

def sr_daily(side_bp=8.0, hold=48):
    d=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
    h=pd.Series(d["close"].to_numpy(),index=d.index).pct_change().fillna(0)
    by=levels.build_levels(d,width=8,tol_atr=0.5,max_age=1000)
    ev=levels.breakout_events(by,d,min_touch=6)
    n=len(d); pos=np.zeros(n); busy=-1
    for (t,dr,_,_) in ev:
        if t<busy: continue
        pos[t:t+hold]=dr; busy=t+hold
    w=pd.Series(np.clip(pos,-1,1),index=d.index).astype(float); held=w.shift(1)
    return ((1+(held*h-side_bp/1e4*held.diff().abs().fillna(0)).dropna()).resample("1D").prod()-1).dropna().to_numpy()

def year(x, day_lim, dd_floor):
    """Rueckgabe (ueberlebt, Rendite, Grund)."""
    out=[]
    for st in range(0,len(x)-365):
        e=1.0; grund=None
        for i in range(st,st+365):
            if day_lim is not None and x[i]<-day_lim: grund="Tag";break
            e*=(1+x[i])
            if e<=1-dd_floor: grund="DD";break
        out.append((grund is None, e-1, grund or "-"))
    return out

d=sr_daily()
print("="*88)
print("Woran stirbt das gefundete Konto?  (S/R-Ausbruch, 12 Monate)")
print("="*88)
print(f"  {'Groesse':>8s} {'ueberlebt':>10s} {'am Tageslimit':>14s} {'am Drawdown':>13s}")
print("  "+"-"*50)
for lev in [0.35,0.50,0.75]:
    r=year(d*lev,0.03,0.06)
    g=pd.Series([q[2] for q in r]).value_counts(normalize=True)*100
    print(f"  {lev:>7.2f}x {g.get('-',0):>9.1f}% {g.get('Tag',0):>13.1f}% {g.get('DD',0):>12.1f}%")

print()
print("="*88)
print("Was aendert sich, wenn eine Regel wegfaellt?  (0,5x)")
print("="*88)
print(f"  {'Regelwerk':38s} {'ueberlebt':>10s} {'Ø Rendite':>11s} {'>=20 %':>8s}")
print("  "+"-"*70)
for name,dl,dd in [("6 % DD + 3 % Tageslimit (Kraken)",0.03,0.06),
                   ("6 % DD, KEIN Tageslimit",None,0.06),
                   ("10 % DD + 3 % Tageslimit",0.03,0.10),
                   ("10 % DD, kein Tageslimit",None,0.10),
                   ("20 % DD, kein Tageslimit",None,0.20),
                   ("eigenes Kapital (kein Limit)",None,0.99)]:
    r=year(d*0.5,dl,dd)
    s=np.array([q[0] for q in r]); ret=np.array([q[1] for q in r])
    print(f"  {name:38s} {s.mean()*100:>9.1f}% {ret.mean()*100:>+10.1f}% "
          f"{((s)&(ret>=.20)).mean()*100:>7.1f}%")

print()
print("="*88)
print("Und der Short-Straddle auf einem gefundeten Konto?")
print("="*88)
px=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)["close"].resample("1D").last().dropna()
iv=pd.read_csv(V+"dvol_BTC.csv",index_col=0,parse_dates=True)["close"].resample("1D").last().dropna()
df=pd.DataFrame({"px":px,"iv":iv}).dropna()
def bs(S,K,T,s):
    if T<=1e-9: return abs(S-K),(1.0 if S>K else -1.0)
    d1=(np.log(S/K)+.5*s*s*T)/(s*np.sqrt(T)); d2=d1-s*np.sqrt(T)
    return (S*norm.cdf(d1)-K*norm.cdf(d2))+(K*norm.cdf(-d2)-S*norm.cdf(-d1)), norm.cdf(d1)-norm.cdf(-d1)
# taegliche PnL-Reihe des gehedgten Straddles
daily=[]; i=0; T0=30
while i+T0<len(df):
    S0=df["px"].iloc[i]; sig=df["iv"].iloc[i]/100*0.98; K=S0
    prem,h0=bs(S0,K,T0/365,sig); hedge=h0; Sp=S0; acc=0.0
    for j in range(1,T0+1):
        Sj=df["px"].iloc[i+j]; Tj=(T0-j)/365
        newv,dn=bs(Sj,K,max(Tj,1e-9),df["iv"].iloc[i+j]/100)
        pnl_day=hedge*(Sj-Sp)-abs(dn-hedge)*Sj*5/1e4
        if j==T0: pnl_day+=prem-abs(Sj-K)-S0*3/1e4
        daily.append(pnl_day/S0); hedge=dn; Sp=Sj
    i+=T0
ds=np.array(daily)
print(f"  Taegliche Reihe: {len(ds)} Tage, Vol p.a. {ds.std()*np.sqrt(365)*100:.1f} %")
print(f"  {'Groesse':>8s} {'Jahresvol':>10s} {'ueberlebt':>10s} {'Ø Rendite':>11s} {'>=20 %':>8s}")
print("  "+"-"*54)
for lev in [0.5,1.0,1.5,2.0,3.0]:
    r=year(ds*lev,0.03,0.06)
    s=np.array([q[0] for q in r]); ret=np.array([q[1] for q in r])
    print(f"  {lev:>7.2f}x {ds.std()*np.sqrt(365)*lev*100:>9.1f}% {s.mean()*100:>9.1f}% "
          f"{ret.mean()*100:>+10.1f}% {((s)&(ret>=.20)).mean()*100:>7.1f}%")
