"""Sauber: taegliches Raster, Rendite = Aenderung der kumulierten PnL
geteilt durch das Kapital am Vortag. Nur Zeitraeume mit relevanter Groesse."""
import warnings; warnings.filterwarnings("ignore")
import json,subprocess
import numpy as np, pandas as pd
S="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad"
body=json.dumps({"type":"vaultDetails",
                 "vaultAddress":"0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"})
r=subprocess.run(["curl","-sS","--max-time","90","-X","POST",
    "-H","Content-Type: application/json","-d",body,
    "https://api.hyperliquid.xyz/info"],capture_output=True)
v=json.loads(r.stdout); port=dict(v["portfolio"])
def reihe(key,feld):
    x=pd.DataFrame(port[key][feld],columns=["ms","w"])
    x["w"]=x.w.astype(float)
    x["ts"]=pd.to_datetime(x.ms,unit="ms",utc=True)
    return x.set_index("ts").w.sort_index()
W=reihe("allTime","accountValueHistory"); P=reihe("allTime","pnlHistory")
# taegliches Raster
Wd=W.resample("1D").last().ffill(); Pd=P.resample("1D").last().ffill()
D=pd.DataFrame({"w":Wd,"p":Pd}).dropna()
D["r"]=D.p.diff()/D.w.shift(1)
D=D[D.w.shift(1)>1e6]                     # erst ab 1 Mio $ Kapital
D=D[np.isfinite(D.r)]
print("="*86); print("HLP-VAULT -- DAS HAUS AUF HYPERLIQUID"); print("="*86)
print(f"  ausgewertet ab {D.index[0]:%Y-%m-%d} (Kapital > 1 Mio $), "
      f"{len(D)} Tage")
print(f"  Kapital am Ende: {D.w.iloc[-1]/1e6:,.1f} Mio $   "
      f"kumulierte PnL: {D.p.iloc[-1]/1e6:,.1f} Mio $")
jahre=(D.index[-1]-D.index[0]).days/365.25
kum=(1+D.r).prod()
print(f"\n  {'kumuliert':<28}{(kum-1)*100:>+9.1f} %  ueber {jahre:.2f} Jahre")
print(f"  {'annualisiert':<28}{(kum**(1/jahre)-1)*100:>+9.1f} %")
print(f"  {'Volatilitaet p.a.':<28}{D.r.std()*np.sqrt(365)*100:>9.1f} %")
print(f"  {'Sharpe':<28}{D.r.mean()/D.r.std()*np.sqrt(365):>9.2f}")
eq=(1+D.r).cumprod(); dd=eq/eq.cummax()-1
print(f"  {'groesster Rueckgang':<28}{dd.min()*100:>9.1f} %")
print(f"  {'Anteil Gewinntage':<28}{(D.r>0).mean()*100:>9.1f} %")
print(f"  {'schlechtester Tag':<28}{D.r.min()*100:>9.2f} %")
m=D.r.resample("MS").apply(lambda x:(1+x).prod()-1)
print(f"  {'schlechtester Monat':<28}{m.min()*100:>9.2f} %")
print(f"  {'Monate im Plus':<28}{(m>0).mean()*100:>9.1f} %  ({(m>0).sum()} von {len(m)})")
print(f"\n  Jahresrenditen:")
for y,x in D.r.groupby(D.index.year):
    print(f"    {y}: {((1+x).prod()-1)*100:>+7.1f} %   "
          f"(schlechtester Tag {x.min()*100:+.2f} %)")

print("\n"+"="*86); print("FUNDING-CARRY -- Spot long, Perp short"); print("="*86)
f=pd.read_csv(f"{S}/funding.csv")
f["time"]=pd.to_datetime(f.time,utc=True,format="mixed")
f=f.set_index("time").funding.sort_index()
print(f"  {len(f):,} Zahlungen, {f.index[0].date()} bis {f.index[-1].date()}")
print(f"  mittlere Rate je 8 h: {f.mean()*100:.5f} %  ->  annualisiert "
      f"{f.mean()*3*365*100:+.2f} %")
print(f"  Anteil positiver Zahlungen: {(f>0).mean()*100:.1f} %")
print(f"\n  {'Jahr':<8}{'Funding-Ertrag':>17}{'positiv':>11}{'schlechtester Monat':>22}")
for y,x in f.groupby(f.index.year):
    mm=x.resample("MS").sum()
    print(f"  {y:<8}{x.sum()*100:>+16.2f} %{(x>0).mean()*100:>10.1f} %"
          f"{mm.min()*100:>21.2f} %")
tagf=f.resample("1D").sum().dropna()
print(f"\n  Volatilitaet p.a.: {tagf.std()*np.sqrt(365)*100:.2f} %   "
      f"Sharpe: {tagf.mean()/tagf.std()*np.sqrt(365):.2f}")
print(f"  Nach Kosten (4 Seiten a 5 bp = 0,20 % einmalig je Umschlag):")
print(f"    bei einmaligem Aufbau und Halten: {f.mean()*3*365*100-0.20:+.2f} % p.a.")
