"""Street part 2b (~1:10, its own video): the product (S16/S17, 2D) and the rebuild (S18/S19, 3D).

Cut out of the old full part 2 (04_street_part2.py) so it stands alone, like 04_street_part2_a.py does for S10-S15.

    S16   (2D) tools for your engineers — scripts/05b_street_part2_boards.py fills these frames
    S17   (2D) tools for your agents
    S18   the wreck before sunrise: he webs INSPECTION back in, it locks with a glow, the floors snap up; the sun
          comes up behind it, floors light one by one, two new floors, cash; he lands on the roof
    S19   the rooftop at sunrise: the call to action, a peace sign, the pull-out; the billboard lights up -> demo

Timeline starts at frame 1 = the S16 cut. He is off frame through S16/S17 (2D frames are laid over in post).

    python3 scripts/05b_street_part2_boards.py build/frames/street_part2_b_720p     # S16/S17 boards
    blender -b build/character.blend --python scripts/04_street_part2_b.py         # -> build/street_part2_b.blend
    blender -b build/street_part2_b.blend --python scripts/check_rules.py -- street_part2_b
"""
import bpy, bmesh, os, sys, math, random, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mathutils import Vector, Matrix, Quaternion
from pipeline import paths, anim, fx, shot, city, swing, streetkit, life, props
from pipeline.mixamo import Performer, ClipGroup
from pipeline.shot import L_HAND, R_HAND, HIPS
from pipeline.streetkit import first, final, face_to, Z, SHOOT, HANG

FPS = 30
NAME = "street_part2_b"
sc = bpy.context.scene
ST, ST2 = (os.path.join(paths.ROOT, "assets", d) for d in ("street", "street2"))
SCR = os.path.join(paths.ROOT, "assets", "screens")
img = lambda n: os.path.join(ST2, n + ".png")
seq0 = lambda n, ext="png": os.path.join(ST2, n, f"f_0001.{ext}")
VO = json.load(open(os.path.join(paths.ROOT, "assets", "audio", "vo_street_part2", "lines.json")))
F = lambda x: int(round(x))
UPRIGHT = 30
CALM = ["Talking (2)", "Talking (1)"]

# ------------------------------------------------------------------ set (same city and lift as part 1)
c = city.load()
sun = city.golden_hour(sun_elev=6.0, sun_az=-60.0, strength=7.2)
sun.data.color = (1.0, 0.66, 0.40)
LIFT = 0.34
for o in c.coll.objects:
    if o.parent is None:
        o.location.z += LIFT
bpy.context.view_layer.update()
rig = bpy.data.objects["MilesRig"]
fx.physical_shading(rig, lift=3.0, sheen=0.85, rough=0.38)
office = props.Office(rig)
for con in (office.ik_phone, office.ik_reach, office.ik_watch):      # the legacy IK solver weighs every IK on the chain
    con.mute = True
for n in ("Watch_Band", "Watch_Face"):
    o = bpy.data.objects.get(n)
    if o:
        o.hide_render = o.hide_viewport = True
perf = Performer(rig).place(x=0, y=0, face=0)
k = streetkit.Kit(c, rig, perf, VO)
signs = fx.collection("Signs")
csite = fx.collection("Sites")
steel = fx.material("Shelter_Steel", (0.08, 0.09, 0.1), rough=0.35, metallic=0.8)


def box(name, size, loc, mat, coll=signs):
    me = bpy.data.meshes.new(name)
    b = bmesh.new()
    bmesh.ops.create_cube(b, size=1.0)
    bmesh.ops.scale(b, vec=size, verts=b.verts)
    b.to_mesh(me)
    b.free()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob.location = loc
    me.materials.append(mat)
    return ob


def parent_keep(child, parent, frame=None):
    if frame is not None:
        sc.frame_set(int(frame))
    bpy.context.view_layer.update()
    m = child.matrix_world.copy()
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()
    child.matrix_world = m


