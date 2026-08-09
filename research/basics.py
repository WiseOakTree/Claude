"""Die vier Grundfragen -- ohne Strategie, ohne Indikator.

 1) Ist es gerade wahrscheinlicher, dass es rauf oder runter geht?
 2) Zu welcher Uhrzeit?
 3) Wie viel Risiko?
 4) Wenn man falsch lag -- was war der Grund?
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC")
d=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
c=d["close"].to_numpy(); n=len(d); idx=d.index

print("="*86)
print("FRAGE 1: Ist es wahrscheinlicher, dass es RAUF oder RUNTER geht?")
print("="*86)
print(f"  {'Horizont':>10s} {'P(rauf)':>9s} {'Suchzeitr.':>11s} {'Holdout':>9s} "
      f"{'Ø Rendite':>11s} {'p-Wert':>8s}")
print("  "+"-"*62)
for h,lab in [(1,"1 Stunde"),(4,"4 Stunden"),(24,"1 Tag"),(48,"2 Tage"),(168,"1 Woche")]:
    r=c[h:]/c[:-h]-1
    m=idx[:-h]<SPLIT
    ne=len(r)/h                       # Ueberlappungskorrektur
    t=r.mean()/(r.std()/np.sqrt(ne))
    p=2*(1-stats.norm.cdf(abs(t)))
    print(f"  {lab:>10s} {(r>0).mean()*100:>8.1f}% {(r[m]>0).mean()*100:>10.1f}% "
          f"{(r[~m]>0).mean()*100:>8.1f}% {r.mean()*1e4:>+10.1f}bp {p:>8.3f}")
print("\n  Muenzwurf waere 50,0 %. Kostenschwelle: 16 bp je Roundtrip.")

print()
print("="*86)
print("FRAGE 2: Zu welcher Uhrzeit? (UTC, naechste Stunde)")
print("="*86)
r1=pd.Series(c,index=idx).pct_change().shift(-1).dropna()
hr=r1.index.hour
print(f"  {'UTC':>4s} {'P(rauf)':>9s} {'Ø bp':>8s} {'p roh':>8s} {'p korrigiert':>13s} "
      f"{'Such Ø':>9s} {'Hold Ø':>9s}")
print("  "+"-"*66)
sig=[]
for h in range(24):
    m=hr==h; x=r1[m].to_numpy()
    t,p=stats.ttest_1samp(x,0)
    pb=min(p*24,1.0)
    ms=r1[m & (r1.index<SPLIT)].mean()*1e4; mh=r1[m & (r1.index>=SPLIT)].mean()*1e4
    star="  <<<" if pb<0.05 else ""
    if pb<0.05: sig.append(h)
    print(f"  {h:>4d} {(x>0).mean()*100:>8.1f}% {x.mean()*1e4:>+7.1f} {p:>8.3f} "
          f"{pb:>13.3f} {ms:>+8.1f} {mh:>+8.1f}{star}")
print(f"\n  Nach Bonferroni (24 Tests) signifikant: {sig if sig else 'KEINE Stunde'}")
print(f"  Groesster Unterschied roh: {(r1.groupby(hr).mean().max()-r1.groupby(hr).mean().min())*1e4:.1f} bp")
