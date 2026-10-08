"""Street part 2 (~2:40, a separate video): why inspection wins (human + agent), and how LiveReview does it.

    S10   why inspect: two identical shops face each other across a street; he gets up from the cash pile, zips to
          the middle; "You don't inspect. Your competitor does." — customers leave you and queue at them
    S10.1 the answer, from the sidewalk: your shop empties, the broken item, the sign flips to CLOSED
    S11   site A, human only: a careful brick storey; bricks pile up faster than the workers can lay them
    S12   site B, agent only: a crane stacks a crooked tower fast; push in on a missing window and a door to
          nowhere; customers look up and run
    S13   site C, human + agent: same speed, square floors; he hangs on a line and stamps every floor (✓ column)
    S14   close-up (masked): three things every team wants, counted on his fingers
    S15   close-up: why humans still matter — common sense
    S16   (2D) the product: tools for your engineers — scripts/05b_street_part2_boards.py fills these frames
    S17   (2D) tools for your agents
    S18   the wreck before sunrise: he webs INSPECTION back in, it locks with a glow, the floors snap up; the sun
          comes up behind it, floors light one by one, two new floors, cash; he lands on the roof
    S19   the rooftop at sunrise: the call to action, a peace sign, the pull-out; the billboard lights up -> demo

Same rules as part 1 (scripts/check_rules.py): web travel = a straight pull, one body angle, no spins; explaining =
upright, facing the camera; him right next to each slide at its LEFT edge; a hang only holding the line by hand.
Captions (lower thirds) are laid over in post from build/street_part2_overlays.json (scripts/06c_street_part2_post.py).

    python3 scripts/03d_street_part2_signs.py v2
    python3 scripts/07c_estimate_vo.py assets/audio/vo_street_part2.md assets/audio/vo_street_part2   # until the take exists
    blender -b build/character.blend --python scripts/04_street_part2.py      # -> build/street_part2.blend
    blender -b build/street_part2.blend --python scripts/check_rules.py -- street_part2
"""
import bpy, bmesh, os, sys, math, random, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mathutils import Vector, Matrix, Quaternion
from pipeline import paths, anim, fx, shot, city, swing, streetkit, life, props
from pipeline.mixamo import Performer, ClipGroup
from pipeline.shot import L_HAND, R_HAND, HIPS
from pipeline.streetkit import first, final, face_to, Z, SHOOT, HANG

FPS = 30
NAME = "street_part2"
sc = bpy.context.scene
ST, ST2 = (os.path.join(paths.ROOT, "assets", d) for d in ("street", "street2"))
SCR = os.path.join(paths.ROOT, "assets", "screens")
img = lambda n: os.path.join(ST2, n + ".png")
seq0 = lambda n, ext="png": os.path.join(ST2, n, f"f_0001.{ext}")
VO = json.load(open(os.path.join(paths.ROOT, "assets", "audio", "vo_street_part2", "lines.json")))
F = lambda x: int(round(x))
UPRIGHT = 30
CALM = ["Talking (2)", "Talking (1)"]            # the two Mixamo talks stay square to the lens

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
for con in (office.ik_phone, office.ik_reach, office.ik_watch):      # unused here; the legacy IK solver weighs every IK on the
    con.mute = True                                                  # chain even at influence 0 (they dragged the hand down)
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


def dome(name, r, mat, coll):
    me = bpy.data.meshes.new(name)
    b = bmesh.new()
    bmesh.ops.create_uvsphere(b, u_segments=16, v_segments=8, radius=r)
    bmesh.ops.delete(b, geom=[v for v in b.verts if v.co.z < -1e-4], context="VERTS")
    b.to_mesh(me)
    b.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
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


def to_bone(ob, arm, bone, offset=(0, 0, 0), rot=(0, 0, 0)):
    """Ride on a bone (at its tail): hard hats, the stamp."""
    ob.parent = arm
    ob.parent_type = "BONE"
    ob.parent_bone = bone
    ob.location = offset
    ob.rotation_euler = rot


# ================================================================== locations
# ---- S10/S10.1 the shop street: the west arm of the cross street, two identical shops facing each other at x -29
SX = -29.0
YS = c.wall((SX, 0.0, 2.0), (0, -1, 0)).point.y          # south facade (faces +y)
YN = c.wall((SX, 0.0, 2.0), (0, 1, 0)).point.y           # north facade (faces -y)
SHOP_W = 5.0
navy = fx.material("ShopFascia", (0.12, 0.16, 0.23), rough=0.6)
awn_mat = fx.material("Awning", (0.75, 0.12, 0.12), rough=0.7)
glass_dark = fx.material("ShopGlassDark", (0.03, 0.04, 0.05), rough=0.08, metallic=0.2)
glass_lit = fx.material("ShopGlassLit", (0.22, 0.17, 0.1), rough=0.1, emit=0.6, emit_color=(1.0, 0.75, 0.45))
shelf_mat = fx.material("Shelf", (0.55, 0.42, 0.3), rough=0.6)
goods = [fx.material(f"Goods{i}", col, rough=0.5) for i, col in enumerate(((0.8, 0.3, 0.2), (0.2, 0.5, 0.8), (0.9, 0.8, 0.3)))]
SHOP = {}
for side, yf, n_ in (("L", YS, 1), ("R", YN, -1)):
    nv = Vector((0, n_, 0))
    front = yf + n_ * 0.35                                   # the shopfront is built a little out from the facade
    box(f"Shop{side}Block", (SHOP_W + 0.4, 0.35, 4.6), (SX, yf + n_ * 0.175, 2.3), navy)
    win = box(f"Shop{side}Window", (SHOP_W - 1.6, 0.05, 2.0), (SX - 0.6 * n_, front + n_ * 0.03, 1.35),
              glass_dark if side == "L" else glass_lit)
    box(f"Shop{side}Door", (1.0, 0.05, 2.3), (SX + 1.9 * n_, front + n_ * 0.03, 1.15), glass_dark)
    awn = box(f"Shop{side}Awning", (SHOP_W, 1.2, 0.08), (SX, front + n_ * 0.6, 2.75), awn_mat)
    awn.rotation_euler = (math.radians(-12) * n_, 0, 0)
    for kk in range(3):                                      # the window display: a shelf and goods
        box(f"Shop{side}Shelf{kk}", (1.0, 0.35, 0.05), (SX - 0.6 * n_ + (kk - 1) * 1.15, front - n_ * 0.25, 0.9), shelf_mat)
        if side == "R" or kk != 1:
            box(f"Shop{side}Goods{kk}", (0.35, 0.25, 0.3), (SX - 0.6 * n_ + (kk - 1) * 1.15, front - n_ * 0.25, 1.08), goods[kk])
    sg = city.sign(f"Shop{side}Sign", img("shopL" if side == "L" else "shopR"), Vector((SX, front, 3.55)), nv, SHOP_W - 0.4,
                   aspect=2400 / 520, emit=0.8, frame="lightbox", offset=0.05)
    SHOP[side] = dict(front=front, n=n_, sign=sg, win=win, door=(SX + 1.9 * n_, front + n_ * 0.25))
closed = city.sign("ShopLClosed", img("shopL_closed"), Vector((SX, SHOP["L"]["front"], 3.55)), Vector((0, 1, 0)), SHOP_W - 0.4,
                   aspect=2400 / 520, emit=0.8, offset=0.06)
