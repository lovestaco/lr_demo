# Frame packet: 08-not-all-diffs-equal

## Project inputs

- Project: /home/taco/pers/demo/videos/livereview-launch
- Design tokens: /home/taco/pers/demo/videos/livereview-launch/frame.md
- RULES_DIR: /home/taco/.claude/skills/hyperframes-animation/rules

## Assigned storyboard block

## Frame 8 — Not all diffs are equal

- status: animated
- src: compositions/frames/08-not-all-diffs-equal.html
- type: feature_showcase
- duration: 9.259s
- transition_in: zoom-through
- narrativeRole: Open HOW with the single clearest statement of the idea — the contrast that makes blast radius obvious in one breath.
- scene: 300-line UI tweak and 3-line DB change enter from opposite wings and hold side by side.
- voiceover: "Because not all diffs are equal. Three hundred lines of UI breaks one page. Three lines of database code breaks the entire app."
- blueprint: comparison-split (Reproduce)
- focal: the 3-line cell
- roles: none — designed beat, no captured candidates
- sfx: whoosh-short, impact-bass-1
- asset_candidates: none — designed beat

The two cells carry equal visual weight so the punchline is the asymmetry of consequence, not
of size. Neutral ink on the 300 side; `negative` #dc2626 on the 3 side. The numbers are the
hero type. Badges spring last: "Breaks one page." / "Breaks the entire app."

Reproduce: comparison-split's mirrored book-open entry from opposite wings, with the inner-edge badge spring-pop as the punctuation. Both cells carry equal visual weight — the asymmetry must be consequence, not size.

Scene 1 (0.0–2.0s): "not all diffs are equal" — bare field; eyebrow and headline set upper-left via per-word staggered reveal (`dynamic-content-sequencing`).
Scene 2 (2.0–4.8s): "Three hundred lines of UI" — the left cell enters from the left wing with a rotationY book-open tilt (`split-tilt-cards`); the numeral 300 counts up (`counting-dynamic-scale`) and "Breaks one page." sets beneath in `text`.
Scene 3 (4.8–7.6s): "Three lines of database code" — the right cell enters from the right wing on the mirrored tilt (`split-tilt-cards`); the numeral 3 arrives at the same type size in `negative`.
Scene 4 (7.6–9.259s): "breaks the entire app" — the inner-edge badge spring-pops on the red cell (`spring-pop-entrance`, smooth settle) and a marker circle scribes around the numeral 3 (`css-marker-patterns`). Both cells then hold motionless.

## Selected blueprint: comparison-split

# comparison-split — Comparison Split-Cards

**intent**: Two paired items of equal weight shown side-by-side with mirrored 3D "book-open" tilts — the eye reads them as a balanced comparison, then a pill badge lands at each card's inner edge to punctuate. The motion IS the symmetry: two cards arriving from opposite wings into a held spread.

**roles served**

- Key_Feature (from `comparison-split-cards`): when two complementary features / capabilities of equal weight should be presented **simultaneously, not sequentially** — an A/B, a "X + Y together," paired concepts the viewer must weigh side-by-side. Not for >2 items (use `grid-card-assemble`) or sequential steps.

**duration**: 4–6s

**shot structure** (a `[bg]` canvas carrying two faint ambient glow blooms — `[accent A]` near 30%, `[accent B]` near 70% — so each side owns a color identity across a 50% symmetry axis; equal-width cards under one shared perspective parent)

- **Scene 1 (0.0–~0.8s) — title sets the concept.** A centered `[title line]` with an `[accent keyword]` slides DOWN into place from just above (a short smooth settle). The downward arrival is deliberate: it forms a non-conflicting T-shape against the cards, which arrive from the sides next.
- **Scene 2 (~0.4–1.9s) — the split-tilt entry (signature move).** Two equal-width feature cards arrive from opposite wings — `[left card]` from the left, `[right card]` from the right ~0.2s behind — each carrying a **mirrored 3D `rotateY` tilt** (left faces right, right faces left, opening like a book) and scaling ~0.85→1 as it lands. The entry overlaps the title's tail so the whole thing reads as ONE arrival, not two beats. Each card holds `[image / label / subtitle]`; box-shadows fall **outward** from the tilt (left shadow right, right shadow left).
- **Scene 3 (~1.9–end) — badges punctuate, then hold.** A pill `[badge]` lands at each card's **inner edge** (left then right, ~0.3s apart), overlapping its card ~15% so it reads as attached, not orbiting. This is the lone overshoot in the shot — it earns the punctuation. Settles and holds.

**motion vocabulary**: title slide-down from above; mirrored opposite-wing card entry; static book-open `rotateY` tilt (`+tilt` left, `−tilt` right); tilt-matched outward box-shadow; inner-edge badge spring-pop; gentle phase-opposed idle float (left vs right, never synchronized) registered as subtle jitter; dual side-glow ambient.

**rule mapping**

