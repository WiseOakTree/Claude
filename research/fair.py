"""Fairness-Check: Sind -128,9 bp auf BTC in 38 Trades ungewoehnlich, oder
ist das die normale Streuung eines so kurzen Fensters?"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/home/user/Claude/src")
from prop_backtester import levels as LV
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
COST=8e-4; H=48
df=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
by=LV.build_levels(df); c=df.close.to_numpy(); N=len(c)
f=np.full(N,np.nan); f[:-H]=c[H:]/c[:-H]-1
A=np.array([d*f[t]-2*COST for t,d,_,_ in LV.breakout_events(by,df,min_touch=6)
            if np.isfinite(f[t])])
B=np.array([-f[t]-2*COST for t,d,_,_ in LV.bounce_events(by,df,min_touch=6)
            if d==1 and np.isfinite(f[t])])
rng=np.random.default_rng(1)
print("="*84)
print("Verteilung zusammenhaengender Bloecke aus der HISTORIE (BTC 2021-2026)")
print("="*84)
for x,lab,n_neu,beob in ((A,"S/R-Ausbruch",38,-128.9),(B,"Gegen-Bounce short",21,-115.7)):
    bl=[x[i:i+n_neu].mean()*1e4 for i in range(0,len(x)-n_neu)]
    bl=np.array(bl)
    p=(bl<=beob).mean()
    print(f"\n  {lab} -- Bloecke aus {n_neu} aufeinanderfolgenden Trades (n={len(bl)})")
    print(f"    Median {np.median(bl):>+7.1f} bp   5-95 %: {np.percentile(bl,5):+.0f} .. "
          f"{np.percentile(bl,95):+.0f} bp")
    print(f"    beobachtet im frischen Zeitraum: {beob:>+7.1f} bp")
    print(f"    Anteil historischer Bloecke, die SCHLECHTER waren: {p*100:.1f} %")
    print(f"    -> {'im normalen Streubereich' if p>0.05 else 'ungewoehnlich schlecht'}")

print("\n"+"="*84)
print("Und der eigentliche Punkt: die ACHT FRISCHEN MAERKTE ueber die volle Historie")
print("="*84)
print("  Dort sind es keine 38 Trades, sondern tausende -- und dort ist das")
print("  Ergebnis eindeutig. Der kurze Zeitraum ist nur die Zugabe.")
