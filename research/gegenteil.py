"""Zwei Fragen zu genau dieser Situation:
 1) Sagt ein frueher Rueckstand etwas ueber das 48-Stunden-Ergebnis?
 2) Was bringt es, das Signal systematisch UMZUDREHEN?
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import levels
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
d=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
c=d["close"].to_numpy(); n=len(d)
by=levels.build_levels(d,width=8,tol_atr=0.5,max_age=1000)
ev=levels.breakout_events(by,d,min_touch=6)
tr=[]; busy=-1
for (t,dr,tc,lv) in ev:
    if t<busy: continue
    if t+48>=n: continue
    busy=t+48
    tr.append((t,dr))
print("="*84)
print(f"FRAGE 1: Sagt ein frueher Rueckstand das Endergebnis voraus?  ({len(tr)} Trades)")
print("="*84)
print(f"  {'nach':>6s} {'im Minus':>10s} {'davon am Ende PLUS':>20s} {'Ø Endergebnis':>15s} "
      f"{'gegen alle Trades':>18s}")
print("  "+"-"*72)
alle=np.array([dr*(c[t+48]/c[t]-1) for t,dr in tr])*1e4
for h in [1,3,6,12,24]:
    sub=[(dr*(c[t+h]/c[t]-1), dr*(c[t+48]/c[t]-1)) for t,dr in tr]
    early=np.array([a for a,b in sub]); final=np.array([b for a,b in sub])
    m=early<0
    print(f"  {h:>4d}h {m.mean()*100:>9.0f}% {(final[m]>0).mean()*100:>19.1f}% "
          f"{final[m].mean()*1e4:>+14.1f}bp {(final>0).mean()*100:>17.1f}%")
print(f"\n  Zum Vergleich: alle Trades {(alle>0).mean():.1%} positiv, Ø {alle.mean():+.1f} bp")
h=6
early=np.array([dr*(c[t+h]/c[t]-1) for t,dr in tr]); final=alle/1e4
r=np.corrcoef(early,final)[0,1]
print(f"  Korrelation frueher Stand (6h) <-> Endergebnis: {r:+.3f}  "
      f"(erklaert {r*r*100:.1f} % der Varianz)")

print()
print("="*84)
print("FRAGE 2: Was bringt es, das Signal umzudrehen?")
print("="*84)
COST=8.0
print(f"  {'Variante':28s} {'Ø je Trade':>12s} {'Trefferquote':>13s} {'p-Wert':>9s}")
print("  "+"-"*66)
for name,sign in [("Signal folgen",1),("Signal UMDREHEN",-1)]:
    x=alle*sign - COST*2
    t,p=stats.ttest_1samp(x,0)
    print(f"  {name:28s} {x.mean():>+11.1f}bp {(x>0).mean()*100:>12.1f}% {p:>9.3f}")
print(f"""
  -> Umdrehen kostet doppelt: du verlierst den Edge UND zahlst
     dieselben Gebuehren. Der Unterschied ist {2*alle.mean():.0f} bp je Trade.

  Bei {len(tr)} Trades in 5,4 Jahren waeren das
  {2*alle.mean()*len(tr)/1e4*100:.0f} Prozentpunkte Gesamtrendite Unterschied.""")

print()
print("="*84)
print("FRAGE 3: Wie oft liegt das Signal 6 Stunden nach Einstieg hinten?")
print("="*84)
for h in [1,3,6,12,24,48]:
    e=np.array([dr*(c[t+h]/c[t]-1) for t,dr in tr])
    print(f"  nach {h:>2d}h im Minus: {(e<0).mean()*100:>5.1f} %")
print("""
  -> Etwa jeder zweite Trade steht zwischendurch im Minus.
     Das ist keine Ausnahme, das ist der Normalzustand.""")
