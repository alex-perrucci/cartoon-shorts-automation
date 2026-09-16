# Cartoon Shorts Automation

Automated renderer for illustrated TikTok / YouTube Shorts.

The editorial layer lives outside this repository: a scheduled ChatGPT task creates a complete JSON package containing the hook, narration, scene prompts, caption, and hashtags. This repository turns that package into a finished vertical video.

## Pipeline

`input JSON -> scene images -> TTS + word timings -> animated vertical render -> captions -> QC -> output package`

## Goals

- One deterministic rendering pipeline.
- No in-repo topic brainstorming or script writing.
- 9:16, 1080x1920 output.
- Consistent visual style across scenes.
- Word-level captions.
- Automatic QC before delivery.
- Safe retries: the same input package is never processed twice unless explicitly forced.

Initial implementation is intentionally minimal. No dashboard, database, or microservices.
