# „Die großen Firmen traden mit Bots — da muss man doch was finden"

Der Einwand stimmt. Es **gibt** etwas zu finden, und ich habe es in diesem
Projekt gefunden und gemessen. Die Frage ist nicht, ob es existiert — sondern
was es kostet, es zu ernten.

---

## Der beste messbare Bot-Edge dieser Untersuchung

**Orderbuch-Ungleichgewicht ±5 %, 4-Stunden-Horizont.**
277.236 Orderbuch-Snapshots, 2023-01 bis 2025-08 (2,7 Jahre), Binance.

| | |
|---|---|
| Trades | **110.786** |
| Brutto je Trade | **+0,87 bp** |
| Streuung je Trade | 103 bp |
| **Signal-Rausch-Verhältnis** | **0,0085** |
| Trades, bis der Edge das Rauschen überragt | **13.920** |

Das ist ein echter Edge. Er hält out-of-sample — er ist sogar das **einzige
Signal der gesamten Untersuchung, das im zweiten Zeitabschnitt stärker wurde**
statt zusammenzubrechen ([`orderflow_test.md`](orderflow_test.md)).

Und er ist **0,87 Basispunkte groß**.

> Die letzte Zeile erklärt, warum es ein Bot sein *muss*: Man braucht knapp
> 14.000 Trades, bevor der Edge das Rauschen überhaupt überragt. Kein Mensch
> macht 14.000 Trades.

---

## Ab welchen Kosten trägt welches Signal?

| Signal | brutto/Trade | Trades/Jahr | brutto p.a. | **max. Kosten** |
|---|---|---|---|---|
| **S/R-Ausbruch ≥6 Berührungen (deins)** | **+45,70 bp** | 40 | **+18,3 %** | **45,70 bp** |
| Orderbuch-Imbalance ±5 %, 4 h | +0,87 bp | 2.190 | +19,1 % | **0,87 bp** |
| Orderflow OFI, 1 h | +1,26 bp | 8.760 | +110,4 % | 1,26 bp |
| Orderflow OFI, 5 min | +0,29 bp | 105.120 | +304,8 % | 0,29 bp |
| Coinbase-Premium (ETF-Fluss) | +3,00 bp | 73 | +2,2 % | 3,00 bp |

**Du zahlst bei Kraken 16 bp je Roundtrip.** Alles, was in der letzten Spalte
unter 16 steht, ist für dich tot — unabhängig davon, wie signifikant es ist.
Der Orderflow hat den stärksten p-Wert der gesamten Untersuchung (10⁻¹⁷³) und
ist trotzdem unerreichbar.

**Deine Strategie ist die einzige Zeile, in der die letzte Spalte über 16
liegt.** Das ist keine Meinung, das ist der ganze Grund, warum sie übrig
geblieben ist.

---

## Was mit dem Bot-Edge passiert, je nachdem wer du bist

Orderbuch-Signal, 2.190 Trades im Jahr:

| Kostenstufe | netto/Trade | p.a. auf Nominal | Sharpe |
|---|---|---|---|
| **Du bei Kraken (Taker)** | **−15,13 bp** | **−331,3 %** | **−6,90** |
| Retail mit gutem Tarif | −7,13 bp | −156,1 % | −3,25 |
| Profi-Taker, VIP-Stufe | −3,13 bp | −68,5 % | −1,43 |
| Maker ohne Gebühr | −1,13 bp | −24,7 % | −0,52 |
| **Market Maker mit Rebate** | **+0,87 bp** | **+19,1 %** | **0,40** |
| MM + Rebate + Colocation | +1,87 bp | +41,0 % | 0,85 |

Derselbe Edge. Dieselben Daten. Derselbe Code. **Der Unterschied zwischen
−331 % und +41 % im Jahr ist ausschließlich die Kostenstruktur.**

Deine Kosten sind **18× zu hoch** für dieses Signal.

---

## Der Vergleich, der alles erklärt

| | je Trade | Trades/Jahr | brutto p.a. | **Sharpe** |
|---|---|---|---|---|
| **Dein S/R-Ausbruch** | **+45,7 bp** | 40 | **+18,3 %** | **0,36** |
| Bot-Orderbuch (als Market Maker) | +0,87 bp | 2.190 | **+19,1 %** | **0,85** |

