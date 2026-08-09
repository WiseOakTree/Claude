"""Telegram-Versand fuer Live-Signale.

Nutzt die Telegram-Bot-API (``sendMessage``). Du brauchst:
  1. Einen Bot-Token von @BotFather (in Telegram: /newbot).
  2. Deine Chat-ID -- z.B. schreibe deinem Bot eine Nachricht und rufe
     https://api.telegram.org/bot<TOKEN>/getUpdates auf; die ``chat.id`` steht drin.
     (Hilfsfunktion ``get_chat_id`` unten.)

Der HTTP-Aufruf ist injizierbar (``request_fn``) -> ohne Netzwerk testbar.
"""

from __future__ import annotations

from typing import Callable, Optional

API = "https://api.telegram.org"


def _default_post(url: str, payload: dict, timeout: float):
    import requests
    return requests.post(url, json=payload, timeout=timeout)


def send_message(token: str, chat_id, text: str, parse_mode: str = "HTML",
                 disable_preview: bool = True, timeout: float = 20.0,
                 request_fn: Optional[Callable] = None) -> bool:
    """Sendet eine Nachricht an einen Telegram-Chat. Gibt True bei Erfolg."""
    post = request_fn or _default_post
    url = f"{API}/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_preview,
    }
    resp = post(url, payload, timeout)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok", False):
        raise RuntimeError(f"Telegram-Fehler: {data}")
    return True


def get_chat_id(token: str, timeout: float = 20.0,
                request_fn: Optional[Callable] = None) -> Optional[int]:
    """Liest die Chat-ID aus den letzten Updates (schreibe dem Bot vorher etwas)."""
    import requests
    get = request_fn or (lambda url, t: requests.get(url, timeout=t))
    url = f"{API}/bot{token}/getUpdates"
    data = get(url, timeout).json()
    for update in reversed(data.get("result", [])):
        msg = update.get("message") or update.get("channel_post")
        if msg and "chat" in msg:
            return msg["chat"]["id"]
    return None
