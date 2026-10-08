"""Street piece (~76 s): Spidey's tour of the inspection story through a city at sunset — one continuous journey.

    S0  aerial: he zips down the avenue on a web line, lands on the wall board's ledge (top-left corner)
    S1  mural: "You already ship a lot of AI-generated code." (stands at the board's corner, presents)
    S2  zips straight across to the billboard, lands on its catwalk at the left edge: "But do you do enough..."
    S3  zips east to the LED ticker (shop-front height), lands at its left end: "Code now ships faster than ever."
    S4  sprints to the bus stop, stops at the ad's left edge; spiders on "bugs": the bug dance; up onto the shelter
    S5  zips to the subway lightbox, stands at its left edge: "Human review can't keep up."
    S6  zips up to the catwalk under the big screen: a few steps on each risk, then moonwalks off with the customers
    S7  zips up to the rooftop, stands at the screen's left edge: "How do you stay competitive?" / "...inspection layer."
    S8  leaps off, zips down into the intersection: the v3 storeyed building, each floor lights on its word, cash on top
    S9  yanks INSPECTION (the ground floor) out -> the floors above hang a beat, then pancake; cash rain; he flops

Review rules (scripts/check_rules.py audits them every build): web travel is a straight pull along the line, body
at one angle, no spins or flips (lean() holds one tilt); explaining = upright and facing the camera (square_up);
he stands right next to each slide at its LEFT edge, never over the text or inside the board; no hangs and no web
from a foot; each slide leaves at the cut after its scene (one focal point per frame).

    python3 scripts/03c_street_signs.py
    blender -b build/character.blend --python scripts/04_street_part_1_final.py   # -> build/street_part_1_final.blend (+ _audit.json)
    blender -b build/street_part_1_final.blend --python scripts/check_rules.py   # the review-rule audit
"""
import bpy, os, sys, math, random, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mathutils import Vector, Euler, Matrix
from pipeline import paths, anim, fx, shot, props, city, swing
from pipeline.mixamo import Performer, ClipGroup
from pipeline.shot import L_HAND, R_HAND, HIPS

FPS = 30
NAME = "street_part_1_final"
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
TICK = NORTH(13.0, z=2.0)                      # east arm, north (near the corner): LED ticker at shop-front height
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
BB_BOT = BB_C.z - 9.6 / 3.0 / 2 - 0.12
# the billboard's service catwalk (what he lands and presents on): runs past the board's left edge (screen-left)
BB_WALK = (BB_C.x - 9.6 / 2 - 1.1, BB_C.x + 9.6 / 2 + 0.2, BB_C.y - 1.05, BB_C.y + 0.05)
BB_SPOT = (BB_C.x - 9.6 / 2 - 0.4, BB_C.y - 0.55)               # just left of the board, beside it (not over the text)
TK_W = 8.4
TK_C = Vector((13.0, TICK.point.y, 2.0))             # shop-front LED strip at eye level, x 8.8-17.2
TK_SPOT = (TK_C.x - TK_W / 2 - 0.45, TICK.point.y - 0.8)          # on the sidewalk at its left end
ticker = city.sign("Ticker", img("ticker_faster"), TK_C, TICK.normal, TK_W, aspect=3600 / 420, emit=2.2, frame="led",
                   offset=0.35)
px, POST = city.flat_spot(c, [26.0, 24.8, 24.4, 25.2, 24.0, 23.6, 27.0], 0.0, -1, 2.4, 3.6)
POST_C = Vector((px, POST.point.y, 1.85))           # low: his head level with the lower half of the box
SUB_SPOT = (POST_C.x + 3.6 / 2 + 0.42, POST.point.y + 0.12 + 0.5)   # screen-left of it (camera looks -y: left = +x)
SUB_N = 180
subway = city.sign("Subway", seq0("st_queue"), POST_C, POST.normal, 3.6, emit=1.4, frame="lightbox", seq=(SUB_N, 1),
                   offset=0.12)
SCR_N = Vector((0, -1, 0))
SCR_C = Vector((25.0, SCREEN.point.y, 7.2))
# rooftop screen on the tall avenue building, facing the avenue (west)
RS_H = 6.2 / 16 * 9
RS_C = Vector((13.4, -19.2, ROOF_Z + 0.35 + RS_H / 2))   # low on the roof: he stands at its left edge (y -15.7, roof to -15)
RF_SPOT = (RS_C.x - 0.7, RS_C.y + 6.2 / 2 + 0.42)
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
BB_WALK_Z = BB_BOT - 0.02
bbw = fx.material("BB_Catwalk", (0.12, 0.13, 0.14), rough=0.5, metallic=0.7)
box("BBCatwalk", (BB_WALK[1] - BB_WALK[0], BB_WALK[3] - BB_WALK[2], 0.12),
    ((BB_WALK[0] + BB_WALK[1]) / 2, (BB_WALK[2] + BB_WALK[3]) / 2, BB_WALK_Z - 0.06), bbw)
for k, x_ in enumerate((BB_C.x - 3.0, BB_C.x + 3.0)):              # struts down to the roof
    box(f"BBStrut{k}", (0.1, 0.1, BB_WALK_Z - BB_ROOF), (x_, BB_WALK[2] + 0.3, (BB_WALK_Z + BB_ROOF) / 2), bbw)
glass = fx.material("Shelter_Glass", (0.6, 0.7, 0.75), rough=0.05)
box("ShelterRoof", (4.2, 1.8, 0.12), BUS + Vector((0, 0, 2.5)), steel)
box("ShelterBack", (4.0, 0.05, 2.2), BUS + Vector((0, -0.8, 1.25)), glass)
for k, dx in enumerate((-2.0, 2.0)):
    box(f"ShelterPost{k}", (0.1, 0.1, 2.5), BUS + Vector((dx, -0.8, 1.25)), steel)
    box(f"ShelterPostF{k}", (0.1, 0.1, 2.5), BUS + Vector((dx, 0.8, 1.25)), steel)
BUS_AD_W = 3.6
BUS_AD_C = BUS + Vector((-2.6, 0.0, 1.55))
BUS_AD_N = Vector((-1, 0, 0))
BUS_SPOT = (BUS_AD_C.x - 0.75, BUS_AD_C.y + BUS_AD_W / 2 + 0.38)    # screen-left of the ad (camera looks +x: left = +y)
BUG_N = 210


# ------------------------------------------------------------------ read shots (computed first: he faces these cameras)
# Review rules for every read: the whole slide straight-on, him upright at its LEFT edge, right next to it (never
# over the text or inside the board), facing the camera. Web travel is a straight pull along the line (hands up on
# it, body at one angle, no tumbles); no hangs.
Z = Vector((0, 0, 1))
SHELTER_TOP = 2.56


def open_to(a, b, slack=0.3):
    """Nothing between a and b (b may be in open air, e.g. where he will stand)."""
    d = Vector(b) - Vector(a)
    h = c.ray(a, d, d.length)
    return h is None or (h.point - Vector(a)).length >= d.length - slack


def clear_cam(cands, pts):
    for cnd in cands:
        if clear_view(cnd[0], pts):
            return cnd
    return cands[0]


def fit(loc, pts, margin=1.12):
    """Aim + focal length (36 mm sensor) that just fit `pts` in a 16:9 frame from `loc`."""
    loc = Vector(loc)
    ds = [Vector(p) - loc for p in pts]
    yaws = [math.atan2(d.x, d.y) for d in ds]
    mean = math.atan2(sum(math.sin(a) for a in yaws), sum(math.cos(a) for a in yaws))
    rel = [(a - mean + math.pi) % (2 * math.pi) - math.pi for a in yaws]
    pit = [math.atan2(d.z, d.xy.length) for d in ds]
    yc, pc = mean + (min(rel) + max(rel)) / 2, (min(pit) + max(pit)) / 2
    hy, hv = (max(rel) - min(rel)) / 2 * margin, (max(pit) - min(pit)) / 2 * margin
    lens = min(18.0 / math.tan(max(hy, 1e-3)), 10.125 / math.tan(max(hv, 1e-3)))
    tgt = loc + Vector((math.sin(yc) * math.cos(pc), math.cos(yc) * math.cos(pc), math.sin(pc))) * 10.0
    return tgt, lens


def presenter(bc, normal, w, h, spot, floor, lens_min=26.0, offset=0.05, eye=None):
    """Static read shot: the whole slide straight-on, him standing at its left edge, both in frame.
    Steps back along the slide's normal until the lens is at least `lens_min` mm and nothing blocks the view."""
    n = Vector((normal[0], normal[1], 0)).normalized()
    right = (-n).cross(Z).normalized()
    bc = Vector(bc)
    sp = Vector((spot[0], spot[1], floor))
    pts = [bc + right * (w / 2 * a) + Z * (h / 2 * b) for a in (-1, 1) for b in (-1, 1)]
    pts += [sp + right * dx + Z * dz for dx in (-0.45, 0.45) for dz in (0.0, 1.9)]
    us = [(p - bc).dot(right) for p in pts]
    mid = bc + right * ((min(us) + max(us)) / 2)
    eye = (min(p.z for p in pts) + max(p.z for p in pts)) / 2 if eye is None else eye
    first = None
    for k in range(8, 70):
        D = k * 0.5
        for side in (0.0, 0.5, -0.5, 1.0, -1.0):
            loc = mid + n * D + right * side
            loc.z = eye
            tgt, lens = fit(loc, pts)
            if lens < lens_min:
                break
            first = first or (loc, tgt, lens)
            if all(open_to(loc, p) for p in board_pts(bc + n * offset, n, w, h) + [sp + Z * dz for dz in (0.3, 1.0, 1.6)]):
                print("PRESENTER", tuple(round(v, 1) for v in loc), f"{lens:.0f}mm D{D}")
                return loc, tgt, lens
    print("PRESENTER blocked, using", first)
    return first or (loc, tgt, lens)


def gesture_side(point, him, cam_loc):
    """His arm on the slide's side: slide to camera-right of him -> his left arm (he faces the camera)."""
    d = Vector(him) - Vector(cam_loc)
    right = Vector((d.y, -d.x))
    return "L" if (Vector(point).xy - Vector(him).xy).dot(right) > 0 else "R"


