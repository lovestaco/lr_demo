---
name: feedback-keep-frames
description: Renders — keep rendered frame folders (never wipe) and always deliver the frame-number (_tc) copy; previews at 360p
metadata:
  type: feedback
---

User (2026-10-06): "render in 360 and always keep the frames dont remove the frame number".

**Why:** the user reviews by frame number and wants rendered frames to stay on disk (no re-render to recover a version).
**How to apply:** `05_render.py full` writes to `build/frames/<name>_<h>p/` and never deletes them (re-renders overwrite in
place); every assembled video also gets its `_tc` burn-in copy (see [[feedback-burnin]]); review renders at 360p
(`full 33`, full quality). Disk is tight (~4 GB free on /home, 1080p frames ≈ 5 GB): warn before a 1080p run.

**Update (2026-10-10):** the user also said "save the high resolution rendered video, don't delete it, I'll check the quality" — never delete 720p/1080p renders or their frame folders (renders/*_720p*, build/frames/*_720p); superseded 360p frames get moved aside (`_before_*`/`_prev_*`), not removed. Disk is tight (~6 GB free): warn before a 1080p run.
