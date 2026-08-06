"""Die harte Pruefung des neunten Filters.
 1) Signifikanz mit Ueberlappungskorrektur, nur auf ungesehenen Daten
 2) Ist die Efficiency Ratio nur ein Stellvertreter fuer VOLATILITAET?
 3) Bonferroni fuer neun geprueften Filter
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import levels
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC")

def trades(asset):
    d=pd.read_csv(V+f"{asset}_1h.csv",index_col=0,parse_dates=True)
    c=d["close"].to_numpy(); hi=d["high"].to_numpy(); lo=d["low"].to_numpy(); n=len(d)
    r=np.diff(np.log(c),prepend=np.log(c[0]))
    atr=pd.Series(np.maximum(hi-lo,np.abs(hi-np.roll(c,1)))).rolling(14).mean().to_numpy()
    by=levels.build_levels(d,width=8,tol_atr=0.5,max_age=1000)
    out=[]; busy=-1
    for (t,dr,tc,lv) in levels.breakout_events(by,d,min_touch=6):
        if t<busy or t+48>=n or t<200: continue
        busy=t+48
        seg=r[t-168:t]
        er=abs(seg.sum())/np.abs(seg).sum() if np.abs(seg).sum()>0 else 0
        rv=np.std(r[t-168:t])*np.sqrt(24*365)          # realisierte Vol
        out.append((d.index[t],dr*(c[t+48]/c[t]-1)*1e4-16.0, er, rv, atr[t]/c[t]))
    return pd.DataFrame(out,columns=["ts","pnl","er","rv","atrp"])

B=trades("btc")
thr=B[B.ts<SPLIT].er.quantile(1/3)     # Schwelle nur aus BTC-Suchzeitraum
print("="*88)
print("1) SIGNIFIKANZ auf ungesehenen Daten (BTC-Holdout + ETH/SOL/XRP komplett)")
print("="*88)
parts=[B[B.ts>=SPLIT]]+[trades(a) for a in ["eth","sol","xrp"]]
A=pd.concat(parts,ignore_index=True)
lo=A[A.er<=thr].pnl.to_numpy(); hi=A[A.er>thr].pnl.to_numpy()
t_,p_=stats.ttest_ind(lo,hi)
# Ueberlappungskorrektur: Trades ueberlappen nicht (eine Position), aber
# aufeinanderfolgende teilen das Regime -> konservativ n/2
neff=len(lo)/2
t_corr=(lo.mean()-hi.mean())/np.sqrt(hi.var()/ (len(hi)/2) + lo.var()/neff)
p_corr=2*(1-stats.norm.cdf(abs(t_corr)))
print(f"  ruhig   n={len(lo):>4d}  Ø {lo.mean():>+8.1f} bp")
print(f"  unruhig n={len(hi):>4d}  Ø {hi.mean():>+8.1f} bp")
print(f"  Differenz {lo.mean()-hi.mean():+.1f} bp   p roh {p_:.4f}   "
      f"p ueberlappungskorrigiert {p_corr:.4f}")
print(f"  Bonferroni fuer 9 geprueften Filter: p = {min(p_corr*9,1):.4f}   "
      f"{'HAELT' if p_corr*9<0.05 else 'FAELLT DURCH'}")

print()
print("="*88)
print("2) Ist das nur VOLATILITAET unter anderem Namen?")
print("="*88)
print(f"  Korrelation Efficiency Ratio <-> realisierte Vol: "
      f"{np.corrcoef(A.er,A.rv)[0,1]:+.3f}")
print(f"  Korrelation Efficiency Ratio <-> ATR/Preis:       "
      f"{np.corrcoef(A.er,A.atrp)[0,1]:+.3f}")
print()
vthr=B[B.ts<SPLIT].rv.quantile(1/3)
print(f"  {'Aufteilung':34s} {'n':>5s} {'Ø netto':>10s}")
print("  "+"-"*52)
for lab,m in [("nur niedrige VOL", A.rv<=vthr),("nur hohe VOL", A.rv>vthr),
              ("nur ruhige PHASE (ER)", A.er<=thr),("nur unruhige PHASE", A.er>thr),
              ("ruhige Phase UND niedrige Vol", (A.er<=thr)&(A.rv<=vthr)),
              ("ruhige Phase, HOHE Vol", (A.er<=thr)&(A.rv>vthr)),
              ("unruhige Phase, niedrige Vol", (A.er>thr)&(A.rv<=vthr))]:
    s=A[m.to_numpy()].pnl
    if len(s)>=10: print(f"  {lab:34s} {len(s):>5d} {s.mean():>+9.1f}bp")
print("""
  -> Wenn "ruhige Phase, HOHE Vol" immer noch gut ist, misst die
     Efficiency Ratio etwas ANDERES als Volatilitaet.""")

print()
print("="*88)
print("3) Quantils-Monotonie: steigt der Effekt gleichmaessig?")
print("="*88)
A2=A.copy(); A2["q"]=pd.qcut(A2.er,5,labels=False)
print(f"  {'Quintil (ruhig -> unruhig)':30s} {'n':>5s} {'Ø netto':>10s}")
print("  "+"-"*48)
for q in range(5):
    s=A2[A2.q==q].pnl
    print(f"  {'Q'+str(q+1):30s} {len(s):>5d} {s.mean():>+9.1f}bp")
sp=stats.spearmanr(A2.q,A2.pnl)
print(f"\n  Spearman-Rangkorrelation: {sp.correlation:+.3f}  p={sp.pvalue:.3f}")
