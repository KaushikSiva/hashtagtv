"""Simple client for GROK-style messaging."""

from typing import Optional

from .config import GROK_API_KEY


def ask_grok(prompt: str) -> Optional[str]:
    """Return a placeholder response (replace with real GROK call if available)."""
    if not GROK_API_KEY:
        return None
    # If GROK becomes available, swap this with the actual HTTP call.
    return f\"\"\"{prompt} — That’s the concise summary powered by GROK.\"\"\"
