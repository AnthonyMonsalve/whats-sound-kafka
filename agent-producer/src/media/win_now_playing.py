# Async reader for Windows GSMTC (winsdk).
from __future__ import annotations
from datetime import datetime, timezone
from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaManager,
    GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus,
)

def _status_name(status_enum: int) -> str:
    """Map PlaybackStatus enum to human-readable string."""
    mapping = {
        int(PlaybackStatus.CLOSED):   "closed",
        int(PlaybackStatus.OPENED):   "opened",
        int(PlaybackStatus.CHANGING): "changing",
        int(PlaybackStatus.STOPPED):  "stopped",
        int(PlaybackStatus.PLAYING):  "playing",
        int(PlaybackStatus.PAUSED):   "paused",
    }
    return mapping.get(int(status_enum), str(status_enum))

async def read_now_playing() -> dict | None:
    """
    Await WinRT async APIs (no .get()).
    Returns a dict (without None values) or None if no session/info.
    NOTE: Must run in an interactive user session.
    """
    mgr = await MediaManager.request_async()
    session = mgr.get_current_session()
    if not session:
        return None

    props = await session.try_get_media_properties_async()
    if not props:
        return None

    info = session.get_playback_info()
    status = info.playback_status if info else None

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sourceApp": getattr(session, "source_app_user_model_id", None),
        "title": getattr(props, "title", None),
        "artist": getattr(props, "artist", None),
        "album": getattr(props, "album_title", None),
        "playbackStatus": _status_name(status) if status is not None else None,
    }
    # Remove None values
    return {k: v for k, v in payload.items() if v is not None}
