# Part 2b — S16/S17 final plan (updated 2026-10-09)

Status: **VO recorded and split in. No scene changes started yet.**

## VO — final (recorded takes, in `assets/audio/vo_street_part2/takes/`)
Tags are ElevenLabs v3-style delivery tags; `07b_split_take.py` strips `[…]` before word matching.
The takes were copied from `videos/livereview-launch/assets/take_08..11.mp3` into
`miles/assets/audio/vo_street_part2/takes/`, re-split, and `lines.json` now has real word times.
`vo_street_part2.md` was updated to match.

| # | Scene | Duration | Line (with delivery tags) |
|---|---|---|---|
| 8 | S16 engineers | **24.84 s** | `[confident]` LiveReview gives your engineers attention and understanding. `[focused]` Every issue is ranked by importance, sorted by real blast radius — what a change touches, how far it spreads, and how risky it is — so the critical one never gets buried. `[matter-of-fact]` A slide deck for every change, explaining what moved and why. `[light]` A quick quiz to check the reviewer understood it. `[casual]` Conversations right on the MR. `[warm]` And Livi, your bot for reports and actions. |
| 9 | S17 agents | **17.32 s** | `[confident]` And it gives your agents what they need to enforce your standards at scale. `[assertive]` CI/CD gates apply precise, customized enforcement on every merge. `[friendly]` Integrations keep the team in the loop — Teams and Slack. `[matter-of-fact]` And MCP lets any preferred AI agent operate Livi right from your own agent. |
| 10 | S18 rebuild | **6.27 s** | `[steady]` Use agents for scale. Use your judgment for better product. `[emphatic]` Inspection holds it all up. |
| 11 | S19 call to action | **12.28 s** | `[confident]` LiveReview keeps you competitive: humans and AI, working together. `[clear]` The blast-radius aware AI code reviewer for your critical systems. `[inviting]` Sign in to try it, or contact us to learn more. |

Notes:
- Line 10 was **recorded as "…use your judgment for better product…"** (not "always") — script set to match; confirm wording.
- Line 10's transcript has a trailing `subs by www.zeoranger.co.uk` — a Whisper hallucination on the clip tail; the audio is clean.
- Line 11 drops the "most efficient way" clause (was flagged as wrong positioning). The matching caption in
  `04_street_part2.py` (`OVER`, ~line 940) still says "the most efficient way…" and must be updated too.

### Word-driven item spans in the new take (what the boards pop on today)
S16 (line 8): issues 4.02 → slide 14.02 (**10.0 s**) · slide → quick 17.88 (**3.9 s**) ·
quick → conversations 20.2 (**2.3 s**) · conversations → livy 22.34 (**2.1 s**) · livy → end (**2.5 s**)
S17 (line 9): ci 4.38 / gates 5.08 → integrations 9.38 (**~4.3 s**) · teams 11.28 → slack 11.78 (**0.5 s**) ·
mcp 12.7 → end (**4.6 s**)

The S16 pacing already lands close to the requested clip lengths. S17 "Teams and Slack" is 0.5 s of speech,
which can't cover 2 s + 2 s — needs fixed durations or a re-read.

## S16 — clip plan ("For your engineers: attention + understanding")
| # | On-screen item | Source (all in `videos/livereview-launch/assets/`) | Requested | vs word span |
|---|---|---|---|---|
| a | Issues ranked by importance | `blast_radius_zoom.mp4` (1612×1080, 12.0 s) | full clip, no trim | 10.0 s |
| b | A slide deck for every change | `slide_deck.gif` (762×656, 5.4 s) | 5 s | 3.9 s |
| c | A quick quiz to check understanding | `quiz.gif` (762×656, 3.7 s) | 3 s | 2.3 s |
| d | Conversations right on the MR | `converse_in_mr.png` (1005×884, still) | 2 s | 2.1 s |
| e | Livi: bot … reports + actions | `demo_livi_chat_bot.mp4` (11.0 s) | **only 2 s–5 s** (trim rest) | 2.5 s |

