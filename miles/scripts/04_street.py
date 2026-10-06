"""Street piece (~65 s): Spidey's tour of the inspection story through a city at sunset — one continuous journey.

    S0  aerial establishing → he swings down the avenue → lands on top of the wall board
    S1  mural: "You already ship a lot of AI-generated code." → close-up, excited
    S2  over his shoulder: the billboard across the street (two-building shot) → swings over, flips into the hang
    S3  lets go, swings east down to the LED ticker: "Code now ships faster than ever." (close-up, amazed)
    S4  sprints across to the bus stop: graph grows, spiders crawl out on "bugs" → leaps onto the shelter roof
    S5  web-hops to the subway lightbox, hangs upside down: "Human review can't keep up."
    S6  swings up onto the big screen's catwalk: the four risks pop on their words; moonwalks off with the customers
    S7  web-zips up to the rooftop: "How do you stay competitive?" → "You need a better inspection layer." (close-up)
    S8  swings down into the intersection, webs the tower down block by block (+ cash) on the words
    S9  yanks INSPECTION out → collapse, cash rain, he flops → helicopter pull-out

No location cuts: every move between places is visible travel (swing / run / hop / zip); cuts are only
camera angles within a scene (wide → close-up → over-the-shoulder).

    python3 scripts/03c_street_signs.py
    blender -b build/character.blend --python scripts/04_street.py          # -> build/street.blend
"""
import bpy, os, sys, math, random, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mathutils import Vector, Euler, Matrix
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
sun = city.golden_hour(sun_elev=6.0, sun_az=-60.0, strength=7.2)     # lower + warmer than the default: long gold light
sun.data.color = (1.0, 0.66, 0.40)
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
# a service ledge on top of the wall board (what he lands and crouches on: the board alone is 25 cm deep)
LEDGE_TOP = G_C.z + GB_H / 2 + 0.12 + 0.1
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
TK_C = Vector((12.6, TICK.point.y, 4.9))             # ends at x 16.8, clear of the screen catwalk
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
box("Board1Ledge", (GB_W + 0.3, 1.25, 0.1), (G_C.x, WALL_G.point.y + WALL_G.normal.y * 0.68, LEDGE_TOP - 0.05),
    fx.material("Ledge", (0.1, 0.11, 0.12), rough=0.45, metallic=0.7))
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
# Standing beats are placed shots (`at=`, height from HEIGHTS + per-frame contact). Every move between
# locations is a TRAVEL: clips played in place whose root is keyed every frame by swing.follow() from where
# the last shot ends to where the next one starts, so the audience sees him get there (no teleport cuts).
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


SW3 = opt("Swing To Land (3)", SW)                 # deeper, faster arc (variety)
FLIP_CLIP = "MX Front Flip"


def fly(face, speed=SW_SPEED, blend=8, clip=SW, to=SW_FLY):
    """Swing pose (hanging from the line, legs trailing) for a travel path."""
    return perf.then(clip, frm=1, to=to, speed=speed, face=face, in_place=1.0, blend=blend)


def land(face, at, speed=SW_SPEED, clip=SW, frm=SW_FLY, to=57):
    """The swing clip's own landing (continues the fly pose), placed where the travel path ends."""
    return perf.then(clip, frm=frm, to=to, speed=speed, face=face, in_place=1.0, at=at)


def flip_in(face, speed=0.9):
    """Let go of the line and front-flip in the air (the flip's take-off already happened off camera)."""
    return perf.then(FLIP_CLIP, frm=19, to=37, speed=speed, blend=6, face=face, in_place=1.0) if have(FLIP_CLIP) else None


def flip_land(face, at, speed=0.9):
    return (perf.then(FLIP_CLIP, frm=37, to=49, speed=speed, face=face, in_place=1.0, at=at) if have(FLIP_CLIP)
            else land(face, at))


def tuck(length, face, blend=8):
    """Classic upside-down hang: the Hard Landing crouch (knees up, hands in) rolled π on a line from the feet."""
    return perf.then("Hard Landing", frm=28, to=46, speed=18 / length, blend=blend, face=face, in_place=1.0)


INV = math.pi                                 # roll about the depth axis: upside down, still facing the camera
FOOT_TOE = "mixamorig:LeftToeBase"
FOOT = "mixamorig:LeftFoot"
# ---- S0/S1: swing down the avenue, land crouched on TOP of the wall board, facing the street
TOP1 = (G_C.x - 2.5, WALL_G.point.y + WALL_G.normal.y * 0.85)       # on the board's top ledge, screen-right corner
sw1 = perf.then(SW, frm=1, to=57, speed=SW_SPEED, face=-160, in_place=1.0, at=TOP1)
perch1 = perf.then(SW, frm=52, to=57, speed=5 / max(40, hold(1, 0.5) + 10), blend=8, face=180)
happy = perf.then(opt("MX Happy Hand Gesture", "Happy Idle"), frm=8, length=54, blend=12, face=180, in_place=1.0)   # CU: excited
# ---- S2: two-building shot: on his ledge he studies the billboard across the street (over the shoulder)
curious = perf.then(opt("MX Thoughtful Head Shake", "Breathing Idle"), frm=1, length=max(70, hold(2, 0.3)), blend=12,
                    face=175, in_place=1.0)
web2 = perf.then("Standing 1H Magic Attack 02", frm=16, to=40, speed=1.1, blend=8, face=172, in_place=1.0)  # line to the billboard
fly2 = fly(180, speed=0.62, clip=SW3, to=30)                 # swing across + up ...
hang2 = tuck(48, face=0)                                     # ... flips into the hang under the billboard
# ---- S3: lets go, swings east along the north side down to the LED ticker
fly3 = fly(90, speed=0.66)
flip3 = flip_in(90)                                            # lets go and flips ...
TICK_SPOT = (TK_C.x + 2.2, TICK.point.y - 1.5)
land3 = flip_land(90, TICK_SPOT)                               # ... landing on his feet under the ticker
tick = perf.then("Breathing Idle", length=hold(3, 1.0, 75), blend=10, face=180)     # faces the ticker, watching the streak
# ---- S4: sprints across the street to the bus stop; spiders → he leaps onto the shelter roof
run4 = perf.then(opt("MX Sprint", "Two Cycle Sprint"), repeat=4, blend=10, face=0)
stop4 = perf.then(opt("MX Run To Stop", "Run To Stop"), blend=5, face=0)
look4 = talk(F(word(4, "bugs") * FPS) + 14, face=40)
shock = perf.then("CMU 120_16 Mickey Surprised", frm=140, to=176, blend=6, face=20, in_place=0.8)
ROOF_SPOT = (BUS.x - 0.8, BUS.y + 0.1)
hop_a = perf.then(opt("MX Jumping Up", "Hard Landing"), blend=4, face=-60, in_place=1.0)
hop_b = perf.then("Hard Landing", frm=10, to=28, blend=3, face=-60, in_place=1.0)
cling_l = perf.then("Hard Landing", frm=28, to=40, face=-60, at=ROOF_SPOT)
cling = (perf.then("MX Terrified", frm=110, length=64, blend=8, face=-60) if have("MX Terrified") else
         perf.then("Hard Landing", frm=40, to=44, speed=4 / 58, blend=8, face=-60))
# ---- S5: web-swings off the shelter and flips into a hang beside the subway lightbox
fly5 = fly(100, speed=1.0, clip=SW3, to=30)
frus = tuck(hold(5, 0.6), face=180)
# ---- S6: swings across the street up onto the big screen's catwalk; risks pop; moonwalks off with the customers
fly6 = fly(180, speed=0.7)
SCR_W = 9.2
TS_SPOT = (25.0 - SCR_W / 2 + 0.7, SCREEN.point.y - 0.9 - 0.25)
TS_Z = 7.2 - SCR_W / 16 * 9 / 2 - 0.08
land6 = land(180, TS_SPOT, speed=0.7)
worry = perf.then("Hard Landing", frm=30, to=44, speed=14 / (F(word(6, "bad") * FPS) + 44), blend=12, face=0)
MOON = opt("MX Moonwalk 1", "Walking")
moon = perf.then(MOON, blend=8, repeat=3, face=-90, in_place=1.0, speed=1.0)     # faces screen-left, glides screen-right
# ---- S7: web-zips from the end of the catwalk up to the tall rooftop
fly7 = fly(-46, speed=0.6)
flip7 = flip_in(-70)                                           # over the parapet ...
RF_SPOT = (10.2, -17.5)
land7 = flip_land(-70, RF_SPOT)                                # ... onto the roof
perch7 = perf.then("Hard Landing", frm=30, to=44, speed=14 / max(20, hold(7, 0.7)), blend=10, face=-70)
conf7 = (perf.then("MX Taunt", blend=10, face=-40, speed=50 / max(50, hold(8, 0.7))) if have("MX Taunt")
         else talk(hold(8, 0.7), face=-60, blend=12))
# ---- S8: swings down into the intersection and webs the tower down block by block, on the words
fall8 = perf.then(opt("MX Falling", "Hard Landing"), frm=1, length=26, blend=10, face=-143, in_place=1.0)   # leaps off: free fall
fly8 = fly(-143, speed=0.7, blend=6, clip=SW3, to=32)                                    # ... the web catches him
FIN_SPOT = (-2.4, -2.0)
land8 = land(-143, FIN_SPOT, speed=0.6, clip=SW3, frm=32, to=55)
rise8 = perf.then("Breathing Idle", length=26, blend=14, face=20)
T = {}
ORDER = [13, 9, 10, 11, 12]                          # "It starts with inspection" opens the tower
T["vo13"] = int(rise8.end) + 6
for a_, b_ in zip(ORDER, ORDER[1:]):
    T[f"vo{b_}"] = T[f"vo{a_}"] + F((dur(a_) + 0.2) * FPS)
