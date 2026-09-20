# Frame packet: 01-faster-not-safer

## Project inputs

- Project: /home/taco/pers/demo/videos/livereview-launch
- Design tokens: /home/taco/pers/demo/videos/livereview-launch/frame.md
- RULES_DIR: /home/taco/.claude/skills/hyperframes-animation/rules

## Assigned storyboard block

## Frame 1 — Faster. Not safer.

- status: animated
- src: compositions/frames/01-faster-not-safer.html
- type: hook
- duration: 6.421s
- transition_in: cut
- narrativeRole: Open on the worsening metric that every engineering leader already feels, so the pain is stated before any product exists.
- scene: AI code volume curve climbs steeply while the review-capacity line stays flat.
- voiceover: "Last year your team started shipping code faster than it ever has. Your review capacity didn't move."
- blueprint: dataviz-countup (Adapt)
- focal: the widening wedge between the two lines
- roles: none — designed beat, no captured candidates
- sfx: riser, impact-bass-1
- asset_candidates: none — designed beat

Two lines on one axis, drawn live. "AI code volume" rises hard and keeps rising; "review
capacity" holds flat underneath it. The gap between them is the whole argument and it is the
only thing that should be legible at a glance. No product, no logo, no UI yet.

Adapt: keep dataviz-countup's "the data carries the argument" spine and its push, but the hero is a divergence between two drawn lines rather than a count-up ring — the gap, not a number, is the statistic.

Scene 1 (0.0–1.8s): bare white field; a single axis baseline self-draws left→right (`svg-path-draw`) and the label "AI code volume" sets above it. Asymmetric 60/40 with the left 40% deliberately empty for now. The frame stays locked — no camera move anywhere in this shot.
Scene 2 (1.8–3.8s): as the VO reaches "faster than it ever has", the volume line completes a steep climb (`svg-path-draw`) and the word **"Faster."** lands in the empty left third via per-word staggered reveal (`dynamic-content-sequencing`), long-tail settle.
Scene 3 (3.8–5.4s): on "your review capacity didn't move", the flat "review capacity" line draws in low and level beneath it (`svg-path-draw`) — deliberately short, deliberately horizontal — and **"Not safer."** sets under the first word in `text-light`.
Scene 4 (5.4–6.421s): the wedge between the two lines fills with a faint `primary` wash (`ambient-glow-bloom`) and holds. Frame still; low-amplitude jitter only (`sine-wave-loop`). No further camera move.

## Selected blueprint: dataviz-countup

# dataviz-countup — Data-Viz / Count-Up

**intent**: Make numbers and charts the hero — a count-up ring/number, a trend chart, a tilted stat/card grid — and traverse the data instruments with a camera that pushes THROUGH them (or scrolls across them) to land on one hero metric, so the data itself carries the argument.

**roles served**

- Problem (from `problem-dataviz-pushthrough`): quantifies the pain with real-looking instruments — a count-up ring → a trend chart → a stat grid — the camera pushing THROUGH each object into the next to dramatize a worsening / large-scale problem ("X% of people struggle with…").
- Product_Intro (from `product-intro-dataviz-scroll-reveal`): a confident "look at the result / the data" open — hard-cut from a hook word into a perspective-tilted grid of data-viz cards, then a hands-off camera scroll lands one glowing hero metric while a kinetic tagline assembles word-by-word.
- Hook (from `hook-counter-burst`): a cold-open hook on ONE dramatic statistic — the frame opens dark and empty, 3–5 thematic icons puncture in clustered at center, then the headline number EXPLODES upward in size as the icons fling outward to their marks (the count-up and the spread are one beat), closed by a slow camera lean-in. Kinetic from frame 1.
- Key_Feature (from dark-stat-scrub-montage): prove the feature with its own analytics — on a black canvas, kinetic headline beats alternate with self-drawing charts and a 3D-tilted dark dashboard that a cursor SCRUBS (tracking line + live tooltips), stitched by hard cuts and one zoom punch. The one variant where a cursor touches the data.
- Social_Proof (from `gauge-beat`): a single count-up instrument — radial gauge arc-draw + rapidly ticking metric + caption — embedded as ONE BEAT inside a kinetic-typography relay; entered and exited by element-level scale/blur push-throughs on a static frame. The instrument guest-stars; the relay itself belongs to kinetic-type-beats.

**duration**: ~4–12s (Hook ~4s · Product_Intro ~6s · dark-scrub-montage ~7.3–7.75s · Problem ~11–12s · gauge-beat ~2.5s inside a ~10.8s relay)

**shot structure** Data-viz field on `[bg color]` (dark or light, soft corner glows); `[gradient A→B]` brand stroke on charts/rings; clean sans-serif white/dark text; a continuous camera move runs underneath that traverses 2–3 data instruments and resolves on a hero metric. One instrument per beat; the camera carries the cut.

