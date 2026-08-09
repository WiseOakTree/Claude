"""Die Bot-Frage sauber beantwortet.

Fuer JEDES in diesem Projekt gemessene Signal: Bei welchen Kosten je
Roundtrip wird es profitabel? Und wie sieht der Ertrag pro JAHR aus --
nicht pro Trade?
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd

S="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/"
f=pd.read_csv(S+"of/depth_feat_hist.csv.gz",index_col=0,parse_dates=True)
px=pd.read_csv(S+"vol/btc_1h.csv",index_col=0,parse_dates=True)["close"]
p5=px.reindex(f.index.union(px.index)).interpolate().reindex(f.index)
fwd=(p5.shift(-48)/p5-1)
x=f["imb5"]; m=(~x.isna())&(~fwd.isna()); xx,yy=x[m],fwd[m]
q=pd.qcut(xx,5,labels=False,duplicates="drop")
sig=np.where(q==4,1,np.where(q==0,-1,0))
tr=(sig*yy)[sig!=0]
gross=tr.mean()*1e4; sd=tr.std()*1e4
print("="*90)
print("Der beste messbare Bot-Edge: Orderbuch-Ungleichgewicht +-5 %, 4h")
print("="*90)
print(f"  {len(tr):,} Trades ueber 2,7 Jahre   brutto {gross:+.2f} bp je Trade   "
      f"Streuung {sd:.0f} bp")
print(f"  Signal-Rausch-Verhaeltnis je Trade: {gross/sd:.4f}")
print(f"  -> Man braucht {(sd/gross)**2:,.0f} Trades, damit der Edge das Rauschen ueberragt.")

print()
print("="*90)
print("MASTERTABELLE: Ab welchen Kosten traegt welches Signal?")
print("="*90)
SIGS=[("S/R-Ausbruch >=6 Beruehrungen (deins)", 45.7,  40),
      ("Orderbuch-Imbalance +-5 %, 4h",          gross, 2190),
      ("Orderbuch-Imbalance +-3 %, 4h (303 T)",  6.21,  2190),
      ("Orderflow OFI 1h (staerkstes p der Studie)", 1.26, 8760),
      ("Orderflow OFI 5 min",                    0.29, 105120),
      ("Coinbase-Premium (ETF-Fluss)",           3.0,   73)]
print(f"  {'Signal':40s} {'brutto/Trade':>13s} {'Trades/Jahr':>12s} "
      f"{'brutto p.a.':>12s} {'max. Kosten':>12s}")
print("  "+"-"*92)
for name,bp,n in SIGS:
    print(f"  {name:40s} {bp:>+12.2f}bp {n:>12,d} {bp*n/100:>+11.1f}% {bp:>11.2f}bp")
print()
print("  Du zahlst bei Kraken 16 bp je Roundtrip.")
print("  -> Alles unter 16 bp in der letzten Spalte ist fuer dich TOT,")
print("     egal wie signifikant es ist.")

print()
print("="*90)
print("Wer verdient daran -- und wie")
print("="*90)
TR=2190
print(f"  {'Kostenstufe':34s} {'netto/Trade':>12s} {'p.a. auf Nominal':>17s} {'Sharpe':>8s}")
print("  "+"-"*76)
for name,c in [("Du bei Kraken (Taker)",16.0),("Retail guter Tarif",8.0),
               ("Profi-Taker VIP",4.0),("Maker ohne Gebuehr",2.0),
               ("Market Maker mit Rebate",0.0),("MM + Rebate + Colocation",-1.0)]:
    net=gross-c
    pa=net*TR/100
    sh=(net/sd)*np.sqrt(TR)
    print(f"  {name:34s} {net:>+11.2f}bp {pa:>+16.1f}% {sh:>8.2f}")
print()
print(f"  Break-even des Signals: {gross:.2f} bp Kosten je Roundtrip.")
print(f"  Deine Kosten sind {16/max(gross,0.01):.0f}x zu hoch.")
print()
print("="*90)
print("DER VERGLEICH, DER ALLES ERKLAERT")
print("="*90)
print(f"  {'':22s} {'je Trade':>10s} {'Trades/Jahr':>12s} {'brutto p.a.':>12s} {'Sharpe':>8s}")
print("  "+"-"*68)
sr_sd=520.0   # gemessene Streuung der S/R-Trades in bp
print(f"  {'Dein S/R-Ausbruch':22s} {45.7:>+9.1f}bp {40:>12d} {45.7*40/100:>+11.1f}% "
      f"{(45.7-16)/sr_sd*np.sqrt(40):>8.2f}")
print(f"  {'Bot-Orderbuch (MM)':22s} {gross:>+9.2f}bp {TR:>12d} {gross*TR/100:>+11.1f}% "
      f"{(gross+1)/sd*np.sqrt(TR):>8.2f}")
print()
print("  Dein Edge je Trade ist ~130x groesser. Ihr Edge ist ~55x haeufiger.")
print("  Brutto pro Jahr liegt ihr sogar NIEDRIGER -- aber ihr Sharpe ist hoeher,")
print("  weil sich das Rauschen ueber 2.190 Trades herausmittelt.")
