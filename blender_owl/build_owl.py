"""Build the controllable cube-owl character + a low-poly street set.

Run headless:
    blender -b --factory-startup --python build_owl.py

Outputs (next to this file):
    owl_rig.blend     owl character only (collection "Owl", armature "OwlRig")
    owl_street.blend  owl + street set + camera rig + lighting

Source model: "Low poly default cube owl model (Rigged)" from Sketchfab
(source/owl1.blend). Its body, legs, pupils and tail feathers are reused;
the face (sclera, brows, two-piece beak), ear tufts and wings are added so
the owl can emote, talk and gesture. The original 4-bone leg rig is replaced
by a full control rig (see RIG.md).
"""
import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "source", "owl1.blend")


# ----------------------------------------------------------------- helpers
def material(name, color, rough=0.55, emit=0.0, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    if m.node_tree is None:
        m.use_nodes = True
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        bsdf = m.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        out = next(n for n in m.node_tree.nodes if n.type == "OUTPUT_MATERIAL")
        m.node_tree.links.new(bsdf.outputs[0], out.inputs[0])
    c = (*color, 1.0)
    bsdf.inputs["Base Color"].default_value = c
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    if emit:
        bsdf.inputs["Emission Color"].default_value = c
        bsdf.inputs["Emission Strength"].default_value = emit
    m.diffuse_color = c
    return m


def new_obj(name, bm, mats, coll, smooth=False, loc=None):
    me = bpy.data.meshes.new(name)
    if smooth:
        for f in bm.faces:
            f.smooth = True
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    if loc is not None:
        ob.location = loc
    return ob


def bm_box(bm, center, size, mi=0):
    r = bmesh.ops.create_cube(bm, size=1.0)
    vs = r["verts"]
    bmesh.ops.scale(bm, vec=Vector(size), verts=vs)
    bmesh.ops.translate(bm, vec=Vector(center), verts=vs)
    for f in {f for v in vs for f in v.link_faces}:
        f.material_index = mi
    return vs


def bm_cyl(bm, center, r1, r2, depth, seg=12, mi=0, matrix=None):
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                                radius1=r1, radius2=r2, depth=depth)
    vs = res["verts"]
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=vs)
    bmesh.ops.translate(bm, vec=Vector(center), verts=vs)
    for f in {f for v in vs for f in v.link_faces}:
        f.material_index = mi
    return vs


def bm_ico(bm, center, radius, subdiv=1, scale=(1, 1, 1), mi=0):
    res = bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=radius)
    vs = res["verts"]
    bmesh.ops.scale(bm, vec=Vector(scale), verts=vs)
    bmesh.ops.translate(bm, vec=Vector(center), verts=vs)
    for f in {f for v in vs for f in v.link_faces}:
        f.material_index = mi
    return vs


ROT_FACE = Matrix.Rotation(math.pi / 2, 4, "X")  # cylinder axis Z -> Y (faces the camera)


