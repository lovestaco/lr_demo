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

## Code changes still to make (not started)
1. `05b_street_part2_boards.py`
   - S16 clips → `blast_radius_zoom.mp4`, `slide_deck.gif`, `quiz.gif`, `converse_in_mr.png`, `demo_livi_chat_bot.mp4`.
   - S17 item a text → "CI/CD Gates: Precise, Customized Merge Enforcement"; clip `demo_cicd_gates.mp4` (full 4 s).
   - S17 item b → show `teams.png` (2 s) then `slack.png` (2 s).
   - S17 item c → drop the MCP clip; render the MCP sentence as styled text.
   - Add the LiveReview wordmark to the board's top-left blue box.
   - Support still images (`.png`) and GIF→MP4 in `clip_frames` (it currently assumes video via ffmpeg).
2. `04_street_part2.py`
   - `s16_items` / `s17_items`: pop words `w8("livi")` → the take spells **"Livy"**; `w9("rules")` no longer
     exists (line is now "CI/CD gates") → use `w9("gates")` (or `w9("ci")`).
   - Move the board timing from word-driven to the requested fixed durations (12/5/3/2/3 and 4/4/5), or re-read.
   - Update the line-11 caption that still says "the most efficient way…".
3. `pipeline/streetkit.py`
   - Add `"livi": "livy"` to `ALIAS` (Whisper spells it "Livy").

## Source prep still to do
- Convert `slide_deck.gif` and `quiz.gif` to MP4 (16:9, e.g. 800×450) to fill the demo box.
- Trim `demo_livi_chat_bot.mp4` to its 2 s–5 s section.
- `blast_radius_zoom.mp4` (3:2) and the GIFs (~1.16:1) are not 16:9 → they letterbox in the 800×450 box;
  crop/re-render to 16:9 for a clean fill.
