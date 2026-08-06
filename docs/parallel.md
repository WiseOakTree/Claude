# Mehrere Konten statt mehr Hebel — richtig, und zwar strukturell

Der Gedanke ist nicht nur besser, er ist **mathematisch strikt besser**. Und
zwar aus einem Grund, der sich in einer Zeile sagen lässt:

> **Bei N Konten wächst der Puffer mit N mit. Bei Hebel nicht.**

---

## Der Kernvergleich: gleiches Gesamt-Nominal, anders verteilt

Basis: Strangle ±5 %, Flügel 2,5 %, Stop bei 50 % des Maximalverlusts
([`validierung.md`](validierung.md)). Stopverlust 1,00 % des Nominals.

| Aufbau | Gesamt-Nominal | Puffer | Stopverlust | **% des Puffers** | überlebt | **$ / Jahr** |
|---|---|---|---|---|---|---|
| 1 Konto, 4× | 4× | 6 % | 4,02 % | **67 %** | **100,0 %** | 14.405 $ |
| 1 Konto, 8× | 8× | 6 % | 8,04 % | **134 %** | 87,9 % | 27.183 $ |
| **1 Konto, 12×** | **12×** | **6 %** | **12,06 %** | **201 %** | **79,4 %** | 39.322 $ |
| 2 Konten je 4× | 8× | 12 % | 4,02 % | 67 % | **100,0 %** | 28.809 $ |
| **3 Konten je 4×** | **12×** | **18 %** | **4,02 %** | **67 %** | **100,0 %** | **43.214 $** |
| 3 Konten je 6× | 18× | 18 % | 6,03 % | 100 % | 93,5 % | 62.880 $ |

**Vergleiche Zeile 3 mit Zeile 5.** Beide haben **12× Gesamt-Nominal**:

| | 1 Konto, 12× | 3 Konten, je 4× |
|---|---|---|
| Stopverlust gegen Puffer | **201 %** | **67 %** |
| Überlebensrate | 79,4 % | **100,0 %** |
| Ertrag im Jahr | 39.322 $ | **43.214 $** |

**Mehr Geld *und* bessere Überlebensrate bei identischer Marktposition.** Das
ist selten — normalerweise kauft man Sicherheit mit Rendite. Hier nicht, weil
der Engpass nie das Kapital war, sondern der Puffer.

Bei 12× auf einem Konto ist das Konto **nach einem einzigen Stopp weg**
(12,06 % Verlust gegen 6 % Puffer). Bei 3 × 4× kostet derselbe Marktschock
jedes Konto 67 % seines Puffers — alle drei leben weiter.

---

## Der Haken: die Konten sind perfekt korreliert

Dieselbe Strategie auf drei Konten heißt, dass ein schlechter Monat **alle drei
gleichzeitig** trifft:

| | |
|---|---|
| P(ein Konto überlebt das Jahr) | 100,0 % |
| P(alle drei überleben) | **100,0 % — identisch** |
| P(mindestens eins überlebt) | **100,0 % — ebenfalls identisch** |

**Parallele Konten schützen nicht vor dem Ereignis. Sie schützen vor der
Größe.** Das ist der Unterschied zwischen „ich habe dreimal so viel Puffer" und
„ich habe drei unabhängige Wetten". Du hast Ersteres, nicht Letzteres.

Wenn ein Ereignis kommt, das 6 % je Konto reißt, sind alle drei gleichzeitig
weg. Die Anzahl der Konten hilft dagegen **nicht**.

---

## Echte Diversifikation: die Verfallszyklen versetzen

Was tatsächlich streut, ist nicht die Kontenzahl, sondern der **Zeitpunkt**.
Konto A startet Woche 1, B Woche 2, C Woche 3 — damit ist nie das gesamte
Kapital an einem Verfall exponiert:

| | Vol p.a. | Sharpe | schlechtester Zyklus |
|---|---|---|---|
| 1 Zyklus (synchron) | 1,65 % | 2,07 | −1,09 % |
| **3 versetzte Zyklen** | **1,14 %** | **2,69** | **−0,92 %** |

**Volatilität −31 %, Sharpe von 2,07 auf 2,69.** Und der schlechteste Zyklus
sinkt von 4,36 % auf 3,67 % des Kontos — von **73 % auf 61 % des Puffers.**

Das kauft dir ungefähr **eine Hebelstufe**.

---

## Die kombinierte Bauform

