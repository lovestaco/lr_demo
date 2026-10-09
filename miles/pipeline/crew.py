"""Construction crew for the building sites: hammering workers, a boss who gives instructions, builder robots and
robot arms. Same idea as life.WalkKit: each model is imported once into an excluded collection and cloned per use
(mesh data shared), its own animation looped on an NLA track with a phase offset.

Assets (Sketchfab, CC-BY; credits in ../blender_assets_downloaded/<folder>/CREDITS.txt):
    sketchfab_worker_hammer   "Low-Poly Construction workers (animated)" (jungle_jim): orange hi-vis, hammering loop
    sketchfab_worker_boss     "Construction Worker" (katelaruine): Mixamo rig, untextured -> coloured per part here;
                              driven by one of Spidey's clips (retarget_from: rest-relative world rotations)
    sketchfab_robot_builder   "Construction Robot" (darkboy571): object-animated idle
    sketchfab_robot_arm       "Low Poly Robot Arm / Animated" (Myjato): 7-joint arm, working loop

    crew = crew.Crew()
    w = crew.worker("Worker0", (x, y), face=(0, -1), phase=0.3)          # faces the wall, hammers
    b = crew.boss("Boss", (x, y), face=(1, 0), rig=MilesRig, clip="CMU 18_08 conversation - explain with hand gesture")
    r = crew.robot("Bot0", (x, y), face=(0, 1)); a = crew.arm("Arm0", (x, y), face=(0, 1), height=2.2)
    crew.show(ob_list, [(1, False), (f0, True), (f1, False)])
"""
import bpy, math, re
from mathutils import Vector, Matrix
from . import anim, fx, life

FOLDERS = {"worker": "sketchfab_worker_hammer", "boss": "sketchfab_worker_boss", "robot": "sketchfab_robot_builder",
           "arm": "sketchfab_robot_arm"}
HEIGHT = {"worker": 1.75, "boss": 1.8, "robot": 1.25, "arm": 2.2}
BOSS_COLORS = {"Object_94": (0.92, 0.92, 0.9), "Object_92": (0.08, 0.2, 0.42), "Object_88": (0.22, 0.2, 0.17),
               "Object_98": (0.1, 0.07, 0.05), "Object_90": (0.55, 0.36, 0.24), "Object_86": (0.02, 0.02, 0.02),
               "Object_96": (0.02, 0.02, 0.02)}           # helmet, jacket, trousers, boots, head, eyes, brows (linear)


class Unit:
    def __init__(self, wrap, objs, arm=None):
        self.wrap, self.objs, self.arm = wrap, objs, arm

    def show(self, spans):
        for o in self.objs:
            anim.visible(o, spans)


