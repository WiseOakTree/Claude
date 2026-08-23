# Gamma Exposure (GEX) — die vier Behauptungen geprüft

Spezifikation vor der Rechnung: [`gex_spec.md`](gex_spec.md).
Binance Options EOHSummary, stündlich, **2023-05-18 bis 2023-10-23**,
147 Tage / 3.493 Stunden, BTC und ETH. Gamma kommt von der Börse.

---

> ## Der Befund in einem Satz
>
> **Alle vier Behauptungen: nicht bestätigt** — bei einer Datenlage, die stark
> genug für ein „nein, nicht so wie behauptet" ist und zu schwach für ein
> endgültiges Urteil.
>
> Der auffälligste Einzelbefund geht in die **falsche Richtung**: Die Volatilität
> hängt am **Betrag** des GEX, nicht an seinem **Vorzeichen** — und der Betrag
> korreliert mit **ρ = 0,83** schlicht mit dem Open Interest.

---

## Warum die Datenlage das Urteil begrenzt

Deribits öffentliche API liefert nur den **aktuellen** Buchstand, keine
Historie je Strike. Frei verfügbar ist einzig Binances stündliche
Options-Zusammenfassung — und die deckt nur **147 Tage in 2023** ab, auf dem
kleineren der beiden Bücher.

| | BTC | ETH |
|---|---|---|
| Stunden | 3.468 | 3.468 |
| Tagesbeobachtungen (nicht überlappend) | 144 | 144 |
| Net GEX **negativ** | 32,1 % der Stunden | 55,0 % |
| Median abs. GEX | 25,7 M$ | 3,0 M$ |
| Ø Strikes je Stunde | 61 | 37 |

Beide Regime kommen ausreichend oft vor — das ist die Voraussetzung, damit die
Prüfung überhaupt möglich ist.

**Getestet wird ausschließlich auf Tagesdaten (n = 144).** Stündliche Werte mit
24-h-Zukunftsfenster überlappen 24-fach; ihre p-Werte sind wertlos. Genau diese
Falle hat dieses Projekt schon einmal getroffen ([`zu_streng.md`](zu_streng.md)).

---

## B1 — „Negatives Gamma verstärkt die Volatilität"

Erwartet: ρ < 0 zwischen Net GEX und der realisierten Vol der nächsten 24 h.

| Markt | Stichprobe | Spearman ρ | p | n |
|---|---|---|---|---|
| BTC | stündlich *(nur beschreibend)* | **+0,094** | 0,0000 | 3.468 |
| BTC | **Tagesdaten** | **+0,081** | 0,334 | 144 |
| BTC | 1. Hälfte / 2. Hälfte | +0,029 / +0,119 | 0,81 / 0,32 | 72 / 72 |
| ETH | stündlich *(nur beschreibend)* | **+0,144** | 0,0000 | 3.468 |
| ETH | **Tagesdaten** | **+0,133** | 0,112 | 144 |
| ETH | 1. Hälfte / 2. Hälfte | +0,066 / +0,045 | 0,58 / 0,71 | 72 / 72 |

**Das Vorzeichen ist durchgehend positiv — das Gegenteil der Behauptung.**
Signifikant ist nichts davon auf Tagesdaten.

Der Vergleich der Gruppen zeigt, warum ein Blick auf nur einen Markt in die Irre
führt:

| | Vol nach negativem GEX | Vol nach positivem GEX | Mann-Whitney p |
|---|---|---|---|
| BTC | **35,5 %** | 27,5 % | 0,140 |
| ETH | 29,6 % | **33,1 %** | 0,956 |

BTC zeigt die erwartete Richtung (nicht signifikant), ETH die umgekehrte.
Wer nur BTC anschaut, hält die These für bestätigt.

### Was stattdessen mit der Volatilität zusammenhängt

Die Vol nach GEX-Quintil (Tagesdaten, %) ist **U-förmig**:

| Quintil | 1 (niedrigstes GEX) | 2 | 3 | 4 | 5 (höchstes GEX) |
|---|---|---|---|---|---|
| BTC | 35,0 | 29,5 | 24,3 | 24,9 | **35,7** |
| ETH | 32,9 | 25,5 | 30,0 | 34,5 | 34,0 |