face_to = lambda a, b: math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1])))      # `face` for standing at a, facing b
# S1 mural: the street camera, the whole board + him on its ledge (top-left corner)
TOP1 = (G_C.x + 2.5, WALL_G.point.y + WALL_G.normal.y * 0.85)       # on the board's top ledge, screen-LEFT corner
b_pts = board_pts(G_C + WALL_G.normal * 0.45, WALL_G.normal, GB_W, GB_H)
s1 = presenter(G_C + WALL_G.normal * 0.45, WALL_G.normal, GB_W, GB_H, TOP1, LEDGE_TOP)
cam2 = presenter(BB_C, (0, -1, 0), 9.6, 3.2, BB_SPOT, BB_WALK_Z)
TK_H = TK_W * 420 / 3600
cam3 = presenter(TK_C + TICK.normal * 0.35, TICK.normal, TK_W, TK_H, TK_SPOT, 0.0)
cam4 = presenter(BUS_AD_C + BUS_AD_N * 0.1, BUS_AD_N, BUS_AD_W, BUS_AD_W * 9 / 16, BUS_SPOT, 0.0)
cam5 = presenter(POST_C + POST.normal * 0.12, POST.normal, 3.6, 3.6 * 9 / 16, SUB_SPOT, 0.0)
SCR_W, SCR_OFF = 9.2, 0.9
SCR_H = SCR_W * 9 / 16
TS_Z = SCR_C.z - SCR_H / 2 - 1.55                 # catwalk below the screen: his head only reaches its bottom margin
TS_SPOT = (SCR_C.x - SCR_W / 2 + 0.8, SCREEN.point.y - SCR_OFF - 0.65)    # on the catwalk, 0.65 m in front of the glass
scr_pts = board_pts(SCR_C + SCR_N * SCR_OFF, SCR_N, SCR_W, SCR_H)
ts = presenter(SCR_C + SCR_N * SCR_OFF, SCR_N, SCR_W, SCR_H, (SCR_C.x + 1.5, TS_SPOT[1]), TS_Z)  # him at the left .. middle
cam7 = presenter(RS_C, (-1, 0, 0), 6.2, RS_H, RF_SPOT, ROOF_Z)
# finale: the v3 storeyed building, in the intersection (the streets and city all around it); he stands at its left corner
FIN_C = Vector((0.0, 2.0))
FIN_W, FIN_D, FIN_N, FIN_S = 12.0, 7.0, 4, 2.4         # compact: the whole building + him read in one frame
FIN_FRONT = FIN_C.y - FIN_D / 2
FIN_TOP = FIN_N * FIN_S
FX_SPOT = (FIN_C.x - FIN_W / 2 - 0.8, FIN_FRONT - 1.3)   # right at its left corner, beside the ground floor's path
_g = c.ray(Vector((FX_SPOT[0], FX_SPOT[1], 1.0)), Vector((0, 0, -1)), 3.0)
FL8 = _g.point.z if _g is not None else 0.0              # plaza paving / road height under him
fin_shot = presenter(Vector((FIN_C.x, FIN_FRONT, (FIN_TOP + 2.6) / 2)), (0, -1, 0), FIN_W, FIN_TOP + 2.6, FX_SPOT, FL8,
                     lens_min=19.0, eye=FL8 + 2.3)     # low and close: him big at the corner, the floors rising behind
fin_loc, fin_tgt, fin_lens = fin_shot
print("FINALE floor", round(FL8, 2))

# ------------------------------------------------------------------ performance
# Standing beats are placed shots (`at=`, height from HEIGHTS + per-frame contact). Every move between
# locations is a TRAVEL keyed every frame by travel() from where the last shot ends to where the next one
# starts, so the audience sees him get there (no teleport cuts).
perf = Performer(rig).place(x=0, y=0, face=0)
hit_pk = perf.extreme("Standing 1H Magic Attack 02", R_HAND, (1, 0, 0), 16, 40)
EXPLAIN = "CMU 18_08 conversation - explain with hand gesture"
PRESENT = ["Talking (2)", "Talking (1)", EXPLAIN]
_turn = [0]


def talk(length, face=0, blend=10, at=None, cut_blend=0):
    parts, left = [], int(length)
    while left > 8:
        clip = PRESENT[_turn[0] % len(PRESENT)]
        _turn[0] += 1
        a0, a1 = bpy.data.actions[clip].frame_range
        n = min(left + (blend if parts else 0), int(a1 - a0) - 2)
        frm = perf.lively(clip, n, target=1.5) if clip == EXPLAIN else a0 + 1
        parts.append(perf.then(clip, frm=frm, length=n, blend=blend, face=face, in_place=0.7,
                               at=at if not parts else None, cut_blend=cut_blend))
        left -= n - (blend if len(parts) > 1 else 0)
    return parts[0] if len(parts) == 1 else ClipGroup(parts)


def talk_until(f, face, blend=10):
    """Explain (upright, to the camera) until scene frame f."""
    return talk(max(14, int(f) - int(perf.end) + blend), face=face, blend=blend)


first = lambda g: g.cycles[0] if hasattr(g, "cycles") else g
final = lambda g: g.cycles[-1] if hasattr(g, "cycles") else g
have = lambda n: n in bpy.data.actions
opt = lambda n, fallback: n if have(n) else fallback       # new Mixamo clips when they're in character.blend


def stride(action, frm=None, to=None):
    """A clip's own ground speed (m / frame), measured on its hips with the root at identity."""
    act = bpy.data.actions[action]
    a0, a1 = act.frame_range
    frm, to = frm or a0, to or a1
    perf.root.animation_data_clear()
    perf.root.matrix_world = Matrix.Identity(4)
    d = (perf._hips(act, to).xy - perf._hips(act, frm).xy).length
    rig.animation_data.action = None
    return d / max(1, to - frm)


HANG = "Hanging Idle"                         # both hands up, gripping: the pose on a web line
SHOOT = "Standing 1H Magic Attack 02"


def shoot(face, blend=8):
    """Fires the line (right hand) towards where he's going."""
    return perf.then(SHOOT, frm=16, to=40, speed=1.1, blend=blend, face=face, in_place=1.0)


def zip_(dist, face, blend=6, cap=72):
    """Pulled along the web line: hands up on it, body straight (lean() angles him along the line). No flips."""
    return perf.then(HANG, frm=20, length=min(cap, int(16 + dist * 1.15)), face=face, in_place=1.0, blend=blend)


def touch(face, at):
    """Lets go just above the spot: feet-first landing, a crouch, up to standing (no roll)."""
    return perf.then("Hard Landing", frm=14, to=64, speed=1.6, face=face, in_place=1.0, at=at, cut_blend=5)


def stand(spot, floor):
    return Vector((spot[0], spot[1], floor + 1.0))


UPRIGHT = 30                                   # a landing (touch) is back up to standing this many frames in: lines start then
# ---- S0/S1: zip down the avenue onto the wall board's ledge (screen-left corner); up, excited, presents
P1_START = Vector((2.0, 30.0, 18.0))
f_1 = face_to(P1_START, TOP1)
zip1 = perf.then(HANG, frm=20, length=44, face=f_1, in_place=1.0)
land1 = touch(f_1, TOP1)
F1 = face_to(TOP1, s1[0])
happy = perf.then(opt("MX Happy Hand Gesture", "Happy Idle"), frm=8, length=54, blend=12, face=F1, in_place=1.0)
T1 = int(land1.start) + UPRIGHT
talk1 = talk_until(T1 + hold(1, 0.4), face=F1)
# ---- S2: straight over to the billboard: web zip across the street, lands on its catwalk at the left edge
f_2 = face_to(TOP1, BB_SPOT)
shoot2 = shoot(f_2)
zip2 = zip_((stand(BB_SPOT, BB_WALK_Z) - stand(TOP1, LEDGE_TOP)).length, f_2)
land2 = touch(f_2, BB_SPOT)
F2 = face_to(BB_SPOT, cam2[0])
T2 = int(land2.start) + UPRIGHT
talk2 = talk_until(T2 + hold(2, 0.5), face=F2)
# ---- S3: east along the north side down to the LED ticker, lands at its left end
f_3 = face_to(BB_SPOT, TK_SPOT)
shoot3 = shoot(f_3)
zip3 = zip_((stand(TK_SPOT, 0) - stand(BB_SPOT, BB_WALK_Z)).length, f_3)
land3 = touch(f_3, TK_SPOT)
F3 = face_to(TK_SPOT, cam3[0])
T3 = int(land3.start) + UPRIGHT
tick = talk_until(T3 + hold(3, 0.9, 70), face=F3)
# ---- S4: sprints across to the bus stop, stops at the ad's left edge; "bugs": the spiders, the dance, onto the roof
SPRINT, RSTOP = opt("MX Sprint", "Two Cycle Sprint"), opt("MX Run To Stop", "Run To Stop")
f_4 = face_to(TK_SPOT, BUS_SPOT)
v_run = stride(SPRINT)
r0_, r1_ = bpy.data.actions[RSTOP].frame_range
d_stop = stride(RSTOP) * (r1_ - r0_)
dist4 = (Vector(BUS_SPOT) - Vector(TK_SPOT)).length
cyc = bpy.data.actions[SPRINT].frame_range[1] - bpy.data.actions[SPRINT].frame_range[0]
n_run = max(2, round((dist4 - d_stop) / max(0.05, v_run) / max(1, cyc - 4)))
print(f"RUN {dist4:.1f} m: sprint {v_run:.3f} m/f x{n_run}, stop {d_stop:.2f} m")
run4 = perf.then(SPRINT, repeat=n_run, blend=10, face=f_4, in_place=1.0)
stop4 = perf.then(RSTOP, blend=5, face=f_4, in_place=1.0)
settle4 = perf.then("Breathing Idle", length=14, face=f_4, at=BUS_SPOT, cut_blend=6, in_place=1.0)
F4 = face_to(BUS_SPOT, cam4[0])
look4 = talk(F(word(4, "bugs") * FPS) + 18, face=F4, blend=12)
shock = perf.then("CMU 120_16 Mickey Surprised", frm=140, to=262, blend=6, face=F4 + 15, in_place=0.8)   # the bug dance (v3)
ROOF_SPOT = (BUS.x - 0.8, BUS.y + 0.1)
f_h = face_to(BUS_SPOT, ROOF_SPOT)
hop_a = perf.then(opt("MX Jumping Up", "Hard Landing"), blend=4, face=f_h, in_place=1.0)
hop_b = perf.then("Hard Landing", frm=10, to=28, blend=3, face=f_h, in_place=1.0)
cling_l = perf.then("Hard Landing", frm=28, to=40, face=f_h, at=ROOF_SPOT)
roof_cam = ((ROOF_SPOT[0] - 5.6, ROOF_SPOT[1] + 3.4, 3.8), (ROOF_SPOT[0] - 0.4, ROOF_SPOT[1], 2.2))
cling = (perf.then("MX Terrified", frm=110, length=64, blend=8, face=face_to(ROOF_SPOT, roof_cam[0])) if have("MX Terrified") else
         perf.then("Hard Landing", frm=40, to=44, speed=4 / 58, blend=8, face=face_to(ROOF_SPOT, roof_cam[0])))
