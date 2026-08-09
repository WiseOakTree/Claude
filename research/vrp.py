"""Misst die Volatilitaets-Risikopraemie: implizite (DVOL) vs. realisierte Vol."""
import numpy as np, pandas as pd
from scipy import stats

D = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"

def load(sym, dv):
    px = pd.read_csv(D + f"{sym}_1h.csv", index_col=0, parse_dates=True)
    d = pd.read_csv(D + f"dvol_{dv}.csv", index_col=0, parse_dates=True)
    # Tagesbasis: 00:00 UTC
    close = px["close"].resample("1D").last().dropna()
    iv = d["close"].resample("1D").last().dropna()
    return close, iv

for sym, dv in (("btc", "BTC"), ("eth", "ETH")):
    close, iv = load(sym, dv)
    ret = np.log(close).diff()

    # realisierte Vol der NAECHSTEN 30 Tage, annualisiert -- das, was DVOL prognostiziert
    fwd_rv = ret.shift(-1).rolling(30).std().shift(-29) * np.sqrt(365) * 100
    # trailing realisierte Vol (rueckblickend, wie im vorherigen Test)
    trail_rv = ret.rolling(30).std() * np.sqrt(365) * 100

    df = pd.DataFrame({"iv": iv, "fwd_rv": fwd_rv, "trail_rv": trail_rv,
                       "px": close}).dropna()
    vrp = df["iv"] - df["fwd_rv"]

    print(f"\n{'='*62}\n{sym.upper()}   n = {len(df)} Tage  ({df.index.min().date()} .. {df.index.max().date()})")
    print(f"{'='*62}")
    print(f"  Implizite Vol (DVOL)        Median {df['iv'].median():6.1f} %")
    print(f"  Realisierte Vol (folgend)   Median {df['fwd_rv'].median():6.1f} %")
    print(f"  ---------------------------------------------")
    print(f"  VRP = IV - RV              Median {vrp.median():+6.2f} pp   Mittel {vrp.mean():+6.2f} pp")
    print(f"  Anteil VRP > 0             {(vrp > 0).mean()*100:5.1f} %")
    t, p = stats.ttest_1samp(vrp.dropna(), 0)
    # Newey-West-artig: ueberlappende Fenster -> effektive n stark reduziert
    n_eff = len(vrp) / 30
    t_adj = vrp.mean() / (vrp.std() / np.sqrt(n_eff))
    p_adj = 2 * (1 - stats.t.cdf(abs(t_adj), n_eff - 1))
    print(f"  t naiv {t:6.2f} (p={p:.2e})  |  t ueberlappungskorrigiert {t_adj:5.2f} (p={p_adj:.4f})")

    # Prognosekraft: ist IV ein besserer Vol-Schaetzer als trailing RV?
    for name, est in (("DVOL (implizit)", df["iv"]), ("trailing 30T RV", df["trail_rv"])):
        r = np.corrcoef(est, df["fwd_rv"])[0, 1]
        mae = (est - df["fwd_rv"]).abs().mean()
        bias = (est - df["fwd_rv"]).mean()
        print(f"  {name:18s} -> korr {r:+.3f}   MAE {mae:5.2f} pp   Bias {bias:+6.2f} pp")