Hohe Vol an **beiden** Enden, ruhige Mitte. Es ist der **Betrag**, nicht das
Vorzeichen: |GEX| gegen Folge-Vol auf BTC ρ = **+0,192** (p = 0,021) — der
stärkste Zusammenhang der ganzen Untersuchung, und er sagt das Gegenteil des
Indikators (extremes Gamma in *beide* Richtungen = mehr Bewegung).

Und selbst der ist wahrscheinlich kein Gamma-Effekt:

> **corr(abs. GEX, Open Interest) = +0,83 (BTC), +0,84 (ETH).**

Abs. GEX ist im Wesentlichen ein Open-Interest-Maß. Viel offenes Interesse
bedeutet aktiven Markt bedeutet Bewegung — dafür braucht es keine
Dealer-Hedging-Theorie.

**Urteil B1: nicht bestätigt** (Vorzeichen falsch, nicht signifikant,
Märkte widersprechen sich).

---

## B2 — „Positives Gamma bringt Mean-Reversion, negatives Trend"

Erwartet: corr(Rendite der letzten 24 h, Rendite der nächsten 24 h) < 0 bei
positivem Gamma, > 0 bei negativem.

| Markt | Regime | ρ | p | n |
|---|---|---|---|---|
| BTC | positives Gamma | −0,068 ✅ | 0,502 | 99 |
| BTC | negatives Gamma | +0,002 ✅ | 0,989 | 44 |
| ETH | positives Gamma | **+0,049** ❌ | 0,676 | 75 |
| ETH | negatives Gamma | **−0,018** ❌ | 0,887 | 68 |

BTC hat die richtigen Vorzeichen, ETH beide falschen — und alle vier Werte
liegen praktisch auf null. Das ist kein schwacher Effekt, das ist keiner.

**Urteil B2: nicht bestätigt.**

---

## B3 — „Call-Wall und Put-Wall wirken als Widerstand und Unterstützung"

Die entscheidende Frage ist nicht, ob der Kurs an der Wall umkehrt — er kehrt
überall irgendwann um. Die Frage ist, ob er dort **öfter** umkehrt als an einem
beliebigen anderen Strike gleicher Entfernung. Genau diese Kontrolle hat in
diesem Projekt schon die Order Blocks erledigt ([`altdata_test.md`](altdata_test.md)).

| Markt | Level | Berührungen | Umkehr | Zufallsstrike | Differenz | p |
|---|---|---|---|---|---|---|
| BTC | Call-Wall | 803 | 59,4 % | 65,7 % | **−6,3 pp** | 0,249 |
| BTC | Put-Wall | 646 | 57,6 % | 68,0 % | **−10,4 pp** | 0,107 |
| ETH | Call-Wall | 637 | 44,1 % | 83,8 % | **−39,7 pp** | 0,000 |
| ETH | Put-Wall | 1.061 | 55,8 % | 44,2 % | +11,6 pp | 0,030 |

**In drei von vier Fällen kehrt der Kurs an der Wall seltener um als an einem
zufälligen Strike derselben Entfernung.** Der einzige positive Fall (ETH
Put-Wall) verfehlt die Bonferroni-Schwelle von 0,0125.

*Einschränkung zu diesem Test:* „Umkehr" ist grob definiert (Kurs 24 h nach der
Berührung wieder auf der Ausgangsseite), und der Kontrollstrike ist nur auf
±50 % der Distanz gematcht. Die −39,7 pp bei ETH sind daher eher ein Zeichen
für ein unsauberes Matching als für einen echten Gegen-Effekt. Belastbar ist
nur die Aussage: **kein Vorteil der Wall gegenüber der Kontrolle.**

**Urteil B3: nicht bestätigt.**

---

## B4 — „Der Gamma-Flip trennt die Regime"

Geprüft am Wechsel des GEX-Vorzeichens (die Linie, die der Flip geometrisch
markiert):

| Markt | Ereignis | n | Vol davor | Vol danach | p |
|---|---|---|---|---|---|
| BTC | Flip nach NEGATIV | 16 | 21,8 % | **38,7 %** | 0,144 |
| BTC | Flip nach POSITIV | 16 | 40,7 % | **22,4 %** | **0,008** |
| ETH | Flip nach NEGATIV | 13 | 41,3 % | 29,6 % ❌ | 0,305 |
| ETH | Flip nach POSITIV | 14 | 35,1 % | 31,5 % | 0,463 |

BTC verhält sich lehrbuchmäßig, ETH beim Wechsel ins negative Gamma genau
umgekehrt.

