# Editorial task contract

This repository does NOT invent its own topics or generate creative artwork at render time. Scheduled ChatGPT tasks are the editorial + artwork layer.

Each scheduled run must create one complete content package consisting of:

- exactly one new UTF-8 JSON manifest under `input/`, such as `input/2026-09-17-am.json`;
- exactly one original SVG illustration per scene under `assets/generated/<package-id>/`, such as `scene_01.svg`.

The render workflow starts when the JSON manifest is committed. Create every SVG asset first and commit the `input/*.json` manifest LAST. An atomic multi-file commit is also acceptable. Never expose Actions to a manifest whose referenced SVG files do not yet exist.

## Editorial identity

The channel voice is critical, satirical, provocative and anti-manipulation. The recurring promise is: expose a hidden commercial, psychological, product-design or platform mechanism in plain Italian and make the viewer feel `ah, quindi è fatto apposta`.

Be punchy without becoming conspiratorial or making unsupported accusations. Strong wording is welcome when the underlying mechanism is factual. Prefer `ti spingono`, `ti guidano`, `è fatto apposta`, `questa è la trappola`, `ti fanno spendere di più`, or similar language over neutral classroom phrasing. Never invent illegality, fraud, intent or causal certainty that the evidence does not support.

## Editorial rules

Before writing a package:

1. Inspect recent files under `input/` and avoid repeating the same topic, hook, core fact, or visual sequence.
2. Pick a topic that can be explained visually and understood without context.
3. Prefer hidden business mechanisms, retail tricks, pricing psychology, subscriptions, app/platform design, money, technology, unusual systems, or useful surprising facts. Do not fabricate factual claims.
4. Verify factual claims when they are not common knowledge.
5. The opening hook is a HARD quality gate. It should normally be 4-9 spoken words, land in roughly the first 1-2 seconds, and sound like a reveal, accusation, contradiction or consequence rather than a lesson title.
6. Prefer hooks in the spirit of `La cassa è l'ultima trappola.`, `Quel prezzo è fatto per fregarti.`, `L'app non vuole che tu esca.`, `Ti fanno spendere di più così.` The exact wording must fit the evidence and must not overclaim.
7. Avoid weak openings such as `Hai mai notato`, `Oggi ti spiego`, `Forse non sai`, `Lo sapevi che`, or a generic `Perché X?` when a sharper factual statement is possible.
8. Narration must begin with EXACTLY the `hook` field and deliver the first useful explanatory beat immediately. Do not spend the first several seconds restating the question.
9. Write natural spoken Italian, normally about 80-125 words and roughly 35-60 seconds after synthesis. Short sentences and controlled sarcasm are preferred over academic prose.
10. Build a mini conflict: viewer vs hidden mechanism. Then explain the mechanism, show a concrete example, explain the consequence, and close with a memorable payoff.
11. Split the narration into 6-10 meaningful scenes. Scene 1 must visually reinforce the hook immediately with one obvious focal idea; no generic establishing shot.
12. Write every `visual` description in English.
13. Create exactly one original vertical SVG illustration for every scene. Preserve the same recurring protagonist and visual grammar across the package: simple 2D editorial cartoon, warm cream/beige background, thick black outlines, sparse props, black suit/white shirt/black tie, minimal shading, no watermark, no third-party logos. Text inside the artwork should be avoided except when essential to the concept.
14. Keep scenes visually distinct while preserving the protagonist.
15. Caption should be short and continue the satirical/revealing angle. Hashtags should be few and relevant, not spammy.

## Hook templates

Templates are inspiration, not mandatory copy. Rotate structures so videos do not sound formulaic:

1. `Ti stanno fregando così.`
2. `Questa cosa è fatta apposta.`
3. `Non stai scegliendo davvero tu.`
4. `Quel prezzo è una trappola.`
5. `Ti fanno spendere di più così.`
6. `Sembra comodo. Invece ti frega.`
7. `La vera trappola arriva dopo.`
8. `Questo trucco vive della tua distrazione.`
9. `L'app non vuole che tu esca.`
10. `Paghi perché sperano che dimentichi.`

Do not mechanically reuse the same template in consecutive packages.

## Hook quality check before push

Reject and rewrite the package before committing if any of these are true:

- the first sentence is merely the topic phrased as a question;
- the opening sounds educational/neutral rather than revealing, critical or satirical;
- the viewer needs prior context to understand why the opening matters;
- the hook uses generic filler when a stronger direct claim is possible;
- the hook promises manipulation or intent that the narration/evidence cannot support;
- the payoff promised by the hook is not actually delivered;
- scene 1 does not make the opening idea visually obvious.

Ask one final question before push: `Would this line make someone stop scrolling because it feels like a hidden trick is being exposed?` If not, rewrite it.

## Artwork transport rules

SVG is the canonical transport format because it is UTF-8 text and can be committed losslessly through the GitHub connector.

For every scene:

1. Save the artwork as `assets/generated/<package-id>/scene_XX.svg`.
2. Use a `1080x1920` viewBox/canvas (9:16 vertical).
3. Keep the SVG self-contained: no external images, remote fonts, scripts, network references, `foreignObject`, file URLs, raster data URIs, or embedded third-party assets.
4. Put its repository-relative path in `image_svg_source`.
5. Set `image_b64` to the ephemeral runner path `work/prepared_assets/<package-id>/scene_XX.b64`.
6. Do NOT create or commit that `.b64` file. `scripts/prepare_svg_assets.py` rasterizes the SVG to PNG inside GitHub Actions and creates the `.b64` file locally before the normal asset validator runs.
7. `image_sha256` is optional. Do not include a precomputed digest unless it was calculated from the exact PNG bytes produced by the same rasterization step. The renderer always computes the actual SHA-256 internally.

The renderer still performs strict base64 decoding, image parsing, path containment, source-size limits and normalization to 1080x1920 before TTS/rendering.

## Required schema

```json
{
  "id": "2026-09-17-am",
  "title": "internal title",
  "hook": "short critical/satirical first spoken sentence",
  "narration": "complete narration beginning exactly with the hook",
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

- hook is immediately understandable and passes the satirical hook quality gate;
- narration begins with exactly the hook and reaches the explanation immediately;
- tone is critical/satirical without unsupported allegations;
- narration has a clear payoff;
- no unsupported statistics or fake quotations;
- no repeated topic, hook structure, core fact or visual sequence from recent packages;
- 6-10 usable visual scenes;
- every visual description matches what is narrated;
- every scene has its own valid self-contained SVG asset;
- narration is at least 55 words;
- valid JSON and valid XML/SVG;
- all `image_svg_source` paths stay under the repository and exist before the manifest is committed.

During normal scheduled editorial runs, do not modify renderer code or workflow files.
