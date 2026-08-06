# Die drei Indikatoren als Informationsquelle

Andere Frage als vorher, und eine fairere. Eine Informationsquelle muss keinen
Trade gewinnen — sie muss **die Erwartung verändern**. Das ist getrennt
messbar, und zwar getrennt nach **Richtung** und **Risiko**.

Ergebnis vorweg: Über die Richtung sagen sie fast nichts. Über das Risiko
sagen sie etwas Echtes — das einzige in dieser ganzen Untersuchung, was den
Holdout auf drei Märkten übersteht.

---

## Teil 1: Was sie über die Richtung sagen

Bedingte Tabellen, BTC 4h 2021-26, jeweils Quintile des Indikatorwerts, dann
die nächsten 5 Tage:

### Stochastik %K

| Korb | n | Ø Rendite | Median | Anteil + | schlechteste 5 % |
|---|---|---|---|---|---|
| sehr tief | 2.321 | +0,16 % | +0,34 % | **53,2 %** | −11,2 % |
| tief | 2.322 | +0,18 % | +0,34 % | 53,5 % | −10,9 % |
| mitte | 2.320 | +0,26 % | +0,09 % | 50,8 % | −9,6 % |
| hoch | 2.332 | +0,28 % | −0,22 % | 48,2 % | −8,6 % |
| sehr hoch | 2.334 | +0,35 % | −0,17 % | **48,4 %** | −9,9 % |

Der Anteil positiver Ausgänge fällt monoton von 53,2 % auf 48,4 %. Das sieht
nach etwas aus — **und der Mittelwert läuft gleichzeitig in die
Gegenrichtung** (+0,16 % → +0,35 %). Median und Mittelwert widersprechen
einander: viele kleine Gewinne unten, wenige große oben.

### MACD-Histogramm

| Korb | Ø Rendite | Anteil + | kommende Vol |
|---|---|---|---|
| sehr tief | +0,24 % | 53,7 % | 59 % |
| tief | −0,04 % | 49,6 % | 46 % |
| mitte | +0,47 % | 53,0 % | 44 % |
| hoch | +0,29 % | 49,5 % | 47 % |
| sehr hoch | +0,27 % | 48,2 % | 55 % |

Keine Ordnung. Spanne der Mittelwerte **0,51 Prozentpunkte** über die ganze
Bandbreite des Indikators.

### Das monotone Muster sauber geprüft

Unterstes gegen oberstes Quintil, als Long-Short-Portfolio, mit
Überlappungskorrektur:

| Markt | Zeitraum | unten | oben | Spanne | t |
|---|---|---|---|---|---|
| BTC | Suche 21-24 | +0,49 % | +0,66 % | −0,17 | −0,34 |
| BTC | **Holdout** | −0,18 % | −0,71 % | **+0,53** | +0,15 |
| ETH | Suche 21-24 | +0,55 % | +1,26 % | −0,70 | −0,58 |
| ETH | **Holdout** | −0,34 % | −1,55 % | **+1,21** | +0,35 |
| SOL | Suche 21-24 | +1,65 % | +2,02 % | −0,37 | −0,25 |
| SOL | **Holdout** | +0,11 % | −0,48 % | **+0,59** | +0,11 |

**Das Vorzeichen kippt in allen drei Märkten.** Alle sechs t-Werte liegen
zwischen −0,58 und +0,35.

### Und formal gemessen

Transinformation zwischen Indikatorwert und Richtung der nächsten 5 Tage,
gegen eine zirkulär verschobene Kontrolle:

| Indikator | Richtung | Kontrolle |
|---|---|---|
| MACD-Histogramm | 0,0017 Bit | 0,0014 |
| MACD-Linie | 0,0020 | 0,0025 |
| Stochastik %K | 0,0026 | 0,0011 |
| Bollinger %B | 0,0025 | 0,0009 |
| Bollinger-Breite | 0,0012 | 0,0020 |

Maximal möglich wäre **1,0 Bit**. Gemessen: **0,002**. Zwei Tausendstel einer
Ja/Nein-Antwort — und teilweise unter der Kontrolle.

> **Über die Richtung sind die drei Indikatoren keine Informationsquelle.
> Nicht „schwach" — praktisch leer.**

---

## Teil 2: Was sie über das Risiko sagen — hier steht etwas

Dieselben Quintile, aber jetzt gegen die **realisierte Volatilität der
nächsten 5 Tage**:

### Bollinger-Breite

| Korb | Ø Rendite | schlechteste 5 % | **kommende Vol** |
|---|---|---|---|
| sehr eng | +0,81 % | −7,3 % | **37 %** |
| eng | −0,11 % | −10,3 % | 43 % |
| mitte | −0,13 % | −9,5 % | 47 % |
| weit | −0,16 % | −10,8 % | 55 % |
| sehr weit | +0,82 % | −12,0 % | **68 %** |

**Faktor 1,84 zwischen engstem und weitestem Quintil.** Und das schlechteste
5-%-Ergebnis wandert von −7,3 % auf −12,0 % — also **das, was dich im
Prop-Konto rauswirft**.

### Und es hält out-of-sample, auf drei Märkten

| Markt | Zeitraum | engstes 20 % | weitestes 20 % | Faktor |
|---|---|---|---|---|
| BTC | Suche 21-24 | 39 % | 72 % | **1,85×** |
| BTC | **Holdout 25-26** | 35 % | 54 % | **1,55×** |
| ETH | Suche 21-24 | 45 % | 96 % | **2,15×** |
| ETH | **Holdout 25-26** | 56 % | 75 % | **1,33×** |
| SOL | Suche 21-24 | 77 % | 147 % | **1,89×** |
| SOL | **Holdout 25-26** | 57 % | 90 % | **1,59×** |

