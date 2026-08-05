# So einfach wie möglich — was Vereinfachung kostet, gemessen

> „Wir haben es uns extrem erschwert. Indikatoren und Strategien funktionieren
> einfach nicht. Wir müssen es so simpel wie möglich machen."

Richtig — und meine eigenen Zahlen sagen, warum: **37,5 % stehen im Regelwerk,
bevor jemand handelt** ([`zufall.md`](zufall.md)). Jede Komplikation kann davon
nur abziehen. Also die Gegenprobe: **Wie viel darf man weglassen?**

---

## Die versteckte Komplikation in der bisherigen Regel

Der Backtest stapelt überlappende Signale (`pos += richtung`, geklippt auf ±1).
Feuern drei Level in 48 Stunden, sitzt man in einer aufgestockten Position.
**Von Hand ist das kaum umsetzbar** — und niemand hat je gefragt, ob es nötig
ist.

Sieben Vereinfachungen, jede einzeln geprüft. Pass-Rate Suchzeitraum/Holdout,
0,5×:

| Variante | BTC | ETH | SOL | XRP | Ø ges | Trades |
|---|---|---|---|---|---|---|
| **Basis** (stapelnd, long+short, 48 h, ≥6) | 50,4 / 52,3 | 34,5 / 9,1 | 19,3 / 12,1 | 22,2 / 23,4 | 30,1 % | 3.946 |
| **A** nur EINE Position gleichzeitig | 40,9 / **57,4** | 57,3 / 4,3 | 36,3 / 0,5 | 24,2 / 9,1 | **33,9 %** | **930** |
| **B** nur LONG (Shorts weglassen) | 38,5 / 26,4 | 49,0 / 24,8 | 35,9 / 34,4 | 18,7 / 2,4 | **37,9 %** | 1.719 |
| C eine Position UND nur long | 42,6 / 0,0 | 44,2 / 0,6 | 30,7 / 23,0 | 17,2 / 2,4 | 28,2 % | 507 |
| D Halten 24 h statt 48 h | 49,6 / 50,2 | 26,6 / 2,9 | 14,9 / 0,4 | 22,8 / 3,7 | 25,0 % | 3.946 |
| **E** nur starke Level ≥10 Berührungen | **0,0 / 0,0** | 0,0 / 0,6 | 0,0 / 1,6 | 0,0 / 0,0 | **0,2 %** | 503 |
| **F** maximal einfach: 1 Pos, long, ≥10 | **0,0 / 0,0** | 0,0 / 0,0 | 13,5 / 0,0 | 8,2 / 0,0 | **3,8 %** | 81 |

**Das wichtigste Ergebnis steht in den letzten zwei Zeilen.** „Nur die besten
Signale nehmen" — der Rat, den jeder gibt — liefert **null Prozent**. Nicht
wenig. Null.

---

## Warum „weniger, aber besser" auf null führt

Weil es gar keine Strategien gibt. Es gibt **effektive Volatilität** und
**Kosten**. Gemessen auf BTC, ganze Historie:

| Variante | Zeit im Markt | Jahresvol | **Pass** | Zufall bei gleicher Vol | Überschuss |
|---|---|---|---|---|---|
| Basis 0,5× | 26 % | **13,6 %** | **50,1 %** | 35,9 % | **+14,2** |
| Basis 0,25× | 26 % | 6,8 % | 33,9 % | 14,0 % | +19,9 |
| Basis 1,0× | 26 % | 27,2 % | 40,2 % | 27,0 % | +13,2 |
| 1 Position | 22 % | 12,5 % | 44,7 % | 34,0 % | +10,7 |
| nur long | 14 % | 10,6 % | 42,7 % | 30,7 % | +12,0 |
| 24 h halten | 19 % | 11,0 % | 49,0 % | 31,9 % | **+17,1** |
| ≥10 Berührungen | **1 %** | **3,1 %** | **0,0 %** | 0,2 % | ±0,0 |
| ≥10, aber 3,0× | 1 % | 19,3 % | **10,4 %** | 35,5 % | **−25,1** |

Drei Dinge stehen in dieser Tabelle:

**1. Die Basis bei 0,5× hat 13,6 % Jahresvolatilität.** Das ist praktisch
exakt das theoretische Optimum von 15 %. **Deshalb** war 0,5× die beste Größe
— nicht aus strategischen Gründen, sondern weil sie zufällig auf dem Optimum
landet.

**2. „Nur starke Level" ist 1 % Zeit im Markt = 3,1 % Vol.** Bei 3 % Vol sagt
die Zufallssimulation 0,2 % Pass-Rate voraus. Gemessen: 0,0 %. Du erreichst
+10 % nie, weil du fast nie im Markt bist. **Selektivität tötet, sie schützt
nicht.**

