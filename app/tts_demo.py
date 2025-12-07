#!/usr/bin/env python3
"""
Demo script for calling the Text-to-Speech API endpoints.

This script demonstrates POST methods for generating
speech from text using the TTS API.
"""

from __future__ import annotations

import argparse
import base64
from pathlib import Path
from textwrap import dedent

import requests

from .config import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_BASE_URL,
    ELEVENLABS_CLARITY,
    ELEVENLABS_PITCH_SHIFT,
    ELEVENLABS_SIMILARITY_BOOST,
    ELEVENLABS_SPEED,
    ELEVENLABS_STABILITY,
    ELEVENLABS_STYLE_EXAGGERATION,
    ELEVENLABS_VOICE_ID,
    SAD_TALKER_AUDIO_FILE,
    SAD_TALKER_VOICE_FILE,
    XAI_API_KEY,
)

BASE_URL = "https://us-east-4.api.x.ai/voice-staging"
ENDPOINT = f"{BASE_URL}/api/v1/text-to-speech/generate"
MAX_INPUT_LENGTH = 4096
MAX_PROMPT_LENGTH = 4096


def file_to_base64(file_path: str) -> str:
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def tts_request(
    input_text: str,
    prompt: str,
    vibe: str,
    voice_file: Path | None,
    output_file: Path,
    *,
    engine: str = "xai",
    eleven_voice_id: str | None = None,
) -> Path | None:
    if engine == "xai":
        return _tts_with_xai(input_text, prompt, vibe, voice_file, output_file)
    if engine == "elevenlabs":
        return _tts_with_elevenlabs(
            text=input_text,
            output_file=output_file,
            voice_id=eleven_voice_id or ELEVENLABS_VOICE_ID,
        )
    raise ValueError(f"Unsupported TTS engine: {engine}")


def _tts_with_xai(
    input_text: str,
    prompt: str,
    vibe: str,
    voice_file: Path | None,
    output_file: Path,
) -> Path:
    if XAI_API_KEY is None:
        raise RuntimeError("Set XAI_API_KEY in your environment before running.")

    if voice_file and not voice_file.exists():
        raise FileNotFoundError(f"Voice file not found: {voice_file}")

    voice_payload = file_to_base64(str(voice_file)) if voice_file else "None"
    input_text = input_text[:MAX_INPUT_LENGTH]
    prompt = prompt[:MAX_PROMPT_LENGTH]

    payload = {
        "model": "grok-voice",
        "input": input_text,
        "prompt": prompt,
        "response_format": "mp3",
        "instructions": vibe,
        "voice": voice_payload,
        "sampling_params": {
            "max_new_tokens": 512,
            "temperature": 1.0,
            "min_p": 0.01,
        },
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    response = requests.post(
        ENDPOINT,
        json=payload,
        stream=True,
        headers={"Authorization": f"Bearer {XAI_API_KEY}"},
        timeout=120,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Text-to-speech request failed ({response.status_code}): {response.text}"
        )

    with output_file.open("wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print(f"Generated speech saved to {output_file}")
    return output_file


def _tts_with_elevenlabs(
    text: str,
    output_file: Path,
    *,
    voice_id: str,
) -> Path:
    if ELEVENLABS_API_KEY is None:
        raise RuntimeError("Set ELEVENLABS_API_KEY in your environment before running.")

    payload = {
        "text": text[:MAX_INPUT_LENGTH],
        "voice_settings": {
            "stability": ELEVENLABS_STABILITY,
            "clarity": ELEVENLABS_CLARITY,
            "style_exaggeration": ELEVENLABS_STYLE_EXAGGERATION,
            "similarity_boost": ELEVENLABS_SIMILARITY_BOOST,
            "pitch_shift": ELEVENLABS_PITCH_SHIFT,
            "speed": ELEVENLABS_SPEED,
        },
    }

    url = f"{ELEVENLABS_BASE_URL}/text-to-speech/{voice_id}"

    output_file.parent.mkdir(parents=True, exist_ok=True)
    response = requests.post(
        url,
        json=payload,
        stream=True,
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        },
        timeout=120,
    )

    if response.status_code != 200:
        error_text = response.text
        if response.status_code == 404:
            error_text = (
                f"Voice '{voice_id}' not found; set ELEVENLABS_VOICE_ID to a valid "
                "identifier (see ElevenLabs dashboard or `/voices` endpoint)."
            )
        raise RuntimeError(
            f"ElevenLabs request failed ({response.status_code}): {error_text}"
        )

    with output_file.open("wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print(f"Generated speech saved to {output_file}")
    return output_file


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=dedent(
            """
            Generate speech via the XAI Text-to-Speech API. The voice template
            defaults to the file pointed to by SAD_TALKER_VOICE_FILE in config.py.
            """
        )
    )
    parser.add_argument(
        "--text",
        "-t",
        required=True,
        help="Text that should be spoken.",
    )
    parser.add_argument(
        "--prompt",
        "-p",
        default="",
        help="Optional voice prompt describing style/character.",
    )
    parser.add_argument(
        "--vibe",
        "-v",
        default="audio",
        help="Instructions/vibe string passed to the API.",
    )
    parser.add_argument(
        "--voice-file",
        help="Path to the voice sample; falls back to SAD_TALKER_VOICE_FILE.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=SAD_TALKER_AUDIO_FILE or "tts_output.mp3",
        help="Where to write the generated audio.",
    )
    parser.add_argument(
        "--engine",
        default="xai",
        choices=["xai", "elevenlabs"],
        help="Which TTS backend to use.",
    )
    parser.add_argument(
        "--eleven-voice-id",
        help="Voice id to use when the ElevenLabs engine is selected.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    voice_path = (
        Path(args.voice_file)
        if args.voice_file
        else Path(SAD_TALKER_VOICE_FILE) if SAD_TALKER_VOICE_FILE else None
    )
    output_path = Path(args.output)

    result = tts_request(
        input_text=args.text,
        prompt=args.prompt,
        vibe=args.vibe,
        voice_file=voice_path,
        output_file=output_path,
        engine=args.engine,
        eleven_voice_id=args.eleven_voice_id,
    )

    if result:
        print("Done.")


if __name__ == "__main__":
    main()
