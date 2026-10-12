---
name: project-lr-demo-videos
description: "LiveReview (hexmos.com) launch video production — two parallel video tracks, context for future sessions"
metadata: 
  node_type: memory
  type: project
  originSessionId: e822d076-33f9-4bf4-b620-4fb098ae9f1f
  modified: 2026-09-30T19:27:00.099Z
---

Two demo videos being produced for LiveReview (hexmos.com), an AI-assisted code review product:

**Track 1 — ATC theme** (`videos/livereview-launch/`)
- 150s, 1920×1080, dark cobalt palette
- Blender 3D radar scope plate (`blender_stuff_lr/scope.blend`) renders as PNG sequence → `assets/plate-atc-150.mp4`
- Render running headlessly: PID 975039, output `blender_stuff_lr/frames/frame_####.png`, ~4500 total frames
- After render: run `blender_stuff_lr/encode_plate.sh` → swap placeholder src in index.html → `npm run render`
- HyperFrames project at `videos/livereview-launch/`, preview at http://127.0.0.1:3002
- Stage 3-6 done; Stage 7 (final render) pending render completion

**Track 2 — Mascot theme** (`videos/livereview-mascot/` — NEW, to be created)
- 3-4 min video using Livi the owl (product mascot) as 2D animated character
- Blender Grease Pencil for character animation; HyperFrames for composition
- Goal: viewers understand the product and want to buy it
- Resources: https://github.com/kevinbadi/blender-skills, https://mumumundo.gumroad.com/l/stick-man-rig

**Why:** User is the founder of hexmos.com/LiveReview and wants high-quality marketing videos.

**How to apply:** Never touch `videos/livereview-launch/` unless explicitly asked. Keep the two tracks separate. Don't kill PID 975039. See [[blender-52-api-quirks]] for Blender API notes.
