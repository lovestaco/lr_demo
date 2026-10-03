"""Shot 01 — Miles drops in on a web, yanks in the LiveReview board, flips it to slide 2. (~7.5s)

    blender -b build/character.blend --python scripts/04_build_scene.py

Reads build/character.blend + assets/slides/, writes build/scene.blend.
All timing is derived from the clip list, so swapping a clip re-times everything.
"""
import bpy, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mathutils import Vector
from pipeline import paths, anim, fx
from pipeline.mixamo import Performer

sc = bpy.context.scene
sc.render.fps = 30
sc.frame_start = 1
rig = bpy.data.objects["MilesRig"]
L_HAND, R_HAND = "mixamorig:LeftHand", "mixamorig:RightHand"

# ------------------------------------------------------------------ performance
# Snappy cut (~7.5s): clips are trimmed to their action and sped up a little.
perf = Performer(rig).place(x=-2.2, y=0.0, face=0)
hang = perf.then("Hanging Idle", length=40)
land = perf.then("Hard Landing", to=50, speed=1.3, blend=6)
shot = perf.then("Standing 1H Magic Attack 02", frm=16, to=40, speed=1.25, blend=6)
pull = perf.then("Pull Heavy Object", speed=1.2, blend=6, face=65)
pull1 = perf.then("Pull Heavy Object Stop", to=22, speed=1.2, blend=5)
talk = perf.then("Talking (2)", frm=18, to=58, blend=8, face=10)
flick = perf.then("Standing 1H Magic Attack 02", frm=18, to=40, speed=1.3, blend=6, face=0)
win = perf.then("Victory Idle", blend=6, face=0)
perf.build()

SHOT_HIT = perf.clip_frame(shot, 27)        # arm fully extended
FLICK_HIT = perf.clip_frame(flick, 27)
IMPACT = perf.clip_frame(land, 30)          # crouch impact
FLIP = int(FLICK_HIT) + 1
END = FLIP + 56                              # ~1.5s to read slide 2
sc.frame_end = END

# lower him on the web: hips of Hanging Idle (1.15) must meet Hard Landing's start (2.44)
HANG_Z = 2.44 - 1.15
perf.root_z([(1, 4.8, "cubic_out"), (int(hang.start) + 26, HANG_Z, "lin"),
             (int(land.start), HANG_Z, "lin"), (int(land.start) + land.blend, 0.0, "lin")])

# ------------------------------------------------------------------ studio + board
fx.studio(theme="light")
props = fx.collection("Props")
BW = 3.6                                     # board width (m) — the slide is the hero
board, hook = fx.board("Board", os.path.join(paths.SLIDES, "slide_01.png"),
                       os.path.join(paths.SLIDES, "slide_02.png"), width=BW, coll=props)
BY, BZ, BX_END = 0.2, 1.95, 1.3
anim.keys(board, "location", [(1, Vector((12.0, BY, BZ)), "const"), (int(SHOT_HIT), Vector((12.0, BY, BZ)), "out")])
board_x = [(pull.start + 2, 11.0, "out"), (pull.start + 12, 7.5, "out"), (pull.start + 22, 4.0, "out"),
           (pull1.start + 4, BX_END - 0.25, "back"), (pull1.start + 14, BX_END, "bez")]
for f, x, e in board_x:
    anim.key(board, "location", int(f), x, 0, e)
anim.keys(board, "rotation_euler", [(int(SHOT_HIT), 0.3, "bez"), (int(pull.start + 10), -0.15, "bez"),
                                    (int(pull1.start + 4), 0.08, "back"), (int(pull1.start + 16), 0.0, "bez")], index=2)
anim.keys(board, "rotation_euler", [(int(SHOT_HIT), 0.0), (int(pull.start + 8), 0.05),
                                    (int(pull1.start + 6), -0.03), (int(pull1.start + 16), 0.0)], index=0)
# flip to slide 2 on the second web flick
anim.keys(board, "rotation_euler", [(FLIP, 0.0, "back"), (FLIP + 16, math.pi, "bez")], index=2)
anim.keys(board, "location", [(FLIP, BZ, "out"), (FLIP + 6, BZ + 0.2, "in"), (FLIP + 14, BZ, "bez")], index=2)

