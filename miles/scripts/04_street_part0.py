"""Street part 0 (36.7 s, its own video): the opening that plays BEFORE part 1. Spidey presents the problem and Meta's answer,
then zips to the mural and lands on its ledge (the old part 1 S0), which is where part 1 picks up.

    0:00  S-A  the volume board (Incoming MRs 12 -> 482 against Reviewed 3 -> 12, two chips) on the east arm; four reviewers
               under it, M R cards piling up on them; a RED high-risk card slides past on "skip" and nobody looks up
    0:13  S-B  he zips across the street to the Meta billboard (the official logo); "the machine": a belt, the part 2 robot arm
               stamps the low-risk cards AUTO-APPROVED and they leave; a high-risk card is carried to a human reviewer
    0:22  S-C  zips up the avenue to a catwalk on the west tower: three white result boards (98 % / 30 % / 33 %), each lit on its number
    0:30       "faster and safer, while also reviewing less"
    0:35  S-D  "Here's why inspection matters": a long web line down the avenue to the mural; part 1 starts on its ledge

Review rules as in part 1 (scripts/check_rules.py): web travel is a straight pull on the line, one body angle, no spins, no hangs;
he stands at the LEFT edge of each board facing the lens; one focal point per frame. Voice-over = line 14 of assets/audio/vo_street
(`assets/audio/vo_street_part0` is a symlink to it); every scene is keyed to its spoken words.

    python3 scripts/03f_street_part0_signs.py
    blender -b build/character.blend --python scripts/04_street_part0.py        # -> build/street_part0.blend (+ _audit.json, _overlays.json)
    blender -b build/street_part0.blend --python scripts/check_rules.py -- street_part0
The JOIN: this video's last frame (1101) is old part 1 frame OLD_LAND1 + JOIN - 1 (the mural's presenter shot, mid-landing: same camera,
pose, light), so part 1 continues with its own old frame OLD_LAND1 + JOIN (printed on every build as "JOIN: ...").
"""
import bpy, bmesh, os, re, sys, math, random, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mathutils import Vector, Matrix
from pipeline import paths, anim, fx, shot, city, swing, streetkit, life, props, crew
from pipeline.mixamo import Performer, ClipGroup
from pipeline.shot import L_HAND, R_HAND, HIPS
from pipeline.streetkit import first, final, face_to, Z, SHOOT, HANG

FPS = 30
NAME = "street_part0"
sc = bpy.context.scene
ST, ST0 = (os.path.join(paths.ROOT, "assets", d) for d in ("street", "street0"))
img = lambda n: os.path.join(ST, n + ".png")                 # part 1's signs (the mural)
img0 = lambda n: os.path.join(ST0, n + ".png")
seq0 = lambda n: os.path.join(ST0, n, "f_0001.png")
VO = json.load(open(os.path.join(paths.ROOT, "assets", "audio", "vo_street", "lines.json")))
F = lambda x: int(round(x))
UPRIGHT = 30
END = F(36.7 * FPS)                                           # 1101 frames = the take (36.68 s) + a breath
OLD = json.load(open(os.path.join(paths.ROOT, "build", "street_part_1_final_cues.json")))["cues"]
OLD_LAND1 = F(OLD["vo 1"] * FPS) - UPRIGHT                    # old part 1: the landing on the ledge starts here (cut to the presenter shot)
OLD_ZIP2 = F(OLD["S2 billboard"] * FPS)                       # ... the presenter shot holds until here (its tiny push-in is keyed over it)
JOIN_AIM = 24                                                 # frames of the landing this video shows (the last frame is old part 1 frame OLD_LAND1 + JOIN - 1)

# ------------------------------------------------------------------ set: the same city, sunset and look as part 1
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
fx.suit_look(rig)                                           # (physical_shading(rig) is a no-op on the armature) real suit gloss + red detail
office = props.Office(rig)
for n in ("Watch_Band", "Watch_Face"):
    o = bpy.data.objects.get(n)
    if o:
        o.hide_render = o.hide_viewport = True
perf = Performer(rig).place(x=0, y=0, face=0)
k = streetkit.Kit(c, rig, perf, VO)
wordf = lambda w, nth=0: 1 + F(k.word(14, w, nth) * FPS)       # the scene frame a spoken word starts on (the take starts on frame 1)
signs = fx.collection("Signs")
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


def show(ob, spans):
    """visible per spans [(frame, bool), ...], the object and everything parented to it."""
    for o in (ob,) + tuple(ob.children_recursive):
        anim.visible(o, spans)


# ================================================================== the mural (S-D, the end: copied from part 1 so the join matches)
GB_W, GB_H = 7.2, 4.05
SOUTH = lambda x, z=6.0: c.wall((x, 0.0, z), (0, -1, 0))
WALL_G = SOUTH(-18.0)
best = None
for gx in (-18.0, -20.0, -16.0, -22.0, -24.0, -14.0, -26.0, -28.0):
    fx_, hit = city.flat_spot(c, [gx], 0.0, -1, 6.0, GB_W * 0.8, tol=0.12)
    if hit is None:
        continue
    found = False
    for dx in (1.4, 0.4, 2.4, -0.6, 3.4):
        cand = (Vector((gx, hit.point.y, 4.9)), ((gx + dx, hit.point.y + 9.4, 2.6), (gx + 1.1, hit.point.y, 3.5)), hit)
        best = best or cand
        if k.clear_view(cand[1][0], k.board_pts(cand[0] + hit.normal * 0.45, hit.normal, GB_W, GB_H)):
            best, found = cand, True
            break
    if found:
        break
