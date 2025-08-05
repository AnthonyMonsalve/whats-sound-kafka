# Application wiring: builds components and runs the loop
from __future__ import annotations
from src.config import settings
from src.kafka.consumer import KafkaNowPlayingConsumer
from src.telegram.client import TelegramClient
from src.telegram.formatters import format_message_html

def run() -> None:
    tg = TelegramClient(settings.bot_token, settings.chat_id)
    consumer = KafkaNowPlayingConsumer(
        brokers=settings.brokers,
        topic=settings.topic,
        group_id=settings.group_id,
        auto_offset_reset=settings.auto_offset_reset,
    )

    def on_media_change(payload: dict) -> None:
        text = format_message_html(payload, settings.prefix)
        tg.send_text_html(text)
        print(f"[→] {text}")

    consumer.start(on_media_change)
