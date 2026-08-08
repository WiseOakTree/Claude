# Markov-Ketten und der Rainbow Chart

Zwei Fragen, beide gemessen. Und zusammen beantworten sie die dahinterliegende:
*Ist jetzt endgültig klar, dass man nichts vorhersagen kann?*

**Nein — die Antwort ist präziser und unangenehmer: Man kann etwas vorhersagen.
Es ist nur zu klein, um es zu bezahlen.**

---

# Teil 1: Markov-Ketten

Der allgemeinste Test auf kurzes Gedächtnis. Renditen in Zustände einteilen
(Quantile), dann fragen: Sagt der Zustand von gestern etwas über heute?
Scheitert das, scheitert jede Regel, die nur aus der jüngsten Zustandsfolge
liest.

## Das Gedächtnis ist da — und es ist überwältigend signifikant

| Markt | Takt | Zustände | Ordnung | n | Chi² | **p** | Cramérs V |
|---|---|---|---|---|---|---|---|
| ETH | 1h | 3 | 2 | 46.736 | 1.651,6 | **0,00** | 0,133 |
| ETH | 1h | 5 | 2 | 46.736 | 3.303,4 | **0,00** | 0,133 |
| BTC | 4h | 5 | 2 | 11.685 | 780,5 | 8,9·10⁻¹⁰⁸ | 0,129 |
| BTC | 1D | 5 | 2 | 1.945 | 143,9 | 1,1·10⁻³ | 0,136 |

**p = 0,00 heißt: kleiner als die Maschine darstellen kann.** Der Markt ist
nachweislich nicht gedächtnislos.

## Und es hält sogar out-of-sample

Verbesserung der Vorhersage (Log-Loss) im Holdout gegenüber „einfach die
Randverteilung raten":

| Markt | Takt | Zustände | Ordnung | **Verbesserung** |
|---|---|---|---|---|
| BTC | 1h | 5 | 2 | **+1,854 %** |
| BTC | 1h | 3 | 2 | +1,389 % |
| BTC | 4h | 5 | 2 | +0,843 % |
| ETH | 4h | 3 | 1 | **−0,104 %** |

**Fünfzehn von sechzehn Fällen positiv.** Das Gedächtnis ist real und es
verallgemeinert.

## 🛑 Und jetzt der Betrag

Handeln nach der Markov-Vorhersage, BTC 4h, Holdout:

| Zustände | Ordnung | Signale | **bp je Trade nach Kosten** |
|---|---|---|---|
| 3 | 1 | 3.275 | **−16,40** |
| 3 | 2 | 3.274 | −15,33 |
| 5 | 1 | 3.275 | −15,97 |
| 5 | 2 | 3.274 | −16,05 |

Die Kostenschwelle liegt bei **16 bp** je Roundtrip. Das Nettoergebnis liegt
bei **−15 bis −16 bp**.

> **Der Bruttovorteil beträgt also zwischen +0,7 und −0,4 Basispunkten. Bei
> einer Kostenschwelle von 16.**

Das ist exakt dasselbe Muster wie beim Orderflow (p = 3·10⁻¹⁷³ bei 0,29 bp
Signal): **Signifikanz und Handelbarkeit haben nichts miteinander zu tun.**

**Markov bringt nichts — nicht weil kein Muster da wäre, sondern weil das
Muster tausendmal kleiner ist als die Gebühr.**

---

# Teil 2: Der Rainbow Chart

Logarithmische Regression über die BTC-Historie, Bänder als Vielfache der
Streuung. „Kaufen im Blauen, verkaufen im Roten."

Der entscheidende Punkt: **Die Regression wird über die ganze Historie
gefittet — auch über Daten, die zum Entscheidungszeitpunkt in der Zukunft
lagen.** Ich habe die übliche Variante gegen eine streng kausale gestellt, bei
der zu jedem Tag nur die bis dahin bekannten Daten in den Fit gehen.

## Der 3-Monats-Effekt verschwindet vollständig

Gleicher Zeitraum, beide Varianten nebeneinander:

| Horizont | Variante | unterstes Quintil | oberstes Quintil | **Spanne** |
|---|---|---|---|---|
| 3 Monate | Fit über alles | +34,3 % | −13,6 % | **+48,0 Pp** |
| 3 Monate | **kausal** | +18,8 % | +17,7 % | **+1,1 Pp** |

**Von 48 Prozentpunkten bleiben 1,1.** Achtundneunzig Prozent des sichtbaren
Effekts sind Look-ahead.

## Der 1-Jahres-Effekt überlebt — scheinbar