| Aufbau | schlechtester Zyklus | % Puffer | überlebt | Ø p.a. | **$ / Jahr** |
|---|---|---|---|---|---|
| 3 Konten, 1 Tranche, 4× | −4,36 % | 73 % | **100,0 %** | +14,3 % | **42.903 $** |
| **3 Konten, 3 Tranchen, 4×** | **−3,67 %** | **61 %** | **100,0 %** | +13,1 % | 39.285 $ |
| **3 Konten, 3 Tranchen, 5×** | −4,58 % | 76 % | 98,1 % | +16,3 % | **49.025 $** |
| 3 Konten, 3 Tranchen, 6× | −5,50 % | 92 % | 95,3 % | +19,3 % | 57.897 $ |

**Die zwei sinnvollen Punkte:**

```
KONSERVATIV   3 Konten, 3 versetzte Tranchen, 4x
              -> 39.285 $ im Jahr, 100 % Ueberlebensrate
              -> ein Stopp kostet 61 % des Puffers

AUSGEWOGEN    3 Konten, 3 versetzte Tranchen, 5x
              -> 49.025 $ im Jahr, 98,1 % Ueberlebensrate
              -> ein Stopp kostet 76 % des Puffers
```

Die 6×-Zeile mit 57.897 $ verlangt, dass ein Stopp **92 % des Puffers** frisst.
Das ist wieder die Kante, an der du 2024 gestanden hast.

### Kosten

| | |
|---|---|
| 3 Evaluierungen à ~400 $, 90,9 % Bestehensquote | **~1.320 $** |
| Dauer (parallel, nicht nacheinander) | ~142 Tage |
| Kommissionen | bereits in den Renditen enthalten (1 bp je Leg) |
| **Erwartungswert erstes Jahr** | **~41.600 $ bis 47.700 $** |

---

## Und das ist derselbe Mechanismus wie ganz am Anfang

In [`spielregeln.md`](spielregeln.md) war das Ergebnis: **Mehrfachantritt ist
der stärkste Hebel überhaupt** — 50,9 % → 63,0 % → 78,7 % für 132 $
Gesamteinsatz.

Das hier ist dieselbe Logik, angewandt auf **gefundete Konten statt auf
Versuche**. Beide Male gilt: Wenn eine Regel dich an einer festen Grenze
begrenzt, ist die Antwort nicht, härter gegen die Grenze zu drücken — sondern
mehr Grenzen zu haben.

**Es ist die einzige Idee in diesem gesamten Projekt, die zweimal unabhängig
funktioniert hat.**

---

## Was du vor dem Kauf klären musst

**1. Erlaubt Vanquish überhaupt identische Strategien auf mehreren Konten?**
Das ist die entscheidende Frage. Viele Prop-Firmen verbieten „Shotgunning" —
also dasselbe Setup parallel zu fahren, um die Varianz auf ihre Kosten
auszunutzen. Manche rechnen mehrere Konten für Risikozwecke **zusammen**, womit
der ganze Vorteil verschwindet.

**Formuliere es genau so bei der Nachfrage:** *„Darf ich auf zwei oder drei
gefundeten Konten dieselbe Strategie mit identischen Strikes gleichzeitig
handeln, oder werden die Konten für Risiko- und Auszahlungszwecke
zusammengefasst?"*

**2. Gilt die Konsistenzregel je Konto oder über alle Konten?** Bei drei
Konten mit identischen Positionen fallen Gewinntage zusammen — was eine
kontenübergreifende Konsistenzregel härter treffen könnte als eine je Konto.

**3. Gibt es eine Obergrenze für das gesamte gefundete Kapital?** „Max 2–3
Konten" heißt bei manchen Anbietern 300.000 $, bei anderen deckelt eine
Gesamtsumme das früher.

---

## Was diese Rechnung weiterhin nicht kann

- **Zehn unabhängige Datenjahre.** Die „100 % Überlebensrate" ruht auf etwa
  zehn Beobachtungen — mehr Konten ändern daran nichts, weil sie dieselben
  zehn Jahre erleben.
- **Kein Ereignis vom Typ März 2020 im Optionsteil** über die volle Bandbreite:
  Der Datensatz enthält COVID, aber nur einmal.
- **Die Vanquish-Regeln** stammen aus deiner Recherche, nicht aus einer
  unabhängigen Prüfung.
- **Der Iron Condor** ist an einer realen Kette kalibriert
  ([`validierung.md`](validierung.md)), aber an **einer** Momentaufnahme bei
  VIX 13,2.

---

*Skripte: `research/parallel.py` (Konten gegen Hebel, Korrelation, Staffelung),
`research/parallel2.py` (kombinierte Bauform und Kosten).*
