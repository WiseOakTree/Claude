"""Ist mein Nullmodell zu eng? Der entscheidende Test.

Widerspruch: Der Reality Check gibt p = 0,0170, aber die Regel selbst hat
nur t = 0,93. Wenn die Streuung der Nullverteilung kleiner ist als der
echte Standardfehler, ist der Test zu liberal -- egal wie das Null gebaut ist.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, pickle
CACHE="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/finaltest.pkl"
daten=pickle.load(open(CACHE,"rb")); COST=8e-4; H=48
NM="Keltner-Ausbruch"

def n_eff(st,hold,N):
    conc=np.zeros(N)
    for i in st: conc[i:i+hold]+=1
    u=[]
    for i in st:
        s=conc[i:i+hold]; s=s[s>0]; u.append((1.0/s).mean() if len(s) else 0)
    return max(np.sum(u),2.0)

def kennzahl(shift=None):
    ges=[]
    for sym,d in daten.items():
        s=d["sig"][NM]
        if shift is not None: s=np.roll(s,shift[sym])
        f=d["f"]; m=(s!=0)&np.isfinite(f)
        if m.sum(): ges.append(s[m]*f[m]-2*COST)
    return np.concatenate(ges) if ges else np.array([])

x=kennzahl()
starts=[]; 
for sym,d in daten.items():
    s=d["sig"][NM]; f=d["f"]; m=(s!=0)&np.isfinite(f)
    starts.append((np.where(m)[0],d["n"]))
ne=sum(n_eff(st,H,N) for st,N in starts)
se_naiv=x.std(ddof=1)/np.sqrt(len(x))*1e4
se_korr=x.std(ddof=1)/np.sqrt(ne)*1e4
print("="*80)
print(f"BEOBACHTET: {x.mean()*1e4:+.2f} bp ueber {len(x):,} Trades")
print("="*80)
print(f"  Standardfehler NAIV (n = {len(x):,}):        {se_naiv:.2f} bp  -> t = {x.mean()*1e4/se_naiv:.2f}")
print(f"  Standardfehler KORRIGIERT (n_eff = {ne:,.0f}): {se_korr:.2f} bp  -> t = {x.mean()*1e4/se_korr:.2f}")

rng=np.random.default_rng(7)
werte=[]
for _ in range(600):
    sh={sym:int(rng.integers(500,d["n"]-500)) for sym,d in daten.items()}
    y=kennzahl(sh)
    if len(y): werte.append(y.mean()*1e4)
werte=np.array(werte)
print(f"\n  STREUUNG DER NULLVERTEILUNG (600 Verschiebungen):")
print(f"    Mittel {werte.mean():+.2f} bp   Standardabweichung {werte.std(ddof=1):.2f} bp")
print(f"    2,5.-97,5. Perzentil: {np.percentile(werte,2.5):+.2f} .. {np.percentile(werte,97.5):+.2f} bp")
print(f"\n  VERGLEICH DER STREUUNGEN")
print(f"    Null-Streuung:                {werte.std(ddof=1):>6.2f} bp")
print(f"    echter Standardfehler:        {se_korr:>6.2f} bp")
print(f"    Verhaeltnis:                  {se_korr/werte.std(ddof=1):>6.2f}x")
if se_korr/werte.std(ddof=1) > 1.3:
    print(f"\n  -> DAS NULL IST ZU ENG. Der Reality Check ist zu liberal.")
    print(f"     Der p-Wert von 0,0170 ist nicht belastbar.")
else:
    print(f"\n  -> Das Null bildet die Unsicherheit angemessen ab.")
