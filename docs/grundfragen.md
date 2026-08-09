# Die vier Grundfragen — ohne Strategie, ohne Indikator

> „Ist es gerade wahrscheinlicher, dass der Preis runter oder rauf geht? Und zu
> welcher Uhrzeit? Und wie viel Risiko geht man ein? Und wenn man falsch liegt:
> was war der Grund?"

Das sind die einzigen vier Fragen, die zählen. Alles andere in diesem Projekt
war ein Umweg. Hier die gemessenen Antworten, BTC 1h, 2021-03 bis 2026-07.

---

## 1. Rauf oder runter? — Du kannst es nicht wissen.

| Horizont | P(rauf) | Suchzeitraum | **Holdout** | Ø Rendite | p-Wert |
|---|---|---|---|---|---|
| 1 Stunde | 50,4 % | 50,6 % | **50,0 %** | +0,2 bp | 0,406 |
| 4 Stunden | 50,5 % | 50,7 % | **50,0 %** | +0,9 bp | 0,408 |
| 1 Tag | 50,9 % | 51,1 % | 50,3 % | +5,3 bp | 0,419 |
| 2 Tage | 51,1 % | 51,5 % | 50,3 % | +10,2 bp | 0,425 |
| 1 Woche | 51,3 % | 52,4 % | **48,6 %** | +36,8 bp | 0,422 |

**50,4 %.** Das ist die Antwort auf die erste Frage, über 47.000 Stunden.

Und der winzige Aufwärtsdrall **verschwindet im Holdout** — auf Wochensicht
kippt er sogar ins Negative (48,6 %). Kein einziger p-Wert liegt unter 0,40.

Das ist keine Schwäche der Messung. Das ist der Markt. Wäre es anders,
gäbe es die Frage nicht.

**Praktisch:** Jede Aussage der Form „jetzt geht es wahrscheinlich rauf" ist
zu ungefähr 50,4 % richtig. Bei 16 bp Kosten je Roundtrip brauchst du 50,8 %,
nur um bei null herauszukommen.

---

## 2. Uhrzeit? — Zwei Stunden, aber zu klein zum Handeln.

Mittlere Rendite der *nächsten* Stunde, nach Einstiegszeit (UTC):

| UTC | P(rauf) | Ø bp | p roh | **p nach Bonferroni** | Such | Holdout |
|---|---|---|---|---|---|---|
| **20** | 54,0 % | **+3,0** | 0,027 | 0,653 | +3,0 | **+3,0** |
| **21** | 51,4 % | **+3,2** | 0,016 | 0,376 | +3,3 | **+2,8** |
| 12 | 47,1 % | −0,2 | 0,893 | 1,000 | +1,6 | −5,0 |
| 15 | 46,7 % | −1,1 | 0,452 | 1,000 | −0,3 | −3,3 |
| 22 | 50,2 % | −1,8 | 0,159 | 1,000 | −1,1 | −3,6 |

**Nach Korrektur für 24 Tests: keine einzige Stunde signifikant.**

Aber eine Beobachtung ist trotzdem etwas wert: **20 und 21 Uhr UTC sind die
einzigen Stunden, die in beiden Zeiträumen gleich aussehen** (+3,0/+3,0 und
+3,3/+2,8). Alle anderen kippen zwischen Suchzeitraum und Holdout. Das ist die
US-Nachmittagssitzung — bei uns **22 bis 23 Uhr** (Sommerzeit).

**Der Haken ist die Größenordnung.** +3 bp. Die Kostenschwelle liegt bei 16 bp.
Der Unterschied zwischen der besten und der schlechtesten Stunde des Tages
beträgt **5,0 bp** — ein Drittel dessen, was ein Trade kostet.

**Praktisch:** Als Handelsgrund taugt die Uhrzeit nicht. Als Tiebreaker taugt
sie: Wenn du ohnehin einsteigen wirst und die Wahl hast, nimm 20–21 Uhr UTC.
Das ist alles, was die Uhrzeit hergibt.

---

## 3. Wie viel Risiko? — Genau so viel, dass ein schlechter Tag dich nicht killt.

10.000-$-Konto, vereinfachte Regel (eine Position, 48 h):

| Größe | Nominal | Ø Tag | **schlechtester Tag** | Tage unter −3 % | Tage unter −2 % |
|---|---|---|---|---|---|
| 0,25× | 2.500 $ | +1 $ | **−3,70 %** | 0,10 % | 0,10 % |
| **0,35×** | **3.500 $** | +2 $ | **−5,16 %** | **0,10 %** | 0,36 % |
| 0,50× | 5.000 $ | +3 $ | −7,31 % | 0,36 % | 1,08 % |
| 1,00× | 10.000 $ | +6 $ | −14,21 % | 1,69 % | 2,36 % |

Kraken bricht ab bei **−3 % an einem Tag (−300 $)** oder −6 % gesamt (−600 $).

**Die unbequeme Zeile ist die erste.** Selbst bei 0,25× gab es in 1.948 Tagen
einen Tag mit −3,70 %. Es gibt **keine vernünftige Größe, die dich immun
macht.** Unter 0,20× wärst du jedem historischen Tag entkommen — aber dann
liegt deine Jahresvolatilität bei ~5 %, und bei 5 % Vol beträgt die Pass-Rate
**4,9 %** ([`zufall.md`](zufall.md)). Du überlebst und kommst nie an.

