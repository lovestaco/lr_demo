---
name: feedback-burnin-review-copies
description: Deliver exactly ONE video per render — the frame-numbered (_tc) file with audio; no clean/silent/extra variants in renders/
metadata:
  node_type: memory
  type: feedback
  originSessionId: f2127c4b-9447-417e-9ee3-f385fd69e341
  modified: 2026-10-11T09:09:17.623Z
---

Every video I render or hand over is ONE file: the frame number + "time / total" burned in at the bottom-right,
with the audio (VO, SFX, music, subtitles) mixed in. That is `06_assemble.py`'s `<name>_mix_tc.mp4`.

The user said on 2026-10-11: "i don't need all these variations… when you create video i want only one with the
frames and audio injected always just one video for anything i specify to render".
- Don't leave extra versions in `renders/`: no silent base `<name>.mp4`, no clean `_mix.mp4`, no 10 MB copy.
  Pipeline intermediates go to `build/intermediate/`. Move them there rather than deleting them; the base video can
  also be rebuilt from the frames with 06c.
- Make a 10 MB copy only when the user asks for one or the _tc file is over the size they named. Make it from the
  _tc file, and it then replaces the _tc file as the one deliverable.

**Why:** reviewers (the user, Shrijith, Lince) cite exact frame numbers. On 2026-10-08 the user watched a 10 MB copy
without frame numbers and was angry. On 2026-10-11 they were tired of 3–4 near-identical files per part. The overlay
is dropped only for the final public release, and only when the user says so.
**How to apply:** after any render or encode, check that a frame shows the number and that the file has audio, then
report the single path.

Related: [[feedback-keep-frames]], [[project-street-direction]]
