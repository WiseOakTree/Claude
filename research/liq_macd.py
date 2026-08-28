"""LIQUIDITAET + MACD auf 1h und 4h -- die Methode des Nutzers, zerlegt.

Aufbau nach docs/liq_macd_spec.md -- vor der Rechnung festgelegt.
Kosten aus den echten Trades des Nutzers: 12 bp Roundtrip (Hauptmodell).
"""
import sys, os, warnings, pickle
sys.path.insert(0, "/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats

from prop_backtester import levels
from prop_backtester.renko import wilder_atr

S = "/tmp/claude-0/-home-user/6ea4b953-8381-58a1-a843-0b428058fee5/scratchpad/"
V = S + "vol/"
MAERKTE = ["btc", "eth", "sol", "xrp", "doge", "ada"]
GRENZE = pd.Timestamp("2025-01-01", tz="UTC")
ZIEL = STOP = 0.006          # 0,6 % Klammer
MAXH = 24                    # Stunden
KOSTEN = {"brutto": 0.0, "8bp": 0.0008, "12bp": 0.0012}
MIN_TOUCH = 3
NAEHE_ATR = 1.0


def macd(x, fast=12, slow=26, sig=9):
    s = pd.Series(x)
    line = s.ewm(span=fast, adjust=False).mean() - s.ewm(span=slow, adjust=False).mean()
    signal = line.ewm(span=sig, adjust=False).mean()
    return (line - signal).to_numpy()


def bausteine(df):
    """Alle Filter je 1h-Bar -- streng kausal."""
    c = df["close"].to_numpy(float)
    n = len(c)
    h1 = macd(c)
    kreuz = np.zeros(n, dtype=int)
    kreuz[1:] = np.where((h1[1:] > 0) & (h1[:-1] <= 0), 1,
                         np.where((h1[1:] < 0) & (h1[:-1] >= 0), -1, 0))
    kreuz[:40] = 0

    # 4h-MACD: auf 4h-Kerzen gerechnet, dann mit shift(1) auf 1h zurueck --
    # der 4h-Wert ist erst NACH dem Schluss der 4h-Kerze bekannt.
    c4 = df["close"].resample("4h").last().dropna()
    h4 = pd.Series(macd(c4.to_numpy()), index=c4.index).shift(1)
    trend4 = np.sign(h4.reindex(df.index, method="ffill").fillna(0).to_numpy()).astype(int)

    atr = wilder_atr(df, 14).to_numpy(float)
    by_bar = levels.build_levels(df, width=8, tol_atr=0.5, max_age=1000)

    # Fuer jeden Bar: Abstand zum naechsten Level ueber und unter dem Kurs
    oben = np.full(n, np.inf); unten = np.full(n, np.inf)
    for t in range(n):
        lv = by_bar.get(t)
        if not lv:
            continue
        p = c[t]
        for preis, art, touch, letzter in lv:
            if touch < MIN_TOUCH:
                continue
            d = abs(preis - p)
            if preis >= p:
                oben[t] = min(oben[t], d)
            else:
                unten[t] = min(unten[t], d)
    with np.errstate(invalid="ignore"):
        nah_oben = oben <= NAEHE_ATR * atr
        nah_unten = unten <= NAEHE_ATR * atr
    return dict(kreuz=kreuz, trend4=trend4, atr=atr,
                nah_oben=np.nan_to_num(nah_oben).astype(bool),
                nah_unten=np.nan_to_num(nah_unten).astype(bool))


def signale(b, stufe, n, rng=None):
    """Gibt ein Feld mit +1/-1/0 je Bar zurueck."""
    k, t4 = b["kreuz"], b["trend4"]
    if stufe == "L1":
        return k.copy()
    if stufe == "L2":
        return np.where(k == t4, k, 0)
    if stufe == "L3a":                       # Einstieg AN einem Level (Fade)
        basis = np.where(k == t4, k, 0)
        an_level = np.where(basis == 1, b["nah_unten"], b["nah_oben"])
        return np.where(an_level, basis, 0)
    if stufe == "L3b":                       # Level in Handelsrichtung (Magnet)
        basis = np.where(k == t4, k, 0)
        ziel_da = np.where(basis == 1, b["nah_oben"], b["nah_unten"])
        return np.where(ziel_da, basis, 0)
    if stufe == "L4":                        # nur Level-Naehe, ohne MACD
        s = np.zeros(n, dtype=int)
        s[b["nah_oben"]] = -1
        s[b["nah_unten"]] = 1
        s[b["nah_oben"] & b["nah_unten"]] = 0
        return s
    raise ValueError(stufe)


def handeln(df, sig, kosten="12bp", ziel=ZIEL, stop=STOP, maxh=MAXH):
    """Feste Klammer, eine Position gleichzeitig, Stop zaehlt vor Ziel."""
    k = KOSTEN[kosten]
    h = df["high"].to_numpy(float); l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float); n = len(c)
    out, i = [], 0
    while i < n - 1:
        s = int(sig[i])
        if s == 0:
            i += 1; continue
        entry = c[i]
        tp = entry * (1 + s * ziel); sl = entry * (1 - s * stop)
        grund, exitp, bis = "zeit", c[min(i + maxh, n - 1)], min(i + maxh, n - 1)
        for j in range(i + 1, min(i + maxh + 1, n)):
            stop_hit = (l[j] <= sl) if s == 1 else (h[j] >= sl)
            ziel_hit = (h[j] >= tp) if s == 1 else (l[j] <= tp)
            if stop_hit:
                grund, exitp, bis = "stop", sl, j; break
            if ziel_hit:
                grund, exitp, bis = "ziel", tp, j; break
        brutto = s * (exitp - entry) / entry
        out.append({"t": df.index[i], "seite": s, "grund": grund,
                    "brutto_bp": brutto * 1e4, "netto_bp": (brutto - k) * 1e4,
                    "stunden": bis - i})
        i = bis + 1          # keine ueberlappenden Positionen
    return pd.DataFrame(out)