LAND_WORD = [(13, "inspection"), (9, "engineers"), (10, "customers"), (11, "competitive")]
UP = "Standing 2H Magic Attack 01"
UP_LEAD = F(14 / 1.15)                               # clip start -> web hit
lands = [T[f"vo{n}"] + F(word(n, w) * FPS) for n, w in LAND_WORD]
Y1 = T["vo12"] + F(word(12, "inspection") * FPS)     # yanks INSPECTION out
starts = [ld - 12 - UP_LEAD for ld in lands]
builds = []
for k, st in enumerate(starts):
    if k == 0:
        perf.then("Breathing Idle", length=max(8, st + 8 - (int(rise8.end) - 8)), blend=8, face=20)
    builds.append(perf.then(UP, start=st, frm=up_pk - 14, to=up_pk + 20, speed=1.15, blend=8, face=25))
    nxt = starts[k + 1] if k + 1 < len(starts) else Y1 - 40
    perf.then("Breathing Idle", length=max(8, nxt + 8 - (int(builds[-1].end) - 8)), blend=8, face=35)
heave = perf.then("Pull Heavy Object Start", start=Y1 - 40, frm=4, to=40, blend=8, face=75)   # lines taut, leaning back
pull = perf.then("Pull Heavy Object Stop", start=Y1 - 4, to=30, speed=1.0, blend=8, face=75)  # the yank
C_EST = T["vo12"] + F(word(12, "everything") * FPS) - 6
watch = perf.then("Breathing Idle", length=max(20, C_EST + 34 - int(pull.end) + 8), blend=8, face=60)   # stares at the wreck
slump = perf.then("Hard Landing", frm=19, to=28, speed=0.8, blend=8, face=20)                 # knees give way...
flop = perf.then("Fallen Idle", length=150, blend=16, face=-60)                               # ...flat on the street
perf.build()

T["vo1"] = int(perch1.start) + 10
T["vo2"] = int(curious.start) + 6
T["vo3"] = int(tick.start) + 6
T["vo4"] = int(first(look4).start) + 4
T["vo5"] = int(frus.start) + 8
T["vo6"] = int(worry.start) + 8
T["vo7"] = int(perch7.start) + 10
T["vo8"] = (int(conf7.start) + 8) if have("MX Taunt") else int(first(conf7).start) + 12
cash_f = T["vo11"] + F(word(11, "money") * FPS)
C = T["vo12"] + F(word(12, "everything") * FPS) - 6                      # the tower comes down

# ------------------------------------------------------------------ body to camera on the talk beats
BUS_CAM = ((BUS_AD_C.x - 6.2, BUS_AD_C.y + 1.1, 1.5), (BUS_AD_C.x, BUS_AD_C.y + 1.0, 1.35))
SUB_CAM = ((POST_C.x - 1.3, POST_C.y + 5.0, 2.3), (POST_C.x - 1.3, POST_C.y, 2.55))        # close: board + him both big
for dx, dy in [(dx_ * 0.5 - 1.3, dy_) for dy_ in (5.0, 5.5, 4.6, 6.0) for dx_ in (0, 1, -1, 2, -2, 3)]:
    cand = ((POST_C.x + dx, POST_C.y + dy, 2.2), (POST_C.x - 1.3, POST_C.y, 2.5))
    if clear_view(cand[0], board_pts(POST_C + POST.normal * 0.12, POST.normal, 3.6, 2.0)):
        SUB_CAM = cand
        print("SUBCAM", dx, dy)
        break
spans = [(int(g.start), int(g.end), Vector(BUS_CAM[0])) for g in [look4]]


def facing_cam(f):
    for a_, b_, p in spans:
        if a_ <= f <= b_:
            return (p.x, p.y)
    h = perf.bone_world(HIPS, f)
    return (h.x, h.y - 5)


square_err = perf.square_up([look4], facing_cam)

# ------------------------------------------------------------------ heights of the standing shots
last = lambda clip: math.ceil(clip.end - 1e-6) - 1      # a shot's final frame (the next shot owns ceil(end))


def low_rel(clip):
    """Lowest toe height of a clip with the root on the ground (so a shot can stand ON a surface)."""
    return min(min(perf.bone_world(b, f).z for b in ("mixamorig:LeftToeBase", "mixamorig:RightToeBase"))
               for f in range(int(clip.start) + 4, int(clip.end) - 2, 6))


SHELTER_TOP = 2.56
on = lambda clips, floor, until: [(int(c.start), (int(n.start) - 1) if n is not None else until, floor - low_rel(c), c)
                                  for c, n in zip(clips, list(clips[1:]) + [None])]
first_low = low_rel(perch1)
HEIGHTS = ([(int(sw1.start), int(perch1.start) - 1, LEDGE_TOP - first_low, sw1)] +
           on([perch1, happy, curious, web2], LEDGE_TOP, int(fly2.start) - 1) +
           on([cling_l, cling], SHELTER_TOP, int(fly5.start) - 1) +
           on([land6, worry, moon], TS_Z, int(fly7.start) - 1) +
           on([land7, perch7, first(conf7)], ROOF_Z, int(fall8.start) - 1))
HEIGHTS.sort(key=lambda h: h[0])
zk = []
for k, (a_, b_, z, clip) in enumerate(HEIGHTS):
    prev = HEIGHTS[k - 1] if k else None
    if prev is not None and prev[1] + 1 >= a_ and getattr(clip, "at", None) is None and clip.blend > 1:
        zk.append((a_, prev[2], "inout"))                  # blended shots on one surface: ease across the blend
        zk.append((a_ + int(clip.blend), z, "const"))
    else:
        zk.append((a_, z, "const"))
    nxt = HEIGHTS[k + 1][0] if k + 1 < len(HEIGHTS) else None
    if nxt is None or nxt > b_ + 1:
        zk.append((b_ + 1, 0.0, "const"))
perf.root_z([(1, 0.0, "const")] + zk)
# upside down: the roll turns over inside the travel (a flip into the hang, a flip back out of it)
FLIP = 12
anim.keys(perf.root, "rotation_euler", [
    (1, 0.0, "const"),
    (int(hang2.start) - FLIP + 6, 0.0, "inout"), (int(hang2.start) + 6, INV, "const"),
    (int(fly3.start), INV, "inout"), (int(fly3.start) + FLIP, 0.0, "const"),
    (int(frus.start) - FLIP + 6, 0.0, "inout"), (int(frus.start) + 6, INV, "const"),
    (int(fly6.start), INV, "inout"), (int(fly6.start) + FLIP, 0.0, "const")], index=1)

# ------------------------------------------------------------------ travel paths (in time order: each starts where the last ended)
hp = lambda f: perf.bone_world(HIPS, f)
SW_LEN = lambda clip: int(perf.clip_frame(clip, SW_FLY) - clip.start)
TRAVEL = []


def travel(path, f0, f1):
    """Key the root along `path` for f0..f1, then restore what the root did after f1 (a lin key at f1 would
    otherwise drag every frame up to the next key towards the end of the path)."""
    f0, f1 = int(f0), int(f1)
    keep = []
    for i in range(3):
        fc = anim.fcurve(perf.root, "location", i)
        prior = [k for k in fc.keyframe_points if k.co.x <= f1 + 1] if fc else []
        gov = max(prior, key=lambda k: k.co.x) if prior else None
        keep.append((fc.evaluate(f1 + 1) if fc else perf.root.location[i],
                     "const" if gov is not None and gov.interpolation == "CONSTANT" else "lin"))
    swing.follow(perf, path, f0, f1)
    for i, (v, ease) in enumerate(keep):
        anim.key(perf.root, "location", f1 + 1, v, i, ease)
    TRAVEL.append((f0, f1))


def pin(point, f0, f1, sway=0.0, period=60.0):
    """Hold the hips at a point (a hang), with an optional slow pendulum sway along x."""
    p = Vector(point)
    n = max(1, f1 - f0)
    travel(lambda t: p + Vector((sway * math.sin(2 * math.pi * t * n / period), 0, 0)), f0, f1)


MINE = {o.name for o in rig.children_recursive} | {rig.name}


def path_hits(f0, f1, name):
    """Report frames where the body's path cuts through set geometry (hips segment rays + a head-height ray)."""
    bad = []
    for f in range(int(f0), int(f1)):
        a, b = hp(f), hp(f + 1)
        d = b - a
        if d.length > 1e-3:
            h = c.ray(a, d, d.length + 0.3)
            if h is not None and h.obj.name not in MINE and not h.obj.name.startswith(("Web",)):
                bad.append((f, h.obj.name))
    print(f"PATH {name} f{int(f0)}-{int(f1)} hits", bad[:12])


def bez(p0, p1, p2, p3):
    p0, p1, p2, p3 = (Vector(v) for v in (p0, p1, p2, p3))

    def fn(t):
        u = swing.ease_pendulum(t) * 0.6 + t * 0.4
        return (1 - u) ** 3 * p0 + 3 * (1 - u) ** 2 * u * p1 + 3 * (1 - u) * u * u * p2 + u ** 3 * p3
    return fn