### Die Kontrolle, die man hier braucht

Volatilität kehrt zum Mittel zurück. Nach einem Tag mit 40,7 % Vol fällt sie
meistens — ganz ohne Gamma. Also: dieselben Ereignisse gegen Tage mit
**gleichem Vol-Niveau, aber ohne Flip**:

| | n | Vol davor | nach Flip | Kontrolle | Differenz | p |
|---|---|---|---|---|---|---|
| BTC | 16 | 40,7 % | **−18,4 pp** | +1,3 pp | **−19,7 pp** | **0,011** |
| ETH | 13 | 34,4 % | −1,8 pp | −1,6 pp | **−0,2 pp** | 0,508 |

**Auf BTC überlebt der Effekt die Kontrolle** — 19,7 Prozentpunkte mehr
Vol-Rückgang, als die Mittelwertrückkehr erklärt, p = 0,011. **Auf ETH ist er
exakt null.**

Bei n = 16 Ereignissen in einem Markt und n = 13 mit gegenteiligem Ergebnis im
anderen ist das kein Befund, sondern ein Hinweis. Das vorab festgelegte
Kriterium „beide Märkte" ist verfehlt.

**Urteil B4: nicht bestätigt** — mit der Anmerkung, dass dies der einzige der
vier Punkte ist, bei dem überhaupt etwas geflackert hat.

---

## Zusammenfassung

| | Behauptung | Urteil |
|---|---|---|
| B1 | Negatives Gamma verstärkt Vol | ❌ Vorzeichen **umgekehrt**, Märkte widersprüchlich |
| B2 | Positives Gamma → Mean-Reversion | ❌ Korrelationen ≈ 0, Vorzeichen widersprüchlich |
| B3 | Walls wirken als S/R | ❌ **schlechter** als ein Zufallsstrike gleicher Distanz |
| B4 | Flip trennt die Regime | ❌ nur BTC, n = 16, ETH gegenläufig |

---

## Was das praktisch heißt

1. **Der Indikator ist als Rechnung korrekt** — das Black-Scholes-Gamma, die
   Aggregation, Flip und Walls sind sauber implementiert. Geprüft wurde nicht
   der Code, sondern die **Deutung**.
2. **Was er anzeigt, ist im Wesentlichen Open Interest** (ρ = 0,83 zwischen
   abs. GEX und OI). Als Karte, *wo* das Open Interest liegt, ist er nützlich.
   Als Vorhersage, *was der Kurs tut*, in diesen Daten nicht.
3. **Als Größenregel statt als Signal** wäre er am ehesten vertretbar: extremes
   |GEX| ging mit mehr Bewegung einher (ρ = +0,19 auf BTC) — also eher kleiner
   handeln, wenn |GEX| extrem ist. Das ist die umgekehrte Verwendung zu der,
   die der Indikatortext nahelegt.
4. **Nicht als Einstiegssignal.** Kein Punkt hat die vorab festgelegten
   Kriterien erfüllt.

---

## Einschränkungen

* **147 Tage, ein Regime.** Der Zeitraum ist BTC-Seitwärtsmarkt 2023
  (26k–31k). Ob GEX in einem Crash trägt, sagen diese Daten nicht.
* **Binance, nicht Deribit.** Deribit hält den Großteil des Krypto-Options-OI.
  Der GEX aus dem kleineren Buch kann das echte Dealer-Gamma verfehlen.
  Der Indikator selbst zieht Deribit-Daten — geprüft wurde ein Stellvertreter.
* **Dealer-Annahme ungeprüft.** „Dealer long Calls, short Puts" ist ein Modell,
  keine Messung. Ist sie falsch, ist das Vorzeichen des Net GEX falsch — was
  die durchgehend umgekehrten Vorzeichen in B1 erklären *könnte*.
* **B3 ist grob.** Umkehrdefinition und Kontroll-Matching sind einfach gehalten.
* **Kein Holdout**, nur ein Hälften-Vergleich. So benannt, nicht schöngeredet.

**Was einen belastbaren Test ermöglichen würde:** eine Deribit-Historie je
Strike. Sie ist frei nicht zu bekommen — entweder kostenpflichtig (Amberdata,
Laevitas, Deribit-Institutional) oder man **sammelt sie ab jetzt selbst**: ein
täglicher Schnappschuss von `get_book_summary_by_currency` kostet nichts und
liefert in einem Jahr das, was hier fehlt.