# ---- S5: web zip off the shelter to the subway lightbox, lands at its left edge
f_5 = face_to(ROOF_SPOT, SUB_SPOT)
shoot5 = shoot(f_5)
zip5 = zip_((stand(SUB_SPOT, 0) - stand(ROOF_SPOT, SHELTER_TOP)).length, f_5)
land5 = touch(f_5, SUB_SPOT)
F5 = face_to(SUB_SPOT, cam5[0])
T5 = int(land5.start) + UPRIGHT
frus = talk_until(T5 + hold(5, 0.6), face=F5)
# ---- S6: zip up onto the big screen's catwalk; a few steps right on each risk, then moonwalks off with the customers
f_6 = face_to(SUB_SPOT, TS_SPOT)
shoot6 = shoot(f_6)
zip6 = zip_((stand(TS_SPOT, TS_Z) - stand(SUB_SPOT, 0)).length, f_6)
land6 = touch(f_6, TS_SPOT)
F6 = face_to(TS_SPOT, ts[0])
T6 = int(land6.start) + UPRIGHT
words6 = [T6 + F(word(6, w) * FPS) for w in ("downtime", "security", "slow", "bad")]
WALK = "Walking"
v_walk = stride(WALK)
WALK_D = (0.7, 0.85, 0.95, 1.05)                    # "walks a little ... a little more"
walks, talks6 = [], []
for k, fw in enumerate(words6):
    talks6.append(talk_until(fw + 6, face=F6))
    room = (words6[k + 1] - fw - 18) if k + 1 < len(words6) else 40
    walks.append(perf.then(WALK, start=fw, frm=1, length=max(12, min(int(WALK_D[k] / v_walk), room)), blend=6, face=90))
LEAVE_AT = int(walks[-1].end) - 4
MOON = opt("MX Moonwalk 1", "Walking")
moon = perf.then(MOON, blend=8, repeat=3, face=-90, in_place=1.0, speed=1.0)     # faces screen-left, glides screen-right
MOON_DIST = 11.0
M_END = (TS_SPOT[0] + sum(WALK_D) + MOON_DIST, TS_SPOT[1])
# ---- S7: off screen at the end of the catwalk, zip up to the rooftop, lands at the roof screen's left edge
f_7 = face_to(M_END, RF_SPOT)
shoot7 = perf.then(SHOOT, frm=16, to=40, speed=1.1, face=f_7, in_place=1.0, at=M_END)
zip7 = zip_((stand(RF_SPOT, ROOF_Z) - stand(M_END, TS_Z)).length, f_7)
land7 = touch(f_7, RF_SPOT)
F7 = face_to(RF_SPOT, cam7[0])
T7 = int(land7.start) + UPRIGHT
T8 = T7 + F((dur(7) + 0.3) * FPS)
talk7 = talk_until(T8 + hold(8, 0.6), face=F7)
# ---- S8: leaps off the roof, the web catches him, zips down the avenue to the building on the plaza
f_8 = face_to(RF_SPOT, FX_SPOT)
fall8 = perf.then(opt("MX Falling", "Hard Landing"), frm=1, length=22, blend=10, face=f_8, in_place=1.0)   # leaps off: free fall
zip8 = zip_(65.0, f_8, blend=6, cap=70)
land8 = touch(f_8, FX_SPOT)
F8 = face_to(FX_SPOT, fin_loc)
T = {}
ORDER = [13, 9, 10, 11, 12]                          # "It starts with inspection" opens the building
T["vo13"] = int(land8.start) + UPRIGHT + 4
for a_, b_ in zip(ORDER, ORDER[1:]):
    T[f"vo{b_}"] = T[f"vo{a_}"] + F((dur(a_) + 0.2) * FPS)
LIGHT_WORD = [(13, "inspection"), (9, "engineers"), (10, "customers"), (11, "competitive")]
lit = [T[f"vo{n}"] + F(word(n, w) * FPS) for n, w in LIGHT_WORD]
Y1 = T["vo12"] + F(word(12, "inspection") * FPS)     # yanks INSPECTION out
show = talk_until(Y1 - 40 + 8, face=F8)
FB = face_to(FX_SPOT, FIN_C)
heave = perf.then("Pull Heavy Object Start", start=Y1 - 40, frm=4, to=40, blend=8, face=FB)   # lines taut, leaning back
pull = perf.then("Pull Heavy Object Stop", start=Y1 - 4, to=30, speed=1.0, blend=8, face=FB)  # the yank
C_EST = T["vo12"] + F(word(12, "everything") * FPS) - 6
watch = perf.then("Breathing Idle", length=max(20, C_EST + 40 - int(pull.end) + 8), blend=8, face=FB)   # stares at the wreck
slump = perf.then("Hard Landing", frm=19, to=28, speed=0.8, blend=8, face=FB - 20)              # knees give way...
flop = perf.then("Fallen Idle", length=150, blend=16, face=F8 - 60)                              # ...flat on the street
perf.build()

T["vo1"], T["vo2"], T["vo3"] = T1, T2, T3
T["vo4"] = int(first(look4).start) + 4
T["vo5"], T["vo6"], T["vo7"], T["vo8"] = T5, T6, T7, T8
cash_f = T["vo11"] + F(word(11, "money") * FPS)
C = T["vo12"] + F(word(12, "everything") * FPS) - 6                      # the building comes down

# ------------------------------------------------------------------ body to camera on every talk beat
flat = lambda gs: [c_ for g in gs for c_ in (g.cycles if hasattr(g, "cycles") else [g])]
AIMS = [([happy, talk1], s1[0]), ([talk2], cam2[0]), ([tick], cam3[0]), ([look4], cam4[0]), ([frus], cam5[0]),
        (talks6, ts[0]), ([talk7], cam7[0]), ([show], fin_loc)]
aim_spans = [(int(first(gs[0]).start), int(final(gs[-1]).end), Vector(loc)) for gs, loc in AIMS]


def facing_cam(f):
    for a_, b_, p in aim_spans:
        if a_ <= f <= b_:
            return (p.x, p.y)
    h = perf.bone_world(HIPS, f)
    return (h.x, h.y - 5)


square_err = perf.square_up(flat(sum((gs for gs, _ in AIMS), [])), facing_cam)

# ------------------------------------------------------------------ heights of the standing shots
last = lambda clip: math.ceil(clip.end - 1e-6) - 1      # a shot's final frame (the next shot owns ceil(end))


def low_rel(clip):
    """Lowest toe height of a clip with the root on the ground (so a shot can stand ON a surface)."""
    return min(min(perf.bone_world(b, f).z for b in ("mixamorig:LeftToeBase", "mixamorig:RightToeBase"))
               for f in range(int(clip.start) + 4, int(clip.end) - 2, 6))


def between(a, b):
    """Every queued clip from a's first cycle to b's last (in order)."""
    i0, i1 = perf.clips.index(first(a)), perf.clips.index(final(b))
    return perf.clips[i0:i1 + 1]


on = lambda clips, floor, until: [(int(c_.start), (int(n.start) - 1) if n is not None else until, floor - low_rel(c_), c_)
                                  for c_, n in zip(clips, list(clips[1:]) + [None])]
SURFACES = [(land1, shoot2, LEDGE_TOP, zip2), (land2, shoot3, BB_WALK_Z, zip3), (cling_l, shoot5, SHELTER_TOP, zip5),
            (land6, shoot7, TS_Z, zip7), (land7, talk7, ROOF_Z, fall8)]
HEIGHTS = sum((on(between(a_, b_), z_, int(nx.start) - 1) for a_, b_, z_, nx in SURFACES), [])
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

# ------------------------------------------------------------------ travel paths (in time order: each starts where the last ended)
hp = lambda f: perf.bone_world(HIPS, f)
TRAVEL = []


def travel(path, f0, f1, axes=(0, 1, 2), name=""):
    """Key the root (every frame f0..f1) so the hips sit on path((f - f0) / (f1 - f0)), then restore what the root
    did after f1 (a lin key at f1 would otherwise drag every frame up to the next key towards the end of the path).
    axes=(0, 1): only the ground plan (a run keeps the clip's own bounce; feet are locked afterwards)."""
    f0, f1 = int(f0), int(f1)
    keep = []
    for i in axes:
        fc = anim.fcurve(perf.root, "location", i)
        prior = [k for k in fc.keyframe_points if k.co.x <= f1 + 1] if fc else []
        gov = max(prior, key=lambda k: k.co.x) if prior else None
        keep.append((i, fc.evaluate(f1 + 1) if fc else perf.root.location[i],
                     "const" if gov is not None and gov.interpolation == "CONSTANT" else "lin"))
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        delta = (rig.matrix_world @ rig.pose.bones[HIPS].head) - perf.root.matrix_world.translation
        want = path((f - f0) / max(1, f1 - f0))
        for i in axes:
            anim.key(perf.root, "location", f, want[i] - delta[i], i, "lin")
    for i, v, ease in keep:
        anim.key(perf.root, "location", f1 + 1, v, i, ease)
    TRAVEL.append((f0, f1, name))


MINE = {o.name for o in rig.children_recursive} | {rig.name}


def path_hits(f0, f1, name):
    """Report frames where the body's path cuts through set geometry (hips segment rays)."""
    bad = []
    for f in range(int(f0), int(f1)):
        a, b = hp(f), hp(f + 1)
        d = b - a
        if d.length > 1e-3:
            h = c.ray(a, d, d.length + 0.3)
            if h is not None and h.obj.name not in MINE and not h.obj.name.startswith(("Web",)):
                bad.append((f, h.obj.name))
    print(f"PATH {name} f{int(f0)}-{int(f1)} hits", bad[:12])


