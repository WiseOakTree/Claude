import numpy as np
import pandas as pd

from prop_backtester import telegram
from prop_backtester.config import BacktestConfig
from prop_backtester import signals
from prop_backtester import data


class _FakeResp:
    def __init__(self, ok=True):
        self._ok = ok
    def raise_for_status(self):
        pass
    def json(self):
        return {"ok": self._ok, "result": {}}


def test_telegram_send_builds_payload():
    captured = {}
    def fake_post(url, payload, timeout):
        captured["url"] = url
        captured["payload"] = payload
        return _FakeResp(ok=True)
    ok = telegram.send_message("TOK", 42, "hallo", request_fn=fake_post)
    assert ok
    assert captured["url"].endswith("/botTOK/sendMessage")
    assert captured["payload"]["chat_id"] == 42
    assert captured["payload"]["text"] == "hallo"


def test_compute_latest_signal_detects_reversal():
    # Kraeftiger Auf- dann Abschwung -> es muss ein Signal geben
    up = np.linspace(100, 140, 200)
    down = np.linspace(140, 100, 200)
    prices = np.concatenate([up, down])
    idx = pd.date_range("2025-01-01", periods=len(prices), freq="1h", tz="UTC")
    df = pd.DataFrame({"open": prices, "high": prices * 1.001, "low": prices * 0.999,
                       "close": prices, "volume": np.ones_like(prices)}, index=idx)
    cfg = BacktestConfig()
    cfg.renko.mode = "fixed"; cfg.renko.fixed_brick = 2.0
    sig = signals.compute_latest_signal(df, cfg)
    assert sig is not None
    assert sig.target in (-1, 1)
    assert sig.size > 0
    assert sig.stop_distance > 0


def test_dedup_state_prevents_resend():
    df = data.generate_synthetic(bars=1500, seed=3)
    cfg = BacktestConfig()
    sig = signals.compute_latest_signal(df, cfg)
    assert sig is not None
    state = {}
    assert signals._is_new(state, "XBTUSD", sig)
    signals._mark_sent(state, "XBTUSD", sig)
    assert not signals._is_new(state, "XBTUSD", sig)


def test_check_pair_sends_once_then_dedups(tmp_path):
    df = data.generate_synthetic(bars=1500, seed=4)
    cfg = BacktestConfig()
    sent = []
    fetch = lambda pair, interval_minutes=60: df
    send = lambda token, chat, text: sent.append(text)
    state = {}
    sp = str(tmp_path / "state.json")
    s1 = signals.check_pair("XBTUSD", cfg, 60, "T", 1, state, sp,
                            fetch_fn=fetch, send_fn=send, verbose=False, mode="signals")
    s2 = signals.check_pair("XBTUSD", cfg, 60, "T", 1, state, sp,
                            fetch_fn=fetch, send_fn=send, verbose=False, mode="signals")
    assert s1 is not None
    assert s2 is None           # zweiter Lauf: kein Doppel-Ping
    assert len(sent) == 1
    assert "Signal" in sent[0]


def test_format_message_contains_key_fields():
    df = data.generate_synthetic(bars=1500, seed=5)
    cfg = BacktestConfig()
    sig = signals.compute_latest_signal(df, cfg)
    msg = signals.format_message("XBTUSD", 60, sig, cfg)
    assert "XBTUSD" in msg
    assert "UTC" in msg
    if sig.target != 0:
        assert "SL" in msg and "TP1" in msg


def test_tp_levels_direction_and_count():
    df = data.generate_synthetic(bars=1500, seed=5)
    cfg = BacktestConfig()
    cfg.risk.tp_r_multiples = [2.0, 4.0]
    sig = signals.compute_latest_signal(df, cfg)
    assert sig is not None and sig.target != 0
    assert len(sig.tp_levels) == 2
    # TP liegt in Handelsrichtung, SL entgegengesetzt
    for m, tp_price, pct in sig.tp_levels:
        if sig.target == 1:
            assert tp_price > sig.trigger_price and sig.stop_price < sig.trigger_price
        else:
            assert tp_price < sig.trigger_price and sig.stop_price > sig.trigger_price
    # 4R doppelt so weit wie 2R
    r2 = abs(sig.tp_levels[0][1] - sig.trigger_price)
    r4 = abs(sig.tp_levels[1][1] - sig.trigger_price)
    assert abs(r4 - 2 * r2) < 1e-6