## S17 — clip plan ("For your agents: enforcement + scale")
| # | On-screen item | Source | Requested | vs word span |
|---|---|---|---|---|
| a | **"CI/CD Gates: Precise, Customized Merge Enforcement"** (text changed) | `demo_cicd_gates.mp4` (2520×1080, 4.0 s) | full 4 s | 4.3 s |
| b | Integrations: Slack, Teams, Discord | images `logos/teams.png` then `logos/slack.png` | **2 s then 2 s** | 0.5 s |
| c | MCP | **no clip** — text only | "MCP can be used to connect to any preferred AI Agent to operate Livi right from your agent." | 4.6 s |

## Board branding (top-left)
- Put the **LiveReview** wordmark inside the board card's top-left blue box: **LiveReview** in white,
  **hexmos.com/livereview** in light grey. Today the card has only a thin blue accent bar and the brand
  line sits under the demo video on the right.

## Implemented (2026-10-09 — built, **not rendered**)
- `scripts/05b_street_part2_boards.py` rewritten:
  - S16 media: `blast_radius_zoom.mp4` (full), `slide_deck.gif` (5 s), `quiz.gif` (3 s),
    `converse_in_mr.png` (2 s), `demo_livi_chat_bot.mp4` (trimmed to 2 s–5 s).
  - S17: item a text + `demo_cicd_gates.mp4` (full 4 s); item b = a **video** (`demo_schedule_review.mp4`,
    starts on the word "integrations", no teams/slack images); item c MCP = text-only card.
  - LiveReview wordmark in the board's blue header (white) + URL (light grey).
  - **Full-screen rule:** the media starts in the right panel and expands to full screen when the item's
    configured media length is **> 2 s**; otherwise it stays in the panel. Result: S16 only "Conversations"
    stays in the panel (others full); S17 MCP is a text card. Handles video / GIF / still and trims.
- `scripts/04_street_part2.py`: pop words fixed — S16 a on `"issue"` (VO says issue, not "issues"),
  e on `"livy"`; S17 a on `"gates"`, b on `"integrations"` (video starts there); S14/S15 `code`→`results`;
  line-11 caption updated to "humans and AI, working together".
- `pipeline/streetkit.py`: `ALIAS` gains `livi → livy`.
- **Standalone build:** `scripts/04_street_part2_b.py` → `build/street_part2_b.blend` (S16-S19 only; timeline starts
  at frame 1 = the S16 cut; he is off frame through S16/S17). The old `04_street_part2.py` / `street_part2.blend` is
  superseded. Overlays `build/street_part2_b_overlays.json`: `end 2159`; s16 `[1,772]` items `[122,422,537,607,671]`;
  s17 `[773,1322]` items `[925,1054,1154]`. `check_rules` → ALL OK, no path hits.
- `05b_street_part2_boards.py` now takes the part name as a 2nd arg (`… OUT street_part2_b`) and reads that overlays file.

## Open questions / notes
- **Integrations video:** no integrations-specific clip exists, so item b uses `demo_schedule_review.mp4`
  (the previous mapping) — confirm, or supply a better clip.
- `teams_integration.png` / `slack_integration.png` (supplied earlier) are currently **unused**.
- The full-screen brand pill can overlap a demo UI's own header (cosmetic).
- Media is cover-cropped to 16:9 (no letterbox), so `blast_radius_zoom.mp4` (3:2) loses top/bottom.

## To finish (when asked)
Render the 3D range skipping S16/S17 → `05b_street_part2_boards.py <frames> ` (boards) →
`06c_street_part2_post.py` (captions) → `06_assemble.py street_part2 --height 720 --music …`.

---

## Changes (2026-10-10) — APPLIED, see 'Done 2026-10-10' at the bottom
Source: colleague review (shrijith): "gives attention and understanding" doesn't make sense. More issues to come.

### Line 8 (S16) — reworded, re-recorded
- New take (replaces `take_08.mp3`, **not copied/split yet**):
  `/home/lovestaco/Downloads/ElevenLabs_2026-10-10T01_10_32_Mark - Natural Conversations_pvc_sp100_s44_sb75_v4.mp3`
  (**26.75 s**, was 24.84 s -> S16 grows ~1.9 s; item spans and S16 length must be re-timed from the new word times).
