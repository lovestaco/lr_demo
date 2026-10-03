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
