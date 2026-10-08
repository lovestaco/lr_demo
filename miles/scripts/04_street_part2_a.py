"""Street part 2a (S10-S15, ~75 s): why inspection wins (human + agent). Part 2 is split in two so each half renders
and reviews faster; part 2b (S16-S19, the product boards, the rebuild, the call to action) stays in 04_street_part2.py.

    S10   one building, two shops side by side (yours on the left: "Ships without inspection"; theirs on the right:
          "Inspects every change"), one board over both. He gets up from the cash pile and zips in beside the board;
          "You don't inspect. Your competitor does." — your customers walk out and queue next door
    S10.1 the answer, same building: your shop empties, the last customer puts the broken item down and joins their
          queue, your sign flickers and flips to CLOSED
    S11   the lot, sites A and B side by side (one wide shot): site A, human only — a neat little brick building, one
          storey; bricks pile up faster than the workers can lay them
    S12   site B, agent only, same shot: a crane stacks a crooked tower fast; push in on a missing window and a door to
          nowhere; customers look up and run
    S13   site C, human + agent (its own shot): same speed, square floors; he hangs on a line and stamps every floor;
          on "that team beats..." the camera pulls back to all three sites side by side
    S14   close-up (masked): three things every team wants, counted on his fingers
    S15   close-up: why humans still matter — common sense

Same rules as part 1 (scripts/check_rules.py). Captions (S14/S15 lower thirds) are laid over in post from
build/street_part2_a_overlays.json (scripts/06c_street_part2_post.py ... street_part2_a).

    python3 scripts/03d_street_part2_signs.py v2 && python3 scripts/03d_street_part2_signs.py v2a
    python3 scripts/07b_split_take.py --lines assets/audio/vo_street_part2/takes --script assets/audio/vo_street_part2.md --out assets/audio/vo_street_part2
    blender -b build/character.blend --python scripts/04_street_part2_a.py      # -> build/street_part2_a.blend
    blender -b build/street_part2_a.blend --python scripts/check_rules.py -- street_part2_a
"""
import bpy, bmesh, os, sys, math, random, json, itertools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mathutils import Vector, Quaternion, Matrix
from pipeline import paths, anim, fx, shot, city, streetkit, life, props, crew
from pipeline.mixamo import Performer
from pipeline.shot import L_HAND, R_HAND, HIPS
from pipeline.streetkit import first, final, face_to, SHOOT

FPS = 30
NAME = "street_part2_a"
sc = bpy.context.scene
ST2 = os.path.join(paths.ROOT, "assets", "street2")
SCR = os.path.join(paths.ROOT, "assets", "screens")
img = lambda n: os.path.join(ST2, n + ".png")
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
# the plaza building behind the lot filled every site shot with a beige wall: gone (the city skyline shows instead)
for o in c.coll.all_objects:
    if o.type == "MESH":
        bb = [o.matrix_world @ Vector(v) for v in o.bound_box]
        if min(p.x for p in bb) > -14 and max(p.x for p in bb) < 14 and min(p.y for p in bb) > 54 and max(p.y for p in bb) < 65:
            o.hide_render = o.hide_viewport = True
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


def brick_mat(name, along):
    """Procedural brick (red, light mortar) in metres on a wall running along `along` ('x' or 'y')."""
    m = fx.material(name, (0.5, 0.2, 0.12), rough=0.85)
    nt = m.node_tree
    bs = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    com = nt.nodes.new("ShaderNodeCombineXYZ")
    br = nt.nodes.new("ShaderNodeTexBrick")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    nt.links.new(sep.outputs["X" if along == "x" else "Y"], com.inputs["X"])
    nt.links.new(sep.outputs["Z"], com.inputs["Y"])
    nt.links.new(com.outputs[0], br.inputs["Vector"])
    br.inputs["Color1"].default_value = (0.42, 0.13, 0.07, 1)
    br.inputs["Color2"].default_value = (0.58, 0.22, 0.12, 1)
    br.inputs["Mortar"].default_value = (0.72, 0.68, 0.6, 1)
    br.inputs["Scale"].default_value = 1.6                   # a brick ~0.31 m x 0.16 m: readable from the wide
    br.inputs["Mortar Size"].default_value = 0.02
    nt.links.new(br.outputs["Color"], bs.inputs["Base Color"])
    return m


cash_mat = fx.material("CashSide", (0.22, 0.75, 0.32), rough=0.55, emit=0.5)
PED = itertools.count()
walk = life.WalkKit()
spawn = lambda name: walk.spawn(next(PED), name)            # every walker its own outfit
rw = random.Random(31)

# ================================================================== locations
# ---- S10/S10.1 the shop building: the south facade of the west arm (faces +y); the camera looks -y at it from the north
# sidewalk, so screen-left is +x: your shop on the left, theirs on the right, one board across both
SX = -29.0
YS = c.wall((SX, 0.0, 2.0), (0, -1, 0)).point.y
YN = c.wall((SX, 0.0, 2.0), (0, 1, 0)).point.y
SHOP_W = 5.0
FRONT = YS + 0.35                                           # the shopfronts are built a little out from the facade
SHOPX = {"L": SX + 2.75, "R": SX - 2.75}
navy = fx.material("ShopFascia", (0.12, 0.16, 0.23), rough=0.6)
pil_m = fx.material("ShopPilaster", (0.2, 0.22, 0.26), rough=0.6)
awn_mat = {"L": fx.material("AwningL", (0.75, 0.12, 0.12), rough=0.7), "R": fx.material("AwningR", (0.75, 0.12, 0.12), rough=0.7)}
glass_dark = fx.material("ShopGlassDark", (0.03, 0.04, 0.05), rough=0.08, metallic=0.2)
glass_lit = fx.material("ShopGlassLit", (0.22, 0.17, 0.1), rough=0.1, emit=0.6, emit_color=(1.0, 0.75, 0.45))
table_m = fx.material("Shelf", (0.55, 0.42, 0.3), rough=0.6)
goods = [fx.material(f"Goods{i}", col, rough=0.5) for i, col in enumerate(((0.8, 0.3, 0.2), (0.2, 0.5, 0.8), (0.9, 0.8, 0.3)))]
SHOP = {}
for kk, x_ in enumerate((SX - 5.5, SX, SX + 5.5)):         # pilasters: one building, two bays
    box(f"ShopPilaster{kk}", (0.5, 0.5, 4.7), (x_, YS + 0.25, 2.35), pil_m)
