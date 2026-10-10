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
from pipeline.streetkit import first, final, face_to, SHOOT, HANG

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
walk.phone_every = 6                                         # one in six on a phone (not everyone)
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


def stripes(name, c1, c2, width=0.32):
    """Awning stripes along x (object space, metres)."""
    m = fx.material(name, c1, rough=0.6)
    nt = m.node_tree
    bs = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tc, sep = nt.nodes.new("ShaderNodeTexCoord"), nt.nodes.new("ShaderNodeSeparateXYZ")
    dv, md = nt.nodes.new("ShaderNodeMath"), nt.nodes.new("ShaderNodeMath")
    dv.operation, md.operation = "DIVIDE", "FLOORED_MODULO"
    dv.inputs[1].default_value, md.inputs[1].default_value = width * 2, 1.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = (*c1, 1)
    ramp.color_ramp.elements[1].position = 0.5
    ramp.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    nt.links.new(sep.outputs["X"], dv.inputs[0])
    nt.links.new(dv.outputs[0], md.inputs[0])
    nt.links.new(md.outputs[0], ramp.inputs[0])
    nt.links.new(ramp.outputs["Color"], bs.inputs["Base Color"])
    return m


def ball(name, r, loc, mat, coll=signs):
    me = bpy.data.meshes.new(name)
    b = bmesh.new()
    bmesh.ops.create_uvsphere(b, u_segments=12, v_segments=8, radius=r)
    b.to_mesh(me)
    b.free()
    for p_ in me.polygons:
        p_.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob.location = loc
    me.materials.append(mat)
    return ob


# the competitor's shop looks the part: its lit interior through the window, a striped awning, brass trim, a
# planter, warm bulbs under the awning, an OPEN neon, warm light spilling onto the sidewalk (yours stays plain)
cxR = SHOPX["R"]
win_c = Vector((cxR - 0.6, FRONT + 0.055, 1.35))
city.sign("ShopRInterior", img("shopR_interior"), win_c, Vector((0, 1, 0)), 3.0, aspect=1500 / 1050, emit=0.9, offset=0.01)
city.sign("ShopROpen", img("open_neon"), win_c + Vector((0.85, 0, 0.62)), Vector((0, 1, 0)), 0.9, aspect=900 / 360, emit=3.0,
          offset=0.02, alpha=True)
bpy.data.objects["ShopRAwning"].data.materials[0] = stripes("AwningStripes", (0.04, 0.32, 0.14), (0.9, 0.9, 0.86))
brass = fx.material("Brass", (0.8, 0.58, 0.22), rough=0.3, metallic=1.0)
for j, (sx_, sz_, dx, dz) in enumerate(((3.16, 0.08, 0, 1.09), (3.16, 0.08, 0, -1.09), (0.08, 2.26, 1.54, 0), (0.08, 2.26, -1.54, 0))):
    box(f"ShopRTrim{j}", (sx_, 0.06, sz_), win_c + Vector((dx, 0.02, dz)), brass)
box("ShopRHandle", (0.04, 0.06, 0.5), (SHOP["R"]["door"][0] - 0.38, FRONT + 0.09, 1.1), brass)
pot_m, leaf_m = fx.material("Planter", (0.12, 0.12, 0.13), rough=0.5), fx.material("Leaves", (0.08, 0.32, 0.08), rough=0.8)
for j, px in enumerate((SHOP["R"]["door"][0] - 0.95, cxR - 2.25)):
    box(f"ShopRPot{j}", (0.45, 0.45, 0.5), (px, FRONT + 0.32, 0.25), pot_m)
    for q, (dx, dz, r_) in enumerate(((0, 0.75, 0.3), (0.12, 0.98, 0.22), (-0.1, 0.92, 0.2))):
        ball(f"ShopRLeaf{j}{q}", r_, Vector((px + dx, FRONT + 0.32, dz)), leaf_m)
bulb = fx.material("Bulb", (1.0, 0.85, 0.55), rough=0.3, emit=6.0, emit_color=(1.0, 0.78, 0.45))
for j in range(12):
    ball(f"ShopRBulb{j}", 0.045, Vector((cxR - 2.3 + j * 0.42, FRONT + 1.15, 2.5 - 0.05 * math.sin(j * 1.3) ** 2)), bulb)
spill = bpy.data.lights.new("ShopRSpill", "AREA")
spill.energy, spill.size, spill.color = 220.0, 3.0, (1.0, 0.78, 0.5)
spill_ob = bpy.data.objects.new("ShopRSpill", spill)
signs.objects.link(spill_ob)
spill_ob.location = win_c + Vector((0, 0.35, 0.4))
spill_ob.rotation_euler = (math.radians(-60), 0, 0)              # out of the window, down onto the sidewalk
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
# S11/S12 read beats: push the lens onto the board text (same camera position, so the angle is unchanged) and back
CAM_AZ = (AB_LOC, *k.fit(AB_LOC, [SIGN_C["A"] + Vector((dx * SW_ / 2, 0, dz * SH_ / 2)) for dx in (-1, 1) for dz in (-1, 1)] +
                                 [Vector((SPOT["A"][0] + 0.8, SPOT["A"][1], z_)) for z_ in (0.0, 1.9)], margin=1.0))