- Scene 1 (0.0–Xs): the first data instrument establishes centered — a `[stat]` reads as the hero. A bold center number COUNTS UP `[start]`→`[end]` while its transform scale grows to the static final type size, with `[stat label]` below; its paired graphic (a circular progress RING sweeping to `[pct]` with a `[gradient]` stroke, or a bar/fill) animates in on the SAME ease so number + graphic land as one beat. Supporting `[avatar/object]` elements pop in with spring overshoot into a scattered glowing orbit; a `[headline]` fades up. A very slow continuous camera zoom-in runs throughout.
- Scene 2 (Xs–Ys): the camera traverses to the next instrument and that instrument animates — a `[gradient]` trend line / area chart DRAWS left→right on grid lines (Problem), or off-center cards SCROLL away as the layout glides (Product_Intro). The arriving `[stat-2]` number counts up / the chart resolves.
- Scene 3 / Scene N (…–end): the camera lands the `[hero metric card]` (big number + label + delta + rising chart) in dead-center; a soft `[accent]` glow blooms behind it; the move reaches its peak then eases to a settled, slightly wider composition with the hero centered and supporting cards flanking it. HOLD on the final frame.

- Variant — Problem (push-THROUGH, count-up → trend → grid): Scene 1 is a centered circular progress ring + count-up center number with scattered glowing `[avatar/object]` orbit. Scene 2 is a fast camera PUSH-IN straight through the center of the ring (ring, number, orbiting elements scale up and fly out of frame) into a rounded `[card]` holding `[stat-2 header]` over a `[gradient]` line chart with grid lines + translucent area fill that draws left→right; camera pushes through then settles. Scene 3: camera PANS to a second `[card]` whose number counts up, holding a grid of the `[avatar/object]` elements — a subset dim/blur while the rest receive `[accent]` circular checkmark badges that SPRING-POP; camera settles to the end. The traversal is z-depth push-through between instruments.
- Variant — Product_Intro (scroll-to-hero + word-by-word tagline): a brief opener — Scene 0 (~0.0–0.85s): a full-frame `[hero-color orb]` with a bold white `[hook phrase]` over it; static shimmer, then HARD CUT. Scene 1 cuts to a slightly perspective-TILTED grid of `[data-viz / product cards]` (charts, heatmaps, stat cards with deltas + source footers) with `[tagline word 1]` centered; the grid begins SCROLLING (e.g. toward upper-left) with its tilt held. Scene 2: the grid keeps scrolling so the `[hero metric card]` glides into dead-center as off-center cards slide away; `[tagline word 1]` translates out and `[word 2]` rises in from a frame edge. Scene 3: hero card settles centered, `[accent]` glow blooms behind it, camera PUSHES IN slightly; `[word 2]` holds near it. Scene 4: `[word 2]` slides out, the final `[tagline word]` drops in from the opposite edge above the still-glowing hero, push-in peaks. Scene 5: overlay type clears, camera eases BACK OUT to a settled wider tilted composition — hero centered with glow, supporting cards flanking. The traversal is a hands-off camera SCROLL across a tilted card plane (no cursor, no clicks) + a one-word-at-a-time kinetic headline + push-in-then-out bookend.
- Variant — Key_Feature (dark-scrub-montage: kinetic beats × instruments, cut-stitched): on black, `[kinetic word]` beats ALTERNATE with data instruments; hard cuts stitch the beats and the camera is locked per beat — the traversal is a montage, not a continuous move. Beat A: a bold `[heading]` holds while a thick `[trend line]` DRAWS itself left→right inside a dark chart band, rising to break above the band's edge; at the peak a `[accent]` dot pops and a pill tooltip springs in, its label building to `[value + delta]`. Beat B: ONE fast zoom PUNCH lands a close-up, slightly 3D-tilted dark `[analytics dashboard]` (metric cards with deltas, translucent oversized numerals floating behind); a white cursor SCRUBS a chart — a vertical tracking line follows it and `[date: value]` tooltips read out live, then a second chart ACTIVATES with a color flip and its own scrubbing tooltip — while the tilted plane drifts gently sideways; quick pull-away/fade to black. Beat C: a `[glowing wave / typed line / impact word]` beat lands the closing stat LOCKUP — `[title]` + big `[stat]` counting up + `[green delta arrow + context line]` — and holds static to the end. Kinetic words between instruments scale up violently past the frame as element-level push-through transitions (no camera).
- Variant — Social_Proof (gauge-beat inside a relay): a static-camera kinetic-type relay hosts ONE instrument beat — thin concentric `[accent]` arcs radiate from center, a thick `[accent]` progress arc draws clockwise over them, a large `[metric]` rapidly ticks up to `[big value]` with a `[caption]` below; the group slowly scales up (element-level drift), then hard-cuts out to the next text beat. Entry/exit for every beat is scale-up-from-blur in / scale-up-and-blur-past-frame out — a fake push-through with no camera anywhere. Use when social proof is one number and the surrounding beats are typography.

