---
workflow: product-launch-video
flow: automation
storyboard: yes
message: "You already generate code with AI — LiveReview is the AI-assisted inspection layer you owe your users."
destination: youtube
aspect: 1920x1080
language: en
audience: engineering-leadership
length: 150s
angle: problem-solution
narration: no
music: bed-only
captions: no
style_preset: blue-professional
---

## Intent

A new LiveReview launch film whose story spine is the **51-slide "LiveReview
Presentation" deck** (extracted verbatim to `../../ppt/LiveReview-Presentation-slides.md`).

That deck is a rhetorical build, not a feature tour: it opens on a gap the viewer
already feels (you do a lot of AI code *generation* — do you do enough AI code
*inspection*?), argues the belief, establishes why velocity and volume make it
urgent, names **four problems**, then answers each one with the real product.

Spine, in deck order:

1. **Hook** (slides 1–2) — "You already do a lot of… AI-Assisted code generation."
   → "But do you do enough of… AI-Assisted Code Inspection?"
2. **Belief** (3–6) — you owe your users, your professionalism and your reputation
   an **AI-assisted inspection layer**.
3. **Why** (7–19) — code accumulates at great VELOCITY → HUGE VOLUME → and you
   still must reduce production incidents, security incidents, performance
   regressions, and deliver stellar customer experiences → but **human attention
   is still limited** → more code means bigger systems, more complexity.
4. **The four problems** (20–25) — #1 ATTENTION · #2 UNDERSTANDING ·
   #3 ENFORCEMENT · #4 CONTROL and IMPROVE.
5. **The answers** (26–46) — each problem stated in the deck's words, answered by
   LiveReview, proven with real product footage, and sealed with "→ Solved":
   - Attention → ranks every hunk by blast radius and review priority.
   - Understanding → summaries, issue navigation, PR quizzes keep humans in the loop.
   - Enforcement → reviews at commit, push, PR, CI/CD and on schedule.
   - Control & Improve → your infrastructure, your choice of model; Adaptive
     Reviews cut AI cost; Livi learns; CLI, IDE, MCP and API fit your workflow.
6. **Close** (47–51) — "A FULL BLOWN AI-ASSISTED CODE INSPECTION LAYER" → the only
   platform that solves all four in one unified system → four ✅ → hexmos.com/livereview.

Tone: confident, engineering-serious, business-literate. Engineering leadership
first, developers second. The film must read from visuals alone (music only, no VO),
so **every frame carries its own on-screen words**, taken from the deck.

## Assets

- ../../ppt/LiveReview-Presentation-slides.md — the story spine and on-screen copy (51 slides).
- assets/clip05_blast.mp4 (8s) — blast-radius scoring in the diff → the Attention answer.
- assets/clip11_slides.mp4 (5.3s) — 60-second summary deck → the Understanding answer.
- assets/clip11_quiz.mp4 (2.7s) — quiz on the diff → the Understanding answer.
- assets/clip08_schedule.mp4 (4s) — scheduled reviews → the Enforcement answer.
- assets/clip10_cicd.mp4 (6.7s) — CI/CD gate ruleset → the Enforcement answer.
- assets/clip15_livi.mp4 (8.1s) — Livi chatbot → the Control & Improve answer.
- assets/clip14_nav.mp4 (7.1s) — Ctrl+K navigation across the product → interfaces.
- assets/clip13_dashboard.mp4 (7.1s) + assets/clip16_report.mp4 (8.6s) — closing montage.
- assets/bgm/bed-150.mp3 (150.0s) — the music bed; the cut is built to its exact length.
- assets/ — kept brand kit: logo.svg, Livi avatar, git-provider logos, AI-provider logos,
  IDE logos, chat-platform logos, Inter font, risk-score screenshots, SFX library.
- frame.md — kept Blue Professional design system, already brand-remixed. Step 2 is done.

## Customizations

- Music bed only: `assets/bgm/bed-150.mp3`. No SFX, no VO, no captions.
- **The cut is exactly 150.000s** so the bed fits end to end with no loop seam —
  frame durations are budgeted to that total.
- Demo clips are 2520x1080 (21:9). Show them whole inside a framed dark app window on
  the 16:9 canvas — `object-fit: contain`, never crop product UI.
- The four problems are the film's skeleton: each act runs problem → answer →
  footage → "→ Solved", and the four ✅ recap at the close pays off all of them.
- Keep the existing icons, logos and design language (frame.md, Blue Professional).

## Notes

- Mid-run the user asked to finish without further checkpoints and deliver the rendered MP4
  ("just render the video and get me the end video"). `STORYBOARD.md` mode is therefore
  `autonomous`; the confirmed `flow`/`storyboard` fields are unchanged.

- The previous cut's story (the v4 deck: blast radius → review depth → three problems
  Capability/Control/Cost) was replaced on purpose. Its frames under
  `compositions/frames/` are disposable — the user confirmed the old video can go.
  The brand kit in `assets/` is kept.
- Pricing facts (site): free 30k LOC/month; paid from $32 for 100k LOC; users unlimited.
- Adaptive Reviews: Leader + Helper models cut AI inference cost 40–50%.
- Impact / onboarding report: 57 charts across 7 sections, one click, PDF/HTML export.
- Deck slides 23/24, 35/36 and 40/41 are build-up variants of the same line; each pair
  collapses into a single beat.