for side, cx in SHOPX.items():
    inner = 1 if side == "R" else -1                        # towards the middle of the building (the doors sit there)
    box(f"Shop{side}Block", (SHOP_W, 0.3, 4.6), (cx, YS + 0.15, 2.3), navy)
    win = box(f"Shop{side}Window", (3.0, 0.05, 2.1), (cx - inner * 0.6, FRONT + 0.03, 1.35), glass_dark if side == "L" else glass_lit)
    door_x = cx + inner * 1.75
    box(f"Shop{side}Door", (1.0, 0.05, 2.3), (door_x, FRONT + 0.03, 1.15), glass_dark if side == "L" else glass_lit)
    awn = box(f"Shop{side}Awning", (SHOP_W - 0.2, 1.2, 0.08), (cx, FRONT + 0.6, 2.75), awn_mat[side])
    awn.rotation_euler = (math.radians(-12), 0, 0)
    tab_x = cx - inner * 0.6                                # a display table out front, under the awning
    box(f"Shop{side}Table", (2.4, 0.7, 0.06), (tab_x, FRONT + 0.75, 0.82), table_m)
    for lg, (dx, dy) in enumerate(((-1.1, -0.28), (1.1, -0.28), (-1.1, 0.28), (1.1, 0.28))):
        box(f"Shop{side}TableLeg{lg}", (0.05, 0.05, 0.8), (tab_x + dx, FRONT + 0.75 + dy, 0.4), steel)
    for kk in range(3):
        if side == "L" and kk == 1:
            continue                                        # (the broken item stands there)
        box(f"Shop{side}Goods{kk}", (0.35, 0.28, 0.32), (tab_x + (kk - 1) * 0.8, FRONT + 0.75, 1.01), goods[kk])
    sg = city.sign(f"Shop{side}Sign", img("shopL" if side == "L" else "shopR"), Vector((cx, FRONT, 3.55)), Vector((0, 1, 0)), SHOP_W - 0.4,
                   aspect=2400 / 520, emit=0.8, frame="lightbox", offset=0.05)
    SHOP[side] = dict(sign=sg, win=win, door=(door_x, FRONT + 0.3), table=(tab_x, FRONT + 0.75))
closed = city.sign("ShopLClosed", img("shopL_closed"), Vector((SHOPX["L"], FRONT, 3.55)), Vector((0, 1, 0)), SHOP_W - 0.4,
                   aspect=2400 / 520, emit=0.8, offset=0.06)
vase = box("BrokenItem", (0.3, 0.3, 0.42), (SHOP["L"]["table"][0], FRONT + 0.75, 1.06), fx.material("Vase", (0.9, 0.9, 0.88), rough=0.3))
crk = city.sign("BrokenCrack", img("crack"), vase.location + Vector((0, 0.16, 0)), Vector((0, 1, 0)), 0.3, aspect=1.0, offset=0.0, alpha=True)
parent_keep(crk, vase)
BOARD_C = Vector((SX, YS, 5.85))
BOARD_W = 10.8
BOARD_H = BOARD_W * 560 / 3000
boards = [city.sign(f"Board{i}", img(f"board_{n}"), BOARD_C, Vector((0, 1, 0)), BOARD_W, aspect=3000 / 560, emit=0.5,
                    frame="billboard" if i == 0 else None, offset=0.32 + 0.006 * i) for i, n in enumerate("abcd")]
CP = Vector((SX + 9.5, YS + 6.3))                           # the cash pile, in the road (left foreground)
SPOT10 = (SX + BOARD_W / 2 + 0.75, FRONT + 1.15)            # under the board's left end, left of your shop, facing the camera
FL_ROAD = k.floor_at(*SPOT10)
rr = random.Random(9)
fx.paper_pour("BillsPile", os.path.join(SCR, "cash_bill.png"), lambda i: Vector((CP.x + rr.uniform(-1, 1), CP.y + rr.uniform(-1, 1), 2.0)),
              (CP.x, CP.y), count=70, start=-70, dur=30, spread=(1.6, 1.2), size=(0.3, 0.13), arc=(0.3, 0.8))
for kk in range(3):
    box(f"CashPile{kk}", (0.9, 0.5, 0.3), Vector((CP.x - 1.2 + kk * 0.9, CP.y - 1.3 + 0.2 * kk, 0.07)), cash_mat, signs).rotation_euler = (0, 0, 0.4 * kk)
cam10_loc = Vector((SX + 0.8, YN - 1.0, 1.9))
pts10 = [Vector((SX + dx, FRONT, z_)) for dx in (-5.6, 5.6) for z_ in (0.0, 4.6)] + \
        [BOARD_C + Vector((dx * BOARD_W / 2, 0, dz * BOARD_H / 2)) for dx in (-1, 1) for dz in (-1, 1)] + \
        [Vector((SPOT10[0] + 0.5, SPOT10[1], 0.0)), Vector((SPOT10[0] + 0.5, SPOT10[1], 1.9))]
cam10 = (cam10_loc, *k.fit(cam10_loc, pts10, margin=1.06))
cam_open = (cam10_loc, *k.fit(cam10_loc, pts10 + [Vector((CP.x + 1.0, CP.y, 0.0)), Vector((CP.x + 1.0, CP.y, 1.6))], margin=1.04))
cam101_loc = cam10_loc + Vector((-0.4, -2.2, -0.15))      # S10.1: the same head-on shot, pushed in a little
cam101 = (cam101_loc, *k.fit(cam101_loc, pts10, margin=1.04))
print("SHOPS facade", round(YS, 2), "/", round(YN, 2), "cam10", round(cam10[2]), "mm  open", round(cam_open[2]), "mm  cam101", round(cam101[2]), "mm")

# ---- S11-S15 the construction lot behind the plaza (open ground; the cameras look south at it, screen-left is +x)
SITES = {"A": 9.0, "B": -1.5, "C": -12.5}                   # left to right on screen: A, B, C
LOT_Y, SIGN_Y, CAM_Y = 72.0, 76.6, 86.0
T_W, T_H = 3.6, 2.3
TOWER = {s: Vector((x - 0.8, LOT_Y, 0.0)) for s, x in SITES.items()}
SIGN_C = {s: Vector((x + (3.6 if s == "C" else 2.6), SIGN_Y, 0.35 + 1.25)) for s, x in SITES.items()}   # C: room for its crew
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
TOP_B = 6 * T_H + 0.6
AB_LOC = Vector((4.2, CAM_Y + 3.0, 2.3))                    # S11/S12: sites A and B side by side
ptsA = [Vector((SPOT["A"][0] + 1.1, SPOT["A"][1], z_)) for z_ in (0.0, 1.9)] + \
       [SIGN_C[s] + Vector((dx * SW_ / 2, 0, dz * SH_ / 2)) for s in "AB" for dx in (-1, 1) for dz in (-1, 1)] + \
       [TOWER["A"] + Vector((dx * 2.6, 0, z_)) for dx in (-1, 1) for z_ in (0.0, 3.0)] + \
       [Vector((TOWER["A"].x - T_W / 2 - 2.9, LOT_Y + 0.6, 4.0)), Vector((TOWER["B"].x - T_W / 2 - 0.4, LOT_Y, 0.0)),
        Vector((TOWER["B"].x - T_W / 2 - 0.4, LOT_Y, 3.5))]
CAM_A = (AB_LOC, *k.fit(AB_LOC, ptsA, margin=1.05))
B_TOP = [TOWER["B"] + Vector((dx * (T_W / 2 + 2.2), 0, z_)) for dx in (-1, 1) for z_ in (TOP_B, 0.0)]   # it leans (up to ~2 m)
B_LOC = Vector((SITES["B"] + 1.6, CAM_Y + 3.0, 2.3))       # S12: site B on its own (A's board out of frame)
ptsB = [Vector((SPOT["B"][0] + 0.45, SPOT["B"][1], z_)) for z_ in (0.0, 1.9)] + \
       [SIGN_C["B"] + Vector((dx * SW_ / 2, 0, dz * SH_ / 2)) for dx in (-1, 1) for dz in (-1, 1)] + B_TOP
