"""Piece 1 (~65s): deck slides 1-19 as one story. Miles = frazzled IT engineer (badge, smartwatch, phone).

    Sc1  drops in on a web, lands, checks his watch, webs LCD #1 in with one yank, taps it on
         -> "You already ship a lot of AI-generated code."
    Sc2  phone buzzes, he reads it, shrugs           -> "But do you inspect it enough?"
    Sc3  walks AROUND the LCD like a presenter       -> users / profession / reputation -> "inspection layer"
    Sc4  cartwheels to LCD #2, taps it on            -> code scrolls faster and faster (velocity)
         paper pours out of the screen and buries his feet; he panics, checks his watch (volume)
    Sc5  steps out, checklist ticks in, phone keeps buzzing
    Sc6  stretch & yawn                              -> "But human attention is still limited."
    Sc7  system graph grows, bugs swarm; screen + lights glitch -> "And there are deeper consequences…"

No magic: he only gets things by web-pulling, walking, or cartwheeling.

    python3 scripts/03b_make_screens.py
    blender -b build/character.blend --python scripts/04_piece1.py      # -> build/piece1.blend
"""
import bpy, os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mathutils import Vector
from pipeline import paths, anim, fx, shot, props
from pipeline.mixamo import Performer
from pipeline.shot import L_HAND, R_HAND, HIPS

sc = bpy.context.scene
SCR = os.path.join(paths.ROOT, "assets", "screens")
scr = lambda n: os.path.join(SCR, n + ".png")
seq = lambda n, length, start: ("seq", os.path.join(SCR, n, "f_0001.png"), length, int(start))

rig = shot.stage(theme="dark", subject=(-2.4, 0.0), physical=True)
# voice-over line lengths drive how long each screen holds (assets/audio/vo/lines.json from 07/07b)
import json
_vo_p = os.path.join(paths.ROOT, "assets", "audio", "vo", "lines.json")
VO = {int(k): v["duration"] for k, v in json.load(open(_vo_p)).items()} if os.path.exists(_vo_p) else {}
hold = lambda n, default: int(round(max(default / 30, VO.get(n, 0) + 0.45) * 30))   # frames
office = props.Office(rig)
WALK = "Walking"

# ------------------------------------------------------------------ performance
perf = Performer(rig).place(x=-2.6, y=0.0, face=0)
hit_pk = perf.extreme("Standing 1H Magic Attack 02", R_HAND, (1, 0, 0), 16, 40)
# Sc1
hang = perf.then("Hanging Idle", length=40)
land = perf.then("Hard Landing", to=60, speed=1.2, blend=6)
idle1 = perf.then("Breathing Idle", length=48, blend=10)                          # watch check
shot1 = perf.then("Standing 1H Magic Attack 02", frm=16, to=40, speed=1.15, blend=6)
yank = perf.then("Pull Heavy Object Stop", to=30, speed=1.1, blend=5, face=65)
tap1 = perf.then("Breathing Idle", length=34, blend=8, face=70)                   # tap TV on
talk1 = perf.then("CMU 18_08 conversation - explain with hand gesture", frm=40, length=95, blend=10, face=15)
# Sc2
phone1 = perf.then("Breathing Idle", length=50, blend=10, face=10)              # phone buzz
shrug = perf.then("CMU 111_25 Shrug", blend=8, face=10)
hold2 = perf.then("CMU 18_08 conversation - explain with hand gesture", frm=150, length=60, blend=10, face=15)
# Sc3: walk around (behind) the LCD
CARD = max(hold(3, 72), hold(4, 72), hold(5, 72))     # frames per users/profession/reputation card
WALK_SPEED = 0.62
w1 = perf.then(WALK, blend=10, face=150, speed=WALK_SPEED)
w2 = perf.then(WALK, blend=6, face=90, repeat=3, speed=WALK_SPEED)          # behind the TV: longer than it is wide
w3 = perf.then(WALK, blend=6, face=30, speed=WALK_SPEED)
pres = perf.then("CMU 18_08 conversation - explain with hand gesture", frm=260, length=hold(6, 110) + 90, blend=12, face=-25)
# Sc4: cartwheel to LCD 2, tap on, velocity, paper avalanche
cart = perf.then("CMU 49_06 cartwheel", frm=20, to=112, blend=10, face=90)
w4 = perf.then(WALK, blend=8, face=90)
tap2 = perf.then("Breathing Idle", length=30, blend=8, face=70)
watch2 = perf.then("CMU 18_08 conversation - explain with hand gesture", frm=330, length=120, blend=10, face=10)
scared = perf.then("CMU 79_73 scared", frm=20, to=120, blend=8, face=5)
stuck = perf.then("Breathing Idle", length=40, blend=8, face=5)                    # watch check in the pile
# Sc5: step out, checklist
w5 = perf.then(WALK, blend=8, face=-60)
chk = perf.then("CMU 18_08 conversation - explain with hand gesture", frm=40, length=265, blend=10, face=25)
# Sc6: attention
yawn = perf.then("CMU 111_32 Stretch and yawn", frm=10, to=150, blend=10, face=10)
# Sc7: bigger systems, bugs, deeper consequences
sys1 = perf.then("CMU 18_08 conversation - explain with hand gesture", frm=380, length=150 + hold(12, 60) - 40, blend=10, face=25)
sh2 = perf.then("CMU 113_16 Shrug", frm=30, to=140, blend=8, face=10)
fear = perf.then("CMU 79_73 scared", frm=40, to=130, blend=8, face=0)
perf.build()

