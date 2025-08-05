# Minimal Telegram client for sendMessage (HTML mode)
from __future__ import annotations
import requests

class TelegramClient:
    """Tiny wrapper around Telegram Bot API for sendMessage."""
    def __init__(self, bot_token: str, chat_id: str) -> None:
        self._chat_id = chat_id
        self._url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def send_text_html(self, html: str) -> None:
        try:
            resp = requests.post(self._url, json={
                "chat_id": self._chat_id,
                "text": html,
                "parse_mode": "HTML",
                # "disable_web_page_preview": True,
                # "disable_notification": True,
            }, timeout=10)
            resp.raise_for_status()
        except Exception as exc:
            print(f"[warn] telegram send failed: {exc}")
