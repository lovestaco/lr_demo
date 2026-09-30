---
format: 1920x1080
duration: 210s
message: "LiveReview is the AI-assisted inspection layer that keeps your team in control while AI writes 10× more code."
arc: Opening (Livi intro) → The Problem → Feature Tour (5 acts) → CTA
audience: engineering-leadership
mode: autonomous
music: assets/bgm/bed-150.mp3 (looped 2x crossfade for 210s)
narration: none
captions: none
character: Livi — SVG owl mascot, cobalt accents, animated with GSAP
---

# LiveReview Mascot Demo — Shot Sheet

Silent film with text. **Every scene carries its own on-screen words.**
Livi (the owl mascot) guides the viewer through all features via speech bubbles.
Product demo clips appear in a dark app-window frame on the right half of the frame.

## Palette (all scenes)

- `bg` #080b12 — near-black background
- `cobalt` #1d56f0 — primary accent (Livi eyes, buttons, highlighted text)
- `cobalt-mid` #4d7cff — secondary accent
- `text` #e8eeff — near-white
- `text-muted` #7a8cb3 — secondary text
- `green` #10b981 — success/pass
- `red` #dc2626 — alert/fail
- `card` #0e1622 — card / app-window body
- `border` #1a2440 — subtle borders

## Typography

Inter variable (`assets/fonts/Inter-var.woff2`). Roles:
- H1: 72px 800 weight, `text` color, −0.02em tracking
- H2: 48px 700 weight
- Eyebrow: 13px 600 UPPERCASE 0.12em tracking, `cobalt`
- Body / bubble: 22px 400
- CTA pill: 18px 700 UPPERCASE, cobalt bg, white text

## Livi — Character design

