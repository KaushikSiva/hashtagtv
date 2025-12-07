## Latest-news listener service

This FastAPI service is an HTTP wrapper around a microphone listener. When you POST to `POST /listen-latest-news`, the server starts listening for a short spoken cue (any of “what's the latest news”, “latest news”, etc.). After it understands that cue, it launches `mpv` to play the hard-coded YouTube video full-screen on the Pi’s `:0` display (for an attached 5" screen that is the default framebuffer).

### Assumptions

1. The Raspberry Pi has:
   - A working microphone exposed to ALSA/PulseAudio (common USB mic or sound card).
   - `mpv` installed with YouTube support. `mpv` invokes `yt-dlp` internally to fetch the actual stream, so install both if needed (`sudo apt install mpv` and `pip install yt-dlp`).
   - A configured “display :0” that routes to the 5" panel. `mpv --fs --display=:0` ensures the video takes the whole screen.

2. `SpeechRecognition` uses `PyAudio` (or PulseAudio/ALSA) to reach the mic. On Debian/Raspbian, install the native headers before installing the Python dependency:

   ```bash
   sudo apt install portaudio19-dev libatlas-base-dev ffmpeg
   pip install pyaudio
   ```

3. You run the listener from the same user session that manages the display since X/Wayland ownership matters when opening a full-screen window.

### Running the service

1. Install Python dependencies (including `SpeechRecognition` and `PyAudio` as described above):
   ```bash
   pip install -r requirements.txt
   ```

2. Launch the FastAPI server in the background or via a process manager:
   ```bash
   uvicorn app.news_trigger_server:app --host 0.0.0.0 --port 8080
   ```

3. Trigger a microphone check:
   ```bash
   curl -X POST http://localhost:8080/listen-latest-news
   ```

   The response will confirm that the server is listening for ~30 seconds. Speak “what's the latest news” (or a variation) during that window.

4. As soon as the phrase is recognized, `mpv` will launch full-screen on the 5" display and stream `https://youtu.be/6c_H-5RkabA`.

### Notes

- The listener is kept intentionally short (30s) so it doesn’t hog the mic. You can change the duration by editing `_run_background_listener`.
- If `mpv` is not found, the logs will clearly state that the dependency needs to be installed.
