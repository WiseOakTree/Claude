"""Haerteprüfung von MVRV -- Richtung, Bonferroni, Out-of-Sample, Zyklenzahl."""
import numpy as np, pandas as pd
from scipy import stats

OUT = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/oc/"
df = pd.read_csv(OUT + "onchain_feat.csv", index_col=0, parse_dates=True)
def cp(ic, n):
    t = ic*np.sqrt(max(n-2,1)/max(1-ic**2,1e-9)); return 2*(1-stats.t.cdf(abs(t), max(n-2,1)))

print("="*80); print("1) Richtung: wie wirkt MVRV wirklich?"); print("="*80)
H = 90
fwd = df["px"].pct_change(H).shift(-H)
s = pd.concat([df["mvrv_z"].rename("z"), df["mvrv"].rename("lvl"), fwd.rename("f")],
              axis=1).replace([np.inf,-np.inf],np.nan).dropna()
ic,_ = stats.spearmanr(s["z"], s["f"])
print(f"  IC(MVRV z-Score, 90T-Folgerendite) = {ic:+.3f}")
print(f"  -> {'HOHES MVRV sagt HOHE Folgerenditen voraus (Momentum)' if ic>0 else 'Kontraindikator'}")
print("\n  Quintile des MVRV z-Score (90-Tage-Folgerendite, Median):")
s["q"] = pd.qcut(s["z"], 5, labels=False, duplicates="drop")
for q in range(5):
    lbl = ["sehr guenstig","guenstig","neutral","teuer","sehr teuer"][q]
    g = s[s["q"]==q]
    print(f"    Q{q+1} ({lbl:13s}) Median {g['f'].median()*100:+7.1f} %   "
          f"Mittel {g['f'].mean()*100:+7.1f} %   n={len(g)}")
print("\n  Klassische Lesart waere fallend (guenstig -> hohe Rendite). "
      f"Tatsaechlich: {'steigend' if s[s.q==4]['f'].median()>s[s.q==0]['f'].median() else 'fallend'}.")

print("\n"+"="*80); print("2) Multiples Testen: 28 Kombinationen gerechnet"); print("="*80)
print(f"  Bonferroni-Schwelle: 0,05 / 28 = {0.05/28:.4f}")
print(f"  MVRV z, 30 T: p = 0,037   -> {'ueberlebt' if 0.037<0.05/28 else 'faellt'}")
print(f"  MVRV z, 90 T: p = 0,048   -> {'ueberlebt' if 0.048<0.05/28 else 'faellt'}")
print("  Bei 28 Tests sind 1,4 Zufallstreffer auf dem 5-%-Niveau zu erwarten. Gefunden: 2.")

print("\n"+"="*80); print("3) Out-of-Sample: erste vs. zweite Haelfte"); print("="*80)
h = len(s)//2
for nm, part in (("1. Haelfte", s.iloc[:h]), ("2. Haelfte", s.iloc[h:])):
    i2,_ = stats.spearmanr(part["z"], part["f"]); ne = len(part)/H
    print(f"  {nm} ({part.index.min().date()}..{part.index.max().date()}): "
          f"IC {i2:+.3f}   p korr. {cp(i2, ne):.3f}   n_eff {ne:.0f}")

print("\n"+"="*80); print("4) Das strukturelle Problem: wie viele Zyklen stecken drin?"); print("="*80)
pk = df["px"].rolling(365, center=True).max()
tops = df.index[(df["px"] >= pk*0.999) & df["px"].notna()]
yrs = sorted(set(t.year for t in tops))
print(f"  Preisgipfel in den Jahren: {yrs}")
print(f"  Datenlaenge: {len(df)/365:.1f} Jahre  ->  etwa {len(df)/365/4:.1f} Vierjahreszyklen")
print("  Ein Zyklusindikator laesst sich mit 3-4 Zyklen nicht validieren:")
print("  n_eff auf 365-Tage-Sicht ist 12 -- das ist eine Stichprobe von zwoelf.")

print("\n"+"="*80); print("5) Gegen die Challenge-Regeln (MVRV als Momentum-Filter)"); print("="*80)
COST = 16e-4
ret = df["px"].pct_change().fillna(0)
print(f"{'Variante':36s} {'Rendite':>9s} {'DD':>7s} {'Pass':>7s}")
print("-"*62)
for thr in (-0.5, 0.0, 0.5):
    for lev in (1.0, 2.0):
        w = pd.Series(np.where(df["mvrv_z"].shift(1) > thr, lev, 0.0), index=df.index).fillna(0)
        turn = w.diff().abs().fillna(0)
        r = (w*ret - COST*turn).dropna().to_numpy()
        passed=tot=0; R=[];DD=[]
        for st in range(0, len(r)-90):
            wnd=r[st:st+90]; eq=np.cumprod(1+wnd)
            dd=(eq/np.maximum.accumulate(eq)-1).min()
            passed += (eq[-1]-1>=.10 and dd>=-.06 and wnd.min()>-.03); tot+=1
            R.append(eq[-1]-1); DD.append(-dd)
        print(f"{f'long wenn MVRV z > {thr:+.1f}, {lev:.0f}x':36s} {np.median(R)*100:+8.1f}% "
              f"{np.median(DD)*100:6.1f}% {passed/tot*100:6.1f}%")
r = ret.dropna().to_numpy(); passed=tot=0; R=[];DD=[]
for st in range(0, len(r)-90):
    wnd=r[st:st+90]; eq=np.cumprod(1+wnd); dd=(eq/np.maximum.accumulate(eq)-1).min()
    passed += (eq[-1]-1>=.10 and dd>=-.06 and wnd.min()>-.03); tot+=1
    R.append(eq[-1]-1); DD.append(-dd)
print(f"{'BTC einfach halten (Vergleich)':36s} {np.median(R)*100:+8.1f}% "
      f"{np.median(DD)*100:6.1f}% {passed/tot*100:6.1f}%")
