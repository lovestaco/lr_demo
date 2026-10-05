"""Physical-plausibility check: every frame, is there something under his feet?

    blender -b build/street.blend --python scripts/check_support.py

Casts a ray down from the lowest toe (ignoring the character, webs, spiders, bills) and reports runs of
frames where the gap to the surface below is > 25 cm, except while an intentionally airborne clip plays
(swings, hangs, drops, flips) or he is upside down. Run it before every render.
"""
import bpy
from mathutils import Vector
sc = bpy.context.scene; rig = bpy.data.objects["MilesRig"]; pb = rig.pose.bones
mine = {o.name for o in rig.children_recursive} | {rig.name}
for o in bpy.data.objects:                       # webs / spiders / bills aren't floors
    if o.name.startswith(("Web", "Spider", "Bills", "BillOnMask", "CodePages")):
        mine.add(o.name)
mk = sorted((m.frame, m.name) for m in sc.timeline_markers if not m.name.startswith(("sfx", "vo", "cam")))
air_names = ("Swing To Land", "Hanging Idle", "MX Backflip", "Hard Landing")   # hangs / swings / drops / dive
bad, runs = [], []
dg = bpy.context.evaluated_depsgraph_get()
for f in range(2, sc.frame_end, 3):
    sc.frame_set(f)
    acts = [s.action.name for t in rig.animation_data.nla_tracks for s in t.strips if s.frame_start <= f <= s.frame_end]
    if any(any(a.startswith(n) for n in air_names) for a in acts):
        continue
    if abs(bpy.data.objects["MilesRig_Root"].rotation_euler.y) > 1:      # upside-down hangs
        continue
    feet = [rig.matrix_world @ pb["mixamorig:" + n].head for n in ("LeftToeBase", "RightToeBase")]
    p = min(feet, key=lambda v: v.z)
    o = p + Vector((0, 0, 0.05))
    gap = None
    for _ in range(4):
        ok, loc, nor, i, ob, m = sc.ray_cast(bpy.context.evaluated_depsgraph_get(), o, Vector((0, 0, -1)), distance=50)
        if not ok:
            break
        if ob.name in mine:
            o = loc - Vector((0, 0, 0.01)); continue
        gap = p.z - loc.z; break
    if gap is None or gap > 0.25 or gap < -0.15:
        bad.append((f, None if gap is None else round(gap, 2), acts[:2]))
for f, g, a in bad:
    if runs and f - runs[-1][1] <= 3: runs[-1][1] = f; runs[-1][2].add(str(g))
    else: runs.append([f, f, {str(g)}, a])
print("UNSUPPORTED RUNS", len(runs))
for r in runs: print("  f%d-%d gaps %s %s" % (r[0], r[1], sorted(r[2])[:4], r[3]))
