# LiveReview — "Separation"
## Treatment v1 · Air Traffic Control

**Format** 1920x1080 · **Length** 150.000s (fits `assets/bgm/bed-150.mp3` end to end, no loop seam)
**Sound** music bed + one SFX voice (radio click). No VO, no captions.
**Reads from visuals alone** — every frame carries its own on-screen words.

---

## 1. The idea in one line

> The thing that used to be scarce became free. The thing that was always
> scarce did not move.

Code changes are aircraft. AI made aircraft free to build. It did not build
more controllers. One tower, one scope, traffic that will not stop growing.

**The film is not about stopping traffic. It is about separating it.**
By the last frame the scope is *fuller* than the first — and every aircraft is
labelled, spaced and clear. That protects the hook: AI code generation is good.
You want more of it. You just need a tower.

---

## 2. Rules of the world

These are what make a metaphor feel authored instead of decorative. Break them
and the film reads as clip art.

1. **We never show the crash.** No collision, no fireball, no near-miss siren.
   The drama is *separation* — the quiet competence of nothing happening.
   Anything else is fearmongering, and this audience can smell it.
2. **The sweep is the clock.** A cobalt radar sweep runs the entire 150s at a
   constant rate. Every reveal happens *as the sweep passes over it*. The sweep
   is the transition device — it replaces most cuts.
3. **Instruments do not bounce.** No overshoot, no elastic, no spring. Linear
   and `power2`/`expo.out` only. Blips travel at constant velocity. The only
   thing that ever accelerates is the dangerous one.
4. **One lit surface at a time.** The world is near-black. Product UI is the
   brightest thing on screen whenever it is present — the footage is the payoff,
   never a texture behind text.
5. **Nothing floats.** Everything is pinned to the scope, a strip, or a rail.

---

## 3. Vocabulary

The spine of the whole piece. Each product capability has a real ATC analogue —
none of these are stretched.

| Tower                          | LiveReview                                    |
| ------------------------------ | --------------------------------------------- |
| Aircraft                       | A change — commit, hunk, PR                   |
| Blip on the scope              | A diff awaiting review                        |
| Sector capacity                | Human attention. Fixed.                       |
| **Collision cone / separation minima** | **Blast radius**                      |
| Flight strip                   | The review summary / briefing deck            |
| **Readback** — pilot repeats the clearance back, proving they understood | **The PR quiz** |
| Clearance at every fix         | Commit · push · PR · CI/CD · schedule gates   |
| Sector handoff                 | The change moving between checkpoints         |
| Your tower, your airspace      | Self-hosting — your infrastructure            |
| Choice of radar feed           | Choice of AI model                            |
| **The tapes** — every transmission recorded, owned, reviewed | Your IP, your data, your model interactions |
| The controller                 | Your engineer                                 |

**Readback is the strongest detail in the film.** In real ATC a clearance is not
valid until the pilot reads it back. Not "did you receive it" — *prove you
understood it.* That is precisely what a PR quiz is, and precisely what
rubber-stamp approval is not. Act 4-2 is built on it.

---

## 4. Look

**Palette** — inverted from the old cut. The film is dark so the screens read.

| Role            | Value                                              |
| --------------- | -------------------------------------------------- |
| Ground          | near-black `#080b12`                               |
| Scope furniture | cobalt `primary` at 20–40% — rings, bearing ticks, grid |
| Sweep           | cobalt, leading edge bright, phosphor decay tail   |
| Type            | white / warm-white; muted `#8a93a6` for secondary  |
| Danger          | existing `negative` red — cones, the one heavy, BLOCK |
| Clear           | existing `positive` green — separated, ALLOW, ✅   |

No green phosphor. Classic radar green would fight the brand and drag in
hacker-terminal cliché. Cobalt-on-black is the same read, on-brand.

**Type** Inter only (`assets/fonts/Inter-var.woff2`), already in the project.
Headlines near-white, −0.02em. Eyebrows and act pills uppercase, 0.08em, cobalt.
A small monospace voice for strip data and callsigns — the only place mono appears.

