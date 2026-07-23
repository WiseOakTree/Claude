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
               fetch_fn=None, send_fn=None, verbose: bool = True) -> Optional[Signal]:
    """Prueft ein Paar einmal; sendet bei neuem Signal. Gibt das Signal zurueck."""
    from . import data as data_mod
    fetch = fetch_fn or data_mod.fetch_kraken_ohlc
    send = send_fn or telegram.send_message

    df = fetch(pair, interval_minutes=interval_minutes)
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
        run_loop(cfg, pairs, interval, token, chat_id, args.state)
    else:
        run_once(cfg, pairs, interval, token, chat_id, args.state)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
