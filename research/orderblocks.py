"""Order Blocks getestet -- exakt die Logik des Pine-Indikators.

Bullish OB = die letzte Abwaerts-Kerze vor N aufeinanderfolgenden Aufwaerts-
Kerzen. These: Preis kehrt zu diesem Level zurueck und reagiert dort.

Entscheidend ist die KONTROLLGRUPPE: Der Kurs kehrt staendig zu irgendwelchen
Levels zurueck. Die Frage ist, ob OB-Level etwas Besonderes sind.
"""
import numpy as np, pandas as pd
from scipy import stats

V = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
df = pd.read_csv(V+"btc_1h.csv", index_col=0, parse_dates=True)
o,h,l,c = (df[x].to_numpy() for x in ("open","high","low","close"))
n = len(df)
COST_BP = 16.0

def find_obs(periods=5, threshold=0.0, usewicks=False):
    """Signal bei Bar i, Level stammt von Bar i-ob_period. Nur Vergangenheit."""
    ob = periods + 1
    out = []
    for i in range(ob+1, n):
        move = abs(c[i-ob] - c[i-1]) / c[i-ob] * 100
        if move < threshold: continue
        up = sum(1 for k in range(1, periods+1) if c[i-k] > o[i-k])
        dn = sum(1 for k in range(1, periods+1) if c[i-k] < o[i-k])
        if c[i-ob] < o[i-ob] and up == periods:
            hi = h[i-ob] if usewicks else o[i-ob]
            out.append((i, "bull", l[i-ob], hi))
        elif c[i-ob] > o[i-ob] and dn == periods:
            lo = l[i-ob] if usewicks else o[i-ob]
            out.append((i, "bear", lo, h[i-ob]))
    return out

def first_touch(obs, max_wait=500):
    """Erster Ruecklauf in die Zone NACH der Erkennung."""
    ev = []
    for (i, side, zlo, zhi) in obs:
        for j in range(i+1, min(i+max_wait, n)):
            if l[j] <= zhi and h[j] >= zlo:            # Zone beruehrt
                ev.append((j, side, (zlo+zhi)/2))
                break
    return ev

def measure(events, label, horizons=(6,24,72)):
    rows=[]
    for hz in horizons:
        rets=[]
        for (j, side, lvl) in events:
            if j+hz >= n: continue
            r = (c[j+hz]/c[j]-1) * (1 if side=="bull" else -1)   # in Richtung der These
            rets.append(r)
        if len(rets) < 30: continue
        a = np.array(rets)*1e4
        t,p = stats.ttest_1samp(a, 0)
        rows.append((hz, len(a), a.mean(), p))
    print(f"\n  {label}  ({len(events)} Ereignisse)")
    print(f"  {'Horizont':>9s} {'n':>6s} {'Ø Reaktion':>12s} {'p':>8s} {'vs 16bp':>9s}")
    for hz,cnt,m,p in rows:
        print(f"  {hz:7d} h {cnt:6d} {m:+10.2f} bp {p:8.3f} {abs(m)/COST_BP:8.2f}x")
    return rows

print("="*76)
print("Order Blocks -- Reaktion beim Ruecklauf in die Zone")
print("="*76)
for per, thr in ((5,0.0),(5,1.0),(3,0.0),(8,0.0)):
    obs = find_obs(periods=per, threshold=thr)
    ev = first_touch(obs)
    measure(ev, f"periods={per}, threshold={thr} %")

print("\n"+"="*76)
print("KONTROLLGRUPPE: zufaellige Level statt Order Blocks")
print("="*76)
print("  Gleiche Anzahl, gleiche Zonenbreite, gleicher Zeitraum -- nur der")
print("  Ort ist zufaellig. Wenn OBs wirken, muessen sie hier deutlich besser sein.")
rng = np.random.default_rng(5)
obs = find_obs(periods=5, threshold=0.0)
widths = [(zhi-zlo) for (_,_,zlo,zhi) in obs]
fake=[]
for (i, side, zlo, zhi) in obs:
    ref = c[i-6]
    shift = rng.normal(0, 0.01)*ref          # Level zufaellig um ~1 % verschoben
    w = zhi-zlo
    mid = (zlo+zhi)/2 + shift
    fake.append((i, side, mid-w/2, mid+w/2))
measure(first_touch(fake), "Zufallslevel (Kontrolle)")

print("\n"+"="*76)
print("KONTROLLE 2: beliebige Kerze statt Order-Block-Kerze")
print("="*76)
idx = rng.choice(np.arange(20, n-600), size=len(obs), replace=False)
plain=[]
for i in idx:
    side = "bull" if rng.random()<0.5 else "bear"
    plain.append((int(i), side, l[i], h[i]))
measure(first_touch(plain), "beliebige Kerze (Kontrolle)")
