# Cartoon Shorts Automation

Automated renderer and draft-distribution pipeline for illustrated TikTok / YouTube Shorts: recurring cartoon character, satirical narration, large high-retention captions, subtle motion, QC, private YouTube upload and TikTok inbox/draft delivery.

Scheduled ChatGPT tasks create the topic, hook, 150+ word script, storyboard, platform metadata and one original SVG illustration per scene. GitHub Actions rasterizes the SVG files locally, validates the prepared assets, synthesizes voice, renders the short, QC-checks it, then prepares it for both social channels.

## Pipeline

`scheduled ChatGPT task -> satirical hook + 60s+ script + SVG scenes + YouTube/TikTok metadata -> GitHub Actions -> SVG rasterization -> male TTS + exact scene timing -> safe-area captions -> FFmpeg render -> QC -> YouTube private + TikTok inbox draft`

Telegram is no longer the delivery path. When configured, it is used only for pipeline-failure notifications.

## Why SVG transport

The GitHub connector writes UTF-8 text reliably. SVG therefore gives the scheduler a lossless text-safe artwork format without requiring a paid image API.

For each production package Actions:

1. validates the referenced self-contained SVG files;
2. rasterizes every scene to a local 1080x1920 image;
3. validates images and path containment;
4. synthesizes the male narration and captures word timings;
5. switches scene artwork on exact narration boundaries;
6. generates large captions with pixel-based safe-area fitting;
7. renders a 60-second-or-longer vertical MP4 and QC-checks it;
8. uploads the finished video to YouTube as private when YouTube OAuth is configured;
9. sends the video to the official TikTok creator inbox/draft flow when TikTok OAuth is configured.

## One-time repository setup

See **`OAUTH_SETUP.md`** for the complete OAuth walkthrough.

Production social automation uses these GitHub Actions secrets:

```text
YOUTUBE_CLIENT_ID
YOUTUBE_CLIENT_SECRET
YOUTUBE_REFRESH_TOKEN
TIKTOK_CLIENT_KEY
TIKTOK_CLIENT_SECRET
TIKTOK_TOKEN_KEY
```

Optional failure notifications:

```text
TELEGRAM_TOKEN
TELEGRAM_CHAT_ID
```

No image-generation API key is required by the renderer.

## Defaults

- Artwork source: scheduler-generated self-contained SVG scenes
- Voice: `it-IT-DiegoNeural` (male)
- TTS rate: `-4%`
- Output: `1080x1920`, H.264 + AAC
- Hard minimum final duration: `60s`
- Script target: `165-190` Italian words, never fewer than `150`
- Scenes: normally `7-10`
- Captions: one or two words per card, dynamically sized to stay inside the horizontal safe area
- YouTube: automatic `private` upload, metadata prefilled
- TikTok: official `video.upload` inbox/draft flow; caption/hashtags remain in the manifest for the final TikTok edit because the draft video endpoint does not accept them

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

Each scene references both the committed SVG and the transient runner asset prepared by Actions. Every new manifest also contains separate `youtube` and `tiktok` metadata objects. See `AGENTS.md` for the full content contract.

## Local tests

```bash
pip install -r requirements.txt
python render_entry.py --self-test
python -m unittest discover -s tests -v
python render_entry.py --input examples/example.json --dry-run
```

`render_entry.py` is the production entrypoint. It reuses the core renderer while applying the current safe subtitle-layout, exact scene-sync and ending-padding policy.

## GitHub Actions

- `CI`: compiles the renderer, social/OAuth scripts and tests, performs the self-test, and renders the dry-run example.
- `Render cartoon short`: starts when an `input/**/*.json` manifest is added/updated, renders and QC-checks the short, uploads the output artifact, then creates social drafts on `main` when OAuth is configured.

Failed render/social steps retain logs as an Actions artifact and can send a concise Telegram failure notification.
