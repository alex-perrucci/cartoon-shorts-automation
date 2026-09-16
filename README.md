# Cartoon Shorts Automation

Automated renderer for illustrated TikTok / YouTube Shorts: recurring cartoon character, spoken narration, large word-level captions, subtle motion, QC, GitHub artifacts and optional Telegram delivery.

The editorial + artwork layer lives outside this repository. Scheduled ChatGPT tasks create the topic, script, storyboard and one original scene image per beat. Each image is stored in GitHub as base64 text (`.b64`), so the renderer does not need an external image-generation API or image-model billing.

## Pipeline

`scheduled ChatGPT task -> script/storyboard -> generated scene images -> base64 scene assets + JSON manifest -> GitHub Actions -> asset validation/decode -> Edge TTS + word timings -> FFmpeg vertical render -> captions -> QC -> GitHub artifact / Telegram`

## Why base64 assets

The GitHub connector can reliably write text. Scene images are therefore encoded as base64 text files under `assets/generated/<package-id>/`. During Actions the renderer:

1. validates every referenced asset path;
2. decodes strict base64;
3. checks optional SHA-256 integrity;
4. verifies the decoded bytes are a real image;
5. rejects tiny or oversized images;
6. normalizes every scene to `1080x1920` PNG;
7. only then starts TTS and video rendering.

This keeps image generation in the scheduled ChatGPT task while leaving deterministic assembly to GitHub Actions.

## One-time repository setup

Under **Settings -> Secrets and variables -> Actions**, only Telegram delivery is optional:

- `TELEGRAM_TOKEN`
- `TELEGRAM_CHAT_ID`

`GEMINI_API_KEY` is no longer used by the renderer and can be removed from this repository if desired.

## Defaults

- Image source: scheduler-generated base64 scene assets
- Voice: `it-IT-IsabellaNeural`
- TTS rate: `+8%`
- Output: `1080x1920`, H.264 + AAC
- Target duration: `30-65s`
- Scenes: normally `6-10`

## Package layout

```text
input/
  2026-09-17-am.json
assets/generated/
  2026-09-17-am/
    scene_01.b64
    scene_02.b64
    ...
```

Each scene in the JSON references its asset:

```json
{
  "narration": "...",
  "visual": "The recurring businessman ...",
  "image_b64": "assets/generated/2026-09-17-am/scene_01.b64",
  "image_sha256": "...64 hex characters..."
}
```

See `AGENTS.md` for the complete scheduled-task contract.

## Local tests

```bash
pip install -r requirements.txt
python main.py --self-test
python -m unittest discover -s tests -v
python main.py --input examples/example.json --dry-run
```

`--dry-run` intentionally ignores scene assets and uses local placeholder images while still exercising TTS, timing, FFmpeg rendering, captions, metadata and QC.

For a real package you can validate all scene assets before rendering:

```bash
python main.py --input input/2026-09-17-am.json --validate-assets
```

## GitHub Actions

- `CI`: compiles the renderer, runs asset-validation tests, performs the self-test and renders the dry-run example.
- `Render cartoon short`: starts when an `input/**/*.json` manifest is added/updated, validates packaged scene assets, renders the video, uploads the output artifact for 14 days and sends the final MP4 to Telegram when configured.

Failed renders retain `render.log` as an Actions artifact and also send a concise failure message to Telegram.

The implementation is intentionally small: no dashboard, database, microservices, in-repository topic generator or paid image API.