# the broken item in YOUR window: a white vase with a crack
vase = box("BrokenItem", (0.3, 0.3, 0.42), (SX - 0.6, SHOP["L"]["front"] - 0.25, 1.14), fx.material("Vase", (0.9, 0.9, 0.88), rough=0.3))
crk = city.sign("BrokenCrack", img("crack"), vase.location + Vector((0, 0.16, 0)), Vector((0, 1, 0)), 0.3, aspect=1.0, offset=0.0, alpha=True)
parent_keep(crk, vase)
# the street banner across the road (the on-screen lines of S10), the LED over the competitor (S10.1)
BAN_C = Vector((SX + 3.4, 0.0, 4.6))                        # just in front of the shops: close enough to read
ban_a = city.sign("BannerA", img("banner_a"), BAN_C, Vector((1, 0, 0)), 9.6, aspect=3000 / 480, emit=0.5, frame="billboard", offset=0.0)
ban_b = city.sign("BannerB", img("banner_b"), BAN_C, Vector((1, 0, 0)), 9.6, aspect=3000 / 480, emit=0.5, offset=0.01)
for kk, yy in enumerate((-5.0, 5.0)):
    box(f"BannerPole{kk}", (0.12, 0.12, 5.6), (BAN_C.x + 0.15, yy, 2.8), steel)
LED_C = Vector((SX, SHOP["R"]["front"], 5.55))
led_a = city.sign("LedA", img("led_a"), LED_C, Vector((0, -1, 0)), 7.0, aspect=3600 / 420, emit=2.0, frame="led", offset=0.05)
led_b = city.sign("LedB", img("led_b"), LED_C, Vector((0, -1, 0)), 7.0, aspect=3600 / 420, emit=2.0, offset=0.06)
zebra = fx.material("Zebra", (0.85, 0.85, 0.82), rough=0.7)
for kk in range(11):                                         # the crosswalk between the shops
    box(f"Zebra{kk}", (2.4, 0.45, 0.012), (SX + 0.2, -5.0 + kk * 1.0, -0.07), zebra)
CP = Vector((-20.8, -2.9))                                   # the cash pile (left foreground)
LAND10 = (SX + 2.0, 0.0)                                     # in the middle, between the shops, facing the camera
FL_ROAD = k.floor_at(*LAND10)
cam10_loc = Vector((-16.6, 0.0, 1.7))
pts10 = [Vector((SX + dx, y_, z_)) for dx in (-2.5, 2.5) for y_ in (YS + 0.4, YN - 0.4) for z_ in (0.0, 4.1)] + \
        [Vector((BAN_C.x, y_, BAN_C.z + dz)) for y_ in (-4.8, 4.8) for dz in (-0.8, 0.8)] + [Vector((CP.x, CP.y, 0.0))]
cam10 = (cam10_loc, *k.fit(cam10_loc, pts10, margin=1.04))
cam101_loc = Vector((SX + 9.0, YS + 2.5, 1.15))             # on your side's sidewalk, your shop filling the left
pts101 = [Vector((SX + 2.2, SHOP["L"]["front"], 3.8)), Vector((SX - 2.6, SHOP["R"]["front"], 6.0)), Vector((SX - 4.0, SHOP["R"]["front"], 0.0)),
          Vector((LAND10[0], LAND10[1], 0.0)), Vector((LAND10[0], LAND10[1], 2.0)), Vector((SX + 2.2, SHOP["L"]["front"], 0.4)),
          Vector((LED_C.x + 3.5, LED_C.y, LED_C.z + 0.5))]
cam101 = (cam101_loc, *k.fit(cam101_loc, pts101, margin=1.05))
print("SHOPS south", round(YS, 2), "north", round(YN, 2), "cam10", round(cam10[2]), "mm  cam101", round(cam101[2]), "mm")

# ---- S11-S15 the construction lot behind the plaza building (open ground; the cameras look south at it)
SITES = {"A": -8.0, "B": 0.0, "C": 8.0}                      # cameras look -y: screen-left is +x
LOT_Y, SIGN_Y, CAM_Y = 72.0, 76.6, 86.0
T_W, T_H = 3.6, 2.3
TOWER = {s: Vector((x - 0.8, LOT_Y, 0.0)) for s, x in SITES.items()}
SIGN_C = {s: Vector((x + 2.6, SIGN_Y, 0.35 + 1.25)) for s, x in SITES.items()}
SW_, SH_ = 4.4, 2.45
SN = Vector((0, 1, 0))
SPOT = {s: (SIGN_C[s].x + SW_ / 2 + 0.45, SIGN_Y + 0.55) for s in SITES}
dirt = fx.material("SiteDirt", (0.32, 0.25, 0.18), rough=0.95)
fence_m = fx.material("SiteFence", (0.16, 0.3, 0.22), rough=0.7)
for s, x in SITES.items():
    box(f"Dirt{s}", (7.4, 9.0, 0.02), (x, LOT_Y + 1.0, 0.01), dirt, csite)
for kk, cx in enumerate((-17.6, 17.6)):                      # the lot's hoarding on both sides (hides the map edge)
    box(f"LotFence{kk}", (0.2, 26.0, 2.6), (cx, 77.0, 1.3), fence_m, csite)
site_signs = {}
for s in SITES:
    n_states = {"A": 2, "B": 3, "C": 2}[s]
    site_signs[s] = [city.sign(f"Site{s}Sign{i}", img(f"site{s}_{i}"), SIGN_C[s], SN, SW_, emit=0.4, frame="lightbox" if i == 0 else None,
                               offset=0.05 + 0.005 * i) for i in range(n_states)]
    for kk, dx in enumerate((-1.4, 1.4)):
        box(f"Site{s}Leg{kk}", (0.1, 0.1, 0.45), (SIGN_C[s].x + dx, SIGN_Y - 0.1, 0.22), steel, csite)
    site_signs[s].append(city.sign(f"Site{s}Blank", img("site_blank"), SIGN_C[s], SN, SW_, emit=0.1, offset=0.08))   # one focal point


def site_cam(s):
    """The same camera for every site (same lot layout, same angle): the whole tower, its sign, him."""
    x = SITES[s]
    top = {"A": 4.4, "B": 6 * T_H + 0.8, "C": 7 * T_H + 0.8}[s]           # same spot and direction; the zoom fits the site
    loc = Vector((x + 0.6, CAM_Y, 2.6))
    pts = [TOWER[s] + Vector((dx * T_W / 2, 0, z_)) for dx in (-1, 1) for z_ in (0.0, top)] + \
          [SIGN_C[s] + Vector((dx * SW_ / 2, 0, dz * SH_ / 2)) for dx in (-1, 1) for dz in (-1, 1)] + \
          [Vector((SPOT[s][0] + 0.4, SPOT[s][1], 0.0)), Vector((SPOT[s][0] + 0.4, SPOT[s][1], 1.9)),
           Vector((TOWER[s].x - T_W / 2 - (3.0 if s == "A" else 0.6), LOT_Y, 0.0))]
    return (loc, *k.fit(loc, pts, margin=1.05))