HANG_Z = 2.44 - 1.15
perf.root_z([(1, 5.0, "cubic_out"), (int(hang.start) + 30, HANG_Z, "lin"),
             (int(land.start), HANG_Z, "lin"), (int(land.start) + land.blend, 0.0, "lin")])
IMPACT = perf.clip_frame(land, 30)
SHOT_HIT = perf.clip_frame(shot1, hit_pk)
Y0 = int(yank.start)
END = int(fear.end) + 6
sc.frame_end = END
hips = lambda f: perf.bone_world(HIPS, int(f))

# ------------------------------------------------------------------ LCD 1 (placed from the walk-around path)
TVW, STAND = 2.6, 0.75
TVH = TVW * 9 / 16
TVZ = STAND + TVH / 2
ws = hips(w1.start)                                     # where he starts walking around
behind = hips(w2.start + w2.span / 2)                   # middle of the behind-the-TV pass
TV1 = Vector((behind.x, ws.y + (behind.y - ws.y) * 0.45, TVZ))
t1_on = int(tap1.start) + 14
tv1_slides = [scr("s01_generation"), scr("s02_inspect"), scr("s03a_users"), scr("s03b_profession"),
              scr("s03c_reputation"), scr("s04_layer")]
tv1 = fx.Board("LCD1", tv1_slides, width=TVW, frame="tv", power=True, glow=0.38, stand_height=STAND,
               coll=fx.collection("LCD1"))
tv1.base_z = TVZ
r1 = tv1.root
anim.keys(r1, "location", [(1, Vector((TV1.x + 9, TV1.y, TVZ)), "const"), (Y0 + 2, Vector((TV1.x + 9, TV1.y, TVZ)), "expo_out"),
                           (Y0 + 14, Vector((TV1.x - 0.25, TV1.y, TVZ)), "back"), (Y0 + 22, TV1, "bez")])
anim.keys(r1, "rotation_euler", [(Y0 + 2, 0.0, "expo_out"), (Y0 + 12, -0.05, "back"), (Y0 + 20, 0.0)], index=1)
tv1.power_on(t1_on)
s2_at = int(shrug.start) + 20
cards = int(w1.start) + 8
step = CARD
LAYER = cards + 3 * step                            # "Every team needs an AI-assisted inspection layer"
for i, f in enumerate([1, s2_at, cards, cards + step, cards + 2 * step, LAYER]):
    tv1.show(f, i)
for f in (s2_at, cards, cards + step, cards + 2 * step, LAYER):
    tv1.flicker(f - 2, n=2)

# ------------------------------------------------------------------ LCD 2 (placed from the cartwheel landing)
cl = hips(w4.end)
TV2 = Vector((cl.x + 0.55 + TVW / 2, cl.y + 0.55, TVZ))
t2_on = int(tap2.start) + 12
VEL_N, CHK_N, SYS_N = 150, 300, 210
pour0 = int(scared.start) - 6
chk_at = int(chk.start) + 4
att_at = int(yawn.start) + 20
sys_at = int(sys1.start)
deep_at = int(fear.start) + 6
tv2_slides = [seq("velocity", VEL_N, t2_on), scr("s05_volume"), seq("checklist", CHK_N, chk_at), scr("s06_attention"),
              seq("system", SYS_N, sys_at), scr("s07_deeper")]
