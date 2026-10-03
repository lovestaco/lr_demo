---
format: 1920x1080
duration: 270s
version: v2 — "The Inspection Layer" (2026-10-01)
supersedes: STORYBOARD.v1-blue.md (150s, Blue Professional motion-graphics cut)
message: "You already generate code with AI — LiveReview is the AI-assisted inspection layer you owe your users."
arc: allegory — a 1930s dam. The river is AI-generated code. The city below is production. Inspection is what keeps the water on the useful side of the wall.
audience: engineering leadership (CTO / VP Eng / EM), developers second
mode: autonomous
music: assets/bgm/bed-270.mp3 (270.024s) — bed only; no VO, no SFX, no captions
narration: none (user declined) — every card must be readable at its stated hold
---

# v2 — The Inspection Layer

## Why this cut exists

The v1 cut (`STORYBOARD.v1-blue.md`) was rejected on three grounds, in the user's words:

1. **"it looks like any other theme who hyperframe use it"** — generic motion graphics, no world.
2. **"if we just show text people cant remember right? we need to show something for them… almost each text can be tied to a scene. it should be like a movie."**
3. **"the problm section its just 48 seconds… the text scenes are too fast the user cant even read. i dont care if the video is even 4 mins."**

v2 answers all three: a real photographic world (public-domain 1930s dam
construction), every deck line tied to a scene in that world, and a problem act
that runs **169s instead of 48s**.

Three directions were put to the user and answered:

- **Turn**: *gradual* — colour seeps back one step per "→ Solved", not one hard cut.
- **Picture**: archival footage and photographs **are** the picture; deck text sits on
  top as period title cards.
- **Narration**: **none**. Text-only, so holds are sized for reading, not for motion.

## The allegory

| Deck idea | The world |
| --- | --- |
| AI code generation | the river — harnessed, poured fast, a city rising on it |
| Velocity & volume | the reservoir filling faster than anyone planned |
| Human attention is limited | two men on ropes against a thousand feet of rock |
| #1 Attention | which crack matters? |
| #2 Understanding | nobody knows how the sluices connect any more |
| #3 Enforcement | the inspection logbook with empty pages |
| #4 Control | your drawings, in somebody else's vault |
| Production incident | **August 31, 1932** — the water found the gap |
| LiveReview | the instrument layer, on your own wall |
| Close | the dam holds; the water goes to work |

## Video direction

### Grade ladder — the gradual turn

The **world** climbs the ladder; **product UI is never graded** (it is the new
technology — always sharp, always true colour). Persist every stage with
`npx hyperframes media-treatment --file <frame> --selector <sel> --grading '<json>' --apply`.
Never hand-roll an equivalent in CSS filters or overlay divs.

| Stage | Frames | `--grading` payload |
| --- | --- | --- |
| **G0** 1931 | 01–17 | `{"preset":"mono-fade","intensity":1,"details":{"vignette":0.45,"vignetteFeather":0.68,"grain":0.45,"grainSize":0.5},"effects":{"filmArtifacts":0.50}}` |
| **G1** warmth | 18 | `{"preset":"vintage-wash","intensity":0.55,"details":{"vignette":0.50,"grain":0.32},"effects":{"filmArtifacts":0.30}}` |
| **G2** partial | 19 | `{"preset":"vintage-wash","intensity":0.35,"details":{"vignette":0.42,"grain":0.22},"effects":{"filmArtifacts":0.18}}` |
| **G3** most | 20 | `{"preset":"vintage-wash","intensity":0.20,"details":{"vignette":0.34,"grain":0.14},"effects":{"filmArtifacts":0.08}}` |
| **G4** near-full | 21 | `{"preset":"vintage-wash","intensity":0.10,"details":{"vignette":0.26,"grain":0.07}}` |
| **G5** clean | 22–25 | no treatment at all |

The music bed carries the identical arc: band-limited and noisy under G0, opening
one step at each stage boundary (169.0 / 186.5 / 204.0 / 221.5 / 239.0), fully
open at G5. Already rendered into `assets/bgm/bed-270.mp3`; do not re-derive it.