def find_anchor(p0, p1, fallback, min_up=7.0, reach=45.0):
    """A real place for the web to stick: the facade / roof edge above the swing (rays fanned up from its middle),
    as close to straight above the middle as possible so he swings under it like a pendulum."""
    p0, p1 = Vector(p0), Vector(p1)
    mid = (p0 + p1) / 2
    top = mid.z
    run = (p1 - p0).xy
    best = None
    for el in (35, 45, 55, 65, 75, 85):
        for az in range(0, 360, 10):
            ce = math.cos(math.radians(el))
            d = Vector((math.cos(math.radians(az)) * ce, math.sin(math.radians(az)) * ce, math.sin(math.radians(el))))
            h_ = c.ray(mid, d, reach)
            if h_ is None or h_.obj.name in MINE or h_.point.z < top + min_up:
                continue
            along = (h_.point.xy - p0.xy).dot(run) / max(1e-6, run.length_squared)
            if not 0.35 <= along <= 1.3:                   # ahead of him, never behind (he swings towards it)
                continue
            off = abs((h_.point.xy - p0.xy).cross(run)) / max(1e-6, run.length)
            if off > 12.0:                                 # roughly in the plane of the swing
                continue
            score = (h_.point.xy - mid.xy).length - 0.35 * (h_.point.z - top)
            if best is None or score < best[0]:
                best = (score, h_.point.copy())
    print("ANCHOR", tuple(round(v, 1) for v in (best[1] if best else Vector(fallback))), "found" if best else "fallback")
    return best[1] if best else Vector(fallback)


def lean(path, f0, f1, anchor, a0, a1, max_deg=55.0, ramp=6):
    """Pendulum body: while the line is attached (a0..a1) the body hangs along it — the root tilts so his long
    axis points at the anchor (centripetal pull along the line), easing in/out over `ramp` frames."""
    fcs = [anim.fcurve(perf.root, "rotation_euler", i) for i in range(3)]
    ev = lambda f: Euler([fc.evaluate(f) if fc else 0.0 for fc in fcs], "XYZ")
    a0, a1 = int(a0), int(a1)
    keep = ev(a1 + 1)
    prev = None
    for f in range(a0, a1 + 1):
        t = (f - f0) / max(1, f1 - f0)
        u = (Vector(anchor) - path(t)).normalized()
        w = max(0.0, min(1.0, (f - a0) / ramp, (a1 - f) / ramp))
        w = w * w * (3 - 2 * w)
        ang = min(math.acos(max(-1.0, min(1.0, u.z))), math.radians(max_deg)) * w
        axis = Vector((0, 0, 1)).cross(u)
        base = ev(f)
        e = base if (axis.length < 1e-6 or ang < 1e-4) else \
            (Matrix.Rotation(ang, 3, axis.normalized()) @ base.to_matrix()).to_euler("XYZ", prev or base)
        for i in range(3):
            anim.key(perf.root, "rotation_euler", f, e[i], i, "lin")
        prev = e
    for i in range(3):
        anim.key(perf.root, "rotation_euler", a1 + 1, keep[i], i, "lin")


# the web anchors: on the billboard, the roof edge, or found on a real facade above each swing
BB_BOT = BB_C.z - 9.6 / 3.0 / 2 - 0.12
HANG_HIPS = Vector((BB_C.x + 3.0, BB_C.y - 0.75, BB_BOT - 0.95))
SUB_HIPS = Vector((POST_C.x - 2.3, POST.point.y + 0.9, 2.6))
A2 = Vector((BB_C.x + 3.0, BB_C.y - 0.1, BB_BOT + 0.05))
A7 = Vector((RF_SPOT[0] - 0.4, RF_SPOT[1] + 1.0, ROOF_Z + 0.3))                       # zip line to the roof edge
# S0: the opening swing down the avenue onto the board
a1, b1 = int(sw1.start), int(sw1.start) + SW_LEN(sw1)
P1_START = Vector((2.0, 30.0, 18.0))
A1 = find_anchor(P1_START, hp(b1), (-9.3, 12.0, 27.0))
p1 = swing.arc(P1_START, hp(b1), sag=8.0, apex=0.45)
lean(p1, a1, b1 - 1, A1, a1, b1 - 6)
travel(p1, a1, b1 - 1)
# S2: ledge → billboard (swing up, flip, hang)
f2a, f2h = int(fly2.start), int(hang2.start) + 6
p2 = swing.arc(hp(f2a - 1), HANG_HIPS, sag=2.5)
lean(p2, f2a, f2h, A2, f2a, f2h - 14)
travel(p2, f2a, f2h)
pin(HANG_HIPS, f2h + 1, int(fly3.start) - 1, sway=0.06)
# S3: billboard → ticker (long swing east along the north side)
f3a, f3b = int(fly3.start), int(land3.start)
e3 = hp(f3b)
p3 = bez(HANG_HIPS, HANG_HIPS + Vector((2.5, -3.5, -3.0)), e3 + Vector((-9.0, -1.5, 7.0)), e3)   # drops out, away from the roof edge
A3 = find_anchor(HANG_HIPS, e3, ((HANG_HIPS.x + TICK_SPOT[0]) / 2, TICK.point.y - 0.05, 24.0))
lean(p3, f3a, f3b - 1, A3, f3a + FLIP, int(perf.clip_frame(fly3, 28)))
travel(p3, f3a, f3b - 1)
# S4: the run is root motion (ground-locked); the hop up onto the shelter roof is a ballistic path
f4a, f4b = int(hop_b.start), int(cling_l.start)
p4 = swing.hop(hp(f4a - 1), hp(f4b), 1.1)
travel(p4, f4a, f4b - 1)
# S5: shelter roof → subway hang (web-swing hop, flip)
f5a, f5h = int(fly5.start), int(frus.start) + 6
cling_end = hp(f5a - 1)
p5 = swing.hop(cling_end, SUB_HIPS, 1.4)                        # springs off the shelter roof, the line catches him
A5 = find_anchor(cling_end, SUB_HIPS, (SUB_HIPS.x - 0.5, POST.point.y + 0.05, 11.0))
lean(p5, f5a, f5h, A5, f5a + 2, f5h - 14)
travel(p5, f5a, f5h)
pin(SUB_HIPS, f5h + 1, int(fly6.start) - 1, sway=0.05)
# S6: subway → catwalk (swing across the street and up)
f6a, f6b = int(fly6.start), int(land6.start)
e6 = hp(f6b)
p6 = swing.arc(SUB_HIPS, e6, sag=3.0)
A6 = find_anchor(SUB_HIPS, e6, ((SUB_HIPS.x + TS_SPOT[0]) / 2, SCREEN.point.y - 0.05, 15.0))
lean(p6, f6a, f6b - 1, A6, f6a + FLIP, int(perf.clip_frame(fly6, 28)))
travel(p6, f6a, f6b - 1)
# moonwalk along the catwalk, with the customers, off the right edge of the screen
m0, m1 = int(moon.start) + 4, int(fly7.start) - 1
mh = hp(m0)
mh = Vector((mh.x, mh.y, hp(int(moon.start) + 14).z))         # standing hip height (not the blend out of the crouch)
MOON_SPEED = 15.0 / (int(moon.end) - 1 - m0)                  # m / frame (v4 pace)
travel(lambda t: mh + Vector((MOON_SPEED * (m1 - m0) * t, 0, 0)), m0, m1)
if MOON == "Walking":                                                                   # fallback: a walk played backwards
    for t in rig.animation_data.nla_tracks:
        for st in t.strips:
            if st.action.name == "Walking" and st.frame_start >= moon.start - 1:
                st.use_reverse = True
# S7: end of the catwalk → web-zip up to the tall rooftop (out over the intersection, up its avenue side)
f7a, f7b = int(fly7.start), int(land7.start)
q0, q3 = hp(f7a - 1), hp(f7b)
p7 = bez(q0, q0 + Vector((-14.0, -4.0, 4.0)), Vector((2.5, -12.0, q3.z + 9.0)), q3)
lean(p7, f7a, f7b - 1, A7, f7a + 2, int(perf.clip_frame(fly7, 26)))
travel(p7, f7a, f7b - 1)
# S8: rooftop → leap, free fall, a web to the corner building catches him → down into the intersection
f8a, f8b = int(fall8.start), int(land8.start)
r0, r3 = hp(f8a - 1), hp(f8b)
p8 = bez(r0, r0 + Vector((-3.0, 2.0, 6.0)), Vector((r3.x + 3.0, r3.y - 6.0, r3.z + 3.0)), r3)
A8 = find_anchor((r0 + r3) / 2, r3, (8.85, 9.4, 16.5), min_up=4.0)       # nothing is above the top of the tallest roof
lean(p8, f8a, f8b - 1, A8, int(fly8.start) + 2, int(perf.clip_frame(fly8, 28)))
travel(p8, f8a, f8b - 1)
for name, (fa, fb) in zip(["S0", "S2", "hang2", "S3", "S4hop", "S5", "frus", "S6", "moon", "S7", "S8"], TRAVEL):
    path_hits(fa, fb, name)

