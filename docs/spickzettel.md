# Spickzettel — Renko-Reversal live handeln

Eine Seite fürs Handy. Für **Kraken Prop „Starter", 10.000 $**, Einstellung
`0.75× ATR(14)`, `0,3 % Risiko`, 1-Stunden-Chart.

---

## 0. Einmalig prüfen (bevor du startest)

| Einstellung | Wert |
|---|---|
| Timeframe | **1h** (nicht 4h, nicht Tages) |
| Kontogröße im Indikator / in der Config | **10000** ← häufigster Fehler |
| Risiko pro Trade | **0,3 %** = 30 $ |
| ATR-Länge / Brick | 14 / **0,75×** |
| Reversal nach | 2 Bricks |

> ⚠️ Steht die Kontogröße falsch (z. B. noch auf 50.000), sind alle Positions-
> größen um das 5-Fache zu groß und du reißt das 6 %-Limit in wenigen Trades.

**Merkregel für die Größe:** `Size = 30 $ ÷ (2 × Brick)`
Beispiel: Brick 236,75 → Size = 30 ÷ 473,50 = **0,0634 BTC** (~4.000 $ Nominal).

---

## 1. Der einzige Ablauf, den du brauchst

1. Nachricht kommt → **eine Stop-Order** auf das genannte Level legen
2. Meldung „Level verschoben" → Order **nachziehen**
3. Order löst aus → Position dreht, neues Level kommt → zurück zu 1.

Mehr ist es nicht. Kein TP, kein manuelles Schließen.

---

## 2. Situation → Aktion

| Situation | Was du tust |
|---|---|
| **Du startest gerade, Indikator zeigt schon eine Position** | **Nicht einsteigen.** Warten, bis das nächste Signal auslöst, dann frisch mitgehen. |
| **Neues Level gemeldet, du bist flat** | Stop-Order auf das Level legen, Größe nach Formel oben. |
| **Du bist Long, Sell-Stop unter dem Einstieg** | Nichts tun. Das ist dein geplantes Risiko (30 $). |
| **Du bist Long, Sell-Stop über dem Einstieg** | Nichts tun — Gewinn ist gesichert, lass laufen. |
| **Level hat sich zu deinen Gunsten verschoben** (Long: höher / Short: tiefer) | Order **nachziehen**. |
| **Level hat sich zu deinen Ungunsten verschoben** (Long: tiefer) | **Order stehen lassen.** Niemals das Risiko nachträglich vergrößern. |
| **Position ist im Minus, Stop rückt näher** | Nichts tun. Aussitzen oder ausstoppen lassen. |
| **Preis nähert sich TP1 / TP2** | Nichts tun. Die TPs sind nur Orientierung — Mitnehmen kostet ~19 Prozentpunkte Erfolgsquote. |
| **Bot war offline / du hast ein Signal verpasst** | Nicht nachträglich einsteigen. Auf das nächste Signal warten. |
| **Drawdown nähert sich 6 % (−600 $)** | Handel pausieren. Die Challenge hat kein Zeitlimit; ein Bust ist endgültig. |
| **Tagesverlust nähert sich 3 % (−300 $)** | Für den Tag aufhören. Reset ist 00:30 UTC. |

---

## 2b. Die Flip-Order (Position drehen)

Du bist in einer Position und das Gegensignal kommt. **Eine** Trigger-Order
erledigt beides — Schließen und Drehen:

```
Flip-Menge = aktuelle Position + 30 $ / (2 x aktueller Brick)
```

Beispiel: short 0,095 BTC, Brick 157,72
→ 0,095 + 30/315,44 = **0,1901 BTC** als Buy-Trigger.

Danach im **Positions-Tab** prüfen: dort muss die Gegenposition stehen
(hier: Long 0,0951), nicht „keine Position".

### Die Schutzlücke — wichtig

Zwischen dem Füllen der Einstiegs-Order und dem Platzieren der Flip-Order bist
du **ohne Stop**. Zwei Wege:

| Lage | Vorgehen |
|---|---|
| **Du bist erreichbar** | Warten bis gefüllt → sofort Flip-Order (doppelte Menge) setzen. Das ist die getestete Variante. |
| **Du bist weg / schläfst** | Einstiegs-Order mit aktiviertem **TP/SL** platzieren, SL auf das Reversal-Level. Schutz ist garantiert. |

Bei der zweiten Variante bist du nach dem Auslösen **flat statt gedreht** — der
Verlust ist begrenzt, aber die Gegenrichtung fehlt. Den Einstieg dann bei der
nächsten Gelegenheit nachholen; je später, desto schlechter der Kurs.

> Merke: Schutz geht vor. Lieber flat und abgesichert als ungedeckt im Markt.

---

## 3. Die drei „Nie"

1. **Nie** den Stop in die falsche Richtung verschieben (Long tiefer, Short höher).
2. **Nie** manuell schließen, weil es rot aussieht — der Stop macht das.
3. **Nie** ein verpasstes Signal nachträglich hinterherkaufen.

---

## 4. Was normal ist (damit du nicht nervös wirst)

- **59 % deiner Trades sind Verlierer.** Das ist by design.
- Ø Verlierer −29 $, Ø Gewinner +75 $ — der **größte** Gewinner in den Daten war
  **+519 $ (17R)**. Diese wenigen Trades tragen das Ergebnis.
- Serien von 4–6 Verlusten hintereinander kommen vor.
- Erwartetes Tempo bis +1.000 $: **~2–3 Monate**.
- Erfolgswahrscheinlichkeit über 4 Jahre Backtest: **93 %** — aber in ~7 % der
  Fälle reißt auch das beste Setting das Limit. Dann: neue Challenge, nicht
  „aufholen wollen".

---

## 5. Zahlen für dein 10k-Konto

| | |
|---|---|
| Ziel | **+1.000 $** (10 %) |
| Max Drawdown | **−600 $** (6 %) |
| Max Tagesverlust | **−300 $** (3 %, Reset 00:30 UTC) |
| Risiko je Trade | **30 $** (0,3 %) |
| Ø Positionsgröße | ~4.000 $ Nominal (0,4× Hebel) |
| Kosten je Trade | ~6,40 $ (Kommission + Funding + Slippage) |

---

## 6. Wenn etwas unklar ist

- Warum kein TP? → [`realism.md`](realism.md), Abschnitt 2c
- Warum vorab platzierte Orders? → [`realism.md`](realism.md), Abschnitt 1
- Bot einrichten → [`deploy_signals.md`](deploy_signals.md)

**Kein Finanzrat. Backtests sagen die Zukunft nicht vorher.**
