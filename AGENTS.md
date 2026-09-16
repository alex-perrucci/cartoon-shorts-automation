# Editorial task contract

This repository does NOT invent its own topics or generate scene artwork at render time. Scheduled ChatGPT tasks are the editorial + image-generation layer.

Each scheduled run must create one complete content package consisting of:

- exactly one new UTF-8 JSON manifest under `input/`, such as `input/2026-09-17-am.json`;
- one base64 text asset per scene under `assets/generated/<package-id>/`, such as `scene_01.b64`;
- every `.b64` file must contain the base64 encoding of the raw PNG/JPEG/WebP image bytes, with no Markdown fences and no explanatory text.

The render workflow starts when the JSON manifest is committed. Therefore the package must be committed atomically when possible. If the GitHub connector cannot make one atomic multi-file commit, create every `.b64` asset first and create the `input/*.json` manifest LAST so Actions never sees an incomplete package.

## Editorial rules

Before writing a package:

1. Inspect recent files under `input/` and avoid repeating the same topic, hook, core fact, or visual sequence.
2. Pick a topic that can be explained visually and understood without context.
3. Prefer evergreen curiosity, money/business mechanisms, psychology, technology, unusual systems, or useful surprising facts. Do not fabricate factual claims.
4. Verify factual claims when they are not common knowledge.
5. The first sentence must work as a strong spoken hook within about two seconds.
6. Write natural Italian narration intended for TTS, normally about 80-125 words and 35-60 seconds after synthesis.
7. Split it into 6-10 scenes. Each scene should correspond to a meaningful narration beat, not arbitrary equal chunks.
8. Write every `visual` prompt in English. It describes the action/props and is also the prompt used when creating the scene artwork.
9. Generate exactly one original vertical illustration for every scene. Preserve the same recurring protagonist and visual grammar across the package: simple 2D editorial cartoon, warm cream/beige background, thick black outlines, sparse props, black suit/white shirt/black tie, minimal shading, no embedded captions, no watermark, no logos.
10. Keep scenes visually distinct while preserving the protagonist.
11. Caption should be short. Hashtags should be few and relevant, not spammy.

## Asset rules

For every generated scene image:

1. Prefer PNG, JPEG, or WebP source images at a useful vertical resolution. Minimum accepted source side is 256 px.
2. Encode the RAW image bytes as standard base64 text.
3. Save the base64 text as `assets/generated/<package-id>/scene_XX.b64`.
4. Compute SHA-256 over the RAW decoded image bytes, not over the base64 text.
5. Put the lowercase 64-character SHA-256 digest in `image_sha256`.
6. Put the repository-relative `.b64` path in `image_b64`.
7. Never reuse a `.b64` file from an unrelated package just to make validation pass.
8. Do not commit binary image files; the renderer reconstructs normalized PNGs inside the GitHub runner.

The renderer rejects missing assets, invalid base64, path traversal, corrupt images, tiny images, oversized assets, and SHA-256 mismatches before TTS/rendering.

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
      "visual": "English prompt describing this scene",
      "image_b64": "assets/generated/2026-09-17-am/scene_01.b64",
      "image_sha256": "64-character lowercase sha256 of the raw image bytes"
    }
  ],
  "caption": "TikTok/Shorts caption",
  "hashtags": ["tag1", "tag2"]
}
```

`image_base64` inline is accepted by the renderer only as a compatibility fallback, but scheduled tasks MUST use separate `.b64` files so manifests stay readable.

## Quality bar before push

- hook is immediately understandable;
- narration has a clear payoff;
- no unsupported statistics or fake quotations;
- no repeated topic from recent packages;
- 6-10 usable visual scenes;
- every visual prompt matches what is being narrated;
- every scene has its own generated `.b64` asset and SHA-256;
- narration is at least 55 words;
- valid JSON, no Markdown fences in the JSON or `.b64` files;
- all referenced asset paths stay under the repository and exist before the manifest is committed.

During normal scheduled editorial runs, do not modify renderer code or workflow files.
