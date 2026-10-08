"""Review-rule audit for the street piece (run after 04_street_part_1_final.py / 04_street_part2.py, which write build/<name>_audit.json).

    blender -b build/street_part_1_final.blend --python scripts/check_rules.py
    blender -b build/street_part2.blend --python scripts/check_rules.py -- street_part2

1 web travel: no spin / roll / cartwheel (body angle steady along the line; max per-frame change, total range)
2 explaining: upright (spine within 20° of vertical)        3 facing the camera (chest within 35°)
4 next to the slide (hips within 1.6 m of its edge, beside / in front of it)
5 hangs: none, and no web from a foot                       6 no clipping (no body point behind a slide's face)
"""
import bpy, json, math, os, sys
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import paths
NAME = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "street_part_1_final"
A = json.load(open(os.path.join(paths.ROOT, "build", f"{NAME}_audit.json")))
sc = bpy.context.scene
rig = bpy.data.objects["MilesRig"]
pb = rig.pose.bones
W = lambda n: rig.matrix_world @ pb["mixamorig:" + n].head
BODY = ("Hips", "Spine1", "Neck", "Head", "LeftHand", "RightHand", "LeftForeArm", "RightForeArm", "LeftFoot", "RightFoot",
        "LeftLeg", "RightLeg")
fails = []


def ang(a, b):
    return math.degrees(math.acos(max(-1.0, min(1.0, a.normalized().dot(b.normalized())))))


# 1 web travel
for a, b, name in A["travel"]:
    axes = []
    for f in range(a, b + 1):
        sc.frame_set(f)
        axes.append(W("Neck") - W("Hips"))
    step = max(ang(p, q) for p, q in zip(axes, axes[1:]))
    tilt = [ang(v, Vector((0, 0, 1))) for v in axes]
    ok = step <= 12.0 and max(tilt) <= 75.0
    print(f"RULE1 travel {name:5s} f{a}-{b}: max turn {step:4.1f}°/frame, tilt {min(tilt):3.0f}-{max(tilt):3.0f}°  {'ok' if ok else 'FAIL'}")
    if not ok:
        fails.append(("travel", name))
# 2 + 3 explaining beats
for a, b, cam in A["talks"]:
    worst_up, worst_face = 0.0, 0.0
    for f in range(a, b + 1, 3):
        sc.frame_set(f)
        h, n = W("Hips"), W("Neck")
        worst_up = max(worst_up, ang(n - h, Vector((0, 0, 1))))
        lt, rt = W("LeftUpLeg"), W("RightUpLeg")
        chest = (lt - rt).cross(Vector((0, 0, 1)))                # hips' facing (left -> right x up = forward)
        to_cam = Vector(cam) - h
        chest.z = to_cam.z = 0
        worst_face = max(worst_face, ang(chest, to_cam))
    ok = worst_up <= 20.0 and worst_face <= 35.0
    print(f"RULE2/3 talk f{a}-{b}: spine ≤{worst_up:4.1f}° from vertical, chest ≤{worst_face:4.1f}° off camera  {'ok' if ok else 'FAIL'}")
    if not ok:
        fails.append(("talk", a))
# 4 + 6 reads
for name, a, b, bc, nn, w, h in A["reads"]:
    bc, n = Vector(bc), Vector(nn).normalized()
    side = n.cross(Vector((0, 0, 1))).normalized()
    far, clip = 0.0, 0
    for f in range(a, b + 1, 3):
        sc.frame_set(f)
        hp = W("Hips")
        u = abs((hp - bc).dot(side)) - w / 2                    # beyond the side edge (<0: in front of the face)
        d = (hp - bc).dot(n)                                     # in front of the face
        gap = max(0.0, u) if d > -0.3 else 99
        far = max(far, math.hypot(max(0.0, u), max(0.0, d - 0.2)))
        for bn in BODY:                                          # 6: nothing behind the face inside its rectangle
            p = W(bn)
            if (p - bc).dot(n) < 0.02 and abs((p - bc).dot(side)) < w / 2 and abs(p.z - bc.z) < h / 2:
                clip += 1
    ok = far <= 1.6 and clip == 0
    print(f"RULE4/6 read {name:9s} f{a}-{b}: hips ≤{far:.2f} m from the slide, {clip} body points inside it  {'ok' if ok else 'FAIL'}")
    if not ok:
        fails.append(("read", name))
# 5 hangs
feet = [w for w in A["webs"] if "Hang" in w or "Sub" in w]
print("RULE5 webs:", len(A["webs"]), "lines, from feet / hang lines:", feet or "none", "ok" if not feet else "FAIL")
print("RULES", "ALL OK" if not fails and not feet else f"FAILS {fails + feet}")