tv2 = fx.Board("LCD2", tv2_slides, width=TVW, frame="tv", power=True, glow=0.38, stand_height=STAND,
               coll=fx.collection("LCD2"))
tv2.root.location = TV2
tv2.power_on(t2_on)
for i, f in enumerate([1, pour0 - 4, chk_at, att_at, sys_at, deep_at]):
    tv2.show(f, i)
tv2.flicker(deep_at - 4, n=8)

# paper avalanche: pages fly out of LCD 2's screen and pile around his feet
mid_p = hips(scared.start + 30)
r = random.Random(4)
fx.paper_pour("CodePages", scr("code_paper"),
              lambda i: TV2 + Vector((r.uniform(-1.0, 1.0), -0.08, r.uniform(-0.55, 0.55))),
              (mid_p.x + 0.3, mid_p.y - 0.1), count=170, start=pour0, dur=70, spread=(1.2, 0.8))

# ------------------------------------------------------------------ overlays: watch, phone, taps
office.check_watch(int(idle1.start) + 6, hold=18)
office.reach(int(tap1.start) + 6, (TV1.x - TVW / 2 + 0.12, TV1.y - 0.05, TVZ - 0.25))
office.check_phone(int(phone1.start) + 4, hold=24)
office.reach(int(tap2.start) + 4, (TV2.x - TVW / 2 + 0.12, TV2.y - 0.05, TVZ - 0.25))
office.check_watch(int(stuck.start) + 4, hold=16)
office.check_phone(chk_at + 70, hold=18)
office.check_phone(chk_at + 190, hold=18)
office.check_watch(int(yawn.end) - 30, hold=10)

# ------------------------------------------------------------------ webs (Sc1 only)
webs = fx.WebShots(rig, fx.collection("Webs"))
top = hips(hang.start + 20)
sky = Vector((top.x, top.y, 14.0))
RELEASE = int(land.start) + 3
webs.shot("Web_HangL", L_HAND, lambda f: sky, 1, 1, RELEASE)
webs.shot("Web_HangR", R_HAND, lambda f: sky, 1, 1, RELEASE)
hook = lambda f: tv1.nearest_hook(webs.hand(R_HAND))
webs.shot("Web_Shot", R_HAND, hook, SHOT_HIT - 4, SHOT_HIT, Y0 + 16)
webs.shot("Web_Yank", L_HAND, hook, Y0, Y0, Y0 + 16)
for o in fx.collection("Webs").objects:
    if o.type == "MESH":
        o.data.materials[0] = fx.material("Web_Dark", (0.92, 0.95, 1.0), rough=0.4, emit=1.6)
webs.bake(range(1, END + 1))

# ------------------------------------------------------------------ lights: follow spot + a light over each screen
fx.follow_spot(rig, energy=380)
for i, tv in enumerate((TV1, TV2)):
    # overhead light in front of each screen: lights the presenter + floor, not the screen glass
    fx.spot(f"ScreenTop{i + 1}", (tv.x, tv.y - 2.2, 4.6), (tv.x, tv.y - 1.4, 0.0), energy=650, angle=60)
# glitch at the end: studio lights stutter
for name in ("RimRed", "RimBlue", "WallWash", "ScreenTop2"):
    ld = bpy.data.objects[name].data
    e = ld.energy
    for k, m in enumerate((1.0, 0.2, 1.0, 0.1, 0.8, 0.3, 1.0)):
        anim.key(ld, "energy", deep_at - 4 + k * 2, e * m, ease="lin")

# ------------------------------------------------------------------ camera
cam = fx.CameraRig(lens=30, fstop=3.2)
h = hips(IMPACT)


def frame_on(tv, f, margin_l=1.1, margin_r=0.5, lens_mm=30, pad=1.18):
    m = hips(f)
    left = min(m.x - margin_l, tv.x - TVW / 2 - 0.4)
    right = max(m.x + margin_l, tv.x + TVW / 2 + margin_r)
    return shot.frame_span(left, right, tv.y, lens_mm=lens_mm, pad=pad, cam_z=1.75, target_z=1.5)


def screen_close(tv, lens_mm=30):
    """Screen-dominant framing for dense screens (checklist, graph)."""
    return shot.frame_span(tv.x - TVW / 2 - 0.9, tv.x + TVW / 2 + 0.25, tv.y, lens_mm=lens_mm, pad=1.1,
                           cam_z=1.7, target_z=TVZ - 0.05)


