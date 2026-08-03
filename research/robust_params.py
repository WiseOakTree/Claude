"""Robuste Parameterwahl: Randverteilung statt Spitzenzelle."""
import numpy as np, pandas as pd
r = pd.read_csv("/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/oc/sweep_results.csv")
ok = r[(r.n_break >= 150) & r.eff_break.notna()]
print(f"Auswertbare Kombinationen: {len(ok)}\n")
print("="*74)
print("Randverteilung: Median-Ausbruchseffekt je Parameterwert")
print("="*74)
for col, nm in (("width","Pivot-Weite"),("tol","Toleranz x ATR"),
                ("age","Level-Alter"),("touch","Mind.-Beruehrungen")):
    print(f"\n  {nm}")
    print(f"  {'Wert':>8s} {'Median bp':>11s} {'Anteil>0':>10s} {'n Kombis':>10s}")
    print("  " + "-"*41)
    for v in sorted(ok[col].unique()):
        g = ok[ok[col]==v]
        print(f"  {v:8} {g.eff_break.median():+10.2f} {(g.eff_break>0).mean()*100:9.0f}% {len(g):10d}")

print("\n" + "="*74)
print("Kandidat aus den Randbesten -- und der bisherige Standard")
print("="*74)
best = {}
for col in ("width","tol","age","touch"):
    med = ok.groupby(col).eff_break.median()
    best[col] = med.idxmax()
print(f"  Randbeste Kombination: Weite {best['width']}, Toleranz {best['tol']}, "
      f"Alter {best['age']}, >={best['touch']} Beruehrungen")
sel = r[(r.width==best['width'])&(r.tol==best['tol'])&(r.age==best['age'])&(r.touch==best['touch'])]
if len(sel):
    print(sel[["n_break","eff_break","p_break","n_bounce","eff_bounce"]]
          .to_string(index=False, float_format=lambda v:f"{v:.2f}"))
print(f"\n  Bisheriger Standard (8 / 0,5 / 1000 / >=6):")
old = r[(r.width==8)&(r.tol==0.5)&(r.age==1000)&(r.touch==6)]
print(old[["n_break","eff_break","p_break","n_bounce","eff_bounce"]]
      .to_string(index=False, float_format=lambda v:f"{v:.2f}"))

print("\n" + "="*74)
print("Kompromiss: genug Ereignisse UND hoher Effekt")
print("="*74)
cand = ok[(ok.n_break >= 400)].nlargest(6, "eff_break")
print(cand[["width","tol","age","touch","n_break","eff_break","p_break","eff_bounce"]]
      .to_string(index=False, float_format=lambda v:f"{v:.2f}"))
