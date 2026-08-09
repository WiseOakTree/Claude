"""Teil 2: Indikatorstudien, VWAP, Volume Profile, Volatilitaetspraemie."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from msb import bars4h, signals
from vwap import build as vwbuild
D="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC"); COST=8e-4

def n_eff(starts,hold,N):
    conc=np.zeros(N)
    for i in starts: conc[i:i+hold]+=1
    u=[]
    for i in starts:
        seg=conc[i:i+hold]; seg=seg[seg>0]
        u.append((1.0/seg).mean() if len(seg) else 0.0)
    return max(np.sum(u),2.0)

def zeile(label,zeit,starts,rets,hold,N):
    x=np.asarray(rets,dtype=float)
    if len(x)<15: return
    ne=n_eff(np.asarray(starts),hold,N)
    ta=x.mean()/(x.std(ddof=1)/np.sqrt(max(len(x)/hold,2)))
    tn=x.mean()/(x.std(ddof=1)/np.sqrt(ne))
    print(f"  {label:<32}{zeit:<14}{len(x):>5}{x.mean()*1e4:>+9.1f} bp"
          f"{ta:>8.2f}{tn:>9.2f}{ne:>8.0f}")
KOPF=(f"  {'Befund':<32}{'Zeitraum':<14}{'n':>5}{'Effekt':>12}{'t ALT':>8}"
      f"{'t NEU':>9}{'n_eff':>8}")

print("="*100); print("3. MACD + STOCHASTIK + BOLLINGER, alle Lesarten (4h)"); print("="*100)
print(KOPF)
for sym in ("btc","eth"):
    df=bars4h(sym); cc=df.close.to_numpy(); NN=len(cc)
    for rd in ("macd_only","stoch_only","boll_only","trend"):
        for HH,hl in ((6,"1T"),(30,"5T")):
            ff=np.full(NN,np.nan); ff[:-HH]=cc[HH:]/cc[:-HH]-1
            L,S=signals(df,rd)
            d=np.where(L.to_numpy(),1,np.where(S.to_numpy(),-1,0))
            ii=np.where((d!=0)&np.isfinite(ff))[0]
            R=pd.DataFrame({"i":ii,"ts":df.index[ii],"ret":d[ii]*ff[ii]-2*COST})
            for nm,m in (("Suche",R.ts<SPLIT),("HOLDOUT",R.ts>=SPLIT)):
                s=R[m]; zeile(f"{sym.upper()} {rd} {hl}",nm,s.i.to_numpy(),
                              s.ret.to_numpy(),HH,NN)
    print()

print("="*100); print("4. VWAP-KREUZUNG (4h)"); print("="*100)
print(KOPF)
for sym in ("btc","eth"):
    d=vwbuild(sym); cc=d.close.to_numpy(); NN=len(cc); HH=30
    ff=np.full(NN,np.nan); ff[:-HH]=cc[HH:]/cc[:-HH]-1
    for col,lab in (("vwap_d","Tages"),("vwap_w","Wochen"),("vwap_r50","roll50")):
        up=(d.close>d[col])&(d.close.shift(1)<=d[col].shift(1))
        dn=(d.close<d[col])&(d.close.shift(1)>=d[col].shift(1))
        sg=np.where(up,1,np.where(dn,-1,0))
        ii=np.where((sg!=0)&np.isfinite(ff))[0]
        R=pd.DataFrame({"i":ii,"ts":d.index[ii],"ret":sg[ii]*ff[ii]-2*COST})
        for nm,m in (("Suche",R.ts<SPLIT),("HOLDOUT",R.ts>=SPLIT)):
            s=R[m]; zeile(f"{sym.upper()} VWAP {lab}",nm,s.i.to_numpy(),
                          s.ret.to_numpy(),HH,NN)
    print()

print("="*100); print("5. VOLATILITAETSPRAEMIE -- ueberlappt sie ueberhaupt?"); print("="*100)
iv=pd.read_csv(D+"dvol_BTC.csv",index_col=0,parse_dates=True).close
iv=iv.resample("1D").last().dropna()/100
px=pd.read_csv(D+"btc_1h.csv",index_col=0,parse_dates=True).close.resample("1D").last()
a=pd.DataFrame({"iv":iv,"px":px}).dropna()
r=np.log(a.px).diff()
rv=r.rolling(30).std().shift(-30)*np.sqrt(365)      # realisiert, 30 Tage voraus
vrp=(a.iv-rv).dropna()
print(f"  Beobachtungen (taeglich, 30-Tage-Fenster): {len(vrp)}")
print(f"  mittlere Praemie: {vrp.mean()*100:+.2f} Vol-Punkte")
t_naiv=vrp.mean()/(vrp.std(ddof=1)/np.sqrt(len(vrp)))
t_alt =vrp.mean()/(vrp.std(ddof=1)/np.sqrt(len(vrp)/30))
ne=n_eff(np.arange(len(vrp)),30,len(vrp)+30)
t_neu =vrp.mean()/(vrp.std(ddof=1)/np.sqrt(ne))
print(f"  t naiv (ohne Korrektur):        {t_naiv:>7.2f}")
print(f"  t ALT (n/30, so berichtet):     {t_alt:>7.2f}")
print(f"  t NEU (Einzigartigkeit):        {t_neu:>7.2f}   n_eff = {ne:.0f}")
print(f"\n  -> Hier feuert an JEDEM Tag ein Fenster, die Ueberlappung ist maximal.")
print(f"     Alt und neu liegen deshalb dicht beieinander: die Korrektur war")
print(f"     an dieser Stelle richtig angewandt.")
