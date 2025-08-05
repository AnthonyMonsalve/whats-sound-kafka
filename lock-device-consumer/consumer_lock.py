# -*- coding: utf-8 -*-
"""
Kafka -> Windows control consumer (lock / wake).
- Listens to control topic (JSON messages).
- If action == "lock" and target == this machine (or "all"), calls LockWorkStation.
- If action == "unlock": wakes display (can't bypass Windows login).
"""

import os
import json
import time
import ctypes
from ctypes import wintypes
from datetime import datetime
from typing import Optional

# Optional .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from confluent_kafka import Consumer, KafkaException, KafkaError

# -------- Config --------
BROKERS     = os.getenv("KAFKA_BROKERS", "localhost:9092")
TOPIC       = os.getenv("TOPIC_CONTROL", "pc.activity.control")
GROUP_ID    = os.getenv("GROUP_ID", "pc-lock-consumer")
MACHINE_KEY = os.getenv("MACHINE_KEY") or os.environ.get("COMPUTERNAME") or "pc"

# -------- Windows helpers --------
# user32.LockWorkStation
_user32 = ctypes.windll.user32
_kernel32 = ctypes.windll.kernel32

# SetThreadExecutionState constants
ES_AWAYMODE_REQUIRED   = 0x00000040
ES_CONTINUOUS          = 0x80000000
ES_DISPLAY_REQUIRED    = 0x00000002
ES_SYSTEM_REQUIRED     = 0x00000001

# keybd_event constants
KEYEVENTF_KEYUP = 0x0002
VK_SHIFT        = 0x10

def lock_workstation() -> bool:
    """Locks the current workstation (requires interactive session)."""
    try:
        res = _user32.LockWorkStation()
        return bool(res)
    except Exception as exc:
        print(f"[warn] LockWorkStation failed: {exc}")
        return False

def wake_display() -> None:
    """
    Try to wake the display and keep the system from sleeping briefly.
    Note: This does NOT unlock a Windows locked session (login required).
    """
    try:
        # Keep system/display on for a short period
        _kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        )
        # Send a SHIFT key tap to wake displays
        _user32.keybd_event(VK_SHIFT, 0, 0, 0)
        _user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0)
    except Exception as exc:
        print(f"[warn] wake_display failed: {exc}")

# -------- Message handling --------
def is_for_me(target: Optional[str]) -> bool:
    """Returns True if target matches this machine or 'all'."""
    if not target:
        return False
    t = str(target).strip().lower()
    return t == "all" or t == MACHINE_KEY.lower()

def handle_control(payload: dict) -> None:
    """
    Expected schema:
      {
        "type": "control",
        "action": "lock" | "unlock",
        "target": "all" | "<machineKey>",
        "by": "telegram:<user_id>",
        "ts": "<ISO8601>"
      }
    """
    action = (payload.get("action") or "").lower()
    target = payload.get("target")
    origin = payload.get("by")
    print(f"[i] Received action={action} target={target} by={origin}")

    if not is_for_me(target):
        print(f"[i] Ignored (target={target}, this={MACHINE_KEY})")
        return

    if action == "lock":
        ok = lock_workstation()
        print("[→] Lock command executed." if ok else "[warn] Lock command failed.")
    elif action == "unlock":
        # We cannot unlock Windows login; we just wake the screen.
        wake_display()
        print("[→] Wake command executed (unlock not possible at OS login).")
    else:
        print(f"[warn] Unknown action: {action}")

# -------- Kafka consumer loop --------
def run_consumer() -> None:
    conf = {
        "bootstrap.servers": BROKERS,
        "group.id": GROUP_ID,
        "enable.auto.commit": True,
        "auto.offset.reset": "latest",
        "session.timeout.ms": 10000,
    }
    c = Consumer(conf)
    c.subscribe([TOPIC])

    print(f"[i] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
          f"Listening topic='{TOPIC}' as group='{GROUP_ID}', machine='{MACHINE_KEY}'")

    try:
        while True:
            msg = c.poll(1.0)
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

            # Only process control messages
            if (payload.get("type") or "").lower() == "control":
                handle_control(payload)
            else:
                print("[i] Non-control message ignored.")
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
    except KafkaException as e:
        print(f"[fatal] kafka exception: {e}")
    finally:
        c.close()
        print("[i] Consumer closed")

if __name__ == "__main__":
    run_consumer()
