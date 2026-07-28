# Wie belastbar sind diese Backtest-Ergebnisse?

Ehrliche Bestandsaufnahme. Ein Backtest beschreibt die Vergangenheit unter
Annahmen — er sagt nichts vorher. Diese Seite misst, **wie stark die Ergebnisse
von jeder einzelnen Annahme abhängen**. Alle Zahlen stammen aus dem
Walk-Forward über 4 Jahre BTC 1h (46 × 90-Tage-Fenster, 2022–2026),
Einstellung 0.75× ATR / 0.3 % Risiko, Preset 1-Step Classic.

## 1. Der kritische Punkt: die Ausführungsannahme

Der Backtest füllt **exakt am Renko-Brick-Level** — dem Preis, der die Bricks
auslöst. Das ist der bestmögliche Fill. Was passiert bei realistischeren Fills?

| Fill-Annahme | Abweichung vom Level | Trefferquote | Median-Rendite |
|---|---|---|---|
| Am Brick-Level (Backtest) | 0,00 % | 47,3 % | **+19,7 %** |
| Nächste Kerzen-Eröffnung | 0,35 % | 33,5 % | **−1,0 %** |
| Nächster Kerzen-Schluss | 0,51 % | 32,4 % | **−0,4 %** |

Pass-Rate über alle 46 Fenster: **91 % bei Level-Fill → 7 % bei 1 Stunde Verzögerung.**

**Warum so brutal:** Der Stop ist nur ~1,3 % breit. Ein um 0,35 % schlechterer
Einstieg frisst ~27 % der Stop-Distanz und kippt das Chance/Risiko-Verhältnis.
Die Trefferquote fällt um 14 Punkte — aus einem Gewinn wird ein Nullsummenspiel.

### Konsequenz für die Praxis

> **Die Strategie funktioniert nur mit vorab platzierten Orders an den
> Brick-Levels — nicht durch manuelles Reagieren auf eine Benachrichtigung.**

Das ist machbar, weil die Levels **im Voraus bekannt** sind: Der nächste
Aufwärts-Brick liegt bei `Anker + Brickgröße`, der nächste Abwärts-Brick bei
`Anker − Brickgröße`. Man kann dort ruhende Stop-Orders hinterlegen.

Wer stattdessen erst nach Kerzenschluss reagiert (klassischer Alert-Workflow),
handelt eine **andere, hier nicht validierte Strategie** — im Test mit
negativer Erwartung.

## 2. Kostensensitivität

Bei ~1,2 Trades/Tag summieren sich Kosten schnell (~0,23 % je Roundtrip,
~25 % Nominal-Umsatzkosten je 90-Tage-Fenster).

| Kostenannahme | Pass-Rate | Median-Rendite |
|---|---|---|
| Null (unrealistisch) | 96 % | +27,4 % |
| **Basis (Modell)** | **91 %** | **+16,5 %** |
| Doppelt | 43 % | +7,1 % |
| Dreifach | 24 % | −1,6 % |
| Fünffach | 2 % | −16,7 % |

Sind die Kosten real doppelt so hoch wie angenommen, halbiert sich die
Pass-Rate. Das Modell rechnet mit 0,05 % Gebühr + 0,02 % halbem Spread +
0,02 % Slippage + volatilitätsabhängigem Aufschlag + Funding. Für einen
liquiden BTC-Markt plausibel — in schnellen Märkten, bei größeren Positionen
oder schlechteren Konditionen aber schnell überschritten.

## 3. Was gut aussieht: kein Overfitting

Parameter **nur auf 2022–2024 optimiert**, dann blind auf 2024–2026 angewendet:

| | Pass-Rate |
|---|---|
| In-Sample (2022–2024, worauf optimiert wurde) | 86 % |
| **Out-of-Sample (2024–2026, blind)** | **91 %** |
| Hindsight-Optimum auf dem Testzeitraum | 100 % |

Derselbe Parameter (0.75× / 0.3 %) gewann auf beiden Hälften, und die
Out-of-Sample-Leistung war sogar besser. Das spricht dafür, dass die
Parameterwahl **nicht** an Zufallsrauschen angepasst ist — ein echtes
Qualitätssignal. Es sagt nichts über die Zukunft aus.

## 4. Weitere Einschränkungen

- **Datenquelle:** 4-Jahres-Test auf Binance BTCUSDT, nicht Kraken (Krakens API
  liefert nur ~720 Kerzen). Kursniveaus und Mikrostruktur weichen leicht ab.
- **Ein Zeitraum, ein Asset:** 2022–2026 enthält genau einen Bärenmarkt und
  einen Bullenzyklus. Vier Jahre sind eine Stichprobe der Größe ~1, kein
  Gesetz. Der 8-Coin-Test lief nur über 30 Tage.
- **Bar-Granularität:** kein Orderbuch, keine Teilausführungen, kein
  Slippage-Modell für Flash-Crashs oder Börsenausfälle.
- **Nicht modelliert:** Challenge-Gebühren, Auszahlungsregeln, Steuern,
  Ausführungsdisziplin, verpasste Signale, psychologische Faktoren.
- **Funding** als konstanter Tagessatz statt echter Funding-Kurve.
- **Regeln können sich ändern:** Die Prop-Presets sind ein dokumentierter Stand
  (2026) und vor Nutzung mit Krakens aktueller Seite abzugleichen.
- **Selbst im besten Fall:** ~9 % der Fenster reißen das 6 %-Limit. Kein Setting
  besteht immer.

## 5. Fazit in einem Satz

Die Strategie zeigt über 4 Jahre und out-of-sample einen echten, robusten Edge —
**aber ausschließlich unter der Annahme, dass an den Brick-Levels gefüllt wird.**
Diese Annahme ist die eigentliche Wette; Kosten sind die zweitgrößte. Beides ist
prüfbar, bevor echtes Geld im Spiel ist: erst mit ruhenden Orders im Demo-/
Kleinbetrieb testen und die realen Fills mit den Signal-Levels vergleichen.
