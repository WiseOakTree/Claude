"""Abschluss: Stabilitaet des 4h-Signals und Zerfall des 3-Tage-Befunds."""
import numpy as np, pandas as pd
from scipy import stats
OUT = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/of/"
hist = pd.read_csv(OUT+"depth_feat_hist.csv.gz", index_col=0, parse_dates=True)
d = pd.read_csv(OUT+"bookdepth.csv.gz"); d["timestamp"]=pd.to_datetime(d["timestamp"],utc=True,format="mixed")
piv = d.pivot_table(index="timestamp",columns="percentage",values="notional",aggfunc="sum")
lv=sorted(piv.columns); neg=[c for c in lv if c<0]; pos=[c for c in lv if c>0]
rec = pd.DataFrame(index=piv.index)
for tag,ns in (("1",1),("3",3),("5",5)):
    b=piv[[c for c in neg if abs(c)<=ns]].sum(axis=1); a=piv[[c for c in pos if abs(c)<=ns]].sum(axis=1)
    rec[f"imb{tag}"]=(b-a)/(b+a)
rec["liq"]=piv.sum(axis=1); rec=rec.resample("5min").last()
feat=pd.concat([hist,rec]).sort_index(); feat=feat[~feat.index.duplicated(keep="last")]
feat=feat.replace([np.inf,-np.inf],np.nan).dropna()
px=pd.read_csv(OUT+"flow_5m.csv.gz",index_col=0,parse_dates=True)["close"]
m=pd.concat([feat,px.rename("px")],axis=1,sort=True).dropna()
def cp(ic,n): 
    t=ic*np.sqrt(max(n-2,1)/max(1-ic**2,1e-9)); return 2*(1-stats.t.cdf(abs(t),max(n-2,1)))

print("="*78); print("Das 4-Stunden-Signal (imb5) ueber die Jahre"); print("="*78)
fwd=m["px"].pct_change(48).shift(-48)
s=pd.concat([m["imb5"].rename("s"),fwd.rename("f")],axis=1).dropna()
for yr,g in s.groupby(s.index.year):
    if len(g)<5000: continue
    ic,_=stats.spearmanr(g["s"],g["f"]); q=pd.qcut(g["s"],5,labels=False,duplicates="drop")
    sp=(g["f"][q==4].mean()-g["f"][q==0].mean())*1e4
    print(f"  {yr}: IC {ic:+.3f}   Q5-Q1 {sp:+6.1f} bp   p {cp(ic,len(g)/48):.4f}   n={len(g):,}")
ic,_=stats.spearmanr(s["s"],s["f"]); q=pd.qcut(s["s"],5,labels=False,duplicates="drop")
sp=(s["f"][q==4].mean()-s["f"][q==0].mean())*1e4
print(f"  ---- gesamt: IC {ic:+.3f}, Q5-Q1 {sp:+.1f} bp, p {cp(ic,len(s)/48):.6f}")

print("\n"+"="*78); print("Der 3-Tage-Befund: was aus den +110 bp wurde"); print("="*78)
fwd3=m["px"].pct_change(864).shift(-864)
s3=pd.concat([m["imb3"].rename("s"),m["imb5"].rename("s5"),fwd3.rename("f")],axis=1).dropna()
recent=s3[s3.index>="2025-09-01"]; older=s3[s3.index<"2025-09-01"]
for nm,g in (("nur 2025-09..2026-06 (Erstbefund)",recent),("2023-01..2025-08 (neu)",older),("gesamt",s3)):
    for k in ("s","s5"):
        ic,_=stats.spearmanr(g[k],g["f"]); q=pd.qcut(g[k],5,labels=False,duplicates="drop")
        sp=(g["f"][q==4].mean()-g["f"][q==0].mean())*1e4
        lbl = "imb3" if k=="s" else "imb5"
        print(f"  {nm:34s} {lbl}: IC {ic:+.3f}  Q5-Q1 {sp:+7.1f} bp  p {cp(ic,len(g)/864):.3f}")
