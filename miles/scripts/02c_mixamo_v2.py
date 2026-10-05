"""Mixamo clips downloaded on the MILES_FOR_MIXAMO upload (a different auto-rig than MilesRig) ->
actions "MX <name>" in build/character.blend, retargeted with the same solver as the CMU mocap.

    blender -b build/character.blend --python scripts/02c_mixamo_v2.py [-- Backflip Taunt ...]

Source: ../blender_assets_downloaded/mixamo_v2/*.fbx and mixamo_v2/packs/*.fbx (pack zips unpacked).
Existing "MX ..." actions are skipped unless named on the command line.
"""
import bpy, glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import paths, retarget

SRC = os.path.join(paths.MIXAMO_CLIPS, "mixamo_v2")
only = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
rig = bpy.data.objects["MilesRig"]
bpy.context.scene.render.fps = 30
saved = rig.animation_data.action if rig.animation_data else None
done = 0
files = sorted(glob.glob(os.path.join(SRC, "*.fbx"))) + sorted(glob.glob(os.path.join(SRC, "packs", "*.fbx")))
for f in files:
    stem = os.path.splitext(os.path.basename(f))[0]
    if stem.lower().startswith("miles_for_mixamo"):
        continue
    name = "MX " + stem.title().replace("(1)", "1").replace("(2)", "2").replace("(3)", "3").replace("(4)", "4").replace("(5)", "5").strip()
    if only and stem not in only and name not in only:
        continue
    if name in bpy.data.actions and not only:
        continue
    try:
        act = retarget.fbx_to_action(f, rig, name)
        print(f"RETARGETED {name}  ({int(act.frame_range[1])} frames)")
        done += 1
    except Exception as e:                          # one bad file shouldn't stop the batch
        print(f"FAILED {name}: {e}")
if rig.animation_data:
    rig.animation_data.action = saved
bpy.ops.wm.save_mainfile()
print("DONE", done)
