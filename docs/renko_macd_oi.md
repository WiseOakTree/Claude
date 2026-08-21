# Renko (OHLC, 1 % Box) + MACD + Open Interest — das Chart-Setup gemessen

Nachgebaut wurde genau der Aufbau vom Chart: Renko mit **Quelle OHLC**,
**Boxgröße 1 % vom Kurs**, klassische **2-Boxen-Umkehr**, **MACD(12/26/9) auf
den Bricks**, Einstieg bei der Kreuzung, gefiltert über **Open Interest**.

Spezifikation vor der Rechnung: [`renko_macd_oi_spec.md`](renko_macd_oi_spec.md).
6 Märkte (BTC, ETH, SOL, XRP, DOGE, ADA), 1 h, 2023-01 bis 2026-07,
3.064 Signale im Suchzeitraum, alle Zahlen nach Kosten.

---

> ## Der Befund in drei Sätzen
>
> **Ein Strategietester, der auf Brick-Preisen rechnet, zeigt für dieses Setup
> +7,68 bp je Trade. Handelbar sind −29,24 bp. Die Differenz von 36,9 bp kippt
> das Vorzeichen** — die Strategie sieht im Test profitabel aus und ist es nicht.
>
> Nach dem ehrlichen Fill erfüllt keine der 21 gerechneten Kombinationen die
> vorab festgelegten Kriterien.
>
> Zwei Dinge überleben trotzdem: Der **harte Stop bringt hier +24,4 bp je Trade**
> — bei einem so langsamen Ausstiegssignal ist er nicht gratis, sondern der
> größte einzelne Hebel. Und der **OI-Filter trennt in beiden Zeiträumen
> gleichsinnig** (+15,5 bp in der Suche, +25,1 bp im Holdout gegenüber der
> Gegenbedingung) — ohne Signifikanz, aber ohne Vorzeichenwechsel.

---

## 1. Die entscheidende Zahl zuerst