SITE_CAM = {s: site_cam(s) for s in SITES}
print("SITECAMS", {s: round(v[2]) for s, v in SITE_CAM.items()})
CU_SPOT = (TOWER["C"].x - 0.6, SIGN_Y + 2.2)               # S14/S15: the finished tower right behind him (its sign out of frame)
OFF_SPOT = (0.0, 96.0)                                      # out of every shot (behind the lot cameras)
# ---- S18/S19 part 1's wreck in the intersection, a billboard screen to its right
FIN_C = Vector((0.0, 2.0))
FIN_W, FIN_D, FIN_N, FIN_S = 12.0, 7.0, 6, 2.4
FIN_FRONT = FIN_C.y - FIN_D / 2
FX_SPOT = (FIN_C.x - FIN_W / 2 - 0.8, FIN_FRONT - 1.3)
FL8 = k.floor_at(*FX_SPOT)
TOP6 = 6 * FIN_S
ROOF_SPOT = (FIN_C.x - 1.2, FIN_FRONT + 0.9)
BB2_C = Vector((12.4, 3.0, 6.6))
BB2_W, BB2_H = 7.2, 7.2 * 9 / 16
cam18_loc = Vector((0.5, -17.5, 4.2))                      # high enough to see him over the slid-out floor
pts18 = [Vector((x_, FIN_FRONT, z_)) for x_ in (-FIN_W / 2, FIN_W / 2) for z_ in (0.0, TOP6 + 1.2)] + \
        [BB2_C + Vector((dx * BB2_W / 2, 0, dz * BB2_H / 2)) for dx in (-1, 1) for dz in (-1, 1)] + \
        [Vector((FX_SPOT[0], FX_SPOT[1], 0.0)), Vector((FIN_C.x, FIN_FRONT - FIN_D - 1.5, 0.0))]
cam18 = (cam18_loc, *k.fit(cam18_loc, pts18, margin=1.05))
print("FINALE cam18", round(cam18[2]), "mm")

# ================================================================== performance
T = {}
# ---- S10: flat in the cash pile, up, a line to the banner, lands in the middle between the shops
open0 = perf.then("Fallen Idle", length=40, face=-120, at=(CP.x, CP.y))
f_0 = face_to(CP, LAND10)
rise0 = perf.then("Hard Landing", frm=30, to=64, speed=1.1, blend=16, face=f_0)
shoot0 = k.shoot(f_0)
zip0 = k.zip_(9.0, f_0)
land0 = k.touch(f_0, LAND10)
F10 = face_to(LAND10, cam10[0])
T[1] = int(land0.start) + UPRIGHT
T[2] = T[1] + F((k.dur(1) + 0.3) * FPS)
talk10 = k.talk_until(T[2] + 4, face=F10, clips=CALM)
# ---- S10.1: the same spot, turned to the sidewalk camera
F101 = face_to(LAND10, cam101[0])
talk101 = k.talk_until(T[2] + k.hold(2, 0.7), face=F101, clips=CALM)
# ---- S11 site A (a cut): he stands at the sign's left edge
FA = face_to(SPOT["A"], SITE_CAM["A"][0])
setA = perf.then("Breathing Idle", length=12, face=FA, at=SPOT["A"], in_place=1.0)
T[3] = int(setA.start) + 12
wordf = lambda n, w, nth=0: T[n] + F(k.word(n, w, nth) * FPS)
nodA = perf.then("MX Head Nod Yes", frm=8, length=40, blend=10, face=FA, in_place=1.0)
talkA = k.talk_until(wordf(3, "can") - 6, face=FA, clips=CALM)
shakeA = perf.then("MX Shaking Head No", frm=6, length=48, blend=10, face=FA, in_place=1.0)
holdA = k.talk_until(T[3] + k.hold(3, 0.7), face=FA, clips=CALM)
# ---- S12 site B: he isn't in it (out of every shot)
off12 = perf.then("Breathing Idle", length=k.hold(4, 0.9) + 14, face=0, at=OFF_SPOT, in_place=1.0)
T[4] = int(off12.start) + 12
# ---- S13 site C: hanging on a line beside the newest floor, stamping each one
n13 = k.hold(5, 0.9) + 14
HX, HY = TOWER["C"].x + T_W / 2 + 0.45, LOT_Y + T_W / 2 + 0.25
hang13 = perf.then(HANG, frm=20, to=140, speed=120 / n13, face=180, at=(HX, HY), in_place=1.0)
T[5] = int(hang13.start) + 12
# ---- S14/S15 the close-up in front of the finished tower
FCU = 180.0                                                # faces +y: the close-up camera
cu14 = perf.then("Breathing Idle", length=10, face=FCU, at=CU_SPOT, in_place=1.0)
T[6] = int(cu14.start) + 10
talk14 = k.talk_until(T[6] + k.hold(6, 0.3), face=FCU, clips=CALM)
T[7] = T[6] + F((k.dur(6) + 0.3) * FPS)
shrug15 = perf.then("CMU 111_25 Shrug", frm=10, to=62, blend=10, face=FCU, in_place=1.0)
talk15 = k.talk_until(T[7] + k.hold(7, 0.6), face=FCU, clips=CALM)
# ---- S16/S17 the product (2D frames in post): he is out of every shot
T[8] = T[7] + F((k.dur(7) + 0.6) * FPS)
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
CU_CAM = Vector((CU_SPOT[0], CU_SPOT[1] + 2.0, 1.62))
R_CAM = Vector((ROOF_SPOT[0] + 0.6, ROOF_SPOT[1] - 3.6, TOP6 + 1.55))
AIMS = [([talk10], cam10[0]), ([talk101], cam101[0]), ([talkA, holdA], SITE_CAM["A"][0]), ([talk14, talk15], CU_CAM), ([talk19], R_CAM)]
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
hp = k.hp
A0 = Vector((BAN_C.x, -1.0, BAN_C.z + 0.75))                # the line catches the banner's top
k.web_zip(zip0, land0, A0, lift=1.4, name="S10")
# S13: hanging beside the newest floor; after each landing he swings up to it (a short pendulum arc), stamps it
FLOOR_GAP, N_C = 16, 7
F13_0 = T[5] + F(k.word(5, "agents") * FPS) - 30 - 2 * 16   # floors 0 and 1 are already up when we cut in
LANDS_C = [F13_0 + i * FLOOR_GAP for i in range(N_C)]
hz = lambda i: T_H * (i + 0.5) - 0.15                      # hips beside floor i
h13a, h13b = int(hang13.start), int(hang13.end) - 1


def p13(t):
    f = h13a + t * (h13b - h13a)
    z, x_out = hz(1), 0.0
    for i, lf in enumerate(LANDS_C):
        if i < 2:
            continue
        a_, b_ = lf + 1, lf + 8
        if f >= b_:
            z = hz(i)
        elif f > a_:
            u = (f - a_) / (b_ - a_)
            z0 = hz(i - 1)
            z = z0 + (hz(i) - z0) * (u * u * (3 - 2 * u))
            x_out = 0.45 * math.sin(math.pi * u)            # swings out and back in on the way up
    return Vector((HX + x_out, HY, z))


k.travel(p13, h13a, h13b, name="S13hang")
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
air = [(a_, b_) for a_, b_, _ in k.travels] + [(int(l_.start), int(l_.start) + LAND_SETTLE) for l_ in (land0, land18, land18b)] + \
      [(int(hang13.start) - 2, int(hang13.end) + 2), (int(land18b.start) - 2, END)]
lock_err = 0.0
for a_, b_, fl in [(1, int(zip0.start) - 1, k.floor_at(CP.x, CP.y)), (int(land0.start), int(setA.start) - 1, FL_ROAD),
                   (int(setA.start), int(off12.start) - 1, k.floor_at(*SPOT["A"])), (int(cu14.start), int(off16.start) - 1, k.floor_at(*CU_SPOT)),
                   (int(land18.start), int(zip18b.start) - 1, FL8)]:
    lock_err = max(lock_err, perf.ground_lock(a_, b_, skip=air, step=1, floor=fl))
hips = lambda f: perf.bone_world(HIPS, int(f))

# ------------------------------------------------------------------ props on him: a hard hat + the stamp on site C
yellow = fx.material("HardHat", (0.95, 0.72, 0.05), rough=0.4)
hat = dome("SpideyHat", 0.135, yellow, csite)
to_bone(hat, rig, "mixamorig:Head", offset=(0, -0.02, 0.0))
stamp_ob = box("StampProp", (0.09, 0.09, 0.14), Vector((0, 0, 0)), fx.material("StampWood", (0.45, 0.3, 0.18), rough=0.6), csite)
to_bone(stamp_ob, rig, R_HAND, offset=(0, 0.02, 0.06))
for o in (hat, stamp_ob):
    anim.visible(o, [(1, False), (int(hang13.start), True), (int(hang13.end) + 1, False)])

