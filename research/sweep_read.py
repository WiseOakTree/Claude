import numpy as np, pandas as pd
r = pd.read_csv("/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/oc/sweep_results.csv")
ok = r[(r.n_bounce>=200) & r.eff_bounce.notna()]

print("="*80)
print("1) Die signifikanten Bounce-Ergebnisse -- in welche RICHTUNG?")
print("="*80)
sig = ok[ok.p_bounce < 0.05]
print(f"  signifikant gesamt: {len(sig)}")
print(f"    davon NEGATIV (Bounce verliert):  {(sig.eff_bounce<0).sum()}")
print(f"    davon positiv  (Bounce gewinnt):  {(sig.eff_bounce>0).sum()}")
print(f"  Bonferroni-Schwelle bei {len(ok)} Tests: {0.05/len(ok):.5f}")
print(f"    Bounce ueberlebt Bonferroni: {(sig.p_bounce < 0.05/len(ok)).sum()}")
sigb = ok[ok.p_break < 0.05]
print(f"    Ausbruch ueberlebt Bonferroni: {(sigb.p_break < 0.05/len(ok)).sum()}")

print("\n"+"="*80)
print("2) Die Symmetrie: derselbe Zaehler treibt beides in Gegenrichtungen")
print("="*80)
print(f"{'Ber.':>5s} {'Bounce bp':>11s} {'Ausbruch bp':>13s} {'Summe':>9s}")
print("-"*42)
for mt in sorted(r.touch.unique()):
    g=r[r.touch==mt]
    b,k = g.eff_bounce.median(), g.eff_break.median()
    print(f"{mt:5d} {b:+10.2f} {k:+12.2f} {b+k:+8.2f}")
cc = np.corrcoef(ok.eff_bounce, ok.eff_break)[0,1]
print(f"\n  Korrelation Bounce-Effekt / Ausbruch-Effekt: {cc:+.3f}")

print("\n"+"="*80)
print("3) Wo die positiven Bounce-Werte herkommen")
print("="*80)
pos = ok[ok.eff_bounce > 0]
print(f"  {len(pos)} positive von {len(ok)}")
print(f"  Pivot-Weite der positiven: {sorted(pos.width.unique())}")
print(f"{'Weite':>7s} {'Anteil positiv':>16s} {'Median bp':>11s}")
print("-"*36)
for w in sorted(ok.width.unique()):
    g=ok[ok.width==w]
    print(f"{w:7d} {(g.eff_bounce>0).mean()*100:15.1f}% {g.eff_bounce.median():+10.2f}")

print("\n"+"="*80)
print("4) Bester Ausbruch-Parametersatz nach Robustheit statt Spitzenwert")
print("="*80)
b = r[(r.n_break>=250) & (r.p_break<0.05)].copy()
b["score"] = b.eff_break / b.p_break.clip(lower=1e-6)**0
print(b.nlargest(8,"eff_break")[["width","tol","age","touch","n_break","eff_break","p_break"]]
      .to_string(index=False, float_format=lambda v: f"{v:.3f}"))
print(f"\n  Alter Standard (8 / 0,5 / 1000 / >=6):")
old = r[(r.width==8)&(r.tol==0.5)&(r.age==1000)&(r.touch==6)]
print(old[["n_break","eff_break","p_break","n_bounce","eff_bounce","p_bounce"]]
      .to_string(index=False, float_format=lambda v: f"{v:.3f}"))