CAM_B = (B_LOC, *k.fit(B_LOC, ptsB, margin=1.05))
C_LOC = Vector((SITES["C"] + 2.4, CAM_Y + 3.0, 2.4))       # S13: the board, him, the crew and the tower
ptsC_lo = [Vector((SPOT["C"][0] + 1.1, SPOT["C"][1], z_)) for z_ in (0.0, 1.9)] + \
          [SIGN_C["C"] + Vector((dx * SW_ / 2, 0, dz * SH_ / 2)) for dx in (-1, 1) for dz in (-1, 1)] + \
          [Vector((TOWER["C"].x - T_W / 2 - 2.3, LOT_Y + T_W / 2 + 2.2, z_)) for z_ in (0.0, 1.9)]     # the boss
ptsC = ptsC_lo + [TOWER["C"] + Vector((dx * T_W / 2, 0, z_)) for dx in (-1, 1) for z_ in (0.0, 7 * T_H + 0.8)]
CAM_C0 = (C_LOC, *k.fit(C_LOC, ptsC_lo + [TOWER["C"] + Vector((dx * T_W / 2, 0, 3 * T_H)) for dx in (-1, 1)], margin=1.06))
CAM_C = (C_LOC, *k.fit(C_LOC, ptsC, margin=1.05))
W3_LOC = Vector((-1.2, CAM_Y + 13.0, 4.0))                 # all three sites side by side
pts3 = ptsA + ptsC + B_TOP
CAM_3 = (W3_LOC, *k.fit(W3_LOC, pts3, margin=1.04))
print("SITECAMS A", round(CAM_A[2]), "B", round(CAM_B[2]), "C", round(CAM_C0[2]), "/", round(CAM_C[2]), "three", round(CAM_3[2]), "mm")
CU_SPOT = (TOWER["C"].x - 0.6, SIGN_Y + 2.2)               # S14/S15: the finished tower right behind him (its sign out of frame)

# ================================================================== performance
T = {}
# ---- S10: flat in the cash pile, up, a line to the board's corner, lands under its left end
open0 = perf.then("Fallen Idle", length=40, face=-120, at=(CP.x, CP.y))
f_0 = face_to(CP, SPOT10)
rise0 = perf.then("Hard Landing", frm=30, to=64, speed=1.1, blend=16, face=f_0)
shoot0 = k.shoot(f_0)
zip0 = k.zip_((Vector(SPOT10) - CP.xy).length, f_0)
land0 = k.touch(f_0, SPOT10)
F10 = face_to(SPOT10, cam10[0])
T[1] = int(land0.start) + UPRIGHT
T[2] = T[1] + F((k.dur(1) + 0.3) * FPS)
talk10 = k.talk_until(T[2] + 4, face=F10, clips=CALM)
# ---- S10.1: the same spot, turned to the closer camera
F101 = face_to(SPOT10, cam101[0])
talk101 = k.talk_until(T[2] + k.hold(2, 0.7), face=F101, clips=CALM)
# ---- S11 the lot (a cut): he stands at site A's sign, its left edge
FA = face_to(SPOT["A"], AB_LOC)
setA = perf.then("Breathing Idle", length=12, face=FA, at=SPOT["A"], in_place=1.0)
T[3] = int(setA.start) + 12
wordf = lambda n, w, nth=0: T[n] + F(k.word(n, w, nth) * FPS)
nodA = perf.then("MX Head Nod Yes", frm=8, length=40, blend=10, face=FA, in_place=1.0)
talkA = k.talk_until(wordf(3, "can") - 6, face=FA, clips=CALM)
shakeA = perf.then("MX Shaking Head No", frm=6, length=48, blend=10, face=FA, in_place=1.0)
holdA = k.talk_until(T[3] + k.hold(3, 0.7), face=FA, clips=CALM)
# ---- S12 "Option two": he sprints across to site B's sign (the camera goes with him), presents it from its left edge
T[4] = int(perf.end) - 4
f_run = face_to(SPOT["A"], SPOT["B"])
RUN0 = T[4] + F(k.word(4, "two") * FPS)
pre12 = perf.then("Breathing Idle", length=max(8, RUN0 - int(perf.end) + 8), blend=8, face=f_run, in_place=1.0)
RUN_D = (Vector(SPOT["A"]) - Vector(SPOT["B"])).length
stride = min(0.24, max(0.14, k.stride("MX Sprint")))
run12 = perf.then("MX Sprint", length=max(24, int(RUN_D / stride)), blend=6, face=f_run, in_place=1.0)
FB = face_to(SPOT["B"], B_LOC)
talkB = k.talk(max(14, T[4] + k.hold(4, 0.9) - int(perf.end) + 10), face=FB, at=SPOT["B"], clips=CALM)
# ---- S13 site C (a cut): he presents its board from its left edge; robots and the crane build, the boss checks
FC = face_to(SPOT["C"], C_LOC)
setC = perf.then("Breathing Idle", length=12, face=FC, at=SPOT["C"], in_place=1.0)
T[5] = int(setC.start) + 12
talkC = k.talk_until(T[5] + k.hold(5, 0.9), face=FC, clips=CALM)
# ---- S14/S15 the close-up in front of the finished tower
FCU = 180.0                                                # faces +y: the close-up camera
cu14 = perf.then("Breathing Idle", length=10, face=FCU, at=CU_SPOT, in_place=1.0)
T[6] = int(cu14.start) + 10
talk14 = k.talk_until(T[6] + k.hold(6, 0.3), face=FCU, clips=CALM)
T[7] = T[6] + F((k.dur(6) + 0.3) * FPS)
shrug15 = perf.then("CMU 111_25 Shrug", frm=10, to=62, blend=10, face=FCU, in_place=1.0)
END = T[7] + F((k.dur(7) + 0.7) * FPS)
talk15 = k.talk_until(END + 2, face=FCU, clips=CALM)
perf.build()
sc.frame_end = END
print("T", T, "END", END)

# ------------------------------------------------------------------ body to camera on every talk beat
CU_CAM = Vector((CU_SPOT[0], CU_SPOT[1] + 2.4, 1.45))
AIMS = [([talk10], cam10[0]), ([talk101], cam101[0]), ([talkA, holdA], AB_LOC), ([talkB], B_LOC), ([talkC], C_LOC), ([talk14, talk15], CU_CAM)]
aim_spans = [(int(first(gs[0]).start), int(final(gs[-1]).end), Vector(loc)) for gs, loc in AIMS]


def facing_cam(f):
    for a_, b_, p in aim_spans:
        if a_ <= f <= b_:
            return (p.x, p.y)
    h = perf.bone_world(HIPS, f)
    return (h.x, h.y - 5)


flat = lambda gs: [c_ for g in gs for c_ in (g.cycles if hasattr(g, "cycles") else [g])]
square_err = perf.square_up(flat(sum((gs for gs, _ in AIMS), [])), facing_cam)
perf.root_z([(f_, 0.0, "const") for f_ in (1, int(setA.start), int(setC.start), int(cu14.start))])   # flat at every cut (no ramps)

