"""Footprint-Merkmale gegen die Zukunft. Echte Tickdaten, 5-Minuten-Bars.

Die Frage ist nicht 'ist es signifikant' -- bei Millionen Trades ist alles
signifikant. Die Frage ist: reicht es ueber die Kostenschwelle von 16 bp?
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy.stats import spearmanr
T="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/tick"
COST_BP=16.0

d=pd.read_csv(f"{T}/footprint.csv",parse_dates=["bar"]).sort_values("bar").reset_index(drop=True)
d["tag"]=d.bar.dt.floor("1D")
print(f"Bars: {len(d):,}   Tage: {d.tag.nunique()}   Trades gesamt: {d.n.sum():,.0f}")
print(f"Zeitraum: {d.bar.min()}  bis  {d.bar.max()}\n")

# Merkmale -- je Tag standardisiert, damit Niveauverschiebungen nicht stoeren
def z(col):
    g=d.groupby("tag")[col]
    return (d[col]-g.transform("mean"))/g.transform("std").replace(0,np.nan)

F={}
F["Delta (alle Trades)"]      = z("delta")
F["Delta / Volumen"]          = d.delta/d.vol.replace(0,np.nan)
F["Delta GROSSE Trades"]      = z("delta_big")
F["Delta KLEINE Trades"]      = z("delta_small")
F["gross minus klein"]        = z("delta_big")-z("delta_small")
F["Anteil grosser Trades"]    = d.vol_big/d.vol.replace(0,np.nan)
F["mittlere Tradegroesse"]    = z("avg_size")
F["Trade-Anzahl"]             = z("n")
F["gestapelte Kauf-Ungl."]    = d.imb_buy
F["gestapelte Verkauf-Ungl."] = d.imb_sell
F["Ungl. netto"]              = d.imb_buy-d.imb_sell
F["POC-Lage im Bar"]          = d.poc_pos
F["Absorption"]               = z("absorb")
# kumuliertes Delta gegen Preis (die klassische Divergenz)
d["cvd"]=d.groupby("tag").delta.cumsum()
F["CVD-Divergenz"] = (d.groupby("tag").cvd.rank(pct=True)
                      - d.groupby("tag").close.rank(pct=True))

X=pd.DataFrame(F,index=d.index)
c=d.close.to_numpy()
SPLIT=pd.Timestamp("2026-01-01",tz="UTC")
tr=(d.bar<SPLIT).to_numpy(); ho=(d.bar>=SPLIT).to_numpy()
print(f"Suchzeitraum: {tr.sum():,} Bars   Holdout: {ho.sum():,} Bars\n")

print("="*104)
print("INFORMATIONSKOEFFIZIENT gegen die Kostenschwelle (16 bp je Roundtrip)")
print("="*104)
print(f"{'Merkmal':<28}{'H':>4}{'IC Suche':>10}{'IC HOLD':>10}{'Q5-Q1 HOLD':>13}"
      f"{'in bp':>9}{'vs 16 bp':>10}")
rows=[]
for H,lab in ((1,"5m"),(3,"15m"),(12,"1h"),(72,"6h")):
    f=np.full(len(c),np.nan); f[:-H]=c[H:]/c[:-H]-1
    # Tagesgrenzen nicht ueberspringen
    same=d.tag.to_numpy()
    ok=np.r_[same[H:]==same[:-H],[False]*H]
    f=np.where(ok,f,np.nan)
    for k in X.columns:
        x=X[k].to_numpy()
        m1=tr&np.isfinite(x)&np.isfinite(f); m2=ho&np.isfinite(x)&np.isfinite(f)
        if m1.sum()<500 or m2.sum()<500: continue
        ic1=spearmanr(x[m1],f[m1]).statistic
        ic2=spearmanr(x[m2],f[m2]).statistic
        q=pd.qcut(pd.Series(x[m2]),5,labels=False,duplicates="drop")
        fr=pd.Series(f[m2])
        spread=(fr[q==4].mean()-fr[q==0].mean())*1e4
        rows.append(dict(H=lab,k=k,ic1=ic1,ic2=ic2,sp=spread))
R=pd.DataFrame(rows)
for _,r in R.reindex(R.sp.abs().sort_values(ascending=False).index).head(22).iterrows():
    print(f"{r.k:<28}{r.H:>4}{r.ic1:>+10.4f}{r.ic2:>+10.4f}{r.sp:>+12.2f}bp"
          f"{'':>9}{abs(r.sp)/COST_BP:>9.2f}x")
print(f"\nMerkmale mit gleichem IC-Vorzeichen in Suche und Holdout: "
      f"{(np.sign(R.ic1)==np.sign(R.ic2)).sum()} von {len(R)} "
      f"({(np.sign(R.ic1)==np.sign(R.ic2)).mean()*100:.0f} %)")
print(f"Groesster Quintil-Spread im Holdout: {R.sp.abs().max():.2f} bp "
      f"= {R.sp.abs().max()/COST_BP:.2f}x der Kostenschwelle")
R.to_csv(f"{T}/ic.csv",index=False)