- two cards entering from opposite wings with mirrored `rotateY` tilts + tilt-matched shadow → `split-tilt-cards` (the signature; keep the two-layer split so the entry `x`/`scale` and the idle never collide on one alias)
- title slide-down settle → `gsap-effects` (translate + opacity on a long-tail `power3`)
- inner-edge pill badge pop (the one overshoot) → `spring-pop-entrance` (overshoot register — earns the punctuation)
- phase-opposed idle float on the pair → `sine-wave-loop` (low-amplitude register — subtle jitter, NOT lazy breathing; left `sin(t)`, right `sin(t+π)` so they never conveyor-belt)
- the two faint side glows behind the cards → `ambient-glow-bloom` (un-triggered soft bloom, one per accent)

**camera modifier**: camera-static by default — the symmetry is the subject and a move would break the balance.

## Selected motion rule: counting-dynamic-scale

---
name: counting-dynamic-scale
description: Counter animation where the value counts up while transform scale grows to its final size, creating escalating visual weight without per-frame text reflow.
metadata:
  tags: counter, counting, scale, transform, number, dynamic, emphasis
---

# Counting with Dynamic Scale

A number counts from A → B while its transform scale grows to the final size — escalating visual weight ("this is impressive") without tweening `font-size` or forcing text layout on every frame. The final font size is static CSS; only the transform changes.

## How It Works

Two synchronized tweens at the SAME timeline position with the SAME ease: (1) a proxy value rendered as text via `onUpdate` (`Math.round(...).toLocaleString()`), (2) the counter's transform `scale: START_SCALE → 1`, where `START_SCALE = START_SIZE / END_SIZE`. A suffix (`%`, `×`, `+`) slides in AFTER the count lands — the number gets its own beat — and a label fades in early.

## Recipe

```html
<!-- inside a standard scene clip (hyperframes-core) -->
<div class="counter-wrap">
  <span class="counter" id="counter">0</span><span class="counter-suffix">{suffix}</span>
</div>
<div class="counter-label">{label}</div>
```

```css
.counter-wrap {
  display: flex;
  align-items: baseline;
  justify-content: center;
  width: {counterContainerWidth}; /* fixed width — no layout shift as digit count changes */
}
.counter {
  font-variant-numeric: tabular-nums; /* MANDATORY — digits keep equal width */
  display: inline-block;
  font-size: {endSize}; /* final size is static; GSAP animates scale, not font-size */
  transform-origin: center center;
}
.counter-suffix {
  opacity: 0;
  transform: translateY(20px);
}
```

```js
const counter = document.getElementById("counter");
const state = { value: 0 };
const START_SCALE = START_SIZE / END_SIZE;

// Count value — onUpdate changes text only
tl.to(
  state,
  {
    value: TARGET_VALUE,
    duration: COUNT_DUR,
    ease: COUNT_EASE,
    onUpdate: () => {
      counter.textContent = Math.round(state.value).toLocaleString();
    },
  },
  0,
);

// Visual growth — compositor transform sharing the count's timing + ease
tl.fromTo(counter, { scale: START_SCALE }, { scale: 1, duration: COUNT_DUR, ease: COUNT_EASE }, 0);

// Suffix slides in AFTER the count completes
tl.to(
  ".counter-suffix",
  { opacity: 1, y: 0, duration: SUFFIX_DUR, ease: `back.out(${SUFFIX_BOUNCE_FACTOR})` },
  COUNT_DUR,
);

// Label fades in early
tl.from(".counter-label", { opacity: 0, y: 12, duration: LABEL_DUR, ease: "power2.out" }, LABEL_AT);
```

## Variations

- **Direct `innerText` tween (no proxy)** — GSAP can tween `innerText` directly for a number-only counter; keep the proxy form when you need locale formatting or suffix logic. The scale tween stays separate either way:

```js
tl.to(
  counter,
  { innerText: TARGET_VALUE, duration: COUNT_DUR, ease: COUNT_EASE, snap: { innerText: 1 } },
  0,
);
```

- **3D depth entry** — add a `tl.from(".counter", { z: -300, ... }, 0)` push-in; requires `perspective` on `.counter-wrap` and `transform-style: preserve-3d` on the counter.
- **Multi-stat coordinated reveal** — 3 stats counting in parallel share the SAME ease, duration, and start position so they finish together (a chord, not an arpeggio). Each stat usually also needs a paired graphic (bar / ring / stars) — don't stop at the number; see [stat-bars-and-fills.md](stat-bars-and-fills.md).

## Values

