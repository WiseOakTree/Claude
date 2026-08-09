# Tageszeit und Sessions — getestet

Vermutung: Die meisten Bewegungen finden während oder kurz vor der
Asia-Session statt.

**Ergebnis: Die Vermutung stimmt nicht — die Bewegung liegt in der
US-Session. Der Eindruck hat aber einen erklärbaren wahren Kern.**

Geprüft auf **allen vier Assets** (BTC, ETH, SOL, XRP), 2021-03 bis 2026-07 —
das ist seit [`heikin_ashi.md`](heikin_ashi.md) der Standard, nachdem sich
gezeigt hat, wie leicht ein Befund auf BTC allein täuscht.

## 1. Wo die Bewegung wirklich ist

Mittlere absolute Stundenrendite, über vier Assets gemittelt:

| Session | Stunden UTC | Bewegung | vs. Tagesmittel |
|---|---|---|---|
| Asien | 00–07 | 51,7 bp | **−7 %** |
| Europa | 08–12 | 50,1 bp | −9 % |
| **US** | **13–20** | **62,9 bp** | **+14 %** |
| vor Asien | 21–23 | 53,6 bp | −3 % |

Stärkste Stunde: **14:00 UTC** (73,5 bp, +33 %) — die US-Eröffnung.
Schwächste: **04:00 UTC** (44,5 bp, −19 %) — mitten in der Asia-Session.

Das Muster ist auf allen vier Assets identisch.

### Der wahre Kern der Vermutung

Die Asia-**Eröffnung** ist tatsächlich laut: 00:00 UTC (Tokio 09:00) liegt mit
64,2 bp auf Platz drei des Tages, 01:00 UTC mit 61,2 bp auf Platz fünf. Danach
fällt die Aktivität steil ab bis zum Tagestief um 04:00.

Wer nachts auf den Chart schaut, sieht also echte Bewegung — nur ist es die
Eröffnungsspitze, nicht die Session. Die Stunden danach sind die ruhigsten des
Tages.

## 2. Gerichtete Drift: nichts

| Session | BTC | ETH | SOL | XRP | Mittel |
|---|---|---|---|---|---|
| Asien | −0,01 | +0,13 | +2,13 | −0,33 | +0,48 bp |
| Europa | +0,50 | +0,42 | +0,77 | −0,42 | +0,32 bp |
| US | −0,16 | −0,30 | −0,03 | +2,72 | +0,56 bp |
| vor Asien | +1,46 | +2,42 | +1,34 | −0,27 | +1,24 bp |

„Vor Asien" sieht mit +1,24 bp am besten aus (BTC p = 0,055), verfehlt aber die
Bonferroni-Schwelle von 0,0125 und ist auf XRP negativ. **Keine handelbare
Richtungsdrift nach Tageszeit.**

## 3. Trägt der S/R-Ausbruch je nach Session unterschiedlich?

| Session | BTC | ETH | SOL | XRP | positiv auf |
|---|---|---|---|---|---|
| Asien | +29,4 | +43,8 | +6,7 | **−26,6** | 3/4 |
| Europa | +26,9 | +4,0 | **−39,0** | −5,9 | 2/4 |
| **US** | **+45,6** | **+27,7** | **+19,6** | **+9,9** | **4/4** |
| vor Asien | +41,4 | +3,3 | +66,6 | +12,9 | 4/4 |
| *alle Stunden* | *+45,7* | *+33,5* | *+18,8* | *−11,3* | — |

**US ist die einzige Session, die auf allen vier Assets positiv ist und dabei
solide Ereigniszahlen hat** (235–335 je Asset). „Vor Asien" ist ebenfalls 4/4,
aber mit den wenigsten Signalen und extremer Streuung (+3,3 bis +66,6).

Bemerkenswert: Auf XRP, wo der Effekt insgesamt negativ ist (−11,3 bp), wird er
in der US-Session **positiv** (+9,9 bp). Der Schaden kommt fast vollständig aus
der Asia-Session (−26,6 bp).

Als Filter auf die Pass-Rate (0,5×, konservative Untergrenze):

| Filter | BTC | ETH | SOL | XRP | **Mittel** |
|---|---|---|---|---|---|
| keiner | 49,4 % | 26,7 % | 20,0 % | 22,5 % | **29,6 %** |
| **nur US** | 59,5 % | 25,2 % | 29,3 % | 17,6 % | **32,9 %** |
| nur Asien | 25,4 % | 41,9 % | 14,9 % | 9,4 % | 22,9 % |
| nur Europa | 18,8 % | 22,1 % | 5,9 % | 23,3 % | 17,5 % |
| nur vor Asien | 0,0 % | 13,1 % | 26,9 % | 14,4 % | 13,6 % |

## Einordnung

Die Beobachtung zur **Bewegungsverteilung** ist statistisch massiv abgesichert
— zehntausende Stunden je Asset, identisches Muster überall. Daran gibt es
nichts zu deuteln: Krypto bewegt sich, wenn die USA wach sind.

Der **US-Session-Filter** für die Strategie ist dagegen nur *suggestiv*:

- dafür: einzige Session mit 4/4 positiven Effekten, beste mittlere Pass-Rate,
  und sie repariert XRP von −11,3 auf +9,9 bp
- dagegen: 16 geprüfte Kombinationen ohne eigenen Holdout, auf ETH und XRP
  wird die Pass-Rate *schlechter*, und der Filter halbiert die Trade-Zahl

Nach dieser Untersuchung sind vier Filter geprüft worden (Mindest-Durchbruch,
Rollenlogik, XGBoost, Heikin-Ashi-Richtung) — **alle vier fielen out-of-sample
durch**. Ein fünfter Filter ohne eigene Out-of-Sample-Prüfung verdient
entsprechend wenig Vertrauen.

**Empfehlung: keine Regeländerung.** Wer den Filter trotzdem nutzen will, hat
mit der US-Session (13–20 UTC) die am besten begründete Wahl — aber die
Begründung ist „am wenigsten widerlegt", nicht „nachgewiesen".
