"""Teil 2: Warum die Konfluenz-Lesart leer ausging, und der Gittersuchlauf
(bestes von N) gegen den Holdout."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, itertools, sys
sys.path.insert(0, "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from msb import bars4h, signals, evaluate, COST_SIDE, SPLIT

btc = bars4h("btc"); tr = btc[btc.index < SPLIT]; ho = btc[btc.index >= SPLIT]

print("="*78); print("Warum 'reversion' leer blieb: Haeufigkeit der Bedingungen (BTC 4h, 2021-24)")
print("="*78)
from msb import macd, stoch, boll
c = tr.close
line, sig, hist = macd(c); K, Dl = stoch(tr); lo, mid, up, pctb = boll(c)
conds = {"Kurs <= unteres Band": (c <= lo), "Stoch < 20": (K < 20),
         "MACD-Hist. steigt": (hist > hist.shift(1))}
for k, v in conds.items():
    print(f"  {k:<24} {v.sum():>5} Bars  ({v.mean()*100:>5.1f} %)")
tri = (c <= lo) & (K < 20) & (hist > hist.shift(1))
pair = (c <= lo) & (K < 20)
print(f"  {'zwei davon':<24} {pair.sum():>5} Bars  ({pair.mean()*100:>5.1f} %)")
print(f"  {'ALLE DREI':<24} {tri.sum():>5} Bars  ({tri.mean()*100:>5.1f} %)")
print(f"\n  -> {tri.sum()} Long-Signale in 3,8 Jahren = {tri.sum()/3.83:.1f} pro Jahr")

print("\n" + "="*78); print("Konfluenz mit gelockerten Schwellen (Stoch<30, %B<0.1)")
print("="*78)
for os_, thr in [(20,0.0),(25,0.05),(30,0.10),(35,0.15)]:
    L = (pctb < thr) & (K < os_) & (hist > hist.shift(1))
    S = (pctb > 1-thr) & (K > 100-os_) & (hist < hist.shift(1))
    for hold in (6, 30):
        r = evaluate(tr, L.fillna(False), S.fillna(False), hold)
        if r: print(f"  Stoch<{os_} %B<{thr:.2f}  {hold*4:>4}h  n={r['n']:>4}  "
                    f"{r['bp']:>+7.1f} bp  t={r['t']:>5.2f}")

print("\n" + "="*78)
print("GITTERSUCHE: bestes von N auf dem Suchzeitraum -> dann Holdout 2025-26")
print("="*78)
grid = list(itertools.product(
    [(12,26,9),(8,21,5),(19,39,9),(5,35,5)],   # MACD
    [(14,3),(9,3),(21,5)],                      # Stochastik
    [(20,2.0),(20,2.5),(50,2.0)],               # Bollinger
    [20,30],                                    # oversold
    ["trend","reversion"],
    [6,12,30]))                                 # Haltedauer
rows=[]
for (mf,ms,msig),(sk,sd),(bp_,bn),os_,rd,hold in grid:
    L,S = signals(tr, rd, mf,ms,msig, sk,sd, bp_,bn, os_, 100-os_)
    r = evaluate(tr,L,S,hold)
    if r is None or r["n"]<30: continue
    rows.append(dict(mf=mf,ms=ms,msig=msig,sk=sk,sd=sd,bp_=bp_,bn=bn,os_=os_,
                     rd=rd,hold=hold,**r))
res = pd.DataFrame(rows).sort_values("bp",ascending=False)
print(f"gueltige Varianten: {len(res)}   davon positiv: {(res.bp>0).sum()} "
      f"({(res.bp>0).mean()*100:.0f} %)")
print(f"Median ueber alle Varianten: {res.bp.median():+.1f} bp/Trade\n")
print("Beste 8 im Suchzeitraum:")
print(res.head(8)[["rd","mf","ms","sk","bp_","bn","os_","hold","n","bp","t"]]
      .to_string(index=False,float_format=lambda v:f"{v:.2f}"))

print("\nDieselben 8 im HOLDOUT 2025-01 .. 2026-06:")
out=[]
for _,b in res.head(8).iterrows():
    L,S = signals(ho, b.rd, int(b.mf),int(b.ms),int(b.msig), int(b.sk),int(b.sd),
                  int(b.bp_), b.bn, b.os_, 100-b.os_)
    r = evaluate(ho,L,S,int(b.hold))
    out.append(dict(rd=b.rd, hold=int(b.hold), such_bp=b.bp,
                    ho_n=r["n"] if r else 0, ho_bp=r["bp"] if r else np.nan,
                    ho_t=r["t"] if r else np.nan))
o=pd.DataFrame(out); print(o.to_string(index=False,float_format=lambda v:f"{v:.2f}"))
print(f"\nMittel Suchzeitraum: {o.such_bp.mean():+.1f} bp   "
      f"Mittel Holdout: {o.ho_bp.mean():+.1f} bp")
