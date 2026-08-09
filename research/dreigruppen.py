"""DREI-GRUPPEN-VERGLEICH: Indikator gegen Bauchgefuehl gegen Zufall.

Aufbau nach docs/dreigruppen_spec.md -- vor der Rechnung festgelegt.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, pickle, os
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
COST=8e-4; H=48
MAERKTE=["btc","eth","sol","bnb","xrp","ada","atom","avax","bch",
         "doge","dot","link","ltc","trx"]

def bauchgefuehl(df):
    """Zehn Heuristiken. Keine Schwellen aus der Literatur -- nur das,
    was ein Mensch beim Draufschauen tut."""
    c,h,l,o,v=df.close,df.high,df.low,df.open,df.volume
    R={}
    r24=c/c.shift(24)-1
    R["sieht bullish aus"]=np.where(r24>0,1.0,0.0)
    R["sieht bearish aus"]=np.where(r24<0,-1.0,0.0)
    r7=c/c.shift(168)-1
    q_lo=r7.rolling(720).quantile(0.10); q_hi=r7.rolling(720).quantile(0.90)
    R["ist ueberverkauft"]=np.where(r7<q_lo,1.0,0.0)
    R["ist ueberkauft"]=np.where(r7>q_hi,-1.0,0.0)
    hh7=h.rolling(168).max()
    vol_hoch=v>v.rolling(168).mean()*1.5
    R["fuehlt sich nach Breakout an"]=np.where((c>=hh7*0.995)&vol_hoch,1.0,0.0)
    tag=c.resample("1D").last()
    gruen=(tag>tag.shift(1)); rot=(tag<tag.shift(1))
    # KORREKTUR: Die Tagesbedingung ist erst am Tagesschluss bekannt.
    # Ohne shift(1) wuesste die Stunde 01:00 schon den Schluss um 23:00.
    drei_g=(gruen&gruen.shift(1)&gruen.shift(2)).shift(1).reindex(c.index,method="ffill")
    drei_r=(rot&rot.shift(1)&rot.shift(2)).shift(1).reindex(c.index,method="ffill")
    R["laeuft heiss"]=np.where(drei_g.fillna(False),1.0,0.0)
    R["faellt ins Messer"]=np.where(drei_r.fillna(False),-1.0,0.0)
    # runde Marke: naechste Zehnerpotenz-Stufe
    stufe=10**np.floor(np.log10(c.clip(lower=1e-9)))
    runde=(c/stufe).round()*stufe
    kreuz_auf=(c>runde)&(c.shift(1)<=runde); kreuz_ab=(c<runde)&(c.shift(1)>=runde)
    R["runde Zahl"]=np.where(kreuz_auf,1.0,np.where(kreuz_ab,-1.0,0.0))
    bew=(c/c.shift(24)-1)
    gross=bew.abs()>bew.abs().rolling(720).quantile(0.80)
    R["grosse Kerze"]=np.where(gross,np.sign(bew),0.0)
    vol_ruhig=c.pct_change().rolling(168).std()
    ruhig=vol_ruhig<vol_ruhig.rolling(720).quantile(0.20)
    aus=(c>c.rolling(168).max().shift(1))|(c<c.rolling(168).min().shift(1))
    R["war ruhig, jetzt gehts los"]=np.where(ruhig.shift(1).fillna(False)&aus,
                                     np.sign(c-c.shift(24)),0.0)
    return {k:pd.Series(np.asarray(x,dtype=float),index=c.index).fillna(0).to_numpy()
            for k,x in R.items()}

CACHE="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/dreigr.pkl"
if os.path.exists(CACHE):
    bg=pickle.load(open(CACHE,"rb"))
else:
    bg={}
    for sym in MAERKTE:
        df=pd.read_csv(V+f"{sym}_1h.csv",index_col=0,parse_dates=True)
        c=df.close.to_numpy(); n=len(c)
        f=np.full(n,np.nan); f[:-H]=c[H:]/c[:-H]-1
        bg[sym]={"f":f,"n":n,"sig":bauchgefuehl(df)}
        print(f"  {sym.upper()}: {len(bg[sym]['sig'])} Heuristiken",flush=True)
    pickle.dump(bg,open(CACHE,"wb"))

ind=pickle.load(open("/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/finaltest.pkl","rb"))

def kennzahl(daten,hol):
    ges=[]
    for sym,d in daten.items():
        s=hol(sym,d); f=d["f"]
        m=(s!=0)&np.isfinite(f)
        if m.sum()==0: continue
        ges.append(s[m]*f[m]-2*COST)
    if not ges: return np.nan,0
    x=np.concatenate(ges); return x.mean()*1e4, len(x)

print("\n"+"="*88)
print("GRUPPE 1 -- INDIKATOR-TRADER (25 kanonische Regeln)")
print("="*88)
g1={}
for nm in sorted(next(iter(ind.values()))["sig"]):
    bp,n=kennzahl(ind,lambda sym,d,nm=nm: d["sig"][nm]); g1[nm]=bp
for nm,bp in sorted(g1.items(),key=lambda x:-x[1]):
    print(f"  {nm:<30}{bp:>+9.2f} bp")

print("\n"+"="*88)
print("GRUPPE 2a -- BAUCHGEFUEHL, simuliert (10 Heuristiken)")
print("="*88)
g2={}
for nm in sorted(next(iter(bg.values()))["sig"]):
    bp,n=kennzahl(bg,lambda sym,d,nm=nm: d["sig"][nm]); g2[nm]=bp
    print(f"  {nm:<30}{bp:>+9.2f} bp   ({n:,} Trades)")

print("\n"+"="*88)
print("GRUPPE 3 -- ZUFALL (gleiche Anzahl, Haltedauer, Long/Short-Quote)")
print("="*88)
rng=np.random.default_rng(20260808)
g3=[]
for i in range(60):
    quelle=ind if i%2==0 else bg
    nm=rng.choice(sorted(next(iter(quelle.values()))["sig"]))
    versch={sym:int(rng.integers(500,d["n"]-500)) for sym,d in quelle.items()}
    bp,_=kennzahl(quelle,lambda sym,d,nm=nm: np.roll(d["sig"][nm],versch[sym]))
    if np.isfinite(bp): g3.append(bp)
g3=np.array(g3)
print(f"  {len(g3)} Zufallsvarianten   Median {np.median(g3):+.2f} bp   "
      f"Spanne {g3.min():+.2f} .. {g3.max():+.2f}")
pickle.dump({"g1":g1,"g2":g2,"g3":g3},
            open("/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/dg_erg.pkl","wb"))
