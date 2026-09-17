# Ti fregano così — Visual Bible V2

This file is the visual authority for every newly scheduled cartoon short. `AGENTS.md` defines editorial/packaging rules; this file defines how the artwork must look and act.

## North star

Target a polished **hand-sketched editorial comic**: professional, expressive, slightly rough, instantly readable on a phone.

Not realism. Not glossy anime. Not 3D. Not clip-art. Not a child's drawing.

Think of a strong magazine/cartoon storyboard: confident ink, warm flat colour, good anatomy, clear facial acting, dynamic composition, and one satirical visual point per frame.

## Hard visual gate

Reject and redraw before push if:

- the protagonist is visibly built from circles, rectangles or stick limbs;
- face, hands or anatomy look childish, generic or mechanically assembled;
- rendering drifts toward photorealism, glossy anime, plastic 3D or airbrushed skin;
- pose/expression do not communicate the spoken beat;
- the character simply stands next to a label;
- all frames reuse the same pose/camera angle;
- text is explaining what the illustration failed to show;
- the background is empty without a compositional reason;
- continuity is wrong (for example the character reacts to an object before it appears).

Every frame should look like it came from the same accomplished cartoonist.

## Recurring protagonist

Use one recognisable young-adult protagonist throughout the channel:

- male-presenting, early-twenties feel;
- slim/average build with believable neck, shoulder and hand anatomy;
- messy dark brown/black hair with a strong silhouette and hand-drawn locks;
- expressive dark eyebrows;
- large readable eyes, but never chibi;
- angular stylised jaw/nose;
- black hoodie or black casual jacket;
- optional small white `TI FREGANO COSÌ` chest mark when composition allows.

No suit/tie as the default V2 costume.

Preserve identity while changing acting aggressively. He is a recurring character, not a frozen mascot.

## Acting language

The character must **act the narration**.

Useful beats:

- side-eye at a suspicious price/UI;
- raised eyebrow and tightened mouth;
- lean closer to inspect;
- compare two objects at different heights;
- palm-up `ma mi prendi per il culo?` gesture;
- head/eyes turn toward a new object;
- point at the mechanism, not randomly at camera;
- direct-to-camera only when narration addresses the viewer or lands the payoff;
- finish with a knowing/confident expression rather than generic rage.

Hands matter. Prominent hands need readable fingers, grip and palm structure, not mittens or straight sticks.

## Drawing language

### Line work

- strong hand-inked contours;
- organic cubic Bézier paths for face, hair, clothes, hands and important props;
- small irregularities are desirable: drawn, not CAD-perfect;
- heavier outer silhouette, lighter interior detail;
- sparse hatching, fold lines, motion ticks and sketch accents;
- round line joins/caps where appropriate.

### Shape construction

Primitive SVG shapes are fine for signs, shelves and simple props. Do **not** use them as the visible construction language for human anatomy.

Hair needs a designed silhouette with layered locks. Faces need a real cheek/jaw contour plus separate nose, eyebrow and eye shapes. Clothes need shoulder/elbow/torso folds so they feel worn by a body.

### Colour

Core palette:

- paper: `#F3E6CC`, `#F7EDD9`;
- ink: `#171512`;
- dark clothing: `#171717`, `#292725`;
- skin base: around `#E7A16F`, `#F1B17F` plus one darker shadow tone;
- red accent: `#D74332`, `#C93228`;
- muted environmental greys/browns.

Use flat colour with restrained 2-3 tone cel shading or sparse hatching. Avoid heavy gradients, plastic highlights and pseudo-3D skin.

## Composition

Every 1080x1920 frame needs one dominant idea:

1. one clear protagonist action or object comparison;
2. one contextual element explaining where/why;
3. one accent element for the mechanism/punchline (price, arrow, receipt, app button, crossed label, etc.).

Use foreground/midground/background when useful. Simplify anything that does not serve the beat.

Vary framing intentionally:

- medium close-up;
- waist-up action;
- over-the-shoulder inspection;
- object comparison insert;
- wider contextual frame;
- direct-to-camera payoff.

## Text inside artwork

Text is secondary.

Good uses: a price, weight, tiny UI label, or 2-6 word punchline.

Bad uses: narration paragraphs, duplicated subtitles, or multiple explanation boxes because the drawing is unclear.

The image should make sense before the viewer reads embedded text.

## Satirical visual grammar

The art exposes the mechanism, not merely decorates the narration.

Examples:

- same `2,49 €` tag under visibly smaller packaging;
- cancel button shrinking while renewal grows;
- points/loyalty metaphorically becoming a leash or maze;
- `gratis` in front while a recurring charge appears behind;
- a dominant default option physically crowding out opt-out.

Visual metaphors must remain factually faithful. Never imply fraud/criminality without evidence.

## Pose-to-pose limited animation

Character-led semantic scenes should normally contain **2-3 full-frame key poses** (maximum 4). Each key pose is a self-contained 1080x1920 SVG using the same character, environment and object continuity.

The goal is meaningful acting progression, not decorative movement.

Good progression:

1. notices the 200 g packet;
2. eyes/head turn to the price;
3. sees the 150 g packet and expression changes;
4. holds both together to compare;
5. turns to camera for payoff.

Within one semantic scene, each successive keyframe must change at least one meaningful element:

- gaze;
- head angle;
- mouth/expression;
- hand/arm action;
- body lean;
- prop position;
- object focus.

Do not make a 'new pose' where only a caption or arrow changes.

Pure diagram/object/insert scenes may use a single hero SVG if character acting adds nothing.

The renderer cuts through key poses in order while applying subtle camera movement. Therefore storyboard them as a coherent action sequence. Never rely on zoom/pan to fake character animation.

## Scene-to-scene continuity

Preserve:

- face/hair identity;
- outfit family;
- ink/shading language;
- cream + black + red palette;
- object continuity when one example spans multiple scenes.

Change deliberately:

- pose and expression;
- gaze and hand action;
- camera distance/angle;
- object position/focus;
- background emphasis.

The full short should feel like a storyboard sequence, not unrelated illustrations and not copies of the same frame.

## SVG craft requirements

Scheduled artwork must remain self-contained SVG.

For character art:

- prefer `<path>` with cubic Bézier curves for silhouettes and anatomy;
- group logically (`character`, `face`, `hair`, `left-hand`, `prop`, `background`);
- use layered fills for cel shading;
- use `stroke-linecap="round"` and `stroke-linejoin="round"` for hand-drawn lines;
- add sparse hatching/folds/motion marks as short accent paths;
- keep SVG deterministic and CairoSVG-friendly.

Never use scripts, `foreignObject`, remote references, embedded raster data, external fonts/images or network resources.

## Final V2 checklist

Before committing, ask:

1. Does the protagonist look professionally drawn rather than like an SVG stick figure?
2. Can emotion and gaze direction be read instantly?
3. Does the pose physically express the exact narration beat?
4. Is the mechanism obvious without relying on subtitles?
5. Is the style sketchy/editorial rather than realistic, glossy or childish?
6. Is the composition strong on a vertical phone screen?
7. Are consecutive key poses meaningfully different while preserving identity?
8. Does the action order make sense with no continuity errors?
9. Would each frame still look intentional if printed as a comic panel?

If an important answer is no, redraw before push.
