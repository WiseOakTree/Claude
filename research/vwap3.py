"""Teil 3: Woher kommt der Vorsprung der VWAP-Baender? Von der
Volumengewichtung oder vom typischen Preis (HLC/3) statt Schlusskurs?"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
from scipy.stats import spearmanr
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from msb import bars4h, SPLIT
HOLD=30
print("="*88)
print("Zerlegung: vier Bandbreiten, die sich in genau zwei Merkmalen unterscheiden")
print("="*88)
print(f"{'Markt':<6}{'Variante':<40}{'Vol 5T HOLD':>13}{'Tag<=-3% HOLD':>15}")
for sym in ("btc","eth"):
    df=bars4h(sym); tp=(df.high+df.low+df.close)/3; v=df.volume; n=20
    r=np.log(df.close).diff()
    volf=r.shift(-HOLD).rolling(HOLD).std()*np.sqrt(6*365)
    neg=(r.shift(-HOLD).rolling(HOLD).min()<=np.log(0.97)).astype(float)
    vw=(tp*v).rolling(n).sum()/v.rolling(n).sum()
    sma_tp=tp.rolling(n).mean(); sma_c=df.close.rolling(n).mean()
    C={
     "Schlusskurs, ungewichtet (= Bollinger)": 2*df.close.rolling(n).std()/sma_c,
     "typ. Preis, ungewichtet":                2*tp.rolling(n).std()/sma_tp,
     "Schlusskurs, volumengewichtet":          np.sqrt(((df.close-vw)**2*v).rolling(n).sum()/v.rolling(n).sum())/vw,
     "typ. Preis, volumengewichtet (= VWAP)":  np.sqrt(((tp-vw)**2*v).rolling(n).sum()/v.rolling(n).sum())/vw,
    }
    A=pd.DataFrame(C); A["volf"]=volf; A["neg"]=neg
    A=A.replace([np.inf,-np.inf],np.nan).dropna(); ho=A.index>=SPLIT
    for k in C:
        b=spearmanr(A[k][ho],A.volf[ho]).statistic
        c=spearmanr(A[k][ho],A.neg[ho]).statistic
        print(f"{sym.upper():<6}{k:<40}{b:>13.3f}{c:>15.3f}")
    print()
