"""Der quantitative Kern: Sharpe bestimmt, wie viel Hebel man ueberlebt --
und damit, was aus einem Edge wird. Plus: wie viele Edges braucht eine Firma?
"""
import numpy as np, pandas as pd
print("="*86)
print("1) WARUM SHARPE ALLES IST: wie viel Hebel traegt welcher Sharpe?")
print("="*86)
print("""  Regel: Bei Sharpe S und Zielvolatilitaet v ist die Rendite S x v.
  Der Drawdown skaliert mit v, die Rendite auch -- das Verhaeltnis
  Rendite/Drawdown haengt NUR am Sharpe.
""")
rng=np.random.default_rng(1)
def maxdd(S, years=10, n=4000):
    """Typischer Maximal-Drawdown in Vielfachen der Jahresvol."""
    d=rng.normal(S/252, 1/np.sqrt(252), size=(n, 252*years))
    eq=np.cumsum(d,axis=1)
    dd=(np.maximum.accumulate(eq,axis=1)-eq).max(axis=1)
    return np.median(dd)
print(f"  {'Sharpe':>7s} {'typ. max. DD':>14s} {'sicherer Hebel':>16s} "
      f"{'Rendite bei 10 % DD':>21s}")
print("  "+"-"*62)
for S in [0.36,0.5,0.85,1.0,1.5,2.0,3.0,5.0]:
    dd=maxdd(S)                      # in Einheiten der Jahresvol
    lev=0.10/ (dd*0.01) if dd>0 else 0
    # Zielvol so, dass der Drawdown 10 % betraegt:
    vol=0.10/dd
    print(f"  {S:>7.2f} {dd:>13.2f}x {vol*100:>15.0f}% {S*vol*100:>20.1f}%")
print("""
  Lies die letzte Spalte: Bei GLEICHEM Drawdown von 10 % liefert
  Sharpe 0,36 rund 2 % im Jahr -- Sharpe 3,0 liefert ueber 30 %.
  Nicht weil der Edge groesser ist, sondern weil er ruhiger ist.""")

print()
print("="*86)
print("2) Wie viele Edges braucht eine Firma fuer Sharpe 3?")
print("="*86)
print("""  Bei UNKORRELIERTEN Strategien waechst der Sharpe mit sqrt(N).
  Gemessen in diesem Projekt: 20 Maerkte -> Faktor 3,5 (theoretisch 4,47).
  Effizienz also rund 78 %.
""")
eff=3.5/np.sqrt(20)
print(f"  {'Ziel-Sharpe':>12s} {'noetige Anzahl (ideal)':>24s} {'mit 78 % Effizienz':>21s}")
print("  "+"-"*60)
for tgt in [0.5,1.0,1.5,2.0,3.0,5.0]:
    n_ideal=(tgt/0.36)**2
    n_real=(tgt/(0.36*eff))**2
    print(f"  {tgt:>12.1f} {n_ideal:>23.0f} {n_real:>20.0f}")
print("""
  -> Fuer Sharpe 3 braucht man rund 70 unkorrelierte Strategien --
     oder 115, wenn sie nur zu 78 % unabhaengig sind.

  DAS ist der eigentliche Unterschied. Keine Firma hat EINEN
  grossartigen Edge. Sie haben siebzig mittelmaessige, die
  nicht miteinander korrelieren.""")

print()
print("="*86)
print("3) Und was kostet es, siebzig Edges zu finden?")
print("="*86)
print("""  Aus diesem Projekt hochgerechnet:
    getestete Ansaetze         ~40
    davon out-of-sample haltbar  2   (VRP, S/R-Ausbruch)
    Trefferquote               ~5 %

  Fuer 70 haltbare Edges muesste man also rund 1.400 Ansaetze
  testen -- mit derselben Sorgfalt: Look-ahead-Kontrolle,
  Ueberlappungskorrektur, Holdout, Bonferroni.

  Das ist kein Wissensvorsprung. Das ist eine Fabrik.
  Genau dafuer stellt Jane Street 200 Forscher ein.""")
