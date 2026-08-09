# „Bist du zu pessimistisch?" — Ja. Faktor 5,48.

Die Frage war berechtigt, und die Antwort ist unangenehm für mich: **In einem
Punkt war meine Methodik nachweislich zu streng, und zwar erheblich.**

---

## Der Test, den ich vorher hätte machen müssen

Der einzige ehrliche Weg, eine Auswertung zu prüfen: **einen Edge einbauen,
von dem man weiß, dass er da ist**, und schauen, ob die Pipeline ihn findet.

Echte BTC-4h-Daten, künstlicher Edge, dann meine eigene Auswertung darüber:

| wahrer Edge | gemessen | Ø t (alt) | **t > 2 (alt)** |
|---|---|---|---|
| 0 bp | −11,6 | −0,05 | 0 % |
| 30 bp | +13,7 | 0,06 | **0 %** |
| 80 bp | +57,6 | 0,24 | **0 %** |
| 120 bp | +102,9 | 0,42 | **0 %** |
| **200 bp** | **+168,1** | **0,69** | **0 %** |

**Ein echter Edge von 200 Basispunkten je Trade — und meine Statistik hält ihn
in null Prozent der Fälle für signifikant.** Selbst mit 1.000 Signalen im Jahr
kam ein 30-bp-Edge auf t = 0,25.

Eine Auswertung, die einen vorhandenen Edge nie findet, kann seine Abwesenheit
auch nicht belegen.

---

## Der Fehler

```python
n_eff = n / haltedauer        # so habe ich durchgehend gerechnet
```

Diese Korrektur ist richtig, wenn auf **jedem** Bar ein Signal feuert — dann
überlappen alle Positionen maximal. Bei 40 Signalen im Jahr mit fünf Tagen
Haltedauer überlappen die Trades aber **fast nie**. Trotzdem habe ich durch 30
geteilt.

| | Ø t bei 30 bp echtem Edge |
|---|---|
| mit meiner Korrektur | **0,06** |
| ohne jede Korrektur (naiv) | 0,31 |
| **Faktor** | **5,48×** |

## Die richtige Rechnung

