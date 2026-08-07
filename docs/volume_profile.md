# Volume Profile getestet

„Das einzige was funktioniert ist Volume Profile." Testbare Aussage, und ich
habe sie so geprüft, dass sie gewinnen konnte: **gegen meine eigene validierte
Regel, Kopf an Kopf, gleiche Mechanik, gleicher Zeitraum.**

Ergebnis: **Als Level verliert sie deutlich. Eine Teilbehauptung hält —
aber es ist nicht die, um die es dir geht.**

---

## Aufbau

Profil aus 1h-Bars, Volumen jedes Bars gleichmäßig über seine Spanne
[Tief, Hoch] verteilt — **dasselbe Verfahren, das TradingView ohne Tickdaten
benutzt**. Rollierendes Fenster von 720 Bars (30 Tage), 100 Körbe, alle 24 Bars
neu gerechnet. Value Area = 70 % des Volumens um den POC.

Suchzeitraum 2021-03 bis 2024-12, **Holdout 2025-01 bis 2026-06**, BTC/ETH/SOL.

> **Einschränkung vorweg:** Mit echten Tickdaten (Footprint) sieht das Profil
> feiner aus. Ob das die Ergebnisse ändert, kann ich nicht messen — ich habe
> keine Tickdaten. Das ist die ehrliche Grenze dieses Tests.

---

## Der entscheidende Test: Volumen-Level gegen Pivot-Level

Meine validierte Regel benutzt Level aus **Pivots**. Volume Profile liefert
Level aus **Volumen**. Gleiche Auswertung, gleiches Halten (48 h), gleiche
Kosten:

| Levelart | Suche 21-24 | **Holdout 25-26** |
|---|---|---|
| POC der Vorwoche | −7,4 bp (750) | **−26,7 bp (343)** |
| Value-Area-Grenzen der Vorwoche | −11,0 bp (1.418) | −15,4 bp (526) |
| POC des Vormonats | −11,0 bp (397) | −16,2 bp (149) |
| Value-Area-Grenzen des Vormonats | −1,5 bp (550) | −25,4 bp (348) |
| **S/R aus Pivots (validiert)** | **+49,4 bp (474)** | **+52,2 bp (301)** |

**Acht von acht Zellen negativ.** Alle t-Werte zwischen −0,01 und −0,25.

Die Pivot-Regel liefert im selben Zeitraum, auf denselben Daten, mit derselben
Auswertung **+52 bp im Holdout**. Das ist kein knappes Rennen.

> **Wenn Volume Profile das Einzige wäre, was funktioniert, müsste es genau
> hier gewinnen. Es verliert um rund 70 Basispunkte je Trade.**

---

## Die drei Standardbehauptungen einzeln

### 1. Der POC ist ein Magnet — nein

Weit unter POC long, weit über POC short (der Magnet-Trade):

| Markt | Suche | Holdout | t Suche | t Holdout |
|---|---|---|---|---|
| BTC | −0,09 | −0,03 | −0,73 | −0,51 |
| ETH | +0,22 | −0,83 | −0,14 | **−1,08** |
| SOL | −1,84 | +0,42 | **−1,82** | +0,09 |

**Alle sechs t-Werte bei null oder negativ.** Wenn überhaupt läuft es in die
Gegenrichtung — Fortsetzung statt Rückkehr.

### 2. Der Value-Area-Ausbruch trägt — teilweise

| Markt | Suche | Holdout |
|---|---|---|
| BTC | −6,7 bp (t −0,05) | +14,5 bp (t 0,12) |
| ETH | −62,8 bp (t −0,34) | +44,5 bp (t 0,16) |
| **SOL** | **+77,1 bp (t 0,23)** | **+101,3 bp (t 0,39)** |

BTC und ETH wechseln das Vorzeichen. **SOL ist in beiden Zeiträumen positiv**
— das ist die stärkste einzelne Zelle in dieser ganzen Untersuchung, und ich
nenne sie, weil sie da steht. Aber t = 0,39 ist weit von einem Befund entfernt,
und ein Markt von dreien ist genau das Muster, das Zufall erzeugt.

### 3. Der Kurs läuft schnell durch dünne Zonen — **das hält**

Mittlere absolute Bewegung über 48 h, je nach Volumendichte am aktuellen Kurs:

| Markt | Zeitraum | LVN (dünnstes 20 %) | HVN (dichtestes 20 %) | Verhältnis |
|---|---|---|---|---|
| BTC | Suche | 3,47 % | 2,80 % | **1,24×** |
| BTC | **Holdout** | 2,57 % | 2,38 % | **1,08×** |
| ETH | Suche | 4,07 % | 3,49 % | **1,17×** |
| ETH | **Holdout** | 4,40 % | 3,48 % | **1,26×** |
| SOL | Suche | 6,53 % | 5,36 % | **1,22×** |
| SOL | **Holdout** | 4,42 % | 4,20 % | **1,05×** |