### Palette

Vintage world — `--ink #0B0A08`, `--paper #EDE4D0`, `--paper-dim #C9BFA8`,
`--rule #8A7F68`, `--oxide #C2703A` (numerals, the flood, warnings only).
Modern world — `--shell #0E1322`, `--stroke #1A2440`, `--text #E8EEFF`,
`--blue #3B82F6`.

### Type

- **Vintage cards** — `"Playfair Display"` (`assets/fonts/PlayfairDisplay-var.woff2`,
  italic file alongside). Cream `--paper`. Kicker 24px / `.34em` tracking / uppercase.
  Primary 54–60px. Emphasis 72–84px weight 700. Quote 32–34px italic `--paper-dim`.
- **Modern cards** (frames 18–25) — `"Inter"` (`assets/fonts/Inter-var.woff2`).
- Every line of text over a plate sits on a **scrim** (a `linear-gradient` layout
  div, not a media treatment) so contrast clears WCAG AA.

### Two fixtures on every frame

1. **Act marker**, top-right, `right: 96px; top: 88px`, 20px, `.30em` tracking,
   uppercase, `rgba(237,228,208,.55)`.
2. **Source slug**, bottom-left, `left: 96px; bottom: 74px`, 17px, `.18em`
   tracking, uppercase, `rgba(237,228,208,.42)` — the archival caption. This is
   what sells the film as real; never omit it on a plate frame.

| Act | Frames | Marker |
| --- | --- | --- |
| I | 01–04 | `I · THE RIVER` |
| II | 05–07 | `II · THE BELIEF` |
| III | 08–12 | `III · THE RISING WATER` |
| IV | 13–14 | `IV · THE CRACKS` |
| V | 15–16 | `V · FOUR QUESTIONS` |
| VI | 17–21 | `VI · THE INSPECTION LAYER` |
| VII | 22–25 | `VII · THE DAM HOLDS` |

### Layouts (literal geometry — reuse exactly)

- **`bleed`** — plate `position:absolute; inset:0; object-fit:cover`. Ken Burns:
  `scale 1.055 → 1.0` over the full frame, `ease:"none"`. Bottom scrim
  `linear-gradient(180deg, transparent 38%, rgba(11,10,8,.88) 100%)`, height 1080.
  Text block left 140, width 1360, anchored so the last line sits at `top: 872px`.
- **`film-bleed`** — archive `<video>` is 1440×1080; place at `left:240; top:0`.
  Side columns `--ink`. 1px `rgba(237,228,208,.20)` hairline at x=240 and x=1680
  (the film gate). Same bottom scrim and text block as `bleed`.
- **`split-right`** — portrait plate at `left:1020; top:0; width:900; height:1080;
  object-fit:cover`. Left field `--ink` 0→1020. Text left-aligned at `left:140`,
  width 780, vertically centred on 540. 1px `--rule` hairline at x=1020.
- **`split-left`** — mirror: plate `left:0; width:900`, text block `left:1060`,
  width 760, hairline at x=900.
- **`card-then-film`** — the found 1931 intertitle clip plays alone in the gate
  (no overlay text — it reads itself), then cross-dissolves at its out-point to
  the live-action clip, over which one gloss line appears.
- **`problem-quad`** — four 8s sub-beats in one frame. Each: plate cross-dissolves
  in over 0.5s, numeral + title at +0.6, question at +1.8, holds. A tally of four
  marks at `right:96; top:150` fills one mark per beat and persists.
- **`answer`** — modern. App window shell `left:230; top:346; 1460×658`, bg
  `--shell`, 1.5px `--stroke` border, 12px radius, 31px top bar. Video rect
  `x:232 y:379 1456×623`, **`object-fit: contain`** (demo clips are 2520×1080 21:9 —
  never crop product UI). Statement card above the window; allegory tie-line and
  "→ Solved" seal below.
- **`recap`** — no media; four rows, modern type, centred.

### Motion rules

