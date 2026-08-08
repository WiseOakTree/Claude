# Footprint und Liquidations-Karte — echte Tickdaten

Die letzte offene Lücke aus [`volume_profile.md`](volume_profile.md) war:
*„Mit echten Tickdaten sieht das Profil feiner aus, das kann ich nicht
messen."* Jetzt kann ich es.

**Daten: 110.886.718 einzelne Trades**, jeder mit Preis, Menge und der
Kennzeichnung, ob Käufer oder Verkäufer der Aggressor war — 72 Tage aus dem
Binance-Futures-Archiv, verdichtet zu 20.736 Fünf-Minuten-Footprints. Dazu
**227.793 Bars Open Interest** im Fünf-Minuten-Takt über 26 Monate.

Das sind Primärdaten. Kein Anbieter, kein Modell, kein Bild — die Rohzahlen.

---

## Zuerst zu Coinglass

Der Schlüssel funktioniert, aber der Tarif gibt nichts frei:

| Endpunkt | Antwort |
|---|---|
| `liquidation/heatmap/model1` | `401 Upgrade plan` |
| `liquidation/aggregated-history` | `401 Upgrade plan` |
| `open-interest/aggregated-history` | `401 Upgrade plan` |
| `futures/supported-coins` (nur eine Liste) | `401 Upgrade plan` |

Ohne Schlüssel kommt `API key missing`, mit Schlüssel `Upgrade plan` — er wird
also erkannt, aber dem kostenlosen Tarif ist bei Coinglass v4 **jeder**
Datenendpunkt gesperrt.

Gebraucht wird er nicht: Die Heatmap ist ein Modell auf Open Interest, Preis
und Positionierung. Alle drei sind frei verfügbar, und unten ist die Rechnung
selbst gebaut.

---

# Teil 1: Footprint

Merkmale, die **nur** mit Tickdaten möglich sind — 5-Minuten-Bars geben das
nicht her:

| Merkmal | was es braucht |
|---|---|
| Delta großer vs. kleiner Trades | Größe **jedes einzelnen** Trades |
| Gestapelte Ungleichgewichte (3:1 diagonal) | Kauf/Verkauf **je Preislevel im Bar** |
| POC-Lage innerhalb des Bars | dito |
| Absorption | Volumen gegen Preisfortschritt |
| CVD-Divergenz | kumuliertes Delta gegen Preisverlauf |

## 🛑 Der Fehler in meinem eigenen Skript

Der erste Lauf sah sehr gut aus:

| Merkmal | IC Suche | IC Holdout | Spread | vs. 16 bp |
|---|---|---|---|---|
| CVD-Divergenz 6 h | **+0,2199** | +0,0931 | +24,71 bp | **1,54×** |
| Delta große Trades 6 h | −0,0793 | −0,1009 | −20,13 bp | 1,26× |
| Delta alle Trades 6 h | −0,0589 | −0,0782 | −19,41 bp | 1,21× |
| Trade-Anzahl 6 h | +0,0770 | +0,0426 | +15,97 bp | 1,00× |

**Vier Merkmale über der Kostenschwelle.** Dann habe ich mein eigenes Skript
geprüft:

```python
def z(col):
    g = d.groupby("tag")[col]
    return (d[col] - g.transform("mean")) / g.transform("std")
```

`transform("mean")` über den **ganzen Tag** — also auch über Bars, die zum
Entscheidungszeitpunkt noch nicht existierten. Dasselbe bei der CVD-Divergenz,
die Tagesränge benutzte.

**Das ist Falle Nummer eins aus der Liste dieses Projekts, in meinem eigenen
Code.** Look-ahead, gemessene Wirkung anderswo: Pass-Rate 93 % → 7 %.

## Streng kausal neu gerechnet

Nur nachlaufende 24-Stunden-Fenster, um einen Bar verzögert:

