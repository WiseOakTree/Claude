# „Auf der Seite des Hauses stehen"

Deine Idee: nicht traden, sondern **das Kapital stellen, das die Gambler
hebeln** — und an den Gebühren verdienen statt an der Richtung.

**Das ist die beste Idee dieses gesamten Projekts, und sie ist messbar.**
Mit drei Einschränkungen, die genauso wichtig sind wie das Ergebnis.

---

## Der HLP-Vault: das Haus auf Hyperliquid, on-chain nachprüfbar

Der *Hyperliquidity Provider* stellt Liquidität, **führt die Liquidationen
aus** und kassiert Plattformgebühren. Wer einzahlt, ist buchstäblich die
Gegenseite aller Trader. Aktuell **214,4 Mio $**.

| | |
|---|---|
| Zeitraum | 2023-06 bis 2026-08 (3,17 Jahre) |
| kumulierte PnL | **136,9 Mio $** |
| **Rendite kumuliert** | **+172,8 %** |
| **annualisiert** | **+37,3 %** |
| Volatilität p.a. | 14,3 % |
| **Sharpe** | **2,12** |
| größter Rückgang (14-Tage-Raster) | −5,8 % |
| Perioden im Plus | **86,7 %** (78 von 90) |
| schlechteste Periode | −4,42 % |

**Sharpe 2,12** — höher als alles, was dieses Projekt je gemessen hat. Der
S/R-Ausbruch lag bei 0,36, die Volatilitätsprämie bei 1,85.

---

## 🛑 Aber: der Ertrag bricht weg, und zwar schnell

| Jahr | Rendite | schlechteste Periode |
|---|---|---|
| 2023 | **+19,6 %** | −4,42 % |
| 2024 | **+79,1 %** | +0,03 % |
| 2025 | **+19,0 %** | −0,80 % |
| 2026 *(bis August)* | **+7,1 %** | −0,51 % |

**Von 79 % auf hochgerechnet rund 11 %.** Das ist kein Zufall, sondern
Mechanik:

> **Der Ertrag des Hauses hängt am Volumen der Gambler, nicht an deinem
> Kapital.** Kommt mehr Kapital in den Vault, wird derselbe Gebührentopf durch
> mehr Anteile geteilt.

Der Vault ist von wenigen Millionen auf 214 Mio $ gewachsen. Genau das frisst
die Rendite. **Was du misst, wenn du heute einsteigst, ist nicht das, was du
bekommst.**

---

## Der zweite Weg: Funding-Carry

Spot kaufen, Perpetual shorten, die Finanzierungsrate kassieren.
Richtungsneutral — dir ist egal, wohin BTC läuft.

| | |
|---|---|
| mittlere Rate je 8 h | 0,00644 % |
| **annualisiert** | **+7,05 %** |
| nach Kosten (4 Seiten à 5 bp) | **+6,85 %** |
| Anteil positiver Zahlungen | **84,4 %** |
| Volatilität p.a. | **0,48 %** |
| Sharpe | 14,57 |

| Jahr | Ertrag | positiv | schlechtester Monat |
|---|---|---|---|
| 2024 | **+11,96 %** | 91,6 % | +0,12 % |
| 2025 | +5,13 % | 87,1 % | +0,18 % |
| 2026 *(bis Juli)* | **+1,12 %** | 67,3 % | −0,18 % |

**Auch hier derselbe Verfall:** 12 % → 5 % → unter 2 %. Und aus demselben
Grund — die Carry ist ein bekannter Trade, und je mehr Kapital sie erntet,
desto dünner wird sie.

Der Sharpe von 14,57 ist irreführend: Er misst die Ruhe der Erträge, nicht das
Risiko der Konstruktion. Das echte Risiko sitzt in der Short-Seite
(Liquidation bei starkem Anstieg) und beim Börsenausfall — beides zeigt sich
nicht in der Volatilität der Funding-Zahlungen.

---

## Der Vergleich aller Wege dieses Projekts

