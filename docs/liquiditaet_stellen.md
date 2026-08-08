# „Was, wenn wir den Gamblern die Liquidität bereitstellen?"

Die schärfste Idee dieses Projekts — und sie folgt zwingend aus zwei
Befunden: dem Orderflow-IC von −0,041 und dem Taker-Anteil der dauerhaft
erfolgreichen Hyperliquid-Konten (38 % gegen 66 %).

Gemessen an **7.812.435 echten Einzeltrades** über fünf Tage.

**Ergebnis: Die Idee stimmt. Die Rechnung geht trotzdem nicht auf — es sei
denn, man bekommt Geld dafür.**

---

## Wie ich es gemessen habe

Kein Quote-Modell, keine Annahme über die Warteschlange. **Jeder Trade in den
Daten hat einen Market Maker auf der Gegenseite** — ich messe direkt, was
dieser Maker verdient hat:

```
Maker kauft (is_buyer_maker = true)  -> Gewinn = (Preis nach 1 min / Fillpreis - 1)
Maker verkauft                        -> umgekehrt
```

Das ist der **realisierte Spread**: was vom kassierten Spread übrig bleibt,
nachdem der informierte Gegenpart den Preis mitgenommen hat.

*(Ein erster Versuch mit einem eigenen Quote-Modell war unbrauchbar: Er
quotete um den letzten Trade-Preis herum und erzeugte damit künstliche adverse
Selektion. Diese Messung braucht keinen Referenzpreis.)*

---

## Der naive Market Maker verliert

| Tag | Trades | 1 s | 10 s | **1 min** | 10 min |
|---|---|---|---|---|---|
| 2026-03-10 | 2.802.252 | −0,581 | −0,665 | **−0,672** | −1,042 |
| 2026-05-19 | 991.693 | −0,479 | −0,633 | **−0,523** | −0,319 |
| 2026-06-24 | 2.352.076 | −0,537 | −0,558 | **−0,439** | −0,332 |
| 2026-07-15 | 1.107.089 | −0,505 | −0,571 | **−0,556** | −0,399 |
| 2026-08-02 | 559.325 | −0,387 | −0,583 | **−0,790** | −0,530 |

**Zwanzig von zwanzig Zellen negativ.** Gepoolt: **−0,575 bp je Trade**,
Median −0,429, in 46,6 % der Fälle positiv.

Das ist die adverse Selektion in Reinform: **Wer den Spread nimmt, weiß im
Schnitt mehr über die nächste Minute als der, der ihn stellt.**

---

## 🛑 Und jetzt der Teil, der deine Hypothese kippt

Deine Idee war präziser als „Market Maker sein": **den Gamblern** Liquidität
stellen, also den Kleinen, nicht den Profis. Nach Tradegröße:

| Tradegröße | Anteil | Trades | **Maker-Ergebnis** | nach 1,5 bp Gebühr |
|---|---|---|---|---|
| **unter 100 $** | 22,7 % | 1.775.277 | **−0,705 bp** | −2,205 |
| **100–500 $** | 40,5 % | 3.167.689 | **−0,715 bp** | −2,215 |
| 500–2.000 $ | 13,3 % | 1.040.364 | −0,374 bp | −1,874 |
| 2.000–10.000 $ | 12,9 % | 1.005.484 | −0,331 bp | −1,831 |
| 10.000–50.000 $ | 7,5 % | 582.595 | **−0,246 bp** | −1,746 |
| über 50.000 $ | 3,1 % | 241.026 | −0,445 bp | −1,945 |

**Die kleinen Trades sind die schlechtesten Gegenparteien, nicht die besten.**
−0,715 bp gegen −0,246 bp bei den großen. Das ist das **Gegenteil** der
Erwartung.

Warum, kann ich nicht sicher sagen. Die plausibelste Erklärung: Kleine Prints
sind oft Bruchstücke großer, informierter Marktorders, die sich durchs Buch
fressen. „Kleiner Trade" ist eben nicht dasselbe wie „kleiner Trader".

Auch die Tageszeit hilft nicht — **alle acht Zeitfenster negativ**:

