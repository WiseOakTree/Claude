"""Die drei Indikatoren als INFORMATIONSQUELLE, nicht als Signal.

Frage: Wenn ich den Wert kenne -- wie sehr aendert sich meine Erwartung?
Gemessen als Transinformation (in Bit) gegen eine gemischte Kontrolle,
getrennt fuer RICHTUNG und fuer VOLATILITAET.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from msb import bars4h, macd, stoch, boll, SPLIT

def feats(df):
    c=df.close
    line,sig,hist=macd(c); K,Dl=stoch(df); lo,mid,up,pctb=boll(c)
    width=(up-lo)/mid
    return pd.DataFrame({
        "MACD-Histogramm": hist/c,
        "MACD-Linie":      line/c,
        "Stochastik %K":   K,
        "Stoch %K-%D":     K-Dl,
        "Bollinger %B":    pctb,
        "Bollinger-Breite":width,
    }, index=df.index)

def mi(x, y, nx=5, ny=2):
    """Transinformation in Bit, beide Seiten in Quantilkoerbe."""
    m=np.isfinite(x)&np.isfinite(y)
    x,y=x[m],y[m]
    if len(x)<200: return np.nan
    try:
        bx=pd.qcut(x,nx,labels=False,duplicates="drop")
        by=pd.qcut(y,ny,labels=False,duplicates="drop")
    except Exception: return np.nan
    t=pd.crosstab(bx,by).to_numpy().astype(float); t/=t.sum()
    px=t.sum(1,keepdims=True); py=t.sum(0,keepdims=True)
    with np.errstate(divide="ignore",invalid="ignore"):
        v=t*np.log2(t/(px*py))
    return np.nansum(v)

def fwd(df,h):
    c=df.close.to_numpy(); f=np.full(len(c),np.nan); f[:-h]=c[h:]/c[:-h]-1
    return f

HOLD=30   # 5 Tage
rng=np.random.default_rng(11)

for sym in ("btc","eth"):
    df=bars4h(sym); F=feats(df); r=fwd(df,HOLD)
    tr=df.index<SPLIT; ho=df.index>=SPLIT
    print("="*84)
    print(f"{sym.upper()} 4h -- Transinformation ueber 5 Tage voraus (Bit)")
    print("="*84)
    print(f"{'Indikator':<20}{'RICHTUNG':>12}{'Kontrolle':>11}{'|  VOLATILITAET':>16}{'Kontrolle':>11}{'| Holdout Vol':>14}")
    for name in F.columns:
        x=F[name].to_numpy()
        # Richtung: Vorzeichen der Rendite (2 Koerbe)
        d_tr=mi(x[tr],r[tr],5,2)
        # Volatilitaet: Betrag der Rendite (2 Koerbe)
        v_tr=mi(x[tr],np.abs(r[tr]),5,2)
        v_ho=mi(x[ho],np.abs(r[ho]),5,2)
        # Kontrolle: Indikator zirkulaer verschoben, 100 Laeufe
        cd=[];cv=[]
        for _ in range(100):
            k=int(rng.integers(200,len(x)-200)); xs=np.roll(x,k)
            cd.append(mi(xs[tr],r[tr],5,2)); cv.append(mi(xs[tr],np.abs(r[tr]),5,2))
        print(f"{name:<20}{d_tr:>12.4f}{np.nanmedian(cd):>11.4f}{v_tr:>16.4f}"
              f"{np.nanmedian(cv):>11.4f}{v_ho:>14.4f}")
    print()