# ================================================================== locations (S18/S19 the wreck in the intersection)
OFF_SPOT = (0.0, 96.0)                                       # out of every shot (behind the lot cameras)
FIN_C = Vector((0.0, 2.0))
FIN_W, FIN_D, FIN_N, FIN_S = 12.0, 7.0, 6, 2.4
FIN_FRONT = FIN_C.y - FIN_D / 2
FX_SPOT = (FIN_C.x - FIN_W / 2 - 0.8, FIN_FRONT - 1.3)
FL8 = k.floor_at(*FX_SPOT)
TOP6 = 6 * FIN_S
ROOF_SPOT = (FIN_C.x - 1.2, FIN_FRONT + 0.9)
BB2_C = Vector((12.4, 3.0, 6.6))
BB2_W, BB2_H = 7.2, 7.2 * 9 / 16
cam18_loc = Vector((0.5, -17.5, 4.2))
pts18 = [Vector((x_, FIN_FRONT, z_)) for x_ in (-FIN_W / 2, FIN_W / 2) for z_ in (0.0, TOP6 + 1.2)] + \
        [BB2_C + Vector((dx * BB2_W / 2, 0, dz * BB2_H / 2)) for dx in (-1, 1) for dz in (-1, 1)] + \
        [Vector((FX_SPOT[0], FX_SPOT[1], 0.0)), Vector((FIN_C.x, FIN_FRONT - FIN_D - 1.5, 0.0))]
cam18 = (cam18_loc, *k.fit(cam18_loc, pts18, margin=1.05))
print("FINALE cam18", round(cam18[2]), "mm")

# ================================================================== performance
T = {}
wordf = lambda n, w, nth=0: T[n] + F(k.word(n, w, nth) * FPS)
# ---- S16/S17 the product (2D frames in post): he is out of every shot, idling off frame
T[8] = 1
T[9] = T[8] + F((k.dur(8) + 0.9) * FPS)
S18_CUT = T[9] + F((k.dur(9) + 1.0) * FPS)
off16 = perf.then("Breathing Idle", length=max(20, S18_CUT - int(perf.end) - 2), face=0, at=OFF_SPOT, in_place=1.0)
# ---- S18 he swings in, webs INSPECTION back, the building rises; then up onto the roof
P18 = Vector((-17.0, -1.0, 13.0))                           # off frame: high over the west arm's road
f_18 = face_to(P18, FX_SPOT)
zip18 = perf.then(HANG, frm=20, length=42, face=f_18, in_place=1.0, at=(P18.x, P18.y))
land18 = k.touch(f_18, FX_SPOT)
T[10] = int(zip18.start) + 6
FBLD = face_to(FX_SPOT, FIN_C)
push18 = perf.then("Standing 2H Magic Attack 01", frm=4, to=60, speed=0.9, blend=10, face=FBLD + 10)
R0 = int(push18.start) + 22                                 # INSPECTION slides back in
HOLD_F = max(wordf(10, "inspection"), R0 + 18)             # it locks in (glow); the floors snap up
watch18 = perf.then("Breathing Idle", length=max(40, HOLD_F + 150 - int(perf.end)), blend=10, face=FBLD)
SUNRISE = HOLD_F + 40
f_rf = face_to(FX_SPOT, ROOF_SPOT)
shoot18b = k.shoot(f_rf)
zip18b = k.zip_(16.0, f_rf)
land18b = k.touch(f_rf, ROOF_SPOT)
# ---- S19 on the roof: turns to the camera, the call to action, a peace sign, holds
F19 = 0.0                                                    # faces -y: the camera south of the roof
T[11] = int(land18b.start) + UPRIGHT + 6
talk19 = k.talk_until(wordf(11, "sign") - 4, face=F19, clips=CALM)
PHONE = "CMU 79_36 answering the phone"                      # its hand comes up beside the head: the peace sign (fingers on top)
pk19 = perf.extreme(PHONE, R_HAND, (0, 0, 1), 10, 120)
up19 = perf.then(PHONE, frm=max(1, pk19 - 24), to=pk19, blend=10, face=F19, in_place=1.0)
n19 = max(30, T[11] + F((k.dur(11) + 0.8) * FPS) + 3 * FPS - int(perf.end) + 6)
peace19 = perf.then(PHONE, frm=pk19, to=pk19 + 1, speed=1.0 / n19, blend=4, face=F19, in_place=1.0)
perf.build()
DEMO_CUT = T[11] + F((k.dur(11) + 0.8) * FPS)
END = DEMO_CUT + 3 * FPS
sc.frame_end = END
print("T", T, "S18", S18_CUT, "R0", R0, "HOLD", HOLD_F, "DEMO", DEMO_CUT, "END", END)

