"""Kombination aller Signale mit messbarer Struktur.

Architektur: Richtung aus dem Signal-Ensemble, Groesse aus Vol-Targeting.
Entscheidend ist die Korrelationsmatrix -- ohne Unabhaengigkeit kein Gewinn.
"""
import numpy as np, pandas as pd
from scipy import stats

V = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
O = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/of/"
C = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/oc/"

px = pd.read_csv(V+"btc_1h.csv", index_col=0, parse_dates=True)["close"].resample("1D").last().dropna()
dvol = pd.read_csv(V+"dvol_BTC.csv", index_col=0, parse_dates=True)["close"].resample("1D").last()
onc = pd.read_csv(C+"onchain_feat.csv", index_col=0, parse_dates=True)
flow = pd.read_csv(O+"flow_5m.csv.gz", index_col=0, parse_dates=True)
hist = pd.read_csv(O+"depth_feat_hist.csv.gz", index_col=0, parse_dates=True)
d = pd.read_csv(O+"bookdepth.csv.gz"); d["timestamp"]=pd.to_datetime(d["timestamp"],utc=True,format="mixed")
piv = d.pivot_table(index="timestamp",columns="percentage",values="notional",aggfunc="sum")
lv=sorted(piv.columns); neg=[c for c in lv if c<0]; pos=[c for c in lv if c>0]
rec = pd.DataFrame(index=piv.index)
b=piv[[c for c in neg if abs(c)<=5]].sum(axis=1); a=piv[[c for c in pos if abs(c)<=5]].sum(axis=1)
rec["imb5"]=(b-a)/(b+a)
depth = pd.concat([hist[["imb5"]], rec[["imb5"]]]).sort_index()
depth = depth[~depth.index.duplicated(keep="last")]

X = pd.DataFrame(index=px.index)
X["px"] = px
X["ret"] = px.pct_change()
def z(s, w=90): return (s - s.rolling(w).mean())/s.rolling(w).std()

# --- Richtungssignale (alle look-ahead-frei, jeweils zum Vortagesschluss bekannt) ---
X["s_mvrv"]  = z(onc["mvrv_z"].reindex(px.index).ffill(), 365)     # Momentum (Vorzeichen wie gemessen)
X["s_book"]  = z(depth["imb5"].resample("1D").mean().reindex(px.index), 90)
ofi = ((2*flow["taker_base"] - flow["volume"]) / flow["volume"]).resample("1D").mean()
X["s_flow"]  = -z(ofi.reindex(px.index), 90)                       # Vorzeichen negativ (gemessen)
X["s_trend"] = z(px/px.rolling(50).mean() - 1, 90)                 # klassische Trendfolge
# --- Groessensignal ---
rv = np.log(px).diff().rolling(30).std()*np.sqrt(365)*100
X["vol_est"] = dvol.reindex(px.index).ffill().fillna(rv)

X = X.dropna()
print(f"Gemeinsamer Zeitraum: {X.index.min().date()} .. {X.index.max().date()}  "
      f"({len(X)} Tage, {len(X)/90:.0f} unabhaengige 90-Tage-Fenster)\n")

SIG = ["s_mvrv","s_book","s_flow","s_trend"]
print("="*74); print("1) Korrelationsmatrix der Signale"); print("="*74)
cm = X[SIG].corr()
print("        " + "".join(f"{s[2:]:>9s}" for s in SIG))
for s in SIG:
    print(f"  {s[2:]:6s}" + "".join(f"{cm.loc[s,t]:+9.2f}" for t in SIG))
off = cm.values[np.triu_indices_from(cm.values, 1)]
print(f"\n  mittlere paarweise Korrelation: {np.abs(off).mean():+.3f}  "
      f"(Spanne {off.min():+.2f} .. {off.max():+.2f})")
k = len(SIG); rho = np.abs(off).mean()
print(f"  theoretischer Diversifikationsgewinn: sqrt({k}) = {np.sqrt(k):.2f}x bei rho=0,")
print(f"  bei rho={rho:.2f} nur {np.sqrt(k/(1+(k-1)*rho)):.2f}x")

print("\n"+"="*74); print("2) IC einzeln vs. kombiniert (20-Tage-Horizont)"); print("="*74)
H = 20
fwd = X["px"].pct_change(H).shift(-H)
def cp(ic,n):
    t=ic*np.sqrt(max(n-2,1)/max(1-ic**2,1e-9)); return 2*(1-stats.t.cdf(abs(t),max(n-2,1)))
for s in SIG:
    m = pd.concat([X[s].rename("s"), fwd.rename("f")],axis=1).dropna()
    ic,_ = stats.spearmanr(m["s"],m["f"])
    print(f"  {s[2:]:8s} IC {ic:+.3f}   p korr. {cp(ic,len(m)/H):.3f}")
X["combo"] = X[SIG].mean(axis=1)
m = pd.concat([X["combo"].rename("s"), fwd.rename("f")],axis=1).dropna()
ic_c,_ = stats.spearmanr(m["s"],m["f"])
print(f"  {'KOMBI':8s} IC {ic_c:+.3f}   p korr. {cp(ic_c,len(m)/H):.3f}   <-- Ensemble")

print("\n"+"="*74); print("3) Gegen die Challenge-Regeln"); print("="*74)
COST = 16e-4
def challenge(r, win=90):
    r=r.dropna().to_numpy(); passed=tot=0; R=[];DD=[]
    for s in range(0,len(r)-win):
        w=r[s:s+win]; eq=np.cumprod(1+w); dd=(eq/np.maximum.accumulate(eq)-1).min()
        passed += (eq[-1]-1>=.10 and dd>=-.06 and w.min()>-.03); tot+=1
        R.append(eq[-1]-1); DD.append(-dd)
    if not tot: return 0,0,0,0
    return passed/tot*100, np.median(R)*100, np.median(DD)*100, tot
print(f"{'Variante':44s} {'Rendite':>9s} {'DD':>7s} {'Pass':>7s}")
print("-"*72)
p,m_,dd,n = challenge(X["ret"]); print(f"{'BTC einfach halten':44s} {m_:+8.1f}% {dd:6.1f}% {p:6.1f}%")
vt = (20.0/X["vol_est"].shift(1)).clip(upper=2.0)
r_vt = vt*X["ret"] - COST*vt.diff().abs().fillna(0)
p,m_,dd,n = challenge(r_vt); print(f"{'nur Vol-Targeting (Referenz)':44s} {m_:+8.1f}% {dd:6.1f}% {p:6.1f}%")
for nm, sig in ([(s[2:], X[s]) for s in SIG] + [("KOMBI (Mittel aller 4)", X["combo"])]):
    for thr in (0.0, 0.5):
        dirn = np.sign(sig.shift(1)) * (sig.shift(1).abs() > thr)
        w = dirn * vt
        r = w*X["ret"] - COST*w.diff().abs().fillna(0)
        p,m_,dd,n = challenge(r)
        print(f"{f'{nm} x Vol-Target, |z|>{thr}':44s} {m_:+8.1f}% {dd:6.1f}% {p:6.1f}%")
