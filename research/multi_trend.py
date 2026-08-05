"""Zeitreihen-Momentum (Trendfolge) auf einem diversifizierten Universum.

Das ist der einzige Strategietyp mit belastbarer Evidenz ueber Anlageklassen
hinweg (Moskowitz/Ooi/Pedersen 2012). Hier auf 20 Maerkten, teils seit 1971.

Look-ahead-frei: Signal aus Daten bis t-1, Ausfuehrung zu t.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, glob, os

MAP={"NASDAQCOM":("Aktien Nasdaq","px"),"SP500":("Aktien S&P 500","px"),
     "DCOILWTICO":("Rohoel WTI","px"),"DCOILBRENTEU":("Rohoel Brent","px"),
     "DHHNGSP":("Erdgas","px"),
     "DEXUSEU":("EUR/USD","px"),"DEXJPUS":("USD/JPY","px"),"DEXUSUK":("GBP/USD","px"),
     "DEXCAUS":("USD/CAD","px"),"DEXSZUS":("USD/CHF","px"),"DEXUSAL":("AUD/USD","px"),
     "DEXNOUS":("USD/NOK","px"),"DEXSDUS":("USD/SEK","px"),"DEXSFUS":("USD/ZAR","px"),
     "DEXKOUS":("USD/KRW","px"),"DEXMXUS":("USD/MXN","px"),"DEXBZUS":("USD/BRL","px"),
     "DEXINUS":("USD/INR","px"),
     "DGS10":("Anleihe 10J","yield8"),"DGS2":("Anleihe 2J","yield1.9")}

rets={}
for k,(name,kind) in MAP.items():
    f=f"fred_{k}.csv"
    if not os.path.exists(f): continue
    d=pd.read_csv(f,parse_dates=["date"]).set_index("date")["v"]
    d=d[~d.index.duplicated()].sort_index()
    if kind=="px":
        r=d.pct_change()
    else:
        dur=float(kind.replace("yield",""))
        r=-dur*d.diff()/100.0          # Anleihenrendite aus Renditeaenderung
    rets[name]=r.replace([np.inf,-np.inf],np.nan)
R=pd.DataFrame(rets)
R=R[R.index>="1990-01-01"]
R=R[R.notna().sum(axis=1)>=8]
print(f"Universum: {R.shape[1]} Maerkte, {len(R)} Handelstage, "
      f"{R.index[0]:%Y-%m} bis {R.index[-1]:%Y-%m}")
print(f"Mittlere Paarkorrelation: {R.corr().values[np.triu_indices(R.shape[1],1)].mean():+.3f}")
print("  (Krypto BTC/ETH/SOL/XRP lag bei +0,68)")

def backtest(R, lookback=252, volwin=60, target=0.15, cost_bp=2.0):
    """Long/Short nach Vorzeichen der Rendite ueber `lookback`, invers vol-gewichtet."""
    sig=np.sign(R.rolling(lookback).sum()).shift(1)          # t-1 -> keine Zukunft
    vol=R.rolling(volwin).std().shift(1)
    w=sig/vol.replace(0,np.nan)
    w=w.div(w.abs().sum(axis=1),axis=0)                       # gleiche Risikoanteile
    gross=(w*R).sum(axis=1)
    # Portfolio auf Zielvol skalieren (nur Vergangenheit)
    pv=gross.rolling(60).std().shift(1)*np.sqrt(252)
    k=(target/pv).clip(0,5).fillna(0)
    net=k*gross
    turn=(w.mul(k,axis=0)).diff().abs().sum(axis=1)
    return (net-cost_bp/1e4*turn).dropna()

def stats(r,label):
    ann=(1+r).prod()**(252/len(r))-1; vol=r.std()*np.sqrt(252)
    sh=r.mean()/r.std()*np.sqrt(252); eq=(1+r).cumprod()
    dd=(eq/eq.cummax()-1).min()
    print(f"  {label:26s} {ann*100:>+7.1f}% {vol*100:>7.1f}% {sh:>7.2f} {dd*100:>8.1f}% "
          f"{(r<-.03).mean()*100:>9.2f}% {r.min()*100:>+9.2f}%")

print()
print("="*94)
print("TRENDFOLGE AUF 20 MAERKTEN  (Zielvol 15 %, 2 bp Kosten je Roundtrip)")
print("="*94)
print(f"  {'':26s} {'p.a.':>8s} {'Vol':>8s} {'Sharpe':>7s} {'max. DD':>9s} "
      f"{'Tage<-3%':>10s} {'schlecht.Tag':>10s}")
print("  "+"-"*82)
r=backtest(R)
stats(r,"Portfolio (20 Maerkte)")
# Einzelmaerkte zum Vergleich
singles=[]
for c in R.columns:
    rr=backtest(R[[c]])
    if len(rr)>1000:
        singles.append(rr.mean()/rr.std()*np.sqrt(252))
print(f"\n  Mittlerer Sharpe der EINZELmaerkte: {np.mean(singles):.2f}")
print(f"  Sharpe des Portfolios:              {r.mean()/r.std()*np.sqrt(252):.2f}")
print(f"  -> Diversifikationsgewinn: Faktor {(r.mean()/r.std())/np.mean(singles)*np.sqrt(252):.1f}")

print()
print("  Out-of-Sample-Kontrolle (Zeitsplit):")
print(f"  {'':26s} {'p.a.':>8s} {'Vol':>8s} {'Sharpe':>7s} {'max. DD':>9s} "
      f"{'Tage<-3%':>10s} {'schlecht.Tag':>10s}")
print("  "+"-"*82)
for lab,m in [("1990-2007",r.index<"2008-01-01"),
              ("2008-2016",(r.index>="2008-01-01")&(r.index<"2017-01-01")),
              ("2017-2026",r.index>="2017-01-01")]:
    stats(r[m],lab)
