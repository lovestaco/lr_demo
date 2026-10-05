"""Street piece (~55 s): Spidey's tour of the inspection story through a city at sunset.

    S0  aerial establishing → he swings down the avenue → lands by a graffiti wall
    S1  mural: "You already ship a lot of AI-generated code."
    S2  web up → swings to a rooftop billboard, perches on it: "But do you do enough code inspection?"
    S3  swings north past an LED ticker (aerial tracking): "Code now ships faster than ever."
    S4  bus-stop lightbox: graph grows, spiders crawl out on "bugs" → shock
    S5  subway lightbox: "Human review can't keep up." (frustrated)
    S6  Times Square screen at the intersection: the four risks pop on their words (worried)
    S7  rooftop at sunset: "How do you stay competitive?" → "You need a better inspection layer." (low angle)
    S8  drops into the intersection, webs down the tower block by block (+ cash)
    S9  yanks INSPECTION out → collapse, cash rain, he flops → helicopter pull-out

Locations are hard cuts (cut on action); every sign holds a still, readable frame.

    python3 scripts/03c_street_signs.py
    blender -b build/character.blend --python scripts/04_street.py          # -> build/street.blend
"""
import bpy, os, sys, math, random, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mathutils import Vector
from pipeline import paths, anim, fx, shot, props, city, swing
from pipeline.mixamo import Performer, ClipGroup
from pipeline.shot import L_HAND, R_HAND, HIPS

FPS = 30
NAME = "street"
sc = bpy.context.scene
ST = os.path.join(paths.ROOT, "assets", "street")
SCR = os.path.join(paths.ROOT, "assets", "screens")
img = lambda n: os.path.join(ST, n + ".png")
seq0 = lambda n: os.path.join(ST, n, "f_0001.png")
VO = json.load(open(os.path.join(paths.ROOT, "assets", "audio", "vo_street", "lines.json")))
dur = lambda n: VO[str(n)]["duration"]
PAD = 0.35
hold = lambda n, extra=0.45, at_least=0: int(round(max(at_least, (dur(n) - PAD + extra) * FPS)))
F = lambda x: int(round(x))
word = lambda n, w: next(t for x, t in VO[str(n)]["words"] if x == w)

# ------------------------------------------------------------------ set: city at sunset, raised so the sidewalk is z=0
c = city.load()
LIFT = 0.34
for o in c.coll.objects:
    if o.parent is None:
        o.location.z += LIFT
bpy.context.view_layer.update()
rig = bpy.data.objects["MilesRig"]
fx.physical_shading(rig, lift=3.0, sheen=0.85, rough=0.38)
office = props.Office(rig)
for n in ("Watch_Band", "Watch_Face"):                       # street look: badge stays, watch goes
    o = bpy.data.objects.get(n)
    if o:
        o.hide_render = o.hide_viewport = True


def wall(y, side, z=6.0, x0=0.0):
    h = c.wall((x0, y, z), (side, 0, 0))
    return h


def clear_view(cam_loc, pts, slack=0.35):
    """True if nothing (lamp post, tree, sign) sits between the camera and every point."""
    for p in pts:
        d = Vector(p) - Vector(cam_loc)
        h = c.ray(cam_loc, d, d.length + 1.0)
        if h is None or (h.point - Vector(cam_loc)).length < d.length - slack:
            return False
    return True


def board_pts(centre, normal, w, h):
    n = Vector(normal).normalized()
    side = n.cross(Vector((0, 0, 1))).normalized()
    grid_a = [k / 20.0 - 0.975 for k in range(40)]               # dense: thin poles and pipes don't slip between rays
    return [centre + side * (w / 2 * a) + Vector((0, 0, h / 2 * b)) + n * 0.05 for a in grid_a for b in (-0.8, -0.4, 0, 0.4, 0.8)]


# signage on the cross street (no street trees there) — positions from the actual facades
SOUTH = lambda x, z=6.0: c.wall((x, 0.0, z), (0, -1, 0))      # facades on the south side (face +y)
NORTH = lambda x, z=6.0: c.wall((x, 0.0, z), (0, 1, 0))       # facades on the north side (face -y)
WALL_G = SOUTH(-18.0)                          # west arm, south: graffiti mural
BBW = NORTH(-19.0)                             # west arm, north: billboard on the roof
BB_ROOF = c.roof(-19.0, BBW.point.y + 2.0)
TICK = NORTH(14.0, z=10.0)                     # east arm, north (near the corner): LED ticker
POST = SOUTH(26.0, z=2.0)                      # east arm, south: subway lightbox
SCREEN = NORTH(25.0, z=9.0)                    # east arm, north (further east): the big screen
ROOF_Z = c.roof(12.0, -17.5)                   # tall building on the avenue (rooftop scene)
print("SET", WALL_G.point, BBW.point, BB_ROOF, TICK.point, POST.point, SCREEN.point, ROOF_Z)

# ------------------------------------------------------------------ signs
signs = fx.collection("Signs")
GB_W, GB_H = 7.2, 4.05                             # small-player rule: sign fills most of the frame
best = None
for gx in (-18.0, -20.0, -16.0, -22.0, -24.0, -14.0, -26.0, -28.0):
    fx_, hit = city.flat_spot(c, [gx], 0.0, -1, 6.0, GB_W * 0.8, tol=0.12)
    if hit is None:
        continue
    found = False
    for dx in (1.4, 0.4, 2.4, -0.6, 3.4):
        cand = (Vector((gx, hit.point.y, 4.9)), ((gx + dx, hit.point.y + 9.4, 2.6), (gx + 1.1, hit.point.y, 3.5)), hit)
        best = best or cand
        if clear_view(cand[1][0], board_pts(cand[0] + hit.normal * 0.45, hit.normal, GB_W, GB_H)):
            best, found = cand, True
            break
    if found:
        break
G_C, mural_cam, WALL_G = best
print("BOARD1", G_C, mural_cam)
city.sign("Board1", img("wallboard_generated"), G_C, WALL_G.normal, GB_W, offset=0.45, emit=0.5, frame="billboard")
BB_C = Vector((-19.0, BBW.point.y + 0.6, BB_ROOF + 3.4))
billboard = city.sign("Billboard", img("billboard_inspection"), BB_C, Vector((0, -1, 0)), 9.6, aspect=3.0, emit=0.6,
                      frame="billboard", offset=0.0)