Deterministic and seek-safe throughout: no `Math.random()`, no `Date.now()`, no
CSS transitions, no `repeat`/`yoyo`. Animate transforms and opacity (`x`, `y`,
`scale`, `opacity`), never `top`/`height`/`width`. One paused GSAP timeline per
composition at `window.__timelines[ID]`. Gate every timed element with
`class="clip"` + `data-start` + `data-duration` + `data-track-index` — never with
an inline `style.visibility` written from an `onUpdate` director (that leaked
across the entire v1 film and took 16 check errors to find).

Text enters by word or line: `opacity 0→1`, `y 18→0`, `blur(6px)→blur(0)`,
`duration .42`, `ease "power3.out"`, `stagger .06`. Nothing exits before its
frame ends — a line that has been read stays on screen.

### Reading-speed floor (the whole point of this cut)

Every card holds at least `max(3.2s, words × 0.42 + 1.4s)` **after** its entrance
completes. When in doubt, hold longer — the runtime budget already absorbed it.

---

## Frames

Total **270.000s**. Durations are computed in `.plan/frames.json`; that file is the
machine-readable source of truth for start/duration and must match this table.

### Act I · THE RIVER

**01 · the-river** — 0.0 → 8.5 (8.5s) · `film-bleed` · `v_river` · G0
- 0.6 `You already do a lot of —` (54px)
- 2.4 **`AI-ASSISTED CODE GENERATION`** (76px/700)
- 4.6 quote, 32px italic `--paper-dim`, centred under: *"…to break the will of a
  treacherous and tempestuous river, tame it and harness its floods."* — then a
  20px attribution line: `BOULDER DAM: THE OFFICIAL PICTURE · U.S. BUREAU OF RECLAMATION · 1931`
- slug: `COLORADO RIVER · BLACK CANYON · 1931`

**02 · the-pour** — 8.5 → 15.5 (7.0s) · `film-bleed` · `v_pour_bucket` · G0
- 0.5 `Day and night, the pouring never stopped.` (54px)
- 3.0 **`Neither does yours.`** (64px/700)
- slug: `PLACING CONCRETE · BOULDER DAM · 1933`

**03 · the-inspection** — 15.5 → 25.0 (9.5s) · `split-right` · `p07_highscaler2` · G0
- 0.6 `But do you do enough of —` (50px)
- 2.6 **`AI-ASSISTED CODE INSPECTION?`** (68px/700, wraps to two lines)
- 5.6 `Two men. A mile of wall. One rope each.` (30px italic `--paper-dim`)
- slug: `HIGH SCALERS · ARIZONA ABUTMENT · 1932`

**04 · the-scalers** — 25.0 → 33.0 (8.0s) · `card-then-film` · `t_scalers_card` (0→3.6) then `v_scalers_b` (3.4→8.0) · G0
- The 1931 intertitle reads itself, no overlay: *"High scalers swarmed over the
  1,000-foot cliffs preparing abutments for the dam."*
- 4.4 gloss over the live footage: `Somebody has to walk the wall before the concrete goes in.` (40px)
- slug: `BOULDER DAM: THE OFFICIAL PICTURE · 1931`

### Act II · THE BELIEF

**05 · believe** — 33.0 → 39.5 (6.5s) · `bleed` · `p05_first_bucket` · G0
- 0.4 kicker `HERE IS WHAT WE BELIEVE`
- 1.2 **`The river was never the problem.`** (58px/700)
- 3.4 **`The unwatched wall was.`** (58px/700 `--oxide`)
- slug: `FIRST CONCRETE PLACED · JUNE 6, 1933`

**06 · you-owe** — 39.5 → 48.0 (8.5s) · `bleed` · `p09_city_pano` · G0
- 0.6 `You owe your users and customers —` (50px)
- 2.6 **`AN AI-ASSISTED INSPECTION LAYER`** (70px/700)
- 5.4 `Everything downstream is built on the assumption that it holds.` (30px italic)
- slug: `BOULDER CITY · THE TOWN BELOW THE DAM · 1932`

