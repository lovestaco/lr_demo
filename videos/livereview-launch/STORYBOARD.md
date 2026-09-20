---
format: 1920x1080
duration: 120s
message: "LiveReview is the independent inspection layer over your AI stack — so review effort lands where the blast radius is"
arc: "PAS with feature-benefit progression — WHY (pain) → WHAT (inspection layer) → HOW (blast radius) → WHEN/WHERE (five pillars) → recap"
audience: "engineering leadership (CTO / VP Eng / EM) first, developers second"
mode: collaborative
music: measured cinematic tech underscore, restrained, minor-to-major turn at the Rickover beat
---

## Video direction

Written once; every frame inherits it. Per-frame Scene lines carry only the delta.

**Palette system** (roles from `frame.md`, never invented): `bg #ffffff` is the ground on every
frame — the product footage is always card-mounted on it, never full-bleed, because that is how
the brand's own landing page sets its dark screens into a light page. `text #05070b` is display
ink. `primary #1d56f0` is the single accent and marks exactly one focal per frame. `negative
#dc2626` is reserved for risk and appears in only three places in the whole film: the 3-line cell
(F05), the severity marks in the Review footage (F09), and the critical-findings figure (F12).
`text-light #9A9A9A` is for de-emphasis. Type by role only — display ramp for headlines and
numerals, body for supporting lines, never a raw family or px.

**Motion grammar + reveal model**: long-tail decel everywhere — `power3` is the default settle, no
`back.out` / `bounce.out` / `elastic.out`, no hand-keyed overshoot. Every frame is VO-paced: at
t=0 only what the voiceover is saying then is on screen, and each further piece reveals on its own
spoken cue, weighted into the back half of the shot. Nothing front-loads. Entrances use `fromTo`
with explicit from-state. During a hold the only sanctioned aliveness is low-amplitude subtle
jitter (`sine-wave-loop`); no breathing, no back-half pan or push.

**Rhythm — held frames, allocated deliberately**: **F03** (the Rickover quote) is the stillest
frame in the film and holds dead still with no jitter at all — it is the breath after F02's crowd
and the pivot the whole story turns on. **F05** holds both cells motionless once the badge lands.
**F08** locks and holds once the return edge closes. **F15** holds from 2.9s. Everything else
reveals against the voiceover. The film's energy arc is: rising (F01–F02) → dead still (F03) →
building (F04–F08) → steady tour (F09–F13) → slam-and-settle (F14–F15).

**Continuity — the ring is the film's spine**: F08 places five nodes at fixed ring positions.
F09–F13 each lift *their own* node out of that ring as the section marker (`card-morph-anchor`),
so the pillar tour reads as a tour of one diagram rather than five new lists. F14 closes the ring
again behind the final clause. Node positions are set once in F08 and never move.

**Footage handling**: every segment of `Ws66OKXUwwE.mp4` is cropped `2192:830:164:0` before use —
this strips the container pillarbox and the original's unplated burned-in captions in one pass.
No reused segment may show the old caption band.

**Caption-band keep-out**: the bottom ~17% of the canvas carries the caption pill. All frame
content plans into the top ~83%; nothing load-bearing sits below that line, captions on or off.