**motion vocabulary** count-up number with transform-scale growth on the value; circular progress-ring sweep; growth bar / progress fill; gradient trend-line + area-fill left→right draw; spring-overshoot pop-in of scattered glowing avatar/object elements; perspective-tilted card grid; directional grid scroll (cards glide in/out of center); hero-card centering; soft accent glow bloom behind the hero; slow continuous zoom-in; fast camera push-IN / push-THROUGH the center of an instrument; lateral/vertical camera pan between cards; gentle push-in that peaks then eases back out to a wider settle; selective dim/blur of a subset + spring-pop checkmark badges; full-frame hook orb → hard cut; kinetic tagline assembled word-by-word (each word drops/rises from a frame edge, prior word slides out). Dark-scrub-montage additions: self-drawing chart line that breaks above its band; peak dot + pill tooltip spring-pop; cursor chart scrub with vertical tracking line + live date/value tooltip readouts; chart activation color flip; 3D-tilted dark dashboard plane with slow lateral drift; translucent oversized numerals floating behind cards; fast zoom punch-in; pull-away/fade-to-black beat exit; hard-cut beat stitching; kinetic word push-through (element scales up past the frame); typed line with blinking cursor; impact slam word + particle-dissolve punctuation; glowing wave draw; green delta arrow pop; stat lockup hold. Gauge-beat additions: concentric static arcs + thick clockwise progress-arc draw; rapid count-up tick; scale-up-from-blur entrance / scale-up-and-blur-past-frame exit (element-level fake push-through).

**rule mapping** (motion verb → `rules/<id>.md`)

- count-up number whose transform scale grows with the value → `counting-dynamic-scale` (primary text rule)
- circular progress-ring sweep (the ring fill) → `stat-bars-and-fills` (ring form) — its draw mechanics delegate to → `svg-path-draw`
- growth bars / progress fill paired beside a number → `stat-bars-and-fills` (primary data rule)
- gradient trend-line / area-chart left→right draw → `svg-path-draw` (a path/line draws itself)
- spring-overshoot pop-in of the avatar/object elements → `spring-pop-entrance` (elastic overshoot); the scattered-ring layout of glowing avatars/objects → `avatar-cloud-network`; if they keep drifting/orbiting → `orbit-3d-entry`
- spring-pop `[accent]` checkmark badges → `spring-pop-entrance`
- perspective-tilted card grid (tilt held static while content moves) → `3d-page-scroll`
- directional scroll across the tilted card plane (cards glide in/out of center) → `3d-page-scroll` (scroll) + `viewport-change` (lateral/vertical pan form)
- hero metric card centering (scroll/pan lands the target dead-center) → `coordinate-target-zoom` (target lands at viewport center) / `viewport-change`
- hard-cut from the hook orb into the grid → `scale-swap-transition`
- kinetic tagline assembled word-by-word → `kinetic-beat-slam` (one onset grid, distinct per-word entrances)
- slow continuous zoom-in + push-THROUGH the instruments + lateral/vertical pan between cards + push-in-then-out bookend → `multi-phase-camera` (see camera modifier)
- soft accent glow BLOOM behind the hero card → `ambient-glow-bloom` (un-triggered soft glow/bloom behind the static hero element — distinct from `press-release-spring`'s press-triggered glow and `asr-keyword-glow`'s word-timed envelope)
- selective dim/blur of a SUBSET of grid items (focus-falloff on the non-highlighted cards) → `depth-of-field-blur` (selective per-element blur/dim to spotlight the highlighted cards — the same focus-falloff rule used in `constellation-hub`)
- cursor chart scrub (cursor-tied vertical tracking line + live data readout in a tooltip) → `chart-scrub-readout` (the tracking line, tooltip pop, and seek-safe live value readout driven by cursor x)
- chart activation color flip (second chart lights up under the scrub) → `gsap-effects` (color/opacity chord at the scrub handoff — basic tween, no dedicated rule needed)
- 3D-tilted dashboard plane + slow lateral drift → `3d-page-scroll` (the tilt framing) + `sine-wave-loop` (the drift; keep amplitude tiny so the scrub stays legible)
- fast zoom punch-in to the dashboard → `multi-phase-camera` (one short aggressive push phase) aimed via `coordinate-target-zoom`; add `motion-blur-streak` at peak velocity
- kinetic word push-through / scale-up-and-blur-past-frame exit / scale-up-from-blur entrance → `kinetic-beat-slam` (the beat grammar) + `motion-blur-streak` (blur peaks at max speed, resolves at the settle — its entrance form runs the blur-in, its exit form the blow-past)
- typed line with blinking cursor → `discrete-text-sequence` + `context-sensitive-cursor` (square-wave blink)
- impact slam word → `kinetic-beat-slam`; its particle-dissolve punctuation → `particle-burst` (glyph→particles dissolve, deterministic)
- glowing wave draw → `svg-path-draw` (the draw) + `ambient-glow-bloom` (the glow envelope)
- green delta arrow pop / peak dot + pill tooltip → `spring-pop-entrance`
- concentric static arcs + clockwise progress-arc draw (gauge beat) → `stat-bars-and-fills` (ring form) → draw mechanics `svg-path-draw` (both already mapped above — the gauge is the existing ring with static concentric chrome behind it)