| token                 | range                                       | notes                                                                         |
| --------------------- | ------------------------------------------- | ----------------------------------------------------------------------------- |
| TARGET_VALUE          | 2–3 digits ideal                            | 4+ digits needs a wider container; must fit at END_SIZE without clipping      |
| START_SIZE / END_SIZE | START ≈ 40–60% of END                       | design inputs used once for START_SCALE; never tween either                   |
| COUNT_DUR             | 1.2–2.5s                                    | below ~0.8s reads as a flash — the eye must read the digits scrolling past    |
| COUNT_EASE            | `power2.out` / `power3.out` ⭐ / `expo.out` | shared by value + scale; more `.out` = more dramatic deceleration at the peak |
| SUFFIX_DUR            | 0.3–0.6s                                    | fires at `COUNT_DUR`, never during the count                                  |
| SUFFIX_BOUNCE_FACTOR  | 1.4–2.0                                     | overshoot is fine on the suffix (it's punctuation, not data)                  |
| LABEL_AT / LABEL_DUR  | AT < COUNT_DUR/2; 0.4–0.7s                  | label arrives before the count peaks                                          |

## Critical Constraints

- **`tabular-nums` mandatory** + fixed-width container as belt-and-suspenders — without them digit-count transitions (9 → 10 → 100) jitter as glyph widths change.
- **Never set `fontSize` in `onUpdate`** — final type size is static CSS; only the transform changes per frame. Keep `onUpdate` O(1): set text only, no style writes or DOM creation.
- **`Math.round`, not `Math.floor`** — halfway through the final integer should already display the final value.
- **Avoid `back.out` / `elastic.out` on the counter itself** — overshoot makes the number look unstable (it's data, not decoration). Grow in place, don't bounce.
- **Label is BIG TEXT, not a page-style caption** — a tiny paragraph under a hero-size number reads as visual noise in video. Display-size, uppercase, tracked: the label is part of the headline.

## See also

`stat-bars-and-fills` (the paired graphic — give it the same ease/duration so number and fill land as one beat) · `svg-path-draw` (icons drawing in around the number) · `center-outward-expansion` (icons bursting outward at the count peak).

## Selected motion rule: css-marker-patterns

# CSS Patterns for Marker Highlighting

Pure CSS + GSAP implementations of all five MarkerHighlight.js drawing modes — no external library dependency, full timeline control. Snippets show mechanism DOM only, inside a standard scene clip (hyperframes-core); assume `tl` exists.

Shared scaffold for every mode: the wrap is `position: relative; display: inline`; the text copy is `position: relative` and z-indexed **above** the accent (below it for sketchout, where the lines cross the text).

## 1. Highlight Mode

Yellow marker sweep behind text — the most common mode.

```html
<span class="mh-highlight-wrap">
  <span class="mh-highlight-bar" id="hl-1"></span>
  <span class="mh-highlight-text">highlighted text</span>
</span>
```

```css
.mh-highlight-bar {
  position: absolute;
  inset: 0 -6px; /* bleed past the text edges */
  background: #fdd835;
  opacity: 0.35;
  transform: scaleX(0);
  transform-origin: left center;
  border-radius: 3px;
  z-index: 0;
}
```

```js
tl.to("#hl-1", { scaleX: 1, duration: 0.5, ease: "power2.out" }, 0.6);
// Optional hand-drawn skew: gsap.set("#hl-1", { skewX: -2 });
// Multi-line: tl.to(".mh-highlight-bar", { scaleX: 1, ..., stagger: 0.3 }, 0.6);
```

## 2. Circle Mode

Hand-drawn ellipse around text — `border-radius: 50%` plus a slight rotation for organic feel.

```html
<span class="mh-circle-wrap">
  <span class="mh-circle-text">IMPORTANT</span>
  <span class="mh-circle-ring" id="circle-1"></span>
</span>
```

```css
.mh-circle-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 130%; /* tight (short words): 150%; rounded-rect: 120% + border-radius: 30% */
  height: 160%;
  transform: translate(-50%, -50%) rotate(-3deg) scale(0);
  border: 3px solid #e53935;
  border-radius: 50%;
  z-index: 0;
}
```

```js
tl.to("#circle-1", { scale: 1, rotation: -3, duration: 0.6, ease: "back.out(1.7)" }, 0.7);
```

## 3. Burst Mode

Radiating lines from text center — each line a positioned span rotated to its angle. Use ~12 lines at 30° steps and **vary `--len` (40–80px)**; equal lengths look mechanical.

```html
<span class="mh-burst-wrap">
  <span class="mh-burst-text">WOW</span>
  <span class="mh-burst-container" id="burst-1">
    <span class="mh-burst-line" style="--angle: 0deg; --len: 70px;"></span>
    <span class="mh-burst-line" style="--angle: 30deg; --len: 55px;"></span>
    <!-- …one line per 30° step through 330deg, --len varied 40-80px -->
  </span>
</span>
```

```css
.mh-burst-container {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  z-index: 1; /* text copy at z-index: 2 */
}
.mh-burst-line {
  position: absolute;
  display: block;
  width: 3px;
  height: var(--len);
  background: #1e88e5;
  left: -1.5px;
  top: calc(-1 * var(--len));
  transform: rotate(var(--angle));
  transform-origin: bottom center;
  opacity: 0;
}
```

```js
tl.fromTo(
  "#burst-1 .mh-burst-line",
  { scaleY: 0, opacity: 0 },
  { scaleY: 1, opacity: 1, duration: 0.4, ease: "power2.out", stagger: 0.03 },
  0.7,
);
```

## 4. Scribble Mode

Wavy SVG underline that draws itself via `stroke-dashoffset`.

```html
<span class="mh-scribble-wrap">
  <span class="mh-scribble-text">underlined text</span>
  <svg class="mh-scribble-svg" viewBox="0 0 500 24" preserveAspectRatio="none">
    <path
      id="scribble-1"
      d="M0,12 Q31,0 62,12 Q93,24 125,12 Q156,0 187,12 Q218,24 250,12 Q281,0 312,12 Q343,24 375,12 Q406,0 437,12 Q468,24 500,12"
      fill="none"
      stroke="#FDD835"
      stroke-width="3"
      stroke-linecap="round"
    />
  </svg>
</span>
```

```css
.mh-scribble-svg {
  position: absolute;
  left: 0;
  bottom: -6px; /* strikethrough variant: top: 50%; transform: translateY(-50%) */
  width: 100%;
  height: 24px;
  z-index: 0;
}
```

```js
const path = document.querySelector("#scribble-1");
const len = path.getTotalLength();
gsap.set(path, { strokeDasharray: len, strokeDashoffset: len });
tl.to("#scribble-1", { strokeDashoffset: 0, duration: 0.8, ease: "power1.inOut" }, 0.7);
```

Path tuning: the `Q` control points alternate y between 0 and 24 for a natural wobble. Tighter waves = smaller x-increments (~25px per half-wave); looser = ~50px; subtler amplitude = y range 0–16.

## 5. Sketchout Mode

Cross-hatch over de-emphasized text — two angled lines create a "crossed out" effect.

```html
<span class="mh-sketchout-wrap">
  <span class="mh-sketchout-text">old price</span>
  <span class="mh-sketchout-lines" id="sketchout-1">
    <span class="mh-sketchout-line mh-sketchout-fwd"></span>
    <span class="mh-sketchout-line mh-sketchout-bwd"></span>
  </span>
</span>
```

```css
.mh-sketchout-lines {
  position: absolute;
  inset: 0 -4px;
  overflow: hidden;
  z-index: 1; /* text at z-index: 0 — the lines cross OVER it */
}
.mh-sketchout-line {
  position: absolute;
  display: block;
  top: 50%;
  left: 0;
  width: 100%;
  height: 2px;
  background: #e53935;
  transform-origin: left center;
}
.mh-sketchout-fwd {
  transform: scaleX(0) rotate(-12deg);
}
.mh-sketchout-bwd {
  transform: scaleX(0) rotate(12deg);
}
```

```js
// Forward slash first, backward follows
tl.to("#sketchout-1 .mh-sketchout-fwd", { scaleX: 1, duration: 0.3, ease: "power2.out" }, 1.0);
tl.to("#sketchout-1 .mh-sketchout-bwd", { scaleX: 1, duration: 0.3, ease: "power2.out" }, 1.15);
```

## Combining Modes in Captions

Cycle modes across caption groups for visual variety — every 2-3 groups for high energy, 3-4 for medium, 4-5 for low:

```js
const MODES = ["highlight", "circle", "burst", "scribble"];
GROUPS.forEach((group, gi) => {
  const mode = MODES[gi % MODES.length];
  group.emphasisWords.forEach((word) => applyMode(word.el, mode, tl, word.start));
});
```

## Selected motion rule: dynamic-content-sequencing

---
name: dynamic-content-sequencing
description: Auto-calculate timeline start/end times from content length + per-item duration config — longer content gets more screen time without hardcoded numbers.
metadata:
  tags: timeline, sequencing, dynamic, duration, content-aware, utility
---

# Dynamic Content Sequencing

A utility pattern (not a motion rule in itself) for scenes that show a SEQUENCE of items (cards, phrases, stats): each item's duration is computed from its content length + per-item config, and the sequencer assigns absolute start/end times automatically — no hardcoded offsets per item. Distinct from [discrete-text-sequence](discrete-text-sequence.md) (one text element changing states) — this rule swaps between distinct content blocks.

## How It Works

A content array of `{ eyebrow, title, body, speedFactor, hold }` entries is reduced once at build time into a flat `TIMELINE` of `{ …entry, start, end }` — duration per entry is `BASE_DURATION + body.length × SEC_PER_CHAR + hold`, so longer text earns more reading time. A single linear driver's `onUpdate` reverse-searches the active entry and swaps the DOM **only on transitions** (a `lastTitle` guard — per-frame `textContent` writes flicker in render); an optional progress bar fills 0→100% across the whole run.

## Recipe

```html
<!-- inside a standard scene clip (hyperframes-core) -->
<div class="display">
  <div class="eyebrow" id="eyebrow"></div>
  <div class="title" id="title"></div>
  <div class="body" id="body"></div>
  <div class="progress-bar"><div class="progress-fill" id="progress-fill"></div></div>
</div>
```

```css
.body {
  min-height: 160px; /* reserve space — content height varies; without this, layout jumps */
}
.progress-fill {
  height: 100%;
  width: 0%;
}
```

```js
// N entries, each with its own pacing (optionally a speedFactor multiplier);
// the final entry uses a larger hold (closing beat).
const CONTENT = [
  { eyebrow: "{eyebrow1}", title: "{title1}", body: "{body1}", hold: HOLD_MID },
  // …
  { eyebrow: "{eyebrowN}", title: "{titleN}", body: "{bodyN}", hold: HOLD_FINAL },
];

// Pre-compute absolute start/end ONCE — never in onUpdate.
let cumulative = 0;
const TIMELINE = CONTENT.map((entry) => {
  const dur = BASE_DURATION + entry.body.length * SEC_PER_CHAR + entry.hold;
  const start = cumulative;
  cumulative += dur;
  return { ...entry, start, end: cumulative };
});

function entryAt(time) {
  for (let i = TIMELINE.length - 1; i >= 0; i--) {
    if (time >= TIMELINE[i].start) return TIMELINE[i];
  }
  return TIMELINE[0];
}

const eyebrowEl = document.getElementById("eyebrow");
const titleEl = document.getElementById("title");
const bodyEl = document.getElementById("body");
const progressEl = document.getElementById("progress-fill");

const TOTAL_DURATION = cumulative + TAIL_PAD;
const driver = { t: 0 };
let lastTitle = "";

tl.to(
  driver,
  {
    t: TOTAL_DURATION,
    duration: TOTAL_DURATION,
    ease: "none",
    onUpdate: () => {
      const entry = entryAt(driver.t);
      // Swap content only on transitions — no per-frame DOM thrash
      if (entry.title !== lastTitle) {
        eyebrowEl.textContent = entry.eyebrow;
        titleEl.textContent = entry.title;
        bodyEl.textContent = entry.body;
        lastTitle = entry.title;
      }
      progressEl.style.width = `${(driver.t / TOTAL_DURATION) * 100}%`;
    },
  },
  0,
);
```

## Variations

- **Crossfade between items** — return BOTH adjacent entries during an overlap window (`time ≥ e.start − overlap && time ≤ e.end + overlap`, overlap ≈ 0.3s) and render them with opacities computed from distance to the boundary.
- **Per-item motion variation** — map an `entry.style` key to an existing rule per chapter (e.g. `3d-text-depth-layers` → `hacker-flip-3d` → `counting-dynamic-scale`); the sequencer only orchestrates timing.
- **Auto-extend composition duration** — you can set `data-duration` from the computed `TOTAL_DURATION` in script, but HF reads `data-duration` at composition load and setting it after init may not take effect — author the duration manually from a rough total.

### Accelerating cadence (geometric hold decay)

For rhetorical escalation — "everyone says…", a roll-call, a praise flurry — the beat grid itself accelerates: early entries hold ~1s (read speed), then windows shrink geometrically into a ~0.15–0.3s flurry, braking on an emphasis state before the resolve. The acceleration is pre-computed into the same flat `TIMELINE` — still content-driven, still deterministic, no speed-up tween anywhere:

```js
// Geometric decay on the hold, clamped at a flurry floor; the brake state holds longest.
const HOLDS = CONTENT.map((entry, i) => Math.max(FLURRY_FLOOR, HOLD_START * Math.pow(DECAY, i)));
HOLDS[CONTENT.length - 1] = HOLD_FINAL;

let cumulative = 0;
const TIMELINE = CONTENT.map((entry, i) => {
  // Past ~0.5s states are glanced as motion texture, not read —
  // drop the per-char term or you never reach flurry speed.
  const readable = HOLDS[i] >= READ_THRESHOLD;
  const dur = HOLDS[i] + (readable ? entry.body.length * SEC_PER_CHAR : 0);
  const start = cumulative;
  cumulative += dur;
  return { ...entry, start, end: cumulative };
});
```

Worked example — **praise-chip flurry**: ~16 short quotes hard-cut through a chip beside a pinned wordmark. First 3 states at `HOLD_START = 1.0` (each reads fully); `DECAY = 0.8` shrinks every following window until `FLURRY_FLOOR = 0.2` catches it (≈12 states over ~2.5s — a churn of acclaim, individually glanced); the longest phrase takes `HOLD_FINAL ≈ 1.6` as the brake before the closing lockup.

Values: `HOLD_START` 0.8–1.2s; `DECAY` 0.75–0.88 (higher = longer runway before the flurry bites); `FLURRY_FLOOR` 0.15–0.3s (below ~0.15s swaps strobe); `READ_THRESHOLD` ~0.5s; brake ≥ 4× the floor or the stop doesn't register as a beat. The 3–6 entry guidance relaxes here — 12–18 states are legal precisely because flurry states aren't individually read. The hard-cut discipline (`lastTitle` guard, instant swaps) is what lets 0.2s states render clean.

## Values

| token         | range                 | notes                                                                                                                 |
| ------------- | --------------------- | --------------------------------------------------------------------------------------------------------------------- |
| BASE_DURATION | 0.6–1.5s              | minimum per entry regardless of length — even one-word entries get read time                                          |
| SEC_PER_CHAR  | 0.03–0.06 s/char      | ≈17–33 chars/sec; uniform across the sequence so the pace reads as one engine; lean high for wide-character languages |
| HOLD_MID      | 0.5–1.0s              | dwell on a non-final entry; `< HOLD_FINAL`                                                                            |
| HOLD_FINAL    | 1.0–2.0s              | climax dwell — must exceed HOLD_MID by a clear margin so the close reads as a beat                                    |
| SPEED_FACTOR  | 0.5–2.0 (default 1.0) | per-entry only; if every entry shares a factor, fold it into SEC_PER_CHAR                                             |
| TAIL_PAD      | 0.0–1.0s              | quiet beat after the last entry; prefer 0 when the next composition owns the breath                                   |
| CONTENT N     | 3–6 entries           | <3 isn't a sequence; >6 drags (accelerating cadence relaxes this — see above)                                         |

Reference: `../examples/messaging-multi-phrase.html`.

## Critical Constraints

- **Pre-compute the TIMELINE once at build** — never recompute in `onUpdate`; the reverse search over the flat array is the whole per-frame cost.
- **DOM swap only on entry transition** (`lastTitle`/key guard) — per-frame `textContent` assignment flickers in HF render.
- **`min-height` on the body element** — without reservation, downstream elements (progress bar, brand) jitter as content height varies.
- **Sequential only** — for parallel tracks use a different reduction.
- **Titles fit one line at the chosen size; bodies fit inside `min-height` after wrapping.**

## See also

`discrete-text-sequence` (per-entry typewriter on the body) · `context-sensitive-cursor` (cursor color per chapter) · `vertical-spring-ticker` (animated word swap instead of hard cut) · `scale-swap-transition` (visual morph between entries).

## Selected motion rule: split-tilt-cards

---
name: split-tilt-cards
description: Two cards side-by-side with opposing Y-rotation creating a symmetric 3D split-screen layout for comparisons or feature pairs.
metadata:
  tags: 3d, cards, split, tilt, comparison, symmetric, layout
---

# Split Tilt Cards

Two cards side-by-side with opposing `rotateY` (left `+TILT`, right `−TILT`) — a symmetric "book-open" 3D split for comparisons, before/after, feature pairs. Each card slides in from its own side (reinforcing "they came from their own worlds and met here"), then the pair idles in counter-phase.

## How It Works

`perspective` on the scene root (REQUIRED — without it `rotateY` flattens to a 2D layout) and `transform-style: preserve-3d` on the stage and both cards. Entry starts each card off-axis with `TILT + TILT_OVERSHOOT`, settling to `TILT` — a pivot-into-place. Idle is a gentle counter-phase y-bob (the two yoyo tweens run in opposite directions); copy fades up during the cards' settle, not after.

## Recipe

```html
<!-- inside a standard scene clip (hyperframes-core) -->
<div class="split-stage">
  <div class="card card-left">
    <div class="card-eyebrow">{leftEyebrow}</div>
    <div class="card-headline">{leftHeadline}</div>
    <div class="card-body">{leftBody}</div>
  </div>
  <div class="card card-right">…</div>
</div>
```

```css
.scene-root {
  display: grid;
  place-items: center;
  perspective: SCENE_PERSPECTIVE; /* REQUIRED */
}
.split-stage {
  display: flex;
  gap: STAGE_GAP;
  transform-style: preserve-3d;
}
.card {
  width: CARD_WIDTH;
  transform-style: preserve-3d;
  will-change: transform;
}
/* Shadow falls WITH the facing direction: left card faces right → shadow right. */
.card-left {
  box-shadow: -CARD_SHADOW_OFFSET CARD_SHADOW_DROP CARD_SHADOW_BLUR {shadowColor};
}
.card-right {
  box-shadow: CARD_SHADOW_OFFSET CARD_SHADOW_DROP CARD_SHADOW_BLUR {shadowColor};
}
```

```js
// Entry — from outside, opposing tilts settle with a small pivot
tl.fromTo(
  ".card-left",
  { x: -ENTRY_SLIDE_DIST, rotateY: TILT + TILT_OVERSHOOT, opacity: 0 },
  { x: 0, rotateY: TILT, opacity: 1, duration: ENTRY_DUR, ease: "power3.out" },
  LEFT_AT,
);
tl.fromTo(
  ".card-right",
  { x: ENTRY_SLIDE_DIST, rotateY: -TILT - TILT_OVERSHOOT, opacity: 0 },
  { x: 0, rotateY: -TILT, opacity: 1, duration: ENTRY_DUR, ease: "power3.out" },
  RIGHT_AT,
);

// Counter-phase idle bob — opposite signs = alive; synchronized = conveyor belt
tl.to(
  ".card-left",
  { y: -FLOAT_AMP, duration: FLOAT_DURATION / 2, ease: "sine.inOut", yoyo: true, repeat: 1 },
  IDLE_START,
);
tl.to(
  ".card-right",
  { y: FLOAT_AMP, duration: FLOAT_DURATION / 2, ease: "sine.inOut", yoyo: true, repeat: 1 },
  IDLE_START,
);

// Copy fades up during the settle
tl.from(
  ".card-eyebrow, .card-headline, .card-body",
  { opacity: 0, y: COPY_RISE, stagger: COPY_STAGGER, duration: COPY_DUR, ease: "power2.out" },
  COPY_REVEAL_AT,
);
```

## Variations

- **Badges / floating labels**: position them on the PARENT, never inside a card — inside they inherit the `rotateY` and tilt off-axis.
- **3+ cards**: center card stays flat (`rotateY: 0`), outer two tilt inward — "old way / nothing / our way."
- **Zoom-through**: a separate camera tween scaling `.split-stage` reads as the viewer crossing the gap between the tilted pair.

## Values

| token             | range                            | notes                                                   |
| ----------------- | -------------------------------- | ------------------------------------------------------- |
| SCENE_PERSPECTIVE | 1000–2400px                      | lower exaggerates the tilt; higher reads near-isometric |
| TILT              | 10–18°                           | < 10 reads almost flat; > 18 folds shut and copy blurs  |
| TILT_OVERSHOOT    | 4–12°                            | the pivot-into-place feel                               |
| STAGE_GAP         | 40–120px (~0.06–0.15×CARD_WIDTH) | small = fused pair; large = compared-but-separate       |
| CARD_WIDTH        | 480–820px @1920                  | `2×CARD_WIDTH + STAGE_GAP ≤ 0.95×stage` at full tilt    |
| ENTRY_SLIDE_DIST  | 200–500px (~0.3–0.6×CARD_WIDTH)  |                                                         |
| ENTRY_DUR         | 0.6–1.2s                         |                                                         |
| RIGHT_AT          | LEFT_AT + 0–0.3s                 | zero feels mechanical; large fragments the pair         |
| FLOAT_AMP         | 3–8px                            | subtle is the point                                     |
| FLOAT_DURATION    | 1.6–3.2s round trip              | breathing cadence; IDLE_START ≥ entry end               |
| COPY_REVEAL_AT    | during the entry tail            | copy popping in after cards are idle reads disconnected |

## Critical Constraints

- **`perspective` on the scene root is REQUIRED**; `preserve-3d` on the stage AND each card.
- **Shadow direction matches tilt** — left card faces right → shadow falls right (and mirrored). Wrong sign reads as broken 3D.
- **Counter-phase idle** — the two bobs run with opposite signs at the same position.
- **Badges outside the card divs** (they'd inherit the rotation).
- **Body copy ≤ 2 lines per card** — tilted long paragraphs collapse into perspective blur.
- **Symmetric weight** — same width, same vertical center, similar line counts; asymmetry breaks the comparison metaphor.

## See also

`card-morph-anchor` (the pair can morph into one unified shape afterward) · `counting-dynamic-scale` (numbers as each side's headline) · `sine-wave-loop` (the idle form).

## Selected motion rule: spring-pop-entrance

---
name: spring-pop-entrance
description: The canonical entrance pop — an element (or staggered group) arrives by scaling 0 → 1 on a smooth long-tail settle (power3 default); bouncy overshoot is a rare, explicitly-playful exception. fromTo so it's correct at t=0 under seek.
metadata:
  tags: spring, entrance, pop, scale, power3, settle, stagger, reveal, arrival
---

# Spring-Pop Entrance

> **Smooth beats bouncy.** This entrance defaults to a smooth long-tail settle — `power3.out` (or `expo.out` for a faster front) — that decelerates cleanly into the resting size with **no overshoot**. Bouncy `back.out` is the **#1 instant turn-off** in agent-made videos and is almost never executed well; it is a rare, explicitly-playful exception (consumer / fun brand), never the default. When unsure, settle smoothly.

THE entrance primitive: an element (or staggered group) arrives by springing from nothing — `scale: 0 → 1`, optional small `y` rise — and settles without bouncing. This is **arrival**, not reaction: distinct from [press-release-spring.md](press-release-spring.md) (a click/press → release feedback chain on an element that already rests on screen). Many blueprints used to borrow that rule to fake an entrance; reach for this instead.

## How It Works

One `fromTo` carries the whole arrival: from `{ scale: 0, opacity: 0 }` (explicit, so t=0 is correct under seek) to `{ scale: 1, opacity: 1, ease: "power3.out" }`. For a **group**, the same `fromTo` runs per element at `i * STAGGER`, capped so the group reads as one arriving beat. The `scale` grow is load-bearing; the `y` rise is garnish — drop everything else and it must still read as a clean entrance. Let the ease produce the settle: never hand-key a `scale: 1.1` mid-state (it double-bounces against the curve).

## Recipe

```html
<!-- inside a standard scene clip (hyperframes-core) -->
<div class="pop-hero" id="hero">{heroLabel}</div>

<div class="pop-grid">
  <div class="pop-item">{itemA}</div>
  <div class="pop-item">{itemB}</div>
  <div class="pop-item">{itemC}</div>
</div>
```

```css
.pop-hero,
.pop-item {
  transform-origin: 50% 50%; /* in-place pop; move to the source point for the anchored variation */
  will-change: transform;
}
.pop-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: GRID_GAP;
  place-items: center;
}
```

```js
// Single hero pop — smooth long-tail settle, no overshoot.
tl.fromTo(
  "#hero",
  { scale: 0, opacity: 0 },
  { scale: 1, opacity: 1, duration: POP_DUR, ease: "power3.out" },
  ENTRY_AT,
);

// Staggered group pop — one arriving beat.
gsap.utils.toArray(".pop-item").forEach((el, i) => {
  tl.fromTo(
    el,
    { scale: 0, opacity: 0, y: Y_RISE },
    { scale: 1, opacity: 1, y: 0, duration: POP_DUR, ease: "power3.out" },
    GROUP_ENTRY_AT + i * STAGGER,
  );
});
```

## Variations

- **Calm settle** (premium / enterprise): `power3.out`, no rotation, `Y_RISE` 0–12px — a weighted, confident landing for a hero wordmark or product shot.
- **Firm settle** (everyday default): `power3.out` or `expo.out` for a punchier front, `Y_RISE` ~24px — cards, icons, callouts.
- **Exact-physics settle**: when the settle IS the shot, swap the ease for `springEase({ response: 0.4 })` (critically damped) from `../adapters/gsap-easing-and-stagger.md` → Spring Eases; take `duration` from the helper.
- **Origin-anchored pop**: a callout growing out of a specific point (marker, pointer tip) sets `transform-origin` to that point (e.g. `0% 100%`) so `scale: 0 → 1` reads as "emerging from the source", not "inflating in place".
- **Pop into a held slot**: land the pop and hold still — no idle loop baked into the entrance. If the held frame genuinely needs life, hand off to [sine-wave-loop.md](sine-wave-loop.md) for subtle jitter on a separate later tween; prefer revealing the next element on its VO cue.
- **Bouncy pop (RARE — explicitly-playful only)**: swap the ease for `back.out(OVERSHOOT)` and optionally settle a small `rotation: ROT_FROM → 0` so elements look hand-placed. Only for a deliberately playful register — never product / enterprise / serious tone:

```js
tl.fromTo(
  el,
  { scale: 0, opacity: 0, rotation: ROT_FROM },
  { scale: 1, opacity: 1, rotation: 0, duration: POP_DUR, ease: `back.out(${OVERSHOOT})` },
  GROUP_ENTRY_AT + i * STAGGER,
);
```

Even here keep `OVERSHOOT ≤ ~2` — past that it reads as cartoon wobble. Better still: the baked spring at `dampingFraction: 0.6–0.7` (same adapters doc) gives ~5–10% overshoot that reads physical where `back.out` reads cartoon.

## Values

| token      | range                                     | notes                                                            |
| ---------- | ----------------------------------------- | ---------------------------------------------------------------- |
| EASE       | `power3.out` default; `expo.out` punchier | `back.out(OVERSHOOT)` only in the playful variant                |
| POP_DUR    | 0.4–0.7s                                  | shorter = tight snap; hero must be visible by **t ≤ 0.5s**       |
| STAGGER    | 0.04–0.08s                                | `min(0.06, 0.5 / ITEM_COUNT)` — self-caps the window             |
| ITEM_COUNT | 3–9                                       | >9 makes the stagger vanish — switch to a wipe/sweep reveal      |
| Y_RISE     | 0–32px                                    | small; never large enough to read as a slide-up                  |
| ROT_FROM   | −10°–+10°                                 | playful variant only; alternate sign by index (`i % 2 ? 6 : -6`) |
| ENTRY_AT   | 0–0.4s                                    | a beat of quiet, but keep the subject landing by t ≤ 0.5s        |

## Critical Constraints

- Default ease `power3.out` (no overshoot); `back.out` only in the explicitly-playful variant, and there `OVERSHOOT ≤ ~2`.
- `ITEM_COUNT × STAGGER ≤ ~0.5s` — the group must land inside one beat.
- Entrances state the collapsed from-state in `fromTo` — never rely on a CSS-hidden start (it renders visible before the tween claims it under seek).
- `transform-origin: 50% 50%` for an in-place pop; the source point only for the anchored variation.
- This is a finite arrival — idle motion on a held element is a separate, later `sine-wave-loop` tween.

## See also

`center-outward-expansion` (pop while radiating to slots) · `press-release-spring` (the click-feedback counterpart) · `sine-wave-loop` (post-arrival jitter, sparingly).
