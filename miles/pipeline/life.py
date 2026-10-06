"""City life: parked + moving traffic, pedestrians and pigeons, placed so they never break a shot.

Assets (Sketchfab; credits in ../blender_assets_downloaded/<folder>/CREDITS.txt):
    sketchfab_cars              10-car pack (CC-BY, comrade1280) — cars face the ring centre, wheels separate
    sketchfab_walk_*            in-place walk loops (Free Standard, denysalmaral), face +Y
    sketchfab_pigeon            rigged pigeon, 9 actions (CC-BY, AnimalMesh3D), faces +Y, real size

    g = life.Guard(cam_ob, hips_fn, (1, END))          # per-frame camera + subject cache
    cars = life.CarKit()                               # car prototypes
    car = cars.spawn(k, "Car3"); car.drive(p0, heading, [(f, s, ease), ...])
    walk = life.WalkKit(); w = walk.spawn(k, "Ped4"); w.walk(p0, p1, f0)
    birds = life.PigeonKit(); b = birds.spawn("Pg0"); b.perch(p, f0, face); b.fly_off(f, direction)

Every moving thing is checked against `Guard` (`clear()`): it never appears or vanishes inside the frame,
never passes through the camera or the subject, and never stands between the lens and the subject.
"""
import bpy, math, os, random
from mathutils import Vector, Matrix
from . import anim, fx, paths

DL = paths.MIXAMO_CLIPS


def _import(folder, coll):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(DL, folder, "model.glb"))
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
        if o.name.startswith("Icosphere"):                 # the asset's preview backdrop
            o.hide_render = o.hide_viewport = True
    return new


def _kit_collection(name):
    return fx.collection(name)


def _exclude(name):
    """Prototypes never render (exclude only after measuring them: excluded objects aren't evaluated)."""
    lc = bpy.context.view_layer.layer_collection.children.get(name)
    if lc:
        lc.exclude = True


def _clone(objs, coll, tag):
    """Copy a hierarchy (data shared), re-link parents and armature modifiers to the copies."""
    m = {}
    for o in objs:
        if o.name.startswith("Icosphere"):
            continue
        c = o.copy()
        c.name = f"{tag}_{o.name}"
        coll.objects.link(c)
        m[o] = c
    for o, c in m.items():
        if o.parent in m:
            c.parent = m[o.parent]
        for md in c.modifiers:
            if md.type == "ARMATURE" and md.object in m:
                md.object = m[md.object]
    return m


def _strip(ob, action, start, frm=None, to=None, repeat=1.0, scale=1.0, name=None, blend=0):
    ad = ob.animation_data or ob.animation_data_create()
    ad.action = None
    tr = ad.nla_tracks.new()
    st = tr.strips.new(name or action.name, int(start), action)
    if hasattr(st, "action_slot") and action.slots:
        st.action_slot = action.slots[0]
    a0, a1 = action.frame_range
    st.action_frame_start, st.action_frame_end = (a0 if frm is None else frm), (a1 if to is None else to)
    st.scale = scale
    st.repeat = repeat
    st.frame_start = start
    st.blend_in = blend
    st.extrapolation = "HOLD_FORWARD"
    st.use_auto_blend = False
    return st


def _yaw_to(d):
    """Z rotation that turns local +Y towards direction d."""
    return math.atan2(-d.x, d.y)