# ------------------------------------------------------------------ polish: feet on the surfaces
LAND_SETTLE = 8                                    # a landing's first frames are still in the air
for a_, b_, top in ((b1 + 1, int(fly2.start) - 1, LEDGE_TOP), (int(cling_l.start) + 4, int(fly5.start) - 1, SHELTER_TOP),
                    (int(land6.start) + LAND_SETTLE, int(fly7.start) - 1, TS_Z),
                    (int(land7.start) + LAND_SETTLE, int(fall8.start) - 1, ROOF_Z)):
    perf.contact(a_, b_, floor=top)
air = [(a_, b_) for a_, b_ in TRAVEL] + [(int(land3.start), int(land3.start) + LAND_SETTLE),
                                          (int(cling_l.start), int(fly8.start) + 2),
                                          (int(land8.start), int(land8.start) + LAND_SETTLE)]
lock_err = perf.ground_lock(int(land3.start), int(flop.end), skip=air, step=1)   # every frame: no lerp across cuts
END = int(flop.start) + 92
sc.frame_end = END
hips = lambda f: perf.bone_world(HIPS, int(f))

# ------------------------------------------------------------------ webs
webs = fx.WebShots(rig, fx.collection("Webs"))
webs.shot("Web_S1", R_HAND, lambda f: A1, a1 - 3, a1, b1 - 4)
W2 = int(perf.clip_frame(web2, hit_pk))
webs.shot("Web_Zip2", R_HAND, lambda f: A2, W2 - 4, W2, f2h - 8)
webs.shot("Web_Hang2", FOOT, lambda f: A2, f2h - 8, f2h - 8, int(fly3.start) + 2)
webs.shot("Web_S3", R_HAND, lambda f: A3, f3a - 2, f3a + 2, int(perf.clip_frame(fly3, 30)))
webs.shot("Web_S5", R_HAND, lambda f: A5, f5a - 2, f5a + 2, f5h - 6)
webs.shot("Web_Sub", FOOT, lambda f: Vector((SUB_HIPS.x, SUB_HIPS.y, 14.0)), f5h - 6, f5h - 6, int(fly6.start) + 2)
webs.shot("Web_S6", R_HAND, lambda f: A6, f6a, f6a + 4, int(perf.clip_frame(fly6, 30)))
webs.shot("Web_S7", R_HAND, lambda f: A7, f7a - 2, f7a + 2, int(perf.clip_frame(fly7, 28)))
webs.shot("Web_S8", R_HAND, lambda f: A8, int(fly8.start) - 2, int(fly8.start) + 2, int(perf.clip_frame(fly8, 30)))

# ------------------------------------------------------------------ S3 ticker: a light streak racing along it, his head chasing it
glint = box("TickerGlint", (0.35, 0.05, 0.9), TK_C, fx.material("Glint", (1.0, 0.85, 0.45), emit=12.0))
left, right = TK_C.x + TK_W / 2 - 0.4, TK_C.x - TK_W / 2 + 0.4
gy = TK_C.y + TICK.normal.y * 0.42
f = int(tick.start) + 4
keys_g = []
for d_ in (34, 26, 19, 14, 10, 8, 7, 6, 6, 6):
    keys_g += [(f, Vector((left, gy, TK_C.z)), "const"), (f + d_, Vector((right, gy, TK_C.z)), "lin")]
    f += d_ + 1
anim.keys(glint, "location", keys_g)
anim.visible(glint, [(1, False), (int(tick.start), True), (int(tick.end), False)])
for o in [ticker] + list(ticker.children):           # the ticker only exists for its scene (not behind the finale)
    anim.visible(o, [(1, False), (f3a - 2, True), (int(run4.end) + 2, False)])
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
# billboard catwalk under the big screen (what he lands, perches and moonwalks on); runs past both screen edges
CW_X0, CW_X1 = SCR_C.x - SCR_W / 2 - 2.2, SCR_C.x + SCR_W / 2 + 8.0     # starts at x 18.2: never in the ticker shot
CW_Y0, CW_Y1 = SCREEN.point.y - SCR_OFF - 1.2, SCREEN.point.y
grate = fx.material("Catwalk", (0.12, 0.13, 0.14), rough=0.5, metallic=0.7)
box("Catwalk", (CW_X1 - CW_X0, CW_Y1 - CW_Y0, 0.14), ((CW_X0 + CW_X1) / 2, (CW_Y0 + CW_Y1) / 2, TS_Z - 0.07), grate)
box("CatwalkKick", (CW_X1 - CW_X0, 0.04, 0.12), ((CW_X0 + CW_X1) / 2, CW_Y0 + 0.02, TS_Z + 0.06), grate)
for k in range(5):                                                      # brackets back to the facade
    bx = CW_X0 + 1.0 + k * (CW_X1 - CW_X0 - 2.0) / 4
    box(f"CatwalkBracket{k}", (0.08, CW_Y1 - CW_Y0, 0.08), (bx, (CW_Y0 + CW_Y1) / 2, TS_Z - 0.5), grate)
lv = city.sign("TSquareLeave", seq0("st_leaving"), SCR_C + SCR_N * 0.06, SCR_N, SCR_W, emit=1.3, offset=SCR_OFF,
               seq=(96, LEAVE_AT))
anim.visible(lv, [(1, False), (LEAVE_AT, True)])

# ------------------------------------------------------------------ S7 rooftop screen (two slides)
rs1 = city.sign("RoofScreen1", img("roof_competitive"), RS_C, Vector((-1, 0, 0)), 6.2, emit=1.2, frame="led")
rs2 = city.sign("RoofScreen2", img("roof_layer"), RS_C + Vector((-0.01, 0, 0)), Vector((-1, 0, 0)), 6.2, emit=1.2)
anim.visible(rs2, [(1, False), (T["vo8"] - 4, True)])
for k, dy in enumerate((-2.2, 2.2)):
    box(f"RoofLeg{k}", (0.15, 0.15, 3.2 - 1.74), (RS_C.x + 0.15, RS_C.y + dy, ROOF_Z + (3.2 - 1.74) / 2), steel)

# ------------------------------------------------------------------ S8/S9 the tower in the intersection: webbed down block by block
arrive = hips(builds[0].start)
SCALE = 1.45                                         # street scale (piece 2's stage blocks were 2 m wide)
TX, TY = arrive.x + 3.3, arrive.y + 0.8
BLOCKS = [("INSPECTION", 2.2, 1.0, 0.72, (0.15, 0.39, 0.92)), ("ENGINEERS' CONFIDENCE", 2.0, 0.95, 0.66, (0.12, 0.16, 0.23)),
          ("CUSTOMER CONFIDENCE", 1.8, 0.9, 0.66, (0.12, 0.16, 0.23)), ("COMPETITIVE PRODUCT", 1.6, 0.85, 0.66, (0.12, 0.16, 0.23))]
BLOCKS = [(n, w * SCALE, d * SCALE, h * SCALE, col) for n, w, d, h, col in BLOCKS]
tcoll = fx.collection("Tower")
TOWER_H = sum(b[3] for b in BLOCKS)


def block(i, w, d, h, col):
    root = fx.empty(f"Block{i}", coll=tcoll, size=0.2)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w, d, h), verts=bm.verts)
    me = bpy.data.meshes.new(f"Block{i}_Mesh")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(f"Block{i}_Body", me)
    tcoll.objects.link(ob)
    ob.parent = root
    ob.data.materials.append(fx.material(f"Block{i}_Mat", col, rough=0.45))
    bev = ob.modifiers.new("Bevel", "BEVEL")
    bev.width, bev.segments = 0.04, 3
    lm = bpy.data.meshes.new(f"Block{i}_Label")                        # label on the front face
    lw, lh = w * 0.94, h * 0.8
    lm.from_pydata([(-lw / 2, -d / 2 - 0.004, -lh / 2), (lw / 2, -d / 2 - 0.004, -lh / 2), (lw / 2, -d / 2 - 0.004, lh / 2),
                    (-lw / 2, -d / 2 - 0.004, lh / 2)], [], [(0, 1, 2, 3)])
    uv = lm.uv_layers.new()
    for li, loop in enumerate(lm.loops):
        uv.data[li].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][loop.vertex_index]
    lo = bpy.data.objects.new(f"Block{i}_LabelObj", lm)
    tcoll.objects.link(lo)
    lo.parent = root
    lm.materials.append(city.image_material(f"Block{i}_LabelMat", os.path.join(SCR, f"tower_{i}.png"), emit=0.6))
    top = fx.empty(f"Block{i}_Top", (0, 0, h / 2), tcoll, 0.08)
    top.parent = root
    return root, top


DROP_H = 9.0
stack_z, roots = 0.0, []
for i, ((label, w, d, h, col), b) in enumerate(zip(BLOCKS, builds)):
    root, top = block(i, w, d, h, col)
    zc = stack_z + h / 2
    stack_z += h
    hit = int(perf.clip_frame(b, up_pk))
    land_f = hit + 12
    rest = Vector((TX + (0.05 if i % 2 else -0.04), TY, zc))
    anim.visible(root, [(1, False), (hit - 6, True)])
    for ch in root.children:
        anim.visible(ch, [(1, False), (hit - 6, True)])
    anim.keys(root, "location", [(1, rest + Vector((0, 0, DROP_H)), "const"), (hit, rest + Vector((0, 0, DROP_H)), "in"),
                                 (land_f, rest, "out"), (land_f + 3, rest + Vector((0, 0, 0.06)), "in"), (land_f + 6, rest)])
    webs.shot(f"Web_BlockL{i}", L_HAND, (lambda t: (lambda f: t.matrix_world.translation))(top), hit - 4, hit, land_f)
    webs.shot(f"Web_BlockR{i}", R_HAND, (lambda t: (lambda f: t.matrix_world.translation))(top), hit - 4, hit, land_f)
    shot.sfx("web_thwip", hit - 3)
    shot.sfx("block_thud", land_f)
    roots.append((root, rest, land_f))
