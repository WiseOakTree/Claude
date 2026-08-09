"""Open Interest und Positionierung -- die Rohdaten der Liquidations-Heatmap.
5-Minuten-Aufloesung aus dem Binance-Archiv, ~11 KB je Tag."""
import os,subprocess,zipfile,sys
import pandas as pd
T="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/tick"
B="https://data.binance.vision/data/futures/um/daily/metrics/BTCUSDT"
out=[]
days=pd.date_range(sys.argv[1],sys.argv[2],freq="D").strftime("%Y-%m-%d")
for d in days:
    z=f"{T}/m.zip"
    r=subprocess.run(["curl","-sS","-f","--max-time","60","-o",z,
                      f"{B}/BTCUSDT-metrics-{d}.zip"],capture_output=True)
    if r.returncode!=0: continue
    try:
        with zipfile.ZipFile(z) as zf:
            out.append(pd.read_csv(zf.open(zf.namelist()[0])))
    except Exception: pass
    os.remove(z)
    if len(out)%60==0: print(f"  {d}  ({len(out)} Tage)",flush=True)
M=pd.concat(out,ignore_index=True)
M["ts"]=pd.to_datetime(M.create_time,utc=True)
M=M.sort_values("ts").drop_duplicates("ts")
M.to_csv(f"{T}/metrics.csv",index=False)
print(f"FERTIG: {len(M):,} Bars, {M.ts.min():%Y-%m-%d} bis {M.ts.max():%Y-%m-%d}")
