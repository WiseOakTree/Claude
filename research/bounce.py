"""Der S/R-Bounce ist mit t = -3,28 signifikant NEGATIV. Sein Gegenteil waere
damit der staerkste Einzeleffekt des Projekts. Das braucht Kontrollen:

  1. Haelt es auf anderen Assets?
  2. Bonferroni ueber alle Tests dieser Runde
  3. Ist es nur der Ausbruch unter anderem Namen?
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/home/user/Claude/src")
from prop_backtester import levels as LV
D="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC"); COST=8e-4; H=48

def n_eff(starts,hold,N):
    conc=np.zeros(N)
    for i in starts: conc[i:i+hold]+=1
    u=[]
    for i in starts:
        seg=conc[i:i+hold]; seg=seg[seg>0]
        u.append((1.0/seg).mean() if len(seg) else 0.0)
    return max(np.sum(u),2.0)

def studie(sym):
    df=pd.read_csv(D+f"{sym}_1h.csv",index_col=0,parse_dates=True)
    by=LV.build_levels(df)
    c=df.close.to_numpy(); N=len(c)
    f=np.full(N,np.nan); f[:-H]=c[H:]/c[:-H]-1
    out={}
    for art,fn in (("Ausbruch",LV.breakout_events),("Bounce",LV.bounce_events)):
        ev=fn(by,df,min_touch=6)
        r=[(t,d,df.index[t],d*f[t]-2*COST) for t,d,_,_ in ev if np.isfinite(f[t])]
        out[art]=(pd.DataFrame(r,columns=["i","d","ts","ret"]),N)
    return out

print("="*98)
print("GEGEN-BOUNCE (Bounce-Signal, aber in die GEGENRICHTUNG gehandelt)")
print("="*98)
print(f"{'Markt':<7}{'Zeitraum':<15}{'n':>6}{'Effekt':>12}{'t NEU':>9}{'n_eff':>8}")
alle=[]
for sym in ("btc","eth","sol","bnb","xrp","ada"):
    try: st=studie(sym)
    except Exception as e: print(f"{sym}: {e}"); continue
    B,N=st["Bounce"]
    for nm,m in (("Suche 21-24",B.ts<SPLIT),("HOLDOUT 25-26",B.ts>=SPLIT)):
        s=B[m]
        if len(s)<40: continue
        x=-s.ret.to_numpy()-0        # Gegenrichtung; Kosten stecken schon drin
        ne=n_eff(s.i.to_numpy(),H,N)
        t=x.mean()/(x.std(ddof=1)/np.sqrt(ne))
        print(f"{sym.upper():<7}{nm:<15}{len(s):>6}{x.mean()*1e4:>+11.1f} bp{t:>9.2f}{ne:>8.0f}")
        alle.append((sym,nm,x.mean()*1e4,t))
    print()

A=pd.DataFrame(alle,columns=["sym","zeit","bp","t"])
ho=A[A.zeit.str.startswith("HOLD")]
print(f"Holdout: {len(ho)} Maerkte, davon positiv {(ho.bp>0).sum()}, "
      f"Median {ho.bp.median():+.1f} bp, Median t {ho.t.median():.2f}")
from scipy import stats
print(f"Bonferroni ueber 12 Tests dieser Runde: t muss > "
      f"{stats.norm.ppf(1-0.05/12/2):.2f} liegen fuer p<0,05")

print("\n"+"="*98)
print("IST ES NUR DER AUSBRUCH UNTER ANDEREM NAMEN? (BTC, Ueberschneidung)")
print("="*98)
st=studie("btc"); A_,N=st["Ausbruch"]; B_,_=st["Bounce"]
sa=set(A_.i); sb=set(B_.i)
print(f"  Ausbruchs-Ereignisse: {len(sa)}   Bounce-Ereignisse: {len(sb)}")
print(f"  gemeinsame Bars: {len(sa&sb)} ({len(sa&sb)/max(len(sb),1)*100:.1f} % der Bounces)")
# Richtungsuebereinstimmung auf gemeinsamen Bars
ga=A_.set_index("i").d; gb=B_.set_index("i").d
gem=sorted(sa&sb)
if gem:
    ueb=(ga.loc[gem].to_numpy()==-gb.loc[gem].to_numpy()).mean()*100
    print(f"  davon Ausbruchsrichtung = GEGEN-Bounce-Richtung: {ueb:.0f} %")
# Bounces ohne gleichzeitigen Ausbruch
rein=B_[~B_.i.isin(sa)]
for nm,m in (("Suche 21-24",rein.ts<SPLIT),("HOLDOUT 25-26",rein.ts>=SPLIT)):
    s=rein[m]
    if len(s)<40: continue
    x=-s.ret.to_numpy(); ne=n_eff(s.i.to_numpy(),H,N)
    print(f"  Gegen-Bounce OHNE Ausbruch  {nm:<15}{len(s):>5}{x.mean()*1e4:>+9.1f} bp"
          f"{x.mean()/(x.std(ddof=1)/np.sqrt(ne)):>8.2f}")