for k, dx in enumerate((-3.0, 3.0)):                          # legs
    leg = fx.material("BB_Leg", (0.06, 0.06, 0.07), rough=0.4, metallic=0.7)
    import bmesh
    me = bpy.data.meshes.new(f"BBLeg{k}")
    b = bmesh.new()
    bmesh.ops.create_cube(b, size=1.0)
    bmesh.ops.scale(b, vec=(0.2, 0.2, 4.2), verts=b.verts)
    b.to_mesh(me)
    b.free()
    ob = bpy.data.objects.new(f"BBLeg{k}", me)
    signs.objects.link(ob)
    ob.location = (-19.0 + dx, BB_C.y + 0.2, BB_ROOF + 0.9)
    me.materials.append(leg)
BB_TOP = Vector((BB_C.x + 3.4, BB_C.y + 0.15, BB_C.z + 9.6 / 3.0 / 2 + 0.14))     # top-right corner (from the street)
TK_W = 8.4
TK_C = Vector((14.0, TICK.point.y, 4.9))
ticker = city.sign("Ticker", img("ticker_faster"), TK_C, TICK.normal, TK_W, aspect=3600 / 420, emit=2.2, frame="led",
                   offset=0.35)
px, POST = city.flat_spot(c, [26.0, 24.8, 24.4, 25.2, 24.0, 23.6, 27.0], 0.0, -1, 2.4, 3.6)
POST_C = Vector((px, POST.point.y, 2.4))
SUB_N = 180
subway = city.sign("Subway", seq0("st_queue"), POST_C, POST.normal, 3.6, emit=1.4, frame="lightbox", seq=(SUB_N, 1),
                   offset=0.12)
SCR_N = Vector((0, -1, 0))
SCR_C = Vector((25.0, SCREEN.point.y, 7.2))
# rooftop screen on the tall avenue building, facing the avenue (west)
RS_C = Vector((13.4, -17.5, ROOF_Z + 3.2))
# bus shelter on the east arm's south sidewalk (long axis along x), lightbox at its west end facing the intersection
BUS = Vector((19.0, -7.2, 0.0))


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


steel = fx.material("Shelter_Steel", (0.08, 0.09, 0.1), rough=0.35, metallic=0.8)
glass = fx.material("Shelter_Glass", (0.6, 0.7, 0.75), rough=0.05)
box("ShelterRoof", (4.2, 1.8, 0.12), BUS + Vector((0, 0, 2.5)), steel)
box("ShelterBack", (4.0, 0.05, 2.2), BUS + Vector((0, -0.8, 1.25)), glass)
for k, dx in enumerate((-2.0, 2.0)):
    box(f"ShelterPost{k}", (0.1, 0.1, 2.5), BUS + Vector((dx, -0.8, 1.25)), steel)
    box(f"ShelterPostF{k}", (0.1, 0.1, 2.5), BUS + Vector((dx, 0.8, 1.25)), steel)
BUS_AD_W = 3.6
BUS_AD_C = BUS + Vector((-2.6, 0.0, 1.55))
BUS_AD_N = Vector((-1, 0, 0))
BUG_N = 210

# ------------------------------------------------------------------ performance
perf = Performer(rig).place(x=0, y=0, face=0)
hit_pk = perf.extreme("Standing 1H Magic Attack 02", R_HAND, (1, 0, 0), 16, 40)
up_pk = perf.extreme("Standing 2H Magic Attack 01", R_HAND, (0, 0, 1), 10, 60)
SW = "Swing To Land (1)"
EXPLAIN = "CMU 18_08 conversation - explain with hand gesture"
PRESENT = ["Talking (2)", "Talking (1)", EXPLAIN]
_turn = [0]


def talk(length, face=0, blend=10, at=None):
    parts, left = [], int(length)
    while left > 8:
        clip = PRESENT[_turn[0] % len(PRESENT)]
        _turn[0] += 1
        a0, a1 = bpy.data.actions[clip].frame_range
        n = min(left + (blend if parts else 0), int(a1 - a0) - 2)
        frm = perf.lively(clip, n, target=1.5) if clip == EXPLAIN else a0 + 1
        parts.append(perf.then(clip, frm=frm, length=n, blend=blend, face=face, in_place=0.7,
                               at=at if not parts else None))
        left -= n - (blend if len(parts) > 1 else 0)
    return parts[0] if len(parts) == 1 else ClipGroup(parts)


first = lambda g: g.cycles[0] if hasattr(g, "cycles") else g
SW_SPEED = 0.9
SW_FLY = 34                                   # swing clip frame where the arc ends (drop to the landing)
have = lambda n: n in bpy.data.actions
opt = lambda n, fallback: n if have(n) else fallback       # new Mixamo clips when they're in character.blend


def swing_clip(face, at, speed=SW_SPEED, to=57):
    return perf.then(SW, frm=1, to=to, speed=speed, face=face, in_place=1.0, at=at)


