"""OI-Squeeze: Hebelaufbau bei Kompression, Einstieg in Ausbruchsrichtung.

2x2-Anordnung -- nur so laesst sich sagen, ob Open Interest etwas UEBER den
reinen Kompressions-Ausbruch hinaus beitraegt:

               ohne OI-Filter    mit dOI > +2 sigma
  ohne Kompr.      (A)                 (B)
  mit Kompr.       (C)                 (D)

Traegt OI, muss B > A und D > C sein -- auf beiden Assets.
Alles look-ahead-frei: Bedingungen aus Daten bis t, Einstieg zum Schluss t.
"""
import sys, warnings, itertools
sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
O="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/oc/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC"); COST=16e-4

def load(sym):
    px=pd.read_csv(V+f"{sym}_1h.csv",index_col=0,parse_dates=True)
    oi=pd.read_csv(O+f"oi_{sym}.csv",index_col=0,parse_dates=True)
    d=px.join(oi,how="inner").ffill().dropna()
    return d

def features(d, bb_len=20, bb_pct_win=500, oi_win=24, oi_z_win=500, brk=20):
    c=d["close"]; h=d["high"]; l=d["low"]
    mid=c.rolling(bb_len).mean(); sd=c.rolling(bb_len).std()
    d["bb_width"]=(2*2*sd/mid)                      # relative Bandbreite
    d["bb_pct"]=d["bb_width"].rolling(bb_pct_win).rank(pct=True)
    oi=d["sum_open_interest"]
    doi=oi.pct_change(oi_win)
    d["oi_z"]=(doi-doi.rolling(oi_z_win).mean())/doi.rolling(oi_z_win).std()
    # Preis stagniert? (Betrag der Bewegung ueber dasselbe Fenster)
    d["px_chg"]=c.pct_change(oi_win).abs()
    d["px_chg_pct"]=d["px_chg"].rolling(bb_pct_win).rank(pct=True)
    d["up"]=c>h.shift(1).rolling(brk).max()
    d["dn"]=c<l.shift(1).rolling(brk).min()
    return d.dropna()

def events(d, need_oi, need_compress, oi_thr=2.0, bb_thr=0.10):
    m=(d["up"]|d["dn"])
    if need_oi: m &= (d["oi_z"]>oi_thr)
    if need_compress: m &= (d["bb_pct"]<bb_thr)
    idx=np.where(m.to_numpy())[0]
    dirs=np.where(d["up"].to_numpy()[idx],1,-1)
    return list(zip(idx,dirs))

def effect(ev, c, n, hz=24):
    seen={}
    for t,dr in ev:
        b=t//hz
        if b not in seen and t+hz<n: seen[b]=(c[t+hz]/c[t]-1)*dr
    a=np.array(list(seen.values()))*1e4
    if len(a)<10: return np.nan,np.nan,len(a)
    _,p=stats.ttest_1samp(a,0); return a.mean(),p,len(a)

print("="*92)
print("2x2: Traegt Open Interest ueber den Kompressions-Ausbruch hinaus?")
print("     Effekt auf 24h in bp, ueberlappungskorrigiert (ein Ereignis je 24h-Block)")
print("="*92)
DATA={s:features(load(s)) for s in ("btc","eth")}
for lab,sub in (("SUCHZEITRAUM 2023-01..2024-12", lambda d: d[d.index<SPLIT]),
                ("HOLDOUT 2025-01..2026-06",      lambda d: d[d.index>=SPLIT])):
    print(f"\n{lab}")
    print(f"  {'Bedingung':34s} " + "".join(f"{s.upper():>20s}" for s in ("btc","eth")))
    print(f"  {'':34s} " + "".join(f"{'Effekt    n   p':>20s}" for _ in range(2)))
    print("  "+"-"*76)
    for need_oi,need_c,name in ((False,False,"(A) nur Ausbruch"),
                                (True, False,"(B) + OI > 2 sigma"),
                                (False,True, "(C) + Kompression"),
                                (True, True, "(D) OI UND Kompression")):
        row=f"  {name:34s} "
        for s in ("btc","eth"):
            d=sub(DATA[s]); c=d["close"].to_numpy(); n=len(d)
            e,p,cnt=effect(events(d,need_oi,need_c),c,n)
            row += f"{e:+8.1f}{cnt:5d}{p:7.3f}" if np.isfinite(e) else f"{'zu wenige':>20s}"
        print(row)

print("\n"+"="*92)
print("Feiner: Wirkt die OI-Schwelle als Dosis?")
print("="*92)
print(f"  {'OI-Schwelle':>12s} " + "".join(f"{s.upper():>22s}" for s in ("btc","eth")))
print("  "+"-"*58)
for thr in (0.0,1.0,1.5,2.0,2.5,3.0):
    row=f"  {thr:11.1f}σ "
    for s in ("btc","eth"):
        d=DATA[s][DATA[s].index<SPLIT]; c=d["close"].to_numpy(); n=len(d)
        e,p,cnt=effect(events(d,True,False,oi_thr=thr),c,n)
        row += f"{e:+10.1f} bp ({cnt:4d})" if np.isfinite(e) else f"{'—':>22s}"
    print(row)