G_C, mural_cam, WALL_G = best
print("BOARD1", G_C, mural_cam)
city.sign("Board1", img("wallboard_generated"), G_C, WALL_G.normal, GB_W, offset=0.45, emit=0.5, frame="billboard")
LEDGE_TOP = G_C.z + GB_H / 2 + 0.12 + 0.1                     # a service ledge on top of the wall board (what he lands and presents on)
box("Board1Ledge", (GB_W + 0.3, 1.25, 0.1), (G_C.x, WALL_G.point.y + WALL_G.normal.y * 0.68, LEDGE_TOP - 0.05),
    fx.material("Ledge", (0.1, 0.11, 0.12), rough=0.45, metallic=0.7))
TOP1 = (G_C.x + 2.5, WALL_G.point.y + WALL_G.normal.y * 0.85)       # on the board's top ledge, screen-LEFT corner
s1 = k.presenter(G_C + WALL_G.normal * 0.45, WALL_G.normal, GB_W, GB_H, TOP1, LEDGE_TOP)

# ================================================================== S-A: the volume board (free-standing, east arm south sidewalk)
A_BX, A_BY, A_BZ, A_W = 9.8, -8.1, 5.8, 7.2           # (street lamps on this sidewalk: x -6.7, 16.5, 25.7: none in front of the board)
A_H = A_W * 9 / 16
A_N = Vector((0, 1, 0))                                       # faces the north sidewalk, where the camera is
A_C = Vector((A_BX, A_BY, A_BZ))
board_a = city.sign("BoardMR", seq0("board_mr"), A_C, A_N, A_W, emit=0.7, frame="billboard", offset=0.0, seq=(460, 1))
for kk, dx in enumerate((-2.9, 2.9)):                          # two posts and a back frame
    box(f"APost{kk}", (0.3, 0.3, A_BZ - A_H / 2 + 0.2), (A_BX + dx, A_BY - 0.3, (A_BZ - A_H / 2 + 0.2) / 2), steel)
REV_X = [A_BX - 2.55, A_BX - 0.85, A_BX + 0.85, A_BX + 2.55]    # the reviewers, one every 1.7 m
REV_Y = A_BY + 1.35
A_SPOT = (A_BX + A_W / 2 + 0.9, A_BY + 1.0)                    # screen-LEFT of the board (the camera looks south: left = +x)
pts_rev = [Vector((x_, REV_Y, z_)) for x_ in (REV_X[0] - 0.5, REV_X[-1] + 0.5) for z_ in (0.0, 3.6)]
camA = k.presenter(A_C, A_N, A_W, A_H, A_SPOT, 0.0, lens_min=24.0, extra=pts_rev)

# ================================================================== S-B: the Meta billboard + the machine (north sidewalk, in front of the facade)
B_BX, B_BY, B_BZ, B_W = 10.5, 8.35, 4.05, 4.8          # (the lamp on this sidewalk is at x 17.0, behind the human)
B_H = B_W * 9 / 16
B_N = Vector((0, -1, 0))
B_C = Vector((B_BX, B_BY, B_BZ))
meta_a = city.sign("MetaA", img0("meta_a"), B_C, B_N, B_W, emit=0.8, frame="billboard", offset=0.0)
meta_b = city.sign("MetaB", img0("meta_b"), B_C + B_N * 0.02, B_N, B_W, emit=0.8, offset=0.0)
BELT_Y, BELT_TOP = 6.35, 0.95
X_IN, X_ARM, X_OUT = B_BX - 2.5, B_BX - 0.2, B_BX + 3.0                           # where cards come on, are stamped, and leave the belt
B_SPOT = (B_BX - B_W / 2 - 0.9, B_BY - 1.2)                    # screen-LEFT of the board (the camera looks north: left = -x)
HUM = (X_OUT + 1.6, BELT_Y - 0.1)                              # the human reviewer, right of the belt
mat_belt = fx.material("Belt", (0.1, 0.11, 0.12), rough=0.5, metallic=0.5)
box("BeltBody", (X_OUT - X_IN + 0.6, 0.85, BELT_TOP - 0.06), ((X_IN + X_OUT) / 2, BELT_Y, (BELT_TOP - 0.06) / 2), mat_belt)
box("BeltTop", (X_OUT - X_IN + 0.6, 0.8, 0.06), ((X_IN + X_OUT) / 2, BELT_Y, BELT_TOP - 0.03), fx.material("BeltRubber", (0.03, 0.03, 0.035), rough=0.9))
for kk, dx in enumerate(range(int(X_IN), int(X_OUT) + 1, 1)):  # rollers' ticks: it reads as a conveyor
    box(f"BeltTick{kk}", (0.05, 0.82, 0.02), (dx + 0.0, BELT_Y, BELT_TOP + 0.005), fx.material("BeltTick", (0.16, 0.17, 0.18), rough=0.7))
gate_m = fx.material("GateGreen", (0.1, 0.7, 0.3), rough=0.4, emit=1.2, emit_color=(0.2, 1.0, 0.45))
for kk, dy in enumerate((-0.55, 0.55)):                        # the gate the approved cards leave through
    box(f"GatePost{kk}", (0.12, 0.12, 1.9), (X_OUT, BELT_Y + dy, 0.95), gate_m)
box("GateBar", (0.14, 1.22, 0.14), (X_OUT, BELT_Y, 1.9), gate_m)
box("ArmPlate", (1.5, 1.2, 0.1), (X_ARM, BELT_Y + 1.7, 0.05), mat_belt)
for kk, dx in enumerate((-1.8, 1.8)):                          # the billboard hangs on a frame on the facade
    box(f"BPost{kk}", (0.3, 0.3, B_BZ - B_H / 2 + 0.2), (B_BX + dx, B_BY + 0.35, (B_BZ - B_H / 2 + 0.2) / 2), steel)
