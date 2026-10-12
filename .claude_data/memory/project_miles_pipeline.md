---
name: project-miles-pipeline
description: Active track — masked Miles (Mixamo rig) presents LiveReview slides in Blender; full knowledge in lr_demo/miles/CLAUDE.md
metadata:
  type: project
---
Since 2026-10-03 the active video track is `lr_demo/miles/`: Act 1 (slides 1–2) and Act 2 (slides 3–6, continues Act 1's take) are built; free CMU mocap retargeting added so new moves don't need mixamo.com.

**Why:** reviewer (a teammate) wants character-driven but attention-managed slides: one idea per frame, black-on-white, one font size + bold, slide as hero.
**How to apply:** read `lr_demo/miles/CLAUDE.md` first; discuss plans before building; iterate at 360p. Related: [[project-cube-owl-rig]], [[blender-52-api-quirks]].

**Naming (2026-10-11):** the street film is three videos: part 1 = `street_part_1_final`, part 2 = `street_part2`
(S10–S15, was "part 2a"), part 3 = `street_part3` (S16–S19 + Meta, was "part 2b"). The user asked for "part 2a/2b" to be
renamed everywhere, so never call them 2a/2b again. The old full 2:40 part 2 script was deleted with the user's OK. Part 3
reads its VO from `assets/audio/vo_street_part2/` (lines 8–14) through the symlink `vo_street_part3`.
