---
workflow: product-launch-video
flow: automation
storyboard: yes
message: "The six things AI-written code breaks — and how an independent inspection layer closes every one of them"
destination: youtube
aspect: 1920x1080
language: en
audience: engineering-leadership
length: 157s
angle: problem-solution-resolution
narration: no
captions: no

## Intent

A relaunch of the LiveReview launch demo. The existing cut (`Ws66OKXUwwE.mp4`, 105s)
works as a feature inventory but not as a film — in the reviewer's words, "this is
like a slideshow of screenshots," "it looks like a feature dump," and "slides without
organization — people won't get any meaning out of it."

The fix is structural, not cosmetic. The video follows one arc, and every screenshot
lives inside it:

- **WHY** — the problem. AI made the org faster; it did not make it safer. Agitate
  with the real complaints, role by role: "AI is making us faster. Is it also making
  us sloppier?" · "How do we avoid another production incident that affects
  customers?" · "Why didn't I know this before opening the PR?"
- **WHAT** — the solution. An **independent inspection layer that sits above your
  generative AI stack** (Claude, Copilot, Cursor, or anything else). Anchored on the
  Rickover quote: *"You get what you inspect, not what you expect."*
- **HOW** — what makes the inspection effective: **blast radius**. Not all diffs are
  created equal. A 300-line UI tweak breaks one page; a 3-line DB change breaks the
  entire app. Score and sort every hunk of the diff by how far it can reach.
- **WHEN / WHERE** — the machinery that runs the inspection layer: the **five pillars**
  — Review, Understand, Enforce, Improve, Connect — as an animated *cycle*, not a list,
  because the site's own line is "Improve feeds straight back into Review: the loop runs
  continuously on every commit, not once at setup." The feature screens hang off the
  pillar they belong to.

First 15–20s establishes the story. Last ~10s recaps it. The feature material in
between is fine as a feature dump *as long as it is contextualized inside the arc*.

Tone: confident, engineering-serious, business-literate. The audience is engineering
leadership first (CTO / VP Eng / EM), developers second.

## Assets

- ../../Ws66OKXUwwE.mp4 — the existing 105s cut, 2520x1080 @30fps. Source footage for the
  HOW and WHEN/WHERE sections; reframed 21:9 -> 16:9 per segment. Contains ~14 screen
  recordings: dashboard/review pipeline, summary deck, issue navigator, PR quiz, Livi
  chat + charts, impact report, onboarding report. Its own burned-in captions are
  unplated and must not survive into the new cut — crop or cover them.
- ../../hexmos.com_livereview_site.md — landing page scrape: hero, blast radius, The
  System, all five pillars with their questions, risk taxonomy, CLI tools, MCP/API.
- ../../hexmos.com_livereview_transform_site.md — the 14-day program page: the role-by-role
  "You're probably asking" complaints (the WHY material) and the Today/After-two-weeks table.
- ../../hexmos.com_livereview_transform_details_site.md — program detail page.

## Customizations

- **Caption plate.** Reviewer note: the first 15–20s of the current cut has captions with
  no background. Captions get a semi-transparent plate, matched to the treatment already
  used on the git-lrc video (hexmos.com/livereview/git-lrc/). This applies to the whole
  cut, not only the opening.
- **Animated five-pillar graph.** Review · Understand · Enforce · Improve · Connect built
  as a closed cycle with the Improve->Review return edge visible, then the feature set
  shown underneath it. Explicitly requested: "turn that into an animated graph kind of thing,
  then show feature set."
- **Comic theme in the WHY.** The /transform/ page ships an illustrated role-benefits comic
  (hexmos.com/livereview/transform/role-benefits-comic.png). Exploit it for the WHY beats
  rather than inventing a separate visual language.
- **Blast-radius contrast as a built beat.** The 300-vs-3 comparison gets its own designed
  moment, not a screenshot of the landing page section.
- **Recap close.** Last ~10s restates WHY -> WHAT -> HOW in one compressed pass.

- **Audio is fully local.** HeyGen sign-in is blocked on the user's side, and no
  Gemini / Google / OpenRouter credential exists either. Confirmed routing:
  VO -> Kokoro (offline, ready); SFX -> the bundled media-use local library;
  BGM -> MusicGen local generation (auto-installs `transformers`/`torch`, one <=30s
  seed clip crossfade-looped to length; CPU-only here, so expect it to be slow).
  Do not re-offer HeyGen.


