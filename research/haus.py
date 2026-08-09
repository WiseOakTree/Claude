"""Auf der Seite des Hauses stehen -- die zwei Wege, die ein Privatkonto
wirklich gehen kann:

  1. HLP-Vault: Kapital in die Gegenseite aller Trader geben
  2. Funding-Carry: Spot kaufen, Perp shorten, Finanzierungsrate kassieren
"""
import warnings; warnings.filterwarnings("ignore")
import json,subprocess
import numpy as np, pandas as pd
S="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad"

body=json.dumps({"type":"vaultDetails",
                 "vaultAddress":"0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"})
r=subprocess.run(["curl","-sS","--max-time","90","-X","POST",
    "-H","Content-Type: application/json","-d",body,
    "https://api.hyperliquid.xyz/info"],capture_output=True)
v=json.loads(r.stdout)
port=dict(v["portfolio"])
hist=port.get("allTime",{}).get("accountValueHistory") or port["month"]["accountValueHistory"]
pnl =port.get("allTime",{}).get("pnlHistory")
H=pd.DataFrame(hist,columns=["ms","wert"]); H["wert"]=H.wert.astype(float)
H["ts"]=pd.to_datetime(H.ms,unit="ms",utc=True); H=H.set_index("ts").sort_index()
P=pd.DataFrame(pnl,columns=["ms","pnl"]); P["pnl"]=P.pnl.astype(float)
P["ts"]=pd.to_datetime(P.ms,unit="ms",utc=True); P=P.set_index("ts").sort_index()

print("="*88); print("1. HLP-VAULT -- DAS HAUS AUF HYPERLIQUID"); print("="*88)
print(f"  Zeitraum: {H.index[0]:%Y-%m-%d} bis {H.index[-1]:%Y-%m-%d}  "
      f"({(H.index[-1]-H.index[0]).days} Tage)")
print(f"  Kapital heute: {H.wert.iloc[-1]/1e6:,.1f} Mio $")
print(f"  kumulierte PnL: {P.pnl.iloc[-1]/1e6:,.1f} Mio $")
# Rendite je Einheit Kapital: dPnL / Kapital
g=pd.DataFrame({"wert":H.wert,"pnl":P.pnl.reindex(H.index).ffill()}).dropna()
g["dp"]=g.pnl.diff()
g["r"]=g.dp/g.wert.shift(1)
tag=g.r.resample("1D").sum().dropna()
jahre=(tag.index[-1]-tag.index[0]).days/365.25
kum=(1+tag).prod()
print(f"\n  Rendite auf das eingesetzte Kapital:")
print(f"    kumuliert ueber {jahre:.2f} Jahre: {(kum-1)*100:+.1f} %")
print(f"    annualisiert:                  {(kum**(1/jahre)-1)*100:+.1f} %")
print(f"    Volatilitaet p.a.:             {tag.std()*np.sqrt(365)*100:.1f} %")
print(f"    Sharpe:                        {tag.mean()/tag.std()*np.sqrt(365):.2f}")
eq=(1+tag).cumprod(); dd=(eq/eq.cummax()-1)
print(f"    groesster Rueckgang:           {dd.min()*100:.1f} %")
print(f"    Anteil Gewinntage:             {(tag>0).mean()*100:.1f} %")
print(f"    schlechtester Tag:             {tag.min()*100:.2f} %")
print(f"    schlechtester Monat:           "
      f"{tag.resample('MS').sum().min()*100:.2f} %")

print("\n"+"="*88); print("2. FUNDING-CARRY -- Spot long, Perp short, Rate kassieren")
print("="*88)
f=pd.read_csv(f"{S}/funding.csv",parse_dates=["time"]).set_index("time").funding
print(f"  Beobachtungen: {len(f):,}  ({f.index[0]:%Y-%m-%d} bis {f.index[-1]:%Y-%m-%d})")
print(f"  mittlere Rate je 8 h: {f.mean()*100:.5f} %  ->  "
      f"annualisiert {f.mean()*3*365*100:+.2f} %")
print(f"  Anteil positiver Zahlungen: {(f>0).mean()*100:.1f} %")
jahr=f.resample("YS").sum()*100
print(f"\n  {'Jahr':<8}{'Funding-Ertrag':>18}{'Anteil positiv':>18}")
for y,v_ in jahr.items():
    sel=f[f.index.year==y.year]
    print(f"  {y.year:<8}{v_:>+17.2f} %{(sel>0).mean()*100:>17.1f} %")
tagf=f.resample("1D").sum().dropna()
print(f"\n  Volatilitaet der Carry p.a.: {tagf.std()*np.sqrt(365)*100:.2f} %")
print(f"  Sharpe der reinen Carry:     {tagf.mean()/tagf.std()*np.sqrt(365):.2f}")
print(f"  schlechtester Monat:         {f.resample('MS').sum().min()*100:+.2f} %")
print(f"\n  ABZUEGE, die in dieser Zahl noch NICHT stecken:")
print(f"    Spot kaufen + Perp shorten + spaeter aufloesen: 4 Seiten a ~5 bp = ~0,20 %")
print(f"    Kapitalbindung: Sicherheiten auf beiden Seiten")
print(f"    Liquidationsrisiko der Short-Seite bei starkem Anstieg")