**Product clips** 2520x1080 (21:9), always `object-fit: contain` inside a framed
window, never cropped. On black the frame can be a thin cobalt hairline — the
window reads as a scope repeater slaved to the main display.

**Sound** The bed carries mood. One SFX only: a short radio squelch/click, used
exactly four times — once at each "→ Solved." Restraint is the whole point.

---

## 5. Beat sheet

Budget sums to 150.000s.

### Act 0 — Hook · 0–16s

Black. Silence under the bed. **One blip.** It drifts, constant velocity.

> You already do a lot of…
> **AI-Assisted code generation**

The blip splits. Two. Eight. Forty. Three hundred. Not a cut — a continuous
bloom, each new blip appearing as the sweep reaches its bearing, so the growth
feels *observed* rather than animated. The scope fills.

Then every label drops off. Three hundred anonymous returns, none identified.

> But do you do enough of…
> **AI-Assisted Code Inspection?**

**The frame that has to land:** a full scope where nothing is labelled. The
problem is not the traffic. It is that nobody knows which one matters.

### Act 1 — Belief · 16–30s

Pull back off the glass. The tower interior — console rail, empty chairs, the
scope the only light source. Slow parallax, barely moving.

> You owe your users and customers —
> to adapt an **AI-assisted inspection layer**

Hold. Let the empty chairs do the work. Slides 4/5/6 are three phrasings of one
idea; take the strongest and cut the others. One line, held, beats three lines rushed.

### Act 2 — Velocity & volume · 30–56s

Back to the glass. The sweep rate **doubles**, visibly. A counter on the rail climbs.

> Code accumulates at **great VELOCITY**
> → **HUGE VOLUME of code**

Four flight strips slide onto the desk rail, one per sweep pass — the duties you
still owe regardless of volume:

> Reduce production incidents · Reduce security incidents ·
> Reduce performance regressions · Deliver stellar customer experiences

Then: one controller silhouette against the scope. Everything else stills.

> And let's remember: **Human attention is still limited**

The strips keep arriving behind them. That image — one person, strips stacking —
is the thesis of the film.

### Act 3 — The four problems · 56–72s

The scope quarters. Each quadrant lights on a sweep pass with its question:

1. **ATTENTION** — Which changes deserve your engineers' scarce attention?
2. **UNDERSTANDING** — How can your engineers maintain intellectual control of the system?
3. **ENFORCEMENT** — How do you make good review happen every time, without slowing the team down?
4. **CONTROL & IMPROVE** — How do you own your IP, your code, your data, your model interactions — and use them to improve yourself?

All four hold together, then collapse into the recap card:

> **#1 ATTENTION · #2 UNDERSTANDING · #3 ENFORCEMENT · #4 CONTROL and IMPROVE**

### Act 4 — The answers · 72–132s

Four acts, ~15s each, **identical rhythm** — that repetition is what makes the
film feel composed rather than listed. By the third the viewer is anticipating
the "Solved" beat, which is exactly what you want.

> metaphor beat (3s) → the deck's line (3s) → product footage (7s) → "→ Solved" (2s) + radio click

**4-1 · Attention** — Blips grow risk halos, sized not coloured at first. One
turns red and opens a widening collision cone across three other aircraft. That
cone *is* blast radius — say nothing, let it read.
> LiveReview ranks every hunk by blast radius and review priority.
→ `clip05_blast.mp4` (8s) → **The Attention Problem → Solved**

**4-2 · Understanding** — A flight strip prints, line by line, into something a
human can actually read. Then the readback: a line comes back *up* from the
aircraft, and only when it matches does the strip turn green.
> LiveReview gives summaries, issue navigation, and PR quizzes to keep humans in the loop.
→ `clip11_slides.mp4` (5.3s) + `clip11_quiz.mp4` (2.7s) → **The Understanding Problem → Solved**