| Horizont | Variante | unten | oben | Spanne |
|---|---|---|---|---|
| 1 Jahr | Fit über alles | +310,9 % | −30,0 % | +340,9 Pp |
| 1 Jahr | **kausal** | **+180,7 %** | −1,3 % | **+182,1 Pp** |

Das sieht nach einem Befund aus. Es ist keiner:

| | |
|---|---|
| Zeitraum | 9,0 Jahre |
| tägliche Beobachtungen | 2.906 |
| **davon unabhängig** | **8** (1-Jahres-Fenster überlappen 365-fach) |
| BTC-Zyklen im Zeitraum | **2** |
| t ohne Überlappungskorrektur | **14,12** |
| **t mit Korrektur** | **0,74** (n_eff = 2,4) |
| Kontrolle gegen verschobenes Band | **p = 0,138** |

> **Der Ein-Jahres-Effekt ist die Beschreibung von zwei Bullenzyklen, nicht
> eine statistische Aussage.** Mit 2,4 effektiven Beobachtungen kann man
> nichts belegen.

## Und die Trendlinie selbst ist nicht stabil

Der Exponent, jeweils nur mit den bis dahin bekannten Daten geschätzt — und
was die Linie für ein Jahr später vorhersagte:

| Stand | Exponent | **Prognose in 1 Jahr** | **tatsächlich** |
|---|---|---|---|
| 2020-01 | 0,039 | 7.326 $ | **28.924 $** |
| 2021-01 | 0,139 | 9.346 $ | **47.723 $** |
| 2022-01 | 0,470 | 20.723 $ | 16.617 $ |
| 2023-01 | 0,515 | 24.985 $ | **44.180 $** |
| 2024-01 | 0,541 | 28.457 $ | **93.576 $** |
| 2025-01 | 0,651 | 38.759 $ | **88.839 $** |
| 2026-01 | 0,764 | 53.262 $ | 62.888 $ |

**Sieben Prognosen, sieben Fehlschläge.** Sechsmal deutlich zu niedrig, einmal
zu hoch. Die Abweichungen reichen von −80 % bis +25 %.

Und der Exponent wanderte von **0,039 auf 0,786** — die „Mitte" des Regenbogens
wurde also laufend neu gezeichnet. Wer 2021 das Blau kaufte, kaufte ein Blau,
das es heute an dieser Stelle nicht mehr gibt.

### 🛑 Was an meinem Rainbow-Test schwach ist

- **Meine Historie beginnt 2017-08** (Binance), der echte Rainbow Chart nutzt
  Daten ab 2010. **Mit fünfzehn statt neun Jahren wäre die Linie deutlich
  stabiler**, und der Exponent hätte weniger gewandert. Das ist eine reale
  Einschränkung, und sie geht zugunsten des Rainbow Charts.
- Die Bandbreite habe ich als Standardabweichung der Residuen definiert; die
  gängigen Rainbow-Varianten benutzen feste Vielfache. Das ändert die Farben,
  nicht die Mechanik.
- Was der Test **zeigt**, ist unabhängig davon: dass der Kurzfristeffekt
  vollständig aus dem Look-ahead kommt, und dass hinter dem Langfristeffekt
  zwei Zyklen stehen.

---

# Die zusammengesetzte Antwort

Du hast gefragt, ob wir zu dem Schluss gekommen sind, dass man nichts
vorhersagen kann. **Der Schluss ist genauer:**

| | |
|---|---|
| Kann man etwas vorhersagen? | **Ja.** Markov: p = 0,00, 15 von 16 out-of-sample bestätigt |
| Wie viel? | **unter 1 Basispunkt** je Trade |
| Was kostet ein Trade? | **16 Basispunkte** |
| Verhältnis | **1 : 20 bis 1 : 50** |

**Das Problem ist nicht, dass der Markt zufällig wäre. Das Problem ist, dass
er *fast* zufällig ist — und die Gebühren in der Lücke sitzen.**

Deshalb ist auch der einzige Befund dieses Projekts, der die
Kostenschwelle je überstanden hat, kein Muster gewesen, sondern eine
**Risikoprämie** (Optionen verkaufen). Und deshalb war der einzige messbare
Unterschied zwischen dauerhaft guten und dauerhaft schlechten Tradern auf
Hyperliquid nicht die Prognose, sondern der **Taker-Anteil**
([`echte_trader.md`](echte_trader.md)).

Beide Male gewinnt nicht, wer besser vorhersagt, sondern wer weniger zahlt.

---

*Skripte: `research/markov.py` (Chi-Quadrat, Log-Loss, wirtschaftlicher Test),
`research/rainbow.py` (kausal gegen Fit-über-alles), `research/rainbow2.py`
(Trendstabilität, effektive Stichprobe, Kontrolle).*