pts_mach = [Vector((x_, BELT_Y, z_)) for x_ in (X_IN - 0.4, HUM[0] + 0.6) for z_ in (-0.3, 2.6)]
camB = k.presenter(B_C, B_N, B_W, B_H, B_SPOT, 0.0, lens_min=24.0, extra=pts_mach)

# ================================================================== S-C: the three results on the west tower
TOWER_X, TOWER_Y, STAT_W = -8.82, 29.0, 4.4
STAT_H = STAT_W * 9 / 16
STAT_Z = [27.65, 24.45, 21.25]
CAT_Z = 22.85                                                 # the catwalk in the gap between the two lower boards
C_SPOT = (TOWER_X + 0.9, TOWER_Y - STAT_W / 2 - 0.5)          # beside the left edge (the camera looks west: left = low y)
C_N = Vector((1, 0, 0))
stat_obs = []
for i_, z_ in enumerate(STAT_Z):
    ob = city.sign(f"Stat{i_ + 1}", seq0(f"stat{i_ + 1}"), Vector((TOWER_X, TOWER_Y, z_)), C_N, STAT_W, emit=1.0, frame="led", offset=0.35, seq=(44, 1))
    stat_obs.append(ob)
stat_pts = [Vector((TOWER_X + 0.35, TOWER_Y + dx * STAT_W / 2, z_ + dz * STAT_H / 2)) for z_ in (STAT_Z[0], STAT_Z[-1]) for dx in (-1, 1) for dz in (-1, 1)]
camC = k.presenter(Vector((TOWER_X + 0.35, TOWER_Y, STAT_Z[1])), C_N, STAT_W, STAT_Z[0] - STAT_Z[-1] + STAT_H, C_SPOT, CAT_Z,
                   lens_min=18.0, extra=stat_pts)
# (the catwalk goes up after the camera is found: it would block the view of the lower board's top edge)
box("TowerCatwalk", (1.5, 10.0, 0.14), (TOWER_X + 0.65, TOWER_Y + 0.2, CAT_Z - 0.07), mat_belt)
box("TowerCatKick", (0.04, 10.0, 0.14), (TOWER_X + 1.38, TOWER_Y + 0.2, CAT_Z + 0.07), mat_belt)
for kk, y_ in enumerate((TOWER_Y - 3.8, TOWER_Y + 4.2)):
    box(f"TowerBracket{kk}", (1.3, 0.1, 0.1), (TOWER_X + 0.6, y_, CAT_Z - 0.45), mat_belt)

# ================================================================== the people: reviewers + the human
cw = crew.Crew()
SAD = crew.retarget(rig, bpy.data.actions["Sad Idle"], cw.src["boss"]["arm"])         # head down, shoulders down: "overwhelmed"
IDLE = crew.retarget(rig, bpy.data.actions["Breathing Idle"], cw.src["boss"]["arm"])
SHIRTS = [(0.1, 0.3, 0.5), (0.55, 0.12, 0.1), (0.15, 0.4, 0.2), (0.35, 0.18, 0.45)]
SKINS = [(0.55, 0.36, 0.24), (0.8, 0.55, 0.4), (0.3, 0.17, 0.1), (0.62, 0.42, 0.3), (0.45, 0.28, 0.18)]


def dress(u, shirt, pants, skin, boots=(0.04, 0.04, 0.04)):
    """Own colours per body part. (crew.person() looks parts up by the plain name 'Object_88': the clones are called
    'Object_88.001' and stay white, and Unit.show() would key the hard hat visible again: both handled here.)"""
    for o in u.objs:
        if o.type != "MESH" or "_" not in o.name:
            continue
        base = re.sub(r"\.\d+$", "", o.name.split("_", 1)[1])
        if base == "Object_94":                                   # the hard hat
            o.hide_render = o.hide_viewport = True
            continue
        col = {"Object_92": shirt, "Object_88": pants, "Object_90": skin, "Object_98": boots}.get(base)
        if col and o.material_slots:
            o.material_slots[0].link = "OBJECT"
            o.material_slots[0].material = fx.material(f"{u.wrap.name}_{base}", col, rough=0.7)


def show_person(u, spans):
    for o in u.objs:
        if not (o.type == "MESH" and re.sub(r"\.\d+$", "", o.name.split("_", 1)[1] if "_" in o.name else "") == "Object_94"):
            anim.visible(o, spans)


revs = []
for i_, x_ in enumerate(REV_X):
    u = crew.person(cw, f"Reviewer{i_}", (x_, REV_Y), face=(0, 1))
    dress(u, SHIRTS[i_], (0.06, 0.07, 0.12), SKINS[i_])
    cw._loop(u.arm, SAD, phase=0.17 * i_, repeat=40)
    revs.append(u)
human = crew.person(cw, "Human", (HUM[0], HUM[1]), face=(-0.5, -1))
dress(human, (0.9, 0.9, 0.88), (0.08, 0.1, 0.16), SKINS[1])
cw._loop(human.arm, IDLE, phase=0.3, repeat=40)
for u in revs:
    show_person(u, [(1, True), (wordf("meta") + 40, False)])    # (they stay out of the later shots)

