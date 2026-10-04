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
- `shot.finish` lays VO + SFX into the .blend's sequencer → Space in Blender plays with sound (check fixes without rendering).
- Camera: hold still while a screen is up; move only in screen-free stretches. Frame at the depth
  between screen and presenter (`frame_on`), otherwise he is cropped at the edge.

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
