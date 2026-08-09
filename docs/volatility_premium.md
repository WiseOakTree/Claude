# Volatilitäts-Risikoprämie und Optionshandel — der erste echte Edge

Vorschlag: Volatilität nicht als Risiko behandeln, sondern gezielt ausnutzen —
über Optionshandel oder Volatilitätsarbitrage.

**Ergebnis: Zum ersten Mal ein statistisch belastbarer, ökonomisch begründeter
Edge. Er ist im Kraken-Prop-Konto nicht handelbar — und würde die Challenge
auch dann nicht bestehen.**

Beides ist wichtig und wird unten getrennt belegt.

## Datengrundlage

Erstmals eine echte Optionsdatenquelle: **DVOL**, der Volatilitätsindex von
Deribit (dem dominierenden Krypto-Optionsmarkt) — die 30-Tage-implizite
Volatilität, also das, was der Markt an künftiger Schwankung *einpreist*.

| | |
|---|---|
| Quelle | Deribit `get_volatility_index_data`, 12h-Auflösung |
| Zeitraum | 2021-03 bis 2026-08 (**5,4 Jahre**, 3.915 Punkte je Coin) |
| Assets | BTC, ETH |
| Preise | Binance 1h → Tagesbasis |

## 1. Die Prämie ist real

Gemessen: implizite Vol (DVOL) gegen die Vol, die in den **darauf folgenden**
30 Tagen tatsächlich eintrat.

| | BTC | ETH |
|---|---|---|
| Implizite Vol (Median) | 56,4 % | 70,2 % |
| Realisierte Vol danach (Median) | 48,5 % | 65,6 % |
| **VRP = IV − RV** | **+10,47 pp** | +7,31 pp |
| Anteil positiv | **72,3 %** | 64,5 % |
| t (überlappungskorrigiert) | **4,12** (p = 0,0001) | 1,57 (p = 0,12) |

Bei BTC hält die Signifikanz auch nach Korrektur für überlappende Fenster —
die Hürde, an der **jedes** andere Signal dieser Untersuchung gescheitert ist
(Coinbase-Premium, DVOL-Richtung, Tech-Kopplung).

Ökonomisch ist das kein Zufallsfund, sondern eine **Versicherungsprämie**:
Optionsverkäufer tragen Gap-Risiko und werden dafür bezahlt. Dieselbe Prämie
ist an Aktien-, Zins- und Rohstoffmärkten seit Jahrzehnten dokumentiert.

### Nebenbefund: DVOL ist der bessere Vol-Schätzer

| Schätzer für die kommende 30-Tage-Vol | Korrelation | MAE |
|---|---|---|
| **DVOL (implizit, vorausschauend)** | **+0,604** | 15,30 pp |
| trailing 30T realisierte Vol | +0,399 | 16,43 pp |

## 2. Die Prämie geerntet: delta-gehedgter Short-Straddle

Monatlich einen 30-Tage-ATM-Straddle zum DVOL-Preis verkaufen, täglich
delta-neutral mit Spot hedgen. 64 Monate.

| Szenario | Median/Monat | Mittel | Trefferquote | Sharpe | schlechtester Monat |
|---|---|---|---|---|---|
| ideal (keine Reibung) | +2,20 % | +2,69 % | 69 % | 1,80 | −10,4 % |
| **Vol-Spread 5 % + 10 bp Hedge** | **+1,17 %** | **+1,56 %** | **62 %** | **1,08** | −11,6 % |
| Vol-Spread 10 % + 16 bp Hedge | +0,24 % | +0,59 % | 52 % | 0,42 | −12,6 % |

Realistischer Fall: **+149 % über 64 Monate** (≈ +18,4 % p.a. bei 13,8 % Vola,
Sharpe **1,33**), maximaler Drawdown **11,6 %**.

Positiver Median **und** positiver Mittelwert bei begrenztem Tail — das
unterscheidet diesen Fund von allem Vorherigen. Beachte aber die dritte Zeile:
Der Edge ist **reibungsempfindlich**. Bei 10 % Vol-Spread bleibt fast nichts.

## 3. Warum es die Challenge trotzdem nicht löst

### Hindernis A: Kraken hat keine Optionen

Direkt gegen die Kraken-APIs geprüft:

| | |
|---|---|
| Spot-Paare | 1.428 |
| Futures-Instrumente | 294 (`flexible_futures`, `futures_inverse`) |
| **Optionen** | **0** |

Die Prämie steckt in der Optionsprämie. Ohne Option gibt es nichts zu
kassieren — man trägt nur das Gamma-Risiko. **Der Edge ist im Challenge-Konto
strukturell nicht erreichbar**, unabhängig davon, wie gut er ist.

### Hindernis B: Er würde auch dann nicht reichen

