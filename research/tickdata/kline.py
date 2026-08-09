"""5-Minuten-Kerzen aus demselben Archiv, passend zu den Metrics."""
import os,subprocess,zipfile,sys
import pandas as pd
T="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/tick"
B="https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/5m"
COLS=["open_time","open","high","low","close","volume","close_time","qav",
      "trades","tbbav","tbqav","ignore"]
out=[]
for m in pd.date_range(sys.argv[1],sys.argv[2],freq="MS").strftime("%Y-%m"):
    z=f"{T}/k.zip"
    r=subprocess.run(["curl","-sS","-f","--max-time","120","-o",z,
                      f"{B}/BTCUSDT-5m-{m}.zip"],capture_output=True)
    if r.returncode!=0: print(f"  {m}: n/a",flush=True); continue
    with zipfile.ZipFile(z) as zf:
        df=pd.read_csv(zf.open(zf.namelist()[0]),header=None,names=COLS)
    os.remove(z); out.append(df); print(f"  {m}: {len(df)}",flush=True)
K=pd.concat(out,ignore_index=True)
K=K[K.open_time.apply(lambda v: str(v).isdigit())]
K["ts"]=pd.to_datetime(K.open_time.astype("int64"),unit="ms",utc=True)
K[["ts","open","high","low","close","volume","trades","tbbav"]].to_csv(f"{T}/k5.csv",index=False)
print(f"FERTIG: {len(K):,} Bars")
