# Was sagt mehr über Risiko als die Bollinger-Bänder?

Vierzehn Kandidaten gegen die Bänder als Messlatte, drei Zielgrößen, zwei
Märkte, Training 2021-24 und Bewertung im Holdout 2025-26.

Kurzfassung: **Ja, fünf davon sind besser — die Bänder liegen im unteren
Drittel.** Und dann kommt ein Ergebnis, mit dem ich nicht gerechnet habe: Die
bessere Risikomessung **senkt die Pass-Rate**.

---

## Die Rangliste — BTC, Holdout 2025-26

Rangkorrelation (Spearman) mit der Zukunft. Eichungsfrei, misst also genau
das, was man praktisch braucht: *„ist es gerade wilder als sonst?"*

| Prädiktor | Vol 5 T | größter Rückgang | **Tag ≤ −3 %** |
|---|---|---|---|
| **DVOL (implizite Vol)** | **0,348** | 0,110 | **0,210** |
| **Abwärts-Semivol 20 T** | **0,323** | **0,190** | **0,166** |
| EWMA (λ = 0,94) | 0,322 | 0,112 | 0,155 |
| ATR(14) / Preis | 0,281 | 0,144 | 0,143 |
| realisierte Vol 20 T | 0,276 | 0,128 | 0,129 |
| größter Rückgang 10 T | 0,267 | 0,126 | 0,110 |
| Parkinson (Hoch-Tief) | 0,229 | 0,112 | 0,107 |
| realisierte Vol 5 T | 0,221 | 0,160 | 0,110 |
| **Bollinger-Breite (20,2)** | **0,210** | 0,143 | **0,078** |
| Garman-Klass (OHLC) | 0,209 | 0,106 | 0,095 |
| Spanne H/T gestern | 0,205 | 0,160 | 0,147 |
| Rogers-Satchell | 0,200 | 0,109 | 0,089 |
| \|Rendite\| gestern | 0,134 | 0,115 | 0,128 |
| Volumen / Ø20 | 0,063 | 0,114 | 0,122 |

**Die Bänder stehen auf Platz 9 von 14.** Bei der Spalte, die für dein Konto
zählt — *Tag mit −3 % oder schlechter*, also das Kraken-Tageslimit — liegen
sie bei 0,078 gegen 0,210 für DVOL. **Faktor 2,7.**

### Die zwei, die vorne stehen

**1. DVOL — die implizite Volatilität von Deribit.** Das ist der Preis, den
der Optionsmarkt gerade für Absicherung verlangt. Die einzige Größe in der
Liste, die **nicht aus der Vergangenheit** kommt: Sie enthält, was andere
Marktteilnehmer über die Zukunft denken, inklusive bekannter Termine.

Kostenlos abrufbar, tägliche Werte:
`https://www.deribit.com/api/v2/public/get_volatility_index_data?currency=BTC`

**2. Abwärts-Semivol.** Dieselbe Standardabweichung wie immer, aber **nur über
die negativen Tage**. Ein Aufwärtsschub und ein Absturz sind für die
Bollinger-Breite dasselbe — für dein Konto nicht. Beim größten Rückgang ist
sie mit **0,190** der beste Wert überhaupt.

```
semivol = std(rendite[rendite < 0], 20 Tage) * sqrt(365)
```

Eine Zeile Code, keine externe Datenquelle, und sie schlägt die Bänder in
allen drei Spalten.

---

## 🛑 Zwei Einschränkungen, bevor das nach viel klingt

**Erstens: auf ETH ist alles deutlich schwächer.**

| Prädiktor | BTC Holdout | **ETH Holdout** |
|---|---|---|
| DVOL | 0,348 | **0,132** |
| Abwärts-Semivol | 0,323 | **0,127** |
| Bollinger-Breite | 0,210 | **0,078** |
| realisierte Vol 20 T | 0,276 | **0,043** |

Die Reihenfolge bleibt grob, aber alle Werte fallen um zwei Drittel. Was auf
BTC gilt, gilt nicht automatisch anderswo.

**Zweitens: das Niveau lässt sich gar nicht vorhersagen, nur der Rang.**

Regression mit Koeffizienten aus 2021-24, angewendet auf 2025-26:

| Prädiktor | R² im Holdout |
|---|---|
| DVOL + HAR | +0,103 |
| EWMA | +0,043 |
| ATR | −0,003 |
| realisierte Vol 20 T | −0,033 |
| **Bollinger-Breite** | **−0,134** |

