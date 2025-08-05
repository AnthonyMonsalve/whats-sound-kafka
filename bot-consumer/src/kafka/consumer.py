# Kafka consumer wrapper with dedup by signature
from __future__ import annotations
import json
from typing import Callable, Dict, Optional
from confluent_kafka import Consumer as KConsumer, KafkaException, KafkaError

class KafkaNowPlayingConsumer:
    """Consumes media events and invokes a callback on change."""
    def __init__(self, brokers: str, topic: str, group_id: str, auto_offset_reset: str = "latest") -> None:
        conf = {
            "bootstrap.servers": brokers,
            "group.id": group_id,
            "enable.auto.commit": True,
            "auto.offset.reset": auto_offset_reset,
            "session.timeout.ms": 10000,
        }
        self._topic = topic
        self._c = KConsumer(conf)
        self._last_sig: Optional[str] = None

    def start(self, on_change: Callable[[Dict], None]) -> None:
        self._c.subscribe([self._topic])
        print(f"[i] Subscribed to {self._topic}")

        try:
            while True:
                msg = self._c.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() != KafkaError._PARTITION_EOF:
                        print(f"[warn] kafka error: {msg.error()}")
                    continue

                try:
                    payload = json.loads(msg.value().decode("utf-8"))
                except Exception as e:
                    print(f"[warn] invalid json: {e}")
                    continue

                sig = json.dumps([
                    payload.get("sourceApp"),
                    payload.get("title"),
                    payload.get("artist"),
                    payload.get("playbackStatus"),
                ], ensure_ascii=False)

                if sig != self._last_sig:
                    self._last_sig = sig
                    on_change(payload)
        except KeyboardInterrupt:
            print("\n[!] Interrupted by user")
        except KafkaException as e:
            print(f"[fatal] kafka exception: {e}")
        finally:
            self._c.close()
            print("[i] Consumer closed")
