"""Support/Resistance-Ausbruch: zaehlt die Zahl der Beruehrungen?

Anders als Donchian (rollierendes Hoch) entsteht eine S/R-Zone durch
MEHRFACHES Antesten. These: mehr Beruehrungen = bedeutsamerer Bruch.

Look-ahead-Sorgfalt: Ein Pivot bei Bar i ist erst bei i+w bestaetigt.
Level werden nur aus Pivots gebaut, die zum Zeitpunkt t schon bekannt sind.
"""
import numpy as np, pandas as pd
from scipy import stats

V = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
df = pd.read_csv(V+"btc_1h.csv", index_col=0, parse_dates=True)
o,h,l,c = (df[x].to_numpy() for x in ("open","high","low","close")); n=len(df)
atr = pd.Series(np.maximum.reduce([h-l, abs(h-np.roll(c,1)), abs(l-np.roll(c,1))])
                ).ewm(alpha=1/14, adjust=False).mean().to_numpy()
COST_BP = 16.0

def pivots(w=8):
    """(bestaetigt_ab, preis, art) -- Pivot bei i ist erst ab i+w bekannt."""
    out=[]
    for i in range(w, n-w):
        seg_h, seg_l = h[i-w:i+w+1], l[i-w:i+w+1]
        if h[i] == seg_h.max(): out.append((i+w, h[i], "R"))
        if l[i] == seg_l.min(): out.append((i+w, l[i], "S"))
    return sorted(out)

def build_levels(pv, tol_atr=0.5, max_age=1000):
    """Fuer jeden Bar: aktive Level mit Beruehrungszahl, nur aus bekannten Pivots."""
    levels = []           # [preis, art, beruehrungen, letzter_bar]
    by_bar = {}
    pi = 0
    for t in range(n):
        while pi < len(pv) and pv[pi][0] <= t:
            _, price, kind = pv[pi]; pi += 1
            tol = tol_atr * atr[min(t, n-1)]
            hit = None
            for L in levels:
                if L[1] == kind and abs(L[0]-price) <= tol: hit = L; break
            if hit:
                hit[0] = (hit[0]*hit[2] + price)/(hit[2]+1)   # Mittel nachfuehren
                hit[2] += 1; hit[3] = t
            else:
                levels.append([price, kind, 1, t])
        levels = [L for L in levels if t - L[3] <= max_age]
        by_bar[t] = [tuple(L) for L in levels]
    return by_bar

def breakouts(by_bar, min_touch):
    """Ausbruch: Schluss kreuzt ein Level mit >= min_touch Beruehrungen."""
    ev=[]
    for t in range(1, n):
        for (price, kind, touches, last) in by_bar.get(t-1, []):
            if touches < min_touch: continue
            if kind=="R" and c[t-1] <= price < c[t]: ev.append((t, +1, touches))
            elif kind=="S" and c[t-1] >= price > c[t]: ev.append((t, -1, touches))
    return ev

print("Pivots und Level werden aufgebaut ...", flush=True)
pv = pivots(8)
by_bar = build_levels(pv)
print(f"  {len(pv)} Pivots, im Mittel {np.mean([len(v) for v in by_bar.values()]):.1f} aktive Level je Bar\n")

print("="*78)
print("Zahlt sich die Zahl der Beruehrungen aus?")
print("="*78)
print(f"{'min. Beruehrungen':>18s} {'Ereignisse':>11s} {'6h':>10s} {'24h':>10s} {'72h':>10s} {'p (24h)':>9s}")
print("-"*78)
for mt in (1,2,3,4,5):
    ev = breakouts(by_bar, mt)
    if len(ev) < 30: continue
    row=[]
    for hz in (6,24,72):
        r = np.array([(c[t+hz]/c[t]-1)*d for (t,d,_) in ev if t+hz<n])*1e4
        row.append(r.mean() if len(r) else np.nan)
    r24 = np.array([(c[t+24]/c[t]-1)*d for (t,d,_) in ev if t+24<n])*1e4
    _,p = stats.ttest_1samp(r24, 0)
    print(f"{mt:18d} {len(ev):11d} {row[0]:+9.2f} {row[1]:+9.2f} {row[2]:+9.2f} {p:9.3f}")

print("\n"+"="*78)
print("KONTROLLE: Ausbruch ueber ein ZUFAELLIGES Level")
print("="*78)
print("  Gleiche Anzahl Ereignisse, gleiche Mechanik -- nur ist das Level")
print("  zufaellig gesetzt statt aus Pivots gebaut.")
rng = np.random.default_rng(9)
ev2 = breakouts(by_bar, 2)
fake=[]
for (t,d,_) in ev2:
    tt = rng.integers(50, n-200)
    fake.append((int(tt), 1 if rng.random()<.5 else -1, 0))
print(f"\n{'Gruppe':>18s} {'Ereignisse':>11s} {'6h':>10s} {'24h':>10s} {'72h':>10s}")
print("-"*66)
for nm, e in (("S/R (>=2 Ber.)", ev2), ("Zufall", fake)):
    row=[]
    for hz in (6,24,72):
        r = np.array([(c[t+hz]/c[t]-1)*d for (t,d,_) in e if t+hz<n])*1e4
        row.append(r.mean() if len(r) else np.nan)
    print(f"{nm:>18s} {len(e):11d} {row[0]:+9.2f} {row[1]:+9.2f} {row[2]:+9.2f}")
for hz in (6,24,72):
    a = np.array([(c[t+hz]/c[t]-1)*d for (t,d,_) in ev2 if t+hz<n])*1e4
    b = np.array([(c[t+hz]/c[t]-1)*d for (t,d,_) in fake if t+hz<n])*1e4
    _,p = stats.ttest_ind(a,b,equal_var=False)
    print(f"  Differenz {hz:3d}h: {a.mean()-b.mean():+7.2f} bp   p = {p:.3f}")

print("\n"+"="*78)
print("Gegen die Challenge-Regeln")
print("="*78)
COST=16e-4
ret = pd.Series(c, index=df.index).pct_change().fillna(0)
def challenge(r):
    d=(1+r.dropna()).resample("1D").prod()-1; a=d.dropna().to_numpy()
    passed=tot=0; R=[];DD=[]
    for s in range(0,len(a)-90):
        w=a[s:s+90]; eq=np.cumprod(1+w); dd=(eq/np.maximum.accumulate(eq)-1).min()
        passed += (eq[-1]-1>=.10 and dd>=-.06 and w.min()>-.03); tot+=1
        R.append(eq[-1]-1); DD.append(-dd)
    return (passed/tot*100, np.median(R)*100, np.median(DD)*100) if tot else (0,0,0)
print(f"{'Variante':38s} {'Trades':>7s} {'Rendite':>9s} {'DD':>7s} {'Pass':>7s}")
print("-"*72)
for mt in (2,3,4):
    for hold in (24,72,168):
        ev = breakouts(by_bar, mt)
        pos=np.zeros(n)
        for (t,d,_) in ev: pos[t:min(t+hold,n)] += d
        w = pd.Series(np.clip(pos,-1,1), index=df.index)
        r = w.shift(1)*ret - COST*w.shift(1).diff().abs().fillna(0)
        p,m,dd = challenge(r)
        print(f"{f'>={mt} Beruehrungen, {hold}h halten':38s} {len(ev):7d} "
              f"{m:+8.1f}% {dd:6.1f}% {p:6.1f}%")
