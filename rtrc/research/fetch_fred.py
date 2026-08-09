"""Datenbeschaffung fuer den Cross-Market-Test. Nur oeffentliche Quellen."""
import os, io, subprocess
import pandas as pd
D="/home/user/Claude/rtrc/data"
os.makedirs(D,exist_ok=True)
SERIEN={
 # Aktienindizes
 "aktien":{"SP500":"S&P 500","NASDAQCOM":"Nasdaq Composite","NIKKEI225":"Nikkei 225"},
 # Devisen (USD je Einheit bzw. Einheit je USD -- Richtung wird normiert)
 "fx":{"DEXUSEU":"EUR/USD","DEXUSUK":"GBP/USD","DEXUSAL":"AUD/USD",
       "DEXJPUS":"USD/JPY","DEXCAUS":"USD/CAD","DEXSZUS":"USD/CHF",
       "DEXMXUS":"USD/MXN","DEXKOUS":"USD/KRW","DEXINUS":"USD/INR",
       "DEXBZUS":"USD/BRL","DEXSDUS":"USD/SEK","DEXNOUS":"USD/NOK",
       "DEXCHUS":"USD/CNY"},
 # Rohstoffe
 "rohstoffe":{"DCOILWTICO":"WTI Rohoel","DCOILBRENTEU":"Brent Rohoel",
              "DHHNGSP":"Erdgas Henry Hub"},
 # Zinsen (Renditen -- werden ueber Duration in Preise umgerechnet)
 "zinsen":{"DGS2":"2J Treasury","DGS10":"10J Treasury","DGS30":"30J Treasury"},
}
alle={}
for klasse,d in SERIEN.items():
    for sid,name in d.items():
        r=subprocess.run(["curl","-sS","--max-time","60",
            f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"],
            capture_output=True)
        try:
            df=pd.read_csv(io.BytesIO(r.stdout))
        except Exception as e:
            print(f"  ✗ {sid}: {e}",flush=True); continue
        df.columns=["date","v"]
        df["v"]=pd.to_numeric(df.v,errors="coerce")
        df["date"]=pd.to_datetime(df.date,utc=True)
        df=df.dropna().set_index("date")
        if len(df)<500: print(f"  ✗ {sid}: nur {len(df)} Werte",flush=True); continue
        df.to_csv(f"{D}/{klasse}_{sid}.csv")
        alle[sid]=(klasse,name,len(df),df.index[0].date(),df.index[-1].date())
        print(f"  ✓ {klasse:<10}{sid:<16}{name:<20}{len(df):>7} Werte  "
              f"{df.index[0].date()} .. {df.index[-1].date()}",flush=True)
print(f"\n{len(alle)} Reihen geladen.")
pd.DataFrame([(k,)+v for k,v in alle.items()],
    columns=["id","klasse","name","n","von","bis"]).to_csv(f"{D}/uebersicht.csv",index=False)
