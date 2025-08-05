# Loads and validates environment variables
from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    # Kafka
    brokers: str = os.getenv("KAFKA_BROKERS", "localhost:9092")
    topic: str = os.getenv("TOPIC", "pc.activity.media")
    group_id: str = os.getenv("GROUP_ID", "pc-media-telegram-bot")

    # Telegram
    bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN") or ""
    chat_id: str = os.getenv("TELEGRAM_CHAT_ID") or ""
    prefix: str = os.getenv("BOT_PREFIX", "[NowPlaying]")

    # Consumer
    auto_offset_reset: str = os.getenv("AUTO_OFFSET_RESET", "latest")

    def validate(self) -> None:
        if not self.bot_token or not self.chat_id:
            raise SystemExit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")

settings = Settings()
settings.validate()
