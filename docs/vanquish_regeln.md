# 🛑 Die echten Vanquish-Regeln — der Plan ist tot

Das Regelwerk-PDF beantwortet alle offenen Fragen aus
[`regelfragen.md`](regelfragen.md). Drei der Antworten beenden das Vorhaben,
jede einzelne davon für sich.

**Wörtlich aus dem Dokument:**

> **„SPX, XSP and VIX can only be traded long as single-leg calls/puts.
> No spreads, no selling to open."**
>
> **„Drawdown Type: Intraday Trailing"**
>
> **„No overnight positions. All trades must be closed by 3:59pm EST or they
> will be auto liquidated as a market order."**

Beide Kontotypen — Evaluierung und gefundetes Konto — tragen **identische**
Beschränkungen.

| Parameter | Evaluierung | Funded |
|---|---|---|
| Gewinnziel | 10 % | keins |
| Mindest-Trades | 10 | unbegrenzt |
| Konsistenz | 30 % | 30 % |
| Verlustlimit | 5 % | 5 % |
| **Drawdown-Typ** | **Intraday Trailing** | **Intraday Trailing** |
| Auszahlungen | — | täglich |
| Reset | 250 $ | — |
| Konten bis | 150.000 $ | 150.000 $ |

---

## Was das der Reihe nach zerstört

### 1. „No selling to open" — der Edge ist strukturell unerreichbar

Der einzige Befund dieses Projekts, der **zwei unabhängige Anlageklassen**
überstanden hat, ist die Volatilitäts-Risikoprämie: implizite Vol übersteigt
die danach realisierte um **+4,65 pp im Median, in 83,4 % der Fälle, t = 4,67**
([`andere_maerkte.md`](andere_maerkte.md)).

**Diese Prämie kassiert nur, wer Optionen verkauft.** Wer sie kauft, bezahlt
sie.

Vanquish erlaubt auf SPX, XSP und VIX **ausschließlich das Kaufen**. Damit ist
dort nicht bloß „die Strategie nicht umsetzbar" — **es ist nur die
Verliererseite genau des Effekts erlaubt, den ich gemessen habe.** Der
Short-Straddle lieferte +8,6 % p.a.; die Gegenposition liefert
spiegelbildlich etwa −8,6 % minus Gebühren.

### 2. „No spreads" — kein Iron Condor

Die gesamte Rechnung aus [`condor.md`](condor.md) und
[`validierung.md`](validierung.md) — vier Legs, definiertes Risiko,
Sharpe 2,38 — beschreibt eine Position, die das System **nicht ausführt.**