# ------------------------------------------------------------------ body to camera on every talk beat
R_CAM = Vector((ROOF_SPOT[0] + 0.6, ROOF_SPOT[1] - 3.6, TOP6 + 1.55))
AIMS = [([talk19], R_CAM)]
aim_spans = [(int(first(gs[0]).start), int(final(gs[-1]).end), Vector(loc)) for gs, loc in AIMS]


def facing_cam(f):
    for a_, b_, p in aim_spans:
        if a_ <= f <= b_:
            return (p.x, p.y)
    h = perf.bone_world(HIPS, f)
    return (h.x, h.y - 5)


flat = lambda gs: [c_ for g in gs for c_ in (g.cycles if hasattr(g, "cycles") else [g])]
square_err = perf.square_up(flat(sum((gs for gs, _ in AIMS), [])), facing_cam)

# ------------------------------------------------------------------ heights (the roof at the end)
def low_rel(clip):
    return min(min(perf.bone_world(b, f).z for b in ("mixamorig:LeftToeBase", "mixamorig:RightToeBase"))
               for f in range(int(clip.start) + 4, int(clip.end) - 2, 6))


def between(a, b):
    i0, i1 = perf.clips.index(first(a)), perf.clips.index(final(b))
    return perf.clips[i0:i1 + 1]


roof_clips = between(land18b, peace19)
HEIGHTS = [(int(c_.start), (int(n.start) - 1) if n is not None else END, TOP6 - low_rel(c_), c_)
           for c_, n in zip(roof_clips, roof_clips[1:] + [None])]
zk = []
for kk, (a_, b_, z, clip) in enumerate(HEIGHTS):
    prev = HEIGHTS[kk - 1] if kk else None
    if prev is not None and prev[1] + 1 >= a_ and getattr(clip, "at", None) is None and clip.blend > 1:
        zk += [(a_, prev[2], "inout"), (a_ + int(clip.blend), z, "const")]
    else:
        zk.append((a_, z, "const"))
perf.root_z([(1, 0.0, "const")] + zk)

# ------------------------------------------------------------------ travel
k.travels = []
hp = k.hp
# S18: off frame, swings in down to the wreck's left corner
s18, e18 = P18, hp(int(land18.start))
p18 = k.bez(s18, s18 + Vector((4.0, -6.0, -2.0)), e18 + Vector((-3.0, 3.0, 5.0)), e18)
A18 = Vector((FX_SPOT[0] + 1.5, FIN_FRONT - 0.05, 3.5))
k.lean(int(zip18.start) + 1, int(land18.start) - 3, A18 - p18(0.5))
k.travel(p18, int(zip18.start), int(land18.start) - 1, name="S18")
A18b = Vector((ROOF_SPOT[0], ROOF_SPOT[1] + 1.0, TOP6 + 0.3))
k.web_zip(zip18b, land18b, A18b, lift=1.5, name="S18roof")
for fa, fb, nm in k.travels:
    k.path_hits(fa, fb, nm)

# ------------------------------------------------------------------ feet
LAND_SETTLE = 6
perf.contact(int(land18b.start) + LAND_SETTLE, END, floor=TOP6)
air = [(a_, b_) for a_, b_, _ in k.travels] + [(int(l_.start), int(l_.start) + LAND_SETTLE) for l_ in (land18, land18b)]
lock_err = perf.ground_lock(int(land18.start), int(zip18b.start) - 1, skip=air, step=1, floor=FL8)
hips = lambda f: perf.bone_world(HIPS, int(f))

# ------------------------------------------------------------------ webs
webs = fx.WebShots(rig, fx.collection("Webs"))
for nm, sh, zc, lc, A in (("S18roof", shoot18b, zip18b, land18b, A18b),):
    W = int(perf.clip_frame(sh, k.hit_pk))
    webs.shot(f"Web_{nm}", R_HAND, (lambda p: (lambda f: p))(Vector(A)), W - 4, W, int(lc.start) - 3)
    shot.sfx("web_thwip", W - 3)
    shot.sfx("cartwheel_whoosh", int(zc.start) + 4)
    shot.sfx("landing_thud", int(lc.start) + 5)
