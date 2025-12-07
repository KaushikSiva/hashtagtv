# SadTalker Prompt Runner

This project ships a tiny wrapper around [OpenTalker/SadTalker](https://github.com/OpenTalker/SadTalker/) so you can type a short prompt and have SadTalker produce a talking-head video.

Key pieces:

- `app/sadtalker_client.py` orchestrates the SadTalker `inference.py` script:
  1. Turns your prompt into a temporary WAV file using `pyttsx3`.
  2. Calls `SadTalker/inference.py` with that audio plus the reference image and optional extras (pose videos, enhancer flags, etc.).
  3. Returns the generated MP4 path along with the directory SadTalker used for temporary assets.

- `app/sadtalker_cli.py` exposes a small `argparse` CLI that lets you pass in a prompt, choose a reference image (defaults to `SadTalker/examples/source_image/full_body_1.png`), and tweak a few knobs (pose style, still-mode, enhancers).

## Getting started

1. **Install the dependencies** (adds `pyttsx3` for audio):
   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare SadTalker** (the repository is expected at `SadTalker`):
   - Clone the repo (already done in this workspace).
   - Download the checkpoints and place them under `SadTalker/checkpoints`. The upstream repo provides [`scripts/download_models.sh`](https://github.com/OpenTalker/SadTalker#download-models) to grab everything, or you can download manually.
   - If your checkpoints live elsewhere, set `SAD_TALKER_PATH` (in `.env` or your shell) to point at the root of the SadTalker repo.
   - Set `SAD_TALKER_REFERENCE_IMAGE`, `SAD_TALKER_AUDIO_FILE`, and `SAD_TALKER_RESULT_DIR` in your `.env` to control the default image, driving audio, and output folder that the CLI will use.

3. **Run the CLI**:
   ```bash
  python3 -m app.sadtalker_cli \
    --prompt "Hello, this is NewsBot turning your text into a voice." \
    --reference-image SadTalker/examples/source_image/full_body_1.png \
    --result-dir outputs/sadtalker/demo \
    --device cpu
   ```
   The script will synthesize the prompt, run SadTalker inference, and print the MP4 path.

4. **Optional tweaks**:
   - Use `--ref-pose` or `--ref-eyeblink` to copy motion from other videos.
   - Turn on `--still` for full-body references.
   - Supply `--checkpoint-dir` if SadTalker lives outside the default `SadTalker/checkpoints`.
   - Pass `--keep-audio` to keep the temporary driving audio if you want to re-use it.

## Notes

- The CLI honors `--device cpu|cuda|gpu`. It defaults to CPU to avoid requiring a GPU in the workspace.
- The SadTalker repo generates videos under the directory you pass to `--result-dir`, inside a timestamped folder (e.g. `outputs/sadtalker/demo/2024_02_...`). The CLI prints the final MP4 path so you can upload or preview it.
- If SadTalker fails, the CLI surfaces a plain error message and exits with a non-zero status so you can script around it.
