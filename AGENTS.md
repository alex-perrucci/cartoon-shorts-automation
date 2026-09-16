# Editorial task contract

This repository does NOT invent its own topics or generate creative artwork at render time. Scheduled ChatGPT tasks are the editorial + artwork layer.

Each scheduled run must create one complete content package consisting of:

- exactly one new UTF-8 JSON manifest under `input/`, such as `input/2026-09-17-am.json`;
- exactly one original SVG illustration per scene under `assets/generated/<package-id>/`, such as `scene_01.svg`.

The render workflow starts when the JSON manifest is committed. Create every SVG asset first and commit the `input/*.json` manifest LAST. An atomic multi-file commit is also acceptable. Never expose Actions to a manifest whose referenced SVG files do not yet exist.

## Editorial identity

The channel voice is critical, satirical, irreverent, provocative and anti-manipulation. The recurring promise is: expose a hidden commercial, psychological, product-design or platform mechanism in plain Italian and make the viewer feel `ah, quindi è fatto apposta`.

The benchmark tone is closer to `Proprio alla fine ti fottono meglio.` than to a neutral explainer such as `Perché succede questa cosa?`. Controlled profanity is allowed when it makes the hook or punchline stronger and still sounds natural. The narration may mock the mechanism, the marketing logic or the absurdity of the situation, but it must not invent crimes, fraud, intent or facts that the evidence does not support.

## Editorial rules

Before writing a package:

1. Inspect recent files under `input/` and avoid repeating the same topic, hook, core fact or visual sequence unless explicitly creating a revised A/B test.
2. Pick a topic that can be explained visually and understood without context.
3. Prefer hidden business mechanisms, retail tricks, pricing psychology, subscriptions, app/platform design, money, technology, unusual systems or useful surprising facts. Do not fabricate factual claims.
4. Verify factual claims when they are not common knowledge.
5. The opening hook is a HARD quality gate. It should normally be 4-9 spoken words, land in roughly the first 1-2 seconds, and sound like a reveal, accusation, contradiction or punchline rather than a lesson title.
6. Prefer hooks in the spirit of `Proprio alla fine ti fottono meglio.`, `Quel prezzo è lì per fregarti.`, `Ti fanno pagare perché sperano che dimentichi.`, `L'app non vuole che tu esca.` The exact wording must fit the evidence.
7. Avoid weak openings such as `Hai mai notato`, `Oggi ti spiego`, `Forse non sai`, `Lo sapevi che`, or a generic `Perché X?` when a sharper factual statement is possible.
8. Narration must begin with EXACTLY the `hook` field and deliver the first useful explanatory beat immediately. Do not spend the opening seconds restating the question.
9. HARD DURATION TARGET: the final video must be at least 60 seconds. Write normally 165-190 Italian words, never fewer than 150 words. Aim for roughly 60-80 seconds with the production voice.
10. Use short spoken sentences, punchy transitions and controlled sarcasm. It should feel like a sharp mini-rant with an explanation inside it, not a school lesson.
11. Build a mini conflict: viewer vs hidden mechanism. Then explain the mechanism, show a concrete example, explain the consequence, add at least one satirical jab, and close with a memorable payoff.
12. Split the narration into 7-10 meaningful scenes. Scene 1 must visually reinforce the hook immediately with one obvious focal idea; no generic establishing shot.
13. CRITICAL SYNC RULE: concatenating every `scene.narration` in order must reproduce the complete `narration` exactly, word for word and in the same order. Do not paraphrase or omit words inside scene narration. The renderer uses these exact boundaries to switch artwork in sync with the spoken audio.
14. Each scene should usually cover one semantic beat. Change the image when the spoken idea changes, not at arbitrary equal intervals.
15. Write every `visual` description in English and make it depict that scene's exact spoken beat, not merely the overall topic.
16. Create exactly one original vertical SVG illustration for every scene. Preserve the same recurring protagonist and visual grammar across the package: simple 2D editorial cartoon, warm cream/beige background, thick black outlines, sparse props, black suit/white shirt/black tie, minimal shading, no watermark, no third-party logos. Text inside the artwork should be avoided except when essential to the concept.
17. Keep scenes visually distinct while preserving the protagonist.
18. Caption should be short and continue the satirical/revealing angle. Hashtags should be few and relevant, not spammy.

## Hook templates

Templates are inspiration, not mandatory copy. Rotate structures so videos do not sound formulaic:

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

## Hook quality check before push

Reject and rewrite the package before committing if any of these are true:

- the first sentence is merely the topic phrased as a question;
- the opening sounds educational/neutral rather than revealing, critical or satirical;
- the viewer needs prior context to understand why the opening matters;
- the hook uses generic filler when a stronger direct claim is possible;
- the hook promises manipulation or intent that the narration/evidence cannot support;
- the payoff promised by the hook is not actually delivered;
- scene 1 does not make the opening idea visually obvious.

Ask one final question before push: `Would this line make someone stop scrolling because it sounds like somebody is exposing a trick and taking the piss out of it?` If not, rewrite it.

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
  "narration": "complete 150+ word narration beginning exactly with the hook",
  "scenes": [
    {
      "narration": "exact consecutive slice of the complete narration",
      "visual": "English description matching this exact spoken beat",
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
- tone is genuinely satirical/irreverent, not merely mildly critical;
- narration contains at least 150 words and is targeted for a 60-80 second final video;
- scene narrations concatenate exactly to the full narration;
- narration has a clear payoff and at least one real satirical jab;
- no unsupported statistics, fake quotations or invented allegations;
- 7-10 usable visual scenes;
- every visual description matches the exact words spoken during that scene;
- every scene has its own valid self-contained SVG asset;
- valid JSON and valid XML/SVG;
- all `image_svg_source` paths stay under the repository and exist before the manifest is committed.

During normal scheduled editorial runs, do not modify renderer code or workflow files.
