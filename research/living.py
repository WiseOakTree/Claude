"""Traden als Beruf: welches Kapital, welche Ueberlebensrate?

Basis ist der EINZIGE in dieser Untersuchung nachgewiesene Edge:
Volatilitaetspraemie, Sharpe 1,33.
"""
import numpy as np
RNG = np.random.default_rng(3)

SHARPE, VOL = 1.33, 0.16
ann_ret = SHARPE * VOL                      # 21,3 % p.a. brutto

print("="*78)
print("A) Eigenes Kapital: was traegt welches Einkommen?")
print("="*78)
print(f"  Annahme: Sharpe {SHARPE}, Volatilitaet {VOL*100:.0f} % -> {ann_ret*100:.1f} % p.a.")
print(f"  (Das ist der beste hier nachgewiesene Edge -- Hedgefonds-Niveau.)\n")
print(f"{'Monatliches Netto-Ziel':>24s} {'noetiges Kapital':>18s} {'realistisch mit Puffer':>24s}")
print("-"*70)
for m in (1000, 2000, 3000, 5000):
    jahr = m*12
    kap = jahr/ann_ret
    # Puffer: man kann nicht 100 % des Erwartungswerts entnehmen, sonst ruiniert
    # der erste schlechte Jahrgang das Konto. Faustregel: halbe Entnahmequote.
    print(f"{m:>21,d} € {kap:>16,.0f} € {kap*2:>22,.0f} €")

print("\n"+"="*78)
print("B) Der Prop-Weg: ueberlebt ein gefundetes Konto ueberhaupt ein Jahr?")
print("="*78)
print("  Kraken Prop: 6 % Max Drawdown gilt WEITER, auch nach dem Bestehen.\n")
DAYS, SIMS = 252, 40_000
print(f"{'Volatilitaet':>13s} {'Rendite p.a.':>13s} {'ueberlebt 1 Jahr':>18s} {'erwartete Lebensdauer':>23s}")
print("-"*72)
for vol in (0.08, 0.10, 0.16, 0.20, 0.30):
    mu = SHARPE*vol/365; sd = vol/np.sqrt(365)
    r = RNG.normal(mu, sd, size=(SIMS, DAYS))
    eq = np.cumprod(1+r, axis=1)
    dd = eq/np.maximum.accumulate(eq, axis=1) - 1
    busted = (dd <= -0.06)
    surv = 1 - busted.any(axis=1).mean()
    # erwartete Lebensdauer in Handelstagen
    first = np.where(busted.any(axis=1), busted.argmax(axis=1), DAYS)
    print(f"{vol*100:12.0f}% {SHARPE*vol*100:12.1f}% {surv*100:17.1f}% "
          f"{np.mean(first):18.0f} Tage")

print("\n"+"="*78)
print("C) Was das fuer 'Traden als Beruf ueber Prop' bedeutet")
print("="*78)
vol = 0.10
mu = SHARPE*vol/365; sd = vol/np.sqrt(365)
r = RNG.normal(mu, sd, size=(SIMS, DAYS))
eq = np.cumprod(1+r, axis=1)
dd = eq/np.maximum.accumulate(eq, axis=1)-1
surv = 1-(dd <= -0.06).any(axis=1).mean()
konto = 10_000
brutto = konto*SHARPE*vol
netto = brutto*0.90
print(f"  Konto 10.000 $, Volatilitaet {vol*100:.0f} % (defensiv gewaehlt fuer Ueberleben)")
print(f"  Bruttoertrag im Jahr:        {brutto:8,.0f} $")
print(f"  nach 90/10-Split:            {netto:8,.0f} $")
print(f"  Ueberlebensrate 1 Jahr:      {surv*100:8.1f} %")
print(f"  erwarteter Jahresertrag:     {netto*surv:8,.0f} $  (Ueberleben eingerechnet)")
print(f"\n  Fuer 3.000 €/Monat = 36.000 €/Jahr braeuchte man rund "
      f"{36000/max(netto*surv,1):.0f} solcher Konten gleichzeitig.")
print(f"  Gebuehren, um sie zu erlangen (4,2 Versuche x 85 $ je Konto): "
      f"{36000/max(netto*surv,1)*4.2*85:,.0f} $")