**camera modifier**: The camera is the through-line that traverses the data instruments — one camera wrapper sequenced by `multi-phase-camera`, with each stop targeted via `coordinate-target-zoom` onto the focal instrument/card.

- Problem — push-THROUGH: a slow continuous zoom-in (drift overlay) plus a fast PUSH-IN straight through the center of one instrument into the next (`multi-phase-camera`, Steady-push pattern), then a lateral/vertical PAN to the final card. Z-depth push-through is the signature (distinguishes it from a flat pan-tour).
- Product_Intro — scroll-to-hero + bookend push: a hands-off directional SCROLL across the tilted card plane (`3d-page-scroll` scroll / `viewport-change` pan) that lands the hero card center, then a gentle push-in that PEAKS and eases BACK OUT to a wider settle (`multi-phase-camera`, Bookend-pull pattern). No cursor, no clicks — the camera does the navigating.
- Key_Feature — montage-cut: the camera is NOT the through-line — hard cuts stitch the instrument beats, the frame is locked inside each beat, and exactly ONE fast zoom punch (`multi-phase-camera` single push phase + `coordinate-target-zoom`) lands the dashboard close-up; exits are pull-away/fade-to-black. Between instruments, ELEMENTS fake the push: kinetic words scale up past the frame (`kinetic-beat-slam` + `motion-blur-streak`). Gauge-beat form drops even the punch — fully static, all push-through element-level. Reach for this mode when the dialect is a dark rapid montage; the Problem/Product_Intro modes remain the default for a single continuous argument.

## Selected motion rule: ambient-glow-bloom

---
name: ambient-glow-bloom
description: Un-triggered soft radial glow that blooms in behind a hero element and holds with a bounded idle breathe, or a single-pass traveling sweep across a surface. No click, no word-sync — it just blooms. Finite, deterministic, seek-safe.
metadata:
  tags: glow, bloom, ambient, radial, sweep, hero, presence, finite, un-triggered
---

# Ambient Glow Bloom

A soft radial glow that **blooms in behind a hero element** (card, logo, metric) and holds, giving it presence. Unlike `press-release-spring`'s click-triggered burst or `asr-keyword-glow`'s word-timed envelope, this glow is **un-triggered** — it blooms on the hero's settle and stays lit. Two forms: a **hero bloom** that swells behind a settling element then breathes, and a **traveling sweep** that translates a soft highlight across a surface exactly once.

## How It Works

A radial-gradient layer sits **behind** the hero (glow `z-index: 1`, hero `z-index: 2` — a glow in front occludes it), starting at `opacity: 0`. Over the bloom-in window it ramps `opacity: 0 → peak` with a gentle `scale` swell, timed so `BLOOM_START + BLOOM_DUR` lands on the hero's settle — glow and hero resolve as ONE beat ("powering on"), never glow-then-card. After bloom-in:

1. **Hero bloom** — a **bounded idle breathe** during the hold: a finite `ease: "none"` tween advances a `phase` proxy and `onUpdate` nudges opacity + scale a hair around peak (never a `yoyo` loop). `sin(0) = 0` → the breathe starts exactly at the bloom's resting state.
2. **Traveling sweep** — a narrow highlight band at one edge translates **once** across to the other (`x` off-surface to off-surface), clipped to the surface (`overflow: hidden`). One pass, no return — a repeating sweep reads as a loading shimmer, not a reveal accent (the shimmer-sweep variation below is the sanctioned exception).

Peak opacity stays restrained (**≤ 0.45 hard ceiling**) so the glow gives presence without washing the frame; the glow color is **darker + more saturated** than the element it backs (a same-hue, same-lightness glow disappears into the surface).

## Recipe

```html
<!-- inside a standard scene clip -->
<div class="bloom-stage">
  <div class="bloom-glow" id="bloom-glow"></div>
  <!-- z-index: 1; inset: GLOW_INSET (negative); background: {glowGradient} -->
  <div class="hero-card" id="hero-card">{HeroLabel}</div>
  <!-- z-index: 2 -->
</div>
<!-- sweep form: <div class="sweep" id="sweep"> inside the overflow:hidden surface -->
```