# ------------------------------------------------------------------ travel
A0 = BOARD_C + Vector((BOARD_W / 2 - 0.6, 0.3, BOARD_H / 2))    # the line catches the board's top-left corner
k.web_zip(zip0, land0, A0, lift=1.2, name="S10")
# S12: the sprint, a straight run (eased in / out) along the front of site A
ra, rb = int(run12.start), int(run12.end) - 1
pA, pB = Vector((SPOT["A"][0], SPOT["A"][1], 0)), Vector((SPOT["B"][0], SPOT["B"][1], 0))
k.travel(lambda t: pA.lerp(pB, t * t * (3 - 2 * t)), ra, rb, axes=(0, 1), name="S12run")
FLOOR_GAP, N_C = 16, 7
F13_0 = T[5] + F(k.word(5, "agents") * FPS) - 30 - 2 * 16   # floors 0 and 1 are already up when we cut in
LANDS_C = [F13_0 + i * FLOOR_GAP for i in range(N_C)]
for fa, fb, nm in k.travels:
    k.path_hits(fa, fb, nm)

# ------------------------------------------------------------------ feet
air = [(a_, b_) for a_, b_, n_ in k.travels if n_ != "S12run"] + [(int(land0.start), int(land0.start) + 6)]
lock_err = 0.0
for a_, b_, fl in [(1, int(zip0.start) - 1, k.floor_at(CP.x, CP.y)), (int(land0.start), int(setA.start) - 1, FL_ROAD),
                   (int(setA.start), int(setC.start) - 1, k.floor_at(*SPOT["A"])), (int(setC.start), int(cu14.start) - 1, k.floor_at(*SPOT["C"])),
                   (int(cu14.start), END, k.floor_at(*CU_SPOT))]:
    lock_err = max(lock_err, perf.ground_lock(a_, b_, skip=air, step=1, floor=fl))
hips = lambda f: perf.bone_world(HIPS, int(f))

# ------------------------------------------------------------------ webs
webs = fx.WebShots(rig, fx.collection("Webs"))
W = int(perf.clip_frame(shoot0, k.hit_pk))
webs.shot("Web_S10", R_HAND, lambda f: A0, W - 4, W, int(land0.start) - 3)
shot.sfx("web_thwip", W - 3)
shot.sfx("cartwheel_whoosh", int(zip0.start) + 4)
shot.sfx("landing_thud", int(land0.start) + 5)

# ================================================================== S10 / S10.1 action
B_WHO, B_CUST, B_HIGH = wordf(1, "who"), wordf(2, "customers"), wordf(2, "higher")
for ob, a_, b_ in ((boards[0], wordf(1, "you") - 2, B_WHO - 2), (boards[1], B_WHO - 2, B_CUST - 2), (boards[2], B_CUST - 2, B_HIGH - 2),
                   (boards[3], B_HIGH - 2, None)):
    spans = [(1, False), (a_, True)] + ([(b_, False)] if b_ else [])
    if ob is boards[0]:                                      # the board itself (frame) is always there: state a shows a blank
        spans = [(1, True)]
    anim.visible(ob, spans)
blank0 = city.sign("BoardBlank", img("site_blank"), BOARD_C, Vector((0, 1, 0)), BOARD_W, aspect=3000 / 560, emit=0.1, offset=0.35)
blank0.data.materials[0] = fx.material("BoardOff", (0.05, 0.06, 0.08), rough=0.4)
anim.visible(blank0, [(1, True), (wordf(1, "you") - 2, False)])
for f_ in (wordf(1, "you"), B_WHO, B_CUST, B_HIGH):
    shot.sfx("ui_pop", f_)