**Sechs von sechs in dieselbe Richtung, drei unabhängige Märkte, beide
Zeiträume.** Nach neununddreißig gescheiterten Ansätzen und neun gescheiterten
Filtern ist das die erste Indikator-Aussage in diesem Projekt, die den Holdout
übersteht.

---

## 🛑 Aber: das ist keine Entdeckung, und die Breite ist die schlechtere Messung

Zwei Einschränkungen, beide wichtig.

**Erstens** ist Volatilitätsclustering seit vierzig Jahren Lehrbuchwissen
(Engle, Nobelpreis 2003). Dass ruhige Phasen ruhig bleiben und wilde wild, ist
das Robusteste, was man über Finanzzeitreihen weiß. Die Bollinger-Breite
*entdeckt* das nicht — sie zeigt es an.

**Zweitens** zeigt sie es schlechter, als wenn man direkt hinschaut:

| Prädiktor für die Vol der nächsten 5 Tage | Suche 21-24 | Holdout |
|---|---|---|
| Bollinger-Breite | R² 0,228 | 0,194 |
| **einfach die realisierte Vol der letzten 20 Bars** | **R² 0,315** | **0,222** |
| beide zusammen | 0,323 | 0,239 |
| **Zuwachs durch die Bollinger-Breite** | **+0,009** | **+0,017** |

Die Bollinger-Breite **ist** im Wesentlichen die realisierte Volatilität
(Korrelation **+0,747**) — nur durch einen Mittelwert geteilt und dadurch
verrauscht. Wer die Vol direkt rechnet, weiß mehr.

---

## Teil 3: Drei Indikatoren, aber nicht drei Informationen

Korrelationen, BTC 4h 2021-26:

| | MACD-Linie | MACD-Hist. | Stoch %K | %B | BB-Breite |
|---|---|---|---|---|---|
| **Momentum 20 Bars** | **+0,88** | +0,55 | +0,63 | +0,66 | −0,05 |
| **Vol 20 Bars** | −0,23 | +0,09 | +0,03 | −0,03 | **+0,75** |
| Stoch %K | +0,54 | +0,74 | +1,00 | **+0,85** | +0,04 |

Drei Zahlen erklären die Tabelle:

- **MACD-Linie ↔ Momentum: +0,88.** Der MACD ist geglättetes Momentum.
- **Bollinger %B ↔ Stochastik: +0,85.** Beide messen, wo der Kurs in seiner
  jüngsten Spanne steht — einmal an der Standardabweichung, einmal an
  Hoch/Tief.
- **Bollinger-Breite ↔ realisierte Vol: +0,75.** Das ist die Volatilität.

Hauptkomponenten aller sechs Werte: **4 von 6 Komponenten erklären 90 %**, die
erste allein 48,9 %.

> **Du schaust auf drei Indikatoren und siehst zwei Größen: wohin der Kurs
> zuletzt lief, und wie wild er dabei war.** Beides steht direkt im Chart. Die
> Indikatoren rechnen es um, sie fügen nichts hinzu.

---

## Was daraus für dich folgt — und das ist nicht nichts

Aus dem vorigen Dokument
([`macd_stoch_boll.md`](macd_stoch_boll.md)) stammt diese Zeile:

| | 0,25× | 0,35× | 0,50× | 1,00× |
|---|---|---|---|---|
| Pass-Rate unter Kraken-Regeln | 63,8 % | 50,5 % | 37,4 % | 30,2 % |

**Die Positionsgröße bewegt die Pass-Rate um 34 Punkte. Die Richtungswahl
bewegt sie um ungefähr null.**

Und die einzige Information, die die drei Indikatoren nachweislich tragen, ist
**genau der Input für die Positionsgröße** — nicht für die Richtung.

Damit haben sie als Informationsquelle tatsächlich einen Job. Nur einen
anderen als den, für den sie gebaut wurden:

| Frage | Antwort der Indikatoren |
|---|---|
| Geht es hoch oder runter? | **keine Information** (0,002 Bit) |
| Wie wild werden die nächsten Tage? | **Faktor 1,3–2,2**, hält out-of-sample |
| Wie groß soll die Position sein? | **darauf läuft die brauchbare Antwort hinaus** |

### Praktisch

- **Bänder eng** → kommende Vol ~35–45 % → normale Größe
- **Bänder weit** → kommende Vol ~55–75 % → **Größe halbieren**, sonst reißt
  der 6-%-Drawdown bei gleichem Trade
- **MACD und Stochastik** sagen dir, wo du in der jüngsten Bewegung stehst.
  Das ist eine Beschreibung der Vergangenheit, keine Aussage über die Zukunft
  — und als Beschreibung ist sie in Ordnung
- **Wer die Vol wirklich braucht, rechnet sie direkt** — die 20-Bar-Standard-
  abweichung ist der bessere Schätzer (R² 0,315 gegen 0,228)

---

## Die ehrliche Zusammenfassung

**Deine Nutzung ist verteidigbar, aber nicht aus dem üblichen Grund.**

Als Richtungsinformation sind die drei leer — 0,002 von 1,0 Bit, und das
einzige monotone Muster kippt in allen drei Märkten. Als Risikoinformation
tragen sie etwas Echtes, das den Holdout auf BTC, ETH und SOL übersteht.

Und Risiko ist die eine Größe, die im Prop-Konto tatsächlich über Bestehen
und Durchfallen entscheidet.

---

*Skripte: `research/info.py` (Transinformation gegen Kontrolle),
`research/info2.py` (bedingte Tabellen, Vol-Prognose, Redundanz),
`research/info3.py` (Monotonie und Holdout auf drei Märkten),
`research/info4.py` (Korrelationsmatrix, Hauptkomponenten).*