# cash stacks on the top block ("and the money coming in")
top_root, top_rest, top_land = roots[-1]
cash_mat = fx.material("CashSide", (0.29, 0.6, 0.38), rough=0.6)
cash = []
for k, (cx, cy) in enumerate([(-0.65, -0.2), (-0.22, 0.15), (0.22, -0.17), (0.65, 0.17), (0.0, 0.0)]):
    ob = box(f"Cash{k}", (0.55, 0.26, 0.2 + 0.07 * (k % 2)), (0, 0, 0), cash_mat, tcoll)
    rest = top_rest + Vector((cx, cy, BLOCKS[-1][3] / 2 + 0.11))
    anim.visible(ob, [(1, False), (cash_f - 4, True)])
    anim.keys(ob, "location", [(1, rest + Vector((0, 0, 4.0)), "const"), (cash_f + k * 2, rest + Vector((0, 0, 4.0)), "in"),
                               (cash_f + k * 2 + 9, rest, "back"), (cash_f + k * 2 + 13, rest)])
    cash.append((ob, rest))
shot.sfx("cash_flutter", cash_f)
# the yank: both lines on INSPECTION, taut while he leans back, then he rips it out; everything above comes down
ins = roots[0][0]
webs.shot("Web_YankL", L_HAND, lambda f: ins.matrix_world.translation + Vector((-0.5, -0.3, 0.2)), Y1 - 34, Y1 - 30, Y1 + 8)
webs.shot("Web_YankR", R_HAND, lambda f: ins.matrix_world.translation + Vector((-0.5, 0.3, 0.2)), Y1 - 34, Y1 - 30, Y1 + 8)
shot.sfx("web_thwip", Y1 - 33)
shot.sfx("tower_crash", C + 4)
rr = random.Random(9)
fallen = [Vector((max(TX - 1.6, arrive.x + 1.9), TY - 1.4, BLOCKS[0][3] / 2)), Vector((TX + 0.5, TY + 0.1, BLOCKS[1][3] / 2)),
          Vector((TX + 3.0, TY + 0.8, BLOCKS[2][3] / 2)), Vector((TX + 2.2, TY - 1.6, BLOCKS[3][3] / 2))]
for i, ((root, rest, _), end) in enumerate(zip(roots, fallen)):
    s0 = Y1 + 2 if i == 0 else C + (i - 1) * 3          # base yanked out; upper blocks hang a beat, then fall
    mid = (rest + end) / 2 + Vector((0, 0, 0.5 + 0.2 * i))
    anim.keys(root, "location", [(s0, rest, "in" if i else "expo_out"), (s0 + 7 + i, mid, "in"), (s0 + 14 + 2 * i, end, "back"),
                                 (s0 + 20 + 2 * i, end)])
    spin = Vector((rr.uniform(-0.6, 0.6), rr.uniform(-1.2, 1.2), rr.uniform(-0.8, 0.8))) if i else Vector((0, 0, 0.35))
    anim.keys(root, "rotation_euler", [(s0, Vector((0, 0, 0)), "in"), (s0 + 7 + i, spin * 1.8, "out"),
                                       (s0 + 14 + 2 * i, Vector((0, 0, spin.z)), "bez")])
for k, (ob, rest) in enumerate(cash):
    end = Vector((TX + rr.uniform(-2.2, 2.2), TY + rr.uniform(-1.6, 0.4), 0.1))
    anim.keys(ob, "location", [(C + 4, rest, "out"), (C + 12 + k, rest + Vector((rr.uniform(-1.0, 1.0), -0.4, 1.2)), "in"),
                               (C + 24 + k, end, "bez")])
    anim.keys(ob, "rotation_euler", [(C + 4, Vector((0, 0, 0))), (C + 24 + k, Vector((0, 0, rr.uniform(-2, 2))))])
fl = hips(flop.start + 30)
fx.paper_pour("Bills", os.path.join(SCR, "cash_bill.png"), lambda i: top_rest + Vector((rr.uniform(-0.8, 0.8), 0, 0.4)),
              (TX - 0.5, TY - 0.6), count=110, start=C + 6, dur=45, spread=(3.6, 1.8), size=(0.3, 0.13), arc=(1.4, 3.0))
fx.paper_pour("BillsOnHim", os.path.join(SCR, "cash_bill.png"), lambda i: top_rest + Vector((rr.uniform(-0.6, 0.6), 0, 0.4)),
              (fl.x, fl.y), count=30, start=int(flop.start) + 4, dur=40, spread=(1.0, 0.7), size=(0.3, 0.13), arc=(1.2, 2.6))
# the last bill lands on his mask
head_f = int(flop.start) + 50
hd = perf.bone_world("mixamorig:Head", head_f)
bill = city.sign("BillOnMask", os.path.join(SCR, "cash_bill.png"), hd + Vector((0, 0, 0.16)), Vector((0, 0, 1)), 0.34,
                 aspect=0.3 / 0.13, offset=0.0, coll=tcoll)
anim.keys(bill, "location", [(head_f - 30, hd + Vector((0.4, -0.3, 2.4)), "lin"), (head_f - 15, hd + Vector((-0.3, 0.2, 1.2)), "lin"),
                             (head_f, hd + Vector((0, 0, 0.16)), "out")])
anim.keys(bill, "rotation_euler", [(head_f - 30, Vector((0.6, 0.3, 0.2))), (head_f - 15, Vector((-0.5, 0.2, 1.2))), (head_f, bill.rotation_euler.copy())])
anim.visible(bill, [(1, False), (head_f - 30, True)])

webs.bake(range(1, END + 1))
for o in fx.collection("Webs").objects:
    if o.type == "MESH":
        o.data.materials[0] = fx.material("Web_Line", (0.95, 0.97, 1.0), rough=0.35, emit=0.9)

# ------------------------------------------------------------------ SFX: every web, jump and landing
for fa in (a1, f2a, f3a, f5a, f6a, f7a, f8a):
    shot.sfx("cartwheel_whoosh", fa + 4)
for fl_ in (int(perf.clip_frame(sw1, 40)) - 6, int(land3.start) + 4, int(cling_l.start) + 2, int(land6.start) + 4,
            int(land7.start) + 4, int(land8.start) + 4):
    shot.sfx("landing_thud", fl_)
for fw in (W2 - 3, f3a - 2, f5a - 2, f6a, f7a - 2, int(fly8.start) - 2, f2h - 8, f5h - 6):
    shot.sfx("web_thwip", fw)
shot.sfx("bugs_skitter", bugs_at)
for f in tiles:
    shot.sfx("ui_pop", f)

# ------------------------------------------------------------------ cameras
cam = fx.CameraRig(lens=28, fstop=4.0)


def at(f, loc, tgt, ease="inout", cut=False):
    cam.at(int(f), loc, tgt, ease, cut=cut)


def clear_cam(cands, pts):
    for cnd in cands:
        if clear_view(cnd[0], pts):
            return cnd
    return cands[0]


def arm(base, offset, pad=0.8):
    """Camera on a collision arm: from the subject out along `offset`, stopped short of any facade."""
    off = Vector(offset)
    h = c.ray(base, off, off.length + pad)
    if h is not None and h.obj.name not in MINE:
        return base + off.normalized() * max(1.2, (h.point - base).length - pad)
    return base + off


def ride(f0, f1, offset, lead=6, step=2, smooth=5, look=Vector()):
    """Tracking shot: camera at the (smoothed) hips + offset (collision arm), aimed a little ahead along his path."""
    pts = {f: hp(f) for f in range(int(f0) - smooth - 5, int(f1) + lead + smooth + 6)}
    sm = lambda f: sum((pts[k] for k in range(f - smooth, f + smooth + 1)), Vector()) / (2 * smooth + 1)
    raw = {f: arm(sm(f), offset) for f in range(int(f0) - 4, int(f1) + 5)}
    cams = {f: sum((raw[k] for k in range(f - 4, f + 5)), Vector()) / 9 for f in range(int(f0), int(f1) + 1)}
    for f in range(int(f0), int(f1) + 1, step):
        cam.at(f, cams[f], sm(f + lead) + look, "lin", cut=(f == int(f0)))


def pan(f0, f1, loc, lead=4, smooth=4, step=2, look=Vector()):
    """Fixed camera panning with him (robust for short moves across a street)."""
    pts = {f: hp(f) for f in range(int(f0) - smooth, int(f1) + lead + smooth + 1)}
    sm = lambda f: sum((pts[k] for k in range(f - smooth, f + smooth + 1)), Vector()) / (2 * smooth + 1)
    for f in range(int(f0), int(f1) + 1, step):
        cam.at(f, Vector(loc), sm(f + lead) + look, "lin", cut=(f == int(f0)))


def head(f, up=0.05):
    return perf.bone_world("mixamorig:Head", f) + Vector((0, 0, up))


