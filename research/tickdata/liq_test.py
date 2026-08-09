"""Die Liquidations-Behauptungen gegen die Zukunft geprueft.

1. Magnet: laeuft der Kurs zur groesseren Liquidationsmasse?
2. Nach dem Treffer: Umkehr oder Fortsetzung?
3. Als Risikomass: sagt die Masse die kommende Bewegung an?
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy.stats import spearmanr
T="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/tick"
COST_BP=16.0
d=pd.read_csv(f"{T}/liqmap.csv",parse_dates=["ts"]).reset_index(drop=True)
# erste 30 Tage verwerfen: die Karte muss sich erst fuellen
d=d.iloc[288*30:].reset_index(drop=True)
SPLIT=pd.Timestamp("2026-01-01",tz="UTC")
tr=(d.ts<SPLIT).to_numpy(); ho=(d.ts>=SPLIT).to_numpy()
c=d.close.to_numpy()
print(f"Bars {len(d):,}   Suche {tr.sum():,}   Holdout {ho.sum():,}")
print(f"Zeitraum {d.ts.min():%Y-%m-%d} bis {d.ts.max():%Y-%m-%d}\n")

F={
 "Asymmetrie oben/unten":  d.liq_asym,
 "Masse oben (log)":       np.log1p(d.liq_ab),
 "Masse unten (log)":      np.log1p(d.liq_be),
 "Masse gesamt (log)":     np.log1p(d.liq_ab+d.liq_be),
 "Abstand groesster oben": d.dist_ab,
 "Abstand groesster unten":d.dist_be,
 "naeher an oben als unten": d.dist_be-d.dist_ab,
 "gerade ausgeloest (log)":np.log1p(d.getroffen),
}
print("="*96)
print("1. MAGNET-TEST: sagt die Liquidationslage die Richtung voraus?")
print("="*96)
print(f"{'Merkmal':<28}{'H':>5}{'IC Suche':>11}{'IC HOLD':>10}{'Spread HOLD':>14}{'vs 16 bp':>10}")
rows=[]
for H,lab in ((12,"1h"),(72,"6h"),(288,"1d"),(864,"3d")):
    f=np.full(len(c),np.nan); f[:-H]=c[H:]/c[:-H]-1
    for k,x in F.items():
        x=np.asarray(x,dtype=float)
        m1=tr&np.isfinite(x)&np.isfinite(f); m2=ho&np.isfinite(x)&np.isfinite(f)
        if m1.sum()<1000 or m2.sum()<1000: continue
        ic1=spearmanr(x[m1],f[m1]).statistic; ic2=spearmanr(x[m2],f[m2]).statistic
        q=pd.qcut(pd.Series(x[m2]),5,labels=False,duplicates="drop"); fr=pd.Series(f[m2])
        sp=(fr[q==4].mean()-fr[q==0].mean())*1e4
        rows.append(dict(H=lab,k=k,ic1=ic1,ic2=ic2,sp=sp,gl=np.sign(ic1)==np.sign(ic2)))
R=pd.DataFrame(rows)
for _,r in R.reindex(R.sp.abs().sort_values(ascending=False).index).head(12).iterrows():
    mk="" if r.gl else "  <-- Vorzeichen kippt"
    print(f"{r.k:<28}{r.H:>5}{r.ic1:>+11.4f}{r.ic2:>+10.4f}{r.sp:>+13.1f}bp"
          f"{abs(r.sp)/COST_BP:>9.2f}x{mk}")
print(f"\ngleiches Vorzeichen: {R.gl.sum()}/{len(R)} ({R.gl.mean()*100:.0f} %)   "
      f"ueber 16 bp im Holdout: {(R.sp.abs()>COST_BP).sum()}   "
      f"davon vorzeichenstabil: {((R.sp.abs()>COST_BP)&R.gl).sum()}")

print("\n"+"="*96)
print("2. NACH DEM TREFFER: Umkehr oder Fortsetzung? (Bars mit ausgeloester Masse)")
print("="*96)
g=np.log1p(d.getroffen.to_numpy())
sig=g>np.nanpercentile(g[g>0],90) if (g>0).any() else np.zeros(len(g),bool)
ret_vor=np.r_[[np.nan]*12,c[12:]/c[:-12]-1]
print(f"{'Zeitraum':<16}{'n':>7}{'nach 1 h':>12}{'nach 6 h':>12}{'Fortsetzung?':>15}")
for nm,m in (("Suche",tr),("HOLDOUT",ho)):
    s=m&sig&np.isfinite(ret_vor)
    if s.sum()<100: continue
    row=[]
    for H in (12,72):
        f=np.full(len(c),np.nan); f[:-H]=c[H:]/c[:-H]-1
        sel=s&np.isfinite(f)
        # Vorzeichen der vorherigen Bewegung x Folgerendite: >0 = Fortsetzung
        row.append(np.nanmean(np.sign(ret_vor[sel])*f[sel])*1e4)
    print(f"{nm:<16}{s.sum():>7}{row[0]:>+11.1f}bp{row[1]:>+11.1f}bp"
          f"{('Fortsetzung' if row[1]>0 else 'Umkehr'):>15}")

print("\n"+"="*96)
print("3. ALS RISIKOMASS: sagt die Liquidationsmasse die kommende Bewegung an?")
print("="*96)
r1=np.log(d.close).diff()
volf=r1.shift(-288).rolling(288).std()*np.sqrt(288*365)
print(f"{'Merkmal':<30}{'Rang Suche':>13}{'Rang HOLDOUT':>15}")
for k,x in [("Masse gesamt (log)",np.log1p(d.liq_ab+d.liq_be)),
            ("gerade ausgeloest (log)",np.log1p(d.getroffen)),
            ("Abwaerts-Semivol (1 Tag)",r1.where(r1<0,0).rolling(288).std()),
            ("realisierte Vol (1 Tag)",r1.rolling(288).std())]:
    x=pd.Series(np.asarray(x,dtype=float))
    a=pd.DataFrame({"x":x,"y":volf.reset_index(drop=True)}).dropna()
    at=a[a.index.isin(np.where(tr)[0])]; ah=a[a.index.isin(np.where(ho)[0])]
    if len(at)<500 or len(ah)<500: continue
    print(f"{k:<30}{spearmanr(at.x,at.y).statistic:>13.3f}"
          f"{spearmanr(ah.x,ah.y).statistic:>15.3f}")
