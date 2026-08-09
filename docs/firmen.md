# „Wie machen das Firmen? Die müssen einen Edge haben"

Die Frage ist richtig gestellt — nur gibt es **zwei völlig verschiedene
Firmentypen**, und nur einer davon handelt überhaupt.

---

## A. Die Prop-Firma: kein Handels-Edge, sondern ein Produkt

Kraken Starter: 85 $ Gebühr, 10.000 $ Konto, 80 % Split.

> **Firmengewinn je verkaufter Challenge = Gebühr − P(besteht) × Auszahlung**

| P(besteht) | Auszahlung 500 $ | 2.000 $ | 4.000 $ |
|---|---|---|---|
| 5 % | +60 $ | −15 $ | −115 $ |
| 10 % | +35 $ | −115 $ | −315 $ |
| 20 % | −15 $ | −315 $ | −715 $ |
| **50 %** | −165 $ | **−915 $** | −1.915 $ |

**Die kritische Bestehensquote:**

| Ø Auszahlung je gefundetem Konto | kritische Quote |
|---|---|
| 500 $ | 17,0 % |
| **1.000 $** | **8,5 %** |
| **2.000 $** | **4,2 %** |
| 4.000 $ | 2,1 % |

Bei realistischen 1.000–2.000 $ Auszahlung liegt die Grenze bei **4–9 %**.
Alles darüber kostet die Firma Geld.

### Und damit erklärt sich das Regelwerk

Konsistenzregeln, Tageslimits, trailende Drawdowns, Mindesthandelstage — jede
einzelne dieser Regeln **senkt die Bestehensquote**. Gemessen:

| Regel | Wirkung auf die Quote |
|---|---|
| Trailing statt statisch (3 % DD, 3×) | **54,5 % → 0,0 %** |
| 3 % Tageslimit statt keins | 78,1 % → 40,2 % |
| Ziel 10 % statt 6 % | 49,3 % → 33,1 % |

> **Diese Regeln sind kein Risikomanagement für dich. Sie sind das Produkt.**

Deine Intuition — *„sonst würden die auch langfristig spekulieren"* — trifft
genau zu. Prop-Firmen spekulieren nicht, weil sie etwas Besseres gefunden
haben: **Sie verkaufen Lose und behalten den Einsatz der Verlierer.**

*(Einschränkung: Die Auszahlungshöhe ist meine Annahme, ich habe keine
Firmenbücher. Die Struktur der Rechnung ändert sich dadurch nicht, die
kritische Quote schon.)*

---

## B. Die Handelsfirma: fünf echte Edges — alle hier gemessen

| Edge | in diesem Projekt gemessen | Mechanik | Größe |
|---|---|---|---|
| **Market Making** | Orderflow-IC **−0,041**, p = 3·10⁻¹⁷³ | Wer Liquidität *nimmt*, zahlt. Wer sie *stellt*, kassiert. | 0,3–1,3 bp/Trade |
| **Volatilitätsprämie** | BTC t = 4,12 \| S&P t = 4,67 | Versicherung verkaufen, Kapital stellen | Sharpe 1,5–1,9 |
| **Orderbuch-Ungleichgewicht** | +0,87 bp über 110.786 Trades | nur bei Rebate-Kosten profitabel | +19 % p.a. als MM |
| **Diversifikation** | Korrelation **+0,001** über 20 Märkte | viele kleine statt ein großer Edge | Sharpe ×3,5 |
| **Kostenstruktur** | −331 % p.a. als Taker, +41 % als MM | derselbe Edge, andere Gebühren | Faktor 18 |

**Der wichtigste davon ist nicht der größte, sondern der erste:** Der
Orderflow-IC ist **negativ**. Das heißt, wer mit Market-Order kauft, verliert
systematisch — und zwar an den, der die Gegenseite stellt. Das ist keine
Prognose, das ist eine **Dienstleistungsgebühr**.

---

## Und jetzt die Zahl, die deine Frage wirklich beantwortet

| | je Trade | Trades/Jahr | brutto p.a. | **Sharpe** |
|---|---|---|---|---|
| **Dein S/R-Ausbruch** | +45,7 bp | 40 | **+18,3 %** | **0,36** |
| **Bot-Orderbuch (als MM)** | +0,87 bp | 2.190 | **+19,1 %** | **0,85** |

**Die Firma verdient pro Jahr nicht mehr als du.** Ihr Edge je Trade ist
**53× kleiner**. Er kommt nur 55× häufiger.

Der Unterschied ist der **Sharpe** — und der ist das, was man hebeln kann.

---

## Warum „viel Kapital" nicht die Ursache ist, sondern die Folge

Bei **gleichem Drawdown von 10 %**, simuliert über zehn Jahre:

