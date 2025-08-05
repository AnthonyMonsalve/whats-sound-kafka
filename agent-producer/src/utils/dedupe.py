# Signature builder to detect changes.
from __future__ import annotations
import json
from typing import Dict

def build_signature(payload: Dict) -> str:
    """Stable signature for media change detection."""
    return json.dumps([
        payload.get("sourceApp"),
        payload.get("title"),
        payload.get("artist"),
        payload.get("playbackStatus"),
    ], ensure_ascii=False)
