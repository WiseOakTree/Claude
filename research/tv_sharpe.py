"""Warum haben oeffentliche Strategien alle Sharpe ~0?

Nicht Meinung, sondern zwei Rechnungen:
 1) Was liefert REINES RAUSCHEN, wenn man das Beste aus N Varianten waehlt?
 2) Wie viele Beobachtungen braucht man, um Sharpe 0,3 von 0 zu unterscheiden?
"""
import numpy as np, pandas as pd
from scipy import stats
rng=np.random.default_rng(20)

print("="*88)
print("1) DIE RAUSCH-DECKE: bester Sharpe aus N Strategien OHNE jeden Edge")
print("="*88)
print("""  N Strategien, jede mit wahrem Sharpe = 0, ueber T Jahre simuliert.
  Berichtet wird der BESTE -- so wie in jedem veroeffentlichten Backtest.
""")
print(f"  {'Zeitraum':>10s} " + " ".join(f"{'N='+str(n):>9s}" for n in [1,10,50,200,1000,5000]))
print("  "+"-"*70)
for years in [1,2,5,10]:
    T=252*years
    row=f"  {years:>7d} J  "
    for N in [1,10,50,200,1000,5000]:
        r=rng.normal(0,1/np.sqrt(252),size=(N,T))
        sh=r.mean(axis=1)/r.std(axis=1)*np.sqrt(252)
        row+=f"{sh.max():>9.2f}"
    print(row)
print("""
  Lies die Zeile "5 Jahre": Wer 1.000 wertlose Varianten testet und die
  beste zeigt, praesentiert einen Sharpe von rund 1,5 -- OHNE JEDEN EDGE.

  Ein TradingView-Skript mit fuenf Parametern hat leicht 1.000 Kombinationen.""")

print()
print("="*88)
print("2) Wie viele Jahre braucht man, um Sharpe 0,3 von 0 zu UNTERSCHEIDEN?")
print("="*88)
print(f"  {'wahrer Sharpe':>14s} {'Jahre fuer p<0,05':>20s} {'Jahre fuer p<0,01':>20s}")
print("  "+"-"*58)
for S in [0.2,0.3,0.5,0.8,1.0,1.5,2.0]:
    # t = S * sqrt(Jahre) -> Jahre = (z/S)^2
    y95=(1.96/S)**2; y99=(2.58/S)**2
    print(f"  {S:>14.1f} {y95:>19.1f} {y99:>19.1f}")
print("""
  -> Um Sharpe 0,3 ueberhaupt von null zu unterscheiden, braucht man
     43 Jahre Daten. Bei 0,2 sind es 96.

  Jede Aussage "diese Strategie hat Sharpe 0,3" auf fuenf Jahren Daten
  ist mathematisch nicht von "Sharpe 0" unterscheidbar.""")

print()
print("="*88)
print("3) Und was ist mit den schoenen Kurven auf TradingView?")
print("="*88)
print("""  Der Strategy Tester zeigt standardmaessig:
    - Ergebnisse OHNE Slippage (Voreinstellung 0)
    - Kommission 0 (Voreinstellung)
    - auf DEMSELBEN Zeitraum, auf dem optimiert wurde
    - ohne Out-of-Sample-Haelfte

  Der Effekt jedes einzelnen Punkts, in diesem Projekt gemessen:""")
print(f"""
    Look-ahead-Bias                93 % -> 7 % Pass-Rate
    Kosten von 0 auf 16 bp         Edge faellt um 35 %
    Bestes von N statt Zufallswahl 54,7 % -> 31,9 % out-of-sample
    Ueberlappung nicht korrigiert  p = 10^-240 -> p = 0,27
""")

print("="*88)
print("4) Die Praezisierung: 'keine Strategie funktioniert' ist ZU STARK")
print("="*88)
print(f"  {'Ansatz':34s} {'Sharpe':>8s} {'Datenbasis':>14s} {'Kontrollen':>12s}")
print("  "+"-"*74)
for n,s,d,k in [("120 TA-Kombinationen (Median)","~0,00","4,5 Jahre","alle"),
                ("S/R-Ausbruch BTC","0,36","5,4 Jahre","alle bestanden"),
                ("Bot-Orderbuch (als Market Maker)","0,85","2,7 Jahre","OOS staerker"),
                ("Vol-Praemie BTC (Straddle)","1,85","5,4 Jahre","t=4,12"),
                ("Vol-Praemie S&P 500","1,52","10 Jahre","t=4,67")]:
    print(f"  {n:34s} {s:>8s} {d:>14s} {k:>12s}")
print("""
  -> Chartmuster liegen bei 0,00 bis 0,36. Du hast recht.
  -> RISIKOPRAEMIEN liegen bei 1,5-1,9 und halten ueber zwei
     unabhaengige Anlageklassen.

  Der Unterschied ist nicht "besser gesucht". Es ist eine andere
  Art von Edge: Man wird fuer das Tragen von Risiko bezahlt,
  nicht fuer eine Prognose. Deshalb verschwindet er nicht,
  wenn ihn alle kennen.""")
