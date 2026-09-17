# Ti fregano così — Visual Bible V2.1

This file is the visual authority for every newly scheduled cartoon short. `AGENTS.md` defines editorial/packaging rules; this file defines how the artwork must look and act.

## Canonical visual target

The approved target is a **polished hand-sketched editorial comic**, like a professionally illustrated vertical magazine/cartoon storyboard.

The canonical mental reference is the approved cinema concession sketch:
- recurring young man with messy black hair, expressive large-but-not-chibi eyes, angular face and black hoodie;
- convincing location: cinema snack counter, warm practical lights, menu boards, popcorn machine, customers, posters and props;
- energetic black ink with slightly imperfect hand-drawn contours;
- warm cream paper base, deep charcoal/black, warm skin, restrained red accents, amber environmental light;
- strong comic-panel staging and facial acting;
- typography that feels hand-lettered but is **clean, deliberate and fully contained**;
- enough detail to feel premium, never so much that the frame becomes noisy on a phone.

**Sketchy does NOT mean crude, unfinished, childish, ugly, wobbly, low-detail or improvised.**
The target is `beautiful finished illustration with visible sketch/ink character`, not `rough draft`.

## Hard quality gate

Reject and redraw before push if any of these are true:
- the protagonist looks like clip-art, a stick figure, primitive SVG geometry or a children's drawing;
- the face/hands/anatomy feel mechanically assembled;
- the frame feels empty, generic or contextless;
- the viewer cannot tell WHERE the scene happens;
- the illustration merely places the character beside a label instead of staging an event;
- the environment has no relevant props, people, surfaces, signage or depth;
- the character is frozen while the narration describes an action;
- consecutive poses only change text/zoom;
- text overlaps text, characters, prices, panel borders or important artwork;
- any word is clipped, squeezed, unreadable or runs outside its intended box;
- the frame depends on a paragraph of embedded text to explain the mechanism;
- rendering drifts into photorealism, glossy anime, plastic 3D or generic corporate vector art.

Every frame should look like it came from the same accomplished cartoonist.

## Recurring protagonist

Use one recognisable young-adult protagonist throughout the channel:
- male-presenting, early-twenties feel;
- slim/average build with believable neck, shoulders, elbows and hands;
- messy dark brown/black hair with layered hand-drawn locks and a strong silhouette;
- expressive dark eyebrows and readable eye direction;
- large expressive eyes but never chibi;
- angular stylised cheek/jaw/nose;
- black hoodie or casual black jacket;
- optional small white `TI FREGANO COSÌ` chest mark;
- warm skin with one darker cel-shadow tone.

He should feel like the same person in every frame while acting differently.

## Acting language

The protagonist must **perform the narration**:
- look at the exact object currently being discussed;
- head turn before pointing;
- lean toward a suspicious price/menu;
- side-eye when something feels manipulative;
- use hands to compare sizes/options;
- react after the relevant object appears, never before;
- direct-to-camera only for viewer address or payoff;
- use knowing/sarcastic expressions rather than constant anger.

Prominent hands need readable fingers, grip and palm structure.

## Environment-first storytelling — HARD gate

Every semantic scene must establish a **specific real-world context** when the topic benefits from one.

Examples:
- cinema pricing -> concession counter, glowing cinema sign, menu board, popcorn tubs, drink cups, staff/customer silhouettes, movie posters;
- supermarket -> shelf, price labels, baskets, products, aisle perspective;
- subscription -> phone/laptop interface in a believable room/work setting;
- delivery fee -> app + food bag + doorstep/courier context.

A background is not decoration: it is evidence for what the viewer is looking at.

For explanatory shorts, prefer a concrete recurring example across multiple scenes instead of abstract cards floating in empty cream space.

## Drawing language

### Ink
- strong hand-inked outer contours;
- smaller interior strokes for folds/details;
- organic cubic Bézier paths for face, hair, clothes, hands and hero props;
- slight line irregularity, never sloppy;
- sparse hatching, motion ticks and sketch accents;
- round joins/caps.

### Colour
Core:
- paper `#F3E6CC`, `#F7EDD9`;
- ink `#171512`;
- charcoal `#171717`, `#292725`;
- skin around `#E7A16F`, `#F1B17F` + one darker shade;
- red accent `#D74332`, `#C93228`;
- cinema/environment amber/brown/cream tones where relevant.

