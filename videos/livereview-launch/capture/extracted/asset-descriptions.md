# Asset inventory

Rebuilt 2026-09-25 for the v4-deck cut. The previous cut's story-only assets (Rickover portrait,
horse hero images, role comic) remain on disk but are **not** part of this story — do not use them.

Paths are relative to `capture/assets/` unless they start with `assets/` (brand kit already staged
in the project's `assets/`).

## Product demo clips — the new footage (primary)

All are 2520x1080 (21:9), 30fps, dark-theme LiveReview UI, with a thin blue/orange glow on the
outer edges. Show them whole inside a framed app window on the 16:9 canvas; never crop the UI.
Audio tracks are present but unused (music bed only).

| File | Dur | What it shows | Deck slide |
| --- | --- | --- | --- |
| `demo_review_blast_radius.mp4` | 4s | Review diff ordered by score → hover a hunk: "71 High risk" popover with Blast Radius / Review Priority bars and factors (cyclomatic, cognitive, test coverage, fan-out) → breakdown panel with the red sunburst call-graph chart. | 3 |
| `demo_schedule_review.mp4` | 2s | Ctrl+K menu → "Schedule Review" → Scheduled Reviews table: repos, provider, branch, per-repo toggle, schedule, last run. | 4–5 |
| `demo_cicd_gates.mp4` | 4s | CI/CD Gates ruleset list → "Edit ruleset: High-confidence critical issues" → jq expression `[.findings[] \| select(.severity == "critical" and .confidence == "high")] \| length > 0` highlighted, presets row, live results. | 6 |
| `demo_review_slides.mp4` | 4s | Summary deck zooms in from 3D perspective → title slide "Restrict JSON Fallback Decoding and Update Cron Schedule Helpers" → red "Technical highlights" slide → "Review complete" with "Take the Quiz". | 7 |
| `demo_review_quiz.mp4` | 2s | Quiz on the diff: multiple-choice questions about the change, "Check My Answers". | 7 |
| `demo_list_reviews.mp4` | 2s | Ctrl+K → List Reviews → loading → table of reviews (branch, repo, source GitHub/CLI, status Completed, author). | 9 |
| `demo_dashboard.mp4` | 10s | Dashboard: review pipeline Sankey (pre-commit → categories) → issue-distribution treemap → radar of categories (Security, Reliability, Correctness…) with counts → contribution heatmap + recent activity. | 9 |
| `demo_all_features_navigation.mp4` | 10s | Ctrl+K command palette: Reviews / Explore / Providers / Reports / Settings columns; drills into Git Providers → Connect Git (GitHub, GitLab, Bitbucket, Gitea, Azure DevOps); Settings → Manage Team / AI / Billing. | 10 |
| `demo_livi_chat_bot.mp4` | 11s | "Hello there! How can I help you?" with suggested questions → user asks "Are engineers actually incorporating reviews into their daily workflow?" → Livi answers with a Daily Review Activity chart → Engineer Adoption Levels bar chart. | 11 |
| `demo_onboarding_report.mp4` | 15s | Onboarding Report generating (7 sections progress) → Engineer Review Activity Distribution bars → repository trend lines + Pareto → Top Engineers by Reviews. | 12 |

## Supporting product media (kept from the site)

| File | What it is | Use |
| --- | --- | --- |
| `risk-score_risk-score-demo-compressed.mp4` | 1600x758, 51.3s. Blast-radius UI: diff with findings (0-10s), factor panels (~14s, ~35s), sunburst chart (~21s), Math Mode formulas (~42s). | Extra blast-radius footage — Math Mode for "the exact math". |
| `risk-score_new-risk-score-3.webp` | Math Mode: score broken down step by step. | "The exact math, not a black box." |
| `risk-score_new-risk-score-4.webp` | Sunburst chart of a function's blast radius across the call graph. | "Visualize blast radius at a glance." |
| `risk-score_new-risk-score-2.webp` | Every factor feeding Blast Radius + Review Priority. | "Every factor that feeds the score." |
| `git-lrc_summary-deck-compressed.mp4` | 1280x1008, 15.9s. Summary deck walkthrough. | Backup for the briefing beat. |
| `quiz-coverage_quiz-coverage-demo-compressed.mp4` | 1280x718, 19.7s. PR quiz mode. | Backup for the quiz beat. |
| `git-lrc_issue-navigator-compressed.mp4` | 1280x840, 20.6s. Issue Navigator. | Optional. |
| `features_detailed_mr_summaries.png` | AI-generated PR summary screen. | "Ready to copy-paste PR summary." |

## Brand kit (icons & logos)

| File | What it is | Use |
| --- | --- | --- |
| `logo.svg` | LiveReview mark. | Wordmark lockups, the close. |
| `lrbot_lrbot.png` | Livi avatar. | Livi beat. |
| `version_control_logos_github-logo-dark.png`, `…gitlab-logo.png`, `…bitbucket-logo.png`, `…azure-devops-logo.png`, `…gitea_logo.png` | Git provider logos. | "Fits your workflow" / self-host beat. |
| `extensions_vscode-logo.png`, `extensions_cursor-logo.png`, `extensions_antigravity-logo.png` | IDE logos. | "CLI, IDE, MCP and API fit your workflow." |
| `assets/brand-claude.svg`, `assets/brand-openai.svg`, `assets/brand-gemini.svg`, `assets/brand-anthropic.svg`, `assets/brand-copilot.svg`, `assets/brand-deepseek.svg`, `assets/brand-openrouter.svg` | AI provider marks. | "Choose which AI models inspect it" / AI writes the code. |
| `assets/brand-slack.svg`, `assets/brand-teams.svg`, `assets/brand-discord.svg` | Chat platform marks. | Optional, Livi "where your team talks". |
| `assets/fonts/Inter-var.woff2` | Inter variable font. | All type. |
| `assets/bgm/track.loop.mp3` | Kept BGM loop. | The music bed. |

## Not captured — build these

- The 300-line vs 3-line contrast (deck slide 1) — a designed beat.
- "AI writes code far faster than your team can review it" — a designed volume/pressure beat.
- The four review-depth tiers (slide 5) and the five checkpoints (slide 4) — designed.
- Pricing / self-host beat (slide 8) — designed with logos.
- "Three problems. One reviewer." Capability · Control · Cost close (slide 13) — designed.
