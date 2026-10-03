"""Act 1 — The Hook (slides 1–2), ~10s.

Miles drops in on a web, lands, web-yanks the sign on stage (slide 1),
then flicks it around to slide 2.

    blender -b build/character.blend --python scripts/04_act1.py      # -> build/act1.blend
"""
import bpy, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mathutils import Vector
from pipeline import paths, anim, fx, shot
from pipeline.mixamo import Performer
from pipeline.shot import L_HAND, R_HAND, HIPS

sc = bpy.context.scene
rig = shot.stage(subject=(-2.4, 0.0))

# ------------------------------------------------------------------ performance
perf = Performer(rig).place(x=-2.2, y=0.0, face=0)
hit_shot = perf.extreme("Standing 1H Magic Attack 02", R_HAND, (1, 0, 0), 16, 40)
hang = perf.then("Hanging Idle", length=45)
land = perf.then("Hard Landing", to=50, speed=1.25, blend=6)
shot1 = perf.then("Standing 1H Magic Attack 02", frm=16, to=40, speed=1.2, blend=6)
pull = perf.then("Pull Heavy Object", speed=1.15, blend=6, face=65)
pull1 = perf.then("Pull Heavy Object Stop", to=22, speed=1.15, blend=5)
talk = perf.then("Talking (2)", frm=18, to=85, blend=8, face=10)            # slide 1 read time
flick = perf.then("Standing 1H Magic Attack 02", frm=16, to=40, speed=1.25, blend=6, face=0)
win = perf.then("Victory Idle", blend=6, face=0, length=50)
fin = perf.then("Happy Idle", blend=8, face=0, length=40)
perf.build()

SHOT_HIT = perf.clip_frame(shot1, hit_shot)
FLICK_HIT = perf.clip_frame(flick, hit_shot)
IMPACT = perf.clip_frame(land, 30)
FLIP = int(FLICK_HIT) + 1
END = FLIP + 80                                  # slide 2 read time
sc.frame_end = END

HANG_Z = 2.44 - 1.15        # Hanging Idle hips (1.15) must meet Hard Landing's start (2.44)
perf.root_z([(1, 4.8, "cubic_out"), (int(hang.start) + 30, HANG_Z, "lin"),
             (int(land.start), HANG_Z, "lin"), (int(land.start) + land.blend, 0.0, "lin")])

# ------------------------------------------------------------------ the sign
BW, STAND = 4.8, 0.6
BX, BY = 0.75, 0.2
BZ = STAND + BW * 9 / 16 / 2
board = fx.Board("Board", [paths.slide(1), paths.slide(2)], width=BW, stand_height=STAND,
                 coll=fx.collection("Props"))
board.base_z = BZ
board.show(1, 0)
b = board.root
anim.keys(b, "location", [(1, Vector((13.0, BY, BZ)), "const"), (int(SHOT_HIT), Vector((13.0, BY, BZ)), "out")])
for f, x, e in [(pull.start + 2, 12.0, "out"), (pull.start + 12, 8.0, "out"), (pull.start + 22, 4.0, "out"),
                (pull1.start + 4, BX - 0.25, "back"), (pull1.start + 14, BX, "bez")]:
    anim.key(b, "location", int(f), x, 0, e)
anim.keys(b, "rotation_euler", [(int(SHOT_HIT), 0.12, "bez"), (int(pull.start + 12), -0.06, "bez"),
                                (int(pull1.start + 4), 0.03, "back"), (int(pull1.start + 14), 0.0, "bez")], index=2)
anim.keys(b, "rotation_euler", [(int(SHOT_HIT), 0.0), (int(pull1.start + 2), 0.0, "out"),
                                (int(pull1.start + 6), -0.035, "back"), (int(pull1.start + 14), 0.0)], index=1)
board.spin = 0.0
board.flip(FLIP, 1)

# ------------------------------------------------------------------ webs
webs = fx.WebShots(rig, fx.collection("Webs"))
RELEASE = int(land.start) + 3
LET_GO = int(pull1.start) + 10
top = perf.bone_world(HIPS, hang.start + 30)
sky = Vector((top.x, top.y, 14.0))
webs.shot("Web_HangL", L_HAND, lambda f: sky, 1, 1, RELEASE)
webs.shot("Web_HangR", R_HAND, lambda f: sky, 1, 1, RELEASE)
hook = lambda f: board.nearest_hook(webs.hand(R_HAND))
webs.shot("Web_Shot", R_HAND, hook, SHOT_HIT - 4, SHOT_HIT, LET_GO)
webs.shot("Web_Pull", L_HAND, hook, pull.start + 4, pull.start + 4, LET_GO)
webs.shot("Web_Flick", R_HAND, hook, FLICK_HIT - 4, FLICK_HIT, FLIP + 4)
webs.bake(range(1, END + 1))

# ------------------------------------------------------------------ camera
cam = fx.CameraRig(lens=30, fstop=4.0)
h = perf.bone_world(HIPS, IMPACT)
span = lambda f: shot.frame_span(perf.bone_world(HIPS, f).x - 1.1, BX + BW / 2 + 0.4, BY)
cam.lens(1, 22, "const")
cam.at(1, (h.x + 0.8, -6.0, 0.4), (h.x, 0, 3.0))                                   # low angle, looking up
cam.at(int(hang.end) - 4, (h.x + 0.6, -5.4, 0.5), (h.x, 0, 2.4))
cam.lens(int(land.start) + 2, 30, "const")
cam.at(int(land.start) + 2, (h.x + 0.9, h.y - 4.0, 0.95), (h.x, h.y, 0.95), cut=True)  # cut on the drop
cam.at(int(SHOT_HIT) - 6, (h.x + 1.0, h.y - 4.1, 1.0), (h.x + 0.1, h.y, 1.0), "expo_out")
cam.at(int(SHOT_HIT) + 6, (0.6, -8.6, 1.8), (0.8, 0, 1.6))                            # whip wide with the web
cam.lens(int(pull1.start) + 4, 32, "inout")
cam.at(int(pull1.start) + 4, (0.6, -8.4, 1.8), (0.8, 0, 1.6), "expo_out")
c, t = span(int(talk.start))
cam.at(int(talk.start) + 4, c, t)                                                    # sign-dominant two-shot
c2, t2 = span(FLIP)
cam.at(END, (c2[0] + 0.15, c2[1] + 0.35, c2[2]), t2)
cam.shake(int(IMPACT), amp=0.06, dur=8)

# where everything ends, so Act 2 can continue the same take
end_state = {"hips": shot.world_bone(rig, HIPS, END),
             "root": shot.world(perf.root, END), "root_rot": perf.root.matrix_world.to_euler().z,
             "fin_action": fin.action.name, "fin_frame": fin.local(END),
             "cam": shot.world(cam.cam, END), "target": shot.world(cam.target, END), "lens": cam.cam.data.lens,
             "board": [BX, BY, BZ], "board_slide": 2, "board_spin": board.spin}
# "slide N" = the moment slide N is readable on screen (used to cue the voice-over)
shot.finish("act1", end_state=end_state, markers=[("descent", 1), ("impact", IMPACT), ("web_shot", SHOT_HIT), ("pull", pull.start),
                     ("slide 1", pull1.start + 12), ("flip", FLIP), ("slide 2", FLIP + 14)])
