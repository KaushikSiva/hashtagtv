from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

XAI_API_KEY = os.getenv("XAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
AVATAR_API_KEY = os.getenv("AVATAR_API_KEY")
GROK_API_KEY = os.getenv("GROK_API_KEY")
SAD_TALKER_PATH = os.getenv("SAD_TALKER_PATH", "SadTalker")
SAD_TALKER_REFERENCE_IMAGE = os.getenv(
    "SAD_TALKER_REFERENCE_IMAGE",
    str(Path(SAD_TALKER_PATH) / "examples" / "source_image" / "full_body_1.png"),
)
SAD_TALKER_AUDIO_FILE = os.getenv("SAD_TALKER_AUDIO_FILE")
SAD_TALKER_VOICE_FILE = os.getenv("SAD_TALKER_VOICE_FILE")
SAD_TALKER_OUTPUT_DIR = os.getenv("SAD_TALKER_OUTPUT_DIR", str(Path("outputs") / "sadtalker"))
SAD_TALKER_RESULT_DIR = os.getenv("SAD_TALKER_RESULT_DIR", SAD_TALKER_OUTPUT_DIR)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "MrLucas")
ELEVENLABS_BASE_URL = os.getenv("ELEVENLABS_BASE_URL", "https://api.elevenlabs.io/v1")

def _float_from_env(var: str, default: str) -> float:
    try:
        return float(os.getenv(var, default))
    except ValueError:
        return float(default)

ELEVENLABS_STABILITY = _float_from_env("ELEVENLABS_STABILITY", "0.32")
ELEVENLABS_CLARITY = _float_from_env("ELEVENLABS_CLARITY", "0.55")
ELEVENLABS_STYLE_EXAGGERATION = _float_from_env("ELEVENLABS_STYLE_EXAGGERATION", "0.42")
ELEVENLABS_SIMILARITY_BOOST = _float_from_env("ELEVENLABS_SIMILARITY_BOOST", "0.88")
ELEVENLABS_PITCH_SHIFT = _float_from_env("ELEVENLABS_PITCH_SHIFT", "1.0")
ELEVENLABS_SPEED = _float_from_env("ELEVENLABS_SPEED", "0.93")
