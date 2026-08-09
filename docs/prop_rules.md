# Welches Regelwerk passt zur Strategie? — und eine Korrektur

Frage: Wenn die gefundene Strategie ein Verhältnis Rendite/Drawdown von
0,95–1,39 liefert und Kraken 1,67 verlangt — wäre dann ein **anderer Anbieter**
die Lösung?

Die Frage ist richtig gestellt. Bei der Prüfung ist außerdem ein Fehler in
meiner bisherigen Auswertung aufgefallen.

## 🛑 Korrektur: meine Regelauslegung war zu streng

Zwei Punkte waren falsch modelliert:

| | bisher (falsch) | korrekt |
|---|---|---|
| Gewinnziel | musste am **Tag 90** erreicht sein | gilt, **sobald** es berührt wird |
| Drawdown | vom laufenden **Hoch** (trailing) | vom **Startguthaben** (statisch) |

Eine Challenge endet, sobald das Ziel erreicht ist — danach handelt man nicht
weiter und kann es auch nicht wieder verlieren. Und Kraken misst den
6-%-Drawdown statisch vom Startguthaben.

**Auswirkung auf alle bisher berichteten Pass-Raten:**

| Strategie | bisher berichtet | korrekt | Differenz |
|---|---|---|---|
| BTC einfach halten | 0,0 % | **24,9 %** | +24,9 pp |
| Vol-Targeting 15 % | 16,3 % | **24,8 %** | +8,4 pp |
| S/R-Ausbruch (≥6, 48 h) | 17,0 % | **33,9 %** | +16,9 pp |

Der Haupttreiber ist „Ziel sofort" (+23,1 pp bei BTC), nicht der Drawdown
(+1,8 pp). **Die Challenge ist deutlich passierbarer, als ich berichtet habe.**

Die *relative* Rangfolge bleibt: S/R-Ausbruch > Vol-Targeting ≈ BTC halten.
Auch die Aussage, dass BTC-Halten und Vol-Targeting gleichauf liegen, bleibt.
Aber die absoluten Zahlen in den älteren Dokumenten sind zu pessimistisch.

## Welche Regel ist der größte Hebel?

Getestet mit der S/R-Strategie (≥6 Berührungen, 48 h halten).

### 1. Das Zeitlimit — der zweitgrößte Hebel

| Regelwerk | 30 T | 60 T | 90 T | 180 T | **ohne Limit** |
|---|---|---|---|---|---|
| Kraken Starter (10 % / 6 %) | 13,3 % | 27,0 % | 33,1 % | 39,5 % | **40,2 %** |
| 8 % Ziel / 10 % DD | 20,8 % | 34,0 % | 37,9 % | 43,5 % | **43,6 %** |
| **6 % Ziel / 10 % DD** | 28,1 % | 43,2 % | 49,3 % | 59,7 % | **60,3 %** |

Von 30 auf 90 Tage verdreifacht sich die Pass-Rate. Über 180 Tage hinaus
bringt „kein Limit" fast nichts mehr — die entscheidende Grenze liegt bei
etwa einem halben Jahr.

### 2. Das Gewinnziel schlägt das Drawdown-Limit deutlich

| Ziel ↓ / max. DD → | 5 % | 6 % | 8 % | 10 % | 15 % |
|---|---|---|---|---|---|
| **5 %** | 50,9 | 52,1 | 52,1 | 52,1 | 52,1 |
| **6 %** | 49,1 | 49,3 | 49,3 | 49,3 | 49,3 |
| **8 %** | 37,6 | 37,9 | 37,9 | 37,9 | 37,9 |
| **10 %** | 32,8 | **33,1** | 33,1 | 33,1 | 33,1 |

**Die Spalten sind praktisch identisch — das Drawdown-Limit ist ab 6 % egal.**
Das Gewinnziel dagegen entscheidet alles: von 10 % auf 6 % steigt die
Pass-Rate von 33 % auf 49 %.

Das ist ein wichtiger Befund: Ein Anbieter, der mit „großzügigen 12 %
Drawdown" wirbt, verkauft eine Regel, die bei dieser Strategie **nichts**
bringt. Entscheidend ist ein niedriges Ziel.

### 3. Die Tagesverlust-Grenze — der größte Hebel überhaupt

| Tagesverlust-Limit | Pass-Rate (10 % / 10 %, ohne Zeitlimit) |
|---|---|
| 2 % | 35,3 % |
| **3 % (Kraken)** | **40,2 %** |
| 4 % | 53,8 % |
| 5 % | 61,0 % |
| keins | **78,1 %** |

**Von 3 % auf 5 % steigt die Pass-Rate um die Hälfte; ganz ohne Limit fast auf
das Doppelte.** Das ist der stärkste einzelne Regelparameter — und der, den
Anbieter am seltensten hervorheben.

### 4. Trailing- gegen statischen Drawdown: fast egal

| Regelwerk | statisch | trailing |
|---|---|---|
| 10 % / 6 % | 40,2 % | 40,1 % |
| 8 % / 10 % | 43,6 % | 43,6 % |

Weil die Challenge beim Erreichen des Ziels endet, kommt ein Trailing-Stop
selten zum Tragen. Der in Foren viel diskutierte Unterschied ist bei dieser
Strategie bedeutungslos.

## Die Einkaufsliste

Nach Wirkung geordnet, für einen Anbieter, bei dem diese Strategie besser
abschneidet als bei Kraken:

| Priorität | Regel | Wirkung |
|---|---|---|
| **1** | **Tagesverlust ≥ 5 % oder keiner** | 40 % → 61–78 % |
| **2** | **Gewinnziel 6 % statt 10 %** | 33 % → 49 % |
| **3** | **Zeitlimit ≥ 180 Tage oder keins** | 33 % → 40 % |
| 4 | Drawdown-Limit | **ab 6 % ohne Wirkung** |
| 5 | statisch vs. trailing | ohne Wirkung |

Ein Regelwerk mit **6 % Ziel, 5 % Tagesverlust, kein Zeitlimit** käme
rechnerisch auf deutlich über 60 % — gegenüber 33 % bei Kraken.

## Zwei Warnungen dazu

**Erstens: Das Geschäftsmodell passt sich an.** Anbieter mit lockeren Regeln
verlangen in der Regel höhere Gebühren, geringere Gewinnbeteiligung, oder
haben zusätzliche Klauseln (Mindesthandelstage, Konsistenzregeln, die
verbieten, dass ein einzelner Tag zu viel zum Gewinn beiträgt). Eine
Konsistenzregel würde genau diese Strategie treffen, weil ihre Rendite aus
wenigen großen Ausbrüchen kommt. **Vor dem Kauf gezielt danach suchen.**

**Zweitens: Die 33,9 % bleiben eine ausgewählte Zahl.** Für die S/R-Strategie
wurden 24 Parameterkombinationen geprüft; „≥6 Berührungen, 48 h" ist die
beste davon. Der *Effekt* ist robust belegt
([`sr_breakout.md`](sr_breakout.md)), die konkrete Pass-Rate ist optimistisch.
Rechne bei einem anderen Anbieter eher mit dem unteren Rand der Spanne.

**Und der ehrliche Rahmen bleibt:** Auch 60 % Pass-Rate je Versuch heißt, dass
das gefundete Konto danach dem fortbestehenden Drawdown-Limit unterliegt
([`trading_as_job.md`](trading_as_job.md)) — dort lag die Ein-Jahres-Überlebensrate
bei 8–48 %. Ein besseres Regelwerk verbessert den Einstieg, nicht den Bestand.
