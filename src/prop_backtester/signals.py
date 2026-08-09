"""Live-Signal-Bot: Renko-Reversal-Signale erkennen und nach Telegram schicken.

Ablauf je Durchlauf:
  1. Aktuelle OHLC-Kerzen von Kraken laden (oeffentliche API, ~720 Kerzen genuegen).
  2. Nur **geschlossene** Kerzen verwenden (kein Repainting).
  3. Renko-Bricks bauen, 2-Brick-Reversal-Signale erzeugen, letztes Signal nehmen.
  4. Ist es neu (anderer Zeitstempel als zuletzt gesendet)? -> Telegram-Nachricht.

Der Zustand (zuletzt gesendetes Signal je Paar) liegt in einer kleinen JSON-Datei,
damit dasselbe Signal nicht mehrfach gepingt wird.

Aufruf:
    python -m prop_backtester.signals --config configs/signals.yaml --once
    python -m prop_backtester.signals --config configs/signals.yaml --loop
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from .config import BacktestConfig, config_from_dict
from .renko import build_renko
from .strategy import generate_signals
from . import telegram


@dataclass
class Signal:
    time: pd.Timestamp     # Zeitstempel der ausloesenden (geschlossenen) Kerze
    target: int            # +1 long, -1 short, 0 flat
    trigger_price: float   # Gitter-Level des ausloesenden Bricks
    current_price: float   # letzter Schlusskurs
    brick_size: float
    stop_price: float
    stop_distance: float
    size: float            # empfohlene Positionsgroesse (Basiswert-Einheiten)
    notional: float        # Nominalwert der Position
    # TP-Level: Liste aus (R-Vielfaches, Preis, Bewegung-in-%)
    tp_levels: List[Tuple[float, float, float]] = field(default_factory=list)

    @property
    def side_text(self) -> str:
        return {1: "LONG", -1: "SHORT", 0: "FLAT/EXIT"}[self.target]


def compute_latest_signal(df: pd.DataFrame, cfg: BacktestConfig,
                          drop_last: bool = True) -> Optional[Signal]:
    """Berechnet das juengste Signal aus geschlossenen Kerzen (oder None)."""
    if drop_last and len(df) > 1:
        df = df.iloc[:-1]  # letzte, noch offene Kerze verwerfen
    bricks = build_renko(df, cfg.renko).bricks
    sig = generate_signals(bricks, cfg.strategy)
    if len(sig) == 0:
        return None
    last = sig.iloc[-1]
    target = int(last["target"])
    price = float(last["price"])
    brick = float(last["brick_size"])
    current = float(df["close"].iloc[-1])

    r = cfg.risk
    stop_dist = r.stop_bricks * brick
    side = target if target != 0 else 0
    stop_price = price - side * stop_dist
    if target != 0 and stop_dist > 0:
        size = (cfg.initial_balance * r.risk_per_trade_pct) / stop_dist
        size = min(size, (cfg.initial_balance * r.max_leverage) / price)
    else:
        size = 0.0
    # TP-Level als R-Vielfache der Stop-Distanz (R = Risiko pro Trade)
    tp_levels: List[Tuple[float, float, float]] = []
    if target != 0 and stop_dist > 0:
        for m in r.tp_r_multiples:
            tp_price = price + side * m * stop_dist
            move_pct = (m * stop_dist / price) * 100 if price else 0.0
            tp_levels.append((float(m), float(tp_price), float(move_pct)))
    return Signal(
        time=pd.Timestamp(last["time"]).tz_convert("UTC"),
        target=target, trigger_price=price, current_price=current,
        brick_size=brick, stop_price=stop_price, stop_distance=stop_dist,
        size=size, notional=size * price, tp_levels=tp_levels,
    )


@dataclass
class PendingOrder:
    """Eine im Voraus platzierbare Stop-Order am naechsten Trigger-Level."""

    direction: int         # +1 Buy-Stop (long), -1 Sell-Stop (short)
    trigger: float         # Kurs, bei dem das Reversal ausloest
    distance_pct: float    # Abstand vom aktuellen Kurs
    bricks_needed: int     # wie viele Bricks noch fehlen
    stop_price: float
    stop_distance: float
    size: float
    notional: float
    tp_levels: List[Tuple[float, float, float]] = field(default_factory=list)

    @property
    def order_text(self) -> str:
        return "Buy-Stop" if self.direction == 1 else "Sell-Stop"

    @property
    def side_text(self) -> str:
        return "LONG" if self.direction == 1 else "SHORT"


@dataclass
class LevelPlan:
    """Aktueller Zustand + die daraus folgenden Order-Level."""

    time: pd.Timestamp       # Zeit der letzten geschlossenen Kerze
    current_price: float
    brick_size: float
    anchor: float            # Schlusskurs des letzten Bricks (Gitter-Anker)
    position: int            # aktuell laut Strategie gehaltene Position
    run_dir: int             # Richtung der laufenden Brick-Serie
    run_len: int
    orders: List[PendingOrder] = field(default_factory=list)

    @property
    def fingerprint(self) -> str:
        """Kennung zur Dedup: Position + gerundete Trigger-Level."""
        trig = "/".join(f"{o.direction}@{o.trigger:.4g}" for o in self.orders)
        return f"{self.position}|{trig}"


def _current_brick_size(df: pd.DataFrame, cfg: BacktestConfig) -> float:
    """Brick-Groesse fuer den *naechsten* Brick (aktuelle ATR bzw. fix)."""
    rc = cfg.renko
    if rc.mode == "atr":
        from .renko import wilder_atr
        atr = wilder_atr(df, rc.atr_period)
        return float(atr.iloc[-1]) * rc.atr_multiplier
    if rc.fixed_brick is not None:
        return float(rc.fixed_brick)
    return float(df["close"].iloc[-1]) * float(rc.fixed_brick_pct)


def compute_level_plan(df: pd.DataFrame, cfg: BacktestConfig,
                       drop_last: bool = True) -> Optional[LevelPlan]:
    """Berechnet, bei welchen Kursen das naechste Reversal ausloest.

    Die Renko-Level stehen im Voraus fest: Der naechste Aufwaerts-Brick entsteht
    bei ``Anker + Brick``, der naechste Abwaerts-Brick bei ``Anker - Brick``.
    Fuer ein Signal braucht es ``reversal_bricks`` Bricks in eine Richtung --
    daraus ergibt sich der exakte Trigger-Kurs, an dem eine Stop-Order liegen muss.
    """
    if drop_last and len(df) > 1:
        df = df.iloc[:-1]
    bricks = build_renko(df, cfg.renko).bricks
    if len(bricks) == 0:
        return None

    anchor = float(bricks["close"].iloc[-1])
    brick = _current_brick_size(df, cfg)
    if not np.isfinite(brick) or brick <= 0:
        return None

    # Laufende Brick-Serie bestimmen
    dirs = bricks["direction"].to_numpy()
    run_dir = int(dirs[-1])
    run_len = 1
    for d in dirs[-2::-1]:
        if int(d) == run_dir:
            run_len += 1
        else:
            break

    sig = generate_signals(bricks, cfg.strategy)
    position = int(sig["target"].iloc[-1]) if len(sig) else 0
    current = float(df["close"].iloc[-1])
    n = cfg.strategy.reversal_bricks
    r = cfg.risk

    def make_order(direction: int) -> Optional[PendingOrder]:
        same = run_len if run_dir == direction else 0
        needed = max(1, n - same)
        trigger = anchor + direction * needed * brick
        # Wuerde dieses Signal die Position ueberhaupt aendern?
        target = direction
        if direction == 1 and not cfg.strategy.allow_long:
            target = 0 if position == -1 else position
        if direction == -1 and not cfg.strategy.allow_short:
            target = 0 if position == 1 else position
        if target == position:
            return None
        stop_dist = r.stop_bricks * brick
        side = target if target != 0 else 0
        stop_price = trigger - side * stop_dist
        if target != 0 and stop_dist > 0:
            size = (cfg.initial_balance * r.risk_per_trade_pct) / stop_dist
            size = min(size, (cfg.initial_balance * r.max_leverage) / trigger)
        else:
            size = 0.0
        tps: List[Tuple[float, float, float]] = []
        if target != 0 and stop_dist > 0:
            for m in r.tp_r_multiples:
                tps.append((float(m), float(trigger + side * m * stop_dist),
                            float(m * stop_dist / trigger * 100)))
        return PendingOrder(
            direction=direction, trigger=float(trigger),
            distance_pct=float((trigger - current) / current * 100),
            bricks_needed=int(needed), stop_price=float(stop_price),
            stop_distance=float(stop_dist), size=float(size),
            notional=float(size * trigger), tp_levels=tps,
        )

    orders = [o for o in (make_order(1), make_order(-1)) if o is not None]
    return LevelPlan(
        time=pd.Timestamp(df.index[-1]).tz_convert("UTC"), current_price=current,
        brick_size=brick, anchor=anchor, position=position,
        run_dir=run_dir, run_len=run_len, orders=orders,
    )


def format_levels_message(pair: str, interval_minutes: int, plan: LevelPlan,
                          cfg: BacktestConfig) -> str:
    """Telegram-Nachricht mit vorab platzierbaren Orders."""
    pos_txt = {1: "🟢 LONG", -1: "🔴 SHORT", 0: "⚪️ keine Position"}[plan.position]
    lines = [
        f"📍 <b>{pair}</b> ({interval_minutes}m) — Order-Level",
        f"Position: {pos_txt}  ·  Kurs {plan.current_price:,.2f}",
        f"Brick {plan.brick_size:,.2f} · Anker {plan.anchor:,.2f} · "
        f"Serie {plan.run_len}× {'▲' if plan.run_dir == 1 else '▼'}",
        "",
    ]
    if not plan.orders:
        lines.append("Keine Order nötig — Position passt zur Lage.")
    for o in plan.orders:
        arrow = "🟢⬆️" if o.direction == 1 else "🔴⬇️"
        lines.append(
            f"{arrow} <b>{o.order_text} {o.trigger:,.2f}</b> "
            f"({o.distance_pct:+.2f}% · {o.bricks_needed} Brick"
            f"{'s' if o.bricks_needed > 1 else ''})"
        )
        lines.append(f"    🛑 SL {o.stop_price:,.2f}")
        for i, (m, tp, pct) in enumerate(o.tp_levels, start=1):
            lines.append(f"    🎯 TP{i} ({m:g}R) {tp:,.2f}")
        lines.append(f"    Size ≈ {o.size:.4g} (Nominal {o.notional:,.0f})")
    lines += [
        "",
        "ℹ️ Orders <b>vorab</b> platzieren — der Edge hängt am Fill auf dem Level.",
        f"⏱ {plan.time.strftime('%Y-%m-%d %H:%M UTC')} · Level verschieben sich mit der ATR",
    ]
    return "\n".join(lines)


def format_message(pair: str, interval_minutes: int, sig: Signal,
                   cfg: BacktestConfig) -> str:
    """Baut die Telegram-Nachricht (HTML) -- auf einen Blick handelbar."""
    arrow = {1: "🟢⬆️", -1: "🔴⬇️", 0: "⚪️➡️"}[sig.target]
    action = {
        1: "Auf <b>LONG</b> drehen (Short schließen, Long eröffnen)",
        -1: "Auf <b>SHORT</b> drehen (Long schließen, Short eröffnen)",
        0: "Position <b>schließen</b> (flat gehen)",
    }[sig.target]
    stop_pct = (sig.stop_distance / sig.trigger_price * 100) if sig.trigger_price else 0
    risk_amt = cfg.initial_balance * cfg.risk.risk_per_trade_pct
    lines = [
        f"{arrow} <b>{sig.side_text}-Signal</b> — {pair} ({interval_minutes}m)",
        "Renko-Reversal: 2 Bricks gedreht",
        "",
        f"▸ Aktion: {action}",
        f"▸ Einstieg (Trigger): <b>{sig.trigger_price:,.2f}</b>",
        f"▸ Aktueller Kurs: {sig.current_price:,.2f}",
        f"▸ Brick (ATR): {sig.brick_size:,.2f}",
    ]
    if sig.target != 0:
        lines.append(f"🛑 SL (2 Bricks): <b>{sig.stop_price:,.2f}</b>  (Risiko ≈{stop_pct:.2f}%)")
        for i, (m, tp_price, move_pct) in enumerate(sig.tp_levels, start=1):
            lines.append(f"🎯 TP{i} ({m:g}R): <b>{tp_price:,.2f}</b>  (+{move_pct:.2f}%)")
        lines += [
            f"▸ Risiko {cfg.risk.risk_per_trade_pct*100:g}% von {cfg.initial_balance:,.0f} "
            f"= {risk_amt:,.0f} → Size ≈ <b>{sig.size:.4g}</b> "
            f"(Nominal {sig.notional:,.0f})",
            "ℹ️ Kern-Ausstieg = Gegensignal (Reversal); TP = optionale Teilmitnahme",
        ]
    lines += ["", f"⏱ {sig.time.strftime('%Y-%m-%d %H:%M UTC')} · geschlossene Kerze"]
    return "\n".join(lines)


# --- Zustand ---------------------------------------------------------------
def _load_state(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def _save_state(path: str, state: dict) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)


def _is_new(state: dict, pair: str, sig: Signal) -> bool:
    prev = state.get(pair)
    key = f"{sig.time.isoformat()}|{sig.target}"
    return prev != key


def _mark_sent(state: dict, pair: str, sig: Signal) -> None:
    state[pair] = f"{sig.time.isoformat()}|{sig.target}"


# --- Runner ----------------------------------------------------------------
def check_pair(pair: str, cfg: BacktestConfig, interval_minutes: int,
               token: str, chat_id, state: dict, state_path: str,
               fetch_fn=None, send_fn=None, verbose: bool = True,
               mode: str = "levels"):
    """Prueft ein Paar einmal und sendet bei Neuigkeit.

    ``mode="levels"``  -- kommende Trigger-Level (fuer vorab platzierte Orders).
                          Empfohlen: nur so ist der Backtest-Edge erreichbar.
    ``mode="signals"`` -- Meldung erst nach ausgeloestem Reversal (Bestaetigung).
    """
    from . import data as data_mod
    fetch = fetch_fn or data_mod.fetch_kraken_ohlc
    send = send_fn or telegram.send_message

    df = fetch(pair, interval_minutes=interval_minutes)

    if mode == "levels":
        plan = compute_level_plan(df, cfg)
        if plan is None:
            if verbose:
                print(f"[{pair}] noch keine Level (zu wenige Daten).")
            return None
        key = f"levels|{plan.fingerprint}"
        if state.get(pair) == key:
            if verbose:
                print(f"[{pair}] Level unveraendert — nichts gesendet.")
            return None
        send(token, chat_id, format_levels_message(pair, interval_minutes, plan, cfg))
        state[pair] = key
        _save_state(state_path, state)
        if verbose:
            trig = ", ".join(f"{o.order_text} {o.trigger:.2f}" for o in plan.orders)
            print(f"[{pair}] Level gesendet: {trig or 'keine'}")
        return plan

    sig = compute_latest_signal(df, cfg)
    if sig is None:
        if verbose:
            print(f"[{pair}] noch kein Signal.")
        return None
    if not _is_new(state, pair, sig):
        if verbose:
            print(f"[{pair}] {sig.side_text} @ {sig.time} — bereits gesendet.")
        return None
    msg = format_message(pair, interval_minutes, sig, cfg)
    send(token, chat_id, msg)
    _mark_sent(state, pair, sig)
    _save_state(state_path, state)
    if verbose:
        print(f"[{pair}] NEU: {sig.side_text} @ {sig.time} — gesendet.")
    return sig


def run_once(cfg: BacktestConfig, pairs, interval_minutes, token, chat_id,
             state_path, **kw) -> None:
    state = _load_state(state_path)
    for pair in pairs:
        try:
            check_pair(pair, cfg, interval_minutes, token, chat_id, state, state_path, **kw)
        except Exception as exc:  # noqa: BLE001
            print(f"[{pair}] Fehler: {exc}", file=sys.stderr)


def run_loop(cfg: BacktestConfig, pairs, interval_minutes, token, chat_id,
             state_path, poll_seconds=None, **kw) -> None:
    """Endlosschleife: kurz nach jedem Kerzenschluss pruefen."""
    period = poll_seconds or interval_minutes * 60
    print(f"Signal-Bot laeuft. Paare: {', '.join(pairs)} · Intervall {interval_minutes}m. "
          f"Strg+C zum Beenden.")
    while True:
        run_once(cfg, pairs, interval_minutes, token, chat_id, state_path, **kw)
        # bis kurz nach dem naechsten Kerzenschluss schlafen (+20s Puffer)
        now = time.time()
        sleep_s = period - (now % period) + 20
        time.sleep(sleep_s)


# --- Config & CLI ----------------------------------------------------------
def _resolve_secret(value: Optional[str], env_name: str) -> Optional[str]:
    """Nimmt den Wert, oder ${VAR}, oder die Umgebungsvariable env_name."""
    if value and value.startswith("${") and value.endswith("}"):
        return os.environ.get(value[2:-1])
    if value:
        return value
    return os.environ.get(env_name)


def load_signal_config(path: str):
    import yaml
    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    cfg = config_from_dict(raw)
    tg = raw.get("telegram") or {}
    token = _resolve_secret(tg.get("token"), "TELEGRAM_TOKEN")
    chat_id = tg.get("chat_id") or os.environ.get("TELEGRAM_CHAT_ID")
    pairs = raw.get("pairs") or ["XBTUSD"]
    interval = int(raw.get("interval_minutes", 60))
    return cfg, pairs, interval, token, chat_id


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="prop_backtester.signals",
        description="Live-Renko-Reversal-Signale nach Telegram")
    p.add_argument("--config", required=True, help="Signal-Config (YAML)")
    p.add_argument("--once", action="store_true", help="einmal pruefen und beenden")
    p.add_argument("--loop", action="store_true", help="dauerhaft laufen")
    p.add_argument("--state", default="signal_state.json", help="Zustandsdatei")
    p.add_argument("--pair", help="einzelnes Paar erzwingen (statt Config-Liste)")
    p.add_argument("--mode", choices=["levels", "signals"], default="levels",
                   help="levels = kommende Order-Level im Voraus (empfohlen); "
                        "signals = Meldung nach ausgeloestem Reversal")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    cfg, pairs, interval, token, chat_id = load_signal_config(args.config)
    if args.pair:
        pairs = [args.pair]
    if not token or not chat_id:
        raise SystemExit("Telegram-Token/Chat-ID fehlen (Config oder Umgebungsvariablen "
                         "TELEGRAM_TOKEN / TELEGRAM_CHAT_ID).")
    if args.loop:
        run_loop(cfg, pairs, interval, token, chat_id, args.state, mode=args.mode)
    else:
        run_once(cfg, pairs, interval, token, chat_id, args.state, mode=args.mode)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
