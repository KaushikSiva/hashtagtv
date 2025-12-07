"""Placeholder avatar provider."""
from .config import AVATAR_API_KEY


def create_avatar_video(script: str) -> dict:
    """Dummy avatar video metadata until a real provider exists."""
    if not AVATAR_API_KEY:
        return {
            "message": "Avatar API key not configured.",
            "script_preview": script[:120],
        }

    return {
        "avatar_id": "demo-anchor-001",
        "video_url": "https://example.com/avatars/demo-anchor/video.mp4",
        "transcript": script,
    }
