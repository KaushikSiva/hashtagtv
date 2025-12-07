"""Command-line helper to turn a prompt into a SadTalker video."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .config import (
    SAD_TALKER_AUDIO_FILE,
    SAD_TALKER_PATH,
    SAD_TALKER_REFERENCE_IMAGE,
    SAD_TALKER_RESULT_DIR,
)
from .sadtalker_client import SadTalkerError, SadTalkerResult, generate_video_from_prompt


def _real_sadtalker_path() -> Path:
    return Path(SAD_TALKER_PATH).expanduser().resolve()


def _default_source_image() -> Path:
    return _real_sadtalker_path() / "examples" / "source_image" / "full_body_1.png"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a SadTalker video directly from a text prompt."
    )
    default_image = _default_source_image()
    env_audio_path = (
        Path(SAD_TALKER_AUDIO_FILE).expanduser().resolve()
        if SAD_TALKER_AUDIO_FILE
        else None
    )
    env_image_path = Path(SAD_TALKER_REFERENCE_IMAGE).expanduser().resolve()
    parser.add_argument(
        "--prompt",
        "-p",
        help="Text that should be spoken in the generated video.",
    )
    parser.add_argument(
        "--prompt-file",
        "-f",
        type=Path,
        default=Path("prompt.txt"),
        help="Path to a text file whose content will be used as the spoken prompt (default: prompt.txt).",
    )
    parser.add_argument(
        "--reference-image",
        "-r",
        type=Path,
        default=env_image_path,
        help=f"Portrait image the animation will be based on (default: {env_image_path}).",
    )
    parser.add_argument(
        "--result-dir",
        "-o",
        type=Path,
        default=Path(SAD_TALKER_RESULT_DIR),
        help=f"Directory where SadTalker writes the final video (default: {SAD_TALKER_RESULT_DIR}).",
    )
    parser.add_argument(
        "--audio-file",
        "-a",
        type=Path,
        default=env_audio_path,
        help="Use a pre-recorded WAV instead of TTS (default: from SAD_TALKER_AUDIO_FILE).",
    )
    parser.add_argument(
        "--checkpoint-dir",
        "-c",
        type=Path,
        help="Override the default SadTalker checkpoints directory if it lives elsewhere.",
    )
    parser.add_argument(
        "--pose-style",
        type=int,
        default=0,
        help="Pose style index (0-46).",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=256,
        help="Render resolution for SadTalker (default: 256).",
    )
    parser.add_argument(
        "--still",
        action="store_true",
        help="Enable still-mode rendering (better for full body).",
    )
    parser.add_argument(
        "--expression-scale",
        type=float,
        default=1.0,
        help="Expression intensity multiplier (default: 1.0).",
    )
    parser.add_argument(
        "--preprocess",
        choices=["crop", "extcrop", "resize", "full", "extfull"],
        default="crop",
        help="Image preprocessing mode.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=2,
        help="Batch size for the rendering stage.",
    )
    parser.add_argument(
        "--device",
        choices=["cpu", "cuda", "gpu"],
        default="cpu",
        help="Hint for whether to force CPU execution or allow CUDA.",
    )
    parser.add_argument(
        "--ref-pose",
        type=Path,
        help="Reference video path that SadTalker can copy poses from.",
    )
    parser.add_argument(
        "--ref-eyeblink",
        type=Path,
        help="Reference video path that supplies eye blinking behavior.",
    )
    parser.add_argument(
        "--enhancer",
        type=str,
        choices=["gfpgan", "RestoreFormer"],
        help="Face enhancer to run after rendering.",
    )
    parser.add_argument(
        "--background-enhancer",
        type=str,
        choices=["realesrgan"],
        help="Background enhancer to run after rendering.",
    )
    parser.add_argument(
        "--old-version",
        action="store_true",
        help="Use the legacy SadTalker checkpoints (use if you only have .pth models).",
    )
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Keep the synthesized driving audio for debugging.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Ask SadTalker to emit the intermediate files instead of deleting them.",
    )

    args = parser.parse_args(argv)
    args.result_dir.mkdir(parents=True, exist_ok=True)

    prompt_text: str | None = None
    if args.prompt_file and args.prompt_file.exists():
        prompt_text = args.prompt_file.read_text().strip()

    if not prompt_text:
        prompt_text = (args.prompt or "").strip()

    if not prompt_text:
        parser.error("Provide --prompt or create a non-empty prompt file.")

    try:
        result: SadTalkerResult = generate_video_from_prompt(
            prompt=prompt_text,
            reference_image=args.reference_image.expanduser().resolve(),
            result_dir=args.result_dir,
            checkpoint_dir=args.checkpoint_dir,
            pose_style=args.pose_style,
            size=args.size,
            still_mode=args.still,
            expression_scale=args.expression_scale,
            preprocess=args.preprocess,
            batch_size=args.batch_size,
            ref_pose=args.ref_pose,
            ref_eyeblink=args.ref_eyeblink,
            enhancer=args.enhancer,
            background_enhancer=args.background_enhancer,
            old_version=args.old_version,
            verbose=args.verbose,
            cleanup_audio=not args.keep_audio,
            device=args.device,
            driven_audio=args.audio_file.expanduser().resolve() if args.audio_file else None,
        )
    except SadTalkerError as exc:
        print(f"SadTalker failed: {exc}", file=sys.stderr)
        return 1

    print(f"Video ready: {result.video_path}")
    print(f"SadTalker artifacts directory: {result.result_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