CAM_BZ = (B_LOC, *k.fit(B_LOC, [SIGN_C["B"] + Vector((dx * SW_ / 2, 0, dz * SH_ / 2)) for dx in (-1, 1) for dz in (-1, 1)] +
                                [Vector((SPOT["B"][0] + 0.8, SPOT["B"][1], z_)) for z_ in (0.0, 1.9)], margin=1.06))
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
TOP_C = 7 * T_H - 0.025                                    # the roof of site C's 7th floor
ROOF_C = (TOWER["C"].x, LOT_Y + T_W / 2 - 0.5)             # S14: at the roof's front edge, the banners below him
FACE_C = LOT_Y + T_W / 2                                    # site C's front face (y)
DOOR15 = Vector((TOWER["C"].x + 0.0, FACE_C, T_H * 6.5 - T_H / 2 + 0.05))   # S15: the door to nowhere, top floor (bottom centre)
PLAT15 = (DOOR15.x - 1.5, FACE_C + 0.4)                    # S15: a scaffold platform at the door's right; he stands on it
JIB_C = TOWER["C"] + Vector((T_W / 2 + 0.5, T_W / 2 + 0.3, 7 * T_H + 4.0))  # the crane jib above the tower (his line)
# S14's wide must hold him on the roof (full body) and the banners
pts3 += [Vector((ROOF_C[0] + dx, ROOF_C[1], TOP_C + dz)) for dx in (-0.5, 0.5) for dz in (0.0, 2.1)]
CAM_3 = (W3_LOC, *k.fit(W3_LOC, pts3, margin=1.04))
ROOF_LOC = Vector((TOWER["C"].x + 1.2, FACE_C + 13.0, TOP_C - 1.2))   # S14: up with him — the roof and the banners below
ROOF_CAM = (ROOF_LOC, *k.fit(ROOF_LOC, [Vector((ROOF_C[0] + dx, ROOF_C[1], TOP_C + dz)) for dx in (-0.6, 0.6) for dz in (0.0, 2.6)] +
                             [Vector((TOWER["C"].x + dx, FACE_C, TOP_C - dz)) for dx in (-1.9, 1.9) for dz in (0.0, 5.8)], margin=1.08))

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
BEAT = 3.0                                                   # seconds of staging after "who does the customer pick?" (some go to one shop, many to the other)
Q1 = T[1] + F(k.dur(1) * FPS)                                # the question has been asked
T[2] = T[1] + F((k.dur(1) + 0.3 + BEAT) * FPS)
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
v_run = k.stride("MX Sprint")                                # the clip's own ground speed (m / frame)
SPR0, SPR1 = bpy.data.actions["MX Sprint"].frame_range
n_cyc = lambda dist: max(2, round(dist / max(0.05, v_run) / max(1, (SPR1 - SPR0) - 4)))     # run cycles (each overlaps the next by 4 frames)
run12 = perf.then("MX Sprint", repeat=n_cyc(RUN_D), blend=6, face=f_run, in_place=1.0)
FB = face_to(SPOT["B"], B_LOC)
RUN2_D = (Vector(SPOT["B"]) - Vector(SPOT["C"])).length
talkB = k.talk(max(14, T[4] + F(k.dur(4) * FPS) - 12 - int(perf.end)), face=FB, at=SPOT["B"], clips=CALM)
# ---- S13 site C: he sprints on from B to C (the camera trucks with him, no cut), presents its board from its left edge;
# robots and the crane build, the boss checks
f_run2 = face_to(SPOT["B"], SPOT["C"])
run13 = perf.then("MX Sprint", repeat=n_cyc(RUN2_D), blend=6, face=f_run2, in_place=1.0)
FC = face_to(SPOT["C"], C_LOC)
setC = perf.then("Breathing Idle", length=12, face=FC, at=SPOT["C"], cut_blend=6, in_place=1.0)   # the run ended exactly here: no visible jump
T[5] = int(setC.start) + 12
talkC = k.talk_until(T[5] + F(k.word(5, "that") * FPS) + 18, face=FC, clips=CALM)
# ---- end of S13 (in the pull-back): a line to the crane jib, up onto site C's roof
f_up = face_to(SPOT["C"], ROOF_C)
shootC = k.shoot(f_up)
zipC = k.zip_(18.0, f_up)
landC = k.touch(f_up, ROOF_C)
# ---- S14 on the roof of site C, full body in the wide of all three sites: counts the three things, points down at it
F14 = face_to(ROOF_C, ROOF_LOC)
T[6] = max(int(landC.start) + UPRIGHT, T[5] + F((k.dur(5) + 0.25) * FPS))
T[7] = T[6] + F((k.dur(6) + 0.3) * FPS)
talk14 = k.talk_until(T[7] - 12, face=F14, clips=CALM)
# ---- S15 (a cut): a medium shot of C's top floor: he stands on a scaffold platform beside the new door to nowhere,
# shrugs with both palms up on "why keep humans in the loop?", then talks (his right arm: chin tap, the line, the stamp)
END = T[7] + F((k.dur(7) + 0.7) * FPS)
F15 = 180.0                                                # faces +y: the camera
set15 = perf.then("Breathing Idle", length=12, face=F15, at=PLAT15, in_place=1.0)
shrug15 = perf.then("CMU 111_25 Shrug", frm=10, to=62, blend=8, face=F15, in_place=1.0)
talk15 = k.talk_until(END + 2, face=F15, clips=CALM)
perf.build()
sc.frame_end = END
print("T", T, "END", END)
w6 = lambda w, nth=0: wordf(6, w, nth)
w7 = lambda w, nth=0: wordf(7, w, nth)
T15a = int(set15.start)
BAL_AT = Vector((DOOR15.x, FACE_C + 0.6, DOOR15.z - 0.1))    # where the balcony goes (under the door)
STAMP15 = Vector((DOOR15.x - 0.95, FACE_C + 0.06, DOOR15.z + 1.3))     # beside the door, in his reach

