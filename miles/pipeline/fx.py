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
                  key=380, fill=0.35, wash=(1.0, 0.97, 0.92), wash_energy=140, rim_energy=260, char_key=300),
    # dark: Spider-Verse night look with coloured rims
    "dark": dict(cyc=(0.012, 0.013, 0.025), rough=0.4, world=(0.004, 0.005, 0.012), world_strength=1.0,
                 key=900, fill=0.18, wash=(0.35, 0.12, 0.85), wash_energy=2500, rim_energy=1400, char_key=0),
}


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

    def area(name, loc, target, energy, color, size, spec=1.0):
        ld = bpy.data.lights.get(name) or bpy.data.lights.new(name, "AREA")
        ld.energy, ld.color, ld.size = energy, color, size
        ld.specular_factor = spec      # low = no hot-spot reflections on the floor
        ob = bpy.data.objects.get(name) or _link(bpy.data.objects.new(name, ld), coll)
        ob.location = loc
        ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        return ob

    area("Key", (-3.5, -5.0, 5.0), (0, 0, 1.2), t["key"], (1.0, 0.96, 0.92), 3.0, spec=0.35)
    area("Fill", (5.0, -6.0, 2.5), (0, 0, 1.2), t["key"] * t["fill"], (0.85, 0.9, 1.0), 4.0, spec=0.2)
    area("WallWash", (0, 2.5, 0.3), (0, 8, 4), t["wash_energy"], t["wash"], 6.0, spec=0.0)
    if rims:
        sx, sy = subject
        area("RimRed", (sx - 2.6, sy + 3.2, 3.0), (sx, sy, 1.3), t["rim_energy"], (1.0, 0.18, 0.14), 1.5, spec=0.8)
        area("RimBlue", (sx + 2.8, sy + 3.0, 3.2), (sx, sy, 1.3), t["rim_energy"] * 0.93, (0.3, 0.5, 1.0), 1.5, spec=0.8)
    if t.get("char_key"):
        # soft key on the character from front-left: its highlights trace the body
        area("CharKey", (subject[0] - 2.2, subject[1] - 3.0, 3.6), (subject[0], subject[1], 1.2), t["char_key"],
             (1.0, 0.97, 0.94), 1.6, spec=1.0)
    return coll


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

    def __init__(self, name, slides, width=2.4, depth=0.06, coll=None, glow=0.06, stand_height=0.0):
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

        alu = material("Board_Aluminium", (0.62, 0.63, 0.65), rough=0.32, metallic=0.9)
        box(name + "_Core", (width, depth, height), (0, 0, 0), material("Board_Core", (0.92, 0.92, 0.9), rough=0.7))
        f = 0.045
        for i, (sz, lc) in enumerate((((width + 2 * f, depth + 0.02, f), (0, 0, hh + f / 2)),
                                      ((width + 2 * f, depth + 0.02, f), (0, 0, -hh - f / 2)),
                                      ((f, depth + 0.02, height), (-hw - f / 2, 0, 0)),
                                      ((f, depth + 0.02, height), (hw + f / 2, 0, 0)))):
            box(f"{name}_Frame{i}", sz, lc, alu)
        if stand_height > 0:
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
        nt.links.new(prev, bsdf.inputs["Base Color"])
        nt.links.new(prev, bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = glow     # tiny lift for legibility only
        bsdf.inputs["Roughness"].default_value = 0.62              # matte print
        bsdf.inputs["Specular IOR Level"].default_value = 0.08     # no sheen: ink stays black
        self.index_nodes[face] = idx
        return m

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
def look(scene=None, samples=24, motion_blur=True, bloom=True, exposure=0.0):
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
    sc.view_settings.view_transform = "Standard"     # keeps slide/brand colours exact
    sc.view_settings.look = "None"
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