# ------------------------------------------------------------------ webs
webs = fx.WebShots(rig, fx.collection("Webs"))
for nm, sh, zc, lc, A in (("S10", shoot0, zip0, land0, A0), ("S18roof", shoot18b, zip18b, land18b, A18b)):
    W = int(perf.clip_frame(sh, k.hit_pk))
    webs.shot(f"Web_{nm}", R_HAND, (lambda p: (lambda f: p))(Vector(A)), W - 4, W, int(lc.start) - 3)
    shot.sfx("web_thwip", W - 3)
    shot.sfx("cartwheel_whoosh", int(zc.start) + 4)
    shot.sfx("landing_thud", int(lc.start) + 5)
webs.shot("Web_S18", R_HAND, lambda f: A18, int(zip18.start) - 2, int(zip18.start), int(land18.start) - 3)
shot.sfx("cartwheel_whoosh", int(zip18.start) + 4)
shot.sfx("landing_thud", int(land18.start) + 5)
JIB_C = TOWER["C"] + Vector((T_W / 2 + 0.5, T_W / 2 + 0.3, 7 * T_H + 4.0))     # the crane jib above him
webs.shot("Web_S13", L_HAND, lambda f: JIB_C, int(hang13.start) - 1, int(hang13.start), int(hang13.end))

