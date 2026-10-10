# CLAUDE.md — miles/ (character-driven LiveReview slide videos)

Masked Miles Morales (Mixamo rig) performs scripted acts in Blender 5.2 (EEVEE) that
present LiveReview slides on a physical sign. Read `README.md` for the full pipeline;
this file holds what you need to work here effectively.

## Pipeline (each step re-runnable, run from `miles/`)

```bash
python3 scripts/00_cmu_fetch.py <words> [--get N] | --ids 02_01 ...      # free CMU mocap -> ../blender_assets_downloaded/cmu/
blender -b miles.blend --python scripts/01_export_for_mixamo.py          # (once) T-pose FBX for mixamo.com
blender -b --factory-startup --python scripts/02_build_character.py     # -> build/character.blend (masked Miles + all Mixamo clips)
blender -b build/character.blend --python scripts/02b_retarget_cmu.py   # CMU BVH -> actions "CMU <id> <desc>" (saved into character.blend)
python3 scripts/03_make_slides.py                                        # SLIDES dict -> assets/slides/slide_NN.png
blender -b build/character.blend --python scripts/04_act1.py            # -> build/act1.blend (+ build/act1_cues.json)
blender -b build/character.blend --python scripts/04_act2.py            # -> build/act2.blend (continues act1's end state)
blender -b build/<act>.blend --python scripts/05_render.py -- sheet     # contact sheet -> build/<act>_sheet.png
blender -b build/<act>.blend --python scripts/05_render.py -- full      # 360p preview -> renders/<act>_360p.mp4
python3 scripts/06_assemble.py piece2 [--music bed.mp3]                 # VO (vo N) + SFX (sfx name) + ducked music -> renders/<shot>_360p_mix.mp4
python3 scripts/07b_split_take.py TAKE.mp3 --script assets/audio/vo_piece2.md --out assets/audio/vo_piece2   # one website take -> line clips + word times
python3 scripts/08_sfx.py                                                # ElevenLabs sound effects for shot.sfx() cues -> assets/audio/sfx/
```
Piece 2 (`scripts/04_piece2.py`, ~93 s) is timed from `assets/audio/vo_piece2/lines.json` (line lengths +
per-word times: risk tiles pop and tower blocks land on their spoken words). Audio cues are timeline
markers: `vo N` and `sfx <name>` (added with `shot.sfx(name, frame)`).
Re-running `02_build_character.py` wipes the CMU actions; re-run `02b` after it.
Join acts without audio: `ffmpeg -i act1_360p.mp4 -i act2_360p.mp4 -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[v]" -map "[v]" ...`

## Code map (`pipeline/`)
- `mixamo.Performer` — `place()`, `then(action, frm, to, length, blend, face, speed, repeat)`, `build()`,
  `root_z()`, `extreme(action, bone, direction)` (auto hit frame), `clip_frame(clip, local)`, `bone_world()`.
  Chains clips as NLA strips with crossfades and stitches root motion via the `MilesRig_Root` empty.
  `face`: 0 = facing camera (-Y), 90 = screen right, negative = screen left.
- `retarget.bvh_to_action()` — CMU BVH → Mixamo action (bone-direction matching, hip-height scaling,
  start facing camera, skips the T-pose first frame). Fingers stay at rest.
