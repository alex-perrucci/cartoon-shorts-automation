# Cartoon Shorts Automation

Automated renderer for illustrated TikTok / YouTube Shorts inspired by the reference format: recurring cartoon character, generated scenes, spoken narration, large word-level captions, and subtle motion.

The editorial layer lives outside this repository. Scheduled ChatGPT tasks create complete JSON packages containing the hook, narration, scene prompts, caption, and hashtags. A push under `input/` starts the render workflow automatically.

## Pipeline

`scheduled ChatGPT task -> input JSON -> Gemini scene images -> Edge TTS + word timings -> FFmpeg vertical render -> captions -> QC -> GitHub artifact / Telegram`

## One-time repository setup

Add these under **Settings -> Secrets and variables -> Actions**:

- `GEMINI_API_KEY` — required for real image generation.
- `TELEGRAM_TOKEN` — optional, used to send the rendered video to Telegram.
- `TELEGRAM_CHAT_ID` — optional, used together with `TELEGRAM_TOKEN`.

Repository secrets are scoped per repository, so values already present in another repository must be added here too.

## Defaults

- Image model: `gemini-3.1-flash-image`
- Voice: `it-IT-IsabellaNeural`
- TTS rate: `+8%`
- Output: `1080x1920`, H.264 + AAC
- Target duration: `30-65s`
- Scenes: normally `6-10`

## Editorial contract

See `AGENTS.md`. Scheduled tasks must create exactly one new JSON package and must not modify renderer code during normal content runs.

Example package: `examples/example.json`.

## Local test

```bash
pip install -r requirements.txt
python main.py --self-test
python main.py --input examples/example.json --dry-run
```

`--dry-run` uses local placeholder illustrations but still exercises TTS, timing, FFmpeg rendering, subtitles, metadata and QC.

## GitHub Actions

- `CI`: compiles the renderer and checks FFmpeg/runtime dependencies.
- `Render cartoon short`: starts whenever a new `input/**/*.json` file is pushed, or can be run manually with an explicit input path.

The finished package is uploaded as a GitHub Actions artifact for 14 days. If Telegram secrets are configured, `final_video.mp4` is also sent there.

The implementation is intentionally small: no dashboard, database, microservices, or in-repository topic generator.
