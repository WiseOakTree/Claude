# Liquidität + MACD auf 1h und 4h — Spezifikation VOR der Rechnung

Festgelegt am 2026-08-28, committet bevor gerechnet wurde.

## Anlass

Der Nutzer hat zwei gewinnende Trades gezeigt und dazu geschrieben:

> „Ich weiß nur nicht, wie ich diese Trades gemacht hab. Ich hab mir angeschaut,
> wo die Liquidität liegt, und hab dann am MACD vom 1h- und 4h-Chart geschaut."

Das ist die richtige Frage. Diese Untersuchung macht aus der Beschreibung eine
prüfbare Regel und misst, **welcher Baustein was beiträgt**.

## Vorbemerkung, die vor jeder Zahl stehen muss

**Zwei gewinnende Trades sind kein Befund.** Bei einer Trefferquote von 50 %
passiert das in **25 %** aller Fälle rein zufällig. Bei den beiden gezeigten
Trades (beide Short, beide im Plus) lässt sich nicht unterscheiden, ob die
Methode funktioniert oder ob es zwei gute Tage waren. Deshalb wird hier nicht
geprüft, ob *diese* Trades gut waren, sondern ob die *Regel dahinter* über
Jahre trägt.

## Was schon gemessen ist — und gescheitert

Beide Bausteine sind in diesem Projekt einzeln geprüft worden:

| Baustein | Ergebnis | Dokument |
|---|---|---|
| MACD 4h, Trendlesart | t = 0,20 in der Suche, **−0,10 im Holdout**; BTC −15,0 bp, ETH −93,0 bp | [`macd_stoch_boll.md`](macd_stoch_boll.md) |
| Liquidations-Karte als Magnet | **Münzwurf**; nach der Kaskade Suche „Fortsetzung", Holdout „Umkehr" | [`footprint_liquidation.md`](footprint_liquidation.md) |

**Neu ist die Kombination:** MACD gleichzeitig auf **1h und 4h** plus Nähe zu
einem Liquiditätslevel. Konfluenz kann besser sein als die Summe der Teile —
oder nur seltener. Genau das wird getrennt.

## Die Regel, wie sie implementiert wird

| | |
|---|---|
| Ausführungs-Zeitrahmen | 1 h |
| Trendfilter | **4h-MACD**: Linie über Signallinie = Long-Seite, darunter = Short-Seite. Das 4h-Signal gilt erst ab dem Schluss der 4h-Kerze (kein Look-ahead) |
| Auslöser | **1h-MACD-Kreuzung** in Richtung des 4h-Filters |
| Liquidität | Level aus bestätigten Pivots (`levels.build_levels`, Breite 8, Toleranz 0,5 ATR), ab **3 Berührungen** |
| Einstieg | Schluss der auslösenden 1h-Kerze |
| Ausstieg | feste Klammer, Ziel und Stop je **0,6 %** (die beiden gezeigten Trades liefen 0,40 % und 0,77 %), sonst Ausstieg nach **24 h** |

## Die Leiter — welcher Baustein trägt?

| | Aufbau |
|---|---|
| **L0** | Zufallseinstieg, gleiche Anzahl, gleiche Long/Short-Quote (Kontrolle) |
| **L1** | nur 1h-MACD-Kreuzung |
| **L2** | 1h-Kreuzung **und** 4h-MACD gleichgerichtet |
| **L3a** | L2 **und** Einstieg **an** einem Level (Fade: short am Widerstand, long an der Unterstützung) |
| **L3b** | L2 **und** ein Level **in Handelsrichtung** in Reichweite (Magnet: das Ziel ist die Liquidität) |
| **L4** | nur Level-Nähe, **ohne** MACD |

„In Reichweite" / „an einem Level" heißt: Abstand ≤ **1,0 ATR(14)** der 1h-Kerze.

## Kosten

Aus den beiden echten Trades des Nutzers abgeleitet
([`push200.md`](push200.md), Punkt 11):

* **Hauptmodell: 12 bp Roundtrip** (der Unterschied zwischen „Net PnL" und
  „Settled PnL" im zweiten Trade)
* optimistisch: 8 bp (4,00 bp je Seite, wie angezeigt)
* zusätzlich ein **Brutto-Lauf** ohne Kosten, um Marktverhalten von Reibung zu trennen

## Daten

BTC, ETH, SOL, XRP, DOGE, ADA — 1 h, 2021-03 bis 2026-07 (4h aus 1h gebildet).

* **Suchzeitraum:** bis 2024-12-31
* **Holdout:** ab 2025-01-01 (BTC nur nachrichtlich, gilt als verbraucht)

## Vorab festgelegte Auswertung

1. Anzahl Signale je Leiterstufe (Konfluenz kann sich zu Tode filtern)
2. Trefferquote gegen Break-even **und** gegen den Zufallseinstieg
3. bp je Trade brutto und netto, je Stufe, Suche und Holdout
4. **Marginaler Beitrag jeder Stufe** — L2 gegen L1, L3 gegen L2
5. Long und Short getrennt (beide gezeigten Trades waren Short)
6. Empfindlichkeit über Ziel/Stop und über die Level-Schwelle
7. Konto-Ebene bei 10x Hebel

## Urteilskriterien — festgelegt vor der Rechnung

Eine Stufe gilt als tragfähig, wenn **alle vier** erfüllt sind:

1. bp je Trade nach Kosten **> 0** im Suchzeitraum
2. **gleiches Vorzeichen** im Holdout (5 Märkte ohne BTC)
3. Trefferquote **signifikant über** dem Zufallseinstieg (Binomialtest, α = 0,05)
4. t über der Bonferroni-Schwelle für 6 Leiterstufen: **t > 2,64**

Zusätzlich, unabhängig davon, wird berichtet: **Bringt die Konfluenz mehr als
ihre Teile?** Wenn L2 nicht besser ist als L1 und L3 nicht besser als L2, ist
die Kombination kein eigener Effekt — egal wie die absoluten Zahlen aussehen.

Danach wird nichts nachjustiert.
