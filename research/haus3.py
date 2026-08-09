"""Auf der NATIVEN Frequenz gerechnet (~14 Tage). Alles andere waere
erfunden."""
import warnings; warnings.filterwarnings("ignore")
import json,subprocess
import numpy as np, pandas as pd
S="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad"
body=json.dumps({"type":"vaultDetails",
                 "vaultAddress":"0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"})
r=subprocess.run(["curl","-sS","--max-time","90","-X","POST",
    "-H","Content-Type: application/json","-d",body,
    "https://api.hyperliquid.xyz/info"],capture_output=True)
port=dict(json.loads(r.stdout)["portfolio"])
def reihe(feld):
    x=pd.DataFrame(port["allTime"][feld],columns=["ms","w"])
    x["w"]=x.w.astype(float); x["ts"]=pd.to_datetime(x.ms,unit="ms",utc=True)
    return x.set_index("ts").w.sort_index()
W=reihe("accountValueHistory"); P=reihe("pnlHistory")
D=pd.DataFrame({"w":W,"p":P}).dropna()
D["dt"]=D.index.to_series().diff().dt.total_seconds()/86400
D["r"]=D.p.diff()/D.w.shift(1)
D=D[(D.w.shift(1)>1e6)&np.isfinite(D.r)]
per_jahr=365/D.dt.median()
jahre=(D.index[-1]-D.index[0]).days/365.25
kum=(1+D.r).prod()
print("="*84); print("HLP-VAULT auf nativer Frequenz (~14-Tage-Schritte)"); print("="*84)
print(f"  {len(D)} Beobachtungen ueber {jahre:.2f} Jahre "
      f"(Abstand Median {D.dt.median():.1f} Tage)")
print(f"  Kapital: {D.w.iloc[-1]/1e6:,.1f} Mio $   PnL kumuliert: {D.p.iloc[-1]/1e6:,.1f} Mio $\n")
print(f"  {'Rendite kumuliert':<30}{(kum-1)*100:>+10.1f} %")
print(f"  {'annualisiert':<30}{(kum**(1/jahre)-1)*100:>+10.1f} %")
print(f"  {'Volatilitaet p.a.':<30}{D.r.std()*np.sqrt(per_jahr)*100:>10.1f} %")
print(f"  {'Sharpe':<30}{D.r.mean()/D.r.std()*np.sqrt(per_jahr):>10.2f}")
eq=(1+D.r).cumprod(); dd=eq/eq.cummax()-1
print(f"  {'groesster Rueckgang (14-Tage)':<30}{dd.min()*100:>10.1f} %")
print(f"  {'Perioden im Plus':<30}{(D.r>0).mean()*100:>9.1f} %  "
      f"({(D.r>0).sum()} von {len(D)})")
print(f"  {'schlechteste Periode':<30}{D.r.min()*100:>10.2f} %")
print(f"\n  Jahresrenditen:")
for y,x in D.r.groupby(D.index.year):
    print(f"    {y}: {((1+x).prod()-1)*100:>+7.1f} %   "
          f"({len(x)} Perioden, schlechteste {x.min()*100:+.2f} %)")
print(f"\n  🛑 Die 14-Tage-Aufloesung VERSTECKT Rueckgaenge innerhalb der Periode.")
print(f"     Der wahre maximale Rueckgang liegt hoeher als {dd.min()*100:.1f} %.")

print("\n"+"="*84); print("VERGLEICH DER WEGE (alles annualisiert)"); print("="*84)
f=pd.read_csv(f"{S}/funding.csv"); f["time"]=pd.to_datetime(f.time,utc=True,format="mixed")
f=f.set_index("time").funding.sort_index()
tagf=f.resample("1D").sum().dropna()
rows=[("HLP-Vault (das Haus)", (kum**(1/jahre)-1)*100,
       D.r.std()*np.sqrt(per_jahr)*100, D.r.mean()/D.r.std()*np.sqrt(per_jahr),
       dd.min()*100, "Vault-Ausfall, Smart Contract, Gegenpartei"),
      ("Funding-Carry (delta-neutral)", f.mean()*3*365*100-0.20,
       tagf.std()*np.sqrt(365)*100, tagf.mean()/tagf.std()*np.sqrt(365),
       -0.18, "Liquidation der Short-Seite, Boersenrisiko"),
      ("Volatilitaetspraemie (Projekt)", 13.6*1.85/1.0, 13.6, 1.85, -13.7,
       "Vol-Schub, taegliche Arbeit"),
      ("Marktmachen ohne Rebate", -0.575*1e-4*365*100, np.nan, np.nan, np.nan,
       "garantiertes Minus")]
print(f"  {'Weg':<32}{'Rendite p.a.':>14}{'Vol':>8}{'Sharpe':>8}{'max DD':>9}")
for n,r_,v_,s_,d_,risk in rows:
    print(f"  {n:<32}{r_:>+13.1f} %{v_:>7.1f}%{s_:>8.2f}{d_:>8.1f}%")
print()
for n,_,_,_,_,risk in rows: print(f"  {n:<32} Risiko: {risk}")
