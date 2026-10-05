"""Scene building blocks: studio, web strands, presentation board, camera, look.

All functions are idempotent-ish: they create named objects and return them.
"""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix
from . import anim


# ------------------------------------------------------------------ helpers
def material(name, color=(0.5, 0.5, 0.5), rough=0.5, metallic=0.0, emit=0.0, emit_color=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    if m.node_tree is None:
        m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    if emit:
        b.inputs["Emission Color"].default_value = (*(emit_color or color), 1)
        b.inputs["Emission Strength"].default_value = emit
    return m


def _link(obj, coll=None):
    (coll or bpy.context.scene.collection).objects.link(obj)
    return obj


def collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def empty(name, loc=(0, 0, 0), coll=None, size=0.2):
    e = bpy.data.objects.get(name) or _link(bpy.data.objects.new(name, None), coll)
    e.empty_display_size = size
    e.location = loc
    return e


# ------------------------------------------------------------------ character shading
def physical_shading(obj, lift=2.2, rough=0.42, sheen=0.6, bump=0.35):
    """Replace a toon/NPR material network with physically lit shading.

    The Sketchfab Miles uses a Shader-to-RGB cel setup that flattens light into a
    few bands (the suit reads as solid black). This wires the diffuse texture into
    a fresh Principled BSDF: brightness lift, fabric sheen, and bump derived from
    the texture so the web pattern and seams catch light.
    """
    for slot in obj.material_slots:
        m = slot.material
        if not m or not m.node_tree:
            continue
        nt = m.node_tree
        imgs = [n for n in nt.nodes if n.type == "TEX_IMAGE" and n.image and not n.mute and
                (n.image.packed_file or os.path.exists(bpy.path.abspath(n.image.filepath)))]
        diff = next((n for n in imgs if "_D" in n.image.name), None)
        if diff is None:
            continue                       # e.g. eye lenses: leave their look alone
        out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
        b = nt.nodes.new("ShaderNodeBsdfPrincipled")
        hsv = nt.nodes.new("ShaderNodeHueSaturation")
        hsv.inputs["Value"].default_value = lift
        bm = nt.nodes.new("ShaderNodeBump")
        bm.inputs["Strength"].default_value = bump
        bm.inputs["Distance"].default_value = 0.004
        nt.links.new(diff.outputs["Color"], hsv.inputs["Color"])
        nt.links.new(hsv.outputs["Color"], b.inputs["Base Color"])
        nt.links.new(diff.outputs["Color"], bm.inputs["Height"])
        nt.links.new(bm.outputs["Normal"], b.inputs["Normal"])
        b.inputs["Roughness"].default_value = rough
        b.inputs["Sheen Weight"].default_value = sheen
        b.inputs["Sheen Roughness"].default_value = 0.35
        b.inputs["Specular IOR Level"].default_value = 0.6
        nt.links.new(b.outputs["BSDF"], out.inputs["Surface"])


# ------------------------------------------------------------------ studio
THEMES = {
    # light: soft cool-grey cyclorama so the black suit reads clearly
    "light": dict(cyc=(0.55, 0.57, 0.62), rough=0.65, world=(0.62, 0.66, 0.74), world_strength=0.32,
                  key=380, fill=0.35, wash=(1.0, 0.97, 0.92), wash_energy=140, rim_energy=260, char_key=300, rim_spec=0.8),
    # dark: Spider-Verse night look with coloured rims
    "dark": dict(cyc=(0.012, 0.013, 0.025), rough=0.4, world=(0.004, 0.005, 0.012), world_strength=1.0,
                 key=900, fill=0.18, wash=(0.35, 0.12, 0.85), wash_energy=2500, rim_energy=1400, char_key=0, rim_spec=0.12),
}


def area_light(name, loc, target, energy, color, size, spec=1.0, coll=None):
    """Soft area light at `loc` aimed at `target` (spec: <1 keeps hot spots off the glossy floor)."""
    ld = bpy.data.lights.get(name) or bpy.data.lights.new(name, "AREA")
    ld.energy, ld.color, ld.size = energy, color, size
    ld.specular_factor = spec
    ob = bpy.data.objects.get(name) or _link(bpy.data.objects.new(name, ld), coll or collection("Studio"))
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return ob


def stage_pool(prefix, center, subject, theme="dark", key=1.0, coll=None):
    """The studio look (backdrop wash, red/blue rims, soft key) re-created around another spot on
    the set, e.g. a finale staged far from the main lights. center: (x, y) of the set piece;
    subject: (x, y) of the character there."""
    t, coll = THEMES[theme], coll or collection("Studio")
    cx, cy = center
    sx, sy = subject
    area_light(prefix + "Wash", (cx, 2.5, 0.3), (cx, 8, 4), t["wash_energy"], t["wash"], 6.0, spec=0.0, coll=coll)
    area_light(prefix + "RimRed", (sx - 2.6, sy + 3.2, 3.0), (sx, sy, 1.3), t["rim_energy"], (1.0, 0.18, 0.14), 1.5,
               spec=t["rim_spec"], coll=coll)
    area_light(prefix + "RimBlue", (sx + 2.8, sy + 3.0, 3.2), (sx, sy, 1.3), t["rim_energy"] * 0.93, (0.3, 0.5, 1.0), 1.5,
               spec=t["rim_spec"], coll=coll)
    area_light(prefix + "Key", (cx - 3.0, cy - 5.0, 5.0), (cx, cy, 1.2), t["key"] * key, (1.0, 0.96, 0.92), 3.0, spec=0.35,
               coll=coll)


def studio(theme="light", rims=True, subject=(-2.4, 0.0)):
    """Infinite cyclorama studio. theme: 'light' | 'dark' (see THEMES)."""
    t = THEMES[theme]
    coll = collection("Studio")
    # cyclorama profile in YZ (floor -> curve -> back wall), extruded along X
    prof = [(y, 0.0) for y in (-30, -10, 0, 3)]
    R = 4.0
    for i in range(1, 9):
        a = -math.pi / 2 + (math.pi / 2) * i / 8
        prof.append((3 + R * math.cos(a), R + R * math.sin(a)))
    prof += [(3 + R, 10.0), (3 + R, 20.0)]
    bm = bmesh.new()
    rows = []
    for x in (-40, 40):
        rows.append([bm.verts.new((x, y, z)) for (y, z) in prof])
    for i in range(len(prof) - 1):
        bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
    for f in bm.faces:
        f.smooth = True
    me = bpy.data.meshes.new("Cyclorama")
    bm.to_mesh(me)
    bm.free()
    cyc = bpy.data.objects.get("Cyclorama") or _link(bpy.data.objects.new("Cyclorama", me), coll)
    cyc.data.materials.clear()
    cyc.data.materials.append(material("Studio_Floor_" + theme, t["cyc"], rough=t["rough"]))

    w = bpy.context.scene.world or bpy.data.worlds.new("StudioWorld")
    bpy.context.scene.world = w
    if w.node_tree is None:
        w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (*t["world"], 1)
    bg.inputs["Strength"].default_value = t["world_strength"]

    area = lambda *a, **k: area_light(*a, coll=coll, **k)

    area("Key", (-3.5, -5.0, 5.0), (0, 0, 1.2), t["key"], (1.0, 0.96, 0.92), 3.0, spec=0.35)
    area("Fill", (5.0, -6.0, 2.5), (0, 0, 1.2), t["key"] * t["fill"], (0.85, 0.9, 1.0), 4.0, spec=0.2)
    area("WallWash", (0, 2.5, 0.3), (0, 8, 4), t["wash_energy"], t["wash"], 6.0, spec=0.0)
    if rims:
        sx, sy = subject
        area("RimRed", (sx - 2.6, sy + 3.2, 3.0), (sx, sy, 1.3), t["rim_energy"], (1.0, 0.18, 0.14), 1.5, spec=t["rim_spec"])
        area("RimBlue", (sx + 2.8, sy + 3.0, 3.2), (sx, sy, 1.3), t["rim_energy"] * 0.93, (0.3, 0.5, 1.0), 1.5, spec=t["rim_spec"])
    if t.get("char_key"):
        # soft key on the character from front-left: its highlights trace the body
        area("CharKey", (subject[0] - 2.2, subject[1] - 3.0, 3.6), (subject[0], subject[1], 1.2), t["char_key"],
             (1.0, 0.97, 0.94), 1.6, spec=1.0)
    return coll


def spot(name, loc, target, energy=900, color=(1.0, 0.95, 0.88), angle=40, blend=0.5, coll=None):
    """Spot light aimed at a point (e.g. an overhead light above a screen)."""
    coll = coll or collection("Studio")
    ld = bpy.data.lights.get(name) or bpy.data.lights.new(name, "SPOT")
    ld.energy, ld.color = energy, color
    ld.spot_size, ld.spot_blend = math.radians(angle), blend
    ld.shadow_soft_size = 0.4
    ob = bpy.data.objects.get(name) or _link(bpy.data.objects.new(name, ld), coll)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return ob


def follow_spot(rig, bone="mixamorig:Spine2", offset=(-1.6, -3.2, 3.4), energy=420, angle=28, coll=None):
    """Theatre follow-spot: rides with the character (rig root) and stays aimed at a bone, so the
    dark suit always gets a key light wherever he walks or cartwheels."""
    coll = coll or collection("Studio")
    ld = bpy.data.lights.get("FollowSpot") or bpy.data.lights.new("FollowSpot", "SPOT")
    ld.energy, ld.color = energy, (1.0, 0.96, 0.92)
    ld.spot_size, ld.spot_blend = math.radians(angle), 0.6
    ld.shadow_soft_size = 0.6
    ob = bpy.data.objects.get("FollowSpot") or _link(bpy.data.objects.new("FollowSpot", ld), coll)
    c = ob.constraints.new("COPY_LOCATION")
    c.target, c.subtarget = rig, "mixamorig:Hips"
    c.use_z = False
    c.use_offset = True
    ob.location = offset
    t = ob.constraints.new("TRACK_TO")
    t.target, t.subtarget = rig, bone
    t.track_axis, t.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
    return ob


def paper_pour(name, texture, emit_fn, land_center, count, start, dur, spread=(1.1, 0.7), coll=None, seed=7,
               size=(0.21, 0.297), arc=(0.5, 1.1)):
    """Sheets of paper burst out of a source (e.g. a screen) and pile up on the floor.

    emit_fn(i) -> world point where sheet i leaves the source; they arc out and land in an
    ellipse around land_center, stacking up. Fully keyed (no physics), deterministic.
    """
    import random
    r = random.Random(seed)
    coll = coll or collection(name)
    mat = bpy.data.materials.new(name + "_Mat")
    if mat.node_tree is None:
        mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(texture, check_existing=True)
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.7
    me = bpy.data.meshes.new(name + "_Sheet")
    w, h = size
    me.from_pydata([(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, loop in enumerate(me.loops):
        uv.data[li].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][loop.vertex_index]
    me.materials.append(mat)
    cx, cy = land_center[0], land_center[1]
    pile = {}
    sheets = []
    for i in range(count):
        ob = _link(bpy.data.objects.new(f"{name}_{i:03d}", me), coll)
        t0 = int(start + dur * (i / count) ** 0.8 + r.uniform(-2, 2))
        t1 = t0 + r.randint(14, 22)
        p0 = Vector(emit_fn(i))
        a = r.uniform(0, 2 * math.pi)
        rad = math.sqrt(r.random())
        land = Vector((cx + math.cos(a) * rad * spread[0], cy + math.sin(a) * rad * spread[1], 0))
        cell = (round(land.x * 4), round(land.y * 4))
        pile[cell] = pile.get(cell, 0) + 1
        land.z = 0.004 + pile[cell] * 0.018 * (1.2 - rad)          # mound: higher near the middle
        apex = (p0 + land) / 2 + Vector((0, -0.4, r.uniform(*arc)))
        anim.visible(ob, [(1, False), (t0, True)])
        anim.keys(ob, "location", [(t0, p0, "out"), ((t0 + t1) // 2, apex, "in"), (t1, land, "bez")])
        rot_end = Vector((r.uniform(-0.25, 0.25), r.uniform(-0.25, 0.25), r.uniform(0, 2 * math.pi)))
        rot_mid = Vector((r.uniform(-3, 3), r.uniform(-3, 3), r.uniform(-3, 3)))
        anim.keys(ob, "rotation_euler", [(t0, Vector((math.pi / 2, 0, 0)), "lin"), ((t0 + t1) // 2, rot_mid, "lin"),
                                         (t1, rot_end, "bez")])
        sheets.append(ob)
    return sheets


# ------------------------------------------------------------------ web strands
def web_strand(name, rig, bone, anchor, radius=0.016, head_tail=0.75, coll=None):
    """Cylinder from a hand bone stretched to an anchor empty (Copy Location + Stretch To)."""
    bm = bmesh.new()
    res = bmesh.ops.create_cone(bm, cap_ends=False, segments=6, radius1=radius, radius2=radius * 0.7, depth=1.0)
    bmesh.ops.rotate(bm, verts=res["verts"], cent=(0, 0, 0), matrix=Matrix.Rotation(-math.pi / 2, 3, "X"))
    bmesh.ops.translate(bm, verts=res["verts"], vec=(0, 0.5, 0))     # base at origin, along +Y
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = _link(bpy.data.objects.new(name, me), coll)
    ob.data.materials.append(material("Web", (0.95, 0.97, 1.0), rough=0.4, emit=0.6))
    c = ob.constraints.new("COPY_LOCATION")
    c.target, c.subtarget, c.head_tail = rig, bone, head_tail
    s = ob.constraints.new("STRETCH_TO")
    s.target = anchor
    s.rest_length = 1.0
    s.volume = "NO_VOLUME"
    s.keep_axis = "PLANE_Z"
    return ob


def bake(frames, jobs, scene=None):
    """Evaluate the scene frame by frame and key empties: jobs = {empty: fn(frame)->Vector|None}."""
    sc = scene or bpy.context.scene
    for f in frames:
        sc.frame_set(f)
        vals = {e: fn(f) for e, fn in jobs.items()}
        for e, v in vals.items():
            if v is not None:
                anim.key(e, "location", f, Vector(v), ease="lin")


class WebShots:
    """Web strands that fire from a hand bone, stick to a target, then release.

        webs = WebShots(rig, coll)
        webs.shot("Web_Flick1", "mixamorig:RightHand", lambda f: board.nearest_hook(...), start, hit, release)
        webs.bake(range(1, end + 1))
    """

    def __init__(self, rig, coll=None):
        self.rig, self.coll, self.shots = rig, coll, []

    def hand(self, bone, head_tail=0.75):
        pb = self.rig.pose.bones[bone]
        return self.rig.matrix_world @ pb.head.lerp(pb.tail, head_tail)

    def shot(self, name, bone, target, start, hit, release):
        """target: fn(frame) -> world point. Grows start->hit (smoothstep), attached until release."""
        anchor = empty(name + "_Anchor", coll=self.coll, size=0.08)
        strand = web_strand(name, self.rig, bone, anchor, coll=self.coll)
        anim.visible(strand, [(1, False), (int(start), True), (int(release), False)])
        self.shots.append((anchor, bone, target, int(start), int(hit), int(release)))
        return strand

    def bake(self, frames):
        def make(anchor, bone, target, a, b, r):
            def fn(f):
                if f < a or f > r + 1:
                    return None
                tgt = Vector(target(f))
                if f < b:
                    t = (f - a) / max(1, b - a)
                    return self.hand(bone).lerp(tgt, t * t * (3 - 2 * t))
                return tgt
            return fn
        bake(frames, {s[0]: make(*s) for s in self.shots})


# ------------------------------------------------------------------ board
class Board:
    """Two-sided presentation sign that can show any number of slides.

    Matte printed faces in an aluminium frame; optional floor stands. Each face's
    material holds every slide and a keyed index picks one, so a spin can reveal
    the next slide on whichever face is turning towards camera.

        b = Board("Board", [png1, png2, png3], width=4.8, stand_height=0.6)
        b.show(1, 0)             # slide 0 on the front at frame 1
        b.flip(120, 1)           # spin 180° revealing slide 1
        b.flip(200, 2, turns=1.5)
    """

    def __init__(self, name, slides, width=2.4, depth=0.06, coll=None, glow=0.06, stand_height=0.0,
                 frame="aluminium", power=False):
        """frame: "aluminium" (physical sign), "glow" (dark slab, emissive blue edge) or "tv" (LCD: glossy
        black bezel, centre stand). power=True starts the screen OFF (black glass) until power_on().
        Slides: png paths, or ("seq", first_png, n_frames, start_frame) for an animated image sequence."""
        self.frame_style, self.power = frame, power
        self.power_nodes = []
        self.name, self.slides, self.width = name, slides, width
        self.height = height = width * 9 / 16
        self.root = root = empty(name, coll=coll, size=0.3)
        self.coll = coll
        self.index_nodes = {}
        self.visible = "front"                  # face currently towards the camera
        self.base_z = 0.0                       # resting height of the panel centre (for hops)
        self.spin = 0.0                         # accumulated Z rotation (radians)
        hw, hh = width / 2, height / 2
        for face, y, flip in (("front", -depth / 2 - 0.001, False), ("back", depth / 2 + 0.001, True)):
            me = bpy.data.meshes.new(f"{name}_{face}")
            verts = ([(hw, y, -hh), (-hw, y, -hh), (-hw, y, hh), (hw, y, hh)] if flip else
                     [(-hw, y, -hh), (hw, y, -hh), (hw, y, hh), (-hw, y, hh)])
            me.from_pydata(verts, [], [(0, 1, 2, 3)])
            uv = me.uv_layers.new()
            for li, loop in enumerate(me.loops):
                uv.data[li].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][loop.vertex_index]
            ob = _link(bpy.data.objects.new(f"{name}_{face}", me), coll)
            ob.parent = root
            ob.data.materials.append(self._slide_material(f"{name}_{face}_Mat", face, glow))

        def box(nm, size, loc, mat):
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=size, verts=bm.verts)
            bmesh.ops.translate(bm, vec=loc, verts=bm.verts)
            me = bpy.data.meshes.new(nm)
            bm.to_mesh(me)
            bm.free()
            ob = _link(bpy.data.objects.new(nm, me), coll)
            ob.parent = root
            ob.data.materials.append(mat)
            bev = ob.modifiers.new("Bevel", "BEVEL")
            bev.width, bev.segments = 0.008, 2

        alu = {"aluminium": lambda: material("Board_Aluminium", (0.62, 0.63, 0.65), rough=0.32, metallic=0.9),
               "glow": lambda: material("Board_GlowEdge", (0.05, 0.1, 0.25), rough=0.3, emit=2.5,
                                        emit_color=(0.23, 0.51, 0.96)),
               "tv": lambda: material("TV_Bezel", (0.012, 0.012, 0.014), rough=0.18, metallic=0.2)}[frame]()
        core = (material("TV_Back", (0.02, 0.02, 0.022), rough=0.4) if frame == "tv" else
                material("Board_Core", (0.92, 0.92, 0.9), rough=0.7))
        box(name + "_Core", (width, depth, height), (0, 0, 0), core)
        f = 0.035 if frame == "tv" else 0.045
        for i, (sz, lc) in enumerate((((width + 2 * f, depth + 0.02, f), (0, 0, hh + f / 2)),
                                      ((width + 2 * f, depth + 0.02, f), (0, 0, -hh - f / 2)),
                                      ((f, depth + 0.02, height), (-hw - f / 2, 0, 0)),
                                      ((f, depth + 0.02, height), (hw + f / 2, 0, 0)))):
            box(f"{name}_Frame{i}", sz, lc, alu)
        if stand_height > 0 and frame == "tv":
            dark = material("TV_Stand", (0.05, 0.05, 0.055), rough=0.3, metallic=0.7)
            post_h = stand_height + 0.3
            box(f"{name}_Post", (0.09, 0.05, post_h), (0, depth, -hh - stand_height + post_h / 2), dark)
            box(f"{name}_Base", (width * 0.35, 0.55, 0.035), (0, depth, -hh - stand_height + 0.0175), dark)
        elif stand_height > 0:
            dark = material("Board_Stand", (0.08, 0.08, 0.09), rough=0.45, metallic=0.6)
            for sx in (-width * 0.33, width * 0.33):
                post_h = stand_height + 0.25
                box(f"{name}_Post{sx:+.1f}", (0.06, 0.06, post_h), (sx, 0, -hh - stand_height + post_h / 2), dark)
                box(f"{name}_Foot{sx:+.1f}", (0.09, 0.9, 0.04), (sx, 0, -hh - stand_height + 0.02), dark)
        # attachment points (children, so they follow every move/spin)
        self.hooks = [empty(f"{name}_Hook{side}", (sx * (hw + f), 0, 0), coll, 0.1)
                      for side, sx in (("L", -1), ("R", 1))]
        self.top = empty(f"{name}_Top", (0, 0, hh + f), coll, 0.1)
        for e in self.hooks + [self.top]:
            e.parent = root

    def _slide_material(self, name, face, glow):
        m = bpy.data.materials.new(name)
        if m.node_tree is None:
            m.use_nodes = True
        nt = m.node_tree
        bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
        idx = nt.nodes.new("ShaderNodeValue")
        idx.name = "SlideIndex"
        idx.outputs[0].default_value = 0
        prev = None
        for i, png in enumerate(self.slides):
            tex = nt.nodes.new("ShaderNodeTexImage")
            if isinstance(png, tuple):                      # ("seq", first_png, n_frames, start_frame)
                _, first, n, start = png
                tex.image = bpy.data.images.load(first, check_existing=False)
                tex.image.source = "SEQUENCE"
                tex.image_user.frame_duration = n
                tex.image_user.frame_start = int(start)
                tex.image_user.use_auto_refresh = True
            else:
                tex.image = bpy.data.images.load(png, check_existing=True)
            if prev is None:
                prev = tex.outputs["Color"]
                continue
            gt = nt.nodes.new("ShaderNodeMath")
            gt.operation = "GREATER_THAN"
            gt.inputs[1].default_value = i - 0.5
            nt.links.new(idx.outputs[0], gt.inputs[0])
            mix = nt.nodes.new("ShaderNodeMix")
            mix.data_type = "RGBA"
            nt.links.new(gt.outputs[0], mix.inputs["Factor"])
            nt.links.new(prev, mix.inputs[6])
            nt.links.new(tex.outputs["Color"], mix.inputs[7])
            prev = mix.outputs[2]
        if self.power:
            # screen off = black glass; "Power" (0..1+, keyed) fades the picture in and drives emission
            pw = nt.nodes.new("ShaderNodeValue")
            pw.name = "Power"
            pw.outputs[0].default_value = 0.0
            clamp = nt.nodes.new("ShaderNodeClamp")
            nt.links.new(pw.outputs[0], clamp.inputs[0])
            dim = nt.nodes.new("ShaderNodeMix")
            dim.data_type = "RGBA"
            dim.inputs[6].default_value = (0.004, 0.004, 0.005, 1)
            nt.links.new(clamp.outputs[0], dim.inputs["Factor"])
            nt.links.new(prev, dim.inputs[7])
            mul = nt.nodes.new("ShaderNodeMath")
            mul.operation = "MULTIPLY"
            mul.inputs[1].default_value = glow
            nt.links.new(pw.outputs[0], mul.inputs[0])
            nt.links.new(dim.outputs[2], bsdf.inputs["Base Color"])
            nt.links.new(prev, bsdf.inputs["Emission Color"])
            nt.links.new(mul.outputs[0], bsdf.inputs["Emission Strength"])
            bsdf.inputs["Roughness"].default_value = 0.12          # glossy glass
            bsdf.inputs["Specular IOR Level"].default_value = 0.35
            self.power_nodes.append(pw)
        else:
            nt.links.new(prev, bsdf.inputs["Base Color"])
            nt.links.new(prev, bsdf.inputs["Emission Color"])
            bsdf.inputs["Emission Strength"].default_value = glow     # tiny lift for legibility only
            bsdf.inputs["Roughness"].default_value = 0.62              # matte print
            bsdf.inputs["Specular IOR Level"].default_value = 0.08     # no sheen: ink stays black
        self.index_nodes[face] = idx
        return m

    def power_on(self, frame):
        """CRT-ish switch-on: flash, flicker, settle."""
        f = int(frame)
        for pw in self.power_nodes:
            anim.keys(pw.outputs[0], "default_value", [(f - 1, 0.0, "lin"), (f + 1, 1.8, "lin"), (f + 3, 0.25, "lin"),
                                                       (f + 5, 1.3, "lin"), (f + 7, 0.7, "lin"), (f + 10, 1.0, "bez")])
        return f + 10

    def power_off(self, frame):
        f = int(frame)
        for pw in self.power_nodes:
            anim.keys(pw.outputs[0], "default_value", [(f, 1.0, "lin"), (f + 2, 1.6, "lin"), (f + 5, 0.0, "lin")])
        return f + 5

    def flicker(self, frame, n=6):
        """Unstable screen (glitch moment)."""
        import random
        r = random.Random(frame)
        for pw in self.power_nodes:
            for i in range(n):
                anim.key(pw.outputs[0], "default_value", int(frame) + i * 2, r.choice((0.15, 0.4, 1.4, 0.9)), ease="lin")
            anim.key(pw.outputs[0], "default_value", int(frame) + n * 2, 1.0, ease="bez")

    def show(self, frame, index, face=None):
        """Put slide `index` on a face (default: the one facing camera) from `frame` on."""
        node = self.index_nodes[face or self.visible]
        anim.key(node.outputs[0], "default_value", int(frame), float(index), ease="const")

    def flip(self, frame, index, turns=0.5, dur=16, hop=0.2, ease="back"):
        """Spin to reveal slide `index`. turns must be an odd multiple of 0.5 (0.5, 1.5, ...)."""
        hidden = "back" if self.visible == "front" else "front"
        self.show(frame - 1, index, hidden)
        r0, r1 = self.spin, self.spin + turns * 2 * math.pi
        anim.key(self.root, "rotation_euler", int(frame), r0, 2, ease)
        anim.key(self.root, "rotation_euler", int(frame + dur), r1, 2, "bez")
        if hop:
            z = self.base_z
            anim.key(self.root, "location", int(frame), z, 2, "out")
            anim.key(self.root, "location", int(frame + dur * 0.4), z + hop, 2, "in")
            anim.key(self.root, "location", int(frame + dur * 0.85), z, 2, "bez")
        self.spin, self.visible = r1, hidden
        return frame + dur

    def nearest_hook(self, point):
        return min((h.matrix_world.translation for h in self.hooks), key=lambda p: (p - Vector(point)).length)


# ------------------------------------------------------------------ camera
def shot_cam(name, loc, target, lens=35, coll=None, rig=None, bone=None, follow_bone=None, frame=None):
    """Extra camera for one shot, switched in with shot.finish(cameras=[(frame, cam), ...]).

    target: world point to aim at, or None with rig+bone to keep a bone centred (Track To the bone).
    follow_bone: ride on that bone (snorricam) — loc is taken at `frame` and kept relative to the bone."""
    coll = coll or collection("Camera")
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.dof.use_dof = False
    ob = _link(bpy.data.objects.new(name, cd), coll)
    ob.location = loc
    tr = ob.constraints.new("TRACK_TO")
    tr.track_axis, tr.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
    if target is None:
        tr.target, tr.subtarget = rig, bone
    else:
        tr.target = empty(name + "Target", target, coll, 0.1)
    if follow_bone:
        bpy.context.scene.frame_set(int(frame))
        m = Matrix.Translation(Vector(loc))
        ob.parent, ob.parent_type, ob.parent_bone = rig, "BONE", follow_bone
        bpy.context.view_layer.update()
        ob.matrix_world = m
    return ob


class CameraRig:
    def __init__(self, name="Cam", lens=35, fstop=2.8, coll=None):
        coll = coll or collection("Camera")
        self.target = empty(name + "Target", (0, 0, 1.2), coll, 0.15)
        cd = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
        cd.lens = lens
        cd.dof.use_dof = True
        cd.dof.focus_object = self.target
        cd.dof.aperture_fstop = fstop
        self.cam = bpy.data.objects.get(name) or _link(bpy.data.objects.new(name, cd), coll)
        if not any(c.type == "TRACK_TO" for c in self.cam.constraints):
            t = self.cam.constraints.new("TRACK_TO")
            t.target, t.track_axis, t.up_axis = self.target, "TRACK_NEGATIVE_Z", "UP_Y"
        bpy.context.scene.camera = self.cam

    def at(self, frame, cam, target, ease="inout", cut=False):
        """Key camera + target. cut=True makes the segment before this key a hard cut."""
        if cut:
            for ob in (self.cam, self.target):
                fc = anim.fcurve(ob, "location", 0)
                if fc:
                    prev = [k for k in fc.keyframe_points if k.co.x < frame]
                    if prev:
                        f_prev = max(k.co.x for k in prev)
                        for i in range(3):
                            fci = anim.fcurve(ob, "location", i)
                            for k in fci.keyframe_points:
                                if abs(k.co.x - f_prev) < 1e-3:
                                    k.interpolation = "CONSTANT"
        anim.key(self.cam, "location", frame, Vector(cam), ease=ease)
        anim.key(self.target, "location", frame, Vector(target), ease=ease)

    def lens(self, frame, mm, ease="inout"):
        anim.key(self.cam.data, "lens", frame, mm, ease=ease)

    def shake(self, frame, amp=0.06, dur=10, seed=4):
        import random
        r = random.Random(seed)
        sc = bpy.context.scene
        for i in range(dur):
            sc.frame_set(frame + i)
            k = amp * (1 - i / dur)
            p = self.target.location.copy() + Vector((r.uniform(-k, k), 0, r.uniform(-k, k)))
            anim.key(self.target, "location", frame + i, p, ease="lin")


# ------------------------------------------------------------------ look
def look(scene=None, samples=24, motion_blur=True, bloom=True, exposure=0.0, view="Standard", grade=None):
    sc = scene or bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    ee = sc.eevee
    ee.taa_render_samples = samples
    ee.use_raytracing = True
    ee.use_shadows = True
    if hasattr(ee, "use_fast_gi"):
        ee.use_fast_gi = True
    sc.render.use_motion_blur = motion_blur
    sc.render.motion_blur_shutter = 0.5
    sc.view_settings.view_transform = view           # Standard keeps slide/brand colours exact; AgX = filmic
    sc.view_settings.look = "None"
    for lk in ([grade] if grade else []):
        try:
            sc.view_settings.look = lk
        except TypeError:
            pass
    sc.view_settings.exposure = exposure
    if bloom:
        ng = bpy.data.node_groups.get("Compositor") or bpy.data.node_groups.new("Compositor", "CompositorNodeTree")
        for n in list(ng.nodes):
            ng.nodes.remove(n)
        sc.compositing_node_group = ng
        rl = ng.nodes.new("CompositorNodeRLayers")
        gl = ng.nodes.new("CompositorNodeGlare")
        gl.inputs["Type"].default_value = "Bloom"
        gl.inputs["Threshold"].default_value = 1.2
        gl.inputs["Size"].default_value = 7.0
        gl.inputs["Strength"].default_value = 0.45
        if not ng.interface.items_tree:
            ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        out = ng.nodes.new("NodeGroupOutput")
        ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
        ng.links.new(gl.outputs[0], out.inputs[0])


class Spiders:
    """A swarm of walking spiders (Sketchfab "Spider animated character" by TheGameAssets, CC-BY).

        sw = Spiders(paths.SPIDER_GLB, size=0.32)
        sw.add([(f0, p0), (f1, p1), ...], walk_speed=1.6)     # pops in at f0, walks the waypoints
    Each spider faces where it is heading and plays the walk cycle; it is hidden before the first
    and after the last waypoint (walk it off-screen to make it leave).
    """

    def __init__(self, path, size=0.32, coll=None, yaw_offset=math.pi / 2):     # model's head points -Y
        self.coll = coll or collection("Spiders")
        self.size, self.yaw_offset, self.n = size, yaw_offset, 0
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=path)
        new = [o for o in bpy.data.objects if o not in before]
        self.arm = next(o for o in new if o.type == "ARMATURE")
        self.mesh = next(o for o in new if o.type == "MESH" and o.find_armature() == self.arm)
        self.walk = next(a for a in bpy.data.actions if a.name.endswith("_Walk"))
        bpy.context.view_layer.update()
        m = self.arm.matrix_world.copy()
        self.arm.parent = None
        self.arm.matrix_world = m
        for o in new:                                   # drop the FBX empties + the ground plane
            if o not in (self.arm, self.mesh):
                bpy.data.objects.remove(o, do_unlink=True)
        bpy.context.view_layer.update()
        pts = [self.mesh.matrix_world @ Vector(c) for c in self.mesh.bound_box]
        span = max(max(p.x for p in pts) - min(p.x for p in pts), max(p.y for p in pts) - min(p.y for p in pts))
        s = size / span
        self.rest = Matrix.Scale(s, 4) @ self.arm.matrix_world
        self.lift = -min(p.z for p in pts) * s          # sole on the floor
        for o in (self.arm, self.mesh):                 # the source stays out of the shot
            for c in list(o.users_collection):
                c.objects.unlink(o)
        if self.arm.animation_data:
            self.arm.animation_data.action = None

    def add(self, waypoints, walk_speed=1.5, pop=4):
        """waypoints: [(frame, Vector)] — points on the surface it walks on."""
        i, self.n = self.n, self.n + 1
        root = empty(f"Spider_{i:02d}", waypoints[0][1], self.coll, 0.05)
        arm = self.arm.copy()
        _link(arm, self.coll)
        arm.parent = root
        arm.matrix_parent_inverse = Matrix.Identity(4)
        arm.matrix_basis = Matrix.Translation((0, 0, self.lift)) @ self.rest
        body = self.mesh.copy()
        _link(body, self.coll)
        body.parent = arm
        body.matrix_parent_inverse = self.mesh.matrix_parent_inverse.copy()
        for md in body.modifiers:
            if md.type == "ARMATURE":
                md.object = arm
        ad = arm.animation_data_create()
        ad.action = None
        tr = ad.nla_tracks.new()
        a0, a1 = self.walk.frame_range
        f0, f1 = int(waypoints[0][0]), int(waypoints[-1][0])
        st = tr.strips.new("walk", f0 - (i * 3) % 9, self.walk)
        if hasattr(st, "action_slot") and self.walk.slots:
            st.action_slot = self.walk.slots[0]
        st.scale = 1.0 / walk_speed
        st.repeat = max(1.0, (f1 - f0 + 12) * walk_speed / (a1 - a0))
        yaw = None
        for k, (f, p) in enumerate(waypoints):
            anim.key(root, "location", int(f), Vector(p), ease="lin")
            q = (waypoints[k + 1][1] - Vector(p)) if k + 1 < len(waypoints) else (Vector(p) - waypoints[k - 1][1])
            if q.xy.length > 1e-4:
                a = math.atan2(q.y, q.x) + self.yaw_offset
                if yaw is not None:                         # unwrap: never spin the long way round
                    a = yaw + (a - yaw + math.pi) % (2 * math.pi) - math.pi
                yaw = a
                anim.key(root, "rotation_euler", int(f), a, index=2, ease="lin")
        anim.keys(root, "scale", [(f0, Vector((0.01, 0.01, 0.01)), "out"), (f0 + pop, Vector((1, 1, 1)), "lin")])
        for o in (arm, body):
            anim.visible(o, [(1, False), (f0, True), (f1, False)])
        return root


def char_lights(rig, cam, key=140.0, rim=260.0, bone="mixamorig:Spine2", coll=None):
    """Film lighting on the character only: soft key from the camera side + warm/cool rims behind him,
    re-oriented to every shot (the rig follows him and turns its back to the active camera).
    Light linking keeps them off the set, so the city's look is unchanged."""
    coll = coll or collection("CharLights")
    pivot = empty("CharLightRig", (0, 0, 0), coll, 0.1)
    c = pivot.constraints.new("COPY_LOCATION")
    c.target, c.subtarget = rig, bone
    t = pivot.constraints.new("LOCKED_TRACK")
    t.target, t.track_axis, t.lock_axis = cam, "TRACK_NEGATIVE_Y", "LOCK_Z"
    receivers = bpy.data.collections.get("CharReceivers") or bpy.data.collections.new("CharReceivers")
    for ch in rig.children_recursive:
        if ch.type == "MESH" and ch.name not in receivers.objects:
            receivers.objects.link(ch)
    lights = []
    for name, loc, energy, color, size in (("CharKey", (-1.6, -2.6, 0.9), key, (1.0, 0.93, 0.85), 1.4),
                                           ("CharRimWarm", (1.7, 1.9, 0.7), rim, (1.0, 0.62, 0.32), 0.6),
                                           ("CharRimCool", (-1.7, 1.9, 0.9), rim * 0.9, (0.45, 0.65, 1.0), 0.6)):
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy, ld.color, ld.size = energy, color, size
        ob = _link(bpy.data.objects.new(name, ld), coll)
        ob.parent = pivot
        ob.location = loc
        tr = ob.constraints.new("TRACK_TO")
        tr.target, tr.track_axis, tr.up_axis = pivot, "TRACK_NEGATIVE_Z", "UP_Y"
        if hasattr(ob, "light_linking"):
            ob.light_linking.receiver_collection = receivers
        lights.append(ob)
    return lights