webs.shot("Web_S18", R_HAND, lambda f: A18, int(zip18.start) - 2, int(zip18.start), int(land18.start) - 3)
shot.sfx("cartwheel_whoosh", int(zip18.start) + 4)
shot.sfx("landing_thud", int(land18.start) + 5)

# ================================================================== S19 the hand: fingers (the peace sign)
FING = ("Index", "Middle", "Ring", "Pinky")


def finger_pose(open_=(), spread=0.0, thumb_in=True):
    q = {}
    for fn in FING:
        for seg, ang in zip("123", (62, 80, 55)):
            rot = Quaternion((1, 0, 0), math.radians(0.0 if fn in open_ else ang))
            if fn in open_ and spread and seg == "1":
                rot = Quaternion((0, 0, 1), math.radians(spread * (1 if fn == "Index" else -1))) @ rot
            q[f"mixamorig:RightHand{fn}{seg}"] = rot
    for seg, ang in zip("123", (25, 30, 25) if thumb_in else (0, 0, 0)):
        q[f"mixamorig:RightHandThumb{seg}"] = Quaternion((0, 0, 1), math.radians(-ang))
    return q


POSES = {"flat": finger_pose(FING, thumb_in=False), "peace": finger_pose(("Index", "Middle"), spread=9.0)}
f_act = bpy.data.actions.new("FingerPoses")
ad = rig.animation_data
keep_action = ad.action
ad.action = f_act
if hasattr(ad, "action_slot") and f_act.slots:
    ad.action_slot = f_act.slots[0]


def key_pose(frame, name):
    for bn, q in POSES[name].items():
        pb_ = rig.pose.bones[bn]
        pb_.rotation_mode = "QUATERNION"
        pb_.rotation_quaternion = q
        pb_.keyframe_insert("rotation_quaternion", frame=int(frame))


PEACE = wordf(11, "sign")
for f_, p_ in ((PEACE - 8, "flat"), (PEACE - 2, "peace"), (END - 2, "peace")):
    key_pose(f_, p_)
if hasattr(f_act, "slots") and f_act.slots and not ad.action_slot:
    ad.action_slot = f_act.slots[0]
ad.action = keep_action
fin_tr = ad.nla_tracks.new()
fin_tr.name = "ZZ Finger poses"
a_, b_ = PEACE - 14, END
st = fin_tr.strips.new(f"Fingers{a_}", int(a_), f_act)
if hasattr(st, "action_slot") and f_act.slots:
    st.action_slot = f_act.slots[0]
st.action_frame_start, st.action_frame_end = a_, b_
st.frame_start, st.frame_end = a_, b_
st.blend_type = "REPLACE"
st.use_auto_blend = False
st.extrapolation = "NOTHING"
st.use_animated_influence = True
for f_, v_ in ((a_, 0.0), (a_ + 6, 1.0), (b_ - 6, 1.0), (b_, 0.0)):
    st.influence = v_
    st.keyframe_insert("influence", frame=int(f_))
HD = lambda f: perf.bone_world("mixamorig:Head", f)

# ================================================================== S18 the wreck, the lock, the rise, the sunrise
fcoll = fx.collection("Finale")
bld = city.Building("Finale", FIN_C, width=FIN_W, depth=FIN_D, floors=FIN_N, storey=FIN_S, facade_img=os.path.join(ST, "facade_floor.png"),
                    coll=fcoll)
for o in list(fcoll.objects):                               # the wreck only exists for S18/S19
    if o.type == "MESH" and o.name.endswith("_Body") and not any(o.name.startswith(f"Finale_F{i}") for i in (4, 5)):
        anim.visible(o, [(1, False), (S18_CUT, True)])
LABELS = [os.path.join(SCR, f"tower_{i}.png") for i in range(4)] + [img("floor_scale"), img("floor_judgment")]
labs = []
for i in range(4):
    lab = bld.light(i, S18_CUT, LABELS[i])
    anim.keys(lab, "scale", [(S18_CUT, Vector((1, 1, 1)), "const"), (S18_CUT + 9, Vector((1, 1, 1)), "const")])
    anim.keys(bld.mix[i].inputs[0], "default_value", [(S18_CUT - 1, 0.15, "const"), (S18_CUT, 0.15, "const"), (S18_CUT + 9, 0.15, "const")])
    labs.append(lab)
