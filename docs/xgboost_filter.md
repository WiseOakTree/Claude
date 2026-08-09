# XGBoost als Signalfilter — getestet

Vorschlag: XGBoost ausprobieren.

Diesmal in der **richtigen** Rolle. In [`ml_ceiling.md`](ml_ceiling.md) ging es
darum, ob ein Modell die Kursrichtung aus dem Nichts vorhersagen kann — dafür
wären 60 % Trefferquote nötig, unerreichbar. Jetzt gibt es eine Signalmenge mit
**bereits positivem Erwartungswert** (Ausbrüche, +27,8 bp bei ≥4 Berührungen).
Die Frage ist nur noch: Kann ein Modell die guten von den schlechten trennen?

Das ist ein Filterproblem, kein Prognoseproblem — und deutlich leichter.

**Ergebnis: XGBoost findet nichts. Auf der tatsächlich gehandelten Menge macht
der Filter das Ergebnis sogar schlechter.**

## Aufbau

| | |
|---|---|
| Ereignisse | 1.757 Ausbrüche (BTC, ≥4 Berührungen, Suchzeitraum 2021-03..2024-12) |
| Merkmale | 21, alle **nur zum Signalzeitpunkt bekannt** |
| Ziel | vorzeichenrichtige 24-h-Folgerendite in bp |
| Modell | XGBoost, Tiefe 3, stark regularisiert (`min_child_weight=20`, `reg_lambda=5`) |

Die Merkmale decken ab: Levelstärke, Durchdringungstiefe, Volatilitätsregime
und -änderung, Momentum über fünf Zeitfenster, Bar-Struktur (Spanne, Lage des
Schlusskurses, Körperanteil), Volumenverhältnis, Umfeld (Zahl aktiver Level,
Abstand zum nächsten Gegenlevel), Lage im 24-h-Fenster, Uhrzeit und Wochentag.

### Zwei methodische Vorkehrungen

**Purged Walk-Forward-CV.** Die Ausgänge überlappen sich über 24 Stunden.
Normale Kreuzvalidierung würde Information aus der Zukunft in die
Trainingsdaten lecken. Getestet wird deshalb immer auf dem *nächsten* Block,
mit einer Sperrzone von 24 Bars davor.

**Nullmodell.** Dieselbe Prozedur mit **zufällig gemischten Zielwerten**,
20 Wiederholungen. Was dort herauskommt, ist das Rauschniveau — jedes echte
Ergebnis muss deutlich darüber liegen.

## In-Sample: grenzwertig

| Auswahl | n | Ergebnis | Vorsprung |
|---|---|---|---|
| alle | 1.256 | +26,4 bp | — |
| beste Hälfte | 628 | +36,6 bp | **+10,2 bp** |
| beste 30 % | 377 | +55,8 bp | +29,4 bp |

Rangkorrelation Vorhersage/Ausgang: **+0,073** (p = 0,010).

Klingt brauchbar — bis zum Nullmodell:

| | Vorsprung |
|---|---|
| Nullmodell (gemischte Ziele) | +1,8 bp, Streuung 7,5 |
| **echtes Modell** | **+10,2 bp** |
| Abstand | **+1,1 Standardabweichungen** |
| Anteil der Nullmodelle, die das echte schlagen | **5 %** |

Nur 1,1 Standardabweichungen über reinem Zufall. Und die Merkmalsgewichte sind
**völlig flach** (0,051 bis 0,061 über die ersten acht) — bei einem echten
Muster würden ein oder zwei Merkmale dominieren. Beides deutet auf Rauschen.

## Out-of-Sample: zerfällt

Das Modell wurde **einmal** auf dem Suchzeitraum trainiert und dann auf
ungesehene Daten angewandt.

| Datensatz | ungefiltert | beste Hälfte | Vorsprung | Rangkorrelation |
|---|---|---|---|---|
| BTC-Holdout, ≥4 Ber. | +10,9 bp | +18,6 bp | +7,7 bp | +0,033 (p = 0,32) |
| **BTC-Holdout, ≥6 Ber.** | **+38,2 bp** | **+30,2 bp** | **−8,0 bp** | −0,078 (p = 0,17) |
| ETH, ≥4 Ber. | +8,1 bp | +10,7 bp | +2,5 bp | +0,008 (p = 0,68) |
| ETH, ≥6 Ber. | +16,1 bp | +43,5 bp | +27,5 bp | +0,065 (p = 0,06) |

**Kein einziger Wert erreicht Signifikanz.** Die Vorsprünge streuen zwischen
**−21,4 bp und +38,7 bp** ohne erkennbares Muster — das ist genau das Bild, das
ein überangepasstes Modell auf neuen Daten erzeugt.

Entscheidend ist die zweite Zeile: Auf der **tatsächlich gehandelten Menge**
(BTC, ≥6 Berührungen) macht der Filter das Ergebnis **schlechter** — von
+38,2 bp auf +30,2 bp bei halber Auswahl, auf +16,8 bp bei den besten 20 %.
Wer diesem Modell folgt, wirft die guten Signale weg.

## Warum es scheitert

**Die Stichprobe.** 1.757 Ereignisse klingen nach viel, sind es aber nicht: Bei
24-Stunden-Ausgängen und überlappenden Fenstern bleiben einige hundert
unabhängige Beobachtungen für ein Modell mit 21 Merkmalen. Das reicht nicht.

**Der vorhandene Filter ist schon der beste.** Die Berührungszahl trennt bereits
sauber (+0,88 bp bei 2 Berührungen bis +19,47 bp bei 8). Was danach übrig
bleibt, ist offenbar Rauschen — und Rauschen lässt sich nicht sortieren.

**Das bestätigt die frühere Obergrenzenrechnung.** In
[`ml_ceiling.md`](ml_ceiling.md) stand: ML ist ein Werkzeug zur Extraktion von
Information, kein Ersatz für sie. Der Unterschied ist nur, dass es dort per
Orakel argumentiert wurde und hier mit einem tatsächlich trainierten Modell —
mit demselben Ergebnis.

## Praktische Folge

Keine. Die Handelsregel bleibt: Level mit ≥6 Berührungen, Einstieg beim Bruch,
kein Stop, nach 24–48 Stunden raus, halbe Positionsgröße.

*Hinweis: `xgboost` und `scikit-learn` werden nur für diesen Forschungsteil
gebraucht, nicht vom Paket selbst. Skripte unter `research/`.*
