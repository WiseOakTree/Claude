# Die Trader, die es nachweislich können — analysiert

Datenquelle: **Hyperliquid**, eine dezentrale Börse, auf der jede Position und
jede PnL **on-chain steht**. Nichts selbst berichtet, nichts geschönt, kein
Anbieter dazwischen. **41.362 Konten.**

Das ist die beste Datengrundlage dieses gesamten Projekts.

---

## Die Grundverteilung

36.889 Konten mit über 1 Mio $ Handelsvolumen:

| | Konten | Anteil |
|---|---|---|
| allTime im Plus | 15.457 | **41,9 %** |
| Gewinn > 100.000 $ | 7.236 | 19,62 % |
| Gewinn > 1 Mio $ | 1.805 | **4,89 %** |
| Gewinn > 10 Mio $ | 211 | **0,57 %** |

**Die obersten 1 % halten 57,7 % aller Gewinne.**

Gesamtbilanz: 15,7 Mrd $ Gewinne, 5,0 Mrd $ Verluste, 10,3 Bio $ Volumen.

---

## 🛑 Der wichtigste Befund zuerst: „zweimal profitabel" heißt gar nichts

Zwei **disjunkte** Perioden gebildet (Monat minus Woche = frühere ~3 Wochen;
Woche minus Tag = spätere ~6 Tage). 2.234 Konten mit über 1 Mio $ Volumen in
**beiden**:

| | |
|---|---|
| in Periode A im Plus | 48,5 % |
| in Periode B im Plus | 54,2 % |
| **in beiden im Plus** | **26,1 %** |
| **bei reiner Unabhängigkeit erwartet** | **26,3 %** |
| **Überschuss** | **−0,2 Prozentpunkte** |

> **„Zweimal hintereinander profitabel" ist exakt das, was Zufall produziert.**

Das ist genau der Nachweis, den Trader als Beleg vorlegen — und er ist wertlos.
*(Es ist auch der Fehler, den ich in dieser Untersuchung selbst zuerst gemacht
habe: Meine erste Gruppeneinteilung „in beiden Perioden im Plus" war eine
Zufallsstichprobe. Der darauf gebaute Vergleich war entsprechend wertlos.)*

---

## 🟢 Aber in den Rändern steckt echtes Können

| Kriterium | tatsächlich | Zufall | Faktor |
|---|---|---|---|
| **oberstes Dezil in beiden Perioden** | **1,88 %** | 1,00 % | **1,9×** |
| oberste 5 % in beiden | 0,45 % | 0,25 % | 1,8× |
| oberstes Prozent in beiden | 0,09 % | 0,01 % | 9,0× *(n=2)* |

Und symmetrisch nach unten: Die schlechtesten 10 % bleiben zu **20,0 %** unten
(Zufall 10 %).

**Es gibt systematisch Gute und systematisch Schlechte — beide etwa doppelt so
häufig, wie Zufall erlaubt.** Die Rangkorrelation über alle Konten liegt
dagegen bei **null** (+0,005 bei hohen Volumenschwellen).

> **Können existiert an den Rändern, nicht in der Mitte.**

---

## Wie handelt die Kerngruppe?

**42 Konten**, die in *beiden* Perioden im obersten Dezil lagen, gegen
**29 Konten**, die zweimal im untersten lagen. Echte Fills, nicht Statistik:

| | **Kerngruppe** | Gegengruppe | p |
|---|---|---|---|
| Fills pro Tag (Median) | 199 | 204 | 0,233 |
| Ordergröße | 4.519 $ | 4.425 $ | — |
| gehandelte Märkte | 6 | 6 | — |
| Gebühren (bp je Volumen) | 1,18 | 1,42 | 0,159 |
| **Taker-Anteil** | **38,0 %** | **66,3 %** | **0,057** |

**Vier von fünf Merkmalen sind identisch.** Frequenz, Ordergröße, Marktzahl,
Gebührenquote — kein Unterschied.

**Der einzige Unterschied: Sie nehmen kaum Liquidität.** 38 % gegen 66 %.

### Und das ist derselbe Edge, den dieses Projekt schon gemessen hat

In [`orderflow_test.md`](orderflow_test.md) steht der stärkste statistische
Fund des Projekts: **Orderflow-IC = −0,041, p = 3·10⁻¹⁷³**. Übersetzt: *Wer
mit Market-Order kauft, verliert systematisch.* Das ist keine Prognose,
sondern eine Dienstleistungsgebühr an den, der die Gegenseite stellt.