rp = random.Random(4)
SQ = 0.42
g0 = bld.floors[0]
G_HOME = g0.location.copy()
PULL = Vector((0.14, -1, 0)).normalized()
G_OUT = G_HOME + PULL * (FIN_D + 1.5) + Vector((0, 0, -0.2))
anim.keys(g0, "location", [(1, G_OUT, "const"), (R0, G_OUT, "inout"), (R0 + 16, G_HOME, "out"), (R0 + 20, G_HOME + Vector((0, 0, 0.05)), "in"),
                           (R0 + 24, G_HOME)])
anim.keys(g0, "rotation_euler", [(1, Vector((0.04, 0, -0.08)), "const"), (R0, Vector((0.04, 0, -0.08)), "inout"), (R0 + 16, Vector((0, 0, 0)))])
crack2 = city.sign("InspectionCrack", img("crack"), Vector((FIN_C.x + 2.6, FIN_FRONT - 0.04, 1.2)), Vector((0, -1, 0)), 1.6, aspect=1.0,
                   offset=0.0, alpha=True, coll=fcoll)
parent_keep(crack2, g0, R0 + 30)
anim.visible(crack2, [(1, False), (S18_CUT, True)])
lab0_bsdf = next(n for n in labs[0].data.materials[0].node_tree.nodes if n.type == "BSDF_PRINCIPLED")
anim.keys(lab0_bsdf.inputs["Emission Strength"], "default_value", [(1, 1.2, "const"), (HOLD_F - 2, 1.2, "lin"), (HOLD_F + 3, 9.0, "out"),
                                                                  (HOLD_F + 24, 1.6, "inout")])
anim.keys(bld.mix[0].inputs[0], "default_value", [(HOLD_F - 2, 0.15, "lin"), (HOLD_F + 4, 0.95, "out")])
shot.sfx("block_thud", HOLD_F)
for i in range(1, 4):
    fl = bld.floors[i]
    home = fl.location.copy()
    crushed = Vector((home.x + rp.uniform(-0.25, 0.25), home.y + rp.uniform(-0.3, 0.3), (i - 1) * FIN_S * SQ + FIN_S * SQ / 2 + 0.02))
    tilt = Vector((rp.uniform(-0.06, 0.06), rp.uniform(-0.1, 0.1), rp.uniform(-0.08, 0.08)))
    up = HOLD_F + 6 + (i - 1) * 5
    anim.keys(fl, "location", [(1, crushed, "const"), (up, crushed, "back"), (up + 10, home, "out"), (up + 13, home + Vector((0, 0, 0.06)), "in"),
                               (up + 16, home)])
    anim.keys(fl, "rotation_euler", [(1, tilt, "const"), (up, tilt, "out"), (up + 10, Vector((0, 0, 0)))])
    anim.keys(fl, "scale", [(1, Vector((1.03, 1.04, SQ)), "const"), (up, Vector((1.03, 1.04, SQ)), "out"), (up + 9, Vector((1, 1, 1)), "back")])
    shot.sfx("block_thud", up + 10)
for i in range(1, 4):
    lf = SUNRISE + 20 + i * 12
    anim.keys(bld.mix[i].inputs[0], "default_value", [(lf, 0.15, "lin"), (lf + 8, 0.9, "out")])
    shot.sfx("ui_pop", lf)
NEW = [(4, SUNRISE + 80), (5, SUNRISE + 98)]
for i, f_ in NEW:
    fl = bld.floors[i]
    home = fl.location.copy()
    bld.light(i, f_ + 2, LABELS[i])
    for o in [fl] + list(fl.children_recursive):
        if o.type == "MESH" and not o.name.endswith(("_L4", "_L5")):
            anim.visible(o, [(1, False), (f_ - 16, True)])
    anim.keys(fl, "location", [(1, home + Vector((0, 0, 12.0)), "const"), (f_ - 16, home + Vector((0, 0, 12.0)), "in"), (f_, home, "out"),
                               (f_ + 3, home + Vector((0, 0, 0.1)), "in"), (f_ + 6, home)])
    shot.sfx("block_thud", f_)
