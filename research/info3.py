"""Teil 3: Die zwei Muster, die in den bedingten Tabellen auffallen, sauber
geprueft -- Monotonie, Ueberlappungskorrektur, Holdout."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from msb import bars4h, macd, stoch, boll, SPLIT
HOLD=30; COST=8e-4

def setup(sym):
    df=bars4h(sym); c=df.close
    line,sig,hist=macd(c); K,Dl=stoch(df); lo,mid,up,pctb=boll(c)
    a=c.to_numpy(); f=np.full(len(a),np.nan); f[:-HOLD]=a[HOLD:]/a[:-HOLD]-1
    ret1=np.log(c).diff(); volf=ret1.shift(-HOLD).rolling(HOLD).std()*np.sqrt(6*365)
    return df,pd.DataFrame({"K":K,"pctB":pctb,"width":(up-lo)/mid,
                            "fwd":f,"volf":volf},index=df.index)

def quint(d, col, target="fwd"):
    g=d.dropna(subset=[col,target]).copy()
    g["q"]=pd.qcut(g[col],5,labels=False,duplicates="drop")
    return g.groupby("q",observed=True)[target].agg(
        n="size",mittel=lambda s:s.mean()*100,plus=lambda s:(s>0).mean()*100)

print("="*80); print("A. Bollinger %B -- die fehlende Tabelle (BTC gesamt)"); print("="*80)
btc,d=setup("btc")
t=quint(d,"pctB")
print(f"  {'Korb':<6}{'n':>7}{'Ø Rendite':>12}{'Anteil +':>11}")
for i,r in t.iterrows(): print(f"  {int(i)+1:<6}{int(r['n']):>7}{r['mittel']:>+11.2f}%{r['plus']:>10.1f}%")

print("\n"+"="*80)
print("B. Das Muster 'hoher Stochastik -> weniger oft plus' geprueft")
print("="*80)
print(f"{'Markt':<6}{'Zeitraum':<16}{'unterstes 20 %':>16}{'oberstes 20 %':>15}{'Spanne':>9}{'t':>7}")
for sym in ("btc","eth","sol"):
    df,d=setup(sym)
    for nm,m in (("Suche 21-24",d.index<SPLIT),("HOLDOUT 25-26",d.index>=SPLIT)):
        g=d[m].dropna(subset=["K","fwd"]).copy()
        if len(g)<300: continue
        g["q"]=pd.qcut(g.K,5,labels=False,duplicates="drop")
        lo_=g[g.q==0].fwd; hi=g[g.q==4].fwd
        # Long-Short-Portfolio: unten long, oben short
        r=np.concatenate([lo_.to_numpy(),-hi.to_numpy()])-2*COST
        ne=max(len(r)/HOLD,2); t_=r.mean()/(r.std(ddof=1)/np.sqrt(ne))
        print(f"{sym.upper():<6}{nm:<16}{lo_.mean()*100:>+15.2f}%{hi.mean()*100:>+14.2f}%"
              f"{(lo_.mean()-hi.mean())*100:>+8.2f}{t_:>7.2f}")
    print()

print("="*80)
print("C. Bollinger-Breite -> kommende Volatilitaet (der eigentliche Nutzen)")
print("="*80)
print(f"{'Markt':<6}{'Zeitraum':<16}{'engstes 20 %':>14}{'weitestes 20 %':>16}{'Faktor':>9}")
for sym in ("btc","eth","sol"):
    df,d=setup(sym)
    for nm,m in (("Suche 21-24",d.index<SPLIT),("HOLDOUT 25-26",d.index>=SPLIT)):
        g=d[m].dropna(subset=["width","volf"]).copy()
        if len(g)<300: continue
        g["q"]=pd.qcut(g.width,5,labels=False,duplicates="drop")
        a_=g[g.q==0].volf.mean()*100; b_=g[g.q==4].volf.mean()*100
        print(f"{sym.upper():<6}{nm:<16}{a_:>13.0f}%{b_:>15.0f}%{b_/a_:>9.2f}x")
    print()
