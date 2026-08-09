import urllib.request, pandas as pd, io, time
S={"SP500":"Aktien S&P 500","NASDAQCOM":"Aktien Nasdaq","DJIA":"Aktien Dow",
   "WILL5000IND":"Aktien Gesamtmarkt","VIXCLS":"Volatilitaet VIX",
   "DCOILWTICO":"Rohoel WTI","DCOILBRENTEU":"Rohoel Brent","DHHNGSP":"Erdgas",
   "DEXUSEU":"FX EUR/USD","DEXJPUS":"FX USD/JPY","DEXUSUK":"FX GBP/USD",
   "DEXCAUS":"FX USD/CAD","DEXCHUS":"FX USD/CNY","DEXSZUS":"FX USD/CHF",
   "DTWEXBGS":"Dollar-Index","DGS10":"Rendite 10J","DGS2":"Rendite 2J",
   "BAMLH0A0HYM2":"Hochzins-Spread","DEXUSAL":"FX AUD/USD","DEXKOUS":"FX USD/KRW",
   "DEXMXUS":"FX USD/MXN","DEXBZUS":"FX USD/BRL","DEXINUS":"FX USD/INR",
   "DEXNOUS":"FX USD/NOK","DEXSDUS":"FX USD/SEK","DEXSFUS":"FX USD/ZAR"}
got={}
for k,name in S.items():
    try:
        r=urllib.request.urlopen(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={k}",timeout=60).read()
        d=pd.read_csv(io.BytesIO(r))
        d.columns=["date","v"]
        d["v"]=pd.to_numeric(d["v"],errors="coerce")
        d=d.dropna()
        d["date"]=pd.to_datetime(d["date"])
        if len(d)>2000:
            d.to_csv(f"fred_{k}.csv",index=False); got[k]=(name,len(d),d.date.min(),d.date.max())
    except Exception as e: print("fehler",k,str(e)[:50])
    time.sleep(0.2)
print(f"{len(got)} Reihen geladen\n")
for k,(n,l,a,b) in got.items():
    print(f"  {k:14s} {n:22s} {l:6d} Tage  {a:%Y-%m} .. {b:%Y-%m}")
