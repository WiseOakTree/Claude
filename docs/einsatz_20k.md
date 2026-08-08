# 20.000 $ eigenes Kapital — was heute wirklich geht

Gut, dass du gefragt hast, bevor du einzahlst. **Die historischen 37 % des
HLP-Vaults sind nicht die aktuelle Rendite.** Ich habe die letzten Fenster
einzeln nachgerechnet, und das Ergebnis ändert die Empfehlung.

---

## 🛑 Der HLP-Vault verdient gerade nichts

Aus demselben API-Aufruf, jedes Fenster einzeln:

| Fenster | Dauer | PnL | Ø Kapital | **annualisiert** |
|---|---|---|---|---|
| letzter Tag | 1,0 d | +1.298 $ | 215,3 M | **+0,2 %** |
| **letzte Woche** | 7,1 d | **−20.753 $** | 217,5 M | **−0,5 %** |
| **letzter Monat** | 30,4 d | +63.818 $ | 231,6 M | **+0,3 %** |
| gesamte Historie | 1.185 d | +136,9 M $ | 222,0 M | +15,9 % |

Und die Jahre, jeweils korrekt annualisiert:

| Jahr | annualisiert |
|---|---|
| 2023 | **+37,9 %** |
| 2024 | **+85,9 %** |
| 2025 | +19,5 % |
| 2026 | +12,6 % |
| **letzte 30 Tage** | **+0,3 %** |

Die API meldet das selbst: das Feld `apr` steht bei **0,0021** — also 0,21 %.

> **Ich habe dir gestern +37,3 % p.a. mit Sharpe 2,12 berichtet. Das war der
> Durchschnitt über drei Jahre. Der aktuelle Lauf liegt bei null.**

Ein Monat ist kurz, und eine flaue Phase ist kein Ende. Aber zusammen mit dem
Verlauf **86 → 20 → 13 → 0** ist das kein Ausreißer, sondern die Fortsetzung
einer Linie.

---

## Der Funding-Carry hält sich besser

| Monat | annualisiert | Anteil positiv |
|---|---|---|
| 2026-01 | +5,39 % | 95,7 % |
| **2026-02** | **−0,83 %** | 46,4 % |
| **2026-03** | **−1,09 %** | 44,1 % |
| **2026-04** | **−2,16 %** | 35,6 % |
| 2026-05 | +2,72 % | 71,0 % |
| 2026-06 | +2,47 % | 76,7 % |
| **2026-07** | **+6,66 %** | 98,9 % |

| | annualisiert |
|---|---|
| letzte 30 Tage | **+6,71 %** |
| letzte 90 Tage | +4,13 % |
| gesamter Zeitraum | +7,05 % |

**Drei negative Monate in Folge im Frühjahr 2026** — die Carry ist nicht
risikofrei, sie ist nur ruhig. Aktuell liefert sie 4 bis 7 %.

---

## Was 20.000 $ realistisch bringen

| Anlage | aktueller Lauf | **auf 20.000 $** |
|---|---|---|
| HLP-Vault | ~0 % | **~0 $** |
| Funding-Carry | 4–7 % | **800–1.400 $** |
| Volatilitätsprämie | ~25 %, aber tägliche Arbeit + Optionszugang | 5.000 $ |
| Tagesgeld / kurzlaufende Anleihen | *(nicht gemessen, Vergleichsanker)* | — |

**Das ist die Zahl, um die es geht: 800 bis 1.400 Dollar im Jahr.**

Und sie ist exakt die Arithmetik aus [`der_weg.md`](der_weg.md): Einkommen =
Kapital × Rendite. Bei 20.000 $ ändert keine Strategie der Welt etwas an der
Größenordnung.

---

## Was ich an deiner Stelle täte

### 1. Nicht alles auf einmal einzahlen

Nicht wegen Timing, sondern weil du **die aktuelle Ertragslage sonst nie
messen kannst**. Vorschlag:

| | |
|---|---|
| **jetzt** | 2.000–3.000 $ in den Funding-Carry, zum Lernen der Mechanik |
| **nach 3 Monaten** | eigene Zahlen prüfen: Was ist tatsächlich angekommen? |
| **dann** | schrittweise aufstocken — oder feststellen, dass es sich nicht lohnt |

Die 20.000 $ laufen dir nicht weg. Der Unterschied zwischen „jetzt alles" und
„über neun Monate verteilt" ist bei 5 % Rendite etwa **500 $** — und dafür
kaufst du dir die Möglichkeit, mit echtem Geld zu messen, statt mit meinen
Tabellen zu planen.

### 2. Den HLP-Vault jetzt nicht bestücken

Nicht weil er schlecht ist, sondern weil **null Prozent** kein Grund für eine
Einzahlung ist. Setz ihn auf Beobachtung: Wenn er in drei Monaten wieder über
8 % annualisiert liefert, ist das eine neue Datenlage.

*(Wenn du dennoch einsteigen willst: die Einlagen dort haben eine Sperrfrist,
und der Vault kann Einzahlungen schließen. Das gehört vor die Entscheidung,
nicht danach.)*

### 3. Die Vergleichszahl nicht vergessen

**4 bis 7 % mit Börsenrisiko, Liquidationsrisiko und laufender Arbeit** muss
sich gegen das messen, was ein Tagesgeldkonto oder ein kurzlaufender
Anleihen-ETF risikoarm liefert. Diese Zahl habe ich hier nicht gemessen — aber
sie ist der Maßstab. **Wenn der Abstand unter zwei Prozentpunkten liegt, ist
der Aufwand nicht bezahlt.**

### 4. Was das Ganze eigentlich ist

| | |
|---|---|
| Was es **nicht** ist | ein Einkommen |
| Was es **ist** | ein Sparbeschleuniger, der ohne Prognose funktioniert |
| Der eigentliche Hebel | wie viel du im Jahr **zurücklegst**, nicht wie du es anlegst |

Aus [`der_weg.md`](der_weg.md): Eine um ein Drittel bessere Rendite bringt
genauso viel wie eine um ein Drittel höhere Sparrate — nur ist die Sparrate
sicher.

---

## Was ich falsch gemacht habe

Ich habe dir gestern **+37,3 % p.a. und Sharpe 2,12** berichtet, ohne zu
prüfen, ob das der aktuelle Lauf ist. Die Kennzahl stimmte für den
Dreijahresdurchschnitt und war für eine Entscheidung **heute** irreführend.

Das ist derselbe Fehlertyp wie der Rainbow Chart: eine über den gesamten
Zeitraum gemittelte Größe als Aussage über die Gegenwart zu lesen. Ich hätte
den `apr`-Wert im ersten Aufruf sehen müssen — er stand in derselben Antwort.

---

*Skripte: `research/haus3.py` (Historie), `research/vault_aktuell.py`
(Fenstervergleich, aktuelle Ertragslage, Funding-Monate).*
