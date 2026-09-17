# Editorial task contract

Scheduled ChatGPT tasks are the editorial + artwork layer. The renderer does not invent topics or artwork.

`AGENTS.md` is authoritative for packaging/editorial rules. `VISUAL_BIBLE_V2.md` is authoritative for art direction. Every scheduled run MUST read both before creating anything. Repository rules override older scheduler wording.

## Package per scheduled run

Create exactly one complete package:

- one new UTF-8 manifest under `input/YYYY-MM-DD-am.json` or `input/YYYY-MM-DD-pm.json`;
- original self-contained SVG artwork under `assets/generated/<package-id>/`;
- production-ready YouTube + TikTok metadata.

Create all SVGs first and the manifest LAST, unless using one atomic commit. Never expose Actions to a manifest that references missing artwork.

## Before creating content

1. Inspect recent `input/` manifests and avoid repeating topic, hook, fact or visual sequence unless explicitly doing an A/B revision.
2. Inspect the latest `Render cartoon short` workflow. If it failed because of renderer/configuration, do not enqueue another package; report the blocker.
3. Pick one evergreen Italian topic that is visually explainable without prior context.
4. Prefer hidden business mechanisms, retail/pricing psychology, subscriptions, product/platform design, money, technology or useful surprising systems.
5. Verify non-obvious factual claims. Never invent fraud, crimes, intent, statistics or certainty unsupported by evidence.

## Editorial identity — HARD gate

Voice: critical, satirical, irreverent, provocative, anti-manipulation. Benchmark: closer to `Proprio alla fine ti fottono meglio.` than to a neutral explainer.

Controlled profanity (`fottono`, `fregano`, `inculata`, `spillarti soldi`) is allowed when natural and factually defensible.

Hook rules:

- normally 4-9 spoken words;
- immediate reveal/accusation/contradiction/punchline;
- narration begins with EXACTLY the hook;
- no weak `Hai mai notato`, `Oggi ti spiego`, `Forse non sai`, `Lo sapevi che`, or bland `Perché X?` when a stronger factual line exists.

Narration rules:

- target 165-190 Italian words; NEVER fewer than 150;
- final video must be at least 60 seconds;
- mini conflict: viewer vs hidden mechanism;
- explain mechanism, concrete example, consequence, at least one genuine satirical jab, memorable payoff;
- short spoken sentences and punchy transitions;
- split into 7-10 meaningful semantic scenes;
- Scene 1 must visually reinforce the hook immediately.

CRITICAL SYNC RULE: concatenating every `scene.narration` in order must reproduce the full `narration` exactly, word for word and in the same order.

Each `visual` description must be in English and depict that exact spoken beat.

## V2 visual system — HARD gate

Read `VISUAL_BIBLE_V2.md` in full.

The old simplistic SVG character is retired. Every new scene must look like a professionally drawn hand-sketched editorial comic:

- recurring young-adult protagonist;
- messy dark hair, readable expressive eyes/eyebrows, angular stylised face;
- black hoodie/casual jacket;
- warm cream paper base, black/dark ink masses, restrained red accents;
- organic Bézier paths and confident imperfect hand-ink lines;
- believable face, hands, shoulders and clothing folds;
- restrained 2-3 tone cel shading/hatching;
- pose, gaze, hands and expression must act the narration;
- strong vertical composition and contextual props;
- preserve character identity while varying pose, expression, angle and object focus.

Reject before push: stick figures, anatomy visibly assembled from circles/rectangles/straight limbs, childish clip-art, glossy anime, semi-photorealism, 3D/plastic rendering, repeated neutral poses, continuity errors, or scenes that need paragraphs of embedded text to explain themselves.

## V2 pose-to-pose motion

The renderer supports optional pose keyframes INSIDE a semantic scene. Use them to create actual limited character motion instead of relying on camera zoom.

For character-led scenes, normally create **2-3 keyframes** (maximum 4). Each keyframe is a full 1080x1920 SVG key pose of the same scene/character/environment, with a meaningful acting change such as:

`notice -> eyes/head turn -> inspect -> compare -> react -> address viewer`

Do not create fake changes where only text moves. Across keyframes, change at least one meaningful element: gaze, head angle, mouth/expression, hand/arm action, body lean, prop position or object focus.

For a purely diagram/object/insert scene where character acting would add nothing, keyframes are optional and a single hero SVG is allowed.

### Keyframe transport

Every scene keeps the legacy primary asset fields for backward compatibility:

- `image_svg_source`
- `image_b64`

When `keyframes` is present, it MUST contain 2-4 objects. The primary fields SHOULD point to the first keyframe asset. Each keyframe object contains its own `image_svg_source` and transient `image_b64` path.

Naming convention:

- `assets/generated/<package-id>/scene_01_pose_01.svg`
- `assets/generated/<package-id>/scene_01_pose_02.svg`
- `assets/generated/<package-id>/scene_01_pose_03.svg`

and transient runner paths:

- `work/prepared_assets/<package-id>/scene_01_pose_01.b64`
- etc.

The renderer divides the semantic scene window across these key poses and cuts between them in order, while retaining subtle camera motion. Therefore order the keyframes as a coherent action progression.

## SVG transport rules

SVG is the only scheduled-task artwork transport format.

For every SVG:

- 1080x1920 canvas/viewBox;
- valid UTF-8 XML;
- self-contained local vector primitives/paths;
- no scripts, `foreignObject`, remote URLs, external fonts/images, file URLs, raster data URIs, PNG/JPEG/WebP, inline base64 or third-party assets;
- prefer organic `<path>` shapes for visible anatomy;
- use round joins/caps and layered cel-shading groups;
- optional artwork text only when essential: prices, weights, tiny UI labels or short 2-6 word punchlines.

Do NOT create/commit `.b64`; `scripts/prepare_svg_assets.py` rasterizes SVGs inside Actions. Normally omit `image_sha256`.

## Platform metadata

Every package MUST include:

### YouTube

- punchy Shorts title <=100 chars;
- concise 1-3 sentence description;
- 3-5 relevant hashtags;
- 5-12 useful search tags;
- do not mechanically copy the TikTok caption.

YouTube upload is private, so metadata must be production-ready before push.

### TikTok

- short conversational/satirical caption;
- 3-6 relevant hashtags;
- no generic spam such as `#fyp` unless genuinely useful.

TikTok draft upload does not populate caption/hashtags automatically; still retain them in the manifest.

Keep legacy top-level `caption` and `hashtags` too.

## Required schema

```json
{
  "id": "2026-09-18-am",
  "title": "internal title",
  "hook": "short satirical first spoken sentence",
  "narration": "complete 150+ word narration beginning exactly with hook",
  "scenes": [
    {
      "narration": "exact sequential narration slice",
      "visual": "English description of exact beat and acting progression",
      "image_svg_source": "assets/generated/2026-09-18-am/scene_01_pose_01.svg",
      "image_b64": "work/prepared_assets/2026-09-18-am/scene_01_pose_01.b64",
      "keyframes": [
        {
          "image_svg_source": "assets/generated/2026-09-18-am/scene_01_pose_01.svg",
          "image_b64": "work/prepared_assets/2026-09-18-am/scene_01_pose_01.b64"
        },
        {
          "image_svg_source": "assets/generated/2026-09-18-am/scene_01_pose_02.svg",
          "image_b64": "work/prepared_assets/2026-09-18-am/scene_01_pose_02.b64"
        }
      ]
    }
  ],
  "caption": "legacy caption",
  "hashtags": ["tag1", "tag2"],
  "youtube": {
    "title": "YouTube title",
    "description": "YouTube description",
    "hashtags": ["marketing", "psicologia", "soldi"],
    "tags": ["marketing", "psicologia dei consumi", "prezzi"]
  },
  "tiktok": {
    "caption": "TikTok caption",
    "hashtags": ["marketing", "psicologia", "soldi"]
  }
}
```

Legacy packages without `keyframes` remain supported.

## Final quality gate before push

Reject/rewrite/redraw unless ALL applicable checks pass:

- hook is sharp, understandable and evidence-compatible;
- narration starts exactly with hook and is 150+ words;
- scene narrations exactly reconstruct full narration;
- 7-10 semantic scenes;
- factual claims verified where needed;
- every visual matches its spoken beat;
- every referenced SVG exists before manifest commit;
- protagonist passes `VISUAL_BIBLE_V2.md` professional-quality test;
- character-led scenes normally have 2-3 coherent pose keyframes;
- keyframes genuinely change acting/focus and do not introduce continuity errors;
- no childish geometry, glossy anime or realism drift;
- YouTube/TikTok metadata complete;
- valid JSON and XML/SVG.

During a normal scheduled run, do not modify renderer/workflow code, `AGENTS.md` or `VISUAL_BIBLE_V2.md`.
