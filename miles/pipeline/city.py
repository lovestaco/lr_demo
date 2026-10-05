"""City set: the Sketchfab "City Scene" street (golukumar, Free Standard) + cinematic light +
in-world signage (graffiti walls, billboards, bus-stop lightboxes, LED screens) that carry the slides.

    from pipeline import city
    c = city.load()                         # imports the street, golden-hour sky + sun
    hit = c.wall((0, -20, 6), (1, 0, 0))    # first facade hit from a point along a direction
    city.sign("Wall1", img, hit.point, hit.normal, 6.0)     # a poster/mural on that wall

Layout (metres): avenue along Y at x≈0 (y -45..45), cross street along X at y≈0, four blocks of
buildings 11-37 m tall, a plaza north (y 51..91).
"""
import bpy, math, os
from mathutils import Vector, Matrix
from . import paths, fx, anim

GLB = os.path.join(paths.MIXAMO_CLIPS, "sketchfab_city_scene", "model.glb")


class Hit:
    def __init__(self, point, normal, obj):
        self.point, self.normal, self.obj = Vector(point), Vector(normal), obj


class City:
    def __init__(self, coll):
        self.coll = coll

    def ray(self, origin, direction, dist=200.0):
        dg = bpy.context.evaluated_depsgraph_get()
        ok, loc, nor, _i, ob, _m = bpy.context.scene.ray_cast(dg, Vector(origin), Vector(direction).normalized(), distance=dist)
        return Hit(loc, nor, ob) if ok else None

    def wall(self, origin, direction):
        """First vertical-ish surface hit (a facade) from origin along direction."""
        o = Vector(origin)
        for _ in range(6):
            h = self.ray(o, direction)
            if h is None:
                return None
            if abs(h.normal.z) < 0.35:
                return h
            o = h.point + Vector(direction).normalized() * 0.05
        return None

    def ground(self, x, y, top=80.0):
        h = self.ray((x, y, top), (0, 0, -1), top + 10)
        return h.point.z if h else 0.0

    def roof(self, x, y):
        """Height of the roof (or ground) under (x, y)."""
        return self.ground(x, y)


def load(coll_name="City"):
    coll = fx.collection(coll_name)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=GLB)
    for o in [o for o in bpy.data.objects if o not in before]:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
    golden_hour()
    return City(coll)


