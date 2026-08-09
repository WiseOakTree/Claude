"""Plausibilitaetsprobe der Liquiditaetskarte + Mechanismus-Test."""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import levels, liquidity

O="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/of/"
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
tab=pd.read_csv(O+"liqmap_search.csv.gz")
lm=liquidity.LiquidityMap(tab, window_days=7)
print(f"Karte: {tab['day'].nunique()} Tage, {len(tab):,} Rasterpunkte\n")

print("="*76)
print("1) Plausibilitaetsprobe: runde Preise sollten mehr Tiefe tragen")
print("="*76)
when = pd.Timestamp("2024-06-15", tz="UTC")
prof = lm.profile(when)
prof = prof[(prof.index > 55000) & (prof.index < 80000)]
if len(prof):
    print(f"  Profil am {when.date()}: {len(prof)} Preispunkte, "
          f"{prof.index.min():.0f} .. {prof.index.max():.0f} $")
    # runde Tausender gegen den Rest
    round_mask = np.array([abs(p % 1000) < 60 or abs(p % 1000) > 940 for p in prof.index])
    if round_mask.sum() > 3:
        rm, om = prof[round_mask].median(), prof[~round_mask].median()
        print(f"  Median-Tiefe an runden Tausendern: {rm/1e6:8.1f} Mio $")
        print(f"  Median-Tiefe sonst:                {om/1e6:8.1f} Mio $")
        print(f"  Verhaeltnis: {rm/om:.2f}x" + ("  (plausibel)" if rm/om > 1.0 else "  (kein Effekt)"))
    print(f"  Gesamttiefe im Fenster: {prof.sum()/1e9:.2f} Mrd $")

print("\n"+"="*76)
print("2) MECHANISMUS: verbrauchen Beruehrungen die Liquiditaet?")
print("="*76)
print("  These aus dem Suchlauf: Ein oft getestetes Level ist duenn geworden.")
print("  Dann muss die Buchtiefe MIT der Beruehrungszahl SINKEN.\n")
full=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
df=full[(full.index>=pd.Timestamp("2023-01-08",tz="UTC")) &
        (full.index< pd.Timestamp("2025-01-01",tz="UTC"))].copy()
by=levels.build_levels(df, width=8, tol_atr=0.5, max_age=1000)
idx=df.index
px=df["close"].to_numpy()

# je Level EIN Datenpunkt: Tiefe relativ zur Tiefe am aktuellen Kurs
rows=[]
step=24*7   # woechentlich abtasten, sonst zaehlt dasselbe Level hundertfach
for t in range(0, len(df), step):
    when=idx[t]
    ref = lm.at(px[t], when, width_pct=0.3)
    if not np.isfinite(ref) or ref<=0: continue
    for (price, kind, touches, _) in by.get(t, ()):
        if abs(price/px[t]-1) > 0.05: continue    # nur Level im Buchbereich +/-5 %
        d = lm.at(price, when, width_pct=0.3)
        if np.isfinite(d) and d>0:
            rows.append((touches, d/ref, abs(price/px[t]-1)*100))
L=pd.DataFrame(rows, columns=["touches","rel_depth","dist_pct"])
print(f"  Beobachtungen: {len(L):,}")
print(f"\n  {'Beruehrungen':>13s} {'n':>7s} {'rel. Tiefe':>12s} {'Median-Abstand':>15s}")
print("  "+"-"*50)
for tc in range(1, 9):
    g = L[L.touches==tc] if tc<8 else L[L.touches>=8]
    if len(g)<20: continue
    lbl = f"{tc}" if tc<8 else ">=8"
    print(f"  {lbl:>13s} {len(g):7d} {g.rel_depth.median():11.3f} {g.dist_pct.median():14.2f} %")
if len(L)>100:
    ic,p = stats.spearmanr(L.touches, L.rel_depth)
    print(f"\n  Korrelation Beruehrungen / Tiefe: {ic:+.3f}  (p={p:.4f})")
    print("  " + ("-> Tiefe SINKT mit Beruehrungen: Mechanismus bestaetigt"
                  if ic < 0 and p < 0.05 else
                  "-> kein Zusammenhang messbar: Mechanismus NICHT bestaetigt"))
    # Abstand als Stoergroesse herausrechnen
    lo = L[L.dist_pct < L.dist_pct.median()]
    hi = L[L.dist_pct >= L.dist_pct.median()]
    for nm,g in (("nah am Kurs",lo),("weiter weg",hi)):
        i2,p2 = stats.spearmanr(g.touches, g.rel_depth)
        print(f"     davon {nm:12s}: {i2:+.3f} (p={p2:.4f})")
