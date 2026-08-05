# Eigenes Kapital, eigener Hebel — die Frage ändert die Antwort

Ohne Challenge fällt das weg, was 95 % aller Fehlschläge verursacht hat: das
3-%-Tagesverlustlimit. Damit ist die Zielgröße nicht mehr die Pass-Rate,
sondern **Sharpe** — denn Sharpe ist das, was man hebeln kann.

Und damit gewinnt ein anderer Ansatz.

---

## 🛑 Zuerst eine Korrektur an meiner eigenen Rechnung

Die gesamte Untersuchung nannte eine Kostenschwelle von **16 bp je
Roundtrip**. Im Code wurde sie aber auf **jede Positionsänderung** angewandt:

```python
s = held*ret - COST*held.diff().abs()      # COST = 16 bp
```

Ein vollständiger Trade erzeugt zwei Positionsänderungen (rein und raus).
**Verrechnet wurden also 32 bp je Roundtrip — das Doppelte des Beabsichtigten.**

Das ist ein Fehler zu meinen Ungunsten: **Alle berichteten Zahlen dieses
Projekts sind unter doppelten Kosten gemessen.** Die Auswirkung:

| Asset | Größe | 32 bp/RT (berichtet) | **16 bp/RT (korrekt)** | Differenz |
|---|---|---|---|---|
| **BTC** | **0,35×** | 48,4 % | **53,8 %** | **+5,4** |
| BTC | 0,50× | 44,7 % | 44,9 % | +0,3 |
| ETH | 0,35× | 45,0 % | 45,7 % | +0,7 |
| SOL | 0,35× | 19,8 % | 20,3 % | +0,6 |
| XRP | 0,50× | 20,3 % | 22,3 % | +2,0 |

BTC 0,35× bei korrekten Kosten: **Suchzeitraum 53,4 %, Holdout 57,0 %.**

**Was sich dadurch nicht ändert:** Kein einziger Fehlschlag dieses Projekts
wird dadurch zum Erfolg. Die Alternativdaten (0,3–6 bp Signal) bleiben unter
jeder Kostenschwelle, die acht Filter bleiben durchgefallen, und die
Rangfolge der Ansätze ist unverändert. Der Effekt ist auf die Pass-Rate klein,
weil die Challenge ein Erstpassage-Problem ist. **Auf die Rendite ist er
groß** — und darum geht es ab hier.

---

## Der eigentliche Punkt: bei Gebühren geht es um deinen Anteil am Edge

Dein Bruttoertrag ist **45,7 bp je Trade**. Was davon ankommt:

| Gebühr je Roundtrip | dein Anteil am Edge | Rendite p.a. | Sharpe | Kelly-Hebel |
|---|---|---|---|---|
| 32 bp (Taker beidseitig, teuer) | 30 % | +19,0 % | 0,82 | 3,28× |
| **16 bp (Kraken-Taker, realistisch)** | **65 %** | **+26,5 %** | **1,07** | **4,26×** |
| 12 bp | 74 % | +28,4 % | 1,13 | 4,50× |
| 8 bp (Maker beidseitig) | 82 % | +30,4 % | 1,19 | 4,75× |
| 0 bp (theoretisch) | 100 % | +34,5 % | 1,31 | 5,23× |

**Deine Sorge ist berechtigt, aber die Größenordnung ist beherrschbar.**
Zwischen der teuersten und der billigsten Ausführung liegen **15,5 Prozentpunkte
Jahresrendite und 0,49 Sharpe**. Das ist viel — aber die Strategie stirbt
nicht daran. Sie stirbt erst bei **45,7 bp je Roundtrip**, und dorthin kommst
du nur, wenn du deutlich häufiger handelst.

**Der Grund, warum es beherrschbar bleibt: 39 Trades im Jahr.** Bei
2.190 Trades (der Bot-Frequenz) wäre dieselbe Gebühr tödlich
([`bots.md`](bots.md)). Deine niedrige Frequenz ist kein Nachteil — sie ist
genau das, was dich gebührenresistent macht.

**Praktisch:** Limit-Orders statt Market-Orders halbieren die Gebühr und
sparen zusätzlich den Spread. Bei 48 Stunden Haltedauer kostet dich ein
Limit-Fill ein paar Minuten Verzögerung — irrelevant.

---

## Was mit eigenem Kapital besser ist als die S/R-Strategie

Ohne die Kraken-Beschränkung wird der **beste Fund dieses Projekts endlich
handelbar**: die Volatilitäts-Risikoprämie. Sie war nur deshalb ausgeschlossen,
weil Kraken 0 Optionen anbietet — Deribit bietet sie.

Monatlich einen 30-Tage-ATM-Straddle verkaufen, täglich delta-neutral hedgen,
64 Monate:

| Szenario | Ø/Monat | p.a. | Sharpe | schlechtester Monat |
|---|---|---|---|---|
| ideal (keine Reibung) | +2,55 % | +33,4 % | 1,78 | −9,4 % |
| **realistisch (2 Vol-Punkte Spread, 5 bp Hedge)** | **+2,11 %** | **+26,7 %** | **1,49** | −9,9 % |
| + Deribit-Gebühren (~3 bp Notional) | +2,08 % | +26,3 % | 1,47 | −9,9 % |
| konservativ (4 Vol-Punkte, 10 bp, 6 bp) | +1,61 % | +19,5 % | 1,15 | −10,4 % |
| sehr konservativ (6 Vol-Punkte, 20 bp) | +0,97 % | +10,9 % | 0,71 | −11,2 % |