# ================================================================== performance (clips are queued twice so the three landings fall on their marks)
FA = face_to(A_SPOT, camA[0])
FB = face_to(B_SPOT, camB[0])
FC = face_to(C_SPOT, camC[0])
F1 = face_to(TOP1, s1[0])
CARRY = {}
HAPPY = "MX Happy Hand Gesture" if "MX Happy Hand Gesture" in bpy.data.actions else "Happy Idle"


def queue(len_a, len_b, len_c):
    """The whole performance with talk lengths (len_*, frames of the free talking before each web shot)."""
    del perf.clips[:]
    P = {}
    P["talkA"] = k.talk(len_a, face=FA, at=A_SPOT)
    f_ab = face_to(A_SPOT, B_SPOT)
    P["shootAB"] = k.shoot(f_ab)
    P["zipAB"] = k.zip_((Vector((B_SPOT[0], B_SPOT[1], 0)) - Vector((A_SPOT[0], A_SPOT[1], 0))).length, f_ab)
    P["landB"] = k.touch(f_ab, B_SPOT)
    P["talkB"] = k.talk(len_b, face=FB)
    f_bc = face_to(B_SPOT, C_SPOT)
    P["shootBC"] = k.shoot(f_bc)
    P["zipBC"] = k.zip_((Vector((C_SPOT[0], C_SPOT[1], CAT_Z)) - Vector((B_SPOT[0], B_SPOT[1], 0))).length, f_bc)
    P["landC"] = k.touch(f_bc, C_SPOT)
    P["talkC"] = k.talk(len_c, face=FC)
    f_cd = face_to(C_SPOT, TOP1)
    P["shootCD"] = k.shoot(f_cd)
    P["zipCD"] = k.zip_((Vector((TOP1[0], TOP1[1], LEDGE_TOP)) - Vector((C_SPOT[0], C_SPOT[1], CAT_Z))).length, f_cd, cap=76)
    P["landD"] = k.touch(f_cd, TOP1)
    P["happy"] = perf.then(HAPPY, frm=8, length=54, blend=12, face=F1, in_place=1.0)
    return P


TARGET = dict(landB=wordf("meta") + 4, landC=wordf("98") - 30, landD=END - (JOIN_AIM - 1))
lens = dict(a=300, b=150, c=150)
for it in range(4):                                            # each landing falls on its mark (the talk before it absorbs the difference)
    P = queue(lens["a"], lens["b"], lens["c"])
    d_b = TARGET["landB"] - int(P["landB"].start)
    d_c = TARGET["landC"] - int(P["landC"].start) - d_b
    d_d = TARGET["landD"] - int(P["landD"].start) - d_b - d_c
    print("FIT", it, d_b, d_c, d_d, {n: int(P[n].start) for n in ("landB", "landC", "landD")})
    if d_b == d_c == d_d == 0:
        break
    lens["a"] += d_b
    lens["b"] += d_c
    lens["c"] += d_d
(talkA, shootAB, zipAB, landB, talkB, shootBC, zipBC, landC, talkC, shootCD, zipCD, landD, happy) = (
    P[n] for n in ("talkA", "shootAB", "zipAB", "landB", "talkB", "shootBC", "zipBC", "landC", "talkC", "shootCD", "zipCD", "landD", "happy"))
JOIN = END - int(landD.start) + 1                              # landing frames shown: the last frame here = old part 1 frame OLD_LAND1 + JOIN - 1
JOIN_OLD = OLD_LAND1 + JOIN
perf.build()
sc.frame_end = END

# ------------------------------------------------------------------ body to camera on every talk beat
AIMS = [([talkA], camA[0]), ([talkB], camB[0]), ([talkC], camC[0]), ([happy], s1[0])]
aim_spans = [(int(first(gs[0]).start), int(final(gs[-1]).end), Vector(loc)) for gs, loc in AIMS]


def facing_cam(f):
    for a_, b_, p in aim_spans:
        if a_ <= f <= b_:
            return (p.x, p.y)
    h = perf.bone_world(HIPS, f)
    return (h.x, h.y - 5)


flat = lambda gs: [c_ for g in gs for c_ in (g.cycles if hasattr(g, "cycles") else [g])]
square_err = perf.square_up(flat(sum((gs for gs, _ in AIMS), [])), facing_cam)

# ------------------------------------------------------------------ heights: the catwalk, the mural's ledge (the street is z = 0)
low_rel = lambda clip: min(min(perf.bone_world(b, f).z for b in ("mixamorig:LeftToeBase", "mixamorig:RightToeBase"))
                           for f in range(int(clip.start) + 4, int(clip.end) - 2, 6))


def between(a, b):
    i0, i1 = perf.clips.index(first(a)), perf.clips.index(final(b))
    return perf.clips[i0:i1 + 1]


def on(clips, floor, until):
    return [(int(c_.start), (int(n.start) - 1) if n is not None else until, floor - low_rel(c_), c_)
            for c_, n in zip(clips, list(clips[1:]) + [None])]


SURFACES = [(landC, shootCD, CAT_Z, int(zipCD.start) - 1), (landD, happy, LEDGE_TOP, END + 60)]    # (past the end: a key at END + 1 would drop him inside the happy clip's blend)
HEIGHTS = sum((on(between(a_, b_), z_, until) for a_, b_, z_, until in SURFACES), [])
HEIGHTS.sort(key=lambda h: h[0])
zk = []
for kk, (a_, b_, z, clip) in enumerate(HEIGHTS):
    prev = HEIGHTS[kk - 1] if kk else None
    if prev is not None and prev[1] + 1 >= a_ and getattr(clip, "at", None) is None and clip.blend > 1:
        zk += [(a_, prev[2], "inout"), (a_ + int(clip.blend), z, "const")]
    else:
        zk.append((a_, z, "const"))
    nxt = HEIGHTS[kk + 1][0] if kk + 1 < len(HEIGHTS) else None
    if nxt is None or nxt > b_ + 1:
        zk.append((b_ + 1, 0.0, "const"))
