"""Retarget every downloaded CMU BVH onto MilesRig and save them into build/character.blend.

    blender -b build/character.blend --python scripts/02b_retarget_cmu.py [-- 02_01 13_29 ...]

Actions are named "CMU <id> <description>" and behave exactly like the Mixamo clips
(Performer.then("CMU 02_01 walk", ...)). Already-retargeted clips are skipped.
"""
import bpy, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import paths, retarget

only = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
meta_p = os.path.join(paths.CMU_DIR, "index.json")
meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
rig = bpy.data.objects["MilesRig"]
bpy.context.scene.render.fps = 30
saved_action = rig.animation_data.action if rig.animation_data else None
done = 0
for path in sorted(glob.glob(os.path.join(paths.CMU_DIR, "*.bvh"))):
    cid = os.path.splitext(os.path.basename(path))[0]
    if only and cid not in only:
        continue
    desc = meta.get(cid, "").replace("/", "-")[:40].strip()
    name = f"CMU {cid} {desc}".strip()
    if name in bpy.data.actions and not only:
        continue
    act = retarget.bvh_to_action(path, rig, name)
    print(f"RETARGETED {name}  ({int(act.frame_range[1])} frames)")
    done += 1
if rig.animation_data:
    rig.animation_data.action = saved_action
bpy.ops.wm.save_mainfile()
print("DONE", done)
