# Validierung an einer echten SPX-Kette — kostenlos, und sie hält

> ## 🛑 HINFAELLIG — DIE ECHTEN REGELN WIDERLEGEN DIESES DOKUMENT
>
> Das Vanquish-Regelwerk-PDF sagt woertlich: **„SPX, XSP and VIX can only be
> traded long as single-leg calls/puts. No spreads, no selling to open."**
> Dazu **Intraday Trailing Drawdown** (nicht statisch) und **keine
> Overnight-Positionen**.
> Damit ist jede Rechnung in diesem Dokument gegenstandslos.
> **Siehe [`vanquish_regeln.md`](vanquish_regeln.md).**

Die drei genannten Quellen (OptionVue, Cboe LiveVol, Tastytrade) sind
kostenpflichtig. Es gibt aber eine **kostenlose**, die für die entscheidende
Frage reicht: die öffentliche CBOE-Schnittstelle für verzögerte Quotes.

**32.168 SPX-Optionen mit echten Bid/Ask, IV und Greeks.** Spot 7.723,55,
Stand 2026-08-05. Damit lassen sich beide offenen Punkte messen statt schätzen.

---

## 🛑 Zuerst: eine Selbstkorrektur, die fast in die Dokumente gewandert wäre

Beim ersten Vergleich sah es so aus, als hätte ich den Straddle systematisch zu
teuer bepreist: Modell **4,23 %** des Spot, echte Kette **3,05 %**. Ich hatte
bereits eine „Korrektur um Faktor 0,721" gerechnet und eine Erklärung parat
(VIX liege wegen des Skew über der ATM-Vol).

**Beides war falsch.** Beim Nachrechnen:

| | |
|---|---|
| `iv30` des Feeds | **13,21 %** (ich hatte 1321 % gelesen — Einheitenfehler) |
| gemessene ATM-Vol | 13,50 % |
| Verhältnis ATM / VIX | **1,022** — praktisch gleich |
| Modell-Straddle bei **heutiger** Vol | **3,09 %** |
| echte Kette | **3,06 %** |
| **Abweichung** | **0,03 pp** |

Die 4,23 % im Backtest sind der **Durchschnitt über 2016–2026** — mittlerer VIX
18,6 %. Heute steht er bei 13,2 %. **Es ist kein Modellfehler, es ist ein
ruhiger Tag.** Die Korrektur um 0,721 gilt nicht; die Zahlen aus
[`condor.md`](condor.md) bleiben.

*(Das ist die sechste Falle, die dieses Projekt produziert hat: eine
„Korrektur", die selbst der Fehler ist. Sie wäre durchgegangen, wenn ich die
Einheit nicht nachgerechnet hätte.)*

---

## Frage 1: Wie viel Prämie behält ein Iron Condor wirklich?

Gemessen an der echten Kette, 30 Tage Restlaufzeit, Mid-Preise:

| Strangle | Flügel | Kredit | in % Spot | **Anteil Straddle** | max. Verlust |
|---|---|---|---|---|---|
| ±2,0 % | 0,8 % | 29,50 | 0,382 % | **12,5 %** | 0,39 % |
| ±2,0 % | 2,5 % | 70,90 | 0,918 % | **30,1 %** | 1,61 % |
| ±3,0 % | 0,8 % | 20,70 | 0,268 % | **8,8 %** | 0,57 % |
| ±5,0 % | 0,8 % | 10,10 | 0,131 % | **4,3 %** | 0,84 % |
| ±5,0 % | 2,5 % | 20,95 | 0,271 % | 8,9 % | 2,32 % |

### Mein Modell gegen die echte Kette

| Konfiguration | Modell | echte Kette | Abweichung |
|---|---|---|---|
| ±2 % / 0,8 % | 10,6 % | 12,5 % | +1,9 pp |
| ±3 % / 0,8 % | 8,0 % | 8,8 % | +0,8 pp |
| ±5 % / 0,8 % | 4,1 % | 4,3 % | +0,2 pp |

**Das Modell trifft, und zwar leicht konservativ.** Die Realität ist 0,2 bis
1,9 Prozentpunkte besser als gerechnet.

**Damit ist die 4–11-%-Zahl an echten Preisen bestätigt.** Deine Schätzung von
20–25 % gilt — aber nur für **breite** Flügel: ±2 % / 2,5 % liefert real
**30,1 %**. Der Unterschied war nie die Skew, sondern immer die Flügelbreite.

---

## Frage 2: Die 4-Leg-Slippage

| Position | Bid | Ask | Spanne | % vom Mid |
|---|---|---|---|---|
| ATM Call | 127,20 | 128,10 | 0,90 | **0,7 %** |
| Short Put −5 % | 27,50 | 28,10 | 0,60 | 2,2 % |
| Long Put −6,5 % | 19,20 | 19,70 | 0,50 | 2,6 % |
| Short Call +5 % | 11,20 | 11,80 | 0,60 | 5,2 % |
| Long Call +6,5 % | 4,20 | 4,60 | 0,40 | **9,1 %** |

Für den Condor ±5 % / 1,5 %:

| | |
|---|---|
| Kredit zum Mid | 15,45 (0,200 % des Spot) |
| Kredit im schlechtesten Fall (Verkauf zum Bid, Kauf zum Ask) | 14,40 |
| Summe der halben Spannen über 4 Legs | **1,05 Punkte = 0,014 % des Spot** |
| **kompletter Roundtrip (rein + raus)** | **0,027 % des Nominals** |
| **davon in % des Kredits** | **14 %** |

