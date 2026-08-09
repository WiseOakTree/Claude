"""FINALER TEST, korrigiertes Nullmodell.

Fehler im ersten Lauf: Das Null zog k UNABHAENGIGE Zufallszeitpunkte. Der
Keltner-Ausbruch ist aber ein ZUSTAND (mittlere Signalserie 3,1 Bars statt
1,0), seine Beobachtungen sind also stark geclustert. Ein Null ohne dieselbe
Clusterstruktur hat eine zu enge Verteilung -> Test zu liberal.

Korrektur: ZIRKULAERE VERSCHIEBUNG der ganzen Signalreihe. Das erhaelt
Anzahl, Long/Short-Quote UND Clusterstruktur exakt und zerstoert nur die
Ausrichtung zum Kurs.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pickle
CACHE="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/finaltest.pkl"
daten=pickle.load(open(CACHE,"rb"))
COST=8e-4; NAMEN=sorted(next(iter(daten.values()))["sig"].keys())

def kennzahl(hol):
    ges=[]
    for sym,d in daten.items():
        s=hol(sym,d); f=d["f"]
        m=(s!=0)&np.isfinite(f)
        if m.sum()==0: continue
        ges.append(s[m]*f[m]-2*COST)
    if not ges: return np.nan
    return np.concatenate(ges).mean()*1e4

beob={nm:kennzahl(lambda sym,d,nm=nm: d["sig"][nm]) for nm in NAMEN}
beob={k:v for k,v in beob.items() if np.isfinite(v)}
best=max(beob.values()); bester=[k for k,v in beob.items() if v==best][0]

rng=np.random.default_rng(20260808)
RUNDEN=2000
max_null=np.empty(RUNDEN)
einzel={nm:np.empty(RUNDEN) for nm in beob}
print("REALITY CHECK mit zirkulaerer Verschiebung (erhaelt die Clusterstruktur)")
print("="*88)
for b in range(RUNDEN):
    versch={sym:int(rng.integers(500,d["n"]-500)) for sym,d in daten.items()}
    w={}
    for nm in beob:
        w[nm]=kennzahl(lambda sym,d,nm=nm: np.roll(d["sig"][nm],versch[sym]))
        einzel[nm][b]=w[nm]
    max_null[b]=np.nanmax(list(w.values()))
    if (b+1)%500==0: print(f"  {b+1} Runden",flush=True)

p_fw=float(np.mean(max_null>=best))
print(f"\n  beobachtetes Maximum:          {best:+.2f} bp  ({bester})")
print(f"  Zufalls-Maximum Median:        {np.median(max_null):+.2f} bp")
print(f"  Zufalls-Maximum 95. Perzentil: {np.percentile(max_null,95):+.2f} bp")
print(f"  Zufalls-Maximum Spanne:        {max_null.min():+.2f} .. {max_null.max():+.2f} bp")
print(f"\n  FAMILIENWEISER p-WERT:         {p_fw:.4f}")
print(f"  URTEIL: {'EDGE NACHGEWIESEN' if p_fw<0.05 else 'KEIN nachweisbarer Edge'}")

print("\n"+"="*88)
print("EINZELN und Romano-Wolf-Schrittabstieg (korrigiertes Null)")
print("="*88)
print(f"{'Regel':<28}{'bp':>9}{'p einzeln':>12}{'p familienweise':>18}")
sort=sorted(beob,key=lambda n:-beob[n]); verbl=list(sort)
for nm in sort:
    p_e=float(np.mean(einzel[nm]>=beob[nm]))
    mx=np.nanmax(np.column_stack([einzel[k] for k in verbl]),axis=1)
    p_rw=float(np.mean(mx>=beob[nm]))
    print(f"{nm:<28}{beob[nm]:>+8.2f}{p_e:>12.4f}{p_rw:>18.4f}")
    verbl.remove(nm)
    if not verbl: break
