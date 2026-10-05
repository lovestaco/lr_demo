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
    grid_a = [k / 10.0 - 0.95 for k in range(20)]                # dense: thin poles and pipes don't slip between rays
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
GB_W, GB_H = 6.4, 3.6
for gx in (-18.0, -20.0, -16.0, -22.0, -24.0, -14.0, -26.0, -28.0):
    fx_, hit = city.flat_spot(c, [gx], 0.0, -1, 5.6, GB_W)
    if hit is None:
        continue
    G_C = Vector((gx, hit.point.y, 5.6))
    mural_cam = ((gx + 3.0, 2.6, 1.6), (gx + 1.8, hit.point.y, 3.6))
    if clear_view(mural_cam[0], board_pts(G_C, hit.normal, GB_W, GB_H)):
        break
WALL_G = hit
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
BB_TOP = Vector((BB_C.x + 1.2, BB_C.y + 0.15, BB_C.z + 9.6 / 3.0 / 2 + 0.14))
TK_C = Vector((14.0, TICK.point.y, 11.5))
ticker = city.sign("Ticker", img("ticker_faster"), TK_C, TICK.normal, 9.6, aspect=3600 / 420, emit=2.2, frame="led")
px, POST = city.flat_spot(c, [26.0, 24.8, 24.4, 25.2, 24.0, 23.6], 0.0, -1, 2.0, 3.0)
POST_C = Vector((px, POST.point.y, 2.7))                         # above head height: he never covers it
SUB_N = 180
subway = city.sign("Subway", seq0("st_queue"), POST_C, POST.normal, 2.6, emit=1.4, frame="lightbox", seq=(SUB_N, 1),
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
BUS_AD_C = BUS + Vector((-2.08, 0.0, 1.35))
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


def swing_clip(face, at, speed=SW_SPEED):
    return perf.then(SW, frm=1, to=57, speed=speed, face=face, in_place=1.0, at=at)


G_SPOT = (G_C.x + 2.2, WALL_G.point.y + 2.8)    # below-right of the wall board (it hangs above his head)
# S0 aerial swing down the avenue → crouch landing at the mural
sw1 = swing_clip(face=-160, at=G_SPOT)
rise1 = perf.then("Breathing Idle", length=22, blend=14, face=20)
talk1 = talk(hold(1, 0.9), face=20)
web2 = perf.then("Standing 1H Magic Attack 02", frm=16, to=40, speed=1.1, blend=8, face=150)    # line up to the billboard
# S2 swing up onto the billboard, perch
BB_SPOT = (BB_TOP.x, BB_TOP.y)
sw2 = swing_clip(face=180, at=BB_SPOT, speed=0.55)                                   # zip up the line, unhurried
perch2 = perf.then(SW, frm=52, to=57, speed=5 / max(30, hold(2, 0.8)), blend=6, face=10)
# S3 swing east along the cross street past the ticker → lands by the bus stop
BUS_SPOT = (BUS.x - 3.6, BUS.y + 2.2)
web3 = perf.then("Standing 1H Magic Attack 02", frm=16, to=40, speed=1.1, blend=6, face=60)
sw3 = swing_clip(face=100, at=BUS_SPOT)
look4 = talk(F(word(4, "bugs") * FPS) + 20, face=40)
shock = perf.then("CMU 120_16 Mickey Surprised", frm=140, to=262, blend=6, face=20, in_place=0.8)
# S5 subway lightbox (cut)
SUB_SPOT = (POST_C.x - 1.5, POST.point.y + 1.6)                 # just screen-right of the board, in front
frus = talk(hold(5, 0.8), face=-20, at=SUB_SPOT)
# S6 the intersection screen (cut): watching the risks pop, worried
TS_SPOT = (23.4, -1.2)
worry = perf.then("CMU 79_71 sad", frm=20, to=20 + hold(6, 1.0), face=170, at=TS_SPOT)
# S7 rooftop (cut): perched on the parapet, then up and confident
RF_SPOT = (10.2, -17.5)
perch7 = perf.then("Hard Landing", frm=30, to=44, speed=14 / max(20, hold(7, 0.7)), face=-70, at=RF_SPOT)
conf7 = talk(hold(8, 1.0), face=-60, blend=12)
# S8 the finale building at the end of the avenue (on the plaza): each floor lights up with its label,
# then he yanks the ground floor out and the whole building pancakes
FIN_C = Vector((0.0, 59.6))
FX_SPOT = (1.2, 47.5)
drop8 = perf.then("Hard Landing", frm=8, to=60, speed=1.15, face=170, at=FX_SPOT)
LIGHT_WORD = [(9, "inspection"), (9, "engineers"), (10, "customers"), (11, "competitive")]
perf.build()
T = {}
T["vo1"] = int(rise1.start) + 6
T["vo2"] = int(perch2.start) + 4
T["vo3"] = int(web3.start) + 2
T["vo4"] = int(look4.start) + 4 if not hasattr(look4, "cycles") else int(look4.cycles[0].start) + 4
T["vo5"] = int(first(frus).start) + 6
T["vo6"] = int(worry.start) + 8
T["vo7"] = int(perch7.start) + 10
T["vo8"] = int(first(conf7).start) + 12
T["vo9"] = int(drop8.end) + 8
for n in (10, 11, 12):
    T[f"vo{n}"] = T[f"vo{n - 1}"] + F((dur(n - 1) + 0.15) * FPS)
lit = [T[f"vo{n}"] + F(word(n, w) * FPS) for n, w in LIGHT_WORD]
cash_f = T["vo11"] + F(word(11, "money") * FPS)
Y1 = T["vo12"] + F(word(12, "inspection") * FPS)
show = talk(Y1 + 6 - (int(drop8.end) - 10), face=175)
pull = perf.then("Pull Heavy Object Stop", start=Y1 - 4, to=30, speed=1.0, blend=12, face=170)
slump = perf.then("Hard Landing", frm=19, to=28, speed=0.8, blend=8, face=170)
flop = perf.then("Fallen Idle", length=150, blend=16, face=60)
perf.build()

# ------------------------------------------------------------------ body to camera on the talk beats
_cams = {}


def aim_for(clip_group, cam_loc):
    for c_ in (clip_group.cycles if hasattr(clip_group, "cycles") else [clip_group]):
        _cams[id(c_)] = Vector(cam_loc)


BUS_CAM = ((BUS_AD_C.x - 6.5, BUS_AD_C.y + 3.4, 1.5), (BUS_AD_C.x + 0.4, BUS_AD_C.y + 0.4, 1.2))
SUB_CAM = ((POST_C.x + 1.0, POST_C.y + 6.6, 1.6), (POST_C.x - 0.2, POST_C.y, 2.2))
for dx, dy in [(dx_ * 0.6, dy_) for dy_ in (6.6, 5.4, 7.6) for dx_ in (2, 0, 4, -2, 6, -4, 8, -6)]:
    cand = ((POST_C.x + dx, POST_C.y + dy, 1.6), (POST_C.x - 0.2, POST_C.y, 2.2))
    if clear_view(cand[0], board_pts(POST_C + POST.normal * 0.12, POST.normal, 2.6, 1.46)):
        SUB_CAM = cand
        print("SUBCAM", dx, dy)
        break
aim_for(talk1, mural_cam[0])
aim_for(look4, BUS_CAM[0])
aim_for(frus, SUB_CAM[0])
aim_for(conf7, (RF_SPOT[0] - 5.5, RF_SPOT[1] - 2.2, 0))
spans = [(int(g.start), int(g.end), _cams[id(first(g))]) for g in (talk1, look4, frus, conf7)]


def facing_cam(f):
    for a_, b_, p in spans:
        if a_ <= f <= b_:
            return (p.x, p.y)
    h = perf.bone_world(HIPS, f)
    return (h.x, h.y - 5)


square_err = perf.square_up([talk1, look4, frus, conf7], facing_cam)

# ------------------------------------------------------------------ root: heights for perches (before swings)
perf.root_z([(int(perch2.start) - 1, 0.0, "const"), (int(perch2.start), BB_TOP.z, "const"),
             (int(perch2.end), BB_TOP.z, "const"), (int(perch2.end) + 1, 0.0, "const")])
perf.root_z([(int(perch7.start) - 1, 0.0, "const"), (int(perch7.start), ROOF_Z, "const"),
             (int(conf7.end), ROOF_Z, "const"), (int(conf7.end) + 1, 0.0, "const")])

# ------------------------------------------------------------------ swings: real arcs (after build + root_z)
hp = lambda f: perf.bone_world(HIPS, f)
SW_LEN = lambda clip: int(perf.clip_frame(clip, SW_FLY) - clip.start)


def do_swing(clip, start_hips, sag, apex=0.5):
    f0, f1 = int(clip.start), int(clip.start) + SW_LEN(clip)
    end = hp(f1)                                         # where the clip's own landing takes over
    path = swing.arc(start_hips, end, sag=sag, apex=apex)
    swing.follow(perf, path, f0, f1)
    return path, f0, f1


p1, a1, b1 = do_swing(sw1, Vector((2.0, 30.0, 18.0)), sag=10.0, apex=0.45)
p2, a2, b2 = do_swing(sw2, Vector((G_SPOT[0] - 0.5, G_SPOT[1] + 0.5, 1.6)), sag=-3.5)        # up and over onto the billboard
p3, a3, b3 = do_swing(sw3, Vector((BB_SPOT[0] + 1.0, BB_SPOT[1] - 1.0, BB_TOP.z + 1.2)), sag=7.0, apex=0.4)

# ------------------------------------------------------------------ polish
airborne = [sw1, sw2, perch2, sw3, perch7, first(conf7), drop8]
lock_err = perf.ground_lock(int(rise1.start), int(flop.end), skip=airborne)
END = int(flop.start) + 75
sc.frame_end = END
hips = lambda f: perf.bone_world(HIPS, int(f))

# ------------------------------------------------------------------ webs: from the gripping hand to an anchor up on a facade
webs = fx.WebShots(rig, fx.collection("Webs"))
anchor = lambda path, x_side, lift=14.0: (lambda f: None)
A1 = Vector((-9.3, 12.0, 27.0))                               # high on the NW corner building
A2 = Vector((BB_TOP.x - 0.6, BB_TOP.y, BB_TOP.z + 0.05))
A3 = Vector(((p3(0).x + p3(1).x) / 2 + 3.0, TICK.point.y - 0.05, 17.5))      # on the ticker building
webs.shot("Web_S1", R_HAND, lambda f: A1, a1 - 3, a1, b1 - 4)
W2 = int(perf.clip_frame(web2, hit_pk))
webs.shot("Web_Zip2", R_HAND, lambda f: A2, W2 - 4, W2, b2 - 2)
W3 = int(perf.clip_frame(web3, hit_pk))
webs.shot("Web_S3", R_HAND, lambda f: A3, W3 - 4, W3, b3 - 4)

# ------------------------------------------------------------------ S4 bus stop: the graph lightbox + spiders
bugs_at = T["vo4"] + F(word(4, "bugs") * FPS)
sys_start = bugs_at - 130                                      # sequence frame 130 = spiders appear on the graph
city.sign("BusAd", seq0("st_bugs"), BUS_AD_C, BUS_AD_N, 2.4, emit=1.4, frame="lightbox", seq=(BUG_N, sys_start))
spiders = fx.Spiders(paths.SPIDER_GLB, size=0.4)
rs = random.Random(5)
him = hips(shock.start + 12)
for k in range(10):
    f0 = bugs_at + 4 + k * 3
    out_ = BUS_AD_C + Vector((-0.12, rs.uniform(-1.0, 1.0), rs.uniform(-0.5, 0.4)))
    drop = Vector((out_.x - 0.4, out_.y, 0.0))
    ang = rs.uniform(-2.8, -0.3)
    near = Vector((him.x + 0.9 * math.cos(ang), him.y - 0.3 + 0.8 * math.sin(ang), 0.0))
    flee = Vector((him.x + rs.choice((-1, 1)) * rs.uniform(4, 6), him.y - rs.uniform(1, 3), 0.0))
    tn = int(shock.start) + 14 + rs.randint(0, 10)
    spiders.add([(f0, out_), (f0 + 8, (out_ + drop) / 2 + Vector((0, -0.2, 0.05))), (f0 + 14, drop), (tn, near),
                 (tn + 22, near), (tn + 22 + rs.randint(26, 40), flee)], walk_speed=3.0)

# ------------------------------------------------------------------ S6 intersection screen: risks pop on their words
tiles = [T["vo6"] + F(word(6, w) * FPS) for w in ("downtime", "security", "slow", "bad")]
SCR_OFF = 0.9                                                  # mounted out from the facade: nothing crosses it
screen = city.sign("TSquare", img("st_quad_0"), SCR_C, SCR_N, 9.2, emit=1.3, frame="led", offset=SCR_OFF)
mat = screen.data.materials[0]
tex = next(n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE")
# swap images over time: one material per state, keyed via a mix of images is heavy; use separate planes
for k, f in enumerate(tiles):
    lay = city.sign(f"TSquare{k + 1}", img(f"st_quad_{k + 1}"), SCR_C + SCR_N * 0.01 * (k + 1), SCR_N, 9.2, emit=1.3,
                    offset=SCR_OFF)
    anim.visible(lay, [(1, False), (f, True)])

# ------------------------------------------------------------------ S7 rooftop screen (two slides)
rs1 = city.sign("RoofScreen1", img("roof_competitive"), RS_C, Vector((-1, 0, 0)), 6.2, emit=1.2, frame="led")
rs2 = city.sign("RoofScreen2", img("roof_layer"), RS_C + Vector((-0.01, 0, 0)), Vector((-1, 0, 0)), 6.2, emit=1.2)
anim.visible(rs2, [(1, False), (T["vo8"] - 4, True)])
for k, dy in enumerate((-2.2, 2.2)):
    box(f"RoofLeg{k}", (0.15, 0.15, 3.2 - 1.74), (RS_C.x + 0.15, RS_C.y + dy, ROOF_Z + (3.2 - 1.74) / 2), steel)

# ------------------------------------------------------------------ S8/S9 the finale building
for o in list(c.coll.objects):                     # replace the plaza's low building with ours (same footprint)
    if o.type == "MESH":
        pts = [o.matrix_world @ Vector(v) for v in o.bound_box]
        if min(p.y for p in pts) > 54.5 and max(p.y for p in pts) < 64.8 and min(p.x for p in pts) > -13.5 and max(p.x for p in pts) < 13.5:
            o.hide_render = o.hide_viewport = True
bld = city.Building("Finale", FIN_C, width=24.0, depth=8.6, floors=4, storey=3.4, facade_img=img("facade_floor"))
for i, f in enumerate(lit):
    bld.light(i, f, os.path.join(SCR, f"tower_{i}.png"))
    shot.sfx("ui_pop", f)
cash_mat = fx.material("CashSide", (0.29, 0.6, 0.38), rough=0.6)
rr = random.Random(9)
for k in range(6):
    rest = Vector((FIN_C.x - 6 + k * 2.4, FIN_C.y - 1.0 + rr.uniform(-1, 1), bld.top + 0.2))
    ob = box(f"Cash{k}", (0.9, 0.45, 0.4 + 0.1 * (k % 2)), rest, cash_mat, fx.collection("Finale"))
    ob.parent = bld.floors[-1]
    ob.location = rest - bld.floors[-1].location
    anim.visible(ob, [(1, False), (cash_f - 4 + k, True)])
    anim.keys(ob, "scale", [(cash_f - 4 + k, Vector((0.01, 0.01, 0.01)), "out"), (cash_f + 4 + k, Vector((1, 1, 1)), "back")])
shot.sfx("cash_flutter", cash_f)
C = T["vo12"] + F(word(12, "everything") * FPS) - 6
ground = bld.floors[0]
webs.shot("Web_Yank", R_HAND, lambda f: ground.matrix_world.translation + Vector((0, -4.3, -0.6)), Y1 - 4, Y1, Y1 + 10)
shot.sfx("web_thwip", Y1 - 3)
bld.collapse(Y1 + 2, C, pull=Vector((0.15, -1.0, 0.0)).normalized(), dist=5.5)
shot.sfx("tower_crash", C + 4)
fl = hips(flop.start + 30)
fx.paper_pour("Bills", os.path.join(SCR, "cash_bill.png"), lambda i: Vector((FIN_C.x + rr.uniform(-8, 8), FIN_C.y - 3, bld.top)),
              (FIN_C.x, FIN_C.y - 7.0), count=120, start=C + 4, dur=50, spread=(9.0, 3.0), size=(0.3, 0.13), arc=(2.0, 4.0))
fx.paper_pour("BillsOnHim", os.path.join(SCR, "cash_bill.png"), lambda i: Vector((FIN_C.x + rr.uniform(-4, 4), FIN_C.y - 4, bld.top)),
              (fl.x, fl.y), count=40, start=C + 12, dur=45, spread=(1.2, 0.8), size=(0.3, 0.13), arc=(2.0, 4.0))
webs.bake(range(1, END + 1))
for o in fx.collection("Webs").objects:
    if o.type == "MESH":
        o.data.materials[0] = fx.material("Web_Line", (0.95, 0.97, 1.0), rough=0.35, emit=0.9)

# ------------------------------------------------------------------ SFX
shot.sfx("cartwheel_whoosh", a1 + 6)
shot.sfx("landing_thud", int(perf.clip_frame(sw1, 40)) - 6)
shot.sfx("web_thwip", W2 - 3)
shot.sfx("cartwheel_whoosh", a2 + 4)
shot.sfx("landing_thud", int(perf.clip_frame(sw2, 40)) - 6)
shot.sfx("web_thwip", W3 - 3)
shot.sfx("cartwheel_whoosh", a3 + 6)
shot.sfx("landing_thud", int(perf.clip_frame(sw3, 40)) - 6)
shot.sfx("bugs_skitter", bugs_at)
for f in tiles:
    shot.sfx("ui_pop", f)
shot.sfx("landing_thud", int(perf.clip_frame(drop8, 30)) - 6)

# ------------------------------------------------------------------ cameras
cam = fx.CameraRig(lens=28, fstop=4.0)


def at(f, loc, tgt, ease="inout", cut=False):
    cam.at(int(f), loc, tgt, ease, cut=cut)


def track(path, f0, f1, offset, look_ahead=0.08, step=3, look=None):
    """Aerial tracking: camera rides with the swing at an offset, looking a little ahead of him
    (or past him by `look`, to keep a sign in the frame)."""
    for f in range(int(f0), int(f1) + 1, step):
        t = (f - f0) / max(1, f1 - f0)
        p = path(t)
        q = path(min(1.0, t + look_ahead)) + (look if look is not None else Vector())
        cam.at(f, p + offset, q, "lin", cut=(f == f0))


# S0: establishing aerial high over the avenue at sunset, then ride the swing, then a LOW hero angle on the landing
cam.cam.data.clip_end = 800.0
cam.lens(1, 18, "const")
at(1, (6.0, 46.0, 44.0), (-2.0, -4.0, 4.0), "lin", cut=True)
at(a1 - 1, (5.0, 40.0, 34.0), (-2.0, 4.0, 8.0), "lin")
track(p1, a1, b1, Vector((7.0, 8.5, 5.0)), 0.12)
cam.lens(b1 + 1, 24, "const")
gl = hips(perf.clip_frame(sw1, 46))                                                      # the landing crouch
at(b1 + 1, (gl.x + 1.6, gl.y + 4.2, 0.4), (gl.x, gl.y, 0.8), "lin", cut=True)                    # LOW hero: the landing
at(int(rise1.start) + 9, (gl.x + 1.4, gl.y + 3.8, 0.5), (gl.x, gl.y, 1.0), "lin")
# S1: the mural across the street, readable, him beside it
cam.lens(int(rise1.start) + 10, 26, "const")
at(int(rise1.start) + 10, *mural_cam, cut=True)
at(int(web2.start) + 4, (mural_cam[0][0] - 0.3, mural_cam[0][1] - 0.6, 1.9), mural_cam[1], "lin")
# S2: the swing up seen from the street (LOW), then the perch on the billboard, readable
cam.lens(int(sw2.start), 24, "const")
s2_cam = ((BB_C.x + 2.6, -7.4, BB_C.z + 0.2), (BB_C.x + 0.9, BB_C.y, BB_C.z + 0.7))
# the zip: a drone across the street rises with him (looking at him), then settles frontal on the billboard
for f in range(a2, b2 + 1, 3):
    t = (f - a2) / max(1, b2 - a2)
    hpos = p2(t)
    loc = Vector(s2_cam[0]).lerp(Vector(s2_cam[0]), 0) + Vector((0, 0, (hpos.z - BB_C.z) * 0.8))
    cam.at(f, loc, hpos.lerp(Vector(s2_cam[1]), t * t), "lin", cut=(f == a2))
at(int(perch2.start) + 6, *s2_cam, "inout")
at(int(perch2.end), (s2_cam[0][0] - 0.3, s2_cam[0][1] + 0.4, s2_cam[0][2] + 0.1), s2_cam[1], "lin")
for o in [ticker] + list(ticker.children):                          # the ticker only lives in its own shot
    anim.visible(o, [(1, True), (int(sw3.end) + 2, False)])
# S3: aerial tracking alongside the swing (south side, a little above), ticker readable behind him
cam.lens(int(web3.start), 24, "const")
at(int(web3.start), (BB_SPOT[0] + 3.0, BB_SPOT[1] - 6.0, BB_TOP.z + 0.6), (BB_SPOT[0], BB_SPOT[1], BB_TOP.z + 1.2), "lin", cut=True)
track(p3, a3, b3, Vector((-3.5, -8.5, 0.6)), 0.06, look=Vector((2.0, 6.0, 1.5)))
# S4: bus-stop lightbox + him; then the swarm on the floor
cam.lens(b3 + 1, 28, "const")
bus_cam = BUS_CAM
at(b3 + 1, *bus_cam, "lin", cut=True)
at(int(shock.start) + 4, bus_cam[0], bus_cam[1], "lin")
at(int(shock.start) + 5, (bus_cam[0][0] + 1.4, bus_cam[0][1] - 0.6, 1.1), (bus_cam[1][0] - 0.4, bus_cam[1][1], 0.7), "lin", cut=True)
# S5 subway lightbox
cam.lens(int(first(frus).start), 28, "const")
sub_cam = SUB_CAM
at(int(first(frus).start), *sub_cam, "lin", cut=True)
at(int(frus.end), (sub_cam[0][0] - 0.3, sub_cam[0][1] - 0.4, 1.6), sub_cam[1], "lin")
# S6 Times Square screen: LOW wide behind him, screen frontal and readable
cam.lens(int(worry.start), 22, "const")
ts_cam = ((SCR_C.x + 1.2, -6.4, 0.9), (SCR_C.x - 0.2, SCR_C.y - SCR_OFF, SCR_C.z - 1.2))
for dx in (1.2, 2.6, -0.4, 3.8, -1.6):                 # keep lamp posts off the screen
    cand = ((SCR_C.x + dx, -6.4, 0.9), ts_cam[1])
    if clear_view(cand[0], board_pts(SCR_C + SCR_N * SCR_OFF, SCR_N, 9.2, 5.2)):
        ts_cam = cand
        break
at(int(worry.start), *ts_cam, "lin", cut=True)
at(int(worry.end), (ts_cam[0][0] + 0.3, ts_cam[0][1] + 1.2, 1.2), ts_cam[1], "lin")
# S7 rooftop at sunset: drone just off the roof edge, a little above; screen + him + skyline; push on the confident line
cam.lens(int(perch7.start), 24, "const")
rf = Vector(RF_SPOT)
roof_cam = ((rf.x - 5.5, rf.y - 2.2, ROOF_Z + 2.4), (RS_C.x - 1.4, RS_C.y + 0.4, ROOF_Z + 2.2))
at(int(perch7.start), *roof_cam, "lin", cut=True)
at(T["vo8"], (roof_cam[0][0] + 0.4, roof_cam[0][1], ROOF_Z + 1.2), roof_cam[1], "inout")      # dips LOW: confident
at(int(conf7.end), (roof_cam[0][0] + 1.0, roof_cam[0][1] + 0.3, ROOF_Z + 1.0), roof_cam[1], "lin")
# S8 the finale building: the drop (LOW), then wide down the avenue on the building as its floors light up,
# slow push in; S9 the yank + pancake collapse, then a helicopter pull-out over him in the cash
cam.lens(int(drop8.start), 22, "const")
fxs = Vector(FX_SPOT)
at(int(drop8.start), (fxs.x + 2.2, fxs.y - 4.6, 0.5), (fxs.x, fxs.y, 1.5), "lin", cut=True)
bw = ((FIN_C.x - 1.5, FIN_C.y - 24.0, 2.2), (FIN_C.x, FIN_C.y, 6.2))          # between the avenue's tree rows
at(int(drop8.end), *bw, "inout")
at(T["vo12"], (bw[0][0] + 0.6, bw[0][1] + 3.0, 2.0), (bw[1][0], bw[1][1], 5.8), "inout")      # PUSH IN: tension
at(C, (bw[0][0] + 0.8, bw[0][1] + 3.6, 1.9), (bw[1][0], bw[1][1], 5.4), "inout")
at(C + 26, (bw[0][0] + 0.5, bw[0][1] + 2.0, 3.5), (FIN_C.x, FIN_C.y - 4.0, 1.5), "inout")       # PULL OUT: release
at(END, (fl.x - 3.0, fl.y - 10.0, 22.0), (fl.x + 1.0, fl.y + 1.0, 0.0), "in")        # HELICOPTER pull-out over him
cam.shake(int(perf.clip_frame(sw1, 40)), amp=0.05, dur=8)
cam.shake(int(perf.clip_frame(drop8, 30)), amp=0.06, dur=8)
cam.shake(C + 2, amp=0.08, dur=14)
office.face_camera(cam.cam, [(c.start + 4, c.end - 2) for c in (talk1, look4, frus, conf7)], amount=0.45)
fx.char_lights(rig, cam.cam)                                     # film key + warm/cool rims on him only
h = hips(T["vo1"] + 6)
office.present_to(T["vo1"] + 6, (G_C.x + 2.0, G_C.y + 0.3, 2.2), h.x)

VO_CUES = {n: T[f"vo{n}"] for n in range(1, 13)}
shot.finish(NAME, exposure=-0.35, samples=24, view="AgX", grade="AgX - Punchy",
            markers=[(f"vo {n}", f) for n, f in VO_CUES.items()] + [
                ("S1 mural", T["vo1"]), ("S2 billboard", int(sw2.start)), ("S3 ticker", int(sw3.start)),
                ("S4 bus", T["vo4"]), ("S5 subway", T["vo5"]), ("S6 screen", T["vo6"]), ("S7 roof", int(perch7.start)),
                ("S8 finale", int(drop8.start)), ("S9 collapse", C), ("end", END)])
cues = sorted(VO_CUES.items())
for (a, fa), (b, fb) in zip(cues, cues[1:]):
    if fa + dur(a) * FPS > fb:
        print(f"VO OVERLAP {a}->{b}: {(fa + dur(a) * FPS - fb) / FPS:.2f}s")
print(f"STREET frames 1-{END} ({END / FPS:.1f}s)  ground-lock {lock_err * 100:.1f} cm")