# ================================================================== S10 / S10.1 action
anim.visible(ban_a, [(1, False), (wordf(1, "you") - 2, True), (wordf(1, "who") - 2, False)])
anim.visible(ban_b, [(1, False), (wordf(1, "who") - 2, True), (T[2] + 2, False)])
anim.visible(led_a, [(1, False), (wordf(2, "customers") - 2, True), (wordf(2, "higher") - 2, False)])
anim.visible(led_b, [(1, False), (wordf(2, "higher") - 2, True)])
# your shop: the sign flickers through S10.1, then flips to CLOSED and the shop goes dark
lsign_mat = SHOP["L"]["sign"].data.materials[0]
lbsdf = next(n for n in lsign_mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
flick = random.Random(3)
CLOSE_F = wordf(2, "higher")
seqk = [(1, 0.8, "const")]
for f_ in range(T[2] - 10, CLOSE_F, 4):
    seqk.append((f_, flick.choice((0.8, 0.8, 0.15, 0.6, 0.05)), "const"))
seqk.append((CLOSE_F, 0.0, "const"))
anim.keys(lbsdf.inputs["Emission Strength"], "default_value", seqk)
anim.visible(closed, [(1, False), (CLOSE_F, True)])
anim.visible(SHOP["L"]["sign"], [(1, True), (CLOSE_F, False)])
shot.sfx("ui_pop", CLOSE_F)
walk = life.WalkKit()
rw = random.Random(31)
LEAVE = wordf(1, "competitor")
QUEUE = lambda i: (SX - 2.6 - 0.75 * i, SHOP["R"]["front"] - 1.0)          # along the north sidewalk, away from the camera
dl = SHOP["L"]["door"]
for i in range(5):                                          # out of your door, across the zebra, into their queue
    w_ = walk.spawn(i % 4, f"Customer{i}")
    w_.route([(dl, 0), ((dl[0] - 0.3, dl[1] + 1.4), 0), ((SX - 0.4 + 0.25 * (i % 2), YN - 2.2), 0), (QUEUE(i + 2), END)],
             LEAVE + i * 16, phase=rw.random(), until=END)
for i in range(2):                                          # already queueing there
    w_ = walk.spawn(i + 1, f"Queued{i}")
    w_.route([((QUEUE(i)[0] + 0.5, QUEUE(i)[1]), 0), (QUEUE(i), END)], 1, phase=rw.random(), until=END)
# the last customer in your shop: the broken item, a look, puts it down, crosses to the end of the queue
w_ = walk.spawn(3, "LastCustomer")
look_p = (SX - 0.6, SHOP["L"]["front"] + 0.55)
item_f = wordf(2, "customers") + 6
w_.route([(dl, 0), (look_p, 70), ((SX - 0.2, YN - 2.2), 0), (QUEUE(8), END)], item_f - 40, phase=0.3, until=END)
w_.face(item_f - 40 + int(((Vector(look_p) - Vector(dl)).length) / w_.speed) + 1, (0, -1, 0))
up_ = vase.location.copy()
anim.keys(vase, "location", [(item_f + 4, up_, "inout"), (item_f + 16, up_ + Vector((0, 0.35, 0.3)), "inout"),
                             (item_f + 44, up_ + Vector((0, 0.35, 0.3)), "inout"), (item_f + 58, up_)])

# ================================================================== S11-S13 the sites
anim.visible(site_signs["A"][1], [(1, False), (wordf(3, "option") - 2, True)])
anim.visible(site_signs["B"][1], [(1, False), (wordf(4, "option") - 2, True)])
anim.visible(site_signs["B"][2], [(1, False), (wordf(4, "most") - 2, True)])
anim.visible(site_signs["C"][1], [(1, False), (wordf(5, "that") - 2, True)])
for s, (a_, b_) in {"A": (int(setA.start) - 1, int(off12.start) - 1), "B": (int(off12.start) - 1, int(hang13.start) - 1),
                    "C": (int(hang13.start) - 1, int(cu14.start) - 1)}.items():
    anim.visible(site_signs[s][-1], [(1, True), (a_, False), (b_, True)])     # blank except during its own scene
for f_ in (wordf(3, "option"), wordf(4, "option"), wordf(4, "most"), wordf(5, "that")):
    shot.sfx("ui_pop", f_)
# ---- site A: one clean brick storey; the workers lay a brick, check it, nod; the pallet pile outgrows the building
brick = fx.material("Brick", (0.58, 0.24, 0.15), rough=0.85)
tA = TOWER["A"]
for kk, (dx, dy, sx_, sy_) in enumerate(((0, T_W / 2, T_W, 0.3), (0, -T_W / 2, T_W, 0.3), (-T_W / 2, 0, 0.3, T_W), (T_W / 2, 0, 0.3, T_W))):
    box(f"WallA{kk}", (sx_, sy_, T_H - 0.25), tA + Vector((dx, dy, (T_H - 0.25) / 2)), brick, csite)
A_IN = T[3] - 40
for kk in range(12):                                        # the top course, one brick at a time
    bx = tA + Vector((-T_W / 2 + 0.3 + kk * 0.27, T_W / 2, T_H - 0.25 + 0.08))
    b_ = box(f"BrickTop{kk}", (0.25, 0.3, 0.14), bx, brick, csite)
    anim.visible(b_, [(1, kk < 2), (A_IN + 30 + kk * 30, True)])
PAL = tA + Vector((-T_W / 2 - 2.1, 0.6, 0.0))              # screen-right of the building (-x)
box("Pallet", (1.3, 1.1, 0.14), PAL + Vector((0, 0, 0.07)), fx.material("PalletWood", (0.5, 0.36, 0.2), rough=0.8), csite)
for kk in range(7):                                         # brick bundles keep dropping in from the top of the frame
    rest = PAL + Vector((0.04 * (kk % 2), -0.03 * (kk % 3), 0.14 + 0.25 + kk * 0.48))
    b_ = box(f"BrickBundle{kk}", (1.15, 0.95, 0.47), rest, brick, csite)
    if kk == 0:
        continue
    land = A_IN + 4 + kk * 30
    anim.visible(b_, [(1, False), (land - 10, True)])
    anim.keys(b_, "location", [(1, rest + Vector((0, 0, 12.0)), "const"), (land - 10, rest + Vector((0, 0, 12.0)), "in"),
                               (land, rest, "out"), (land + 3, rest + Vector((0, 0, 0.05)), "in"), (land + 5, rest)])
    shot.sfx("block_thud", land, gain=0.6)
yellow_hat = fx.material("WorkerHat", (0.95, 0.72, 0.05), rough=0.4)
for i in range(3):                                           # the workers: hard hats, a slow careful loop
    w_ = walk.spawn((i * 2 + 1) % 4, f"Worker{i}")
    pal_p = (PAL.x + 0.9, PAL.y - 0.9 + 0.5 * i)
    wall_p = (tA.x - 1.0 + i * 1.0, tA.y + T_W / 2 + 0.55)
    legs = [(pal_p, 14 + 6 * i)]
    for _ in range(10):
        legs += [(wall_p, 40), (pal_p, 16)]
    w_.route(legs, A_IN - 40 + i * 25, phase=rw.random(), until=int(off12.end) + 4)
    arm_ob = w_.arm
    head_b = next((b.name for b in arm_ob.data.bones if "head" in b.name.lower() and "end" not in b.name.lower() and "top" not in b.name.lower()), None)
    if head_b:
        h_ = dome(f"WorkerHat{i}", 0.14, yellow_hat, csite)
        to_bone(h_, arm_ob, head_b)
        anim.visible(h_, [(1, False), (A_IN - 40 + i * 25, True), (int(off12.end) + 5, False)])
# he follows the pile up with his head: a look target riding up the bundles
look_t = fx.empty("LookPile", PAL + Vector((0, 0, 0.6)), csite, 0.1)
lk = office._look(rig.pose.bones["mixamorig:Head"], look_t, "Look pile")
f_up0, f_up1 = int(nodA.end) + 2, wordf(3, "can") - 8
anim.keys(look_t, "location", [(f_up0, PAL + Vector((0, 0, 0.6)), "inout"), (f_up1, PAL + Vector((0, 0, 3.6)), "inout")])
anim.keys(lk, "influence", [(1, 0.0, "const"), (f_up0 - 6, 0.0, "inout"), (f_up0 + 4, 0.8, "inout"), (f_up1, 0.8, "inout"), (f_up1 + 8, 0.0, "inout")])
# ---- site B / C: the cranes, the floors
concrete = fx.material("Concrete", (0.48, 0.47, 0.45), rough=0.9)
holes = fx.material("Holes", (0.01, 0.01, 0.01), rough=1.0)
crane_y = fx.material("CraneYellow", (0.95, 0.7, 0.05), rough=0.5, metallic=0.3)


def crane(name, tc, top):
    mast_p = tc + Vector((-(T_W / 2 + 1.2), -(T_W / 2 + 0.6), 0))         # behind it, screen-right
    box(f"{name}Mast", (0.45, 0.45, top), mast_p + Vector((0, 0, top / 2)), crane_y, csite)
    pivot = fx.empty(f"{name}Slew", mast_p + Vector((0, 0, top)), csite, 0.3)
    jib = box(f"{name}Jib", (9.0, 0.4, 0.5), mast_p + Vector((3.0, 0, top + 0.25)), crane_y, csite)
    cw = box(f"{name}Counter", (1.4, 0.9, 0.9), mast_p + Vector((-2.0, 0, top - 0.2)), concrete, csite)
    cab = box(f"{name}Cab", (0.9, 0.9, 0.9), mast_p + Vector((-0.6, 0, top - 0.6)), crane_y, csite)
    for o in (jib, cw, cab):
        parent_keep(o, pivot)
    return pivot


def stack(name, tc, n, f_first, gap, mat, crooked=0.0, seed=1):
    """Floors lowered by the crane, one every `gap` frames: a quick drop, a thud. Returns [(floor, land, rest)]."""
    r = random.Random(seed)
    out_ = []
    offs = Vector((0, 0, 0))
    for i in range(n):
        offs = offs + Vector((r.uniform(-1, 1) * crooked, r.uniform(-1, 1) * crooked * 0.6, 0))
        rest = tc + offs + Vector((0, 0, T_H * (i + 0.5)))
        fl = box(f"{name}F{i}", (T_W, T_W, T_H - 0.05), rest, mat, csite)
        rz = r.uniform(-1, 1) * crooked * 0.12
        land = f_first + i * gap
        anim.visible(fl, [(1, False), (land - 14, True)])
        anim.keys(fl, "location", [(land - 14, rest + Vector((0, 0, 7.0)), "in"), (land, rest, "out"),
                                   (land + 3, rest + Vector((0, 0, 0.08)), "in"), (land + 6, rest)])
        anim.keys(fl, "rotation_euler", [(1, Vector((0, 0, rz + 0.6)), "out"), (land, Vector((0, 0, rz)), "bez")])
        out_.append((fl, land, rest))
    return out_


def windows(fl, rest, seed, missing=0.0, hole=None, glass=None, appear=1, landed=1, force=()):
    """Window bays on the two faces the camera sees (+y front, +x side); some missing: dark holes."""
    r = random.Random(seed)
    for side, (nx, ny) in enumerate(((0, 1), (1, 0))):
        for j in range(3):
            u = (j - 1) * 1.1
            pos = rest + Vector((nx * (T_W / 2 + 0.02) + (u if ny else 0), ny * (T_W / 2 + 0.02) + (u if nx else 0), 0.1))
            m = hole if ((side, j) in force or r.random() < missing) else glass
            w = box(f"{fl.name}W{side}{j}", (0.8 if ny else 0.05, 0.05 if ny else 0.8, 1.1), pos, m, csite)
            parent_keep(w, fl, landed)
            anim.visible(w, [(1, False), (appear, True)])


glassB = fx.material("WinGlass", (0.2, 0.28, 0.35), rough=0.1, metallic=0.4)
T4_0 = T[4] - 10                                             # the crane is already going when we cut in
pivB = crane("CraneB", TOWER["B"], 17.0)
floorsB = stack("TowerB", TOWER["B"], 6, T4_0, 14, concrete, crooked=0.35, seed=5)
HOLE_FL, DOOR_FL = 2, 4
for i, (fl, land, rest) in enumerate(floorsB):
    windows(fl, rest, 10 + i, missing=0.3, hole=holes, glass=glassB, appear=land - 14, landed=land + 10,
            force=((0, 1),) if i == HOLE_FL else ())
anim.keys(pivB, "rotation_euler", [(f_, Vector((0, 0, 0.35 * math.sin(f_ / 9.0))), "inout") for f_ in range(T4_0 - 30, T4_0 + 6 * 14 + 30, 8)])
# the door to nowhere: an upper-floor door on the front face, it swings open over the drop
dfl, dland, drest = floorsB[DOOR_FL]
door_piv = fx.empty("DoorHinge", drest + Vector((T_W / 2 - 0.25, T_W / 2 + 0.06, -T_H / 2 + 0.05)), csite, 0.1)
door = box("DoorNowhere", (0.8, 0.06, 1.9), door_piv.location + Vector((-0.4, 0, 0.95)), fx.material("DoorRed", (0.6, 0.12, 0.1), rough=0.5), csite)
parent_keep(door, door_piv)
parent_keep(door_piv, dfl, dland + 10)
anim.visible(door, [(1, False), (dland - 14, True)])
DOOR_F = wordf(4, "break") - 6
anim.keys(door_piv, "rotation_euler", [(1, Vector((0, 0, 0)), "const"), (DOOR_F, Vector((0, 0, 0)), "out"), (DOOR_F + 10, Vector((0, 0, -1.4)), "back")])
shot.sfx("ui_pop", DOOR_F)
wob = fx.empty("TowerBWobble", TOWER["B"], csite, 0.2)
for fl, land, rest in floorsB:
    parent_keep(fl, wob)
WOB_F = T[4] + k.hold(4, 0.2)
anim.keys(wob, "rotation_euler", [(1, Vector((0, 0, 0)), "const"), (WOB_F - 6, Vector((0, 0, 0)), "inout")] +
          [(WOB_F + kk * 6, Vector((0.03 * math.sin(kk * 1.3) * (1 - kk / 9), 0.04 * math.cos(kk * 1.1) * (1 - kk / 9), 0)), "inout")
           for kk in range(10)])
for fl, land, rest in floorsB:
    shot.sfx("block_thud", land, gain=0.8)
# the customers come to look, spot the flaws and run
RUN_F = wordf(4, "notice")
for i in range(4):
    w_ = walk.spawn(i % 4, f"Onlooker{i}")
    st_ = (TOWER["B"].x - 11.0 - i * 0.7, LOT_Y + 6.0 + 0.4 * i)          # they walk in from screen-right after the cut
    look = (TOWER["B"].x - 1.2 + i * 0.9, LOT_Y + T_W / 2 + 1.8 + 0.3 * (i % 2))
    away = (TOWER["B"].x - 18.0, LOT_Y + 9.0 + i)
    walk_n = int((Vector(look) - Vector(st_)).length / (w_.speed * 1.5))
    go = T[4] + 2 + i * 6
    w_.route([(st_, 0), (look, max(10, RUN_F + 3 * i - (go + walk_n))), (away, 0)], go, phase=rw.random(), pace=[1.5, 2.4])
# ---- site C: square floors at the same speed; every one gets a green stamp as he reaches it
blueglass = fx.material("BlueFloor", (0.12, 0.33, 0.78), rough=0.35, metallic=0.2)
glassC = fx.material("WinGlassC", (0.65, 0.82, 0.95), rough=0.08, metallic=0.3, emit=0.4)
pivC = crane("CraneC", TOWER["C"], 19.5)
floorsC = stack("TowerC", TOWER["C"], N_C, F13_0, FLOOR_GAP, blueglass, crooked=0.0, seed=7)
for i, (fl, land, rest) in enumerate(floorsC):
    windows(fl, rest, 30 + i, missing=0.0, hole=glassC, glass=glassC, appear=land - 14, landed=land + 10)
    stf = land + 9 if i >= 2 else int(hang13.start)          # floors 0-1 were stamped before we cut in
    st_ = city.sign(f"StampC{i}", img("stamp_ok"), rest + Vector((T_W / 2 - 0.5, T_W / 2 + 0.06, 0.2)), SN, 0.8, aspect=1.0,
                    offset=0.0, alpha=True, emit=0.3, coll=csite)
    parent_keep(st_, fl, land + 10)
    anim.visible(st_, [(1, False), (stf, True)])
    anim.keys(st_, "scale", [(stf, Vector((2.2, 2.2, 2.2)), "out"), (stf + 5, Vector((1, 1, 1)), "back")])
    if i >= 2:
        shot.sfx("block_thud", land)
        shot.sfx("ui_pop", stf)
        office.present(stf - 4, rest + Vector((T_W / 2 - 0.5, T_W / 2 + 0.1, 0.2)), side="R", hold=3, ramp=4, amount=0.9)
anim.keys(pivC, "rotation_euler", [(f_, Vector((0, 0, 0.3 * math.sin(f_ / 8.0))), "inout") for f_ in range(F13_0 - 40, F13_0 + N_C * FLOOR_GAP + 20, 8)])
COME_F = wordf(5, "that")
for i in range(5):                                           # the customers come back: a queue at the tower's base
    w_ = walk.spawn((i + 2) % 4, f"Returner{i}")
    st_ = (TOWER["C"].x - 9.0 - 0.6 * i, LOT_Y + 7.0)
    q = (TOWER["C"].x - 1.4 - 0.7 * i, LOT_Y + T_W / 2 + 1.0)
    w_.route([(st_, 0), (q, END)], COME_F - 50 + i * 8, phase=rw.random(), until=int(off16.start) + 2)

# ================================================================== S14 / S15 / S19 the hand: fingers + arm (IK)
FING = ("Index", "Middle", "Ring", "Pinky")


def finger_pose(open_=(), spread=0.0, thumb_in=True):
    """Bone -> quaternion: curled fingers (+X curls) except `open_`; thumb tucked."""
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


POSES = {"one": finger_pose(("Index",)), "two": finger_pose(("Index", "Middle")), "three": finger_pose(("Index", "Middle", "Ring")),
         "point": finger_pose(("Index",)), "fist": finger_pose(()), "flat": finger_pose(FING, thumb_in=False),
         "peace": finger_pose(("Index", "Middle"), spread=9.0)}
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


w6 = lambda w, nth=0: wordf(6, w, nth)
w7 = lambda w, nth=0: wordf(7, w, nth)
PEACE = wordf(11, "sign")
SEQ = [(w6("headcount") - 6, "flat"), (w6("headcount") - 2, "one"), (w6("code") - 2, "two"), (w6("better") - 2, "three"),
       (w6("only") - 4, "three"), (w6("only"), "fist"), (w6("human") - 2, "point"), (w6("stay") + 10, "point"), (w6("stay") + 18, "flat"),
       (w7("why") + 40, "flat"), (w7("why") + 46, "point"), (w7("cuz") - 2, "point"), (w7("ai") + 4, "flat"), (w7("human") - 4, "flat"),
       (PEACE - 8, "flat"), (PEACE - 2, "peace"), (END - 2, "peace")]
for f_, p_ in SEQ:
    key_pose(f_, p_)
if hasattr(f_act, "slots") and f_act.slots and not ad.action_slot:
    ad.action_slot = f_act.slots[0]
ad.action = keep_action
fin_tr = ad.nla_tracks.new()
fin_tr.name = "ZZ Finger poses"
for a_, b_ in ((T[6] - 4, T[8] - 4), (PEACE - 14, END)):
    st = fin_tr.strips.new(f"Fingers{a_}", int(a_), f_act)
    if hasattr(st, "action_slot") and f_act.slots:
        st.action_slot = f_act.slots[0]
    st.action_frame_start, st.action_frame_end = a_, b_
    st.frame_start, st.frame_end = a_, b_
    st.blend_type = "REPLACE"
    st.use_auto_blend = False
    st.extrapolation = "NOTHING"
    st.use_animated_influence = True                    # (an API-made strip otherwise evaluates at influence 0)
    for f_, v_ in ((a_, 0.0), (a_ + 6, 1.0), (b_ - 6, 1.0), (b_, 0.0)):
        st.influence = v_
        st.keyframe_insert("influence", frame=int(f_))
cuh = lambda f: perf.bone_world("mixamorig:Spine2", f)
HD = lambda f: perf.bone_world("mixamorig:Head", f)
fwd = Vector((0, 1, 0))                                      # he faces +y (the close-up camera)
CHEST = lambda f: HD(f) + fwd * 0.34 + Vector((0.2, 0, -0.16))           # beside his face, his own (right) side
office.present(w6("headcount") - 10, CHEST(w6("headcount")), side="R", hold=w6("only") - w6("headcount") + 4, ramp=8, amount=0.95)
office.present(w6("human") - 6, CU_CAM, side="R", hold=w6("stay") - w6("human") + 6, ramp=7, amount=0.8)
office.present(w7("why") + 40, HD(w7("why") + 40) + fwd * 0.12 + Vector((0, 0, -0.1)), side="R", hold=16, ramp=6, amount=1.0)   # chin
office.present(w7("cuz") - 6, HD(w7("cuz")) + Vector((-0.11, 0.04, 0.05)), side="R", hold=12, ramp=5, amount=1.0)              # temple
office.present(w7("human") - 8, cuh(w7("human")) + fwd * 0.16 + Vector((0.05, 0, 0.05)), side="R", hold=26, ramp=7, amount=1.0)    # chest


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
# the lock: INSPECTION's label flares as it seats; the floors above snap back up on top of it
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
for i in range(1, 4):                                       # after the line: the floors light up one by one, bottom first
    lf = SUNRISE + 20 + i * 12
    anim.keys(bld.mix[i].inputs[0], "default_value", [(lf, 0.15, "lin"), (lf + 8, 0.9, "out")])
    shot.sfx("ui_pop", lf)
NEW = [(4, SUNRISE + 80), (5, SUNRISE + 98)]
for i, f_ in NEW:                                           # two new floors land on top
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
# the cash pile he lies in at the start of S10
fx.paper_pour("BillsPile", os.path.join(SCR, "cash_bill.png"), lambda i: Vector((CP.x + rr.uniform(-1, 1), CP.y + rr.uniform(-1, 1), 2.0)),
              (CP.x, CP.y), count=70, start=-70, dur=30, spread=(1.6, 1.2), size=(0.3, 0.13), arc=(0.3, 0.8))
for kk in range(3):
    box(f"CashPile{kk}", (0.9, 0.5, 0.3), Vector((CP.x - 1.2 + kk * 0.9, CP.y - 1.3 + 0.2 * kk, 0.07)), cash_mat, signs).rotation_euler = (0, 0, 0.4 * kk)
# the billboard screen to the right of the site: dark until the very end, then the LiveReview demo
bb_dark = city.sign("BB2Dark", img("site_blank"), BB2_C, Vector((0, -1, 0)), BB2_W, emit=0.0, frame="led", offset=0.0)
bb_dark.data.materials[0] = fx.material("BB2Off", (0.02, 0.02, 0.03), rough=0.3)
BB_ON = DEMO_CUT - 45
demo = city.sign("BB2Demo", seq0("demo", "jpg"), BB2_C, Vector((0, -1, 0)), BB2_W, emit=1.4, offset=0.01, seq=(180, BB_ON))
anim.visible(demo, [(1, False), (BB_ON, True)])
for o in (bb_dark,) + tuple(bb_dark.children):
    anim.visible(o, [(1, False), (S18_CUT, True)])
for kk, dx in enumerate((-2.4, 2.4)):
    pole = box(f"BB2Pole{kk}", (0.3, 0.3, BB2_C.z - BB2_H / 2 + 0.2), (BB2_C.x + dx, BB2_C.y + 0.4, (BB2_C.z - BB2_H / 2) / 2), steel)
    anim.visible(pole, [(1, False), (S18_CUT, True)])
shot.sfx("ui_pop", BB_ON)
# the sky: golden hour through S15; before sunrise at the S18 cut; the sun comes up behind the building; full sunrise in S19
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
    lamp_el = max(L["elev"], 7.0)                          # the lamp stays above the horizon (a pre-dawn sky fill)
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
k.read_shot(1, T[2] - 1, cam10, drift=0.2)                  # S10: head-on from the middle of the road
k.read_shot(T[2], int(setA.start) - 1, cam101, drift=0.1)   # S10.1: from the sidewalk, at an angle
k.read_shot(int(setA.start), int(off12.start) - 1, SITE_CAM["A"], drift=0.15)
# S12: wide, push in on the missing window then the door to nowhere, back wide as the customers run
bw = SITE_CAM["B"]
hole_p = floorsB[HOLE_FL][2] + Vector((0, T_W / 2, 0.1))
door_p = floorsB[DOOR_FL][2] + Vector((T_W / 2 - 0.6, T_W / 2, 0.0))
SUB = wordf(4, "subtle")
cam.lens(int(off12.start), round(bw[2]), "const")
k.at(int(off12.start), bw[0], bw[1], "lin", cut=True)
k.at(SUB - 2, bw[0], bw[1], "inout")
cam.lens(SUB - 2, round(bw[2]), "inout")
cam.lens(SUB + 22, 45, "inout")
k.at(SUB + 22, hole_p + Vector((1.5, 7.5, 1.0)), hole_p, "inout")
k.at(DOOR_F - 4, hole_p + Vector((1.3, 7.2, 1.0)), hole_p, "inout")
k.at(DOOR_F + 14, door_p + Vector((1.5, 7.5, 0.6)), door_p, "inout")
cam.lens(RUN_F - 6, 45, "const")
k.at(RUN_F - 6, door_p + Vector((1.5, 7.4, 0.6)), door_p, "lin")
cam.lens(RUN_F - 5, round(bw[2]), "const")
k.at(RUN_F - 5, bw[0], bw[1], "lin", cut=True)
k.at(int(hang13.start) - 1, bw[0] + Vector((0, -0.3, 0)), bw[1], "lin")
CUTS.append(("B back wide", RUN_F - 5))
k.read_shot(int(hang13.start), int(cu14.start) - 1, SITE_CAM["C"], drift=0.1)
# S14 / S15: the close-up (head and shoulders; S15 a little tighter); the tower soft behind him
cu_t = lambda f: HD(f) + Vector((0, 0, -0.04))
cam.lens(int(cu14.start), 55, "const")
cam.lens(T[7] - 1, 55, "inout")
cam.lens(T[7] + 20, 60, "inout")
cu_pts = {f: cu_t(f) for f in range(int(cu14.start) - 8, T[8] + 9)}
cu_sm = lambda f: sum((cu_pts[q] for q in range(f - 8, f + 9)), Vector()) / 17          # follows his head, smoothly
for f in range(int(cu14.start), T[8], 3):
    push = min(1.0, max(0.0, (f - T[7]) / 20.0)) * 0.25
    k.at(f, CU_CAM + Vector((0, -push, 0)), cu_sm(f), "lin", cut=(f == int(cu14.start)))
CUTS.append(("close-up", int(cu14.start)))
# S16/S17: 2D (post) — the camera parks on the lot
k.at(T[8], SITE_CAM["C"][0], SITE_CAM["C"][1], "lin", cut=True)
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
for f_ in (int(land0.start) + 5, int(land18.start) + 5, int(land18b.start) + 5, HOLD_F):
    cam.shake(f_, amp=0.04, dur=8)
for i, f_ in NEW:
    cam.shake(f_, amp=0.04, dur=8)
FSTOPS = [(1, 8.0), (T[2], 8.0), (int(setA.start), 8.0), (int(off12.start), 8.0), (SUB + 22, 4.0), (RUN_F - 5, 8.0), (int(hang13.start), 8.0),
          (int(cu14.start), 2.0), (T[8], 8.0), (S18_CUT, 8.0), (int(land18b.start) + 41, 4.0), (PEACE + 7, 8.0), (DEMO_CUT, 8.0)]
for f_, v_ in sorted(FSTOPS):
    anim.key(cam.cam.data.dof, "aperture_fstop", int(f_), v_, ease="const")
TALKS = [talk10, talk101, talkA, holdA, talk19]
office.face_camera(cam.cam, [(int(first(g).start) + 4, int(final(g).end) - 2) for g in TALKS] + [(int(cu14.start), T[8] - 4)], amount=0.55)
office.nod(w6("stay"), depth=0.6)
office.nod(w7("cuz") + 6, depth=-0.4)
for kk in range(3):                                          # a light head shake on "doesn't make more great products"
    f_ = w7("doesn") + kk * 7
    anim.keys(office.cam_eye, "location", [(f_, 0.0, "inout"), (f_ + 3, 0.35 * (-1) ** kk, "inout"), (f_ + 7, 0.0, "inout")], index=0)
anim.keys(office.cam_eye, "location", [(T[2] - 14, 0.0, "inout"), (T[2] - 6, 0.5, "inout"), (T[2] + 2, 0.0, "inout")], index=0)   # the head tilt (S10)
fx.char_lights(rig, cam.cam, key=170.0, rim=340.0)
# he looks at your shop, then theirs (S10)
look_s = fx.empty("LookShops", (SX, SHOP["L"]["front"], 2.0), signs, 0.1)
lks = office._look(rig.pose.bones["mixamorig:Head"], look_s, "Look shops")
fL, fR = wordf(1, "without"), wordf(1, "competitor")
anim.keys(look_s, "location", [(fL - 6, Vector((SX, SHOP["L"]["front"], 2.0)), "const"), (fR - 4, Vector((SX, SHOP["L"]["front"], 2.0)), "inout"),
                               (fR + 6, Vector((SX, SHOP["R"]["front"], 2.0)), "inout")])
anim.keys(lks, "influence", [(1, 0.0, "const"), (fL - 6, 0.0, "inout"), (fL + 2, 0.75, "inout"), (wordf(1, "who") - 6, 0.75, "inout"),
                             (wordf(1, "who") + 2, 0.0, "inout")])
# thumb over the shoulder at the queue (S10.1, "Easy"); presenting the site A sign
qp = Vector((SX - 1.5, SHOP["R"]["front"] - 1.0, 1.4))
office.present(T[2] + 2, qp, side=k.gesture_side(qp, hips(T[2]), cam101[0]), hold=30, ramp=7, amount=0.7)
office.present(T[3] + 6, SIGN_C["A"] + Vector((0, 0.4, 0)), side=k.gesture_side(SIGN_C["A"], hips(T[3]), SITE_CAM["A"][0]), hold=24, ramp=8, amount=0.6)
from pipeline import face
eyes = face.Lenses(bpy.data.objects["MilesMasked"])
for f_, w_ in ((1, dict(Squint=0.85)), (int(rise0.start) + 10, dict(Squint=0.0, Wide=0.4)), (T[1], dict(Wide=0.0, Squint=0.25)),
               (wordf(1, "who"), dict(Squint=0.0, Wide=0.7)), (T[2], dict(Wide=0.3)), (wordf(2, "higher"), dict(Wide=0.0, Angry=0.25)),
               (T[3], dict(Angry=0.0, Squint=0.3)), (wordf(3, "can"), dict(Squint=0.0, Sad=0.6)), (T[5], dict(Sad=0.0, Squint=0.4)),
               (T[6], dict(Squint=0.0, Wide=0.45)), (w6("only"), dict(Wide=0.0, Squint=0.35, Angry=0.3)), (w6("stay"), dict(Squint=0.0, Angry=0.0, Wide=0.3)),
               (T[7], dict(Wide=0.0, Sad=0.3)), (w7("cuz"), dict(Sad=0.0, Wide=1.0)), (w7("doesn"), dict(Wide=0.0, Angry=0.35)),
               (w7("human"), dict(Angry=0.0, Squint=0.3)), (S18_CUT, dict(Squint=0.0, Angry=0.4)), (HOLD_F, dict(Angry=0.0, Wide=0.8)),
               (T[11], dict(Wide=0.3)), (PEACE, dict(Wide=0.0, Squint=0.45))):
    eyes.set(f_, **w_)
eyes.blinks(1, END, every=95)
webs.bake(range(1, END + 1))
for o in fx.collection("Webs").objects:
    if o.type == "MESH":
        o.data.materials[0] = fx.material("Web_Line", (0.95, 0.97, 1.0), rough=0.35, emit=0.9)

# ================================================================== captions (laid over in post) + the 2D product frames
OVER = [(w6("headcount") - 2, T[7] - 6, "Same headcount.", 0), (w6("code") - 2, T[7] - 6, "More code.", 1),
        (w6("better") - 2, T[7] - 6, "Better product.", 2), (w7("not") - 2, T[8] - 2, "Common sense isn't in the **training data.**", 0),
        (T[10], HOLD_F - 4, "Let agents scale. **You do the judging.**", 0), (HOLD_F, SUNRISE + 60, "Inspection **holds it all up.**", 0),
        (wordf(11, "livereview") - 2, PEACE + 60, "LiveReview keeps you competitive: **the most efficient way for humans and AI to work together.**", 0),
        (DEMO_CUT, END, "hexmos.com/livereview", 0)]
w8 = lambda w: wordf(8, w)
w9 = lambda w: wordf(9, w)
json.dump(dict(fps=FPS, end=END, captions=[dict(f0=a_, f1=b_, text=t_, row=r_) for a_, b_, t_, r_ in OVER],
               boards=dict(s16=[T[8], T[9] - 1], s17=[T[9], S18_CUT - 1],
                           s16_title=w8("attention"), s16_items=[w8("issues"), w8("slide"), w8("quick"), w8("conversations"), w8("livi")],
                           s17_title=w9("agents"), s17_items=[w9("rules"), w9("integrations"), w9("mcp")])),
          open(os.path.join(paths.ROOT, "build", "street_part2_overlays.json"), "w"), indent=1)

# ------------------------------------------------------------------ parked cars (none on the shop street)
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
READS = [("siteA", talkA, SIGN_C["A"], SN, SW_, SH_)]
json.dump(dict(travel=[(a_, b_, n_) for a_, b_, n_ in k.travels if n_ != "S13hang"],
               talks=[(int(first(g).start + first(g).blend) + 4, int(final(g).end) - 12, v3(loc)) for gs, loc in AIMS for g in gs],
               reads=[(n_, int(first(g).start + first(g).blend) + 4, int(final(g).end) - 6, v3(bc), v3(nn), w_, h_)
                      for n_, g, bc, nn, w_, h_ in READS],
               webs=[o.name for o in fx.collection("Webs").objects if o.type == "MESH"]),
          open(os.path.join(paths.ROOT, "build", "street_part2_audit.json"), "w"))
VO_CUES = {n: T[n] for n in range(1, 12)}
shot.finish(NAME, exposure=-0.35, samples=24, view="AgX", grade="AgX - Punchy",
            markers=[(f"vo {n}", f) for n, f in VO_CUES.items()] + [
                ("S10 shops", T[1]), ("S10.1 answer", T[2]), ("S11 human", T[3]), ("S12 agent", T[4]), ("S13 both", T[5]),
                ("S14 close-up", T[6]), ("S15 common sense", T[7]), ("S16 engineers (2D)", T[8]), ("S17 agents (2D)", T[9]),
                ("S18 rebuild", S18_CUT), ("S19 call to action", T[11]), ("demo", DEMO_CUT), ("end", END)])
fx.cine_grade(sc)
bpy.ops.wm.save_mainfile()
cues = sorted(VO_CUES.items(), key=lambda kv: kv[1])
for (a, fa), (b, fb) in zip(cues, cues[1:]):
    if fa + k.dur(a) * FPS > fb:
        print(f"VO OVERLAP {a}->{b}: {(fa + k.dur(a) * FPS - fb) / FPS:.2f}s")
print("CUTS", CUTS)
print(f"STREET2 frames 1-{END} ({END / FPS:.1f}s)  ground-lock {lock_err * 100:.1f} cm  square {square_err:.1f}")