**Selbst im sehr konservativen Szenario bleibt Sharpe 0,71.** Das ist der
Unterschied zwischen einem echten Edge und einem gefundenen Muster: Er
verträgt Reibung.

---

## Der Direktvergleich

| | p.a. | Vol | **Sharpe** | max. DD | Kelly | bei 2× Hebel |
|---|---|---|---|---|---|---|
| S/R-Ausbruch BTC (16 bp) | +26,5 % | 25,0 % | 1,07 | −30,4 % | 4,26× | +53 % / DD −61 % |
| **Short-Straddle (VRP)** | **+26,3 %** | **17,0 %** | **1,47** | **−9,9 %** | 8,67× | **+53 % / DD −20 %** |
| BTC einfach halten | +3,2 % | 55,6 % | 0,34 | −76,6 % | 0,60× | +6 % / DD −153 % |

**Gleiche Rendite. Ein Drittel des Drawdowns.**

Und genau hier zahlt sich Sharpe aus: Bei 2× Hebel liefern beide ~53 % im
Jahr — aber die S/R-Strategie mit 61 % Drawdown und der Straddle mit 20 %.
Den einen hältst du durch, den anderen nicht.

Nebenbei: **BTC einfach zu halten war über diese 5,4 Jahre die mit Abstand
schlechteste der drei Anlagen** — +3,2 % p.a. bei 76,6 % Drawdown. Das ist die
Anlage, die praktisch jeder tatsächlich hat.

---

## Die Warnungen, ohne die das unseriös wäre

**1. Short-Straddle heißt Short Gamma. Das ist Versicherung verkaufen.**
Du kassierst regelmäßig kleine Prämien und zahlst selten sehr viel. Der
schlechteste Monat im Datensatz war −9,9 % — aber der Datensatz beginnt
2021-03 und enthält **kein Ereignis vom Typ März 2020** (BTC −50 % in zwei
Tagen). Ein solcher Tag kostet einen ungehedgten Straddle ein Vielfaches der
Jahresprämie. Der tägliche Delta-Hedge mildert das, beseitigt es aber nicht —
er reagiert erst *nach* der Bewegung.

**2. Kelly gilt hier nicht.** Die Formel unterstellt normalverteilte Renditen.
Short Gamma hat einen fetten linken Rand — Kelly unterschätzt das Risiko
systematisch. **Faustregel: höchstens ein Viertel Kelly**, also ~2× statt
8,67×. Wer bei dieser Strategie voll hebelt, wird irgendwann ausgelöscht,
egal wie gut der Backtest aussieht.

**3. Margin-Anforderungen wirken prozyklisch.** Deribit erhöht die
Margin, wenn die Volatilität steigt — also genau dann, wenn deine Position im
Minus ist. Zwangsschließung im schlechtesten Moment ist das reale
Ausfallszenario, nicht der Backtest-Drawdown.

**4. Es ist Arbeit.** Täglich delta-hedgen, 30-Tage-Straddles rollen,
Margin überwachen. Das ist kein „setzen und liegen lassen" — und wenn du das
Hedging automatisierst, brauchst du eine Infrastruktur, die auch nachts läuft.

**5. Die Simulation nutzt DVOL als Preis.** Das ist der Deribit-Vol-Index, kein
tatsächlich handelbarer Quote. Ich habe 2–6 Vol-Punkte Spread angesetzt; das
ist realistisch, aber es ist eine Annahme, keine Messung an echten
Orderbüchern.

---

## Wenn ich es mit eigenem Kapital machen müsste

```
1. NICHT gehebelt anfangen. 1,0x, ein Jahr, echtes Geld, kleine Summe.
   Der Backtest hat 64 Monate; deine Erfahrung hat null.

2. Kern:      Short-Straddle auf Deribit, ~50-70 % des Kapitals.
              Sharpe 1,47, Drawdown -10 %. Taeglich hedgen.

3. Beimischung: S/R-Ausbruch BTC, ~30 % des Kapitals.
              Sharpe 1,07, 39 Trades im Jahr, LIMIT-Orders.

4. Hebel:     Erst nach 12 Monaten Live-Erfahrung. Dann hoechstens 2x.
              Niemals Kelly folgen.

5. Gebuehren: Maker-Rebate-Stufen ansteuern. Zwischen 32 und 8 bp je
              Roundtrip liegen 11 Prozentpunkte Jahresrendite.
```

**Die realistische Erwartung: 20–27 % im Jahr bei 10–30 % Drawdown,
ungehebelt.** Das ist ein sehr gutes Ergebnis — und es ist ungefähr das
Doppelte dessen, was gute Aktienfonds liefern. Es macht dich nicht in einem
Jahr reich, und jeder, der dir etwas anderes verspricht, verkauft dir etwas.

**Und der ehrlichste Satz zum Schluss:** Die S/R-Strategie ist auf BTC
gefunden und auf BTC bestätigt worden; ETH/SOL/XRP tragen sie kaum. Die VRP
ist auf BTC signifikant (t = 4,12) und auf ETH **nicht** (t = 1,57). Beide
Ergebnisse stehen auf einem einzigen Instrument. Das ist die dünnste Stelle
dieser ganzen Untersuchung, und sie wird durch eigenes Kapital nicht dicker.

---

*Skripte: `research/eigenkapital.py` (beide Ansätze als Anlage,
Gebührensensitivität), `research/kosten_fix.py` (Auswirkung der
Kostenkorrektur).*