perf.root_z([(1, 0.0, "const")] + zk)

# ------------------------------------------------------------------ travel (each web: a straight pull from the end of one shot to the next)
k.travels = []
hp = k.hp
lastf = lambda clip: int(clip.start) - 1
# A -> B: across the street (web on the billboard's top left corner)
a0_, b0_ = hp(int(zipAB.start) - 1), hp(int(landB.start))
AB_ANCH = Vector((B_BX - B_W / 2 + 0.3, B_BY - 0.1, B_BZ + B_H / 2 + 0.2))
k.web_zip(zipAB, landB, AB_ANCH, lift=1.6, name="AB")
# B -> C: out over the avenue and up the tower
a1_, b1_ = hp(int(zipBC.start) - 1), hp(int(landC.start))
BC_ANCH = Vector((TOWER_X - 0.05, C_SPOT[1] + 0.4, STAT_Z[0] + STAT_H / 2 + 0.2))
k.web_zip(zipBC, landC, BC_ANCH, lift=1.0, name="BC")
# C -> the mural (the old S0): out into the avenue, then down the avenue and over the intersection to the ledge's left corner
fa, fb = int(zipCD.start), int(landD.start)
q0, q3 = hp(fa - 1), hp(fb)
CD_ANCH = k.find_anchor(q0, q3, (TOP1[0], WALL_G.point.y + 0.05, LEDGE_TOP + 7.0))
pCD = k.bez(q0, q0 + Vector((7.0, -5.0, -2.5)), q3 + Vector((6.0, 20.0, 6.0)), q3)
k.web_zip(zipCD, landD, CD_ANCH, path=pCD, name="CD")
for fa_, fb_, nm in k.travels:
    k.path_hits(fa_, fb_, nm)

# ------------------------------------------------------------------ polish: feet on the surfaces
LAND_SETTLE = 6
RAISED = [(int(landC.start) + LAND_SETTLE, int(zipCD.start) - 1, CAT_Z), (int(landD.start) + LAND_SETTLE, END, LEDGE_TOP)]
for a_, b_, top in RAISED:
    perf.contact(a_, b_, floor=top)
air = [(a_, b_) for a_, b_, _ in k.travels] + [(int(l_.start), int(l_.start) + LAND_SETTLE) for l_ in (landB, landC, landD)] + \
      [(a_ - 2, b_ + 2) for a_, b_, _ in RAISED]
lock_err = perf.ground_lock(1, int(zipBC.start) - 1, skip=air, step=1)
hips = lambda f: perf.bone_world(HIPS, int(f))
T1_CUT = int(landD.start)
print("JOIN: this video ends on old part 1 frame", OLD_LAND1 + JOIN - 1, "(landing started at", OLD_LAND1, "); part 1 resumes at old frame", JOIN_OLD,
      "| our landing starts at", T1_CUT, "of", END)

# ------------------------------------------------------------------ webs
webs = fx.WebShots(rig, fx.collection("Webs"))
for nm, sh, zc, lc, A in (("AB", shootAB, zipAB, landB, AB_ANCH), ("BC", shootBC, zipBC, landC, BC_ANCH), ("CD", shootCD, zipCD, landD, CD_ANCH)):
    W = int(perf.clip_frame(sh, k.hit_pk))
    webs.shot(f"Web_{nm}", R_HAND, (lambda p: (lambda f: p))(Vector(A)), W - 4, W, int(lc.start) - 3)
    shot.sfx("web_thwip", W - 3)
    shot.sfx("cartwheel_whoosh", int(zc.start) + 4)
    shot.sfx("landing_thud", int(lc.start) + 5)

# ================================================================== S-A scene: cards pile up on the reviewers; the red one slides past
card_mats = [img0(f"mr_{i}") for i in range(6)]
CW = 0.74
CAR = 512 / 360
N_PILE = 32
rp = random.Random(11)
pile_t = [wordf("every") - 40 + int((wordf("skip") - 24 - (wordf("every") - 40)) * (j / (N_PILE - 1)) ** 1.5) for j in range(N_PILE)]
levels = [0] * len(REV_X)
for j, tf in enumerate(pile_t):
    i_ = [1, 3, 0, 2][j % 4] if j < 28 else rp.randrange(4)
    lv = levels[i_]
    levels[i_] += 1
    rest = Vector((REV_X[i_] + rp.uniform(-0.2, 0.2), REV_Y - 0.02 * lv, 2.12 + lv * 0.14))
    top = Vector((rest.x + rp.uniform(-0.3, 0.3), rest.y, 3.5))   # the cards drop out of the board's lower edge (never across its text)
    cd = city.sign(f"MRCard{j}", card_mats[j % 6], top, A_N, CW, aspect=CAR, offset=0.0, emit=0.3, alpha=True, coll=signs)
    rz0 = cd.rotation_euler.z
    tilt = rp.uniform(-0.2, 0.2)
    anim.keys(cd, "location", [(tf - 10, top, "in"), (tf, rest, "out"), (tf + 3, rest + Vector((0, 0, 0.05)), "in"), (tf + 6, rest)])
    cd.rotation_euler = (0, 0, rz0)
    anim.keys(cd, "rotation_euler", [(tf - 10, Vector((0, 0, rz0 + 0.8 * tilt * 3)), "out"), (tf, Vector((0, 0, rz0 + tilt)), "bez")])
    show(cd, [(1, False), (tf - 10, True), (wordf("meta") + 40, False)])
    if j % 4 == 0:
        shot.sfx("board_thud", tf, gain=0.5)
