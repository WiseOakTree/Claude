"""Liquidations-Karte selbst gebaut -- die Rechnung hinter jeder Heatmap.

Zutaten (alle aus Primaerquellen, kein Anbieter dazwischen):
  * Open Interest je 5 Minuten  -> wie viele NEUE Positionen wurden eroeffnet
  * Taker-Long/Short-Verhaeltnis -> waren es eher Longs oder Shorts
  * Preis                        -> zu welchem Kurs

Modell: neue Position bei Kurs P mit Hebel L wird liquidiert bei
  Long:  P * (1 - 1/L)      Short: P * (1 + 1/L)
Hebelmischung wie bei Binance-Retail ueblich: 10x, 25x, 50x, 100x.
Masse zerfaellt (Positionen werden geschlossen) und verschwindet, wenn der
Kurs das Niveau durchlaeuft -- dann WURDE liquidiert.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
T="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/tick"

BIN=50.0; LO=20000.0; HI=260000.0
NB=int((HI-LO)/BIN)
HALBWERT=864          # 3 Tage in 5-Minuten-Bars
LEV=[(10,0.20),(25,0.30),(50,0.30),(100,0.20)]

k=pd.read_csv(f"{T}/k5.csv",parse_dates=["ts"])
m=pd.read_csv(f"{T}/metrics.csv",parse_dates=["ts"])
m=m[["ts","sum_open_interest","sum_taker_long_short_vol_ratio",
     "count_toptrader_long_short_ratio"]]
d=k.merge(m,on="ts",how="inner").sort_values("ts").reset_index(drop=True)
d=d[(d.close>LO)&(d.close<HI)].reset_index(drop=True)
print(f"Bars mit Preis UND Open Interest: {len(d):,}")
print(f"Zeitraum {d.ts.min():%Y-%m-%d} bis {d.ts.max():%Y-%m-%d}\n")

oi=d.sum_open_interest.to_numpy()
doi=np.r_[0.0,np.diff(oi)]
ratio=d.sum_taker_long_short_vol_ratio.replace(0,np.nan).ffill().fillna(1.0).to_numpy()
p_long=np.clip(ratio/(1+ratio),0.1,0.9)
close=d.close.to_numpy(); high=d.high.to_numpy(); low=d.low.to_numpy()

longs=np.zeros(NB); shorts=np.zeros(NB)
lam=np.log(2)/HALBWERT
idx=lambda x: np.clip(((x-LO)/BIN).astype(int),0,NB-1)

liq_ab=np.zeros(len(d)); liq_be=np.zeros(len(d))
biggest_ab=np.full(len(d),np.nan); biggest_be=np.full(len(d),np.nan)
getroffen=np.zeros(len(d))

for t in range(len(d)):
    # 1) taeglicher Zerfall (Positionen werden geschlossen)
    if t % 288 == 0 and t > 0:
        f=np.exp(-lam*288); longs*=f; shorts*=f
    # 2) was der Kurs in diesem Bar durchlaufen hat, wurde liquidiert
    a,b=idx(low[t]),idx(high[t])
    getroffen[t]=longs[a:b+1].sum()+shorts[a:b+1].sum()
    longs[a:b+1]=0.0; shorts[a:b+1]=0.0
    # 3) neue Positionen eintragen
    if doi[t]>0:
        neu=doi[t]; P=close[t]
        for L,w in LEV:
            longs[idx(P*(1-1/L))]  += neu*p_long[t]*w
            shorts[idx(P*(1+1/L))] += neu*(1-p_long[t])*w
    # 4) Merkmale: Masse innerhalb +-3 % um den Kurs
    P=close[t]
    a1,b1=idx(P),idx(P*1.03); a2,b2=idx(P*0.97),idx(P)
    liq_ab[t]=shorts[a1:b1+1].sum()+longs[a1:b1+1].sum()
    liq_be[t]=shorts[a2:b2+1].sum()+longs[a2:b2+1].sum()
    if b1>a1:
        j=a1+int(np.argmax(shorts[a1:b1+1]+longs[a1:b1+1]))
        biggest_ab[t]=(LO+j*BIN)/P-1
    if b2>a2:
        j=a2+int(np.argmax(shorts[a2:b2+1]+longs[a2:b2+1]))
        biggest_be[t]=1-(LO+j*BIN)/P

d["liq_ab"]=liq_ab; d["liq_be"]=liq_be
d["liq_asym"]=(liq_ab-liq_be)/(liq_ab+liq_be+1e-9)
d["dist_ab"]=biggest_ab; d["dist_be"]=biggest_be
d["getroffen"]=getroffen
d.to_csv(f"{T}/liqmap.csv",index=False)
print(f"Karte gebaut. Ø Masse ueber dem Kurs {liq_ab.mean():,.0f}, "
      f"darunter {liq_be.mean():,.0f}")
print(f"Bars mit ausgeloester Liquidationsmasse: {(getroffen>0).mean()*100:.1f} %")
