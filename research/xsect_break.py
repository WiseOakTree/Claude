"""Bei welchen Kosten traegt Cross-Sectional-Momentum -- und schlaegt es dann
ueberhaupt das gleichgewichtete Halten?"""
import sys, glob, os, warnings
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

def run(px,lb,rb,k,mode):
    ret=px.pct_change(); sig=px.pct_change(lb).shift(1)
    hi=sig.rank(axis=1,ascending=False); lo=sig.rank(axis=1,ascending=True)
    W=(hi<=k).astype(float)*(0.5/k)
    if mode=="ls": W=W-(lo<=k).astype(float)*(0.5/k)
    reb=np.zeros(len(px),dtype=bool); reb[::rb]=True
    W=W.where(pd.Series(reb,index=px.index),other=np.nan).ffill().fillna(0.0)
    turn=W.diff().abs().sum(axis=1).fillna(0)
    return (W.shift(1)*ret).sum(axis=1).fillna(0), turn

def stats(s):
    d=((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()
    eq=np.cumprod(1+d); dd=(eq/np.maximum.accumulate(eq)-1).min()
    a=(max(eq[-1],1e-9)**(365/len(d))-1)*100
    v=d.std()*np.sqrt(365)*100
    return a, -dd*100, a/v if v>0 else 0

px=universe(); S=px[px.index<SPLIT]
years=len(S)/24/365
ew=px.pct_change().mean(axis=1).fillna(0)
ew_a,ew_dd,ew_sh=stats(ew[ew.index<SPLIT])
print("="*82)
print("Vergleichsmassstab: alle 14 Coins gleichgewichtet halten")
print("="*82)
print(f"  {ew_a:+.1f} % p.a. | Drawdown {ew_dd:.0f} % | Sharpe {ew_sh:+.2f}\n")

print("="*82)
print("Bei welchen Kosten traegt es? (long-only, k=3, Rueckblick 48h)")
print("="*82)
print(f"{'alle Xh':>8s} {'Umsatz/J':>10s} {'brutto':>9s} " +
      "".join(f"{c:>9s}" for c in ("16 bp","10 bp","5 bp","2 bp","0 bp")) +
      f" {'Break-even':>11s}")
print("-"*82)
for rb in (8,24,72,168,336):
    g,t=run(S,48,rb,3,"lo")
    ty=t.sum()/years
    ga,_,_=stats(g)
    row=f"{rb:7d}h {ty:9.0f}x {ga:+8.1f}% "
    for c in (16e-4,10e-4,5e-4,2e-4,0.0):
        a,_,_=stats(g-c*t); row+=f"{a:+8.1f}%"
    be = ga/ty*1e4 if ty>0 else np.nan          # Kosten, bei denen netto = 0
    be_bench = (ga-ew_a)/ty*1e4 if ty>0 else np.nan
    print(row + f" {be:8.1f} bp")
print("\n  Break-even = Kosten, bei denen die Strategie bei NULL landet.")

print("\n"+"="*82)
print("Haerter: Ab welchen Kosten schlaegt sie das gleichgewichtete Halten?")
print("="*82)
for rb in (24,72,168,336):
    g,t=run(S,48,rb,3,"lo")
    ty=t.sum()/years; ga,_,_=stats(g)
    need=(ga-ew_a)/ty*1e4 if ty>0 else np.nan
    verdict = f"{need:.1f} bp noetig" if need>0 else "schlaegt es NIE (brutto zu schwach)"
    print(f"  alle {rb:3d}h neu: brutto {ga:+6.1f} % gegen Benchmark {ew_a:+.1f} % -> {verdict}")

print("\n"+"="*82)
print("Bestes Netto-Ergebnis bei echten 16 bp -- mit Drawdown")
print("="*82)
best=None
for lb in (24,48,72,168):
    for rb in (72,168,336):
        for mode in ("lo","ls"):
            g,t=run(S,lb,rb,3,mode)
            a,dd,sh=stats(g-16e-4*t)
            if best is None or a>best[0]: best=(a,dd,sh,lb,rb,mode)
a,dd,sh,lb,rb,mode=best
print(f"  {mode}, Rueckblick {lb}h, alle {rb}h neu: {a:+.1f} % p.a., "
      f"Drawdown {dd:.0f} %, Sharpe {sh:+.2f}")
print(f"  Benchmark (gleichgewichtet halten):        {ew_a:+.1f} % p.a., "
      f"Drawdown {ew_dd:.0f} %, Sharpe {ew_sh:+.2f}")
print(f"\n  -> {'schlaegt' if a>ew_a else 'VERLIERT gegen'} den Vergleichsmassstab")