cash_mat = fx.material("CashSide", (0.22, 0.75, 0.32), rough=0.55, emit=0.5)
CASH_F = SUNRISE + 112
for kk, dx in enumerate((-5.0, -3.6, 3.6, 5.0)):
    rest = Vector((FIN_C.x + dx, FIN_FRONT + 1.6, TOP6 + 0.6))
    ob = box(f"Cash{kk}", (1.2, 1.0, 1.1 + 0.3 * (kk % 2)), rest, cash_mat, fcoll)
    anim.visible(ob, [(1, False), (CASH_F + kk * 3, True)])
    anim.keys(ob, "location", [(CASH_F + kk * 3, rest + Vector((0, 0, 6.0)), "in"), (CASH_F + kk * 3 + 9, rest, "back")])
shot.sfx("cash_flutter", CASH_F)
rr = random.Random(9)
chunk_mat = fx.material("ConcreteChunk", (0.42, 0.4, 0.38), rough=0.9)
for kk in range(14):
    s_ = rr.uniform(0.15, 0.38)
    p_ = Vector((FIN_C.x + rr.uniform(-5.5, 5.5), FIN_FRONT - rr.uniform(0.3, 2.6), s_ * 0.3 - 0.08))
    if (p_.xy - Vector(FX_SPOT)).length < 1.2:
        continue
    ch_ = box(f"Chunk{kk}", (s_, s_ * rr.uniform(0.6, 1.2), s_ * rr.uniform(0.5, 1.0)), p_, chunk_mat, fcoll)
    ch_.rotation_euler = (0, 0, rr.uniform(0, 3))
    anim.visible(ch_, [(1, False), (S18_CUT, True)])
webs.shot("Web_PushL", L_HAND, lambda f: g0.matrix_world @ Vector((-FIN_W / 2 + 1.2, -FIN_D / 2 - 0.05, 0.2)), R0 - 14, R0 - 6, R0 + 16)
webs.shot("Web_PushR", R_HAND, lambda f: g0.matrix_world @ Vector((-FIN_W / 2 + 2.4, -FIN_D / 2 - 0.05, 0.2)), R0 - 14, R0 - 6, R0 + 16)
shot.sfx("web_thwip", R0 - 13)
# the billboard screen to the right of the site: dark until the very end, then LiveReview + its address
bb_dark = city.sign("BB2Dark", img("site_blank"), BB2_C, Vector((0, -1, 0)), BB2_W, emit=0.0, frame="led", offset=0.0)
bb_dark.data.materials[0] = fx.material("BB2Off", (0.02, 0.02, 0.03), rough=0.3)
BB_ON = DEMO_CUT - 45
demo = city.sign("BB2Demo", img("billboard_url"), BB2_C, Vector((0, -1, 0)), BB2_W, emit=1.4, offset=0.01)      # just the address, no footage
anim.visible(demo, [(1, False), (BB_ON, True)])
for o in (bb_dark,) + tuple(bb_dark.children):
    anim.visible(o, [(1, False), (S18_CUT, True)])
for kk, dx in enumerate((-2.4, 2.4)):
    pole = box(f"BB2Pole{kk}", (0.3, 0.3, BB2_C.z - BB2_H / 2 + 0.2), (BB2_C.x + dx, BB2_C.y + 0.4, (BB2_C.z - BB2_H / 2) / 2), steel)
    anim.visible(pole, [(1, False), (S18_CUT, True)])
shot.sfx("ui_pop", BB_ON)
# the sky: pre-dawn at the S18 cut; the sun comes up behind the building; full sunrise in S19
sky = next(n for n in sc.world.node_tree.nodes if n.type == "TEX_SKY")
bg = next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND")
DAY = dict(elev=6.0, az=-60.0, energy=7.2, color=(1.0, 0.66, 0.40), bgs=0.18)
DAWN = dict(elev=-1.5, az=92.0, energy=1.6, color=(0.62, 0.7, 1.0), bgs=1.6)
RISE = dict(elev=4.5, az=92.0, energy=6.0, color=(1.0, 0.6, 0.32), bgs=0.3)
FULL = dict(elev=9.0, az=70.0, energy=7.0, color=(1.0, 0.78, 0.55), bgs=0.2)


