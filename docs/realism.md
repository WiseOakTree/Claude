# Wie belastbar sind diese Backtest-Ergebnisse?

> ## 🛑 KRITISCHE KORREKTUR (2026-08-01)
>
> **Die in diesem Dokument genannten Pass-Raten (91-93 %) sind NICHT gueltig.**
> Der Backtest enthaelt einen Look-ahead-Bias: Er entscheidet anhand des
> **Kerzenschlusses**, ob ein Signal vorliegt, fuellt aber zum **Brick-Level**,
> das frueher innerhalb der Kerze lag. Zum Fill-Zeitpunkt ist real nicht
> bekannt, ob der Schluss das Signal bestaetigt.
>
> Gemessener systematischer Fill-Vorteil: **0,34 % je Trade** in Handelsrichtung.
> Bei ~108 Trades je Fenster ist das der gesamte vermeintliche Edge.
>
> **Look-ahead-freie Ergebnisse (4 Jahre BTC, 46 Fenster, echte Gebuehren):**
>
> | Variante | Pass-Rate | Median |
> |---|---|---|
> | Fill am Brick-Level (fehlerhaft) | 93 % | +17,5 % |
> | Fill zum Schlusskurs der Signalkerze | **7 %** | **-5,3 %** |
> | Ruhende Stop-Order (Fill auf Beruehrung) | **0 %** | -29,6 % |
>
> Bei ruhenden Stop-Orders sind **55,5 % aller Ausloesungen Fehlausloesungen**
> (Dochte ohne Bestaetigung); die Handelsfrequenz liegt bei 2,25x des Backtests.
> Kein Parameter rettet die Strategie: die beste look-ahead-freie Variante
> erreicht 15 % Pass-Rate bei +1,4 % Median.
>
> **Fazit: Die Renko-Reversal-Strategie hat auf 1h-BTC keinen nachweisbaren
> Edge. Nicht live handeln, keine Challenge darauf kaufen.**
>
> Die folgenden Abschnitte sind als Dokumentation des Analysewegs erhalten --
> alle Zahlen darin unterliegen dem oben beschriebenen Bias.

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

### Konsequenz für die Praxis — und die Lösung

> **Die Strategie funktioniert nur mit vorab platzierten Orders an den
> Brick-Levels — nicht durch manuelles Reagieren auf eine Benachrichtigung.**

Das ist machbar, weil die Levels **im Voraus bekannt** sind: Der nächste
Aufwärts-Brick liegt bei `Anker + Brickgröße`, der nächste Abwärts-Brick bei
`Anker − Brickgröße`; für ein Signal braucht es `reversal_bricks` davon. Genau
das macht der Signal-Bot im Modus `levels` (Default).

**Validierung der vorhergesagten Level** (705 echte Signale, 1,5 Jahre BTC):

| Kennzahl | Wert |
|---|---|
| Level exakt getroffen (< 0,05 % Fehler) | 78,9 % |
| Abweichung Median | **0,017 %** |
| Abweichung 95. Perzentil | 0,146 % |

Und der entscheidende Test — Handel **mit den vorhergesagten Leveln** statt den
perfekten Brick-Levels (16 Walk-Forward-Fenster):

| Variante | Pass-Rate | Median-Rendite |
|---|---|---|
| Ideal: Fill am echten Brick-Level | 88 % | +18,6 % |
| **Real: Fill am vorhergesagten Level** | **94 %** | **+20,9 %** |
| Reagieren nach Kerzenschluss (1 h) | 7 % | −4,6 % |

Der Edge bleibt mit ruhenden Orders vollständig erhalten (minimal besser, weil
ATR-Drift teils zu einem früheren, günstigeren Fill führt). Wer stattdessen erst
nach Kerzenschluss reagiert, handelt eine **andere, hier nicht validierte
Strategie** — im Test mit negativer Erwartung.