# ------------------------------------------------------------------ body to camera on every talk beat
CAM15 = Vector((DOOR15.x - 0.4, FACE_C + 7.4, DOOR15.z + 1.0))   # S15: the medium shot of the top floor
AIMS = [([talk10], cam10[0]), ([talk101], cam101[0]), ([talkA, holdA], AB_LOC), ([talkB], B_LOC), ([talkC], C_LOC), ([talk14], ROOF_LOC),
        ([talk15], CAM15)]
aim_spans = [(int(first(gs[0]).start), int(final(gs[-1]).end), Vector(loc)) for gs, loc in AIMS]


def facing_cam(f):
    for a_, b_, p in aim_spans:
        if a_ <= f <= b_:
            return (p.x, p.y)
    h = perf.bone_world(HIPS, f)
    return (h.x, h.y - 5)


flat = lambda gs: [c_ for g in gs for c_ in (g.cycles if hasattr(g, "cycles") else [g])]
square_err = perf.square_up(flat(sum((gs for gs, _ in AIMS), [])), facing_cam)
# flat at every cut (no ramps); on the roof: the roof's height under each clip's own lowest foot
def low_rel(clip):
    return min(min(perf.bone_world(b, f).z for b in ("mixamorig:LeftToeBase", "mixamorig:RightToeBase"))
               for f in range(int(clip.start) + 4, max(int(clip.start) + 5, int(clip.end) - 2), 6))


roof_clips = perf.clips[perf.clips.index(first(landC)):perf.clips.index(final(talk14)) + 1]
plat_clips = perf.clips[perf.clips.index(first(set15)):perf.clips.index(final(talk15)) + 1]
zk = [(f_, 0.0, "const") for f_ in (1, int(setA.start), int(setC.start))]
for c_ in roof_clips:
    zk.append((int(c_.start), TOP_C - low_rel(c_), "const"))
for c_ in plat_clips:                                        # S15: the platform is at the door's sill
    zk.append((int(c_.start), DOOR15.z - low_rel(c_), "const"))
perf.root_z(zk)

# ------------------------------------------------------------------ travel
A0 = BOARD_C + Vector((BOARD_W / 2 - 0.6, 0.3, BOARD_H / 2))    # the line catches the board's top-left corner
k.web_zip(zip0, land0, A0, lift=1.2, name="S10")
# S12: the sprint, a straight run (eased in / out) along the front of site A
ra, rb = int(first(run12).start), int(final(run12).end) - 1
pA, pB = Vector((SPOT["A"][0], SPOT["A"][1], 0)), Vector((SPOT["B"][0], SPOT["B"][1], 0))
k.travel(lambda t: pA.lerp(pB, t), ra, rb, axes=(0, 1), name="S12run")                  # constant speed = the run cycle's: feet don't slide
ra2, rb2 = int(first(run13).start), int(final(run13).end) - 1
pC = Vector((SPOT["C"][0], SPOT["C"][1], 0))
k.travel(lambda t: pB.lerp(pC, t), ra2, rb2, axes=(0, 1), name="S13run")
FLOOR_GAP, N_C = 16, 7
F13_0 = T[5] + F(k.word(5, "agents") * FPS) - 30 - 2 * 16   # floors 0 and 1 are already up when we cut in
LANDS_C = [F13_0 + i * FLOOR_GAP for i in range(N_C)]
k.web_zip(zipC, landC, JIB_C, lift=1.5, name="S13roof")
for fa, fb, nm in k.travels:
    k.path_hits(fa, fb, nm)

# ------------------------------------------------------------------ feet
air = [(a_, b_) for a_, b_, n_ in k.travels if n_ not in ("S12run", "S13run")] + [(int(land0.start), int(land0.start) + 6),
                                                                      (int(landC.start), int(landC.start) + 6)]
lock_err = 0.0
for a_, b_, fl in [(1, int(zip0.start) - 1, k.floor_at(CP.x, CP.y)), (int(land0.start), int(setA.start) - 1, FL_ROAD),
                   (int(setA.start), int(setC.start) - 1, k.floor_at(*SPOT["A"])), (int(setC.start), int(zipC.start) - 1, k.floor_at(*SPOT["C"]))]:
    lock_err = max(lock_err, perf.ground_lock(a_, b_, skip=air, step=1, floor=fl))
perf.contact(int(landC.start) + 6, int(set15.start) - 1, floor=TOP_C)
perf.contact(int(set15.start) + 2, END, floor=DOOR15.z)
hips = lambda f: perf.bone_world(HIPS, int(f))

# ------------------------------------------------------------------ webs
webs = fx.WebShots(rig, fx.collection("Webs"))
W = int(perf.clip_frame(shoot0, k.hit_pk))
webs.shot("Web_S10", R_HAND, lambda f: A0, W - 4, W, int(land0.start) - 3)
shot.sfx("web_thwip", W - 3)
shot.sfx("cartwheel_whoosh", int(zip0.start) + 4)
shot.sfx("landing_thud", int(land0.start) + 5)
Wc = int(perf.clip_frame(shootC, k.hit_pk))
webs.shot("Web_S13roof", R_HAND, lambda f: JIB_C, Wc - 4, Wc, int(landC.start) - 3)
shot.sfx("web_thwip", Wc - 3)
shot.sfx("cartwheel_whoosh", int(zipC.start) + 4)
shot.sfx("landing_thud", int(landC.start) + 5)

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
dl, dr = SHOP["L"]["door"], SHOP["R"]["door"]
QUEUE = lambda i: (dr[0] - 0.35 - 0.72 * i, FRONT + 1.45)
LANE = FRONT + 2.5                                          # the outer lane of the sidewalk (they pass the queue there)
DOOR_IN = (dr[0], FRONT + 0.05)
ENTER0, ENTER_GAP = Q1 + 90, 52
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