cam.cam.data.clip_end = 800.0
CUTS = []                                            # every camera cut, for the cut log (location vs angle)
# S0 establishing aerial, ride the swing
cam.lens(1, 18, "const")
at(1, (6.0, 46.0, 44.0), (-2.0, -4.0, 4.0), "lin", cut=True)
at(a1 - 1, (5.0, 40.0, 34.0), (-2.0, 4.0, 8.0), "lin")
ride(a1, b1, Vector((7.0, 8.5, 5.0)), lead=8)
# S1 wide from the street, raised so he reads on the board top (f65), the text right below him
cam.lens(b1 + 1, 24, "const")
b_pts = board_pts(G_C + WALL_G.normal * 0.45, WALL_G.normal, GB_W, GB_H)
s1 = clear_cam([((G_C.x + dx, WALL_G.point.y + 8.8, 5.4), (G_C.x - 1.1, WALL_G.point.y, 5.75)) for dx in (-0.9, 0.3, -1.9, 1.3, -2.9)],
               b_pts)
at(b1 + 1, *s1, "lin", cut=True)
s1_end = Vector(s1[0]).lerp(Vector((TOP1[0], TOP1[1], LEDGE_TOP + 1.0)), 0.1)          # slow drift in (the whole board stays in frame)
at(int(happy.start) + 5, s1_end, Vector(s1[1]).lerp(Vector((TOP1[0], TOP1[1], LEDGE_TOP + 0.4)), 0.05), "inout")
# CU excited: his face big, the gesture
cu1 = int(happy.start) + 6
hc = head(cu1 + 20)
cam.lens(cu1, 35, "const")
at(cu1, hc + Vector((0.5, 2.3, -0.2)), hc + Vector((0, 0, -0.15)), "lin", cut=True)
at(int(curious.start) + 5, hc + Vector((0.35, 2.0, -0.2)), hc + Vector((0, 0, -0.15)), "lin")
CUTS.append(("CU excited", cu1))
# OTS curious: from just behind his shoulder on the near building, the billboard readable across the street
ots = int(curious.start) + 6
hc = head(ots + 20, up=0.0)
cam.lens(ots, 24, "const")
ots_loc = Vector((hc.x + 0.5, max(hc.y - 0.62, WALL_G.point.y + 0.12), hc.z + 0.1))
ots_tgt = Vector((BB_C.x + 0.5, BB_C.y, ots_loc.z + 18.0 * math.tan(math.radians(9.0))))
at(ots, ots_loc, ots_tgt, "lin", cut=True)
at(f2a - 1, ots_loc + Vector((0.05, 0.1, 0.05)), ots_tgt, "lin")
CUTS.append(("OTS billboard", ots))
# S2 swing across: side-tracking, then frontal on the billboard as he lands the flip into the hang
cam.lens(f2a, 24, "const")
ride(f2a, f2h - 6, Vector((9.0, -2.0, 1.2)), lead=8)
cam.lens(f2h - 5, 24, "const")
cam.lens(f2h - 5, 20, "const")
s2_cam = ((BB_C.x + 0.6, BB_C.y - 6.8, BB_C.z - 2.0), (BB_C.x + 0.6, BB_C.y, BB_C.z - 1.25))   # billboard + him both big
at(f2h - 5, *s2_cam, "lin", cut=True)
at(f3a + 2, (s2_cam[0][0] - 0.3, s2_cam[0][1] + 0.5, s2_cam[0][2]), s2_cam[1], "lin")
# S3 the long swing to the ticker: tracking from the street, then the ticker shot as he lands
cam.lens(f3a + 3, 22, "const")
ride(f3a + 3, f3b - 1, Vector((0.0, -11.0, 1.5)), lead=10)
cam.lens(f3b, 22, "const")
tk_pts = board_pts(TK_C + TICK.normal * 0.35, TICK.normal, TK_W, 1.0)
s3 = clear_cam([((TK_C.x + dx, TICK.point.y - 7.4, 1.9), (TK_C.x + 1.0, TICK.point.y, 3.0)) for dx in (1.0, 0.0, 2.0, -1.0, 3.0)],
               tk_pts)
at(f3b, *s3, "lin", cut=True)
cu3 = int(tick.end) - 46                             # CU amazed: the streak is racing now, his head whipping after it
at(cu3 - 1, s3[0], s3[1], "lin")
hc = head(cu3 + 10)
cam.lens(cu3, 30, "const")
at(cu3, hc + Vector((0.55, 1.15, 0.45)), hc + Vector((-0.1, -0.2, 0.0)), "lin", cut=True)   # in front + above: his upturned face
at(int(run4.start) + 1, hc + Vector((0.5, 1.1, 0.42)), hc + Vector((-0.1, -0.2, 0.0)), "lin")
anim.keys(look_t, "influence", [(cu3 - 6, 0.95, "inout"), (cu3, 0.4, "inout"), (int(tick.end) - 4, 0.4, "lin")])   # gaze up, not sideways
CUTS.append(("CU amazed", cu3))
# S4 the sprint across the street (side-tracking), the bus stop, the leap onto the shelter
cam.lens(int(run4.start) + 2, 24, "const")
ride(int(run4.start) + 2, int(first(look4).start) - 1, Vector((-7.5, -1.5, 0.4)), lead=6)
cam.lens(int(first(look4).start), 28, "const")
at(int(first(look4).start), *BUS_CAM, "lin", cut=True)
at(int(hop_a.start) - 1, BUS_CAM[0], BUS_CAM[1], "lin")
roof_cam = ((ROOF_SPOT[0] - 5.6, ROOF_SPOT[1] + 3.4, 3.8), (ROOF_SPOT[0] - 0.4, ROOF_SPOT[1], 2.2))
at(int(hop_a.start), *roof_cam, "lin", cut=True)
at(f5a - 1, (roof_cam[0][0] + 0.4, roof_cam[0][1] - 0.2, 3.9), (ROOF_SPOT[0], ROOF_SPOT[1], 2.4), "lin")
# S5 the hop over to the subway (wide), push into the close two-shot: board + him both big (f769)
cam.lens(f5a, 26, "const")
pan(f5a, f5h + 4, (SUB_HIPS.x - 2.6, POST.point.y + 7.2, 5.0), look=Vector((0, 0, -0.2)))
cam.lens(f5h + 5, 24, "const")
at(f5h + 5, *SUB_CAM, "lin", cut=True)
at(f6a - 1, (SUB_CAM[0][0] - 0.2, SUB_CAM[0][1] - 0.3, SUB_CAM[0][2]), SUB_CAM[1], "lin")
# S6 swing across the street up to the catwalk (tracking), then straight on the screen; hold through the moonwalk
cam.lens(f6a, 22, "const")
pan(f6a, f6b - 1, (14.5, 0.5, 4.5), lead=6)
cam.lens(f6b, 24, "const")
scr_pts = board_pts(SCR_C + SCR_N * SCR_OFF, SCR_N, SCR_W, SCR_W * 9 / 16)
cam.lens(f6b, 35, "const")
ts = clear_cam([((SCR_C.x + dx, SCREEN.point.y - 11.6, SCR_C.z - 0.6), (SCR_C.x + dx * 0.5, SCREEN.point.y, SCR_C.z - 0.55))
                for dx in (0, 0.6, -0.6, 1.2, -1.2)], scr_pts)
at(f6b, *ts, "lin", cut=True)
at(f7a - 1, ts[0], ts[1], "lin")
# S7 the zip up to the rooftop: a wide chase from behind and below
cam.lens(f7a, 20, "const")
ride(f7a, f7b - 1, Vector((7.0, 7.0, -3.0)), lead=10)
cam.lens(f7b, 24, "const")
rf = Vector(RF_SPOT)
roof_cam7 = ((rf.x - 5.4, rf.y - 2.2, ROOF_Z + 2.0), (RS_C.x - 1.6, RS_C.y + 0.2, ROOF_Z + 1.7))
at(f7b, *roof_cam7, "lin", cut=True)
at(T["vo8"] - 1, (roof_cam7[0][0] + 0.4, roof_cam7[0][1], ROOF_Z + 1.2), roof_cam7[1], "inout")
cu7 = T["vo8"] + 2                                   # CU confident: low, close, the screen behind him
hc = head(cu7 + 20)
cam.lens(cu7, 30, "const")
at(cu7, hc + Vector((-1.7, -1.0, -0.55)), hc + Vector((0.6, 0.3, 0.15)), "lin", cut=True)
at(f8a - 1, hc + Vector((-1.5, -0.9, -0.5)), hc + Vector((0.6, 0.3, 0.15)), "lin")
CUTS.append(("CU confident", cu7))
# S8 the swing down into the intersection (tracking), a low hero angle on the landing
cam.lens(f8a, 20, "const")
ride(f8a, f8b - 1, Vector((-7.0, -5.0, 4.0)), lead=10)
fs = hp(f8b + 20)
cam.lens(f8b, 22, "const")
at(f8b, (fs.x - 2.2, fs.y + 3.8, 0.6), (fs.x, fs.y, 1.2), "lin", cut=True)
# the tower: wide from down the avenue (him + tower + cash in frame), slow push in
mid_x = (arrive.x + TX) / 2
tw = ((mid_x, TY - 7.0, 2.0), (mid_x, TY, (TOWER_H + 0.6) * 0.5))
cam.lens(int(rise8.end) - 6, 24, "const")
w0, w1, wf0, wf1 = Vector(tw[0]), Vector((tw[0][0] + 0.2, tw[0][1] + 2.2, 2.1)), int(rise8.end) - 6, Y1 - 30
wide = lambda f: w0.lerp(w1, swing.ease_pendulum((f - wf0) / (wf1 - wf0)))
at(wf0, w0, tw[1], "lin", cut=True)
low_cam = (Vector((arrive.x - 1.3, arrive.y - 3.0, 0.45)), Vector((TX - 0.3, TY, 3.6)))    # low hero angle up at the block
for i in (1, 3):                                      # two blocks seen coming down from below, back to the wide to land
    _root, _rest, lf = roots[i]
    hit_i = lf - 12
    at(hit_i - 15, wide(hit_i - 15), tw[1], "lin")
    cam.lens(hit_i - 14, 20, "const")
    at(hit_i - 14, *low_cam, "lin", cut=True)
    at(lf - 4, low_cam[0] + Vector((0.15, 0.3, 0.05)), low_cam[1], "lin")
    cam.lens(lf - 3, 24, "const")
    at(lf - 3, wide(lf - 3), tw[1], "lin", cut=True)
    anim.key(cam.cam.data.dof, "aperture_fstop", hit_i - 14, 4.0, ease="const")
    anim.key(cam.cam.data.dof, "aperture_fstop", lf - 3, 5.6, ease="const")
    CUTS.append((f"low block {i}", hit_i - 14))
