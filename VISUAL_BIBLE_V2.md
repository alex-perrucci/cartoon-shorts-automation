# Ti fregano così — Visual Bible V2

This file is the visual authority for every newly scheduled cartoon short. `AGENTS.md` defines the editorial/packaging contract; this file defines what the artwork must look and feel like.

## North star

The target is a polished **hand-sketched editorial comic**, not realism, not glossy anime, not clip-art and not a child's drawing.

Think: a strong magazine/cartoon storyboard drawn by a professional illustrator, with expressive acting, confident ink, warm flat colour, a little visual roughness and a clear satirical point in every frame.

The image must read instantly on a phone, but reward a second look with good anatomy, facial acting, composition and small contextual details.

## Hard visual gate

Reject and redraw a scene before push if any of these are true:

- the protagonist is built from circles, rectangles and stick limbs;
- anatomy, hands or face look childish, generic or mechanically assembled;
- the character is semi-photorealistic, glossy, 3D, hyper-rendered or anime-like;
- the scene is only a static person standing next to a label;
- the pose does not communicate the spoken beat;
- the expression is neutral when the narration implies suspicion, disbelief, irritation, smugness or accusation;
- the background is empty without a compositional reason;
- all scenes reuse effectively the same pose/camera angle;
- text is doing the explanatory work that the illustration should do;
- the frame contains decorative clutter that weakens the focal idea.

A scene should look like it came from the same accomplished cartoonist as the rest of the package.

## Recurring protagonist

Use one recognisable young-adult protagonist throughout the channel.

Default design:

- male-presenting young adult, roughly early twenties;
- slim/average build with believable shoulder, neck and hand anatomy;
- messy dark brown/black hair with a strong silhouette and several hand-drawn locks;
- expressive dark eyebrows;
- large but not chibi eyes, with visible whites/pupils so gaze direction is readable;
- slightly angular jaw and nose; handsome in a stylised cartoon way, never photorealistic;
- black hoodie or black casual jacket as the default outfit;
- small white `TI FREGANO COSÌ` mark on the chest may appear when composition allows, but it is not mandatory in every frame;
- no suit/tie as the default V2 costume.

The protagonist is not a mascot frozen in one model-sheet pose. Preserve identity while changing acting aggressively from scene to scene.

## Acting and pose language

The character must **act the narration**.

Useful recurring acting beats:

- side-eye at a suspicious price or UI;
- raised eyebrow with one corner of the mouth tightened;
- leaning closer to inspect something;
- holding two objects at different heights to compare them;
- palm-up `ma mi prendi per il culo?` gesture;
- finger pointing to the mechanism, not randomly at the viewer;
- direct-to-camera look only when the narration addresses the viewer or lands the punchline;
- shoulders/head turning toward the new object when the visual focus changes;
- final confident or knowing expression rather than generic anger.

Hands matter. If a hand is prominent, draw a readable palm/fingers/grip instead of a mitten or five straight sticks.

## Drawing language

### Line work

- Strong, hand-inked contour language.
- Use organic cubic Bézier paths for faces, hair, clothes, hands and important props.
- Allow small irregularities so the result feels drawn, not CAD-perfect.
- Main silhouette strokes should usually feel heavier than interior detail lines.
- Add sparse short hatching, crease lines, motion ticks and sketch accents where they improve form or emphasis.
- Avoid perfectly uniform outlines everywhere.

### Shape construction

- Primitive SVG shapes are fine for signs, shelves and simple props.
- Do **not** construct visible human anatomy from obvious circles/rectangles/straight-line limbs.
- Hair should be a designed silhouette with layered locks, not one ellipse.
- Faces should have a real cheek/jaw silhouette and separate nose/eyebrow/eye shapes.
- Clothing needs folds at shoulders, elbows and torso so it feels worn by a body.

### Colour

Core palette:

- warm cream / paper: `#F3E6CC` / `#F7EDD9`;
- ink: `#171512`;
- hoodie/dark masses: `#171717`, `#292725`;
- skin base: around `#E7A16F` / `#F1B17F` with one darker shadow tone;
- red accent: `#D74332` / `#C93228`;
- muted supermarket/environment greys and browns rather than rainbow colour.

