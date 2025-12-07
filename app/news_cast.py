#!/usr/bin/env python3
"""High-level helper to turn text + remote URL into a merged news avatar clip."""

from __future__ import annotations

import argparse
from pathlib import Path
from shutil import copy2
from textwrap import dedent

from .config import (
    SAD_TALKER_AUDIO_FILE,
    SAD_TALKER_OUTPUT_DIR,
    SAD_TALKER_REFERENCE_IMAGE,
    SAD_TALKER_RESULT_DIR,
    SAD_TALKER_VOICE_FILE,
)
from .sadtalker_client import SadTalkerResult, SadTalkerError, generate_video_from_prompt
from .tts_demo import tts_request
from .video_merger import merge_local_with_remote


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=dedent(
            """
            Generate a short news cast by:
            1. TTS’ing the provided prompt
            2. Driving SadTalker with the generated audio + reference image
            3. Concatenating the avatar segment with a remote video URL
            """
        )
    )
    parser.add_argument("--prompt", "-p", required=True, help="Text the avatar should speak.")
    parser.add_argument(
        "--url",
        "-u",
        required=True,
        help="Remote video URL to append after the avatar segment.",
    )
    parser.add_argument(
        "--voice-file",
        help="Path to source voice sample (default from config).",
    )
    parser.add_argument(
        "--audio-output",
        help="Where to save the TTS audio (default from config).",
    )
    parser.add_argument(
        "--reference-image",
        help="Reference image for SadTalker (defaults to config value).",
    )
    parser.add_argument(
        "--result-dir",
        help="Where SadTalker writes the generated video (defaults to config value).",
    )
    parser.add_argument(
        "--merged-output",
        default=str(Path(SAD_TALKER_OUTPUT_DIR) / "news_cast.mp4"),
        help="Final merged video path.",
    )
    parser.add_argument(
        "--vibe",
        default="audio",
        help="Instructions/vibe string forwarded to the TTS API.",
    )
    parser.add_argument(
        "--engine",
        default="xai",
        choices=["xai", "elevenlabs"],
        help="TTS engine to use for the prompt.",
    )
    parser.add_argument(
        "--eleven-voice-id",
        help="Voice identifier to use when the ElevenLabs engine is selected.",
    )
    return parser


def _resolve_paths(args: argparse.Namespace) -> tuple[Path | None, Path, Path, Path]:
    voice_path = (
        Path(args.voice_file)
        if args.voice_file
        else Path(SAD_TALKER_VOICE_FILE) if SAD_TALKER_VOICE_FILE else None
    )
    audio_output = (
        Path(args.audio_output)
        if args.audio_output
        else Path(SAD_TALKER_AUDIO_FILE) if SAD_TALKER_AUDIO_FILE else Path("outputs/tts_audio.mp3")
    )
    reference_image = (
        Path(args.reference_image)
        if args.reference_image
        else Path(SAD_TALKER_REFERENCE_IMAGE)
        if SAD_TALKER_REFERENCE_IMAGE
        else None
    )
    resolved_result_dir = (
        Path(args.result_dir) if args.result_dir else None
    )
    if resolved_result_dir is None:
        resolved_result_dir = (
            Path(SAD_TALKER_RESULT_DIR)
            if SAD_TALKER_RESULT_DIR
            else Path(SAD_TALKER_OUTPUT_DIR)
        )
    if reference_image is None:
        raise ValueError("Reference image must be provided via config or --reference-image.")
    return voice_path, audio_output, reference_image, resolved_result_dir


def _synthesize_prompt(
    prompt: str,
    voice_path: Path | None,
    audio_output: Path,
    vibe: str,
    engine: str,
    eleven_voice_id: str | None,
) -> Path:
    audio = tts_request(
        input_text=prompt,
        prompt=prompt,
        vibe=vibe,
        voice_file=voice_path,
        output_file=audio_output,
        engine=engine,
        eleven_voice_id=eleven_voice_id,
    )
    if audio is None:
        raise RuntimeError("TTS request failed; no audio was produced.")
    return audio


def _create_avatar_video(
    prompt: str, reference: Path, driven_audio: Path, result_dir: Path
) -> SadTalkerResult:
    return generate_video_from_prompt(
        prompt=prompt,
        reference_image=reference,
        driven_audio=driven_audio,
        result_dir=result_dir,
        verbose=False,
    )


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    voice_path, audio_output, reference_image, result_dir = _resolve_paths(args)
    audio_path = _synthesize_prompt(
        args.prompt,
        voice_path,
        audio_output,
        args.vibe,
        args.engine,
        args.eleven_voice_id,
    )

    try:
        avatar = _create_avatar_video(args.prompt, reference_image, audio_path, result_dir)
    except SadTalkerError as exc:
        raise SystemExit(f"SadTalker failed: {exc}") from exc

    avatar_output_dir = Path(SAD_TALKER_OUTPUT_DIR)
    avatar_output_dir.mkdir(parents=True, exist_ok=True)
    avatar_destination = avatar_output_dir / avatar.video_path.name

    if avatar.video_path.parent != avatar_output_dir:
        copy2(avatar.video_path, avatar_destination)
    else:
        avatar_destination = avatar.video_path

    merged = merge_local_with_remote(
        avatar_destination, args.url, Path(args.merged_output)
    )
    print(f"Final news cast saved to {merged}")


if __name__ == "__main__":
    main()