class Crew:
    def __init__(self, coll_name="CrewKit"):
        self.kit = fx.collection(coll_name)
        self.coll_name = coll_name
        self.src = {}
        sc = bpy.context.scene
        for kind, fo in FOLDERS.items():
            acts0 = set(bpy.data.actions)
            objs = [o for o in life._import(fo, self.kit) if not o.name.startswith("Icosphere")]
            acts = [a for a in bpy.data.actions if a not in acts0]
            bpy.context.view_layer.update()
            meshes = [o for o in objs if o.type == "MESH"]
            dg = bpy.context.evaluated_depsgraph_get()
            pts = []
            for o in meshes:
                e = o.evaluated_get(dg)
                m = e.to_mesh()
                pts += [o.matrix_world @ v.co for v in m.vertices]
                e.to_mesh_clear()
            lo = Vector([min(p[i] for p in pts) for i in range(3)])
            hi = Vector([max(p[i] for p in pts) for i in range(3)])
            arm = next((o for o in objs if o.type == "ARMATURE"), None)
            if arm is not None and arm.animation_data:                 # the clips the rig really plays (the longest
                ad_ = arm.animation_data                             # first); stray 1-frame copies come along too
                used = {ad_.action} | {st.action for t in ad_.nla_tracks for st in t.strips}
                used.discard(None)
                if used:
                    acts = sorted(used, key=lambda a: -(a.frame_range[1] - a.frame_range[0]))
            fwd = self._forward(arm) if kind in ("worker", "boss") else Vector((0, -1, 0))
            self.src[kind] = dict(objs=objs, acts=acts, arm=arm, scale=HEIGHT[kind] / max(1e-6, hi.z - lo.z),
                                  centre=Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z)), fwd=fwd)
            print("CREW", kind, "height", round(hi.z - lo.z, 2), "acts", [a.name for a in acts], "fwd", tuple(round(v, 2) for v in fwd))
        if self.src["boss"]["arm"]:
            for o in self.src["boss"]["objs"]:
                if o.type == "MESH" and o.name in BOSS_COLORS:
                    o.data.materials[0] = fx.material(f"Boss_{o.name}", BOSS_COLORS[o.name], rough=0.7)
        life._exclude(coll_name)

    @staticmethod
    def _forward(arm):
        """Which way a character faces: from the heels to the toes, rest pose."""
        if arm is None:
            return Vector((0, -1, 0))
        bones = arm.data.bones
        d = Vector()
        feet = [b for b in bones if re.search(r"(L|R|Left|Right)_?Foot", b.name) and "end" not in b.name.lower()]
        for b in feet:
            d += (arm.matrix_world @ b.tail_local) - (arm.matrix_world @ b.head_local)
        d.z = 0
        return d.normalized() if d.length > 1e-6 else Vector((0, -1, 0))

    def _spawn(self, kind, name, p, face, coll):
        s = self.src[kind]
        coll = coll or fx.collection("Crew")
        m = life._clone(s["objs"], coll, name)
        wrap = fx.empty(name, (0, 0, 0), coll, 0.2)
        inner = fx.empty(name + "_Fit", (0, 0, 0), coll, 0.1)       # scale + recentre the asset, its own forward -> local -Y
        inner.parent = wrap
        inner.matrix_basis = Matrix.Rotation(-math.pi / 2 - math.atan2(s["fwd"].y, s["fwd"].x), 4, "Z") @ \
            Matrix.Scale(s["scale"], 4) @ Matrix.Translation(-s["centre"])
        for o, c in m.items():
            if o.parent is None:
                c.parent = inner
        d = Vector((face[0], face[1], 0)).normalized()
        wrap.location = Vector((p[0], p[1], p[2] if len(p) > 2 else 0.0))
        wrap.rotation_euler = (0, 0, math.atan2(d.x, -d.y))             # local -Y -> face
        arm = next((c for o, c in m.items() if c.type == "ARMATURE"), None)
        return Unit(wrap, list(m.values()) + [wrap, inner], arm)

    @staticmethod
    def _loop(ob, action, phase=0.0, repeat=60.0, speed=1.0, slot=None):
        ad = ob.animation_data or ob.animation_data_create()
        ad.action = None
        for t in ad.nla_tracks:                              # the importer stashes every clip as a live track
            t.mute = True
        tr = ad.nla_tracks.new()
        a0, a1 = action.frame_range
        st = tr.strips.new(action.name, int(1 - phase * (a1 - a0)), action)
        if hasattr(st, "action_slot") and action.slots:
            st.action_slot = slot or action.slots[0]
        st.action_frame_start, st.action_frame_end = a0, a1    # (read before the slot was set: a 1-frame range)
        st.frame_start = int(1 - phase * (a1 - a0))
        st.repeat = repeat
        st.scale = 1.0 / speed
        st.extrapolation = "HOLD_FORWARD"
        st.use_animated_influence = True                    # (an API-made strip can evaluate at influence 0)
        st.influence = 1.0
        st.keyframe_insert("influence", frame=1)
        return st

    def worker(self, name, p, face=(0, -1), phase=0.0, speed=1.0, coll=None):
        u = self._spawn("worker", name, p, face, coll)
        self._loop(u.arm, self.src["worker"]["acts"][0], phase, speed=speed)
        return u

    def robot(self, name, p, face=(0, -1), phase=0.0, coll=None):
        u = self._spawn("robot", name, p, face, coll)
        src = {o.name: o for o in self.src["robot"]["objs"]}
        for c in u.objs:
            o = src.get(c.name.split("_", 1)[1]) if "_" in c.name else None
            if o is not None and o.animation_data and o.animation_data.action:
                act = o.animation_data.action
                self._loop(c, act, phase, repeat=80, slot=o.animation_data.action_slot)
        return u

    def arm(self, name, p, face=(0, -1), phase=0.0, speed=1.0, coll=None):
        u = self._spawn("arm", name, p, face, coll)
        self._loop(u.arm, self.src["arm"]["acts"][0], phase, repeat=30, speed=speed)
        return u

    def boss(self, name, p, face=(0, -1), rig=None, clip=None, frames=None, coll=None):
        """The boss; with rig + clip he performs one of Spidey's clips (retargeted), else his own idle."""
        u = self._spawn("boss", name, p, face, coll)
        if rig is not None and clip:
            if not hasattr(self, "_baked"):
                self._baked = {}
            if clip not in self._baked:                      # one bake per clip, shared by every boss
                self._baked[clip] = retarget(rig, bpy.data.actions[clip], self.src["boss"]["arm"], frames=frames)
            act = self._baked[clip]
        else:
            act = next(a for a in self.src["boss"]["acts"] if "Idle" in a.name)
        self._loop(u.arm, act, 0.0, repeat=40)
        return u


