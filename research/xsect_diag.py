"""Diagnose: Ist das negative Ergebnis Signal oder Reibung?

Und die naheliegende Umkehr: Wenn Gewinner-kaufen verliert, gewinnt dann
Verlierer-kaufen (Cross-Sectional-Reversal)?
"""
import sys, glob, os, warnings, itertools
sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC")

def universe():
    cols={}
    for f in sorted(glob.glob(V+"*_1h.csv")):
        nm=os.path.basename(f)[:-7]
        if nm=="btc_recent": continue
        cols[nm.upper()]=pd.read_csv(f,index_col=0,parse_dates=True)["close"]
    px=pd.DataFrame(cols).sort_index()
    return px[px.notna().sum(axis=1)>=int(len(px.columns)*0.8)]

def run(px, lookback, rebal, k, mode, cost, reverse=False):
    ret=px.pct_change()
    sig=px.pct_change(lookback).shift(1)
    if reverse: sig=-sig
    hi=sig.rank(axis=1,ascending=False); lo=sig.rank(axis=1,ascending=True)
    W=(hi<=k).astype(float)*(0.5/k)
    if mode=="ls": W=W-(lo<=k).astype(float)*(0.5/k)
    reb=np.zeros(len(px),dtype=bool); reb[::rebal]=True
    W=W.where(pd.Series(reb,index=px.index),other=np.nan).ffill().fillna(0.0)
    turn=W.diff().abs().sum(axis=1).fillna(0)
    gross=(W.shift(1)*ret).sum(axis=1).fillna(0)
    return gross, turn, (gross-cost*turn)

def ann(s):
    d=((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()
    if len(d)<50: return np.nan
    eq=np.cumprod(1+d)
    return (max(eq[-1],1e-9)**(365/len(d))-1)*100

px=universe(); S=px[px.index<SPLIT]
print("="*88)
print("1) Signal oder Reibung? Brutto gegen Netto")
print("="*88)
print(f"{'Variante':30s} {'Umsatz/Jahr':>12s} {'Kosten/Jahr':>12s} {'BRUTTO':>10s} {'NETTO':>10s}")
print("-"*88)
for mode in ("ls","lo"):
    for rb in (4,8,24,72,168):
        g,t,n=run(S,24,rb,3,mode,16e-4)
        turn_y=t.sum()/(len(S)/24/365)
        print(f"{f'{mode}, alle {rb}h neu':30s} {turn_y:11.0f}x {turn_y*16e-4*100:11.0f}% "
              f"{ann(g):+9.1f}% {ann(n):+9.1f}%")

print("\n"+"="*88)
print("2) Umkehr: Verlierer kaufen statt Gewinner (Cross-Sectional-Reversal)")
print("="*88)
print(f"{'Rueckblick':>11s} {'alle Xh':>9s} " + f"{'Momentum':>22s} {'Reversal':>22s}")
print(f"{'':11s} {'':9s} {'brutto':>11s}{'netto':>11s} {'brutto':>11s}{'netto':>11s}")
print("-"*88)
for lb in (12,24,72):
    for rb in (24,72,168):
        gm,_,nm_=run(S,lb,rb,3,"ls",16e-4,reverse=False)
        gr,_,nr=run(S,lb,rb,3,"ls",16e-4,reverse=True)
        print(f"{lb:10d}h {rb:8d}h {ann(gm):+10.1f}%{ann(nm_):+10.1f}% "
              f"{ann(gr):+10.1f}%{ann(nr):+10.1f}%")

print("\n"+"="*88)
print("3) Und was macht der Markt selbst? (gleichgewichtet halten)")
print("="*88)
ew=px.pct_change().mean(axis=1).fillna(0)
print(f"  Gleichgewichtetes Halten aller 14 Coins: {ann(ew[ew.index<SPLIT]):+.1f} % p.a. (Suchzeitraum)")
btc=px["BTC"].pct_change().fillna(0)
print(f"  BTC allein:                              {ann(btc[btc.index<SPLIT]):+.1f} % p.a.")