at(wf1, w1, tw[1], "inout")
# the yank: his face close, both lines taut (push in = pressure)
cuy = Y1 - 26
hc = head(Y1 - 10)
cam.lens(cuy, 40, "const")
at(cuy, hc + Vector((1.4, -2.0, -0.1)), hc + Vector((0.2, 0, -0.1)), "lin", cut=True)
at(Y1 + 3, hc + Vector((1.2, -1.6, -0.1)), hc + Vector((0.2, 0, -0.1)), "lin")
CUTS.append(("CU yank", cuy))
# the collapse: wide again (pull out = release)
cam.lens(Y1 + 4, 22, "const")
at(Y1 + 4, (tw[0][0] - 0.3, tw[0][1] + 1.0, 2.6), (tw[1][0] + 0.4, tw[1][1], 1.8), "lin", cut=True)
at(head_f - 35, (tw[0][0] - 0.6, tw[0][1] - 0.5, 3.2), (tw[1][0] + 0.2, tw[1][1] - 0.5, 1.2), "lin")
# end: top-down on him, the bill lands on his mask, then a helicopter pull-out over the wreck
cam.lens(head_f - 34, 35, "const")
at(head_f - 34, (fl.x + 0.3, fl.y - 0.6, 2.3), (fl.x, fl.y, 0.2), "lin", cut=True)
at(head_f + 22, (fl.x + 0.3, fl.y - 0.5, 1.9), (fl.x, fl.y, 0.2), "lin")
cam.lens(head_f + 23, 20, "const")
at(head_f + 23, (fl.x - 3.0, fl.y - 6.0, 9.0), (fl.x + 2.0, fl.y + 6.0, 0.0), "lin", cut=True)
at(END, (fl.x - 6.0, fl.y - 16.0, 30.0), (fl.x + 2.0, fl.y + 8.0, 0.0), "in")
# impacts: the camera feels every landing, block and the collapse
for f_, a_ in ((int(perf.clip_frame(sw1, 40)), 0.05), (int(land3.start) + 4, 0.05), (int(cling_l.start) + 2, 0.04),
               (int(land6.start) + 4, 0.05), (int(land7.start) + 4, 0.05), (int(land8.start) + 4, 0.07), (Y1 + 1, 0.06)):
    cam.shake(f_, amp=a_, dur=8)
for _r, _rest, lf in roots:
    cam.shake(lf, amp=0.03, dur=6)
cam.shake(C + 2, amp=0.1, dur=16)
# depth of field per shot (focus = the camera's aim point): deep on wides and chases, shallow on close-ups
FSTOPS = [(1, 5.6), (b1 + 1, 4.0), (cu1, 1.8), (ots, 2.0), (f2a, 5.6), (f2h - 5, 4.0), (f3a + 3, 5.6), (f3b, 4.0), (cu3, 2.0),
          (int(run4.start) + 2, 4.0), (int(hop_a.start), 4.0), (f5a, 4.0), (f5h + 5, 2.8), (f6a, 5.6), (f6b, 5.6), (f7a, 5.6),
          (f7b, 4.0), (cu7, 2.4), (f8a, 5.6), (f8b, 2.8), (int(rise8.end) - 6, 5.6), (cuy, 1.8), (Y1 + 4, 5.6), (head_f - 34, 2.8),
          (head_f + 23, 8.0)]
for f_, v_ in FSTOPS:
    anim.key(cam.cam.data.dof, "aperture_fstop", int(f_), v_, ease="const")
office.face_camera(cam.cam, [(c_.start + 4, c_.end - 2) for c_ in [look4, happy]] + [(cu7, int(conf7.end) - 2)] +
                   [(f2h + 4, f3a - 4), (f5h + 4, f6a - 4)], amount=0.45)          # hangs: head lifts towards the lens
fx.char_lights(rig, cam.cam, key=170.0, rim=340.0)
office.present_to(T["vo1"] + 4, (G_C.x - 1.0, G_C.y + 0.4, G_C.z), hips(T["vo1"]).x)
# hangs: both hands together in front of the chest, holding on (not dangling)
for h0, h1, fwd in ((f2h + 2, f3a - 2, Vector((0, -1, 0))), (f5h + 2, f6a - 2, Vector((0, 1, 0)))):
    ch = perf.bone_world("mixamorig:Spine2", h0 + 8)
    for sd, dx in (("L", 0.07), ("R", -0.07)):
        office.present(h0, ch + fwd * 0.3 + Vector((dx, 0, 0.05)), side=sd, hold=max(4, h1 - h0 - 12), ramp=6, amount=0.85)
# the lenses act: wide when excited / amazed / shocked, a squint to study or look cool, angled when
# determined or worried, and a blink every few seconds
from pipeline import face
eyes = face.Lenses(bpy.data.objects["MilesMasked"])
for f_, w_ in ((int(happy.start) + 4, dict(Wide=0.75)), (int(curious.start) + 8, dict(Wide=0.0, Squint=0.35)),
               (f2a, dict(Squint=0.0)), (cu3 - 4, dict(Wide=1.0)), (int(run4.start) + 6, dict(Wide=0.2)),
               (int(shock.start) + 3, dict(Wide=1.0)), (int(cling.start) + 6, dict(Wide=0.7, Sad=0.35)),
               (f5a, dict(Wide=0.0, Sad=0.0)), (int(frus.start) + 8, dict(Sad=0.9)), (f6a, dict(Sad=0.0)),
               (int(worry.start) + 10, dict(Sad=0.8)), (int(moon.start) + 4, dict(Sad=0.0, Squint=0.35)),
               (f7a, dict(Squint=0.0)), (cu7, dict(Squint=0.45, Angry=0.3)), (f8a, dict(Squint=0.0, Angry=0.0)),
               (int(rise8.end), dict(Angry=0.45)), (Y1 - 30, dict(Angry=1.0, Squint=0.3)), (C, dict(Angry=0.0, Squint=0.0, Wide=1.0)),
               (int(flop.start) + 12, dict(Wide=0.0, Squint=0.85))):
    eyes.set(f_, **w_)
eyes.blinks(1, int(flop.start), every=95, skip=[(Y1 - 34, C + 10)])


# ------------------------------------------------------------------ city life: traffic, pedestrians, pigeons
# Everything is checked against a per-frame cache of the camera and Spidey (life.Guard): nothing pops in or out
# on screen, nothing drives or walks through him or the lens, nothing steps between the lens and him.
from pipeline import life
guard = life.Guard(cam.cam, lambda f: rig.matrix_world @ rig.pose.bones[HIPS].head, (1, END), step=2)
guard.keepout.append((int(fly8.start), END, Vector((TX, TY, 0)), 7.0))          # the tower, its wreck and the bills
rl = random.Random(21)
cars = life.CarKit()
ROAD_END, LANE, CURB_LANE, Z_ROAD = 47.0, 2.0, 4.25, -0.08
# parked cars along both curbs of both streets (not in the intersection, not where he runs or lands)
parked = 0
for axis in ("x", "y"):
    for side in (-1, 1):
        u = -ROAD_END + rl.uniform(0, 4)
        while u < ROAD_END:
            if abs(u) > 12.5 and rl.random() < 0.72:
                p_ = Vector((u, side * CURB_LANE, 0.4)) if axis == "x" else Vector((side * CURB_LANE, u, 0.4))
                if all(guard.ok(f, p_, r_sub=2.6, r_cam=2.6, r_line=1.0) for f in guard.cam):
                    car = cars.spawn(rl.randrange(10), f"Parked{parked}")
                    hd = Vector((side, 0, 0)) if axis == "y" else Vector((0, 0, 0))
                    heading = Vector((1, 0, 0)) * -side if axis == "x" else Vector((0, 1, 0)) * side
                    car.place(Vector((p_.x, p_.y, Z_ROAD)), heading)
                    parked += 1
            u += rl.uniform(5.6, 7.5)
