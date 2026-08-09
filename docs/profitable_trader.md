# „Es gibt profitable Trader, das kann kein Glück mehr sein"

Die Aussage ist **wahr** — und die öffentliche Statistik ist trotzdem kein
Beleg dafür. Beides gleichzeitig. Hier ist die Rechnung.

---

## Wie viele „profitable Trader" zeigt reiner Zufall?

100.000 Trader, **alle mit wahrem Erwartungswert exakt null**, 60 %
Jahresvolatilität (ein typisch gehebeltes Retail-Konto):

| nach | im Plus | über +20 % | über +50 % | **über +100 %** | **jedes Jahr im Plus** |
|---|---|---|---|---|---|
| 1 Jahr | 38,2 % | 27,3 % | 16,6 % | 7,3 % | 38,2 % |
| 2 Jahre | 33,5 % | 26,1 % | 18,5 % | 10,7 % | 14,6 % |
| 3 Jahre | 30,0 % | 24,3 % | 18,2 % | 11,7 % | 5,5 % |
| **5 Jahre** | 25,0 % | 20,8 % | 16,4 % | **11,8 %** | **0,8 %** |
| 10 Jahre | 17,3 % | 15,0 % | 12,4 % | 9,5 % | 0,0 % |

Bei 100.000 Tradern heißt das nach fünf Jahren:

> **11.550 Trader mit über +100 %.**
> **858 Trader mit fünf Gewinnjahren in Folge.**
> **Und niemand von ihnen hat irgendein Können.**

Eine Bestenliste sieht mit null Können praktisch genauso aus wie mit. Deshalb
ist „ich sehe profitable Trader" **kein** Beweis — nicht weil die Trader nicht
existieren, sondern weil die Beobachtung nicht zwischen den beiden Welten
unterscheidet.

*(Die Zahlen wirken hoch, weil eine Handvoll enormer Gewinner die Verteilung
schief zieht: Der Median liegt tief im Minus, aber die rechte Flanke ist lang.
Genau diese Flanke ist es, die man in Ranglisten sieht.)*

---

## 🟢 Und jetzt die andere Hälfte: Können existiert und ist messbar

Angenommen, **1 % der Trader haben echtes Können** (Sharpe 1,0 — sehr gut).
Wie viele davon stehen in den besten 1 % der Rangliste?

| nach | Anteil echter Könner unter den besten 1 % |
|---|---|
| 1 Jahr | 8,3 % |
| 3 Jahren | 24,2 % |
| 5 Jahren | **41,1 %** |
| 10 Jahren | **65,5 %** |

**Nach zehn Jahren sind zwei Drittel der Spitzenliste echte Könner.** Das ist
das Gegenteil von „alles Zufall" — die Information ist da, sie braucht nur
Zeit, um sich vom Rauschen zu trennen.

Konkret, bei 100.000 Tradern und 1 % Könnern nach drei Jahren:

| Liste | Trader darin | davon echte Könner |
|---|---|---|
| im Plus | 30.617 | 906 (**3,0 %**) |
| über +50 % | 18.680 | 809 (**4,3 %**) |
| **über +200 %** | 6.404 | **538 (8,4 %)** |

Selbst in der Liste „über +200 % in drei Jahren" stehen **538 echte Könner
neben 5.866 Glücklichen**. Die Könner sind real. Sie sind nur nicht
identifizierbar, solange man auf die Rendite schaut.

---

## Der einzige Test, der trennt: Persistenz

Anteil der Bestenliste aus Jahr 1, der auch in Jahr 2 wieder oben steht
(Zufallserwartung: 1,0 %):

| Anteil Könner | Sharpe | Persistenz | Zufall |
|---|---|---|---|
| 0 % | — | 0,8 % | 1,0 % |
| 1 % | 1,0 | 2,3 % | 1,0 % |
| 5 % | 1,0 | 3,1 % | 1,0 % |
| **1 %** | **2,0** | **12,9 %** | 1,0 % |
| 10 % | 0,5 | 2,0 % | 1,0 % |

**Persistenz trennt, Rendite nicht.** Wer wissen will, ob eine Rangliste
Können enthält, muss fragen: *Wie viele der Vorjahressieger sind dieses Jahr
wieder oben?* Nicht: *Wie hoch ist der Beste?*

Und: Selbst bei Sharpe 2,0 und 1 % Könnern bleibt die Persistenz bei 12,9 % —
also sind **87 % der Vorjahressieger auch dann noch Glückstreffer**.

---

## Was du daraus praktisch mitnimmst

**Wenn dir jemand seine Statistik zeigt, sind das die Fragen:**

1. **Über wie viele Jahre?** Unter drei Jahren sagt eine Kurve nichts —
   11,8 % erreichen +100 % ohne Können.
2. **Wie viele Konten stehen daneben?** Ein Anbieter mit 50.000 Nutzern
   produziert seine Spitzengruppe automatisch.
3. **Wie oft war er vorher schon oben?** Das ist die einzige Frage, deren
   Antwort zwischen Können und Glück unterscheidet.
4. **Wie hoch ist die Volatilität?** Bei 60 % Jahresvol ist +100 % ein
   Rauschereignis. Bei 8 % Jahresvol wäre es eines von Millionen.

**Und der Punkt, der für dich zählt:** Deine eigene Geschichte — 2k → 10k →
76k → 10k → 100k → 3k → null — ist exakt die Bahn, die diese Simulation
erzeugt. Nicht als Vorwurf, sondern als Einordnung: Du warst zeitweise in der
Spitzengruppe, die es **auch ohne jedes Können gibt**. Die Frage ist nie, ob
man dort ankommt. Die Frage ist, ob man dort bleibt.

---

## Was diese Rechnung nicht sagt

- **Sie unterstellt eine Normalverteilung** der Jahresrenditen. Echte
  gehebelte Konten haben fettere Ränder und Totalverluste; die Zahl der
  scheinbaren Gewinner wäre real eher höher.
- **Der Anteil von 1 % Könnern ist eine Annahme.** Die akademische Literatur
  zu Tageshändlern (Taiwan, Brasilien) landet in derselben Größenordnung, aber
  ich habe diese Studien hier nicht nachgeschlagen — nimm die 1 % als
  Rechenbeispiel, nicht als gemessenen Branchenwert.
- **Sie sagt nichts über die Höhe des Könnens**, die tatsächlich erreichbar
  ist. Was ein realistischer Edge bringt, steht in
  [`firmen.md`](firmen.md).

---

*Skript: `research/trader.py` (Rauschdecke bei Tradern, Erkennbarkeit von
Können, Persistenztest).*
