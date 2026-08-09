"""Kennzahlen, Textbericht und optionaler Equity-Plot."""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd

from .engine import BacktestResult
from .prop import ChallengeResult


def compute_metrics(result: BacktestResult) -> dict:
    """Berechnet Standard-Kennzahlen aus einem Backtest-Ergebnis."""
    trades = result.trades
    eq = result.equity["equity_close"]
    ret_pct = result.final_balance / result.initial_balance - 1.0

    # Max Drawdown auf der (konservativen) Intrabar-Tief-Kurve
    low = result.equity["equity_low"]
    running_peak = eq.cummax().clip(lower=result.initial_balance)
    dd = 1.0 - low / running_peak.where(running_peak > 0, np.nan)
    max_dd = float(np.nanmax(dd.to_numpy())) if len(dd) else 0.0

    n_trades = len(trades)
    if n_trades:
        wins = trades[trades["pnl"] > 0]
        losses = trades[trades["pnl"] <= 0]
        win_rate = len(wins) / n_trades
        gross_win = float(wins["pnl"].sum())
        gross_loss = float(-losses["pnl"].sum())
        profit_factor = (gross_win / gross_loss) if gross_loss > 0 else float("inf")
        avg_win = float(wins["pnl"].mean()) if len(wins) else 0.0
        avg_loss = float(losses["pnl"].mean()) if len(losses) else 0.0
    else:
        win_rate = profit_factor = avg_win = avg_loss = 0.0

    return {
        "initial_balance": result.initial_balance,
        "final_balance": result.final_balance,
        "return_pct": ret_pct,
        "max_drawdown_pct": max_dd,
        "num_trades": n_trades,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
    }


def _fmt_pct(x: float) -> str:
    if x == float("inf"):
        return "inf"
    return f"{x * 100:.2f}%"


def format_report(result: BacktestResult, metrics: dict,
                  challenges: Dict[str, ChallengeResult]) -> str:
    """Erzeugt einen lesbaren Textbericht fuer die Konsole."""
    lines = []
    lines.append("=" * 62)
    lines.append(" KRYPTO PROP BACKTEST -- ERGEBNIS")
    lines.append("=" * 62)
    lines.append("")
    lines.append("Performance:")
    lines.append(f"  Startkapital     : {metrics['initial_balance']:,.2f}")
    lines.append(f"  Endkapital       : {metrics['final_balance']:,.2f}")
    lines.append(f"  Rendite          : {_fmt_pct(metrics['return_pct'])}")
    lines.append(f"  Max Drawdown     : {_fmt_pct(metrics['max_drawdown_pct'])}")
    lines.append(f"  Trades           : {metrics['num_trades']}")
    lines.append(f"  Trefferquote     : {_fmt_pct(metrics['win_rate'])}")
    lines.append(f"  Profit Factor    : {metrics['profit_factor']:.2f}")
    lines.append(f"  Ø Gewinn / Verlust: {metrics['avg_win']:,.2f} / {metrics['avg_loss']:,.2f}")
    lines.append("")
    lines.append("Kraken-Prop-Challenges (realized + unrealized, Daily-Reset 00:30 UTC):")
    for key, ch in challenges.items():
        mark = "PASS" if ch.passed else "FAIL"
        lines.append(f"  [{mark}] {ch.rules.name}")
        for ph in ch.phases:
            detail = ph.status.upper()
            if ph.fail_reason:
                detail += f" ({ph.fail_reason})"
            when = "" if ph.end_time is None else f" @ {ph.end_time.date()}"
            lines.append(
                f"        Phase {ph.index + 1} [Ziel {_fmt_pct(ph.target_pct)}]: "
                f"{detail}{when} | maxDD {_fmt_pct(ph.max_drawdown_pct)}, "
                f"Peak {_fmt_pct(ph.peak_profit_pct)}, Tage {ph.trading_days}"
            )
    lines.append("")
    lines.append("Hinweis: konservative Intrabar-Bewertung. Prop-Regeln vor Kauf")
    lines.append("mit der aktuellen Kraken-Seite abgleichen (siehe README).")
    lines.append("=" * 62)
    return "\n".join(lines)


def format_sweep(sweep, top: int = 12) -> str:
    """Formatiert das Sweep-Ergebnis als Ranking-Tabelle."""
    from .prop import PRESETS

    table = sweep.table
    param_cols = [c for c in table.columns
                  if c not in ("pass_rate", "median_return", "median_maxdd",
                               "worst_maxdd", "n_scenarios")]
    lines = []
    lines.append("=" * 78)
    lines.append(" PARAMETER-SWEEP -- ROBUSTHEIT ueber Szenarien")
    lines.append("=" * 78)
    lines.append(f" Preset   : {PRESETS[sweep.preset].name}")
    lines.append(f" Szenarien: {sweep.n_scenarios}  (Pass-Rate = Anteil bestandener Versuche)")
    lines.append("-" * 78)

    header = "  ".join(f"{c.split('.')[-1]:>12s}" for c in param_cols)
    lines.append(f" {header}   pass%   medRet%   medDD%   worstDD%")
    lines.append("-" * 78)
    for _, r in table.head(top).iterrows():
        params = "  ".join(f"{r[c]:>12.4g}" for c in param_cols)
        lines.append(
            f" {params}   {r['pass_rate']*100:5.1f}  {r['median_return']*100:7.2f}  "
            f"{r['median_maxdd']*100:6.2f}  {r['worst_maxdd']*100:7.2f}"
        )
    lines.append("-" * 78)
    best = sweep.best
    best_desc = ", ".join(f"{c.split('.')[-1]}={best[c]:g}" for c in param_cols)
    lines.append(f" BESTE ROBUSTE EINSTELLUNG: {best_desc}")
    lines.append(f"   -> Pass-Rate {best['pass_rate']*100:.1f}%, "
                 f"Median-Rendite {best['median_return']*100:.2f}%, "
                 f"Worst-Drawdown {best['worst_maxdd']*100:.2f}%")
    lines.append("=" * 78)
    return "\n".join(lines)


def save_plot(result: BacktestResult, path: str) -> bool:
    """Speichert Equity-Kurve + Drawdown als PNG. Gibt False zurueck ohne matplotlib."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return False

    eq = result.equity["equity_close"]
    peak = eq.cummax().clip(lower=result.initial_balance)
    dd = (eq / peak - 1.0) * 100

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True,
                                   gridspec_kw={"height_ratios": [3, 1]})
    ax1.plot(eq.index, eq.values, color="#1f77b4", linewidth=1.2)
    ax1.axhline(result.initial_balance, color="gray", linestyle="--", linewidth=0.8)
    ax1.set_ylabel("Equity")
    ax1.set_title("Equity-Kurve")
    ax1.grid(alpha=0.3)

    ax2.fill_between(dd.index, dd.values, 0, color="#d62728", alpha=0.4)
    ax2.set_ylabel("Drawdown %")
    ax2.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return True
