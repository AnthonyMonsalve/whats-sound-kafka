# Thin Kafka producer wrapper.
from __future__ import annotations
import json
from confluent_kafka import Producer
from src.config import build_kafka_config, settings

class KafkaNowPlayingProducer:
    """Encapsulates a confluent-kafka Producer with simple send method."""
    def __init__(self) -> None:
        self._producer = Producer(build_kafka_config())

    def send(self, payload: dict) -> None:
        """Send a JSON payload with machine_key as message key."""
        self._producer.produce(
            settings.topic,
            key=settings.machine_key,
            value=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        )
        # Drive delivery callbacks (non-blocking tick).
        self._producer.poll(0)

    def flush(self, timeout: float = 5.0) -> None:
        self._producer.flush(timeout)
