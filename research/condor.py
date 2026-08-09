"""Echter Iron Condor statt Naeherung -- mit Skew und OHNE Delta-Hedge.

Ersetzt die bisherige Kappungs-Naeherung durch:
  - explizite Strikes (Short-Strangle +-x %, Long-Fluegel +-(x+w) %)
  - Black-Scholes-Bepreisung mit VIX als ATM-Vol
  - VOLATILITAETS-SKEW: Puts teurer als Calls (linear in Log-Moneyness)
  - Abrechnung am Verfall aus der TATSAECHLICHEN Bewegung -> Delta-Drag ist drin
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy.stats import norm

px=pd.read_csv("fred_SP500.csv",parse_dates=["date"]).set_index("date")["v"]
vx=pd.read_csv("fred_VIXCLS.csv",parse_dates=["date"]).set_index("date")["v"]
d=pd.DataFrame({"px":px,"iv":vx}).dropna().sort_index()

def bsprice(S,K,T,s,typ):
    if T<=1e-9: return max(0.0,(S-K) if typ=="c" else (K-S))
    d1=(np.log(S/K)+.5*s*s*T)/(s*np.sqrt(T)); d2=d1-s*np.sqrt(T)
    return S*norm.cdf(d1)-K*norm.cdf(d2) if typ=="c" else K*norm.cdf(-d2)-S*norm.cdf(-d1)

def iv_at(atm,k,skew):
    """k = ln(K/S). Puts (k<0) teurer, Calls (k>0) billiger."""
    return max(atm - skew*k, 0.03)

def condor(x_pct, w_pct, skew=0.7, T0=21, fee_bp=1.0, stop=None):
    """Short-Strangle +-x_pct, Long-Fluegel +-(x_pct+w_pct). Rueckgabe: Monatsrenditen
    als Anteil des Index-Nominals, plus Kredit- und Verluststatistik."""
    out=[]; credits=[]; strad=[]
    i=0
    while i+T0<len(d):
        S=d.px.iloc[i]; atm=d.iv.iloc[i]/100; T=T0/252
        Kp,Kc=S*(1-x_pct), S*(1+x_pct)
        Lp,Lc=S*(1-x_pct-w_pct), S*(1+x_pct+w_pct)
        pr=lambda K,t: bsprice(S,K,T,iv_at(atm,np.log(K/S),skew),t)
        credit=(pr(Kp,"p")+pr(Kc,"c")) - (pr(Lp,"p")+pr(Lc,"c"))
        credit-=S*fee_bp/1e4*4                      # 4 Legs
        straddle=pr(S,"p")+pr(S,"c")
        ST=d.px.iloc[i+T0]
        loss=0.0
        if ST<Kp: loss=min(Kp-ST, Kp-Lp)
        elif ST>Kc: loss=min(ST-Kc, Lc-Kc)
        pnl=(credit-loss)/S
        if stop is not None:
            maxl=(w_pct*S-credit)/S
            pnl=max(pnl,-stop*maxl)                 # frueher Ausstieg
        out.append(pnl); credits.append(credit/S); strad.append(straddle/S)
        i+=T0
    r=pd.Series(out)
    return r, np.mean(credits), np.mean(strad), (w_pct-np.mean(credits))

print("="*94)
print("1) DEIN EINWAND ZUR PRAEMIE, GEPRUEFT: wie viel bleibt bei echtem Skew?")
print("="*94)
print(f"  {'Strangle':>9s} {'Fluegel':>8s} {'Skew':>6s} {'Kredit':>8s} {'Straddle':>9s} "
      f"{'Anteil':>8s} {'max.Verlust':>12s}")
print("  "+"-"*70)
for skew in [0.0,0.4,0.7,1.0]:
    r,cr,st,ml=condor(0.03,0.008,skew=skew)
    print(f"  {'3,0 %':>9s} {'0,8 %':>8s} {skew:>6.1f} {cr*100:>7.3f}% {st*100:>8.2f}% "
          f"{cr/st*100:>7.1f}% {ml*100:>11.2f}%")
print()
for x in [0.02,0.03,0.04,0.05]:
    r,cr,st,ml=condor(x,0.008,skew=0.7)
    print(f"  {x*100:>8.1f}% {'0,8 %':>8s} {0.7:>6.1f} {cr*100:>7.3f}% {st*100:>8.2f}% "
          f"{cr/st*100:>7.1f}% {ml*100:>11.2f}%")

print()
print("="*94)
print("2) MIT DELTA-DRAG (Abrechnung aus der echten Bewegung, kein Hedge)")
print("="*94)
print(f"  {'Strangle':>9s} {'Fluegel':>8s} {'Ø/Monat':>9s} {'p.a.':>8s} {'Vol':>7s} "
      f"{'Sharpe':>7s} {'Trefferq.':>10s} {'schlecht.Mon':>13s}")
print("  "+"-"*76)
best=None
for x in [0.02,0.025,0.03,0.04,0.05]:
    for w in [0.008,0.015]:
        r,cr,st,ml=condor(x,w,skew=0.7)
        ann=(1+r).prod()**(12/len(r))-1; vol=r.std()*np.sqrt(12)
        sh=r.mean()/r.std()*np.sqrt(12)
        print(f"  {x*100:>8.1f}% {w*100:>7.1f}% {r.mean()*100:>+8.3f}% {ann*100:>+7.2f}% "
              f"{vol*100:>6.2f}% {sh:>7.2f} {(r>0).mean()*100:>9.1f}% {r.min()*100:>+12.2f}%")
        if best is None or sh>best[0]: best=(sh,x,w,r,ml)
print(f"\n  Bester Sharpe: Strangle +-{best[1]*100:.1f} %, Fluegel {best[2]*100:.1f} %")

print()
print("="*94)
print("3) Hilft ein frueher Ausstieg (Stop bei Anteil des Maximalverlusts)?")
print("="*94)
x,w=best[1],best[2]
print(f"  {'Stop':>18s} {'p.a.':>8s} {'Vol':>7s} {'Sharpe':>7s} {'schlecht.Monat':>15s}")
print("  "+"-"*58)
for stop in [None,1.0,0.75,0.5,0.35]:
    r,cr,st,ml=condor(x,w,skew=0.7,stop=stop)
    ann=(1+r).prod()**(12/len(r))-1
    lab="kein Stop" if stop is None else f"{stop*100:.0f} % vom Max"
    print(f"  {lab:>18s} {ann*100:>+7.2f}% {r.std()*np.sqrt(12)*100:>6.2f}% "
          f"{r.mean()/r.std()*np.sqrt(12):>7.2f} {r.min()*100:>+14.2f}%")
