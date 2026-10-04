"""IT-employee props and overlay gestures for the Mixamo rig.

    office = props.Office(rig)            # lanyard + ID badge, smartwatch (left wrist), phone (right hand, hidden)
    office.check_watch(frame, hold=24)    # raise left wrist in front of chest, head looks at it
    office.check_phone(frame, hold=30)    # phone appears, right hand up, head looks at it
    office.reach(frame, target_point)     # right hand reaches/taps a world point (e.g. a TV power button)

Gestures are IK / look-at constraints whose influence is keyed 0 -> 1 -> 0, so they
layer on top of whatever clip is playing underneath (idle, walk, talk ...).
"""
import bpy, bmesh, math
from mathutils import Matrix, Vector
from . import anim, fx

P = "mixamorig:"


def _box(name, size, center, axes, mat, coll):
    """Box with half-extents along given world axes (3 orthonormal vectors)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    m = Matrix.Identity(4)
    for i in range(3):
        m[0][i], m[1][i], m[2][i] = axes[i] * size[i]
    m.translation = center
    bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob.data.materials.append(mat)
    bev = ob.modifiers.new("Bevel", "BEVEL")
    bev.width, bev.segments = min(size) * 0.25, 2
    return ob


def _frame_from(d, hint):
    d = d.normalized()
    x = (hint - d * hint.dot(d)).normalized()
    return [x, d, x.cross(d)]


class Office:
    def __init__(self, rig):
        self.rig = rig
        self.coll = fx.collection("Props_Office")
        rig.data.pose_position = "REST"
        bpy.context.view_layer.update()
        mw = rig.matrix_world
        bone = lambda n: rig.data.bones[P + n]
        head = lambda n: mw @ bone(n).head_local
        objs = []

        # --- lanyard + ID badge (LiveReview blue)
        badge_c = Vector((0.0, -0.078, 1.17))
        objs.append((_box("ID_Badge", (0.062, 0.095, 0.004), badge_c, [Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, 1, 0))],
                          fx.material("Badge_Card", (0.92, 0.94, 0.97), rough=0.35), self.coll), "Spine2"))
        objs.append((_box("ID_Badge_Stripe", (0.062, 0.022, 0.0045), badge_c + Vector((0, -0.0005, 0.03)),
                          [Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, 1, 0))],
                          fx.material("Badge_Blue", (0.23, 0.51, 0.96), rough=0.4, emit=0.3), self.coll), "Spine2"))
        strap = fx.material("Lanyard", (0.12, 0.32, 0.85), rough=0.6)
        for sx in (-1, 1):
            top = Vector((sx * 0.055, -0.02, 1.43))
            bot = badge_c + Vector((sx * 0.012, 0.0, 0.05))
            d = (bot - top)
            c = (top + bot) / 2
            axes = _frame_from(d, Vector((1, 0, 0)))
            objs.append((_box(f"Lanyard_{sx:+d}", (0.012, d.length, 0.003), c, [axes[0], axes[1], axes[2]], strap, self.coll),
                         "Spine2"))

        # --- smartwatch on the left wrist
        wrist, fore = head("LeftHand"), head("LeftForeArm")
        d = (wrist - fore).normalized()
        c = wrist - d * 0.035
        out = Vector((1, 0, 0))
        axes = _frame_from(d, out)                      # axes[0] = outward (back of wrist)
        band = bpy.data.meshes.new("Watch_Band")
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.041, radius2=0.041, depth=0.024)
        rot = Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4()
        bmesh.ops.transform(bm, matrix=Matrix.Translation(c) @ rot, verts=bm.verts)
        bm.to_mesh(band)
        bm.free()
        wb = bpy.data.objects.new("Watch_Band", band)
        self.coll.objects.link(wb)
        wb.data.materials.append(fx.material("Watch_Black", (0.02, 0.02, 0.025), rough=0.3))
        objs.append((wb, "LeftForeArm"))
        face = _box("Watch_Face", (0.03, 0.036, 0.008), c + axes[0] * 0.043, [axes[2], axes[1], axes[0]],
                    fx.material("Watch_Screen", (0.25, 0.75, 1.0), rough=0.2, emit=2.0), self.coll)
        objs.append((face, "LeftForeArm"))
        self.watch = face

        # --- phone in the right hand (hidden until used)
        rh, rtip = head("RightHand"), mw @ bone("RightHandMiddle1").head_local
        dh = (rtip - rh).normalized()
        palm = Vector((1, 0, 0))
        axes = _frame_from(dh, palm)
        pc = rh + dh * 0.06 + axes[0] * 0.03
        phone = _box("Phone", (0.072, 0.15, 0.009), pc, [axes[2], axes[1], axes[0]],
                     fx.material("Phone_Body", (0.04, 0.04, 0.05), rough=0.25, metallic=0.4), self.coll)
        glass = _box("Phone_Screen", (0.064, 0.135, 0.002), pc - axes[0] * 0.0055, [axes[2], axes[1], axes[0]],
                     fx.material("Phone_Glow", (0.45, 0.7, 1.0), rough=0.1, emit=2.5), self.coll)
        objs += [(phone, "RightHand"), (glass, "RightHand")]
        self.phone = [phone, glass]

        bpy.context.view_layer.update()
        for ob, bname in objs:
            m = ob.matrix_world.copy()
            ob.parent, ob.parent_type, ob.parent_bone = rig, "BONE", P + bname
            bpy.context.view_layer.update()
            ob.matrix_world = m
        rig.data.pose_position = "POSE"
        for ob in self.phone:
            anim.visible(ob, [(1, False)])

        # --- overlay controls: IK targets ride on the chest so gestures follow the body
        def target(name, rest_world):
            e = fx.empty(name, rest_world, self.coll, 0.05)
            m = Matrix.Translation(rest_world)          # (matrix_world isn't evaluated yet for a new object)
            e.parent, e.parent_type, e.parent_bone = rig, "BONE", P + "Spine2"
            bpy.context.view_layer.update()
            e.matrix_world = m
            return e

        rig.data.pose_position = "REST"
        bpy.context.view_layer.update()
        self.t_watch = target("IK_Watch", Vector((0.06, -0.34, 1.2)))
        self.p_left = target("Pole_Left", Vector((0.7, 0.1, 1.0)))
        self.t_phone = target("IK_Phone", Vector((-0.04, -0.33, 1.42)))
        self.p_right = target("Pole_Right", Vector((-0.7, 0.1, 1.0)))
        self.t_reach = fx.empty("IK_Reach", (0, 0, 0), self.coll, 0.05)
        rig.data.pose_position = "POSE"
        pb = rig.pose.bones
        self.ik_watch = self._ik(pb[P + "LeftForeArm"], self.t_watch, self.p_left, "IK watch")
        self.ik_phone = self._ik(pb[P + "RightForeArm"], self.t_phone, self.p_right, "IK phone")
        self.ik_reach = self._ik(pb[P + "RightForeArm"], self.t_reach, self.p_right, "IK reach")
        self.look_watch = self._look(pb[P + "Head"], self.watch, "Look watch")
        # presenter gesture: open hand towards a screen, either arm
        self.t_present = {sd: fx.empty(f"IK_Present_{sd}", (0, 0, 0), self.coll, 0.05) for sd in ("L", "R")}
        self.ik_present = {sd: self._ik(pb[P + ("LeftForeArm" if sd == "L" else "RightForeArm")], self.t_present[sd],
                                        self.p_left if sd == "L" else self.p_right, f"IK present {sd}")
                           for sd in ("L", "R")}
        self.look_phone = self._look(pb[P + "Head"], phone, "Look phone")

    @staticmethod
    def _ik(pbone, target, pole, name):
        c = pbone.constraints.new("IK")
        c.name, c.target, c.chain_count = name, target, 2
        c.pole_target, c.pole_angle = pole, -math.pi / 2
        c.influence = 0.0
        return c

    @staticmethod
    def _look(pbone, target, name):
        c = pbone.constraints.new("DAMPED_TRACK")
        c.name, c.target, c.track_axis = name, target, "TRACK_Z"
        c.influence = 0.0
        return c

    @staticmethod
    def _pulse(con, frame, ramp, hold, peak=1.0):
        f = int(frame)
        anim.keys(con, "influence", [(f, 0.0, "inout"), (f + ramp, peak, "inout"),
                                     (f + ramp + hold, peak, "inout"), (f + 2 * ramp + hold, 0.0, "bez")])

    def check_watch(self, frame, hold=24, ramp=8):
        self._pulse(self.ik_watch, frame, ramp, hold)
        self._pulse(self.look_watch, frame + 2, ramp, hold - 2, 0.75)
        return frame + 2 * ramp + hold

    def check_phone(self, frame, hold=30, ramp=8):
        self._pulse(self.ik_phone, frame, ramp, hold)
        self._pulse(self.look_phone, frame + 2, ramp, hold - 2, 0.7)
        for ob in self.phone:
            anim.visible(ob, [(int(frame) + 2, True), (int(frame + 2 * ramp + hold) - 2, False)])
        return frame + 2 * ramp + hold

    def present(self, frame, point, side="R", hold=22, ramp=9, amount=0.55):
        """Presenter "this one" gesture: arm sweeps part-way towards a world point (a screen) and back.
        Partial IK influence keeps the underlying talk clip's motion alive."""
        anim.key(self.t_present[side], "location", int(frame), Vector(point), ease="const")
        self._pulse(self.ik_present[side], frame, ramp, hold, amount)
        return frame + ramp

    def present_to(self, frame, point, from_x, **kw):
        """present() with the arm on the screen's side: screen to camera-right of him -> his left arm."""
        return self.present(frame, point, side="L" if point[0] > from_x else "R", **kw)

    def face_camera(self, cam, spans, amount=0.7, ramp=8):
        """Turn the head towards the camera during [(start, end), ...] (talking to the viewer).
        The head tracks an empty riding on the camera, so nod() can dip it for emphasis."""
        if "look_cam" not in self.__dict__:
            self.cam_eye = fx.empty("LookCam", (0, 0, 0), self.coll, 0.05)
            self.cam_eye.parent = cam
            self.look_cam = self._look(self.rig.pose.bones[P + "Head"], self.cam_eye, "Look camera")
        con = self.look_cam
        for a, b in spans:
            anim.keys(con, "influence", [(int(a), 0.0, "inout"), (int(a) + ramp, amount, "inout"),
                                         (int(b) - ramp, amount, "inout"), (int(b), 0.0, "bez")])
        return con

    def nod(self, frame, depth=0.7):
        """Emphasis nod on a stressed word (needs face_camera): the head's look point dips and recovers."""
        f = int(frame)
        anim.keys(self.cam_eye, "location", [(f - 4, 0.0, "out"), (f, -depth, "inout"), (f + 7, 0.0, "bez")], index=1)

    def beat(self, frame, point, side, amount=0.55):
        """Small hand 'beat' on a stressed word with the free arm (side = "L"/"R")."""
        return self.present(frame - 5, point, side=side, hold=4, ramp=5, amount=amount)

    def reach(self, frame, point, hold=6, ramp=7):
        anim.key(self.t_reach, "location", int(frame), Vector(point), ease="const")
        self._pulse(self.ik_reach, frame, ramp, hold)
        return frame + ramp
