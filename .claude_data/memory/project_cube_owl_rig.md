---
name: project-cube-owl-rig
description: 3D cube-owl character (Livi) rigged + action library for MCP-directed Blender animation, in blender_owl/
metadata:
  type: project
---
Started 2026-10-03 (team idea from a teammate: import a 3D owl, control it via Blender MCP like "directing a movie" to escape "lazy default slides").

Location: `lr_demo/blender_owl/` — build_owl.py (rebuilds owl_rig.blend + owl_street.blend from Sketchfab source/owl1.blend), owl_lib.py (Owl + Cam action library: walk/hop/jump/cartwheel/look/express/talk/point/wave/enter/exit + camera shots), demo_street.py (33s demo → owl_demo.blend, owl_demo_preview.mp4), README.md documents rig axes + API.

Next planned stages: shot-spec driven scenes from the launch PPT (owl + floating slide panels), more environments.

**Why:** Goal 1 = prove MCP can control character motion in a setting; later stages turn launch script into shots.
**How to apply:** Reuse owl_lib rather than rewriting keyframes; avoid ELASTIC easing on flat keys (oscillates). See [[blender-52-api-quirks]], [[project-lr-demo-videos]].