# moving traffic: right-hand lanes, one signal cycle so cross traffic never meets in the intersection
SIG = 240                                            # frames per green (avenue first)
green = lambda f, axis: (int(f // SIG) % 2 == 0) == (axis == "y")
FIN_BLOCK = int(fly8.start) - 40                     # from here the intersection is his (and then the tower's)
LANES = [("y", Vector((LANE, -ROAD_END, 0)), Vector((0, 1, 0))), ("y", Vector((-LANE, ROAD_END, 0)), Vector((0, -1, 0))),
         ("x", Vector((-ROAD_END, -LANE, 0)), Vector((1, 0, 0))), ("x", Vector((ROAD_END, LANE, 0)), Vector((-1, 0, 0)))]
moving, last_in_lane = 0, {}
for li, (axis, p0, h) in enumerate(LANES):
    speed = rl.uniform(0.30, 0.38)                   # m / frame (9–11 m/s), one speed per lane: no overtaking
    f = -int(2 * ROAD_END / speed) + rl.randint(0, 60)
    while f < END:
        n = int(2 * ROAD_END / speed)
        t_in = f + int((ROAD_END - 7.0) / speed)       # enters / leaves the intersection box
        t_out = f + int((ROAD_END + 7.0) / speed)
        okay = green(t_in, axis) and green(t_out, axis) and t_out < FIN_BLOCK
        if okay:
            track = [(k, p0 + h * (speed * (k - f)) + Vector((0, 0, 0.7))) for k in range(max(1, f), min(END, f + n) + 1, 4)]
            okay = bool(track) and guard.clear(track, r_sub=3.0, r_cam=3.0, r_line=1.2) if f + n > 1 else False
        if okay:
            car = cars.spawn(rl.randrange(10), f"Drive{moving}")
            car.drive(p0, h, [(f, 0.0, "lin"), (f + n, speed * n, "lin")], z=Z_ROAD)
            car.show([(1, False), (max(1, f), True), (f + n + 1, False)])
            moving += 1
            f += rl.randint(45, 110)
        else:
            f += 17
# the finale: traffic stops at the stop lines and queues while he builds (and wrecks) the tower
queued = 0
for li, (axis, p0, h) in enumerate(LANES):
    for q in range(3):
        stop = ROAD_END - 11.0 - q * 6.2
        arrive = FIN_BLOCK + 20 + q * 26 + li * 9
        track = [(k, p0 + h * stop + Vector((0, 0, 0.7))) for k in range(arrive, END + 1, 6)]
        if not all(guard.ok(fk, pk, r_sub=3.0, r_cam=3.0, r_line=1.2) for fk, pk in track):
            continue
        car = cars.spawn(rl.randrange(10), f"Queue{queued}")
        car.drive(p0, h, [(arrive - 70, stop - 0.32 * 50, "lin"), (arrive - 20, stop - 0.32 * 10, "out"), (arrive, stop, "const")],
                  z=Z_ROAD)
        car.show([(1, False), (arrive - 70, True)])
        queued += 1
# pedestrians: keep right on all four sidewalks, at their own stride speed, never through him, the lens or a sign
walk = life.WalkKit()
WALKS = [("x", -7.15, (-ROAD_END, -9.5)), ("x", -7.15, (9.5, ROAD_END)), ("x", 6.95, (-ROAD_END, -9.5)), ("x", 6.95, (9.5, ROAD_END)),
         ("y", -7.3, (-ROAD_END, -10.0)), ("y", -7.3, (10.0, ROAD_END)), ("y", 7.3, (-ROAD_END, -10.0)), ("y", 7.3, (10.0, ROAD_END))]


def sidewalk_clear(a, b):
    for z_ in (0.35, 1.1):
        pa, pb = Vector((a.x, a.y, z_)), Vector((b.x, b.y, z_))
        h_ = c.ray(pa, pb - pa, (pb - pa).length)
        if h_ is not None and h_.obj.name not in MINE:
            return False
    return True


peds = 0
for attempt in range(900):
    axis, line, (u0, u1) = WALKS[rl.randrange(len(WALKS))]
    kind = rl.randrange(4)
    spd = walk.kinds[kind][4]
    dirn = rl.choice((-1, 1))
    off = 0.45 * dirn * (1 if axis == "x" else -1) * (1 if line < 0 else -1)
    L = rl.uniform(14.0, 34.0)
    if u1 - u0 < L:
        continue
    a_ = rl.uniform(u0, u1 - L)
    s_, e_ = (a_, a_ + L) if dirn > 0 else (a_ + L, a_)
    mk = (lambda u, ln=line + off, ax=axis: Vector((u, ln, 0)) if ax == "x" else Vector((ln, u, 0)))
    A, B = mk(s_), mk(e_)
    n = int(L / spd)
    f0 = rl.randint(-n // 2, END - 20)
    track = [(k, A.lerp(B, (k - f0) / n) + Vector((0, 0, 1.0))) for k in range(max(1, f0), min(END, f0 + n) + 1, 4)]
    if len(track) < 4 or not (f0 + n > 1) or not guard.clear(track, r_sub=1.4, r_cam=1.8, r_line=0.55):
        continue
    if not sidewalk_clear(A, B):
        continue
    w = walk.spawn(kind, f"Ped{peds}")
    w.walk(A, B, f0, phase=rl.random())
    peds += 1
    if peds >= 14:                                   # a few people sell the street (each one is a rig to evaluate)
        break
# pigeons: on the board's ledge (startled by his landing), on the rooftop, on the street at the finale, + a flock
birds = life.PigeonKit()
pg = 0


def flock(points, f_go, away, face=0.0):
    global pg
    for i, p_ in enumerate(points):
        b_ = birds.spawn(f"Pigeon{pg}")
        b_.perch(p_, 1, face + rl.uniform(-70, 70), phase=rl.randint(0, 120))
        b_.fly_off(f_go + rl.randint(-3, 5), Vector((away[0] + rl.uniform(-0.3, 0.3), away[1] + rl.uniform(-0.3, 0.3), 0)),
                   speed=rl.uniform(0.24, 0.32), seed=pg)
        pg += 1


land1 = int(perf.clip_frame(sw1, 40)) - 8
ledge_y = WALL_G.point.y + WALL_G.normal.y * 0.6
flock([Vector((x_, ledge_y + rl.uniform(-0.2, 0.25), LEDGE_TOP)) for x_ in (-14.6, -13.4)], land1, (0.7, 0.7))
flock([Vector((RF_SPOT[0] + 2.4, RF_SPOT[1] + 0.8, ROOF_Z))], int(land7.start) - 6, (-0.6, -0.8))
flock([Vector((FIN_SPOT[0] + rl.uniform(-2.5, 1.5), FIN_SPOT[1] + rl.uniform(-4.5, -2.0), Z_ROAD)) for _ in range(2)],
      int(land8.start) - 10, (-0.2, -1.0))
print(f"LIFE parked {parked}, moving {moving}, queued {queued}, pedestrians {peds}, pigeons {pg}")


# ------------------------------------------------------------------ checks: is he in frame and unobstructed?
def visible_report():
    bad = []
    dg = bpy.context.evaluated_depsgraph_get()
    for f in range(1, END, 6):
        sc.frame_set(f)
        cl = cam.cam.matrix_world.translation
        h = hp(f)
        d = h - cl
        ok, loc, nor, i, ob, m = sc.ray_cast(bpy.context.evaluated_depsgraph_get(), cl, d.normalized(), distance=d.length - 0.6)
        if ok and ob.name not in MINE and not ob.name.startswith(("Web", "Bills", "Spider", "Cash")):
            bad.append((f, ob.name))
    print("OCCLUDED", bad)


visible_report()
VO_CUES = {n: T[f"vo{n}"] for n in range(1, 14)}
shot.finish(NAME, exposure=-0.35, samples=24, view="AgX", grade="AgX - Punchy",
            markers=[(f"vo {n}", f) for n, f in VO_CUES.items()] + [
                ("S1 board", T["vo1"]), ("S2 billboard", f2a), ("S3 ticker", int(tick.start)),
                ("S4 bus", T["vo4"]), ("S5 subway", T["vo5"]), ("S6 screen", T["vo6"]), ("S7 roof", f7b),
                ("S8 tower", f8a), ("S9 yank", Y1), ("end", END)])
fx.cine_grade(sc)                                     # haze (aerial perspective), bloom, dispersion, vignette
bpy.ops.wm.save_mainfile()
cues = sorted(VO_CUES.items(), key=lambda kv: kv[1])
for (a, fa), (b, fb) in zip(cues, cues[1:]):
    if fa + dur(a) * FPS > fb:
        print(f"VO OVERLAP {a}->{b}: {(fa + dur(a) * FPS - fb) / FPS:.2f}s")
print("CUTS", CUTS)
print("TIMES", {k: (getattr(v, 'start', None) and int(v.start)) for k, v in dict(sw1=sw1, perch1=perch1, happy=happy, curious=curious,
      web2=web2, fly2=fly2, hang2=hang2, fly3=fly3, land3=land3, tick=tick, run4=run4, look4=first(look4), hop_a=hop_a, cling_l=cling_l,
      fly5=fly5, frus=frus, fly6=fly6, land6=land6, worry=worry, moon=first(moon), fly7=fly7, land7=land7, perch7=perch7,
      conf7=first(conf7), fly8=fly8, land8=land8, rise8=rise8, heave=heave, pull=pull, flop=flop).items()}, "Y1", Y1, "C", C)
print(f"STREET frames 1-{END} ({END / FPS:.1f}s)  ground-lock {lock_err * 100:.1f} cm  optional clips:",
      {n: have(n) for n in ("MX Moonwalk 1", "MX Terrified", "MX Taunt", "MX Sprint", "MX Happy Hand Gesture")})
