# Saubere Strategiesuche — Ergebnis

Nachdem der Look-ahead-Bias behoben war ([`realism.md`](realism.md)), habe ich
systematisch nach einer Strategie gesucht, die die Kraken-Prop-Challenge
(„Starter": +10 % Ziel, 6 % Drawdown, 3 % Tagesverlust) zuverlässig besteht.

**Ergebnis: keine der getesteten Strategien besteht.**

## Testaufbau

| | |
|---|---|
| Daten | BTC 1h, 4 Jahre (2022–2026), inkl. Bärenmarkt |
| Timeframes | 1h, 4h, 1D |
| Auswertung | Walk-Forward, 90-Tage-Fenster, jedes ein eigener Challenge-Versuch |
| Kosten | echte Kraken-Prop-Konditionen (0,04 %/Seite, 0,033 %/Tag Funding) + Spread/Slippage |
| Ausführung | `execution.mode="close"` — look-ahead-frei per Konstruktion |
| Kombinationen | 120 (5 Strategiefamilien × Parameter × Timeframes) |

Alle Strategien sind durch Tests als look-ahead-frei nachgewiesen
(`tests/test_strategies.py::test_no_lookahead`: Signale auf abgeschnittener
Kursreihe müssen mit denen der vollen Reihe übereinstimmen).

## Ergebnisse

Beste Pass-Rate je Strategiefamilie:

| Strategie | beste Pass-Rate | Median-Rendite | Worst-DD | TF |
|---|---|---|---|---|
| EMA-Kreuzung | **20 %** | +0,1 % | 11,24 % | 1h |
| Ausbruch + Trendfilter | 17 % | +0,1 % | 17,24 % | 1h |
| Donchian-Ausbruch | 15 % | −0,8 % | 17,24 % | 1h |
| Momentum | 13 % | −2,5 % | 16,79 % | 1h |
| Bollinger-Reversion | 0 % | +0,0 % | 2,71 % | 1D |
| *(Renko-Reversal, Ausgangspunkt)* | *7 %* | *−5,3 %* | *23,15 %* | *1h* |

Über alle 120 Kombinationen:

- **0,0 %** erreichen eine Pass-Rate von 50 % oder mehr
- **30,8 %** haben überhaupt einen positiven Median
- Median-Rendite über alle Kombinationen: **+0,00 %**

## Interpretation

Die Median-Rendite von exakt 0 % über 120 Kombinationen ist das eigentliche
Ergebnis: Diese Strategiefamilien haben auf BTC **keinen Edge**. Was übrig
bleibt, ist Rauschen — mal knapp positiv, mal knapp negativ, im Mittel null.
Die Kosten (~0,08 % je Roundtrip plus Funding) drücken das Ganze zusätzlich
nach unten.

Die Challenge verlangt **+10 % ohne 6 % Drawdown**. Selbst eine Strategie mit
leicht positiver Erwartung schafft das selten, weil das Drawdown-Limit vorher
greift: Die besten gefundenen Varianten haben Worst-Drawdowns von 11–17 % — das
Zwei- bis Dreifache des Erlaubten.

## Was das praktisch heißt

- **Klassische technische Analyse auf BTC löst diese Aufgabe nicht.** Weder
  Trendfolge (Donchian, EMA, Momentum) noch Mean-Reversion (Bollinger), auf
  keinem der drei Timeframes.
- Ein Parameter-Sweep findet keinen Edge, wenn keiner da ist. Wer lange genug
  sucht, findet Kombinationen, die *im Rückblick* gut aussehen — das ist
  Überanpassung, kein Ergebnis (deshalb der Walk-Forward über 46 Fenster).
- **Empfehlung: die Challenge nicht auf Basis dieser Strategien handeln.**

## Was einen echten Edge ausmachen könnte

Nicht getestet, deutlich aufwendiger, und ohne Erfolgsgarantie:

- Andere Datenquellen als Preis allein (Orderbuch, Funding-Raten, On-Chain,
  Cross-Exchange-Basis)
- Marktmikrostruktur auf sehr kurzen Zeitskalen (erfordert Infrastruktur, die
  ein manueller Trader nicht hat)
- Portfolio- statt Einzelasset-Ansätze (viele Märkte, kleine Einzelrisiken)

Alles davon ist ein Forschungsprojekt, kein Parameter-Sweep. Wer die Challenge
handeln will, sollte wissen, dass er ohne nachgewiesenen Edge gegen Gebühren
und ein enges Drawdown-Limit antritt.

## Rohdaten

Die vollständige Tabelle aller 120 Kombinationen entsteht mit dem Suchlauf aus
diesem Dokument; die Strategien liegen in `src/prop_backtester/strategies.py`.

---

## Nachtrag: Wochen-Swing (wenige Trades, große Bewegungen)

Die logische Antwort auf das Kostenproblem: weniger Trades, größere Bewegungen,
Wochenchart. Getestet — und die Arithmetik entscheidet.

**Wochen-ATR bei BTC: 9,1 % vom Kurs** (Tages-ATR: 3,53 %). Ein 2-ATR-Stop
bedeutet 18,2 % Kursbewegung. Daraus folgt die Falle:

| Risiko/Trade | Position | für +10 % nötige Kursbewegung |
|---|---|---|
| 0,3 % | 1,6 % des Kontos | **607 %** |
| 1,0 % | 5,5 % | 182 % |
| 2,0 % | 11,0 % | **91 %** |

Zum Vergleich: die beste 26-Wochen-Bewegung in vier Jahren war +167 %.

**Gemessen** (Trendfolge auf Wochenkerzen, 26-Wochen-Fenster, 36 Kombinationen
aus Strategie × Stop-Breite × Risiko): beste Pass-Rate **6 %**, Median-Rendite
**+0,0 %**, **1 Trade** je Fenster. Die Drawdowns sind niedrig (0,5–10 %) — die
Risikokontrolle funktioniert einwandfrei. Es passiert nur nichts.

### Die Zwickmühle

| Ansatz | Warum er scheitert |
|---|---|
| Viele Trades | 16 bp je Roundtrip fressen den Edge |
| Wenige Trades | ~1 Gelegenheit je 180 Tage, Median +0,0 % |
| Breite Stops | Position 1,6–11 % → 91–607 % Kursbewegung nötig |
| Enge Stops | bei 9,1 % Wochen-ATR permanent ausgestoppt |

### Der eigentliche Maßstab

Wie gut ist **BTC selbst** über 90-Tage-Fenster (einfach halten, 138 Fenster)?

| | |
|---|---|
| Rendite | median +6,8 %, bestes +81,8 % |
| Drawdown | median 18,5 %, größter 38,1 % |
| Verhältnis Rendite/Drawdown | **median 0,41** |

Die Challenge verlangt ein Verhältnis von **1,67** *und* +10 % *und* Drawdown
≤ 6 %. **BTC selbst erfüllt das in 1 % der Fenster (1 von 138).**

Das ist die Kernaussage der gesamten Untersuchung: Nicht die Strategie ist das
Problem, sondern die **Struktur der Aufgabe**. Ein 6-%-Drawdown-Limit auf einem
Asset mit 18,5 % typischem 90-Tage-Drawdown verlangt, dass man viermal besser
ist als der Markt selbst — dauerhaft, ohne Diversifikation, mit 16 bp Reibung
je Trade.