## Revision — 2026-09-20 (silent restructure)

Feedback after the second render, from the user and from the reviewer:

- The problems of AI-generated code must be **listed explicitly at the start**, and the film must end
  by showing **those same problems addressed** — the user's analogy was a sports film: the character
  starts with the dream and ends as the star. Same list, opened and closed.
- **"I actually didn't get what the problem was first time around."** The previous cut spent 12.5s on
  the problem and reached the Rickover turn at 0:12 — about 10% of the runtime on the thing that has
  to make a viewer care.
- **"We should have more text for the problem — audio alone is not giving enough emphasis."**
- The stacked-clause treatment used in the recap frame should appear **at the beginning too**.
- **The film must be fully understandable from the visuals alone**, like reading a storyboard. The
  user is removing audio entirely for this reason.
- The middle (solution, blast radius, five pillars, features) was explicitly called good — leave it.

What changed:

- **Silent.** `music: none`, no `SCRIPT.md`, no `audio_meta.json`, no SFX. The narration, score and
  SFX are archived under `.hyperframes/disabled/`. Every frame now carries its own words. Frame
  `voiceover:` fields are kept only as a record of what a beat used to say.
- **19 frames, ~157s** (was 15 frames, 121s). Reading-paced, not speech-paced.
- **ACT 1 grew 12.5s → 35.5s**: F01 stacked-clause hook · F02 the widening gap · **F03 the six problems,
  named and listed** · F04 who feels it · F05 what it costs. Rickover now lands at ~0:36, not 0:12.
- **ACT 3 gained F17** — the same six problems, same order, same layout, each ✕ flipping to ✓.
  F03 and F17 are a matched pair; the recognition between them is the film's payoff. Their six labels
  must never be reworded or reordered independently.
- The six come from the product's own Today/After table on hexmos.com/livereview/transform/.
- Existing frames were renumbered (old 01→02, 02→04, 03→06 … 14→18, 15→19). Composition ids and
  timeline keys were rewritten to match; class prefixes were deliberately left alone to avoid
  collisions in the shared DOM. Originals are in `.hyperframes/old-frames/`.
- New frames use `n01-` / `n03-` / `n05-` / `n17-` class prefixes for the same reason.

## Notes

- Captions were REMOVED at the user's request after reviewing the first render (2026-09-19). The caption skin and `compositions/captions.html` are preserved under `.hyperframes/disabled/` — restore by moving it back and re-assembling. Note this reverses the reviewer's original note about caption background plates.

- Source-of-truth quotes, verbatim:
  - "You get what you inspect, not what you expect." — Admiral Hyman G. Rickover, U.S. Navy
  - "Blast-Radius Aware AI Code Review for Business-Critical Systems."
  - "300 line UI tweak — breaks one page." / "3 line DB change — breaks the entire app."
  - "Improve feeds straight back into Review."
  - Hero framing: "AI generates code fast, like a wild horse. LiveReview tames it into your workhorse."
- The five pillar questions, used to re-anchor each feature beat to the story:
  Review "What matters in this code change?" · Understand "Can an engineer quickly understand
  what changed and what it means?" · Enforce "Can we make our engineering standards and review
  policies actually happen?" · Improve "How are we doing, and where should engineering improve?"
  · Connect "Can LiveReview fit into our existing engineering environment?"
- 120s sits above this route's 30–90s sweet spot. Mitigation agreed at intent: each pillar beat
  opens on its own question so the story re-anchors roughly every 12s; blast radius gets the
  largest single slice (~25s) as the differentiator.
- The existing cut's audio is a MUSIC BED, not narration — 30s of it transcribes to 4 words.
  There is no VO script to carry over; the new cut gets its own Kokoro VO and its own BGM.
- Caption timing is solved offline: whisper-cpp was built locally
  (`~/.cache/hyperframes/whisper/whisper.cpp/build/bin/whisper-cli`, `small.en` model cached),
  which is the Kokoro -> word-timings path the captions pipeline needs. `cmake` was pip-installed
  to make that build possible.
- Source footage inventory with timecodes and pillar mapping: see `footage-map.md`.
- Do not rebuild the landing page in HTML. Designed beats for the story; captured screens for
  the product.
