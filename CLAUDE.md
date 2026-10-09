# CLAUDE.md — lr_demo (LiveReview launch/marketing videos)

Video production for LiveReview (hexmos.com) — AI-assisted code inspection. Several
independent tracks live here; scope work to one subfolder and read its own docs.

| Folder | What | Docs |
|---|---|---|
| `miles/` | **Active.** Masked Miles Morales (Mixamo rig) presents slides on a web-pulled sign in Blender; acts per script, CMU mocap retargeting | `miles/CLAUDE.md`, `miles/README.md` |
| `blender_owl/` | Cube-owl mascot rig + `owl_lib.py` action vocabulary, street set | `blender_owl/README.md` |
| `blender_stuff_lr/` | ATC radar scope plate for the HyperFrames launch video | scripts inside |
| `videos/livereview-launch/`, `videos/livereview-mascot/` | HyperFrames compositions | their BRIEF/STORYBOARD files |
| `blender_assets_downloaded/` | Mixamo FBX clips + `cmu/` BVH mocap downloads | — |
| `ppt/LiveReview-Presentation-slides.md` | The presentation deck text (Acts 1–6) that the videos are built from | — |

## Shared facts
- Blender 5.2 LTS (`/snap/bin/blender`), run headless with `-b`; live control via Blender MCP when the user connects it.
- Rendering: EEVEE only (GTX 1650, 4 GB VRAM). Preview at 360p; render high-res only for finals.
- Secrets (Sketchfab token) are in `blender_owl/.env` — gitignored, never commit. `.env`, render
  frame folders, `miles/build/` and >100 MB renders are gitignored (GitHub 100 MB limit).
- Before building a new scene/act, discuss the plan with the user first.
- For new character motion, use the free CMU mocap pipeline in `miles/` (`scripts/00_cmu_fetch.py`
  → `scripts/02b_retarget_cmu.py`) instead of hand-downloading from mixamo.com.

## Installed tools
- **TripoSR** (image → 3D mesh, MIT licence, VAST-AI/Stability) at `~/tools/TripoSR` with its own venv
  (`.venv`, uv-managed Python 3.10, torch 2.4.1+cu121). Weights: HF cache `stabilityai/TripoSR` (~1.7 GB).
  For one-off static props only (no rig, no animation; soft/blobby, the back is guessed) — Sketchfab first.
      cd ~/tools/TripoSR && .venv/bin/python run.py IMAGE.png --output-dir OUT --chunk-size 4096 \
          --model-save-format glb --bake-texture --texture-resolution 1024      # -> OUT/0/mesh.glb
  The GTX 1650 has 4 GB: keep `--chunk-size` ≤ 4096 (default 8192 wants ~6 GB). Local patch:
  `tsr/models/isosurface.py` uses PyMCubes (CPU) instead of torchmcubes (its CUDA build fails with CUDA 12.0 here);
  winding flipped to outward normals. Background removal (rembg) downloads its model on first run.
- Blender skills pack (kevinbadi/blender-skills) in `~/.claude/skills/` (turntable, slow-zoom, PolyHaven, ...):
  written for macOS — METAL device, `~/Desktop/Blender Videos`, ProRes 4444; adapt before use.