# 1. the question is asked to an empty street; 2. a few customers go into the shop that doesn't inspect;
# 3. many more queue up at the one that does; 4. only then the answer (line 2)
DOOR_L = (dl[0], FRONT + 0.05)
for i in range(3):
    start = (SHOPX["L"] + 6.5 + 1.4 * i, FRONT + 0.5)                               # in from the left along the facade (behind him), into your shop
    spawn(f"Visitor{i}").route([(start, 0), (DOOR_L, 0)], Q1 - 40 + i * 34, phase=rw.random())
N_CUST = 11
for i in range(N_CUST):                                     # in from the street (off frame right), into their queue
    start = (SX - 9.5 - 0.9 * i, LANE + 0.35 * (i % 2))
    queue_route(spawn(f"Customer{i}"), i, Q1 - 60 + i * 24, approach=[(start, 0)], phase=rw.random())
# (nobody comes out of your shop: the broken item sits in its window, the sign flips to CLOSED)

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
CREW_END = int(set15.start) + 2
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


def stack(name, tc, n, f_first, gap, mat, crooked=0.0, seed=1, i0=0):
    """Floors lowered by the crane, one every `gap` frames: a quick drop, a thud. Returns [(floor, land, rest)]."""
    r = random.Random(seed)
    out_ = []
    offs = Vector((0, 0, 0))
    for i in range(n):
        offs = offs + Vector((r.uniform(-1, 1) * crooked, r.uniform(-1, 1) * crooked * 0.6, 0))
        rest = tc + offs + Vector((0, 0, T_H * (i + i0 + 0.5)))
        fl = box(f"{name}F{i + i0}", (T_W, T_W, T_H - 0.05), rest, mat, csite)
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


glassB = fx.material("WinGlassB", (0.12, 0.42, 0.75), rough=0.05, metallic=0.5, emit=0.25, emit_color=(0.4, 0.7, 1.0))
panelB = fx.material("AgentPanel", (0.84, 0.86, 0.9), rough=0.22, metallic=0.1)
bandB = [fx.material("AgentBandTeal", (0.1, 0.8, 0.85), rough=0.3, emit=2.0, emit_color=(0.1, 0.9, 1.0)),
         fx.material("AgentBandPink", (0.9, 0.2, 0.7), rough=0.3, emit=2.0, emit_color=(1.0, 0.25, 0.8))]
T4_0 = T[4] + 6                                              # the crane starts on "option two"
pivB = crane("CraneB", TOWER["B"], 17.0)
floorsB = stack("TowerB", TOWER["B"], 6, T4_0, 14, panelB, crooked=0.35, seed=5)
for i, (fl, land, rest) in enumerate(floorsB):                # a glowing band at the foot of every floor
    bd = box(f"TowerBBand{i}", (T_W + 0.06, T_W + 0.06, 0.16), rest + Vector((0, 0, -T_H / 2 + 0.12)), bandB[i % 2], csite)
    parent_keep(bd, fl, land + 10)
    anim.visible(bd, [(1, False), (land - 14, True)])
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
boss_c.show([(1, False), (int(first(run13).start), True)])

# ---- S14: three rolled banners at C's roof edge unroll down its front, one per thing he counts
BAN_L = 5.5
ban_top = TOP_C - 0.12
roll_m = fx.material("BannerRoll", (0.9, 0.9, 0.86), rough=0.6)
for i, (nm, word) in enumerate((("banner_headcount", "headcount"), ("banner_results", "results"), ("banner_product", "better"))):
    bx = TOWER["C"].x + 1.2 - 1.2 * i                        # left to right on screen: +x first
    piv = fx.empty(f"BannerPivot{i}", Vector((bx, FACE_C + 0.14, ban_top)), csite, 0.1)
    cloth = city.sign(f"Banner{i}", img(nm), Vector((bx, FACE_C + 0.02, ban_top - BAN_L / 2)), SN, 1.05, aspect=600 / 3000,
                      emit=0.35, offset=0.12, coll=csite)
    parent_keep(cloth, piv, 1)
    me = bpy.data.meshes.new(f"BannerRoll{i}")
    bm_ = bmesh.new()
    bmesh.ops.create_cone(bm_, cap_ends=True, segments=14, radius1=0.1, radius2=0.1, depth=1.1)
    bmesh.ops.rotate(bm_, verts=bm_.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "Y"))
    bm_.to_mesh(me)
    bm_.free()
    roll = bpy.data.objects.new(f"BannerRoll{i}", me)
    csite.objects.link(roll)
    me.materials.append(roll_m)
    f_ = w6(word) - 2
    anim.keys(piv, "scale", [(1, Vector((1, 1, 0.001)), "const"), (f_, Vector((1, 1, 0.001)), "out"), (f_ + 14, Vector((1, 1, 1)), "back")])
    anim.keys(roll, "location", [(1, Vector((bx, FACE_C + 0.2, ban_top)), "const"), (f_, Vector((bx, FACE_C + 0.2, ban_top)), "out"),
                                 (f_ + 14, Vector((bx, FACE_C + 0.2, ban_top - BAN_L)), "back")])
    shot.sfx("cartwheel_whoosh", f_)
    for o in (cloth, roll):
        anim.visible(o, [(1, False), (int(landC.start), True), (T15a, False)])
# ---- S15: the door to nowhere on C's top floor, a customer walking out of it, the balcony he webs in
fl6 = bpy.data.objects[f"TowerCF{N_C - 1}"]
win6 = bpy.data.objects.get(f"TowerCF{N_C - 1}W01")
if win6:
    anim.visible(win6, [(1, True), (T15a, False)])