def golden_hour(sun_elev=8.0, sun_az=-60.0, strength=6.0, sky_strength=0.18):
    """Low warm sun raking down the avenue, cool sky: long shadows, warm facades, cool shade."""
    sc = bpy.context.scene
    w = sc.world or bpy.data.worlds.new("CityWorld")
    sc.world = w
    if w.node_tree is None:
        w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    sky = nt.nodes.new("ShaderNodeTexSky")
    for t in ("MULTIPLE_SCATTERING", "NISHITA", "SINGLE_SCATTERING", "HOSEK_WILKIE"):
        try:
            sky.sky_type = t
            break
        except TypeError:
            continue
    if hasattr(sky, "sun_elevation"):
        sky.sun_elevation = math.radians(sun_elev)
        sky.sun_rotation = math.radians(sun_az)
    if hasattr(sky, "sun_disc"):
        sky.sun_disc = False
    nt.links.new(sky.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = sky_strength
    nt.links.new(bg.outputs[0], out.inputs[0])
    sun = bpy.data.objects.get("Sun") or bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    if sun.name not in sc.collection.objects:
        sc.collection.objects.link(sun)
    sun.data.energy = strength
    sun.data.color = (1.0, 0.78, 0.55)
    sun.data.angle = math.radians(1.2)
    sun.rotation_euler = (math.radians(90 - sun_elev), 0, math.radians(sun_az + 90))
    return sun


def _plane(name, w, h, coll):
    me = bpy.data.meshes.new(name)
    me.from_pydata([(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, loop in enumerate(me.loops):
        uv.data[li].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][loop.vertex_index]
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def image_material(name, image_path, emit=0.0, rough=0.7, seq=None):
    """Image texture material; emit>0 makes it a lightbox/LED. seq=(n_frames, start) plays an image sequence."""
    m = bpy.data.materials.new(name)
    if m.node_tree is None:
        m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    img = bpy.data.images.load(image_path, check_existing=True)
    if seq:
        img.source = "SEQUENCE"
        tex.image_user.frame_duration = seq[0]
        tex.image_user.frame_start = seq[1]
        tex.image_user.use_auto_refresh = True
    tex.image = img
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    if emit:
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = emit
    return m


def sign(name, image_path, point, normal, width, aspect=16 / 9, offset=0.04, emit=0.0, frame=None, coll=None,
         seq=None, rough=0.7):
    """A flat image on a surface: mural/poster/billboard face. frame: None | 'billboard' | 'lightbox' | 'led'."""
    coll = coll or fx.collection("Signs")
    h = width / aspect
    n = Vector(normal).normalized()
    ob = _plane(name, width, h, coll)
    ob.data.materials.append(image_material(name + "_Mat", image_path, emit, rough, seq))
    ob.location = Vector(point) + n * offset
    ob.rotation_euler = (-n).to_track_quat("Y", "Z").to_euler()      # plane faces along -Y: point it out of the wall
    if frame:
        depth = {"billboard": 0.25, "lightbox": 0.18, "led": 0.3}[frame]
        rim = {"billboard": 0.12, "lightbox": 0.06, "led": 0.08}[frame]
        bm = bpy.data.meshes.new(name + "_Frame")
        import bmesh
        b = bmesh.new()
        bmesh.ops.create_cube(b, size=1.0)
        bmesh.ops.scale(b, vec=(width + 2 * rim, depth, h + 2 * rim), verts=b.verts)
        bmesh.ops.translate(b, vec=(0, depth / 2 + 0.01, 0), verts=b.verts)
        b.to_mesh(bm)
        b.free()
        fr = bpy.data.objects.new(name + "_Frame", bm)
        coll.objects.link(fr)
        fr.data.materials.append(fx.material(name + "_FrameMat", (0.05, 0.05, 0.06), rough=0.35, metallic=0.6))
        fr.parent = ob
    return ob


def flat_spot(c, xs, y_probe, side, z, width, tol=0.03):
    """First x in xs where the facade (hit from y_probe along side=±1 in y) is flat across `width`."""
    for x in xs:
        hits = [c.wall((x + dx, y_probe, z), (0, side, 0)) for dx in (-width / 2, -width / 4, 0, width / 4, width / 2)]
        if all(hits) and max(h.point.y for h in hits) - min(h.point.y for h in hits) < tol:
            return x, hits[2]
    return None, None


class Building:
    """A storeyed building for the finale: each floor can light up (facade turns blue + a label band
    slides on), and the stack can pancake when the ground floor is yanked out.

        b = Building("Finale", centre=(0, 59.5), width=24, depth=8.5, floors=4, storey=3.4, facade_img=...)
        b.light(i, frame, label_img)           # floor i turns blue and shows its label
        b.collapse(yank_frame, crash_frame, pull_dir)
    """

    def __init__(self, name, centre, width, depth, floors, storey, facade_img, coll=None):
        import bmesh
        self.coll = coll or fx.collection(name)
        self.name, self.w, self.d, self.n, self.h = name, width, depth, floors, storey
        self.c = Vector((centre[0], centre[1], 0.0))
        self.floors, self.mix = [], []
        for i in range(floors):
            root = fx.empty(f"{name}_F{i}", self.c + Vector((0, 0, storey * (i + 0.5))), self.coll, 0.3)
            me = bpy.data.meshes.new(f"{name}_F{i}_Mesh")
            b = bmesh.new()
            bmesh.ops.create_cube(b, size=1.0)
            bmesh.ops.scale(b, vec=(width, depth, storey), verts=b.verts)
            b.to_mesh(me)
            b.free()
            body = bpy.data.objects.new(f"{name}_F{i}_Body", me)
            self.coll.objects.link(body)
            body.parent = root
            m = bpy.data.materials.new(f"{name}_F{i}_Mat")
            if m.node_tree is None:
                m.use_nodes = True
            nt = m.node_tree
            bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
            tex = nt.nodes.new("ShaderNodeTexImage")
            tex.image = bpy.data.images.load(facade_img, check_existing=True)
            mix = nt.nodes.new("ShaderNodeMix")
            mix.data_type = "RGBA"
            mix.inputs[0].default_value = 0.0
            mix.inputs[7].default_value = (0.1, 0.38, 0.95, 1.0)
            nt.links.new(tex.outputs["Color"], mix.inputs[6])
            nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
            bsdf.inputs["Roughness"].default_value = 0.8
            # box UVs: map the facade image across each side face
            uv = me.uv_layers.new()
            for poly in me.polygons:
                nrm = poly.normal
                for li in poly.loop_indices:
                    v = me.vertices[me.loops[li].vertex_index].co
                    if abs(nrm.y) > 0.5:
                        uv.data[li].uv = (v.x / width + 0.5, v.z / storey + 0.5)
                    elif abs(nrm.x) > 0.5:
                        uv.data[li].uv = ((v.y / depth + 0.5) * depth / width, v.z / storey + 0.5)
                    else:
                        uv.data[li].uv = (0.5, 0.5)
            me.materials.append(m)
            self.floors.append(root)
            self.mix.append(mix)
        self.top = self.c.z + storey * floors

    def light(self, i, frame, label_img, ramp=8):
        anim.keys(self.mix[i].inputs[0], "default_value", [(int(frame) - 1, 0.0, "lin"), (int(frame) + ramp, 0.85, "out")])
        lw = min(self.w * 0.7, self.h * 0.78 * 4.0)              # label band fits inside its storey
        lab = sign(f"{self.name}_L{i}", label_img, Vector((0, -self.d / 2 - 0.02, 0)), Vector((0, -1, 0)), lw,
                   aspect=4.0, offset=0.0, emit=1.2, coll=self.coll)
        lab.parent = self.floors[i]
        lab.location = (0, -self.d / 2 - 0.03, 0)
        anim.visible(lab, [(1, False), (int(frame), True)])
        anim.keys(lab, "scale", [(int(frame), Vector((0.02, 1, 1)), "out"), (int(frame) + ramp, Vector((1, 1, 1)), "back")])
        return lab

    def collapse(self, yank, crash, pull=Vector((0, -1, 0)), dist=7.0):
        """Ground floor shoots out along `pull` at `yank`; the floors above drop one storey each
        (pancake), tilting and settling into a heap after `crash`."""
        import random
        r = random.Random(4)
        g = self.floors[0]
        p0 = g.location.copy()
        anim.keys(g, "location", [(int(yank), p0, "in"), (int(yank) + 10, p0 + pull * dist + Vector((0, 0, -0.4)), "out"),
                                  (int(yank) + 16, p0 + pull * (dist + 0.6) + Vector((0, 0, -0.4)))])
        anim.keys(g, "rotation_euler", [(int(yank), Vector((0, 0, 0))), (int(yank) + 16, Vector((0.05, 0.0, r.uniform(-0.25, 0.25))))])
        for i in range(1, self.n):
            f = self.floors[i]
            p = f.location.copy()
            s = int(crash) + (i - 1) * 2
            end = Vector((p.x + r.uniform(-0.8, 0.8), p.y + r.uniform(-0.6, 0.6), self.h * 0.32 * i + 0.3))
            tilt = Vector((r.uniform(-0.12, 0.12), r.uniform(-0.18, 0.18), r.uniform(-0.15, 0.15)))
            anim.keys(f, "location", [(s, p, "in"), (s + 9, end + Vector((0, 0, 0.25)), "out"), (s + 13, end, "bez")])
            anim.keys(f, "rotation_euler", [(s, Vector((0, 0, 0)), "in"), (s + 10, tilt, "out")])
            anim.keys(f, "scale", [(s + 8, Vector((1, 1, 1)), "out"), (s + 11, Vector((1.02, 1.02, 0.55)), "out")])
