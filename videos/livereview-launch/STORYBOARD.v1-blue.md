---
format: 1920x1080
duration: 150s
message: "You already generate code with AI — LiveReview is the AI-assisted inspection layer you owe your users."
arc: Hook (generation vs inspection) → Belief → Why (velocity · volume · limited attention) → Four problems → four problem→answer→proof→Solved acts → Close + CTA
audience: engineering leadership (CTO / VP Eng / EM), developers second
mode: autonomous
music: assets/bgm/bed-150.mp3 (150.048s) — music bed only; no VO, no SFX, no captions
---

# LiveReview — The Inspection Layer (51-slide deck cut)

Silent-except-music film: **every frame carries its own words.** The `voiceover:` field on each
frame is the ON-SCREEN copy, taken from the deck and phrase-segmented into reveal cues — it is
**not spoken**. Reading pace, not speech pace.

Story spine = the deck order (`../../ppt/LiveReview-Presentation-slides.md`). The deck names four
problems (ATTENTION · UNDERSTANDING · ENFORCEMENT · CONTROL and IMPROVE) and answers each with the
product. Those four acts are the film's skeleton; the close pays off all four.

**The cut is exactly 150.000s** so `bed-150.mp3` fits end to end with no loop seam. Frame durations
below sum to 150.0 — do not change one without rebalancing another.

Demo clips are 2520x1080 (21:9): always shown whole inside a framed dark app window, never cropped.

## Build notes (post-assembly fixes)

Applied by the orchestrator after the frame workers returned; keep them if frames are rebuilt:

- **Frame 1** — the lead-line swap was driven by inline `style.visibility`, which persists in the
  DOM after the frame's window closes, so "But do you do enough of…" stayed visible for the whole
  film. Moved onto the framework's clip gating (`class="clip"` + `data-start`/`data-duration` on
  `lead-a` / `lead-b` / `gen`); the inline-visibility director is gone.
- **Frame 3** — the mass block was tweened on `top`/`height` (layout properties snap to integer
  pixels under seek-by-frame capture). Pinned at its final rect and animated with a
  bottom-anchored `scaleY`.
- **Frame 14** — the seal fired at 11.9s, leaving it fully resolved for only 0.16s before the cut.
  Moved to 11.0s to match the other three acts, and both clips retimed to land flush at 11.0s
  (`clip08_schedule` 2.9→5.9 at rate 1.3333; `clip10_cicd` 5.9→11.0 at rate 1.3072) so no clip
  is left playing after its window fades.
- **Frame 17** — the seal's check sat before the arrow; reordered to `→ Solved ✓` to match acts 1-3.
- **Frame 20** — label grey was 2.65:1; darkened to `#909090` for WCAG AA.
- **index.html** — the assembler gives both clips of a two-clip frame the same generated id, and it
  drops `data-playback-rate` when hoisting. Patched in place: unique ids (`…-video-11b`,
  `…-video-13b`) and the rates restored. **Re-running `assemble-index.mjs` will undo both** (the
  videos now live only in `index.html`, having been hoisted out of the frame files), so patch
  `index.html` directly rather than reassembling.

## Video direction

- **Palette** (from `frame.md`, never invented): white ground `bg`; cobalt `primary` #1d56f0 is the
  ONLY accent — eyebrows, act pills, quadrant numerals, highlighted words, checkpoint dots, the CTA
  pill, the progress strip; headlines near-black `text`; body `text-muted`; tinted cards `card-bg`
  + `border`, 12–14px radius, no shadow. `negative` red appears ONLY where the deck's argument is
  pressure — the VOLUME flood in Frame 3, the struck-through "Aspirations" in Frame 13. `positive`
  green appears ONLY on the four ✅ in Frame 20 and the four "→ Solved" seals. Product clips live in
  a dark **app window** (`#0e1322` body, `#1a2440` hairline, 12px radius, 31px top bar with three
  dots) — the one dark surface in the film.
- **Type**: Inter only (`assets/fonts/Inter-var.woff2`), roles by `frame.md`'s ramp — h1/h2/h3
  near-black at −0.02em; eyebrow + act pill uppercase 0.08em cobalt; numerals cobalt 700.
  Load-bearing text ≥ 1.4cqw.
- **Reveal model — reading pace, not speech pace.** There is no voiceover: the `voiceover:` field is
  the frame's ON-SCREEN copy, segmented by `|` into reveal cues. Reveal each segment when the read
  reaches it — roughly one cue per 1.2–1.8s — spread across the shot and especially the back half.
  Never dump a frame's whole canvas at t=0.
- **Motion grammar**: long-tail eases, `power3.out` default; `expo.out` for a surface arriving;
  `back.out(2.2–2.6)` reserved for pills, chips and checkmarks only. Word reveals stagger 0.045–0.06s
  with a 6px blur burn-off. Once a frame has resolved it **holds still** — no drift, no breathing.
- **THE RECURRING MOTIF — the four-quadrant map.** A 2×2 grid of the deck's four problems is the
  film's spine. Frame 7 builds it full size at a fixed geometry that every later frame reuses:
  outer box **left 360, top 300, 1200×560**; four cells of 588×268 with a 24px gutter (cell 1 at
  360,300 · cell 2 at 972,300 · cell 3 at 360,592 · cell 4 at 972,592). Frames 9/11/13/15 carry the
  same grid **shrunk to a 132×62 glyph at 1656,96** with only its own quadrant filled cobalt.
  Frame 20 rebuilds the full-size grid at the **identical** coordinates and checks each cell off.
  The geometry never changes — that is what makes the payoff land.