| Sharpe | typ. max. Drawdown | tragbare Zielvol | **Rendite p.a.** |
|---|---|---|---|
| **0,36** (deins) | 2,46× Jahresvol | 4 % | **+1,5 %** |
| 0,85 | 1,80× | 6 % | +4,7 % |
| 1,50 | 1,35× | 7 % | +11,1 % |
| **3,00** | 0,85× | 12 % | **+35,2 %** |
| 5,00 | 0,59× | 17 % | +84,6 % |

**Bei identischem Risiko liefert Sharpe 3 das Zwanzigfache von Sharpe 0,36.**
Nicht weil der Edge größer ist — weil er ruhiger ist und man ihn deshalb
größer fahren darf.

Kapital ist nicht die Ursache des Edges. **Kapital ist das, was ein hoher
Sharpe erlaubt.**

---

## Wie viele Edges braucht eine Firma für Sharpe 3?

Bei unkorrelierten Strategien wächst der Sharpe mit **√N**. In diesem Projekt
gemessen: 20 Märkte → Faktor 3,5 statt theoretisch 4,47, also **78 %
Effizienz**.

| Ziel-Sharpe | nötige Anzahl (ideal) | mit 78 % Effizienz |
|---|---|---|
| 1,0 | 8 | 13 |
| 2,0 | 31 | 50 |
| **3,0** | **69** | **113** |
| 5,0 | 193 | 315 |

> **Keine Firma hat einen großartigen Edge. Sie haben siebzig mittelmäßige,
> die nicht miteinander korrelieren.**

Und jeder einzelne davon ist **kleiner** als der, den ich hier gefunden habe.

### Was das kostet

Aus diesem Projekt hochgerechnet:

| | |
|---|---|
| getestete Ansätze | ~40 |
| out-of-sample haltbar | **2** (VRP, S/R-Ausbruch) |
| Trefferquote | **~5 %** |
| **für 70 haltbare Edges** | **~1.400 Ansätze** |

Und zwar mit derselben Sorgfalt: Look-ahead-Kontrolle, Überlappungskorrektur,
Holdout, Bonferroni — sonst findet man 70 Scheinbefunde statt 70 Edges.

**Das ist kein Wissensvorsprung. Das ist eine Fabrik.** Genau dafür stellt
eine Handelsfirma zweihundert Forscher ein — nicht um *den* Edge zu finden,
sondern um Nummer 71 zu finden, während Nummer 12 gerade abstirbt.

---

## Die Antwort in vier Sätzen

1. **Prop-Firmen haben keinen Handels-Edge.** Ihr Geschäft ist die
   Durchfallquote; ab 4–9 % Bestehensquote verlieren sie Geld. Die Regeln
   sind das Produkt.
2. **Handelsfirmen haben echte Edges** — Market Making, Volatilitätsprämie,
   Orderbuch. Alle sind winzig (unter 1,5 bp je Trade) und alle verlangen
   eine Kostenstruktur, die Privatanleger nicht bekommen.
3. **Ihr Vorteil ist nicht die Größe des Edges, sondern der Sharpe.** Bei
   gleichem Risiko bringt Sharpe 3 das Zwanzigfache von Sharpe 0,36.
4. **Der Sharpe kommt aus der Anzahl, nicht aus der Qualität.** Siebzig
   mittelmäßige unkorrelierte Edges schlagen jeden einzelnen guten.

Und der Satz, der für dich zählt: **Du hast einen Edge gefunden, der größer
ist als jeder einzelne, den eine Handelsfirma benutzt.** Was dir fehlt, sind
die anderen neunundsechzig — und die Kostenstruktur, um sie zu ernten.

---

## Was an dieser Rechnung schwach ist

- **Die Auszahlungshöhe der Prop-Firmen ist geschätzt.** Ohne ihre Bücher ist
  die kritische Quote eine Größenordnung, keine Zahl.
- **Die Sharpe-Hebel-Simulation unterstellt Normalverteilung.** Echte
  Strategien haben fette Ränder; der sichere Hebel liegt real niedriger als
  in der Tabelle.
- **Die Hochrechnung auf 1.400 Ansätze** unterstellt, dass meine Trefferquote
  von 5 % verallgemeinerbar ist. Das ist eine Extrapolation aus einer
  einzelnen Untersuchung, kein gemessener Branchenwert.
- **Latenz-Arbitrage konnte ich nicht messen** — dafür fehlen Tickdaten. Sie
  ist strukturell dasselbe wie Market Making, nur schneller.

---

*Skripte: `research/firmen_edge.py` (Prop-Firmen-Ökonomie, gemessene Edges),
`research/firmen_edge2.py` (Sharpe gegen Hebel, Anzahl nötiger Edges).*
