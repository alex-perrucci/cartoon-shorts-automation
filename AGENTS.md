# Editorial task contract

This repository does NOT invent its own topics or generate creative artwork at render time. Scheduled ChatGPT tasks are the editorial + artwork layer.

`AGENTS.md` is authoritative for package/editorial rules. `VISUAL_BIBLE_V2.md` is authoritative for the current art direction. Every scheduled run MUST read both before creating content. If an older prompt conflicts with either file, the repository files win.

Each scheduled run must create one complete content package consisting of:

- exactly one new UTF-8 JSON manifest under `input/`, such as `input/2026-09-17-am.json`;
- exactly one original self-contained SVG illustration per scene under `assets/generated/<package-id>/`;
- platform-specific publishing metadata for YouTube and TikTok.

The render workflow starts when the JSON manifest is committed. Create every SVG asset first and commit the `input/*.json` manifest LAST. An atomic multi-file commit is also acceptable. Never expose Actions to a manifest whose referenced SVG files do not yet exist.

## Editorial identity

The channel voice is critical, satirical, irreverent, provocative and anti-manipulation. The recurring promise is: expose a hidden commercial, psychological, product-design or platform mechanism in plain Italian and make the viewer feel `ah, quindi è fatto apposta`.

The benchmark tone is closer to `Proprio alla fine ti fottono meglio.` than to a neutral explainer such as `Perché succede questa cosa?`. Controlled profanity is allowed when it makes the hook or punchline stronger and still sounds natural. The narration may mock the mechanism, the marketing logic or the absurdity of the situation, but it must not invent crimes, fraud, intent or facts that the evidence does not support.

## Editorial rules

Before writing a package:

1. Inspect recent files under `input/` and avoid repeating the same topic, hook, core fact or visual sequence unless explicitly creating a revised A/B test.
2. Inspect the latest `Render cartoon short` workflow result. If the latest render failed because of a renderer/configuration problem, do not enqueue another package; report the blocker instead.
3. Pick a topic that can be explained visually and understood without context.
4. Prefer hidden business mechanisms, retail tricks, pricing psychology, subscriptions, app/platform design, money, technology, unusual systems or useful surprising facts. Do not fabricate factual claims.
5. Verify factual claims when they are not common knowledge.
6. The opening hook is a HARD quality gate. It should normally be 4-9 spoken words, land in roughly the first 1-2 seconds, and sound like a reveal, accusation, contradiction or punchline rather than a lesson title.
7. Prefer hooks in the spirit of `Proprio alla fine ti fottono meglio.`, `Quel prezzo è lì per fregarti.`, `Ti fanno pagare perché sperano che dimentichi.`, `L'app non vuole che tu esca.` The exact wording must fit the evidence.
8. Avoid weak openings such as `Hai mai notato`, `Oggi ti spiego`, `Forse non sai`, `Lo sapevi che`, or a generic `Perché X?` when a sharper factual statement is possible.
9. Narration must begin with EXACTLY the `hook` field and deliver the first useful explanatory beat immediately.
10. HARD DURATION TARGET: final video at least 60 seconds. Write normally 165-190 Italian words and NEVER fewer than 150 words. Aim for roughly 60-80 seconds with the production voice.
11. Use short spoken sentences, punchy transitions and controlled sarcasm. It should feel like a sharp mini-rant with an explanation inside it, not a school lesson.
12. Build a mini conflict: viewer vs hidden mechanism. Explain the mechanism, show a concrete example, explain the consequence, add at least one genuine satirical jab, and close with a memorable payoff.
13. Split narration into 7-10 meaningful scenes. Scene 1 must visually reinforce the hook immediately with one obvious focal idea; no generic establishing shot.
14. CRITICAL SYNC RULE: concatenating every `scene.narration` in order must reproduce the complete `narration` exactly, word for word and in the same order.
15. Each scene should cover one semantic beat. Change the image when the spoken idea changes, not at arbitrary equal intervals.
16. Write every `visual` description in English and make it depict that scene's exact spoken beat, not merely the overall topic.
17. Keep the legacy top-level `caption` and `hashtags`; they remain required by the renderer.

## V2 artwork contract — HARD quality gate

Read and follow `VISUAL_BIBLE_V2.md` in full before drawing anything.

The old simplistic SVG look is retired. New scheduled packages MUST use the V2 visual language:

- professional hand-sketched editorial comic;
- expressive recurring young-adult protagonist;
- messy dark hair, readable eyes/eyebrows, angular stylised face, black hoodie/casual jacket;
- warm cream paper base, black ink/dark clothing, restrained red accent;
- confident organic Bézier linework, imperfect hand-ink feel, flat/cel colour and restrained 2-3 tone shading;
- believable hands, shoulders, face and clothing folds;
- strong acting: pose, gaze, hands and facial expression must match the exact spoken beat;
- meaningful environmental context and props without clutter;
- continuity across scenes while changing pose, expression, camera angle and object focus deliberately.

Explicitly reject:

- stick figures;
- human anatomy assembled visibly from circles/rectangles/straight-line limbs;
- childish clip-art/cartoon construction;
- semi-photorealism, glossy anime, 3D or plastic rendering;
- the same neutral standing pose repeated across scenes;
- a static character staring at an object that has not yet entered the visual sequence;
- scenes that rely on text boxes because the drawing itself does not explain the beat.

### Motion-ready staging

Every scene is a key pose in a limited-animation storyboard, even though scheduled transport remains one SVG per scene today.

When one action continues across scenes, create a believable progression: notice object -> turn eyes/head -> inspect new object -> compare -> react -> address viewer. The character must visibly change acting between consecutive frames. The renderer's zoom/pan is only polish; never rely on camera movement to fake character motion.

### Artwork text