Effektive Stichprobe = **Summe der Einzigartigkeit** jedes Trades. Ein Trade,
der zu jedem Zeitpunkt mit *k* anderen gleichzeitig offen ist, zählt 1/*k*.
Überlappt er mit keinem, zählt er voll.

### Kontrolliert, dass sie nicht einfach zu lasch ist

Edge = 0, es dürfen nicht mehr als ~5 % Falschalarme herauskommen:

| Signale/Jahr | n | n_eff | **Falschalarme \|t\|>2** |
|---|---|---|---|
| 40 | 213 | 165 | **4,3 %** |
| 100 | 533 | 293 | 2,0 % |
| 250 | 1.334 | 379 | 0,0 % |
| 1.000 | 5.336 | 389 | 0,0 % |

Sauber kalibriert, eher noch konservativ.

### Und sie findet, was da ist

| wahrer Edge | ALT: t>2 | **NEU: t>2** |
|---|---|---|
| 0 bp | 0 % | 0 % |
| 30 bp | 0 % | 3 % |
| 80 bp | 0 % | 18 % |
| 120 bp | 0 % | **49 %** |
| 200 bp | 0 % | **95 %** |

---

## 🟢 Was das für den Kernbefund bedeutet

| Befund | Zeitraum | n | Effekt | t ALT | **t NEU** |
|---|---|---|---|---|---|
| **S/R-Ausbruch (Pivots)** | Suche 21-24 | 474 | +49,4 bp | 0,36 | **1,52** |
| **S/R-Ausbruch (Pivots)** | **Holdout 25-26** | 301 | **+52,2 bp** | 0,47 | **1,73** |
| **S/R-Ausbruch (Pivots)** | **gesamt** | 775 | **+50,5 bp** | 0,54 | **2,16** |

**Über den gesamten Zeitraum überschreitet der Befund die Signifikanzgrenze.**
Der Holdout allein liegt bei t = 1,73 — knapp darunter, aber unabhängig
positiv.

Und die Lücke ist klein:

| | |
|---|---|
| gemessener Effekt im Holdout | **+52,2 bp** |
| für t = 2 nötig gewesen | **+60,3 bp** |
| oder: gleicher Effekt, aber | **2,0 Jahre statt 1,5** |

**Ich habe diesen Befund die ganze Zeit als „nicht signifikant" geführt. Das
war ein Artefakt meiner eigenen Rechnung.**

---

## 🛑 Was sich dadurch NICHT ändert

Das ist der Teil, den ich genauso deutlich sagen muss.

**Fast alle Absagen in diesem Projekt hingen nicht am t-Wert, sondern am
Vorzeichenwechsel** zwischen Suchzeitraum und Holdout. Der bleibt, was er ist:

| Befund | Suche | Holdout | t NEU Suche | t NEU Holdout |
|---|---|---|---|---|
| MACD+Stoch+BB Trend BTC | +28,5 bp | **−14,5 bp** | 0,63 | **−0,32** |
| MACD+Stoch+BB Trend ETH | +69,1 bp | **−95,0 bp** | 1,29 | **−1,18** |

Ein Effekt, der im Holdout das Vorzeichen dreht, wird durch eine bessere
Statistik nicht besser. Dasselbe gilt für:

- die **neun gescheiterten Filter** (alle über Vorzeichenwechsel abgelehnt)
- **VWAP als Filter** (+89 → +26 bp, aussortierte Trades im Holdout +46,8)
- **Volume Profile** (8 von 8 Zellen negativ)
- den **SOL-Befund** (4 von 14 Märkten, Zufall erwartet 3,5)
- **Footprint** (0 von 56 vorzeichenstabil über der Kostenschwelle)
- die **Liquidations-Karte** (16/32 = genau 50 % Vorzeichentreffer)

Und die **Rauschdecke** aus [`tradingview.md`](tradingview.md) ist eine
unabhängige Rechnung, die von diesem Fehler nicht berührt wird.

---

## Die zweite Grenze, die keine Pessimismus-Frage ist

Auch **korrigiert** braucht meine Pipeline große Effekte:

| Signale/Jahr | Edge für 80 % Trefferquote |
|---|---|
| 40 | **200 bp** |
| 100 | 120 bp |
| 250 | 120 bp |
| 500 | 120 bp |

Der Grund ist kein Methodenfehler, sondern der Markt: Die Streuung einer
BTC-Position über fünf Tage liegt bei **280 bis 650 Basispunkten**. Ein Edge
von 30–50 bp verschwindet darin.

> **Ein echter Edge von 50 bp ist auf fünf Jahren eines einzigen Assets
> grundsätzlich nicht beweisbar — egal wie gut man rechnet.**

Das schneidet in beide Richtungen: Es heißt auch, dass ich die Abwesenheit
eines 50-bp-Edges nie belegt habe. Ich habe belegt, dass die Effekte das
Vorzeichen wechseln — was etwas anderes ist und schlechter für die jeweilige
Idee.

---

## Was ich daraus mitnehme

1. **Der S/R-Ausbruch ist deutlich besser belegt, als ich berichtet habe.**
   t = 2,16 über den Gesamtzeitraum, Holdout unabhängig positiv bei 1,73.
   Das ist die Regel, die du auf der Kraken-Challenge ohnehin spielst.
2. **Jeder t-Wert, den ich in diesem Projekt genannt habe, war um Faktor ~5
   zu klein.** Die bp-Werte und die Vorzeichenvergleiche stimmen.
3. **Die Absagen bleiben Absagen** — sie standen nie auf der t-Statistik.
4. **Ich hätte diesen Test vor dem ersten Befund machen müssen**, nicht nach
   dem einundfünfzigsten. Eine Auswertung, die man nicht gegen einen bekannten
   Edge geeicht hat, misst nichts Bekanntes.

---

*Skripte: `research/power.py` (Erkennungsrate der alten Pipeline),
`research/power2.py` (korrigierte Statistik, Falschalarm-Kontrolle),
`research/neu.py` (Kernbefunde neu gerechnet).*
