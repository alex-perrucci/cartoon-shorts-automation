# Editorial task contract

This repository does NOT invent its own topics or generate creative artwork at render time. Scheduled ChatGPT tasks are the editorial + artwork layer.

Each scheduled run must create one complete content package consisting of:

- exactly one new UTF-8 JSON manifest under `input/`, such as `input/2026-09-17-am.json`;
- exactly one original SVG illustration per scene under `assets/generated/<package-id>/`, such as `scene_01.svg`.

The render workflow starts when the JSON manifest is committed. Create every SVG asset first and commit the `input/*.json` manifest LAST. An atomic multi-file commit is also acceptable. Never expose Actions to a manifest whose referenced SVG files do not yet exist.

## Editorial rules

Before writing a package:

1. Inspect recent files under `input/` and avoid repeating the same topic, hook, core fact, or visual sequence.
2. Pick a topic that can be explained visually and understood without context.
3. Prefer evergreen curiosity, money/business mechanisms, psychology, technology, unusual systems, or useful surprising facts. Do not fabricate factual claims.
4. Verify factual claims when they are not common knowledge.
5. The first sentence must work as a strong spoken hook within about two seconds.
6. Write natural Italian narration intended for TTS, normally about 80-125 words and 35-60 seconds after synthesis.
7. Split it into 6-10 scenes. Each scene should correspond to a meaningful narration beat, not arbitrary equal chunks.
8. Write every `visual` description in English.
9. Create exactly one original vertical SVG illustration for every scene. Preserve the same recurring protagonist and visual grammar across the package: simple 2D editorial cartoon, warm cream/beige background, thick black outlines, sparse props, black suit/white shirt/black tie, minimal shading, no watermark, no third-party logos. Text inside the artwork should be avoided except when it is essential to the concept, such as a price or number being explained.
10. Keep scenes visually distinct while preserving the protagonist.
11. Caption should be short. Hashtags should be few and relevant, not spammy.

## Artwork transport rules

SVG is the canonical transport format because it is UTF-8 text and can be committed losslessly through the GitHub connector.

For every scene:

1. Save the artwork as `assets/generated/<package-id>/scene_XX.svg`.
2. Use a `1080x1920` viewBox/canvas (9:16 vertical).
3. Keep the SVG self-contained: no external images, remote fonts, scripts, network references, or embedded third-party assets.
4. Put its repository-relative path in `image_svg_source`.
5. Set `image_b64` to the ephemeral runner path `work/prepared_assets/<package-id>/scene_XX.b64`.
6. Do NOT create or commit that `.b64` file. `scripts/prepare_svg_assets.py` rasterizes the SVG to PNG inside GitHub Actions and creates the `.b64` file locally before the normal asset validator runs.
7. `image_sha256` is optional. Do not include a precomputed digest unless it was calculated from the exact PNG bytes produced by the same rasterization step. The renderer always computes the actual SHA-256 of the prepared image internally.

The renderer still performs strict base64 decoding, image parsing, path containment, source-size limits and normalization to 1080x1920 before TTS/rendering.

## Required schema

```json
{
  "id": "2026-09-17-am",
  "title": "internal title",
  "hook": "first spoken sentence",
  "narration": "complete narration",
  "scenes": [
    {
      "narration": "the narration beat represented by this scene",
      "visual": "English description of this scene",
      "image_svg_source": "assets/generated/2026-09-17-am/scene_01.svg",
      "image_b64": "work/prepared_assets/2026-09-17-am/scene_01.b64"
    }
  ],
  "caption": "TikTok/Shorts caption",
  "hashtags": ["tag1", "tag2"]
}
```

Legacy committed `.b64` assets and inline `image_base64` remain supported by the renderer for compatibility, but scheduled tasks MUST use SVG transport.

## Quality bar before push

- hook is immediately understandable;
- narration has a clear payoff;
- no unsupported statistics or fake quotations;
- no repeated topic from recent packages;
- 6-10 usable visual scenes;
- every visual description matches what is narrated;
- every scene has its own valid self-contained SVG asset;
- narration is at least 55 words;
- valid JSON and valid XML/SVG;
- all `image_svg_source` paths stay under the repository and exist before the manifest is committed.

During normal scheduled editorial runs, do not modify renderer code or workflow files.
