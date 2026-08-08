"""Persistenz auf echten, on-chain verifizierbaren Daten.

Die Fenster ueberlappen (allTime > month > week > day). Fuer einen sauberen
Test bilde ich DISJUNKTE Perioden ueber Differenzen:
   Periode A = month - week  (die frueheren ~3 Wochen)
   Periode B = week          (die letzte Woche)
A und B ueberschneiden sich nicht.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy.stats import spearmanr
S="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/hl"
L=pd.read_csv(f"{S}/leaderboard.csv")

# nur Konten mit ernsthafter Aktivitaet in BEIDEN Perioden
L["pnl_A"]=L.pnl_month-L.pnl_week          # frueher
L["pnl_B"]=L.pnl_week-L.pnl_day            # spaeter (ohne heute)
L["vlm_A"]=L.vlm_month-L.vlm_week
L["vlm_B"]=L.vlm_week-L.vlm_day
akt=(L.vlm_A>10_000)&(L.vlm_B>10_000)&(L.wert>500)
A=L[akt].copy()
print(f"Konten gesamt: {len(L):,}   aktiv in beiden Perioden: {len(A):,}")
# Rendite relativ zum Volumen -- fair ueber Kontogroessen hinweg
A["rA"]=A.pnl_A/A.vlm_A; A["rB"]=A.pnl_B/A.vlm_B
# und relativ zum Kontowert
A["eA"]=A.pnl_A/A.wert;  A["eB"]=A.pnl_B/A.wert

print("\n"+"="*88)
print("1. PERSISTENZ: sagt die fruehere Periode die spaetere voraus?")
print("="*88)
for lab,(a,b) in {"PnL je Volumen":("rA","rB"),"PnL je Kontowert":("eA","eB"),
                  "PnL absolut":("pnl_A","pnl_B")}.items():
    rho=spearmanr(A[a],A[b]).statistic
    print(f"  {lab:<22} Rangkorrelation frueher <-> spaeter: {rho:>+7.3f}")

print("\n"+"="*88)
print("2. BLEIBEN DIE BESTEN OBEN? (Quintile nach PnL je Volumen)")
print("="*88)
A["qA"]=pd.qcut(A.rA,5,labels=False,duplicates="drop")
print(f"  {'Quintil frueher':<20}{'n':>7}{'Ø PnL/Vol spaeter':>20}{'Anteil im Plus':>18}")
for q in range(5):
    g=A[A.qA==q]
    print(f"  {q+1:<20}{len(g):>7}{g.rB.mean()*1e4:>+18.1f} bp{(g.rB>0).mean()*100:>16.1f} %")
oben=A.rA>=A.rA.quantile(0.99)
print(f"\n  Beste 1 % frueher (n={oben.sum()}):")
print(f"    davon auch in den besten 1 % spaeter: "
      f"{(A[oben].rB>=A.rB.quantile(0.99)).mean()*100:>5.1f} %   (Zufall: 1,0 %)")
print(f"    davon im Plus in der spaeteren Periode: "
      f"{(A[oben].rB>0).mean()*100:>5.1f} %   (alle Konten: {(A.rB>0).mean()*100:.1f} %)")
unten=A.rA<=A.rA.quantile(0.01)
print(f"  Schlechteste 1 % frueher: im Plus spaeter {(A[unten].rB>0).mean()*100:.1f} %")

print("\n"+"="*88)
print("3. WAS UNTERSCHEIDET DIE DAUERHAFT GUTEN?")
print("="*88)
gut=(A.rA>0)&(A.rB>0)          # in BEIDEN Perioden im Plus
schlecht=(A.rA<0)&(A.rB<0)
print(f"  in beiden Perioden im Plus:  {gut.sum():>6} ({gut.mean()*100:.1f} %)")
print(f"  in beiden Perioden im Minus: {schlecht.sum():>6} ({schlecht.mean()*100:.1f} %)")
print(f"  bei Unabhaengigkeit erwartet: "
      f"{(A.rA>0).mean()*(A.rB>0).mean()*100:.1f} % bzw. "
      f"{(A.rA<0).mean()*(A.rB<0).mean()*100:.1f} %")
print()
print(f"  {'Merkmal':<26}{'dauerhaft gut':>16}{'dauerhaft schlecht':>21}{'alle':>12}")
for lab,col,fmt in (("Kontowert (Median $)","wert","{:,.0f}"),
                    ("Volumen/Monat (Median $)","vlm_month","{:,.0f}"),
                    ("Umschlag (Vol/Wert)","umschlag","{:.1f}"),
                    ("PnL je Volumen (bp)","rmit","{:+.1f}")):
    A["umschlag"]=A.vlm_month/A.wert
    A["rmit"]=(A.pnl_A+A.pnl_B)/(A.vlm_A+A.vlm_B)*1e4
    print(f"  {lab:<26}{fmt.format(A[gut][col].median()):>16}"
          f"{fmt.format(A[schlecht][col].median()):>21}{fmt.format(A[col].median()):>12}")
A.to_csv(f"{S}/aktiv.csv",index=False)
