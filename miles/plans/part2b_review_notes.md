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
- Built `build/street_part2.blend`. Overlays: `end 4353`; s16 `[2195,2966]` items `[2316,2616,2731,2801,2865]`;
  s17 `[2967,3516]` items `[3119,3248,3348]`. No `OCCLUDED`, no path hits.

## Open questions / notes
- **Integrations video:** no integrations-specific clip exists, so item b uses `demo_schedule_review.mp4`
  (the previous mapping) — confirm, or supply a better clip.
- `teams_integration.png` / `slack_integration.png` (supplied earlier) are currently **unused**.
- The full-screen brand pill can overlap a demo UI's own header (cosmetic).
- Media is cover-cropped to 16:9 (no letterbox), so `blast_radius_zoom.mp4` (3:2) loses top/bottom.

## To finish (when asked)
Render the 3D range skipping S16/S17 → `05b_street_part2_boards.py <frames> ` (boards) →
`06c_street_part2_post.py` (captions) → `06_assemble.py street_part2 --height 720 --music …`.
