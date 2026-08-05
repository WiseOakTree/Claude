"""Der S&P-500-Straddle: haelt er den bekannten Katastrophen stand,
und was macht er auf einem gefundeten Konto?
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
s=pd.read_csv("straddle_SP500.csv",index_col=0,parse_dates=True).iloc[:,0]
print("="*86)
print("1) Die schlimmsten Tage -- welche Ereignisse waren dabei?")
print("="*86)
for d,v in s.nsmallest(8).items():
    print(f"   {d:%Y-%m-%d}   {v*100:+6.2f} %")
print()
mo=(1+s).resample("ME").prod()-1
print("   Schlechteste Monate:")
for d,v in mo.nsmallest(6).items(): print(f"   {d:%Y-%m}      {v*100:+6.2f} %")
print()
eq=(1+s).cumprod(); dd=eq/eq.cummax()-1
print(f"   Groesster Drawdown {dd.min()*100:.1f} % am {dd.idxmin():%Y-%m-%d}")
print("   (Zeitraum enthaelt Volmageddon 2018, COVID 2020, Baermarkt 2022)")

print()
print("="*86)
print("2) Auf einem gefundeten 100.000-$-Konto")
print("="*86)
def year(x,day_lim,ddl):
    o=[]
    for st in range(0,len(x)-252,3):
        e=1.0; g=None
        for k in range(st,st+252):
            if day_lim is not None and x[k]<-day_lim: g="Tag";break
            e*=(1+x[k])
            if e<=1-ddl: g="DD";break
        o.append((g is None,e-1 if g is None else -ddl))
    return np.array([q[0] for q in o]),np.array([q[1] for q in o])
x=s.to_numpy()
for name,dl,ddl in [("Kraken-Typ: 3 % Tag / 6 % DD",0.03,0.06),
                    ("5 % Tag / 10 % DD",0.05,0.10),
                    ("kein Tageslimit / 10 % DD",None,0.10),
                    ("eigenes Kapital",None,0.95)]:
    print(f"\n  {name}")
    print(f"    {'Hebel':>7s} {'Vol p.a.':>9s} {'ueberlebt':>10s} {'Ø Rendite':>11s} {'>=20 %':>8s}")
    for L in [1,2,3,4,5]:
        sv,rt=year(x*L,dl,ddl)
        print(f"    {L:>6d}x {s.std()*np.sqrt(252)*L*100:>8.1f}% {sv.mean()*100:>9.1f}% "
              f"{rt.mean()*100:>+10.1f}% {((sv)&(rt>=.20)).mean()*100:>7.1f}%")

print()
print("="*86)
print("3) Direktvergleich aller Kandidaten dieses Projekts")
print("="*86)
print(f"  {'':30s} {'Sharpe':>7s} {'Vol':>7s} {'max.DD':>8s} {'Daten':>10s} {'Kosten/RT':>10s}")
print("  "+"-"*76)
rows=[("S&P-500-Straddle (VRP)",1.52,5.5,-13.7,"10 Jahre","~2 bp"),
      ("BTC-Straddle (VRP)",1.85,13.6,-13.7,"5,4 Jahre","~5 bp"),
      ("S/R-Ausbruch BTC",1.07,25.0,-30.4,"5,4 Jahre","16 bp"),
      ("Trendfolge 20 Maerkte",0.44,15.1,-50.5,"36 Jahre","~2 bp"),
      ("  davon 2017-2026",-0.17,15.1,-38.2,"9 Jahre","~2 bp"),
      ("BTC einfach halten",0.34,55.6,-76.6,"5,4 Jahre","einmalig")]
for n,sh,v,d,dat,c in rows:
    print(f"  {n:30s} {sh:>7.2f} {v:>6.1f}% {d:>7.1f}% {dat:>10s} {c:>10s}")