**4-3 · Enforcement** — An approach path with five gates on it: commit, push,
PR, CI/CD, schedule. An aircraft is *held* at gate four — a red BLOCK pill —
then released green. Clearance every time, not when someone remembers.
> LiveReview reviews at commit, push, PR, CI/CD, and on schedule, enforcing your rules.
→ `clip08_schedule.mp4` (4s) + `clip10_cicd.mp4` (6.7s) → **The Enforcement Problem → Solved**

**4-4 · Control & Improve** — Widest shot of the film. The radar dish is on
*your* roof. A feed selector cycles — Claude, GPT, Gemini, DeepSeek, local
(brand SVGs already in `assets/`). Below the console, the tapes: every
transmission recorded, owned, yours to learn from.
> Keep your code in your infrastructure and choose which AI models inspect it.
> Adaptive Reviews cut AI cost; Livi learns from reviews; CLI, IDE, MCP and API fit your workflow.
→ `clip15_livi.mp4` (8.1s) + `clip14_nav.mp4` (7.1s) → **The Control and Improve Problem → Solved**

### Act 5 — Close · 132–150s

Back to the full scope from Act 0 — **and it is fuller.** More traffic than the
opening. Every aircraft labelled, spaced, moving clean. Nothing held.

> And that's why you owe your customers, your profession and your reputation
> **A FULL BLOWN AI-ASSISTED CODE INSPECTION LAYER**

Four ✅, one per sweep pass:
> The attention problem ✅ · The understanding problem ✅ ·
> The enforcement problem ✅ · The control and improve problem ✅

Scope dims to the logo. Sweep continues behind it.

> **hexmos.com/livereview**

The last image is the sweep still running. The tower does not stop.

---

## 6. Budget

| Act | Beat             | In    | Out   | Len  |
| --- | ---------------- | ----- | ----- | ---- |
| 0   | Hook             | 0     | 16    | 16   |
| 1   | Belief           | 16    | 30    | 14   |
| 2   | Velocity/volume  | 30    | 56    | 26   |
| 3   | Four problems    | 56    | 72    | 16   |
| 4-1 | Attention        | 72    | 87    | 15   |
| 4-2 | Understanding    | 87    | 103   | 16   |
| 4-3 | Enforcement      | 103   | 119   | 16   |
| 4-4 | Control          | 119   | 132   | 13   |
| 5   | Close            | 132   | 150   | 18   |

Act 4-3 carries 10.7s of footage in a 16s act — `clip08_schedule` trims to ~3s
or runs at a constant faster rate. 4-4 carries 15.2s in 13s; either widen 4-4 by
borrowing from Act 2, or cut `clip14_nav` to its Ctrl+K moment only.

---

## 7. Assets

Reused from `videos/livereview-launch/assets/`:
`clip05_blast` · `clip11_slides` · `clip11_quiz` · `clip08_schedule` ·
`clip10_cicd` · `clip15_livi` · `clip14_nav` · `clip13_dashboard` ·
`clip16_report` (spare) · `bgm/bed-150.mp3` · `Inter-var.woff2` · `logo.svg` ·
`brand-{claude,openai,gemini,deepseek,openrouter}.svg` · `lrbot_lrbot.png`

To build: scope furniture (rings, bearing ticks, sweep + decay), blip system,
collision cone, flight strip, gate rail, tower interior plate, feed selector.
All 2D vector. **None of this needs Blender** — radar reads better flat than
rendered. If 3D earns a place it is one slow parallax tower-interior plate
behind Act 1, as mood, not story.

## 8. Open questions

1. **Dark world vs. existing light brand.** This treatment inverts the old cut.
   Dark is the right call for a scope, but it is a real brand decision.
2. **The radio click.** One SFX, four uses. Or keep it music-only.
3. **Act 2 length.** 26s is generous. It is also where the argument is won.
4. **Drop Rickover, the horses, the role comic.** None survive into this world.