Use flat colour with restrained 2-3 tone shading. Shadows can be graphic shapes or sparse hatching. Avoid glossy airbrush rendering, heavy gradients, plastic highlights and pseudo-3D skin.

## Composition

Every 1080x1920 frame needs one dominant idea.

Preferred structure:

1. one clear protagonist action or object comparison;
2. one secondary contextual element that explains where/why;
3. one accent element for the punchline (price tag, arrow, crossed label, app button, receipt, etc.).

Use foreground/midground/background when useful. A supermarket should feel like a supermarket, an app should feel like a phone interaction, a subscription should have believable billing/UI cues — but simplify everything that does not serve the spoken beat.

Vary framing across a package:

- medium close-up;
- waist-up action;
- over-the-shoulder inspection;
- object comparison insert;
- wider contextual frame;
- direct-to-camera payoff.

Do not alternate randomly. Camera choice must support the beat.

## Text inside artwork

Text is optional and secondary.

Good uses:

- a price (`2,49 €`);
- a weight (`200 g`, `150 g`);
- a tiny UI label or button;
- a 2-6 word satirical punchline;
- one concise comparison label.

Bad uses:

- pasting narration paragraphs into the frame;
- repeating subtitles already burned into the video;
- using multiple explanatory boxes because the illustration is unclear.

Whenever possible, make the image understandable before reading any embedded text.

## Satirical visual grammar

The art should expose the mechanism visually, not merely decorate it.

Examples:

- same `2,49 €` price tag under visibly smaller packaging;
- cancel button shrinking or sliding away while the renewal button grows;
- loyalty points transformed into a leash/maze metaphor;
- a `gratis` sign in front while a recurring charge quietly appears behind it;
- a progress bar that visually resets when the user tries to leave;
- a giant default option physically crowding a smaller opt-out.

Metaphors should be immediately legible and factually faithful. Never draw criminal/fraud imagery unless the factual claim actually supports it.

## Scene-to-scene continuity

Preserve:

- protagonist face/hair identity;
- outfit family;
- ink/shading language;
- cream + black + red palette;
- object continuity when the same example spans multiple scenes.

Change deliberately:

- pose;
- facial expression;
- gaze direction;
- hand action;
- camera distance/angle;
- object position;
- background emphasis.

A package should feel like a storyboard sequence, not eight unrelated illustrations and not eight copies of one illustration.

## Motion-ready staging

Even while scheduled transport remains SVG-per-scene, compose every scene as if it were a key pose in limited animation.

Across consecutive scenes, create believable pose progression when the same action continues. Example:

1. protagonist notices the 200 g packet;
2. eyes/head turn to the price;
3. a 150 g packet becomes the new focus and the expression changes;
4. both packets are held together for comparison;
5. protagonist turns to camera for the payoff.

Do not create continuity errors such as the protagonist staring at an object before it exists in the visual sequence.

The renderer may add camera movement, but the illustration itself must carry the acting. Never rely on zoom/pan to fake character motion.

## SVG craft requirements

Scheduled artwork must remain self-contained SVG as required by `AGENTS.md`.

For character art:

- prefer `<path>` with cubic Bézier curves for silhouettes and anatomy;
- use `<g>` groups with descriptive ids such as `character`, `face`, `hair`, `left-hand`, `prop`, `background`;
- use layered fills for simple cel shading;
- use `stroke-linecap="round"` and `stroke-linejoin="round"` on hand-drawn lines;
- use short accent paths for hatching, folds and motion marks;
- keep the SVG deterministic, local and easy for CairoSVG to rasterise.

Do not use scripts, `foreignObject`, remote references, embedded raster data, external fonts or network resources.

## Final V2 checklist

Before committing a package, ask:

1. Does the protagonist look like a professionally drawn recurring character rather than an SVG stick figure?
2. Can I read the emotion and gaze direction instantly?
3. Does the pose physically express this exact narration beat?
4. Is the visual mechanism obvious without relying on subtitles?
5. Is the frame sketchy/editorial rather than realistic, glossy or childish?
6. Is the composition strong enough for a vertical phone screen?
7. Is this scene visibly different from the previous one while preserving character identity?
8. Would this frame still look intentional if printed as a comic panel?

If any important answer is no, redraw before push.
