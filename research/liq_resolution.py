"""Kann die Karte ueberhaupt levelspezifische Struktur aufloesen?

Wenn die Tiefe fast vollstaendig durch den ABSTAND zum Mittelkurs erklaert
wird, traegt sie keine Information ueber einzelne Preisniveaus -- dann ist der
Mechanismus-Test nicht widerlegend, sondern nur nicht durchfuehrbar.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import liquidity

O="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/of/"
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
lm=liquidity.LiquidityMap(pd.read_csv(O+"liqmap_search.csv.gz"), window_days=7)
df=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
df=df[(df.index>=pd.Timestamp("2023-01-08",tz="UTC"))&(df.index<pd.Timestamp("2025-01-01",tz="UTC"))]
px=df["close"].to_numpy(); idx=df.index

rows=[]
for t in range(0, len(df), 24*7):
    when=idx[t]; base=px[t]
    for off in np.arange(-4.5, 4.6, 0.25):        # Abstand in Prozent
        p = base*(1+off/100)
        d = lm.at(p, when, width_pct=0.3)
        if np.isfinite(d) and d>0: rows.append((when, off, d))
R=pd.DataFrame(rows, columns=["when","off","depth"])
R["rel"]=R.groupby("when").depth.transform(lambda s: s/s.median())
print("="*74)
print("Erklaert der blosse ABSTAND zum Mittelkurs die gemessene Tiefe?")
print("="*74)
print(f"  Messpunkte: {len(R):,} an {R['when'].nunique()} Tagen\n")
prof = R.groupby(R.off.round(2)).rel.median()
print(f"  {'Abstand':>9s} {'rel. Tiefe':>12s}")
print("  "+"-"*23)
for o in (-4.0,-3.0,-2.0,-1.0,-0.5,0.0,0.5,1.0,2.0,3.0,4.0):
    if round(o,2) in prof.index: print(f"  {o:8.1f}% {prof.loc[round(o,2)]:11.3f}")

# Wie viel Streuung bleibt, wenn man den Abstandseffekt herausrechnet?
R["pred"]=R.off.round(2).map(prof)
resid = R.rel - R.pred
r2 = 1 - resid.var()/R.rel.var()
print(f"\n  Anteil der Streuung, den allein der Abstand erklaert: {r2*100:.1f} %")
print(f"  Verbleibende Streuung (Standardabw. des Rests): {resid.std():.4f}")
print(f"  Streuung der rel. Tiefe insgesamt:              {R.rel.std():.4f}")
if r2 > 0.9:
    print("\n  -> Die Karte ist im Wesentlichen eine Funktion des Abstands.")
    print("     Levelspezifische Cluster loest sie NICHT auf. Der Mechanismus-Test")
    print("     ist damit nicht widerlegend, sondern mit diesen Daten nicht moeglich.")
else:
    print("\n  -> Es bleibt levelspezifische Struktur uebrig; der Test ist aussagekraeftig.")

print("\n"+"="*74)
print("Gegenprobe: variiert die Tiefe an EINEM festen Preis ueber die Zeit?")
print("="*74)
sub=R[R.off.round(2)==0.0]
print(f"  Tiefe am Mittelkurs ueber {len(sub)} Tage: "
      f"Median {sub.depth.median()/1e6:.1f} Mio, "
      f"Spanne {sub.depth.min()/1e6:.1f}-{sub.depth.max()/1e6:.1f} Mio")