**Fast alles negativ** — schlechter, als einfach den Mittelwert zu raten. Der
Grund: BTC-Vol fiel von 51,8 % auf 39,0 %, die alte Eichung sagt systematisch
zu hohe Werte voraus. (Auf ETH blieb das Niveau fast gleich, 65,4 → 63,0 % —
dort ist die Rangaussage einfach schwach.)

> **Praktische Folge: keine festen Vol-Schwellen einbauen.** „Über 60 % Vol
> halbiere ich" ist in zwei Jahren falsch geeicht. Nur relativ arbeiten —
> Quantil der letzten 6–12 Monate.

---

## Und jetzt das Ergebnis, mit dem ich nicht gerechnet habe

Die naheliegende Anwendung: Position klein machen, wenn die Vol hoch ist. Bei
**gleichem durchschnittlichem Einsatz** (0,35×), BTC long-only, echte
Kraken-Regeln:

| Steuergröße | Pass-Rate | gegen feste Größe | max. Drawdown |
|---|---|---|---|
| **feste Größe 0,35×** | **41,4 %** | — | −36,6 % |
| EWMA (λ 0,94) | 32,3 % | **−9,1 Pp** | −31,4 % |
| ATR(14) | 32,3 % | −9,1 Pp | −32,3 % |
| DVOL | 32,2 % | −9,2 Pp | −31,0 % |
| Abwärts-Semivol | 31,2 % | −10,2 Pp | −32,1 % |
| realisierte Vol 20 T | 30,5 % | −10,9 Pp | −31,5 % |
| Bollinger-Breite | 26,1 % | **−15,4 Pp** | −29,5 % |

**Jede Vol-Steuerung senkt die Pass-Rate — um 9 bis 15 Punkte.** Und zwar
obwohl sie den Drawdown wie beabsichtigt senkt (−36,6 % → −29,5 bis −32,3 %).

### Warum

Das Kraken-Regelwerk hat ein **Ziel**, nicht nur eine Grenze. Du musst +10 %
erreichen. Vol-Steuerung macht die Position genau dann klein, wenn große
Bewegungen möglich sind — und groß in ruhigen Phasen, in denen du die +10 %
nie erreichst, aber trotzdem Gebühren zahlst und langsam blutest.

> **Volatilität ist unter diesem Regelwerk keine reine Gefahr. Sie ist auch
> der einzige Weg zum Ziel.** Wer sie wegdämpft, überlebt länger und besteht
> seltener.

Die Rangfolge bleibt trotzdem intakt: Die schlechteste Risikomessung
(Bollinger, −15,4 Pp) richtet den größten Schaden an, die besten (EWMA, DVOL)
den kleinsten. Bessere Messung heißt hier **weniger Schaden**, nicht Gewinn.

---

## Die Antwort auf deine Frage

**Ja, es gibt Besseres als die Bänder — fünf Dinge:**

| statt Bollinger-Breite | Gewinn | Aufwand |
|---|---|---|
| **Abwärts-Semivol 20 T** | +0,113 auf Vol, +0,088 auf Tageslimit | eine Zeile |
| **DVOL / implizite Vol** | +0,138 auf Vol, +0,132 auf Tageslimit | ein API-Aufruf |
| EWMA (λ 0,94) | +0,112 / +0,077 | eine Zeile |
| ATR(14) | +0,071 / +0,065 | im Chart vorhanden |
| realisierte Vol 20 T | +0,066 / +0,051 | eine Zeile |

**Wenn du eine einzige austauschen willst: die Bollinger-Breite gegen die
Abwärts-Semivol.** Sie misst dasselbe, aber nur die Seite, die dein Konto
umbringt — und sie braucht keine externe Datenquelle.

**Wenn du eine hinzunehmen willst: DVOL.** Sie ist die einzige Größe hier, die
nicht aus dem Chart kommt, und deshalb die einzige, die überhaupt Neues
beitragen kann.

**Aber benutze sie nicht zur Positionssteuerung** — dafür ist oben der
Gegenbeweis. Benutze sie, um zu wissen, **wann du der laufenden Position nicht
trauen solltest** und wann ein Trade fair aussieht. Die Größe selbst bleibt
konstant und klein; das ist die einzige Stellschraube, die gemessen
funktioniert.

---

*Skripte: `research/risk.py` (14 Prädiktoren, drei Zielgrößen,
Out-of-Sample-R²), `research/risk2.py` (Rangkorrelationen, Niveau gegen Rang),
`research/risk3.py` (Vol-Steuerung gegen feste Größe unter Kraken-Regeln).*