**Negative list — never appears**: nav bars, footers, scrollbars, browser chrome, or a real OS
cursor (the footage's own in-app cursor is fine); generic decorative shapes standing in for a real
asset; floating bokeh or purple-blue "AI" gradients; stock-photo texture. And both motion failure
modes are banned outright — **slideshow** (everything dumped in the first 25%, then frozen) and
**screensaver** (elements floating independently to fake life). No `repeat` / `yoyo`, no
`Math.random` / `Date.now`, no CSS `transition` / `@keyframes` for motion.

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

## Frame 2 — The question everyone is already asking

- status: animated
- src: compositions/frames/02-the-question.html
- type: pain_point
- duration: 6.123s
- transition_in: cut
- narrativeRole: Agitate — prove the pain is not one role's complaint but the same worry arriving at every level at once.
- scene: Comic role panels crowd in from the edges, each carrying its real speech bubble, until they surround the frame.
- voiceover: "The CTO asks whether you're getting sloppier. The developer asks why nobody told them sooner."
- blueprint: overwhelm-surround (Adapt)
- focal: capture/assets/transform_role-benefits-comic.png
- roles: role-benefits-comic = supporting (cropped BEFORE panels, card scale only)
- sfx: whoosh-short, impact-bass-2
- asset_candidates: capture/assets/transform_role-benefits-comic.png

Crop the BEFORE panels out of the role comic and bring them in as cards — CTO/VP Eng ("AI is
making us faster. Is it also making us sloppier?"), Developer ("Why didn't I know this before
opening the PR?"), Business Leadership (the burning production server), Engineering Manager.
They arrive staggered and close in. **The comic is 1480x704 — a single panel is ~350x200, so
these stay card-scale. Never blow one up full-bleed.** Hold on a crowded, unanswered frame.

Adapt: keep overwhelm-surround's accumulate-then-close-in signature, but the density markers are cropped comic panels and there is no avatar morph — the centre stays empty, because the unanswered question is the point.

Scene 1 (0.0–1.9s): near-empty frame; the CTO panel arrives from upper-left on a smooth long-tail settle (`spring-pop-entrance`), its speech bubble legible at card scale (~26% of frame). Layered-depth, 3 layers.
Scene 2 (1.9–3.6s): on "the developer asks", the Developer panel arrives from lower-right (`spring-pop-entrance`); the Business Leadership and Engineering Manager panels follow staggered into the remaining two corners (`center-outward-expansion`, run inward).
Scene 3 (3.6–5.2s): all four panels drift inward, closing the negative space — the surround. `depth-of-field-blur` softens the two secondary panels so only the CTO and Developer bubbles stay readable.
Scene 4 (5.2–6.123s): hold on the crowded frame with the centre still empty. Still; subtle jitter only. Nothing answers the question — F03 does.

## Frame 3 — You get what you inspect

- status: animated
- src: compositions/frames/03-you-get-what-you-inspect.html
- type: product_intro
- duration: 6.699s
- transition_in: blur-crossfade
- narrativeRole: The turn. The calm beat that answers the crowd, and where the video's value claim lands.
- scene: The crowd clears to one still quote card — Rickover's portrait beside the line.
- voiceover: "Admiral Rickover ran the nuclear navy on one rule: you get what you inspect, not what you expect."
- blueprint: titlecard-reveal (Reproduce)
- focal: capture/assets/rickover_rickover-portrait.jpg
- roles: rickover-portrait = cutout
- sfx: none — the silence is the beat
- asset_candidates: capture/assets/rickover_rickover-portrait.jpg

Stillness is the payload. After the overwhelm this frame barely moves: the portrait and the
quote, one restrained reveal, then a held hold. Attribution set small — "Admiral Hyman G.
Rickover, U.S. Navy". This is the frame the whole film pivots on; give it air.

Reproduce: titlecard-reveal's calm landing beat, wipe-away-to-reveal variant. Exactly ONE restrained move, then a still hold. This is the stillest frame in the film — do not add jitter.

Scene 1 (0.0–2.2s): F02's crowd hands off — the portrait wipes up from the lower edge into the left third on a single long-tail move (`scale-swap-transition` receiving the outgoing cluster). Rule-of-thirds; portrait ~30% of frame.
Scene 2 (2.2–4.6s): as the VO reaches the quote, the line reveals per-word across the right two-thirds in display type (`dynamic-content-sequencing`), with "inspect" and "expect" each landing on their own spoken beat.
Scene 3 (4.6–6.699s): the attribution sets small beneath the quote; `asr-keyword-glow` touches "inspect", then "expect", synced to the word rail. The frame then holds **dead still** — no push, no drift, no jitter. The stillness is the payload.

## Frame 4 — An independent inspection layer

- status: animated
- src: compositions/frames/04-inspection-layer.html
- type: product_intro
- duration: 8.981s
- transition_in: push-slide
- narrativeRole: Name the product as a category, not a feature list — the layer that sits above whatever writes the code.
- scene: AI provider marks ring a center; the LiveReview layer resolves above them.
- voiceover: "LiveReview is that inspection layer. Independent — and sitting above whatever writes your code. Claude. Copilot. Cursor. Anything."
- blueprint: constellation-hub (Adapt)
- focal: capture/assets/logo.svg
- roles: logo = cutout · deepseek-logo = supporting · openrouter-logo = supporting
- sfx: whoosh, ping
- asset_candidates: assets/logo.svg, assets/brand-claude.svg, assets/brand-copilot.svg, assets/brand-cursor.png, assets/brand-deepseek.svg, assets/brand-openrouter.svg

Claude, Copilot, Cursor, OpenAI, Gemini as the ring — the first three are wordmarks on the site
with no file, so set them as type; DeepSeek and OpenRouter have real SVGs. The pillar word here
is **above**: the layer is not another generator in the ring, it is the thing over it. Land on
the LiveReview mark.

Adapt: keep constellation-hub's ring of nodes and its camera push-in, but resolve the hub ABOVE the ring rather than at its centre — "above your stack" is the claim, so the geometry has to say it.

Scene 1 (0.0–2.4s): "LiveReview is that inspection layer" — the mark enters centred on a smooth long-tail settle (`spring-pop-entrance`). Nothing else on screen.
Scene 2 (2.4–4.4s): on "sitting above", the mark rises to the upper third and a thin full-width rule draws beneath it (`svg-path-draw`) — the layer line.
Scene 3 (4.4–7.4s): as the VO names them, Claude, then Copilot, then Cursor flip in at their ring positions below the rule, one per spoken name (`orbit-3d-entry`, entry only, no continuing orbit); the DeepSeek and OpenRouter marks follow staggered on "anything". **Every provider card carries its real brand mark beside the name** — all five marks are staged in `assets/` and none is set as bare type.
Scene 4 (7.4–8.981s): SVG connectors draw upward from each provider to the layer rule (`avatar-cloud-network`); a single slow push settles (`multi-phase-camera`) and stops. Hold.

## Frame 5 — Not all diffs are equal

- status: animated
- src: compositions/frames/05-not-all-diffs-equal.html
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

## Frame 6 — Scored by blast radius

- status: animated
- src: compositions/frames/06-blast-radius-scored.html
- type: feature_showcase
- duration: 9.067s
- transition_in: push-slide
- narrativeRole: Show the mechanism actually running, so the claim reads as a product and not a slogan.
- scene: The risk-score UI held as hero; the sunburst call-graph resolves inside it.
- voiceover: "So LiveReview scores every hunk by its blast radius — how far a change can reach, traced through a live call graph of your codebase."
- blueprint: device-surface-showcase (Adapt)
- focal: assets/footage/risk-score.mp4
- roles: risk-score.mp4 = cutout (card-mounted hero; carries the factor panels AND the sunburst) · risk-score-demo = supporting · new-risk-score-4 = supporting
- sfx: whoosh, ping
- asset_candidates: assets/footage/risk-score.mp4, capture/assets/risk-score_risk-score-demo-compressed.mp4, capture/assets/risk-score_new-risk-score-4.webp

Use the demo video around its sunburst beat (~21s in the 51s source) — the orange-to-red rings
are the money shot. Card-mounted on the light ground the way the landing page mounts its own
dark screenshots; do not run it full-bleed against the cream canvas.

Adapt: keep device-surface-showcase's held hero surface whose screens advance through a real flow; adapt it to two sources — the user's own cut carries the numeric score, the landing-page demo carries the sunburst this recording never shows. Card-mounted on the white ground, never full-bleed.

Scene 1 (0.0–2.2s): "LiveReview scores every hunk" — the headline sets left per-word (`dynamic-content-sequencing`); the surface card mounts right on a long-tail settle, showing the diff with findings. Asymmetric 40/60.
Scene 2 (2.2–5.0s): "by its blast radius" — the surface advances to the score panel (Ws66OKXUwwE 24–26s): "71 High risk", Blast Radius 51, Review Priority 100. `coordinate-target-zoom` frames the numerals without re-centring the card.
Scene 3 (5.0–7.6s): "how far a change can reach" — the surface advances to the sunburst (risk-score demo ~21s); the rings read outward from the centre. `depth-of-field-blur` drops the supporting text back so the chart holds the eye.
Scene 4 (7.6–9.067s): "traced through a live call graph" — the supporting line sets beneath the card; hold, card still, subtle jitter only.

## Frame 7 — The exact math, not a black box

- status: animated
- src: compositions/frames/07-exact-math.html
- type: feature_showcase
- duration: 8.32s
- transition_in: crossfade
- narrativeRole: Answer the objection a technical buyer is already forming — that an AI risk score is hand-waving.
- scene: Factor cards self-assemble around the score: callers, storage writes, nesting depth, test coverage.
- voiceover: "Not a black box. Every factor is on the table — callers, storage writes, nesting, test coverage — and the math behind them."
- blueprint: grid-card-assemble (Reproduce)
- focal: capture/assets/risk-score_new-risk-score-3.webp
- roles: new-risk-score-3 = cutout · new-risk-score-2 = supporting · risk-score-demo = supporting · Ws66OKXUwwE 24–26s = supporting
- sfx: click-soft, chime
- asset_candidates: capture/assets/risk-score_new-risk-score-3.webp, capture/assets/risk-score_new-risk-score-2.webp, capture/assets/risk-score_risk-score-demo-compressed.mp4

The factor cards assemble in a staggered cascade and hold. Land on Math Mode (the demo video's
~42s beat, or the new-risk-score-3 still) so the closing image is literal arithmetic. Two
scores, named plainly: Blast Radius (how far) and Review Priority (how much scrutiny).

Reproduce: grid-card-assemble's staggered self-assembly, then hand off to the artifact. One card per spoken factor — the cascade is cued by the list, not by a timer.

Scene 1 (0.0–1.8s): "Not a black box." — the line lands alone, centre-left, on a percussive but smooth beat-slam (`kinetic-beat-slam`, long-tail settle, no overshoot).
Scene 2 (1.8–5.4s): the four factor cards self-assemble in a staggered cascade (`center-outward-expansion`), **one per spoken factor** — callers, storage writes, nesting, test coverage — each landing exactly on its word. 2x2, ~55% of frame.
Scene 3 (5.4–7.2s): "and the math behind them" — the cards recede and the Math Mode panel scale-swaps into their place (`scale-swap-transition`), formulas legible at read size.
Scene 4 (7.2–8.32s): `asr-keyword-glow` touches the two score names — Blast Radius, then Review Priority — as the frame settles. Hold still.

## Frame 8 — Five pillars, one loop

- handoff_out: five-pillar ring nodes, node box 260x88 radius 14, at the frame's final locked camera (scale 1.00, opacity 1). Review (960, 290) · Understand (1430, 480) · Enforce (1250, 830) · Improve (670, 830) · Connect (490, 480). Geometry sits 55px above the sketch's original placement so the bottom nodes clear the caption keep-out band.
- status: animated
- src: compositions/frames/08-five-pillars-loop.html
- type: benefit_highlight
- duration: 11.563s
- transition_in: zoom-through
- narrativeRole: The structural spine — turn the feature set into a system the viewer can hold in their head before any of it is shown.
- scene: Five labelled nodes place around a ring; the camera travels the loop; the Improve→Review edge closes it.
- voiceover: "That inspection runs on five pillars. Review. Understand. Enforce. Improve. Connect. And Improve feeds straight back into Review — it's a loop, not a checklist."
- blueprint: spatial-pan-stations (Adapt)
- focal: the Improve → Review return edge
- roles: none — designed beat, no captured candidates
- sfx: ping, riser, chime
- asset_candidates: none — designed beat

**This is the frame the reviewer explicitly asked for.** Five nodes on a ring, each named as the
voiceover names it. The return edge from Improve back to Review draws LAST and is the beat the
frame lands on — the site's own line is "the loop runs continuously on every commit, not once at
setup." Each node keeps its ring position for the rest of the video so the next five frames read
as a tour of this diagram, not a new list.

Adapt: keep spatial-pan-stations' pre-placed stations traversed by one virtual camera, but bend the traversal into a closed ring so the path returns to where it started. The return edge IS the signature beat of this frame and of the film — it is the thing the reviewer asked for.

Scene 1 (0.0–2.2s): "runs on five pillars" — empty field; a faint ring guide self-draws (`svg-path-draw`) with no labels yet.
Scene 2 (2.2–7.4s): the five nodes place **one per spoken name** — Review, Understand, Enforce, Improve, Connect — each flipping in at its fixed ring position (`orbit-3d-entry`, entry only), the camera panning to centre each as it lands (`viewport-change`), roughly 1s per pillar. Forward edges draw between consecutive nodes as they arrive.
Scene 3 (7.4–9.6s): "And Improve feeds straight back into Review" — the **return edge draws from Improve to Review** (`svg-path-draw`), closing the circuit. Hold the completed loop for a beat before anything else moves.
Scene 4 (9.6–11.563s): "a loop, not a checklist" — one pull-back frames the whole ring (`multi-phase-camera`, single settle, no re-push). The ring locks and holds still. **These node positions are fixed here and inherited unchanged by Frames 9–13.**

## Frame 9 — Review

- handoff_in: the Review node arrives from the five-pillar ring at (960, 290), node box 260x88 radius 14, scale 1.00, opacity 1, motionless at the cut; it then travels to this frame's section-marker slot. Frames 9-13 each inherit their own node from Frame 8's locked ring — same box, same radius, same colour treatment.
- status: animated
- src: compositions/frames/09-review.html
- type: feature_showcase
- duration: 6.677s
- transition_in: push-slide
- narrativeRole: First pillar — re-anchor to the story by opening on the pillar's own question.
- scene: "What matters in this code change?" over the review pipeline, then the ranked diff findings.
- voiceover: "Review asks what actually matters in this change — then ranks every finding by how much it can hurt you."
- blueprint: cursor-ui-demo (Adapt)
- focal: assets/footage/review-diff.mp4
- roles: review-pipeline.mp4 = cutout (card-mounted) · review-diff.mp4 = cutout (card-mounted)
- sfx: click, whoosh-short
- asset_candidates: assets/footage/review-pipeline.mp4, assets/footage/review-diff.mp4

Open on the pillar question as type, then hand the frame to the footage. **Crop the source's own
burned-in bottom-left caption out — reframing 21:9 to 16:9 from the sides does not remove it.**

Adapt: keep cursor-ui-demo's cursor-led surface tour, but the cursor is the footage's own in-app pointer — no synthetic cursor is drawn over real product video.

Scene 1 (0.0–1.8s): the **Review** node lifts out of F08's ring into the upper-left and becomes the section marker (`card-morph-anchor`); the pillar question sets beneath it per-word (`dynamic-content-sequencing`).
Scene 2 (1.8–4.2s): "what actually matters" — the footage card mounts right (0–5s review pipeline sankey), cropped `2192:830:164:0`, entering on a long-tail settle. Asymmetric 40/60.
Scene 3 (4.2–6.677s): "ranks every finding by how much it can hurt you" — the surface advances to the diff findings (21–23s) and `coordinate-target-zoom` frames the severity marks, the one place `negative` is allowed in this frame. Hold.

## Frame 10 — Understand

- handoff_in: the Understand node arrives from the five-pillar ring at (1430, 480), node box 260x88 radius 14, scale 1.00, opacity 1, motionless at the cut; it then travels to this frame's section-marker slot. Frames 9-13 each inherit their own node from Frame 8's locked ring — same box, same radius, same colour treatment.
- status: animated
- src: compositions/frames/10-understand.html
- type: feature_showcase
- duration: 9.003s
- transition_in: push-slide
- narrativeRole: Second pillar — the one that speaks to intellectual control, the CTO's real fear from Frame 2.
- scene: "Can an engineer quickly understand what changed?" then the summary deck and issue navigator as evidence.
- voiceover: "Understand turns a diff into something a human can reason about — a summary deck, a filterable issue list, and a quiz before you commit."
- blueprint: transcript-scroll-artifact-reveal (Adapt)
- focal: capture/assets/quiz-coverage_quiz-coverage-demo-compressed.mp4
- roles: quiz-cta.mp4 = cutout · summary-deck.mp4 = supporting · git-lrc demos = supporting
- sfx: whoosh, click-soft, chime
- asset_candidates: assets/footage/summary-deck.mp4, assets/footage/quiz-cta.mp4, capture/assets/git-lrc_summary-deck-compressed.mp4, capture/assets/git-lrc_issue-navigator-compressed.mp4, capture/assets/quiz-coverage_quiz-coverage-demo-compressed.mp4

This pillar has the richest captured material — three purpose-shot demo clips. Travel down the
generated work as evidence, then pivot to the quiz as the payoff: it is the beat that answers
Frame 2's "rubber-stamping code you never understood".

Adapt: keep transcript-scroll-artifact-reveal's travel-the-work-then-reveal-the-artifact spine; the travel runs across three real demo surfaces instead of one long document, seamed at matched velocity.

Scene 1 (0.0–2.0s): the **Understand** node lifts from its ring position (`card-morph-anchor`); the pillar question sets per-word (`dynamic-content-sequencing`).
Scene 2 (2.0–4.4s): "a summary deck" — the summary-deck surface enters and travels vertically through its slides (`viewport-change`).
Scene 3 (4.4–6.6s): "a filterable issue list" — a cut-the-curve seam at matched velocity into the issue navigator (`cut-catalog.md`); the severity filters read as it settles.
Scene 4 (6.6–9.003s): "a quiz before you commit" — the quiz artifact reveals via `scale-swap-transition`, landing on the "Take the Quiz" state. This is the payoff that answers F02's rubber-stamping fear. Hold still.

## Frame 11 — Enforce

- handoff_in: the Enforce node arrives from the five-pillar ring at (1250, 830), node box 260x88 radius 14, scale 1.00, opacity 1, motionless at the cut; it then travels to this frame's section-marker slot. Frames 9-13 each inherit their own node from Frame 8's locked ring — same box, same radius, same colour treatment.
- status: animated
- src: compositions/frames/11-enforce.html
- type: feature_showcase
- duration: 6.72s
- transition_in: push-slide
- narrativeRole: Third pillar — standards stop being aspirational and become mechanical.
- scene: "Can our standards actually happen?" then repository rules and CI/CD gates checking off in sequence.
- voiceover: "Enforce turns the standards you already agreed on into checks that run on every commit, and every merge."
- blueprint: agent-progress-theater (Adapt)
- focal: assets/footage/cicd-ruleset.mp4
- roles: cicd-ruleset.mp4 = cutout (card-mounted) · scheduled-reviews.mp4 = supporting
- sfx: click-soft, chime
- asset_candidates: assets/footage/cicd-ruleset.mp4, assets/footage/scheduled-reviews.mp4

The rows arriving and checking off IS the demo — commit, before push, MR/PR, CI/CD, scheduled.
Five checkpoints, mirroring the five pillars without stating the rhyme.

Adapt: keep agent-progress-theater's receipt-cascade — rows arriving and checking off IS the demo — but the trigger is the pillar question rather than a menu click, and the real ruleset editor closes the beat.

Scene 1 (0.0–1.6s): the **Enforce** node lifts from its ring position (`card-morph-anchor`); the question sets per-word.
Scene 2 (1.6–4.4s): "checks that run on every commit" — five checkpoint rows arrive staggered and **check off in sequence** (`dynamic-content-sequencing` + `stat-bars-and-fills`): Commit · Before push · MR/PR · CI/CD gate · Scheduled sweep. One row per beat, left column, ~45% of frame.
Scene 3 (4.4–6.72s): "and every merge" — the footage card mounts right (33–38s, "Edit ruleset: High-confidence critical issues" with its live jq expression), cropped, and the rule text reads. Hold.

## Frame 12 — Improve

- handoff_in: the Improve node arrives from the five-pillar ring at (670, 830), node box 260x88 radius 14, scale 1.00, opacity 1, motionless at the cut; it then travels to this frame's section-marker slot. Frames 9-13 each inherit their own node from Frame 8's locked ring — same box, same radius, same colour treatment.
- status: animated
- src: compositions/frames/12-improve.html
- type: feature_showcase
- duration: 7.765s
- transition_in: push-slide
- narrativeRole: Fourth pillar — the leadership payoff, and the pillar that closes the loop back to Review.
- scene: "How are we doing?" then the impact report's charts, landing on 57.
- voiceover: "Improve turns your review history into answers. Fifty-seven charts, one click — and a chatbot you can just ask."
- blueprint: dataviz-countup (Adapt)
- focal: assets/charts-57-banner.png
- roles: charts-57-banner.png = cutout · stats-headline.mp4 = supporting · livi-adoption.mp4 = supporting · lrbot = supporting
- sfx: ping, chime
- asset_candidates: assets/footage/stats-headline.mp4, assets/charts-57-banner.png, assets/footage/charts-57.mp4, assets/footage/livi-adoption.mp4, capture/assets/lrbot_lrbot.png

The count-up to 57 is the hit. This is the most over-represented material in the source footage
(~55s of 105s) — take two segments, not six. End on the Livi question in plain English so the
next frame's return edge has something to carry.

Adapt: keep dataviz-countup's "numbers are the hero" spine and its push toward one metric, but the count-up lands on the product's own on-screen wording rather than an invented figure.

Scene 1 (0.0–1.6s): the **Improve** node lifts from its ring position (`card-morph-anchor`); the question sets per-word.
Scene 2 (1.6–3.4s): "review history into answers" — the headline stats card enters on a long-tail settle (69–71s: 2,271 findings · 366 critical · 1,395 warnings), `negative` permitted on the critical figure only.
Scene 3 (3.4–5.6s): "Fifty-seven charts, one click" — the numeral **57** counts up with value-scaled growth (`counting-dynamic-scale`) while the chart wall assembles behind it (`center-outward-expansion`), resolving on the product's own "57 charts across 7 sections" line (90–92s).
Scene 4 (5.6–7.765s): "a chatbot you can just ask" — Livi's mark and one plain-English question scale-swap into the lower-left (`scale-swap-transition`). Hold. This frame closes the loop back to Review — F13 inherits the handoff.

## Frame 13 — Connect

- handoff_in: the Connect node arrives from the five-pillar ring at (490, 480), node box 260x88 radius 14, scale 1.00, opacity 1, motionless at the cut; it then travels to this frame's section-marker slot. Frames 9-13 each inherit their own node from Frame 8's locked ring — same box, same radius, same colour treatment.
- status: animated
- src: compositions/frames/13-connect.html
- type: feature_showcase
- duration: 8.171s
- transition_in: push-slide
- narrativeRole: Fifth pillar — remove the adoption objection: this is not a rebuild.
- scene: The LiveReview mark stays pinned while git hosts, IDEs, and chat platforms cycle around it.
- voiceover: "And Connect means none of this is a rebuild. Your git host, your AI provider, your IDE, your chat — it already fits."
- blueprint: fixed-anchor-cycle (Reproduce)
- focal: capture/assets/logo.svg
- roles: logo = cutout (pinned anchor) · connect-git.mp4 = supporting · version_control_logos_* = supporting · extensions_* = supporting
- sfx: click-soft, ping
- asset_candidates: assets/footage/connect-git.mp4, assets/brand-openai.svg, assets/brand-anthropic.svg, assets/brand-gemini.svg, assets/brand-deepseek.svg, assets/brand-slack.svg, assets/brand-teams.svg, assets/brand-discord.svg, capture/assets/logo.svg, capture/assets/version_control_logos_github-logo-dark.png, capture/assets/version_control_logos_gitlab-logo.png, capture/assets/version_control_logos_bitbucket-logo.png, capture/assets/version_control_logos_azure-devops-logo.png, capture/assets/version_control_logos_gitea_logo.png, capture/assets/extensions_vscode-logo.png, capture/assets/extensions_cursor-logo.png, capture/assets/extensions_antigravity-logo.png

The anchor's stillness is the claim. LiveReview never moves; everything else rotates through.
Closing this frame on the pinned mark sets up the pull-back to the recap.

Reproduce: fixed-anchor-cycle — one element pinned and never moving while everything around it cycles. The anchor's stillness IS the claim; if the mark moves, the frame has failed.

Scene 1 (0.0–1.8s): the **Connect** node lifts from its ring position and morphs into the pinned LiveReview mark at centre (`card-morph-anchor`). From this instant the mark does not move again.
Scene 2 (1.8–6.4s): the categories cycle around the pinned mark **one per spoken item** — git hosts, then AI providers, then IDEs, then chat — each a hard-cut token swap in the same slots (`discrete-text-sequence`), logo rows swapping in place rather than re-flowing. **Every chip in AI PROVIDERS and CHAT now carries its real brand mark**, matching the GIT HOSTS and IDE EXTENSIONS rows that already had them — no group is left as bare type. Email has no brand mark: use a simple inline envelope glyph in `text-light`.
Scene 3 (6.4–8.171s): "it already fits" — the connect-git footage (54–56s, GitHub / GitLab.com / self-hosted GitLab / Bitbucket) reads briefly in a side card, then the satellites settle into a static ring. The anchor holds dead still.

## Frame 14 — What this adds up to

- status: animated
- src: compositions/frames/14-adds-up-to.html
- type: branding
- duration: 10.048s
- transition_in: zoom-through
- narrativeRole: The recap the reviewer asked for — restate WHY, WHAT and HOW in one compressed pass so the story closes where it opened.
- scene: Three type beats, each re-showing a ghost of its own earlier frame.
- voiceover: "AI writes more of your code every week. Inspection is what keeps it dependable. And blast radius is what makes that inspection land where it counts."
- blueprint: kinetic-type-beats (Reproduce)
- focal: the third clause
- roles: none — designed beat, reuses F01 / F03–F04 / F05 motifs as faint ghosts
- sfx: impact-bass-1, riser
- asset_candidates: none — designed beat

Three beats, one per clause, each carrying a faint echo of the frame it recaps: the diverging
curve (Frame 1), the inspection layer (Frames 3–4), the 300-vs-3 split (Frame 5). The five-pillar
ring can resolve behind the last beat as the loop closing. This is the last ten seconds — it must
restate the story, not introduce anything.

Reproduce: kinetic-type-beats — full-screen statement beats, each its own move, resolving on a locked finale. The ghosts are at low opacity and must never compete with the clause; they are recall, not decoration.

Scene 1 (0.0–3.2s): clause one — "AI writes more of your code every week" — lands full-width on a smooth beat-slam (`kinetic-beat-slam`, long-tail, no overshoot); F01's diverging-curve motif ghosts in faintly behind it.
Scene 2 (3.2–6.2s): a waterfall cut at word granularity carries clause two into place (`cut-catalog.md`) — "Inspection is what keeps it dependable" — with F03/F04's layer motif ghosting behind.
Scene 3 (6.2–8.6s): a second waterfall cut into clause three in `primary` — "blast radius is what makes that inspection land where it counts" — the F05 300-vs-3 split ghosting behind it.
Scene 4 (8.6–10.048s): the five-pillar ring resolves faintly behind the final clause and closes (`svg-path-draw`). Hold dead still into the CTA.

## Frame 15 — The close

- status: animated
- src: compositions/frames/15-start-free.html
- type: cta
- duration: 6.4s
- transition_in: blur-crossfade
- narrativeRole: One ask, framed as ownership rather than a free-tier number.
- scene: The LiveReview lockup settles; the ownership triad lands beneath it, then the self-hosted offer and the URL.
- voiceover: "Your code. Your infrastructure. Your reviewer. Start free, and we'll walk you through self-hosted setup."
- blueprint: logo-assemble-lockup (Reproduce)
- focal: assets/logo.svg
- roles: logo = cutout
- sfx: chime
- asset_candidates: assets/logo.svg

Lockup, triad, offer, URL. Calm landing. The old "30k reviewed LOC" line is REPLACED — it must not
appear anywhere in this frame.

Reproduce: logo-assemble-lockup — the mark comes to exist on a cleared stage and resolves into a centred lockup extended to the offer. This is the only frame in the film with a real exit.

Scene 1 (0.0–1.6s): F14's ring collapses inward and the LiveReview mark assembles at centre from its parts (`center-outward-expansion` run inward), settling on the film's default long-tail curve.
Scene 2 (1.6–3.6s): the ownership triad sets beneath the mark as **three beats, one per spoken clause** (`dynamic-content-sequencing`): "Your code." · "Your infrastructure." · "Your reviewer." The frame's hero line, display ramp.
Scene 3 (3.6–5.4s): on "Start free", the offer line sets beneath the triad — "Start free — we'll walk you through self-hosted setup." — in the body ramp, one measure, never wrapping onto the URL.
Scene 4 (5.4–6.4s): "hexmos.com/livereview" sets small beneath in `primary`. Everything holds dead still. No flourish, no second CTA.