- New script text:
  `[confident]` LiveReview helps your engineers focus on what matters. `[focused]` Every issue is ranked by importance,
  sorted by real blast radius — what a change touches, how far it spreads, and how risky it is — so the critical one
  never gets buried. `[matter-of-fact]` Then they can understand every change: a slide deck for each one, explaining
  what moved and why. `[light]` A quick quiz to check the reviewer understood it. `[casual]` Conversations right on
  the MR. `[warm]` And Livi, your bot for reports and actions.
- Board title (S16 card) to match: the spoken opening, "LiveReview helps your engineers focus on what matters"
  (was "For your engineers: attention + understanding") — confirm if a shorter title is wanted.
- Pop words unchanged (`issue`, `slide`, `quick`, `conversations`, `livy`) — verify they still match after the re-split.

### Line 9 (S17) — "team / Teams" ambiguity (reviewer) -> reworded
- Problem (VO only): "Integrations keep **the team** in the loop — **Teams** and Slack." = people vs. the chat app.
- Chosen sentence 3 (replaces the "Integrations keep the team in the loop — Teams and Slack." sentence; needs a re-record
  of take 09, the rest of line 9 unchanged):
  `[friendly]` Integrations help you work with Livi everywhere — in Microsoft Teams and Slack.
- New take 09 (replaces `take_09.mp3`, **not copied/split yet**, duration 18.68 s, was 17.32 s):
  `/home/lovestaco/Downloads/ElevenLabs_2026-10-10T01_15_24_Mark - Natural Conversations_pvc_sp100_s44_sb75_v4.mp3`
- Full line 9 then: `[confident]` And it gives your agents what they need to enforce your standards at scale.
  `[assertive]` CI/CD gates apply precise, customized enforcement on every merge. `[friendly]` Integrations help you work
  with Livi everywhere — in Microsoft Teams and Slack. `[matter-of-fact]` And MCP lets any preferred AI agent operate
  Livi right from your own agent.
- Pop words: `integrations` still the trigger; the Teams/Slack images (2 s + 2 s) can key off "Microsoft Teams" / "Slack"
  (more speech time than the old 0.5 s) — re-check after the split. "Livi" is in the aliases (`livi -> livy`).
- Board item text "Integrations: Slack, Teams, Discord" (`05b_street_part2_boards.py:42`): consider "Microsoft Teams, Slack" for consistency.

### To do when told to start
1. Copy the new takes (08 and the re-recorded 09) over `assets/audio/vo_street_part2/takes/take_08.mp3` (and `videos/livereview-launch/assets/take_08.mp3`);
   re-split with `07b_split_take.py`; check `lines.json` word times.
2. Update `vo_street_part2.md` line 8 + the table above; S16 board title in `05b_street_part2_boards.py`.
3. Rebuild `04_street_part2_b.py` (S16 is longer: overlay frame ranges shift), re-render boards/3D range, captions, assemble.
4. Wait for the further issues from the reviewer before rebuilding.

## Pending change (2026-10-10): subtitles everywhere — REQUIRED (user: "need to have subtitles"), NOTES ONLY
Reviewer (shrijith) + user agree: show subtitles whenever the narrator speaks — "or at least try", it should help understanding.
- Today: only selective key-phrase lower-thirds (`OVER` in `04_street_part2*.py` -> overlays json -> `06c_street_part2_post.py`
  `caption()`: dark band, white text, **bold** in yellow, 6-frame fade). They are not a transcript.
- Data already exists: `assets/audio/vo_street_part2/lines.json` has per-line start/length + per-word times (whisper), so
  the cues can be generated automatically; the same data gives an `.srt` per video as a by-product.
- Plan sketch: a new step (e.g. `06d_subtitles.py`) builds cues from lines.json (delivery tags stripped, ~1 line / 6-9 words,
  split at punctuation, min ~1 s, ends at the line end), writes `build/<name>_subs.srt` + feeds the same renderer in
  `06c` (new "subtitle" style: smaller, white only, no yellow, bottom-centre).
- CONFIRMED by user: subtitles for all three — part 1 (`street_part_1_final`, VO `vo_street`), part 2a (`street_part2_a`, lines 1-7), part 2b (`street_part2_b`, lines 8-11), same style. Build 2b first (after takes 08/09 are re-split), then 2a, then part 1.
- Decisions to confirm before building:
  1. Existing key-phrase captions (S14 "Same headcount / More results", S18 "Inspection holds it all up", S19 closing line):
     keep (moved up / different style), or drop since the subtitle says the same thing?
  2. Burned-in (always visible, in the review `_tc` copy and the final) vs. a separate `.srt` only — user said "show everywhere", so burned-in; `.srt` also exported.
  3. Placement on S16/S17 full-screen demo clips (bottom band may cover UI) and the S19 billboard end card.