| Weg | Rendite p.a. | Vol | Sharpe | max DD | eigentliches Risiko |
|---|---|---|---|---|---|
| **HLP-Vault (das Haus)** | **+37,3 %** | 14,3 % | **2,12** | −5,8 % | Vault-Ausfall, Smart Contract, Börse |
| Volatilitätsprämie | +25,2 % | 13,6 % | 1,85 | −13,7 % | Vol-Schub, tägliche Arbeit |
| Funding-Carry | +6,8 % | 0,5 % | 14,57 | −0,2 % | Liquidation, Börsenausfall |
| Marktmachen ohne Rebate | **−2,1 %** | — | — | — | garantiertes Minus |
| S/R-Ausbruch | *im Vorwärtstest gescheitert* | | | | |

---

## 🛑 Drei Einschränkungen, ohne die die Zahlen lügen

**1. Überlebensauswahl.** HLP ist **ein** Vault auf **einer** Börse, die
funktioniert hat. Andere Perp-Börsen hatten Liquiditätspools, die deutlich
schlechter liefen oder verschwanden. Ich habe hier den Gewinner gemessen —
genau der Fehler, vor dem dieses Projekt fünfzehnmal gewarnt hat. Die
Zahlen sagen, was **dieser** Vault erreicht hat, nicht was ein Vault erreicht.

**2. Das 14-Tage-Raster versteckt Rückgänge.** Die Historie liefert nur 90
Punkte über drei Jahre. Ein Einbruch innerhalb einer Zweiwochenperiode ist
unsichtbar. **Der wahre maximale Rückgang liegt über −5,8 %.**

**3. Es ist kein risikofreies Geschäft, sondern ein Versicherungsgeschäft.**
Der Vault nimmt die Gegenseite. In einer Bewegung, in der *alle* Trader
gleichzeitig recht haben — ein Absturz, in dem jeder short ist — verliert das
Haus. Die 86,7 % Gewinnperioden sind genau die Signatur, die auch ein
Versicherer hat: viele kleine Gewinne, seltene große Verluste. In den drei
Jahren ist dieser Fall nicht eingetreten. Das ist kein Beweis, dass er nicht
eintritt.

---

## Und die Zahl, die du genannt hast

Du hast gesagt: statt auf der 2-%-Seite auf der 98-%-Seite stehen.

**Die 98 % gibt es nicht.** Gemessen:

| | |
|---|---|
| Perioden im Plus beim HLP-Vault | **86,7 %** |
| positive Funding-Zahlungen | **84,4 %** |
| Hyperliquid-Konten allTime im Plus | 41,9 % |

Das Haus gewinnt in **rund 85 %** der Perioden, nicht in 98. Und der Rest ist
kein Rauschen, sondern genau der Teil, in dem das Geschäftsmodell auf die
Probe gestellt wird.

---

## Was ich an deiner Stelle daraus machen würde

**Die Richtung stimmt, und sie stimmt aus einem strukturellen Grund:** Der
Gebührenstrom existiert unabhängig davon, ob du recht hast. Das gilt für
keinen einzigen der 57 anderen Ansätze in diesem Projekt.

Praktisch:

| | |
|---|---|
| **Erwartung** | eher **10–15 % p.a.**, nicht 37 — der Ertrag ist im Verfall |
| **Einstieg** | klein, und über mehrere Wege verteilt, nicht in einen Vault |
| **Was du dafür brauchst** | Kapital. Genau das, was `der_weg.md` als Engpass benannt hat |
| **Was du dafür nicht brauchst** | eine Prognose, einen Indikator, eine Meinung |

Und die unbequeme Verbindung zum Anfang: **Dieser Weg braucht kein Können,
aber Kapital.** Er löst nicht das Problem, dass 10.000 € auch bei 15 % nur
1.500 € im Jahr bringen. Er löst nur das andere Problem — dass du bisher
nichts gefunden hast, worauf man überhaupt setzen kann.

---

*Skripte: `research/haus.py` und `research/haus2.py` (erste Versuche, wegen
Startkapital nahe null und Tagesraster fehlerhaft — als Beleg behalten),
`research/haus3.py` (native Frequenz, Vergleich). Daten: Hyperliquid
`vaultDetails` (on-chain), Funding-Historie aus dem Projektbestand.*
