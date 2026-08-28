# Nachtrag: derselbe Aufbau auf Heikin-Ashi-Kerzen

Ergänzung zu [`liq_macd.md`](liq_macd.md). Der Nutzer hatte den Chart auf
**Heikin Ashi** gestellt — der MACD lief also auf HA-Schlusskursen, nicht auf
echten. Dieselbe Leiter, dieselben Märkte, dieselben 12 bp Kosten,
**Fill immer zum echten Kurs**.

---

> ## Der Befund in drei Sätzen
>
> **Heikin Ashi schadet nicht — es hilft ein wenig.** In allen acht Vergleichen
> besser als echte Kerzen, um **+0,05 bis +2,96 bp**. Das ist konsistent, aber
> winzig gegen die Lücke von 13–21 bp.
>
> **Mit HA schlägt eine Stufe erstmals den Zufallseinstieg in beiden
> Zeiträumen:** 1h + 4h HA plus Level als Ziel, 44,5 % gegen 44,1 % (Suche) und
> **49,2 % gegen 46,4 %** (Holdout). Der Vorsprung in der Suche ist mit 0,4
> Punkten allerdings nichts.
>
> **Die 4h-Bestätigung schadet auch auf HA** — −0,95 bp in beiden Zeiträumen.
> Der Befund aus [`liq_macd.md`](liq_macd.md) bleibt bestehen.

---

## Die Leiter auf Heikin Ashi

### Suchzeitraum (6 Märkte)

| | Aufbau | n | Treffer | brutto bp | netto bp | t | Märkte + |
|---|---|---|---|---|---|---|---|
| **H0** | **Zufallseinstieg (Kontrolle)** | — | **44,1 %** | — | −19,04 | — | — |
| H1 | nur 1h-MACD auf HA | 13.121 | 43,2 % | −8,09 | −20,09 | −38,8 | 0/6 |
| H2 | 1h + 4h HA gleichgerichtet | 5.479 | 42,5 % | −9,04 | −21,04 | −26,3 | 0/6 |
| H3a | H2 + Einstieg **am** Level | 1.960 | 43,9 % | −7,34 | −19,34 | −14,4 | 0/6 |
| **H3b** | **H2 + Level als Ziel** | 1.968 | **44,5 %** | −6,55 | **−18,55** | −13,8 | 0/6 |

### Holdout (5 Märkte ohne BTC)

| | Aufbau | n | Treffer | brutto bp | netto bp | t | Märkte + |
|---|---|---|---|---|---|---|---|
| **H0** | **Zufallseinstieg** | — | **46,4 %** | — | −16,27 | — | — |
| H1 | nur 1h-MACD auf HA | 4.525 | 47,7 % | −2,76 | −14,76 | −16,6 | 0/5 |
| H2 | 1h + 4h HA gleichgerichtet | 1.862 | 46,9 % | −3,71 | −15,71 | −11,3 | 0/5 |
| H3a | H2 + Einstieg am Level | 671 | 48,3 % | −2,06 | −14,06 | −6,1 | 0/5 |
| **H3b** | **H2 + Level als Ziel** | 664 | **49,2 %** | −0,99 | **−12,99** | −5,6 | 0/5 |

**H3b ist die erste Stufe in dieser ganzen Untersuchungsreihe, die den
Zufallseinstieg in beiden Zeiträumen schlägt.** Ehrlich dazu: In der Suche sind
es 0,4 Prozentpunkte — das ist nichts. Erst im Holdout sind es 2,8 Punkte.
Und weiterhin: **0 von 6 bzw. 0 von 5 Märkten positiv.**

---

## Heikin Ashi gegen echte Kerzen — direkt gegenübergestellt

netto bp, 12 bp Kosten, Fill zum echten Kurs in beiden Fällen:

| | echte Kerzen | Heikin Ashi | Differenz |
|---|---|---|---|
| **Suche** | | | |
| nur 1h-MACD | −20,14 | −20,09 | **+0,05** |
| 1h + 4h gleichgerichtet | −21,44 | −21,04 | **+0,40** |
| + Einstieg am Level | −20,87 | −19,34 | **+1,53** |
| + Level als Ziel | −19,42 | −18,55 | **+0,87** |
| **Holdout** | | | |
| nur 1h-MACD | −15,18 | −14,76 | **+0,43** |
| 1h + 4h gleichgerichtet | −17,04 | −15,71 | **+1,33** |
| + Einstieg am Level | −17,01 | −14,06 | **+2,96** |
| + Level als Ziel | −14,08 | −12,99 | **+1,09** |

**Acht von acht Vergleichen zugunsten von HA.** Das ist mehr Konsistenz, als
die meisten Befunde dieses Projekts erreicht haben — und es ist trotzdem viel
zu klein: Im besten Fall +2,96 bp gegen eine Lücke von 14 bp.

Der Grund ist plausibel: HA glättet, der MACD kreuzt seltener und
zusammenhängender. Das entfernt einen Teil der schlechtesten Signale (3 bis 5 %
weniger Signale) — es fügt aber keine Information hinzu, weil HA nur eine
Transformation derselben OHLC-Daten ist.

**Einordnung zum früheren Befund:** [`heikin_ashi.md`](heikin_ashi.md) kam zu
„HA bringt nichts". Das galt für die klassische HA-Trendfolge (Farbwechsel) und
einen HA-Richtungsfilter. Für **MACD auf HA** in dieser Kombination ist der
Beitrag klein, aber konsistent positiv. Der Unterschied ist real und wird hier
festgehalten.