| Merkmal | IC Suche | IC Holdout | Spread | vs. 16 bp | |
|---|---|---|---|---|---|
| mittlere Tradegröße 6 h | +0,0062 | −0,0424 | −23,80 bp | 1,49× | **kippt** |
| **CVD-Divergenz 6 h** | **−0,0021** | +0,0616 | +23,01 bp | 1,44× | **kippt** |
| Trade-Anzahl 6 h | +0,0221 | −0,0658 | −9,51 bp | 0,59× | kippt |
| Anteil großer Trades 6 h | −0,0246 | +0,0260 | +8,21 bp | 0,51× | kippt |
| Ungleichgewicht netto 6 h | −0,0148 | −0,0238 | −8,11 bp | 0,51× | stabil |
| Delta alle Trades 6 h | +0,0043 | −0,0126 | −6,45 bp | 0,40× | kippt |

**Der CVD-IC fällt von +0,2199 auf −0,0021.** Die 0,22 waren vollständig
Look-ahead.

| | |
|---|---|
| Merkmale gesamt | 56 |
| gleiches IC-Vorzeichen in Suche und Holdout | 38 (68 %) |
| **über der Kostenschwelle im Holdout** | **2** |
| **davon vorzeichenstabil** | **0** |

**Null überlebende.** Auch die gestapelten 3:1-Ungleichgewichte — das
Kernkonzept des Footprint-Handels — liegen bei **0,51×** der Schwelle.

---

# Teil 2: Die Liquidations-Karte, selbst gebaut

## Die Rechnung

```
Neue Positionen  =  Zunahme des Open Interest je 5 Minuten
Richtung         =  Taker-Long/Short-Verhältnis
Einstiegskurs    =  Schlusskurs des Bars

Liquidationskurs bei Hebel L:
    Long:   P × (1 − 1/L)        Short:  P × (1 + 1/L)
Hebelmischung:  10× (20 %), 25× (30 %), 50× (30 %), 100× (20 %)
```

Die Masse **zerfällt** (Halbwertszeit 3 Tage, Positionen werden geschlossen)
und **verschwindet**, sobald der Kurs das Niveau durchläuft — dann *wurde*
liquidiert.

| | |
|---|---|
| Bars mit Preis und Open Interest | **227.793** |
| Zeitraum | 2024-06 bis 2026-07 |
| Ø Masse über dem Kurs (±3 %) | 8.540 BTC |
| Ø Masse unter dem Kurs | 6.794 BTC |
| Bars mit ausgelöster Masse | 8,1 % |

## 1. Der Magnet-Test — ein Münzwurf

*„Der Kurs läuft zur größeren Liquidationsmasse."*

| Merkmal | H | IC Suche | IC Holdout | Spread | vs. 16 bp | |
|---|---|---|---|---|---|---|
| Asymmetrie oben/unten | 3 d | +0,0258 | −0,1388 | −143,4 bp | **8,96×** | **kippt** |
| Masse unten | 3 d | −0,0275 | +0,1016 | +115,0 bp | 7,19× | **kippt** |
| Masse oben | 3 d | +0,0222 | −0,1124 | −79,8 bp | 4,99× | **kippt** |
| Abstand größter oben | 3 d | +0,0037 | +0,0725 | +73,9 bp | 4,62× | stabil |
| näher an oben als unten | 3 d | +0,0092 | −0,0265 | −34,5 bp | 2,16× | **kippt** |

| | |
|---|---|
| gleiches Vorzeichen | **16 von 32 = genau 50 %** |
| über 16 bp im Holdout | 6 |
| davon vorzeichenstabil | 2 |

**Genau 50 % Vorzeichenübereinstimmung ist der Erwartungswert eines
Münzwurfs.** Die drei größten Effekte — 8,96×, 7,19×, 4,99× der Kostenschwelle
— **kippen alle das Vorzeichen**. Und die zwei „stabilen" haben im
Suchzeitraum einen IC von +0,0037 bzw. +0,0170, also praktisch null; sie sind
nicht stabil, sie sind zweimal knapp auf derselben Seite gelandet.

Der 3-Tage-Horizont auf 5-Minuten-Bars überlappt 864-fach. Die scheinbar
riesigen Spreads stehen auf einer Handvoll unabhängiger Beobachtungen.

