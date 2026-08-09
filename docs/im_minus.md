# „Ich bin im Minus — heißt das was?" — gemessen

Ausgelöst durch einen Live-Screenshot: Der Indikator meldet **LONG @ 64.842,25**
(7 Berührungen), der Kurs steht bei **64.446,81** — also 0,61 % im Rückstand.
Der Nutzer hatte an derselben Stelle **verkauft** und lag vorne.

Zwei Fragen dazu, beide messbar.

---

## 1. Ist ein früher Rückstand normal?

213 Trades der vereinfachten Regel (BTC 1h, ≥6 Berührungen, eine Position, 48 h):

| nach | Anteil im Minus |
|---|---|
| 1 h | 47,4 % |
| 3 h | 51,6 % |
| **6 h** | **50,2 %** |
| 12 h | 45,1 % |
| 24 h | 43,7 % |
| 48 h (Ende) | 41,8 % |

**Etwa jeder zweite Trade steht zwischendurch im Minus.** Das ist kein
Warnsignal, das ist der Normalzustand einer Strategie mit 55,9 % Trefferquote.

---

## 2. Sagt der frühe Rückstand das Endergebnis voraus?

Auf den ersten Blick sieht es stark aus:

| nach | im Minus | davon am Ende positiv | Ø Endergebnis |
|---|---|---|---|
| 6 h | 50 % | **45,8 %** | **−29,1 bp** |
| 24 h | 44 % | **29,0 %** | **−142,5 bp** |

Gegen 58,2 % positiv und +83,1 bp über alle Trades. Die Korrelation zwischen
6-Stunden-Stand und Endergebnis liegt bei **+0,454**.

### Aber das ist zum größten Teil Arithmetik, nicht Information

**Die 48-Stunden-Rendite enthält die 6-Stunden-Rendite bereits.** Selbst bei
einem reinen Zufallspfad wäre die Korrelation √(6/48) = **+0,354**.

Entscheidend ist der **Vorwärts-Teil** — was von Stunde 6 bis Stunde 48
passiert:

| nach | Korrelation gesamt | mechanisch | **vorwärts** | Ø vorwärts wenn im Minus | p |
|---|---|---|---|---|---|
| 6 h | +0,454 | +0,354 | **+0,145** | **+44,1 bp** | 0,346 |
| 12 h | +0,530 | +0,500 | **+0,107** | +23,3 bp | 0,281 |
| 24 h | +0,753 | +0,707 | **+0,171** | +6,0 bp | 0,357 |

**Kein p-Wert unter 0,28.** Und die Zahl, auf die es ankommt: Wer nach
6 Stunden im Minus liegt, verdient von dort an im Schnitt trotzdem
**+44,1 bp**.

> **Ein Rückstand nach ein paar Stunden ist keine Information über den
> Ausgang. Er ist die erste Hälfte des Weges.**

---

## 3. Und was bringt es, das Signal umzudrehen?

| Variante | Ø je Trade | Trefferquote | p |
|---|---|---|---|
| **Signal folgen** | **+67,1 bp** | 55,9 % | 0,016 |
| **Signal umdrehen** | **−99,1 bp** | 37,6 % | <0,001 |

**Differenz: 166 bp je Trade.** Über 213 Trades in 5,4 Jahren sind das
**354 Prozentpunkte Gesamtrendite.**

Der Grund, warum Umdrehen schlechter ist als der Edge groß: Du verlierst
+67 bp **und** zahlst dieselben Gebühren nochmal. Die Kosten wechseln nicht
die Seite.

---

## Die ehrliche Einordnung

Ein einzelner Gegentrade, der aufgeht, ist **keine Widerlegung** — er ist
das, was in 44,1 % der Fälle passiert. Bei 55,9 % Trefferquote hat man alle
paar Trades recht, wenn man das Gegenteil macht.

Der Punkt ist nicht, dass die Gegenposition falsch war. Der Punkt ist, dass
**ein Ergebnis nichts über die Regel aussagt, die es erzeugt hat.** Genau
dieser Schluss — „ich hatte recht, also war meine Einschätzung besser als das
System" — ist der Mechanismus, aus dem 2024 entstanden ist
([`ziel.md`](ziel.md)).

**Der Trade im Screenshot war zum Zeitpunkt des Bildes außerdem noch gar nicht
beendet** („Noch offen", Regel: nach 48 h raus). Bewertet wird bei Stunde 48,
nicht bei Stunde 6.

---

*Skript: `research/gegenteil.py` (Rückstand, Vorwärts-Zerlegung, Signalumkehr).*