# your shop: the sign flickers through S10.1, then flips to CLOSED and the window goes dark
lsign_mat = SHOP["L"]["sign"].data.materials[0]
lbsdf = next(n for n in lsign_mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
flick = random.Random(3)
CLOSE_F = B_HIGH
seqk = [(1, 0.8, "const")]
for f_ in range(T[2] - 10, CLOSE_F, 4):
    seqk.append((f_, flick.choice((0.8, 0.8, 0.15, 0.6, 0.05)), "const"))
seqk.append((CLOSE_F, 0.0, "const"))
anim.keys(lbsdf.inputs["Emission Strength"], "default_value", seqk)
anim.visible(closed, [(1, False), (CLOSE_F, True)])
anim.visible(SHOP["L"]["sign"], [(1, True), (CLOSE_F, False)])
shot.sfx("ui_pop", CLOSE_F)
# the customers: out of your door, along the sidewalk, into the queue at their door (it runs off to the right). The
# queue moves: every ENTER_GAP frames the one at their door goes in and everyone steps up a place.
LEAVE = wordf(1, "competitor")
dl, dr = SHOP["L"]["door"], SHOP["R"]["door"]
QUEUE = lambda i: (dr[0] - 0.35 - 0.72 * i, FRONT + 1.45)
LANE = FRONT + 2.5                                          # the outer lane of the sidewalk (they pass the queue there)
DOOR_IN = (dr[0], FRONT + 0.05)
ENTER0, ENTER_GAP = LEAVE - 60, 60
entries = [ENTER0 + i * ENTER_GAP for i in range(40)]
n_in = lambda t: sum(1 for e in entries if e <= t)


def queue_route(w_, rank, f0, approach=(), phase=0.0):
    """rank = place in the overall order (0 = first at their door). approach = [(point, wait), ...] from where they
    start to the sidewalk (empty: already in the line at f0). Then: into their place, a step up at every entry, and
    in through the door at their own turn (they vanish inside)."""
    sp = w_.speed
    walk_n = lambda p_, q_: max(1, int(round((Vector(q_) - Vector(p_)).length / sp)))
    legs, t = [], int(f0)
    if approach:
        legs = [[p_, wt] for p_, wt in approach]
        for (p_, wt), (q_, _) in zip(approach, approach[1:]):
            t += wt + walk_n(p_, q_)
        t += approach[-1][1]
        slot = max(0, rank - n_in(t + 30))
        lane_pt = (QUEUE(slot)[0], LANE)
        t += walk_n(approach[-1][0], lane_pt)
        t += walk_n(lane_pt, QUEUE(slot))
        legs += [[lane_pt, 0], [QUEUE(slot), 0]]
    else:
        slot = max(0, rank - n_in(t))
        legs = [[QUEUE(slot), 0]]
    t_arr = t
    my_in = max(entries[rank], t + 2)
    for e in entries:
        if e <= t or e >= my_in or slot == 0:
            continue
        legs[-1][1] = e - t
        slot -= 1
        t = e + walk_n(legs[-1][0], QUEUE(slot))
        legs.append([QUEUE(slot), 0])
    legs[-1][1] = max(0, my_in - t)
    t = max(t, my_in)
    t_door = t + walk_n(legs[-1][0], DOOR_IN)
    legs.append([DOOR_IN, 0])
    w_.route([tuple(l) for l in legs], int(f0), phase=phase, until=t_door)
    w_.face(t_arr if approach else int(f0), (1, 0))         # in line: facing their door (+x)
    return t_door


N_PRE = 6
for i in range(N_PRE):                                      # already queueing at their door
    queue_route(spawn(f"Queued{i}"), i, 1, phase=rw.random())
for i in range(5):                                          # yours walk out and join their line
    queue_route(spawn(f"Customer{i}"), N_PRE + i, LEAVE + i * 18, approach=[(dl, 0), ((dl[0], LANE), 0)], phase=rw.random())
# the last customer in your shop: picks up the broken item, looks, puts it down, joins the end of their line
w_ = spawn("LastCustomer")
look_p = (SHOP["L"]["table"][0], FRONT + 1.45)
item_f = B_CUST + 6
f0_last = item_f - 40
queue_route(w_, N_PRE + 5, f0_last, approach=[(dl, 0), (look_p, 70), ((look_p[0], LANE), 0)], phase=0.3)
w_.face(f0_last + int(((Vector(look_p) - Vector(dl)).length) / w_.speed) + 1, (0, -1))
up_ = vase.location.copy()
anim.keys(vase, "location", [(item_f + 4, up_, "inout"), (item_f + 16, up_ + Vector((0, 0.45, 0.3)), "inout"),
                             (item_f + 44, up_ + Vector((0, 0.45, 0.3)), "inout"), (item_f + 58, up_)])

# ================================================================== S11-S13 the sites
anim.visible(site_signs["A"][1], [(1, False), (wordf(3, "option") - 2, True), (T[4], False)])
anim.visible(site_signs["B"][1], [(1, False), (wordf(4, "option") - 2, True)])
anim.visible(site_signs["B"][2], [(1, False), (wordf(4, "most") - 2, True)])
anim.visible(site_signs["C"][1], [(1, False), (wordf(5, "that") - 2, True)])
THAT = wordf(5, "that")
# one focal point: a site's sign shows its title only in its own scene; on the three-site pull-back A and B show their titles
anim.visible(site_signs["A"][-1], [(1, True), (int(setA.start) - 1, False), (T[4], True), (THAT, False)])
anim.visible(site_signs["B"][-1], [(1, True), (T[4] - 1, False)])
anim.visible(site_signs["B"][1], [(1, False), (wordf(4, "option") - 2, True), (THAT, False)])
anim.visible(site_signs["B"][2], [(1, False), (wordf(4, "most") - 2, True), (THAT, False)])
anim.visible(site_signs["C"][-1], [(1, True), (int(setC.start) - 1, False)])
for f_ in (wordf(3, "option"), wordf(4, "option"), wordf(4, "most"), THAT):
    shot.sfx("ui_pop", f_)
# ---- site A: a neat one-storey brick building (door, windows); the workers lay the top course; the pallet pile outgrows it
tA = TOWER["A"]
AW, AD, AH = 4.6, 3.6, 2.5
brick_x, brick_y = brick_mat("BrickX", "x"), brick_mat("BrickY", "y")
for kk, (dx, dy, sx_, sy_, m_) in enumerate(((0, AD / 2, AW, 0.3, brick_x), (0, -AD / 2, AW, 0.3, brick_x),
                                             (-AW / 2, 0, 0.3, AD, brick_y), (AW / 2, 0, 0.3, AD, brick_y))):
    box(f"WallA{kk}", (sx_, sy_, AH), tA + Vector((dx, dy, AH / 2)), m_, csite)
trim = fx.material("WinTrim", (0.85, 0.85, 0.82), rough=0.5)
winA = fx.material("WinGlassA", (0.25, 0.4, 0.55), rough=0.08, metallic=0.3)
doorA = fx.material("DoorA", (0.35, 0.2, 0.1), rough=0.6)
fy = tA.y + AD / 2 + 0.16
for kk, wx in enumerate((-1.25, 1.25)):                     # two windows and a door on the front
    box(f"WinA{kk}", (0.95, 0.04, 0.9), tA + Vector((wx, fy - tA.y, 1.45)), winA, csite)
    for j, (sx_, sz_, dx, dz) in enumerate(((1.1, 0.08, 0, 0.49), (1.1, 0.08, 0, -0.49), (0.08, 1.0, 0.51, 0), (0.08, 1.0, -0.51, 0))):
        box(f"WinA{kk}Trim{j}", (sx_, 0.05, sz_), tA + Vector((wx + dx, fy - tA.y + 0.01, 1.45 + dz)), trim, csite)
box("DoorA", (0.9, 0.04, 1.9), tA + Vector((0.0, fy - tA.y, 0.95)), doorA, csite)
box("DoorAStep", (1.3, 0.5, 0.12), tA + Vector((0.0, AD / 2 + 0.4, 0.06)), fx.material("Concrete", (0.48, 0.47, 0.45), rough=0.9), csite)
A_IN = T[3] - 40
brick = fx.material("Brick", (0.5, 0.2, 0.12), rough=0.85)
for kk in range(14):                                        # the top course along the front, one brick at a time
    bx = tA + Vector((-AW / 2 + 0.3 + kk * 0.31, AD / 2, AH + 0.08))
    b_ = box(f"BrickTop{kk}", (0.29, 0.3, 0.15), bx, brick, csite)
    anim.visible(b_, [(1, kk < 2), (A_IN + 30 + kk * 28, True)])
box("Pallet", (1.2, 1.0, 0.14), tA + Vector((-AW / 2 - 1.3, 0.6, 0.07)), fx.material("PalletWood", (0.5, 0.36, 0.2), rough=0.8), csite)
box("BrickBundle", (1.0, 0.85, 0.42), tA + Vector((-AW / 2 - 1.3, 0.6, 0.35)), brick_x, csite)        # one bundle on its pallet
# the crew: two builders at the front wall (3/4 to the camera), the boss beside them giving instructions
cw = crew.Crew()
CREW_END = int(cu14.start) + 2
CLIP_BOSS = "CMU 18_08 conversation - explain with hand gesture"
builders = [cw.worker("BuilderA0", (tA.x + 1.0, tA.y + AD / 2 + 0.75), face=(-0.6, -0.8), phase=0.0),
            cw.worker("BuilderA1", (tA.x - 1.2, tA.y + AD / 2 + 0.75), face=(0.6, -0.8), phase=0.45)]
BOSS_A = (tA.x - AW / 2 - 0.9, tA.y + AD / 2 + 1.7)
boss_a = cw.boss("BossA", BOSS_A, face=(tA.x - BOSS_A[0], tA.y + AD / 2 + 0.75 - BOSS_A[1]), rig=rig, clip=CLIP_BOSS)
for u in builders:
    u.show([(1, True), (CREW_END, False)])
boss_a.show([(1, True), (int(setC.start), False)])          # S13: he is at site C
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
T4_0 = T[4] + 6                                              # the crane starts on "option two"
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
RUN_F = wordf(4, "notice")
# ---- site C: square floors at the same speed; every one gets a green stamp as he reaches it
blueglass = fx.material("BlueFloor", (0.12, 0.33, 0.78), rough=0.35, metallic=0.2)
glassC = fx.material("WinGlassC", (0.65, 0.82, 0.95), rough=0.08, metallic=0.3, emit=0.4)
pivC = crane("CraneC", TOWER["C"], 19.5)
floorsC = stack("TowerC", TOWER["C"], N_C, F13_0, FLOOR_GAP, blueglass, crooked=0.0, seed=7)
for i, (fl, land, rest) in enumerate(floorsC):
    windows(fl, rest, 30 + i, missing=0.0, hole=glassC, glass=glassC, appear=land - 14, landed=land + 10)
    stf = land + 9 if i >= 2 else int(setC.start)            # floors 0-1 were stamped before we cut in
    st_ = city.sign(f"StampC{i}", img("stamp_ok"), rest + Vector((T_W / 2 - 0.5, T_W / 2 + 0.06, 0.2)), SN, 0.8, aspect=1.0,
                    offset=0.0, alpha=True, emit=0.3, coll=csite)
    parent_keep(st_, fl, land + 10)
    anim.visible(st_, [(1, False), (stf, True)])
    anim.keys(st_, "scale", [(stf, Vector((2.2, 2.2, 2.2)), "out"), (stf + 5, Vector((1, 1, 1)), "back")])
    if i >= 2:
        shot.sfx("block_thud", land)
        shot.sfx("ui_pop", stf)
anim.keys(pivC, "rotation_euler", [(f_, Vector((0, 0, 0.3 * math.sin(f_ / 8.0))), "inout") for f_ in range(F13_0 - 40, F13_0 + N_C * FLOOR_GAP + 20, 8)])
# the builders at site C are robots: two arms at the tower's foot, a builder bot; the boss (human judgment) checks
tc = TOWER["C"]
for i, (dx, ph) in enumerate(((T_W / 2 - 0.3, 0.0), (-T_W / 2 + 0.2, 0.5))):
    cw.arm(f"RobotArmC{i}", (tc.x + dx, tc.y + T_W / 2 + 0.9), face=(0, -1), phase=ph)
cw.robot("RobotC0", (tc.x + 0.4, tc.y + T_W / 2 + 2.4), face=(0.3, 1))
BOSS_C = (tc.x - T_W / 2 - 1.1, tc.y + T_W / 2 + 2.2)
boss_c = cw.boss("BossC", BOSS_C, face=(0.8, -0.6), rig=rig, clip=CLIP_BOSS)
boss_c.show([(1, False), (int(setC.start), True)])

# ================================================================== S14 / S15 the hand: fingers + arm (IK)
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
         "point": finger_pose(("Index",)), "fist": finger_pose(()), "flat": finger_pose(FING, thumb_in=False)}
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
SEQ = [(w6("headcount") - 6, "flat"), (w6("headcount") - 2, "one"), (w6("code") - 2, "two"), (w6("better") - 2, "three"),
       (w6("only") - 4, "three"), (w6("only"), "fist"), (w6("only") + 14, "flat"),
       (w7("why") + 40, "flat"), (w7("why") + 46, "point"), (w7("cuz") - 2, "point"), (w7("ai") + 4, "flat"), (w7("human") - 4, "flat"),
       (END - 2, "flat")]
