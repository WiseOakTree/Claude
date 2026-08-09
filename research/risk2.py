"""Teil 2: Zwei getrennte Fragen.

(a) Kann man das NIVEAU der kommenden Vol mit alten Koeffizienten treffen?
(b) Kann man RANGWEISE sagen, ob es gerade wilder wird als sonst?

(b) ist das, was fuer die Positionsgroesse zaehlt -- und ist eichungsfrei.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy.stats import spearmanr
import sys
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from risk import daily, predictors, targets, SPLIT

extra_names={"_har1":"|Rendite| gestern","_har5":"realisierte Vol 5 T",
             "_har22":"realisierte Vol 22 T"}

def more(df):
    c,h,l=df.close,df.high,df.low; r=np.log(c).diff(); AN=np.sqrt(365)
    M={}
    M["Abwaerts-Semivol 20 T"]=r.where(r<0,0).rolling(20).std()*AN
    M["groesster Rueckgang 10 T"]=-(c/c.rolling(10).max()-1)
    M["|Rendite| gestern"]=r.abs()*AN
    M["realisierte Vol 5 T (bisher)"]=r.rolling(5).std()*AN
    M["Spanne H/T gestern"]=np.log(h/l)*AN
    return pd.DataFrame(M,index=df.index)

for sym in ("btc","eth"):
    df=daily(sym); P=predictors(df,sym); T=targets(df); X=more(df)
    P=P.drop(columns=[c for c in P.columns if c.startswith("_")])
    A=pd.concat([P,X,T],axis=1).replace([np.inf,-np.inf],np.nan).dropna()
    tr=A.index<SPLIT; ho=A.index>=SPLIT
    print("="*96)
    print(f"{sym.upper()} -- Rangkorrelation (Spearman) mit der Zukunft, "
          f"getrennt nach Zeitraum")
    print("="*96)
    print(f"{'Praediktor':<26}{'Vol 5T Suche':>14}{'Vol 5T HOLD':>13}"
          f"{'Rueckg. Suche':>15}{'Rueckg. HOLD':>14}{'-3% HOLD':>11}")
    rows=[]
    for n in list(P.columns)+list(X.columns):
        a=spearmanr(A[n][tr],A["realisierte Vol 5 T"][tr]).statistic
        b=spearmanr(A[n][ho],A["realisierte Vol 5 T"][ho]).statistic
        cc=spearmanr(A[n][tr],A["max. Rueckgang 5 T"][tr]).statistic
        d=spearmanr(A[n][ho],A["max. Rueckgang 5 T"][ho]).statistic
        e=spearmanr(A[n][ho],A["Tag <= -3 % (ja/nein)"][ho]).statistic
        rows.append((n,a,b,cc,d,e))
    for n,a,b,cc,d,e in sorted(rows,key=lambda x:-x[2]):
        mark=" <--" if n.startswith("Bollinger") else ""
        print(f"{n:<26}{a:>14.3f}{b:>13.3f}{cc:>15.3f}{d:>14.3f}{e:>11.3f}{mark}")
    print()

print("="*96); print("Und die Frage (a): warum die Regressionen ins Negative kippen")
print("="*96)
for sym in ("btc","eth"):
    df=daily(sym); T=targets(df)
    v=T["realisierte Vol 5 T"].dropna()
    print(f"  {sym.upper()}  Ø realisierte Vol   Suche 2021-24: {v[v.index<SPLIT].mean()*100:>5.1f} %"
          f"   Holdout 2025-26: {v[v.index>=SPLIT].mean()*100:>5.1f} %")
print("\n  -> BTC: Niveau faellt 51,8 -> 39,0 %. Wer auf altem Niveau eicht,")
print("     sagt zu hohe Werte voraus. ETH aber kaum veraendert (65,4 -> 63,0 %)")
print("     -- dort ist die Rangaussage im Holdout schlicht schwach (0,04-0,19).")
