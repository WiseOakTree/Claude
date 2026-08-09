"""Teil 2: Was sagen sie dir, wenn du hinschaust? Bedingte Tabellen --
und die Frage, ob sie etwas enthalten, was nicht schon im Preis steht."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from msb import bars4h, macd, stoch, boll, SPLIT
HOLD=30
btc=bars4h("btc"); c=btc.close
line,sig,hist=macd(c); K,Dl=stoch(btc); lo,mid,up,pctb=boll(c)
width=((up-lo)/mid)
ret1=np.log(c).diff()
vol_past=ret1.rolling(20).std()*np.sqrt(6*365)      # realisierte Vol, 20 Bars
mom_past=c/c.shift(20)-1
f=np.full(len(c),np.nan); a=c.to_numpy(); f[:-HOLD]=a[HOLD:]/a[:-HOLD]-1
fwd=pd.Series(f,index=c.index)
vol_fwd=ret1.shift(-HOLD).rolling(HOLD).std()*np.sqrt(6*365)

print("="*80)
print("BEDINGTE TABELLEN: Was passiert in den naechsten 5 Tagen? (BTC 4h, 2021-26)")
print("="*80)
for name,x in [("Stochastik %K",K),("Bollinger %B",pctb*100),
               ("MACD-Histogramm",hist/c*1e4),("Bollinger-Breite",width*100)]:
    q=pd.qcut(x,5,labels=["sehr tief","tief","mitte","hoch","sehr hoch"],duplicates="drop")
    g=pd.DataFrame({"q":q,"fwd":fwd,"vol":vol_fwd}).dropna()
    t=g.groupby("q",observed=True).agg(n=("fwd","size"),
        mittel=("fwd",lambda s:s.mean()*100), med=("fwd",lambda s:s.median()*100),
        anteil_plus=("fwd",lambda s:(s>0).mean()*100),
        schlechteste5=("fwd",lambda s:np.percentile(s,5)*100),
        vol=("vol",lambda s:s.mean()*100))
    print(f"\n{name}:")
    print(f"  {'Korb':<11}{'n':>6}{'Ø Rendite':>11}{'Median':>9}{'Anteil +':>10}"
          f"{'schlecht. 5%':>14}{'kommende Vol':>14}")
    for i,r in t.iterrows():
        n=int(r['n']); mi_=r['mittel']; md=r['med']; ap=r['anteil_plus']
        s5=r['schlechteste5']; vv=r['vol']
        print(f"  {str(i):<11}{n:>6}{mi_:>+10.2f}%{md:>+8.2f}%"
              f"{ap:>9.1f}%{s5:>+13.1f}%{vv:>13.0f}%")
    print(f"  Spanne Rendite: {t.mittel.max()-t.mittel.min():>5.2f} Pp   "
          f"Spanne kommende Vol: {t.vol.max()-t.vol.min():>4.0f} Pp")

print("\n"+"="*80)
print("ENTHALTEN SIE ETWAS, WAS NICHT SCHON IM PREIS STEHT?")
print("="*80)
base=pd.DataFrame({"Bollinger-Breite":width,"realisierte Vol (20 Bars)":vol_past,
                   "Stochastik %K":K,"Momentum 20 Bars":mom_past,
                   "MACD-Linie":line/c,"Bollinger %B":pctb}).dropna()
print("\nKorrelation der Indikatoren mit dem, was direkt im Preis steht:")
print(f"  Bollinger-Breite  <->  realisierte Vol (20 Bars):  "
      f"{base['Bollinger-Breite'].corr(base['realisierte Vol (20 Bars)']):+.3f}")
print(f"  Stochastik %K     <->  Momentum 20 Bars:           "
      f"{base['Stochastik %K'].corr(base['Momentum 20 Bars']):+.3f}")
print(f"  Bollinger %B      <->  Stochastik %K:              "
      f"{base['Bollinger %B'].corr(base['Stochastik %K']):+.3f}")
print(f"  MACD-Linie        <->  Momentum 20 Bars:           "
      f"{base['MACD-Linie'].corr(base['Momentum 20 Bars']):+.3f}")

print("\n"+"="*80)
print("VOLATILITAETSPROGNOSE: R^2 fuer die kommenden 5 Tage")
print("="*80)
d=pd.DataFrame({"w":width,"v":vol_past,"y":vol_fwd}).dropna()
tr=d.index<SPLIT; ho=d.index>=SPLIT
def r2(x,y):
    x=np.asarray(x); y=np.asarray(y)
    return np.corrcoef(x,y)[0,1]**2
print(f"{'Praediktor':<34}{'Suche 21-24':>13}{'Holdout 25-26':>15}")
print(f"  {'Bollinger-Breite':<32}{r2(d.w[tr],d.y[tr]):>13.3f}{r2(d.w[ho],d.y[ho]):>15.3f}")
print(f"  {'realisierte Vol (ohne Indikator)':<32}{r2(d.v[tr],d.y[tr]):>13.3f}{r2(d.v[ho],d.y[ho]):>15.3f}")
import numpy.linalg as la
X=np.column_stack([np.ones(tr.sum()),d.v[tr],d.w[tr]])
b=la.lstsq(X,d.y[tr],rcond=None)[0]
pred_ho=np.column_stack([np.ones(ho.sum()),d.v[ho],d.w[ho]])@b
print(f"  {'beide zusammen':<32}{r2(X@b,d.y[tr]):>13.3f}{r2(pred_ho,d.y[ho]):>15.3f}")
print("\n  -> Zuwachs durch die Bollinger-Breite gegenueber der reinen Vol:")
print(f"     Suche {r2(X@b,d.y[tr])-r2(d.v[tr],d.y[tr]):+.4f}   "
      f"Holdout {r2(pred_ho,d.y[ho])-r2(d.v[ho],d.y[ho]):+.4f}")
