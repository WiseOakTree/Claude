"""Die eigentliche Frage: Nicht ALLEN Liquiditaet stellen, sondern den
GAMBLERN. Kleine Trades = Privatleute. Grosse Trades = informiert.

Wenn das Vorzeichen zwischen den Gruppen kippt, ist die Idee richtig --
man muss nur wissen, WEN man bedient.
"""
import warnings; warnings.filterwarnings("ignore")
import os,subprocess,zipfile
import numpy as np, pandas as pd
T="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/tick"
B="https://data.binance.vision/data/futures/um/daily/aggTrades/BTCUSDT"
def hole(tag):
    z=f"{T}/m3.zip"
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
teile=[]
for tag in TAGE:
    d=hole(tag)
    if d is None: continue
    p=d.price.to_numpy(); t=d.transact_time.to_numpy(); q=d.quantity.to_numpy()
    md=np.where(d.is_buyer_maker.to_numpy(),1,-1)
    n=len(p); j=np.minimum(np.searchsorted(t,t+60000),n-1)
    r=md*(p[j]/p-1)*1e4
    notional=p*q
    # Tageszeit und lokale Aktivitaet
    std=((t//3600000)%24).astype(int)
    teile.append(pd.DataFrame({"r":r,"notional":notional,"std":std,
                              "md":md,"tag":tag}))
A=pd.concat(teile,ignore_index=True)
print(f"Trades gesamt: {len(A):,}\n")

print("="*94)
print("1. NACH TRADEGROESSE -- bediene ich Privatleute oder Profis?")
print("="*94)
kanten=[0,100,500,2000,10000,50000,1e12]
lab=["unter 100 $","100-500 $","500-2.000 $","2.000-10.000 $",
     "10.000-50.000 $","ueber 50.000 $"]
A["kl"]=pd.cut(A.notional,kanten,labels=lab)
print(f"  {'Tradegroesse':<20}{'Anteil':>9}{'Trades':>12}{'Maker-Ergebnis':>17}"
      f"{'nach 1,5 bp':>14}{'mit -1 bp Rebate':>19}")
for k in lab:
    g=A[A.kl==k]
    if not len(g): continue
    m=g.r.mean()
    print(f"  {k:<20}{len(g)/len(A)*100:>8.1f}%{len(g):>12,}{m:>+16.3f} bp"
          f"{m-1.5:>+13.3f}{m+1.0:>+18.3f}")

print("\n"+"="*94)
print("2. STABIL UEBER DIE TAGE? (kleinste gegen groesste Gruppe)")
print("="*94)
print(f"  {'Tag':<13}{'unter 100 $':>15}{'ueber 50.000 $':>18}{'Differenz':>13}")
for tag in A.tag.unique():
    g=A[A.tag==tag]
    a=g[g.kl=="unter 100 $"].r.mean(); b=g[g.kl=="ueber 50.000 $"].r.mean()
    print(f"  {tag:<13}{a:>+14.3f} bp{b:>+17.3f} bp{a-b:>+12.3f}")

print("\n"+"="*94)
print("3. NACH TAGESZEIT (UTC) -- wann sind die Gegenparteien am harmlosesten?")
print("="*94)
g=A.groupby(A["std"]//3).r.agg(["mean","size"])
print(f"  {'Zeitfenster UTC':<20}{'Trades':>12}{'Maker-Ergebnis':>18}")
for i,row in g.iterrows():
    print(f"  {i*3:02d}-{i*3+3:02d} Uhr{'':<11}{int(row['size']):>12,}{row['mean']:>+17.3f} bp")

print("\n"+"="*94)
print("4. NUR KLEINE TRADES BEDIENEN -- was bliebe uebrig?")
print("="*94)
klein=A[A.notional<500]
print(f"  Anteil am Handelsaufkommen (Anzahl): {len(klein)/len(A)*100:.1f} %")
print(f"  Anteil am VOLUMEN:                   "
      f"{klein.notional.sum()/A.notional.sum()*100:.1f} %")
print(f"  Maker-Ergebnis brutto:               {klein.r.mean():+.3f} bp")
print(f"  Volumen je Tag in dieser Gruppe:     "
      f"{klein.notional.sum()/len(TAGE)/1e6:,.1f} Mio $")
for geb,l in ((1.5,"Standard 1,5 bp"),(0.0,"Gebuehr null"),(-1.0,"Rebate -1,0 bp")):
    netto=(klein.r.mean()-geb)/1e4
    print(f"    {l:<20} -> {netto*klein.notional.sum()/len(TAGE)*365:>+14,.0f} $ im Jahr, "
          f"wenn man das GESAMTE Segment bedient")
