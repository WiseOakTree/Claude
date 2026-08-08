"""Auswertung des Drei-Gruppen-Vergleichs nach der vorab festgelegten
Spezifikation: Kruskal-Wallis, paarweise Mann-Whitney mit Holm-Korrektur.
Plus Gruppe 2b -- 41.362 echte Hyperliquid-Konten."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, pickle
from scipy import stats
S="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad"
E=pickle.load(open(f"{S}/dg_erg.pkl","rb"))
g1=np.array(sorted(E["g1"].values())); g2=np.array(sorted(E["g2"].values()))
g3=np.array(sorted(E["g3"]))

# Gruppe 2b: echte Menschen
L=pd.read_csv(f"{S}/hl/leaderboard.csv")
akt=L[(L.vlm_allTime>1e6)&(L.wert>1000)].copy()
# PnL je gehandeltem Volumen -> Boersen zaehlen jede Seite, also x2 fuer Roundtrip
akt["bp"]=akt.pnl_allTime/akt.vlm_allTime*1e4*2
g2b=akt.bp.to_numpy()
g2b=g2b[np.isfinite(g2b)]

print("="*92)
print("DIE VIER GRUPPEN AUF GEMEINSAMEM MASSSTAB (bp je Trade nach Kosten)")
print("="*92)
print(f"{'Gruppe':<34}{'n':>8}{'Median':>10}{'25 %':>10}{'75 %':>10}{'Spanne':>22}")
G={"1  Indikator-Trader (Regeln)":g1,
   "2a Bauchgefuehl (Heuristiken)":g2,
   "2b Bauchgefuehl (echte Menschen)":g2b,
   "3  Zufall":g3}
for k,v in G.items():
    print(f"{k:<34}{len(v):>8,}{np.median(v):>+10.2f}{np.percentile(v,25):>+10.2f}"
          f"{np.percentile(v,75):>+10.2f}{f'{v.min():+.1f} .. {v.max():+.1f}':>22}")

print("\n"+"="*92)
print("VORAB FESTGELEGTER TEST: Kruskal-Wallis ueber die drei Hauptgruppen")
print("="*92)
h,p=stats.kruskal(g1,g2,g3)
print(f"  H = {h:.3f}   p = {p:.4f}")
print(f"  URTEIL: {'Gruppen UNTERSCHEIDBAR' if p<0.05 else '1 = 2 = 3, NICHT unterscheidbar'}")
h4,p4=stats.kruskal(g1,g2,g2b,g3)
print(f"\n  mit echten Menschen (4 Gruppen): H = {h4:.3f}   p = {p4:.2e}")

print("\n"+"="*92)
print("PAARWEISE (Mann-Whitney-U, Holm-korrigiert)")
print("="*92)
paare=[("1 Indikator","2a Bauchgefuehl",g1,g2),
       ("1 Indikator","3 Zufall",g1,g3),
       ("2a Bauchgefuehl","3 Zufall",g2,g3),
       ("2b echte Menschen","3 Zufall",g2b,g3),
       ("2b echte Menschen","1 Indikator",g2b,g1)]
roh=[(a,b,stats.mannwhitneyu(x,y).pvalue) for a,b,x,y in paare]
srt=sorted(range(len(roh)),key=lambda i:roh[i][2])
holm={}
for rang,i in enumerate(srt):
    holm[i]=min(1.0,roh[i][2]*(len(roh)-rang))
print(f"  {'Vergleich':<38}{'p roh':>10}{'p Holm':>10}{'Urteil':>22}")
for i,(a,b,p_) in enumerate(roh):
    ph=holm[i]
    print(f"  {a+' gegen '+b:<38}{p_:>10.4f}{ph:>10.4f}"
          f"{('unterscheidbar' if ph<0.05 else 'nicht unterscheidbar'):>22}")

print("\n"+"="*92)
print("UEBERLAPPUNG DER VERTEILUNGEN")
print("="*92)
for a,b,x,y in paare[:3]:
    lo=max(np.percentile(x,10),np.percentile(y,10))
    hi=min(np.percentile(x,90),np.percentile(y,90))
    ax=np.mean((x>=lo)&(x<=hi))*100; ay=np.mean((y>=lo)&(y<=hi))*100
    print(f"  {a} / {b}: gemeinsamer Bereich {lo:+.1f} .. {hi:+.1f} bp   "
          f"enthaelt {ax:.0f} % bzw. {ay:.0f} % der Faelle")
print()
print(f"  Anteil ueber null:  Indikator {np.mean(g1>0)*100:.0f} %   "
      f"Bauchgefuehl {np.mean(g2>0)*100:.0f} %   "
      f"echte Menschen {np.mean(g2b>0)*100:.0f} %   "
      f"Zufall {np.mean(g3>0)*100:.0f} %")
