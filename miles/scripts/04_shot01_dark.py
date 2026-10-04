"""Shot 01 (original dark version, ~16s) with a BLANK board — text gets added in edit.

Recreates the first cut: dark Spider-Verse studio, original toon-shaded suit, 2.4 m
floating board with a glowing blue edge. Miles lowers in on a web, lands, webs the
board in from off-screen right, pulls it into place, then flicks it around.

    python3 scripts/03_make_slides.py                                      # makes assets/slides/blank_dark.png
    blender -b build/character.blend --python scripts/04_shot01_dark.py   # -> build/shot01_dark.blend
"""
import bpy, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mathutils import Vector
from pipeline import paths, anim, fx, shot
from pipeline.mixamo import Performer
from pipeline.shot import L_HAND, R_HAND, HIPS

sc = bpy.context.scene
rig = shot.stage(theme="dark", subject=(0.0, 0.0), physical=False)
BLANK = os.path.join(paths.SLIDES, "blank_dark.png")

# ------------------------------------------------------------------ performance (original timing)
perf = Performer(rig).place(x=-1.4, y=0.0, face=0)
hang = perf.then("Hanging Idle", length=100)
land = perf.then("Hard Landing", blend=6)
shot1 = perf.then("Standing 1H Magic Attack 02", blend=8, to=60)
pull0 = perf.then("Pull Heavy Object Start", blend=8, face=65)
pull = perf.then("Pull Heavy Object", blend=6, repeat=2)
pull1 = perf.then("Pull Heavy Object Stop", blend=6)
talk = perf.then("Talking (2)", blend=10, face=10, length=55)
flick = perf.then("Standing 1H Magic Attack 02", blend=8, face=0, frm=8, to=55)
win = perf.then("Victory Idle", blend=8, face=0)
perf.build()
END = int(win.end) + 6
sc.frame_end = END

HANG_Z = 2.44 - 1.15        # Hanging Idle hips must meet Hard Landing's start
perf.root_z([(1, 6.5, "cubic_out"), (int(hang.start) + 78, HANG_Z, "lin"),
             (int(land.start), HANG_Z, "lin"), (int(land.start) + land.blend, 0.0, "lin")])
SHOT_HIT = perf.clip_frame(shot1, 27)
FLICK_HIT = perf.clip_frame(flick, 27)
IMPACT = perf.clip_frame(land, 30)
FLIP = int(FLICK_HIT) + 2

# ------------------------------------------------------------------ board (blank, floating, glowing edge)
BW, BY, BZ, BX = 2.4, 0.8, 1.72, 1.65
board = fx.Board("Board", [BLANK, BLANK], width=BW, glow=0.9, frame="glow", coll=fx.collection("Props"))
board.base_z = BZ
board.show(1, 0)
b = board.root
anim.keys(b, "location", [(1, Vector((9.5, BY, BZ)), "const"), (int(SHOT_HIT), Vector((9.5, BY, BZ)), "out")])
for f, x, e in [(pull0.start + 14, 8.4, "out"), (pull.start + 6, 6.6, "out"), (pull.start + 22, 5.0, "out"),
                (pull.start + 40, 3.4, "out"), (pull.start + 56, 2.4, "out"), (pull1.start + 8, BX - 0.15, "back"),
                (pull1.start + 26, BX, "bez")]:
    anim.key(b, "location", int(f), x, 0, e)
anim.keys(b, "rotation_euler", [(int(SHOT_HIT), 0.35, "bez"), (int(pull.start), -0.18, "bez"),
                                (int(pull.start + 34), 0.14, "bez"), (int(pull1.start + 10), -0.12, "back"),
                                (int(pull1.start + 30), -0.06, "bez")], index=2)
anim.keys(b, "rotation_euler", [(int(SHOT_HIT), 0.0), (int(pull.start + 10), 0.06),
                                (int(pull.start + 40), -0.05), (int(pull1.start + 24), 0.0)], index=0)
board.spin = -0.06
board.flip(FLIP, 1, dur=22, hop=0.18)

# ------------------------------------------------------------------ webs
webs = fx.WebShots(rig, fx.collection("Webs"))
RELEASE, LET_GO = int(land.start) + 3, int(pull1.start) + 14
top = perf.bone_world(HIPS, hang.start + 60)
sky = Vector((top.x, top.y, 14.0))
webs.shot("Web_HangL", L_HAND, lambda f: sky, 1, 1, RELEASE)
webs.shot("Web_HangR", R_HAND, lambda f: sky, 1, 1, RELEASE)
hook = lambda f: board.nearest_hook(webs.hand(R_HAND))
webs.shot("Web_Shot", R_HAND, hook, SHOT_HIT - 4, SHOT_HIT, LET_GO)
webs.shot("Web_Pull", L_HAND, hook, pull0.start + 10, pull0.start + 10, LET_GO)
webs.shot("Web_Flick", R_HAND, hook, FLICK_HIT - 4, FLICK_HIT, FLIP + 4)
for o in fx.collection("Webs").objects:
    if o.type == "MESH":
        o.data.materials[0] = fx.material("Web_Dark", (0.92, 0.95, 1.0), rough=0.4, emit=1.6)
webs.bake(range(1, END + 1))

# ------------------------------------------------------------------ camera (original moves)
cam = fx.CameraRig(lens=26, fstop=2.8)
h = perf.bone_world(HIPS, IMPACT)


def two_shot(f, lens_mm=30, pad=1.15):
    mx = perf.bone_world(HIPS, f)
    left, right = mx.x - 1.1, BX + 1.3
    cx = (left + right) / 2
    dist = (right - left) * pad / 2 / math.tan(math.atan(18 / lens_mm))
    return (cx, BY - dist, 1.65), (cx, BY * 0.5, 1.45)


cam.lens(1, 22)
cam.at(1, (h.x + 0.9, -6.4, 0.35), (h.x, 0, 3.4))
cam.at(int(hang.start) + 88, (h.x + 0.7, -5.6, 0.45), (h.x, 0, 2.6))
cam.at(int(land.start) + 2, (h.x + 1.0, h.y - 4.3, 1.0), (h.x, h.y, 0.95), cut=True)
cam.lens(int(land.start) + 2, 30, "const")
cam.at(int(SHOT_HIT) - 10, (h.x + 1.1, h.y - 4.4, 1.05), (h.x + 0.1, h.y, 1.0), "expo_out")
cam.at(int(SHOT_HIT) + 12, (0.9, -7.8, 1.6), (0.9, 0, 1.35))
cam.at(int(pull1.start), (0.7, -6.9, 1.55), (0.6, 0, 1.35))
c, t = two_shot(int(talk.start) + 18)
cam.at(int(talk.start) + 18, c, t)
c, t = two_shot(FLIP + 26)
cam.at(FLIP + 26, c, t)
cam.at(END, (0.4, -6.4, 1.5), (0.3, 0, 1.35))
cam.shake(int(IMPACT), amp=0.07, dur=12)

shot.finish("shot01_dark", exposure=0.0, markers=[("descent", 1), ("impact", IMPACT), ("web_shot", SHOT_HIT),
                                                   ("pull", pull.start), ("board in", pull1.start + 26),
                                                   ("flip", FLIP), ("end", END)])
