"""NVT nachgereicht -- Luecken der Volumenreihe durch Interpolation geschlossen."""
import numpy as np, pandas as pd
from scipy import stats
OUT = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/oc/"
df = pd.read_csv(OUT+"onchain_feat.csv", index_col=0, parse_dates=True)
def cp(ic,n):
    t=ic*np.sqrt(max(n-2,1)/max(1-ic**2,1e-9)); return 2*(1-stats.t.cdf(abs(t),max(n-2,1)))

# Volumenreihe ist nur alle ~3-4 Tage besetzt -> linear auffuellen (nur vorwaerts bekannt)
vol = df["estimated-transaction-volume-usd"].interpolate(limit_area="inside")
df["nvt"] = df["CapMrktCurUSD"] / vol.rolling(28, min_periods=14).mean()
df["nvt_z"] = (df["nvt"] - df["nvt"].rolling(365, min_periods=200).mean()) \
              / df["nvt"].rolling(365, min_periods=200).std()
# klassische Lesart: niedriges NVT = guenstig = Kaufsignal
df["nvt_sig"] = -df["nvt_z"]

print("="*84); print("NVT (Network Value to Transactions) -- nachgereicht"); print("="*84)
valid = df["nvt_sig"].replace([np.inf,-np.inf],np.nan).dropna()
print(f"  gueltige Werte: {len(valid):,}  ({valid.index.min().date()} .. {valid.index.max().date()})\n")
print(f"{'Horizont':>9s} {'IC':>8s} {'p naiv':>10s} {'p korr.':>9s} {'n_eff':>6s} {'Q5-Q1':>9s}")
print("-"*60)
for h in (30, 90, 180, 365):
    fwd = df["px"].pct_change(h).shift(-h)
    s = pd.concat([df["nvt_sig"].rename("s"), fwd.rename("f")],
                  axis=1).replace([np.inf,-np.inf],np.nan).dropna()
    if len(s) < 400:
        print(f"{h:7d} T   zu wenige Daten ({len(s)})"); continue
    ic,p = stats.spearmanr(s["s"], s["f"]); ne = len(s)/h
    q = pd.qcut(s["s"],5,labels=False,duplicates="drop")
    sp = (s["f"][q==4].mean()-s["f"][q==0].mean())*100
    print(f"{h:7d} T {ic:+8.3f} {p:10.1e} {cp(ic,ne):9.3f} {ne:6.0f} {sp:+7.1f} %"
          + ("  <<<" if cp(ic,ne)<0.05 else ""))
