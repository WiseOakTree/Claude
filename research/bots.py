"""Was die Bots finden -- und ab welcher Kostenstruktur es Geld wird.

Das Orderbuch-Ungleichgewicht ist das einzige Signal dieser Untersuchung,
das out-of-sample STAERKER wurde. Es ist ein echter Bot-Edge. Hier wird
durchgerechnet, welche Kostenstruktur noetig waere, damit er traegt.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats

S="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/"
f=pd.read_csv(S+"of/depth_feat_hist.csv.gz",index_col=0,parse_dates=True)
px=pd.read_csv(S+"vol/btc_1h.csv",index_col=0,parse_dates=True)["close"]
p5=px.reindex(f.index.union(px.index)).interpolate().reindex(f.index)

print("="*88)
print("Der beste Bot-Edge dieser Untersuchung: Orderbuch-Ungleichgewicht")
print(f"{len(f):,} Snapshots, {f.index[0]:%Y-%m} bis {f.index[-1]:%Y-%m}".rjust(88))
print("="*88)

BARS={"1h":12,"4h":48}
res={}
for hname,k in BARS.items():
    fwd=(p5.shift(-k)/p5-1)
    for col in ["imb3","imb5"]:
        x=f[col]; m=(~x.isna())&(~fwd.isna())
        xx,yy=x[m],fwd[m]
        ic=np.corrcoef(xx,yy)[0,1]
        q=pd.qcut(xx,5,labels=False,duplicates="drop")
        spread=(yy[q==4].mean()-yy[q==0].mean())*1e4
        # Handelbare Umsetzung: Long im obersten Quintil, Short im untersten
        sig=np.where(q==4,1,np.where(q==0,-1,0))
        gross=(sig*yy).mean()*1e4                  # bp je Position
        res[(hname,col)]=(ic,spread,gross,len(xx))
        print(f"  {col} / {hname:>2s}   IC {ic:+.4f}   Q5-Q1 {spread:+6.2f} bp   "
              f"brutto je Trade {gross:+6.2f} bp")

print()
print("="*88)
print("Ab welcher Kostenstruktur wird daraus Geld?  (imb3, 4h-Horizont)")
print("="*88)
ic,spread,gross,nn = res[("4h","imb3")]
trades_pa = 365*24/4          # alle 4 Stunden umschichten
print(f"  Bruttoertrag je Trade: {gross:.2f} bp    Trades pro Jahr: {trades_pa:.0f}")
print()
print(f"  {'Wer':38s} {'Kosten/RT':>10s} {'netto/Trade':>12s} {'Rendite p.a.':>13s}")
print("  "+"-"*76)
COSTS=[("Du bei Kraken Prop (Taker)",16.0),
       ("Retail mit gutem Tarif (Taker)",8.0),
       ("Profi-Taker, VIP-Stufe",4.0),
       ("Maker, keine Gebuehr",2.0),
       ("Market Maker mit Rebate",0.0),
       ("MM mit Rebate + Colocation",-1.0)]
for name,c in COSTS:
    net=gross-c
    pa=net*trades_pa/1e4*100
    print(f"  {name:38s} {c:>9.1f}bp {net:>+11.2f}bp {pa:>+12.0f}%")
print()
print(f"  Break-even liegt bei {gross:.2f} bp Kosten je Roundtrip.")
print(f"  Du zahlst 16 bp. Faktor: {16/gross:.1f}x zu viel.")

print()
print("="*88)
print("Die zweite Haelfte der Antwort: WIE VIEL Kapital braucht das?")
print("="*88)
print(f"  {'Kostenstufe':28s} {'netto/Trade':>12s} {'noetiges Kapital fuer 100.000 $/Jahr':>36s}")
print("  "+"-"*78)
for name,c in COSTS[2:]:
    net=(gross-c)/1e4
    if net<=0: continue
    kap=100000/(net*trades_pa)
    print(f"  {name:28s} {(gross-c):>+11.2f}bp {kap:>34,.0f} $")
print()
print("  Bei diesen Margen ist der Ertrag proportional zum Kapital --")
print("  deshalb sind es GROSSE Firmen. Der Edge je Trade ist winzig.")
