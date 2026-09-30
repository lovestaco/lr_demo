# Frame packet: 10-blast-radius

## Project inputs

- Project: /home/lovestaco/pers/lr_demo/videos/livereview-launch
- Design tokens: /home/lovestaco/pers/lr_demo/videos/livereview-launch/frame.md
- RULES_DIR: /home/lovestaco/.claude/skills/hyperframes-animation/rules

## Assigned storyboard block

## Frame 10 — Ranked by blast radius

- scene: The answer line, then the real diff scoring every hunk, then "→ Solved"
- duration: 13s
- transition_in: cut
- status: outline
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

## Selected blueprint: video-text-pivot

# video-text-pivot — Video → Text Pivot

**intent**: A product video holds center and claims attention, then slides aside to hand its weight to a hero stat in the space it vacates, then both clear and kinetic text types into the center — accent words carrying the meaning the video used to carry — sealed by a gradient pill. The arc is "show → yield → pivot → stamp," and each handoff pairs an exit with a same-anchor entrance so two beats read, not four.

**roles served**

- Product_Intro (from `metric-video-text-pivot`): when the open is "see the feature" then "see the impact" and the `[product video]` must stay visible through the stat reveal — it slides, it doesn't cut.
- Key_Feature: a feature clip that yields to a frame-filling metric and a typographic impact line.

**duration**: 6–8s

**shot structure** (a `[bg]` canvas; one `[product video]` as a real muted `.mp4` clip, a hero stat, then kinetic text — each pair shares a screen anchor so the handoff reads as a weight-transfer)

- **Scene 1 (0.0–~1.6s) — the video shows.** The `[product video]` lands centered on a smooth scale-up and breathes (a small y-bob), claiming full attention. Camera static.
- **Scene 2 (~1.6–3.2s) — yield + stat (signature move).** The video SLIDES aside (x + scale down) **into the very space** the `[hero stat]` now fills as the stat pops in with 3D-depth type — one weight-transfer reading as a single event, not two. The stat breathes within this window.
- **Scene 3 (~3.2–5.0s) — pivot to text.** Both video and stat clear out and kinetic `[impact text]` TYPES into the vacated center, character by character; its `[accent words]` carry the meaning the video used to carry.
- **Scene 4 (~5.0–end) — stamp.** A gradient `[pill]` snaps shut around the closing line (`scaleX` 0→1), its glow halo resolving a beat behind so the silhouette reads before the bloom — sealing the statement as one graphic. Holds.

**motion vocabulary**: video scale-in + small breath; weight-transfer slide (video x + scale-down handing off to the stat at the same anchor); 3D-depth stat type; character-stream typing; gradient pill scaleX-snap; glow-halo bloom trailing the silhouette.

**rule mapping**

- video entrance (smooth) and the weight-transfer slide → `gsap-effects` (scale/opacity then x + scale on a long-tail `power3`); the video itself is a muted `<video class="clip">` direct child of the root
- hero stat's frame-filling 3D type → `3d-text-depth-layers` (static-depth variation — layers built at setup, no cascade fighting the entry)
- the same-anchor video-exit ↔ stat-entry handoff (if treated as a morph) → `scale-swap-transition` (shared center)
- character-by-character impact typing through segmented spans → `dynamic-content-sequencing` (clean character stream) or `discrete-text-sequence`
- pill `scaleX` snap + trailing glow halo → `gsap-effects` (scaleX) + `ambient-glow-bloom` (the halo, resolving a beat behind)
- video / stat breath within their windows → `sine-wave-loop` (low-amplitude register — subtle jitter, gated to each element's window, never a forever loop)

**camera modifier**: camera-static — all motion is element-space (the video translates), so the "pivot" is the elements moving, not a camera.
