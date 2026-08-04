"""Breiteres Universum fuer den Cross-Sectional-Test, 1h."""
import sys; sys.path.insert(0,"/home/user/Claude/src")
from prop_backtester import binance
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
COINS=["ADAUSDT","DOGEUSDT","LINKUSDT","AVAXUSDT","DOTUSDT","LTCUSDT",
       "BCHUSDT","ATOMUSDT","BNBUSDT","TRXUSDT"]
for s in COINS:
    try:
        d=binance.download_klines(s,"1h",start="2021-03",progress=False)
        d.to_csv(V+s[:-4].lower()+"_1h.csv")
        print(f"{s[:-4]:6s} {len(d):6d} Bars", flush=True)
    except Exception as e:
        print(f"{s[:-4]:6s} FEHLER {e}", flush=True)
print("FERTIG")
