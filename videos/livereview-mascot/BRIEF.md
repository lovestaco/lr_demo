---
workflow: general-video
flow: automation
storyboard: yes
message: "LiveReview is the AI-assisted inspection layer that keeps your team in control while AI writes 10× more code."
destination: youtube
aspect: 1920x1080
language: en
audience: engineering-leadership
length: 210s
angle: mascot-guided-tour
narration: no
music: bed-only
captions: no
style_preset: dark-cobalt
---

## Intent

A 3.5-minute product demo video for LiveReview (hexmos.com/livereview) guided by Livi — a
friendly animated owl who is also LiveReview's AI chat assistant persona. Livi appears
on-screen throughout, gesturing to product demos, expressing reactions, and speaking via
text bubbles (no VO). The mascot makes the product feel approachable and alive, not just
a slide deck.

The story arc is a guided tour: Livi introduces herself, explains the problem (more AI code
generation = more PRs, same limited human attention), then walks through each major feature
one by one, capping with the CTA. Target: CTOs, VPs Engineering, EMs who are already using
AI coding tools and wondering "how do we keep up with the review burden?"

Tone: friendly, confident, playful-but-sharp. Not enterprise-dry. Livi is knowledgeable
and a little wry. The video should feel like a product you *want* to use.

## Assets

- videos/livereview-launch/assets/clip05_blast.mp4 — blast radius demo (8s)
- videos/livereview-launch/assets/clip11_quiz.mp4 — PR quiz / readback demo (2.7s)
- videos/livereview-launch/assets/clip10_cicd.mp4 — CI/CD gates demo
- videos/livereview-launch/assets/clip15_livi.mp4 — Livi chat bot demo
- videos/livereview-launch/assets/clip13_dashboard.mp4 — dashboard & analytics
- videos/livereview-launch/assets/clip08_schedule.mp4 — scheduled review demo
- videos/livereview-launch/assets/clip16_report.mp4 — reports
- videos/livereview-launch/assets/clip11_slides.mp4 — summary slides
- videos/livereview-launch/assets/logo.svg — LiveReview logo
- videos/livereview-launch/assets/brand-claude.svg — Claude brand mark
- videos/livereview-launch/assets/brand-gemini.svg — Gemini brand mark
- videos/livereview-launch/assets/brand-openai.svg — OpenAI brand mark
- videos/livereview-launch/assets/brand-deepseek.svg — DeepSeek brand mark
- videos/livereview-launch/assets/bgm/bed-150.mp3 — music bed (loops for 210s)
- videos/livereview-launch/assets/fonts/Inter-var.woff2 — Inter variable font
- videos/livereview-mascot/blender/renders/ — Livi pose renders (PNG sequences, transparent)

## Scene breakdown

### Scene 01 — Opening (0–12s)
Livi enters from the left, waves. Speech bubble: "Hey! I'm Livi — your AI review
companion from LiveReview." Logo fades in. Background: #080b12.

### Scene 02 — The Problem (12–38s)
Livi looks concerned. PRs multiply on screen (animated counter). Speech bubble:
"AI writes code 10× faster. But your reviewers? Still just you."

### Scene 03 — Blast Radius (38–68s)
Livi points right → product clip plays in app window frame.
Speech bubble: "I rank every change by blast radius — which PRs could actually break prod?"
clip05_blast.mp4 featured.

### Scene 04 — PR Quiz (68–95s)
Livi looks surprised/inquisitive. Speech bubble:
"Does your reviewer actually understand what they're approving?" 
clip11_quiz.mp4 featured.

### Scene 05 — CI/CD Enforcement (95–125s)
Livi is in "enforcer" pose. Animated gate chain: Lint → Unit → Coverage → Security → Deploy.
Speech bubble: "Every gate, automated. Nothing slips through."
clip10_cicd.mp4 featured.

### Scene 06 — Model Freedom (125–148s)
Livi gestures to brand logos (Claude, GPT-4o, Gemini, DeepSeek).
Speech bubble: "Your team picks the model. No vendor lock-in, ever."

### Scene 07 — Livi Chat (148–170s)
Livi waves enthusiastically. Speech bubble: "Ask me anything about the codebase — right inside your review."
clip15_livi.mp4 featured.

### Scene 08 — Dashboard (170–190s)
Livi holds a clipboard, looks pleased. Speech bubble: "And track how your team's review quality improves over time."
clip13_dashboard.mp4 featured.

### Scene 09 — CTA Close (190–210s)
Livi in welcoming/CTA pose, arms open. Big headline: "LiveReview."
Subline: "The inspection layer your team deserves."
URL: hexmos.com/livereview

## Customizations

- Livi owl character built in Blender Grease Pencil, rendered as transparent-bg PNG sequences
- Each Livi pose is a short render sequence used as a video element in HyperFrames
- Product clips shown inside a dark app window frame (1920x1080 outer, #0e1322 body)
- Text bubbles: rounded white pill on dark bg, Inter font, #e8eeff text
- Livi occupies left 35% of frame when paired with product clip (right 55%)
- Color palette: bg #080b12, cobalt #1d56f0, text #e8eeff, secondary #4d7cff, green #10b981, red #dc2626
- BGM loops at reduced volume under the whole video

## Notes

- Blender version: 5.2.2 LTS with Eevee renderer (GTX 1650, 4GB VRAM)
- Livi render resolution: 960x1080 (portrait, 1:1 for Livi's half of frame)
- Render output: PNG sequence with RGBA, saved to blender/renders/<pose>/
- HyperFrames composes Livi + product clips + typography on dark background
- Music bed: bed-150.mp3 (150s) — play twice with crossfade for 210s total
- DO NOT touch videos/livereview-launch/ (render in progress, PID 975039)