RED_F = wordf("skip") - 6
red = city.sign("MRRed", img0("mr_red"), Vector((A_BX + 5.2, REV_Y - 0.9, 1.55)), A_N, 1.3, aspect=CAR, offset=0.0, emit=0.6, alpha=True, coll=signs)
rz0 = red.rotation_euler.z
anim.keys(red, "location", [(RED_F, Vector((A_BX + 5.2, REV_Y - 0.9, 1.55)), "lin"), (RED_F + 36, Vector((A_BX - 5.4, REV_Y - 0.9, 1.7)), "lin")])
anim.keys(red, "rotation_euler", [(RED_F, Vector((0, 0, rz0 + 0.12)), "lin"), (RED_F + 36, Vector((0, 0, rz0 - 0.1)), "lin")])
show(red, [(1, False), (RED_F, True), (RED_F + 37, False)])
shot.sfx("board_whoosh", RED_F)
shot.sfx("ui_pop", wordf("every", 0))
shot.sfx("ui_pop", wordf("every", 1))
# the board is on for S-A only: gone once he has landed at the Meta billboard
show(board_a, [(1, True), (int(landB.start) + 2, False)])
show(meta_a, [(1, False), (int(zipAB.start) - 20, True)])
show(meta_b, [(1, False), (wordf("risk", 0) - 2, True)])
shot.sfx("ui_pop", wordf("risk", 0))

# ================================================================== S-B scene: the machine (belt, the part 2 robot arm, cards with risk scores, a human reviewer)
V_BELT = 0.06                                                  # m / frame
FRAME_IN = lambda f_arm: f_arm - int((X_ARM - X_IN) / V_BELT)
CONTACT = [wordf("approved") + 6, wordf("approved") + 6 + 48]  # the arm's down-strokes (one every 48 frames): the two stamps
ARM_SPEED = 180.0 / 48.0
arm_u = cw.arm("MachineArm", (X_ARM, BELT_Y + 1.7, -0.55), face=(0, 1), phase=0.0, speed=ARM_SPEED)
st_arm = arm_u.arm.animation_data.nla_tracks[-1].strips[0]
a_nm = arm_u.arm.pose.bones[-1].name
tip_at = lambda: arm_u.arm.matrix_world @ arm_u.arm.pose.bones[a_nm].tail
loc_t = []
for t in range(0, 181, 2):                                     # the strip starts on frame 1: local action frame t plays on frame 1 + t / speed
    sc.frame_set(1 + int(round(t / ARM_SPEED)))
    loc_t.append((t, tip_at().copy()))
reach = [x for x in loc_t if x[1].y < BELT_Y + 1.0]       # (the arm sits behind the belt and reaches towards the lens)
stamp_pt = min(reach or loc_t, key=lambda x: x[1].z)           # the stroke's lowest point is where the stamp lands
print("ARM stamp stroke at local frame", stamp_pt[0], "tip", tuple(round(v, 2) for v in stamp_pt[1]))
PER = 180.0 / ARM_SPEED
s_arm = CONTACT[0] - stamp_pt[0] / ARM_SPEED
s_arm -= math.ceil((s_arm - 1) / PER) * PER                    # start before frame 1 so the loop is already running
st_arm.frame_start_ui = s_arm
sc.frame_set(CONTACT[0])
arm_u.wrap.location += Vector((X_ARM, BELT_Y, BELT_TOP + 0.5)) - tip_at()
for o in arm_u.objs:
    anim.visible(o, [(1, False), (int(zipAB.start) - 25, True), (int(shootBC.start) + 40, False)])
shot.sfx("board_thud", CONTACT[0], gain=0.7)
shot.sfx("board_thud", CONTACT[1], gain=0.7)
cards_b = [("risk_g0", "low", CONTACT[0]), ("risk_g1", "low", CONTACT[1]), ("risk_r0", "high", CONTACT[1] + 22)]
for nm, kind, f_arm in cards_b:
    f0 = FRAME_IN(f_arm)
    half = 0.31
    cd = city.sign(f"B_{nm}", img0(nm), Vector((X_IN, BELT_Y, BELT_TOP + 0.41)), B_N, 1.15, aspect=CAR, offset=0.0, emit=0.5, alpha=True, coll=signs)
    rz0 = cd.rotation_euler.z
    x_arm_f = f_arm
    keys_ = [(f0, Vector((X_IN, BELT_Y, BELT_TOP + 0.41)), "lin"), (x_arm_f, Vector((X_ARM, BELT_Y, BELT_TOP + 0.41)), "lin")]
    if kind == "low":
        f_out = x_arm_f + int((X_OUT - X_ARM) / V_BELT)
        keys_.append((f_out, Vector((X_OUT, BELT_Y, BELT_TOP + 0.41)), "lin"))
        keys_.append((f_out + 14, Vector((X_OUT + 1.6, BELT_Y, BELT_TOP + 0.41)), "lin"))
        end_f = f_out + 14
        stamp_args = (f"B_{nm}_stamp", x_arm_f, end_f)
        shot.sfx("ui_pop", x_arm_f)
    else:                                                      # the arm lifts it out and carries it to the human, who reads it
        top = Vector((X_ARM + 0.2, BELT_Y - 0.1, 2.35))
        mid = Vector((X_OUT + 0.4, BELT_Y - 0.2, 2.5))
        to_h = Vector((HUM[0] - 0.55, HUM[1] - 0.35, 1.45))
        keys_ += [(x_arm_f + 7, top, "out"), (x_arm_f + 17, mid, "inout"), (x_arm_f + 27, to_h, "out")]
        end_f = x_arm_f + 27 + 90
        keys_.append((end_f, to_h, "lin"))
        shot.sfx("board_whoosh", x_arm_f + 6)
        shot.sfx("ui_pop", x_arm_f + 27)
    anim.keys(cd, "location", keys_)
    show(cd, [(1, False), (f0, True), (end_f + 1, False)])
    if kind == "low":                                          # the stamp rides on the card (parented once the card's keys exist)
        sn, sf, ef = stamp_args
        stp = city.sign(sn, img0("stamp_ok"), Vector((X_ARM, BELT_Y - 0.03, BELT_TOP + 0.3)), B_N, 0.8, aspect=560 / 190, offset=0.0, emit=0.7, alpha=True, coll=signs)
        parent_keep(stp, cd, sf)
        anim.visible(stp, [(1, False), (sf, True), (ef + 1, False)])
        anim.keys(stp, "scale", [(sf, Vector((2.6, 2.6, 2.6)), "out"), (sf + 4, Vector((1, 1, 1)), "back")])
    if kind == "high":
        anim.keys(cd, "rotation_euler", [(x_arm_f, Vector((0, 0, rz0)), "inout"), (x_arm_f + 17, Vector((0.0, 0.0, rz0 + 0.35)), "inout"), (x_arm_f + 27, Vector((0, 0, rz0 + 0.1)), "out")])
    CARRY[nm] = (f0, x_arm_f)

