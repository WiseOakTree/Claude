# Renko-Trail — Spezifikation VOR der Rechnung

Festgelegt am 2026-08-21, committet bevor gerechnet wurde.

## Die Frage

Der Ausgangspunkt dieses Projekts war eine Renko-Strategie, die **immer im
Markt** ist: zwei Gegen-Bricks drehen die Position um (Stop-and-Reverse). Sie
hat keinen Edge — das ist gemessen und dokumentiert.

Der naheliegende Einwand lautet: *Das Signal ist nicht der entscheidende Teil.
Entscheidend ist, was man mit dem Trade danach macht — Stop, Break-even,
Nachziehen, Teilmitnahme.* Diese Untersuchung prüft genau diesen Einwand.

Zwei getrennte Fragen, die im Alltag ständig vermischt werden:

> **A — Erwartungswert:** Verändert Handelsmanagement den Erwartungswert je
> Trade (Basispunkte nach Kosten)?

> **B — Risiko-Treue:** Bringt Handelsmanagement den Trade zu dem Ergebnis,
> das beim Einstieg geplant war? Konkret: Wie oft ist der tatsächliche Verlust
> größer als das geplante Risiko (1R)?

A und B sind unabhängig voneinander beantwortbar. Ein System kann bei A
scheitern und bei B gewinnen — und genau dann ist Risikomanagement trotzdem
der Unterschied zwischen Handel und Roulette.

**Vorab festgelegte Erwartung (damit sie nicht nachträglich passend gemacht
wird):** A: nein, kein Erwartungswert-Effekt über die Kostenwirkung hinaus.
B: ja, deutlich messbarer Effekt. Wenn A wider Erwarten ja ergibt, gelten die
verschärften Kriterien unten.

---

## Der eingebaute Fehler im Ausgangspunkt

Die bisherige Engine bemisst die Positionsgröße über eine **geplante**
Stop-Distanz (`risk.stop_bricks * Brick`), führt diesen Stop aber **nie aus**.
Der Ausstieg ist ausschließlich das Gegensignal. Das heißt: Es wird ein Risiko
von 0,5 % des Kontos *behauptet*, aber nichts erzwingt es.

Diese Untersuchung misst als Erstes, wie groß die Lücke zwischen behauptetem
und tatsächlichem Risiko ist. Das ist kein Nebenbefund, sondern Frage B in
ihrer schärfsten Form.

---

## Die Strategie: Renko-Trail

Neue Strategie, bewusst anders als der Ausgangspunkt: **diskrete Trades statt
Dauerposition.**

| Baustein | Regel |
|---|---|
| Gitter | ATR(14)-Renko, Brickgröße = ATR × 1,0 (unverändert) |
| Einstieg | nach `entry_bricks` = 3 gleichgerichteten Bricks, in Brick-Richtung |
| Anfangsstop | `stop_bricks` = 2 Bricks hinter dem Einstiegs-Brick, auf dem Gitter |
| Break-even | nach `be_bricks` = 2 Bricks Vorsprung → Stop auf Einstieg + Kosten |
| Trailing | Stop folgt dem Gitter mit `trail_bricks` = 2 Abstand zum letzten Brick |
| Teilmitnahme | `tp_fraction` = 0,5 bei `tp_r` = 2R |
| Zeitstop | Ausstieg nach `max_bars` = 240 Bars (10 Tage), wenn nicht ≥ 1R im Plus |
| Wiedereinstieg | erlaubt, sobald flat und ein neues Einstiegssignal steht |

Kein Parameter wird nach Sichtung der Ergebnisse geändert. Alle Werte sind
Lehrbuch-Rundwerte, keine optimierten.

---

## Die Leiter

Jede Stufe fügt genau einen Baustein hinzu. So ist jeder Effekt einzeln
zurechenbar.

| Stufe | Aufbau |
|---|---|
| **V0** | Stop-and-Reverse, kein echter Stop (der bisherige Ausgangspunkt) |
| **V1** | V0 + harter Stop bei 2 Bricks |
| **V2** | diskrete Trades (3 Bricks Einstieg) + harter Stop |
| **V3** | V2 + Break-even nach 2 Bricks |
| **V4** | V3 + Brick-Trailing |
| **V5** | V4 + Teilmitnahme 50 % bei 2R |
| **V6** | V5 + Zeitstop (= vollständiger Renko-Trail) |

