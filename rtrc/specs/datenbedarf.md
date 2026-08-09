# Datenbedarf für den vollständigen Test

Was von hier aus fehlt, und was es bräuchte. Damit die Lücke benannt ist
statt umgangen.

## 1. Point-in-time-Universen (die wichtigste Lücke)

**Problem:** Ein Backtest 2005–2026 auf den *heutigen* S&P-500-Mitgliedern
misst nicht, was investierbar war, sondern was überlebt hat. Der Effekt ist
in der Literatur mit mehreren Prozentpunkten pro Jahr beziffert.

**Was nötig wäre:**

| Quelle | was sie liefert | Kosten |
|---|---|---|
| CRSP (Center for Research in Security Prices) | Kurse und Indexmitgliedschaft nach Datum, inkl. delisteter Titel | akademische Lizenz |
| Compustat | Fundamentaldaten point-in-time | akademische Lizenz |
| Refinitiv / Bloomberg | beides | kommerziell |
| Norgate Data | Futures und Aktien mit Delisting-Historie | ~50–90 $/Monat |
| Sharadar (Nasdaq Data Link) | US-Aktien inkl. delisteter, mit Indexmitgliedschaft | ~50 $/Monat |

**Günstigster gangbarer Weg:** Sharadar SEP + SF1 über Nasdaq Data Link.
Enthält delistete Titel und historische Indexzugehörigkeit.

## 2. Einzelaktien und ETFs

Von hier aus blockiert: Stooq antwortet mit einer JavaScript-Sperre, Yahoo
mit HTTP 429.

**Alternativen, die geprüft werden müssten:**
- Nasdaq Data Link (kostenpflichtig, siehe oben)
- Alpha Vantage (kostenloses Kontingent, API-Schlüssel nötig)
- Tiingo (kostenloses Kontingent, API-Schlüssel nötig)
- EOD Historical Data (kostenpflichtig)

**Was du beisteuern könntest:** ein API-Schlüssel für Alpha Vantage oder
Tiingo. Beide haben kostenlose Stufen, die für Indexmitglieder ausreichen —
allerdings **ohne** delistete Titel, das Survivorship-Problem bliebe.

## 3. Futures

Für Rollrenditen und echte Terminkurven nötig. Frei nicht erreichbar.
Norgate oder Barchart wären die üblichen Quellen.

Ersatzweise verwendet die Untersuchung **Kassakurse und Indizes**. Das ist
für Ebene A und C ausreichend (die Regeln lesen Preise), verfälscht aber
Ebene B (Carry, Roll).

## 4. Fundamentaldaten

Für Value und Quality nötig. Nicht erreichbar. Diese beiden Faktoren bleiben
in Ebene B ausgespart und werden als solche gekennzeichnet.

## 5. Zinsdifferenzen für FX-Carry

Teilweise über FRED möglich (US-Sätze vollständig, ausländische Geldmarkt-
sätze lückenhaft). Wird geprüft; wenn unvollständig, entfällt Carry als
Faktor oder wird auf die Paare beschränkt, für die Daten vorliegen.

---

## Was das für den Zuschnitt bedeutet

| Anlageklasse | Ebene A | Ebene B | Ebene C | Ebene D |
|---|---|---|---|---|
| Krypto | ✅ | ✅ | ✅ | ✅ |
| Aktien**indizes** | ✅ | ✅ (ohne Value/Quality) | ✅ | ✅ |
| **Einzelaktien** | ❌ | ❌ | ❌ | ❌ |
| Devisen | ✅ | ⚠️ (Carry offen) | ✅ | ✅ |
| Rohstoffe | ✅ | ⚠️ (kein Roll) | ✅ | ✅ |
| Zinsen | ✅ | ✅ | ✅ | ✅ |
| Futures | ❌ | ❌ | ❌ | ❌ |

**Die Untersuchung kann damit vier von sieben gewünschten Anlageklassen
abdecken.** Das Ergebnis wird entsprechend eingeschränkt formuliert: Es gilt
für liquide Indizes, Währungspaare, Rohstoffkassakurse und Staatsanleihe-
renditen — nicht für Einzelaktien.
