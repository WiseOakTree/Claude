# „Marktphasen und Price Action sind das Wichtigste" — gemessen

Eine Behauptung, die sich prüfen lässt. Und zwar mit dem stärksten Test, den
es gibt: einem **perfekten Orakel**. Wenn selbst das Wissen um die Zukunft
nichts brächte, wäre die Sache erledigt.

---

## Teil 1: Marktphasen — der Guru hat recht. Und das hilft nicht.

Phase gemessen über die **Efficiency Ratio**: |Nettobewegung| geteilt durch
die Summe der Einzelbewegungen. Nahe 1 = sauberer Trend, nahe 0 = Seitwärts.

### Mit Orakel (Blick in die nächsten 48 Stunden — verbotenes Wissen)

| Phase | n | Ø netto | positiv | p |
|---|---|---|---|---|
| **Seitwärts** | 71 | **−80,5 bp** | **19,7 %** | <0,001 |
| gemischt | 71 | +13,8 bp | 69,0 % | 0,610 |
| **Trend** | 71 | **+268,1 bp** | **78,9 %** | <0,001 |

**Eine Spanne von 348 Basispunkten.** Das ist der mit Abstand größte
Einzeleffekt, den dieses Projekt gefunden hat — größer als der S/R-Edge
selbst, größer als alles andere.

**Der Guru hat also völlig recht: Die Marktphase entscheidet.**

### Und jetzt die Frage, die er nicht stellt: kann man sie kennen?

Korrelation zwischen der Phase der **Vergangenheit** und der Phase der
**nächsten 48 Stunden**:

| Rückblick | Korrelation | p |
|---|---|---|
| 24 h | **−0,077** | 0,266 |
| 48 h | +0,023 | 0,733 |
| 96 h | +0,026 | 0,708 |
| 168 h | **−0,138** | 0,044 |
| 336 h | −0,015 | 0,827 |

**Null. Und der einzige halbwegs signifikante Wert ist negativ.**

Die Phase, in der du dich befindest, sagt praktisch nichts über die Phase,
in der du gleich sein wirst. Marktphasen **persistieren nicht** — jedenfalls
nicht auf der Zeitskala, auf der man handelt.

> **„Marktphasen verstehen" heißt in der Praxis: die Phase erkennen, in der
> man bereits war. Die zählt aber nicht — es zählt die, in die man
> hineinhandelt.**

Das ist dieselbe Struktur wie bei der Volatilitätsprognose
([`ml_ceiling.md`](ml_ceiling.md)): Ein perfektes Orakel wäre Gold wert, und
genau deshalb gibt es keins.

---

## Der neunte Filter — und warum er auch fällt

Der Test hat einen Nebenbefund erzeugt, der zunächst stark aussah: Auf dem
BTC-Suchzeitraum liefert der Ausbruch **nach einer ruhigen 168-Stunden-Phase**
+112 bp gegen −3 bp nach einer unruhigen. Im BTC-Holdout sogar **+226 bp gegen
−7 bp**. Das ist die Gegenrichtung zur üblichen Lehre — *„handle Ausbrüche aus
der Ruhe heraus, nicht aus der Bewegung"*.

Nach den Regeln dieses Projekts geprüft, auf **ungesehenen Daten**
(BTC-Holdout plus ETH, SOL, XRP komplett):

| | n | Ø netto |
|---|---|---|
| ruhige Phase | 239 | **+21,7 bp** |
| unruhige Phase | 546 | **−20,2 bp** |
| **Differenz** | | **+41,9 bp** |

| Prüfung | Ergebnis |
|---|---|
| p roh | 0,380 |
| p überlappungskorrigiert | **0,586** |
| **p nach Bonferroni (9 Filter)** | **1,000** |
| Quantils-Monotonie (Spearman) | **−0,063**, p = 0,076 |

