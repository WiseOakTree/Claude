# Vorwärtstest — Spezifikation VOR dem Test

Festgelegt am 2026-08-08, **bevor** die neuen Daten berührt wurden.
Kein Parameter wird nach dem Test geändert.

## Die zwei Regeln

**A) S/R-Ausbruch** (validiert, t = 2,16 gesamt)
```
Level aus Pivots, >= 6 Beruehrungen
Schlusskurs durchbricht das Level -> in Bruchrichtung
48 Stunden halten, kein Stop
Kosten 8 bp je Seite
```

**B) Gegen-Bounce, nur SHORT** (Kandidat, t = 2,65 im Holdout)
```
Kurs laeuft in eine UNTERSTUETZUNG (>= 6 Beruehrungen),
Schluss bleibt darueber (= klassisches Bounce-Long-Signal)
-> stattdessen SHORT
48 Stunden halten, kein Stop
```

## Drei unberührte Datenquellen

1. **Frischer Zeitraum**: 2026-07-01 bis heute — liegt hinter dem Ende
   aller bisherigen Daten (2026-06-30). Nie berührt.
2. **Frische Märkte**: ATOM, AVAX, BCH, DOGE, DOT, LINK, LTC, TRX —
   für diese beiden Regeln nie getestet.
3. **Andere Anlageklasse**, falls beschaffbar.

## Was als bestanden gilt — vorher festgelegt

| | S/R-Ausbruch | Gegen-Bounce short |
|---|---|---|
| Vorhersage | > 0 bp | > 0 bp |
| erwartete Groesse | ~+50 bp | ~+100 bp |
| **bestanden** | Effekt > 0 auf der **Mehrheit** der frischen Maerkte |
| **klar bestanden** | zusaetzlich gepoolt t > 2 |
| **gescheitert** | Mehrheit negativ oder gepoolt < 0 |

Der frische Zeitraum allein ist zu kurz für Signifikanz — er zaehlt als
Richtungsangabe, nicht als Beweis. Entschieden wird ueber die frischen
Maerkte.