Ein Renko-Brick schließt auf einem **Gitter-Level**, das *innerhalb* einer
Stunde erreicht wurde. Ein Strategietester, der die Brick-Preise als Bar-Preise
behandelt — das tun Chart-Tester auf Renko-Charts —, füllt dort. Die
Entscheidung („der MACD hat gekreuzt") steht aber erst fest, wenn der Brick
fertig ist.

Beides gerechnet, dieselben Signale, dieselben Kosten:

| | Fill am Brick-Level | ehrlicher Fill (Bar-Schluss) | **Differenz** |
|---|---|---|---|
| Suche / ohne Stop | **+7,68 bp** | −29,24 bp | **36,92 bp** |
| Suche / harter Stop | +6,72 bp | −4,82 bp | 11,54 bp |
| Suche / Stop+Trailing | −8,73 bp | −23,07 bp | 14,34 bp |
| Holdout / ohne Stop | +56,52 bp | +19,04 bp | 37,47 bp |
| Holdout / harter Stop | +23,52 bp | +8,91 bp | 14,61 bp |
| Holdout / Stop+Trailing | +1,86 bp | −11,99 bp | 13,84 bp |

**11,5 bis 37,5 Basispunkte je Trade**, und in vier von sechs Fällen wechselt
das Vorzeichen. Bei 94 bis 389 Signalen je Markt und Jahr ist das der
Unterschied zwischen „funktioniert" und „funktioniert nicht".

Dieses Projekt hat denselben Fehler schon einmal selbst gemacht und alle
Ergebnisse deswegen zurückgezogen ([`realism.md`](realism.md)). Er ist nicht
offensichtlich, weil nichts im Test falsch aussieht — die Kurve steigt einfach.

**Praktisch:** Zahlen aus einem Strategietester auf einem Renko-, Heikin-Ashi-
oder Point-&-Figure-Chart sind keine Backtest-Ergebnisse. Sie sind eine
Zeichnung.

---

## 2. Wirkt der Open-Interest-Filter?

Sieben Lesarten von „positives Open Interest", alle vorab festgelegt, alle
berichtet. Ehrlicher Fill, harter Stop.

### Suchzeitraum 2023-01 bis 2024-12 (6 Märkte)

| Lesart | n | bp/Trade | t (Märkte) | Märkte + | Ø Gew. R | Ø Verl. R |
|---|---|---|---|---|---|---|
| ohne Filter | 2.962 | −20,00 | −3,74 | 0/6 | 2,64 | −1,00 |
| **ΔOI 24 h > 0 (Haupt)** | 1.321 | **−4,82** | 0,16 | 2/6 | 3,83 | −1,03 |
| ΔOI 1 h > 0 | 1.011 | +21,21 | 1,09 | 3/6 | 5,13 | −1,05 |
| ΔOI 168 h > 0 | 1.421 | −1,78 | −0,77 | 2/6 | 3,48 | −1,02 |
| OI > Mittel 24 h | 1.294 | −4,34 | 0,32 | 3/6 | 3,95 | −1,03 |
| ΔOI-Wert 24 h > 0 | 1.384 | −9,45 | −0,19 | 3/6 | 3,65 | −1,03 |
| ΔOI 24 h < 0 (Gegenteil) | 1.464 | −20,31 | −2,00 | 1/6 | 3,51 | −1,02 |

### Holdout 2025-01 bis 2026-07 (5 Märkte, BTC ausgeschlossen)

| Lesart | n | bp/Trade | t (Märkte) | Märkte + |
|---|---|---|---|---|
| ohne Filter | 2.010 | +4,47 | 0,75 | 3/5 |
| **ΔOI 24 h > 0 (Haupt)** | 886 | **+15,93** | 1,20 | 3/5 |
| ΔOI 1 h > 0 | 783 | +0,59 | 0,29 | 3/5 |
| ΔOI 168 h > 0 | 1.035 | +4,93 | 0,35 | 2/5 |
| OI > Mittel 24 h | 839 | +21,10 | 1,43 | 4/5 |
| ΔOI-Wert 24 h > 0 | 772 | +5,92 | 0,57 | 3/5 |
| ΔOI 24 h < 0 (Gegenteil) | 1.010 | −9,13 | −0,55 | 2/5 |

**Der saubere Vergleich ist der Split:** dasselbe MACD-Signal, nur danach
geteilt, ob OI in den 24 h davor gestiegen oder gefallen ist.

| | OI steigt | OI fällt | Differenz |
|---|---|---|---|
| Suche | −4,82 bp (n=1.321) | −20,31 bp (n=1.464) | **+15,49 bp** |
| Holdout | +15,93 bp (n=886) | −9,13 bp (n=1.010) | **+25,05 bp** |

Der Filter schlägt in **beiden** Zeiträumen sowohl sein Gegenteil als auch
„kein Filter". Das ist mehr, als die meisten Filter in diesem Projekt geschafft
haben — acht andere sind an genau dieser Stelle gescheitert.

**Und trotzdem reicht es nicht:** t = 0,16 bzw. 1,20 über die Märkte, t = −0,32
über alle Trades. Bei 21 gerechneten Kombinationen liegt die Bonferroni-Schwelle
bei t > 3,09. Der Effekt ist nicht von Rauschen zu unterscheiden — und im
Suchzeitraum bleibt er **negativ**, er ist also bestenfalls „weniger schlecht".

Wie leicht man sich hier täuscht, zeigt „ΔOI 1 h > 0": **+21,21 bp** im
Suchzeitraum — die beste Zahl der ganzen Tabelle — und **+0,59 bp** im Holdout.
Wer aus sieben Lesarten die beste auswählt, wählt Rauschen aus.

---

## 3. Das Management ist hier der größere Hebel als der Filter

Hauptdefinition, ehrlicher Fill, Suchzeitraum:

| | n | bp/Trade | Ø R | Treffer | Ø Gew. R | Ø Verl. R | Ø im Markt |
|---|---|---|---|---|---|---|---|
| **M0** kein Stop, dreht am Gegensignal | 1.050 | **−29,24** | −0,146 | 35,8 % | 3,52 | **−2,19** | 98,1 % |
| **M1** harter Stop, 2 Boxen | 1.321 | **−4,82** | −0,024 | 20,7 % | 3,83 | −1,03 | 50,7 % |
| **M2** + Break-even + Trailing | 1.437 | −23,07 | −0,115 | 28,9 % | **1,23** | −0,66 | 11,5 % |

**Der harte Stop bringt +24,4 bp je Trade.** Das ist etwas anderes als bei der
Renko-Trail-Untersuchung, wo derselbe Baustein nur 0,16 bp gekostet hat — und
der Grund ist lehrreich:

> Dort war das Ausstiegssignal **schnell** (zwei Gegen-Bricks). Ein Verlust
> wurde ohnehin früh beendet, der Stop änderte wenig.
>
> Hier ist das Ausstiegssignal **langsam**: der MACD muss zurückkreuzen. Ohne
> Stop läuft der durchschnittliche Verlust auf **−2,19 R**, der schlimmste auf
> **−40,90 R**, bei 4,1 Tagen Haltedauer. Der Stop kürzt das auf 1,7 Tage.

**Je träger dein Ausstiegssignal, desto teurer ist ein fehlender Stop.** MACD
auf Renko-Bricks ist ein träges Ausstiegssignal.

Das Trailing (M2) macht es wieder kaputt: Es drückt den durchschnittlichen
Gewinn von 3,83 R auf **1,23 R** und die Zeit im Markt auf 11,5 %. Dasselbe
Muster wie bei Renko-Trail.

---

## 4. Risiko-Treue und Tageslimit

Hauptdefinition, ehrlicher Fill, Suchzeitraum:

| | Verlust > 1,2 R | größter Verlust | Ø Tage < −3 % | Ø max. DD | Ø Rendite |
|---|---|---|---|---|---|
| M0 kein Stop | **39,8 %** | **−40,90 R** | 13,7 | 31,2 % | −12,5 % |
| M1 harter Stop | **0,0 %** | −1,09 R | 3,5 | 20,3 % | −3,6 % |
| M2 + Trailing | 0,0 % | −1,09 R | 1,5 | 16,9 % | −12,4 % |

**Vier von zehn Trades reißen ohne Stop das geplante Risiko** — bei diesem
Aufbau noch deutlich mehr als bei Renko-Trail (25,8 %), weil das
Ausstiegssignal träger ist. Der schlimmste Einzeltrade kostet **41 R**: geplant
waren 0,5 % des Kontos, verloren gingen gut 20 %.

Mit Stop: **kein einziger Trade** über 1,2 R Verlust, schlimmster −1,09 R. Der
2-%-Stop ist hier so weit, dass ihn keine Kurslücke der sechs Märkte
übersprungen hat — anders als beim engeren ATR-Stop von Renko-Trail.

Tage über dem 3-%-Tageslimit — die Größe, an der über 95 % aller
Prop-Challenges scheitern: **13,7 → 3,5 → 1,5.**

Im Holdout: M0 +3,8 % Rendite bei 10,0 Limit-Tagen, M1 +2,8 % bei 2,3 Tagen,
M2 −5,0 % bei 0,8 Tagen.

---

## 5. Urteil nach den vorab festgelegten Kriterien

| Kriterium | Ergebnis |
|---|---|
| 1. bp/Trade > 0 im Suchzeitraum (ehrlicher Fill) | ❌ **−4,82 bp** |
| 2. gleiches Vorzeichen im Holdout | ❌ Suche −4,82 / Holdout +15,93 |
| 3. OI-Filter schlägt „kein Filter" **und** sein Gegenteil | ✅ in beiden Zeiträumen |
| 4. t > 3,09 (Bonferroni, 21 Kombinationen) | ❌ t = 0,16 (Suche), 1,20 (Holdout) |

**Drei von vier verfehlt: nicht tragfähig.** Es werden jetzt keine Parameter
nachjustiert — das war vorher so festgelegt.

Kriterium 3 ist trotzdem bemerkenswert. Der OI-Filter ist der erste Filter in
diesem Projekt, der in beiden Zeiträumen sowohl sein Gegenteil als auch die
ungefilterte Variante schlägt. Er ist nur zu schwach, um die Kosten zu tragen:
16 bp Roundtrip gegen 15–25 bp Trennschärfe, bei t ≈ 1.

---

## 6. Was daraus praktisch folgt

1. **Der Strategietester auf dem Renko-Chart lügt** — nicht aus Bosheit, sondern
   weil Brick-Preise keine handelbaren Zeitpunkte sind. Für dieses Setup:
   11,5 bis 37,5 bp je Trade zu gut. Wer die Strategie beurteilen will, muss
   auf Zeitbars zurückrechnen. Genau dafür ist der Code hier:
   `--config configs/tradingview_renko_1pct.yaml --variant MACD1`.

2. **Der Stop ist bei diesem Aufbau nicht optional.** +24,4 bp je Trade, und
   der schlimmste Trade fällt von −41 R auf −1,09 R. Ohne ihn hängt das Ergebnis
   an vier von zehn Trades, die weiter laufen als geplant.

3. **Kein Trailing.** Es kostet hier 18,3 bp je Trade und schneidet den
   Durchschnittsgewinn um zwei Drittel. Es kauft ruhigere Tage (1,5 statt 3,5
   über dem Limit) — wenn du ein Tageslimit hast, kann das den Preis wert sein.
   Sonst nicht.

4. **Der OI-Gedanke ist nicht falsch, nur zu schwach.** Steigendes OI trennt
   gleichsinnig in beiden Zeiträumen. Als alleiniger Filter trägt er die Kosten
   nicht. Wenn du ihn behalten willst: als **Größenregel** statt als
   Ein/Aus-Filter (kleiner handeln, wenn OI fällt) — dann kostet ein Fehlurteil
   weniger.

5. **Weniger handeln.** SOL erzeugt 389 Signale im Jahr, BTC 94. Bei 16 bp
   Roundtrip kostet das SOL-Konto allein **6,2 % im Jahr** an Reibung, bevor
   irgendetwas passiert ist.

---

## Einschränkungen

* **Renko-Nachbau, nicht TradingView-Code.** Boxgröße, Quelle und
  2-Boxen-Umkehr sind nachgebaut; die Reihenfolge Hoch/Tief innerhalb einer
  Stunde ist ohne Tickdaten unbekannt und wurde **pessimistisch** gewählt.
  TradingViews genaue Brick-Konstruktion (Anker, Rundung) kann leicht abweichen.
* **Die Fill-Differenz ist der belastbare Teil, nicht die exakte Zahl eines
  bestimmten Testers.** Gemessen wurde „Fill am Brick-Level gegen Fill zum
  Bar-Schluss".
* **Binance-Spot-Kurse, Binance-Futures-OI.** Andere Börse, andere Zahlen.
* **OI erst ab 2023-01** verfügbar — kürzerer Zeitraum als die übrigen
  Untersuchungen, entsprechend weniger Aussagekraft.
* **Nur die Long/Short-Symmetrie aus der Beschreibung.** Steigendes OI wird für
  beide Richtungen verlangt; „positives OI nur für long, negatives für short"
  ist als Gegenbedingung mitgerechnet (ΔOI < 0) und ist schlechter.
