"""Footprint-Auswertung, STRENG KAUSAL.

Der erste Lauf hatte Look-ahead: z-Scores und CVD-Divergenz benutzten
Tagesmittel bzw. Tagesraenge -- also auch Bars, die zum Entscheidungs-
zeitpunkt noch nicht existierten. Hier nur nachlaufende Fenster.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy.stats import spearmanr
T="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/tick"
COST_BP=16.0; W=288        # nachlaufendes Fenster = 24 h auf 5-Minuten-Bars

d=pd.read_csv(f"{T}/footprint.csv",parse_dates=["bar"]).sort_values("bar").reset_index(drop=True)
d["tag"]=d.bar.dt.floor("1D")
# unvollstaendige Tage raus
voll=d.groupby("tag").size(); gut=voll[voll>=280].index
d=d[d.tag.isin(gut)].reset_index(drop=True)
print(f"Bars: {len(d):,}   Tage: {d.tag.nunique()}   Trades: {d.n.sum():,.0f}")
print(f"Zeitraum {d.bar.min():%Y-%m-%d} bis {d.bar.max():%Y-%m-%d}\n")

def zc(col):
    """z-Score gegen die VERGANGENEN W Bars, um 1 Bar verzoegert."""
    s=d[col]
    m=s.shift(1).rolling(W,min_periods=60).mean()
    sd=s.shift(1).rolling(W,min_periods=60).std().replace(0,np.nan)
    return (s-m)/sd

F={}
F["Delta (alle Trades)"]      = zc("delta")
F["Delta / Volumen"]          = d.delta/d.vol.replace(0,np.nan)
F["Delta GROSSE Trades"]      = zc("delta_big")
F["Delta KLEINE Trades"]      = zc("delta_small")
F["gross minus klein"]        = zc("delta_big")-zc("delta_small")
F["Anteil grosser Trades"]    = d.vol_big/d.vol.replace(0,np.nan)
F["mittlere Tradegroesse"]    = zc("avg_size")
F["Trade-Anzahl"]             = zc("n")
F["gestapelte Kauf-Ungl."]    = d.imb_buy
F["gestapelte Verkauf-Ungl."] = d.imb_sell
F["Ungl. netto"]              = d.imb_buy-d.imb_sell
F["POC-Lage im Bar"]          = d.poc_pos
F["Absorption"]               = zc("absorb")
# CVD-Divergenz KAUSAL: kumuliertes Delta gegen Preis, beides ueber das
# nachlaufende Fenster normiert
cvd=d.delta.cumsum()
def rel(s):
    m=s.shift(1).rolling(W,min_periods=60).mean()
    sd=s.shift(1).rolling(W,min_periods=60).std().replace(0,np.nan)
    return (s-m)/sd
F["CVD-Divergenz (kausal)"]=rel(cvd)-rel(d.close)

X=pd.DataFrame(F,index=d.index)
c=d.close.to_numpy(); same=d.tag.to_numpy()
SPLIT=pd.Timestamp("2026-01-01",tz="UTC")
tr=(d.bar<SPLIT).to_numpy(); ho=(d.bar>=SPLIT).to_numpy()
print(f"Suchzeitraum {tr.sum():,} Bars   Holdout {ho.sum():,} Bars\n")
print("="*100)
print("STRENG KAUSAL: Quintil-Spread im Holdout gegen die Kostenschwelle (16 bp)")
print("="*100)
print(f"{'Merkmal':<28}{'H':>5}{'IC Suche':>11}{'IC HOLD':>10}{'Spread HOLD':>14}{'vs 16 bp':>11}")
rows=[]
for H,lab in ((1,"5m"),(3,"15m"),(12,"1h"),(72,"6h")):
    f=np.full(len(c),np.nan); f[:-H]=c[H:]/c[:-H]-1
    ok=np.r_[same[H:]==same[:-H],[False]*H]
    f=np.where(ok,f,np.nan)
    for k in X.columns:
        x=X[k].to_numpy()
        m1=tr&np.isfinite(x)&np.isfinite(f); m2=ho&np.isfinite(x)&np.isfinite(f)
        if m1.sum()<500 or m2.sum()<500: continue
        ic1=spearmanr(x[m1],f[m1]).statistic; ic2=spearmanr(x[m2],f[m2]).statistic
        q=pd.qcut(pd.Series(x[m2]),5,labels=False,duplicates="drop"); fr=pd.Series(f[m2])
        sp=(fr[q==4].mean()-fr[q==0].mean())*1e4
        rows.append(dict(H=lab,k=k,ic1=ic1,ic2=ic2,sp=sp,
                         gleich=np.sign(ic1)==np.sign(ic2)))
R=pd.DataFrame(rows)
for _,r in R.reindex(R.sp.abs().sort_values(ascending=False).index).head(14).iterrows():
    mark=" <-- Vorzeichen kippt" if not r.gleich else ""
    print(f"{r.k:<28}{r.H:>5}{r.ic1:>+11.4f}{r.ic2:>+10.4f}{r.sp:>+13.2f}bp"
          f"{abs(r.sp)/COST_BP:>10.2f}x{mark}")
print(f"\nGleiches IC-Vorzeichen in Suche und Holdout: {R.gleich.sum()} von {len(R)} "
      f"({R.gleich.mean()*100:.0f} %)")
print(f"Merkmale ueber der Kostenschwelle im Holdout: {(R.sp.abs()>COST_BP).sum()} von {len(R)}")
print(f"  davon mit gleichem Vorzeichen:            "
      f"{((R.sp.abs()>COST_BP)&R.gleich).sum()}")
R.to_csv(f"{T}/ic_kausal.csv",index=False)