for f_, p_ in SEQ:
    key_pose(f_, p_)
if hasattr(f_act, "slots") and f_act.slots and not ad.action_slot:
    ad.action_slot = f_act.slots[0]
ad.action = keep_action
fin_tr = ad.nla_tracks.new()
fin_tr.name = "ZZ Finger poses"
a_, b_ = T[6] - 4, END
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
office.present(w7("why") + 40, HD(w7("why") + 40) + fwd * 0.12 + Vector((0, 0, -0.1)), side="R", hold=16, ramp=6, amount=1.0)   # chin
office.present(w7("cuz") - 6, HD(w7("cuz")) + Vector((-0.11, 0.04, 0.05)), side="R", hold=12, ramp=5, amount=1.0)              # temple
office.present(w7("human") - 8, cuh(w7("human")) + fwd * 0.16 + Vector((0.05, 0, 0.05)), side="R", hold=26, ramp=7, amount=1.0)    # chest
# the hand's own rotation per gesture (the IK only places the wrist; left to the talk clip, the wrist twisted into a
# claw). Columns: hand X, Y (along the fingers), Z (the palm side: fingers curl towards +Z). He faces +y.
hand_t = fx.empty("HandAim", (0, 0, 0), csite, 0.05)
hand_rot = rig.pose.bones[R_HAND].constraints.new("COPY_ROTATION")
hand_rot.name = "Hand aim"
hand_rot.target = hand_t
hand_rot.owner_space = hand_rot.target_space = "WORLD"
hand_rot.influence = 0.0
hk = [(1, 0.0, "const")]


def orient(frame, X, Y, Z, hold, ramp):
    anim.key(hand_t, "rotation_euler", int(frame), Matrix((X, Y, Z)).transposed().to_euler(), ease="const")
    hk.extend([(int(frame), 0.0, "inout"), (int(frame) + ramp, 1.0, "inout"), (int(frame) + ramp + hold, 1.0, "inout"),
               (int(frame) + 2 * ramp + hold, 0.0, "inout")])


UP, TOWARD, BACK, HIS_L = (0, 0, 1), (0, 1, 0), (0, -1, 0), (1, 0, 0)
orient(w6("headcount") - 10, (-1, 0, 0), UP, TOWARD, w6("only") - w6("headcount") + 4, 8)        # count: palm to the camera
orient(w7("why") + 40, HIS_L, UP, BACK, 16, 6)                                                   # chin: palm to his face
orient(w7("cuz") - 6, TOWARD, UP, (1, 0, 0), 12, 5)                                               # temple: palm to his head
orient(w7("human") - 8, (0, 0, -1), HIS_L, BACK, 26, 7)                                          # chest: palm on it
anim.keys(hand_rot, "influence", sorted(hk))

