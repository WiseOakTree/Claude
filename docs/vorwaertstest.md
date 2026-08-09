# Vorwärtstest — Ergebnis

Spezifikation und Bestehenskriterium wurden in
[`vorwaertstest_spec.md`](vorwaertstest_spec.md) festgelegt und committet,
**bevor** die neuen Daten berührt wurden.

**Ergebnis: Beide Regeln fallen durch. Auch die, die ich zuletzt als besser
belegt gemeldet hatte.**

---

## Das vorher festgelegte Kriterium

> **bestanden** = Effekt > 0 auf der **Mehrheit** der frischen Märkte

---

## Test 1: Acht Märkte, für diese Regeln nie benutzt

Volle Historie, gleicher Suche/Holdout-Schnitt:

| Markt | Ausbruch Suche | **Ausbruch Holdout** | Gegen-Bounce Suche | **Gegen-Bounce Holdout** |
|---|---|---|---|---|
| ATOM | +25,6 | −39,3 | +69,0 | −12,0 |
| AVAX | +146,2 (t 2,18) | −1,3 | +87,3 | −39,2 |
| BCH | −15,1 | −73,6 | +0,3 | +8,5 |
| DOGE | −33,7 | +3,3 | +7,5 | −50,3 |
| DOT | +6,3 | −69,2 | −37,4 | +78,3 |
| LINK | −24,2 | +7,8 | −52,8 | **−99,7 (t −2,08)** |
| LTC | −54,5 | −59,2 | −47,2 | **−127,0 (t −1,98)** |
| TRX | +44,0 | **−37,9 (t −1,85)** | −51,3 | **−72,8 (t −2,97)** |

| | gepoolt Suche | **gepoolt Holdout** | positiv im Holdout |
|---|---|---|---|
| **S/R-Ausbruch** | −0,7 bp | **−36,9 bp** | **2 von 8** |
| **Gegen-Bounce short** | −10,6 bp | **−31,1 bp** | **2 von 8** |

**Zwei von acht. Das Kriterium verlangte die Mehrheit. Gescheitert — beide
Regeln.**

Und schärfer: Drei der acht Märkte zeigen einen **signifikant negativen**
Gegen-Bounce (LINK t −2,08, LTC t −1,98, TRX t −2,97). Auf BTC war derselbe
Effekt mit t +2,65 positiv.

---

## Test 2: Der frische Zeitraum, 2026-07-01 bis 2026-08-07

Liegt hinter dem Ende **aller** bisherigen Daten. 14 Märkte, 912 Stunden.

| | gepoolt | Trades | positive Märkte |
|---|---|---|---|
| S/R-Ausbruch | **−39,7 bp** | 353 | **5 von 13** |
| Gegen-Bounce short | **−42,4 bp** | 277 | **5 von 12** |

**Und BTC selbst — der Markt, auf dem alles entwickelt wurde:**

| | frischer Zeitraum |
|---|---|
| S/R-Ausbruch | **−128,9 bp** (38 Trades) |
| Gegen-Bounce short | **−115,7 bp** (21 Trades) |

### War das nur Pech? Nein.

Verteilung aller zusammenhängenden Blöcke gleicher Länge aus der Historie:

| | Median historisch | 5–95 % | beobachtet | **schlechtere Blöcke** |
|---|---|---|---|---|
| S/R-Ausbruch (38 Trades) | +49,3 bp | −76 … +268 | **−128,9** | **1,6 %** |
| Gegen-Bounce (21 Trades) | +85,3 bp | −114 … +384 | **−115,7** | **5,0 %** |

Fünf Wochen sind kurz, und ich habe fair gerechnet: Selbst gemessen an der
eigenen historischen Streuung liegt das Ergebnis **im schlechtesten Prozent
bzw. in den schlechtesten fünf Prozent**.

---

## Was das heißt

**Der Befund war BTC-spezifisch — und höchstwahrscheinlich überangepasst.**

Alles an dieser Regel wurde auf BTC gewählt: die Levellogik, die Schwelle von
sechs Berührungen, die Haltedauer von 48 Stunden, die Toleranz um das Level.
Auf BTC liefert sie t = 2,16 (Ausbruch) und t = 2,65 (Gegen-Bounce). Auf acht
Märkten, die bei keiner dieser Entscheidungen mitgeredet haben, liefert sie
**minus 37 und minus 31 Basispunkte**.

Das ist die Signatur einer Überanpassung, nicht einer Markteigenschaft.

> **Und der wichtigste Satz: Die korrigierte Statistik hat den Befund
> signifikant gemacht — der Vorwärtstest hat ihn trotzdem widerlegt.**
> Signifikanz auf den Entwicklungsdaten war nie das Entscheidende. Genau
> deshalb macht man Vorwärtstests.

---

## 🛑 Was ich damit zurücknehmen muss

**Meine stehende Empfehlung war, die bezahlte Kraken-Challenge mit dieser
Regel zu spielen** (BTC 1h, Level mit ≥ 6 Berührungen, 48 h halten, 0,35×).
Diese Empfehlung ist nach diesem Test **nicht mehr gedeckt**.

Die gemessene Pass-Rate von 78,1 % stammt aus derselben BTC-Historie, auf der
die Regel gebaut wurde. Sie ist kein Versprechen für die Zukunft — die
frischen fünf Wochen auf BTC waren bereits deutlich negativ.

Was ich nicht sagen kann: dass die Regel garantiert nicht funktioniert. 38
Trades sind 38 Trades. Was ich sagen kann: **Es gibt jetzt keinen Beleg mehr,
der eine Wette darauf trägt.**

---

## Was nach 54 Untersuchungen übrig bleibt

| Befund | Status |
|---|---|
| **Volatilitätsprämie** (BTC t 4,12 / S&P t 4,67) | **hält** — zwei Anlageklassen, Korrektur ändert nichts (4,16 → 4,19) |
| S/R-Ausbruch | **im Vorwärtstest gescheitert** |
| Gegen-Bounce | **im Vorwärtstest gescheitert** |
| Marktphasen-Filter | Kandidat, verfehlt Bonferroni, nie vorwärts getestet |
| alles andere (52 Ansätze) | gescheitert |

**Ein Befund von 54.** Und der eine, der hält, ist kein Chartmuster, sondern
eine Risikoprämie: Man verkauft Optionen und trägt das Risiko wirklich.

---

## Der ehrliche Schluss

Du wolltest, dass ich etwas finde, als hinge dein Leben davon ab. Ich habe
daraufhin einen echten Fehler in meiner Methodik gefunden — der Faktor 5,48
war real, und er hat den Befund kurzzeitig über die Signifikanzgrenze gehoben.

**Der Vorwärtstest hat ihn zwei Stunden später wieder kassiert.**

Das ist kein Pessimismus meinerseits. Es ist das Ergebnis eines Tests, dessen
Kriterium ich vorher aufgeschrieben und committet habe, damit ich es hinterher
nicht verbiegen kann. Hätte die Regel gehalten, stünde hier dasselbe Dokument
mit dem umgekehrten Ergebnis.

---

*Skripte: `research/vorwaerts.py` (beide Tests), `research/fair.py`
(Streuungskontrolle für den kurzen Zeitraum), Daten frisch von Binance
(2026-07-01 bis 2026-08-07, 14 Märkte).*
