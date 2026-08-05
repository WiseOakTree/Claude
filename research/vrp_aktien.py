"""Die Volatilitaets-Risikopraemie in AKTIEN statt Krypto.

In Krypto war sie der einzige Edge, der alle Kontrollen bestand (Sharpe 1,85).
In Aktien gibt es dafuer 36 Jahre Daten statt 5,4 -- und der VIX ist der
bestdokumentierte Risikoaufschlag der Finanzwissenschaft.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats as st

vix=pd.read_csv("fred_VIXCLS.csv",parse_dates=["date"]).set_index("date")["v"]
spx=pd.read_csv("fred_NASDAQCOM.csv",parse_dates=["date"]).set_index("date")["v"]
sp5=pd.read_csv("fred_SP500.csv",parse_dates=["date"]).set_index("date")["v"]
# S&P 500 ab 2016; davor Nasdaq als Traeger -- besser: nur SP500-Zeitraum plus
# langer Nasdaq-Test getrennt
def analyse(px,vx,name):
    d=pd.DataFrame({"px":px,"iv":vx}).dropna()
    r=np.log(d.px).diff()
    rv_fwd=r.shift(-21).rolling(21).std()*np.sqrt(252)*100     # realisiert DANACH
    x=pd.DataFrame({"iv":d.iv,"rv":rv_fwd}).dropna()
    vrp=x.iv-x.rv
    n_eff=len(vrp)/21
    t=vrp.mean()/(vrp.std()/np.sqrt(n_eff))
    print(f"\n  {name}  ({len(x)} Tage, {x.index[0]:%Y-%m} .. {x.index[-1]:%Y-%m})")
    print(f"    implizit (Median) {x.iv.median():5.1f} %   realisiert danach "
          f"{x.rv.median():5.1f} %   VRP {vrp.median():+5.2f} pp")
    print(f"    Anteil positiv {(vrp>0).mean()*100:5.1f} %   "
          f"t (ueberlappungskorrigiert) {t:5.2f}   p {2*(1-st.norm.cdf(abs(t))):.5f}")
    return x, vrp

print("="*88)
print("1) Existiert die Praemie in Aktien?")
print("="*88)
x1,v1=analyse(spx,vix,"Nasdaq gegen VIX, 1990-2026")
x2,v2=analyse(sp5,vix,"S&P 500 gegen VIX, 2016-2026")
print(f"\n  Zum Vergleich Krypto (BTC/DVOL, 5,4 Jahre): VRP +10,47 pp, t = 4,12")

print()
print("="*88)
print("2) Geerntet: monatlicher Short-Straddle auf den Index")
print("="*88)
from scipy.stats import norm
def bs(S,K,T,s):
    if T<=1e-9: return abs(S-K),(1.0 if S>K else -1.0)
    d1=(np.log(S/K)+.5*s*s*T)/(s*np.sqrt(T)); d2=d1-s*np.sqrt(T)
    return (S*norm.cdf(d1)-K*norm.cdf(d2))+(K*norm.cdf(-d2)-S*norm.cdf(-d1)), norm.cdf(d1)-norm.cdf(-d1)

def straddle(px,vx,ba=0.02,hedge_bp=2.0,fee_bp=2.0,T0=21):
    d=pd.DataFrame({"px":px,"iv":vx}).dropna()
    daily=[]; idx=[]; i=0
    while i+T0<len(d):
        S0=d.px.iloc[i]; K=S0
        valp,hedge=bs(S0,K,T0/252,d.iv.iloc[i]/100*(1-ba)); valp-=S0*fee_bp/1e4
        Sp=S0
        for j in range(1,T0+1):
            Sj=d.px.iloc[i+j]; Tj=(T0-j)/252
            val,dn=bs(Sj,K,max(Tj,1e-9),d.iv.iloc[i+j]/100)
            daily.append(((valp-val)+hedge*(Sj-Sp)-abs(dn-hedge)*Sj*hedge_bp/1e4)/S0)
            idx.append(d.index[i+j]); valp=val; hedge=dn; Sp=Sj
        i+=T0
    return pd.Series(daily,index=idx)

for nm,px_,lab in [("Nasdaq",spx,"1990-2026"),("S&P 500",sp5,"2016-2026")]:
    s=straddle(px_,vix)
    ann=(1+s).prod()**(252/len(s))-1; vol=s.std()*np.sqrt(252)
    eq=(1+s).cumprod(); dd=(eq/eq.cummax()-1).min()
    print(f"\n  {nm} {lab}: {len(s)} Tage")
    print(f"    Rendite p.a. {ann*100:+6.1f} %   Vol {vol*100:5.1f} %   "
          f"Sharpe {s.mean()/s.std()*np.sqrt(252):5.2f}")
    print(f"    groesster Drawdown {dd*100:6.1f} %   schlechtester Tag {s.min()*100:+6.2f} %   "
          f"Tage < -3 %: {(s<-.03).mean()*100:.2f} %")
    for a,b,l in [("1990","2000","1990er"),("2000","2010","2000er"),
                  ("2010","2020","2010er"),("2020","2027","2020er")]:
        m=s[(s.index>=a)&(s.index<b)]
        if len(m)>200:
            print(f"      {l}: Sharpe {m.mean()/m.std()*np.sqrt(252):5.2f}   "
                  f"p.a. {((1+m).prod()**(252/len(m))-1)*100:+6.1f} %")
    s.to_csv(f"straddle_{nm.replace(' ','').replace('&','')}.csv")
