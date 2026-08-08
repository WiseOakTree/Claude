"""Der Rainbow Chart: logarithmische Regression ueber die BTC-Historie,
Baender als Vielfache. Gurus lesen daraus 'kaufen' und 'verkaufen'.

Der entscheidende Punkt: Die Regression wird auf der GANZEN Historie
gefittet -- auch auf Daten, die zum Entscheidungszeitpunkt in der Zukunft
lagen. Genau das teste ich gegen die kausale Variante.
"""
import warnings; warnings.filterwarnings("ignore")
import os,subprocess,zipfile
import numpy as np, pandas as pd
from scipy.stats import spearmanr
T="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/rb"
os.makedirs(T,exist_ok=True)
COLS=["open_time","open","high","low","close","volume","close_time","qav",
      "trades","tbbav","tbqav","ignore"]
if not os.path.exists(f"{T}/btc_d.csv"):
    out=[]
    for m in pd.date_range("2017-08-01","2026-07-01",freq="MS").strftime("%Y-%m"):
        z=f"{T}/z.zip"
        r=subprocess.run(["curl","-sS","-f","--max-time","90","-o",z,
          f"https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1d/BTCUSDT-1d-{m}.zip"],
          capture_output=True)
        if r.returncode!=0: continue
        with zipfile.ZipFile(z) as zf:
            d=pd.read_csv(zf.open(zf.namelist()[0]),header=None,names=COLS)
        os.remove(z)
        d=d[d.open_time.apply(lambda v:str(v).isdigit())].copy()
        ot=d.open_time.astype("int64")
        d["ts"]=pd.to_datetime(ot,unit="us" if ot.max()>1e14 else "ms",utc=True)
        out.append(d[["ts","close"]])
    K=pd.concat(out).drop_duplicates("ts").sort_values("ts")
    K.to_csv(f"{T}/btc_d.csv",index=False)
K=pd.read_csv(f"{T}/btc_d.csv",parse_dates=["ts"]).set_index("ts")
K["close"]=pd.to_numeric(K.close)
print(f"BTC taeglich: {len(K):,} Tage, {K.index[0]:%Y-%m-%d} bis {K.index[-1]:%Y-%m-%d}")

tage=np.arange(1,len(K)+1)
lx=np.log(tage); ly=np.log(K.close.to_numpy())

# --- Variante A: der uebliche Rainbow (Fit ueber ALLES) ---
b,a=np.polyfit(lx,ly,1)
resA=ly-(a+b*lx)
bandA=(resA-resA.mean())/resA.std()

# --- Variante B: kausal (Fit nur mit Daten bis t) ---
bandB=np.full(len(K),np.nan)
MIN=365*2
for t in range(MIN,len(K)):
    bb,aa=np.polyfit(lx[:t],ly[:t],1)
    r=ly[:t]-(aa+bb*lx[:t])
    bandB[t]=((ly[t]-(aa+bb*lx[t]))-r.mean())/r.std()

print(f"\nRegression ueber alles:  log(Preis) = {a:.3f} + {b:.3f} * log(Tag)")
print(f"Korrelation Band A (ueber alles) <-> Band B (kausal): "
      f"{np.corrcoef(bandA[MIN:],bandB[MIN:])[0,1]:+.3f}")

def test(band,lab,H):
    c=K.close.to_numpy(); f=np.full(len(c),np.nan); f[:-H]=c[H:]/c[:-H]-1
    m=np.isfinite(band)&np.isfinite(f)
    x=band[m]; y=f[m]
    rho=spearmanr(x,y).statistic
    q=pd.qcut(pd.Series(x),5,labels=False,duplicates="drop")
    sp=(pd.Series(y)[q==4].mean()-pd.Series(y)[q==0].mean())*100
    return rho,sp,m.sum(),pd.Series(y)[q==0].mean()*100,pd.Series(y)[q==4].mean()*100

print("\n"+"="*96)
print("VORHERSAGEKRAFT: Bandposition -> kuenftige Rendite")
print("="*96)
print(f"{'Variante':<34}{'Horizont':>10}{'n':>7}{'Rho':>9}"
      f"{'unterstes 20 %':>17}{'oberstes 20 %':>16}")
for lab,band in (("A  Fit ueber ALLES (ueblich)",bandA),
                 ("B  kausal, nur Vergangenheit",bandB)):
    for H,hl in ((30,"1 Monat"),(90,"3 Monate"),(365,"1 Jahr")):
        rho,sp,n,lo,hi=test(band,lab,H)
        print(f"{lab:<34}{hl:>10}{n:>7}{rho:>+9.3f}{lo:>+16.1f}%{hi:>+15.1f}%")
    print()

print("="*96)
print("DER TEST, DER ES ENTSCHEIDET: nur der Zeitraum, den die kausale")
print("Variante ueberhaupt beurteilen kann (ab 2019-08), beide nebeneinander")
print("="*96)
c=K.close.to_numpy()
for H,hl in ((90,"3 Monate"),(365,"1 Jahr")):
    f=np.full(len(c),np.nan); f[:-H]=c[H:]/c[:-H]-1
    m=np.isfinite(bandB)&np.isfinite(f)
    for lab,band in (("Fit ueber alles",bandA),("kausal",bandB)):
        x=band[m]; y=f[m]
        q=pd.qcut(pd.Series(x),5,labels=False,duplicates="drop")
        lo=pd.Series(y)[q==0].mean()*100; hi=pd.Series(y)[q==4].mean()*100
        print(f"  {hl:<11}{lab:<20}Rho {spearmanr(x,y).statistic:>+6.3f}   "
              f"unten {lo:>+7.1f} %   oben {hi:>+7.1f} %   Spanne {lo-hi:>+7.1f} Pp")
    print()
