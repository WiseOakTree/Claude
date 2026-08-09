"""Kraken-Prop-Regeln und Challenge-Evaluator.

Enthaelt die offiziellen Kraken-Prop-Presets (Stand 2026) und einen Evaluator,
der eine Equity-Kurve gegen die Regeln prueft:

  * Profit-Target(s) pro Phase
  * Max Daily Loss (Reset 00:30 UTC, auf Basis des Tages-Anfangsstands)
  * Max Total Drawdown (statisch = ab Startkapital, oder trailing = ab Equity-Hoch)
  * realized + unrealized PnL zaehlen (Equity-basiert)

Wichtig: Prop-Firmen aendern Regeln. Die Presets sind ein sinnvoller, dokumentierter
Ausgangspunkt -- bitte vor dem Kauf mit der aktuellen Kraken-Seite abgleichen.
Quellen sind im README verlinkt.

Mehrstufige Challenges (2-Step) werden phasenweise auf einem *frischen* Konto der
gleichen Groesse ausgewertet -- so wie es real ablaeuft (Phase 2 startet neu).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


@dataclass
class PropRules:
    name: str
    profit_targets: List[float]      # ein Eintrag pro Phase (z.B. [0.10] oder [0.10, 0.05])
    max_daily_loss_pct: float        # z.B. 0.03
    max_total_drawdown_pct: float    # z.B. 0.03 / 0.06 / 0.08
    drawdown_type: str = "static"    # "static" oder "trailing"
    daily_reset_utc: time = time(0, 30)
    min_trading_days: int = 0
    note: str = ""

    @property
    def steps(self) -> int:
        return len(self.profit_targets)


# --- Offizielle Kraken-Prop-Presets ------------------------------------------
# 3% Max Daily Loss gilt tierweit. 1-Step = statischer Drawdown ab Startkapital,
# 2-Step = trailing Drawdown ab Equity-Hoch.
PRESETS: Dict[str, PropRules] = {
    "1step_turbo": PropRules(
        name="Kraken 1-Step Turbo",
        profit_targets=[0.09],
        max_daily_loss_pct=0.03,
        max_total_drawdown_pct=0.03,
        drawdown_type="static",
        note="9% Target, 3% statischer Drawdown, 3% Daily Loss.",
    ),
    "1step_pro": PropRules(
        name="Kraken 1-Step Pro",
        profit_targets=[0.12],
        max_daily_loss_pct=0.03,
        max_total_drawdown_pct=0.03,
        drawdown_type="static",
        note="12% Target, 3% statischer Drawdown, 3% Daily Loss.",
    ),
    # In der Kraken-App heisst dieser Plan "Starter" -- Werte am 2026-07-31 in der
    # Evaluations-Maske bestaetigt (10k Wallet: Target 10%, Daily 3%, Drawdown 6%,
    # Hebel bis 5x, Profit-Split bis 90%, Gebuehr 85 USD).
    "1step_classic": PropRules(
        name="Kraken Starter (1-Step Classic)",
        profit_targets=[0.10],
        max_daily_loss_pct=0.03,
        max_total_drawdown_pct=0.06,
        drawdown_type="static",
        note="10% Target, 6% statischer Drawdown, 3% Daily Loss. "
             "= Plan 'Starter' in der Kraken-App (bestaetigt).",
    ),
    "2step_classic": PropRules(
        name="Kraken 2-Step Classic",
        profit_targets=[0.10, 0.05],
        max_daily_loss_pct=0.03,
        max_total_drawdown_pct=0.08,
        drawdown_type="trailing",
        note="Phase1 10% + Phase2 5% Target, 8% trailing Drawdown, 3% Daily Loss.",
    ),
}

DEFAULT_PRESET = "1step_classic"

# Namen aus der Kraken-App -> interne Preset-Schluessel. Bewusst NICHT in PRESETS
# aufgenommen, damit Berichte dasselbe Regelwerk nicht doppelt auswerten.
ALIASES = {
    "starter": "1step_classic",
}


def resolve_preset(key: str) -> str:
    """Loest App-Namen wie 'starter' auf den internen Preset-Schluessel auf."""
    return ALIASES.get(key, key)


@dataclass
class PhaseResult:
    index: int
    target_pct: float
    status: str                       # "passed" | "failed" | "incomplete"
    fail_reason: Optional[str] = None
    end_time: Optional[pd.Timestamp] = None
    trading_days: int = 0
    max_drawdown_pct: float = 0.0     # groesster beobachteter Rueckgang in der Phase
    peak_profit_pct: float = 0.0      # hoechster erreichter Gewinn in der Phase


@dataclass
class ChallengeResult:
    rules: PropRules
    account_size: float
    passed: bool
    phases: List[PhaseResult] = field(default_factory=list)
    total_trading_days: int = 0

    @property
    def summary(self) -> str:
        status = "BESTANDEN" if self.passed else "NICHT bestanden"
        return f"{self.rules.name}: {status}"

    def to_dict(self) -> dict:
        return {
            "rules": self.rules.name,
            "account_size": self.account_size,
            "passed": self.passed,
            "total_trading_days": self.total_trading_days,
            "phases": [
                {
                    "phase": p.index + 1,
                    "target_pct": p.target_pct,
                    "status": p.status,
                    "fail_reason": p.fail_reason,
                    "end_time": None if p.end_time is None else p.end_time.isoformat(),
                    "trading_days": p.trading_days,
                    "max_drawdown_pct": p.max_drawdown_pct,
                    "peak_profit_pct": p.peak_profit_pct,
                }
                for p in self.phases
            ],
        }


def _day_key(ts: pd.Timestamp, reset: time) -> tuple:
    """Handelstag-Schluessel mit Reset zur ``reset``-Uhrzeit (UTC)."""
    shifted = ts - pd.Timedelta(hours=reset.hour, minutes=reset.minute)
    return (shifted.year, shifted.month, shifted.day)


def _factors(equity: pd.DataFrame, initial_balance: float):
    """Bar-zu-Bar-Faktoren (close/low/high) relativ zum Vorgaenger-Close."""
    ec = equity["equity_close"].to_numpy(float)
    el = equity["equity_low"].to_numpy(float)
    eh = equity["equity_high"].to_numpy(float)
    prev = np.empty_like(ec)
    prev[0] = initial_balance
    prev[1:] = ec[:-1]
    with np.errstate(divide="ignore", invalid="ignore"):
        cf = np.where(prev > 0, ec / prev, 0.0)
        lf = np.where(prev > 0, el / prev, 0.0)
        hf = np.where(prev > 0, eh / prev, 0.0)
    return cf, lf, hf


def _evaluate_phase(cf, lf, hf, times, start_i: int, target_pct: float,
                    rules: PropRules, account_size: float) -> PhaseResult:
    """Wertet eine einzelne Phase auf einem frischen Konto aus.

    Rueckgabe enthaelt Status und -- bei Erfolg -- den End-Bar-Index via
    ``end_time`` sowie ``_end_i`` (angehaengt fuer die Ablaufsteuerung).
    """
    dd = rules.max_total_drawdown_pct
    mdl = rules.max_daily_loss_pct
    target_equity = account_size * (1 + target_pct)

    cur = account_size
    peak = account_size
    day_start = account_size
    cur_day = None
    trading_days = 0
    max_dd = 0.0
    peak_profit = 0.0

    res = PhaseResult(index=-1, target_pct=target_pct, status="incomplete")
    res._end_i = len(times) - 1  # type: ignore[attr-defined]

    for i in range(start_i, len(times)):
        # Tages-Reset (00:30 UTC): Referenz = Equity zu Tagesbeginn
        dk = _day_key(times[i], rules.daily_reset_utc)
        if dk != cur_day:
            cur_day = dk
            day_start = cur
            trading_days += 1

        bar_high_eq = cur * hf[i]
        bar_low_eq = cur * lf[i]
        bar_close_eq = cur * cf[i]

        # Trailing-Peak pessimistisch zuerst anheben (schlechteste Reihenfolge)
        if rules.drawdown_type == "trailing":
            peak = max(peak, bar_high_eq)
            dd_floor = peak * (1 - dd)
        else:
            dd_floor = account_size * (1 - dd)
        daily_floor = day_start * (1 - mdl)
        floor = max(dd_floor, daily_floor)

        # Statistik
        peak_profit = max(peak_profit, bar_high_eq / account_size - 1.0)
        max_dd = max(max_dd, 1.0 - bar_low_eq / max(peak, account_size))

        # 1) Breach zuerst pruefen (pessimistisch), dann Target
        if bar_low_eq <= floor or cur <= 0:
            reason = "daily_loss" if daily_floor >= dd_floor else "max_drawdown"
            res.status = "failed"
            res.fail_reason = reason
            res.end_time = times[i]
            res._end_i = i  # type: ignore[attr-defined]
            break
        if bar_high_eq >= target_equity:
            res.status = "passed"
            res.end_time = times[i]
            res._end_i = i  # type: ignore[attr-defined]
            break

        cur = bar_close_eq

    res.trading_days = trading_days
    res.max_drawdown_pct = float(max_dd)
    res.peak_profit_pct = float(peak_profit)
    return res


def evaluate_challenge(equity: pd.DataFrame, rules: PropRules,
                       initial_balance: float,
                       account_size: Optional[float] = None) -> ChallengeResult:
    """Prueft eine Equity-Kurve gegen einen kompletten (ggf. mehrstufigen) Regelsatz."""
    if account_size is None:
        account_size = initial_balance
    if len(equity) == 0:
        return ChallengeResult(rules=rules, account_size=account_size, passed=False)

    cf, lf, hf = _factors(equity, initial_balance)
    times = list(equity.index)

    phases: List[PhaseResult] = []
    start_i = 0
    all_passed = True
    total_days = 0

    for p, target in enumerate(rules.profit_targets):
        phase = _evaluate_phase(cf, lf, hf, times, start_i, target, rules, account_size)
        phase.index = p
        phases.append(phase)
        total_days += phase.trading_days
        if phase.status != "passed":
            all_passed = False
            break
        # Naechste Phase startet frisch am Folge-Bar
        start_i = getattr(phase, "_end_i", len(times) - 1) + 1
        if start_i >= len(times):
            # Keine Daten mehr fuer die naechste Phase
            if p < len(rules.profit_targets) - 1:
                all_passed = False
            break

    passed = all_passed and len(phases) == rules.steps and \
        all(ph.status == "passed" for ph in phases)

    result = ChallengeResult(
        rules=rules,
        account_size=account_size,
        passed=passed,
        phases=phases,
        total_trading_days=total_days,
    )
    if rules.min_trading_days and total_days < rules.min_trading_days and passed:
        result.passed = False
    return result


def evaluate_all_presets(equity: pd.DataFrame, initial_balance: float,
                         account_size: Optional[float] = None
                         ) -> Dict[str, ChallengeResult]:
    """Wertet die Equity-Kurve gegen alle bekannten Kraken-Presets aus."""
    return {
        key: evaluate_challenge(equity, rules, initial_balance, account_size)
        for key, rules in PRESETS.items()
    }
