"""dev.to GIF (~5.5s): Miles drops in on a web, lands, webs a DEV board in with ONE yank.

Dark studio, original toon-shaded suit, floating board with a glowing blue edge.

    python3 scripts/03_make_slides.py                                     # makes assets/slides/devto.png
    blender -b build/character.blend --python scripts/04_devto_gif.py    # -> build/devto_gif.blend
    blender -b build/devto_gif.blend --python scripts/05_render.py -- full 50
    # then: renders/devto_gif_540p.mp4 -> GIF (see 05 notes / ffmpeg palettegen)
"""
import bpy, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mathutils import Vector
from pipeline import paths, anim, fx, shot
from pipeline.mixamo import Performer
from pipeline.shot import L_HAND, R_HAND, HIPS

sc = bpy.context.scene
rig = shot.stage(theme="dark", subject=(0.0, 0.0), physical=False)
FACE = os.path.join(paths.SLIDES, "devto.png")

# ------------------------------------------------------------------ performance
perf = Performer(rig).place(x=-1.6, y=0.0, face=0)
hit_pk = perf.extreme("Standing 1H Magic Attack 02", R_HAND, (1, 0, 0), 16, 40)
hang = perf.then("Hanging Idle", length=34)
land = perf.then("Hard Landing", to=50, speed=1.3, blend=6)
shot1 = perf.then("Standing 1H Magic Attack 02", frm=16, to=40, speed=1.25, blend=6)
yank = perf.then("Pull Heavy Object Stop", to=30, speed=1.1, blend=5, face=65)   # one big heave back
win = perf.then("Victory Idle", blend=8, face=10, length=51)
end = perf.then("Breathing Idle", blend=10, face=10, length=24)
perf.build()
END = int(end.end)
sc.frame_end = END

HANG_Z = 2.44 - 1.15
perf.root_z([(1, 4.6, "cubic_out"), (int(hang.start) + 26, HANG_Z, "lin"),
             (int(land.start), HANG_Z, "lin"), (int(land.start) + land.blend, 0.0, "lin")])
SHOT_HIT = perf.clip_frame(shot1, hit_pk)
IMPACT = perf.clip_frame(land, 30)
Y0 = int(yank.start)

# ------------------------------------------------------------------ board: one yank, flies in, overshoots, settles
BW, BY, BZ, BX = 2.9, 0.8, 1.85, 1.45
board = fx.Board("Board", [FACE], width=BW, glow=0.9, frame="glow", coll=fx.collection("Props"))
board.base_z = BZ
board.show(1, 0)
b = board.root
anim.keys(b, "location", [(1, Vector((10.5, BY, BZ)), "const"), (Y0 + 2, Vector((10.5, BY, BZ)), "expo_out"),
                          (Y0 + 14, Vector((BX - 0.35, BY, BZ + 0.15)), "back"),
                          (Y0 + 24, Vector((BX, BY, BZ)), "bez")])
anim.keys(b, "rotation_euler", [(Y0 + 2, 0.45, "expo_out"), (Y0 + 14, -0.14, "back"), (Y0 + 26, -0.05, "bez")], index=2)
anim.keys(b, "rotation_euler", [(Y0 + 2, 0.0, "expo_out"), (Y0 + 14, -0.08, "back"), (Y0 + 24, 0.0, "bez")], index=1)

# ------------------------------------------------------------------ webs
webs = fx.WebShots(rig, fx.collection("Webs"))
top = perf.bone_world(HIPS, hang.start + 20)
sky = Vector((top.x, top.y, 14.0))
RELEASE = int(land.start) + 3
webs.shot("Web_HangL", L_HAND, lambda f: sky, 1, 1, RELEASE)
webs.shot("Web_HangR", R_HAND, lambda f: sky, 1, 1, RELEASE)
hook = lambda f: board.nearest_hook(webs.hand(R_HAND))
webs.shot("Web_Shot", R_HAND, hook, SHOT_HIT - 4, SHOT_HIT, Y0 + 18)
webs.shot("Web_Yank", L_HAND, hook, Y0, Y0, Y0 + 18)
for o in fx.collection("Webs").objects:
    if o.type == "MESH":
        o.data.materials[0] = fx.material("Web_Dark", (0.92, 0.95, 1.0), rough=0.4, emit=1.6)
webs.bake(range(1, END + 1))

# ------------------------------------------------------------------ camera
cam = fx.CameraRig(lens=26, fstop=2.8)
h = perf.bone_world(HIPS, IMPACT)
end_m = perf.bone_world(HIPS, END)
left, right = end_m.x - 1.4, BX + BW / 2 + 0.35
cx = (left + right) / 2
dist = (right - left) * 1.08 / 2 / math.tan(math.atan(18 / 30))
cam.lens(1, 22, "const")
cam.at(1, (h.x + 0.8, -6.0, 0.4), (h.x, 0, 3.0))
cam.at(int(hang.end) - 2, (h.x + 0.6, -5.4, 0.5), (h.x, 0, 2.4))
cam.lens(int(land.start) + 2, 30, "const")
cam.at(int(land.start) + 2, (h.x + 0.9, h.y - 4.0, 0.95), (h.x, h.y, 0.95), cut=True)
cam.at(int(SHOT_HIT) - 6, (h.x + 1.0, h.y - 4.1, 1.0), (h.x + 0.1, h.y, 1.0), "expo_out")
cam.at(int(SHOT_HIT) + 6, (cx + 0.6, BY - dist - 1.2, 1.7), (cx + 0.6, BY * 0.5, 1.45))
cam.at(Y0 + 18, (cx, BY - dist, 1.75), (cx, BY * 0.5, 1.55))
cam.at(END, (cx - 0.1, BY - dist + 0.35, 1.75), (cx, BY * 0.5, 1.55))
cam.shake(int(IMPACT), amp=0.07, dur=8)

shot.finish("devto_gif", exposure=0.0, markers=[("impact", IMPACT), ("web_shot", SHOT_HIT), ("yank", Y0),
                                                ("board in", Y0 + 24)])