def person(crew_, name, p, face=(0, -1), colors=None, coll=None):
    """A customer: the boss model without the hard hat, in his own colours (per-object material slots)."""
    u = crew_._spawn("boss", name, p, face, coll)
    colors = colors or {"Object_92": (0.55, 0.08, 0.1), "Object_88": (0.06, 0.08, 0.16), "Object_98": (0.05, 0.05, 0.05)}
    for c in u.objs:
        src = c.name.split("_", 1)[1] if "_" in c.name else ""
        if c.type != "MESH":
            continue
        if src == "Object_94":                                # the hard hat
            c.hide_render = c.hide_viewport = True
        elif src in colors and c.material_slots:
            c.material_slots[0].link = "OBJECT"
            c.material_slots[0].material = fx.material(f"{name}_{src}", colors[src], rough=0.7)
    return u


def in_place(action, root="Hips"):
    """A copy of a clip with its root's travel removed (keeps the bob: bone-local Y is up for a Mixamo hips)."""
    act = action.copy()
    act.name = action.name + " (in place)"
    bags = [cb for ly in getattr(act, "layers", []) for st in ly.strips for cb in st.channelbags]
    fcs = [fc for cb in bags for fc in cb.fcurves] if bags else list(getattr(act, "fcurves", []))
    for cb in bags or [None]:
        for fc in list(cb.fcurves if cb else act.fcurves):
            if root in fc.data_path and fc.data_path.endswith("location") and fc.array_index != 1:
                (cb.fcurves if cb else act.fcurves).remove(fc)
    return act


def sequence(arm, clips):
    """[(action, f0, f1), ...] one after another on stacked NLA tracks (later on top), each held inside its span."""
    ad = arm.animation_data or arm.animation_data_create()
    ad.action = None
    for t in ad.nla_tracks:
        t.mute = True
    for action, f0, f1 in clips:
        tr = ad.nla_tracks.new()
        st = tr.strips.new(action.name, int(f0), action)
        if hasattr(st, "action_slot") and action.slots:
            st.action_slot = action.slots[0]
        a0, a1 = action.frame_range
        st.action_frame_start, st.action_frame_end = a0, a1
        st.frame_start = int(f0)
        st.repeat = max(1.0, (f1 - f0) / max(1.0, a1 - a0))
        st.extrapolation = "NOTHING"
        st.use_animated_influence = True
        st.influence = 1.0
        st.keyframe_insert("influence", frame=int(f0))


def _strip_suffix(n):
    return re.sub(r"_\d+$", "", n)


