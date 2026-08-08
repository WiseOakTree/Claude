"""Aktuelle Ertragslage statt Dreijahresdurchschnitt.

Der Fehler, den dieses Skript korrigiert: +37,3 % p.a. war der Mittelwert
ueber die gesamte Historie. Fuer eine Entscheidung HEUTE zaehlt der
aktuelle Lauf -- und der steht bei null.
"""
import json,subprocess
import numpy as np, pandas as pd
S="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad"
body=json.dumps({"type":"vaultDetails",
                 "vaultAddress":"0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"})
r=subprocess.run(["curl","-sS","--max-time","60","-X","POST",
    "-H","Content-Type: application/json","-d",body,
    "https://api.hyperliquid.xyz/info"],capture_output=True)
v=json.loads(r.stdout); port=dict(v["portfolio"])
print(f"Gemeldeter APR im API-Feld: {v.get('apr')}  = {float(v.get('apr',0))*100:.2f} %\n")
print(f"{'Fenster':<12}{'Punkte':>8}{'Dauer':>10}{'PnL':>16}{'Ø Kapital':>16}{'annualisiert':>15}")
for k in ("day","week","month","allTime"):
    if k not in port: continue
    W=pd.DataFrame(port[k]["accountValueHistory"],columns=["ms","w"])
    P=pd.DataFrame(port[k]["pnlHistory"],columns=["ms","p"])
    W["w"]=W.w.astype(float); P["p"]=P.p.astype(float)
    ts=pd.to_datetime(W.ms,unit="ms",utc=True)
    tage=(ts.iloc[-1]-ts.iloc[0]).total_seconds()/86400
    if tage<=0: continue
    dp=P.p.iloc[-1]-P.p.iloc[0]; kap=W.w.mean()
    print(f"{k:<12}{len(W):>8}{tage:>9.1f}d{dp:>15,.0f} ${kap/1e6:>14,.1f}M"
          f"{((1+dp/kap)**(365/tage)-1)*100:>+14.1f} %")

W=pd.DataFrame(port["allTime"]["accountValueHistory"],columns=["ms","w"])
P=pd.DataFrame(port["allTime"]["pnlHistory"],columns=["ms","p"])
W["w"]=W.w.astype(float); P["p"]=P.p.astype(float)
D=pd.DataFrame({"ts":pd.to_datetime(W.ms,unit="ms",utc=True),"w":W.w,"p":P.p}).set_index("ts")
D["r"]=D.p.diff()/D.w.shift(1); D=D[(D.w.shift(1)>1e6)&np.isfinite(D.r)]
print("\nJahreswerte, korrekt annualisiert:")
for y,x in D.r.groupby(D.index.year):
    tage=(x.index[-1]-x.index[0]).days; kum=(1+x).prod()
    print(f"  {y}: kumuliert {((kum-1)*100):>+7.1f} % ueber {tage:>3} Tage"
          f"  -> annualisiert {(kum**(365/max(tage,1))-1)*100:>+7.1f} %")

print("\n" + "="*66)
print("FUNDING-CARRY: die letzten Monate einzeln")
print("="*66)
f=pd.read_csv(f"{S}/funding.csv"); f["time"]=pd.to_datetime(f.time,utc=True,format="mixed")
f=f.set_index("time").funding.sort_index()
m=f.resample("MS").sum()*100; ann=f.resample("MS").mean()*3*365*100
print(f"{'Monat':<12}{'Monatsertrag':>15}{'annualisiert':>16}{'Anteil positiv':>17}")
for d,val in m.tail(14).items():
    sel=f[(f.index.year==d.year)&(f.index.month==d.month)]
    print(f"{d:%Y-%m}{'':<5}{val:>+14.3f} %{ann[d]:>+15.2f} %{(sel>0).mean()*100:>16.1f} %")
print(f"\n  letzte 30 Tage: {f.tail(90).mean()*3*365*100:+.2f} %   "
      f"letzte 90 Tage: {f.tail(270).mean()*3*365*100:+.2f} %   "
      f"gesamt: {f.mean()*3*365*100:+.2f} %")
