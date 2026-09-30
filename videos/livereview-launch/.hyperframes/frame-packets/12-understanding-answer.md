# Frame packet: 12-understanding-answer

## Project inputs

- Project: /home/lovestaco/pers/lr_demo/videos/livereview-launch
- Design tokens: /home/lovestaco/pers/lr_demo/videos/livereview-launch/frame.md
- RULES_DIR: /home/lovestaco/.claude/skills/hyperframes-animation/rules

## Assigned storyboard block

## Frame 12 — Summaries, navigation, quizzes

- scene: The answer line, then the summary deck and the quiz play back to back, then "→ Solved"
- duration: 12.5s
- transition_in: cut
- status: outline
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
