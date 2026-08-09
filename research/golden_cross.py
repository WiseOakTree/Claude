"""Golden Cross / Death Cross (SMA 50/200) -- inkl. dynamischem SMA-Stop."""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from prop_backtester import binance

D = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
h1 = pd.read_csv(D+"btc_1h.csv", index_col=0, parse_dates=True)
def rs(df,r):
    return df if r=="1h" else df.resample(r).agg(
        {"open":"first","high":"max","low":"min","close":"last","volume":"sum"}).dropna()

COST = 16e-4
def challenge(r, win=90):
    r = r.dropna().to_numpy(); passed=tot=0; R=[];DD=[]
    for s in range(0,len(r)-win):
        w=r[s:s+win]; eq=np.cumprod(1+w); dd=(eq/np.maximum.accumulate(eq)-1).min()
        passed += (eq[-1]-1>=.10 and dd>=-.06 and w.min()>-.03); tot+=1
        R.append(eq[-1]-1); DD.append(-dd)
    if not tot: return 0,0,0
    return passed/tot*100, np.median(R)*100, np.median(DD)*100

def run(df, fast, slow, allow_short, trail_stop, lev=1.0):
    """Positionsreihe -> Tagesrenditen. Alles nur mit Daten bis Bar i."""
    c = df["close"]
    f = c.rolling(fast).mean(); s = c.rolling(slow).mean()
    raw = pd.Series(np.where(f>s, 1.0, -1.0 if allow_short else 0.0), index=df.index)
    raw[s.isna()] = 0.0
    if trail_stop:
        # dynamischer Stop: Long endet, wenn der Kurs unter den kurzen SMA faellt
        raw = raw.where(~((raw>0) & (c < f)), 0.0)
        raw = raw.where(~((raw<0) & (c > f)), 0.0)
    w = raw.shift(1).fillna(0) * lev          # Ausfuehrung fruehestens naechster Bar
    ret = c.pct_change().fillna(0)
    turn = w.diff().abs().fillna(w.abs())
    pnl = w*ret - COST*turn
    return pnl.resample("1D").sum().dropna(), int((w.diff().abs()>0).sum())

print("="*86)
print("Golden Cross / Death Cross gegen die Challenge-Regeln (16 bp Kosten)")
print("="*86)
print(f"{'TF':4s} {'SMA':>9s} {'Short':>6s} {'SMA-Stop':>9s} {'Hebel':>6s} "
      f"{'Trades':>7s} {'Rendite':>9s} {'DD':>7s} {'Pass':>7s}")
print("-"*86)
rows=[]
for tf in ("1D","4h","1h"):
    df = rs(h1, tf)
    for fast, slow in ((50,200),(20,100),(10,50)):
        if len(df) < slow*3: continue
        for sh in (True, False):
            for ts in (False, True):
                for lev in (1.0, 2.0):
                    pnl, n = run(df, fast, slow, sh, ts, lev)
                    p, m, d = challenge(pnl)
                    rows.append((tf,f"{fast}/{slow}",sh,ts,lev,n,m,d,p))
                    print(f"{tf:4s} {f'{fast}/{slow}':>9s} {'ja' if sh else 'nein':>6s} "
                          f"{'ja' if ts else 'nein':>9s} {lev:5.0f}x {n:7d} "
                          f"{m:+8.1f}% {d:6.1f}% {p:6.1f}%")
r = pd.DataFrame(rows, columns=["tf","sma","short","stop","lev","trades","med","dd","pass"])
print(f"\nBeste Pass-Rate: {r['pass'].max():.1f} %   |   "
      f"Median-Rendite ueber alle {len(r)} Varianten: {r['med'].median():+.2f} %")
print(f"Varianten mit Pass-Rate >= 50 %: {(r['pass']>=50).sum()}")
b = r.sort_values("pass", ascending=False).iloc[0]
print(f"\nBeste Variante: {b.tf}, SMA {b.sma}, Short {b['short']}, SMA-Stop {b['stop']}, "
      f"{b.lev:.0f}x -> Pass {b['pass']:.1f} %, Median {b.med:+.1f} %, DD {b.dd:.1f} %")

# Out-of-Sample der 50/200-Tagesvariante
print("\n" + "="*86)
print("Out-of-Sample: SMA 50/200 auf Tageskerzen")
print("="*86)
df = rs(h1,"1D"); half = len(df)//2
for nm, d_ in (("1. Haelfte", df.iloc[:half]), ("2. Haelfte", df.iloc[half:]), ("gesamt", df)):
    for ts in (False, True):
        pnl, n = run(d_, 50, 200, True, ts)
        p, m, dd = challenge(pnl)
        if p or m:
            print(f"  {nm:11s} SMA-Stop {'ja ' if ts else 'nein'}: "
                  f"Pass {p:5.1f}%  Median {m:+6.1f}%  DD {dd:5.1f}%  ({n} Trades)")