```js
// ── Form A: HERO BLOOM ── bloom in soft, landing on the hero's settle.
tl.fromTo(
  "#bloom-glow",
  { opacity: 0, scale: GLOW_START_SCALE },
  { opacity: GLOW_PEAK_OPACITY, scale: 1, duration: BLOOM_DUR, ease: "power2.out" },
  BLOOM_START,
);
// Bounded breathe during the hold — finite phase tween, NOT a yoyo loop.
const glow = document.getElementById("bloom-glow");
const phase = { p: 0 };
tl.to(
  phase,
  {
    p: Math.PI * 2 * BREATHE_CYCLES,
    duration: BREATHE_DUR,
    ease: "none",
    onUpdate: () => {
      const s = Math.sin(phase.p);
      glow.style.opacity = String(GLOW_PEAK_OPACITY + s * OPACITY_AMP);
      glow.style.transform = `scale(${1 + s * SCALE_AMP})`;
    },
  },
  BLOOM_START + BLOOM_DUR,
);

// ── Form B: TRAVELING SWEEP ── one finite pass, constant glide.
tl.fromTo(
  "#sweep",
  { x: SWEEP_START_X, opacity: 0 },
  { x: SWEEP_END_X, opacity: SWEEP_PEAK_OPACITY, duration: SWEEP_DUR, ease: "none" },
  SWEEP_START,
);
tl.to("#sweep", { opacity: 0, duration: SWEEP_FADE_DUR, ease: "power1.in" }, SWEEP_FADE_START);
```

## Variations

- **Bloom-and-hold** — for scenes <3s or a hero with its own idle, skip the breathe: the single `fromTo` is the whole recipe.
- **Pulse-on-arrival** — bloom slightly PAST peak (`GLOW_OVERSHOOT_OPACITY`, `scale: 1.06`), then a second adjacent tween eases down to a steady hold — one breath punctuating the landing, no ongoing loop.
- **Multi-hero relay** — stagger per-glow `BLOOM_START` by ~0.15–0.3s across a row; shrink `OPACITY_AMP` / `SCALE_AMP` per the `/√N` rule below.
- **Diagonal raked sweep** — angle `{sweepGradient}` (~105°) across a wordmark: the classic one-pass logo sheen. Narrower `SWEEP_WIDTH`, higher `SWEEP_PEAK_OPACITY`.

### Shimmer sweep (text-clipped status-phrase working-state)

The sweep re-aimed **inside type**: a soft highlight gradient clipped into a status phrase ("Thinking…", "Analyzing dataset…") via `background-clip: text` travels left→right through the letterforms — the grey-on-grey shimmer that says _still working_. Unlike every other form here it legitimately **repeats while the status is live**: the repetition is diegetic working-state, not idle wobble (same defense as a blinking caret — the motion performs status). Two things keep it honest: it is **bounded** (one finite tween whose pass count is computed from the status window, never `repeat: -1`), and it is **killed at resolve** — the moment the status completes, the shimmer stops dead; a shimmer surviving into the answer beat turns a working indicator into decoration.

```js
// Status shimmer — N passes as ONE bounded tween. Killed at resolve.
const status = document.getElementById("status-phrase");
// CSS on #status-phrase: background: {shimmerGradient}; background-size: 300% 100%;
// -webkit-background-clip: text; background-clip: text; color: transparent;
const shimmer = { p: 0 };
const PASSES = Math.round(STATUS_DUR / PASS_PERIOD); // whole passes, computed up front
tl.to(
  shimmer,
  {
    p: PASSES,
    duration: STATUS_DUR,
    ease: "none",
    onUpdate: () => {
      const t = shimmer.p % 1; // 0→1 within each pass; percent axis inverted → left→right travel
      status.style.backgroundPosition = `${(1 - t) * 100}% 50%`;
    },
  },
  STATUS_START,
);
tl.set(status, { backgroundPosition: "100% 50%" }, STATUS_START + STATUS_DUR); // resolve: dead.
```

Keep it a whisper: `{shimmerGradient}` is the status text's own grey with one slightly-lighter band (highlight stop a step above the base, nothing near white); `background-size` ~300% keeps the band narrow in the glyphs; `PASS_PERIOD` 1.2–1.8s — slower reads as a sheen accent, faster as a spinner. Whole-number `PASSES` lands the band at its start position exactly at the kill frame, so the `tl.set` is visually a no-op. This is the working-state cousin of `gradient-text-sweep`: reach **here** when the sweep _means_ "in progress," **there** when the gradient is the typographic treatment itself.

## Values

