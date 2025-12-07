"""Simple helper to stitch a local clip before a remote video URL via ffmpeg."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path
from shutil import copy2

STREAMING_DOMAINS = (
    "youtube.com",
    "youtu.be",
    "x.com",
    "twitter.com",
    "tiktok.com",
    "vimeo.com",
    "bitchute.com",
    "rumble.com",
)


def _ensure_ffmpeg_available() -> None:
    """Raise if ffmpeg is not on the PATH."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("ffmpeg is required to merge videos; please install it.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("Unable to run ffmpeg binary.") from exc


def _has_audio_stream(video_path: Path) -> bool:
    """Return True if the file has at least one audio stream."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "a",
                "-show_entries",
                "stream=index",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("ffprobe is required to inspect audio tracks.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"ffprobe could not analyze {video_path}.") from exc

    return bool(result.stdout.strip())


def _probe_video_dimensions(video_path: Path) -> tuple[int, int]:
    """Return the width and height of the first video stream."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("ffprobe is required to inspect video streams.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"ffprobe could not analyze {video_path}.") from exc

    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(lines) < 2:
        raise RuntimeError(f"Unable to determine dimensions for {video_path}")

    return int(lines[0]), int(lines[1])


def _scale_video_to_target(
    source: Path, target_size: tuple[int, int], destination: Path
) -> None:
    """Re-encode source to match target_size while preserving aspect ratio."""
    width, height = target_size
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
    )

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "copy",
            str(destination),
        ],
        check=True,
    )


def _concat_with_reencoding(
    local_path: Path, remote_path: Path, output_path: Path, include_audio: bool
) -> None:
    """Re-encode both clips while concatenating so format mismatches are avoided."""
    filter_complex = (
        "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]"
        if include_audio
        else "[0:v][1:v]concat=n=2:v=1:a=0[v]"
    )

    args = [
        "ffmpeg",
        "-y",
        "-i",
        str(local_path),
        "-i",
        str(remote_path),
        "-filter_complex",
        filter_complex,
        "-map",
        "[v]",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-pix_fmt",
        "yuv420p",
    ]

    if include_audio:
        args.extend(
            [
                "-map",
                "[a]",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-ar",
                "44100",
            ]
        )

    args.append(str(output_path))
    subprocess.run(args, check=True)


def _is_streaming_url(remote_url: str) -> bool:
    """Heuristic for URLs that yt-dlp can resolve where ffmpeg cannot."""
    lowered = remote_url.lower()
    return any(domain in lowered for domain in STREAMING_DOMAINS)


def _download_with_ytdlp(remote_url: str, destination: Path) -> None:
    """Download from platforms like YouTube/X into destination via yt-dlp."""
    try:
        from yt_dlp import YoutubeDL
    except ImportError as exc:
        raise RuntimeError("yt-dlp is required for streaming URLs like X/YouTube") from exc

    destination.parent.mkdir(parents=True, exist_ok=True)
    template = destination.parent / "remote.%(ext)s"
    ydl_opts = {
        "outtmpl": str(template),
        "format": "bestvideo+bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(remote_url, download=True)
        downloaded_name = ydl.prepare_filename(info)

    downloaded_path = Path(downloaded_name)
    if not downloaded_path.exists():
        raise RuntimeError(f"yt-dlp failed to download {remote_url}")
    downloaded_path.replace(destination)


def _download_remote_clip(remote_url: str, destination: Path) -> None:
    """Use ffmpeg to pull the remote clip without re-encoding."""
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            remote_url,
            "-c",
            "copy",
            str(destination),
        ],
        check=True,
    )


def _prepare_remote_clip(remote_url: str, destination: Path) -> None:
    """Fetch remote content via local copy, yt-dlp (streaming), or ffmpeg."""
    candidate = Path(remote_url).expanduser()
    if candidate.exists():
        copy2(candidate, destination)
        return

    if _is_streaming_url(remote_url):
        _download_with_ytdlp(remote_url, destination)
        return

    _download_remote_clip(remote_url, destination)


def merge_local_with_remote(local_path: Path, remote_url: str, output_path: Path) -> Path:
    """
    Stitch the local clip before the remote URL content and write to output_path.

    Raises FileNotFoundError if the local clip is missing and RuntimeError if ffmpeg is unavailable.
    """
    local_path = local_path.expanduser().resolve()
    if not local_path.exists():
        raise FileNotFoundError(f"Local video does not exist: {local_path}")

    _ensure_ffmpeg_available()
    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        working_remote = Path(tmpdir) / "remote.mp4"

        _prepare_remote_clip(remote_url, working_remote)
        local_size = _probe_video_dimensions(local_path)
        remote_size = _probe_video_dimensions(working_remote)

        if local_size != remote_size:
            normalized_remote = Path(tmpdir) / "remote_scaled.mp4"
            _scale_video_to_target(working_remote, local_size, normalized_remote)
        else:
            normalized_remote = working_remote

        local_has_audio = _has_audio_stream(local_path)
        remote_has_audio = _has_audio_stream(normalized_remote)

        _concat_with_reencoding(
            local_path, normalized_remote, output_path, local_has_audio and remote_has_audio
        )

    return output_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Merge a local video file with a remote video URL (local first)."
    )
    parser.add_argument(
        "--local",
        "-l",
        type=Path,
        required=True,
        help="Path to the local video that should appear first.",
    )
    parser.add_argument(
        "--remote",
        "-r",
        required=True,
        help="Remote video URL to append after the local clip.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("merged_video.mp4"),
        help="Destination path for the merged video.",
    )
    return parser


def main() -> None:
    """CLI entry point so the script can be used directly."""
    parser = _build_parser()
    args = parser.parse_args()

    try:
        merged_path = merge_local_with_remote(args.local, args.remote, args.output)
    except Exception as exc:  # pragma: no cover - CLI helper
        parser.error(str(exc))
    print(f"Merged video saved at: {merged_path}")


if __name__ == "__main__":
    main()
