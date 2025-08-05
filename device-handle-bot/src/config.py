# Load environment & provide settings and Kafka config builder
from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    # Kafka
    brokers: str = os.getenv("KAFKA_BROKERS", "localhost:9092")
    topic_control: str = os.getenv("KAFKA_TOPIC_CONTROL", "pc.activity.control")
    machine_target: str = os.getenv("MACHINE_TARGET", "all")

    # Optional security
    security_protocol: str | None = os.getenv("KAFKA_SECURITY_PROTOCOL")
    sasl_mechanism: str | None     = os.getenv("KAFKA_SASL_MECHANISM")
    sasl_username: str | None      = os.getenv("KAFKA_SASL_USERNAME")
    sasl_password: str | None      = os.getenv("KAFKA_SASL_PASSWORD")
    ssl_ca_location: str | None    = os.getenv("KAFKA_SSL_CA_LOCATION")

    # Telegram
    bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    allowed_user_ids: list[int] = tuple(
        int(x) for x in os.getenv("ALLOWED_USER_IDS", "").split(",") if x.strip().isdigit()
    )
    bot_title: str = os.getenv("BOT_TITLE", "[AdminPC]")

    def validate(self) -> None:
        if not self.bot_token:
            raise SystemExit("Set TELEGRAM_BOT_TOKEN in .env")

settings = Settings()
settings.validate()

def build_kafka_config() -> dict:
    """Build confluent-kafka Producer config from settings."""
    cfg = {
        "bootstrap.servers": settings.brokers,
        "client.id": "telegram-control-bot",
        "compression.type": "lz4",
        "socket.keepalive.enable": True,
        "linger.ms": 5,
        "acks": "all",
        "retries": 5,
        "enable.idempotence": True,
    }
    if settings.security_protocol: cfg["security.protocol"] = settings.security_protocol
    if settings.sasl_mechanism:   cfg["sasl.mechanism"]     = settings.sasl_mechanism
    if settings.sasl_username:    cfg["sasl.username"]      = settings.sasl_username
    if settings.sasl_password:    cfg["sasl.password"]      = settings.sasl_password
    if settings.ssl_ca_location:  cfg["ssl.ca.location"]    = settings.ssl_ca_location
    return cfg
