"""Vollstaendige Pruefung der Orderbuch-Imbalance auf 3,5 Jahren Historie."""
import numpy as np, pandas as pd
from scipy import stats

OUT = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/of/"

hist = pd.read_csv(OUT + "depth_feat_hist.csv.gz", index_col=0, parse_dates=True)
d = pd.read_csv(OUT + "bookdepth.csv.gz")
d["timestamp"] = pd.to_datetime(d["timestamp"], utc=True, format="mixed")
piv = d.pivot_table(index="timestamp", columns="percentage", values="notional", aggfunc="sum")
lv = sorted(piv.columns); neg=[c for c in lv if c<0]; pos=[c for c in lv if c>0]
recent = pd.DataFrame(index=piv.index)
for tag, ns in (("1",1),("3",3),("5",5)):
    b = piv[[c for c in neg if abs(c)<=ns]].sum(axis=1)
    a = piv[[c for c in pos if abs(c)<=ns]].sum(axis=1)
    recent[f"imb{tag}"] = (b-a)/(b+a)
recent["liq"] = piv.sum(axis=1)
recent = recent.resample("5min").last()

feat = pd.concat([hist, recent]).sort_index()
feat = feat[~feat.index.duplicated(keep="last")].replace([np.inf,-np.inf], np.nan).dropna()
px = pd.read_csv(OUT+"flow_5m.csv.gz", index_col=0, parse_dates=True)["close"]
m = pd.concat([feat, px.rename("px")], axis=1, sort=True).dropna()
print(f"Gesamt: {len(m):,} Punkte, {len(m)/288:.0f} Tage "
      f"({m.index.min().date()} .. {m.index.max().date()})\n")

def corr_p(ic, n_eff):
    t = ic*np.sqrt(max(n_eff-2,1)/max(1-ic**2,1e-9))
    return 2*(1-stats.t.cdf(abs(t), max(n_eff-2,1)))

print("=" * 92)
print("1) Horizonte -- jetzt mit ausreichender Zahl unabhaengiger Fenster")
print("=" * 92)
print(f"{'Signal':8s} {'Horizont':>9s} {'IC':>7s} {'p korr.':>9s} {'Q5-Q1':>10s} "
      f"{'vs 16bp':>8s} {'n_eff':>7s}")
print("-" * 92)
best = None
for key in ("imb1","imb3","imb5"):
    for bars, lbl in ((48,"4 h"),(288,"1 T"),(576,"2 T"),(864,"3 T"),(1440,"5 T"),(2016,"7 T")):
        fwd = m["px"].pct_change(bars).shift(-bars)
        s = pd.concat([m[key].rename("s"), fwd.rename("f")], axis=1).dropna()
        if len(s) < 5000: continue
        ic,_ = stats.spearmanr(s["s"], s["f"]); n_eff = len(s)/bars
        pa = corr_p(ic, n_eff)
        q = pd.qcut(s["s"],5,labels=False,duplicates="drop")
        sp = (s["f"][q==4].mean()-s["f"][q==0].mean())*1e4
        ok = pa < 0.05 and abs(sp) > 16
        print(f"{key:8s} {lbl:>9s} {ic:+7.3f} {pa:9.3f} {sp:+7.1f} bp {abs(sp)/16:7.2f}x "
              f"{n_eff:7.0f}{'  <<< haelt' if ok else ''}")
        if ok and (best is None or abs(sp) > abs(best[3])): best = (key,bars,ic,sp,pa)

if best is None:
    print("\nKeine Kombination ueberlebt beide Huerden (Signifikanz UND Kostenschwelle).")
else:
    key, bars, ic, sp, pa = best
    print(f"\n{'='*92}\n2) Out-of-Sample-Kontrolle: {key}, {bars*5//60} h\n{'='*92}")
    fwd = m["px"].pct_change(bars).shift(-bars)
    s = pd.concat([m[key].rename("s"), fwd.rename("f")], axis=1).dropna()
    h = len(s)//2
    for nm, part in (("1. Haelfte", s.iloc[:h]), ("2. Haelfte", s.iloc[h:])):
        i2,_ = stats.spearmanr(part["s"], part["f"])
        q = pd.qcut(part["s"],5,labels=False,duplicates="drop")
        sp2 = (part["f"][q==4].mean()-part["f"][q==0].mean())*1e4
        print(f"  {nm} ({part.index.min().date()}..{part.index.max().date()}): "
              f"IC {i2:+.3f}  Q5-Q1 {sp2:+.1f} bp  p {corr_p(i2, len(part)/bars):.3f}")

    print(f"\n{'='*92}\n3) Als Strategie gegen die Challenge-Regeln\n{'='*92}")
    COST = 16e-4
    sig = m[key].shift(1)
    z = (sig - sig.rolling(288*30).mean())/sig.rolling(288*30).std()
    ret5 = m["px"].pct_change().fillna(0)
    print(f"{'Variante':34s} {'Rendite':>9s} {'DD':>7s} {'Pass':>7s}")
    print("-"*60)
    for thr in (0.0, 0.5, 1.0):
        for lev in (1.0, 2.0):
            w = pd.Series(np.where(z > thr, lev, np.where(z < -thr, -lev, 0.0)), index=m.index)
            w = w.reindex(m.index).ffill().fillna(0)
            turn = w.diff().abs().fillna(0)
            r = (w*ret5 - COST*turn).resample("1D").sum().dropna()
            a = r.to_numpy(); passed=tot=0; R=[];DD=[]
            for st in range(0, len(a)-90):
                wnd=a[st:st+90]; eq=np.cumprod(1+wnd)
                dd=(eq/np.maximum.accumulate(eq)-1).min()
                passed += (eq[-1]-1>=.10 and dd>=-.06 and wnd.min()>-.03); tot+=1
                R.append(eq[-1]-1); DD.append(-dd)
            if tot:
                print(f"{f'|z| > {thr}, Hebel {lev:.0f}x':34s} {np.median(R)*100:+8.1f}% "
                      f"{np.median(DD)*100:6.1f}% {passed/tot*100:6.1f}%")
