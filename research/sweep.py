"""Parametersuche fuer S/R-Level -- Bounce UND Ausbruch je Kombination.

WICHTIG: laeuft ausschliesslich auf dem Suchzeitraum. Der Holdout
(2025-01 .. 2026-06) wird hier nicht angefasst.
"""
import sys, itertools, warnings
sys.path.insert(0, "/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
full = pd.read_csv(V+"btc_1h.csv", index_col=0, parse_dates=True)
SEARCH_END = pd.Timestamp("2025-01-01", tz="UTC")
df = full[full.index < SEARCH_END].copy()
c = df["close"].to_numpy(); n = len(df)
print(f"Suchzeitraum: {df.index.min().date()} .. {df.index.max().date()}  ({n} Bars)")
print(f"Holdout ab {SEARCH_END.date()} -- unangetastet ({(full.index>=SEARCH_END).sum()} Bars)\n")

def block_p(ev, hz):
    """Effekt + ueberlappungskorrigiertes p (ein Ereignis je Horizontblock)."""
    if not ev: return 0, np.nan, np.nan
    seen = {}
    for (t, d, _, _) in ev:
        b = t // hz
        if b not in seen and t + hz < n:
            seen[b] = (c[t+hz]/c[t]-1) * d
    a = np.array(list(seen.values())) * 1e4
    if len(a) < 20: return len(a), np.nan, np.nan
    _, p = stats.ttest_1samp(a, 0)
    return len(a), a.mean(), p

WIDTHS  = (4, 6, 8, 12, 16)
TOLS    = (0.25, 0.5, 0.75, 1.0)
AGES    = (500, 1000, 2000)
TOUCHES = (2, 3, 4, 5, 6, 7, 8)
HZ = 24

rows = []
total = len(WIDTHS)*len(TOLS)*len(AGES)
done = 0
for w, tol, age in itertools.product(WIDTHS, TOLS, AGES):
    by = levels.build_levels(df, width=w, tol_atr=tol, max_age=age)
    for mt in TOUCHES:
        bo = levels.breakout_events(by, df, min_touch=mt)
        bn = levels.bounce_events(by, df, min_touch=mt, zone_atr=0.25)
        nbo, ebo, pbo = block_p(bo, HZ)
        nbn, ebn, pbn = block_p(bn, HZ)
        rows.append(dict(width=w, tol=tol, age=age, touch=mt,
                         n_break=len(bo), eff_break=ebo, p_break=pbo,
                         n_bounce=len(bn), eff_bounce=ebn, p_bounce=pbn))
    done += 1
    if done % 15 == 0: print(f"  {done}/{total} Level-Konfigurationen", flush=True)

r = pd.DataFrame(rows)
r.to_csv("/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/oc/sweep_results.csv", index=False)
print(f"\nKombinationen: {len(r)}\n")

print("="*88)
print("Traegt der BOUNCE? (nur Kombinationen mit >= 50 unabh. Beobachtungen)")
print("="*88)
ok = r[(r.n_bounce >= 200) & r.eff_bounce.notna()]
print(f"  auswertbar: {len(ok)} von {len(r)}")
print(f"  Median-Effekt Bounce:   {ok.eff_bounce.median():+7.2f} bp")
print(f"  Median-Effekt Ausbruch: {ok.eff_break.median():+7.2f} bp")
print(f"  Anteil Bounce positiv:   {(ok.eff_bounce>0).mean()*100:5.1f} %")
print(f"  Anteil Ausbruch positiv: {(ok.eff_break>0).mean()*100:5.1f} %")
print(f"  p<0,05 Bounce:   {(ok.p_bounce<0.05).sum()} von {len(ok)}  (zufaellig erwartet: {len(ok)*0.05:.0f})")
print(f"  p<0,05 Ausbruch: {(ok.p_break<0.05).sum()} von {len(ok)}")

print("\n" + "="*88)
print("Dosis-Wirkung nach Beruehrungszahl (Mittel ueber alle Level-Konfigurationen)")
print("="*88)
print(f"{'Ber.':>5s} {'Bounce n':>10s} {'Bounce bp':>11s} {'Ausbruch n':>11s} {'Ausbruch bp':>12s}")
print("-"*54)
for mt in TOUCHES:
    g = r[r.touch == mt]
    print(f"{mt:5d} {g.n_bounce.median():10.0f} {g.eff_bounce.median():+10.2f} "
          f"{g.n_break.median():11.0f} {g.eff_break.median():+11.2f}")

print("\n" + "="*88)
print("Beste 10 nach Ausbruch-Effekt (mit ausreichend Ereignissen)")
print("="*88)
b = r[(r.n_break >= 150) & r.eff_break.notna()].nlargest(10, "eff_break")
print(b[["width","tol","age","touch","n_break","eff_break","p_break"]].to_string(index=False,
      float_format=lambda v: f"{v:.3f}"))

print("\n" + "="*88)
print("Beste 10 nach Bounce-Effekt")
print("="*88)
b2 = r[(r.n_bounce >= 150) & r.eff_bounce.notna()].nlargest(10, "eff_bounce")
print(b2[["width","tol","age","touch","n_bounce","eff_bounce","p_bounce"]].to_string(index=False,
      float_format=lambda v: f"{v:.3f}"))
