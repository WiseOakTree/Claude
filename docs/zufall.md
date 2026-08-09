# Reiner Zufall — und die eine Formel, nach der man eine Challenge aussucht

Zwei Behauptungen, beide getestet:

1. *„Es muss eine andere Challenge mit anderen Bedingungen geben."*
2. *„Oder pure randomness."*

**Beide stimmen. Und sie sind dieselbe Aussage.**

---

## 1. Was reiner Zufall wirklich liefert

Zufallsprozess ohne Drift, ohne Kosten, ohne jedes Können. Nur die
Positionsgröße wird richtig gewählt. Kraken Starter (10 % Ziel, 6 % Drawdown,
3 % Tagesverlust), 365 Tage:

| Jahresvolatilität | **bestanden** | am Drawdown | am Tageslimit | offen |
|---|---|---|---|---|
| 5 % | 4,9 % | 21,2 % | 0,0 % | 74,0 % |
| 10 % | 28,3 % | 52,7 % | 0,0 % | 18,9 % |
| **15 %** | **36,7 %** | 60,5 % | 0,7 % | 2,2 % |
| 20 % | 35,3 % | 52,7 % | 11,9 % | 0,1 % |
| 25 % | 29,0 % | 36,1 % | 34,9 % | 0,0 % |
| 30 % | 24,7 % | 21,6 % | 53,7 % | 0,0 % |
| 50 % | 19,7 % | 3,5 % | 76,8 % | 0,0 % |
| 100 % | 25,5 % | 0,3 % | 74,2 % | 0,0 % |

**36,7 % — mit null Können.**

Und das ist kein Zufallsfund, sondern ein bekanntes Resultat. Für einen
driftlosen Prozess ist die Wahrscheinlichkeit, die obere Schranke vor der
unteren zu erreichen:

> **P(bestehen) = Drawdown / (Drawdown + Ziel)**

Für Kraken: 6 / (6 + 10) = **37,5 %**. Gemessen: 36,7 %. Die 0,8 Punkte
Differenz sind das Tageslimit.

**Diese Zahl hängt von nichts ab, was du kannst.** Nicht von der Strategie,
nicht vom Indikator, nicht vom Asset. Nur vom Regelwerk und davon, dass du
die richtige Größe wählst.

---

## 2. Damit ist die Frage „welche Challenge?" eine Formel

Reiner Zufall unter verschiedenen Regelwerken, Volatilität je Regelwerk optimiert:

| Regelwerk | beste Vol | **Zufall bestanden** | Formel DD/(DD+Ziel) |
|---|---|---|---|
| **Kraken Starter** (10 / 6 / 3) | 15 % | **36,6 %** | 37,5 % |
| Kraken, aber 5 % Tageslimit | 20 % | 38,6 % | 37,5 % |
| Kraken, aber kein Tageslimit | 25 % | 38,7 % | 37,5 % |
| 6 % Ziel / 6 % DD / 3 % | 12 % | **49,8 %** | 50,0 % |
| **6 % Ziel / 10 % DD / 5 %** | 20 % | **61,4 %** | **62,5 %** |
| 8 % Ziel / 10 % DD / kein Tag | 25 % | 54,8 % | 55,6 % |
| Zwei-Phasen-Typ (8 % + 5 %) / 10 % DD | 25 % | 43,0 % | 43,5 % |

**Die Einkaufsformel lautet: maximiere Drawdown / (Drawdown + Ziel).**

Alles andere im Kleingedruckten ist Beiwerk. Ein Anbieter mit 6 % Ziel und
10 % Drawdown ist rechnerisch **62,5 % wert, bevor du die erste Kerze
angeschaut hast**. Kraken ist 37,5 % wert.

### 🛑 Korrektur an meiner eigenen früheren Aussage

In [`prop_rules.md`](prop_rules.md) habe ich das **Tagesverlustlimit als
größten Hebel** bezeichnet (40 % → 78 % ohne Limit). Das war gemessen mit der
S/R-Strategie bei 0,5× — also bei rund **28 % Jahresvolatilität**. Bei dieser
Größe bindet das Tageslimit ständig.

Bei **15 % Volatilität bindet es fast gar nicht**: 36,6 % mit Limit gegen
38,7 % ohne. Zwei Prozentpunkte, nicht achtunddreißig.

**Das Tageslimit ist kein Regelproblem, es ist ein Größenproblem.** Wer sich
darüber beschwert, handelt zu groß. Der Hebel, der bleibt, ist das Verhältnis
Ziel zu Drawdown — und der ist nicht verhandelbar.

---

## 3. Aber: Zufall heißt *nicht handeln*

Der Haken. Die 36,7 % gelten für einen Prozess **ohne Kosten**. Sobald man
Zufall *handelt*, ist er tot.

Zufallseinstiege auf BTC 1h, gleiche Frequenz wie die S/R-Strategie
(775 Ereignisse), Münzwurf-Richtung, 48 h halten, 16 bp je Roundtrip,
Median über 40 Ziehungen:

| Größe | bestanden |
|---|---|
| 0,50× | **13,9 %** |
| 1,00× | 16,6 % |

**36,7 % theoretisch, 13,9 % gehandelt.** Das Handeln selbst kostet
23 Prozentpunkte. Das ist die teuerste Zahl in diesem ganzen Projekt.

Die Konsequenz: Wer keinen Edge hat, darf **nicht traden**, sondern muss
Volatilität besitzen, ohne für sie zu bezahlen. Also: einmal einsteigen,
liegen lassen.

