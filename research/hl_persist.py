"""Persistenz sauber: hohe Mindestvolumina in BEIDEN Perioden, damit die
Verhaeltnisse nicht durch kleine Nenner explodieren. Mit Schwellenanalyse."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy.stats import spearmanr
S="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/hl"
L=pd.read_csv(f"{S}/leaderboard.csv")
L["pnl_A"]=L.pnl_month-L.pnl_week; L["vlm_A"]=L.vlm_month-L.vlm_week
L["pnl_B"]=L.pnl_week-L.pnl_day;   L["vlm_B"]=L.vlm_week-L.vlm_day

print("="*92)
print("SCHWELLENANALYSE: haengt die Persistenz am Mindestvolumen?")
print("="*92)
print(f"{'Mindestvol. je Periode':>24}{'n':>8}{'Rho(PnL/Vol)':>15}"
      f"{'Rho(PnL/Wert)':>15}{'beide +':>10}{'erwartet':>10}")
for schwelle in (1e4,1e5,5e5,2e6,1e7,5e7):
    A=L[(L.vlm_A>schwelle)&(L.vlm_B>schwelle)&(L.wert>1000)].copy()
    if len(A)<60: continue
    A["rA"]=A.pnl_A/A.vlm_A; A["rB"]=A.pnl_B/A.vlm_B
    A["eA"]=A.pnl_A/A.wert;  A["eB"]=A.pnl_B/A.wert
    r1=spearmanr(A.rA,A.rB).statistic; r2=spearmanr(A.eA,A.eB).statistic
    beide=((A.rA>0)&(A.rB>0)).mean()*100
    erw=(A.rA>0).mean()*(A.rB>0).mean()*100
    print(f"{schwelle:>22,.0f} ${len(A):>8,}{r1:>+15.3f}{r2:>+15.3f}"
          f"{beide:>9.1f}%{erw:>9.1f}%")

print("\n"+"="*92)
print("HAUPTANALYSE bei 2 Mio $ Mindestvolumen je Periode")
print("="*92)
A=L[(L.vlm_A>2e6)&(L.vlm_B>2e6)&(L.wert>1000)].copy()
A["rA"]=A.pnl_A/A.vlm_A; A["rB"]=A.pnl_B/A.vlm_B
print(f"  Konten: {len(A):,}   Median Kontowert {A.wert.median():,.0f} $")
print(f"  PnL/Volumen frueher: 1. Perz {np.percentile(A.rA,1)*1e4:+.0f} bp, "
      f"Median {A.rA.median()*1e4:+.1f} bp, 99. Perz {np.percentile(A.rA,99)*1e4:+.0f} bp")
A["qA"]=pd.qcut(A.rA,5,labels=False,duplicates="drop")
print(f"\n  {'Quintil frueher':<18}{'n':>6}{'Ø PnL/Vol spaeter':>20}"
      f"{'Median spaeter':>17}{'Anteil im Plus':>17}")
for q in range(5):
    g=A[A.qA==q]
    print(f"  {q+1:<18}{len(g):>6}{g.rB.mean()*1e4:>+18.1f} bp"
          f"{g.rB.median()*1e4:>+15.1f} bp{(g.rB>0).mean()*100:>16.1f} %")
top=A.rA>=A.rA.quantile(0.90)
print(f"\n  Beste 10 % frueher (n={top.sum()}):")
print(f"    im Plus spaeter:            {(A[top].rB>0).mean()*100:>5.1f} %  "
      f"(alle: {(A.rB>0).mean()*100:.1f} %)")
print(f"    auch in den besten 10 %:    {(A[top].rB>=A.rB.quantile(0.90)).mean()*100:>5.1f} %  "
      f"(Zufall: 10,0 %)")
bot=A.rA<=A.rA.quantile(0.10)
print(f"  Schlechteste 10 % frueher: im Plus spaeter {(A[bot].rB>0).mean()*100:.1f} %, "
      f"wieder in den schlechtesten 10 %: {(A[bot].rB<=A.rB.quantile(0.10)).mean()*100:.1f} %")

print("\n"+"="*92)
print("DIE GRUNDVERTEILUNG: wer verdient auf Hyperliquid?")
print("="*92)
akt=L[L.vlm_allTime>1e6]
print(f"  Konten mit > 1 Mio $ Gesamtvolumen: {len(akt):,}")
print(f"  davon allTime im Plus: {(akt.pnl_allTime>0).mean()*100:.1f} %")
for s,lab in ((1e4,"> 10.000 $"),(1e5,"> 100.000 $"),(1e6,"> 1 Mio $"),(1e7,"> 10 Mio $")):
    n=(akt.pnl_allTime>s).sum()
    print(f"    Gewinn {lab:<14}{n:>6} Konten ({n/len(akt)*100:>5.2f} %)")
print(f"\n  Die obersten 1 % halten {akt.pnl_allTime.nlargest(int(len(akt)*0.01)).sum()/akt.pnl_allTime[akt.pnl_allTime>0].sum()*100:.1f} % "
      f"aller Gewinne.")
A.to_csv(f"{S}/top.csv",index=False)