dark = box("DoorwayC", (0.84, 0.04, 1.94), Vector((DOOR15.x, FACE_C + 0.03, DOOR15.z + 0.97)), holes, csite)
d_piv = fx.empty("DoorHingeC", Vector((DOOR15.x + 0.42, FACE_C + 0.08, DOOR15.z)), csite, 0.1)
d15 = box("DoorC", (0.82, 0.06, 1.9), d_piv.location + Vector((-0.41, 0, 0.95)), fx.material("DoorC", (0.85, 0.85, 0.82), rough=0.4), csite)
parent_keep(d15, d_piv, 1)
DOOR_OPEN = T[7] + 4
anim.keys(d_piv, "rotation_euler", [(1, Vector((0, 0, 0)), "const"), (DOOR_OPEN, Vector((0, 0, 0)), "out"), (DOOR_OPEN + 10, Vector((0, 0, -1.5)), "back")])
for o in (dark, d15):
    anim.visible(o, [(1, False), (T15a, True)])
shot.sfx("ui_pop", DOOR_OPEN)
# the scaffold platform he stands on: a plank at the sill, two brackets, a rail on its outer side
scaf = fx.material("Scaffold", (0.55, 0.42, 0.25), rough=0.8)
plat = [box("ScafPlank", (1.4, 0.8, 0.08), Vector((PLAT15[0], FACE_C + 0.4, DOOR15.z - 0.04)), scaf, csite)]
for j, dx in enumerate((-0.55, 0.55)):
    br = box(f"ScafBracket{j}", (0.06, 0.06, 1.1), Vector((PLAT15[0] + dx, FACE_C + 0.35, DOOR15.z - 0.45)), steel, csite)
    br.rotation_euler = (math.radians(40), 0, 0)
    plat.append(br)
plat += [box("ScafRailPost0", (0.05, 0.05, 1.05), Vector((PLAT15[0] - 0.68, FACE_C + 0.1, DOOR15.z + 0.52)), steel, csite),
         box("ScafRailPost1", (0.05, 0.05, 1.05), Vector((PLAT15[0] - 0.68, FACE_C + 0.77, DOOR15.z + 0.52)), steel, csite),
         box("ScafRail", (0.05, 0.72, 0.05), Vector((PLAT15[0] - 0.68, FACE_C + 0.43, DOOR15.z + 1.03)), steel, csite)]
for o in plat:
    anim.visible(o, [(1, False), (T15a, True)])
# the balcony: flies in on his line from below the door and locks under it
BAL = fx.empty("BalconyC", BAL_AT, csite, 0.1)
rail = fx.material("Rail", (0.92, 0.92, 0.9), rough=0.35, metallic=0.6)
bal_parts = [box("BalSlab", (1.5, 1.0, 0.12), BAL_AT + Vector((0, -0.08, 0.04)), concrete, csite)]
for j, (sx_, sy_, sz_, dx, dy, dz) in enumerate(((1.5, 0.05, 0.05, 0, 0.4, 1.05), (0.05, 1.0, 0.05, 0.73, -0.08, 1.05), (0.05, 1.0, 0.05, -0.73, -0.08, 1.05),
                                                  (0.05, 0.05, 1.0, 0.73, 0.4, 0.55), (0.05, 0.05, 1.0, -0.73, 0.4, 0.55), (0.05, 0.05, 1.0, 0, 0.4, 0.55))):
    bal_parts.append(box(f"BalRail{j}", (sx_, sy_, sz_), BAL_AT + Vector((dx, dy, dz)), rail, csite))
for o in bal_parts:
    parent_keep(o, BAL, 1)
CUZ = w7("cuz")
from_ = BAL_AT + Vector((-1.4, 0.9, -2.2))
anim.keys(BAL, "location", [(1, from_, "const"), (CUZ + 2, from_, "out"), (CUZ + 12, BAL_AT, "back")])
anim.keys(BAL, "scale", [(1, Vector((0.3, 0.3, 0.3)), "const"), (CUZ + 2, Vector((0.3, 0.3, 0.3)), "out"), (CUZ + 12, Vector((1, 1, 1)), "back")])
for o in bal_parts:
    anim.visible(o, [(1, False), (CUZ + 2, True)])
shot.sfx("web_thwip", CUZ)
shot.sfx("block_thud", CUZ + 12)
# the customer: out of the door towards the drop, stops on the edge; steps onto the balcony; leans on the rail and waves
cust = cw._spawn("boss", "DoorBoss", (DOOR15.x, FACE_C + 0.05, DOOR15.z), (0, 1), None)        # the boss, hard hat on
bacts = {a.name.split("|")[-1]: a for a in cw.src["boss"]["acts"]}
walk_ip = crew.in_place(bacts["Walk"])
crew.sequence(cust.arm, [(walk_ip, DOOR_OPEN + 4, DOOR_OPEN + 36), (bacts["Sad_Idle"], DOOR_OPEN + 36, CUZ + 14),
                         (walk_ip, CUZ + 14, CUZ + 34), (bacts["Victory_Idle"], CUZ + 34, w7("human") - 4), (bacts["Waving"], w7("human") - 4, END + 2)])
anim.keys(cust.wrap, "location", [(1, Vector((DOOR15.x, FACE_C - 0.05, DOOR15.z)), "const"), (DOOR_OPEN + 4, Vector((DOOR15.x, FACE_C - 0.05, DOOR15.z)), "lin"),
                                  (DOOR_OPEN + 36, Vector((DOOR15.x, FACE_C + 0.28, DOOR15.z)), "const"), (CUZ + 14, Vector((DOOR15.x, FACE_C + 0.28, DOOR15.z)), "lin"),
                                  (CUZ + 34, Vector((DOOR15.x, FACE_C + 0.85, DOOR15.z)), "const")])
