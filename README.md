# Cartoon Shorts Automation

Automated renderer for illustrated TikTok / YouTube Shorts: recurring cartoon character, spoken narration, large high-retention captions, subtle motion, QC, GitHub artifacts and optional Telegram delivery.

The editorial + artwork layer lives outside this repository. Scheduled ChatGPT tasks create the topic, hook, script, storyboard and one original SVG illustration per scene. GitHub Actions rasterizes those SVG files locally, validates the prepared scene assets, synthesizes voice, renders the short and sends the finished MP4 to Telegram when configured.

## Pipeline

`scheduled ChatGPT task -> strong hook + script/storyboard + SVG scenes -> JSON manifest -> GitHub Actions -> SVG rasterization -> asset validation -> male Edge TTS + word timings -> safe-area captions -> FFmpeg vertical render -> QC -> GitHub artifact / Telegram`

## Why SVG transport

The GitHub connector writes UTF-8 text reliably. SVG therefore gives the scheduler a lossless text-safe artwork format without requiring a paid image API.

For each production package Actions:

1. validates the referenced self-contained SVG files;
2. rasterizes every scene to a local 1080x1920 image;
3. creates transient local base64 assets for the existing strict image validator;
4. verifies image parsing, dimensions and path containment;
5. synthesizes narration;
6. generates large captions with pixel-based safe-area fitting;
7. renders and QC-checks the final MP4.

## One-time repository setup

Under **Settings -> Secrets and variables -> Actions**, Telegram delivery is optional:

- `TELEGRAM_TOKEN`
- `TELEGRAM_CHAT_ID`

No image-generation API key is required by the renderer.

## Defaults

- Artwork source: scheduler-generated self-contained SVG scenes
- Voice: `it-IT-DiegoNeural` (male)
- TTS rate: `+8%`
- Output: `1080x1920`, H.264 + AAC
- Target duration: `30-65s`
- Scenes: normally `6-10`
- Captions: one or two words per card, dynamically sized to stay inside a horizontal safe area

## Package layout

```text
input/
  2026-09-17-am.json
assets/generated/
  2026-09-17-am/
    scene_01.svg
    scene_02.svg
    ...
```

Each scene in the JSON references both the committed SVG and the transient runner asset that Actions prepares:

```json
{
  "narration": "...",
  "visual": "The recurring businessman ...",
  "image_svg_source": "assets/generated/2026-09-17-am/scene_01.svg",
  "image_b64": "work/prepared_assets/2026-09-17-am/scene_01.b64"
}
```

See `AGENTS.md` for the complete scheduled-task and hook-quality contract.

## Local tests

```bash
pip install -r requirements.txt
python render_entry.py --self-test
python -m unittest discover -s tests -v
python render_entry.py --input examples/example.json --dry-run
```

`render_entry.py` is the production entrypoint. It reuses the core renderer while applying the current safe subtitle-layout policy.

For a real package the workflow first prepares SVG assets and then validates them before rendering.

## GitHub Actions

- `CI`: compiles the core renderer and production wrapper, runs asset/subtitle tests, performs the self-test and renders the dry-run example using the production entrypoint.
- `Render cartoon short`: starts when an `input/**/*.json` manifest is added/updated, prepares SVG scene assets, validates them, renders the video, uploads the output artifact for 14 days and sends the final MP4 to Telegram when configured.

Failed renders retain `render.log` as an Actions artifact and send a concise failure message to Telegram.

The implementation stays intentionally small: no dashboard, database, microservices, in-repository topic generator or paid image API.
