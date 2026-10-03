"""Act 2 — The Belief (slides 3–6). Continues Act 1's take on the same stage.

    (Act 1 ends: Miles left of sign A showing slide 2)
    push   — double web-blast knocks sign A back and off to the right
    swing  — he web-swings across to the right side of the stage
    pull   — webs sign B in from the LEFT edge: slide 3 "Here's what we believe:"
    4,5,6  — web flicks spin sign B through the remaining slides; fist pump to finish

    blender -b build/character.blend --python scripts/04_act2.py      # needs build/act1_cues.json
"""
import bpy, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mathutils import Vector
from pipeline import paths, anim, fx, shot
from pipeline.mixamo import Performer
from pipeline.shot import L_HAND, R_HAND, HIPS

sc = bpy.context.scene
prev = shot.load_end_state("act1")
rig = shot.stage(subject=(-2.4, 0.0))          # identical lighting to Act 1 -> invisible cut
READ = {3: 75, 4: 145, 5: 145, 6: 160}          # frames each slide stays up (30fps)
TOWARD_LEFT = -60                                # facing (deg) that aims his forward reach at screen-left

# ------------------------------------------------------------------ performance
perf = Performer(rig).place(x=prev["root"][0], y=prev["root"][1], face=math.degrees(prev["root_rot"]))
PUSH, SHOOT, F4, F5, F6 = ("Standing 2H Magic Attack 02", "Standing 1H Magic Attack 01", "Standing 1H Magic Attack 03",
                           "Standing 2H Magic Attack 04", "Standing 1H Magic Attack 01")
fwd = (0, -1, 0)
push_pk = perf.extreme(PUSH, R_HAND, fwd)
shoot_pk = perf.extreme(SHOOT, R_HAND, fwd)
f4_pk = perf.extreme(F4, R_HAND, fwd)
f5_pk = perf.extreme(F5, R_HAND, fwd)

start = perf.then(prev["fin_action"], frm=prev["fin_frame"], length=10)
push = perf.then(PUSH, frm=push_pk - 14, to=push_pk + 10, speed=1.15, blend=6, face=80)
swing = perf.then("Swing To Land (1)", blend=6, face=90)
shoot1 = perf.then(SHOOT, frm=shoot_pk - 12, to=shoot_pk + 10, speed=1.2, blend=8, face=TOWARD_LEFT)
pull = perf.then("Pull Heavy Object", speed=1.15, blend=6, face=TOWARD_LEFT - 5)
pull1 = perf.then("Pull Heavy Object Stop", to=22, speed=1.15, blend=5)
hold3 = perf.then("Talking (2)", frm=18, length=READ[3], blend=8, face=-20)
flick4 = perf.then(F4, frm=f4_pk - 10, to=f4_pk + 12, speed=1.2, blend=6, face=TOWARD_LEFT)
hold4 = perf.then("Talking (1)", frm=1, length=READ[4], blend=8, face=-20)
flick5 = perf.then(F5, frm=f5_pk - 12, to=f5_pk + 12, speed=1.15, blend=6, face=TOWARD_LEFT)
hold5 = perf.then("Talking (2)", frm=1, length=READ[5], blend=8, face=-20)
flick6 = perf.then(F6, frm=shoot_pk - 10, to=shoot_pk + 12, speed=1.2, blend=6, face=TOWARD_LEFT)
win = perf.then("Victory Idle", blend=6, face=-10)
hold6 = perf.then("Happy Idle", blend=8, face=-5, length=READ[6] - 40)
perf.build()

PUSH_HIT = int(perf.clip_frame(push, push_pk))
SHOOT_HIT = perf.clip_frame(shoot1, shoot_pk)
HIT4, HIT5, HIT6 = (perf.clip_frame(c, p) for c, p in ((flick4, f4_pk), (flick5, f5_pk), (flick6, shoot_pk)))
END = int(hold6.end)
sc.frame_end = END

# a second character key for the right side of the stage, faded in after the swing
key_l = bpy.data.objects["CharKey"]
key_r = bpy.data.objects.new("CharKeyR", key_l.data.copy())
fx.collection("Studio").objects.link(key_r)
key_r.location = key_l.location + Vector((5.0, 0, 0))
key_r.rotation_euler = key_l.rotation_euler
e = key_l.data.energy
anim.keys(key_r.data, "energy", [(1, 0.0), (int(swing.end) - 6, 0.0, "inout"), (int(swing.end) + 10, e)])
anim.keys(key_l.data, "energy", [(1, e), (int(swing.end) - 6, e, "inout"), (int(swing.end) + 10, e * 0.35)])

# ------------------------------------------------------------------ signs
BW, STAND = 4.8, 0.6
BY = 0.2
BZ = STAND + BW * 9 / 16 / 2
props = fx.collection("Props")

# sign A: where Act 1 left it (slide 2), blasted away to the right
sign_a = fx.Board("SignA", [paths.slide(2)], width=BW, stand_height=STAND, coll=props)
a = sign_a.root
ax, ay, az = prev["board"]
anim.keys(a, "location", [(1, Vector((ax, ay, az)), "const"), (PUSH_HIT + 2, Vector((ax, ay, az)), "out"),
                          (PUSH_HIT + 20, Vector((ax + 11.0, ay + 2.5, az)), "bez")])
