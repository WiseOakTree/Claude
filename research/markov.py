"""Markov-Ketten: traegt der Zustand von gestern Information ueber heute?

Das ist der allgemeinste Test auf kurzes Gedaechtnis. Wenn er scheitert,
scheitert jede Regel, die nur aus der jueangsten Zustandsfolge liest.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
from scipy import stats
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from msb import bars4h
D="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC"); COST=8e-4

def zustaende(r, k, kanten=None):
    if kanten is None:
        kanten=np.quantile(r[np.isfinite(r)],np.linspace(0,1,k+1))
        kanten[0]=-np.inf; kanten[-1]=np.inf
    return np.digitize(r,kanten[1:-1]), kanten

def uebergang(s,k,ordnung=1):
    """Zaehlmatrix: (Zustandsfolge der Laenge `ordnung`) -> naechster Zustand."""
    n=len(s)
    vor=np.zeros(n-ordnung,dtype=int)
    for j in range(ordnung): vor=vor*k+s[j:n-ordnung+j]
    nach=s[ordnung:]
    M=np.zeros((k**ordnung,k))
    np.add.at(M,(vor,nach),1)
    return M

print("="*94)
print("1. HAT DER MARKT EIN MARKOV-GEDAECHTNIS? (Chi-Quadrat gegen Unabhaengigkeit)")
print("="*94)
print(f"{'Markt':<6}{'Takt':<7}{'Zustaende':>10}{'Ordnung':>9}{'n':>8}{'Chi²':>10}"
      f"{'Freiheitsgr.':>13}{'p':>12}{'Cramers V':>11}")
for sym in ("btc","eth"):
    for takt,lade in (("1h",lambda s: pd.read_csv(D+f"{s}_1h.csv",index_col=0,parse_dates=True)),
                      ("4h",bars4h),
                      ("1D",lambda s: pd.read_csv(D+f"{s}_1h.csv",index_col=0,parse_dates=True)
                           .resample("1D").agg({"close":"last"}).dropna())):
        df=lade(sym); r=np.log(df.close).diff().dropna().to_numpy()
        for k in (3,5):
            for o in (1,2):
                s,_=zustaende(r,k)
                M=uebergang(s,k,o)
                M=M[M.sum(1)>=20]           # nur Zeilen mit genug Beobachtungen
                if M.shape[0]<2: continue
                chi2,p,dof,_=stats.chi2_contingency(M+0.5)
                V=np.sqrt(chi2/(M.sum()*(min(M.shape)-1)))
                print(f"{sym.upper():<6}{takt:<7}{k:>10}{o:>9}{int(M.sum()):>8}"
                      f"{chi2:>10.1f}{dof:>13}{p:>12.2e}{V:>11.3f}")
    print()

print("="*94)
print("2. NUTZT ES ETWAS? Vorhersagekraft im HOLDOUT gegen die Randverteilung")
print("="*94)
print(f"{'Markt':<6}{'Takt':<7}{'k':>4}{'Ord.':>6}{'LogLoss Modell':>16}"
      f"{'LogLoss Basis':>15}{'Verbesserung':>14}")
for sym in ("btc","eth"):
    for takt,lade in (("1h",lambda s: pd.read_csv(D+f"{s}_1h.csv",index_col=0,parse_dates=True)),
                      ("4h",bars4h)):
        df=lade(sym); rs=np.log(df.close).diff().dropna()
        tr=rs[rs.index<SPLIT].to_numpy(); ho=rs[rs.index>=SPLIT].to_numpy()
        for k in (3,5):
            for o in (1,2):
                s_tr,kanten=zustaende(tr,k)
                s_ho,_=zustaende(ho,k,kanten)
                M=uebergang(s_tr,k,o)+1.0            # Laplace
                P=M/M.sum(1,keepdims=True)
                p0=(np.bincount(s_tr,minlength=k)+1.0); p0=p0/p0.sum()
                n=len(s_ho); vor=np.zeros(n-o,dtype=int)
                for j in range(o): vor=vor*k+s_ho[j:n-o+j]
                nach=s_ho[o:]
                ll_m=-np.mean(np.log(P[vor,nach]))
                ll_0=-np.mean(np.log(p0[nach]))
                print(f"{sym.upper():<6}{takt:<7}{k:>4}{o:>6}{ll_m:>16.5f}"
                      f"{ll_0:>15.5f}{(ll_0-ll_m)/ll_0*100:>13.3f}%")

print("\n"+"="*94)
print("3. UND WIRTSCHAFTLICH? Handeln nach der Markov-Vorhersage (BTC 4h, Holdout)")
print("="*94)
df=bars4h("btc"); rs=np.log(df.close).diff().dropna()
tr=rs[rs.index<SPLIT]; ho=rs[rs.index>=SPLIT]
print(f"{'k':>4}{'Ord.':>6}{'Signale':>10}{'bp je Trade':>14}{'Kostenschwelle':>17}")
for k in (3,5):
    for o in (1,2):
        s_tr,kanten=zustaende(tr.to_numpy(),k)
        s_ho,_=zustaende(ho.to_numpy(),k,kanten)
        M=uebergang(s_tr,k,o)+1.0; P=M/M.sum(1,keepdims=True)
        mitte=(np.array([np.mean(tr.to_numpy()[s_tr==j]) for j in range(k)]))
        erw=P@mitte                      # erwartete naechste Rendite je Vorzustand
        n=len(s_ho); vor=np.zeros(n-o,dtype=int)
        for j in range(o): vor=vor*k+s_ho[j:n-o+j]
        pred=erw[vor]; ist=ho.to_numpy()[o:]
        sig=np.sign(pred)
        m=sig!=0
        netto=sig[m]*ist[m]-2*COST
        print(f"{k:>4}{o:>6}{m.sum():>10}{netto.mean()*1e4:>+13.2f}"
              f"{abs(netto.mean()*1e4)/16:>16.3f}x")