def light_key(f_, L, ease="const"):
    anim.key(sky, "sun_elevation", int(f_), math.radians(L["elev"]), ease=ease)
    anim.key(sky, "sun_rotation", int(f_), math.radians(L["az"]), ease=ease)
    anim.key(bg.inputs[1], "default_value", int(f_), L["bgs"], ease=ease)
    lamp_el = max(L["elev"], 7.0)
    anim.key(sun, "rotation_euler", int(f_), Vector((math.radians(90 - lamp_el), 0, math.radians(L["az"] + 90))), ease=ease)
    anim.key(sun.data, "energy", int(f_), L["energy"], ease=ease)
    anim.key(sun.data, "color", int(f_), Vector(L["color"]), ease=ease)


light_key(1, DAY)
light_key(S18_CUT - 1, DAY)
light_key(S18_CUT, DAWN)
light_key(SUNRISE, DAWN, ease="inout")
light_key(SUNRISE + 120, RISE, ease="inout")
light_key(T[11] - 21, RISE)
light_key(T[11] - 20, FULL)

# ================================================================== cameras
cam = k.camera()
CUTS = []
# S16/S17: 2D (post) — the camera parks on the lot (frames replaced by the boards)
k.at(T[8], cam18[0], cam18[1], "lin", cut=True)
CUTS.append(("S16/S17 (2D)", T[8]))
# S18: the wide from ground level; S19 the rooftop medium shot, then the helicopter pull-out; the demo on the billboard
k.read_shot(S18_CUT, int(land18b.start) + 40, cam18, drift=0.6)
rtgt = lambda f: HD(f) + Vector((0, 0, -0.25))
cam.lens(int(land18b.start) + 41, 35, "const")
k.at(int(land18b.start) + 41, R_CAM, rtgt(T[11]), "lin", cut=True)
k.at(PEACE + 6, R_CAM + Vector((0.1, -0.3, 0.0)), rtgt(PEACE), "inout")
k.at(DEMO_CUT - 2, Vector((FIN_C.x + 9.0, FIN_FRONT - 26.0, TOP6 + 14.0)), Vector((FIN_C.x + 4.0, FIN_C.y, 6.0)), "inout")
cam.lens(PEACE + 6, 35, "inout")
cam.lens(DEMO_CUT - 2, 28, "inout")
d_loc = BB2_C + Vector((0, -10.0, -0.6))
d_tgt, d_lens = k.fit(d_loc, [BB2_C + Vector((dx * BB2_W / 2, 0, dz * BB2_H / 2)) for dx in (-1, 1) for dz in (-1, 1)], margin=1.08)
k.read_shot(DEMO_CUT, END, (d_loc, d_tgt, d_lens), drift=0.2)
CUTS.append(("demo", DEMO_CUT))
for f_ in (int(land18.start) + 5, int(land18b.start) + 5, HOLD_F):
    cam.shake(f_, amp=0.04, dur=8)
for i, f_ in NEW:
    cam.shake(f_, amp=0.04, dur=8)
FSTOPS = [(1, 8.0), (T[8], 8.0), (S18_CUT, 8.0), (int(land18b.start) + 41, 4.0), (PEACE + 7, 8.0), (DEMO_CUT, 8.0)]
for f_, v_ in sorted(FSTOPS):
    anim.key(cam.cam.data.dof, "aperture_fstop", int(f_), v_, ease="const")
office.face_camera(cam.cam, [(int(first(talk19).start) + 4, int(final(talk19).end) - 2)], amount=0.55)
fx.char_lights(rig, cam.cam, key=170.0, rim=340.0)
from pipeline import face
eyes = face.Lenses(bpy.data.objects["MilesMasked"])
for f_, w_ in ((1, dict(Squint=0.85)), (S18_CUT, dict(Squint=0.0, Angry=0.4)), (HOLD_F, dict(Angry=0.0, Wide=0.8)),
               (T[11], dict(Wide=0.3)), (PEACE, dict(Wide=0.0, Squint=0.45))):
    eyes.set(f_, **w_)