def zip_path(p0, p1, lift=0.0):
    """Near-straight pull along the line: accelerates off the start, eases into the release."""
    p0, p1 = Vector(p0), Vector(p1)
    ctrl = (p0 + p1) / 2 + Z * lift

    def fn(t):
        u = 0.6 * (t * t * (3 - 2 * t)) + 0.4 * t
        return (1 - u) ** 2 * p0 + 2 * (1 - u) * u * ctrl + u * u * p1
    return fn


def bez(p0, p1, p2, p3):
    p0, p1, p2, p3 = (Vector(v) for v in (p0, p1, p2, p3))

    def fn(t):
        u = swing.ease_pendulum(t) * 0.6 + t * 0.4
        return (1 - u) ** 3 * p0 + 3 * (1 - u) ** 2 * u * p1 + 3 * (1 - u) * u * u * p2 + u ** 3 * p3
    return fn


def find_anchor(p0, p1, fallback, min_up=3.0, reach=45.0):
    """A real place for the web to stick: a facade / roof edge above the end of the zip, ahead of him."""
    p0, p1 = Vector(p0), Vector(p1)
    mid = p0.lerp(p1, 0.75)
    run = (p1 - p0).xy
    best = None
    for el in (35, 45, 55, 65, 75, 85):
        for az in range(0, 360, 10):
            ce = math.cos(math.radians(el))
            d = Vector((math.cos(math.radians(az)) * ce, math.sin(math.radians(az)) * ce, math.sin(math.radians(el))))
            h_ = c.ray(mid, d, reach)
            if h_ is None or h_.obj.name in MINE or h_.point.z < max(p0.z, p1.z) + min_up:
                continue
            along = (h_.point.xy - p0.xy).dot(run) / max(1e-6, run.length_squared)
            if not 0.7 <= along <= 1.4:                     # ahead of him, over the end of the zip
                continue
            off = abs((h_.point.xy - p0.xy).cross(run)) / max(1e-6, run.length)
            if off > 8.0:
                continue
            score = (h_.point.xy - p1.xy).length + 0.4 * off
            if best is None or score < best[0]:
                best = (score, h_.point.copy())
    print("ANCHOR", tuple(round(v, 1) for v in (best[1] if best else Vector(fallback))), "found" if best else "fallback")
    return best[1] if best else Vector(fallback)


def lean(f0, f1, direction, max_deg=48.0, ramp=6):
    """Body at ONE angle along the line for the whole pull (no tumbling): the root tilts so his long axis points
    along `direction` (towards the anchor), easing in/out over `ramp` frames."""
    fcs = [anim.fcurve(perf.root, "rotation_euler", i) for i in range(3)]
    ev = lambda f: Euler([fc.evaluate(f) if fc else 0.0 for fc in fcs], "XYZ")
    f0, f1 = int(f0), int(f1)
    keep = ev(f1 + 1)
    bases = {f: ev(f) for f in range(f0, f1 + 1)}        # sample first: keying frame f changes how f + 1 evaluates
    u = Vector(direction).normalized()
    axis = Z.cross(u)
    full = min(math.acos(max(-1.0, min(1.0, u.z))), math.radians(max_deg))
    prev = None
    for f in range(f0, f1 + 1):
        w = max(0.0, min(1.0, (f - f0) / ramp, (f1 - f) / ramp))
        w = w * w * (3 - 2 * w)
        base = bases[f]
        e = base if (axis.length < 1e-6 or full * w < 1e-4) else \
            (Matrix.Rotation(full * w, 3, axis.normalized()) @ base.to_matrix()).to_euler("XYZ", prev or base)
        for i in range(3):
            anim.key(perf.root, "rotation_euler", f, e[i], i, "lin")
        prev = e
    for i in range(3):
        anim.key(perf.root, "rotation_euler", f1 + 1, keep[i], i, "lin")


def web_zip(zclip, lclip, anchor, p0=None, lift=0.6, name="", start_path=None):
    """Zip from where he is (or `p0`) to where the landing starts, body angled at the anchor the whole way."""
    f0, f1 = int(zclip.start), int(lclip.start) - 1
    a = Vector(p0) if p0 is not None else hp(f0 - 1)
    b = hp(f1 + 1)
    path = start_path or zip_path(a, b, lift=lift)
    lean(f0 + 1, f1 - 2, Vector(anchor) - path(0.5))
    travel(path, f0, f1, name=name)
    return path


# S0: the opening zip down the avenue onto the board's ledge
a1, b1 = int(zip1.start), int(land1.start)
A1 = find_anchor(P1_START, hp(b1), (TOP1[0], WALL_G.point.y + 0.05, LEDGE_TOP + 7.0))
web_zip(zip1, land1, A1, p0=P1_START, lift=2.5, name="S0")
# S2: ledge -> billboard catwalk (web on the board's top-left corner)
A2 = Vector((BB_C.x - 9.6 / 2 + 0.25, BB_C.y - 0.05, BB_C.z + 9.6 / 3.0 / 2 + 0.1))
web_zip(zip2, land2, A2, lift=1.2, name="S2")
# S3: billboard -> ticker, a long pull east along the north side (out over the sidewalk, clear of the facades)
f3a, f3b = int(zip3.start), int(land3.start)
e3, s3_ = hp(f3b), hp(f3a - 1)
A3 = find_anchor(s3_, e3, (TK_SPOT[0] + 2.0, TICK.point.y - 0.05, 9.0))
p3 = bez(s3_, s3_ + Vector((6.0, -3.0, 0.5)), e3 + Vector((-8.0, -2.5, 2.5)), e3)
web_zip(zip3, land3, A3, name="S3", start_path=p3)
# S4: the sprint across (plan only: the clip keeps its bounce), easing into the stop at the ad
fr0, fr1, fs_ = int(run4.start), int(settle4.start) - 1, int(stop4.start)
pa_, pb_ = hp(fr0), hp(fr1 + 1)
L_run, L_stop = fs_ - fr0, fr1 - fs_


def p4(t):
    f = t * (fr1 - fr0)
    s = f if f <= L_run else L_run + L_stop * ((u := (f - L_run) / max(1, L_stop)) - u * u / 2)
    return pa_.lerp(pb_, s / (L_run + L_stop / 2))


travel(p4, fr0, fr1, axes=(0, 1), name="S4run")
# S4: the hop up onto the shelter roof: out along the curb past the ad's edge, then over onto the roof (low arc:
# a street-light arm hangs above the stop)
f4a, f4b = int(hop_b.start), int(cling_l.start)
h0_, h1_ = hp(f4a - 1), hp(f4b)
k4 = Vector((h0_.x + 0.75 * (h1_.x - h0_.x), h0_.y, 0))


def p4h(t):
    xy = (1 - t) ** 2 * h0_.xy + 2 * (1 - t) * t * k4.xy + t * t * h1_.xy
    return Vector((xy.x, xy.y, h0_.z + (h1_.z - h0_.z) * t + 4 * 1.4 * t * (1 - t)))


travel(p4h, f4a, f4b - 1, name="S4hop")
# S5: shelter roof -> subway lightbox
A5 = find_anchor(hp(int(zip5.start) - 1), hp(int(land5.start)), (SUB_SPOT[0], POST.point.y + 0.05, 7.0))
web_zip(zip5, land5, A5, lift=1.0, name="S5")
# S6: subway -> catwalk (up across the street; web on the screen's top-left frame)
A6 = Vector((SCR_C.x - SCR_W / 2 + 0.3, SCREEN.point.y - SCR_OFF + 0.05, SCR_C.z + SCR_H / 2 + 0.1))
web_zip(zip6, land6, A6, lift=1.0, name="S6")
# moonwalk along the catwalk, with the customers, from the middle of the screen off its right edge
m0, m1 = int(moon.start) + 4, int(shoot7.start) - 1
mh = hp(m0)
mh = Vector((mh.x, mh.y, hp(int(moon.start) + 14).z))
m_end = Vector((M_END[0], M_END[1], mh.z))
travel(lambda t: mh.lerp(m_end, t), m0, m1, name="moon")
if MOON == "Walking":                                                                   # fallback: a walk played backwards
    for t in rig.animation_data.nla_tracks:
        for st in t.strips:
            if st.action.name == "Walking" and st.frame_start >= moon.start - 1:
                st.use_reverse = True
# S7: end of the catwalk -> rooftop: out over the intersection, up the avenue side (web on the roof screen's corner)
f7a, f7b = int(zip7.start), int(land7.start)
q0, q3 = hp(f7a - 1), hp(f7b)
A7 = Vector((RS_C.x + 0.05, RS_C.y + 6.2 / 2 - 0.3, RS_C.z + RS_H / 2 + 0.1))
p7 = bez(q0, q0 + Vector((-4.0, -6.0, 10.0)), q3 + Vector((-3.0, 8.0, 3.0)), q3)       # up and out first: clear of the facade fittings
web_zip(zip7, land7, A7, name="S7", start_path=p7)
# S8: rooftop -> leap, free fall, the web catches him -> along the avenue to the building on the plaza
f8a, f8b = int(fall8.start), int(land8.start)
r0, r3 = hp(f8a - 1), hp(f8b)
A8 = Vector((FX_SPOT[0] + 1.5, FIN_FRONT - 0.05, FIN_N * FIN_S - 0.4))      # the building's front edge, up top
p8 = bez(r0, r0 + Vector((-3.0, 3.0, 3.0)), r3 + Vector((2.0, -5.0, 6.0)), r3)
lean(int(zip8.start) + 1, f8b - 3, A8 - p8(0.6))
travel(p8, f8a, f8b - 1, name="S8")
for fa, fb, name in TRAVEL:
    path_hits(fa, fb, name)

# ------------------------------------------------------------------ polish: feet on the surfaces
LAND_SETTLE = 6                                    # a landing's first frames are still in the air
RAISED = [(int(land1.start) + LAND_SETTLE, int(zip2.start) - 1, LEDGE_TOP),
          (int(land2.start) + LAND_SETTLE, int(zip3.start) - 1, BB_WALK_Z),
          (int(cling_l.start) + 4, int(zip5.start) - 1, SHELTER_TOP),
          (int(land6.start) + LAND_SETTLE, int(zip7.start) - 1, TS_Z),
          (int(land7.start) + LAND_SETTLE, int(fall8.start) - 1, ROOF_Z)]