def test_empty_tp_multiples_no_tp():
    df = data.generate_synthetic(bars=1500, seed=5)
    cfg = BacktestConfig()
    cfg.risk.tp_r_multiples = []
    sig = signals.compute_latest_signal(df, cfg)
    assert sig.tp_levels == []


def test_resolve_secret_env(monkeypatch):
    monkeypatch.setenv("MY_TOK", "secret123")
    assert signals._resolve_secret("${MY_TOK}", "X") == "secret123"
    assert signals._resolve_secret("direct", "X") == "direct"
    monkeypatch.setenv("FALLBACK", "fb")
    assert signals._resolve_secret(None, "FALLBACK") == "fb"


# --- Levels-Modus: vorab platzierbare Orders --------------------------------
def _ramp_df(prices):
    idx = pd.date_range("2025-01-01", periods=len(prices), freq="1h", tz="UTC")
    p = np.asarray(prices, float)
    return pd.DataFrame({"open": p, "high": p, "low": p, "close": p,
                         "volume": np.ones_like(p)}, index=idx)


def _fixed_cfg(brick=1.0):
    cfg = BacktestConfig()
    cfg.renko.mode = "fixed"
    cfg.renko.fixed_brick = brick
    cfg.renko.fixed_brick_pct = None
    return cfg


def test_level_plan_trigger_math():
    # Aufwaertslauf -> Position long; Short-Trigger muss 2 Bricks unter dem Anker liegen
    df = _ramp_df(list(range(100, 121)))
    cfg = _fixed_cfg(1.0)
    plan = signals.compute_level_plan(df, cfg, drop_last=False)
    assert plan is not None
    assert plan.position == 1 and plan.run_dir == 1
    shorts = [o for o in plan.orders if o.direction == -1]
    assert len(shorts) == 1
    # 2 Gegen-Bricks noetig -> Anker - 2 * Brick
    assert abs(shorts[0].trigger - (plan.anchor - 2 * cfg.renko.fixed_brick)) < 1e-9
    assert shorts[0].bricks_needed == 2
    # keine Long-Order, da bereits long
    assert all(o.direction != 1 for o in plan.orders)


def test_level_plan_pending_reversal_needs_one_brick():
    # Auf, dann genau 1 Gegen-Brick -> Short-Trigger nur noch 1 Brick entfernt
    df = _ramp_df([100, 101, 102, 103, 104, 105, 104])
    cfg = _fixed_cfg(1.0)
    plan = signals.compute_level_plan(df, cfg, drop_last=False)
    assert plan.run_dir == -1 and plan.run_len == 1
    shorts = [o for o in plan.orders if o.direction == -1]
    assert shorts and shorts[0].bricks_needed == 1
    assert abs(shorts[0].trigger - (plan.anchor - 1.0)) < 1e-9


def test_level_plan_stop_and_tp_orientation():
    df = _ramp_df(list(range(100, 121)))
    cfg = _fixed_cfg(1.0)
    plan = signals.compute_level_plan(df, cfg, drop_last=False)
    o = [x for x in plan.orders if x.direction == -1][0]
    assert o.stop_price > o.trigger            # Short: SL oberhalb
    assert all(tp < o.trigger for _, tp, _ in o.tp_levels)  # TPs unterhalb
    assert o.size > 0


def test_levels_message_and_dedup(tmp_path):
    df = data.generate_synthetic(bars=1200, seed=11)
    cfg = BacktestConfig()
    sent = []
    fetch = lambda pair, interval_minutes=60: df
    send = lambda token, chat, text: sent.append(text)
    state, sp = {}, str(tmp_path / "s.json")
    p1 = signals.check_pair("XBTUSD", cfg, 60, "T", 1, state, sp,
                            fetch_fn=fetch, send_fn=send, verbose=False, mode="levels")
    p2 = signals.check_pair("XBTUSD", cfg, 60, "T", 1, state, sp,
                            fetch_fn=fetch, send_fn=send, verbose=False, mode="levels")
    assert p1 is not None and p2 is None      # unveraenderte Level -> kein Spam
    assert len(sent) == 1
    assert "Order-Level" in sent[0] and "Stop" in sent[0]
