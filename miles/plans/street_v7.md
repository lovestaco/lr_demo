# Plan — Street v7: one focus point per slide (Shrijith review of v6)

## Context
Shrijith's review of v6 (360p, frame numbers = v6 timeline), confirmed by lovestaco:
- **Two focal points.** Spidey and the slide compete for attention in most slides ("guide the eye", one message per
  slide). Viewers don't know whether to watch the gimmick or read.
- **Distance.** Spidey is too far from the slide (f583 bus stop). His diagram: face in the foreground on the **left**,
  covering ~10% of the board, slide filling the rest. One focus point that reads left → right.
- **f0160 board shot.** Spidey moves on top of the board while it's read; he should be at the left side instead.
- **Slides not shown in full.**
  - f1352: the close-up covers the slide.
  - f1246: the camera sees the back of the roof screen; he should land directly in front of it.
  - f0269: the over-the-shoulder shot keeps too much distance between face and board.
- **Camera feels confused.** Front, back, then front again.
- **"More bugs".** Restore the old shock dance + "yuck" with the spiders swarming (v3: the full `Mickey Surprised` take,
  frames 140–262). lovestaco: keep the old one, not the roof hop.
- **Finale.** The boxes are good, but in front of building floors (v3) was more dramatic. v3's only problem: the money
  wasn't visible until the fall.
- **Word highlighting.** Highlight the spoken words on the slide (YouTube-style active word/phrase). The VO matches
  almost every slide word for word.
- **Goal.** (1) interesting enough to watch to the end (Spidey); (2) viewers get the problem and want the product.
  Both.

## Rule for every slide read (the core change)
While a VO line reads a slide:
- the **whole slide** is on screen, straight-on, static camera;
- Spidey stands or hangs **at the slide's left edge, close to it**;
- his head/shoulders overlap only the slide's reserved left margin (~10% of the board), never the text;
- he's calm and supporting: presents or looks at the words, with lens expressions;
- **gimmicks happen between reads**: swings, flips, the dance, the moonwalk (which acts out "customers walk away").
- Close-ups, over-the-shoulder shots and sign backs are used only where no slide is being read.

## 1. Presenter shot helper (`pipeline/shot.py`)
`presenter(sign_c, sign_n, w, h, stand_z, side="L", face_frac=0.10, fill=0.78)` returns
`(spidey_xy, face_deg, cam_loc, cam_target, lens)`:
- **Spidey:** stands ~0.6 m in front of the sign plane at its left edge (screen-left as seen from the camera).
- **Camera:** on the sign normal, at the distance where the sign width fills ~78% of the frame, shifted so the sign
  sits right of centre and his head lands over the left margin.
- **Lens and depth of field:** 28–35 mm, f/8, so face and slide are both sharp.

Also a build check, `read_check()`, run for every VO read frame range. It projects the slide corners, the text box and
his head into the camera and prints, per line:
- whether the slide is fully in frame;
- the text-occlusion percentage (target 0);
- head-to-slide overlap, face % of board, distance to board;
- `BACKSIDE`: any visible sign the camera is behind.

## 2. Slides: left margin + spoken-word highlights (`scripts/03c_street_signs.py`)
- **Left margin.** Every read slide reserves ~16% of its width on the left (`text_block` box x0 shifted). Applies to
  `board`, `ticker`, the graffiti/mural and roof slides, plus the caption areas of the `queue_big`, `st_bugs` and quads
  layouts.
- **Word boxes.** `text_block()` already lays out every token. Have it also write the word boxes (normalised UV) to
  `assets/street/<sign>_words.json`.
- **Markers in Blender.** New `city.highlight(sign_obj, words_json, cues)` puts a highlighter-marker strip (brand
  yellow, alpha) 1 cm in front of each word.
  - **Sync:** each marker *sweeps left → right over the word as it's spoken*, using the VO word times already in
    `vo_street/lines.json` (`word()` helper).
  - **Which words:** the active word lights as it's spoken; the **bold keywords** keep their marker afterwards; normal
    words fade back. Matching is word-for-word by text against the VO line; non-matching words are skipped.
  - **Sequences:** the same works on the bus/subway sequence slides, since their captions are static regions.