# ================================================================== S-C scene: each result lights on its number
M_STATS = [wordf("98") - 3, wordf("30") - 3, wordf("33") - 3]
for ob, f_on in zip(stat_obs, M_STATS):
    show(ob, [(1, False), (f_on, True), (int(zipCD.start) + 20, False)])
    shot.sfx("ui_pop", f_on)

# ================================================================== webs baked + the mural scene's pigeons are with the life below
# ================================================================== cameras
cam = k.camera()
CUTS = []


def at(f, loc, tgt, ease="inout", cut=False):
    cam.at(int(f), loc, tgt, ease, cut=cut)


# S-A the volume board, him at its left edge, the reviewers under it (holds through his web shot)
k.read_shot(1, int(zipAB.start) - 1, camA, drift=0.3)
# the zip across the street (side-tracking), then the Meta billboard + the machine from his landing
cam.lens(int(zipAB.start), 22, "const")
k.ride(int(zipAB.start), int(landB.start) - 1, Vector((8.0, -3.0, 2.0)), lead=8)
k.read_shot(int(landB.start), int(zipBC.start) - 1, camB, drift=0.3)
# the zip up the avenue to the tower (tracking), then the three results
cam.lens(int(zipBC.start), 20, "const")
k.ride(int(zipBC.start), int(landC.start) - 1, Vector((6.0, -10.0, 1.5)), lead=8)
k.read_shot(int(landC.start), int(zipCD.start) - 1, camC, drift=0.4)
# the old S0: the aerial down the avenue (lens 18, riding the zip), then the cut to the mural's presenter shot at the landing
cam.lens(int(zipCD.start), 18, "const")
k.ride(int(zipCD.start), int(landD.start) - 1, Vector((7.0, 8.5, 5.0)), lead=8)
loc1, tgt1, lens1 = s1
cam.lens(int(landD.start), round(lens1), "const")
at(int(landD.start), loc1, tgt1, "lin", cut=True)
drift_f = int(landD.start) + (OLD_ZIP2 - 1 - OLD_LAND1)         # old part 1 keyed the same tiny push-in over frames OLD_LAND1 .. OLD_ZIP2 - 1
at(drift_f, Vector(loc1).lerp(Vector(tgt1), 0.15 / max(1.0, (Vector(tgt1) - Vector(loc1)).length)), tgt1, "lin")
CUTS += [("billboard", int(landB.start)), ("tower", int(landC.start)), ("mural", int(landD.start))]
for lc in (landB, landC, landD):
    cam.shake(int(lc.start) + 5, amp=0.04, dur=8)
fs_ = [(1, 8.0), (int(zipAB.start), 5.6), (int(landB.start), 8.0), (int(zipBC.start), 5.6), (int(landC.start), 8.0),
       (int(zipCD.start), 5.6), (int(landD.start), 8.0)]
for f_, v_ in fs_:
    anim.key(cam.cam.data.dof, "aperture_fstop", int(f_), v_, ease="const")
TALKS = [talkA, talkB, talkC, happy]
office.face_camera(cam.cam, [(int(first(g).start) + 4, int(final(g).end) - 2) for g in TALKS], amount=0.5)
fx.char_lights(rig, cam.cam, key=170.0, rim=340.0)
# open-hand presenting towards the board as each idea lands (the arm on the board's side)
for f_, board_c, spot, cloc in ((wordf("every", 0), A_C + A_N * 0.3, A_SPOT, camA[0]), (wordf("every", 1), A_C + A_N * 0.3, A_SPOT, camA[0]),
                                (wordf("risk", 0), B_C + B_N * 0.4, B_SPOT, camB[0]), (M_STATS[0] + 2, Vector((TOWER_X + 0.5, TOWER_Y, STAT_Z[0])), C_SPOT, camC[0]),
                                (M_STATS[1] + 2, Vector((TOWER_X + 0.5, TOWER_Y, STAT_Z[1])), C_SPOT, camC[0]),
                                (M_STATS[2] + 2, Vector((TOWER_X + 0.5, TOWER_Y, STAT_Z[2])), C_SPOT, camC[0])):
    office.present(f_, board_c, side=k.gesture_side(board_c, hips(f_), cloc), hold=26, ramp=8, amount=0.6)