**Die ehrliche Beschreibung von 0,35×:** Du akzeptierst eine Chance von rund
**1 zu 1.000 pro Tag**, sofort und ohne Vorwarnung auszuscheiden. Dafür
bekommst du 13 % Jahresvolatilität — genug, um das Ziel zu erreichen. Das ist
der Handel. Er ist nicht wegzuoptimieren.

Und: **+2 $ pro Tag im Mittel.** So sieht ein echter Edge aus. Nicht wie ein
Chart mit Pfeilen.

---

## 4. Wenn man falsch lag — was war der Grund?

213 Trades der vereinfachten Regel. Trefferquote **55,9 %**, Ø **+67 bp**,
Median +29 bp. Ø Gewinn **+308 bp**, Ø Verlust **−238 bp**.

| Unterscheidung | Gruppe A | Gruppe B | **p** |
|---|---|---|---|
| Richtung | LONG +55 bp (51 %, n=100) | SHORT +78 bp (60 %, n=113) | 0,682 |
| Bruch mit dem Trend? | mit Trend +84 bp (53 %, n=147) | gegen +30 bp (62 %, n=66) | 0,371 |
| Volatilität | hoch +18 bp (48 %, n=102) | niedrig **+112 bp** (63 %, n=111) | 0,088 |
| Berührungen | ≥8 **+159 bp** (65 %, n=43) | 6–7 +44 bp (54 %, n=170) | 0,095 |
| Durchdringung | ≥0,25 ATR +46 bp | knapp +100 bp | 0,335 |
| Uhrzeit 19–22 UTC | abends +126 bp (n=34) | sonst +56 bp | 0,356 |
| Wochenende | Sa/So +88 bp (n=40) | Mo–Fr +62 bp | 0,712 |

**Nichts ist signifikant.** Die beiden besten Kandidaten — niedrige
Volatilität (p=0,088) und viele Berührungen (p=0,095) — verfehlen die Schwelle,
und **beide wurden in diesem Projekt bereits als Filter getestet und sind
out-of-sample durchgefallen** ([`einfach.md`](einfach.md),
[`sr_bounce.md`](sr_bounce.md)).

### Die sechs größten Einzelverluste

| Datum | Richtung | Verlust | Trend | Volatilität | Berührungen |
|---|---|---|---|---|---|
| 2022-11-08 06:00 | LONG | **−1571 bp** | gegen | hoch | 6 |
| 2021-05-12 03:00 | LONG | −1505 bp | mit | niedrig | 6 |
| 2023-06-19 18:00 | SHORT | −1388 bp | gegen | hoch | 6 |
| 2022-08-17 17:00 | LONG | −872 bp | gegen | hoch | 6 |
| 2021-05-03 07:00 | LONG | −684 bp | mit | niedrig | 7 |
| 2022-04-18 04:00 | SHORT | −665 bp | mit | hoch | 6 |

Long und Short. Mit Trend und gegen Trend. Hohe Vol und niedrige Vol. Morgens,
mittags, abends. **Es gibt kein gemeinsames Merkmal.**

Zum Vergleich: Der 8. November 2022 war der Tag des FTX-Zusammenbruchs.
Das ist der „Grund" — und er stand am 7. November in keinem Chart.

### Die Antwort auf Frage 4

**Es gab keinen Grund, den du vorher hättest wissen können.** Die Verlierer
sehen genau aus wie die Gewinner. Das ist nicht Resignation, das ist das
Messergebnis von 213 Trades und sieben geprüften Merkmalen.

Wer nach dem Trade einen Grund findet, hat den Grund erfunden. Das ist die
Tätigkeit, die als „Trading-Journal führen" verkauft wird.

**Was tatsächlich passiert:** Deine Verluste sind −238 bp im Schnitt, deine
Gewinne +308 bp, und du hast in 55,9 % der Fälle recht. Der Edge steckt in
dieser Asymmetrie — nicht in einem erkennbaren Merkmal einzelner Trades.
Deshalb funktioniert **kein** Filter: Es gibt nichts zu filtern.

---

## Die vier Antworten auf einer Karte

```
1. RAUF ODER RUNTER?
   50,4 %. Im Holdout 50,0 %. Du kannst es nicht wissen.
   Fuer Kostendeckung braeuchtest du 50,8 %.

2. UHRZEIT?
   20-21 Uhr UTC (22-23 Uhr bei uns) ist die einzige Zeit,
   die in beiden Zeitraeumen gleich aussieht: +3 bp.
   Zu klein zum Handeln. Nur als Tiebreaker.

3. WIE VIEL RISIKO?
   0,35x = 3.500 $ Nominal bei 10.000 $ Konto.
   Schlechtester Tag der Historie: -5,16 %.
   Es gibt KEINE Groesse ohne Risiko -- nur zu klein
   (kommst nie an) oder zu gross (fliegst raus).

4. WARUM WAR ICH FALSCH?
   Es gab keinen erkennbaren Grund. Sieben Merkmale geprueft,
   keines signifikant. Verlierer sehen aus wie Gewinner.
   Der Edge liegt in +308 gegen -238 bp, nicht im Einzeltrade.
```

**Und daraus folgt das ganze Projekt:** Wenn Frage 1 und 4 keine Antwort haben,
bleiben nur Frage 2 (zu klein) und Frage 3. **Risikogröße ist die einzige der
vier Fragen, auf die es eine belastbare Antwort gibt.** Deshalb war
Positionsgröße von Anfang an der stärkste Hebel — nicht weil sie clever ist,
sondern weil sie das Einzige ist, was du kontrollierst.

---

*Skripte: `research/basics.py` (Fragen 1 und 2), `research/basics2.py`
(Fragen 3 und 4).*
