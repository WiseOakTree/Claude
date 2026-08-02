# Traden als Beruf — die Rechnung

Nicht mehr die Frage „geht die Challenge", sondern die dahinter: **Was
bräuchte es, damit Traden ein Einkommen trägt?**

Grundlage ist der **einzige in dieser Untersuchung nachgewiesene Edge**: die
Volatilitäts-Risikoprämie, Sharpe 1,33 nach realistischen Kosten
([`volatility_premium.md`](volatility_premium.md)). Das ist
Hedgefonds-Niveau — eine wohlwollende Annahme, keine vorsichtige.

## A) Mit eigenem Kapital

Bei Sharpe 1,33 und 16 % Volatilität: **21,3 % pro Jahr**.

| Monatliches Netto-Ziel | nötiges Kapital | realistisch mit Puffer |
|---|---|---|
| 1.000 € | 56.000 € | **113.000 €** |
| 2.000 € | 113.000 € | **226.000 €** |
| 3.000 € | 169.000 € | **338.000 €** |
| 5.000 € | 282.000 € | **564.000 €** |

Die zweite Spalte ist der Erwartungswert, die dritte das Realistische: Man
kann nicht 100 % der erwarteten Rendite entnehmen, sonst beendet der erste
schlechte Jahrgang das Konto. Faustregel ist die halbe Entnahmequote.

## B) Über Prop-Konten — die strukturelle Falle

Entscheidend und leicht zu übersehen: **Das 6-%-Drawdown-Limit gilt nach dem
Bestehen weiter.** Ein gefundetes Konto ist kein Besitz, sondern ein Konto auf
Bewährung.

| Volatilität | Rendite p.a. | **überlebt 1 Jahr** | erwartete Lebensdauer |
|---|---|---|---|
| 8 % | 10,6 % | **69,5 %** | 219 Tage |
| 10 % | 13,3 % | **48,2 %** | 187 Tage |
| **16 %** | 21,3 % | **8,6 %** | 102 Tage |
| 20 % | 26,6 % | 1,8 % | 68 Tage |
| 30 % | 39,9 % | 0,0 % | 33 Tage |

**Hier liegt die Falle.** Aus [`required_edge.md`](required_edge.md): Die
Volatilität, die die Pass-Rate maximiert, ist **15–16 %**. Genau dort überlebt
das Konto danach nur **8,6 %** eines Jahres.

| | um zu **bestehen** | um zu **überleben** |
|---|---|---|
| optimale Volatilität | 15–16 % | 8–10 % |
| Pass-Rate dort | 23 % | 2,5–8 % |
| Ein-Jahres-Überleben dort | 8,6 % | 48–70 % |

**Beides gleichzeitig geht nicht.** Man handelt entweder groß genug, um die
+10 % zu schaffen, und verliert das Konto danach — oder klein genug, um es zu
behalten, und besteht nie.

## C) Was ein Prop-Konto tatsächlich einbringt

Konto 10.000 $, defensiv auf 10 % Volatilität gefahren:

| | |
|---|---|
| Bruttoertrag im Jahr | 1.330 $ |
| nach 90/10-Split | 1.197 $ |
| Überlebensrate | 47,7 % |
| **erwarteter Jahresertrag** | **571 $** |

Für **3.000 €/Monat** bräuchte man rund **63 solcher Konten gleichzeitig** —
und rund **22.500 $ an Gebühren**, um sie zu erlangen (4,2 Versuche je Konto).

Zum Vergleich: Dieselben 22.500 $ als **eigenes** Kapital, mit demselben Edge
gehandelt, ergeben rund 4.800 $ im Jahr — ohne Drawdown-Limit, ohne
Gebührenzyklus, ohne dass jemand das Konto schließen kann.

## Fazit

Traden **als Beruf** scheitert hier nicht am Spaß und nicht am Können, sondern
an zwei Zahlen:

1. **Kapital.** Selbst mit Hedgefonds-Niveau (Sharpe 1,33) braucht ein
   Einkommen von 3.000 €/Monat etwa **338.000 €**. Unterhalb von ~100.000 €
   ist Trading eine Nebeneinnahme, kein Gehalt — unabhängig vom Können.
2. **Die Prop-Falle.** Prop-Konten lösen das Kapitalproblem scheinbar, aber
   das fortbestehende 6-%-Limit macht das gefundete Konto zu einem Gut mit
   **102 Tagen erwarteter Lebensdauer** bei der Volatilität, die zum Bestehen
   nötig ist.

Was daraus **nicht** folgt: dass die Beschäftigung damit verschwendet war. Die
Fähigkeiten, die diese Untersuchung verlangt hat — bemerken, dass Backtest und
Realität auseinanderlaufen; eine Hypothese so formulieren, dass sie falsch sein
kann; einen Befund verwerfen, der zu gut aussieht — sind genau die, für die in
der Branche bezahlt wird. Der Look-ahead-Bias in diesem Repository wurde
gefunden, **weil** jemand gemerkt hat, dass TradingView und Kraken nicht
übereinstimmen.