| token                   | range / default                                        | notes                                                                      |
| ----------------------- | ------------------------------------------------------ | -------------------------------------------------------------------------- |
| GLOW_PEAK_OPACITY       | 0.15 (subtle) → 0.30 (default) → **0.45 hard ceiling** | higher washes the frame; a glow you consciously notice is too strong       |
| GLOW_INSET              | −200 to −450px (1920×1080)                             | negative so the halo extends past the hero; too small reads as a tight rim |
| GLOW_START_SCALE        | 0.80–1.0                                               | ≤1.0 — grow into place, never shrink                                       |
| BLOOM_DUR / BLOOM_START | 0.6–1.4s                                               | `BLOOM_START + BLOOM_DUR` ≈ the hero's settle frame                        |
| OPACITY_AMP / SCALE_AMP | 0.02–0.05 / 0.01–0.03 default                          | `PEAK + OPACITY_AMP ≤ 0.45`; push only when the glow is the sole motion    |
| BREATHE_CYCLES          | period 2.5–4s per breath                               | glow breathes slower than element breathing                                |
| SWEEP_WIDTH             | 15–35% of surface (grid) / 8–15% (wordmark)            |                                                                            |
| SWEEP_DUR               | 0.8–1.6s                                               | one deliberate pass — slow enough to read as light                         |
| SWEEP_PEAK_OPACITY      | 0.10 → 0.25 (default) → 0.40                           | same ≤ ~0.45 wash limit; tight sweeps tolerate the high end                |
| SWEEP_START_X / END_X   | fully off-surface both ends                            | no visible spawn/despawn mid-surface; fade reaches 0 as the band clears    |
| PASS_PERIOD (shimmer)   | 1.2–1.8s                                               | with whole-number PASSES                                                   |

## Critical Constraints

- **Glow peak opacity ≤ 0.45** — including breathe amplitude; default to the LOW end (0.15–0.30).
- **Glow behind, hero in front**; glow color darker + more saturated than the hero surface.
- **Land glow and hero as one beat** — before or after reads as two separate events.
- **Breathe is bounded, sweep is one pass** — the only sanctioned repetition is the shimmer sweep, bounded and killed at resolve.
- **Concurrent halos compound** — per-glow amps ≤ default `/√N`, stagger breathe periods (2.6s / 2.9s / 3.3s) so they don't pulse in lockstep.
- **Don't combine a `boxShadow` glow on the hero with this halo layer** — they compete and read muddy; the glow lives on the dedicated layer.

## See also

`sine-wave-loop` (hero breathes on scale/y while the glow breathes on opacity, out of phase) · `press-release-spring` (the click-triggered sibling — never both behind one element) · `counting-dynamic-scale` / `stat-bars-and-fills` (bloom behind a landing stat) · `center-outward-expansion` (sweep across the assembled grid) · `gradient-text-sweep` (the design-beat gradient counterpart).

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

## Selected motion rule: sine-wave-loop

---
name: sine-wave-loop
description: Bounded sine-driven idle — subtle jitter or a single genuinely-needed bounded ambient breath on a held element. De-emphasized: circular breathing as "aliveness" is cheap; prefer sequential reveal timed to the VO, then subtle jitter, before reaching here.
metadata:
  tags: idle, jitter, bounded-ambient, sine, trigonometry, low-amplitude, post-entry
---

# Sine Wave Loop (subtle jitter / bounded ambient)

> **Reach for this last.** Per the motion doctrine (`references/motion-language.md`): circular breathing — scaling text/cards up and down to look "alive" — is cheap, the agent's reflexive cheat, and reads weak. "I'd rather have NO motion than BAD motion." First fill the back of a shot with **sequential reveal timed to the VO**; if a frame has genuinely settled and still needs life, the **sanctioned move is subtle jitter** — this rule at the LOW end of its amplitude range. A full breathing loop is the rare last resort on a single held hero, never stamped on every element.

Keeps a settled element from feeling dead using `Math.sin` on the timeline clock. Two forms:

- **Yoyo form** — one `sine.inOut` tween with `yoyo: true` and a **finite** `repeat` count. Preferred when the idle stands alone on a property nothing else touches.
- **onUpdate form** — one long `ease: "none"` tween drives a `phase` proxy `0 → 2π·CYCLES`; `onUpdate` maps `Math.sin(phase)` into the transform. Required when the offset multiplies/adds onto another live value (compound transforms, amplitude envelopes, multi-octave).

Either way, idle begins where the entry settled: at `phase = 0`, `sin(0) = 0` — the offset is zero, so there is no jump from the entry's resting state.

## Recipe

```js
// onUpdate form — phase-driven, composable.
const phase = { p: 0 };
tl.to(
  phase,
  {
    p: Math.PI * 2 * CYCLES,
    duration: IDLE_DUR,
    ease: "none", // sine provides the easing; a non-linear phase tween distorts the wave
    onUpdate: () => {
      const s = Math.sin(phase.p);
      hero.style.transform = `translateY(${s * Y_AMP_PX}px) scale(${1 + s * SCALE_AMP})`;
      // secondary elements: offset by Math.PI / 2 — synced motion looks mechanical
      dot.style.transform = `scale(${1 + Math.sin(phase.p + Math.PI / 2) * DOT_SCALE_AMP})`;
    },
  },
  IDLE_START_TIME,
);

// Yoyo form — standalone property, finite repeats.
tl.to(
  "#badge",
  { y: -Y_AMP_PX, duration: PERIOD / 2, ease: "sine.inOut", yoyo: true, repeat: REPEATS },
  IDLE_START_TIME,
);
```