# ------------------------------------------------------------------- owl
def build_owl(scene):
    coll = bpy.data.collections.new("Owl")
    scene.collection.children.link(coll)

    with bpy.data.libraries.load(SRC, link=False) as (src, dst):
        dst.objects = list(src.objects)
    objs = {o.name: o for o in dst.objects if o}
    for o in objs.values():
        coll.objects.link(o)

    # Bake every mesh into world space, drop the old armature, turn the owl to
    # face -Y (towards the default camera) and stand it on z=0.
    R = Matrix.Rotation(-math.pi / 2, 4, "Z")
    meshes = [o for o in objs.values() if o.type == "MESH"]
    bpy.context.view_layer.update()
    for o in meshes:
        if o.data.users > 1:
            o.data = o.data.copy()
        mw = o.matrix_world.copy()
        for m in list(o.modifiers):
            o.modifiers.remove(m)
        o.parent = None
        o.data.transform(R @ mw)
        o.matrix_world = Matrix.Identity(4)
        o.vertex_groups.clear()
    for n in ("Armature", "Camera", "Light"):
        if n in objs:
            bpy.data.objects.remove(objs.pop(n))

    body = objs["Body"]
    xs = [v.co.x for v in body.data.vertices]
    ys = [v.co.y for v in body.data.vertices]
    zs = [v.co.z for v in body.data.vertices]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    minz = min(v.co.z for o in meshes for v in o.data.vertices)
    shift = Matrix.Translation((-cx, -cy, -minz))
    for o in meshes:
        o.data.transform(shift)
    ZC = (min(zs) + max(zs)) / 2 - minz          # body centre height
    HALF = (max(zs) - min(zs)) / 2               # half body size (~1)
    FY = min(ys) - cy                            # front face plane (-Y)

    # Body: remove the little stub wings baked into the cube (real wings are
    # added below), fill the holes, bevel for a soft toy-like cube.
    bm = bmesh.new()
    bm.from_mesh(body.data)
    stub = [v for v in bm.verts if abs(v.co.x) > HALF + 0.01]
    bmesh.ops.delete(bm, geom=stub, context="VERTS")
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(body.data)
    bm.free()
    bev = body.modifiers.new("Bevel", "BEVEL")
    bev.width, bev.segments, bev.harden_normals = 0.14, 4, True
    bev.limit_method = "ANGLE"

    # palette
    M = dict(
        body=material("Owl_Body", (0.30, 0.15, 0.06), 0.6),
        feather=material("Owl_Feather", (0.16, 0.07, 0.03), 0.7),
        disc=material("Owl_FaceDisc", (0.93, 0.80, 0.60), 0.6),
        belly=material("Owl_Belly", (0.80, 0.62, 0.40), 0.65),
        sclera=material("Owl_Sclera", (0.97, 0.97, 0.95), 0.3),
        pupil=material("Owl_Pupil", (0.01, 0.01, 0.012), 0.15),
        glint=material("Owl_Glint", (1, 1, 1), 0.2, emit=3.0),
        beak=material("Owl_Beak", (1.0, 0.55, 0.08), 0.4),
        brow=material("Owl_Brow", (0.10, 0.05, 0.02), 0.6),
        leg=material("Owl_Leg", (0.95, 0.55, 0.12), 0.5),
    )
    body.data.materials.clear()
    body.data.materials.append(M["body"])

    parts = {}  # object -> bone name
    parts[body] = "body"

    # legs: original cylinders (upper + foot) per side; owl's left = +X
    for n in ("Cylinder", "Cylinder.001", "Cylinder.002", "Cylinder.003"):
        o = objs[n]
        o.data.materials.clear()
        o.data.materials.append(M["leg"])
        side = "L" if sum(v.co.x for v in o.data.vertices) > 0 else "R"
        o.name = f"Owl_Leg{'Upper' if n in ('Cylinder', 'Cylinder.002') else 'Foot'}_{side}"
        parts[o] = f"leg_{side}"
    LEGX = abs(sum(v.co.x for v in objs["Cylinder"].data.vertices) / len(objs["Cylinder"].data.vertices))

    # tail feathers
    for n in ("Tail feather1", "Tail feather2", "Tail feather3"):
        o = objs[n]
        o.data.materials.clear()
        o.data.materials.append(M["feather"])
        parts[o] = "tail"

    # pupils: reuse the original glossy black eyes, smaller and flattened
    EX, EZ = 0.46, ZC + 0.36
    for n, side, sx in (("Eye2", "L", 1), ("Eye1", "R", -1)):
        o = objs[n]
        vs = o.data.vertices
        c = sum((v.co for v in vs), Vector()) / len(vs)
        tgt = Vector((sx * EX, FY - 0.06, EZ - 0.02))
        o.data.transform(Matrix.Translation(tgt) @ Matrix.Diagonal((0.85, 0.5, 0.85, 1)) @ Matrix.Translation(-c))
        o.data.materials.clear()
        o.data.materials.append(M["pupil"])
        o.name = f"Owl_Pupil_{side}"
        parts[o] = f"pupil_{side}"
    bpy.data.objects.remove(objs["Nose"])

    for side, sx in (("L", 1), ("R", -1)):
        # facial disc (two overlapping cream circles make the owl "mask")
        bm = bmesh.new()
        bm_cyl(bm, (sx * 0.44, FY - 0.005, ZC + 0.30), 0.47, 0.47, 0.02, seg=32, matrix=ROT_FACE)
        parts[new_obj(f"Owl_Disc_{side}", bm, [M["disc"]], coll)] = "body"
        # sclera
        bm = bmesh.new()
        bm_cyl(bm, (sx * EX, FY - 0.02, EZ), 0.30, 0.30, 0.04, seg=32,
               matrix=Matrix.Diagonal((1, 1, 1.08, 1)) @ ROT_FACE)
        parts[new_obj(f"Owl_Sclera_{side}", bm, [M["sclera"]], coll, smooth=True)] = f"blink_{side}"
        # eye glint
        bm = bmesh.new()
        bm_ico(bm, (sx * EX + 0.06, FY - 0.13, EZ + 0.06), 0.045, 2)
        parts[new_obj(f"Owl_Glint_{side}", bm, [M["glint"]], coll, smooth=True)] = f"pupil_{side}"
        # brow
        bm = bmesh.new()
        bm_box(bm, (sx * EX, FY - 0.04, ZC + 0.79), (0.38, 0.06, 0.085))
        parts[new_obj(f"Owl_Brow_{side}", bm, [M["brow"]], coll)] = f"brow_{side}"
        # ear tuft (4-sided cone, flattened, leaning outwards)
        bm = bmesh.new()
        bm_cyl(bm, (0, 0, 0.26), 0.22, 0.0, 0.52, seg=4,
               matrix=Matrix.Rotation(math.pi / 4, 4, "Z"))
        bmesh.ops.transform(bm, verts=bm.verts, matrix=
                            Matrix.Translation((sx * 0.70, -0.35, ZC + HALF - 0.08))
                            @ Matrix.Rotation(sx * 0.42, 4, "Y")
                            @ Matrix.Diagonal((1, 0.45, 1, 1)))
        parts[new_obj(f"Owl_Tuft_{side}", bm, [M["feather"]], coll)] = f"tuft_{side}"
        # wing: tapered slab hanging from the shoulder
        bm = bmesh.new()
        vs = bm_box(bm, (0, 0, 0), (1, 1, 1))
        for v in vs:
            top = v.co.z > 0
            v.co.x *= 0.15
            v.co.y = v.co.y * 2 * (0.46 if top else 0.20) + (0.0 if top else 0.10)
            v.co.z = 0.12 if top else -1.08
        bmesh.ops.transform(bm, verts=bm.verts, matrix=
                            Matrix.Translation((sx * (HALF + 0.08), 0.05, ZC + 0.18))
                            @ Matrix.Rotation(sx * 0.10, 4, "Y"))
        wing = new_obj(f"Owl_Wing_{side}", bm, [M["feather"]], coll)
        wb = wing.modifiers.new("Bevel", "BEVEL")
        wb.width, wb.segments = 0.04, 2
        parts[wing] = f"wing_{side}"

    # belly patch
    bm = bmesh.new()
    bm_cyl(bm, (0, FY - 0.004, ZC - 0.48), 0.55, 0.55, 0.02, seg=32,
           matrix=Matrix.Diagonal((1.3, 1, 0.75, 1)) @ ROT_FACE)
    parts[new_obj("Owl_Belly", bm, [M["belly"]], coll)] = "body"
    # belly chevrons (little "v" feather marks)
    bm = bmesh.new()
    for (bx, bz) in ((-0.3, -0.35), (0.3, -0.35), (0.0, -0.55), (-0.45, -0.68), (0.45, -0.68)):
        for s in (-1, 1):
            vs = bm_box(bm, (0, 0, 0), (0.16, 0.02, 0.035))
            bmesh.ops.transform(bm, verts=vs, matrix=
                                Matrix.Translation((bx + s * 0.06, FY - 0.02, ZC + bz))
                                @ Matrix.Rotation(-s * 0.6, 4, "Y"))
    parts[new_obj("Owl_Chevrons", bm, [M["feather"]], coll)] = "body"

    # two-piece beak: upper (hinged at top) + jaw (opens for talking)
    def beak_mesh(name, top, bot, w, tip_y, tip_z):
        bm = bmesh.new()
        a = bm.verts.new((-w, FY, top)); b = bm.verts.new((w, FY, top))
        c = bm.verts.new((0, FY, bot)); d = bm.verts.new((0, FY - tip_y, tip_z))
        for f in ((a, b, c), (a, d, b), (b, d, c), (c, d, a)):
            bm.faces.new(f)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return new_obj(name, bm, [M["beak"]], coll)
    parts[beak_mesh("Owl_Beak", ZC + 0.16, ZC - 0.16, 0.15, 0.22, ZC + 0.02)] = "beak"
    parts[beak_mesh("Owl_Jaw", ZC - 0.04, ZC - 0.30, 0.12, 0.16, ZC - 0.16)] = "jaw"
    bm = bmesh.new()
    bm_cyl(bm, (0, FY - 0.003, ZC - 0.08), 0.13, 0.13, 0.01, seg=16,
           matrix=Matrix.Diagonal((1, 1, 1.3, 1)) @ ROT_FACE)
    parts[new_obj("Owl_Mouth", bm, [material("Owl_MouthIn", (0.25, 0.04, 0.03), 0.6)], coll)] = "face"

    # ------------------------------------------------------------ armature
    arm_data = bpy.data.armatures.new("OwlRig")
    rig = bpy.data.objects.new("OwlRig", arm_data)
    coll.objects.link(rig)
    rig.show_in_front = True
    arm_data.display_type = "STICK"
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_data.edit_bones

    def bone(name, head, parent=None, length=0.3, inherit_scale="FULL"):
        b = eb.new(name)
        b.head = Vector(head)
        b.tail = Vector(head) + Vector((0, 0, length))
        b.roll = 0
        if parent:
            b.parent = eb[parent]
        b.inherit_scale = inherit_scale
        return b

    # every bone points +Z with roll 0, so pose channels mean:
    #   loc.x = right(+X)  loc.y = up(+Z)  loc.z = towards camera(-Y)
    #   rot.x = pitch (+ nods forward)  rot.y = yaw (+ turns to owl's left/screen right)
    #   rot.z = roll in the face plane (+ tilts top towards screen left)
    bone("root", (0, 0, 0), length=0.8)
    bone("spin", (0, 0, ZC), "root", 0.5)
    bone("body", (0, 0, ZC - HALF), "spin", HALF)
    bone("face", (0, FY, ZC + 0.3), "body", 0.25)
    for side, sx in (("L", 1), ("R", -1)):
        bone(f"eye_{side}", (sx * EX, FY, EZ), "face", 0.2)
        bone(f"blink_{side}", (sx * EX, FY, EZ), f"eye_{side}", 0.18)
        bone(f"pupil_{side}", (sx * EX, FY, EZ), f"blink_{side}", 0.15)
        bone(f"brow_{side}", (sx * EX, FY, ZC + 0.79), "face", 0.15)
        bone(f"tuft_{side}", (sx * 0.70, -0.35, ZC + HALF - 0.08), "body", 0.3)
        bone(f"wing_{side}", (sx * (HALF + 0.08), 0.05, ZC + 0.18), "body", 0.3)
        bone(f"leg_{side}", (sx * LEGX, 0, ZC - HALF), "body", 0.25, inherit_scale="NONE")
    bone("beak", (0, FY, ZC + 0.16), "face", 0.15)
    bone("jaw", (0, FY, ZC - 0.04), "face", 0.12)
    bone("tail", (0, -FY, ZC - 0.45), "body", 0.3)
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in rig.pose.bones:
        pb.rotation_mode = "XYZ"
    rig["body_center"] = ZC
    rig["front_y"] = FY

    bpy.context.view_layer.update()
    for o, bname in parts.items():
        mw = o.matrix_world.copy()
        o.parent = rig
        o.parent_type = "BONE"
        o.parent_bone = bname
        bpy.context.view_layer.update()
        o.matrix_world = mw
    return rig, coll