cust.show([(1, False), (DOOR_OPEN + 4, True)])
# the crane keeps stacking floors above, unaware ("AI lets everyone ship more")
floorsC2 = stack("TowerC", TOWER["C"], 3, w7("ai") - 4, 14, blueglass, crooked=0.0, seed=8, i0=N_C)
for i, (fl, land, rest) in enumerate(floorsC2):
    windows(fl, rest, 60 + i, missing=0.0, hole=glassC, glass=glassC, appear=land - 14, landed=land + 10)
    shot.sfx("block_thud", land, gain=0.7)
anim.keys(pivC, "rotation_euler", [(f_, Vector((0, 0, 0.3 * math.sin(f_ / 8.0))), "inout") for f_ in range(T15a - 30, END + 10, 8)])
# "Human judgment and care do that": the green check beside the door, the stamp in his hand
STAMP_F = w7("human") + 2
st15 = city.sign("StampDoor", img("stamp_ok"), STAMP15, SN, 0.6, aspect=1.0, offset=0.0, alpha=True, emit=0.3, coll=csite)
anim.visible(st15, [(1, False), (STAMP_F, True)])
anim.keys(st15, "scale", [(STAMP_F, Vector((2.2, 2.2, 2.2)), "out"), (STAMP_F + 5, Vector((1, 1, 1)), "back")])
shot.sfx("ui_pop", STAMP_F)
stamp_ob = box("StampProp", (0.09, 0.09, 0.14), Vector((0, 0, 0)), fx.material("StampWood", (0.45, 0.3, 0.18), rough=0.6), csite)
to_bone(stamp_ob, rig, R_HAND, offset=(0, 0.02, 0.06))
anim.visible(stamp_ob, [(1, False), (T15a, True)])

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
T15a = int(set15.start)
SEQ = [(w6("headcount") - 6, "flat"), (w6("headcount") - 2, "one"), (w6("results") - 2, "two"), (w6("better") - 2, "three"),
       (w6("only") - 6, "three"), (w6("only"), "flat"), (w6("human") - 8, "point"), (w6("stay") + 12, "point"), (w6("stay") + 20, "flat"),
       (T15a, "flat"), (w7("loop") - 2, "point"), (w7("cuz") - 4, "flat"), (w7("human") - 10, "flat"), (w7("human") - 6, "fist"),
       (END - 2, "fist")]
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
CHEST = lambda f: cuh(f) + fwd * 0.26 + Vector((0.16, 0, 0.08))          # in front of his chest, his right side (+x: he faces +y)
# ---- S14/S15 the right-arm gestures (count, chin, temple tap, hand on chest): no IK here — the legacy solver flipped
# this arm (hand behind the shoulder, elbow up: the "dinosaur"). Instead a two-bone solve per frame (elbow down and
# out), plus the hand's own rotation, keyed on a REPLACE arm layer over the talk clips, eased in and out.
UP, TOWARD, BACK = Vector((0, 0, 1)), Vector((0, 1, 0)), Vector((0, -1, 0))   # he faces +y: his right is +x
RWM = rig.matrix_world
RW3, RWi = RWM.to_3x3(), RWM.inverted()
ARM_B = ["mixamorig:RightShoulder", "mixamorig:RightArm", "mixamorig:RightForeArm", "mixamorig:RightHand"]
rest3 = {n: rig.data.bones[n].matrix_local.to_3x3() for n in ARM_B}
LEN_UP, LEN_FA = rig.pose.bones[ARM_B[1]].length, rig.pose.bones[ARM_B[2]].length
SHW = lambda f: perf.bone_world(ARM_B[1], f)
BAL_AT = Vector((DOOR15.x, FACE_C + 0.6, DOOR15.z - 0.1))    # where the balcony goes (under the door)
STAMP15 = Vector((DOOR15.x - 0.95, FACE_C + 0.06, DOOR15.z + 1.3))     # beside the door, in his reach
_d = (BAL_AT - SHW(w7("cuz"))).normalized()
_z = (-UP - _d * (-UP).dot(_d)).normalized()
WEB_AXES = (_d.cross(_z), _d, _z)                             # the arm along the shot, palm down
_py = Vector((0, 0.6, -0.8)).normalized()
seg = lambda a_, b_: max(4, int(b_) - int(a_))
GEST = [  # start, ramp, hold, wrist target (world), elbow pull, hand axes (X, Y = along the fingers, Z = palm side)
    # S14 on the roof: the count, hand raised high (palm to the camera); then pointing down at his own tower
    (w6("headcount") - 10, 8, seg(w6("headcount") - 2, w6("only") - 20), lambda f: SHW(f) + Vector((0.1, 0.12, 0.38)),
     Vector((1, 0, -0.3)), (Vector((-1, 0, 0)), UP, TOWARD)),
    (w6("human") - 10, 7, seg(w6("human") - 3, w6("stay") + 8), lambda f: SHW(f) + Vector((0.06, 0.42, -0.2)),
     Vector((0.6, -0.3, -1)), (_py.cross(Vector((-1, 0, 0))), _py, Vector((-1, 0, 0)))),
    # S15 on the platform (the shrug is the clip, both palms): a chin tap, the line to the balcony, the stamp
    (w7("loop") - 4, 4, seg(w7("loop"), w7("cuz") - 8), lambda f: HD(f) + fwd * 0.12 + Vector((0.02, 0, -0.13)),
     Vector((0.5, 0, -1)), (Vector((1, 0, 0)), UP, BACK)),
    (w7("cuz") - 3, 3, 14, lambda f: SHW(f) + _d * 0.45, Vector((0.5, 0, -1)), WEB_AXES),
    (w7("human") - 8, 6, 20, lambda f: STAMP15 + Vector((0, 0.1, -0.06)), Vector((0.6, 0, -1)), (Vector((1, 0, 0)), UP, BACK)),
]