Use flat colour with restrained 2-3 tone cel shading. No glossy gradients on skin.

## Composition

Every 1080x1920 frame should have:
1. one dominant protagonist action;
2. one unmistakable contextual environment;
3. one mechanism/object focus;
4. foreground/midground/background when useful;
5. intentional negative space for subtitles and any essential embedded text.

Vary framing:
- medium close-up;
- waist-up action;
- over-the-shoulder menu inspection;
- wider environment reveal;
- object insert;
- direct-to-camera payoff.

Do not render every scene as the same waist-up character plus a box on the right.

## Text-safe layout — HARD gate

Embedded artwork text is allowed only when it improves the visual story: location signs, prices, product sizes, very short headlines, tiny labels.

### Rules
- keep all embedded text inside a dedicated safe box or sign;
- minimum outer canvas safety margin: **70 px**;
- minimum box inner padding: **28 px**;
- manually wrap text before rendering; do not rely on overflow/clipping;
- maximum **2 main text blocks** per frame, excluding tiny natural environmental labels;
- headline target: **2-6 words**;
- a sign/menu may contain short rows such as `PICCOLO 6 €`, `MEDIO 8,50 €`, `GRANDE 9 €`;
- text must never overlap another text element;
- text must never cover the protagonist's face/hands or the hero object;
- avoid long sentences inside art; narration belongs in subtitles;
- if copy does not fit comfortably, SHORTEN THE COPY rather than shrinking it until unreadable.

### Pre-push visual check
For each SVG, verify by inspection/calculation that:
- every text x/y position stays inside its intended rectangle;
- line spacing leaves visible breathing room;
- no two text bounding regions intersect;
- no text is clipped by the 1080x1920 viewport;
- no word crosses a panel/sign border.

Any overflow = automatic redraw.

## Concrete-example grammar

The short should teach through something the viewer recognises.

For example, for decoy pricing at a cinema:
1. establish the cinema/snack counter;
2. protagonist sees three drink or popcorn sizes;
3. show an **illustrative** price ladder (for example 6 €, 8,50 €, 9 €);
4. protagonist first judges the large as expensive;
5. then compares it with the middle option;
6. the relative difference becomes visually salient;
7. explain that this is an illustration of context/decoy effects, not a claim that every cinema uses the tactic;
8. close with a practical viewer check.

The environment, objects and acting should carry most of this explanation.

## Pose-to-pose animation

Character-led semantic scenes normally use **2-3 full-frame key poses** (maximum 4).

Good sequence:
`enter context -> notice -> inspect -> compare -> react -> address viewer`

Each new pose must change one or more:
- gaze;
- head angle;
- mouth/expression;
- hand/arm action;
- body lean;
- prop position;
- object focus.

Keep the same environment and object continuity inside a semantic scene. Never fake character motion with zoom/pan alone.

## Scene continuity

Preserve:
- face/hair/outfit;
- drawing language;
- palette;
- cinema/store/room continuity when an example spans scenes;
- menu prices/objects from one frame to the next unless narration intentionally changes them.

Change deliberately:
- pose;
- expression;
- camera;
- object focus;
- depth;
- composition.

The full short should feel like a coherent comic sequence, not eight unrelated posters.

## SVG craft requirements

Scheduled artwork remains self-contained 1080x1920 SVG:
- valid UTF-8 XML;
- local vector primitives and paths only;
- organic paths for visible anatomy;
- grouped layers for environment/character/props/text;
- CairoSVG-friendly;
- no scripts, foreignObject, external images/fonts/network references or raster data URIs.

## Final V2.1 checklist

Before committing:
1. Is this beautiful finished sketch art rather than crude vector art?
2. Is the setting immediately recognisable?
3. Does the frame contain a concrete example/prop instead of abstraction?
4. Is protagonist anatomy/face/hair professionally drawn?
5. Does gaze/pose match the spoken beat?
6. Does every text element fit with comfortable padding?
7. Is there zero text overlap or clipping?
8. Are key poses meaningfully different?
9. Is continuity correct?
10. Would the frame still work as a polished comic panel without subtitles?

If any answer is no, redraw before push.
