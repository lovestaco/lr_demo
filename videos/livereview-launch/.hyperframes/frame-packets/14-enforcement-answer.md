# Frame packet: 14-enforcement-answer

## Project inputs

- Project: /home/lovestaco/pers/lr_demo/videos/livereview-launch
- Design tokens: /home/lovestaco/pers/lr_demo/videos/livereview-launch/frame.md
- RULES_DIR: /home/lovestaco/.claude/skills/hyperframes-animation/rules

## Assigned storyboard block

## Frame 14 — Every checkpoint, every time

- scene: Five checkpoints light along a pipeline rail, then scheduled reviews and the CI/CD gate, then "→ Solved"
- duration: 13s
- transition_in: cut
- status: outline
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
