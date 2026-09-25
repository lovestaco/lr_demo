# Source footage map — `Ws66OKXUwwE.mp4`

105.03s · 2520x1080 container · 30fps · AAC stereo (music bed, no narration — 30s of it
transcribes to 4 words). Dark product UI throughout.

## Geometry — verified, use these numbers

- The container is **pillarboxed**: pure black bars either side. Real content is
  **x = 164 … 2355, i.e. 2192x1080** (`cropdetect` agrees across the whole runtime).
- The original's burned-in captions occupy roughly **y = 840 … 1040**, left-aligned from
  x ≈ 105 within the content region. They are large — several run to two lines.
- **`crop=2192:830:164:0` removes the pillarbox and the captions in one pass.** Verified
  visually at four points in the film; output is 2192x830 (2.64:1), which mounts cleanly as a
  wide UI card inside a 1920x1080 frame. For a fuller card, take a 16:9 window out of that
  region (1476x830) instead.

## Segment map — 3s intervals, linear decode

Earlier versions of this file were sampled with fast seek (`-ss` before `-i`), which lands on
keyframes and mislabelled several segments. These timecodes come from a linear decode and are
reliable to ±1.5s.

| Time | On screen | Pillar |
| --- | --- | --- |
| 0–5s | Dashboard — Review Pipeline sankey | Review |
| 3–5s | Issue Distribution treemap | Review |
| 6–8s | Stage Volume Comparison — pre-commit 177 · MR/PR 3 · API/MCP 5 | Review |
| 9–11s | Contribution Activity heatmap + Recent Activity | Improve |
| 12–14s | Command palette — Reviews / Explore / Providers / Reports | Connect |
| 15–17s | Summary Deck — "Restrict JSON Fallback Decoding…" slide | Understand |
| 18–20s | **"Review complete — you finished all 7 slides · Take the Quiz"** | Understand |
| 21–23s | Inline code diff with findings | Review |
| **24–26s** | **RISK SCORE — "71 High risk", Blast Radius 51, Review Priority 100, with cyclomatic complexity / cognitive complexity / test coverage factors** | **HOW** |
| 30–32s | Scheduled Reviews — repo table, cadence toggles | Enforce |
| 33–38s | **CI/CD Gates — "Edit ruleset: High-confidence critical issues", live jq expression** | Enforce |
| 39–41s | Chat with Livi — generating | Improve |
| 42–44s | Daily Review Activity chart | Improve |
| 45–50s | Livi answer — Engineer Adoption Levels bar chart | Improve |
| 54–56s | **Providers → Connect Git — GitHub, GitLab.com, self-hosted GitLab, Bitbucket** | Connect |
| 57–65s | Settings — Manage Team, Invite User, Customize AI, Manage API Access, Integrations | Connect |
| 66–68s | Reports menu — findings by severity, download report | Improve |
| **69–71s** | **Headline stats — 2,271 findings · 366 CRITICAL · 1,395 WARNINGS · 510 INFO** | Improve |
| 72–74s | By Severity + By Category/Subcategory bars | Improve |
| 75–77s | Onboarding Report generating | Improve |
| 78–89s | Cumulative LOC trend · adoption breadth · LOC by engineer · top repos | Improve |
| **90–92s** | **"Onboarding report generated successfully! 57 charts across 7 sections"** | Improve |
| 93–101s | Median review duration · top repos by LOC · trigger-type donut | Improve |
| **102–105s** | **"hexmos.co" end card on black** | — |

## Corrections to earlier assumptions

1. **Blast-radius footage DOES exist**, at ~24–26s: the risk score panel with its numeric
   breakdown. An earlier pass claimed this footage was absent and that the whole HOW section had
   to come from the landing-page demo. Wrong — the user's own cut can carry part of it, with the
   landing-page demo supplying the sunburst and Math Mode that this recording never shows.
2. **The cut does not end cold.** There is a "hexmos.co" end card at ~102s.
3. The film is still Improve-heavy — roughly 45s of 105s is reports and analytics — so the
   pillar beats must still pull segments out of order rather than follow the tape.