# ------------------------------------------------------------------ webs
webs = fx.collection("Webs")
hang_anchor = fx.empty("WebAnchor_Hang", coll=webs)
shot_anchor = fx.empty("WebAnchor_Shot", coll=webs)
web_hl = fx.web_strand("Web_HangL", rig, L_HAND, hang_anchor, coll=webs)
web_hr = fx.web_strand("Web_HangR", rig, R_HAND, hang_anchor, coll=webs)
# which hand reaches screen-right in the web-shot pose?
pl, pr = perf.bone_world(L_HAND, SHOT_HIT), perf.bone_world(R_HAND, SHOT_HIT)
SHOOT_HAND, OTHER_HAND = (L_HAND, R_HAND) if pl.x > pr.x else (R_HAND, L_HAND)
web_s = fx.web_strand("Web_Shot", rig, SHOOT_HAND, shot_anchor, coll=webs)
web_p = fx.web_strand("Web_Pull", rig, OTHER_HAND, shot_anchor, coll=webs)

hips_top = perf.bone_world("mixamorig:Hips", hang.start + 30)
hang_anchor.location = (hips_top.x, hips_top.y, 14.0)
RELEASE = int(land.start) + 3
LET_GO = int(pull1.start) + 10
FLIP_RELEASE = FLIP + 4
SHOT_START, FLICK_START = int(SHOT_HIT) - 4, int(FLICK_HIT) - 4
anim.visible(web_hl, [(1, True), (RELEASE, False)])
anim.visible(web_hr, [(1, True), (RELEASE, False)])
anim.visible(web_s, [(1, False), (SHOT_START, True), (LET_GO, False), (FLICK_START, True), (FLIP_RELEASE, False)])
anim.visible(web_p, [(1, False), (int(pull.start) + 4, True), (LET_GO, False)])


def hand(f):
    pb = rig.pose.bones[SHOOT_HAND]
    return rig.matrix_world @ pb.head.lerp(pb.tail, 0.75)


def shot_anchor_at(f):
    h = hook.matrix_world.translation
    for a, b in ((SHOT_START, int(SHOT_HIT)), (FLICK_START, int(FLICK_HIT))):
        if a <= f < b:
            t = (f - a) / (b - a)
            return hand(f).lerp(h, t * t * (3 - 2 * t))
    return h


fx.bake(range(1, END + 1), {shot_anchor: shot_anchor_at})

# ------------------------------------------------------------------ camera
cam = fx.CameraRig(lens=30, fstop=4.0)
m = lambda f: perf.bone_world("mixamorig:Hips", f)
h = m(IMPACT)


def two_shot(f, lens_mm=32, pad=1.06):
    """Board-dominant framing with Miles at the left edge."""
    mx = m(f)
    left, right = mx.x - 1.3, BX_END + BW / 2 + 0.25
    cx = (left + right) / 2
    dist = (right - left) * pad / 2 / math.tan(math.atan(18 / lens_mm))
    return (cx, BY - dist, 1.8), (cx, BY * 0.5, 1.6)


# descent: low angle looking up
cam.lens(1, 22, "const")
cam.at(1, (h.x + 0.8, -6.0, 0.4), (h.x, 0, 3.0))
cam.at(int(hang.end) - 4, (h.x + 0.6, -5.4, 0.5), (h.x, 0, 2.4))
# landing: hard cut to a medium, shake on impact
cam.lens(int(land.start) + 2, 30, "const")
cam.at(int(land.start) + 2, (h.x + 0.9, h.y - 4.0, 0.95), (h.x, h.y, 0.95), cut=True)
cam.at(int(SHOT_HIT) - 6, (h.x + 1.0, h.y - 4.1, 1.0), (h.x + 0.1, h.y, 1.0), "expo_out")
# web shot: fast whip out to wide so the strand flies off frame-right
cam.at(int(SHOT_HIT) + 6, (0.6, -8.6, 1.8), (0.8, 0, 1.6))
# board lands: quick push into the slide two-shot, hold through the flip
c, t = two_shot(int(talk.start))
cam.lens(int(pull1.start) + 4, 32, "inout")
cam.at(int(pull1.start) + 4, (0.6, -8.4, 1.8), (0.8, 0, 1.6), "expo_out")
cam.at(int(talk.start) + 4, c, t)
c2, t2 = two_shot(FLIP)
cam.at(END, (c2[0] + 0.15, c2[1] + 0.35, c2[2]), t2)
cam.shake(int(IMPACT), amp=0.06, dur=8)

# ------------------------------------------------------------------ look + save
fx.look(samples=24)
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 67
for name, f in (("descent", 1), ("impact", IMPACT), ("web_shot", SHOT_HIT), ("pull", pull.start),
                ("slide_1", talk.start), ("flip", FLIP), ("slide_2", FLIP + 30)):
    sc.timeline_markers.new(name, frame=int(f))
sc.frame_set(1)
os.makedirs(paths.BUILD, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=paths.SCENE_BLEND)
print(f"SCENE OK frames 1-{END} ({END / 30:.1f}s)  shoot hand={SHOOT_HAND}  impact={IMPACT:.0f} hit={SHOT_HIT:.0f} flip={FLIP}")