- `fx` — `studio(theme)` (light|dark), `physical_shading()` (replaces the model's toon shader),
  `Board` (multi-slide sign: `show`, `flip(frame, idx, turns)`, `hooks`, `nearest_hook`, `base_z`),
  `WebShots` (web strands: `shot(name, bone, target_fn, start, hit, release)` + `bake`), `CameraRig`, `look()`.
- `shot` — `stage()`, `frame_span()` (fit an x-range), `finish(name, markers, end_state)`,
  `load_end_state(act)` for seamless act-to-act continuity.
- `anim` — keyframes with easing on Blender 5 layered actions. `preview.clip_sheet()` — compare clips fast.

## Slide rules (from review — follow strictly)
- **Attention management: one idea per frame.** No logo/wordmark on content slides (logo gets its own frame later).
- Black text on white, **one font size** per slide (reads left→right, top→bottom); emphasis only with `**bold**`.
- The slide is the hero: sign is 4.8 m wide and fills ~70% of frame during reads.
- Reading time: ~2.5 s for short lines, ~4.5–5 s for long ones. Act 1 ≈ 10 s; Act 2+ can be longer.
- Deck text source: `../ppt/LiveReview-Presentation-slides.md` (slide numbers = `slide_NN.png`).

## Working agreements with the user
- **Subtitles are burned into every street video** by `06_assemble.py` (`pipeline/subs.py`; word-timed, spoken word bold). No key-phrase captions, no .srt.
- **Every rendered video gets a review copy with burn-in** (`<name>_tc.mp4`: Blender frame number + time / total,
  bottom-right) — `06_assemble.py` does it by default; reviewers cite frames like "f 1201". Clean file stays alongside.
- **Discuss the plan before building** anything new (new act, new scene idea); then build.
- Iterate with **360p** renders (`full` default, ~1–2 min); 720p/1080p only for finals.
- Always check a contact sheet (`sheet`, or ffmpeg tile from the mp4) before handing over a render.
- Keep code reusable: shared logic in `pipeline/`, one script per act, numbered steps.
- Same stage across acts unless asked; continuity via `end_state` (lighting must match across the cut).

## Motion polish (use in every new scene)
- `perf.ground_lock(start, end, skip=[airborne clips])` after `build()` — retargeted CMU clips hover 5–10 cm;
  planted hands count as floor, so cartwheels can stay locked.
- `then(..., in_place=0.8)` for emotes with big root travel (e.g. `CMU 120_16 Mickey Surprised` drifts 1.8 m).
- Presenting: `perf.lively(clip, length, target=1.5)` picks a *calm* gesture window (no target = most
  animated, which looks frantic — CMU 80_48 arguing scores 7–10). Piece 2's `talk()` rotates Mixamo
  `Talking (1)/(2)` + CMU 18_08 in place, `face≈±5`.
- `office.present_to(frame, point, his_x)` — open-hand gesture on the screen's side; aim 0.3 m in front of the glass.
- `office.face_camera(cam.cam, [(start, end), ...])` — head looks at the lens on talk beats.
- Retarget damps mocap clavicles (`retarget.CLAVICLE_KEEP = 0.25`); without it CMU shoulders sit 5–8 cm high.
  After changing retarget, re-run 02b with every id (`-- $(ls ../blender_assets_downloaded/cmu/*.bvh ...)`): it skips existing clips otherwise.
- `fx.Spiders(paths.SPIDER_GLB, size)` + `.add([(frame, point), ...])` — walking spider swarm (Sketchfab, CC-BY,
  credit in `../blender_assets_downloaded/sketchfab_spider/CREDITS.txt`).
- Despair: `CMU 79_72 crying` keeps both hands on the head (frames 18–218).
- `perf.then(..., at=(x, y))` — hard cut to a spot (off-camera move during a screen close-up); combine with root
  keys after `square_up()`: `perf.root_z(...)` for height, `anim.keys(perf.root, "rotation_euler", ..., index=1)` for
  roll (π = head-down hang facing camera, ±30° = lean in from a frame edge). Piece 2's `head_down()` helper:
  `Hard Landing` frames 28–46 upside down = comic-book tuck on a line from the feet (`WebShots` bone `LeftFoot`).
- Peeks in piece 2: lean-in from the frame edge (`rqp`), over the top of the screen (`topp`, hands on the bezel
  via `office.present(..., amount=1)`; keep grips ±0.45 m from centre or the IK can't fold).
- `Swing To Land (1)` = web swing → crouch with one hand down; `Fallen Idle` = flat on the floor.
- Camera `locked()` spans must not overlap: an overlapping key turns a cut into a slow drift.
- 07b cuts each line in the middle of the real pause (whisper word edges clip syllables); clips carry
  ~0.35 s of breath, so scenes subtract `PAD` when timing holds.
- `shot.finish` lays VO + SFX into the .blend's sequencer → Space in Blender plays with sound (check fixes without rendering).
- Camera: hold still while a screen is up; move only in screen-free stretches. Frame at the depth
  between screen and presenter (`frame_on`), otherwise he is cropped at the edge.

## Street part 1 (final: `scripts/04_street_part_1_final.py` → `build/street_part_1_final.blend`, renders `renders/street_part_1_final_720p*`)
- Set: Sketchfab "City Scene" (golukumar, Free Standard) via `pipeline/city.py` (`load()`, sunset `golden_hour()`,
  `wall()/roof()/ground()` ray casts, `sign()` image planes with billboard/lightbox/LED frames). The city is lifted
  0.34 m so the sidewalk is z=0. Avenue along Y at x≈0 has street trees at x≈±6 — put signs on the tree-free
  cross street (facades y≈−9.3 south / +8.9 north).
- Slides live in the world: `scripts/03c_street_signs.py` → `assets/street/` (graffiti mural, billboard, LED ticker,
  lightbox sequences, risk screen, rooftop screens).
- **v5 structure: no location cuts** (review: max 1–2 direct cuts in the film). Standing beats are `at=` shots
  (height from `HEIGHTS` + `perf.contact()`); every move between locations is a TRAVEL — `fly()` (= `Swing To Land (1)`
  frames 1–34 in place) / sprint / hop — keyed every frame by `travel(path, f0, f1)` (wraps `swing.follow`) from
  `hp(prev_shot_end)` to `hp(next_shot_start)`; the landing is `land()` (= the same clip's frames 34–57, `at=` the
  path's end) so pose and position are continuous. `travel()` re-keys the root at f1+1 with what was there before
  (a lin key at the path end otherwise drags every frame up to the next key towards it: he floated at 14 m).
- Hangs: `tuck()` (Hard Landing 28–46 crouch) rolled π, pinned with `pin(point, f0, f1, sway)`; the roll turns over
  inside the incoming/outgoing travel (a flip into / out of the hang). Line from the feet (`FOOT`).
  Facing: rolling about Y keeps the facing direction, so a hang facing a +y camera needs face=180.
- Paths are checked for collisions (`path_hits`, prints `PATH <name> hits`) and the camera for occlusion
  (`OCCLUDED [...]`) on every build. Chase cameras: `ride()` (hips + offset on a collision arm that stops short
  of facades, smoothed); short moves across a street: `pan()` (fixed camera following him).
- Close-ups with feeling: CU excited (board ledge), OTS two-building shot (billboard across the street from his
  ledge), CU amazed (profile, ticker above), CU confident (roof), CU yank. Head look constraints must not
  point behind him (ticker: he faces it, `face=180`), or the neck turns 180°.
- **v8 (review: animation rules):** every read is a `presenter()` shot (whole slide straight-on, him upright at its
  LEFT edge, facing the lens via `square_up`); travel = `zip_()` (`Hanging Idle`, hands up on the line) + `touch()`
  (`Hard Landing` 14-64 placed with `at=` + `cut_blend`), `lean()` holds ONE tilt (sample the root rotation before
  keying, or each frame compounds the tilt into a spin: that was the old "spinning" swings). No hangs. `Performer`
  turns the short way (180 -> -160 was a 340° spin on the mural landing). Finale = v3 `city.Building` (12 m, 4 floors)
  in the intersection, shown from the S8 cut; `pancake()` = gravity fall, squash, dust puffs, debris.
  `scripts/check_rules.py` audits rules 1-6 from `build/<name>_audit.json`; `check_support.py` reports false
  "None" gaps when a toe sits exactly on the road (its ray steps through his own mesh).
- Finale: blocks tower in the intersection (piece-2 block code, ×1.45 street scale) on the words of vo 13/9/10/11,
  yank on "inspection" (vo 12): `Pull Heavy Object Start` (lines taut) → `Stop`; he watches the collapse, then flops.
- Look: `shot.finish(view="AgX", grade="AgX - Punchy")` + `fx.cine_grade()` (mist-pass haze = aerial
  perspective, bloom, lens dispersion, vignette — `05_render.py` rescales the vignette blur via
  `fx.fit_vignette()`); per-shot `aperture_fstop` keys (f/1.8–2.4 close-ups, f/5.6 chases); `cam.shake` on every
  landing / block / the collapse. Camera clip_end 800 for aerials.
- **v6 additions:**
  - `pipeline/life.py` — city life checked against `life.Guard` (per-frame camera + Spidey cache):
    - parked + moving cars (right-hand lanes ±2 m, signal cycle so cross traffic never meets, a queue at the stop lines for the finale);
    - pedestrians (`WalkKit`, moving at each loop's measured planted-foot speed, keep right);
    - pigeons (`PigeonKit`: idle → startled take-off on his landings).
    - Nothing pops in/out on screen, passes through him or the lens, or blocks the lens.
    - Assets via `scripts/09_sketchfab_fetch.py` (search/get, CC licences, credits saved).
  - `pipeline/face.py` — mask lens shape keys (Wide/Squint/Angry/Sad) + blinks, keyed per story beat.
  - Swings: varied clips (`Swing To Land (3)`, mid-air `MX Front Flip` landings, `MX Falling` leap off the roof).
    `find_anchor()` puts every web on a real facade ahead of him, in the swing plane. `lean()` hangs the body
    along the line (pendulum).
  - Warmer, lower sun (`golden_hour(6°)`, colour 1.0/0.66/0.40); closer ticker / screen / tower wides.
  - 06_assemble varies each SFX cue's pitch/level. 05_render keeps frames in `build/frames/<name>_<h>p/`.
- VO: `assets/audio/vo_street/` (Mark v4 take, 13 lines); music `assets/audio/music/bed_street.mp3`
  ("Superhero Cinematic Opener" by ArctSound, Pixabay, not Content ID registered, 70.2 s).
- Assemble: `python3 scripts/06_assemble.py street_part_1_final --height 720 --music assets/audio/music/bed_street.mp3`
  (film 69 s < the 70 s bed; `--music-once` if a cut ever runs longer than the bed).

## Street part 2 (a separate video: `scripts/04_street_part2.py` → `build/street_part2.blend`, ~2:10)
- v2 story (colleague script): S10 two identical shops facing each other across the west arm (head-on from the middle
  of the road; customers cross the zebra to the competitor) → S10.1 the answer from the sidewalk (your sign flickers,
  the broken item, CLOSED) → S11-S13 three sites on the open lot BEHIND the plaza building (cameras at y 86 looking
  south; same camera per site, zoom fits the site; boards blank outside their own scene) → S14/S15 masked close-ups
  (finger count, point, temple tap, hand on chest; lower-third captions) → S16/S17 2D product boards → S18 the wreck
  before sunrise (sky + sun keyed), INSPECTION locks with a glow, floors rise, sunrise, new floors → S19 rooftop,
  peace sign, pull-out, billboard demo. Unmasked lip-sync was declined (no face rig on MilesUnmasked).
- Pipeline: `03d_street_part2_signs.py v2` → `07c_estimate_vo.py` (until the Mark take) → build →
  `05c_render_range.py OUT 1-1600 ...` (skips the 2D frames) + `05b_street_part2_boards.py OUT` (S16/S17 frames from
  `videos/livereview-launch/assets` demo clips) → `06c_street_part2_post.py OUT` (captions from
  `build/street_part2_overlays.json`, piped straight to ffmpeg) → `06_assemble.py street_part2 --height 720 --music ...`.
- Shared helpers: `pipeline/streetkit.py` (`Kit`); `life.Walker.route([(point, wait)], f0, pace=[...])` for queues,
  workers, onlookers (pace 2.4 = running off).
- Hands: a fingers-only REPLACE NLA track ("ZZ Finger poses"); finger curl = +X rotation per segment. An NLA strip made
  through the API evaluates at influence 0 unless `use_animated_influence` with keyed influence. Office IK: mute the
  unused IK constraints on a chain (the legacy solver weighs them even at influence 0 — the hand couldn't rise); IK
  can't lift a hand above the shoulder anyway → the peace sign uses the hand-to-ear frame of `CMU 79_36 answering the
  phone` + the finger layer.
- `parent_keep(child, parent, frame)` must update the view layer first (a just-placed object reads identity).
- Audit: `blender -b build/street_part2.blend --python scripts/check_rules.py -- street_part2`.

## Street part 2a (S10-S15 on its own: `scripts/04_street_part2_a.py` → `build/street_part2_a.blend`, ~73 s)
Part 2 is split for faster iteration. **Part 2b (S16-S19) is now its own build: `scripts/04_street_part2_b.py` →
`build/street_part2_b.blend`** (~72 s; timeline starts at frame 1 = the S16 cut; he is off frame through S16/S17,
whose 2D boards come from `05b_street_part2_boards.py OUT street_part2_b`). The old full `04_street_part2.py`
(→ `build/street_part2.blend`) is superseded and no longer used.
- S10/S10.1: ONE building on the west arm's south facade, two shops side by side (yours screen-left, theirs right, doors
  in the middle), one board over both (states `board_a..d`, `03d ... v2a`); one head-on camera from the north sidewalk
  (S10.1 = a slow push, no cut). Customers walk out of your door along the sidewalk into their queue (it runs off to
  the right, everyone faces the door). The merged city lamp mesh had a pole in front of your shop: the build deletes
  that island only (`drop_islands`, by hit face + same xy).
- Their queue moves (`queue_route`): every 60 frames the one at their door goes inside; yours join the end.
- S11 site A: brick one-storey building, two hammering builders + the boss giving instructions (`pipeline/crew.py`;
  the boss is a Mixamo-rigged Sketchfab model driven by Spidey's own CMU clip via a rest-relative world-rotation
  bake — his rig rests in a T-pose, Spidey's in an A-pose). S12: on "Option two" he sprints to site B's board (`MX
  Sprint` + a straight root travel) and the camera trucks right (A's board leaves the frame); no onlookers. S13 site
  C its own shot: he presents its board; robot arms + a builder bot + the crane build, the boss (from A) checks;
  framing recomputed every 8 frames as floors land; then the pull-back to all three. Plaza building behind the lot
  hidden. Root z keyed flat at every cut (a travel's first key otherwise ramps him up into the air).
- No close-ups and no three-site wide any more. End of S13: he zips from C's board to C's roof and the camera rises
  with him (`ROOF_CAM`: roof + the banners below). S14 on the roof (root z = roof minus each clip's lowest foot,
  `perf.contact`): three banners (`banner_*`, 03d v2a) unroll on "headcount / results / better"; count raised, then he
  points down at the tower. S15 (cut) = medium shot of C's top floor: he STANDS on a scaffold platform beside the door
  to nowhere (no hanging): the Shrug clip (both palms) on "why keep humans in the loop", then talks; right arm: chin
  tap, the line that pulls a balcony in under the door ("cuz"), the stamp (green check beside the door). The boss
  (hard hat) walks out of the door to the edge, steps onto the balcony, waves; three more floors land above.
- Right-arm gestures (S14 count raised / pointing down, S15 chin / web / stamp) are NOT Office IK (the legacy
  IK flipped that arm): `solve()` two-bone per frame + the hand's axes on a REPLACE NLA layer "ZZZ Arm gestures"
  (spans must not overlap — asserted). He faces +y there, so HIS RIGHT IS +X.
- Shop queue: new customers walk in from the street (off frame right); nobody comes out of your shop.
- Crew: `pipeline/crew.py` — NLA loop strips must set action_frame_start/end AFTER the slot (else a 1-frame range:
  frozen workers); the boss retarget turns the src motion to the dst heading and strips the clip's own body turn.
- Walkers: `walk.phone_every = 6` (one in six on a phone); the competitor's shop has an interior image, striped
  awning, brass trim, neon, bulbs, a planter; tower B is glossy (white panels, blue glass, glowing bands).
- VO: real Mark takes per line (website, Generation 1) in `assets/audio/vo_street_part2/takes/take_NN.mp3` →
  `07b_split_take.py --lines ...` (whisper word times, merged into lines.json; Kit.word aliases "cuz"→"cause" etc.).
- Build name `street_part2_a` (underscore: 06_assemble's prefix lookup then finds `vo_street_part2`).
- Pipeline: build → `05c_render_range.py build/frames/street_part2_a_720p 1-2158` → `06c_street_part2_post.py
  build/frames/street_part2_a_720p street_part2_a` → `06_assemble.py street_part2_a --height 720 --music ...`.
  Quick review: `05c_render_range.py OUT 1-2158 --h 360 --fast` (no ray-traced reflections, 8 samples) then
  `06c_street_part2_post.py OUT street_part2_a --height 360` → `06_assemble.py street_part2_a --height 360
  --music assets/audio/music/bed_street.mp3 --music-once` (writes `<name>_360p_mix.mp4` + frame-numbered `_tc.mp4`).
  Run at most 2 renders in parallel: RAM (13 GB) and the 4 GB GPU both thrash at 3.
- Pedestrians (all scenes, `pipeline/life.py`): the walk models face -Y (turn them with `_walk_yaw`, never `_yaw_to`
  — they moonwalked before); every spawn index gets its own outfit (shirt/pants/skin/hair colour slots).

## Shot grammar (what each camera choice is for)
- WIDE to open a scene (where are we), then MEDIUM (waist up) on the character; CLOSE-UP for emotion
  (shock face) or an action that matters (finger on the power button).
- OVER-THE-SHOULDER when he looks at a screen; POV ("the camera becomes the screen") when he taps it on.
- Static frame + subject moving through it (dash out of frame); TRACKING for journeys.
- PUSH IN = pressure before a turn (the yank), PULL OUT = release after it; HIGH angle = small/tired/defeated,
  LOW angle = confident; SNORRICAM (camera on his chest) = chaos, ≤1.5 s.
- Extra cameras: `fx.shot_cam(...)` + `shot.finish(cameras=[(frame, cam), ...])` (marker-bound switches);
  main `CameraRig` keeps everything else. Build a variant without touching the main one:
  `blender -b build/character.blend --python scripts/04_piece2.py -- piece2_cine` (VO folder found by prefix).

## Before every render: physical checks
- `blender -b build/<shot>.blend --python scripts/check_support.py` — feet must be on something (no standing or
  moonwalking on thin air). Thin set pieces (a 25 cm board top) need a real ledge/catwalk under him.
- Height per shot comes from `HEIGHTS` in 04_street_part_1_final.py using `low_rel(clip)` (each clip's own foot height);
  path keys (`swing.follow`) must stop one frame before the next shot's first frame.
- Movement must match the story beat on screen (e.g. moonwalk WITH the customers, same direction).
- Hip height across blends (reviewer tip): crossfading poses (crouch → stand, idle → moonwalk) lift or drop the feet
  even when the root height is eased. On raised surfaces run `perf.contact(start, end, floor=surface_z)` (per-frame
  toe contact, ±35 cm cap so hops stay hops); on the street `ground_lock(..., step=1)`. Never key the root every
  2nd frame with linear interpolation: the in-between frame at a hard cut lands halfway between two shots.
- A hard cut starts on a whole frame (`then(at=...)` rounds up); a shot's last frame is `ceil(end) - 1`.
- Removing many keyframes: go back to front (`fast=True` while iterating drops the wrong keys).

## Gotchas
- Blender 5.2 API: layered actions (`action.layers[].strips[].channelbag(slot)`), assign `action_slot`
  when setting actions; compositor = `scene.compositing_node_group`; Glare params are socket inputs.
  Material `use_nodes` deprecated — check `node_tree is None`.
- The Sketchfab Miles uses a Shader-to-RGB toon network → suit renders flat black; always call
  `fx.physical_shading()`. Source pack has no normal/spec maps (Sketchfab glTF neither).
- Avoid `ELASTIC` easing on keys with equal values (oscillates). `BACK` is safe.
- Masked suit is aligned in armature-local REST space, so posing/moving rigs in `miles.blend` is harmless.
- GPU is a GTX 1650 (4 GB): EEVEE only; tools needing 8 GB VRAM (GVHMR, UniRig) won't run locally.
- Tokens live in `../blender_owl/.env` (`SKETCHFAB_API_TOKEN`, `ELEVEN_LABS_API_KEY`), gitignored — never commit them.
- ElevenLabs free tier: library voices are website-only (API 402), Sound Effects API works, Music can be
  generated on the website but **downloading music needs a paid plan**. Free-tier audio is non-commercial.
- `build/` and `build/frames/` are gitignored; outputs worth keeping go to `renders/`.

## Motion sources
- Mixamo clips: `../blender_assets_downloaded/*.fbx` (base "Hanging Idle" downloaded *with skin*).
  The site has no bulk download; prefer CMU for new moves.
- CMU mocap (~2,500 clips, free for any use): index at `../blender_assets_downloaded/cmu/cmu-mocap-index-text.txt`,
  mirror `github.com/una-dinosauria/cmu-mocap`. Higher-numbered subjects are cleaner.
