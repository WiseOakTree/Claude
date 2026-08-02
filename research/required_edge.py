"""Umkehrung der Frage: Welchen Edge verlangt die Challenge eigentlich?

Statt Strategien zu suchen und zu scheitern: simuliere Strategien mit
VORGEGEBENEM Sharpe und miss die Pass-Rate. Das gibt die Anforderung als Zahl.
"""
import numpy as np

RNG = np.random.default_rng(7)
DAYS, SIMS = 90, 40_000

def pass_rate(sharpe, ann_vol, target=0.10, max_dd=0.06, daily_lim=0.03):
    """Anteil der 90-Tage-Laeufe, die alle drei Challenge-Regeln erfuellen."""
    mu_d = sharpe * ann_vol / 365          # taegliche Drift
    sd_d = ann_vol / np.sqrt(365)
    r = RNG.normal(mu_d, sd_d, size=(SIMS, DAYS))
    eq = np.cumprod(1 + r, axis=1)
    peak = np.maximum.accumulate(eq, axis=1)
    dd = (eq / peak - 1).min(axis=1)
    ok = (eq[:, -1] - 1 >= target) & (dd >= -max_dd) & (r.min(axis=1) > -daily_lim)
    return ok.mean() * 100

print("="*78)
print("Pass-Rate je 90-Tage-Versuch, nach Sharpe und Volatilitaet")
print("(+10 % Ziel, 6 % max. Drawdown, 3 % Tagesverlust)")
print("="*78)
vols = [0.10, 0.15, 0.20, 0.30, 0.50]
print(f"{'Sharpe':>7s} |" + "".join(f"{v*100:7.0f}%" for v in vols) + "   <- Jahresvolatilitaet")
print("-"*78)
for s in (0.0, 0.5, 1.0, 1.33, 2.0, 3.0, 5.0, 8.0):
    row = "".join(f"{pass_rate(s, v):7.1f}" for v in vols)
    tag = "  <- Vol-Praemie (gefunden)" if s == 1.33 else ""
    print(f"{s:7.2f} |{row}{tag}")

print("\n" + "="*78)
print("Bester Fall je Sharpe (optimal gewaehlte Volatilitaet)")
print("="*78)
fine = np.arange(0.06, 0.61, 0.01)
print(f"{'Sharpe':>7s} {'beste Vola':>11s} {'Pass-Rate':>11s} {'Versuche bis Erfolg':>21s} {'Kosten (85 $)':>14s}")
print("-"*78)
for s in (0.5, 1.0, 1.33, 2.0, 3.0, 5.0, 8.0):
    rates = [(pass_rate(s, v), v) for v in fine]
    best, bv = max(rates)
    n = 1/(best/100) if best > 0 else float("inf")
    print(f"{s:7.2f} {bv*100:10.0f}% {best:10.1f}% {n:20.1f} {n*85:13.0f} $")

print("\n" + "="*78)
print("Die Umkehrung: welcher Sharpe fuer welche Erfolgsquote?")
print("="*78)
for goal in (25, 50, 75, 90):
    lo, hi = 0.0, 30.0
    for _ in range(40):
        mid = (lo+hi)/2
        best = max(pass_rate(mid, v) for v in np.arange(0.08, 0.61, 0.02))
        if best < goal: lo = mid
        else: hi = mid
    print(f"  fuer {goal:2d} % Erfolgsquote je Versuch:  Sharpe {(lo+hi)/2:5.2f}")

print("\n" + "="*78)
print("Zum Vergleich: real dokumentierte Sharpe-Ratios")
print("="*78)
for nm, s in (("S&P 500, langfristig", 0.4), ("guter Hedgefonds", 1.0),
              ("Volatilitaetspraemie (hier gemessen)", 1.33),
              ("sehr guter systematischer Fonds", 2.0),
              ("Renaissance Medallion (geschaetzt)", 3.0)):
    best = max(pass_rate(s, v) for v in np.arange(0.08, 0.61, 0.02))
    print(f"  {nm:38s} Sharpe {s:4.2f} -> Pass-Rate {best:5.1f} %")