# ------------------------------------------------------------------ guard
class Guard:
    def __init__(self, cam_ob, subject_fn, frames, step=2):
        sc = bpy.context.scene
        self.step = step
        self.cam, self.inv, self.sub = {}, {}, {}
        for f in range(frames[0], frames[1] + 1, step):
            sc.frame_set(f)
            M = cam_ob.matrix_world.copy()
            self.cam[f] = (M, cam_ob.data.lens, cam_ob.data.sensor_width)
            self.inv[f] = M.inverted()
            self.sub[f] = Vector(subject_fn(f))
        self.aspect = sc.render.resolution_y / sc.render.resolution_x
        self.keepout = []                                   # (f0, f1, centre, radius): tower, bills, ...
        self.f_lo, self.f_hi = min(self.cam), max(self.cam)

    def _k(self, f):
        f = int(f)
        f -= (f - self.f_lo) % self.step
        return max(self.f_lo, min(self.f_hi, f))

    def in_view(self, f, p, margin=0.2, far=120.0):
        k = self._k(f)
        q = self.inv[k] @ Vector(p)
        if q.z > -0.2 or -q.z > far:
            return False
        M, lens, sw = self.cam[k]
        hx = sw / 2 / lens
        hy = hx * self.aspect
        return abs(q.x / -q.z) < hx * (1 + margin) and abs(q.y / -q.z) < hy * (1 + margin)

    def ok(self, f, p, r_sub=2.0, r_cam=2.5, r_line=0.9):
        k = self._k(f)
        p = Vector(p)
        c, s = self.cam[k][0].translation, self.sub[k]
        if (p - s).length < r_sub or (p - c).length < r_cam:
            return False
        d = s - c
        t = (p - c).dot(d) / max(1e-6, d.length_squared)
        if 0.0 < t < 1.0 and (c + d * t - p).length < r_line:
            return False
        for a, b, ctr, r in self.keepout:
            if a <= f <= b and (p.xy - ctr.xy).length < r:
                return False
        return True

    def clear(self, track, r_sub=2.0, r_cam=2.5, r_line=0.9):
        """track: [(frame, point)] samples of a moving thing (first/last = where it appears/vanishes)."""
        (fa, pa), (fb, pb) = track[0], track[-1]
        if self.in_view(fa, pa) or self.in_view(fb, pb):
            return False
        return all(self.ok(f, p, r_sub, r_cam, r_line) for f, p in track)


# ------------------------------------------------------------------ cars
class Car:
    def __init__(self, root, parts, wheels, radius, length):
        self.root, self.parts, self.wheels, self.radius, self.length = root, parts, wheels, radius, length

    def place(self, p, heading):
        self.root.location = Vector(p)
        self.root.rotation_euler = (0, 0, _yaw_to(Vector(heading)))

    def drive(self, p0, heading, keys, z=-0.08):
        """keys: [(frame, distance along heading, ease)]; wheels roll with the distance (no skid)."""
        h = Vector((heading[0], heading[1], 0)).normalized()
        p0 = Vector((p0[0], p0[1], z))
        self.root.rotation_euler = (0, 0, _yaw_to(h))
        anim.keys(self.root, "location", [(f, p0 + h * s, e) for f, s, e in keys])
        for w in self.wheels:
            anim.keys(w, "rotation_euler", [(f, -s / self.radius, e) for f, s, e in keys], index=0)

    def show(self, spans):
        for o in [self.root] + self.parts + self.wheels:
            anim.visible(o, spans)


class CarKit:
    def __init__(self, coll_name="CarKit"):
        kit = _kit_collection(coll_name)
        objs = _import("sketchfab_cars", kit)
        bpy.context.view_layer.update()
        meshes = [o for o in objs if o.type == "MESH" and not o.name.startswith(("Cylinder", "Icosphere"))]
        bodies = [o for o in objs if o.name.lower().endswith(" body")]
        bbox = lambda o: [o.matrix_world @ Vector(c) for c in o.bound_box]
        centre = lambda pts: sum(pts, Vector()) / len(pts)
        groups = {b: [m for m in meshes if m.parent == b] for b in bodies}
        groups = {b: g for b, g in groups.items() if g}
        ctr = {b: centre([p for m in g for p in bbox(m)]) for b, g in groups.items()}
        wheels = {b: [] for b in groups}
        for m in meshes:
            if "Wheel" in m.name:
                wc = centre(bbox(m))
                b = min(groups, key=lambda b: (ctr[b].xy - wc.xy).length)
                wheels[b].append(m)
        self.models = []
        for b, g in groups.items():
            c = ctr[b]
            fwd = Vector((-c.x, -c.y, 0)).normalized()                     # the pack's cars face the ring centre
            M = Matrix.Translation((c.x, c.y, 0)) @ Matrix.Rotation(_yaw_to(fwd), 4, "Z")
            inv = M.inverted()
            parts = [(m.data, inv @ m.matrix_world, None) for m in g]
            rad = []
            for w in wheels[b]:
                pts = bbox(w)
                wc = inv @ centre(pts)
                rad.append((max(p.z for p in pts) - min(p.z for p in pts)) / 2)
                parts.append((w.data, inv @ w.matrix_world, wc))
            loc = [inv @ p for m in g for p in bbox(m)]
            length = max(p.y for p in loc) - min(p.y for p in loc)
            width = max(p.x for p in loc) - min(p.x for p in loc)
            self.models.append({"name": b.name.replace(" Body", "").replace(" body", ""), "parts": parts,
                                "radius": sum(rad) / len(rad) if rad else 0.3, "length": length, "width": width})
        self.models.sort(key=lambda m: m["name"])
        _exclude(coll_name)

    def spawn(self, k, name, coll=None):
        coll = coll or fx.collection("Traffic")
        m = self.models[k % len(self.models)]
        root = fx.empty(name, (0, 0, 0), coll, 0.3)
        parts, wheels = [], []
        for i, (me, ml, wc) in enumerate(m["parts"]):
            ob = bpy.data.objects.new(f"{name}_{i}", me)
            coll.objects.link(ob)
            if wc is None:
                ob.parent = root
                ob.matrix_parent_inverse.identity()
                ob.matrix_basis = ml
            else:
                piv = fx.empty(f"{name}_W{i}", wc, coll, 0.1)
                piv.parent = root
                piv.matrix_parent_inverse.identity()
                piv.location = wc
                ob.parent = piv
                ob.matrix_parent_inverse.identity()
                ob.matrix_basis = Matrix.Translation(-wc) @ ml
                wheels.append(piv)
            parts.append(ob)
        return Car(root, parts, wheels, m["radius"], m["length"])