# ================================================================== cameras
cam = k.camera()
CUTS = []
# S10: framed wide enough for the cash pile, then settles on the building as he lands beside the board
cam.lens(1, round(cam_open[2]), "const")
k.at(1, cam_open[0], cam_open[1], "lin", cut=True)
k.at(int(zip0.start), cam_open[0], cam_open[1], "inout")
cam.lens(int(zip0.start), round(cam_open[2]), "inout")
k.at(int(land0.start) + 14, cam10[0], cam10[1], "inout")
cam.lens(int(land0.start) + 14, round(cam10[2]), "inout")
k.at(T[2], cam10[0] + Vector((0, -0.15, 0)), cam10[1], "inout")   # S10.1: no cut, a slow push in on the same building
cam.lens(T[2], round(cam10[2]), "inout")
k.at(int(setA.start) - 1, cam101[0], cam101[1], "inout")
cam.lens(int(setA.start) - 1, round(cam101[2]), "const")
# S11: site A (B's empty plot at the right edge); S12: the camera trucks right with his sprint and settles on site B
cam.lens(int(setA.start), round(CAM_A[2]), "const")
k.at(int(setA.start), CAM_A[0], CAM_A[1], "lin", cut=True)
k.at(ra - 2, CAM_A[0] + Vector((0, -0.2, 0)), CAM_A[1], "inout")
cam.lens(ra - 2, round(CAM_A[2]), "inout")
k.at(rb + 10, CAM_B[0], CAM_B[1], "inout")
cam.lens(rb + 10, round(CAM_B[2]), "inout")
CUTS.append(("A", int(setA.start)))
hole_p = floorsB[HOLE_FL][2] + Vector((0, T_W / 2, 0.1))
door_p = floorsB[DOOR_FL][2] + Vector((T_W / 2 - 0.6, T_W / 2, 0.0))
SUB = wordf(4, "subtle")
k.at(max(SUB - 2, rb + 12), CAM_B[0], CAM_B[1], "inout")
cam.lens(max(SUB - 2, rb + 12), round(CAM_B[2]), "inout")
cam.lens(SUB + 22, 45, "inout")
k.at(SUB + 22, hole_p + Vector((1.5, 7.5, 1.0)), hole_p, "inout")
k.at(DOOR_F - 4, hole_p + Vector((1.3, 7.2, 1.0)), hole_p, "inout")
k.at(DOOR_F + 14, door_p + Vector((1.5, 7.5, 0.6)), door_p, "inout")
cam.lens(RUN_F - 6, 45, "const")
k.at(RUN_F - 6, door_p + Vector((1.5, 7.4, 0.6)), door_p, "lin")
cam.lens(RUN_F - 5, round(CAM_B[2]), "const")
k.at(RUN_F - 5, CAM_B[0], CAM_B[1], "lin", cut=True)
k.at(int(setC.start) - 1, CAM_B[0] + Vector((0, -0.3, 0)), CAM_B[1], "lin")
cam.lens(int(setC.start) - 1, round(CAM_B[2]), "const")
CUTS.append(("B back", RUN_F - 5))
# S13: site C (board, him, the robots, the boss, the lower floors), widening as the tower goes up; on "That team
# beats..." the pull-back to all three sites side by side
C_TOP = lambda f: T_H * max(3, min(N_C, sum(1 for lf in LANDS_C if lf <= f))) + 0.8      # the top of the tower so far
c_fit = lambda f: k.fit(C_LOC, ptsC_lo + [TOWER["C"] + Vector((dx * T_W / 2, 0, C_TOP(f))) for dx in (-1, 1)], margin=1.06)
c_keys = list(range(int(setC.start), THAT - 4, 8)) + [THAT - 4]
c_sm = {f: c_fit(f) for f in range(int(setC.start) - 16, THAT + 20)}
for f in c_keys:                                             # widens with the tower, the ground always in frame
    tg = sum((c_sm[q][0] for q in range(f - 16, f + 17)), Vector()) / 33
    ln = sum(c_sm[q][1] for q in range(f - 16, f + 17)) / 33
    k.at(f, C_LOC, tg, "lin", cut=(f == int(setC.start)))
    cam.lens(f, ln, "const" if f == int(setC.start) else "lin")
P3 = min(int(cu14.start) - 12, THAT + 50)
k.at(P3, CAM_3[0], CAM_3[1], "inout")
cam.lens(P3, round(CAM_3[2]), "inout")
k.at(int(cu14.start) - 1, CAM_3[0] + Vector((0, -0.2, 0)), CAM_3[1], "lin")
cam.lens(int(cu14.start) - 1, round(CAM_3[2]), "const")
CUTS.append(("C", int(setC.start)))
# S14 / S15: a medium close-up (head to waist: his hands stay in frame; S15 a touch tighter); the tower soft behind
cu_t = lambda f: HD(f) + Vector((0, 0, -0.36))
cam.lens(int(cu14.start), 36, "const")
cam.lens(T[7] - 1, 36, "inout")
cam.lens(T[7] + 20, 40, "inout")
cu_pts = {f: cu_t(f) for f in range(int(cu14.start) - 8, END + 10)}
cu_sm = lambda f: sum((cu_pts[q] for q in range(f - 8, f + 9)), Vector()) / 17          # follows his head, smoothly
for f in range(int(cu14.start), END + 1, 3):
    push = min(1.0, max(0.0, (f - T[7]) / 20.0)) * 0.25
    k.at(f, CU_CAM + Vector((0, -push, 0)), cu_sm(min(f, END)), "lin", cut=(f == int(cu14.start)))
CUTS.append(("close-up", int(cu14.start)))
cam.shake(int(land0.start) + 5, amp=0.04, dur=8)
FSTOPS = [(1, 8.0), (T[2], 8.0), (int(setA.start), 8.0), (SUB + 22, 4.0), (RUN_F - 5, 8.0), (int(setC.start), 8.0), (int(cu14.start), 2.8)]
for f_, v_ in sorted(FSTOPS):
    anim.key(cam.cam.data.dof, "aperture_fstop", int(f_), v_, ease="const")
TALKS = [talk10, talk101, talkA, holdA, talkB, talkC]
office.face_camera(cam.cam, [(int(first(g).start) + 4, int(final(g).end) - 2) for g in TALKS] + [(int(cu14.start), END - 4)], amount=0.55)
office.nod(w6("stay"), depth=0.6)
office.nod(w7("cuz") + 6, depth=-0.4)
for kk in range(3):                                          # a light head shake on "doesn't make more great products"
    f_ = w7("doesn") + kk * 7
    anim.keys(office.cam_eye, "location", [(f_, 0.0, "inout"), (f_ + 3, 0.35 * (-1) ** kk, "inout"), (f_ + 7, 0.0, "inout")], index=0)
anim.keys(office.cam_eye, "location", [(T[2] - 14, 0.0, "inout"), (T[2] - 6, 0.5, "inout"), (T[2] + 2, 0.0, "inout")], index=0)   # the head tilt (S10)
fx.char_lights(rig, cam.cam, key=170.0, rim=340.0)
# S10: he presents your shop on "you ship without inspection", theirs on "your competitor"; S10.1 a thumb at their queue
fL, fR = wordf(1, "without"), wordf(1, "competitor")
pL = Vector((SHOPX["L"], FRONT + 0.6, 2.2))
pR = Vector((SHOPX["R"], FRONT + 0.6, 2.2))
office.present(fL - 6, pL, side=k.gesture_side(pL, hips(fL), cam10[0]), hold=max(8, fR - fL - 16), ramp=7, amount=0.6)
office.present(fR - 4, pR, side=k.gesture_side(pR, hips(fR), cam10[0]), hold=max(8, B_WHO - fR - 12), ramp=7, amount=0.6)
qp = Vector((QUEUE(4)[0], QUEUE(4)[1], 1.4))
office.present(T[2] + 2, qp, side=k.gesture_side(qp, hips(T[2]), cam101[0]), hold=30, ramp=7, amount=0.7)
office.present(T[3] + 6, SIGN_C["A"] + Vector((0, 0.4, 0)), side=k.gesture_side(SIGN_C["A"], hips(T[3]), AB_LOC), hold=24, ramp=8, amount=0.6)
fB = int(first(talkB).start) + 12
office.present(fB, SIGN_C["B"] + Vector((0, 0.4, 0)), side=k.gesture_side(SIGN_C["B"], hips(fB), B_LOC), hold=24, ramp=8, amount=0.6)
office.present(T[5] + 6, SIGN_C["C"] + Vector((0, 0.4, 0)), side=k.gesture_side(SIGN_C["C"], hips(T[5]), C_LOC), hold=24, ramp=8, amount=0.6)
from pipeline import face
eyes = face.Lenses(bpy.data.objects["MilesMasked"])
for f_, w_ in ((1, dict(Squint=0.85)), (int(rise0.start) + 10, dict(Squint=0.0, Wide=0.4)), (T[1], dict(Wide=0.0, Squint=0.25)),
               (B_WHO, dict(Squint=0.0, Wide=0.7)), (T[2], dict(Wide=0.3)), (B_HIGH, dict(Wide=0.0, Angry=0.25)),
               (T[3], dict(Angry=0.0, Squint=0.3)), (wordf(3, "can"), dict(Squint=0.0, Sad=0.6)), (T[4], dict(Sad=0.0, Wide=0.5)),
               (RUN_F, dict(Wide=0.0, Squint=0.5)), (T[5], dict(Squint=0.4)),
               (T[6], dict(Squint=0.0, Wide=0.45)), (w6("only"), dict(Wide=0.0, Squint=0.35, Angry=0.3)), (w6("stay"), dict(Squint=0.0, Angry=0.0, Wide=0.3)),
               (T[7], dict(Wide=0.0, Sad=0.3)), (w7("cuz"), dict(Sad=0.0, Wide=1.0)), (w7("doesn"), dict(Wide=0.0, Angry=0.35)),
               (w7("human"), dict(Angry=0.0, Squint=0.3))):
    eyes.set(f_, **w_)