## Variations

- **Multi-octave** (organic): stack a higher-frequency overlay — `1 + Math.sin(p) * AMP_PRIMARY + Math.sin(p * OCTAVE_RATIO) * AMP_SECONDARY`, with `AMP_SECONDARY < AMP_PRIMARY` and the combined max inside the normal SCALE_AMP range.
- **Settle and fade** (strongly recommended when `IDLE_DUR > 6s`): ramp amplitude to zero over the last ~20% of idle so the scene visibly settles before the inter-scene transition, instead of handing off mid-drift:

```js
const t = phase.p / (Math.PI * 2 * CYCLES); // 0 → 1 across idle
const env = t < 1 - FADE_FRAC ? 1 : (1 - t) / FADE_FRAC; // FADE_FRAC ≈ 0.2
const scale = 1 + Math.sin(phase.p) * SCALE_AMP * env;
```

This is the single biggest fix when finalize snapshots show "everything's still moving at the end"; it pairs naturally with break-boundary transitions (the outgoing visual is static when the crossfade/push begins).

## Values

| token           | range / default                      | notes                                                                      |
| --------------- | ------------------------------------ | -------------------------------------------------------------------------- |
| SCALE_AMP       | **0.008–0.015 default**              | push to 0.02–0.04 only when isolated on canvas / scene <6s / kinetic brief |
| Y_AMP_PX        | **2–3px default**                    | 4–6px only under the same gating; rotation ±0.3–0.8° rarely needed at all  |
| period          | 1.5–3s (2.5–4s when idle is long)    | <1.5s frantic; >4s lifeless in a short window                              |
| CYCLES          | `IDLE_DUR/3 ≤ CYCLES ≤ IDLE_DUR/1.5` | derive from the period, not the other way round                            |
| IDLE_START_TIME | ≥ entry settle + ~0.1s               | `sin(0)=0` at this moment → no jump off the entry tail                     |
| IDLE_DUR        | `TOTAL_DURATION − IDLE_START_TIME`   | one long tween fills the hold — never restarted                            |
| DOT_SCALE_AMP   | 0.04–0.12                            | small accents tolerate more than the hero                                  |
| OCTAVE_RATIO    | 2.0–4.0                              | integer-ish reads musical; non-integer reads organic                       |

## Critical Constraints

- **Prefer reveal, then jitter, then breath** — the doctrine order above; default to the LOW end of every amplitude range. At the upper end across 5+ consecutive scenes the whole film reads as "shimmering".
- **Long idle window** (`IDLE_DUR > 6s` OR idle > 30% of composition): halve `SCALE_AMP` / `Y_AMP_PX`, slow the period to 3–4s, and add the settle-and-fade tail.
- **Concurrent idle on N elements** (columns, card grid, stat row): per-element amplitude ≤ default `/ √N`, AND stagger the periods (2.1s / 1.9s / 2.4s). Three columns at ±6px compound to ±18px of competing motion; three at ±2–3px read as one collective breath.
- **Compose, don't replace** — idle ADDS to the element's resting transform; never overwrite the entry's final translation.
- **Phase tween `ease: "none"`** — sine itself is the curve.
- **No CSS `@keyframes` for idle** — CSS animation runs on the browser's render clock, independent of the HF seek clock; a CSS-driven idle flickers/desyncs. Drive idle inside the timeline.

## See also

`ambient-glow-bloom` (the glow-layer counterpart, same bounded-breathe discipline) · `press-release-spring` / `counting-dynamic-scale` / `card-morph-anchor` / `orbit-3d-entry` (settled elements this can follow) · `spring-pop-entrance` (the arrival that precedes any idle).

## Selected motion rule: svg-path-draw

---
name: svg-path-draw
description: Animate SVG paths drawing progressively using stroke-dasharray and stroke-dashoffset.
metadata:
  tags: svg, stroke, draw, path, reveal, icon, vector
---

# SVG Path Draw

Reveals an SVG shape by animating its stroke as if a pen were tracing it. Two stroke properties together: **`stroke-dasharray = <pathLength>`** makes the entire path one dash; **`stroke-dashoffset`** starts at the path length (dash shifted fully out of view → invisible) and tweens to `0` (fully drawn). The length comes from the DOM API `path.getTotalLength()` — measured, never guessed.

Works on anything with a stroke: `<path>`, `<circle>`, `<rect>`, `<line>`, `<polyline>`, `<polygon>`, `<ellipse>`.

## Recipe