## 2. Nach der Liquidations-Kaskade — Widerspruch

| Zeitraum | n | nach 1 h | nach 6 h | |
|---|---|---|---|---|
| Suche 2024-25 | 1.360 | −0,0 bp | **+7,6 bp** | Fortsetzung |
| **Holdout 2026** | 442 | −5,5 bp | **−14,2 bp** | **Umkehr** |

Der Suchzeitraum sagt Fortsetzung, der Holdout sagt Umkehr. **Beide gängigen
Erzählungen finden im jeweils anderen Zeitraum ihr Gegenteil.**

## 3. Als Risikomaß — und hier ist der Haken ein eigener

| Maß | Rang Suche | Rang Holdout |
|---|---|---|
| Liquidationsmasse gesamt | **−0,287** | **−0,547** |
| gerade ausgelöste Masse | +0,138 | +0,139 |
| **Abwärts-Semivol (1 Tag)** | **0,545** | **0,605** |
| **realisierte Vol (1 Tag)** | **0,553** | **0,616** |

Die Masse korreliert **negativ** mit kommender Volatilität, konsistent und
deutlich. Klingt nach einem Befund — ist aber **vermutlich ein Artefakt meiner
eigenen Konstruktion**: Die Karte wird geleert, wenn der Kurs durchläuft. Viel
angesammelte Masse heißt also vor allem *„der Kurs hat sich zuletzt wenig
bewegt"* — und ruhige Phasen bleiben ruhig. Das misst Volatilitäts-Clustering
auf einem Umweg.

**Und die schlichte realisierte Volatilität schlägt sie ohnehin um Längen**
(0,616 gegen 0,547 im Betrag).

---

## Bilanz

| Behauptung | Ergebnis |
|---|---|
| Footprint schlägt 5-Minuten-Bars | **nein** — 0 von 56 Merkmalen überleben |
| Gestapelte Ungleichgewichte (3:1) | **0,51×** der Kostenschwelle |
| Große Trades zeigen die Richtung | Vorzeichen kippt |
| CVD-Divergenz | **war Look-ahead** (+0,22 → −0,00) |
| Liquidations-Magnet | **50 % Vorzeichentreffer** = Münzwurf |
| Umkehr nach der Kaskade | Suche: Fortsetzung, Holdout: Umkehr |
| Liquidationsmasse als Risikomaß | Artefakt, verliert gegen einfache Vol |

**Sechstes und siebtes Werkzeug getestet, siebtes Mal dasselbe Ergebnis.** Und
diesmal mit den feinsten Daten, die es für diesen Markt überhaupt gibt: jeder
einzelne Trade, jede Positionsveränderung im Fünf-Minuten-Takt.

> **Es lag nicht an der Datenauflösung.** Das war die letzte offene Ausrede,
> und sie ist jetzt gemessen.

---

## Was das ehrlich nicht abdeckt

- **Nur BTC-Futures auf Binance.** Andere Börsen, andere Coins nicht geprüft.
- **72 Tage Footprint**, nicht die volle Historie — für die Kostenrechnung
  reicht das, für seltene Ereignisse nicht.
- **Meine Hebelmischung ist eine Annahme.** Coinglass benutzt eine eigene;
  die Struktur der Rechnung ändert sich dadurch nicht, die genauen Niveaus
  schon.
- **Latenz.** Wer die Daten in Millisekunden statt Minuten verarbeitet,
  handelt etwas anderes. Das ist Market Making, und dafür fehlt die
  Kostenstruktur ([`firmen.md`](firmen.md)).
- **Diskretionäre Anwendung** erfasst kein Backtest.

---

*Skripte in `research/tickdata/`: `fetch.py` (110,9 Mio Trades → Footprints),
`analyse.py` (erster Lauf, mit dem Look-ahead), `analyse2.py` (streng kausal),
`metrics.py` + `kline.py` (Open Interest und Kerzen), `liq.py`
(Liquidations-Karte), `liq_test.py` (Magnet, Kaskade, Risikomaß).*