for a_, b_, top in RAISED:
    perf.contact(a_, b_, floor=top)
landings = [(int(l_.start), int(l_.start) + LAND_SETTLE) for l_ in (land3, land5, land8)]
air = [(a_, b_) for a_, b_, _ in TRAVEL] + landings + [(int(hop_a.start), int(cling_l.start) + 4)] + \
      [(a_ - 2, b_ + 2) for a_, b_, _ in RAISED]
lock_err = perf.ground_lock(int(land3.start), int(land8.start) - 1, skip=air, step=1)   # sidewalks: z=0
perf.contact(int(run4.start), int(settle4.start) + 4, floor=0.0)    # the in-place sprint floats: toes on the street each frame
lock_err = max(lock_err, perf.ground_lock(int(land8.start), int(flop.end), floor=FL8, step=1,
                                          skip=[(int(land8.start) - 2, int(land8.start) + LAND_SETTLE)]))   # the plaza is road level
END = int(flop.start) + 92
sc.frame_end = END
hips = lambda f: perf.bone_world(HIPS, int(f))

# ------------------------------------------------------------------ webs: one line from his hand to a real anchor per zip
webs = fx.WebShots(rig, fx.collection("Webs"))
ZIPS = [("S1", None, zip1, land1, A1), ("S2", shoot2, zip2, land2, A2), ("S3", shoot3, zip3, land3, A3),
        ("S5", shoot5, zip5, land5, A5), ("S6", shoot6, zip6, land6, A6), ("S7", shoot7, zip7, land7, A7),
        ("S8", None, zip8, land8, A8)]
for nm, sh, zc, lc, A in ZIPS:
    W = int(perf.clip_frame(sh, hit_pk)) if sh is not None else int(zc.start)
    webs.shot(f"Web_{nm}", R_HAND, (lambda p: (lambda f: p))(Vector(A)), W - 4, W, int(lc.start) - 3)
    shot.sfx("web_thwip", W - 3)
    shot.sfx("cartwheel_whoosh", int(zc.start) + 4)
    shot.sfx("landing_thud", int(lc.start) + 5)

# ------------------------------------------------------------------ S3 ticker: a light streak racing along it (guides the eye left -> right)
glint = box("TickerGlint", (0.35, 0.05, TK_H * 0.9), TK_C, fx.material("Glint", (1.0, 0.85, 0.45), emit=12.0))
left, right = TK_C.x - TK_W / 2 + 0.4, TK_C.x + TK_W / 2 - 0.4       # camera looks +y: screen-left is -x
gy = TK_C.y + TICK.normal.y * 0.42
f = T3
keys_g = []
for d_ in (34, 26, 19, 14, 10, 8, 7, 6, 6, 6):
    keys_g += [(f, Vector((left, gy, TK_C.z)), "const"), (f + d_, Vector((right, gy, TK_C.z)), "lin")]
    f += d_ + 1
anim.keys(glint, "location", keys_g)
anim.visible(glint, [(1, False), (T3, True), (int(final(tick).end), False)])
for o in [ticker] + list(ticker.children):           # the ticker only exists for its scene
    anim.visible(o, [(1, False), (int(zip3.start) - 2, True), (int(run4.end) + 2, False)])

# ------------------------------------------------------------------ S4 bus stop: the graph lightbox + spiders
bugs_at = T["vo4"] + F(word(4, "bugs") * FPS)
sys_start = bugs_at - 130
bus_seq = city.sign("BusAd", seq0("st_bugs"), BUS_AD_C, BUS_AD_N, BUS_AD_W, emit=1.4, frame="lightbox", seq=(BUG_N, sys_start))
bus_still = city.sign("BusAdStill", seq0("st_bugs"), BUS_AD_C + BUS_AD_N * 0.005, BUS_AD_N, BUS_AD_W, emit=1.4)   # before the sequence starts
anim.visible(bus_seq, [(1, False), (sys_start, True)])
anim.visible(bus_still, [(1, True), (sys_start, False)])
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
    dz = hips(int(shock.start) + 40)
    at_him = Vector((dz.x + rs.uniform(-1.1, 1.1), dz.y + rs.uniform(-1.1, 1.1), 0.0))
    t_him = max(f0 + 20, int(shock.start) + 22 + 2 * k)
    spiders.add([(f0, out_), (f0 + 8, (out_ + drop) / 2 + Vector((0, -0.2, 0.05))), (f0 + 14, drop), (t_him, at_him),
                 (max(t_him + 20, int(shock.end) - 10), at_him + Vector((rs.uniform(-0.6, 0.6), rs.uniform(-0.6, 0.6), 0))), (tn, near),
                 (tn + 18, near + Vector((rs.uniform(-0.4, 0.4), rs.uniform(-0.4, 0.4), 0))),
                 (int(cling.end) + 4, near + Vector((rs.uniform(-0.6, 0.6), rs.uniform(-0.6, 0.6), 0)))], walk_speed=3.0)
shot.sfx("bugs_skitter", bugs_at)

# ------------------------------------------------------------------ S6 the big screen: risks pop on their words, customers leave
tiles = words6
screen = city.sign("TSquare", img("st_quad_0"), SCR_C, SCR_N, SCR_W, emit=1.3, frame="led", offset=SCR_OFF)
for k, f in enumerate(tiles):
    lay = city.sign(f"TSquare{k + 1}", img(f"st_quad_{k + 1}"), SCR_C + SCR_N * 0.01 * (k + 1), SCR_N, SCR_W, emit=1.3,
                    offset=SCR_OFF)
    anim.visible(lay, [(1, False), (f, True)])
    shot.sfx("ui_pop", f)
# billboard catwalk under the big screen (what he lands, walks and moonwalks on); runs past both screen edges
CW_X0, CW_X1 = SCR_C.x - SCR_W / 2 - 2.2, SCR_C.x + SCR_W / 2 + 8.0     # starts at x 18.2: never in the ticker shot
CW_Y0, CW_Y1 = SCREEN.point.y - SCR_OFF - 1.6, SCREEN.point.y
grate = fx.material("Catwalk", (0.12, 0.13, 0.14), rough=0.5, metallic=0.7)
box("Catwalk", (CW_X1 - CW_X0, CW_Y1 - CW_Y0, 0.14), ((CW_X0 + CW_X1) / 2, (CW_Y0 + CW_Y1) / 2, TS_Z - 0.07), grate)
box("CatwalkKick", (CW_X1 - CW_X0, 0.04, 0.12), ((CW_X0 + CW_X1) / 2, CW_Y0 + 0.02, TS_Z + 0.06), grate)
for k in range(5):                                                      # brackets back to the facade
    bx = CW_X0 + 1.0 + k * (CW_X1 - CW_X0 - 2.0) / 4
    box(f"CatwalkBracket{k}", (0.08, CW_Y1 - CW_Y0, 0.08), (bx, (CW_Y0 + CW_Y1) / 2, TS_Z - 0.5), grate)
lv = city.sign("TSquareLeave", seq0("st_leaving"), SCR_C + SCR_N * 0.06, SCR_N, SCR_W, emit=1.3, offset=SCR_OFF,
               seq=(96, LEAVE_AT))
anim.visible(lv, [(1, False), (LEAVE_AT, True)])

# ------------------------------------------------------------------ S7 rooftop screen (two slides), low on the roof
rs1 = city.sign("RoofScreen1", img("roof_competitive"), RS_C, Vector((-1, 0, 0)), 6.2, emit=1.2, frame="led")
rs2 = city.sign("RoofScreen2", img("roof_layer"), RS_C + Vector((-0.01, 0, 0)), Vector((-1, 0, 0)), 6.2, emit=1.2)
anim.visible(rs2, [(1, False), (T8 - 4, True)])
LEG_H = RS_C.z - RS_H / 2 - ROOF_Z
for k, dy in enumerate((-2.2, 2.2)):
    box(f"RoofLeg{k}", (0.15, 0.15, LEG_H + 0.1), (RS_C.x + 0.15, RS_C.y + dy, ROOF_Z + LEG_H / 2), steel)

# ------------------------------------------------------------------ S8/S9 the finale building (v3): floors light on their words,
# money on the roof; he yanks the ground floor (INSPECTION) out and the whole building pancakes
fcoll = fx.collection("Finale")
bld = city.Building("Finale", FIN_C, width=FIN_W, depth=FIN_D, floors=FIN_N, storey=FIN_S, facade_img=img("facade_floor"),
                    coll=fcoll)
for o in fcoll.objects:                              # the building stands in the intersection only for the finale
    if o.type == "MESH" and o.name.endswith("_Body"):
        anim.visible(o, [(1, False), (f8a, True)])
for i, f in enumerate(lit):
    bld.light(i, f, os.path.join(SCR, f"tower_{i}.png"))
    shot.sfx("ui_pop", f)
# the money: cash pallets along the roof's front edge (seen from the street), they pop up on "money"
cash_mat = fx.material("CashSide", (0.22, 0.75, 0.32), rough=0.55, emit=0.5)
band_mat = fx.material("CashBand", (0.85, 0.75, 0.4), rough=0.5)
top = bld.floors[-1]
rr = random.Random(9)
cash = []
for k in range(5):
    w_, h_ = 1.7, 1.1 + 0.35 * (k % 3)
    rest = Vector((FIN_C.x - 4.8 + k * 2.4, FIN_FRONT + 0.9, bld.top + h_ / 2))
    ob = box(f"Cash{k}", (w_, 1.0, h_), rest, cash_mat, fcoll)
    band = box(f"CashBand{k}", (w_ + 0.02, 0.92, 0.12), Vector((0, 0, 0)), band_mat, fcoll)
    band.parent = ob
    ob.parent = top
    ob.location = rest - top.location
    anim.visible(ob, [(1, False), (cash_f - 4 + k, True)])
    anim.visible(band, [(1, False), (cash_f - 4 + k, True)])
    anim.keys(ob, "scale", [(cash_f - 4 + k, Vector((0.01, 0.01, 0.01)), "out"), (cash_f + 4 + k, Vector((1, 1, 1)), "back")])
    cash.append(ob)
