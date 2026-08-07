# VWAP getestet

Guter Vorschlag, und zwar aus einem strukturellen Grund: **Der VWAP ist der
einzige der vier, der Volumen benutzt.** MACD, Stochastik und Bollinger lesen
alle nur den Preis. Wenn irgendwo neue Information steckt, dann dort.

Ergebnis: **Als Kurslinie ist er ein gleitender Durchschnitt. Als Bandbreite
schlägt er die Bollinger-Bänder — und zwar genau wegen des Volumens.**

---

## Vorfrage: Ist der VWAP überhaupt etwas anderes als ein Durchschnitt?

| Markt | Fenster | VWAP ↔ SMA | Abstand zu VWAP ↔ Abstand zu SMA | Ø \|Differenz\| |
|---|---|---|---|---|
| BTC | 20 Bars | **+0,9999** | +0,9819 | 0,346 % |
| BTC | 50 Bars | **+0,9999** | +0,9871 | 0,515 % |
| ETH | 20 Bars | +0,9996 | +0,9797 | 0,469 % |
| ETH | 50 Bars | +0,9992 | +0,9848 | 0,714 % |

**Die VWAP-Linie ist praktisch identisch mit einem schlichten gleitenden
Durchschnitt.** Wer über den VWAP entscheidet, entscheidet über die SMA — der
Unterschied liegt im Mittel bei einem Drittel bis dreiviertel Prozent.

---

## Als Richtungsinformation: nichts

Abstand zum Tages-VWAP, unterstes gegen oberstes Quintil, 5 Tage voraus:

| Markt | Zeitraum | unter VWAP | über VWAP | Spanne | t |
|---|---|---|---|---|---|
| BTC | Suche 21-24 | +0,26 % | +0,46 % | −0,20 | −0,38 |
| BTC | **Holdout** | −0,37 % | −0,56 % | **+0,19** | −0,09 |
| ETH | Suche 21-24 | +0,72 % | +0,91 % | −0,20 | −0,28 |
| ETH | **Holdout** | −0,56 % | −0,99 % | **+0,42** | +0,04 |
| SOL | Suche 21-24 | +2,80 % | +2,20 % | +0,60 | +0,10 |
| SOL | **Holdout** | −0,31 % | −1,02 % | +0,71 | +0,16 |

Alle sechs t-Werte zwischen −0,38 und +0,16.

## Als Signal: zwölf von zwölf negativ

VWAP-Kreuzung, bp je Trade nach Kosten:

| Markt | VWAP-Art | Suche | Holdout |
|---|---|---|---|
| BTC | Tages-VWAP | −14,8 (3.153) | −15,7 (1.176) |
| BTC | Wochen-VWAP | −13,1 | −15,7 |
| BTC | rollierend 50 | −2,5 | −15,7 |
| ETH | Tages-VWAP | −13,5 | −6,2 |
| ETH | Wochen-VWAP | −12,8 | −4,2 |
| ETH | rollierend 50 | −5,7 | −28,3 |

**Keine einzige positive Zelle.** Die Tages-VWAP-Kreuzung feuert auf 4h etwa
780-mal im Jahr — das sind über 100 % Gebühren jährlich.

## Als zehnter Filter auf das S/R-Signal: gescheitert

| Variante | Suche 21-24 | **Holdout 25-26** |
|---|---|---|
| ohne Filter (Ausgangslage) | +49,4 bp (474) | **+52,2 bp (301)** |
| nur im Einklang mit Tages-VWAP | +71,2 bp (365) | +53,8 bp (235) |
| **nur im Einklang mit VWAP(50)** | **+89,4 bp (324)** | **+26,1 bp (188)** |
| gegen den Tages-VWAP | −23,8 bp (109) | **+46,8 bp (66)** |

Im Suchzeitraum sieht der Filter hervorragend aus: +49 → **+89 bp**, und die
aussortierten Trades sind mit −23,8 bp tatsächlich schlecht.

Im Holdout **halbiert er den Effekt** (+52 → +26), und die aussortierten
Trades liefern **+46,8 bp** — sie waren völlig in Ordnung.

> **Das ist Filter Nummer zehn, und er fällt durch wie die neun davor.**
> Der Zähler steht weiter bei null.

---

## 🟢 Aber die Bänder: hier steht etwas

Rangkorrelation mit der Zukunft, 4h-Bars, **Holdout 2025-26**:

| Markt | Maß | Vol 5 T | **Tag ≤ −3 %** |
|---|---|---|---|
| BTC | **VWAP-Bandbreite (20)** | **0,420** | **0,241** |
| BTC | Abwärts-Semivol 20 | 0,409 | **0,301** |
| BTC | Bollinger-Breite (20,2) | 0,365 | 0,200 |
| BTC | \|Abstand\| zum Tages-VWAP | 0,136 | 0,078 |
| BTC | Volumen / Ø20 | −0,007 | 0,000 |
| ETH | **VWAP-Bandbreite (20)** | **0,366** | **0,166** |
| ETH | Abwärts-Semivol 20 | 0,361 | 0,168 |
| ETH | Bollinger-Breite (20,2) | 0,305 | 0,148 |

**Die VWAP-Bandbreite schlägt die Bollinger-Breite in jeder Spalte auf beiden
Märkten** — und liegt bei der Vol-Prognose sogar knapp vor der Abwärts-Semivol.

### Und der Vorsprung kommt nachweislich vom Volumen

Vier Bandbreiten, die sich in genau zwei Merkmalen unterscheiden — typischer
Preis (HLC/3) statt Schlusskurs, und volumengewichtet statt ungewichtet:

| Variante | BTC Vol | BTC Tag ≤ −3 % | ETH Vol | ETH Tag ≤ −3 % |
|---|---|---|---|---|
| Schlusskurs, ungewichtet *(= Bollinger)* | 0,365 | 0,200 | 0,305 | 0,148 |
| typ. Preis, ungewichtet | 0,365 | 0,201 | 0,300 | 0,147 |
| **Schlusskurs, volumengewichtet** | **0,415** | **0,239** | **0,363** | **0,164** |
| **typ. Preis, volumengewichtet** *(= VWAP)* | **0,420** | **0,241** | **0,366** | **0,166** |

Die Zerlegung ist eindeutig:

- **HLC/3 statt Schlusskurs bringt null** (0,365 → 0,365 / 0,200 → 0,201)
- **Volumengewichtung bringt alles** (0,365 → 0,415 / 0,200 → 0,239)

> **Dein Vorschlag hat als erster etwas hinzugefügt — und zwar genau die
> Größe, die den anderen drei Indikatoren fehlt.**

Die Mechanik dahinter ist plausibel, aber nicht bewiesen: Eine
volumengewichtete Streuung misst, wie weit der Preis in den Bars gestreut hat,
in denen **wirklich gehandelt wurde**. Eine ruhige Nacht mit wenig Umsatz zählt
kaum; ein Abverkauf mit hohem Umsatz zählt voll. Für das Risiko der nächsten
Tage ist das offenbar die relevantere Frage.

---

## Praktisch

**In TradingView:** Der eingebaute Indikator heißt **VWAP** (Suchbegriff
„VWAP"), mit Bändern unter **„VWAP" → Einstellungen → Bands**. Es gibt auch
**Anchored VWAP** (Anker frei wählbar) und **Rolling VWAP**.

**Für das Risiko-Panel** (`tradingview/risiko_panel.pine`) ist es diese
Rechnung:

```pine
tp   = (high + low + close) / 3
vw   = math.sum(tp * volume, 20) / math.sum(volume, 20)
var_ = math.sum(math.pow(tp - vw, 2) * volume, 20) / math.sum(volume, 20)
vwb  = 2 * math.sqrt(var_) / vw
rang = ta.percentrank(vwb, 1000)        // nur der Rang zaehlt
```

**Und dieselben zwei Regeln wie vorher:** kein absoluter Schwellenwert (nur
Perzentile), und **nicht zur Positionssteuerung** — gemessen senkt jede
Vol-gesteuerte Größe die Pass-Rate um 9–15 Punkte.

---

## Die Bilanz für den VWAP

| Verwendung | Ergebnis |
|---|---|
| als Kurslinie / Durchschnitt | **identisch mit der SMA** (+0,9999) |
| als Richtungsinformation | nichts (t −0,38 bis +0,16) |
| als Ein-/Ausstiegssignal | **12 von 12 Zellen negativ** |
| als Filter auf das S/R-Signal | **gescheitert** — Filter Nr. 10 |
| **als Bandbreite / Risikomaß** | **besser als Bollinger, auf beiden Märkten** |

Genau dasselbe Muster wie bei den anderen drei: **über die Richtung leer, über
das Risiko brauchbar.** Nur ist der VWAP dort besser als alles, was du bisher
benutzt.

---

*Skripte: `research/vwap.py` (Vorfrage, Richtung, Signal),
`research/vwap2.py` (Bandbreite in der Risiko-Rangliste, Filtertest auf das
S/R-Signal), `research/vwap3.py` (Zerlegung: Volumen oder typischer Preis).*