**07 · professional** — 48.0 → 56.5 (8.5s) · `split-left` · `p10_concrete_ctrl` · G0
- 0.6 `If you are professional —` (48px)
- 2.4 **`you must adopt it.`** (62px/700)
- 4.8 `For the sake of your business reputation.` (38px)
- slug: `CONCRETE TESTING LABORATORY · PERSONNEL · 1933`

### Act III · THE RISING WATER

**08 · velocity** — 56.5 → 64.5 (8.0s) · `film-bleed` · `v_cableway_car` · G0
- 0.4 kicker `HERE IS WHY`
- 1.6 **`Code accumulates at great VELOCITY`** (68px/700)
- 4.6 `Eight cubic yards at a time. Every few minutes. For two years.` (30px italic)
- slug: `EIGHT-YARD BUCKET ON THE CABLEWAY · 1933`

**09 · volume** — 64.5 → 73.5 (9.0s) · `bleed` · `p12_cofferdam` · G0
- 0.6 `The higher velocity leads to` (50px)
- 2.4 **`a HUGE VOLUME of code.`** (72px/700)
- 5.6 `And all of it is now standing behind one wall.` (30px italic)
- **Motion — the one water-line beat**: a 1px `--paper` hairline spanning the full
  width rises from `y:900` to `y:520` between 2.8 and 8.2, `ease:"none"`, driven by
  `y` translate (never `top`). A 17px label `RESERVOIR` rides its right end.
- slug: `UPSTREAM COFFERDAM AT MAXIMUM ELEVATION · 1932`

**10 · deliver** — 73.5 → 80.5 (7.0s) · `bleed` · `p13_ranch_res` · G0
- 0.6 `And you still need to deliver to your customers —` (46px)
- 2.4 / 3.1 / 3.8 three words land in sequence on one line (64px/700):
  `faster,` `safer,` `higher quality.`
- slug: `IRRIGATED RANCH BELOW THE DAM · 1935`

**11 · you-still-must** — 80.5 → 95.0 (14.5s) · `split-right` · `p14_grouting` · G0
- 0.3 kicker `YOU STILL MUST`
- Four ledger rows, 38px, each preceded by an **unticked** 22px `--oxide` box, a
  1px `--rule` divider between rows. Rows enter at 1.2 / 4.2 / 7.0 / 9.8 and all
  four stay to the end:
  - `Reduce production incidents`
  - `Reduce security incidents`
  - `Reduce performance regressions`
  - `Deliver stellar customer experiences`
- The boxes never tick — these are obligations, not achievements.
- slug: `GROUTING CREW · ARIZONA ABUTMENT · 1934`

**12 · attention-limited** — 95.0 → 105.5 (10.5s) · `film-bleed` · `v_scalers` · G0 — **hero**
- 0.8 `And let's remember —` (48px)
- 2.8 **`HUMAN ATTENTION IS STILL LIMITED`** (80px/700, two lines)
- 5.4 two soft cream lamp-pools (radial-gradient divs, r≈92) fade to `opacity .26`
  at two points over the rock face while a `rgba(11,10,8,.55)` field covers the
  rest — the covered fraction is visibly tiny.
- 7.6 `Two lamps. One thousand feet of rock.` (28px italic)
- slug: `HIGH SCALERS · 1,000-FOOT CLIFFS · 1932`

### Act IV · THE CRACKS

**13 · bigger-systems** — 105.5 → 114.0 (8.5s) · `card-then-film` · `t_blocks_card` (0→3.8) then `v_blocks` (3.6→8.5) · G0
- The 1931 intertitle reads itself: *"The Dam was constructed of an intricate
  pattern of individual blocks — each keyed to the next."*
- 4.6 gloss: `More code means bigger systems — and more interconnections.` (44px)
- slug: `BOULDER DAM: THE OFFICIAL PICTURE · 1931`

**14 · more-complexity** — 114.0 → 122.5 (8.5s) · `split-left` · `p17_pothole` · G0
- 0.6 `More code means —` (48px)
- 2.4 **`more complexity, more bugs, more issues.`** (60px/700, wraps)
- 5.2 `And there are deeper consequences to take care of.` (30px italic `--oxide`)
- slug: `POT-HOLE EROSION DISCLOSED IN THE FOUNDATION · 1933`