def zufall(df, n_signale, long_anteil, kosten="12bp", ziehungen=30, seed=11):
    """Kontrolle: gleiche Anzahl, gleiche Quote, zufaellige Zeitpunkte."""
    rng = np.random.default_rng(seed)
    n = len(df)
    quoten, bps = [], []
    for _ in range(ziehungen):
        sig = np.zeros(n, dtype=int)
        idx = rng.choice(np.arange(40, n - MAXH - 1), size=min(n_signale, n - 60),
                         replace=False)
        sig[idx] = np.where(rng.random(len(idx)) < long_anteil, 1, -1)
        t = handeln(df, sig, kosten)
        if not len(t):
            continue
        ent = t[t["grund"].isin(["ziel", "stop"])]
        if len(ent):
            quoten.append((ent["grund"] == "ziel").mean())
        bps.append(t["netto_bp"].mean())
    return float(np.mean(quoten)), float(np.mean(bps))


def rechne(cache=S + "liq_macd.pkl"):
    if os.path.exists(cache):
        return pickle.load(open(cache, "rb"))
    alle, kontrolle = [], []
    for sym in MAERKTE:
        voll = pd.read_csv(V + f"{sym}_1h.csv", index_col=0, parse_dates=True)
        b_voll = bausteine(voll)
        for periode, maske in (("suche", voll.index < GRENZE),
                               ("holdout", voll.index >= GRENZE)):
            df = voll[maske]
            b = {k: (v[maske] if isinstance(v, np.ndarray) else v)
                 for k, v in b_voll.items()}
            for stufe in ("L1", "L2", "L3a", "L3b", "L4"):
                sig = signale(b, stufe, len(df))
                for kost in ("brutto", "8bp", "12bp"):
                    t = handeln(df, sig, kost)
                    if not len(t):
                        continue
                    t["markt"], t["periode"], t["stufe"], t["kosten"] = \
                        sym, periode, stufe, kost
                    alle.append(t)
                # Kontrolle nur fuer das Hauptkostenmodell
                nz = int((sig != 0).sum())
                if nz > 10:
                    la = float((sig == 1).sum()) / nz
                    q, bp = zufall(df, nz, la)
                    kontrolle.append({"markt": sym, "periode": periode,
                                      "stufe": stufe, "quote": q, "bp": bp})
        print(f"  {sym} fertig", flush=True)
    out = (pd.concat(alle, ignore_index=True), pd.DataFrame(kontrolle))
    pickle.dump(out, open(cache, "wb"))
    return out