**Deine Sorge ist berechtigt, aber die Größenordnung ist klein.** SPX ist
extrem liquide. Mein Modell hat 1 bp je Leg berechnet = 0,04 % je Einstieg —
also **das Anderthalbfache der gemessenen Kosten.** Auch hier war das Modell
konservativ.

Die Einschränkung bleibt: Das sind Spannen an einem **ruhigen Tag**. In einem
Vol-Schub weiten sie sich, und genau dann würde ein Stop auslösen. Der Faktor
dafür lässt sich aus einer Momentaufnahme nicht messen.

---

## Was die echte Kette zusätzlich zeigt: ich habe die falsche Konfiguration optimiert

Kredit im Verhältnis zum Maximalverlust:

| Konfiguration | Kredit/Risiko |
|---|---|
| ±2 % / 0,8 % | **1,29** |
| ±2 % / 2,5 % | 0,93 |
| ±3 % / 1,5 % | 0,68 |
| **±5 % / 1,5 %** (meine bisherige Wahl) | **0,27** |

Meine bisherige „beste" Konfiguration hat die **schlechteste Kapitaleffizienz**
von allen. Ich hatte auf Sharpe optimiert, nicht auf Ertrag je Risikoeinheit.

### Vollständiger Sweep, Stop bei 50 % des Maximalverlusts

| Strangle | Flügel | Kredit | max. Verlust | p.a. | Sharpe | Stopverlust |
|---|---|---|---|---|---|---|
| ±3,0 % | 3,5 % | 1,133 % | 2,37 % | +4,77 % | 1,54 | 1,18 % |
| ±4,0 % | 2,5 % | 0,671 % | 1,83 % | +3,61 % | 1,79 | 0,91 % |
| ±5,0 % | 2,5 % | 0,491 % | 2,01 % | +3,47 % | **2,07** | 1,00 % |
| **±5,0 %** | **3,5 %** | 0,617 % | 2,88 % | +4,63 % | **2,20** | 1,44 % |

---

## Die Endzahl, gegen den 6-%-Puffer

| Konfiguration | Nominal | Stopverlust | Anteil Puffer | überlebt | Ø p.a. | **$ auf 100k** |
|---|---|---|---|---|---|---|
| ±5 % / 3,5 % | 4× | 5,77 % | **96 %** | 98,1 % | +19,0 % | 19.021 $ |
| **±5 % / 2,5 %** | **4×** | **4,02 %** | **67 %** | **100,0 %** | **+14,4 %** | **14.405 $** |
| ±5 % / 1,5 % | 6× | 3,53 % | 59 % | 98,1 % | +13,1 % | 13.105 $ |
| ±5 % / 1,5 % | 10× | 5,88 % | 98 % | 90,7 % | +21,3 % | 21.276 $ |

**Die 20 %-Zeilen verlangen alle, dass ein einziges Stop-Ereignis 96–98 % deines
gesamten Risikokapitals frisst.** Danach handelst du mit Null Puffer weiter.
Das ist keine Konfiguration, das ist eine Wette.

---

## Was ich jetzt freigebe

> **±5 % Strangle, 2,5 % Flügel, 4× Nominal, Stop bei 50 % des Maximalverlusts.**
>
> **+14,4 % im Jahr. 100 % Überlebensrate über alle geprüften Jahresfenster.
> Ein Stop kostet 67 % des Puffers. Auf 100.000 $ bei vollem Split:
> rund 14.400 $.**

Und der Grund, warum ich das für belastbar halte, ist nicht die einzelne Zahl,
sondern **die Stabilität**: Vier verschiedene Modellierungswege — gekappte
Straddle-Näherung, echtes Condor-Modell mit Skew, Kalibrierung an einer echten
Kette, vollständiger Konfigurations-Sweep — landen alle zwischen **13 % und
16 %**. Das ist das erste Mal in diesem gesamten Projekt, dass eine Zahl unter
Methodenwechsel stabil bleibt.

**20–30 % bleiben außer Reichweite**, solange der Puffer 6.000 $ beträgt. Nicht
wegen der Strategie — wegen der Arithmetik zwischen Stopverlust und Puffer.

---

## Was weiterhin ungeprüft ist

- **Eine Momentaufnahme ist keine Historie.** Ich habe die Kette *eines* Tages
  bei VIX 13,2. Wie sich Kredit und Spannen bei VIX 30 oder 60 verhalten, sagt
  sie nicht. Genau dafür wären die kostenpflichtigen Quellen nötig.
- **Rollen statt Stoppen** ist weiterhin nicht modelliert.
- **Zehn Jahre Daten**, effektiv ~zehn unabhängige Jahresbeobachtungen.
- **Die Vanquish-Regeln** stammen aus deiner Recherche und sind nicht
  unabhängig verifiziert.

---

*Skripte: `research/echte_kette.py` (Condor und Spannen an der realen Kette),
`research/kalibrierung.py` (Vergleich Modell/Realität — enthält die widerlegte
Erstannahme), `research/final.py` (vollständiger Sweep mit Stop).
Datenquelle: `https://cdn.cboe.com/api/global/delayed_quotes/options/_SPX.json`
— kostenlos, verzögert, mit Bid/Ask und Greeks.*