## 3. Scene-by-scene restaging (`scripts/04_street.py`)
| Read | Change |
|---|---|
| VO1 mural | Lower the wall board to street level (a wall mural, bottom ~0.4 m). He swings in and lands on the **sidewalk at its left**. Presenter shot, excited lenses, `office.present_to` toward the text. Drop the board-top crouch. |
| VO2 billboard | Two-building shot done right: he web-zips up the south building (visible) to its roof edge, **facing the camera**, billboard across the street behind/right of him. Camera on the same roof ~2.5 m from him: face at left over ~10% of the board, whole billboard readable. Replaces the OTS shot and the billboard hang. |
| VO3 ticker | Lower the ticker to shop-front height (~3 m). He lands (flip) at its **left end**. The light streak runs left → right along the text and his head follows it (guides the eye). Amazed lenses in-frame, no separate close-up. |
| VO4 bus ad | Sprint ends **at the ad's left edge**, close. Presenter shot. On "bugs" the spiders burst out → **restore v3's reaction**: full `CMU 120_16 Mickey Surprised` 140–262 (the dance) on the street, swarm at his feet, v3's low close camera, plus a "yuck" head shake (`MX Shaking Head No` / `MX Annoyed Head Shake`). Remove the shelter-roof hop. |
| VO5 subway | He hangs upside down at the board's **left edge** (east side, +x from the camera), head at caption height, close. Presenter framing, sad lenses. |
| VO6 screen | Already lands at the left. Presenter framing (camera closer and lower, his head at the lower-left margin). Tiles pop and highlight on their words; moonwalk with the customers stays (it acts out the message). |
| VO7/8 roof | Lower the roof screen (bottom ~0.3 m above the roof). Route the zip and camera so he **lands in front** of the screen (from the avenue/west side; never a shot of its back). Presenter shot for both lines (no close-up over the slide); confident lenses. |
| Finale | Move the block tower in front of the v3 finale building (`city.Building`, plaza at the avenue's north end, `FIN_C (0, 59.6)`). Blocks sized to its floors; each floor lights as its block lands, all go dark on the collapse. **Money visible from "money" on**: a bigger cash stack on the top block, elevated wide camera so the top is seen. Keep the low hero angles, the yank close-up (no slide in that shot), collapse, bill on the mask, helicopter. |

Keep from v6: all travel between reads (no location cuts), city life, lens expressions, pendulum swings, the
`check_support` / `PATH` / `OCCLUDED` checks. Traffic keepout moves to the plaza.

## 4. Render time (106 min at 360p — too slow to iterate)
Profile one frame with toggles: cars/pedestrians hidden, ray tracing off, motion blur off. Then fix the main cost,
for example:
- join each car into one mesh (wheels kept separate for spin);
- `--fast` for drafts;
- simplify the far city.

Target ≤ 1.5 s/frame at 360p.

## Critical files
- `miles/scripts/04_street.py`: staging, cameras, finale, highlights wiring.
- `miles/scripts/03c_street_signs.py`: margins, word boxes.
- `miles/pipeline/shot.py`: `presenter()`, `read_check()`.
- `miles/pipeline/city.py`: `highlight()`; reuse `Building` for the finale.
- `miles/pipeline/life.py`: keepout and lanes for the plaza.

Reuse:
- `perf.then(..., at=)`, `travel()`, `find_anchor()`, `lean()`, `fly()/land()/flip_land()`;
- `office.present_to`, `face.Lenses`, `fx.Spiders`;
- v3's bus camera and Mickey Surprised timing (`git show 461b1cf:miles/scripts/04_street.py`, lines ~208–209,
  460–465);
- v3's `city.Building` finale (lines ~361–386).

## Verification
1. `python3 scripts/03c_street_signs.py`, then check the slide PNGs: text starts right of the margin; `*_words.json`
   boxes overlay the words correctly (debug overlay image).
2. Build, then check the printout:
   - `read_check` for every VO line: slide 100% in frame, text occlusion 0%, face 8–14% of the board, no `BACKSIDE`;
   - plus `PATH` / `OCCLUDED` / `check_support` clean.
3. A contact sheet at each VO's first word + its keyword frames: highlight markers visible on the right words.
4. Bus: the dance plays fully with the swarm. Finale: cash visible from "money"; floors light per block.
5. 360p full-quality render: frames kept in `build/frames/street_360p/`, plus the `_tc` copy. Then commit.