### Act V · FOUR QUESTIONS

**15 · four-problems** — 122.5 → 154.5 (32.0s) · `problem-quad` · G0
Four 8.0s sub-beats. Tally at `right:96; top:150`: four 28×3px marks, one filling
per beat, `--oxide`, persisting.

| Beat | at | plate | numeral + title | question |
| --- | --- | --- | --- | --- |
| 1 | 0.0 | `p16_cleavage` | `№ 1 · THE ATTENTION PROBLEM` | `Which changes deserve your engineers' scarce attention?` |
| 2 | 8.0 | `p18_drillbit` | `№ 2 · THE UNDERSTANDING PROBLEM` | `How can your engineers keep intellectual control of the system?` |
| 3 | 16.0 | `p11_recorders` | `№ 3 · THE ENFORCEMENT PROBLEM` | `How do you make good review happen every time — without slowing the team down?` |
| 4 | 24.0 | `p19_controltower` | `№ 4 · THE CONTROL & IMPROVE PROBLEM` | `How do you own your IP, your code, your data, your model interactions?` |

Numeral+title 26px `.22em` `--oxide`; question 52px/600 `--paper`, wraps to two
lines max. Each plate is its own `clip`, cross-dissolving 0.5s into the next.
Slug changes per beat to that plate's archival caption.

**16 · the-flood** — 154.5 → 164.0 (9.5s) · `card-then-bleed` · `t_menace_card` (0→3.6) then `p21_flood_portal` (3.4→9.5) · G0 — **darkest**
- The 1931 intertitle reads itself first, no overlay: *"— its turbid floods, an ever
  present menace to life and property —"*
- 4.2 **`AUGUST 31, 1932`** (72px/700 `--oxide`)
- 6.0 `The water found the gap. Nobody was watching that section.` (38px)
- Motion: plate `scale 1.0 → 1.08` from 3.4 to 9.5, `ease:"none"`.
- slug: `FLASH FLOOD · OUTLET PORTAL, DIVERSION TUNNEL No. 2`

### Act VI · THE INSPECTION LAYER

**17 · heres-how** — 164.0 → 169.0 (5.0s) · `bleed` · `p02_first_water` · G0 — **pivot, last G0 frame**
- 0.6 **`Here's HOW LiveReview solves them all:`** (62px/700)
- 3.0 the LiveReview mark (`assets/logo.svg`, 44px tall) fades in beneath — its
  first appearance in the film.
- slug: `FIRST WATER THROUGH THE DIVERSION TUNNELS · 1932`

Frames 18–21 all share the `answer` layout and this beat structure:

| at | what |
| --- | --- |
| 0.4 | statement card, Inter 42px/600, above the window |
| 1.4 | window shell opens (`scale .965 → 1`, `opacity 0 → 1`, .5s `power3.out`) |
| 2.0 | product clip(s) play |
| ~10.8 | allegory tie-line, 26px italic, `rgba(237,228,208,.62)`, below the window |
| 12.4 | seal: `The <N> Problem → Solved` + check glyph, 40px/700 |
| — | seal resolves by ~14.2, leaving ≥3.3s of hold before the cut |

**18 · answer-attention** — 169.0 → 186.5 (17.5s) · G1
- statement: `LiveReview ranks every hunk by blast radius and review priority.`
- clip: `clip05_blast.mp4` (8.0s) at 2.0
- tie: `The wall, mapped. The dangerous sections lit.`
- seal: `The Attention Problem → Solved`

**19 · answer-understanding** — 186.5 → 204.0 (17.5s) · G2
- statement: `Summaries, issue navigation and PR quizzes keep humans in the loop.`
- clips: `clip11_slides.mp4` (5.33s) at 2.0, `clip11_quiz.mp4` (2.67s) at 7.4
- tie: `The blueprints, restored. The crew, examined.`
- seal: `The Understanding Problem → Solved`