---

## 4. Einfach BTC halten — bestechend, und trotzdem kein Ergebnis

Halten kostet die 16 bp **einmal**, nicht je Roundtrip. Positionsgröße
durchgesweept, ganze Historie:

| Größe | Jahresvol | bestanden | unaufgelöst |
|---|---|---|---|
| 0,15× | 8 % | 36,1 % | 33,1 % |
| **0,25×** | **14 %** | **46,5 %** | 6,8 % |
| 0,35× | 19 % | 39,9 % | 2,7 % |
| 0,50× | 28 % | 25,7 % | 0,0 % |
| 1,00× | 56 % | 23,9 % | 0,0 % |

0,25× trifft exakt die theoretisch optimalen ~15 % Volatilität und liefert
**46,5 %** — praktisch gleichauf mit der S/R-Strategie (49–50 %). Nach
35 getesteten Ansätzen ist das eine unangenehme Zahl.

**Nur hält sie der Prüfung nicht stand:**

| Asset | Zeitraum | Halten 0,25× | S/R 0,5× | Differenz |
|---|---|---|---|---|
| BTC | Suchzeitraum | 60,6 % | 50,4 % | +10,3 |
| **BTC** | **Holdout** | **9,5 %** | **52,3 %** | **−42,8** |
| ETH | Suchzeitraum | 53,1 % | 34,5 % | +18,6 |
| ETH | Holdout | 19,6 % | 9,1 % | +10,5 |
| SOL | Suchzeitraum | 46,4 % | 19,3 % | +27,0 |
| SOL | Holdout | 17,2 % | 12,1 % | +5,1 |
| XRP | Suchzeitraum | 56,9 % | 22,2 % | +34,7 |
| XRP | Holdout | 20,7 % | 23,4 % | −2,7 |

Im Suchzeitraum schlägt Halten **alles**. Im Holdout bricht es auf **9,5 bis
20,7 %** ein. Der Grund ist offensichtlich, sobald man ihn misst:

| Jahresdrift | bestanden (bei 15 % Vol) |
|---|---|
| −20 % | 11,6 % |
| −10 % | 21,6 % |
| **0 %** | **36,6 %** |
| **+10 %** | **54,9 %** |
| +20 % | 69,9 % |
| +30 % | 82,6 % |
| +50 % | 94,3 % |

**Halten ist keine Strategie, es ist eine Richtungswette.** 2021–2024 stieg
BTC, also gewann sie. 2025–2026 nicht, also verlor sie. Die Drift des
Basiswerts während deines Versuchs ist der mit Abstand größte Einzelfaktor —
größer als jede Strategie, die ich getestet habe. Und sie ist nicht
prognostizierbar; das war der Inhalt der ersten dreißig Tests.

---

## 5. Die ehrliche Rangfolge

| Ansatz | Pass-Rate | was es wirklich ist |
|---|---|---|
| Zufall **gehandelt**, 0,5× | **13,9 %** | Kosten fressen alles |
| BTC halten, Holdout | **9,5 %** | Richtungswette, verloren |
| **Reiner Zufall, richtig dimensioniert** | **36,7 %** | **geschenkt — DD/(DD+Ziel)** |
| BTC halten 0,25×, ganze Historie | 46,5 % | Zufall + Aufwärtsdrift |
| **S/R-Ausbruch, 0,5×** | **49–50 %** | Zufall + ~12 pp Edge |
| S/R, BTC-Holdout | 52,3 % | hält (aber Holdout 5× benutzt) |

**Der gesamte Ertrag von 35 getesteten Ansätzen, 8 Filtern und XGBoost sind
rund 12 Prozentpunkte über einem korrekt dimensionierten Münzwurf.**

Das ist die ehrlichste Beschreibung dieses Projekts. Es ist kein Nichts —
12 Punkte auf einen 85-$-Einsatz sind viel. Aber es ist auch nicht das, was
man sucht, wenn man „eine Lösung" sagt.

---

## Was daraus praktisch folgt

**1. Deine Antwort auf „pure randomness" ist ja — aber richtig dimensioniert.**
~15 % Jahresvolatilität ist der Punkt, an dem das Tageslimit aufhört zu
existieren und die Ruin-Schranke voll greift. Das entspricht bei BTC etwa
**0,25× Nominal**, also 2.500 $ bei einem 10.000-$-Konto.

**2. Deine Antwort auf „andere Challenge" ist eine Formel, keine Suche.**
Nicht nach „großzügigem Drawdown" oder „keinem Zeitlimit" suchen — nach dem
**Verhältnis** DD/(DD+Ziel). Alles über 50 % ist besser als Kraken. Dabei auf
Konsistenzregeln und Mindesthandelstage prüfen: Beide zerstören genau die
Strategie „einmal groß genug einsteigen und warten".

**3. Die beiden Hebel multiplizieren sich nicht.** Die S/R-Strategie läuft
bei 0,5× auf ~28 % Volatilität — dort bindet das Tageslimit. Sie ist trotzdem
dort am besten, weil ihr Edge davon lebt, zum richtigen Zeitpunkt im Markt zu
sein. Kleiner handeln nimmt ihr den Edge, größer handeln kostet am Tageslimit.
0,5× bleibt der Kompromiss.

---

*Skripte: `research/zufall.py` (Obergrenze, Halten-Sweep, Zufallseinstiege),
`research/zufall2.py` (Holdout und Drift-Sensitivität),
`research/zufall3.py` (Regelwerke).*