eyes.blinks(1, END, every=95)
webs.bake(range(1, END + 1))
for o in fx.collection("Webs").objects:
    if o.type == "MESH":
        o.data.materials[0] = fx.material("Web_Line", (0.95, 0.97, 1.0), rough=0.35, emit=0.9)

# ------------------------------------------------------------------ nothing of the city between the lens and the shops
deps = bpy.context.evaluated_depsgraph_get()
blockers = set()
for loc in (cam10[0], cam101[0], cam_open[0]):
    for p in pts10 + [Vector((x_, FRONT + 0.3, z_)) for x_ in [SX - 5.2 + 0.8 * i for i in range(14)] for z_ in (0.5, 1.5, 2.5, 3.5)]:
        d = p - loc
        ok, hp_, nn, ii, ob, mm = sc.ray_cast(deps, loc, d.normalized(), distance=d.length - 0.3)
        if ok and ob.name in c.coll.all_objects:
            dims = ob.dimensions
            if max(dims) < 9.0:
                blockers.add(ob.name)
for n_ in sorted(blockers):
    bpy.data.objects[n_].hide_render = bpy.data.objects[n_].hide_viewport = True
big_hits = {}
for loc in (cam10[0], cam101[0], cam_open[0]):
    tg = pts10 + [Vector((x_, FRONT + 0.3, z_)) for x_ in [SX - 5.2 + 0.4 * i for i in range(28)] for z_ in (0.5, 1.5, 2.5, 3.5, 4.5)] + \
         [Vector((SPOT10[0] + dx, SPOT10[1], z_)) for dx in (-0.3, 0.0, 0.3) for z_ in (0.3, 1.0, 1.7)]
    for p in tg:
        d = p - loc
        ok, hp_, nn, ii, ob, mm = sc.ray_cast(deps, loc, d.normalized(), distance=d.length - 0.3)
        if ok and ob.name in c.coll.all_objects and max(ob.dimensions) >= 9.0:
            big_hits.setdefault(ob.name, []).append((ii, hp_.copy()))


def drop_islands(ob, hits, r_xy=0.5, max_size=12.0):
    """Delete the mesh islands (a lamp head, its pole) of a merged city mesh that contain the hit faces, or stand on
    the same spot (a pole's vertices sit at its ends, right above / below a mid-height hit)."""
    me = ob.data.copy()
    ob.data = me
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    M = ob.matrix_world
    seeds = {v for i, _ in hits if i < len(bm.faces) for v in bm.faces[i].verts}
    pts_ = [p_ for _, p_ in hits]
    seeds |= {v for v in bm.verts if any(((M @ v.co).xy - p_.xy).length < r_xy for p_ in pts_)}
    seeds = list(seeds)
    seen, stack = set(seeds), list(seeds)
    while stack:
        v = stack.pop()
        for e in v.link_edges:
            o_ = e.other_vert(v)
            if o_ not in seen:
                seen.add(o_)
                stack.append(o_)
    ws = [M @ v.co for v in seen]
    size = max((max(w[i] for w in ws) - min(w[i] for w in ws)) for i in range(3)) if ws else 0
    if seen and size <= max_size:
        bmesh.ops.delete(bm, geom=list(seen), context="VERTS")
        bm.to_mesh(me)
        print("SHOPS removed", len(seen), "verts of", ob.name, f"({size:.1f} m)")
    else:
        print("SHOPS kept", ob.name, f"island {size:.1f} m")
    bm.free()


for n_, pts_ in big_hits.items():
    drop_islands(bpy.data.objects[n_], pts_)
print("SHOPS cleared", sorted(blockers))

# ================================================================== captions (laid over in post)
OVER = [(w6("headcount") - 2, T[7] - 6, "Same headcount.", 0), (w6("code") - 2, T[7] - 6, "More code.", 1),
        (w6("better") - 2, T[7] - 6, "Better product.", 2), (w7("not") - 2, END, "Common sense isn't in the **training data.**", 0)]
json.dump(dict(fps=FPS, end=END, captions=[dict(f0=a_, f1=b_, text=t_, row=r_) for a_, b_, t_, r_ in OVER]),
          open(os.path.join(paths.ROOT, "build", f"{NAME}_overlays.json"), "w"), indent=1)

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
READS = [("siteA", talkA, SIGN_C["A"], SN, SW_, SH_), ("siteB", talkB, SIGN_C["B"], SN, SW_, SH_), ("siteC", talkC, SIGN_C["C"], SN, SW_, SH_)]
json.dump(dict(travel=[(a_, b_, n_) for a_, b_, n_ in k.travels if n_ != "S12run"],
               talks=[(int(first(g).start + first(g).blend) + 4, int(final(g).end) - 12, v3(loc)) for gs, loc in AIMS for g in gs],
               reads=[(n_, int(first(g).start + first(g).blend) + 4, int(final(g).end) - 6, v3(bc), v3(nn), w_, h_)
                      for n_, g, bc, nn, w_, h_ in READS],
               webs=[o.name for o in fx.collection("Webs").objects if o.type == "MESH"]),
          open(os.path.join(paths.ROOT, "build", f"{NAME}_audit.json"), "w"))
VO_CUES = {n: T[n] for n in range(1, 8)}
shot.finish(NAME, exposure=-0.35, samples=24, view="AgX", grade="AgX - Punchy",
            markers=[(f"vo {n}", f) for n, f in VO_CUES.items()] + [
                ("S10 shops", T[1]), ("S10.1 answer", T[2]), ("S11 human", T[3]), ("S12 agent", T[4]), ("S13 both", T[5]),
                ("S14 close-up", T[6]), ("S15 common sense", T[7]), ("end", END)])
fx.cine_grade(sc)
bpy.ops.wm.save_mainfile()
cues = sorted(VO_CUES.items(), key=lambda kv: kv[1])
for (a, fa), (b, fb) in zip(cues, cues[1:]):
    if fa + k.dur(a) * FPS > fb:
        print(f"VO OVERLAP {a}->{b}: {(fa + k.dur(a) * FPS - fb) / FPS:.2f}s")
print("CUTS", CUTS)
print(f"STREET2A frames 1-{END} ({END / FPS:.1f}s)  ground-lock {lock_err * 100:.1f} cm  square {square_err:.1f}")
