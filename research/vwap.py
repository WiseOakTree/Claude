"""VWAP auf 4h -- als Richtungssignal, als Filter und als Risikomass.

Die entscheidende Vorfrage: Aendert die Volumengewichtung ueberhaupt etwas
gegenueber dem schlichten Durchschnitt?
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from msb import bars4h, SPLIT
COST=8e-4; HOLD=30

def build(sym):
    df=bars4h(sym).copy()
    tp=(df.high+df.low+df.close)/3          # typischer Preis, wie TradingView
    pv=tp*df.volume
    # 1) Tages-VWAP (Anker 00:00 UTC) -- der Standard fuer Krypto
    d=df.index.floor("1D")
    df["vwap_d"]=pv.groupby(d).cumsum()/df.volume.groupby(d).cumsum()
    # 2) Wochen-VWAP
    w=df.index.to_period("W").start_time
    df["vwap_w"]=pv.groupby(w).cumsum()/df.volume.groupby(w).cumsum()
    # 3) rollierender VWAP 20 / 50 Bars
    for n in (20,50):
        df[f"vwap_r{n}"]=pv.rolling(n).sum()/df.volume.rolling(n).sum()
    # 4) schlichter gleitender Durchschnitt zum Vergleich
    for n in (20,50):
        df[f"sma{n}"]=tp.rolling(n).mean()
    # 5) VWAP-Baender (volumengewichtete Streuung, 20 Bars)
    vw=df["vwap_r20"]
    var=( (tp-vw)**2 * df.volume ).rolling(20).sum()/df.volume.rolling(20).sum()
    df["vwband"]=2*np.sqrt(var)/vw
    df["tp"]=tp
    a=df.close.to_numpy(); f=np.full(len(a),np.nan); f[:-HOLD]=a[HOLD:]/a[:-HOLD]-1
    df["fwd"]=f
    r=np.log(df.close).diff()
    df["volf"]=r.shift(-HOLD).rolling(HOLD).std()*np.sqrt(6*365)
    df["dmin"]=r.shift(-HOLD).rolling(HOLD).min()
    return df

print("="*80)
print("VORFRAGE: Ist der VWAP etwas anderes als ein gleitender Durchschnitt?")
print("="*80)
for sym in ("btc","eth"):
    d=build(sym).dropna()
    for n in (20,50):
        c1=d[f"vwap_r{n}"].corr(d[f"sma{n}"])
        # Abstand des Kurses zu beiden
        a=(d.close/d[f"vwap_r{n}"]-1); b=(d.close/d[f"sma{n}"]-1)
        print(f"  {sym.upper()} {n:>2} Bars:  VWAP <-> SMA  {c1:+.4f}   "
              f"Abstand zu VWAP <-> Abstand zu SMA  {a.corr(b):+.4f}   "
              f"Ø |Differenz| {abs(a-b).mean()*100:.3f} %")

print("\n"+"="*80)
print("A. RICHTUNG: Abstand zum Tages-VWAP -> naechste 5 Tage")
print("="*80)
print(f"{'Markt':<6}{'Zeitraum':<16}{'unter VWAP':>13}{'ueber VWAP':>13}{'Spanne':>9}{'t':>7}")
for sym in ("btc","eth","sol"):
    d=build(sym)
    for nm,m in (("Suche 21-24",d.index<SPLIT),("HOLDOUT 25-26",d.index>=SPLIT)):
        g=d[m].dropna(subset=["vwap_d","fwd"]).copy()
        if len(g)<300: continue
        dist=g.close/g.vwap_d-1
        q=pd.qcut(dist,5,labels=False,duplicates="drop")
        lo=g.fwd[q==0]; hi=g.fwd[q==4]
        r=np.concatenate([lo.to_numpy(),-hi.to_numpy()])-2*COST
        t=r.mean()/(r.std(ddof=1)/np.sqrt(max(len(r)/HOLD,2)))
        print(f"{sym.upper():<6}{nm:<16}{lo.mean()*100:>+12.2f}%{hi.mean()*100:>+12.2f}%"
              f"{(lo.mean()-hi.mean())*100:>+8.2f}{t:>7.2f}")
    print()

print("="*80)
print("B. SIGNAL: VWAP-Kreuzung, bp je Trade nach Kosten")
print("="*80)
print(f"{'Markt':<6}{'VWAP-Art':<14}{'Zeitraum':<16}{'n':>6}{'bp':>9}{'t':>7}")
for sym in ("btc","eth"):
    d=build(sym)
    for col,lab in (("vwap_d","Tages"),("vwap_w","Wochen"),("vwap_r50","roll. 50")):
        for nm,m in (("Suche",d.index<SPLIT),("HOLDOUT",d.index>=SPLIT)):
            g=d[m].dropna(subset=[col,"fwd"])
            if len(g)<300: continue
            up=(g.close>g[col])&(g.close.shift(1)<=g[col].shift(1))
            dn=(g.close<g[col])&(g.close.shift(1)>=g[col].shift(1))
            sgn=np.where(up,1,np.where(dn,-1,0)); msk=sgn!=0
            if msk.sum()<20: continue
            r=sgn[msk]*g.fwd.to_numpy()[msk]-2*COST
            t=r.mean()/(r.std(ddof=1)/np.sqrt(max(msk.sum()/HOLD,2)))
            print(f"{sym.upper():<6}{lab:<14}{nm:<16}{msk.sum():>6}{r.mean()*1e4:>+8.1f}{t:>7.2f}")
        print()
