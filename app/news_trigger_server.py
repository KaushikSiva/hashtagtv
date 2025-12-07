"""Minimal FastAPI service that listens for "latest news" via the mic and plays a fixed YouTube video."""
import logging
import subprocess
import threading
import time
from typing import Optional

import speech_recognition as sr
from fastapi import BackgroundTasks, FastAPI

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI()

# YouTube video that should be played full-screen when the trigger phrase is heard.
YOUTUBE_VIDEO_URL = "https://youtu.be/6c_H-5RkabA"

# Phrase variants that are treated as the “latest news” cue.
PHRASE_TOKENS = ["latest news", "recent news", "what's the latest news", "what is the latest news"]


def _recognize_microphone_phrase(timeout: float = 10) -> Optional[str]:
    """Capture a short audio sample and convert it to text using Google Speech Recognition."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as mic:
        logger.info("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(mic, duration=1)
        logger.info("Listening for a phrase...")
        audio = recognizer.listen(mic, timeout=timeout)

    try:
        text = recognizer.recognize_google(audio)
        logger.info("Heard: %s", text)
        return text.strip().lower()
    except sr.UnknownValueError:
        logger.info("Could not understand the audio.")
    except sr.RequestError as exc:
        logger.error("Speech recognition request failed: %s", exc)
    return None


def wait_for_phrase_and_play_video(stop_after_seconds: float = 30) -> None:
    """Block until a trigger phrase is heard, then launch the video player."""
    deadline = time.monotonic() + stop_after_seconds
    while time.monotonic() < deadline:
        heard = _recognize_microphone_phrase()
        if not heard:
            continue

        if any(token in heard for token in PHRASE_TOKENS):
            _play_video_fullscreen()
            return

    logger.info("Stopped listening after %.1f seconds without trigger.", stop_after_seconds)


def _play_video_fullscreen() -> None:
    """Run mpv (or a fallback) to play the YouTube video in full screen on :0."""
    logger.info("Launching video player in full screen.")
    cmd = ["mpv", "--fs", "--display=:0", "--no-terminal", "--no-input-default-bindings", YOUTUBE_VIDEO_URL]
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info("Video player started.")
    except FileNotFoundError:
        logger.error(
            "mpv is not installed. Install mpv on the Raspberry Pi (e.g. sudo apt install mpv) "
            "and make sure yt-dlp is available for YouTube playback."
        )


def _run_background_listener(stop_after_seconds: float = 30) -> None:
    """Helper to run the listening loop in a dedicated thread."""
    listen_thread = threading.Thread(target=wait_for_phrase_and_play_video, args=(stop_after_seconds,))
    listen_thread.daemon = True
    listen_thread.start()


@app.post("/listen-latest-news")
def trigger_listening(background_tasks: BackgroundTasks) -> dict:
    """HTTP endpoint that kicks off a microphone listener."""
    logger.info("Received request to wait for the latest-news phrase.")
    background_tasks.add_task(_run_background_listener)
    return {"status": "listening for 'latest news' question on the microphone", "duration_seconds": 30}