from pipeline import face
eyes = face.Lenses(bpy.data.objects["MilesMasked"])
for f_, w_ in ((1, dict(Squint=0.35, Sad=0.35)), (wordf("risky"), dict(Sad=0.0, Squint=0.0)), (wordf("meta") + 12, dict(Wide=0.5)),
               (wordf("98"), dict(Wide=0.9)), (wordf("engineers"), dict(Wide=0.0, Squint=0.3)), (int(landD.start) + 20, dict(Wide=0.75, Squint=0.0))):
    eyes.set(f_, **w_)
eyes.blinks(1, END, every=95)
webs.bake(range(1, END + 1))
for o in fx.collection("Webs").objects:
    if o.type == "MESH":
        o.data.materials[0] = fx.material("Web_Line", (0.95, 0.97, 1.0), rough=0.35, emit=0.9)

# ================================================================== city life: parked cars on the curbs, pigeons on the mural's ledge
guard = life.Guard(cam.cam, lambda f: rig.matrix_world @ rig.pose.bones[HIPS].head, (1, END), step=2)
guard.keepout += [(1, END, Vector((A_BX, A_BY + 6.0, 0)), 11.0), (1, END, Vector((B_BX + 2.0, 2.0, 0)), 11.0)]    # no car in front of the two stages
rl = random.Random(21)
cars = life.CarKit()
parked = 0
for axis in ("x", "y"):
    for side in (-1, 1):
        u = -47.0 + rl.uniform(0, 4)
        while u < 47.0:
            if abs(u) > 12.5 and rl.random() < 0.72:
                p_ = Vector((u, side * 4.25, 0.4)) if axis == "x" else Vector((side * 4.25, u, 0.4))
                if all(guard.ok(f, p_, r_sub=2.6, r_cam=2.6, r_line=1.0) for f in guard.cam):
                    car = cars.spawn(rl.randrange(10), f"Parked{parked}")
                    heading = Vector((1, 0, 0)) * -side if axis == "x" else Vector((0, 1, 0)) * side
                    car.place(Vector((p_.x, p_.y, -0.08)), heading)
                    parked += 1
            u += rl.uniform(5.6, 7.5)
birds = life.PigeonKit()
for i_, x_ in enumerate((-14.6, -13.4)):
    b_ = birds.spawn(f"Pigeon{i_}")
    b_.perch(Vector((x_, WALL_G.point.y + WALL_G.normal.y * 0.6 + rl.uniform(-0.2, 0.25), LEDGE_TOP)), 1, rl.uniform(-70, 70), phase=rl.randint(0, 120))
    b_.fly_off(int(landD.start) - 4 + rl.randint(-3, 5), Vector((0.7 + rl.uniform(-0.3, 0.3), 0.7 + rl.uniform(-0.3, 0.3), 0)), speed=rl.uniform(0.24, 0.32), seed=i_)
print("LIFE parked", parked)

# ------------------------------------------------------------------ checks + audit data + finish
k.visible_report(END)
v3 = lambda v: [round(float(x), 3) for x in v]
json.dump(dict(travel=[(a_, b_, n_) for a_, b_, n_ in k.travels],
               talks=[(int(first(g).start + first(g).blend) + 4, int(final(g).end) - 12, v3(loc)) for gs, loc in AIMS for g in gs],
               reads=[("volume", talkA, A_C, A_N, A_W, A_H), ("meta", talkB, B_C, B_N, B_W, B_H),
                      ("results", talkC, Vector((TOWER_X + 0.35, TOWER_Y, STAT_Z[1])), C_N, STAT_W, STAT_Z[0] - STAT_Z[-1] + STAT_H)] and
                     [(n_, int(first(g).start + first(g).blend) + 4, int(final(g).end) - 6, v3(bc), v3(nn), w_, h_)
                      for n_, g, bc, nn, w_, h_ in (("volume", talkA, A_C, A_N, A_W, A_H), ("meta", talkB, B_C, B_N, B_W, B_H),
                                                    ("results", talkC, Vector((TOWER_X + 0.35, TOWER_Y, STAT_Z[1])), C_N, STAT_W, STAT_Z[0] - STAT_Z[-1] + STAT_H))],
               webs=[o.name for o in fx.collection("Webs").objects if o.type == "MESH"]),
          open(os.path.join(paths.ROOT, "build", f"{NAME}_audit.json"), "w"))
json.dump(dict(fps=FPS, end=END, captions=[]), open(os.path.join(paths.ROOT, "build", f"{NAME}_overlays.json"), "w"), indent=1)
shot.finish(NAME, exposure=-0.35, samples=24, view="AgX", grade="AgX - Punchy",
            markers=[("vo 14", 1), ("A volume", 1), ("B meta", int(landB.start)), ("C results", int(landC.start)), ("D mural", int(landD.start)),
                     ("end", END)])
fx.cine_grade(sc)
bpy.ops.wm.save_mainfile()
print("CUTS", CUTS)
print("TIMES", {n: (int(first(v).start), int(final(v).end)) for n, v in P.items()}, "stamps", CONTACT, "stats", M_STATS, "square", round(square_err, 1))
print(f"STREET0 frames 1-{END} ({END / FPS:.1f}s)  ground-lock {lock_err * 100:.1f} cm")