---

## Kosten und Ausführung

Kein Ergebnis ohne Reibung. Alle Zahlen nach Kosten.

* **8 bp je Seite** (Gebühr + halber Spread + Slippage) = 16 bp je Roundtrip
* **Funding** 0,01 % je 8 h auf den Nominalwert offener Positionen
* **Stop-Slippage: zusätzlich 5 bp** auf jede Stop-Ausführung. Ein Stop ist
  eine Markt-Order in eine Bewegung hinein und füllt nicht am Stop-Preis.
* **Gap-Regel:** Eröffnet eine Bar jenseits des Stops, wird zur **Eröffnung**
  gefüllt, nicht am Stop-Preis. Der Stop schützt nicht gegen Lücken.
* **Reihenfolge innerhalb einer Bar:** Können Stop und Ziel in derselben Bar
  getroffen worden sein, zählt der **Stop zuerst**. Ohne Tickdaten ist alles
  andere geschönt.
* Fill-Zeitpunkt für Signale: Schlusskurs der Signal-Bar (kein Look-ahead).

---

## Daten

12 Märkte, 1 h, Binance-Spot, 2021-03 bis 2026-07:
BTC, ETH, SOL, BNB, XRP, ADA, DOGE, LINK, LTC, AVAX, DOT, BCH.

* **Suchzeitraum:** bis 2024-12-31
* **Holdout:** ab 2025-01-01

⚠️ Der BTC-Holdout ist in diesem Projekt über zwanzigmal benutzt worden und
gilt als verbraucht (siehe [`audit_und_finaltest.md`](audit_und_finaltest.md)).
Das Holdout-Urteil stützt sich deshalb auf die **elf übrigen Märkte**; BTC wird
nur nachrichtlich mitgeführt.

---

## Vorab festgelegte Auswertung

1. **bp je Trade nach Kosten** je Variante — gepoolt und je Markt
2. **Erwartungswert in R** (R = geplantes Anfangsrisiko in Geld)
3. **Risiko-Treue:**
   * Anteil der Trades mit realisiertem Verlust > 1,2 R
   * 95-%-Quantil des Verlusts in R
   * größter Einzelverlust in R
4. **Verteilungsform:** Trefferquote, Ø Gewinn / Ø Verlust in R
5. **Zufallseinstiege mit identischem Management:** gleiche Anzahl Trades,
   gleiche Long/Short-Quote, Zeitpunkte gleichverteilt über dieselben Bars,
   200 Ziehungen je Variante. Berichtet wird das Perzentil der echten Variante
   in dieser Verteilung.
6. **Prop-Kennzahlen:** Anzahl Tage mit Verlust > 3 % (Kraken-Tageslimit),
   maximaler Drawdown, Pass-Rate
7. **Holdout** für alle obigen Größen

---

## Urteilskriterien — festgelegt vor der Rechnung

### Frage A (Erwartungswert)

Management erzeugt einen Edge nur, wenn **alle vier** Bedingungen erfüllt sind:

1. bp je Trade nach Kosten **> 0** im Suchzeitraum
2. **gleiches Vorzeichen** im Holdout (11 Märkte ohne BTC)
3. über dem **95. Perzentil** der Zufallseinstiege mit identischem Management
4. t-Wert über der Bonferroni-Schwelle für 7 Varianten: **t > 2,69**
   (zweiseitig, α = 0,05/7)

Wird auch nur eine Bedingung verfehlt: **kein Edge durch Management.**

### Frage B (Risiko-Treue)

Management verbessert die Risikotreue, wenn gegenüber V0:

1. der Anteil der Trades mit Verlust > 1,2 R **sinkt** und
2. das 95-%-Quantil des Verlusts in R **sinkt**

Berichtet wird zusätzlich, was das kostet — Frage A und Frage B werden
**getrennt** beantwortet und nicht gegeneinander verrechnet.

### Der Preis der Sicherheit

Ausdrücklich mitberichtet wird der Erwartungswert-Unterschied zwischen V0 und
der besten V-Stufe bei Frage B. Wenn Risikomanagement Erwartungswert kostet,
steht diese Zahl im Ergebnis — nicht im Kleingedruckten.
