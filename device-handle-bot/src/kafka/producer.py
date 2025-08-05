# Thin Kafka producer wrapper for control messages
from __future__ import annotations
import json
from datetime import datetime, timezone
from confluent_kafka import Producer
from src.config import build_kafka_config, settings

class ControlProducer:
    """Encapsulates Kafka producer for lock/unlock control events."""
    def __init__(self) -> None:
        self._p = Producer(build_kafka_config())

    def send_control(self, action: str, target: str, actor: str) -> None:
        """
        Send a control event to Kafka.

        Schema example:
        {
          "type": "control",
          "action": "lock" | "unlock",
          "target": "all" | "<machineKey>",
          "by": "telegram:<user_id>",
          "ts": "<ISO8601 UTC>"
        }
        """
        payload = {
            "type": "control",
            "action": action,
            "target": target,
            "by": actor,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        self._p.produce(
            settings.topic_control,
            key=target,
            value=json.dumps(payload, ensure_ascii=False).encode("utf-8")
        )
        self._p.poll(0)

    def flush(self, timeout: float = 5.0) -> None:
        self._p.flush(timeout)