---

## Die Abrechnungsfalle — und eine Korrektur

`HA_close = (open + high + low + close) / 4` ist **kein handelbarer Preis**.
Wer Signale auf HA rechnet und den Gewinn auch mit HA-Preisen misst, misst
nicht das, was auf dem Konto ankommt.

Dieselben HA-Signale, einmal zum echten Kurs gefüllt, einmal mit HA-Preisen:

| | echt gefüllt | mit HA-Preisen | Verzerrung |
|---|---|---|---|
| **Suche** | | | |
| nur 1h-MACD auf HA | −20,09 | −24,27 | **−4,18 bp** |
| 1h + 4h HA | −21,04 | −28,35 | **−7,31 bp** |
| + Einstieg am Level | −19,34 | −27,53 | **−8,19 bp** |
| + Level als Ziel | −18,55 | −24,92 | **−6,37 bp** |
| **Holdout** | | | |
| nur 1h-MACD auf HA | −14,47 | −18,36 | −3,89 bp |
| 1h + 4h HA | −15,67 | −22,35 | −6,68 bp |
| + Einstieg am Level | −15,59 | −21,13 | −5,53 bp |
| + Level als Ziel | −13,00 | −19,61 | −6,61 bp |

**Die Verzerrung geht hier in die andere Richtung als in
[`heikin_ashi.md`](heikin_ashi.md).** Dort machte die HA-Abrechnung eine
verlierende Strategie scheinbar profitabel (+22 bis +40 bp). Hier macht sie das
Ergebnis um 4 bis 8 bp **schlechter**.

Der Grund ist mechanisch: Bei dieser Konstruktion ist
`HA_high = max(High, HA_open, HA_close) ≥ High` und
`HA_low = min(Low, HA_open, HA_close) ≤ Low`. Die HA-Kerze ist also **nie
schmaler** als die echte — beide Klammerseiten werden häufiger berührt, und
weil bei Gleichstand pessimistisch der Stop zählt, fällt das Ergebnis
schlechter aus.

**Die Lehre bleibt dieselbe, nur präziser formuliert:** Die HA-Abrechnung
verzerrt um mehrere Basispunkte, und **das Vorzeichen der Verzerrung hängt vom
Strategietyp ab.** Bei Trendfolge schönt sie, bei einer festen Klammer
verschlechtert sie. Man kann sich in beide Richtungen täuschen — deshalb: Fill
immer zum echten Kurs, immer.

---

## Marginaler Beitrag auf HA

| Schritt | Suche | Holdout |
|---|---|---|
| H1 → H2 **(4h-Bestätigung dazu)** | **−0,95 bp** | **−0,95 bp** |
| H2 → H3a (Einstieg am Level) | +1,70 bp | +1,65 bp |
| H2 → H3b **(Level als Ziel)** | **+2,49 bp** | **+2,71 bp** |

Auf HA ist das Bild aufgeräumter als auf echten Kerzen:

* **Die 4h-Bestätigung schadet weiterhin** — aber gleichmäßiger (−0,95 in
  beiden Zeiträumen statt −1,29 / −1,86).
* **Beide Liquiditäts-Lesarten tragen jetzt**, auch der Einstieg am Level
  (+1,70 / +1,65, auf echten Kerzen war das +0,57 / +0,03).
* **„Level als Ziel" bleibt der stärkste Baustein** (+2,49 / +2,71).

---

## Break-even

Ziel und Stop je 0,6 % = 60 bp, Kosten 12 bp → **nötig 60,0 %**.
Gemessen bei H3b: **44,5 %** (Suche) und **49,2 %** (Holdout).
Lücke: −15,5 bzw. −10,8 Prozentpunkte.

---

## Urteil

| Kriterium | H3b (beste Stufe) |
|---|---|
| 1. netto bp > 0 in der Suche | ❌ −18,55 |
| 2. gleiches Vorzeichen im Holdout | (beide negativ) |
| 3. Trefferquote über dem Zufall | ⚠️ **ja, aber +0,4 pp in der Suche** |
| 4. t > 2,64 | ❌ −13,8 |

**Nicht tragfähig.** Kriterium 3 ist erstmals nicht klar verfehlt — das ist
festzuhalten, ändert aber nichts am Urteil.

---

## Was daraus folgt

1. **Lass den Chart auf Heikin Ashi.** Er schadet nicht und hilft ein wenig —
   acht von acht Vergleichen. Nur: erwarte davon nichts Großes.
2. **Die 4h-Bestätigung bleibt der teuerste Baustein.** Auch auf HA.
3. **„Wohin läuft der Kurs" schlägt „wo steige ich ein".** Auf HA tragen beide
   Lesarten, die Ziel-Lesart doppelt so stark.
4. **Rechne nie mit HA-Preisen ab.** Nicht im Kopf, nicht im Tester. Der
   Unterschied ist hier 4 bis 8 bp — bei anderen Strategietypen 22 bis 40 bp in
   die andere Richtung.
5. **Die Lücke bleibt.** 44,5 % gegen nötige 60,0 %. Alle Verbesserungen dieser
   Untersuchung zusammen — HA, Liquidität als Ziel, 4h weglassen — bringen
   vielleicht 4 bis 5 bp. Gebraucht werden 19.