INV = math.pi                                 # roll about the depth axis: upside down, still facing the camera
FOOT_TOE = "mixamorig:LeftToeBase"
# ---- S0/S1: swing down the avenue, land crouched on TOP of the wall board (light stone behind him, no windows)
TOP1_Z = G_C.z + GB_H / 2 + 0.12
TOP1 = (G_C.x - 2.5, WALL_G.point.y + WALL_G.normal.y * 0.33)       # board's top edge, screen-right corner
sw1 = swing_clip(face=-160, at=TOP1)
perch1 = perf.then(SW, frm=52, to=57, speed=5 / max(40, hold(1, 0.9) + 26), blend=8, face=10)
web2 = perf.then("Standing 1H Magic Attack 02", frm=16, to=40, speed=1.1, blend=8, face=160)  # line to the billboard
# ---- S2: swing across to the billboard, then hang UPSIDE DOWN from its bottom edge (legs hooked over it)
BB_BOT = BB_C.z - 9.6 / 3.0 / 2 - 0.12
HANG2 = (BB_C.x + 3.0, BB_C.y - 0.2)
sw2 = swing_clip(face=180, at=HANG2, speed=0.62, to=SW_FLY)
hang2 = perf.then("Hanging Idle", length=hold(2, 1.1) + 6, face=0, at=HANG2)
# ---- S3: under the LED ticker, head whipping after a light streak racing along it, faster and faster
TICK_SPOT = (TK_C.x + 2.2, TICK.point.y - 1.5)
tick = perf.then("Breathing Idle", length=hold(3, 1.6, 75), face=0, at=TICK_SPOT)
# ---- S4: bus stop: spiders come out, he startles and leaps onto the shelter roof, clinging there
BUS_SPOT = (BUS_AD_C.x - 1.0, BUS_AD_C.y + 2.4)
look4 = talk(F(word(4, "bugs") * FPS) + 14, face=40, at=BUS_SPOT)
shock = perf.then("CMU 120_16 Mickey Surprised", frm=140, to=176, blend=6, face=20, in_place=0.8)
ROOF_SPOT = (BUS.x - 0.8, BUS.y + 0.1)
cling = (perf.then("MX Terrified", frm=110, length=64, face=-60, at=ROOF_SPOT) if have("MX Terrified") else
         perf.then("Hard Landing", frm=30, to=44, speed=14 / 58, face=-60, at=ROOF_SPOT))
# ---- S5: subway: drops in upside down on a web line beside the board
SUB_SPOT = (POST_C.x - 2.3, POST.point.y + 0.9)
frus = perf.then("Hanging Idle", length=hold(5, 0.9), face=0, at=SUB_SPOT)
# ---- S6: perched on the big screen's frame while the risks pop; moonwalks off with the customers
SCR_W = 9.2
TS_SPOT = (25.0 - SCR_W / 2 + 0.7, SCREEN.point.y - 0.9 - 0.25)
TS_Z = 7.2 - SCR_W / 16 * 9 / 2 - 0.08
worry = perf.then("Hard Landing", frm=30, to=44, speed=14 / (F(word(6, "bad") * FPS) + 44), face=0, at=TS_SPOT)
MOON = opt("MX Moonwalk 1", "Walking")
moon = perf.then(MOON, blend=8, repeat=3, face=90, in_place=1.0, speed=1.0)
# ---- S7: rooftop at sunset
RF_SPOT = (10.2, -17.5)
perch7 = perf.then("Hard Landing", frm=30, to=44, speed=14 / max(20, hold(7, 0.7)), face=-70, at=RF_SPOT)
conf7 = (perf.then("MX Taunt", blend=10, face=-40, speed=50 / max(50, hold(8, 1.0))) if have("MX Taunt")
         else talk(hold(8, 1.0), face=-60, blend=12))
# ---- S8: the runaway train. He webs an INSPECTION net across the avenue, holds the train with it;
# "Without inspection" -> he lets go, dives clear, the train derails, the cash explodes.
FIN_SPOT = (3.4, 31.2)
fin_land = perf.then("Hard Landing", frm=8, to=60, speed=1.15, face=0, at=FIN_SPOT)
shoot = perf.then("Standing 2H Magic Attack 01", frm=up_pk - 14, to=up_pk + 20, speed=1.15, blend=8, face=0)
perf.build()

# ------------------------------------------------------------------ timeline (frames)
T = {}
T["vo1"] = int(perch1.start) + 10
T["vo2"] = int(hang2.start) + 4
T["vo3"] = int(tick.start) + 6
T["vo4"] = int(first(look4).start) + 4
T["vo5"] = int(frus.start) + 8
T["vo6"] = int(worry.start) + 8
T["vo7"] = int(perch7.start) + 10
T["vo8"] = (int(conf7.start) + 8) if have("MX Taunt") else int(first(conf7).start) + 12
NET_F = int(perf.clip_frame(shoot, up_pk))                      # the net forms on "inspection"
T["vo13"] = NET_F - F(word(13, "inspection") * FPS)
T["vo9"] = T["vo13"] + F((dur(13) + 0.1) * FPS)
for n in (10, 11, 12):
    T[f"vo{n}"] = T[f"vo{n - 1}"] + F((dur(n - 1) + 0.15) * FPS)
CAR_F = [T["vo9"] + F(word(9, "engineers") * FPS), T["vo10"] + F(word(10, "customers") * FPS),
         T["vo11"] + F(word(11, "competitive") * FPS)]
cash_f = T["vo11"] + F(word(11, "money") * FPS)
REL = T["vo12"] + F(word(12, "inspection") * FPS)              # lets go of the net
CRASH = T["vo12"] + F(word(12, "collapses") * FPS)
holdc = perf.then("Pulling A Rope", length=REL - int(shoot.end) + 10, blend=10, face=0, in_place=0.8)
DIVE = opt("MX Backflip", "Hard Landing")
dive = perf.then(DIVE, frm=(14 if have("MX Backflip") else 8), to=(90 if have("MX Backflip") else 40), blend=4,
                 face=-90, in_place=1.0, speed=1.25)
flop = perf.then("Fallen Idle", length=150, blend=10, face=-60)
perf.build()

# ------------------------------------------------------------------ body to camera on the talk beats
_cams = {}


def aim_for(clip_group, cam_loc):
    for c_ in (clip_group.cycles if hasattr(clip_group, "cycles") else [clip_group]):
        _cams[id(c_)] = Vector(cam_loc)


BUS_CAM = ((BUS_AD_C.x - 6.2, BUS_AD_C.y + 1.1, 1.5), (BUS_AD_C.x, BUS_AD_C.y + 1.0, 1.35))
SUB_CAM = ((POST_C.x - 1.0, POST_C.y + 6.0, 1.7), (POST_C.x - 1.0, POST_C.y, 1.9))
for dx, dy in [(dx_ * 0.5 - 1.0, dy_) for dy_ in (6.0, 6.8, 5.4) for dx_ in (0, 2, -2, 4, -4, 6)]:
    cand = ((POST_C.x + dx, POST_C.y + dy, 1.7), (POST_C.x - 1.0, POST_C.y, 1.9))
    if clear_view(cand[0], board_pts(POST_C + POST.normal * 0.12, POST.normal, 3.6, 2.0)):
        SUB_CAM = cand
        print("SUBCAM", dx, dy)
        break
