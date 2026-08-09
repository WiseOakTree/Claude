# „Alle TradingView-Strategien haben Sharpe unter 0,3"

Die Beobachtung deckt sich exakt mit den Messungen dieses Projekts. Aber sie
verdient zwei Ergänzungen: **warum** das so ist — und wo die Aussage zu weit
geht.

---

## Die Rauschdecke: was reines Rauschen liefert

N Strategien, jede mit **wahrem Sharpe = 0**. Berichtet wird die **beste** —
so wie in jedem veröffentlichten Backtest.

| Zeitraum | N=1 | N=10 | N=50 | N=200 | **N=1.000** | N=5.000 |
|---|---|---|---|---|---|---|
| 1 Jahr | −2,45 | 0,32 | 2,78 | 2,74 | **4,01** | 3,94 |
| 2 Jahre | −0,80 | 0,91 | 1,22 | 2,38 | 2,12 | 2,36 |
| **5 Jahre** | 0,09 | 0,57 | 1,19 | 1,44 | **1,77** | 1,85 |
| 10 Jahre | −0,22 | 0,70 | 0,67 | 0,70 | 1,02 | 1,12 |

**Wer 1.000 wertlose Varianten über fünf Jahre testet und die beste zeigt,
präsentiert einen Sharpe von rund 1,8 — bei null Edge.**

Ein TradingView-Skript mit fünf Parametern (Länge, Schwelle, Timeframe, Stop,
Ziel) hat leicht 1.000 Kombinationen. Der Autor probiert sie durch, findet die
beste, veröffentlicht sie mit Screenshot.

> **Die schöne Kurve ist kein Betrug. Sie ist das arithmetisch erwartete
> Ergebnis der Suche.**

---

## Und die zweite Hälfte: Sharpe 0,3 ist gar nicht messbar

Wie viele Jahre Daten braucht man, um einen Sharpe von 0 zu **unterscheiden**?

| wahrer Sharpe | Jahre für p < 0,05 | Jahre für p < 0,01 |
|---|---|---|
| 0,2 | **96,0** | 166,4 |
| **0,3** | **42,7** | 74,0 |
| 0,5 | 15,4 | 26,6 |
| 0,8 | 6,0 | 10,4 |
| 1,0 | 3,8 | 6,7 |
| 1,5 | 1,7 | 3,0 |

**Um Sharpe 0,3 überhaupt von null zu unterscheiden, braucht man 43 Jahre.**

Jede Behauptung *„diese Strategie hat Sharpe 0,3"* auf fünf Jahren Daten ist
mathematisch **nicht von „Sharpe 0" unterscheidbar**. Der Satz ist nicht
falsch — er ist bedeutungslos.

Und das gilt auch für meinen eigenen Fund: **Der S/R-Ausbruch hat Sharpe 0,36
über 5,4 Jahre. Nach dieser Tabelle bräuchte er 43 Jahre, um beweisbar zu
sein.** Er hat vier andere Kontrollen bestanden (Holdout, Überlappungs-
korrektur, Bonferroni, vier Assets) — aber der Sharpe allein trägt ihn nicht.

---

## Warum die Kurven trotzdem so gut aussehen

Der TradingView Strategy Tester zeigt standardmäßig:

- Slippage: **0** (Voreinstellung)
- Kommission: **0** (Voreinstellung)
- Auswertung auf **demselben Zeitraum**, auf dem optimiert wurde
- Keine Out-of-Sample-Hälfte

Der Effekt jedes einzelnen Punkts — in diesem Projekt gemessen:

| Fehler | gemessene Wirkung |
|---|---|
| Look-ahead-Bias | **93 % → 7 %** Pass-Rate |
| Kosten von 0 auf 16 bp | Edge fällt um **35 %** |
| Bestes von N statt Zufallswahl | 54,7 % → **31,9 %** out-of-sample |
| Überlappung nicht korrigiert | p = 10⁻²⁴⁰ → **p = 0,27** |

**Vier Fehler, jeder für sich ausreichend, um aus Nichts einen Backtest zu
machen.** Wer alle vier begeht — und die Voreinstellungen tun das
automatisch — findet garantiert eine funktionierende Strategie.

---

## 🛑 Wo die Aussage zu weit geht

| Ansatz | Sharpe | Datenbasis | Kontrollen |
|---|---|---|---|
| 120 TA-Kombinationen (Median) | **~0,00** | 4,5 Jahre | alle |
| S/R-Ausbruch BTC | **0,36** | 5,4 Jahre | alle bestanden |
| Bot-Orderbuch (als Market Maker) | 0,85 | 2,7 Jahre | OOS stärker |
| **Vol-Prämie BTC (Straddle)** | **1,85** | 5,4 Jahre | **t = 4,12** |
| **Vol-Prämie S&P 500** | **1,52** | 10 Jahre | **t = 4,67** |

**Bei Chartmustern hast du vollkommen recht: 0,00 bis 0,36.** Nach 39
getesteten Ansätzen ist das kein Verdacht mehr, das ist ein Befund.

**Aber Risikoprämien liegen bei 1,5 bis 1,9** — und die Volatilitätsprämie hat
als einziger Befund dieses Projekts **zwei unabhängige Anlageklassen**
überstanden (BTC t = 4,12, S&P t = 4,67).

### Der Unterschied ist nicht „besser gesucht"

Es ist eine **andere Art von Edge**:

| | Chartmuster | Risikoprämie |
|---|---|---|
| Woher kommt das Geld? | jemand handelt schlechter als du | du trägst ein Risiko, das andere loswerden wollen |
| Was passiert, wenn alle es kennen? | **verschwindet** | **bleibt** — die Versicherung wird trotzdem gebraucht |
| Auf TradingView zu finden? | ja, tausendfach | nein — kein Chartmuster |

**Deshalb steht sie nicht auf TradingView.** Nicht weil sie geheim ist —
sondern weil sie kein Indikator ist. Man kann sie nicht in Pine Script
zeichnen; man muss Optionen verkaufen und das Risiko wirklich tragen.

---

## Die brauchbare Version deiner Aussage

> **„Kein Chartmuster hat einen nachweisbaren Edge, und die meisten
> veröffentlichten Backtests zeigen den Erwartungswert einer Suche, nicht das
> Ergebnis einer Strategie."**

Das ist gemessen, und zwar hier:
- 120 TA-Kombinationen: Median-Rendite **0,00 %**
- 39 Ansätze insgesamt, **2 haltbar** — Trefferquote 5 %
- 9 Filter auf das überlebende Signal, **alle out-of-sample gescheitert**
- Rauschdecke: 1.000 Varianten → Sharpe 1,8 **ohne Edge**

Und der Satz, den ich anhängen würde:

> **Wer dir eine Strategie mit Sharpe 1,5 auf fünf Jahren zeigt, hat entweder
> eine Risikoprämie gefunden — oder tausend Varianten durchprobiert. Frag ihn,
> wie viele er getestet hat. Die Antwort entscheidet alles.**

---

*Skript: `research/tv_sharpe.py` (Rauschdecke, Nachweisbarkeit, Vergleich der
Edge-Typen).*
