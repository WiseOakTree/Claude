"""Frische 1h-Kerzen: Zeitraum NACH dem Ende aller bisherigen Daten."""
import os,subprocess,zipfile,sys
import pandas as pd
T="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/fresh"
os.makedirs(T,exist_ok=True)
COLS=["open_time","open","high","low","close","volume","close_time","qav",
      "trades","tbbav","tbqav","ignore"]
def konv(df):
    df=df[df.open_time.apply(lambda v:str(v).isdigit())].copy()
    ot=df.open_time.astype("int64")
    einheit="us" if ot.max()>1e14 else "ms"   # Binance stellte auf Mikrosekunden um
    df["open_time"]=pd.to_datetime(ot,unit=einheit,utc=True)
    return df

def hol(sym,monate,tage):
    out=[]
    for m in monate:
        z=f"{T}/z.zip"
        r=subprocess.run(["curl","-sS","-f","--max-time","120","-o",z,
          f"https://data.binance.vision/data/spot/monthly/klines/{sym}/1h/{sym}-1h-{m}.zip"],
          capture_output=True)
        if r.returncode!=0: continue
        with zipfile.ZipFile(z) as zf:
            out.append(konv(pd.read_csv(zf.open(zf.namelist()[0]),header=None,names=COLS)))
        os.remove(z)
    for d in tage:
        z=f"{T}/z.zip"
        r=subprocess.run(["curl","-sS","-f","--max-time","120","-o",z,
          f"https://data.binance.vision/data/spot/daily/klines/{sym}/1h/{sym}-1h-{d}.zip"],
          capture_output=True)
        if r.returncode!=0: continue
        with zipfile.ZipFile(z) as zf:
            out.append(konv(pd.read_csv(zf.open(zf.namelist()[0]),header=None,names=COLS)))
        os.remove(z)
    if not out: return None
    K=pd.concat(out,ignore_index=True)
    K=K.sort_values("open_time").drop_duplicates("open_time").set_index("open_time")
    return K[["open","high","low","close","volume"]].astype(float)

MON=["2026-07"]
TAGE=pd.date_range("2026-08-01","2026-08-07").strftime("%Y-%m-%d").tolist()
for sym in ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT",
            "ATOMUSDT","AVAXUSDT","BCHUSDT","DOGEUSDT","DOTUSDT","LINKUSDT",
            "LTCUSDT","TRXUSDT"]:
    d=hol(sym,MON,TAGE)
    if d is None: print(f"  {sym}: nicht verfuegbar",flush=True); continue
    d.to_csv(f"{T}/{sym.replace('USDT','').lower()}_neu.csv")
    print(f"  {sym}: {len(d)} Bars  {d.index[0]:%Y-%m-%d} bis {d.index[-1]:%Y-%m-%d}",flush=True)