def solve(f, tgt, pull, axes):
    """Armature-space rotations for shoulder (as is), upper arm, forearm, hand at frame f."""
    sc.frame_set(f)
    pbs = rig.pose.bones
    M = {n: pbs[n].matrix.to_3x3() for n in ARM_B}
    S = RWi @ (RWM @ pbs[ARM_B[1]].head)
    T = RWi @ tgt(f)
    P = (RW3.inverted() @ pull).normalized()
    d = T - S
    L = min(d.length, (LEN_UP + LEN_FA) * 0.98)
    u = d.normalized()
    ca = max(-1.0, min(1.0, (LEN_UP ** 2 + L ** 2 - LEN_FA ** 2) / (2 * LEN_UP * L)))
    v = (P - u * P.dot(u)).normalized()
    E = S + (u * ca + v * math.sqrt(1 - ca * ca)) * LEN_UP
    T = S + u * L
    r1 = M[ARM_B[1]].col[1].normalized().rotation_difference((E - S).normalized()).to_matrix()
    up = r1 @ M[ARM_B[1]]
    fa0 = r1 @ M[ARM_B[2]]
    fa = fa0.col[1].normalized().rotation_difference((T - E).normalized()).to_matrix() @ fa0
    X, Y, Z = (Vector(a_).normalized() for a_ in axes)
    hand = RW3.inverted() @ Matrix((X, Y, Z)).transposed()
    return {ARM_B[0]: M[ARM_B[0]], ARM_B[1]: up, ARM_B[2]: fa, ARM_B[3]: hand}


GEST.sort(key=lambda g: g[0])
for g0, g1 in zip(GEST, GEST[1:]):                           # one layer: the spans must not overlap
    assert int(g0[0]) + 2 * g0[1] + g0[2] < int(g1[0]), ("gestures overlap", g0[0], g1[0])
arm_act = bpy.data.actions.new("ArmGestures")
keyed = []
for f0, ramp, hold, tgt, pull, axes in GEST:
    for f in range(int(f0), int(f0) + 2 * ramp + hold + 1, 2):
        keyed.append((f, solve(f, tgt, pull, axes)))
ad.action = arm_act
if hasattr(ad, "action_slot") and arm_act.slots:
    ad.action_slot = arm_act.slots[0]
for f, Ms in keyed:
    for i, n in enumerate(ARM_B[1:], start=1):
        par = ARM_B[i - 1]
        basis = (rest3[n].inverted() @ rest3[par]) @ Ms[par].inverted() @ Ms[n]
        pbn = rig.pose.bones[n]
        pbn.rotation_quaternion = basis.to_quaternion()
        pbn.keyframe_insert("rotation_quaternion", frame=f)
if hasattr(arm_act, "slots") and arm_act.slots and not ad.action_slot:
    ad.action_slot = arm_act.slots[0]
ad.action = keep_action
arm_tr = ad.nla_tracks.new()
arm_tr.name = "ZZZ Arm gestures"
for f0, ramp, hold, tgt, pull, axes in GEST:
    a_, b_ = int(f0), int(f0) + 2 * ramp + hold
    st = arm_tr.strips.new(f"Arm{a_}", a_, arm_act)
    if hasattr(st, "action_slot") and arm_act.slots:
        st.action_slot = arm_act.slots[0]
    st.action_frame_start, st.action_frame_end = a_, b_
    st.frame_start, st.frame_end = a_, b_
    st.blend_type = "REPLACE"
    st.use_auto_blend = False
    st.extrapolation = "NOTHING"
    st.use_animated_influence = True
    for f_, v_ in ((a_, 0.0), (a_ + ramp, 1.0), (b_ - ramp, 1.0), (b_, 0.0)):
        st.influence = v_
        st.keyframe_insert("influence", frame=int(f_))

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
# read: push onto site A's board text, hold it, then back out to the wide before the sprint
k.at(int(talkA.start) + 6, CAM_AZ[0], CAM_AZ[1], "inout")
cam.lens(int(talkA.start) + 6, round(CAM_AZ[2]), "inout")
k.at(ra - 18, CAM_AZ[0], CAM_AZ[1], "inout")             # held on site A until just before the sprint, then out ...
cam.lens(ra - 18, round(CAM_AZ[2]), "inout")
k.at(ra - 2, CAM_A[0] + Vector((0, -0.2, 0)), CAM_A[1], "inout")      # ... and across to site B with him
cam.lens(ra - 2, round(CAM_A[2]), "inout")
k.at(rb + 10, CAM_B[0], CAM_B[1], "inout")
cam.lens(rb + 10, round(CAM_B[2]), "inout")
# read: push onto site B's board text, hold, then the existing pull to CAM_B (on "subtle") brings it back out
fBZ = max(rb + 14, int(talkB.start) + 8)
k.at(fBZ, CAM_B[0], CAM_B[1], "inout")
cam.lens(fBZ, round(CAM_B[2]), "inout")
k.at(fBZ + 34, CAM_BZ[0], CAM_BZ[1], "inout")
cam.lens(fBZ + 34, round(CAM_BZ[2]), "inout")
k.at(fBZ + 84, CAM_BZ[0], CAM_BZ[1], "inout")
cam.lens(fBZ + 84, round(CAM_BZ[2]), "inout")
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
CUTS.append(("B back", RUN_F - 5))
# S13: site C (board, him, the robots, the boss, the lower floors), widening as the tower goes up; on "That team
# beats..." the pull-back to all three sites side by side
C_TOP = lambda f: T_H * max(3, min(N_C, sum(1 for lf in LANDS_C if lf <= f))) + 0.8      # the top of the tower so far
c_fit = lambda f: k.fit(C_LOC, ptsC_lo + [TOWER["C"] + Vector((dx * T_W / 2, 0, C_TOP(f))) for dx in (-1, 1)], margin=1.06)
c_keys = list(range(int(setC.start) + 10, THAT - 4, 8)) + [THAT - 4]      # the first key is where the camera arrives (10 frames after his run ends)
c_sm = {f: c_fit(f) for f in range(int(setC.start) - 16, THAT + 20)}
k.at(ra2 - 2, CAM_B[0] + Vector((0, -0.2, 0)), CAM_B[1], "inout")      # trucks right with his sprint to site C (no cut)
cam.lens(ra2 - 2, round(CAM_B[2]), "inout")
for f in c_keys:                                             # widens with the tower, the ground always in frame
    tg = sum((c_sm[q][0] for q in range(f - 16, f + 17)), Vector()) / 33
    ln = sum(c_sm[q][1] for q in range(f - 16, f + 17)) / 33
    k.at(f, C_LOC, tg, "lin")
    cam.lens(f, ln, "lin")