- Depends on the re-recorded takes 08/09: build subtitles AFTER the re-split so the timings match.

## Done 2026-10-10 (applied; not committed)
- Takes 08 + 09 replaced (assets/audio/vo_street_part2/takes + videos/livereview-launch/assets), re-split; `vo_street_part2.md`
  lines 8/9 updated (whisper confirmed the new wording). Part 2b is now 2257 frames (75.2 s; was 2159): S16 0-27.7 s, S17 27.7-47.4 s.
- Board: S16 title = "LiveReview helps your engineers **focus on what matters**" (pops on "engineers"); S17 item 2 =
  "Integrations: Microsoft Teams, Slack".
- Key-phrase captions removed from 2a and 2b (`OVER` is empty in 2a; only the end URL `hexmos.com/livereview` stays in 2b).
- Subtitles: `pipeline/subs.py` (cues from `build/<shot>_cues.json` `vo N` markers + `lines.json` word times; one phrase at a time,
  spoken word bold) burned in by `06_assemble.py` (street shots; `--no-subs` skips; no .srt). Works for joined shots:
  `06_assemble.py street_part_1_final street_part2_a street_part2_b --height 360 --music ...`.
- Renders (360p, in renders/): `street_part2_b_360p_mix(_tc).mp4`, `street_part2_a_360p_mix(_tc).mp4`, `street_part_1_final_360p_mix(_tc).mp4`
  (part 1's 360p = downscale of its 720p render), and the joined `street_part_1_final-street_part2_a-street_part2_b_360p_mix(_tc).mp4` (223.9 s).
  Old 2b frames: `build/frames/street_part2_b_360p_prev/`.
- Known cosmetics: the subtitle band can cover a board/UI at the bottom (e.g. S12 site-B sign); 2a's last 7 frames (2159-2165) are black (never rendered).

---

## Review round 3 (2026-10-10, user) — requirements; implement AFTER the subtitle preview is approved
Frame numbers below are in the JOINED video (part 1 = f1-2295, 2a starts f2296, 2b starts ~f4461): 2a frame = f - 2295; 2b frame = f - 4460.
1. **Subtitle area at the bottom (in progress):** reserve a strip at the bottom of the frame ONLY for subtitles (slightly smaller text than now);
   the video sits ABOVE it, nothing behind the text. Preview first on ~100 frames, then the whole video.
2. **S10 shops (2a), more sequencing** — "Ships without inspection" + "Inspects every change": (1) introduce the problem/question,
   (2) show some people going into the no-inspection shop, (3) show way more people going into the inspection shop,
   (4) only THEN the result/conclusion. Today the result is visible before the question is asked. (User can download more audio if needed.)
3. **S11 site A -> B (2a), f2960-f3137 joined (2a ~665-842):** zoom in a bit more on site A until f3110, then zoom out and move the camera to
   site B by f3137; NO zoom for site B (keep as is).
4. **Run to site C (2a):** after site B he must RUN to site C like he runs A -> B (today he isn't running). Also fix that run:
   he isn't using both legs, it looks like sliding.
5. **f3859 (2a ~1564):** voice says "more results" but the green banner says "more code" -> change the banner to "more results".
6. **S17 (2b) "Integrations help you work…":** remove the existing video there; use images instead:
   `videos/livereview-launch/assets/teams_integration.png` at 3:05-3:06 (1 s) then `slack_integration.png` at 3:06-3:08 (2 s) (joined timeline).
7. **f6437 (2b ~1976):** VO line 11 now says "risk aware AI code reviewer for your critical systems" (was "blast-radius aware") -> the user
   changed/will change the take; subtitle/caption text must follow the new wording (needs the new take: ask the user for it).
8. **f6531 (2b end):** show the livereview URL itself (hexmos.com/livereview) at that point; drop the separate billboard demo video and the
   separate link at the end.
