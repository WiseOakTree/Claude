"""Was sagt mehr ueber Risiko als die Bollinger-Baender?

Neun Praediktoren gegen drei Zielgroessen, alle auf Tagesbasis,
Training 2021-24, Bewertung im HOLDOUT 2025-26 (echtes Out-of-Sample-R2).
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
D="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT="2025-01-01"; H=5          # 5 Tage voraus
AN=np.sqrt(365)

def daily(sym):
    d=pd.read_csv(D+f"{sym}_1h.csv",index_col=0,parse_dates=True)
    return d.resample("1D").agg({"open":"first","high":"max","low":"min",
                                 "close":"last","volume":"sum"}).dropna()

def predictors(df, sym):
    c,h,l,o,v = df.close,df.high,df.low,df.open,df.volume
    r=np.log(c).diff()
    P={}
    # 1 Bollinger-Breite (die Messlatte)
    m=c.rolling(20).mean(); sd=c.rolling(20).std()
    P["Bollinger-Breite (20,2)"]=4*sd/m
    # 2 realisierte Vol close-to-close
    P["realisierte Vol 20 T"]=r.rolling(20).std()*AN
    # 3 ATR
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    P["ATR(14)/Preis"]=tr.rolling(14).mean()/c*AN
    # 4 Parkinson (Hoch-Tief)
    P["Parkinson (H-T)"]=np.sqrt((np.log(h/l)**2).rolling(20).mean()/(4*np.log(2)))*AN
    # 5 Garman-Klass
    gk=0.5*np.log(h/l)**2-(2*np.log(2)-1)*np.log(c/o)**2
    P["Garman-Klass (OHLC)"]=np.sqrt(gk.rolling(20).mean().clip(lower=0))*AN
    # 6 Rogers-Satchell
    rs=np.log(h/c)*np.log(h/o)+np.log(l/c)*np.log(l/o)
    P["Rogers-Satchell"]=np.sqrt(rs.rolling(20).mean().clip(lower=0))*AN
    # 7 EWMA (RiskMetrics)
    P["EWMA (lambda 0,94)"]=np.sqrt((r**2).ewm(alpha=0.06,adjust=False).mean())*AN
    # 8 HAR: 1 Tag / 1 Woche / 1 Monat
    P["_har1"]=r.abs()*AN; P["_har5"]=r.rolling(5).std()*AN; P["_har22"]=r.rolling(22).std()*AN
    # 9 Volumen-Ueberraschung
    P["Volumen / Ø20"]=v/v.rolling(20).mean()
    # 10 implizite Vol
    try:
        iv=pd.read_csv(D+f"dvol_{sym.upper()}.csv",index_col=0,parse_dates=True).close
        P["DVOL (implizite Vol)"]=iv.resample("1D").last().reindex(df.index).ffill()/100
    except Exception: pass
    return pd.DataFrame(P,index=df.index)

def targets(df):
    c=df.close; r=np.log(c).diff()
    T={}
    T["realisierte Vol 5 T"]=r.shift(-H).rolling(H).std()*AN
    # groesster Rueckgang in den naechsten 5 Tagen
    dd=[]
    a=c.to_numpy()
    for i in range(len(a)):
        w=a[i:i+H+1]
        dd.append((w/np.maximum.accumulate(w)-1).min() if len(w)>1 else np.nan)
    T["max. Rueckgang 5 T"]=-pd.Series(dd,index=c.index)
    # Tag mit -3 % oder schlechter (Kraken-Tageslimit)
    daymin=r.shift(-H).rolling(H).min()
    T["Tag <= -3 % (ja/nein)"]=(daymin<=np.log(0.97)).astype(float)
    return pd.DataFrame(T,index=df.index)

def oos_r2(xtr,ytr,xho,yho):
    """R2 im Holdout mit auf dem Suchzeitraum geschaetzten Koeffizienten."""
    X=np.column_stack([np.ones(len(xtr)),xtr]); b=np.linalg.lstsq(X,ytr,rcond=None)[0]
    p=np.column_stack([np.ones(len(xho)),xho])@b
    return 1-((yho-p)**2).sum()/((yho-yho.mean())**2).sum()

for sym in ("btc","eth"):
    df=daily(sym); P=predictors(df,sym); T=targets(df)
    A=pd.concat([P,T],axis=1).replace([np.inf,-np.inf],np.nan).dropna()
    tr=A.index<SPLIT; ho=A.index>=SPLIT
    print("="*92)
    print(f"{sym.upper()} taeglich -- Out-of-Sample-R² im Holdout 2025-26 "
          f"(Schaetzung auf 2021-24, n={tr.sum()}/{ho.sum()})")
    print("="*92)
    names=[c for c in P.columns if not c.startswith("_")]
    print(f"{'Praediktor':<26}{'Vol 5 T':>11}{'max. Rueckgang':>17}{'Tag <= -3 %':>14}")
    rows=[]
    for n in names:
        vals=[oos_r2(A[n][tr].to_numpy(),A[t][tr].to_numpy(),
                     A[n][ho].to_numpy(),A[t][ho].to_numpy()) for t in T.columns]
        rows.append((n,*vals))
    # HAR als Dreier-Regression
    har=["_har1","_har5","_har22"]
    vals=[oos_r2(A[har][tr].to_numpy(),A[t][tr].to_numpy(),
                 A[har][ho].to_numpy(),A[t][ho].to_numpy()) for t in T.columns]
    rows.append(("HAR (1T/1W/1M kombin.)",*vals))
    if "DVOL (implizite Vol)" in names:
        cmb=["DVOL (implizite Vol)","_har1","_har5","_har22"]
        vals=[oos_r2(A[cmb][tr].to_numpy(),A[t][tr].to_numpy(),
                     A[cmb][ho].to_numpy(),A[t][ho].to_numpy()) for t in T.columns]
        rows.append(("DVOL + HAR",*vals))
    for n,a,b,c_ in sorted(rows,key=lambda x:-x[1]):
        mark=" <-- Messlatte" if n.startswith("Bollinger") else ""
        print(f"{n:<26}{a:>11.3f}{b:>17.3f}{c_:>14.3f}{mark}")
    print()