| UTC | Trades | Maker-Ergebnis |
|---|---|---|
| 15–18 Uhr | 1.559.512 | −0,368 bp *(bestes)* |
| 09–12 Uhr | 634.165 | −0,426 bp |
| 00–03 Uhr | 854.222 | **−0,772 bp** *(schlechtestes)* |

---

## 🟢 Was die Rechnung rettet: die Gebühr

| Gebührenstufe | **Ergebnis je Trade** |
|---|---|
| Standard-Maker 1,5 bp | **−2,075 bp** |
| Maker-Gebühr null | **−0,575 bp** |
| Rebate −0,5 bp | −0,075 bp |
| **Rebate −1,0 bp** | **+0,425 bp** |

Und mit Rebate ist **jedes** Segment profitabel:

| Tradegröße | mit −1,0 bp Rebate |
|---|---|
| unter 100 $ | +0,295 bp |
| 100–500 $ | +0,285 bp |
| 10.000–50.000 $ | **+0,754 bp** |

> **Das Geschäft besteht nicht darin, die richtige Gegenpartei zu finden.
> Es besteht darin, dafür bezahlt zu werden, dass man überhaupt quotet.**

### In Zahlen

Das Segment unter 500 $ — die „Gambler" — ist **63,3 % aller Trades**, aber
nur **1,4 % des Volumens**: 163,4 Mio $ am Tag.

Wer dieses **gesamte** Segment bedienen würde:

| | pro Jahr |
|---|---|
| bei 1,5 bp Standardgebühr | **−13.192.459 $** |
| bei Gebühr null | −4.245.365 $ |
| **bei −1,0 bp Rebate** | **+1.719.364 $** |

Dieselbe Tätigkeit, dieselben Gegenparteien, dasselbe Risiko — **ein
Unterschied von fast 15 Millionen Dollar, allein durch die Gebührenstufe.**

Das ist exakt der Faktor, den dieses Projekt schon früher gemessen hatte:
*−331 % p.a. als Taker, +41 % als Market Maker — derselbe Edge, andere
Gebühren.*

---

## Was das für dich heißt

**Die Idee ist richtig und sie beschreibt ein reales Geschäft.** Es ist das
Geschäft, das die dauerhaft erfolgreichen Hyperliquid-Konten betreiben, und es
ist der Grund, warum ihr Taker-Anteil bei 38 % statt 66 % liegt.

**Aber der Eintrittspreis ist eine Gebührenstufe, keine Strategie.** Rebates
gibt es für Volumen, das ein Privatkonto nicht erzeugt — und ohne Rebate
verlierst du bei jedem gestellten Trade, unabhängig davon, wen du bedienst.

Was dennoch bleibt und sofort anwendbar ist:

| | |
|---|---|
| **Limit statt Market** | Du sparst den Spread, den du sonst zahlst — das ist die Hälfte des Weges |
| **Nicht Vollzeit-Maker werden wollen** | Ohne Rebate ist das ein garantiertes Minusgeschäft |
| **Gebührenstufe verhandeln** | Bei jeder Börse die einzige Stellschraube mit belegtem Effekt |

---

## Was diese Messung nicht kann

- **Sie misst den DURCHSCHNITTLICHEN Maker.** Echte Market Maker sind
  selektiv: Sie verschieben ihre Quotes bei Ungleichgewicht, ziehen sie
  zurück, wenn giftiger Flow kommt, und steuern ihren Bestand. −0,575 bp ist
  der **Startpunkt**, nicht das Schicksal. Genau darin liegt das Handwerk.
- **Keine Warteschlange modelliert.** In Wirklichkeit wird man nicht bei jedem
  Trade gefüllt — und bei den ungünstigen Trades häufiger als bei den
  günstigen. Meine Schätzung ist deshalb eher **zu optimistisch**.
- **Fünf Tage, ein Instrument.** BTC-Perpetuals auf Binance. Andere Märkte
  haben andere Spreads und andere Gegenparteien.
- **Die Rebate-Stufen sind Szenarien.** Welche Konditionen aktuell wo
  erreichbar sind, kann ich von hier nicht prüfen.

---

*Skripte: `research/mm.py` (erster Versuch mit Quote-Modell, als Fehlerbeleg
behalten), `research/mm2.py` (realisierter Spread über 7,8 Mio Trades),
`research/mm3.py` (nach Tradegröße, Tageszeit und Segment).*