eyes.blinks(1, END, every=95)
webs.bake(range(1, END + 1))
for o in fx.collection("Webs").objects:
    if o.type == "MESH":
        o.data.materials[0] = fx.material("Web_Line", (0.95, 0.97, 1.0), rough=0.35, emit=0.9)

# ================================================================== captions (laid over in post) + the 2D product frames
OVER = []                                                       # no captions: subtitles come from 06_assemble; the URL is on the billboard
w8 = lambda w: wordf(8, w)
w9 = lambda w: wordf(9, w)
json.dump(dict(fps=FPS, end=END, captions=[dict(f0=a_, f1=b_, text=t_, row=r_) for a_, b_, t_, r_ in OVER],
               boards=dict(s16=[T[8], T[9] - 1], s17=[T[9], S18_CUT - 1],
                           s16_title=w8("engineers"), s16_items=[w8("issue"), w8("slide"), w8("quick"), w8("conversations"), w8("livy")],
                           s17_title=w9("agents"),
                           # item 2 = the Teams / Slack stills (1 s then 2 s, on the words "Microsoft" and "Slack"); MCP waits for Slack's 2 s
                           s17_items=[w9("gates"), w9("integrations"), max(w9("mcp"), w9("slack") + 2 * FPS)],
                           s17_seq=[[w9("microsoft"), "teams_integration.png", w9("slack")],
                                    [w9("slack"), "slack_integration.png", w9("slack") + 2 * FPS]])),
          open(os.path.join(paths.ROOT, "build", "street_part2_b_overlays.json"), "w"), indent=1)

# ------------------------------------------------------------------ parked cars
guard = life.Guard(cam.cam, lambda f: rig.matrix_world @ rig.pose.bones[HIPS].head, (1, END), step=2)
cars = life.CarKit()
rl = random.Random(21)
parked = 0
for axis in ("x", "y"):
    for side in (-1, 1):
        u = -47.0 + rl.uniform(0, 4)
        while u < 47.0:
            ok_zone = abs(u) > 12.5 and not (axis == "x" and -40.0 < u < -12.0)
            if ok_zone and rl.random() < 0.6:
                p_ = Vector((u, side * 4.25, 0.4)) if axis == "x" else Vector((side * 4.25, u, 0.4))
                if all(guard.ok(f, p_, r_sub=2.6, r_cam=2.6, r_line=1.0) for f in guard.cam):
                    car = cars.spawn(rl.randrange(10), f"Parked{parked}")
                    heading = Vector((1, 0, 0)) * -side if axis == "x" else Vector((0, 1, 0)) * side
                    car.place(Vector((p_.x, p_.y, -0.08)), heading)
                    parked += 1
            u += rl.uniform(5.6, 7.5)
print("LIFE parked", parked)

# ------------------------------------------------------------------ checks + audit data + finish
k.visible_report(END)
v3 = lambda v: [round(float(x), 3) for x in v]
json.dump(dict(travel=[(a_, b_, n_) for a_, b_, n_ in k.travels],
               talks=[(int(first(g).start + first(g).blend) + 4, int(final(g).end) - 12, v3(loc)) for gs, loc in AIMS for g in gs],
               reads=[],
               webs=[o.name for o in fx.collection("Webs").objects if o.type == "MESH"]),
          open(os.path.join(paths.ROOT, "build", "street_part2_b_audit.json"), "w"))
VO_CUES = {n: T[n] for n in (8, 9, 10, 11)}
shot.finish(NAME, exposure=-0.35, samples=24, view="AgX", grade="AgX - Punchy",
            markers=[(f"vo {n}", f) for n, f in VO_CUES.items()] + [
                ("S16 engineers (2D)", T[8]), ("S17 agents (2D)", T[9]),
                ("S18 rebuild", S18_CUT), ("S19 call to action", T[11]), ("demo", DEMO_CUT), ("end", END)])
fx.cine_grade(sc)
bpy.ops.wm.save_mainfile()
print("CUTS", CUTS)
print(f"STREET2B frames 1-{END} ({END / FPS:.1f}s)  ground-lock {lock_err * 100:.1f} cm  square {square_err:.1f}")