**Sechs von sechs über 1,0.** Der Kurs bewegt sich in dünnen Zonen tatsächlich
schneller — konsistent über drei Märkte und beide Zeiträume.

**Das ist die wahre Aussage in deiner Behauptung.** Nur sagt sie etwas über die
**Geschwindigkeit**, nicht über die **Richtung**. Sie sagt dir, dass es schnell
gehen wird — nicht wohin. Und die Größe ist bescheiden: 5 bis 26 %.

---

## Und als Risikomaß? Schlechter als das, was du schon hast

Da die letzten drei Untersuchungen alle auf „Risiko ja, Richtung nein"
hinausliefen, habe ich das Profil auch dort eingeordnet:

| Markt | Maß | Vol 48 h Holdout | Tag ≤ −3 % |
|---|---|---|---|
| BTC | Value-Area-Breite | 0,332 | 0,151 |
| BTC | \|Abstand zum POC\| | 0,180 | 0,078 |
| BTC | Volumendichte am Kurs | 0,068 | 0,015 |
| BTC | Bollinger-Breite (120 h) | **0,385** | **0,185** |
| BTC | **Abwärts-Semivol (120 h)** | **0,435** | **0,188** |
| ETH | Value-Area-Breite | 0,252 | 0,061 |
| ETH | **Abwärts-Semivol** | **0,376** | **0,181** |
| SOL | Value-Area-Breite | 0,435 | 0,147 |
| SOL | **Abwärts-Semivol** | **0,532** | **0,206** |

**Die Abwärts-Semivol schlägt jedes Profil-Maß in jedem Markt in jeder
Spalte.** Und die Bollinger-Breite auch — dieselbe Bollinger-Breite, die im
vorigen Dokument gegen die VWAP-Bandbreite verloren hat.

Das ist bemerkenswert im Vergleich: **Der VWAP hat als Bandbreite die
Bollinger geschlagen. Das Volume Profile schafft das nicht** — obwohl beide
Volumen benutzen.

---

## Die Bilanz

| Behauptung | Ergebnis |
|---|---|
| Volumen-Level schlagen Pivot-Level | **nein — 8 von 8 negativ, −70 bp Abstand** |
| POC ist ein Magnet | **nein** — alle sechs t ≤ 0,09 |
| Value-Area-Ausbruch trägt | **1 von 3 Märkten** (SOL, t 0,39) |
| Kurs läuft schnell durch dünne Zonen | **ja — 6 von 6**, aber 5–26 % |
| Profil ist ein gutes Risikomaß | **nein** — schlechter als Semivol und Bollinger |

**„Das Einzige, was funktioniert" trifft nicht zu.** Was zutrifft: Ein Teil
davon — die dünnen Zonen — beschreibt zuverlässig, **wo es schnell gehen
kann**. Das ist eine echte Eigenschaft des Marktes, und sie ist mit sechs von
sechs konsistenter als fast alles andere in diesem Projekt.

Sie ist nur eine Aussage über **Tempo**, und Tempo verdient kein Geld. Genau
wie bei MACD, Stochastik, Bollinger und VWAP landet auch hier die einzige
haltbare Information auf der Risikoseite.

> **Fünf Werkzeuge getestet, fünfmal dasselbe Muster: über die Richtung leer,
> über das Risiko brauchbar.** Das ist kein Zufall mehr, das ist die
> Beschaffenheit von Preisdaten.

---

## Was das nicht widerlegt

- **Tickdaten / Footprint.** Mein Profil verteilt Bar-Volumen gleichmäßig über
  die Spanne. Wer echte Tickdaten hat, sieht ein feineres Bild. Ich kann nicht
  messen, ob das etwas ändert.
- **Diskretionäre Anwendung.** Wer das Profil ansieht und *dann* entscheidet,
  handelt etwas, das kein Backtest erfasst.
- **Andere Anker.** Ich habe rollierend, wöchentlich und monatlich getestet.
  Ereignis-Anker (Hoch, Tief, News) habe ich nicht getestet.
- **SOL bleibt offen.** +77 bp und +101 bp in beiden Zeiträumen ist die
  auffälligste Zelle. Ein Markt von dreien reicht nicht, aber ich verschweige
  sie nicht.

---

*Skripte: `research/vp.py` (Profilbau, POC-Magnet), `research/vp2.py`
(Value-Area-Ausbruch, LVN-Geschwindigkeit, Profil als Risikomaß),
`research/vp3.py` (Kopf-an-Kopf gegen die Pivot-Level).*
