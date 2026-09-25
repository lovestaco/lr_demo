# Asset inventory

Assembled on the **no-capture path**. `hyperframes capture` hung on
https://hexmos.com/livereview/ (~15 min, zero bytes written, no BLOCKED.md) while a
direct fetch of the same origin returned 47KB in 0.49s — the crawler stalled, the
network did not. The brief supplied the page text up front (three full scrapes the user
placed in the working directory), so the source material is first-party, not reconstructed.
Every file below was fetched directly from hexmos.com and verified (HTTP 200, non-trivial size).
Brand tokens in `tokens.json` were read out of the site's own stylesheets and markup.

All paths are relative to `capture/assets/`.

## Story assets — WHY

| File | What it is | Use |
| --- | --- | --- |
| `transform_role-benefits-comic.png` | 1480x704. Illustrated 7-role before/after grid. Each role gets a PAIN panel (worried figure + speech bubble) and an AFTER panel. Roles: Business Leadership (CEO, head in hands, production server on fire), CTO/VP Eng ("AI is making us faster. Is it also making us sloppier?"), Engineering Manager, Product Manager, Project Manager, Team/Tech Lead, Developer ("Why didn't I know this before opening the PR?"). | The WHY section's visual vocabulary. **Resolution limit: a single cropped panel is only ~350x200 — usable as a card/inset, never full-bleed.** |
| `hero_wild-horse.webp` | 121KB. Wild, untamed horse — the site's "AI Speed / raw power, uncontrolled behavior" image. | The WHY metaphor: AI generating code unchecked. |
| `hero_domesticated-horse.webp` | 72KB. Bridled horse under human control — "Human Control / guided, focused, reliable". | Pairs with the above for the before/after turn into WHAT. |

## Story assets — WHAT

| File | What it is | Use |
| --- | --- | --- |
| `rickover_rickover-portrait.jpg` | 164KB. Portrait of Admiral Hyman G. Rickover, U.S. Navy. | The anchor quote beat: "You get what you inspect, not what you expect." |
| `logo.svg` | 895B. LiveReview wordmark/mark. | Product intro and the close. |
| `transform_ai-logos_deepseek-logo.svg`, `transform_ai-logos_openrouter-logo.svg` | AI provider marks. | The "sits above your AI stack" beat. Claude / OpenAI / Gemini are wordmarks on the page, not files — set them as type. |

## Story assets — HOW (blast radius)

**The existing MP4 contains no blast-radius footage.** These are the only sources for the
video's largest section.

| File | What it is | Use |
| --- | --- | --- |
| `risk-score_risk-score-demo-compressed.mp4` | **1600x758, 51.3s.** The blast-radius UI running. Beats: code diff with severity findings (0-10s), Blast Radius + Review Priority factor panels (~14s, ~35s), **the sunburst call-graph chart, orange-to-red rings (~21s)**, stacked risk visualization (~28s), **Math Mode showing the exact formulas (~42s)**. | Hero footage for HOW. The sunburst and Math Mode are the two money shots. |
| `risk-score_new-risk-score-3.webp` | 48KB. Blast Radius and Review Priority scores broken down step by step in Math Mode. | "The exact math, not a black box." |
| `risk-score_new-risk-score-4.webp` | 57KB. Sunburst chart visualizing a function's blast radius across the call graph. | "Visualize blast radius at a glance." |
| `risk-score_new-risk-score-2.webp` | 54KB. Full breakdown of every factor feeding both scores. | "Every factor that feeds the score." |

## Story assets — WHEN/WHERE (the five pillars)

| File | What it is | Pillar |
| --- | --- | --- |
| `git-lrc_summary-deck-compressed.mp4` | 1280x1008, 15.9s. Summary Deck — a generated slide walkthrough of a change. | Understand |
| `git-lrc_issue-navigator-compressed.mp4` | 1280x840, 20.6s. Issue Navigator — filter findings by severity/category, send to an agent. | Understand |
| `quiz-coverage_quiz-coverage-demo-compressed.mp4` | 1280x718, 19.7s. PR Quiz / Cognitive Coverage mode. | Understand |
| `features_detailed_mr_summaries.png` | 135KB. AI-generated pull request summary screen. | Understand |
| `features_clarification_question.png` | 56KB. Asking the AI for clarification / debating a change. | Understand |
| `lrbot_lrbot.png` | 23KB. Livi, the analytics chatbot avatar. | Improve |
| `version_control_logos_*.png` | GitHub (dark), GitLab, Bitbucket, Azure DevOps, Gitea. 5 files. | Connect |
| `extensions_*.png` | VS Code, Cursor, Antigravity. 3 files. | Connect |

## Not captured — build these, don't hunt for them

- **The five-pillar cycle graph.** Review -> Understand -> Enforce -> Improve -> Connect with the
  Improve->Review return edge. The site renders it as a nav list and five prose cards, not as a
  graph. This is a designed beat.
- **The 300-vs-3 blast-radius contrast.** On the site it is a two-cell HTML table. It gets its
  own built moment, per the brief.
- **The AI-code-volume before/after curves.** Site-rendered charts, no image file.
- **Product UI screens for Review / Enforce / Improve / Connect** — these come from the user's
  own `Ws66OKXUwwE.mp4`; see `../../footage-map.md` for the timecode-to-pillar map.