cam.lens(1, 22, "const")
cam.at(1, (h.x + 0.8, -6.0, 0.4), (h.x, 0, 3.0))                                     # low angle, looking up
cam.at(int(hang.end) - 2, (h.x + 0.6, -5.4, 0.5), (h.x, 0, 2.4))
cam.lens(int(land.start) + 2, 30, "const")
cam.at(int(land.start) + 2, (h.x + 0.9, h.y - 4.0, 0.95), (h.x, h.y, 0.95), cut=True)    # cut on the drop
cam.at(int(idle1.end), (h.x + 0.9, h.y - 3.4, 1.25), (h.x, h.y, 1.2), "inout")         # watch check: closer
c, t = frame_on(Vector((TV1.x, TV1.y, 0)), int(talk1.start))
cam.at(int(SHOT_HIT) + 4, (c[0] + 1.0, c[1] - 1.5, 1.8), (t[0] + 0.8, t[1], 1.4), "expo_out")  # wide as the web flies
cam.at(Y0 + 22, c, t)
cam.at(int(phone1.start) + 4, (h.x + 0.6, hips(phone1.start).y - 3.0, 1.5), (hips(phone1.start).x, 0, 1.45))  # phone: close
c2, t2 = frame_on(Vector((TV1.x, TV1.y, 0)), int(shrug.end))
cam.at(int(shrug.start) + 18, c2, t2)
c3, t3 = frame_on(Vector((TV1.x, TV1.y, 0)), int(pres.start) + 20, margin_l=0.9)
cam.at(int(w1.start), c2, t2)
cm, tm = frame_on(Vector((TV1.x, TV1.y, 0)), int(w2.end), margin_l=0.9)
cam.at(int(w2.end), cm, tm)                                                             # keep him in frame as he emerges
cam.at(int(pres.start) + 20, c3, t3)
cam.at(int(cart.start) + 6, c3, t3)
c4, t4 = frame_on(Vector((TV2.x, TV2.y, 0)), int(tap2.start))
cam.at(int(w4.end), c4, t4, "inout")                                                    # truck right with the cartwheel
cam.at(int(scared.start) + 10, (c4[0] - 0.3, c4[1] - 0.6, 1.6), (t4[0] - 0.3, t4[1], 1.1))  # see the pile
c5, t5 = frame_on(Vector((TV2.x, TV2.y, 0)), int(chk.start))
cc, tc = screen_close(Vector((TV2.x, TV2.y, 0)))
cam.at(chk_at - 6, c5, t5)
cam.at(chk_at + 16, cc, tc)                                                             # read the checklist
cam.at(att_at - 10, cc, tc)
cam.at(att_at + 10, c5, t5)                                                             # wide for the yawn
cam.at(sys_at, c5, t5)
cam.at(sys_at + 20, cc, tc)                                                             # read the graph
cam.at(deep_at - 6, cc, tc)
cam.at(END, (cc[0] + 0.1, cc[1] + 0.5, cc[2]), (tc[0] + 0.1, tc[1], tc[2]))
cam.shake(int(IMPACT), amp=0.06, dur=8)
cam.shake(deep_at, amp=0.05, dur=14)

# voice-over cues: line N starts at marker "vo N" (06_assemble places the clips there)
VO_CUES = {1: t1_on + 6, 2: s2_at + 4, 3: cards + 4, 4: cards + step + 4, 5: cards + 2 * step + 4, 6: LAYER + 4,
           7: t2_on + 6, 8: pour0, 9: chk_at + 4, 10: att_at + 4, 11: sys_at + 4, 12: sys_at + 134, 13: deep_at + 4}
shot.finish("piece1", exposure=0.0, markers=[(f"vo {n}", f) for n, f in VO_CUES.items()] + [
    ("sc1 drop", 1), ("sc1 tv on", t1_on), ("sc2 phone", phone1.start), ("sc2 slide2", s2_at),
    ("sc3 walk-around", w1.start), ("sc3 layer", LAYER), ("sc4 cartwheel", cart.start),
    ("sc4 velocity", t2_on), ("sc4 avalanche", pour0), ("sc5 checklist", chk_at), ("sc6 attention", att_at),
    ("sc7 system", sys_at), ("sc7 deeper", deep_at)])