Weil die Level mit ATR und Trend wandern, müssen die Orders **stündlich
nachgezogen** werden — der Bot meldet Änderungen automatisch.

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

## 2b. Welches Produkt? (Gebühren entscheiden)

Die Strategie handelt ~1,2 mal täglich — die Gebühr pro Roundtrip wirkt daher
direkt auf den Edge. Gemessen über dieselben 46 Fenster (Konto 10.000 $):

| Taker-Gebühr | Pass-Rate | Median-Rendite | |
|---|---|---|---|
| 0,02 % | 93 % | +19,4 % | ideal |
| **0,05 %** | **91 %** | **+16,5 %** | Futures/Perps — der Referenzfall |
| 0,08 % | 78 % | +13,8 % | noch brauchbar |
| 0,10 % | 76 % | +12,1 % | **Schmerzgrenze** |
| 0,16 % | 46 % | +7,2 % | grenzwertig |
| 0,20 % | 33 % | +3,9 % | kaum noch |
| 0,25 % | 30 % | +0,1 % | Edge weg |

**Regel: Die Taker-Gebühr muss ≤ 0,10 % sein, besser ≤ 0,05 %.**

Konkret auf Kraken:

| Produkt | Typische Taker-Gebühr | Ergebnis |
|---|---|---|
| Futures / Perpetuals | ~0,05 % | **91 % Pass-Rate** |
| Kraken Pro **Spot-Margin** (bis 5×) | ~0,25 % + Rollover ~0,02 %/4 h | **30 % Pass-Rate, +0,1 %** |

Spot-Margin auf Kraken Pro macht die Strategie also praktisch wertlos — nicht
wegen des Hebels, sondern wegen Gebühren und Rollover-Kosten. Nötig sind
**niedriggebührige Derivate**.

### ✅ Kraken-Prop-Gebühren bestätigt (Stand 2026-07)

Die tatsächlichen Konditionen im Prop-Konto:

| Kostenart | Wert |
|---|---|
| Kommission | **4 bps = 0,04 % pro Seite** (0,08 % je Roundtrip) |
| Margin-Finanzierung | **0,033 % pro Tag**, alle 4 h berechnet |

Beides mindert das Guthaben und zählt auf **MDL und MDD** — die Engine zieht
beides laufend von der Equity ab, ist also korrekt modelliert.

Damit liegt die Gebühr **unter** meiner ursprünglichen Annahme (0,05 %). Ergebnis
über dieselben 46 Fenster (10.000 $ Konto):

| Kostenszenario | Pass-Rate | Median | Worst-DD |
|---|---|---|---|
| Ursprüngliche Annahme (0,05 % / 0,030 %) | 91 % | +16,5 % | 6,94 % |
| **Echte Prop-Gebühren (0,04 % / 0,033 %)** | **93 %** | **+17,5 %** | **6,80 %** |
| Echte Gebühren + doppelte Slippage | 70 % | +11,1 % | 7,71 % |

**Fazit: Die Gebühren tragen die Strategie.** Sie liegen komfortabel unter der
Schmerzgrenze von 0,10 %.

### Die verbleibende Unsicherheit ist jetzt die Slippage

Kommission und Finanzierung sind bestätigte Zahlen. **Slippage und Spread bleiben
Schätzungen** (zusammen ~0,09 % je Fill) — und sie sind jetzt der größte
verbliebene Hebel: Verdoppeln sie sich, fällt die Pass-Rate von 93 % auf 70 %.

Kostenlast je Trade bei 10.000 $ (Ø Nominal 3.357 $):

| | |
|---|---|
| Kommission (Roundtrip) | 2,69 $ |
| Finanzierung (Ø 15,5 h Haltedauer) | 0,72 $ |
| Slippage + Spread (geschätzt) | 3,02 $ |
| **Summe je Trade** | **~6,42 $** (bei 30 $ Risiko je Trade) |
| Über ein 90-Tage-Fenster (108 Trades) | ~690 $ |