c_last = c_sm[THAT - 4]
k.at(int(shootC.start), C_LOC, c_last[0], "inout")             # hold the site C framing while he aims the line
cam.lens(int(shootC.start), c_last[1], "inout")
k.at(int(landC.start) + 12, ROOF_CAM[0], ROOF_CAM[1], "inout")   # then up with him: the roof, the banners below him
cam.lens(int(landC.start) + 12, round(ROOF_CAM[2]), "inout")
k.at(int(set15.start) - 1, ROOF_CAM[0] + Vector((0, -0.5, 0)), ROOF_CAM[1], "lin")
cam.lens(int(set15.start) - 1, round(ROOF_CAM[2]), "const")
# S15: the medium shot of C's top floor (him on the line, the door, the balcony); it tilts up to the floors still
# stacking above on "AI lets everyone ship more", and back down for the customer on the balcony
T15a = int(set15.start)
tgt15 = Vector((DOOR15.x - 0.45, FACE_C + 0.3, DOOR15.z + 1.05))
up15 = Vector((0, 0, 1.3))
cam.lens(T15a, 35, "const")
k.at(T15a, CAM15, tgt15, "lin", cut=True)
for f_, off in ((w7("ai") - 8, Vector()), (w7("ai") + 10, up15), (w7("human") - 10, up15), (w7("human") + 6, Vector())):
    k.at(f_, CAM15 + off * 0.3, tgt15 + off, "inout")
k.at(END, CAM15 + Vector((0, -0.2, 0)), tgt15, "lin")
CUTS.append(("S15 top floor", T15a))
cam.shake(int(land0.start) + 5, amp=0.04, dur=8)
FSTOPS = [(1, 8.0), (T[2], 8.0), (int(setA.start), 8.0), (SUB + 22, 4.0), (RUN_F - 5, 8.0), (int(setC.start), 8.0), (T15a, 5.6)]
for f_, v_ in sorted(FSTOPS):
    anim.key(cam.cam.data.dof, "aperture_fstop", int(f_), v_, ease="const")
TALKS = [talk10, talk101, talkA, holdA, talkB, talkC, talk14, talk15]
office.face_camera(cam.cam, [(int(first(g).start) + 4, int(final(g).end) - 2) for g in TALKS], amount=0.55)
office.nod(w6("stay"), depth=0.6)
office.nod(w7("cuz") + 6, depth=-0.4)
for kk in range(3):                                          # a light head shake on "doesn't make more great products"
    f_ = w7("doesn") + kk * 7
    anim.keys(office.cam_eye, "location", [(f_, 0.0, "inout"), (f_ + 3, 0.35 * (-1) ** kk, "inout"), (f_ + 7, 0.0, "inout")], index=0)
anim.keys(office.cam_eye, "location", [(T[2] - 14, 0.0, "inout"), (T[2] - 6, 0.5, "inout"), (T[2] + 2, 0.0, "inout")], index=0)   # the head tilt (S10)
anim.keys(office.cam_eye, "location", [(w7("loop") - 8, 0.0, "inout"), (w7("loop"), -0.45, "inout"), (w7("cuz") - 4, -0.45, "inout"),
                                       (w7("cuz") + 4, 0.0, "inout")], index=0)                                      # the tilt (chin tap)
fx.char_lights(rig, cam.cam, key=170.0, rim=340.0)
# S10: he presents your shop on "you ship without inspection", theirs on "your competitor"; S10.1 a thumb at their queue
fL, fR = wordf(1, "without"), wordf(1, "competitor")
pL = Vector((SHOPX["L"], FRONT + 0.6, 2.2))
pR = Vector((SHOPX["R"], FRONT + 0.6, 2.2))
office.present(fL - 6, pL, side=k.gesture_side(pL, hips(fL), cam10[0]), hold=max(8, fR - fL - 16), ramp=7, amount=0.6)
office.present(fR - 4, pR, side=k.gesture_side(pR, hips(fR), cam10[0]), hold=max(8, B_WHO - fR - 12), ramp=7, amount=0.6)
qp = Vector((QUEUE(2)[0], QUEUE(2)[1], 1.4))
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
               (T[7], dict(Wide=0.4)), (w7("loop") - 4, dict(Wide=0.0, Squint=0.55)), (w7("cuz") - 2, dict(Squint=0.0, Wide=1.0)),
               (w7("ai"), dict(Wide=0.3)), (w7("doesn"), dict(Wide=0.0, Angry=0.35)), (w7("human"), dict(Angry=0.0, Squint=0.3))):
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
OVER = []                                                       # no key-phrase captions: subtitles come from 06_assemble
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
