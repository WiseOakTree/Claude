"""Wie verdienen Firmen Geld? Zwei voellig verschiedene Antworten.

A) PROP-FIRMEN: verkaufen Evaluierungen. Rechnung aus SICHT DER FIRMA.
B) HANDELSFIRMEN: echte Edges. Alle in diesem Projekt bereits gemessen.
"""
import numpy as np, pandas as pd
print("="*88)
print("A) DIE PROP-FIRMA: Rechnung aus IHRER Sicht")
print("="*88)
FEE=85; ACC=10000; SPLIT=0.80
print(f"""  Kraken Starter: {FEE} $ Gebuehr, {ACC:,} $ Konto, {SPLIT*100:.0f} % Split.

  Firmengewinn je verkaufter Challenge
    = Gebuehr - P(besteht) x erwartete Auszahlung
""")
print(f"  {'P(besteht)':>11s} {'Auszahlung wenn gefunded':>26s} {'Firmengewinn je Challenge':>27s}")
print("  "+"-"*68)
for p in [0.05,0.10,0.20,0.35,0.50,0.70]:
    for payout in [500,1000,2000]:
        pass
    row=f"  {p*100:>10.0f}% "
    for payout in [500,1000,2000,4000]:
        row+=f"{FEE-p*payout:>+8.0f}$ "
    print(f"  {p*100:>10.0f}%  " + "  ".join(
        f"{payout:>5}$ -> {FEE-p*payout:>+6.0f}$" for payout in [500,2000,4000]))
print(f"""
  Lies die Zeilen: Bei einer Bestehensquote von 5-10 % -- dem
  Branchendurchschnitt -- verdient die Firma an fast jeder Challenge.
  Bei 50 % und 2.000 $ Auszahlung verliert sie 915 $ je Stueck.

  -> Das Geschaeftsmodell IST die Durchfallquote. Kein Handels-Edge.""")

print()
print("="*88)
print("Ab welcher Bestehensquote wird die Prop-Firma unprofitabel?")
print("="*88)
print(f"  {'Ø Auszahlung je gefundetem Konto':>34s} {'kritische Quote':>17s}")
print("  "+"-"*54)
for payout in [300,500,1000,2000,4000,8000]:
    print(f"  {payout:>33,d}$ {FEE/payout*100:>16.1f}%")
print(f"""
  Bei realistischen 1.000-2.000 $ Auszahlung liegt die kritische
  Quote bei 4-9 %. Alles darueber kostet die Firma Geld.

  Deshalb gibt es Konsistenzregeln, Tageslimits, trailende Drawdowns
  und Mindesthandelstage: Jede dieser Regeln senkt die Quote.
  Sie sind KEIN Risikomanagement fuer dich -- sie sind das Produkt.""")

print()
print("="*88)
print("B) DIE HANDELSFIRMA: die echten Edges -- alle hier gemessen")
print("="*88)
rows=[
 ("Market Making / Liquiditaet",
  "Orderflow-IC NEGATIV: -0,041, p=3e-173",
  "Wer nimmt, zahlt. Wer stellt, kassiert.", "0,3-1,3 bp je Trade"),
 ("Volatilitaets-Risikopraemie",
  "BTC t=4,12 | S&P t=4,67",
  "Versicherung verkaufen, Kapital stellen", "Sharpe 1,5-1,9"),
 ("Orderbuch-Ungleichgewicht",
  "+0,87 bp, 110.786 Trades, OOS staerker",
  "nur bei Rebate-Kosten profitabel", "+19 % p.a. als MM"),
 ("Diversifikation",
  "Korrelation +0,001 ueber 20 Maerkte",
  "viele kleine Edges statt einem grossen", "Sharpe x3,5"),
 ("Kostenstruktur",
  "-331 % p.a. als Taker, +41 % als MM",
  "derselbe Edge, andere Gebuehren", "Faktor 18"),
]
for name,mess,mech,wert in rows:
    print(f"\n  {name}")
    print(f"    gemessen:  {mess}")
    print(f"    Mechanik:  {mech}")
    print(f"    Groesse:   {wert}")

print()
print("="*88)
print("DER VERGLEICH, DER DIE FRAGE BEANTWORTET")
print("="*88)
print(f"  {'':22s} {'je Trade':>10s} {'Trades/Jahr':>12s} {'brutto p.a.':>12s} {'Sharpe':>8s}")
print("  "+"-"*68)
print(f"  {'Dein S/R-Ausbruch':22s} {'+45,7 bp':>10s} {40:>12d} {'+18,3 %':>12s} {0.36:>8.2f}")
print(f"  {'Bot-Orderbuch (MM)':22s} {'+0,87 bp':>10s} {2190:>12d} {'+19,1 %':>12s} {0.85:>8.2f}")
print("""
  -> Die Firma verdient pro Jahr NICHT MEHR als du.
     Ihr Edge je Trade ist 53x KLEINER. Er kommt nur 55x haeufiger.
     Der Unterschied ist der SHARPE -- und der laesst sich hebeln.

     Bei Sharpe 0,36 kannst du 1x fahren.
     Bei Sharpe 3-5 (viele Maerkte kombiniert) faehrt man 10x.
     Aus 19 % werden 190 %. DAS ist "viel Kapital".""")