aim_for(look4, BUS_CAM[0])
if not have("MX Taunt"):
    aim_for(conf7, (RF_SPOT[0] - 5.5, RF_SPOT[1] - 2.2, 0))
spans = [(int(g.start), int(g.end), _cams[id(first(g))]) for g in ([look4] + ([] if have("MX Taunt") else [conf7]))]


def facing_cam(f):
    for a_, b_, p in spans:
        if a_ <= f <= b_:
            return (p.x, p.y)
    h = perf.bone_world(HIPS, f)
    return (h.x, h.y - 5)


square_err = perf.square_up([look4] + ([] if have("MX Taunt") else [conf7]), facing_cam)

# ------------------------------------------------------------------ upside-down hangs: heights measured on the upright clip
toe_rel = perf.bone_world(FOOT_TOE, int(hang2.start) + 8).z
head_rel = perf.bone_world("mixamorig:Head", int(frus.start) + 8).z


# Root height / upside-down per shot, written from one table so adjacent hard cuts can't overwrite each other
# (each interval holds its value; the root returns to 0 / upright only where no shot follows directly).
HEIGHTS = [  # (first frame, last frame, root z, upside down)
    (int(sw1.start), int(web2.end), TOP1_Z - 0.1, False),
    (int(hang2.start), int(hang2.end), BB_BOT + toe_rel - 0.05, True),        # feet hooked over the board's bottom edge
    (int(cling.start), int(cling.end), 2.56 - 0.1, False),                     # on the bus-shelter roof
    (int(frus.start), int(frus.end), 2.15 + head_rel, True),                   # head at the board's middle
    (int(worry.start), int(moon.end), TS_Z, False),                            # on the big screen's frame
    (int(perch7.start), int(conf7.end), ROOF_Z, False),
]
HEIGHTS.sort()
zk, rk = [], []
for k, (a_, b_, z, inv) in enumerate(HEIGHTS):
    zk.append((a_, z, "const"))
    rk.append((a_, INV if inv else 0.0, "const"))
    nxt = HEIGHTS[k + 1][0] if k + 1 < len(HEIGHTS) else None
    if nxt is None or nxt > b_ + 1:
        zk.append((b_ + 1, 0.0, "const"))
        rk.append((b_ + 1, 0.0, "const"))
perf.root_z([(1, 0.0, "const")] + zk)
anim.keys(perf.root, "rotation_euler", [(1, 0.0, "const")] + rk, index=1)

# ------------------------------------------------------------------ swings + moonwalk + dive: real paths
hp = lambda f: perf.bone_world(HIPS, f)
SW_LEN = lambda clip: int(perf.clip_frame(clip, SW_FLY) - clip.start)


def do_swing(clip, start_hips, sag, apex=0.5, end=None):
    f0, f1 = int(clip.start), int(clip.start) + SW_LEN(clip)
    end = end if end is not None else hp(f1)
    path = swing.arc(start_hips, end, sag=sag, apex=apex)
    swing.follow(perf, path, f0, f1 - 1)                     # the next shot owns frame f1 (hard cut)
    return path, f0, f1


p1, a1, b1 = do_swing(sw1, Vector((2.0, 30.0, 18.0)), sag=8.0, apex=0.45)
HANG_HIPS = Vector((HANG2[0], HANG2[1], BB_BOT - 0.9))
p2, a2, b2 = do_swing(sw2, hp(int(web2.end) - 2), sag=3.0, end=HANG_HIPS)
m0, m1 = int(moon.start) + 4, int(moon.end)
mh = hp(m0)
swing.follow(perf, lambda t: mh + Vector((-6.5 * t, 0, 0)), m0, m1 - 1)              # glide back along the screen frame
if MOON == "Walking":                                                                   # fallback: a walk played backwards
    for t in rig.animation_data.nla_tracks:
        for st in t.strips:
            if st.action.name == "Walking" and st.frame_start >= moon.start - 1:
                st.use_reverse = True
d0, d1 = int(dive.start) + 2, int(dive.end) - 6
dh = hp(d0)
swing.follow(perf, swing.hop(dh, Vector((3.8, 33.6, dh.z)), 1.6), d0, d1)            # clear of the train, clear of the trees
# path keys own their frames; re-assert each shot's height right after any path that ran into it
FOLLOWED = [(a1, b1 - 1), (a2, b2 - 1), (m0, m1 - 1), (d0, d1)]
for a_, b_, z, inv in HEIGHTS:
    for fa, fb in FOLLOWED:
        if fa <= a_ <= fb + 1 <= b_ or a_ <= fb + 1 <= b_:
            anim.key(perf.root, "location", fb + 1, z, 2, "const")

# ------------------------------------------------------------------ polish
airborne = [sw1, perch1, web2, sw2, hang2, cling, frus, worry, moon, perch7, conf7, fin_land, dive]
lock_err = perf.ground_lock(int(tick.start), int(flop.end), skip=airborne)
END = int(flop.start) + 105
sc.frame_end = END
hips = lambda f: perf.bone_world(HIPS, int(f))

# ------------------------------------------------------------------ webs
webs = fx.WebShots(rig, fx.collection("Webs"))
A1 = Vector((-9.3, 12.0, 27.0))
webs.shot("Web_S1", R_HAND, lambda f: A1, a1 - 3, a1, b1 - 4)
W2 = int(perf.clip_frame(web2, hit_pk))
A2 = Vector((BB_C.x + 3.0, BB_C.y - 0.1, BB_BOT + 0.05))
webs.shot("Web_Zip2", R_HAND, lambda f: A2, W2 - 4, W2, b2)
top5 = hips(frus.start + 4)
webs.shot("Web_Sub", FOOT_TOE, lambda f: Vector((top5.x, top5.y, 14.0)), int(frus.start), int(frus.start), int(frus.end) + 2)

