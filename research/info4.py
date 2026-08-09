"""Teil 4: Wie viel sagen die drei Indikatoren einander -- und wie viele
unabhaengige Groessen bleiben uebrig?"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from msb import bars4h, macd, stoch, boll
btc=bars4h("btc"); c=btc.close
line,sig,hist=macd(c); K,Dl=stoch(btc); lo,mid,up,pctb=boll(c)
ret1=np.log(c).diff()
F=pd.DataFrame({
  "MACD-Linie":line/c, "MACD-Hist.":hist/c, "Stoch %K":K, "Stoch %K-%D":K-Dl,
  "Bollinger %B":pctb, "BB-Breite":(up-lo)/mid,
  "Momentum 20":c/c.shift(20)-1, "Vol 20 Bars":ret1.rolling(20).std(),
}).dropna()
print("="*88); print("Korrelationsmatrix (BTC 4h, 2021-26)"); print("="*88)
C=F.corr()
cols=list(F.columns)
print(f"{'':<14}" + "".join(f"{c_[:11]:>12}" for c_ in cols))
for i in cols:
    print(f"{i:<14}" + "".join(f"{C.loc[i,j]:>+12.2f}" for j in cols))

print("\n" + "="*88); print("Hauptkomponenten der SECHS Indikatorwerte"); print("="*88)
X=(F[cols[:6]]-F[cols[:6]].mean())/F[cols[:6]].std()
ev=np.linalg.eigvalsh(np.cov(X.T.to_numpy()))[::-1]
cum=np.cumsum(ev)/ev.sum()
for i,(e,cu) in enumerate(zip(ev,cum),1):
    print(f"  Komponente {i}: erklaert {e/ev.sum()*100:>5.1f} %   kumuliert {cu*100:>5.1f} %")
print(f"\n  -> {int(np.searchsorted(cum,0.90))+1} Komponenten erklaeren 90 % der Bewegung "
      f"aller sechs Werte.")
