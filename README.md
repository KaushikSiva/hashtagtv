# 🟦 HashtagTV by AI Avatar  

## X Trending News → AI Anchor → YouTube TV  

HashtagTV automatically finds trending topics on X (Twitter), asks xAI’s Grok why they are trending **right now**, generates a professional **news-anchor style** summary, converts the summary into **speech**, animates a **talking avatar video using SadTalker**, **combines it with the actual trending video**, and uploads the final clip to **YouTube** as a short breaking-news bulletin.  

It can also be voice-activated using Bruno (“Hey Bruno, what’s the latest news?”) and instantly display the most recent video on screen—like a mini **Jarvis AI-TV system**.  


---

# 🟣 Part A – Automated News Generation Pipeline  

### Steps
1. Fetch **top trends from X** (US trending, top 10)
2. User picks a trend index (0–9)
3. Query **recent tweets with videos** for that trending topic
4. Send the tweet JSON to **xAI Grok**
   - why is this trending right now?
   - summarize in <50 words
   - news anchor tone
   - return JSON `{story, url}`
5. Convert summary text → voice using **Grok TTS**
6. Animate avatar using **SadTalker**
7. Use **FFmpeg** to merge:
   - the AI avatar clip
   - real video tweet
8. Upload final video automatically to **YouTube**

### One-sentence summary
> Trending topic → Grok summary → AI avatar → stitched news video → uploaded to YouTube.  


---

# 🟠 Part B – Voice-Activated Jarvis Mode (“Bruno”)  

Bruno allows on-demand playback via natural speech.

### If user says:
**“Hey Bruno, what’s the latest news?”**
- Instantly triggers HashtagTV
- Opens and displays the most recent YouTube news video on screen

### If user says anything else:
- Continue using Grok as a conversational assistant  
- Just like a **Jarvis-style agent**


---

# 🔴 Future Feature: Real-Time Emergency Alerts  

HashtagTV will continuously monitor X in the background and detect:
- earthquakes  
- severe storms  
- emergency events  
- disaster warnings  

When a critical alert appears, HashtagTV will **interrupt instantly** and display an emergency video on Bruno’s screen—even without user interaction.  


---

# ⚙️ Technology Stack  

| Layer | Tool |
|---|---|
| Trending source | X API |
| News reasoning | xAI Grok |
| Speech | Grok TTS |
| Avatar video | SadTalker |
| Video merging | FFmpeg |
| Upload | YouTube API |
| Assistant | Bruno |
| Wake word | “Hey Bruno…” |
| Host | macOS Apple Silicon |


---

# 💽 Requirements  

- Python **3.10** recommended  
- macOS with Apple Silicon (M4 Air tested)
- SadTalker models downloaded locally
- FFmpeg installed
- X bearer token
- xAI API key
- YouTube OAuth credentials  


---

# 🔐 Environment Variables  

XAI_API_KEY=...
BEARER_TOKEN=...
YOUTUBE_API_KEY=...



---

# 🚀 Example CLI Usage  

1)To generate the prompt and video url for step 2 based on trending news for video

```
python app.py
select trend between 0 to 9:
```

2)This command does 3 things:

Converts the text prompt into spoken audio

using your Grok (or other) TTS pipeline

Fetches the referenced X/Twitter video

using the provided URL:
https://x.com/i/status/1997464637114114374

Generates a complete AI news cast

animates your avatar talking the script

grabs the X video

merges avatar + tweet video into one combined MP4

```
/venv/bin/python -m app.news_cast \
  --prompt "Georgia brought out the belt after beating Alabama in the SEC Championship" \
  --url https://x.com/i/status/1997464637114114374
```

Video is uploaded to youtube


3)This triggers the robot to show the news:
```
XAI_API_KEY=xai-xxx python3 news_voice.py
```

# 🎬 Avatar Generation (SadTalker)

Input:

story.wav

avatar.png

Output:

avatar.mp4

Runs fully locally—no cloud cost.

# 🧩 Video Merge (FFmpeg)

# 📤 YouTube Upload

# Current Capabilities

X trend detection

recent video tweet retrieval

Grok summary + JSON

TTS generation

SadTalker avatar

FFmpeg merge

YouTube upload

Bruno voice activation

# 💡 Future Ideas

24/7 monitoring

auto emergency alerts

multi-language anchors

live streaming

face-switching avatars

multi-region news feeds

ticker overlays

⭐ Final Summary

HashtagTV turns live trending topics on X into professional AI video news bulletins using Grok + SadTalker, and publishes directly to YouTube—while Bruno acts as a voice-activated on-demand news anchor similar to Jarvis.