# ----------------------------------------------------------------- street
def build_street(scene):
    rnd = random.Random(7)
    coll = bpy.data.collections.new("Street")
    scene.collection.children.link(coll)

    # paving: brick texture on object coordinates
    pav = material("Street_Paving", (0.72, 0.70, 0.66), 0.85)
    nt = pav.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Color1"].default_value = (0.74, 0.72, 0.68, 1)
    br.inputs["Color2"].default_value = (0.66, 0.64, 0.60, 1)
    br.inputs["Mortar"].default_value = (0.45, 0.44, 0.42, 1)
    br.inputs["Scale"].default_value = 0.35
    br.inputs["Mortar Size"].default_value = 0.03
    nt.links.new(tc.outputs["Object"], br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], bsdf.inputs["Base Color"])

    asphalt = material("Street_Asphalt", (0.10, 0.10, 0.11), 0.9)
    nt = asphalt.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.5
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.07, 0.07, 0.08, 1)
    ramp.color_ramp.elements[1].color = (0.15, 0.15, 0.16, 1)
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    curb = material("Street_Curb", (0.55, 0.55, 0.55), 0.8)
    paint = material("Street_Paint", (0.95, 0.93, 0.85), 0.6)
    yellow = material("Street_Yellow", (0.98, 0.78, 0.15), 0.6)
    glass = material("Street_Glass", (0.20, 0.32, 0.45), 0.08, metallic=0.3)
    glass_lit = material("Street_GlassLit", (1.0, 0.82, 0.5), 0.2, emit=1.2)
    trim = material("Street_Trim", (0.95, 0.94, 0.90), 0.6)
    dark = material("Street_Dark", (0.12, 0.12, 0.13), 0.5)
    trunk = material("Street_Trunk", (0.30, 0.18, 0.10), 0.9)
    leaf = material("Street_Leaf", (0.30, 0.55, 0.22), 0.8)
    leaf2 = material("Street_Leaf2", (0.42, 0.65, 0.25), 0.8)
    lamp = material("Street_LampGlow", (1.0, 0.85, 0.55), 0.3, emit=4.0)
    red = material("Street_Red", (0.80, 0.12, 0.10), 0.4)
    teal = material("Street_Teal", (0.10, 0.55, 0.55), 0.35)
    blue = material("Street_Blue", (0.15, 0.30, 0.70), 0.45)
    wood = material("Street_Wood", (0.55, 0.34, 0.18), 0.7)
    far = material("Street_Far", (0.62, 0.70, 0.80), 0.9)

    # ground slabs.  Sidewalk top is z=0 (owl walks at y~0), road sits lower.
    bm = bmesh.new(); bm_box(bm, (0, -6, -0.5), (240, 20, 1.0))
    new_obj("Sidewalk", bm, [pav], coll)
    bm = bmesh.new(); bm_box(bm, (0, 4.25, -0.25), (240, 0.5, 0.5))
    new_obj("Curb", bm, [curb], coll)
    bm = bmesh.new(); bm_box(bm, (0, 13.25, -0.6), (240, 17.5, 0.5))
    new_obj("Road", bm, [asphalt], coll)
    bm = bmesh.new(); bm_box(bm, (0, 22.25, -0.25), (240, 0.5, 0.5))
    new_obj("CurbFar", bm, [curb], coll)
    bm = bmesh.new(); bm_box(bm, (0, 26, -0.5), (240, 7.5, 1.0))
    new_obj("SidewalkFar", bm, [pav], coll)
    # lane markings + crosswalk
    bm = bmesh.new()
    for x in range(-110, 111, 12):
        if abs(x - 24) > 8:
            bm_box(bm, (x, 13.25, -0.34), (6, 0.35, 0.02))
    for i in range(7):
        bm_box(bm, (24, 6.0 + i * 2.5, -0.34), (6, 1.3, 0.02))
    new_obj("RoadPaint", bm, [paint], coll)

    # buildings along the far sidewalk
    palette = [(0.90, 0.52, 0.42), (0.97, 0.82, 0.50), (0.55, 0.72, 0.84),
               (0.72, 0.82, 0.62), (0.94, 0.72, 0.76), (0.86, 0.80, 0.72),
               (0.80, 0.62, 0.86)]
    x = -95.0
    i = 0
    while x < 95:
        w = rnd.choice((10, 12, 14, 16))
        floors = rnd.randint(3, 6)
        h = floors * 5 + 1.5
        cx = x + w / 2
        col = material(f"Street_Facade{i}", palette[i % len(palette)], 0.85)
        awn = material(f"Street_Awning{i}", palette[(i + 3) % len(palette)], 0.6)
        bm = bmesh.new()
        front = 30.0
        bm_box(bm, (cx, front + 6, h / 2), (w - 0.3, 12, h), 0)            # mass
        bm_box(bm, (cx, front - 0.15, h + 0.3), (w, 0.9, 0.6), 1)           # cornice
        bm_box(bm, (cx, front - 0.05, 0.35), (w - 0.3, 0.3, 0.7), 1)        # base trim
        # ground floor: shop window, door, awning
        bm_box(bm, (cx - w * 0.15, front - 0.05, 2.2), (w * 0.5, 0.2, 2.8), 3 if rnd.random() < 0.5 else 2)
        bm_box(bm, (cx + w * 0.30, front - 0.05, 1.8), (2.0, 0.2, 3.6), 5)
        aw = bm_box(bm, (cx - w * 0.05, front - 1.0, 4.4), (w * 0.8, 2.0, 0.15), 4)
        for v in aw:
            if v.co.y < front - 1.0:
                v.co.z -= 0.7
        # upper floor windows
        cols = int(w // 3.5)
        for f in range(1, floors):
            for c in range(cols):
                wx = cx - w / 2 + (c + 0.5) * (w / cols)
                wz = f * 5 + 2.4
                lit = rnd.random() < 0.18
                bm_box(bm, (wx, front - 0.08, wz), (1.6, 0.16, 2.4), 3 if lit else 2)
                bm_box(bm, (wx, front - 0.2, wz - 1.3), (2.0, 0.4, 0.2), 1)
        new_obj(f"Building{i}", bm, [col, trim, glass, glass_lit, awn, dark], coll)
        x += w
        i += 1

    # distant skyline for depth
    bm = bmesh.new()
    x = -140
    while x < 140:
        w = rnd.uniform(8, 18)
        h = rnd.uniform(30, 70)
        bm_box(bm, (x + w / 2, 70 + rnd.uniform(0, 15), h / 2), (w, 10, h))
        x += w + rnd.uniform(0, 3)
    new_obj("Skyline", bm, [far], coll)

    # street lamps, trees and props along the near curb (behind the owl)
    bm = bmesh.new()
    for lx in range(-84, 85, 21):
        bm_cyl(bm, (lx, 3.4, 4.5), 0.16, 0.12, 9, seg=8, mi=0)
        bm_box(bm, (lx, 2.6, 9.0), (0.18, 1.8, 0.18), 0)
        bm_box(bm, (lx, 1.8, 8.75), (0.7, 0.9, 0.35), 1)
        bm_cyl(bm, (lx, 3.4, 0.2), 0.32, 0.3, 0.4, seg=8, mi=0)
    new_obj("Lamps", bm, [dark, lamp], coll)

    bm = bmesh.new()
    for tx in range(-73, 74, 21):
        tx += rnd.uniform(-1.5, 1.5)
        bm_cyl(bm, (tx, 3.2, 2.2), 0.3, 0.22, 4.4, seg=6, mi=0)
        bm_ico(bm, (tx, 3.2, 6.0), 2.3, 1, (1, 1, 0.9), mi=1)
        bm_ico(bm, (tx + 1.2, 3.0, 7.3), 1.5, 1, mi=2)
        bm_ico(bm, (tx - 1.0, 3.6, 7.0), 1.3, 1, mi=1)
    new_obj("Trees", bm, [trunk, leaf, leaf2], coll)

    # hydrant
    bm = bmesh.new()
    bm_cyl(bm, (0, 0, 0.9), 0.38, 0.38, 1.8, seg=10)
    bm_ico(bm, (0, 0, 1.85), 0.42, 1)
    bm_cyl(bm, (0, 0, 1.2), 0.15, 0.15, 1.2, seg=8, matrix=Matrix.Rotation(math.pi / 2, 4, "X"))
    new_obj("Hydrant", bm, [red], coll, loc=(-9, 2.6, 0))
    # bench
    bm = bmesh.new()
    bm_box(bm, (0, 0, 1.4), (5, 1.4, 0.2), 0)
    bm_box(bm, (0, 0.65, 2.3), (5, 0.18, 1.2), 0)
    for bx in (-2.1, 2.1):
        bm_box(bm, (bx, 0, 0.7), (0.2, 1.2, 1.4), 1)
    new_obj("Bench", bm, [wood, dark], coll, loc=(11, 2.6, 0))
    # trash can + mailbox
    bm = bmesh.new()
    bm_cyl(bm, (0, 0, 1.2), 0.75, 0.65, 2.4, seg=10)
    new_obj("TrashCan", bm, [teal], coll, loc=(-17, 2.8, 0))
    bm = bmesh.new()
    bm_box(bm, (0, 0, 1.5), (1.5, 1.2, 2.2), 0)
    bm_box(bm, (0, 0, 0.2), (0.3, 0.3, 0.4), 1)
    new_obj("Mailbox", bm, [blue, dark], coll, loc=(29, 2.6, 0))

    # parked cars
    def car(name, cx, cy, mat_body):
        bm = bmesh.new()
        bm_box(bm, (0, 0, 1.4), (9, 4, 1.8), 0)
        bm_box(bm, (-0.4, 0, 2.9), (5, 3.6, 1.4), 1)
        for wx in (-2.9, 2.9):
            for wy in (-1.9, 1.9):
                bm_cyl(bm, (wx, wy, 0.75), 0.8, 0.8, 0.5, seg=12, mi=2,
                       matrix=Matrix.Rotation(math.pi / 2, 4, "X"))
        bm_box(bm, (4.5, -1.3, 1.6), (0.1, 0.8, 0.4), 3)
        bm_box(bm, (4.5, 1.3, 1.6), (0.1, 0.8, 0.4), 3)
        new_obj(name, bm, [mat_body, glass, dark, lamp], coll, loc=(cx, cy, -0.35))
    car("CarRed", -30, 7.5, red)
    car("CarTeal", 46, 7.5, teal)
    car("CarYellow", 6, 18.5, yellow)
    bpy.data.objects["CarYellow"].rotation_euler.z = math.pi

    for o in coll.objects:
        o.data.polygons.foreach_set("use_smooth", [False] * len(o.data.polygons))
    return coll


# --------------------------------------------------------- camera + light
def build_camera_light(scene):
    coll = bpy.data.collections.new("CameraRig")
    scene.collection.children.link(coll)
    tgt = bpy.data.objects.new("CamTarget", None)
    tgt.empty_display_type = "SPHERE"
    tgt.empty_display_size = 0.3
    tgt.location = (0, 4, 3.0)
    coll.objects.link(tgt)
    cd = bpy.data.cameras.new("Cam")
    cd.lens = 35
    cd.dof.use_dof = True
    cd.dof.focus_object = tgt
    cd.dof.aperture_fstop = 5.6
    cam = bpy.data.objects.new("Cam", cd)
    cam.location = (0, -24, 5)
    coll.objects.link(cam)
    c = cam.constraints.new("TRACK_TO")
    c.target = tgt
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    scene.camera = cam

    sd = bpy.data.lights.new("Sun", "SUN")
    sd.energy = 3.2
    sd.color = (1.0, 0.95, 0.86)
    sd.angle = math.radians(4)
    sun = bpy.data.objects.new("Sun", sd)
    sun.rotation_euler = (math.radians(50), math.radians(8), math.radians(-35))
    coll.objects.link(sun)

    world = bpy.data.worlds.new("Sky")
    scene.world = world
    if world.node_tree is None:
        world.use_nodes = True
    nt = world.node_tree
    bg = next(n for n in nt.nodes if n.type == "BACKGROUND")
    # vertical gradient: horizon haze -> blue zenith
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.85, 0.90, 0.95, 1)
    ramp.color_ramp.elements[1].position = 0.45
    ramp.color_ramp.elements[1].color = (0.35, 0.58, 0.90, 1)
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    # Generated z of the world is direction-based: remap -1..1 -> 0..1
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.5
    mr.inputs["From Max"].default_value = 1.0
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.7


def setup_render(scene):
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.fps = 24
    scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
    scene.render.resolution_percentage = 50
    scene.eevee.taa_render_samples = 24
    scene.frame_start, scene.frame_end = 1, 240
    try:
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.exposure = -0.35
    except TypeError:
        pass


if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    setup_render(scene)
    build_owl(scene)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "owl_rig.blend"))
    build_street(scene)
    build_camera_light(scene)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "owl_street.blend"))
    print("BUILD OK")