shot.sfx("cash_flutter", cash_f)
fx.paper_pour("BillsUp", os.path.join(SCR, "cash_bill.png"), lambda i: Vector((FIN_C.x + rr.uniform(-5, 5), FIN_FRONT + 0.9, bld.top + 1.6)),
              (FIN_C.x + 1.0, FIN_FRONT - 2.0), count=26, start=cash_f + 6, dur=40, spread=(5.0, 1.4), size=(0.3, 0.13),
              arc=(1.0, 2.5), seed=3)
# the yank: both lines on the ground floor's face, taut while he leans back, then he rips it out
ground = bld.floors[0]
G_FACE = lambda dx: (lambda f: ground.matrix_world @ Vector((dx, -FIN_D / 2 - 0.05, -0.4)))
webs.shot("Web_YankL", L_HAND, G_FACE(-FIN_W / 2 + 1.2), Y1 - 34, Y1 - 30, Y1 + 10)
webs.shot("Web_YankR", R_HAND, G_FACE(-FIN_W / 2 + 2.2), Y1 - 34, Y1 - 30, Y1 + 10)
shot.sfx("web_thwip", Y1 - 33)
PULL = Vector((0.14, -1, 0)).normalized()              # out of the front, angled away from him: it shoots past him
dust_mat = bpy.data.materials.new("Dust")
if dust_mat.node_tree is None:
    dust_mat.use_nodes = True
_nt = dust_mat.node_tree
_bs = next(n for n in _nt.nodes if n.type == "BSDF_PRINCIPLED")
_bs.inputs["Base Color"].default_value = (0.55, 0.5, 0.45, 1.0)
_bs.inputs["Roughness"].default_value = 1.0
if hasattr(dust_mat, "surface_render_method"):
    dust_mat.surface_render_method = "BLENDED"
dust = []


def puff(name, centre, frame, size, rise=1.5, life=50, seed=0):
    """A soft dust cloud: blooms out fast, drifts up, thins away."""
    rp = random.Random(seed)
    for k in range(6):
        me = bpy.data.meshes.new(f"{name}{k}")
        b = bmesh.new()
        bmesh.ops.create_icosphere(b, subdivisions=2, radius=1.0)
        b.to_mesh(me)
        b.free()
        for p in me.polygons:
            p.use_smooth = True
        ob = bpy.data.objects.new(f"{name}{k}", me)
        fcoll.objects.link(ob)
        m = dust_mat.copy()
        me.materials.append(m)
        alpha = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Alpha"]
        p0 = Vector(centre) + Vector((rp.uniform(-1, 1) * size, rp.uniform(-0.4, 0.4) * size, 0.2))
        s0, s1_ = size * rp.uniform(0.2, 0.35), size * rp.uniform(0.75, 1.1)
        f0 = int(frame) + rp.randint(0, 4)
        anim.visible(ob, [(1, False), (f0, True), (f0 + life + 2, False)])
        anim.keys(ob, "location", [(f0, p0, "cubic_out"), (f0 + life, p0 + Vector((rp.uniform(-0.6, 0.6), -0.4, rise)), "lin")])
        anim.keys(ob, "scale", [(f0, Vector((s0, s0, s0 * 0.7)), "cubic_out"), (f0 + life, Vector((s1_, s1_, s1_ * 0.7)), "lin")])
        anim.keys(alpha, "default_value", [(f0, 0.0, "out"), (f0 + 5, 0.55, "lin"), (f0 + life, 0.0, "lin")])
        dust.append(ob)


def debris(name, centre, frame, n, spread, seed=0):
    """Chunks of concrete thrown out by an impact (ballistic, tumbling, they stay on the ground)."""
    rd = random.Random(seed)
    mat = fx.material("Concrete", (0.42, 0.4, 0.38), rough=0.9)
    g = 9.81 / FPS ** 2
    for k in range(n):
        s = rd.uniform(0.12, 0.38)
        ob = box(f"{name}{k}", (s, s * rd.uniform(0.6, 1.2), s * rd.uniform(0.5, 1.0)), Vector(centre), mat, fcoll)
        p0 = Vector(centre) + Vector((rd.uniform(-1, 1) * spread, rd.uniform(-0.3, 0.3), rd.uniform(0, 1.0)))
        v = Vector((rd.uniform(-1, 1) * 0.12, -rd.uniform(0.05, 0.2), rd.uniform(0.08, 0.2)))
        f0 = int(frame)
        t_land = (v.z + math.sqrt(v.z ** 2 + 2 * g * max(0.05, p0.z))) / g
        seq = []
        for t in range(0, int(t_land) + 1, 2):
            seq.append((f0 + t, p0 + Vector((v.x * t, v.y * t, v.z * t - 0.5 * g * t * t)), "lin"))
        end = p0 + Vector((v.x * t_land, v.y * t_land, 0))
        end.z = s * 0.3 - 0.08
        seq.append((f0 + int(t_land) + 1, end, "out"))
        seq.append((f0 + int(t_land) + 6, end + Vector((v.x * 3, v.y * 3, 0)), "bez"))
        anim.visible(ob, [(1, False), (f0, True)])
        anim.keys(ob, "location", seq)
        spin = Vector((rd.uniform(-8, 8), rd.uniform(-8, 8), rd.uniform(-8, 8)))
        anim.keys(ob, "rotation_euler", [(f0, Vector((0, 0, 0)), "lin"), (f0 + int(t_land) + 6, spin, "out")])


