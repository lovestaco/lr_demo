# NOW (do first): dev.to moonwalk GIF for the blog

The big screen shows a **dev.to** logo instead of the risk tiles. Spidey moonwalks along the catwalk under it.
- **Source:** the existing `build/street.blend` (no rebuild).
- **Changes, applied in a throwaway render script:**
  - Every screen layer (`TSquare*`) shows `assets/slides/devto.png` (or a generated white "DEV" logo slide).
  - The camera holds the straight-on screen shot.
- **Frames:** the moonwalk only (~f954–1035, ~3 s) plus a short lead-in.
- **Render:** 540p, full quality.
- **Output:** `ffmpeg` palette GIF (480 px wide, 15 fps, loops) → `renders/devto_moonwalk.gif` + `.mp4`.
  Also copied into `/home/lovestaco/pers/blog/blender2/`.
- **No burn-in overlay:** it's a release asset, not a review copy.
- **Check:** contact frames before handing over (logo readable, he stays on the catwalk, exits frame right).

---

# Plan — Street v5: continuous travel, close-ups with feeling, blocks finale, 1080p (LATER)

(Saved for later; to be copied into the repo as `miles/plans/street_v5.md`.)

## Context
Review of street v4 (Shrijith + user):
- **Finale:** "the earlier analogy was better — the blocks". Go back to the blocks tower instead of the train.
- **Close shots are underused.** Show how Spidey feels (excited, interested, friendly, touring).
  Two-building setup: the board on the far building; Spidey and the camera on the near building, his face
  big in the foreground, the board readable behind him.
- **f65:** on the board top he isn't visible.
- **Too many direct cuts:** at most 1–2 in the film. The rest must be visible travel (jumps, landings,
  swings, runs, flips) using the 58 downloaded Mixamo clips:
  - f251: billboard hang starts standing straight.
  - f353: billboard → ticker with no jump.
  - ~f600: suddenly on the bus-shelter roof.
  - f691: subway, another direct cut.
- **f748:** the upside-down hang looks like a dead body. It should be the classic Spidey hang (legs folded
  on the web line, hands together, head down).
- **f769:** subway camera too far.
- **Final:** render at 1080p, full quality (no `--fast`).

## 1. Continuous route (cuts → travel), max 2 hard cuts
| From → to | Travel |
|---|---|
| Wall-board ledge → billboard | web line + swing, `MX Front Flip` into the inverted hang (no cut) |
| Billboard → ticker | `MX Falling` / `MX Falling To Landing` (or `MX Jumping Down`) on a `swing.hop` arc down, land |
| Ticker → bus stop | `MX Running` / `MX Sprint` + `Run To Stop` along the sidewalk |
| Bus stop → shelter roof | `MX Jumping Up` + `MX Running Jump` hop up onto the roof, then `MX Terrified` |
| Shelter roof → subway | `MX Jumping Down`, short run, web-zip up, drop in inverted on a visible line |
| Subway → screen catwalk | web zip (`swing.arc`), `MX Falling To Landing` |
| Catwalk → rooftop | moonwalk exits right, swing up (`Swing To Land (1)`) onto the roof |
| Rooftop → finale | `MX Running Forward Flip` + swing down to the intersection (allowed cut #2 if too long) |

Replace most `then(at=…)` hard cuts with `swing.follow`/`swing.hop` paths. Keep the HEIGHTS intervals and
the `contact()` pass on raised surfaces.

## 2. Close-ups with feeling (two-building setup)
3–4 shots of ~1.2–1.8 s each. The camera sits ~1 m from his head on the near ledge or roof and looks past him
at the board on the far building (shot camera `fstop` ~2.0, rack focus him → board). Use `fx.shot_cam` +
marker camera switches.

| Beat | Feeling | Clip |
|---|---|---|
| first board | excited | `MX Happy Hand Gesture`, `MX Being Cocky` |
| billboard | curious | `MX Thoughtful Head Shake` |
| ticker | amazed | head-whip gag + close |
| rooftop | confident / friendly | `MX Taunt`, `MX Acknowledging` |

## 3. f65 visibility
Camera higher and closer (~5 m) on the board-top ledge, aimed at his head. Then the over-the-shoulder close.

## 4. Proper inverted Spidey hang (billboard + subway)
- Base: the crouch tuck (Hard Landing ~28–46) inverted via the root roll (`INV`).
- New `Office.hold_line()` IK overlay: hands together in front of the chest, holding the line.
- Web line from the feet up (`WebShots`, foot bone).
- Slow sway (±4°) and a head lift toward the camera.

## 5. f769 subway camera
Closer, board + head both large; `clear_view` keeps pipes out.

## 6. Finale back to the blocks tower (in the intersection)
- He webs down INSPECTION → ENGINEERS' CONFIDENCE → CUSTOMER CONFIDENCE → COMPETITIVE PRODUCT + cash,
  each on its spoken word.
- He visibly yanks INSPECTION out (`Pull Heavy Object` start/heave/stop, both lines taut).
- Collapse, cash rain, flop, bill on the mask, helicopter pull-out.
- Reuse the block/label code from git history (`04_piece2` / street v3) and `assets/screens/tower_*.png`.
- Remove the train from the scene; keep the asset.
- Camera: wide while building (tower + cash in frame), face close-up on the yank, wide on the collapse.

## 7. Extras
- SFX on every new jump, land and flip.
- Match-on-action for the remaining cuts.

## 8. Final render
- Free `build/frames/*`: 1080p frames need ~4–5 GB, and 8.9 GB is free.
- `05_render.py -- full 100`, then `06_assemble.py street --height 1080 --music …` (clean + `_tc`).
- ~2–3 h on the GTX 1650. Commit after.

## Verification
- `check_support.py` clean except intended airborne moments.
- Hard-cut count ≤ 2.
- 480 px contact sheet: signs readable, Spidey visible in every shot, close-ups ≥ 25% of frame height.
- Hang stills vs the reference image.
- Finale: tower + cash in frame at "money"; the yank is driven by his pull.
- No VO overlaps, −16 LUFS.
- 270p `--fast` smoke test before the 1080p render.

---
## Progress log (autonomous run, started 2026-10-06 ~02:00; user back 11:00, wants 1080p full-quality render)
- Approach: standing beats = `at=` shots (HEIGHTS + contact); every move between locations = travel clips
  (fly = Swing To Land 1..34 in place) fully keyed by `swing.follow` from hp(prev shot end) to hp(next shot start);
  hangs = Hard Landing 28–46 tuck, rolled π, pinned by follow; roll ramps keyed inside the travel.
- v4 blend backed up to scratchpad street_v4.blend (build/ is regenerated anyway).
- 02:50 v5 built (73.2 s): all location moves are travel (0 location cuts; 5 close-ups/OTS), blocks tower finale,
  hangs = tuck, subway camera closer, f65 board shot raised; cine_grade (haze/bloom/dispersion/vignette), DOF per shot,
  impact shakes; check_support clean (sprint flight phases only). 270p fast smoke test running; then 1080p final.
- 03:15 270p smoke test OK (13/13 VO, 37/37 SFX, −16 LUFS). Added tower low-angle cuts, board drift, hang head-lift,
  `--music-once` (70 s bed, 73 s film). FINAL 1080p full-quality render started (~2 h):
  `05_render.py -- full 100` → `06_assemble.py street --height 1080 --music … --music-once` → renders/street_1080p_mix(_tc).mp4.
  Remaining after render: frame check, commit (local, no push).
- 04:20 DONE: renders/street_1080p_mix.mp4 (+_tc), 73.2 s, -16 LUFS; committed 2513ae6 (local, not pushed).