**3. Und man kann es nicht mit Hebel reparieren.** ≥10 Berührungen bei 3,0×
trifft die richtige Vol (19,3 %) — und liefert trotzdem nur 10,4 % statt der
35,5 %, die Zufall bei dieser Vol gäbe. **25 Punkte unter Zufall.** Weil
dieselbe Volatilität in wenigen konzentrierten Schüben das 3-%-Tageslimit
reißt, während sie über viele Tage verteilt harmlos ist.

> **Die Regel, die alles zusammenfasst: viel Zeit klein im Markt schlägt wenig
> Zeit groß im Markt — bei exakt gleicher Volatilität.**

---

## Was Vereinfachung tatsächlich kostet: fast nichts

Direktvergleich, heutige Regel gegen „nur eine Position gleichzeitig":

| Asset | Basis 0,5× (Such/Hold/ges) | 1 Position 0,65× | Differenz |
|---|---|---|---|
| BTC | 50,4 / 52,3 / **50,1** | 50,5 / 40,5 / 47,0 | −3,1 |
| ETH | 34,5 / 9,1 / 27,1 | 47,6 / 5,0 / **35,5** | **+8,4** |
| SOL | 19,3 / 12,1 / 20,3 | 24,2 / 2,2 / 22,1 | +1,8 |
| XRP | 22,2 / 23,4 / 22,9 | 24,0 / 8,6 / 20,0 | −2,9 |
| **Mittel** | **30,1 %** | **31,1 %** | **+1,0** |
| **Trades** | **3.946** | **930** | **−76 %** |

**Ein Viertel der Trades, gleiche Pass-Rate.** Das ist der beste Tausch in
diesem gesamten Projekt: Alles, was die aufgestockte Position an Komplexität
kostete, war umsonst.

### Und die Größe ist erstaunlich egal

BTC, eine Position gleichzeitig:

| Größe | Jahresvol | Such | Holdout | gesamt |
|---|---|---|---|---|
| **0,35×** | 8,8 % | 47,4 % | **53,9 %** | **48,4 %** |
| 0,50× | 12,5 % | 40,9 % | **57,4 %** | 44,7 % |
| 0,65× | 16,2 % | 50,5 % | 40,5 % | 47,0 % |
| 0,80× | 20,0 % | 48,3 % | 34,7 % | 43,9 % |
| 1,00× | 25,0 % | 53,4 % | 37,6 % | 48,3 % |

44 bis 48 % über die ganze Spanne, ohne erkennbares Optimum. **Hör auf, die
Größe zu optimieren.** Irgendetwas zwischen 0,35× und 0,5× ist richtig; der
Rest ist Rauschen. Nur oberhalb ~25 % Vol wird es messbar schlechter.

---

## Die einfachste Regel, die alles überlebt hat

```
Asset      NUR BTC. 1-Stunden-Chart.
Signal     Level mit >=6 Beruehrungen, Einstieg beim Bruch.
Position   EINE. Bist du drin, ignorierst du jedes neue Signal.
Halten     48 Stunden. Dann raus. Egal was.
Stop       KEINER.
Groesse    3.500 $ Nominal bei 10.000 $ Konto  (0,35x)
Frequenz   ~40 Trades im Jahr.
Zeit       Kein Limit bei Kraken. Rechne mit ~4 Monaten.
```

**Erwartung: 48 % (Suchzeitraum 47,4 %, Holdout 53,9 %).**

Gegenüber der alten Regel: gleiche Zahlen, **ein Viertel der Trades**, keine
gestapelten Positionen, keine Entscheidung während einer laufenden Position.

## Die vier Sätze, die den Rest ersetzen

1. **Selektiver werden macht es schlechter, nicht besser.** ≥10 Berührungen
   statt ≥6 → 0,0 %.
2. **Der Hebel repariert das nicht.** Gleiche Vol in Schüben statt verteilt →
   25 Punkte unter Zufall.
3. **Handeln kostet 23 Prozentpunkte** ([`zufall.md`](zufall.md)). Jeder Trade,
   den du nicht machst und nicht brauchst, ist bares Geld.
4. **Die Größe zwischen 0,35× und 0,5× ist Rauschen.** Wähle 0,35× und rühr
   sie nicht mehr an.

---

## Was auch die einfachste Regel nicht ändert

- **Sie gilt für BTC.** ETH-, SOL- und XRP-Holdouts liegen bei 2 bis 9 %,
  in jeder geprüften Variante. Das ist die alte Warnung
  ([`heikin_ashi.md`](heikin_ashi.md)), und sie wird durch Vereinfachung
  nicht kleiner.
- **Der BTC-Holdout ist inzwischen sechsmal benutzt.** Seine 53,9 % sind kein
  unabhängiger Beleg mehr.
- **Der Edge selbst ist ~12–17 Punkte über einem gleich dimensionierten
  Münzwurf.** Nicht mehr. Der Rest der 48 % gehört dem Regelwerk.

---

*Skripte: `research/simpel.py` (Varianten), `research/simpel2.py`
(Volatilität sagt Pass-Rate voraus), `research/simpel3.py` (Größensweep und
Direktvergleich).*