**20 · answer-enforcement** — 204.0 → 221.5 (17.5s) · G3
- statement: `LiveReview reviews at commit, push, PR, CI/CD and on schedule — enforcing your rules.`
- clips: `clip08_schedule.mp4` (4.0s) at 2.0, `clip10_cicd.mp4` (6.67s) at 6.0
- tie: `Not a promise to inspect. A gate that will not open.`
- seal: `The Enforcement Problem → Solved`

**21 · answer-control** — 221.5 → 239.0 (17.5s) · G4
- statement: `Your infrastructure. Your choice of model. Livi learns from every review.`
- clip: `clip15_livi.mp4` (8.13s) at 2.0
- tie: `Your drawings stay in your own vault.`
- seal: `The Control and Improve Problem → Solved`

### Act VII · THE DAM HOLDS

**22 · full-blown** — 239.0 → 247.0 (8.0s) · `bleed` · `p40_dam_today` · **G5, no treatment**
- 0.6 `That's why you owe your customers, your profession and your reputation —` (40px)
- 2.8 **`A FULL-BLOWN AI-ASSISTED CODE INSPECTION LAYER`** (62px/700, two lines)
- slug: `HOOVER DAM · TODAY`
- This is the first fully clean, fully colour frame. Let it land.

**23 · one-system** — 247.0 → 254.5 (7.5s) · `answer` · `clip13_dashboard.mp4` · G5
- 0.4 statement: `The only platform that solves all four — in one unified system.`
- clip at 1.4

**24 · four-checks** — 254.5 → 262.5 (8.0s) · `recap` · G5, no media
- 0.4 `Here's what LiveReview solves:` (42px)
- rows at 1.4 / 2.4 / 3.4 / 4.4, 44px, each with a `--blue` check:
  `The attention problem` · `The understanding problem` · `The enforcement problem` · `The control and improve problem`

**25 · cta** — 262.5 → 270.0 (7.5s) · `bleed` · `p41_lake_today` · G5
- 0.8 `assets/logo.svg`, 64px tall
- 2.2 **`hexmos.com/livereview`** (70px/700)
- 4.4 `The water still comes. Now something is watching the wall.` (30px italic)
- slug: `LAKE MEAD · THE WATER, PUT TO WORK`

---

## Assets

Archival picture is **public domain** (U.S. Bureau of Reclamation / NARA, and
Prelinger/FedFlix film). Provenance recorded in `assets/plates/_manifest.json`
and `ATTRIBUTION.md`.

- `assets/plates/p*.jpg` — 34 archival photographs, scan borders trimmed, normalised.
  Originals kept at `assets/plates_raw/`.
- `assets/archive/v_*.mp4` — 10 hero film clips, 1440×1080, silent, cut from
  `BoulderD1931` and `BoulderD1931_2` (archive.org, public domain).
- `assets/archive/t_*.mp4` — 3 **found 1931 intertitles**, used verbatim as cards.
- `assets/clip*.mp4` — the existing LiveReview product captures (unchanged).
- `assets/bgm/bed-270.mp3` — the bed with the restoration arc baked in.
- `assets/fonts/PlayfairDisplay-var.woff2` (+ italic) — the period face; `Inter-var.woff2` — the modern face.

## Notes