Damit fällt auch die Grundlage weg, auf der ich „komplexe Multi-Leg-Strategien"
für plausibel gehalten habe. Der Begriff steht **einmal** im PDF, und zwar im
Werbetext („the first prop firm to offer both options & advanced options
strategies"). In den Regeln steht das Gegenteil. **Die Wörter „credit",
„condor", „strangle", „straddle", „multi" und „static" kommen im gesamten
Dokument kein einziges Mal vor.**

### 3. „Intraday Trailing" — und zwar die härteste Variante

Deine erste Recherche sagte, das Live-Konto wechsle auf einen **statischen**
Drawdown. **Das PDF sagt das Gegenteil, für beide Kontotypen.** Gemessen
([`regelfragen.md`](regelfragen.md)):

| Nominal | statisch überlebt / p.a. | **trailing überlebt / p.a.** |
|---|---|---|
| 4× | 95,1 % / +19,9 % | 77,2 % / +16,2 % |
| 6× | 86,1 % / +29,5 % | **15,9 % / −1,0 %** |
| 8× | 81,4 % / +39,9 % | **13,1 % / −0,6 %** |

Und **Intraday** Trailing ist noch schärfer als das EOD-Trailing, das ich
gerechnet habe: Der Boden zieht mit jedem *unrealisierten* Zwischenhoch mit.

### 4. „No overnight positions" — auch die Zeitstruktur ist weg

Alles muss um 15:59 EST geschlossen sein, sonst Zwangsliquidation zur Market
Order. Damit sind **Wochen- und Monatszyklen unmöglich** — die Lösung für die
Konsistenzregel aus [`regelfragen.md`](regelfragen.md) fällt ebenfalls weg.

Was bleibt, ist **0DTE-Intraday-Handel mit gekauften Einzeloptionen** — die
Struktur mit dem schnellsten Theta-Verfall, die es gibt, auf der falschen
Seite der einzigen gemessenen Prämie.

---

## Was ich daraus lerne — und wo ich zu leichtgläubig war

Ich habe in [`anbieter.md`](anbieter.md) geschrieben:

> *„Vanquish (funded), statisch — einziger, der die Strategie traden kann und
> die richtige Mechanik hat."*

**Beide Hälften dieses Satzes sind falsch.** Ich habe sie auf zwei
Recherchezusammenfassungen gestützt und beim Schreiben zwar markiert („nach
Angaben des Nutzers, nicht unabhängig verifiziert"), aber trotzdem **fünf
Dokumente lang darauf aufgebaut**, statt die Quelle zuerst zu beschaffen.

Der Fehler ist nicht, dass die Recherche falsch war. Der Fehler ist, dass ich
auf einer unverifizierten Angabe eine Rechnung nach der anderen aufgetürmt
habe, obwohl das Primärdokument ein PDF-Download entfernt war.

**Es ist dieselbe Falle wie am Anfang des Projekts** — dort war es die
angenommene 90-Tage-Frist bei Kraken, die es nie gab
([`no_time_limit.md`](no_time_limit.md)). Beide Male habe ich eine Regel
modelliert, statt sie nachzulesen.

---

## Was jetzt noch steht

| Weg | Status |
|---|---|
| **Vanquish** | **tot** — nur Long-Einzeloptionen, Intraday-Trailing, kein Overnight |
| MFF / TradeDay / Apex (Futures) | Trendfolge seit 2017 bei **Sharpe −0,17** — keine tragfähige Futures-Strategie gefunden |
| **Kraken** (bereits bezahlt) | **S/R-Ausbruch, BTC 1h, ≥6 Berührungen, 0,35×, eine Position, 48 h.** ~53,8 % je Versuch ([`einfach.md`](einfach.md)) |
| **Eigenes Kapital** | **Der VRP-Edge ist real und dort handelbar.** S&P-Straddle Sharpe 1,52, Drawdown −13,7 % ([`eigenkapital.md`](eigenkapital.md)) |

**Die unbequeme Schlussfolgerung:** Der einzige Edge, den dieses Projekt
gefunden und zweimal unabhängig bestätigt hat, verlangt, dass man **Optionen
verkauft**. Genau das erlaubt kein Prop-Konto — weil es das Risiko ist, das
Prop-Firmen nicht tragen wollen.

Das ist kein Zufall und keine Lücke im Angebot. **Prop-Firmen verkaufen
Zugang zu Hebel, nicht Zugang zu Risikoprämien.** Wer eine Versicherungsprämie
kassieren will, muss das Kapital selbst stellen — sonst trägt jemand anderes
das Tail-Risiko.

---

## Was ich dir konkret raten würde

**1. Vanquish nicht kaufen.** Nicht wegen des Preises, sondern weil die
Regeln die einzige funktionierende Strategie ausschließen und stattdessen
ihre Umkehrung erzwingen.

**2. Den bereits bezahlten Kraken-Versuch spielen.** Die Regel steht,
sie ist gemessen, und sie kostet dich nichts mehr:
BTC 1h, Level mit ≥6 Berührungen, eine Position, 48 h halten, 3.500 $ Nominal.

**3. Falls du weiter Prop-Konten suchst:** Die Frage ist nicht mehr „kein
Tageslimit", sondern **„darf ich Optionen verkaufen und über Nacht halten?"**
Das ist ein sehr viel engeres Kriterium — und meine Vermutung nach diesem PDF
ist, dass die Antwort fast überall nein lautet. Prüf das an der
**Regel-PDF**, nicht an der Werbeseite.

**4. Der ehrliche langfristige Weg** ist eigenes Kapital bei einem normalen
Broker. Dort sind 20–27 % p.a. bei Sharpe 1,5 messbar erreichbar — nur
eben mit deinem Geld und deinem Tail-Risiko.

---

*Quelle: Regelwerk-PDF von Vanquish, 39 Seiten, vom Nutzer bereitgestellt.
Textextraktion mit `research/pdfx.py` (reines Python, da die
PDF-Bibliotheken der Umgebung defekt sind).*