def retarget(src_rig, action, dst_arm, frames=None, step=1):
    """Bake `action` (made for src_rig) onto dst_arm (same Mixamo bone names up to a _NN suffix): every bone gets
    the source bone's world-space rotation change from its rest pose (bone rolls / rest axes may differ). In place
    (no hips translation). Returns the new action."""
    sc = bpy.context.scene
    proxy = bpy.data.objects.new("RetargetProxy", src_rig.data)
    sc.collection.objects.link(proxy)
    proxy.matrix_world = src_rig.matrix_world.copy()        # the rig's own transform (its clips assume it)
    bpy.context.view_layer.update()                          # (a new armature object has no pose until evaluated)
    for pb in proxy.pose.bones:
        for c in list(pb.constraints):
            pb.constraints.remove(c)
    ad = proxy.animation_data_create()
    ad.action = action
    if hasattr(ad, "action_slot") and action.slots:
        ad.action_slot = action.slots[0]
    a0, a1 = (int(v) for v in action.frame_range)
    frames = frames or (a0, a1)
    dst_bones = {_strip_suffix(b.name): b.name for b in dst_arm.data.bones}
    fwd = Crew._forward(dst_arm)                             # the dst rest heading (world)
    fwd_s = Crew._forward(proxy)                             # the src rest heading: Spidey's rig faces the other way
    Rh = Matrix.Rotation(math.atan2(fwd_s.x * fwd.y - fwd_s.y * fwd.x, fwd_s.x * fwd.x + fwd_s.y * fwd.y), 3, "Z")
    hips_s = next((s for s in (pb.name for pb in proxy.pose.bones) if s.endswith("Hips")), None)
    pairs = [(pb.name, dst_bones[pb.name]) for pb in proxy.pose.bones if pb.name in dst_bones]
    S3 = proxy.matrix_world.to_3x3().normalized()
    D3 = dst_arm.matrix_world.to_3x3().normalized()
    rest_s = {s: (S3 @ proxy.data.bones[s].matrix_local.to_3x3()).normalized() for s, d in pairs}
    rest_d = {d: dst_arm.data.bones[d].matrix_local.to_3x3().normalized() for s, d in pairs}
    # the rest poses differ (Spidey's rig rests in an A-pose, the boss in a T-pose): first turn each dst bone onto the
    # src bone's rest direction (shortest arc, world), then apply the src bone's change from its rest
    dirw = lambda arm_, b: (arm_.matrix_world.to_3x3() @ (b.tail_local - b.head_local)).normalized()
    align = {d: dirw(dst_arm, dst_arm.data.bones[d]).rotation_difference(Rh @ dirw(proxy, proxy.data.bones[s])).to_matrix() for s, d in pairs}
    order = [d for d in (b.name for b in dst_arm.data.bones) if d in rest_d]          # parents first
    src_of = {d: s for s, d in pairs}
    out = bpy.data.actions.new(f"{action.name} -> {dst_arm.name}")
    dad = dst_arm.animation_data or dst_arm.animation_data_create()
    keep = dad.action
    dad.action = out
    for f in range(frames[0], frames[1] + 1, step):
        sc.frame_set(f)
        M = {}
        # the clip's own turn (its body heading) is taken out: the dst keeps facing where it was placed
        yaw = Matrix.Identity(3)
        if hips_s in rest_s:
            h = (Rh @ (S3 @ proxy.pose.bones[hips_s].matrix.to_3x3()).normalized() @ rest_s[hips_s].inverted() @ Rh.inverted()) @ fwd
            yaw = Matrix.Rotation(-math.atan2(fwd.x * h.y - fwd.y * h.x, fwd.x * h.x + fwd.y * h.y), 3, "Z")
        for d in order:
            s = src_of[d]
            ws = (S3 @ proxy.pose.bones[s].matrix.to_3x3()).normalized()
            delta = yaw @ Rh @ ws @ rest_s[s].inverted() @ Rh.inverted()       # the src motion, turned to the dst heading
            M[d] = (D3.inverted() @ delta @ align[d] @ D3 @ rest_d[d]).normalized()   # armature space, dst
        for d in order:
            b = dst_arm.data.bones[d]
            par = b.parent
            while par is not None and par.name not in M:
                par = par.parent
            if par is None:
                basis = rest_d[d].inverted() @ M[d]
            else:
                basis = (rest_d[d].inverted() @ par.matrix_local.to_3x3()) @ M[par.name].inverted() @ M[d]
            pb = dst_arm.pose.bones[d]
            pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = basis.to_quaternion()
            pb.keyframe_insert("rotation_quaternion", frame=f - frames[0])
    dad.action = keep
    bpy.data.objects.remove(proxy)
    return out
