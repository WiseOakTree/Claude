"""Holdout fuer Cross-Sectional-Momentum + korrigierte Break-even-Rechnung."""
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
    if len(d)<60: return (np.nan,)*4
    eq=np.cumprod(1+d); dd=(eq/np.maximum.accumulate(eq)-1).min()
    a=(max(eq[-1],1e-9)**(365/len(d))-1)*100; v=d.std()*np.sqrt(365)*100
    return a, -dd*100, a/v if v>0 else 0, a/(-dd*100) if dd<0 else np.nan

px=universe()
print("="*84); print("KORREKTUR: Break-even-Kosten (vorher um Faktor 100 zu hoch)"); print("="*84)
S=px[px.index<SPLIT]; years=len(S)/24/365
ew=px.pct_change().mean(axis=1).fillna(0)
ew_s=stats(ew[ew.index<SPLIT])
print(f"{'alle Xh':>8s} {'Umsatz/J':>10s} {'brutto':>9s} {'netto 16bp':>11s} "
      f"{'Break-even':>11s} {'um Benchmark zu schlagen':>25s}")
print("-"*84)
for rb in (8,24,72,168,336):
    g,t=run(S,48,rb,3,"lo"); ty=t.sum()/years
    ga=stats(g)[0]; na=stats(g-16e-4*t)[0]
    be=ga/ty*100 if ty>0 else np.nan
    beb=(ga-ew_s[0])/ty*100 if ty>0 else np.nan
    txt=f"{beb:6.1f} bp" if beb>0 else "  nie (brutto zu schwach)"
    print(f"{rb:7d}h {ty:9.0f}x {ga:+8.1f}% {na:+10.1f}% {be:8.1f} bp {txt:>25s}")

print("\n"+"="*84)
print("HOLDOUT: beste Variante aus dem Suchzeitraum, unveraendert angewandt")
print("="*84)
LB,RB,K,MODE = 168,72,3,"lo"      # bestes Netto im Suchzeitraum
print(f"  Konfiguration: {MODE}, Rueckblick {LB}h, alle {RB}h neu, k={K}\n")
print(f"  {'Zeitraum':22s} {'p.a.':>9s} {'Drawdown':>10s} {'Sharpe':>8s} {'R/DD':>7s}")
print("  "+"-"*60)
for lab,sub in (("Suchzeitraum",px[px.index<SPLIT]),("HOLDOUT 2025-01..",px[px.index>=SPLIT])):
    g,t=run(sub,LB,RB,K,MODE); a,dd,sh,rdd=stats(g-16e-4*t)
    b=sub.pct_change().mean(axis=1).fillna(0); ba,bdd,bsh,brdd=stats(b)
    print(f"  {lab:22s} {a:+8.1f}% {dd:9.1f}% {sh:+7.2f} {rdd:6.2f}")
    print(f"  {'  Benchmark (gleichgew.)':22s} {ba:+8.1f}% {bdd:9.1f}% {bsh:+7.2f} {brdd:6.2f}")

print("\n"+"="*84)
print("Die Challenge-Frage: Verhaeltnis Rendite/Drawdown")
print("="*84)
g,t=run(px[px.index<SPLIT],LB,RB,K,MODE); a,dd,sh,rdd=stats(g-16e-4*t)
print(f"  erreicht: {rdd:.2f}    noetig: 1,67    Luecke: Faktor {1.67/rdd:.1f}" if rdd>0
      else "  negativ")
print(f"  Auf 6 % Drawdown skaliert: {a*6/dd:+.1f} % p.a. "
      f"-> +10 % dauern {10/(a*6/dd)*12:.0f} Monate" if a>0 else "")