def pancake(yank, crash, slide=FIN_D + 1.2):
    """The polished collapse. The ground floor is ripped out along the pull (fast, then scraping to a stop); the floors
    above hang one comic beat, shudder, then fall under gravity: each one slams onto the one below, squashes, bulges,
    cracks to a tilt and settles; dust blooms out of every impact, chunks fly; the money on top rides it down."""
    rp = random.Random(4)
    g = 9.81 / FPS ** 2 * 1.3
    h = FIN_S
    p0 = ground.location.copy()
    out = p0 + PULL * slide + Vector((0, 0, -0.2))
    anim.keys(ground, "location", [(yank, p0, "expo_out"), (yank + 8, out, "out"), (yank + 14, out + PULL * 0.3)])
    anim.keys(ground, "rotation_euler", [(yank, Vector((0, 0, 0)), "out"), (yank + 14, Vector((0.04, 0.0, -0.08)))])   # twists away
    puff("DustYank", Vector((p0.x, FIN_FRONT, 0)) + PULL * 1.5, yank + 2, 2.2, rise=0.8, life=40, seed=1)
    SQ = 0.42                                                   # crushed storey height (share of a storey)
    impacts = []
    for i in range(1, FIN_N):
        fl = bld.floors[i]
        p = fl.location.copy()
        rest = Vector((p.x + rp.uniform(-0.25, 0.25), p.y + rp.uniform(-0.3, 0.3), (i - 1) * h * SQ + h * SQ / 2 + 0.02))
        start = int(crash) + (i - 1)                           # the bottom goes first, the rest follow a frame apart
        shud = [(yank + 3 + k * 3, p + Vector((rp.uniform(-0.05, 0.05), 0, rp.uniform(-0.04, 0.02))), "lin")
                for k in range(max(1, (start - yank - 3) // 3))]
        drop = p.z - rest.z
        t_hit = int(math.sqrt(2 * drop / g))
        seq = [(yank, p, "lin")] + shud + [(start, p, "lin")]
        for t in range(2, t_hit, 2):
            seq.append((start + t, p.lerp(rest, 0.0) + Vector((0, 0, -0.5 * g * t * t)) + (rest - p).to_2d().to_3d() * (t / t_hit), "lin"))
        hit_f = start + t_hit
        seq += [(hit_f, rest, "out"), (hit_f + 3, rest + Vector((0, 0, 0.12)), "in"), (hit_f + 6, rest, "bez")]
        anim.keys(fl, "location", seq)
        tilt = Vector((rp.uniform(-0.06, 0.06), rp.uniform(-0.1, 0.1), rp.uniform(-0.08, 0.08)))
        anim.keys(fl, "rotation_euler", [(start, Vector((0, 0, 0)), "in"), (hit_f, tilt * 0.4, "out"), (hit_f + 8, tilt, "bez")])
        anim.keys(fl, "scale", [(hit_f - 1, Vector((1, 1, 1)), "out"), (hit_f + 2, Vector((1.05, 1.06, SQ * 0.85)), "out"),
                                (hit_f + 7, Vector((1.03, 1.04, SQ)), "bez")])
        impacts.append(hit_f)
        puff(f"Dust{i}_", Vector((FIN_C.x, FIN_FRONT - 0.5, rest.z)), hit_f, 2.2 + 0.8 * i, rise=1.5 + i, life=55, seed=10 + i)
        debris(f"Chunk{i}_", Vector((FIN_C.x, FIN_FRONT - 0.3, rest.z + 0.4)), hit_f, 8, FIN_W / 2 - 1.5, seed=20 + i)
    for i, m in enumerate(bld.mix):                            # the lights die as it comes down
        anim.keys(m.inputs[0], "default_value", [(int(crash) + i, 0.85, "lin"), (int(crash) + i + 10, 0.25, "out")])
    return impacts


impacts = pancake(Y1 + 2, C)
shot.sfx("tower_crash", C + 4)
fl = hips(flop.start + 30)
fx.paper_pour("Bills", os.path.join(SCR, "cash_bill.png"), lambda i: Vector((FIN_C.x + rr.uniform(-5, 5), FIN_FRONT + 0.5, FIN_S * 1.4)),
              (FIN_C.x - 1.5, FIN_FRONT - 2.5), count=110, start=impacts[-1] - 2, dur=45, spread=(5.5, 2.0), size=(0.3, 0.13),
              arc=(1.6, 3.2))
fx.paper_pour("BillsOnHim", os.path.join(SCR, "cash_bill.png"), lambda i: Vector((fl.x + rr.uniform(-1.5, 1.5), FIN_FRONT, FIN_S * 1.2)),
              (fl.x, fl.y), count=30, start=int(flop.start) + 4, dur=40, spread=(1.0, 0.7), size=(0.3, 0.13), arc=(1.2, 2.6))
# the last bill lands on his mask
head_f = int(flop.start) + 50
hd = perf.bone_world("mixamorig:Head", head_f)
bill = city.sign("BillOnMask", os.path.join(SCR, "cash_bill.png"), hd + Vector((0, 0, 0.16)), Vector((0, 0, 1)), 0.34,
                 aspect=0.3 / 0.13, offset=0.0, coll=fcoll)
anim.keys(bill, "location", [(head_f - 30, hd + Vector((0.4, -0.3, 2.4)), "lin"), (head_f - 15, hd + Vector((-0.3, 0.2, 1.2)), "lin"),
                             (head_f, hd + Vector((0, 0, 0.16)), "out")])
anim.keys(bill, "rotation_euler", [(head_f - 30, Vector((0.6, 0.3, 0.2))), (head_f - 15, Vector((-0.5, 0.2, 1.2))), (head_f, bill.rotation_euler.copy())])
anim.visible(bill, [(1, False), (head_f - 30, True)])

# one slide at a time: each sign leaves at the cut after its scene (never a second focal point in a later shot)
for ob_, gone in ((bpy.data.objects["Board1"], int(land2.start)), (billboard, int(land3.start)),
                  (bpy.data.objects["BusAd"], int(land5.start)), (bpy.data.objects["BusAdStill"], int(land5.start)),
                  (subway, int(land6.start)), (rs1, f8a), (rs2, f8a)):
    for o in [ob_] + list(ob_.children):
        keyed = anim.fcurve(o, "hide_render") is not None           # already has its own on/off keys: just add the exit
        anim.visible(o, ([] if keyed else [(1, True)]) + [(gone, False)])
for o in fx.collection("Signs").objects:
    if o.name.startswith("TSquare"):
        anim.visible(o, ([] if anim.fcurve(o, "hide_render") is not None else [(1, True)]) + [(int(land7.start), False)])
webs.bake(range(1, END + 1))
for o in fx.collection("Webs").objects:
    if o.type == "MESH":
        o.data.materials[0] = fx.material("Web_Line", (0.95, 0.97, 1.0), rough=0.35, emit=0.9)

# ------------------------------------------------------------------ cameras
cam = fx.CameraRig(lens=28, fstop=4.0)


def at(f, loc, tgt, ease="inout", cut=False):
    cam.at(int(f), loc, tgt, ease, cut=cut)


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


def read_shot(f0, f1, shot_, drift=0.15):
    """Static presenter shot for a read (a slow, tiny push in; the slide never leaves the frame)."""
    loc, tgt, lens = shot_
    cam.lens(f0, round(lens), "const")
    at(f0, loc, tgt, "lin", cut=True)
    at(f1, Vector(loc).lerp(Vector(tgt), drift / max(1.0, (Vector(tgt) - Vector(loc)).length)), tgt, "lin")


cam.cam.data.clip_end = 800.0
CUTS = []                                            # every camera cut, for the cut log (location vs angle)
# S0 establishing aerial, ride the zip
cam.lens(1, 18, "const")
ride(a1, b1 - 1, Vector((7.0, 8.5, 5.0)), lead=8)
# S1 wide from the street: the whole board, him on its top-left corner (the slide is read with him beside it)
read_shot(b1, int(zip2.start) - 1, s1)
# S2 the zip across the street (side-tracking), then the billboard presenter shot from his landing
cam.lens(int(zip2.start), 22, "const")
ride(int(zip2.start), int(land2.start) - 1, Vector((9.0, -2.0, 1.2)), lead=8)
read_shot(int(land2.start), int(zip3.start) - 1, cam2)
# S3 the long zip to the ticker (tracking from the street), then the ticker presenter shot
cam.lens(int(zip3.start), 22, "const")
ride(int(zip3.start), int(land3.start) - 1, Vector((0.0, -11.0, 1.5)), lead=10)
read_shot(int(land3.start), int(run4.start) + 1, cam3)
# S4 the sprint across the street (side-tracking), the ad presenter shot, the bug dance, the leap onto the shelter
cam.lens(int(run4.start) + 2, 24, "const")
ride(int(run4.start) + 2, int(settle4.start) - 1, Vector((-7.5, -1.5, 0.4)), lead=6)
read_shot(int(settle4.start), int(shock.start) + 4, cam4)
dance = hp(int(shock.start) + 30)
fwd_d = Vector((math.sin(math.radians(F4)), -math.cos(math.radians(F4)), 0))
side_d = Z.cross(fwd_d)
cam.lens(int(shock.start) + 5, 24, "const")
dcam = dance + fwd_d * 2.9 + side_d * 1.2 + Vector((0, 0, -0.15))
at(int(shock.start) + 5, dcam, dance + Vector((0, 0, -0.25)), "lin", cut=True)
at(int(hop_a.start) - 1, dcam + fwd_d * 0.2, dance + Vector((0, 0, -0.25)), "lin")
CUTS.append(("bug dance", int(shock.start) + 5))
at(int(hop_a.start), *roof_cam, "lin", cut=True)
at(int(zip5.start) - 1, (roof_cam[0][0] + 0.4, roof_cam[0][1] - 0.2, 3.9), (ROOF_SPOT[0], ROOF_SPOT[1], 2.4), "lin")
# S5 the zip over to the subway (wide pan), then the subway presenter shot
cam.lens(int(zip5.start), 26, "const")
pan(int(zip5.start), int(land5.start) - 1, (POST_C.x - 1.5, POST.point.y + 7.2, 5.0), look=Vector((0, 0, -0.2)))
read_shot(int(land5.start), int(zip6.start) - 1, cam5)
# S6 the zip across the street up to the catwalk (pan), then straight on the screen; hold through the walk + moonwalk
cam.lens(int(zip6.start), 22, "const")
pan(int(zip6.start), int(land6.start) - 1, (14.5, 0.5, 4.5), lead=6)
read_shot(int(land6.start), int(zip7.start) - 1, ts, drift=0.0)
# S7 the zip up to the rooftop: a wide from the avenue (the screen's face, never its back), then the roof presenter shot
cam.lens(int(zip7.start), 20, "const")
pan(int(zip7.start), int(land7.start) - 1, (RS_C.x - 17.0, RS_C.y + 7.0, ROOF_Z + 4.0), lead=6)
read_shot(int(land7.start), int(fall8.start) - 1, cam7)
# S8 the leap + zip down the avenue (tracking), a low hero angle on the landing
cam.lens(f8a, 20, "const")
ride(f8a, f8b - 1, Vector((4.5, -7.0, 3.5)), lead=10)
fs = hp(f8b + 20)
cam.lens(f8b, 22, "const")
at(f8b, (fs.x - 2.2, fs.y - 3.8, 0.6), (fs.x + 0.1, fs.y + 0.4, 0.9), "lin", cut=True)
CUTS.append(("hero landing", f8b))
# the building: wide down the plaza (him + all four floors + the money), slow push in while the floors light
wf0 = int(land8.start) + 24
cam.lens(wf0, round(fin_lens), "const")
at(wf0, fin_loc, fin_tgt, "lin", cut=True)
at(Y1 - 27, Vector(fin_loc).lerp(Vector(fin_tgt), 0.03), fin_tgt, "inout")     # a slow, slight push in while the floors light
# the yank: his face close (in front of him), both lines taut (push in = pressure)
cuy = Y1 - 26
hc = head(Y1 - 10)
fwd_y = Vector((math.sin(math.radians(FB)), -math.cos(math.radians(FB)), 0))
cam.lens(cuy, 40, "const")
cy_loc = hc + fwd_y * 0.7 + Z.cross(fwd_y) * 2.1 + Vector((0, 0, -0.1))     # his left, three-quarter: clear of the building
at(cuy, cy_loc, hc + Vector((0, 0, -0.1)), "lin", cut=True)
at(Y1, cy_loc.lerp(hc, 0.15), hc + Vector((0, 0, -0.1)), "lin")
CUTS.append(("CU yank", cuy))
# the collapse: wide again (pull out = release)
# from front-left at three-quarters: the floor shoots out across the frame past him, he stays in view
col_loc = Vector((FIN_C.x - 12.0, FIN_FRONT - 6.0, 3.2))          # down the cross street's west arm
col_pts = [Vector((x_, y_, z_)) for x_ in (-FIN_W / 2, FIN_W / 2) for y_ in (FIN_FRONT - FIN_D - 1.2, FIN_C.y + FIN_D / 2)
           for z_ in (0.0, FIN_TOP + 1.6)] + [Vector((FX_SPOT[0], FX_SPOT[1], z_)) for z_ in (0.0, 1.9)]
col_tgt, col_lens = fit(col_loc, col_pts, margin=1.05)
cam.lens(Y1 + 1, round(col_lens), "const")
at(Y1 + 1, col_loc, col_tgt, "lin", cut=True)
at(head_f - 35, col_loc + Vector((0.3, -0.5, 0.6)), col_tgt + Vector((0, 0, -1.0)), "lin")
# end: top-down on him, the bill lands on his mask, then a helicopter pull-out over the wreck
cam.lens(head_f - 34, 35, "const")
at(head_f - 34, (fl.x + 0.3, fl.y - 0.6, 2.3), (fl.x, fl.y, 0.2), "lin", cut=True)
at(head_f + 22, (fl.x + 0.3, fl.y - 0.5, 1.9), (fl.x, fl.y, 0.2), "lin")
cam.lens(head_f + 23, 20, "const")
at(head_f + 23, (fl.x + 1.0, fl.y - 6.0, 9.0), (fl.x + 3.0, fl.y + 6.0, 0.0), "lin", cut=True)       # helicopter: up the plaza,
at(END, (FIN_C.x, fl.y - 16.0, 30.0), (FIN_C.x, fl.y + 6.0, 0.0), "in")                                  # over the avenue's middle
# impacts: the camera feels every landing and the collapse
for _n, _sh, _z, lc, _A in ZIPS:
    cam.shake(int(lc.start) + 5, amp=0.04, dur=8)
cam.shake(int(cling_l.start) + 2, amp=0.04, dur=8)
shot.sfx("landing_thud", int(cling_l.start) + 2)
cam.shake(Y1 + 1, amp=0.06, dur=10)
for k, hf in enumerate(impacts):
    cam.shake(hf, amp=0.07 + 0.03 * k, dur=12 + 2 * k, seed=11 + k)
# depth of field per shot (focus = the camera's aim point): deep on reads (him + slide sharp), shallow on close-ups
FSTOPS = [(1, 5.6), (b1, 8.0), (int(zip2.start), 5.6), (int(land2.start), 8.0), (int(zip3.start), 5.6), (int(land3.start), 8.0),
          (int(run4.start) + 2, 4.0), (int(settle4.start), 8.0), (int(shock.start) + 5, 2.8), (int(hop_a.start), 4.0),
          (int(zip5.start), 4.0), (int(land5.start), 8.0), (int(zip6.start), 5.6), (int(land6.start), 8.0), (int(zip7.start), 5.6),
          (int(land7.start), 8.0), (f8a, 5.6), (f8b, 2.8), (wf0, 8.0), (cuy, 1.8), (Y1 + 1, 8.0), (head_f - 34, 2.8),
          (head_f + 23, 8.0)]
for f_, v_ in FSTOPS:
    anim.key(cam.cam.data.dof, "aperture_fstop", int(f_), v_, ease="const")
TALKS = [happy, talk1, talk2, tick, look4, frus] + talks6 + [talk7, show]
office.face_camera(cam.cam, [(int(first(g).start) + 4, int(final(g).end) - 2) for g in TALKS], amount=0.5)
fx.char_lights(rig, cam.cam, key=170.0, rim=340.0)
# open-hand presenting towards each slide as its line starts (the arm on the slide's side)
for f_, board_c, spot, cloc in ((T1 + 4, G_C + WALL_G.normal * 0.6, TOP1, s1[0]), (T2 + 4, BB_C + Vector((0, -0.4, 0)), BB_SPOT, cam2[0]),
                                (T3 + 4, TK_C + TICK.normal * 0.7, TK_SPOT, cam3[0]), (T["vo4"] + 6, BUS_AD_C - Vector((0.4, 0, 0)), BUS_SPOT, cam4[0]),
                                (T5 + 4, POST_C + POST.normal * 0.5, SUB_SPOT, cam5[0]), (T7 + 4, RS_C - Vector((0.4, 0, 0)), RF_SPOT, cam7[0]),
                                (T8 + 6, RS_C - Vector((0.4, 0, 0)), RF_SPOT, cam7[0])):
    office.present(f_, board_c, side=gesture_side(board_c, hips(f_), cloc), hold=26, ramp=8, amount=0.6)
for k, f_ in enumerate(lit):                          # presents each floor as it lights up
    pt = Vector((FIN_C.x, FIN_FRONT - 0.3, FIN_S * (k + 0.5)))
    office.present(f_ - 3, pt, side=gesture_side(pt, hips(f_), fin_loc), hold=14, ramp=6, amount=0.55)
# the lenses act: wide when excited / amazed / shocked, a squint to study or look cool, angled when
# determined or worried, and a blink every few seconds
from pipeline import face
eyes = face.Lenses(bpy.data.objects["MilesMasked"])
for f_, w_ in ((int(land1.start) + 20, dict(Wide=0.75)), (int(shoot2.start), dict(Wide=0.0)),
               (T2, dict(Squint=0.35, Angry=0.15)), (int(shoot3.start), dict(Squint=0.0, Angry=0.0)),
               (T3, dict(Wide=1.0)), (int(run4.start) + 6, dict(Wide=0.2)),
               (int(shock.start) + 3, dict(Wide=1.0)), (int(shock.start) + 50, dict(Wide=0.0, Squint=0.55, Angry=0.35)),
               (int(shock.end) - 4, dict(Squint=0.0, Angry=0.0, Wide=0.6)), (int(cling.start) + 6, dict(Wide=0.7, Sad=0.35)),
               (int(zip5.start), dict(Wide=0.0, Sad=0.0)), (T5, dict(Sad=0.9)), (int(shoot6.start), dict(Sad=0.0)),
               (words6[0], dict(Sad=0.8)), (int(moon.start) + 4, dict(Sad=0.0, Squint=0.35)),
               (int(shoot7.start), dict(Squint=0.0)), (T7, dict(Wide=0.35)), (T8, dict(Wide=0.0, Squint=0.45, Angry=0.3)),
               (f8a, dict(Squint=0.0, Angry=0.0)), (T["vo13"], dict(Angry=0.3)), (cash_f, dict(Angry=0.0, Wide=0.6)),
               (Y1 - 30, dict(Wide=0.0, Angry=1.0, Squint=0.3)), (C, dict(Angry=0.0, Squint=0.0, Wide=1.0)),
               (int(flop.start) + 12, dict(Wide=0.0, Squint=0.85))):
    eyes.set(f_, **w_)
eyes.blinks(1, int(flop.start), every=95, skip=[(Y1 - 34, C + 10)])


# ------------------------------------------------------------------ city life: traffic, pedestrians, pigeons
# Everything is checked against a per-frame cache of the camera and Spidey (life.Guard): nothing pops in or out
# on screen, nothing drives or walks through him or the lens, nothing steps between the lens and him.
from pipeline import life
guard = life.Guard(cam.cam, lambda f: rig.matrix_world @ rig.pose.bones[HIPS].head, (1, END), step=2)
guard.keepout.append((int(zip8.start), END, Vector((FIN_C.x, FIN_FRONT - 3.0, 0)), 15.0))   # the building, its wreck, the bills
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
FIN_BLOCK = int(zip8.start) - 40                     # from here the avenue is his (and then the building's)
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


touch1 = int(land1.start) - 4
ledge_y = WALL_G.point.y + WALL_G.normal.y * 0.6
flock([Vector((x_, ledge_y + rl.uniform(-0.2, 0.25), LEDGE_TOP)) for x_ in (-14.6, -13.4)], touch1, (0.7, 0.7))
flock([Vector((RF_SPOT[0] - 0.4, RF_SPOT[1] - 1.8, ROOF_Z))], int(land7.start) - 6, (-0.6, -0.8))
flock([Vector((FX_SPOT[0] + rl.uniform(-2.5, 1.5), FX_SPOT[1] + rl.uniform(-4.5, -2.0), Z_ROAD)) for _ in range(2)],
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
# review audit data (scripts/check_rules.py): every web travel, every explaining beat, every read's board
v3 = lambda v: [round(float(x), 3) for x in v]
READS = [("mural", talk1, G_C + WALL_G.normal * 0.45, WALL_G.normal, GB_W, GB_H), ("billboard", talk2, BB_C, (0, -1, 0), 9.6, 3.2),
         ("ticker", tick, TK_C + TICK.normal * 0.35, TICK.normal, TK_W, TK_H), ("bus", look4, BUS_AD_C, BUS_AD_N, BUS_AD_W, BUS_AD_W * 9 / 16),
         ("subway", frus, POST_C + POST.normal * 0.12, POST.normal, 3.6, 3.6 * 9 / 16),
         ("screen", talks6[0], SCR_C + SCR_N * SCR_OFF, SCR_N, SCR_W, SCR_H), ("roof", talk7, RS_C, (-1, 0, 0), 6.2, RS_H),
         ("building", show, Vector((FIN_C.x, FIN_FRONT, FIN_TOP / 2)), (0, -1, 0), FIN_W, FIN_TOP)]
json.dump(dict(travel=[(a_, b_, n_) for a_, b_, n_ in TRAVEL if n_ not in ("S4run", "S4hop", "moon")],
               talks=[(int(first(g).start + first(g).blend) + 4, int(final(g).end) - 6, v3(loc)) for gs, loc in AIMS for g in gs],
               reads=[(n_, int(first(g).start + first(g).blend) + 4, int(final(g).end) - 6, v3(bc), v3(nn), w_, h_)
                      for n_, g, bc, nn, w_, h_ in READS],
               webs=[o.name for o in fx.collection("Webs").objects if o.type == "MESH"]),
          open(os.path.join(paths.ROOT, "build", f"{NAME}_audit.json"), "w"))
VO_CUES = {n: T[f"vo{n}"] for n in range(1, 14)}
shot.finish(NAME, exposure=-0.35, samples=24, view="AgX", grade="AgX - Punchy",
            markers=[(f"vo {n}", f) for n, f in VO_CUES.items()] + [
                ("S1 board", T["vo1"]), ("S2 billboard", int(zip2.start)), ("S3 ticker", int(land3.start)),
                ("S4 bus", T["vo4"]), ("S5 subway", T["vo5"]), ("S6 screen", T["vo6"]), ("S7 roof", int(land7.start)),
                ("S8 building", f8a), ("S9 yank", Y1), ("end", END)])
fx.cine_grade(sc)                                     # haze (aerial perspective), bloom, dispersion, vignette
bpy.ops.wm.save_mainfile()
cues = sorted(VO_CUES.items(), key=lambda kv: kv[1])
for (a, fa), (b, fb) in zip(cues, cues[1:]):
    if fa + dur(a) * FPS > fb:
        print(f"VO OVERLAP {a}->{b}: {(fa + dur(a) * FPS - fb) / FPS:.2f}s")
print("CUTS", CUTS)
named = dict(zip1=zip1, land1=land1, happy=happy, talk1=talk1, shoot2=shoot2, zip2=zip2, land2=land2, talk2=talk2, zip3=zip3,
             land3=land3, tick=tick, run4=run4, stop4=stop4, settle4=settle4, look4=look4, shock=shock, hop_a=hop_a, cling_l=cling_l,
             cling=cling, zip5=zip5, land5=land5, frus=frus, zip6=zip6, land6=land6, moon=moon, shoot7=shoot7, zip7=zip7,
             land7=land7, talk7=talk7, fall8=fall8, zip8=zip8, land8=land8, show=show, heave=heave, pull=pull, flop=flop)
print("TIMES", {k: (int(first(v).start), int(final(v).end)) for k, v in named.items()}, "Y1", Y1, "C", C, "impacts", impacts,
      "walks", [(int(w.start), int(w.end)) for w in walks], "words6", words6, "square", round(square_err, 1))
print(f"STREET frames 1-{END} ({END / FPS:.1f}s)  ground-lock {lock_err * 100:.1f} cm  optional clips:",
      {n: have(n) for n in ("MX Moonwalk 1", "MX Terrified", "MX Taunt", "MX Sprint", "MX Happy Hand Gesture")})