# ------------------------------------------------------------------ S3 ticker: a light streak racing along it, his head chasing it
glint = box("TickerGlint", (0.35, 0.05, 0.9), TK_C, fx.material("Glint", (1.0, 0.85, 0.45), emit=12.0))
left, right = TK_C.x + TK_W / 2 - 0.4, TK_C.x - TK_W / 2 + 0.4             # from the camera: +x is screen-left
gy = TK_C.y + TICK.normal.y * 0.42
f = int(tick.start) + 4
keys_g = []
for d_ in (34, 26, 19, 14, 10, 8, 7, 6, 6, 6):
    keys_g += [(f, Vector((left, gy, TK_C.z)), "const"), (f + d_, Vector((right, gy, TK_C.z)), "lin")]
    f += d_ + 1
anim.keys(glint, "location", keys_g)
anim.visible(glint, [(1, False), (int(tick.start), True), (int(tick.end), False)])
for o in [ticker] + list(ticker.children):
    anim.visible(o, [(1, False), (int(tick.start) - 2, True), (int(tick.end) + 2, False)])
look_t = office._look(rig.pose.bones["mixamorig:Head"], glint, "Look ticker")
anim.keys(look_t, "influence", [(int(tick.start), 0.0, "lin"), (int(tick.start) + 6, 0.95, "lin"), (int(tick.end) - 4, 0.95, "lin"),
                                (int(tick.end), 0.0, "lin")])

# ------------------------------------------------------------------ S4 bus stop: the graph lightbox + spiders (he's on the roof)
bugs_at = T["vo4"] + F(word(4, "bugs") * FPS)
sys_start = bugs_at - 130
city.sign("BusAd", seq0("st_bugs"), BUS_AD_C, BUS_AD_N, BUS_AD_W, emit=1.4, frame="lightbox", seq=(BUG_N, sys_start))
for k, dy in enumerate((-1.2, 1.2)):
    box(f"BusAdLeg{k}", (0.12, 0.12, BUS_AD_C.z - BUS_AD_W / 16 * 9 / 2), (BUS_AD_C.x + 0.12, BUS_AD_C.y + dy,
        (BUS_AD_C.z - BUS_AD_W / 16 * 9 / 2) / 2), steel)
spiders = fx.Spiders(paths.SPIDER_GLB, size=0.4)
rs = random.Random(5)
for k in range(12):
    f0 = bugs_at + 4 + k * 3
    out_ = BUS_AD_C + Vector((-0.12, rs.uniform(-1.4, 1.4), rs.uniform(-0.6, 0.5)))
    drop = Vector((out_.x - 0.4, out_.y, 0.0))
    ang = rs.uniform(0, 2 * math.pi)
    near = Vector((ROOF_SPOT[0] + 1.9 * math.cos(ang), ROOF_SPOT[1] + 1.3 * math.sin(ang), 0.0))   # circling the shelter
    tn = int(cling.start) + rs.randint(0, 12)
    spiders.add([(f0, out_), (f0 + 8, (out_ + drop) / 2 + Vector((0, -0.2, 0.05))), (f0 + 14, drop), (tn, near),
                 (tn + 18, near + Vector((rs.uniform(-0.4, 0.4), rs.uniform(-0.4, 0.4), 0))),
                 (int(cling.end) + 4, near + Vector((rs.uniform(-0.6, 0.6), rs.uniform(-0.6, 0.6), 0)))], walk_speed=3.0)

# ------------------------------------------------------------------ S6 the big screen: risks pop on their words, customers leave
tiles = [T["vo6"] + F(word(6, w) * FPS) for w in ("downtime", "security", "slow", "bad")]
SCR_OFF = 0.9
screen = city.sign("TSquare", img("st_quad_0"), SCR_C, SCR_N, SCR_W, emit=1.3, frame="led", offset=SCR_OFF)
for k, f in enumerate(tiles):
    lay = city.sign(f"TSquare{k + 1}", img(f"st_quad_{k + 1}"), SCR_C + SCR_N * 0.01 * (k + 1), SCR_N, SCR_W, emit=1.3,
                    offset=SCR_OFF)
    anim.visible(lay, [(1, False), (f, True)])
LEAVE_AT = tiles[-1] + 22
lv = city.sign("TSquareLeave", seq0("st_leaving"), SCR_C + SCR_N * 0.06, SCR_N, SCR_W, emit=1.3, offset=SCR_OFF,
               seq=(96, LEAVE_AT))
anim.visible(lv, [(1, False), (LEAVE_AT, True)])

# ------------------------------------------------------------------ S7 rooftop screen (two slides)
rs1 = city.sign("RoofScreen1", img("roof_competitive"), RS_C, Vector((-1, 0, 0)), 6.2, emit=1.2, frame="led")
rs2 = city.sign("RoofScreen2", img("roof_layer"), RS_C + Vector((-0.01, 0, 0)), Vector((-1, 0, 0)), 6.2, emit=1.2)
anim.visible(rs2, [(1, False), (T["vo8"] - 4, True)])
for k, dy in enumerate((-2.2, 2.2)):
    box(f"RoofLeg{k}", (0.15, 0.15, 3.2 - 1.74), (RS_C.x + 0.15, RS_C.y + dy, ROOF_Z + (3.2 - 1.74) / 2), steel)

# ------------------------------------------------------------------ S8/S9 the runaway train
TRAIN_X = 0.6
NET_Y, NET_W, NET_H = 26.0, 17.6, 6.6
net = city.sign("WebNet", img("web_net"), Vector((-0.3, NET_Y, 3.3)), Vector((0, -1, 0)), NET_W, aspect=NET_W / NET_H,
                offset=0.0, emit=0.6, alpha=True, coll=fx.collection("Train"))
net_back = city.sign("WebNetBack", img("web_net"), Vector((0, 0.01, 0)), Vector((0, 1, 0)), NET_W, aspect=NET_W / NET_H,
                     offset=0.0, emit=0.6, alpha=True, coll=fx.collection("Train"))
net_back.parent = net
net_back.location = (0, 0.02, 0)
net_back.rotation_euler = (0, 0, math.pi)                                   # faces north, text reads correctly from there
for o_ in (net, net_back):
    o_.data.materials[0].use_backface_culling = True                     # each face shows only from its own side
