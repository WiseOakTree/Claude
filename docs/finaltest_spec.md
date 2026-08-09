# Finaler Test — Spezifikation VOR der Rechnung

Festgelegt am 2026-08-08, committet bevor gerechnet wurde.

## Die Frage

> **Kann ein privater Krypto-Trader mit öffentlich bekannten Regeln einen
> statistisch signifikanten Edge gegenüber einem fairen Zufallsprozess
> erzielen?**

## Warum das stärker ist als ein weiterer Backtest

Ein einzelner Backtest fragt „funktioniert Regel X". Dieser Test fragt
**„funktioniert die beste aus einer vorab festgelegten Familie besser, als die
beste aus einer gleich großen Zufallsfamilie"** — und beantwortet damit das
Mehrfachtestproblem im Instrument selbst, nicht durch eine Korrektur danach.

## Regelfamilie: keine Optimierung, nur Lehrbuchwerte

Alle Parameter sind die **kanonischen** aus der Literatur. Es wird **kein
einziger Parameter gesucht** — jede Suche würde das Mehrfachtestproblem wieder
einführen.

| Regel | Parameter (Standard) |
|---|---|
| MACD-Kreuzung | 12 / 26 / 9 |
| RSI überkauft/überverkauft | 14, Schwellen 30 / 70 |
| Stochastik-Kreuzung | 14 / 3 / 3, Schwellen 20 / 80 |
| Bollinger-Rückkehr | 20 / 2 |
| Bollinger-Ausbruch | 20 / 2 |
| Goldenes Kreuz | SMA 50 / 200 |
| SMA-Kreuzung kurz | 20 / 50 |
| Donchian-Ausbruch | 20 |
| Donchian-Ausbruch lang | 55 |
| ATR-Ausbruch | Schluss > Vortagshoch + 1 ATR(14) |
| Momentum | 90 Bars, Vorzeichen |
| Momentum-Umkehr | 90 Bars, Gegenvorzeichen |
| VWAP-Kreuzung (Tag) | Standard |
| CCI | 20, Schwellen ±100 |
| Williams %R | 14, Schwellen −20 / −80 |
| ADX-Trendfilter + MA | ADX 14 > 25 |
| Ichimoku Tenkan/Kijun | 9 / 26 |
| Parabolic SAR | 0,02 / 0,2 |
| Aroon-Kreuzung | 25 |
| MFI | 14, Schwellen 20 / 80 |
| OBV-Trend | SMA 20 des OBV |
| Keltner-Ausbruch | EMA 20, 2 × ATR(10) |
| Heikin-Ashi-Wechsel | Standard |
| **S/R-Ausbruch (dieses Projekt)** | ≥ 6 Berührungen |
| **Gegen-Bounce (dieses Projekt)** | ≥ 6 Berührungen, short |

## Testaufbau

| | |
|---|---|
| Märkte | **14** (BTC, ETH, SOL, BNB, XRP, ADA, ATOM, AVAX, BCH, DOGE, DOT, LINK, LTC, TRX) |
| Takt | 1 h |
| Haltedauer | 48 h, fest, kein Stop |
| Kosten | **8 bp je Seite = 16 bp je Roundtrip** |
| Zeitraum | 2021-03 bis 2026-08 |
| Auswertung | gepoolt über alle Märkte, je Regel eine Kennzahl |

## Der Nullprozess: „fairer Zufall"

Für jede Bootstrap-Runde und jeden Markt:

- **gleiche Anzahl Signale** wie die echte Regel
- **gleiche Haltedauer** (48 h)
- **gleiches Long/Short-Verhältnis**
- **dieselbe Kursreihe** — Drift, Volatilitäts-Cluster und fette Ränder
  bleiben also vollständig erhalten
- nur **Zeitpunkt und Richtung** werden gewürfelt

Damit misst der Test ausschließlich, ob die Regel **Information über den
Zeitpunkt und die Richtung** trägt — nicht, ob der Markt gestiegen ist.

## Die Statistik: White's Reality Check

1. Beobachtet: die Kennzahl jeder Regel, und das **Maximum** über alle Regeln.
2. Null: 2.000 Runden. In jeder Runde alle Regeln durch Zufallssignale
   ersetzen, Kennzahlen berechnen, **Maximum** notieren.
3. **familienweiser p-Wert** = Anteil der Runden, in denen das Zufalls-Maximum
   das beobachtete Maximum erreicht oder übertrifft.

Zusätzlich als Einzelbefund: Romano-Wolf-Schrittabstieg für jede Regel.

## Vorab festgelegtes Urteil

| Ergebnis | Schlussfolgerung |
|---|---|
| familienweiser p < 0,05 | **Ja** — es gibt einen nachweisbaren Edge in öffentlich bekannten Regeln |
| familienweiser p ≥ 0,05 | **Nein** — nach Kosten und sauberer Statistik bleibt kein reproduzierbarer Edge |

Es wird **kein Parameter, keine Regel und kein Markt nach Sichtung der
Ergebnisse geändert.** Das Urteil steht mit dem p-Wert.
