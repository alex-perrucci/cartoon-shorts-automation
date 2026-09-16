# Editorial task contract

This repository does NOT invent its own topics. Scheduled ChatGPT tasks are the editorial layer.

For each run, create exactly one new UTF-8 JSON file under `input/` using a unique filename such as `2026-09-17-am.json` or `2026-09-17-pm.json`.

Before writing a package:

1. Inspect recent files under `input/` and avoid repeating the same topic, hook, core fact, or visual sequence.
2. Pick a topic that can be explained visually and understood without context.
3. Prefer evergreen curiosity, money/business mechanisms, psychology, technology, unusual systems, or useful surprising facts. Do not fabricate factual claims.
4. The first sentence must work as a strong spoken hook within about two seconds.
5. Write natural Italian narration intended for TTS, normally about 80-125 words and 35-60 seconds after synthesis.
6. Split it into 6-10 scenes. Each scene should correspond to a meaningful narration beat, not arbitrary equal chunks.
7. Write every `visual` prompt in English. It must describe the action/props only; the renderer adds the global recurring-character style.
8. Keep scenes visually distinct while preserving one recurring protagonist.
9. Do not put text, labels, UI copy, watermarks, or logos inside image prompts unless the concept is impossible without them.
10. Caption should be short. Hashtags should be few and relevant, not spammy.

Required schema:

```json
{
  "id": "unique-id",
  "title": "internal title",
  "hook": "first spoken sentence",
  "narration": "complete narration",
  "scenes": [
    {
      "narration": "the narration beat represented by this scene",
      "visual": "English prompt describing this scene"
    }
  ],
  "caption": "TikTok/Shorts caption",
  "hashtags": ["tag1", "tag2"]
}
```

Quality bar before push:

- hook is immediately understandable;
- narration has a clear payoff;
- no unsupported statistics or fake quotations;
- no repeated topic from recent packages;
- 6-10 usable visual scenes;
- every visual prompt matches what is being narrated;
- narration is at least 55 words;
- valid JSON, no Markdown fences in the file.

Push only the new package. Do not modify renderer code during normal scheduled editorial runs.
