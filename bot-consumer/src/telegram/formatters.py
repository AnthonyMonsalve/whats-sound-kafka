# Helpers for HTML escaping and message formatting
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict

def escape_html(s: Optional[str]) -> str:
    """Escape HTML for Telegram parse_mode=HTML."""
    s = s or ""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def format_source_app(app: Optional[str]) -> str:
    """Map known app ids to nicer labels."""
    if not app:
        return "Unknown App 💻"
    if "Spotify" in app:
        return "Spotify 💚"
    return app

def format_timestamp_iso_to_local(ts_iso: Optional[str]) -> str:
    """Convierte un ISO-8601 a hora local de la computadora (dd/mm/YYYY HH:MM:SS)."""
    if not ts_iso:
        return ""
    dt = datetime.fromisoformat(ts_iso)
    # Si viene sin zona horaria, asumimos UTC (ajústalo si prefieres otra cosa)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    local_dt = dt.astimezone()  # usa la zona horaria local del sistema
    return local_dt.strftime("%d/%m/%Y %H:%M:%S")

def format_message_html(payload: Dict, prefix: str = "[NowPlaying]") -> str:
    """Build a rich HTML message with bold/italic and an icon for status."""
    title   = escape_html(payload.get("title", "Unknown title"))
    artist  = escape_html(payload.get("artist", "")) or None
    app     = escape_html(payload.get("sourceApp", "")) or None
    status  = escape_html(payload.get("playbackStatus", "")) or None
    ts_iso  = escape_html(payload.get("timestamp", "")) or None

    # Leading status icon
    icon = ""
    if status:
        icon = "<b><i>Playing ▶️</i></b>" if status == "playing" else "<b><i>Paused ⏸️</i></b>"

    lines = []
    if icon:
        lines.append(icon)

    lines.append(f"<b>{escape_html(prefix)}</b> {title}")
    if artist:
        lines.append(f"— 🎤 <i>{artist}</i>")

    meta = []
    if app:
        meta.append(f"<b>App:</b> {format_source_app(app)}")
    if meta:
        lines.append("\n" + "\n".join(meta))

    if ts_iso:
        lines.append(f"🕑 {format_timestamp_iso_to_local(ts_iso)}")

    return "\n".join(lines)