Livi is a flat-design owl built as inline SVG:
- Round warm-white body (#F5F0E8)
- Round head on top, same cream color
- Large cobalt (#1d56f0) eye irises, black pupils, white glint
- Small amber beak (#E8A020)
- Dark blue-grey (#1a2b4e) wing tips and ear tufts
- Cobalt chest pattern (three wavy horizontal lines, thin)
- Soft drop shadow under body

Poses (animated via GSAP class-swap + GSAP timeline):
1. **neutral** — standing, facing forward, slight head sway (idle loop)
2. **pointing** — body rotated 10°, right wing extended toward screen
3. **surprised** — eyes wide (scale up), lean back, feathers raised
4. **happy** — eyes curved (squinting), wings slightly up, subtle bounce
5. **cta** — wings fully open (spread wide), slight forward lean

Speech bubble: white rounded-rect (#ffffff), cobalt border 2px, dark text #1a1a2e, 16px Inter.
Bubble tail points toward Livi's beak.

## Scene 01 — Opening (0–12s · 12s)
**File:** compositions/scene-01-opening.html

Layout: Full-bleed dark background. Livi enters from left edge (slide in + pop), logo fades in top-right, speech bubble appears.

| Time (s) | Action |
|-----------|--------|
| 0–2 | Logo fade in top-right corner |
| 0–3 | Livi slides in from left (cubic ease) |
| 3–12 | Livi idle sway · speech bubble: "Hey! I'm Livi — your AI review companion from LiveReview." |

Copy:
- Eyebrow: MEET LIVI
- Bubble: "Hey! I'm Livi — your AI review companion from LiveReview."

---

## Scene 02 — The Problem (12–38s · 26s)
**File:** compositions/scene-02-problem.html

Layout: Livi on left (surprised pose). Right side: animated counter showing PR count exploding.

| Time (s) | Action |
|-----------|--------|
| 0–4 | Eyebrow fades in: THE PROBLEM |
| 2–5 | Livi switches to surprised pose |
| 3–10 | H1 "AI writes code 10× faster." fades word by word |
| 5–12 | PR counter animates: 4 → 12 → 31 → 47 PRs (count-up) |
| 10–20 | Body copy: "But your reviewers? Still just you." |
| 15–26 | Second stat: "10× more PRs. Same reviewers." — counter at 47 glows red |

Copy:
- Eyebrow: THE PROBLEM
- H1: "AI writes code 10× faster."
- Stat: 47 OPEN PRS → glows red
- Body: "But your reviewers? Still just you."
- Bubble (Livi): "Something had to give."

---

## Scene 03 — Blast Radius (38–68s · 30s)
**File:** compositions/scene-03-blast.html

Layout: Livi (pointing) on left 35%. App window frame + clip05_blast.mp4 on right 55%.

| Time (s) | Action |
|-----------|--------|
| 0–3 | Eyebrow: BLAST RADIUS ANALYSIS |
| 2–5 | Livi switches to pointing pose |
| 3–8 | H2 "Which PRs could actually break prod?" fades in |
| 4–30 | clip05_blast.mp4 plays in app window (loops if shorter than 26s) |
| 8–25 | Bubble: "I rank every change by blast radius — so reviewers focus where it matters." |
| 25–30 | Green pill: "→ Problem #1 solved: ATTENTION" |

Product clip: assets/clips/clip05_blast.mp4

---

## Scene 04 — PR Quiz (68–95s · 27s)
**File:** compositions/scene-04-quiz.html

Layout: Livi (surprised then happy) on left. App window + clip11_quiz.mp4 on right.

| Time (s) | Action |
|-----------|--------|
| 0–3 | Eyebrow: PR READBACK QUIZ |
| 2–5 | Livi surprised pose |
| 3–8 | H2 "Does your reviewer actually understand this diff?" |
| 5–22 | clip11_quiz.mp4 plays in app window |
| 8–20 | Bubble: "Like air traffic control readback — confirm you heard what was really changed." |
| 20–27 | Livi → happy pose · green pill: "→ Problem #2 solved: UNDERSTANDING" |

Product clip: assets/clips/clip11_quiz.mp4

---

## Scene 05 — CI/CD Gates (95–125s · 30s)
**File:** compositions/scene-05-cicd.html

Layout: Livi (pointing) on left. On right: animated gate chain + app window with clip10_cicd.mp4.

| Time (s) | Action |
|-----------|--------|
| 0–3 | Eyebrow: AUTOMATED ENFORCEMENT |
| 2–6 | H2 "Every gate, automated. Nothing slips through." |
| 3–18 | Gate chain animates in sequence: Lint ✓ → Unit ✓ → Coverage ✓ → Security ✓ → Deploy ✓ |
| 8–28 | clip10_cicd.mp4 plays in app window |
| 15–27 | Bubble: "Set your checkpoints. I enforce them at every commit, push, and PR." |
| 27–30 | Green pill: "→ Problem #3 solved: ENFORCEMENT" |

Product clip: assets/clips/clip10_cicd.mp4

---

## Scene 06 — Model Freedom (125–148s · 23s)
**File:** compositions/scene-06-models.html

Layout: Livi (happy) centered-left. Right: 2×2 grid of brand logos (Claude, GPT-4o, Gemini, DeepSeek) with animated "connecting" lines.

| Time (s) | Action |
|-----------|--------|
| 0–3 | Eyebrow: YOUR MODEL, YOUR CHOICE |
| 2–6 | H2 "No vendor lock-in. Ever." |
| 5–18 | Brand logos stagger in: Claude · GPT-4o · Gemini · DeepSeek |
| 8–20 | Bubble: "Your team picks the AI model. Claude, GPT-4o, Gemini, DeepSeek — or host your own." |
| 18–23 | Green pill: "→ Problem #4 solved: CONTROL & IMPROVE" |

Logos: assets/logos/brand-claude.svg, brand-openai.svg, brand-gemini.svg, brand-deepseek.svg

---

## Scene 07 — Livi Chat (148–170s · 22s)
**File:** compositions/scene-07-livi-chat.html

Layout: Livi (happy/waving) on left. App window + clip15_livi.mp4 on right.

| Time (s) | Action |
|-----------|--------|
| 0–3 | Eyebrow: ASK LIVI ANYTHING |
| 2–6 | H2 "Questions about the codebase? Just ask." |
| 4–20 | clip15_livi.mp4 plays in app window |
| 6–20 | Bubble: "I can explain any function, trace a data flow, or tell you why a change is risky." |
| 20–22 | Livi tips wings forward |

Product clip: assets/clips/clip15_livi.mp4

---

## Scene 08 — Dashboard (170–190s · 20s)
**File:** compositions/scene-08-dashboard.html

Layout: Livi (happy, clipboard) on left. App window + clip13_dashboard.mp4 on right.

| Time (s) | Action |
|-----------|--------|
| 0–3 | Eyebrow: TEAM ANALYTICS |
| 2–6 | H2 "Track your team's review quality over time." |
| 4–18 | clip13_dashboard.mp4 plays in app window |
| 6–18 | Bubble: "Review quality, coverage trends, and blast radius scores — all in one place." |
| 18–20 | Livi nods |

Product clip: assets/clips/clip13_dashboard.mp4

---

## Scene 09 — CTA (190–210s · 20s)
**File:** compositions/scene-09-cta.html

Layout: Livi CTA pose centered. Logo. Big headline. URL. No product clip.

| Time (s) | Action |
|-----------|--------|
| 0–4 | Livi CTA pose fades in, wings spread |
| 3–8 | H1 "LiveReview." fades in + cobalt underline sweeps |
| 6–12 | H2 "The inspection layer your team deserves." |
| 9–15 | Logo + URL pill: hexmos.com/livereview |
| 10–20 | Livi idle sway (welcoming) |

---

## Build notes

- Livi SVG is defined once in `compositions/_livi.svg` and included in each scene via JS
- GSAP CDN replaced with local (no external requests allowed in HyperFrames)
  → copy gsap.min.js to assets/js/gsap.min.js
- Each scene is standalone and correct at t=0 (for thumbnail/seek)
- Scene transitions in index.html use data-start / data-duration attributes
- Music: bed-150.mp3 looped twice with 2s crossfade at 150s mark