Angenommen, es gäbe die Optionen. Gegen die Challenge-Regeln (90-Tage-Fenster):

| Hebel | 90T-Rendite | 90T-Drawdown | Pass-Rate |
|---|---|---|---|
| 1× Notional | +3,6 % | 5,2 % | **12,6 %** |
| 2× | +7,1 % | 10,3 % | 7,0 % |
| 3× | +10,6 % | 15,4 % | 0,3 % |
| 5× | +16,2 % | 24,9 % | 0,0 % |

Verhältnis Rendite/Drawdown: **0,69**. Die Challenge verlangt **1,67**.

Hochskalieren hilft nicht — bei 3× wird das Renditeziel zwar erreicht, aber der
Drawdown ist dann zweieinhalbfach über dem Limit. **Rendite und Drawdown
skalieren gemeinsam**; dieselbe Mauer wie in [`altdata_test.md`](altdata_test.md).

Ein Sharpe von 1,33 ist ein gutes Investmentergebnis. Für „+10 % in 90 Tagen
ohne 6 % Drawdown" bräuchte es Sharpe ~3.

## 4. Was ohne Optionen übrig bleibt — getestet

### DVOL als Richtungssignal: fällt durch

Der auffälligste Rohwert der ganzen Untersuchung war der DVOL-z-Score
(90 Tage) gegen 20-Tage-Folgerenditen: IC **+0,147**, naiv p = 3·10⁻¹⁰.
Ökonomisch plausibel („Angst kaufen"). Vier Prüfungen:

| Prüfung | Ergebnis |
|---|---|
| Überlappungskorrektur (n_eff = 91) | p = **0,164** → nicht signifikant |
| Quintile monoton? | Q1 −2,3 %, Q3 +3,6 %, Q4 +2,8 %, **Q5 +2,0 %** → nein |
| Out-of-Sample | 1. Hälfte IC +0,276 → 2. Hälfte **−0,004** |
| Als Strategie (beste Variante) | Pass-Rate **6,9 %** |

Vollständiger Zusammenbruch out-of-sample. Der naive p-Wert war ein
Überlappungsartefakt.

### DVOL als Sizing-Eingabe: kleine, echte Verbesserung

Der eine übertragbare Nutzen: Da DVOL die kommende Vol besser prognostiziert,
kann es das trailing RV im Vol-Targeting ersetzen
([`volatility_targeting.md`](volatility_targeting.md)).

| Zielvola | Schätzer | 90T-Drawdown | Pass-Rate |
|---|---|---|---|
| 15 % | trailing RV | 7,4 % | 21,0 % |
| 15 % | **DVOL** | **5,6 %** | 17,2 % |
| 20 % | trailing RV | 9,7 % | 14,1 % |
| 20 % | **DVOL** | **7,4 %** | 14,8 % |
| 25 % | trailing RV | 12,1 % | 2,5 % |
| 25 % | **DVOL** | **9,2 %** | **12,1 %** |

Der Drawdown sinkt **durchgängig** um 2–3 Prozentpunkte bei gleicher oder
leicht besserer Rendite. Das ist eine reale, wenn auch kleine Verbesserung —
und der einzige Teil dieses Kapitels, der im Challenge-Konto ankommt.

*(Die Pass-Raten liegen hier niedriger als in `volatility_targeting.md`, weil
dieser Datensatz ab 2021-03 beginnt und damit mehr Bärenmarkt enthält. Der
Vergleich innerhalb der Tabelle ist gültig, der über Dokumente hinweg nicht.)*

## Fazit

Zum ersten Mal ein Edge, der alle Prüfungen besteht: ökonomisch begründet,
statistisch signifikant nach Überlappungskorrektur, positiv über 64 Monate,
mit Sharpe 1,33 nach realistischen Kosten.

**Und er hilft bei dieser Aufgabe nicht** — aus zwei unabhängigen Gründen, von
denen jeder allein genügen würde: Kraken bietet keine Optionen, und selbst mit
Optionen läge das Verhältnis Rendite/Drawdown bei 0,69 statt der nötigen 1,67.

Das ist ein präziseres Ergebnis als „funktioniert nicht". Es zeigt, wo der Edge
tatsächlich liegt: **in einem Instrument, das die Challenge nicht anbietet, und
auf einer Zeitskala, die das 90-Tage-Fenster nicht zulässt.** Ein Sharpe-1,33-
Verfahren ist eine gute Anlage über Jahre — kein Werkzeug für einen
Drei-Monats-Sprint mit 6-%-Drawdown-Limit.

Praktisch übertragbar bleibt genau eines: **DVOL statt trailing RV für die
Positionsgröße** — 2–3 Prozentpunkte weniger Drawdown, kostenlos.
