"""Scene building blocks: studio, web strands, presentation board, camera, look.

All functions are idempotent-ish: they create named objects and return them.
"""
import bpy, bmesh, math
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


# ------------------------------------------------------------------ studio
THEMES = {
    # light: soft cool-grey cyclorama so the black suit reads clearly
    "light": dict(cyc=(0.55, 0.57, 0.62), rough=0.65, world=(0.62, 0.66, 0.74), world_strength=0.32,
                  key=320, fill=0.35, wash=(1.0, 0.97, 0.92), wash_energy=140, rim_energy=180),
    # dark: Spider-Verse night look with coloured rims
    "dark": dict(cyc=(0.012, 0.013, 0.025), rough=0.4, world=(0.004, 0.005, 0.012), world_strength=1.0,
                 key=900, fill=0.18, wash=(0.35, 0.12, 0.85), wash_energy=2500, rim_energy=1400),
}


def studio(theme="light", rims=True):
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
        area("RimRed", (-4.0, 3.5, 3.0), (0, 0, 1.3), t["rim_energy"], (1.0, 0.12, 0.10), 1.5, spec=0.12)
        area("RimBlue", (4.5, 3.0, 3.2), (0.5, 0, 1.3), t["rim_energy"] * 0.93, (0.25, 0.45, 1.0), 1.5, spec=0.12)
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


# ------------------------------------------------------------------ board
def board(name, front_png, back_png, width=2.4, depth=0.07, coll=None, glow=0.35,
          edge=(0.04, 0.04, 0.05), edge_glow=0.0):
    """Two-sided presentation panel: front faces -Y, back faces +Y; origin at centre."""
    height = width * 9 / 16
    root = empty(name, coll=coll, size=0.3)

    def face(nm, png, y, flip):
        me = bpy.data.meshes.new(nm)
        hw, hh = width / 2, height / 2
        if not flip:   # facing -Y
            verts = [(-hw, y, -hh), (hw, y, -hh), (hw, y, hh), (-hw, y, hh)]
            uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
        else:          # facing +Y, reads correctly from behind
            verts = [(hw, y, -hh), (-hw, y, -hh), (-hw, y, hh), (hw, y, hh)]
            uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
        me.from_pydata(verts, [], [(0, 1, 2, 3)])
        uv = me.uv_layers.new()
        for li, loop in enumerate(me.loops):
            uv.data[li].uv = uvs[loop.vertex_index]
        ob = _link(bpy.data.objects.new(nm, me), coll)
        ob.parent = root
        m = bpy.data.materials.new(nm + "_Mat")
        m.use_nodes = True if m.node_tree is None else m.use_nodes
        nt = m.node_tree
        bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(png, check_existing=True)
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = glow
        bsdf.inputs["Roughness"].default_value = 0.25
        ob.data.materials.append(m)
        return ob

    face(name + "_Front", front_png, -depth / 2 - 0.002, False)
    face(name + "_Back", back_png, depth / 2 + 0.002, True)
    # frame: dark slab + thin glowing blue edge
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(width + 0.08, depth, height + 0.08), verts=bm.verts)
    me = bpy.data.meshes.new(name + "_Frame")
    bm.to_mesh(me)
    bm.free()
    fr = _link(bpy.data.objects.new(name + "_Frame", me), coll)
    fr.parent = root
    fr.data.materials.append(material("Board_Edge", edge, rough=0.35, emit=edge_glow,
                                      emit_color=(0.23, 0.51, 0.96)))
    bev = fr.modifiers.new("Bevel", "BEVEL")
    bev.width, bev.segments = 0.03, 3
    hook = empty(name + "_Hook", (-width / 2 - 0.04, 0, 0), coll, 0.1)
    hook.parent = root
    return root, hook


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
def look(scene=None, samples=24, motion_blur=True, bloom=True):
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