def zeile(t, kt=None):
    ent = t[t["grund"].isin(["ziel", "stop"])]
    q = (ent["grund"] == "ziel").mean() if len(ent) else np.nan
    x = t["netto_bp"].to_numpy()
    tw = x.mean() / (x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 2 else np.nan
    je_markt = t.groupby("markt")["netto_bp"].mean()
    return (f"{len(t):6d} {q*100:7.1f}% {t['brutto_bp'].mean():9.2f} "
            f"{x.mean():9.2f} {tw:7.2f} {int((je_markt>0).sum())}/{len(je_markt)}"
            f" {t['stunden'].mean():7.1f}h")


if __name__ == "__main__":
    print("Rechne (oder lade Cache) ...", flush=True)
    tr, kt = rechne()
    ohne_btc = [m for m in MAERKTE if m != "btc"]
    NAMEN = {"L1": "nur 1h-MACD-Kreuzung",
             "L2": "1h + 4h gleichgerichtet",
             "L3a": "L2 + Einstieg AM Level (Fade)",
             "L3b": "L2 + Level als Ziel (Magnet)",
             "L4": "nur Level-Naehe, ohne MACD"}

    for periode, maerkte in (("SUCHE", MAERKTE), ("HOLDOUT", ohne_btc)):
        print("\n" + "=" * 112)
        print(f"DIE LEITER -- {periode} (Kosten 12 bp, wie aus den echten Trades abgeleitet)")
        print("=" * 112)
        print(f"{'':4s} {'Aufbau':32s} {'n':>6s} {'Treffer':>8s} {'brutto bp':>9s} "
              f"{'netto bp':>9s} {'t':>7s} {'+Mkt':>5s} {'Ø Dauer':>8s}")
        print("-" * 112)
        d = tr[(tr["periode"] == periode.lower()) & (tr["kosten"] == "12bp")
               & (tr["markt"].isin(maerkte))]
        for st in ("L1", "L2", "L3a", "L3b", "L4"):
            t = d[d["stufe"] == st]
            if len(t):
                print(f"{st:4s} {NAMEN[st]:32s} {zeile(t)}")
        k = kt[(kt["periode"] == periode.lower()) & (kt["markt"].isin(maerkte))]
        if len(k):
            print(f"{'L0':4s} {'Zufallseinstieg (Kontrolle)':32s} "
                  f"{'':6s} {k['quote'].mean()*100:7.1f}% {'':9s} "
                  f"{k['bp'].mean():9.2f}")

    print("\n" + "=" * 112)
    print("BRINGT DIE KONFLUENZ MEHR ALS IHRE TEILE? (netto bp, 12 bp Kosten)")
    print("=" * 112)
    print(f"{'Schritt':40s} {'Suche':>12s} {'Holdout':>12s} {'Signale S':>11s} {'Signale H':>11s}")
    print("-" * 112)
    def mw(st, per, maerkte):
        t = tr[(tr["stufe"] == st) & (tr["periode"] == per) & (tr["kosten"] == "12bp")
               & (tr["markt"].isin(maerkte))]
        return (t["netto_bp"].mean(), len(t)) if len(t) else (np.nan, 0)
    for a, b in (("L1", "L2"), ("L2", "L3a"), ("L2", "L3b")):
        s_a, n_sa = mw(a, "suche", MAERKTE); s_b, n_sb = mw(b, "suche", MAERKTE)
        h_a, n_ha = mw(a, "holdout", ohne_btc); h_b, n_hb = mw(b, "holdout", ohne_btc)
        print(f"{a + ' -> ' + b + '  (' + NAMEN[b] + ')':40s} "
              f"{s_b - s_a:+12.2f} {h_b - h_a:+12.2f} "
              f"{n_sb:5d}/{n_sa:<5d} {n_hb:5d}/{n_ha:<5d}")

    print("\n" + "=" * 112)
    print("KOSTEN: was der Markt gibt und was die Boerse nimmt (Suche, alle Maerkte)")
    print("=" * 112)
    print(f"{'':4s} {'Aufbau':32s} {'brutto':>9s} {'8 bp':>9s} {'12 bp':>9s}")
    print("-" * 112)
    for st in ("L1", "L2", "L3a", "L3b", "L4"):
        w = []
        for kost in ("brutto", "8bp", "12bp"):
            t = tr[(tr["stufe"] == st) & (tr["periode"] == "suche") & (tr["kosten"] == kost)]
            w.append(t["netto_bp"].mean() if len(t) else np.nan)
        print(f"{st:4s} {NAMEN[st]:32s} {w[0]:9.2f} {w[1]:9.2f} {w[2]:9.2f}")

    print("\n" + "=" * 112)
    print("LONG GEGEN SHORT (12 bp) -- beide gezeigten Trades waren Short")
    print("=" * 112)
    print(f"{'':4s} {'Aufbau':32s} {'Long n':>7s} {'Long bp':>9s} {'Short n':>8s} {'Short bp':>9s}")
    print("-" * 112)
    for st in ("L2", "L3a", "L3b"):
        for periode, maerkte in (("suche", MAERKTE), ("holdout", ohne_btc)):
            t = tr[(tr["stufe"] == st) & (tr["periode"] == periode)
                   & (tr["kosten"] == "12bp") & (tr["markt"].isin(maerkte))]
            lo, sh = t[t["seite"] == 1], t[t["seite"] == -1]
            print(f"{st:4s} {NAMEN[st][:24] + ' ' + periode:32s} {len(lo):7d} "
                  f"{lo['netto_bp'].mean():9.2f} {len(sh):8d} {sh['netto_bp'].mean():9.2f}")

    print("\n" + "=" * 112)
    print("BREAK-EVEN: Ziel und Stop je 0,6 % = 60 bp, Kosten 12 bp")
    print("=" * 112)
    be = (60 + 12) / 120
    print(f"  noetige Trefferquote: {be*100:.1f} %")
    for periode, maerkte in (("suche", MAERKTE), ("holdout", ohne_btc)):
        for st in ("L2", "L3a", "L3b"):
            t = tr[(tr["stufe"] == st) & (tr["periode"] == periode)
                   & (tr["kosten"] == "12bp") & (tr["markt"].isin(maerkte))]
            ent = t[t["grund"].isin(["ziel", "stop"])]
            if len(ent) < 20: continue
            q = (ent["grund"] == "ziel").mean()
            print(f"  {periode:8s} {st:4s} gemessen {q*100:5.1f} %  "
                  f"Luecke {(q-be)*100:+5.1f} pp")
    print("\nFERTIG")
