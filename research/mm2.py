"""Sauberer: Jeder Trade in den Daten HAT einen Market Maker auf der
Gegenseite. Ich messe direkt, was dieser Maker verdient hat -- kein
Quote-Modell, keine Verzoegerung, keine Annahme.

Klassische Zerlegung:
  effektiver Spread = was der Taker zahlt
  realisierter Spread = was der Maker BEHAELT (nach adverser Selektion)
  Preiseinfluss = die adverse Selektion
"""
import warnings; warnings.filterwarnings("ignore")
import os,subprocess,zipfile
import numpy as np, pandas as pd
T="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/tick"
B="https://data.binance.vision/data/futures/um/daily/aggTrades/BTCUSDT"

def hole(tag):
    z=f"{T}/m2.zip"
    r=subprocess.run(["curl","-sS","-f","--max-time","300","-o",z,
                      f"{B}/BTCUSDT-aggTrades-{tag}.zip"],capture_output=True)
    if r.returncode!=0: return None
    with zipfile.ZipFile(z) as zf:
        d=pd.read_csv(zf.open(zf.namelist()[0]),
            usecols=["price","quantity","transact_time","is_buyer_maker"],
            dtype={"price":"float64","quantity":"float64",
                   "transact_time":"int64","is_buyer_maker":"bool"})
    os.remove(z); return d

TAGE=["2026-03-10","2026-05-19","2026-06-24","2026-07-15","2026-08-02"]
print("="*98)
print("WAS VERDIENT DER MAKER BEI JEDEM ECHTEN TRADE?")
print("(positiv = der Maker behaelt etwas, negativ = er wurde ausgenommen)")
print("="*98)
print(f"{'Tag':<13}{'Trades':>11}{'1 s':>10}{'10 s':>10}{'1 min':>10}"
      f"{'10 min':>10}{'gewichtet 1min':>16}")
alle={}
for tag in TAGE:
    d=hole(tag)
    if d is None: continue
    p=d.price.to_numpy(); t=d.transact_time.to_numpy(); q=d.quantity.to_numpy()
    # Taker-Richtung: is_buyer_maker=False -> Kaeufer war aggressiv -> Maker VERKAUFT
    maker_dir=np.where(d.is_buyer_maker.to_numpy(),1,-1)   # +1 = Maker kauft
    n=len(p); zeile=[]
    for hor in (1000,10000,60000,600000):
        j=np.minimum(np.searchsorted(t,t+hor),n-1)
        # Maker kauft zu p, spaeter wert p[j]  -> Gewinn (p[j]/p - 1)
        r=maker_dir*(p[j]/p-1)*1e4
        zeile.append(r.mean())
        if hor==60000: gew=np.average(r,weights=q); r60=r
    alle[tag]=r60
    print(f"{tag:<13}{n:>11,}"+"".join(f"{x:>+10.3f}" for x in zeile)+f"{gew:>+16.3f}")

R=np.concatenate(list(alle.values()))
print(f"\n  Gepoolt ueber {len(R):,} Trades, Horizont 1 Minute: "
      f"{R.mean():+.3f} bp je Trade")
print(f"  Median {np.median(R):+.3f} bp   Anteil positiv {np.mean(R>0)*100:.1f} %")

print("\n"+"="*98)
print("UND JETZT DIE RECHNUNG, DIE ZAEHLT")
print("="*98)
brutto=R.mean()
for gebuehr,lab in ((1.5,"Standard-Maker (Binance/Hyperliquid)"),
                    (0.0,"Maker-Gebuehr null (hoehere Stufe)"),
                    (-0.5,"mit Rebate -0,5 bp (VIP/Marktmacher-Programm)"),
                    (-1.0,"mit Rebate -1,0 bp (Top-Stufe)")):
    netto=brutto-gebuehr
    print(f"  {lab:<44}{netto:>+8.3f} bp je Trade")

print("\n  Was das bei realistischem Volumen bedeutet:")
print(f"  {'gestelltes Volumen/Tag':<28}{'bei 1,5 bp':>14}{'bei 0 bp':>12}"
      f"{'bei -0,5 bp':>14}{'bei -1,0 bp':>14}")
for vol in (100_000,1_000_000,10_000_000):
    z=[(brutto-g)/1e4*vol*365 for g in (1.5,0.0,-0.5,-1.0)]
    print(f"  {vol:>22,} $"+"".join(f"{x:>13,.0f} $" for x in z))
print("\n  (Jahresrechnung, unterstellt gleichbleibendes Volumen und dass man")
print("   ueberhaupt gefuellt wird -- die Warteschlange ist hier nicht modelliert.)")
