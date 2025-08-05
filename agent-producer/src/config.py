# Loads and validates environment variables; builds Kafka config.
from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    brokers: str = os.getenv("KAFKA_BROKERS", "localhost:9092")
    topic: str = os.getenv("TOPIC", "pc.activity.media")
    machine_key: str = os.getenv("MACHINE_KEY") or os.environ.get("COMPUTERNAME") or "pc"

    poll_interval_sec: float = float(os.getenv("POLL_INTERVAL_SEC", "2"))
    enable_idempotence: bool = os.getenv("ENABLE_IDEMPOTENCE", "true").lower() != "false"

    # Optional security
    security_protocol: str | None = os.getenv("KAFKA_SECURITY_PROTOCOL")     # e.g., SASL_SSL
    sasl_mechanism: str | None     = os.getenv("KAFKA_SASL_MECHANISM")       # e.g., PLAIN
    sasl_username: str | None      = os.getenv("KAFKA_SASL_USERNAME")
    sasl_password: str | None      = os.getenv("KAFKA_SASL_PASSWORD")
    ssl_ca_location: str | None    = os.getenv("KAFKA_SSL_CA_LOCATION")

settings = Settings()

def build_kafka_config() -> dict:
    """Build confluent-kafka Producer config from settings."""
    cfg = {
        "bootstrap.servers": settings.brokers,
        "client.id": "pc-agent-media-py",
        "compression.type": "lz4",
        "socket.keepalive.enable": True,
        "linger.ms": 10,
        "retries": 5,
        "acks": "all",
        "enable.idempotence": settings.enable_idempotence,
    }
    if settings.security_protocol: cfg["security.protocol"] = settings.security_protocol
    if settings.sasl_mechanism:   cfg["sasl.mechanism"]     = settings.sasl_mechanism
    if settings.sasl_username:    cfg["sasl.username"]      = settings.sasl_username
    if settings.sasl_password:    cfg["sasl.password"]      = settings.sasl_password
    if settings.ssl_ca_location:  cfg["ssl.ca.location"]    = settings.ssl_ca_location
    return cfg
