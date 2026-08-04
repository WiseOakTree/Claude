"""Ist der BTC-Befund (+111 bp) robust oder eine von acht Zellen?"""
import sys, warnings, itertools
sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
O="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/oc/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC")

def prep(sym, oi_win, brk, bb_len=20, win=500):
    px=pd.read_csv(V+f"{sym}_1h.csv",index_col=0,parse_dates=True)
    oi=pd.read_csv(O+f"oi_{sym}.csv",index_col=0,parse_dates=True)
    d=px.join(oi,how="inner").ffill().dropna()
    c,h,l=d["close"],d["high"],d["low"]
    mid=c.rolling(bb_len).mean(); sd=c.rolling(bb_len).std()
    d["bb_pct"]=(2*2*sd/mid).rolling(win).rank(pct=True)
    doi=d["sum_open_interest"].pct_change(oi_win)
    d["oi_z"]=(doi-doi.rolling(win).mean())/doi.rolling(win).std()
    d["up"]=c>h.shift(1).rolling(brk).max()
    d["dn"]=c<l.shift(1).rolling(brk).min()
    return d.dropna()

def eff(d, oi_thr=None, bb_thr=None, hz=24):
    m=(d["up"]|d["dn"])
    if oi_thr is not None: m &= d["oi_z"]>oi_thr
    if bb_thr is not None: m &= d["bb_pct"]<bb_thr
    idx=np.where(m.to_numpy())[0]; dr=np.where(d["up"].to_numpy()[idx],1,-1)
    c=d["close"].to_numpy(); n=len(d); seen={}
    for t,x in zip(idx,dr):
        b=t//hz
        if b not in seen and t+hz<n: seen[b]=(c[t+hz]/c[t]-1)*x
    a=np.array(list(seen.values()))*1e4
    if len(a)<10: return np.nan,np.nan,len(a)
    _,p=stats.ttest_1samp(a,0); return a.mean(),p,len(a)

print("="*88)
print("1) Wie selten ist die vorgeschlagene Kombination (OI UND Kompression)?")
print("="*88)
for s in ("btc","eth"):
    d=prep(s,24,20)
    for bb in (0.10,0.20,0.30):
        m=(d["up"]|d["dn"])&(d["oi_z"]>2.0)&(d["bb_pct"]<bb)
        jahre=len(d)/24/365
        print(f"  {s.upper()} Kompression<{bb:.0%}: {m.sum():4d} Signale in {jahre:.1f} Jahren "
              f"= {m.sum()/jahre:5.1f} je Jahr")

print("\n"+"="*88)
print("2) Robustheit des BTC-Befunds: haelt er ueber verschiedene Fenster?")
print("     (Suchzeitraum, OI > 2 sigma, ohne Kompressionsfilter)")
print("="*88)
print(f"  {'OI-Fenster':>11s} {'Ausbruch':>9s} " + "".join(f"{s.upper():>22s}" for s in ("btc","eth")))
print("  "+"-"*66)
hits=0; total=0
for oi_win in (12,24,48,72):
    for brk in (12,20,40):
        row=f"  {oi_win:10d}h {brk:8d}h "
        for s in ("btc","eth"):
            d=prep(s,oi_win,brk); d=d[d.index<SPLIT]
            e,p,n=eff(d,oi_thr=2.0)
            total+=1; hits += (np.isfinite(e) and e>0 and p<0.05)
            row += f"{e:+10.1f} ({n:3d})" if np.isfinite(e) else f"{'—':>22s}"
        print(row)
print(f"\n  positiv UND p<0,05: {hits} von {total} Zellen "
      f"(Zufallserwartung bei 5 %: {total*0.05:.1f})")

print("\n"+"="*88)
print("3) Der harte Test: dieselben Fenster im HOLDOUT")
print("="*88)
print(f"  {'OI-Fenster':>11s} {'Ausbruch':>9s} " + "".join(f"{s.upper():>22s}" for s in ("btc","eth")))
print("  "+"-"*66)
h2=0; t2=0
for oi_win in (12,24,48,72):
    for brk in (12,20,40):
        row=f"  {oi_win:10d}h {brk:8d}h "
        for s in ("btc","eth"):
            d=prep(s,oi_win,brk); d=d[d.index>=SPLIT]
            e,p,n=eff(d,oi_thr=2.0)
            t2+=1; h2 += (np.isfinite(e) and e>0 and p<0.05)
            row += f"{e:+10.1f} ({n:3d})" if np.isfinite(e) else f"{'—':>22s}"
        print(row)
print(f"\n  positiv UND p<0,05: {h2} von {t2} Zellen")