```html
<!-- inside a standard scene clip -->
<svg class="logo-mark" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <path id="bar-left" d="M 60 40 L 60 160" />
  <path id="bar-right" d="M 140 40 L 140 160" />
  <path id="bar-mid" d="M 60 100 L 140 100" />
</svg>
```

```css
.logo-mark path {
  fill: none; /* outline-only draw — a fill would appear immediately and ruin the reveal */
  stroke: {accentColor};
  stroke-width: 12;
  stroke-linecap: round; /* softer endpoints */
  stroke-linejoin: round;
}
```

```js
// Setup: measure each path and set its dash pattern. Real measured geometry, not a magic number.
document.querySelectorAll(".logo-mark path").forEach((p) => {
  const len = p.getTotalLength();
  p.style.strokeDasharray = `${len}`;
  p.style.strokeDashoffset = `${len}`;
});

// Stagger draws so the eye reads continuous motion — each segment starts at
// ~70-80% of the previous segment's duration, before it finishes.
tl.to(
  "#bar-left",
  { strokeDashoffset: 0, duration: SEGMENT_DRAW_DUR, ease: "power2.out" },
  SEG_1_START,
);
tl.to(
  "#bar-right",
  { strokeDashoffset: 0, duration: SEGMENT_DRAW_DUR, ease: "power2.out" },
  SEG_2_START,
);
tl.to(
  "#bar-mid",
  { strokeDashoffset: 0, duration: FINAL_SEGMENT_DUR, ease: "power2.out" },
  SEG_3_START,
);

// Companion wordmark fades in only after the last stroke settles.
tl.to(
  ".brand-line",
  { opacity: 1, duration: BRAND_FADE_DUR, ease: "power1.out" },
  BRAND_FADE_START,
);
```

## Variations

- **Ring starting at 12 o'clock** — `<circle>` / `<rect>` strokes start at 3 o'clock by default; rotate the element `-90deg` so a progress ring draws from the top:

```html
<circle
  cx="100"
  cy="100"
  r="60"
  id="ring"
  style="transform-origin: 100px 100px; transform: rotate(-90deg)"
/>
```

- **Linear (constant-speed) draw** — `ease: "none"` for a steady-rate "real pen" trace.
- **Draw then fill** — for filled shapes, tween `fillOpacity: 0 → 1` AFTER the stroke completes (requires `fill-opacity: 0` initially and a real `fill` in CSS):

```js
tl.to(
  "#path",
  { strokeDashoffset: 0, duration: SEGMENT_DRAW_DUR, ease: "power2.out" },
  SEG_1_START,
);
tl.to(
  "#path",
  { fillOpacity: 1, duration: FILL_FADE_DUR, ease: "power1.out" },
  SEG_1_START + SEGMENT_DRAW_DUR,
);
```

## Values

| token             | range                                   | notes                                                                                              |
| ----------------- | --------------------------------------- | -------------------------------------------------------------------------------------------------- |
| SEGMENT_DRAW_DUR  | 0.3–0.8s                                | fast snap vs deliberate pen trace; >~1s feels sluggish for a logo reveal                           |
| FINAL_SEGMENT_DUR | 60–80% of SEGMENT_DRAW_DUR              | proportional to segment length — a short connector at full duration reads slower than its siblings |
| SEG_N_START       | previous start + 70–80% of its duration | reads as continuous motion, not N isolated animations                                              |
| SEG_1_START       | 0–0.4s                                  | a small ~0.2s lead-in lets the viewer settle before motion                                         |
| BRAND_FADE_START  | ≥ last stroke end (+ ~0.2s beat)        | earlier and the wordmark competes with the draw                                                    |
| BRAND_FADE_DUR    | 0.3–0.8s                                | snap (urgent) vs glide (premium)                                                                   |

Ease families are discrete choices: **stroke draws** use `power2.out` (a hand lifting at end of stroke) or `none` for constant speed — never `back.out` / `elastic.out` (pens don't bounce). **Fades** use `power1.out`.

## Critical Constraints

- **`fill: none`** for outline-only draws — otherwise the fill appears immediately.
- **Dasharray/dashoffset = the measured `getTotalLength()`**, set at setup; requires the SVG in the DOM (inline SVG is fine; a loaded `<image>` SVG is not).
- **Complex paths**: if `getTotalLength()` looks wrong, overestimate slightly (`len * 1.05`) — too large is invisible at animation start; too small clips the end.
- **Stagger multi-path draws at ~70–80%** of the previous segment's duration.
- **A drawn line must land on something.** When the path is a connector (rail, beam, underline, callout) rather than a shape, both endpoints must sit on real elements and the draw must do a job — reveal, route, validate, or emphasize. A stroke that only decorates empty space reads as filler; attach it or cut it.

## See also

`svg-icon-enrichment` (internal parts animate after the outline draws) · `counting-dynamic-scale` (stroke draws an icon while a number counts up) · `hacker-flip-3d` (logo draws, wordmark decodes beneath).
