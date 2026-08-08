"""VORWAERTSTEST nach der am 2026-08-08 festgelegten Spezifikation.

Test 1: acht Maerkte, fuer diese Regeln nie benutzt (volle Historie)
Test 2: Zeitraum 2026-07-01 bis 2026-08-07 -- liegt HINTER allen bisherigen
        Daten, auf 14 Maerkten
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys, os
sys.path.insert(0,"/home/user/Claude/src")
from prop_backtester import levels as LV
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
F="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/fresh/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC"); FRISCH=pd.Timestamp("2026-07-01",tz="UTC")
COST=8e-4; H=48

def n_eff(st,hold,N):
    conc=np.zeros(N)
    for i in st: conc[i:i+hold]+=1
    u=[]
    for i in st:
        s=conc[i:i+hold]; s=s[s>0]; u.append((1.0/s).mean() if len(s) else 0)
    return max(np.sum(u),2.0)

def lade(sym, mit_frisch=False):
    d=pd.read_csv(V+f"{sym}_1h.csv",index_col=0,parse_dates=True)
    if mit_frisch and os.path.exists(F+f"{sym}_neu.csv"):
        n=pd.read_csv(F+f"{sym}_neu.csv",index_col=0,parse_dates=True)
        d=pd.concat([d[d.index<n.index[0]],n])
    return d

def signale(df):
    by=LV.build_levels(df); c=df.close.to_numpy(); N=len(c)
    f=np.full(N,np.nan); f[:-H]=c[H:]/c[:-H]-1
    A=[(t,d,df.index[t],d*f[t]-2*COST)
       for t,d,_,_ in LV.breakout_events(by,df,min_touch=6) if np.isfinite(f[t])]
    B=[(t,-1,df.index[t],-f[t]-2*COST)          # nur Unterstuetzungs-Bounce -> SHORT
       for t,d,_,_ in LV.bounce_events(by,df,min_touch=6) if d==1 and np.isfinite(f[t])]
    return (pd.DataFrame(A,columns=["i","d","ts","ret"]),
            pd.DataFrame(B,columns=["i","d","ts","ret"]), N)

def st(s,N):
    if len(s)<10: return None
    x=s.ret.to_numpy(); ne=n_eff(s.i.to_numpy(),H,N)
    return x.mean()*1e4, x.mean()/(x.std(ddof=1)/np.sqrt(ne)), len(x)

FRISCHE=["atom","avax","bch","doge","dot","link","ltc","trx"]
print("="*94)
print("TEST 1: ACHT MAERKTE, FUER DIESE REGELN NIE BENUTZT (volle Historie)")
print("="*94)
print(f"{'Markt':<7}{'':<3}{'Ausbruch Suche':>18}{'Ausbruch HOLDOUT':>20}"
      f"{'GegenBounce Suche':>20}{'GegenBounce HOLD':>20}")
pool={"A_tr":[],"A_ho":[],"B_tr":[],"B_ho":[]}
zeilen=[]
for sym in FRISCHE:
    A,B,N=signale(lade(sym))
    r=[]
    for df_,key in ((A,"A"),(B,"B")):
        for nm,m in (("tr",df_.ts<SPLIT),("ho",df_.ts>=SPLIT)):
            s=df_[m]; o=st(s,N)
            r.append(o)
            if o: pool[f"{key}_{nm}"].append(s.ret.to_numpy())
    fmt=lambda o: f"{o[0]:>+9.1f}bp(t{o[1]:>5.2f})" if o else f"{'--':>18}"
    print(f"{sym.upper():<10}"+"".join(fmt(x) for x in r))
    zeilen.append((sym,*[x[0] if x else np.nan for x in r]))

Z=pd.DataFrame(zeilen,columns=["sym","A_tr","A_ho","B_tr","B_ho"])
print()
for key,lab in (("A","S/R-Ausbruch"),("B","Gegen-Bounce short")):
    for nm,zt in (("tr","Suche 21-24"),("ho","HOLDOUT 25-26")):
        x=np.concatenate(pool[f"{key}_{nm}"])
        pos=(Z[f"{key}_{nm}"]>0).sum(); ges=Z[f"{key}_{nm}"].notna().sum()
        print(f"  {lab:<20}{zt:<15}gepoolt {x.mean()*1e4:>+7.1f} bp   "
              f"positiv in {pos}/{ges} Maerkten")

print("\n"+"="*94)
print("TEST 2: ZEITRAUM 2026-07-01 BIS 2026-08-07 -- hinter allen bisherigen Daten")
print("="*94)
ALLE=["btc","eth","sol","bnb","xrp","ada"]+FRISCHE
print(f"{'Markt':<8}{'Ausbruch n':>12}{'bp':>10}{'GegenBounce n':>16}{'bp':>10}")
pa=[]; pb=[]; za=[]; zb=[]
for sym in ALLE:
    try: A,B,N=signale(lade(sym,mit_frisch=True))
    except Exception as e: print(f"{sym}: {e}"); continue
    a=A[A.ts>=FRISCH]; b=B[B.ts>=FRISCH]
    print(f"{sym.upper():<8}{len(a):>12}{(a.ret.mean()*1e4 if len(a) else np.nan):>+10.1f}"
          f"{len(b):>16}{(b.ret.mean()*1e4 if len(b) else np.nan):>+10.1f}")
    if len(a): pa.append(a.ret.to_numpy()); za.append(a.ret.mean())
    if len(b): pb.append(b.ret.to_numpy()); zb.append(b.ret.mean())
PA=np.concatenate(pa) if pa else np.array([]); PB=np.concatenate(pb) if pb else np.array([])
print()
if len(PA): print(f"  S/R-Ausbruch       gepoolt {PA.mean()*1e4:>+7.1f} bp ueber {len(PA)} Trades   "
                  f"positiv in {sum(np.array(za)>0)}/{len(za)} Maerkten")
if len(PB): print(f"  Gegen-Bounce short gepoolt {PB.mean()*1e4:>+7.1f} bp ueber {len(PB)} Trades   "
                  f"positiv in {sum(np.array(zb)>0)}/{len(zb)} Maerkten")