anim.keys(net, "scale", [(NET_F - 2, Vector((0.02, 1, 0.02)), "out"), (NET_F + 8, Vector((1, 1, 1)), "back")])
for o_ in (net, net_back):
    anim.visible(o_, [(1, False), (NET_F - 2, True), (REL + 8, False)])
shot.sfx("web_thwip", NET_F - 3)
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=os.path.join(paths.MIXAMO_CLIPS, "sketchfab_subway_r142", "model.glb"))
src = [o for o in bpy.data.objects if o not in before]
tcoll = fx.collection("Train")
for o in src:
    for cl in list(o.users_collection):
        cl.objects.unlink(o)
    tcoll.objects.link(o)
src_meshes = [o for o in src if o.type == "MESH"]
bpy.context.view_layer.update()
mats = {o: o.matrix_world.copy() for o in src_meshes}
CAR_L, CAR_FRONT = 20.0, 9.85
LABELS = ["car_engineers", "car_customers", "car_product"]
cars = []
for i in range(3):
    root = fx.empty(f"Car{i}", (TRAIN_X, 0, -0.2), tcoll, 0.5)
    for o in src_meshes:
        cp = o if i == 0 else o.copy()
        if i:
            tcoll.objects.link(cp)
        cp.parent = root
        cp.matrix_parent_inverse.identity()
        cp.matrix_basis = mats[o]
    # roof label (read from the helicopter on the west side): a flat plane on the roof
    me = bpy.data.meshes.new(f"CarRoof{i}")
    w, l = 2.5, 17.0
    me.from_pydata([(-w / 2, l / 2, 3.78), (-w / 2, -l / 2, 3.78), (w / 2, -l / 2, 3.78), (w / 2, l / 2, 3.78)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, loop in enumerate(me.loops):
        uv.data[li].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][loop.vertex_index]
    lab = bpy.data.objects.new(f"CarRoof{i}", me)
    tcoll.objects.link(lab)
    me.materials.append(city.image_material(f"CarRoof{i}_Mat", img(LABELS[i]), emit=0.9))
    lab.parent = root
    side = city.sign(f"CarSide{i}", img(LABELS[i]), Vector((-1.45, 0, 2.1)), Vector((-1, 0, 0)), 12.0, aspect=3000 / 520,
                     offset=0.0, emit=0.6, coll=tcoll)
    side.parent = root
    cars.append(root)
for o in src:
    if o.type != "MESH" and o.parent is None:
        o.hide_render = o.hide_viewport = True
# motion: the front car's nose position over time
y_start, y_contact, y_stop = -95.0, NET_Y - 0.4, NET_Y + 1.6
contact = CAR_F[0] - 8
stop_f = CAR_F[1] + 10
nose = [(T["vo13"] - 10, y_start, "lin"), (contact, y_contact, "out"), (stop_f, y_stop, "out"), (REL + 2, y_stop, "in"),
        (REL + 18, y_stop + 18.0, "lin")]
for i, root in enumerate(cars):
    off = -CAR_FRONT - i * CAR_L
    anim.keys(root, "location", [(f_, Vector((TRAIN_X, y + off, -0.2)), e) for f_, y, e in nose], )
anim.keys(net, "location", [(contact, Vector((-0.3, NET_Y, 3.3)), "out"), (stop_f, Vector((-0.3, NET_Y + 1.5, 3.3)), "out"),
                            (REL, Vector((-0.3, NET_Y + 1.5, 3.3)), "in"), (REL + 8, Vector((-0.3, NET_Y + 3.0, 0.4)), "lin")])
anim.keys(net, "scale", [(REL, Vector((1, 1, 1)), "in"), (REL + 8, Vector((1.2, 1, 0.05)), "lin")])
shot.sfx("block_thud", contact)
shot.sfx("cartwheel_whoosh", REL + 2)
# derail: the cars jackknife across the plaza; the money car spills everything
rr = random.Random(9)
crash_end = [(Vector((TRAIN_X + 3.5, 49.0, -0.2)), Vector((0.0, 1.15, 0.7))),
             (Vector((TRAIN_X - 4.0, 33.0, -0.2)), Vector((0.0, -1.05, -0.9))),
             (Vector((TRAIN_X + 2.0, 14.0, 0.4)), Vector((0.25, 1.45, 0.45)))]
for i, (root, (endp, endr)) in enumerate(zip(cars, crash_end)):
    s0 = REL + 18 + i * 3
    p0 = Vector((TRAIN_X, y_stop + 18.0 - CAR_FRONT - i * CAR_L, -0.2))
    anim.keys(root, "location", [(s0, p0, "lin"), (s0 + 14, (p0 + endp) / 2 + Vector((0, 0, 0.8)), "out"), (s0 + 24, endp, "bez")])
    anim.keys(root, "rotation_euler", [(s0, Vector((0, 0, 0)), "in"), (s0 + 24, endr, "out")])
CRASH = max(CRASH, REL + 22)
shot.sfx("tower_crash", REL + 22)
cash_mat = fx.material("CashSide", (0.29, 0.6, 0.38), rough=0.6)
for k in range(8):
    ob = box(f"Cash{k}", (0.8, 0.4, 0.35 + 0.08 * (k % 2)), (0, 0, 0), cash_mat, tcoll)
    ob.parent = cars[2]
    ob.location = Vector((rr.uniform(-0.7, 0.7), -7.0 + k * 1.9, 4.0))
    anim.visible(ob, [(1, False), (cash_f - 4 + k, True)])
    anim.keys(ob, "scale", [(cash_f - 4 + k, Vector((0.01, 0.01, 0.01)), "out"), (cash_f + 4 + k, Vector((1, 1, 1)), "back")])
shot.sfx("cash_flutter", cash_f)
fl = hips(flop.start + 30)
fx.paper_pour("Bills", os.path.join(SCR, "cash_bill.png"), lambda i: Vector((TRAIN_X + rr.uniform(-2, 2), rr.uniform(10, 40), 4.5)),
              (TRAIN_X + 1.0, 30.0), count=160, start=REL + 24, dur=55, spread=(9.0, 12.0), size=(0.3, 0.13), arc=(2.0, 5.0))
# the last bill lands on his mask
head_f = int(flop.start) + 50
hd = perf.bone_world("mixamorig:Head", head_f)
bill = city.sign("BillOnMask", os.path.join(SCR, "cash_bill.png"), hd + Vector((0, 0, 0.16)), Vector((0, 0, 1)), 0.34,
                 aspect=0.3 / 0.13, offset=0.0, coll=tcoll)
anim.keys(bill, "location", [(head_f - 30, hd + Vector((0.4, -0.3, 2.4)), "lin"), (head_f - 15, hd + Vector((-0.3, 0.2, 1.2)), "lin"),
                             (head_f, hd + Vector((0, 0, 0.16)), "out")])
anim.keys(bill, "rotation_euler", [(head_f - 30, Vector((0.6, 0.3, 0.2))), (head_f - 15, Vector((-0.5, 0.2, 1.2))), (head_f, bill.rotation_euler.copy())])
anim.visible(bill, [(1, False), (head_f - 30, True)])

# web lines: his hands to the net while he holds it
hands_net = lambda dx: (lambda f: net.matrix_world.translation + Vector((dx, 0.05, 1.6)))
webs.shot("Web_NetL", L_HAND, hands_net(1.6), NET_F - 4, NET_F, REL)
webs.shot("Web_NetR", R_HAND, hands_net(-1.6), NET_F - 4, NET_F, REL)
webs.bake(range(1, END + 1))
for o in fx.collection("Webs").objects:
    if o.type == "MESH":
        o.data.materials[0] = fx.material("Web_Line", (0.95, 0.97, 1.0), rough=0.35, emit=0.9)

# ------------------------------------------------------------------ SFX
shot.sfx("cartwheel_whoosh", a1 + 6)
shot.sfx("landing_thud", int(perf.clip_frame(sw1, 40)) - 6)
shot.sfx("web_thwip", W2 - 3)
shot.sfx("cartwheel_whoosh", a2 + 4)
shot.sfx("web_thwip", int(frus.start))
shot.sfx("bugs_skitter", bugs_at)
for f in tiles:
    shot.sfx("ui_pop", f)
shot.sfx("landing_thud", int(fin_land.start) + 12)

# ------------------------------------------------------------------ cameras
cam = fx.CameraRig(lens=28, fstop=4.0)


def at(f, loc, tgt, ease="inout", cut=False):
    cam.at(int(f), loc, tgt, ease, cut=cut)


def track(path, f0, f1, offset, look_ahead=0.08, step=3, look=None):
    for f in range(int(f0), int(f1) + 1, step):
        t = (f - f0) / max(1, f1 - f0)
        p = path(t)
        q = path(min(1.0, t + look_ahead)) + (look if look is not None else Vector())
        cam.at(f, p + offset, q, "lin", cut=(f == f0))


def clear_cam(cands, pts):
    for cnd in cands:
        if clear_view(cnd[0], pts):
            return cnd
    return cands[0]


cam.cam.data.clip_end = 800.0
# S0 establishing aerial, ride the swing
cam.lens(1, 18, "const")
at(1, (6.0, 46.0, 44.0), (-2.0, -4.0, 4.0), "lin", cut=True)
at(a1 - 1, (5.0, 40.0, 34.0), (-2.0, 4.0, 8.0), "lin")
track(p1, a1, b1, Vector((7.0, 8.5, 5.0)), 0.12)
# S1 one continuous hero shot from the street: he lands on top of the board, the text right below him
cam.lens(b1 + 1, 24, "const")
b_pts = board_pts(G_C + WALL_G.normal * 0.45, WALL_G.normal, GB_W, GB_H)
s1 = clear_cam([((G_C.x + dx, WALL_G.point.y + 9.4, 2.4), (G_C.x - 0.9, WALL_G.point.y, 6.0)) for dx in (-0.9, 0.3, -1.9, 1.3, -2.9)],
               b_pts)
at(b1 + 1, *s1, "lin", cut=True)
at(int(web2.start), (s1[0][0], s1[0][1] - 0.6, s1[0][2]), s1[1], "lin")
# S2 side-tracking on the swing across (never loses him), then frontal on the billboard with him hanging below it
cam.lens(int(sw2.start), 24, "const")
track(p2, a2, b2, Vector((-10.0, -1.0, 1.0)), 0.05)
cam.lens(int(hang2.start), 24, "const")
s2_cam = ((BB_C.x + 1.0, BB_C.y - 9.2, BB_C.z - 1.0), (BB_C.x + 1.0, BB_C.y, BB_C.z - 1.1))
at(int(hang2.start), *s2_cam, "lin", cut=True)
at(int(hang2.end), (s2_cam[0][0] - 0.3, s2_cam[0][1] + 0.5, s2_cam[0][2]), s2_cam[1], "lin")
# S3 ticker: static, ticker big + him below it
cam.lens(int(tick.start), 24, "const")
tk_pts = board_pts(TK_C + TICK.normal * 0.35, TICK.normal, TK_W, 1.0)
s3 = clear_cam([((TK_C.x + dx, TICK.point.y - 8.6, 2.0), (TK_C.x + 0.6, TICK.point.y, 3.3)) for dx in (0.6, -0.6, 1.6, -1.6, 2.6)],
               tk_pts)
at(int(tick.start), *s3, "lin", cut=True)
at(int(tick.end), s3[0], s3[1], "lin")
# S4 bus stop; then a low angle up at him clinging to the shelter roof, the swarm below
cam.lens(int(first(look4).start), 28, "const")
at(int(first(look4).start), *BUS_CAM, "lin", cut=True)
at(int(cling.start) - 1, BUS_CAM[0], BUS_CAM[1], "lin")
at(int(cling.start), (ROOF_SPOT[0] - 5.6, ROOF_SPOT[1] + 3.4, 3.8), (ROOF_SPOT[0], ROOF_SPOT[1], 2.4), "lin", cut=True)
at(int(cling.end), (ROOF_SPOT[0] - 5.2, ROOF_SPOT[1] + 3.2, 3.9), (ROOF_SPOT[0], ROOF_SPOT[1], 2.4), "lin")
# S5 subway
cam.lens(int(frus.start), 28, "const")
at(int(frus.start), *SUB_CAM, "lin", cut=True)
at(int(frus.end), (SUB_CAM[0][0] - 0.3, SUB_CAM[0][1] - 0.4, 1.7), SUB_CAM[1], "lin")
# S6 the big screen: straight on, a little wider; hold through the moonwalk
cam.lens(int(worry.start), 24, "const")
scr_pts = board_pts(SCR_C + SCR_N * SCR_OFF, SCR_N, SCR_W, SCR_W * 9 / 16)
ts = clear_cam([((SCR_C.x - 0.6 + dx, SCREEN.point.y - 15.0, SCR_C.z - 0.5), (SCR_C.x - 0.6, SCREEN.point.y, SCR_C.z - 0.6))
                for dx in (0, 1.2, -1.2, 2.4, -2.4)], scr_pts)
at(int(worry.start), *ts, "lin", cut=True)
at(int(moon.end), ts[0], ts[1], "lin")
# S7 rooftop at sunset
cam.lens(int(perch7.start), 24, "const")
rf = Vector(RF_SPOT)
roof_cam = ((rf.x - 5.4, rf.y - 2.2, ROOF_Z + 2.0), (RS_C.x - 1.6, RS_C.y + 0.2, ROOF_Z + 1.7))
at(int(perch7.start), *roof_cam, "lin", cut=True)
at(T["vo8"], (roof_cam[0][0] + 0.4, roof_cam[0][1], ROOF_Z + 1.2), roof_cam[1], "inout")
at(int(conf7.end), (roof_cam[0][0] + 1.0, roof_cam[0][1] + 0.3, ROOF_Z + 1.0), roof_cam[1], "lin")
# S8 train: hero landing (low, front) → behind him as he webs the net and the train comes down the avenue
cam.lens(int(fin_land.start), 22, "const")
fs = Vector(FIN_SPOT)
at(int(fin_land.start), (fs.x + 1.6, fs.y - 4.2, 0.55), (fs.x, fs.y, 1.3), "lin", cut=True)
at(int(shoot.start), (fs.x + 1.0, fs.y + 6.5, 2.4), (TRAIN_X, NET_Y - 10.0, 2.4), "lin", cut=True)
at(contact - 12, (fs.x + 0.8, fs.y + 5.8, 2.3), (TRAIN_X, NET_Y - 6.0, 2.4), "lin")
# helicopter tracking over the cars: each label as it's spoken
car_c = lambda i, f: cars[i].matrix_world.translation


def heli(f0, f1, i):
    for f in range(int(f0), int(f1) + 1, 2):
        sc.frame_set(f)
        cpos = cars[i].matrix_world.translation.copy()
        cam.at(f, cpos + Vector((-8.6, -1.0, 12.0)), cpos + Vector((0.4, 0.0, 3.6)), "lin", cut=(f == int(f0)))


cam.lens(contact - 11, 20, "const")
heli(contact - 11, CAR_F[1] - 8, 0)
heli(CAR_F[1] - 7, CAR_F[2] - 8, 1)
heli(CAR_F[2] - 7, REL - 6, 2)
# the release: low wide from the north-east sidewalk; train bursts through, derails across the plaza
cam.lens(REL - 5, 20, "const")
at(REL - 5, (3.6, 45.0, 2.4), (TRAIN_X + 1.2, 28.0, 2.2), "lin", cut=True)
at(CRASH + 20, (3.8, 46.0, 3.0), (TRAIN_X + 1.2, 36.0, 1.4), "lin")
# end: top-down on him, the bill lands on his mask, then a helicopter pull-out over the wreck
cam.lens(head_f - 34, 35, "const")
at(head_f - 34, (fl.x + 0.3, fl.y - 0.6, 2.3), (fl.x, fl.y, 0.2), "lin", cut=True)
at(head_f + 22, (fl.x + 0.3, fl.y - 0.5, 1.9), (fl.x, fl.y, 0.2), "lin")
cam.lens(head_f + 23, 20, "const")
at(head_f + 23, (fl.x - 3.0, fl.y - 6.0, 9.0), (fl.x + 2.0, fl.y + 6.0, 0.0), "lin", cut=True)
at(END, (fl.x - 6.0, fl.y - 16.0, 30.0), (fl.x + 2.0, fl.y + 8.0, 0.0), "in")
cam.shake(int(perf.clip_frame(sw1, 40)), amp=0.05, dur=8)
cam.shake(contact, amp=0.06, dur=10)
cam.shake(CRASH, amp=0.1, dur=18)
office.face_camera(cam.cam, [(c.start + 4, c.end - 2) for c in [look4] + ([] if have("MX Taunt") else [conf7])], amount=0.45)
fx.char_lights(rig, cam.cam)
office.present_to(T["vo1"] + 4, (G_C.x - 1.0, G_C.y + 0.4, G_C.z), hips(T["vo1"]).x)

VO_CUES = {n: T[f"vo{n}"] for n in range(1, 14)}
shot.finish(NAME, exposure=-0.35, samples=24, view="AgX", grade="AgX - Punchy",
            markers=[(f"vo {n}", f) for n, f in VO_CUES.items()] + [
                ("S1 board", T["vo1"]), ("S2 billboard", int(sw2.start)), ("S3 ticker", int(tick.start)),
                ("S4 bus", T["vo4"]), ("S5 subway", T["vo5"]), ("S6 screen", T["vo6"]), ("S7 roof", int(perch7.start)),
                ("S8 train", int(fin_land.start)), ("S9 release", REL), ("end", END)])
cues = sorted(VO_CUES.items(), key=lambda kv: kv[1])
for (a, fa), (b, fb) in zip(cues, cues[1:]):
    if fa + dur(a) * FPS > fb:
        print(f"VO OVERLAP {a}->{b}: {(fa + dur(a) * FPS - fb) / FPS:.2f}s")
print(f"STREET frames 1-{END} ({END / FPS:.1f}s)  ground-lock {lock_err * 100:.1f} cm  optional clips:",
      {n: have(n) for n in ("MX Moonwalk 1", "MX Terrified", "MX Taunt", "MX Backflip")})