- The user asked to finish autonomously across any session-limit reset and deliver
  the rendered file ("if tokens get exhausted wait until it resets and continue…
  I'll see you in the morning"). Mode is therefore `autonomous`.
- Runtime is **4:30**, up from 2:30. The problem world alone is 169s (was 48s).
  State the runtime in the delivery message — running past the original target was
  the user's explicit call ("i dont care if the video is even 4 mins").
- `p25_dam_1935` came back at only 1250×1250 and is unused. `p28_testlab`,
  `p22_catwalk`, `p23_hotspring`, `p26_aggregates`, `p27_coach`, `p36_cableway`,
  `p37_headtower`, `p38_rim_pano` are sourced but unassigned — spares for notes.

---

## Build notes (v2, 2026-10-01)

Recorded so a later session does not re-derive them.

### Structural fixes applied after the frame workers finished

1. **`video_nested_in_timed_element` (8 frames)** — the lint rule fires on *any*
   timed `<video>` inside *any* timed element, even when the wrapper starts at 0.
   Fix: the 1440×1080 film gate (and frame 19's window shell) is now an **untimed
   geometric container** — no `class="clip"`, no `data-start`/`data-duration`. The
   media inside carries all the timing. Frames 18, 20, 21 solved it differently
   (media as a stage-level sibling at absolute coords); both forms are correct.
   **Do not re-add timing to a gate div.**
2. **`root_missing_dimensions` (21 frames)** — every frame `#root` now carries
   `data-width="1920" data-height="1080"`.
3. **`media_missing_data_start`** — every `<img>`/`<video>` now carries
   `class="clip"` + `data-start` + `data-duration` + `data-track-index`.
4. **The archival "ghost"** — frames 18–21 each gained a full-bleed plate behind
   the product window at `opacity .26` under a radial scrim. Each answer uses the
   **same plate as its matching problem beat in frame 15**, so the answer rhymes
   back to the problem and the G1→G4 ladder has archival media to act on.
   (Without it the answer frames contain only product UI, which is never graded,
   and the gradual restoration would be invisible.) Inserted by
   `.plan/add_ghosts.py`.
5. **Frame 22 key line** moved 2.8 → 2.6 to clear the reading-speed floor.
6. **The LiveReview mark is never graded** — `.plan/apply_grades.py` excludes
   `logo.svg` and `brand-*`; it was briefly mono-faded in frame 17 and cleared.

### Known, accepted

- **238 × `id_requires_css_escape` warnings.** Inherent to the mandated
  frame-id-prefixed ids (they start with a digit). Every stylesheet uses
  `[id="…"]` attribute selectors and every script uses `getElementById`, so
  nothing ever feeds them to `querySelector`. Not fixable without renaming every
  id in the film; harmless.
- **Frame 24's last row** holds 3.16s against a 3.5s computed floor. Accepted:
  it is the fourth item of a recap list the viewer has already met four times,
  and retiming two frames to recover 0.34s was not worth the regression risk.

### Tooling written for this cut (`.plan/`)

| file | does |
| --- | --- |
| `frames.json` | machine-readable timeline; the source of truth for start/duration |
| `content.json` | per-frame copy and timings |
| `make_packets.py` | emits one bounded worker packet per frame |
| `_role.md` | the shared frame-worker contract |
| `assemble.py` | builds `index.html` from `frames.json` |
| `apply_grades.py` | applies the G0–G4 ladder; never touches product clips or the logo |
| `add_ghosts.py` | inserts the archival backdrop into frames 18–21 |
| `fix_structure.py` | the three structural lint fixes above |

`assemble.py` is idempotent and re-runnable — unlike v1, **no hand-patching of
`index.html` is required**, because no media is hoisted out of the frames.

### Visual-QA fixes (contact sheet pass, 2026-10-01)

Five defects the contact sheet caught that neither lint nor check would have:

1. **Frame 15 retimed 32.0s → 36.0s** (film 270 → **274.0s**). Questions 3 and 4
   are 14 and 13 words and got only 5.59s of hold against a ~7.3s reading floor.
   Since "the text scenes are too fast the user cant even read" is the reason
   this cut exists, a beat that fails the floor is the one defect that cannot
   ship. New beats: 8.0 / 9.0 / 9.5 / 9.5. All four questions now clear the floor
   (margins +1.25 / +0.99 / +0.11 / +0.23). Beat 3's question enters at beat+1.5
   rather than beat+1.8 — the only way to buy the last 0.19s without lengthening
   the frame again. The music bed was rebuilt at 274s with the grade boundaries
   moved to 173.0 / 190.5 / 208.0 / 225.5 / 243.0.
2. **The product window sat empty for 5–7s** in frames 18–21: the demo clip ends
   around 10s but the frame runs to 17.5s, leaving a blank blue rectangle under
   the seal. The shell now **dissolves out** 0.15s after its clip ends and the
   archival ghost lifts from .26 to .44, so the tie-line and the "→ Solved" seal
   land on the recovering plate instead of on an empty window. This is better
   than the original design, not just a patch.
3. **`assets/logo.svg` is an eye icon, not a wordmark** — at 44/64px it read as a
   dot. Frames 17 and 25 now set the mark beside the word "LiveReview".
4. **G0 was crushing the plates.** Vignette .45 → .32, feather .68 → .78, plus
   `exposure +0.06 / shadows +0.18 / blacks +0.08` on the mono-fade. The stack of
   vignette + bottom scrim + mono-fade was compounding into near-black corners.
5. **Scrims strengthened on frames 16, 22 and 25**, whose text sits high in the
   frame where a bottom-only gradient has not ramped up yet. All three now use a
   four-stop ramp with real density behind the type.

### Latent bug worth remembering

`video_nested_in_timed_element` **cannot be trusted**. Its nesting scan stops at
the first `</div>`, so a timed `<video>` inside a timed wrapper is missed whenever
another div closes in between — which is exactly what the `answer` layout's top
bar does. Three frames passed lint while carrying the real bug. Verify this class
of defect with an actual HTML parser walking each media element's full ancestor
chain, not with the lint rule. The invariant to hold: **no `<img>`/`<video>`
carrying `data-start` may sit under any element that also carries `data-start`.**

### Rendering: the shaders had to be baked out

The film would not render with runtime media treatments. Both capture paths failed:

- **With the GPU** (`--browser-gpu`): repeated `WebGL: CONTEXT_LOST_WEBGL` and the
  capture stalled hard at frame 255 (= 8.50s, the frame 01→02 cut). The renderer
  rated the workload `costMultiplier: 8` and dropped itself to 1 worker.
- **Without it** (`--no-browser-gpu`, SwiftShader): ~0.06 fps — a 31-hour render.

Cause: grain / vignette / `filmArtifacts` are WebGL shaders evaluated **every
frame**, on 23 media elements. v1 had no treatments, which is why it rendered in
under nine minutes.

Fix: **`.plan/bake_grades.py`** bakes each stage into the media with ffmpeg and
strips `data-color-grading` entirely. Every treatment in this film is static per
element — nothing animates a treatment — so baking is output-equivalent. Graded
copies live in `assets/plates_graded/` and `assets/archive_graded/`, named
`<source>.<stage>.<ext>`; the originals are untouched, so the shader version can
be restored by re-running `apply_grades.py` against the original `src` paths.

After baking: **6.45 fps, 20m 13s total.**

The render settings that work on this machine:

```bash
npx hyperframes@0.8.99 render . --browser-gpu --workers 1 \
  --protocol-timeout 900000 --player-ready-timeout 240000 --browser-timeout 300 \
  -o renders/livereview-inspection-layer.mp4
```

- `--workers 1` is required. Multi-worker disables streaming encode and wants
  ~8.5 GB of frame staging; it fails the disk gate on this box.
- The long timeouts are required: 25 sub-compositions / 16 videos / 249 timed
  clips blow past the default 45s player-ready and 300s protocol timeouts.
- **`hyperframes check` does not work here** — it hung twice producing zero bytes
  over 30+ minutes and had to be killed. Verification was done instead with
  `lint` (0 errors), a parser-based nesting audit, `hyperframes timeline` to
  confirm every media window, and ~34 snapshot sample points.

### Audio must be an element, not just `audio_meta.json`

The first successful render came out with **no audio track**. `audio_meta.json`
alone is not enough — the root composition needs an explicit
`<audio id="el-bgm" src="…" data-start data-duration data-volume>`, which v1 had
and the new assembler was missing. `.plan/assemble.py` now emits it.

### Delivery encode

The baked grain resists inter-frame compression: the raw render is 408 MB
(12.3 Mbps). The shipped file is a CRF 20 / `-tune film` / `aq-mode=3` re-encode
at **197 MB (5.8 Mbps)**, verified indistinguishable from the master at 1:1 crop.