Die Quintile: +37,7 / −21,1 / +18,5 / +10,7 / −83,0 bp. **Kein Gefälle,
sondern Rauschen mit einem schlechten Extremquintil.**

Und je Asset kippt es: ETH-Holdout **−210 bp** (umgekehrt), SOL-Holdout
+12,6 bp (verschwunden), XRP-Suchzeitraum −73,9 bp.

**Damit ist es der neunte Filter, der out-of-sample durchfällt.**

*(Immerhin sauber ausgeschlossen: Es ist **nicht** dieselbe Größe wie
Volatilität — Korrelation +0,029. Es misst wirklich etwas anderes. Nur
eben nichts Nutzbares.)*

---

## Teil 2: Price Action — der einzige Teil, der etwas wert ist

Und zwar messbar, aber deutlich weniger als der Satz suggeriert.

| Ansatz | Ergebnis |
|---|---|
| **S/R-Ausbruch nach Berührungszahl** | **+45,7 bp je Trade** — der einzige Chartmuster-Befund, der alle Kontrollen bestand |
| Order Blocks („Smart Money") | Zufallskerze **genauso gut** |
| Heikin Ashi | nichts; die HA-Preise sind nicht einmal handelbar |
| Bollinger-Reversion | Pass-Rate 0 % |
| Donchian, EMA-Kreuzung, MACD, Momentum | Median-Rendite 0,00 % |

**Price Action ist real — und sie ist rund 12 Prozentpunkte über einem korrekt
dimensionierten Münzwurf wert** ([`zufall.md`](zufall.md)). Nicht null. Aber
auch nicht „das Wichtigste".

Der Punkt ist: **Von allem, was unter „Price Action" verkauft wird, hat genau
ein Muster gehalten** — Levels nach Berührungszahl. Order Blocks, Liquidity
Grabs, Heikin Ashi, alle Indikatorvarianten: gemessen nicht unterscheidbar von
Zufall.

---

## Was tatsächlich das Wichtigste ist

Gemessen, in der Reihenfolge ihrer Wirkung:

| Rang | Faktor | Wirkung | prognostizierbar? |
|---|---|---|---|
| 1 | **Regelwerk** (DD/(DD+Ziel)) | 37,5 % geschenkt | **fix, kein Können nötig** |
| 2 | **Positionsgröße** | 39,6 % → 49,4 % | **vollständig kontrollierbar** |
| 3 | **Zeitlicher Versatz mehrerer Versuche** | 70,9 % → ~100 % | **vollständig kontrollierbar** |
| 4 | Price Action (S/R-Level) | ~12 pp über Münzwurf | teilweise |
| 5 | **Marktphase** | **348 bp Spanne** | **nein** |

**Die Marktphase steht auf Platz 1 nach Wirkung und auf dem letzten Platz
nach Nutzbarkeit.** Genau das macht sie zum perfekten Lehrinhalt: Man kann
sie im Rückblick immer zeigen, und sie erklärt jedes vergangene Chart
vollständig.

Die drei Faktoren, die tatsächlich etwas bringen, sind **Arithmetik, nicht
Marktverständnis**. Sie stehen in keinem Kurs, weil man sie in zehn Minuten
erklärt hat.

---

## Der ehrliche Satz zur Behauptung

> „Marktphasen und Price Action sind die wichtigsten Dinge, die ich als
> Trader verstehen muss."

**Beides ist wahr und beides hilft kaum.**

Marktphasen sind der größte Effekt im Datensatz — und unprognostizierbar.
Price Action ist prognostizierbar — und klein. Was groß **und** kontrollierbar
ist, kommt in dem Satz nicht vor: **wie viel du setzt und wie oft du antrittst.**

---

*Skripte: `research/marktphasen.py` (Orakel-Test, Persistenz),
`research/phasen_oos.py` (neunter Filter, vier Assets),
`research/phasen_streng.py` (Signifikanz, Volatilitätskontrolle,
Quantils-Monotonie).*