- **Progress strip**: a 3px cobalt strip pinned to the bottom edge, width = elapsed/150. Every frame
  advances it linearly across its own window. It is the only element in the bottom band; captions are
  disabled, so no caption pill competes with it.
- **Rhythm / held frames**: Frames **5**, **8** and **18** are deliberate held beats — content
  resolves early and then reads still, against the busier frames around them. Frame 5 is the pivot
  breather, Frame 8 is the hard turn, Frame 18 is the climax.
- **App window geometry (identical in every clip frame)**: shell at **left 230, top 346, 1460×658**;
  31px top bar with three #334155 dots; the video rect is **x 232, y 379, 1456×623**, `object-fit:
  contain` — clips are 2520×1080 (21:9) and are never cropped. The shell rises into place and lands
  **before** its clip's `data-start`, then never moves again.
- **Negative list**: no nav bars, footers, scrollbars, browser chrome or real cursors; no floating
  bokeh or purple-blue "AI" gradients; no shadows on cards; no looping ambient drift; no second
  accent hue. Both motion failure modes are banned — **slideshow** (everything fired at t=0 then
  frozen) and **screensaver** (elements floating independently of the read).

## Frame 1 — You already do a lot of…

- scene: "AI-Assisted code generation" lands confident, then the frame flips the question to inspection
- duration: 8s
- transition_in: cut
- status: animated
- blueprint: kinetic-type-beats
- type: hook
- voiceover: "You already do a lot of… | AI-Assisted code generation. | But do you do enough of… | AI-Assisted Code Inspection?"
- asset_candidates: assets/brand-claude.svg, assets/brand-openai.svg, assets/brand-copilot.svg, assets/brand-gemini.svg
- src: compositions/frames/01-generation-vs-inspection.html
- roles: brand-claude/openai/copilot/gemini = supporting (drifting field, 22% opacity)
- progress: 0.0% → 5.3%
- handoff_out: none — Frame 2 opens on a clean white field.

Deck slides 1–2. The whole film in one move: the viewer is already spending on generation. The
accent word swaps in place — **generation** → **Inspection** — and the swap is the argument. AI
provider marks drift behind the first half, then clear away when the question turns.

- **blueprint: kinetic-type-beats (Adapt)** — keep the in-place token-swap signature; the swapped
  token is the whole argument (`generation` → `Inspection`). Changed: a supporting AI-mark field
  behind the first half, cleared by the swap.

Scene 1 (0.0–2.2s): white field. Eyebrow "01 · THE GAP" pops top-left; the h1 lead "You already do a
lot of…" reveals per word, upper-third, centered, ~55% of frame. Behind it, five AI provider marks
(Claude · OpenAI · Copilot · Gemini · DeepSeek) fade up at 22% opacity, scattered at layered depth,
drifting outward slowly — background layer only.
Scene 2 (2.2–3.8s): the payoff line "AI-Assisted code generation" scale-pops onto the centre line in
cobalt, tight under the lead. The mark field settles and stops.
Scene 3 (3.8–5.4s): hard beat — the lead swaps in place to "But do you do enough of…" (token swap,
no fade-out/fade-in drift), and the AI marks clear outward and vanish. The centre line is left empty.
Scene 4 (5.4–8.0s): "AI-Assisted Code Inspection?" types-in weight-first into the vacated centre
line, near-black, one size larger than the generation line; the "?" lands last and the frame holds
still. Centered, ~60% of frame, 3 depth layers (white ground · cleared mark field · type).
## Frame 2 — Here's what we believe

- scene: Three belief statements stack, each resolving on the same three words
- duration: 7.5s
- transition_in: cut
- status: animated
- blueprint: kinetic-type-beats
- type: hook
- voiceover: "Here's what we BELIEVE: | You owe your users and customers | If you are professional | For the sake of your business reputation | — an AI-assisted inspection layer."
- src: compositions/frames/02-belief.html
- progress: 5.3% → 10.3%

Deck slides 3–6. Three reasons converge on one fixed phrase. The phrase "AI-assisted inspection
layer" enters once and **never moves** while the reasons cycle above it — the anchor's stillness is
the claim.

- **blueprint: fixed-anchor-cycle (Adapt)** — keep the pinned-anchor signature: "AI-assisted
  inspection layer" enters once and never moves while the reasons cycle above it. Changed: the deck
  gives three reasons, so three cycles, not a carousel.

Scene 1 (0.0–1.4s): "Here's what we BELIEVE:" reveals per word, upper-third, near-black. Below it a
thin cobalt rule draws left-to-right and the anchor phrase "an AI-assisted inspection layer" fades up
beneath it in cobalt 700 — the anchor, lower-centre, and it never moves again.
Scene 2 (1.4–3.2s): reason 1 "You owe your users and customers" reveals into the slot above the rule.
Scene 3 (3.2–4.8s): reason 1 hard-cuts out and reason 2 "If you are professional" takes the same
slot — same baseline, same size, a swap not a transition.
Scene 4 (4.8–7.5s): reason 3 "For the sake of your business reputation" swaps in, then the anchor
phrase scale-pops once (1.0 → 1.06 → 1.0) as the three-reason build completes, and holds still.
Centered, ~50% of frame; hierarchy by position (reasons cycle, anchor is fixed).
## Frame 3 — Velocity into volume

- scene: "Great VELOCITY" accelerates into "HUGE VOLUME" as code lines flood the frame
- duration: 6s
- transition_in: cut
- status: animated
- blueprint: kinetic-type-beats
- type: pain_point
- voiceover: "Here's WHY: | Code accumulates at great VELOCITY | The higher velocity leads to HUGE VOLUME of code"
- src: compositions/frames/03-velocity-volume.html
- progress: 10.3% → 14.3%

Deck slides 7–9. VELOCITY is a rate; VOLUME is a mass. The motion has to earn both: fast streaking
lines that pile up and stop moving.

- **blueprint: kinetic-type-beats (Adapt)** — keep the escalating multi-beat statement; the motion
  must make VELOCITY a rate and VOLUME a mass, so the code-line field streaks then piles.

Scene 1 (0.0–1.3s): "Here's WHY:" alone, centered, near-black, holds one beat then shrinks up to the
eyebrow slot top-left as the frame opens out.
Scene 2 (1.3–3.2s): "Code accumulates at great VELOCITY" reveals per word across the upper third;
behind it thin cobalt code-lines streak in from the right at speed and exit left — a rate, nothing
accumulating yet. Full-width strip, 3 depth layers.
Scene 3 (3.2–5.0s): the streaking stops dead. The lines that are on screen fall and stack into a
dense block filling the lower 55% of the frame — the mass. A thin `negative` red hairline marks the
top of the stack as it grows.
Scene 4 (5.0–6.0s): "The higher velocity leads to HUGE VOLUME of code" lands over the stack, with
"HUGE VOLUME" in cobalt at 1.6x the surrounding size; the stack is still and the frame holds.
## Frame 4 — And you still must

- scene: Four obligations stack as cards under the volume pressure, none of them optional
- duration: 8s
- transition_in: cut
- status: animated
- blueprint: grid-card-assemble
- type: pain_point
- voiceover: "And you still need to deliver faster, safer, higher quality. | Reduce production incidents | Reduce security incidents | Reduce performance regressions | Deliver stellar customer experiences"
- src: compositions/frames/04-you-still-must.html
- progress: 14.3% → 19.7%

Deck slides 10–14. Four "you still must" lines accumulate as a vertical list. The accumulation is
the point — the list gets heavier while nothing is taken away.

- **blueprint: grid-card-assemble (Adapt)** — keep the staggered self-assembling list signature; the
  list is vertical and each row stays on screen, so weight accumulates rather than cycling.

Scene 1 (0.0–1.6s): lead line "And you still need to deliver faster, safer, higher quality" reveals
per word in the upper third; the code-stack from Frame 3 is gone, white ground.
Scene 2 (1.6–3.0s): row 1 "Reduce production incidents" slides up into a tinted card, left-aligned,
with a small cobalt index numeral. Asymmetric 60/40 — cards left, open white right.
Scene 3 (3.0–4.2s): row 2 "Reduce security incidents" assembles below it on the same stagger.
Scene 4 (4.2–5.4s): row 3 "Reduce performance regressions" assembles below.
Scene 5 (5.4–8.0s): row 4 "Deliver stellar customer experiences" assembles, then all four rows
settle together with a single 0.3s weight shift downward — the stack visibly gets heavier — and
holds. Four rows, none removed; density ≥ 40% of canvas.
## Frame 5 — Human attention is still limited

- scene: The stack of obligations compresses down to one thin line: finite attention
- duration: 4s
- transition_in: crossfade
- status: animated
- blueprint: titlecard-reveal
- type: pain_point
- voiceover: "And let's remember: | Human attention is still limited"
- src: compositions/frames/05-attention-limited.html
- progress: 19.7% → 22.3%

Deck slide 15. The breather beat — and the pivot. Everything before is demand; this is supply.

- **blueprint: titlecard-reveal (Reproduce)** — the calm breather. Exactly ONE restrained move, then
  a still hold. This frame is deliberately held; low motion IS the payload.

Scene 1 (0.0–1.2s): the four cards from Frame 4 are implied gone. "And let's remember:" fades up
small and grey in the upper third, centered.
Scene 2 (1.2–2.4s): "Human attention is still limited" slide-up crossfades into the centre line at
h1 scale, near-black, with "limited" in cobalt. One move only.
Scene 3 (2.4–4.0s): total stillness. Nothing animates but the progress strip. Centered, ~45% of
frame — the emptiest frame in the film, and the pivot from demand to supply.
## Frame 6 — More code means

- scene: One fixed lead-in, two consequences swapping into the same slot
- duration: 5.5s
- transition_in: cut
- status: animated
- blueprint: fixed-anchor-cycle
- type: pain_point
- voiceover: "More code means: | Bigger systems, inter connections | More complexity, bugs, issues"
- src: compositions/frames/06-more-code-means.html
- progress: 22.3% → 26.0%

Deck slides 16–19. "More code means:" is pinned; the consequence cycles beneath it. A sparse node
graph densifies behind the swap.

- **blueprint: fixed-anchor-cycle (Reproduce)** — "More code means:" is pinned and never moves; the
  consequence cycles beneath it while a node graph densifies behind.

Scene 1 (0.0–1.2s): "More code means:" reveals per word, pinned at the upper-left third. A sparse
node graph (9 cobalt nodes, 6 links) fades up at 18% behind the right two-thirds.
Scene 2 (1.2–3.0s): "Bigger systems, inter connections" reveals in the slot below the anchor; the
node graph grows links between existing nodes — connections, not new nodes.
Scene 3 (3.0–5.5s): the consequence hard-swaps to "More complexity, bugs, issues" in the same slot;
the graph doubles its node count and the links tangle, holding at ~28% opacity so the type stays
dominant. Anchor motionless throughout. Asymmetric 60/40, 3 depth layers.
## Frame 7 — Four problems

- scene: Four numbered problem cards assemble into a 2x2, each with its question
- duration: 8s
- transition_in: crossfade
- status: animated
- blueprint: grid-card-assemble
- type: pain_point
- voiceover: "#1 ATTENTION — Which changes deserve your engineers' scarce attention? | #2 UNDERSTANDING — How can your engineers maintain intellectual control of the system? | #3 ENFORCEMENT — How do you make good review happen every time without slowing the team down? | #4 CONTROL and IMPROVE — How to own your IP, your code, your data and your model interactions?"
- src: compositions/frames/07-four-problems.html
- progress: 26.0% → 31.3%
- handoff_out: the 2x2 grid — outer box at 360,300 1200x560, four cells 588x268 (360,300 / 972,300 / 360,592 / 972,592), opacity 1, scale 1, fully built, motionless at the cut.

Deck slides 20–25. **The film's skeleton.** This 2x2 is a map the viewer will see three more times —
each act lights up its own quadrant, and the close checks all four off.

- **blueprint: grid-card-assemble (Adapt)** — keep the staggered assemble into a grid; the grid is
  2x2 at a FIXED geometry that Frames 9/11/13/15 and 20 reuse. This is the film's map.

Scene 1 (0.0–1.0s): lead "And there are deeper consequences…" fades up in the eyebrow slot, then the
empty 2x2 outline draws on — outer box 360,300 1200x560, four cells 588x268 at 360,300 / 972,300 /
360,592 / 972,592, 1.5px cobalt-20% borders, 14px radius. Centered, ~62% of frame.
Scene 2 (1.0–2.8s): cell 1 fills — big cobalt "#1", label "ATTENTION", question "Which changes
deserve your engineers' scarce attention?" — on a stagger inside the cell (numeral pops, label
reveals, question fades up).
Scene 3 (2.8–4.4s): cell 2 fills the same way — "#2 UNDERSTANDING · How can your engineers maintain
intellectual control of the system?"
Scene 4 (4.4–6.0s): cell 3 fills — "#3 ENFORCEMENT · How do you make good review happen every time
without slowing the team down?"
Scene 5 (6.0–8.0s): cell 4 fills — "#4 CONTROL and IMPROVE · How to own your IP, your code, your
data and your model interactions?" — then all four cells settle and the grid holds completely still
for the last beat. Nothing moves at the cut.
## Frame 8 — Here's how LiveReview solves them all

- scene: The 2x2 collapses behind the LiveReview wordmark
- duration: 3s
- transition_in: cut
- status: animated
- blueprint: logo-assemble-lockup
- type: product_intro
- voiceover: "Here's HOW LiveReview solves them all:"
- asset_candidates: assets/logo.svg
- src: compositions/frames/08-heres-how.html
- focal: assets/logo.svg
- roles: logo.svg = focal (centered lockup)
- progress: 31.3% → 33.3%
- handoff_in: the 2x2 grid arrives exactly as Frame 7 left it — same coordinates, opacity 1, scale 1 — and is the first thing that moves.

Deck slide 26. The turn. Short and hard — the problems have been stated, now the product arrives.

- **blueprint: logo-assemble-lockup (Adapt)** — keep the mark coming-to-exist signature; here it is
  built out of the collapsing grid rather than from abstract parts. A held turn: short and hard.

Scene 1 (0.0–1.0s): the 2x2 arrives exactly as Frame 7 left it and immediately collapses — the four
cells scale down and converge on frame centre on one heavy ease, their borders dissolving.
Scene 2 (1.0–1.8s): at the convergence point the LiveReview mark (`assets/logo.svg`) spring-blooms
from zero to full, centered, ~24% of frame width.
Scene 3 (1.8–3.0s): "Here's HOW LiveReview solves them all:" reveals per word beneath the mark and
the frame holds still. Centered, ~40% of frame. Deliberately held — this is the turn.
## Frame 9 — Problem 1: attention

- scene: Quadrant #1 lights up; the attention question stands alone
- duration: 4s
- transition_in: cut
- status: animated
- blueprint: kinetic-type-beats
- type: pain_point
- voiceover: "#1 ATTENTION | There's a lot of code, limited engineering attention"
- src: compositions/frames/09-problem-attention.html
- progress: 33.3% → 36.0%

Deck slide 27. Act 1 opens. The quadrant chrome from Frame 7 returns as a small act marker.

- **blueprint: kinetic-type-beats (Reproduce)** — short pain statements landing alone on a bare
  canvas, with the act marker establishing which quadrant we are in.

Scene 1 (0.0–0.9s): the 2x2 glyph (132x62 at 1656,96) draws on top-right with cell 1 filled cobalt
and cells 2–4 as empty outlines. The act pill "#1 · ATTENTION" pops top-left.
Scene 2 (0.9–2.4s): "There's a lot of code," reveals per word, centered, h1 scale, near-black.
Scene 3 (2.4–4.0s): "limited engineering attention" reveals on the line beneath with "limited" in
cobalt, then holds. Centered, ~50% of frame.
## Frame 10 — Ranked by blast radius

- scene: The answer line, then the real diff scoring every hunk, then "→ Solved"
- duration: 13s
- transition_in: cut
- status: animated
- blueprint: video-text-pivot
- type: feature_showcase
- voiceover: "LiveReview ranks every hunk by blast radius and review priority. | The Attention Problem → Solved"
- asset_candidates: assets/clip05_blast.mp4, assets/risk-score_new-risk-score-4.webp
- src: compositions/frames/10-blast-radius.html
- focal: assets/clip05_blast.mp4
- roles: clip05_blast = focal (app window, contain) · risk-score_new-risk-score-4.webp = unused backup
- progress: 36.0% → 44.7%

Deck slides 28–30. The answer line holds, the app window rises with `clip05_blast.mp4` (8s) playing
whole, then the window recedes and **"The Attention Problem → Solved"** seals the act.

- **blueprint: video-text-pivot (Adapt)** — keep the "video holds, then hands its weight to the
  payoff" signature; the payoff here is the "→ Solved" seal rather than a stat. The window never
  slides: it rises once, holds under the clip, then recedes.

Scene 1 (0.0–1.0s): act pill "#1 · ATTENTION" and the quadrant glyph carry over from Frame 9. The
answer line "LiveReview ranks every hunk by blast radius and review priority." reveals per word in
the upper third, with "blast radius" and "review priority" in cobalt 600.
Scene 2 (1.0–2.0s): the dark app window rises from below into 230,346 1460x658 on a long-tail
settle and LANDS — fully at rest before the clip starts.
Scene 3 (2.0–10.0s): `assets/clip05_blast.mp4` plays whole in the window rect 232,379 1456x623,
contain, rate 1.0 — the diff ordered by score, the "71 High risk" popover, the sunburst. The frame
is otherwise still; the clip is the only motion. At 6.2s a small white "71 · HIGH RISK" chip springs
in beside the window's lower-right edge, in `negative` red, and holds.
Scene 4 (10.0–13.0s): the window and chip fade down to 0 together; "The Attention Problem" reveals
centered, then "→ Solved" scale-pops beside it in `positive` green with a check. Holds still.
## Frame 11 — Problem 2: understanding

- scene: Quadrant #2 lights up; the understanding question stands alone
- duration: 4s
- transition_in: cut
- status: animated
- blueprint: kinetic-type-beats
- type: pain_point
- voiceover: "#2 UNDERSTANDING | How to make sure engineers have intellectual understanding of the system, and take responsibility?"
- src: compositions/frames/11-problem-understanding.html
- progress: 44.7% → 47.3%

Deck slide 31. Act 2 opens.

- **blueprint: kinetic-type-beats (Reproduce)** — same shape as Frame 9 so the four acts read as a
  set; only the quadrant and the words change.

Scene 1 (0.0–0.9s): the 2x2 glyph redraws top-right with cell 2 now filled cobalt (cell 1 drops to a
20% cobalt tint — solved, not active). Act pill "#2 · UNDERSTANDING" pops top-left.
Scene 2 (0.9–2.2s): "How do engineers keep intellectual understanding of the system" reveals per
word, centered, h2 scale.
Scene 3 (2.2–4.0s): "— and take responsibility?" reveals beneath, with "responsibility" in cobalt,
then holds.
## Frame 12 — Summaries, navigation, quizzes

- scene: The answer line, then the summary deck and the quiz play back to back, then "→ Solved"
- duration: 12.5s
- transition_in: cut
- status: animated
- blueprint: video-text-pivot
- type: feature_showcase
- voiceover: "LiveReview gives summaries, issue navigation, and PR quizzes to keep humans in the loop. | The Understanding Problem → Solved"
- asset_candidates: assets/clip11_slides.mp4, assets/clip11_quiz.mp4
- src: compositions/frames/12-understanding-answer.html
- focal: assets/clip11_slides.mp4
- roles: clip11_slides = focal (app window, contain) · clip11_quiz = focal (same window, hard cut after)
- progress: 47.3% → 55.7%

Deck slides 32–34. Two clips in one window: `clip11_slides.mp4` (5.3s) then `clip11_quiz.mp4`
(2.7s), hard-cut between them inside the same frame. Then the "→ Solved" seal.

- **blueprint: video-text-pivot (Adapt)** — same window discipline as Frame 10, but TWO clips hard-cut
  inside the one window: the summary deck, then the quiz.

Scene 1 (0.0–1.0s): act pill and quadrant glyph carry over. "LiveReview gives summaries, issue
navigation, and PR quizzes" reveals per word in the upper third, the three nouns in cobalt 600.
Scene 2 (1.0–2.0s): the app window rises into 230,346 1460x658 and lands at rest.
Scene 3 (2.0–7.33s): `assets/clip11_slides.mp4` plays whole in the rect, contain, rate 1.0 — the
60-second summary deck. The sub-line "…to keep humans in the loop." fades up under the title at 3.4s.
Scene 4 (7.33–10.0s): HARD CUT inside the window to `assets/clip11_quiz.mp4`, rate 1.0 — the quiz on
the diff. No crossfade; the window frame itself does not move, only its content swaps.
Scene 5 (10.0–12.5s): window fades down; "The Understanding Problem" + "→ Solved" resolve exactly as
in Frame 10 — same position, same green, same check. Holds still.
## Frame 13 — Problem 3: enforcement

- scene: Quadrant #3 lights up; aspirations struck through
- duration: 4.5s
- transition_in: cut
- status: animated
- blueprint: kinetic-type-beats
- type: pain_point
- voiceover: "#3 ENFORCEMENT | Aspirations don't work — you need finegrained enforcement mechanisms. | How to make sure good inspections happen consistently at scale?"
- src: compositions/frames/13-problem-enforcement.html
- progress: 55.7% → 58.7%

Deck slides 35–36. Act 3 opens. "Aspirations" gets visibly struck through — the one place in the
film where a word is deleted rather than replaced.

- **blueprint: kinetic-type-beats (Adapt)** — same act shape as Frames 9/11, with ONE deviation that
  exists nowhere else in the film: a word is struck through rather than replaced.

Scene 1 (0.0–0.9s): the 2x2 glyph redraws with cell 3 filled cobalt (cells 1–2 at 20% tint). Act pill
"#3 · ENFORCEMENT" pops top-left.
Scene 2 (0.9–2.3s): "Aspirations don't work" reveals per word, centered, h1 scale. A `negative` red
rule then draws left-to-right straight through "Aspirations" — the only strikethrough in the film.
Scene 3 (2.3–3.4s): "— you need finegrained enforcement mechanisms." reveals beneath in near-black.
Scene 4 (3.4–4.5s): the question "How do you make good inspections happen consistently at scale?"
fades up small and grey below, then holds.
## Frame 14 — Every checkpoint, every time

- scene: Five checkpoints light along a pipeline rail, then scheduled reviews and the CI/CD gate, then "→ Solved"
- duration: 13s
- transition_in: cut
- status: animated
- blueprint: video-text-pivot
- type: feature_showcase
- voiceover: "LiveReview reviews at commit, push, PR, CI/CD, and on schedule — enforcing your rules. | The Enforcement Problem → Solved"
- asset_candidates: assets/clip08_schedule.mp4, assets/clip10_cicd.mp4
- src: compositions/frames/14-enforcement-answer.html
- focal: assets/clip10_cicd.mp4
- roles: clip08_schedule = supporting (app window, first) · clip10_cicd = focal (same window, hard cut after)
- progress: 58.7% → 67.3%

Deck slides 37–39. A five-stop rail (commit · push · PR · CI/CD · schedule) lights stop by stop,
then the window plays `clip08_schedule.mp4` (4s) → `clip10_cicd.mp4` (6.7s). Then the seal.

- **blueprint: video-text-pivot (Adapt)** — the window discipline of Frames 10/12, preceded by a
  five-stop rail that makes "every checkpoint" literal before any footage plays.

Scene 1 (0.0–2.0s): act pill and glyph carry over. A horizontal rail spans the upper third with five
cobalt stops — commit · push · PR · CI/CD · schedule — and the stops light left to right on a 0.3s
stagger, each label fading up as its dot fills.
Scene 2 (2.0–2.9s): the rail shrinks and docks under the title line; the app window rises into
230,346 1460x658 and lands at rest.
Scene 3 (2.9–6.9s): `assets/clip08_schedule.mp4` plays whole in the rect, contain, rate 1.0 — the
Ctrl+K "Schedule Review" flow into the Scheduled Reviews table. The "schedule" stop on the docked
rail is highlighted while it plays.
Scene 4 (6.9–11.0s): HARD CUT inside the window to `assets/clip10_cicd.mp4` at rate 1.333 (6.667s →
5.0s, ending flush at 11.0s) — the CI/CD gate ruleset and the jq expression. The "CI/CD" stop takes
the highlight.
Scene 5 (11.0–13.0s): window fades down; "The Enforcement Problem" + "→ Solved" resolve in the
established position. Holds still.
## Frame 15 — Problem 4: control

- scene: Quadrant #4 lights up; the ownership question
- duration: 4.5s
- transition_in: cut
- status: animated
- blueprint: kinetic-type-beats
- type: pain_point
- voiceover: "#4 CONTROL and IMPROVE | You need a strong inspection capability while maintaining control. | You own your IP, your data, your model interactions — and use them to improve market competitiveness."
- src: compositions/frames/15-problem-control.html
- progress: 67.3% → 70.3%

Deck slides 40–41. Act 4 opens.

- **blueprint: kinetic-type-beats (Reproduce)** — the fourth and last act opener; same shape as 9/11
  so the set closes cleanly.

Scene 1 (0.0–0.9s): the 2x2 glyph redraws with cell 4 filled cobalt (cells 1–3 at 20% tint). Act pill
"#4 · CONTROL AND IMPROVE" pops top-left.
Scene 2 (0.9–2.4s): "You need a strong inspection capability" reveals per word, centered.
Scene 3 (2.4–4.5s): "while maintaining control." reveals beneath with "control" in cobalt, then the
sub-line "Your IP. Your data. Your model interactions." fades up small and grey and holds.
## Frame 16 — Your infrastructure, your models

- scene: A server boundary holds the code inside; AI provider marks queue at the edge and one is chosen
- duration: 7.5s
- transition_in: cut
- status: animated
- blueprint: constellation-hub
- type: feature_showcase
- voiceover: "Keep your code in your infrastructure | and choose which AI models inspect it."
- asset_candidates: assets/brand-claude.svg, assets/brand-openai.svg, assets/brand-gemini.svg, assets/brand-deepseek.svg, assets/brand-openrouter.svg, assets/logo.svg
- src: compositions/frames/16-self-host-models.html
- focal: assets/logo.svg
- roles: logo.svg = focal (inside the boundary) · brand-claude/openai/gemini/deepseek/openrouter = supporting (outside the boundary)
- progress: 70.3% → 75.3%

Deck slides 42–43. The only frame with a spatial idea: a boundary. Code stays inside it; models are
selected from outside it. The AI marks from Frame 1 return here — they wrote the code, now you pick
which one inspects it.

- **blueprint: constellation-hub (Adapt)** — keep the nodes-spring-into-a-ring-around-a-centre
  signature, but cut the ring with a BOUNDARY: the hub and the code sit inside a drawn perimeter and
  the model marks stay outside it. The boundary is the argument.

Scene 1 (0.0–1.4s): "Keep your code in your infrastructure" reveals per word in the upper third. A
dashed cobalt perimeter (rounded rect, ~640x420, centred at 760,660) draws itself on, and the
LiveReview mark plus a small stack of code-line glyphs fade up INSIDE it.
Scene 2 (1.4–3.4s): five AI provider marks (Claude · OpenAI · Gemini · DeepSeek · OpenRouter) spring
in one by one along an arc OUTSIDE the perimeter to the right, each in a white tinted chip. None
crosses the boundary.
Scene 3 (3.4–5.4s): "and choose which AI models inspect it." reveals beneath the first line. One mark
— Claude — scales up 1.18x and a thin cobalt connector draws from it to the perimeter edge and stops
AT the edge; the other four dim to 35%.
Scene 4 (5.4–7.5s): a small cobalt pill "your infrastructure" fades up on the perimeter's lower edge,
and the frame holds still. Asymmetric 60/40 (boundary left-of-centre, marks right), 3 depth layers.
## Frame 17 — Adaptive, learning, everywhere you work

- scene: Three capability lines, Livi answering a real question, then "→ Solved"
- duration: 12.5s
- transition_in: cut
- status: animated
- blueprint: video-text-pivot
- type: feature_showcase
- voiceover: "Adaptive Reviews cut AI cost. | Livi learns from your reviews. | CLI, IDE, MCP and API fit your workflow. | The Control and Improve Problem → Solved"
- asset_candidates: assets/clip15_livi.mp4, assets/lrbot_lrbot.png, assets/extensions_vscode-logo.png, assets/extensions_cursor-logo.png
- src: compositions/frames/17-control-answer.html
- focal: assets/clip15_livi.mp4
- roles: clip15_livi = focal (app window, contain) · lrbot_lrbot.png = supporting (Livi avatar chip) · vscode/cursor logos = supporting (interfaces row)
- progress: 75.3% → 83.7%

Deck slides 44–46. `clip15_livi.mp4` (8.1s) carries it — Livi answering "Are engineers actually
incorporating reviews into their daily workflow?" with real charts. Then the fourth seal.

- **blueprint: video-text-pivot (Adapt)** — the last window frame; three capability lines accumulate
  BEFORE the clip rather than after, so the clip is the proof of the third one.

Scene 1 (0.0–2.0s): act pill and glyph carry over. Three short capability lines assemble as a
staggered vertical list, upper-left, each with a cobalt index dot: "Adaptive Reviews cut AI cost." ·
"Livi learns from your reviews." · "CLI, IDE, MCP and API fit your workflow." The VS Code and Cursor
marks fade up small beside the third line.
Scene 2 (2.0–2.9s): the list docks to a single condensed line at the top; the app window rises into
230,346 1460x658 and lands at rest. The Livi avatar chip (`assets/lrbot_lrbot.png`) pops at the
window's upper-left corner.
Scene 3 (2.9–11.03s): `assets/clip15_livi.mp4` plays whole in the rect, contain, rate 1.0 — Livi
answering "Are engineers actually incorporating reviews into their daily workflow?" with the Daily
Review Activity and Engineer Adoption charts. Frame otherwise still.
Scene 4 (11.03–12.5s): window and avatar fade down; "The Control and Improve Problem" + "→ Solved"
resolve in the established position — the fourth and final seal. Holds still.
## Frame 18 — A full blown inspection layer

- scene: The film's thesis, at its largest, all four quadrants glowing behind it
- duration: 5s
- transition_in: crossfade
- status: animated
- blueprint: kinetic-type-beats
- type: benefit_highlight
- voiceover: "And that's why you owe your customers, profession and reputation | A FULL BLOWN AI-ASSISTED CODE INSPECTION LAYER"
- src: compositions/frames/18-full-blown-layer.html
- progress: 83.7% → 87.0%

Deck slide 47. The callback to Frame 2's belief, now earned. Biggest type in the film.

- **blueprint: kinetic-type-beats (Adapt)** — the climax. Keep the escalating multi-beat build onto a
  spring-pop payoff; the payoff is the largest type in the film. Deliberately held at the end.

Scene 1 (0.0–1.6s): all four quadrant glyph cells are shown filled cobalt, centred small and high,
then dissolve. "And that's why you owe your customers, profession and reputation" reveals per word
beneath, grey, small — deliberately understated.
Scene 2 (1.6–2.6s): "A FULL BLOWN" scale-pops onto the centre line, near-black, uppercase.
Scene 3 (2.6–3.6s): "AI-ASSISTED" lands beneath it on the same beat, one step larger.
Scene 4 (3.6–5.0s): "CODE INSPECTION LAYER" lands last and largest, in cobalt, and everything stops.
Total stillness for the final beat — the biggest type in the film, motionless. Centered, ~70% of
frame; this is the callback to Frame 2's anchor phrase, now earned.
## Frame 19 — One unified system

- scene: Dashboard and report footage plays behind the claim that it is all one platform
- duration: 7s
- transition_in: cut
- status: animated
- blueprint: device-surface-showcase
- type: social_proof
- voiceover: "LiveReview is the only platform that solves all the major issues in one unified system"
- asset_candidates: assets/clip13_dashboard.mp4, assets/clip16_report.mp4
- src: compositions/frames/19-one-system.html
- focal: assets/clip13_dashboard.mp4
- roles: clip13_dashboard = focal (app window, contain) · clip16_report = unused backup
- progress: 87.0% → 91.7%
- handoff_out: the app window sits at 230,346 1460x658, opacity 1, scale 1, motionless at the cut; Frame 20 opens on white with no window.

Deck slides 48–49. Breadth proof: `clip13_dashboard.mp4` (7.1s) held in the window while the claim
sits over it.

- **blueprint: device-surface-showcase (Reproduce)** — the window held as hero while the real product
  cycles inside it; the claim sits over the footage rather than replacing it.

Scene 1 (0.0–0.8s): the app window rises into 230,346 1460x658 and lands at rest — faster than the
act frames, because the film is closing.
Scene 2 (0.8–7.0s): `assets/clip13_dashboard.mp4` plays in the rect, contain, rate 1.14 (7.067s →
6.2s, ending flush at 7.0s) — the review-pipeline Sankey, the issue treemap, the category radar, the
contribution heatmap. Over it, in the upper third and clear of the window, "the only platform that
solves all the major issues" reveals per word at 1.4s, and "in one unified system" lands in cobalt at
3.6s. Nothing else moves; the dashboard's own motion carries the frame.
## Frame 20 — Four problems, four checks

- scene: The Frame 7 2x2 returns and each quadrant checks off in turn
- duration: 7.5s
- transition_in: cut
- status: animated
- blueprint: grid-card-assemble
- type: benefit_highlight
- voiceover: "Here's what LiveReview solves: | The attention problem ✅ | The understanding problem ✅ | The enforcement problem ✅ | The control and improve problem ✅"
- src: compositions/frames/20-four-checks.html
- progress: 91.7% → 96.7%
- handoff_in: the 2x2 grid rebuilds at the exact Frame 7 geometry (outer 360,300 1200x560; cells at 360,300 / 972,300 / 360,592 / 972,592).
- handoff_out: the four checked cells are at opacity 1, scale 1, motionless at the cut; Frame 21 crossfades from them.

Deck slide 50. **The payoff frame.** The exact 2x2 from Frame 7, same positions, same cards — now
each one flips to a check. Nothing new is introduced; the frame's whole job is closure.

- **blueprint: grid-card-assemble (Adapt)** — the payoff frame. Nothing new is introduced: the EXACT
  Frame 7 grid rebuilds at the identical geometry and each cell checks off in turn.

Scene 1 (0.0–1.0s): "Here's what LiveReview solves:" reveals in the eyebrow slot, and the 2x2 rebuilds
instantly at the Frame 7 geometry — outer 360,300 1200x560, cells at 360,300 / 972,300 / 360,592 /
972,592 — with all four labels already present and greyed.
Scene 2 (1.0–2.4s): cell 1 flips — the label "The attention problem" goes near-black and a `positive`
green ✅ spring-pops at the cell's right edge; the cell's border warms to green.
Scene 3 (2.4–3.8s): cell 2 flips the same way — "The understanding problem ✅".
Scene 4 (3.8–5.2s): cell 3 flips — "The enforcement problem ✅".
Scene 5 (5.2–7.5s): cell 4 flips — "The control and improve problem ✅" — then all four checks pulse
once together (1.0 → 1.07 → 1.0) and the grid holds completely still. Centered, ~62% of frame.
## Frame 21 — hexmos.com/livereview

- scene: The checked grid clears into the wordmark and the URL
- duration: 5s
- transition_in: crossfade
- status: animated
- blueprint: logo-assemble-lockup
- type: cta
- voiceover: "LiveReview | hexmos.com/livereview"
- asset_candidates: assets/logo.svg
- src: compositions/frames/21-cta.html
- focal: assets/logo.svg
- roles: logo.svg = focal (centered lockup above the URL)
- progress: 96.7% → 100%

Deck slide 51. Held long enough to read and type. The bed's tail fades under it.

- **blueprint: logo-assemble-lockup (Reproduce)** — the checked grid clears and the mark settles as
  the satellites go; extended to the URL end card.

Scene 1 (0.0–1.2s): the four checked cells scale down and clear outward; the LiveReview mark
(`assets/logo.svg`) is already at centre and settles into place as they go, ~26% of frame width.
Scene 2 (1.2–2.4s): "hexmos.com/livereview" reveals beneath the mark inside a cobalt pill, letter by
letter, at h2 scale.
Scene 3 (2.4–5.0s): total stillness — held long enough to read and type. The progress strip completes
to 100% and the music bed fades out beneath it. Centered, ~35% of frame.