**Lies die vorletzte Spalte zweimal.**

Der Bot verdient pro Jahr **nicht mehr** als du. 19,1 % gegen 18,3 % brutto.
Dein Edge je Trade ist **130× größer** als seiner. Seiner kommt **55× häufiger**.

**Der Unterschied ist nicht der Ertrag. Es ist der Sharpe: 0,85 gegen 0,36.**

Und darauf kommt es an, denn Sharpe ist das, was man hebeln kann. Ein Market
Maker, der dieses Signal über hunderte Instrumente gleichzeitig fährt, kommt
auf Sharpe 3 bis 5 — und kann deshalb das Zehnfache seines Kapitals einsetzen.
Aus 19 % werden 190 %. Du mit Sharpe 0,36 kannst das nicht, weil dich der
zweite schlechte Tag aus der Challenge wirft.

**Die Bots sind nicht schlauer. Sie sind ruhiger.**

---

## Und die unangenehmste Erkenntnis: du bist ihr Ertrag

Der Orderflow-IC ist **negativ**: Aggressives Kaufen sagt *fallende* Kurse
voraus ([`orderflow_test.md`](orderflow_test.md), IC −0,041, p = 3·10⁻¹⁷³).

Das ist keine Anomalie. Das ist die Bezahlung des Market Makers. Wer
Liquidität *nimmt* — also mit Market-Order kauft, wie du es tust — bezahlt
sie. Der Bot ist auf der anderen Seite.

**Als Taker kannst du dieses Signal nicht ernten, weil du es erzeugst.**

---

## Was daraus folgt

**1. Der Einwand ist richtig, und er ist gleichzeitig die Erklärung für
35 Fehlschläge.** Wenn Bots jede Ineffizienz in Millisekunden abräumen, dann
ist genau das der Grund, warum Donchian, MACD, Bollinger, Order Blocks,
On-Chain, Funding und die anderen alle bei null landeten. Deine Beobachtung
widerspricht den Ergebnissen nicht — sie erklärt sie.

**2. Was übrig bleibt, ist das, was für Bots zu langsam und zu klein ist.**
Ein Bot, der 2.190-mal im Jahr für 0,87 bp handelt, interessiert sich nicht
für 40 Trades im Jahr mit 48 Stunden Haltedauer und 5.000 $ Nominal. Diese
Nische ist nicht *trotz* der Bots da, sondern *wegen* ihnen: Sie ist zu klein,
als dass es sich für jemanden lohnte, sie wegzuarbitrieren.

**3. Der Weg in die Bot-Liga ist keine bessere Idee, sondern eine bessere
Kostenstruktur.** Maker statt Taker, Rebates statt Gebühren, Colocation statt
Heimanschluss. Das ist eine Infrastruktur-Investition von Hunderttausenden
Euro, keine Strategie. Und mit einem 10.000-$-Prop-Konto ist sie
ausgeschlossen — Prop-Firmen erlauben typischerweise keine Market-Making-
Frequenzen und du bekommst dort ohnehin keine Rebates.

---

## Die Zahl zum Merken

> **Der beste Bot-Edge, den ich in 5,4 Jahren Daten und 9,2 Millionen
> Orderbuch-Snapshots finden konnte, ist 0,87 Basispunkte groß.
> Deine Kostenschwelle ist 16.**

Es gibt also etwas zu finden. Es ist nur nicht für dich gefunden.

---

*Skripte: `research/bots.py`, `research/bots2.py`. Datengrundlage:
`orderflow_test.md` (277.236 Orderbuch-Snapshots, 472.896 Fünf-Minuten-Bars
mit Taker-Volumen).*

*Anmerkung zur Ehrlichkeit: Frühere Notizen nannten für dieses Signal
+6,21 bp. Das war auf einem 303-Tage-Fenster gemessen. Auf den vollen
2,7 Jahren sind es +0,87 bp — die höhere Zahl war ein Artefakt des kurzen
Fensters, wie in [`orderflow_test.md`](orderflow_test.md) dokumentiert.*
