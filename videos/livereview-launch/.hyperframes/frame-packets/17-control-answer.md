# Frame packet: 17-control-answer

## Project inputs

- Project: /home/lovestaco/pers/lr_demo/videos/livereview-launch
- Design tokens: /home/lovestaco/pers/lr_demo/videos/livereview-launch/frame.md
- RULES_DIR: /home/lovestaco/.claude/skills/hyperframes-animation/rules

## Assigned storyboard block

## Frame 17 — Adaptive, learning, everywhere you work

- scene: Three capability lines, Livi answering a real question, then "→ Solved"
- duration: 12.5s
- transition_in: cut
- status: outline
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