# ------------------------------------------------------------------ pedestrians
class Walker:
    def __init__(self, wrap, objs, arm, action, speed):
        self.wrap, self.objs, self.arm, self.action, self.speed = wrap, objs, arm, action, speed

    def walk(self, p0, p1, f0, phase=0.0):
        """Walk p0 → p1 starting at f0 at the clip's own stride speed (feet don't skate). Returns end frame."""
        p0, p1 = Vector((p0[0], p0[1], 0.0)), Vector((p1[0], p1[1], 0.0))
        d = p1 - p0
        n = max(1, int(round(d.length / self.speed)))
        self.wrap.rotation_euler = (0, 0, _yaw_to(d))
        anim.keys(self.wrap, "location", [(f0, p0, "lin"), (f0 + n, p1, "lin")])
        a0, a1 = self.action.frame_range
        cyc = a1 - a0
        _strip(self.arm, self.action, f0 - int(phase * cyc), repeat=(n + cyc) / cyc + 1)
        for o in self.objs:
            anim.visible(o, [(1, False), (f0, True), (f0 + n + 1, False)])
        return f0 + n


class WalkKit:
    FOLDERS = ("sketchfab_walk_male", "sketchfab_walk_female", "sketchfab_walk_male_phone", "sketchfab_walk_female_phone")

    def __init__(self, coll_name="WalkKit"):
        kit = _kit_collection(coll_name)
        self.kinds = []
        sc = bpy.context.scene
        for fo in self.FOLDERS:
            objs = _import(fo, kit)
            arm = next(o for o in objs if o.type == "ARMATURE")
            act = arm.animation_data.action
            feet = [b.name for b in arm.pose.bones if ("Foot" in b.name or "Toe" in b.name) and "root" not in b.name]
            a0, a1 = (int(v) for v in act.frame_range)
            prev, sp = None, []
            for f in range(a0, a1 + 1):                    # planted-foot speed = walking speed (m / frame)
                sc.frame_set(f)
                pts = {b: arm.matrix_world @ arm.pose.bones[b].head for b in feet}
                low = min(pts, key=lambda b: pts[b].z)
                if prev and prev[0] == low:
                    sp.append((pts[low] - prev[1]).xy.length)
                prev = (low, pts[low])
            sp.sort()
            speed = sp[len(sp) // 2] if sp else 0.04
            self.kinds.append((fo, [o for o in objs if not o.name.startswith("Icosphere")], arm, act, speed))
            for t in list(arm.animation_data.nla_tracks):
                arm.animation_data.nla_tracks.remove(t)
            arm.animation_data.action = None
        _exclude(coll_name)

    def spawn(self, k, name, coll=None):
        coll = coll or fx.collection("Crowd")
        fo, objs, arm, act, speed = self.kinds[k % len(self.kinds)]
        m = _clone(objs, coll, name)
        wrap = fx.empty(name, (0, 0, 0), coll, 0.2)
        for o, c in m.items():
            if o.parent is None:
                c.parent = wrap
        return Walker(wrap, list(m.values()) + [wrap], m[arm], act, speed)


# ------------------------------------------------------------------ pigeons
class Pigeon:
    def __init__(self, wrap, objs, arm, acts):
        self.wrap, self.objs, self.arm, self.acts = wrap, objs, arm, acts

    def perch(self, p, f0, face_deg=0.0, act="Pigeon_Look", phase=0):
        self.wrap.location = Vector(p)
        self.wrap.rotation_euler = (0, 0, math.radians(face_deg))
        a = self.acts[act]
        _strip(self.arm, a, f0 - phase, repeat=40)
        self.start = f0
        self.p = Vector(p)

    def fly_off(self, f, direction, speed=0.28, climb=0.45, dur=70, seed=0):
        """Startle: jump-flap off, then flap away along `direction` (m / frame), climbing, gently curving."""
        r = random.Random(seed)
        d = Vector((direction[0], direction[1], 0)).normalized()
        side = Vector((-d.y, d.x, 0)) * r.uniform(-0.25, 0.25)
        ad = self.arm.animation_data
        tr = ad.nla_tracks.new()                                     # takeoff then flap loop, over the idle
        jf, fl = self.acts["Pigeon_JFly"], self.acts["AA_Pigeon_Fly"]
        s1 = tr.strips.new("jfly", int(f), jf)
        if hasattr(s1, "action_slot") and jf.slots:
            s1.action_slot = jf.slots[0]
        s1.extrapolation = "NOTHING"
        tr2 = ad.nla_tracks.new()
        jl = jf.frame_range[1] - jf.frame_range[0]
        s2 = tr2.strips.new("fly", int(f + jl * 0.6), fl)
        if hasattr(s2, "action_slot") and fl.slots:
            s2.action_slot = fl.slots[0]
        s2.repeat = 60
        s2.extrapolation = "HOLD_FORWARD"
        keys, pos = [], self.p.copy()
        keys.append((f, pos.copy(), "lin"))
        v = Vector((0, 0, 0))
        for k in range(1, dur + 1, 2):
            acc = min(1.0, k / 10.0)
            v = (d + side * (k / dur)) * speed * acc + Vector((0, 0, climb * speed * (1.0 if k < 30 else 0.4)))
            pos = pos + v * 2
            keys.append((f + k, pos.copy(), "lin"))
        anim.keys(self.wrap, "location", keys)
        yaw = _yaw_to(d + side * 0.5)
        anim.keys(self.wrap, "rotation_euler", [(f, self.wrap.rotation_euler.z, "inout"), (f + 6, yaw, "const")], index=2)
        for o in self.objs:
            anim.visible(o, [(1, False), (self.start, True), (f + dur, False)])


class PigeonKit:
    def __init__(self, coll_name="PigeonKit"):
        kit = _kit_collection(coll_name)
        objs = _import("sketchfab_pigeon", kit)
        self.objs = [o for o in objs if not o.name.startswith("Icosphere")]
        self.arm = next(o for o in objs if o.type == "ARMATURE")
        self.acts = {}
        for a in bpy.data.actions:
            for key in ("Pigeon_Look", "Pigeon_JFly", "AA_Pigeon_Fly", "Pigeon_Bite", "Pigeon_Walk", "Pigeon_Floating"):
                if a.name.endswith("|" + key) and key not in self.acts:
                    self.acts[key] = a
        if self.arm.animation_data:
            for t in list(self.arm.animation_data.nla_tracks):
                self.arm.animation_data.nla_tracks.remove(t)
            self.arm.animation_data.action = None
        _exclude(coll_name)

    def spawn(self, name, coll=None):
        coll = coll or fx.collection("Pigeons")
        m = _clone(self.objs, coll, name)
        wrap = fx.empty(name, (0, 0, 0), coll, 0.1)
        for o, c in m.items():
            if o.parent is None:
                c.parent = wrap
        return Pigeon(wrap, list(m.values()) + [wrap], m[self.arm], self.acts)