Avoid embedded text unless it is essential. Good uses are prices, weights, tiny UI labels or a very short 2-6 word punchline. Never paste narration paragraphs into the artwork or duplicate burned-in subtitles.

## Hook quality check before push

Reject and rewrite the package before committing if any of these are true:

- the first sentence is merely the topic phrased as a question;
- the opening sounds educational/neutral rather than revealing, critical or satirical;
- the viewer needs prior context to understand why the opening matters;
- the hook uses generic filler when a stronger direct claim is possible;
- the hook promises manipulation or intent that the narration/evidence cannot support;
- the payoff promised by the hook is not delivered;
- scene 1 does not make the opening idea visually obvious.

Ask one final question before push: `Would this line make someone stop scrolling because it sounds like somebody is exposing a trick and taking the piss out of it?` If not, rewrite it.

## Platform metadata

Every new scheduled package MUST include both `youtube` and `tiktok` objects.

### YouTube

- `youtube.title`: punchy, specific, curiosity-driven, max 100 characters.
- `youtube.description`: 1-3 concise sentences explaining the value without spoiling every beat.
- `youtube.hashtags`: normally 3-5 relevant hashtags; no broad spam.
- `youtube.tags`: normally 5-12 useful search phrases/keywords without `#`.
- Do not mechanically copy the TikTok caption into the YouTube title.

YouTube is uploaded automatically as `private`, so metadata must already be production-ready before the manifest is pushed.

### TikTok

- `tiktok.caption`: short, conversational and satirical; it can extend the joke/reveal rather than repeat the hook verbatim.
- `tiktok.hashtags`: normally 3-6 relevant hashtags.
- Do not add generic spam such as `#fyp` unless genuinely useful.

The TikTok Content Posting draft endpoint does not populate the caption/hashtags from this manifest. Still generate and retain them accurately for the final edit.

## Hook templates

Templates are inspiration, not mandatory copy. Rotate structures:

1. `Proprio alla fine ti fottono meglio.`
2. `Ti stanno fregando così.`
3. `Questa cosa è fatta apposta.`
4. `Non stai scegliendo davvero tu.`
5. `Quel prezzo è una trappola.`
6. `Ti fanno spendere di più così.`
7. `Sembra comodo. Invece ti frega.`
8. `La vera inculata arriva dopo.`
9. `Questo trucco vive della tua distrazione.`
10. `Paghi perché sperano che dimentichi.`

Do not mechanically reuse the same template in consecutive packages.

## Artwork transport rules

SVG is the canonical scheduled-task transport format because it is UTF-8 text and can be committed losslessly through the GitHub connector.

For every scene:

1. Save artwork as `assets/generated/<package-id>/scene_XX.svg`.
2. Use a `1080x1920` viewBox/canvas (9:16 vertical).
3. Keep SVG self-contained: no external images, remote fonts, scripts, network references, `foreignObject`, file URLs, raster data URIs or embedded third-party assets.
4. Put its repository-relative path in `image_svg_source`.
5. Set `image_b64` to `work/prepared_assets/<package-id>/scene_XX.b64`.
6. Do NOT create/commit that `.b64`; `scripts/prepare_svg_assets.py` rasterizes the SVG inside Actions and creates it transiently.
7. Normally omit `image_sha256`; include it only if calculated from the exact rasterized PNG bytes.
8. Follow the SVG craft rules in `VISUAL_BIBLE_V2.md`: organic `<path>` silhouettes for anatomy, layered groups, round joins/caps, controlled cel shading and sparse sketch/hatching accents.

## Required schema

```json
{
  "id": "2026-09-17-am",
  "title": "internal title",
  "hook": "short critical/satirical first spoken sentence",
  "narration": "complete 150+ word narration beginning exactly with the hook",
  "scenes": [
    {
      "narration": "exact consecutive slice of the complete narration",
      "visual": "English description matching this exact spoken beat and V2 acting/staging",
      "image_svg_source": "assets/generated/2026-09-17-am/scene_01.svg",
      "image_b64": "work/prepared_assets/2026-09-17-am/scene_01.b64"
    }
  ],
  "caption": "legacy short caption",
  "hashtags": ["tag1", "tag2"],
  "youtube": {
    "title": "YouTube Shorts title",
    "description": "YouTube description",
    "hashtags": ["marketing", "psicologia", "soldi"],
    "tags": ["marketing", "psicologia dei consumi", "trucchi supermercato"]
  },
  "tiktok": {
    "caption": "TikTok-ready caption",
    "hashtags": ["marketing", "psicologia", "supermercato"]
  }
}
```

Legacy committed `.b64` assets and inline `image_base64` remain supported for compatibility, but scheduled tasks MUST use SVG transport.

## Quality bar before push

Reject/redraw/rewrite before committing unless ALL applicable checks pass:

- hook is immediately understandable and genuinely critical/satirical;
- narration begins exactly with hook and reaches explanation immediately;
- 150+ words, targeted for 60-80 seconds;
- scene narrations concatenate exactly to full narration;
- clear payoff and at least one real satirical jab;
- no unsupported statistics, fake quotations or invented allegations;
- 7-10 meaningful scenes;
- every visual matches its exact spoken beat;
- every scene has its own valid self-contained SVG;
- protagonist passes the V2 professional-character test in `VISUAL_BIBLE_V2.md`;
- expressions, gaze, hands and poses change meaningfully with the sequence;
- no childish geometry, clip-art anatomy, glossy anime or photoreal rendering;
- YouTube metadata complete and within limits;
- TikTok caption/hashtags complete;
- valid JSON and XML/SVG;
- all `image_svg_source` paths exist before manifest commit.

During a normal scheduled editorial run, do not modify renderer code, workflow files, `AGENTS.md` or `VISUAL_BIBLE_V2.md`.
