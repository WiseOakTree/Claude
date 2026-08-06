"""Teil 3: Der Zahltag. Bringt ein besserer Risikoindikator eine hoehere
Pass-Rate -- bei GLEICHEM durchschnittlichem Einsatz?"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from risk import daily, SPLIT
D="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
COST=8e-4; AN=np.sqrt(365)

df=daily("btc"); c=df.close; r=np.log(c).diff(); h,l,o=df.high,df.low,df.open
sig={}
m=c.rolling(20).mean(); sd=c.rolling(20).std()
sig["Bollinger-Breite"]=4*sd/m
sig["realisierte Vol 20 T"]=r.rolling(20).std()*AN
sig["EWMA (lambda 0,94)"]=np.sqrt((r**2).ewm(alpha=0.06,adjust=False).mean())*AN
sig["Abwaerts-Semivol 20 T"]=r.where(r<0,0).rolling(20).std()*AN
tr_=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
sig["ATR(14)"]=tr_.rolling(14).mean()/c*AN
iv=pd.read_csv(D+"dvol_BTC.csv",index_col=0,parse_dates=True).close
sig["DVOL (implizite Vol)"]=iv.resample("1D").last().reindex(df.index).ffill()/100

ret=c.pct_change().fillna(0).to_numpy()

def passrate(w):
    """w = taegliche Positionsgroesse (schon um 1 Tag verzoegert)."""
    turn=np.abs(np.diff(np.concatenate([[0.0],w])))
    s=w*ret-COST*turn
    n=len(s); ok=tot=0
    for st in range(0,n-30,3):
        e=1.0
        for k in range(st,n):
            e*=(1+s[k])
            if s[k]<-0.03 or e-1<=-0.06: hit=False; break
            if e-1>=0.10: hit=True; break
        else: continue
        ok+=hit; tot+=1
    return (ok/tot*100 if tot else 0), tot

print("="*84)
print("BTC long-only. Feste Groesse gegen vol-gesteuerte Groesse,")
print("jeweils auf denselben DURCHSCHNITTLICHEN Einsatz normiert.")
print("="*84)
base=0.35
fixed=np.full(len(c),base)
pr0,_=passrate(fixed)
print(f"  {'feste Groesse 0,35x':<28}Ø Einsatz {base:.2f}x   Pass-Rate {pr0:>5.1f} %\n")
print(f"  {'Steuergroesse':<28}{'Pass-Rate':>11}{'gegen fest':>13}{'max. DD':>10}")
rows=[]
for name,x in sig.items():
    v=x.shift(1)                       # nur Vergangenheit
    w=(v.median()/v).clip(0.25,3.0)    # invers zur Vol
    w=(w*base/np.nanmean(w)).fillna(base).to_numpy()   # gleicher Ø Einsatz
    pr,_=passrate(w)
    eq=np.cumprod(1+w*ret); dd=(eq/np.maximum.accumulate(eq)-1).min()*100
    rows.append((name,pr,pr-pr0,dd))
eqf=np.cumprod(1+fixed*ret); ddf=(eqf/np.maximum.accumulate(eqf)-1).min()*100
for n,p,d,dd in sorted(rows,key=lambda x:-x[1]):
    print(f"  {n:<28}{p:>10.1f} %{d:>+12.1f} Pp{dd:>9.1f} %")
print(f"  {'(feste Groesse zum Vergleich)':<28}{pr0:>10.1f} %{0.0:>+12.1f} Pp{ddf:>9.1f} %")