**Die Kerngruppe auf Hyperliquid ist die Gegenseite.**

---

## Was Frequenz damit zu tun hat: nichts

Getrennte Stichprobe quer durch alle Größen, nach Handelsfrequenz:

| Frequenzklasse | n | dauerhaft im Plus | Ø Taker-Anteil |
|---|---|---|---|
| **unter 20 Fills/Tag (menschlich)** | 23 | **56,5 %** | 73,1 % |
| 20–100 (aktiv, noch manuell) | 56 | 51,8 % | 68,9 % |
| 100–500 (halbautomatisch) | 42 | 38,1 % | 71,1 % |
| 500–2000 (Bot) | 11 | 72,7 % | 79,0 % |
| über 2000 (HFT) | 7 | 57,1 % | 50,8 % |

*(Stichprobe geschichtet, Basisrate daher 50 % — nicht 25,5 % wie in der
Grundgesamtheit.)*

**Keine Klasse sticht heraus.** Und in der Kerngruppe handeln **18,8 %** mit
unter 20 Fills am Tag.

> **Menschliche Frequenz ist kein Ausschlusskriterium.** Man muss kein Bot
> sein. Man muss aufhören, den Spread zu zahlen.

---

## 🛑 Was diese Analyse nicht trägt

- **Die Perioden sind kurz.** Drei Wochen gegen sechs Tage. Das ist ein
  schwacher Persistenznachweis, egal wie sauber gerechnet. Ein Jahr gegen ein
  Jahr wäre etwas anderes — dafür bräuchte ich Momentaufnahmen über die Zeit,
  die ich nicht habe.
- **p = 0,057 ist nicht signifikant**, und es ist einer von fünf Vergleichen,
  die ich angestellt habe. Nach Korrektur für Mehrfachtests bleibt davon
  nichts Beweisbares. Es ist der **einzige** Vergleich, der überhaupt in die
  Nähe kommt — mehr sage ich nicht.
- **n = 32 gegen 26.** Klein.
- **Das Leaderboard ist eine Auswahl.** Wer nie gehandelt hat, steht nicht
  drin. Konten, die auf null gingen und geschlossen wurden, vermutlich
  ebenfalls nicht — die echte Verliererquote liegt wahrscheinlich über
  58,1 %.
- **Eine Adresse ist kein Mensch.** Große Akteure verteilen sich auf viele
  Wallets, manche Adressen sind Vaults mit fremdem Geld.

---

## Die Antwort auf deine Frage

**Ja, es gibt Trader, die es nachweislich können.** Rund 1,9-mal so viele, wie
Zufall erzeugen würde — also grob **1 bis 2 % der aktiven Konten**, nicht die
20 %, die man in Ranglisten zu sehen glaubt.

**Und sie unterscheiden sich in genau einem Punkt von den anderen.** Nicht in
der Frequenz, nicht in der Kontogröße, nicht in der Zahl der Märkte, nicht in
der Ordergröße:

> **Sie stellen Liquidität, statt sie zu nehmen. 38 % gegen 66 %.**

Das ist kein Chartmuster, kein Indikator und keine Strategie. Es ist eine
**Ausführungsentscheidung** — und zwar die einzige, die in dieser Datenmenge
messbar zwischen dauerhaft oben und dauerhaft unten trennt.

Was das praktisch heißt: **Limit-Orders statt Market-Orders.** Auf den Preis
warten, statt ihn zu nehmen. Das kostet Trades, die man verpasst, und es
erspart bei jedem ausgeführten Trade den Spread.

Es ist auch die einzige Erkenntnis dieses Projekts, die man **sofort umsetzen
kann**, ohne einen Edge gefunden zu haben — sie macht jede Strategie besser,
auch eine ohne Vorteil.

---

*Skripte: `research/hl_persist.py` (Leaderboard, Schwellenanalyse),
`research/hl_kern.py` (Zufallsanteil, Kerngruppe, Fill-Vergleich),
`research/hl_frequenz.py` (Persistenz nach Handelsfrequenz),
`research/hl_fills.py` (erster, größenverzerrter Vergleich — als Fehlerbeleg
behalten).*