Die geschätzte Slippage ist also der größte einzelne Kostenblock — größer als die
Kommission. Sie lässt sich in der Praxis direkt messen: reale Fills mit den
Signal-Leveln vergleichen (siehe Abschnitt 1).

### Hebel wird nicht gebraucht

Bei 0,3 % Risiko und ~2-Brick-Stop liegt der Nominalwert bei nur **0,2–0,5 ×**
des Kontos. Die `max_leverage: 5.0` in der Config ist eine Obergrenze, die
praktisch nie greift. Gebraucht wird die Fähigkeit zu **shorten**, nicht Hebel.

### Kontogröße ist egal

Die Strategie rechnet prozentual und skaliert exakt. Über dieselben 46 Fenster
liefern 5.000 $, 10.000 $, 25.000 $ und 50.000 $ **identische** Werte
(Pass-Rate 91 %, Median +16,5 %, Worst-DD 6,94 %) — es ändern sich nur die
absoluten Beträge. Bei 10.000 $: 30 $ Risiko pro Trade, Ø-Order ~3.400 $,
~0,05 BTC — weit über Krakens Mindestordergröße.

## 2c. Teil-Gewinnmitnahmen (getestet — und verworfen)

Naheliegende Idee: an TP1 einen Großteil mitnehmen, den Rest laufen lassen.
Die Engine unterstützt das (`risk.tp_take_fractions`). Gemessen über dieselben
46 Fenster mit den echten Prop-Gebühren:

| Variante | Pass-Rate | Median | Worst-DD | Trefferquote |
|---|---|---|---|---|
| **Ohne TP (nur Reversal)** | **93 %** | **+17,5 %** | 6,80 % | 44,5 % |
| 25 % @TP1 | 91 % | +15,8 % | 6,27 % | 47,2 % |
| 50 % @TP1 | 76 % | +13,6 % | 5,85 % | 47,6 % |
| 75 % @TP1 | 74 % | +11,9 % | 5,69 % | 47,7 % |
| 50 % @TP1 + 50 % @TP2 | 74 % | +12,1 % | 5,85 % | 47,6 % |
| 75 % @TP1 + 25 % @TP2 | 67 % | +11,0 % | 5,69 % | 47,7 % |

Je mehr früh mitgenommen wird, desto schlechter — monoton. Der Grund ist
strukturell: Es ist ein **Trendfolgesystem**. Der Ertrag kommt aus wenigen weit
laufenden Gewinnern. Wer bei 2R drei Viertel abschneidet, deckelt genau diese
Gewinner, während Verlierer weiter voll verlieren. Die Trefferquote *steigt*
(fühlt sich besser an), die Erwartung sinkt.

Teilmitnahmen senken den Drawdown (6,80 % → 5,69 %). Deshalb der faire
Gegentest: freigewordenes Risikobudget in größere Positionen stecken.

| Variante | Pass-Rate | Median | Worst-DD |
|---|---|---|---|
| **Ohne TP, Risiko 0,30 %** | **93 %** | +17,5 % | **6,80 %** |
| 75 % @TP1, Risiko 0,40 % | 83 % | +16,1 % | 7,55 % |
| 75 % @TP1, Risiko 0,50 % | 83 % | +20,5 % | 9,41 % |
| 50/50, Risiko 0,40 % | 87 % | +16,4 % | 7,77 % |

Auch mit mehr Risiko bleibt keine TP-Variante an die Basis heran — die gewinnt
gleichzeitig bei Pass-Rate, Rendite **und** Drawdown.

> **Fazit: Keine Teil-Gewinnmitnahmen.** Der Ausstieg bleibt das Gegensignal.
> Die TP-Level in den Nachrichten sind Orientierung, keine Handlungsanweisung.
> Wer sie dennoch nutzen will, zahlt ~19 Prozentpunkte Pass-Rate für eine
> ruhigere Equity-Kurve.

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
