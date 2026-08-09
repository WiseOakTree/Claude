"""Cross-Sectional Relative Strength -- relativ statt gerichtet.

Der strukturelle Unterschied zu allem Bisherigen: Die Wette ist nicht "Kurs
steigt", sondern "A laeuft besser als B". Marktrichtung faellt heraus -- genau
der Hebel, der das Drawdown-Problem angreifen koennte.

Suchzeitraum 2021-03..2024-12, Holdout ab 2025-01.
"""
import sys, glob, os, warnings, itertools
sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
COST=16e-4; SPLIT=pd.Timestamp("2025-01-01",tz="UTC")
EXCL={"btc_recent"}

def universe():
    cols={}
    for f in sorted(glob.glob(V+"*_1h.csv")):
        nm=os.path.basename(f)[:-7]
        if nm in EXCL: continue
        s=pd.read_csv(f,index_col=0,parse_dates=True)["close"]
        cols[nm.upper()]=s
    px=pd.DataFrame(cols).sort_index()
    return px.dropna(thresh=int(len(px.columns)*0.8))

def backtest(px, lookback, rebal, k, mode):
    """mode: 'ls' = long/short, 'lo' = long-only (Rest in Cash)."""
    ret=px.pct_change()
    mom=px.pct_change(lookback)
    # nur zu Rebalancing-Zeitpunkten neu gewichten, Signal vom VORBAR
    sig=mom.shift(1)
    idx=px.index
    reb=np.zeros(len(idx),dtype=bool); reb[::rebal]=True
    W=pd.DataFrame(0.0,index=idx,columns=px.columns)
    cur=pd.Series(0.0,index=px.columns)
    for i in range(len(idx)):
        if reb[i]:
            row=sig.iloc[i].dropna()
            if len(row)>=2*k:
                rank=row.rank(ascending=False)
                cur=pd.Series(0.0,index=px.columns)
                top=rank.nsmallest(k).index; bot=rank.nlargest(k).index
                cur[top]=0.5/k
                if mode=="ls": cur[bot]=-0.5/k
        W.iloc[i]=cur.values
    turn=W.diff().abs().sum(axis=1).fillna(0)
    pnl=(W.shift(1)*ret).sum(axis=1) - COST*turn
    return pnl.fillna(0)

def metrics(s, lev=1.0):
    s=(s*lev).dropna()
    d=((1+s).resample("1D").prod()-1).dropna()
    a=d.to_numpy()
    if len(a)<200: return dict(pass_rate=0,ann=0,vol=0,dd=0,sharpe=0)
    eq=np.cumprod(1+a); dd=(eq/np.maximum.accumulate(eq)-1).min()
    ann=(eq[-1]**(365/len(a))-1)*100; vol=a.std()*np.sqrt(365)*100
    p=f=cn=0
    for st in range(0,len(a)-1):
        e=1.0; done=None
        for i in range(st,min(st+365,len(a))):
            r=a[i]
            if r<-.03: done="f";break
            e*=(1+r)
            if e<=.94: done="f";break
            if e-1>=.10: done="p";break
        if done=="p": p+=1
        elif done=="f": f+=1
        else: cn+=1
    tot=p+f+cn
    return dict(pass_rate=p/tot*100 if tot else 0, ann=ann, vol=vol,
                dd=-dd*100, sharpe=ann/vol if vol>0 else 0)

px=universe()
print(f"Universum: {len(px.columns)} Coins -- {', '.join(px.columns)}")
print(f"Zeitraum: {px.index.min().date()} .. {px.index.max().date()}, {len(px)} Stunden\n")
S=px[px.index<SPLIT]

rows=[]
for lb,rb,k,mode in itertools.product((12,24,48,72),(4,8,12,24),(1,2,3),("ls","lo")):
    if k*2>len(px.columns): continue
    m=metrics(backtest(S,lb,rb,k,mode))
    rows.append(dict(lookback=lb,rebal=rb,k=k,mode=mode,**m))
R=pd.DataFrame(rows)
R.to_csv("/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/oc/xsect_search.csv",index=False)

print("="*84); print(f"SUCHZEITRAUM -- {len(R)} Kombinationen"); print("="*84)
print(f"  Anteil mit positiver Jahresrendite: {(R.ann>0).mean()*100:.0f} %")
print(f"  Median Jahresrendite: {R.ann.median():+.1f} %   Median Sharpe: {R.sharpe.median():+.2f}")
print(f"  Median Drawdown: {R.dd.median():.1f} %   Median Pass-Rate: {R.pass_rate.median():.1f} %\n")
for mode,lab in (("ls","Long/Short (marktneutral)"),("lo","Long-only (Rest Cash)")):
    g=R[R["mode"]==mode]
    print(f"  {lab:28s} Median p.a. {g.ann.median():+6.1f} %  "
          f"DD {g.dd.median():5.1f} %  Sharpe {g.sharpe.median():+5.2f}  "
          f"Pass {g.pass_rate.median():5.1f} %")
print("\nBeste 8 nach Pass-Rate:")
print(R.nlargest(8,"pass_rate")[["mode","lookback","rebal","k","ann","vol","dd","sharpe","pass_rate"]]
      .to_string(index=False,float_format=lambda v:f"{v:.2f}"))
