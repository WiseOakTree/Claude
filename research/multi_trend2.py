"""Fair gegenueber der Trendfolge: mehrere Zeithorizonte, Sektoraufteilung,
und die Frage, ob der Zerfall an meinem FX-lastigen Universum liegt.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, os
SEC={"NASDAQCOM":"Aktien","SP500":"Aktien","DJIA":"Aktien",
     "DCOILWTICO":"Rohstoffe","DCOILBRENTEU":"Rohstoffe","DHHNGSP":"Rohstoffe",
     "DEXUSEU":"FX","DEXJPUS":"FX","DEXUSUK":"FX","DEXCAUS":"FX","DEXSZUS":"FX",
     "DEXUSAL":"FX","DEXNOUS":"FX","DEXSDUS":"FX","DEXSFUS":"FX","DEXKOUS":"FX",
     "DEXMXUS":"FX","DEXBZUS":"FX","DEXINUS":"FX",
     "DGS10":"Anleihen","DGS2":"Anleihen"}
DUR={"DGS10":8.0,"DGS2":1.9}
rets={}
for k,s in SEC.items():
    f=f"fred_{k}.csv"
    if not os.path.exists(f): continue
    d=pd.read_csv(f,parse_dates=["date"]).set_index("date")["v"]
    d=d[~d.index.duplicated()].sort_index()
    r=(-DUR[k]*d.diff()/100.0) if k in DUR else d.pct_change()
    rets[k]=r.replace([np.inf,-np.inf],np.nan)
R=pd.DataFrame(rets); R=R[R.index>="1990-01-01"]; R=R[R.notna().sum(axis=1)>=8]

def bt(R,lbs=(252,),target=0.15,cost_bp=2.0):
    sigs=[np.sign(R.rolling(l).sum()).shift(1) for l in lbs]
    sig=sum(sigs)/len(sigs)
    vol=R.rolling(60).std().shift(1)
    w=sig/vol.replace(0,np.nan); w=w.div(w.abs().sum(axis=1),axis=0)
    g=(w*R).sum(axis=1)
    k=(target/(g.rolling(60).std().shift(1)*np.sqrt(252))).clip(0,5).fillna(0)
    turn=(w.mul(k,axis=0)).diff().abs().sum(axis=1)
    return (k*g-cost_bp/1e4*turn).dropna()

def sh(r): return r.mean()/r.std()*np.sqrt(252) if len(r)>100 else np.nan
P=[("1990-2007","1990","2008"),("2008-2016","2008","2017"),("2017-2026","2017","2027")]

print("="*84)
print("1) Liegt es am Zeithorizont?  (alle 20 Maerkte)")
print("="*84)
print(f"  {'Horizonte (Tage)':28s} {'gesamt':>8s} " + " ".join(f"{p[0]:>10s}" for p in P))
print("  "+"-"*72)
for lbs in [(21,),(63,),(126,),(252,),(504,),(63,126,252),(21,63,126,252,504)]:
    r=bt(R,lbs)
    row=f"  {str(lbs):28s} {sh(r):>8.2f} "
    for _,a,b in P: row+=f"{sh(r[(r.index>=a)&(r.index<b)]):>10.2f} "
    print(row)

print()
print("="*84)
print("2) Liegt es am Sektor?  (Horizonte 63/126/252)")
print("="*84)
print(f"  {'Sektor':16s} {'Maerkte':>8s} {'gesamt':>8s} " + " ".join(f"{p[0]:>10s}" for p in P))
print("  "+"-"*72)
for s in ["Aktien","Rohstoffe","FX","Anleihen"]:
    cols=[c for c in R.columns if SEC[c]==s]
    if not cols: continue
    r=bt(R[cols],(63,126,252))
    row=f"  {s:16s} {len(cols):>8d} {sh(r):>8.2f} "
    for _,a,b in P: row+=f"{sh(r[(r.index>=a)&(r.index<b)]):>10.2f} "
    print(row)
r=bt(R,(63,126,252))
row=f"  {'ALLE':16s} {len(R.columns):>8d} {sh(r):>8.2f} "
for _,a,b in P: row+=f"{sh(r[(r.index>=a)&(r.index<b)]):>10.2f} "
print(row)

print()
print("="*84)
print("3) Und wenn man gar nicht folgt, sondern GEGEN den Trend?")
print("="*84)
rr=-bt(R,(63,126,252))
print(f"  Trendfolge      Sharpe {sh(r):+.2f}")
print(f"  Gegen den Trend Sharpe {sh(rr):+.2f}")
print()
print("="*84)
print("4) Der Vergleich, auf den es ankommt")
print("="*84)
best=bt(R,(63,126,252))
a=(1+best).prod()**(252/len(best))-1; v=best.std()*np.sqrt(252)
eq=(1+best).cumprod()
print(f"  {'':30s} {'Sharpe':>7s} {'Vol':>7s} {'max.DD':>8s} {'Tage<-3%':>9s} {'Korrelation':>12s}")
print("  "+"-"*76)
print(f"  {'Trendfolge 20 Maerkte':30s} {sh(best):>7.2f} {v*100:>6.1f}% "
      f"{(eq/eq.cummax()-1).min()*100:>7.1f}% {(best<-.03).mean()*100:>8.2f}% {'+0,001':>12s}")
print(f"  {'S/R-Ausbruch BTC (Krypto)':30s} {1.07:>7.2f} {25.0:>6.1f}% {-30.4:>7.1f}% "
      f"{0.36:>8.2f}% {'+0,68':>12s}")
print(f"  {'Short-Straddle BTC':30s} {1.85:>7.2f} {13.6:>6.1f}% {-13.7:>7.1f}% "
      f"{0.68:>8.2f}% {'-':>12s}")
