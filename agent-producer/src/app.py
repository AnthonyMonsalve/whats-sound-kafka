# Application wiring & loop.
from __future__ import annotations
import asyncio
from src.config import settings
from src.kafka.producer import KafkaNowPlayingProducer
from src.media.win_now_playing import read_now_playing
from src.utils.dedupe import build_signature

async def run() -> None:
    producer = KafkaNowPlayingProducer()
    print(f"[i] Kafka producer ready (brokers={settings.brokers}) topic={settings.topic}")

    last_sig: str | None = None
    try:
        while True:
            try:
                data = await read_now_playing()
                if data:
                    sig = build_signature(data)
                    if sig != last_sig:
                        last_sig = sig
                        producer.send(data)
                        print(f"[→] {data}")
            except Exception as e:
                print(f"[warn] read/send error: {e}")

            await asyncio.sleep(settings.poll_interval_sec)
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
    finally:
        producer.flush(5)
        print("[i] Producer flushed. Bye.")