anim.keys(a, "rotation_euler", [(PUSH_HIT + 2, 0.0, "out"), (PUSH_HIT + 20, -0.9, "bez")], index=2)
anim.keys(a, "rotation_euler", [(PUSH_HIT + 2, 0.0, "out"), (PUSH_HIT + 8, 0.12, "bez"), (PUSH_HIT + 20, 0.0)], index=1)

# sign B: pulled in from the left; settles left of where Miles stands after the swing
mx = perf.bone_world(HIPS, int(hold3.start)).x
BX = mx - 0.9 - BW / 2
sign_b = fx.Board("SignB", [paths.slide(n) for n in (3, 4, 5, 6)], width=BW, stand_height=STAND, coll=props)
sign_b.base_z = BZ
sign_b.show(1, 0)
b = sign_b.root
anim.keys(b, "location", [(1, Vector((BX - 14, BY, BZ)), "const"), (int(SHOOT_HIT), Vector((BX - 14, BY, BZ)), "out")])
for f, x, e in [(pull.start + 2, BX - 13, "out"), (pull.start + 12, BX - 9, "out"), (pull.start + 22, BX - 4.5, "out"),
                (pull1.start + 4, BX + 0.25, "back"), (pull1.start + 14, BX, "bez")]:
    anim.key(b, "location", int(f), x, 0, e)
anim.keys(b, "rotation_euler", [(int(SHOOT_HIT), -0.12, "bez"), (int(pull.start + 12), 0.06, "bez"),
                                (int(pull1.start + 4), -0.03, "back"), (int(pull1.start + 14), 0.0, "bez")], index=2)
anim.keys(b, "rotation_euler", [(int(SHOOT_HIT), 0.0), (int(pull1.start + 2), 0.0, "out"),
                                (int(pull1.start + 6), 0.035, "back"), (int(pull1.start + 14), 0.0)], index=1)
sign_b.flip(int(HIT4) + 1, 1)
sign_b.flip(int(HIT5) + 1, 2, turns=1.5, dur=26, hop=0.35)
sign_b.flip(int(HIT6) + 1, 3)

# ------------------------------------------------------------------ webs
webs = fx.WebShots(rig, fx.collection("Webs"))
near = lambda sign, bone: (lambda f: sign.nearest_hook(webs.hand(bone)))
webs.shot("Web_PushL", L_HAND, near(sign_a, L_HAND), PUSH_HIT - 4, PUSH_HIT, PUSH_HIT + 5)
webs.shot("Web_PushR", R_HAND, near(sign_a, R_HAND), PUSH_HIT - 4, PUSH_HIT, PUSH_HIT + 5)
# swing line: anchored high above the middle of the arc
mid = perf.bone_world(HIPS, int(swing.start + swing.span * 0.45))
swing_hand = max((L_HAND, R_HAND), key=lambda h: perf.bone_world(h, int(swing.start + 8)).z)
pivot = Vector((mid.x, mid.y + 0.5, 9.0))
webs.shot("Web_Swing", swing_hand, lambda f: pivot, swing.start + 2, swing.start + 6, swing.start + swing.span * 0.62)
LET_GO = int(pull1.start) + 10
webs.shot("Web_Shoot", R_HAND, near(sign_b, R_HAND), SHOOT_HIT - 4, SHOOT_HIT, LET_GO)
webs.shot("Web_Pull", L_HAND, near(sign_b, L_HAND), pull.start + 4, pull.start + 4, LET_GO)
webs.shot("Web_Flick4", R_HAND, near(sign_b, R_HAND), HIT4 - 4, HIT4, HIT4 + 6)
webs.shot("Web_Flick5L", L_HAND, near(sign_b, L_HAND), HIT5 - 5, HIT5, HIT5 + 7)
webs.shot("Web_Flick5R", R_HAND, near(sign_b, R_HAND), HIT5 - 5, HIT5, HIT5 + 7)
webs.shot("Web_Flick6", R_HAND, near(sign_b, R_HAND), HIT6 - 4, HIT6, HIT6 + 6)
webs.bake(range(1, END + 1))

# ------------------------------------------------------------------ camera
cam = fx.CameraRig(lens=prev["lens"], fstop=4.0)
cam.lens(1, prev["lens"], "const")
cam.at(1, prev["cam"], prev["target"])                                        # exactly where Act 1 ended
cam.at(PUSH_HIT - 2, prev["cam"], prev["target"], "expo_out")
cam.at(PUSH_HIT + 14, (0.6, -10.2, 2.0), (0.6, 0.0, 1.5))                       # wide: sign A flies, he swings
cam.at(int(pull1.start), (-0.4, -10.0, 2.0), (-0.4, 0.0, 1.5))
c, t = shot.frame_span(BX - BW / 2 - 0.4, mx + 1.5, BY)
tight = lambda k: (Vector(c).lerp(Vector(t), k), Vector(t))
cam.at(int(pull1.start) + 16, c, t)                                            # sign B two-shot
for f, k in ((int(hold3.start) + 10, 0.0), (int(HIT4) - 2, 0.06), (int(HIT4) + 8, 0.0), (int(HIT5) - 2, 0.07),
             (int(HIT5) + 10, -0.04), (int(HIT6) - 2, 0.06), (int(HIT6) + 8, 0.0), (END, 0.08)):
    cam.at(f, *tight(k))

shot.finish("act2", markers=[("push", PUSH_HIT), ("swing", swing.start), ("slide 3", pull1.start + 12),
                             ("slide 4", HIT4 + 14), ("slide 5", HIT5 + 24), ("slide 6", HIT6 + 14)])
