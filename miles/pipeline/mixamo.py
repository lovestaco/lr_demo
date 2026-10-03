"""Chain Mixamo clips on one rig with crossfades and continuous root motion.

    perf = Performer(rig)                       # parents the rig to an empty "<rig>_Root"
    perf.place(x=-1.4, y=0, face=0)
    perf.then("Hanging Idle", length=100)
    perf.then("Hard Landing", blend=6)
    perf.then("Pull Heavy Object", repeat=2, face=65)
    perf.build()                                # NLA strips + root keys

Each clip is an NLA strip on its own track, blended in over `blend` frames.
Mixamo bakes travel into the Hips bone, so at every hand-off the root empty is
moved/rotated (over the blend window) so the hips continue from where the
previous clip left them. `face` is the heading in degrees (0 = towards -Y /
camera, 90 = screen right). Root Z is left free for your own keys (e.g. lowering
the character on a web); see `root_z()`.
"""
import bpy, math
from mathutils import Vector, Matrix
from . import anim

HIPS = "mixamorig:Hips"


class Clip:
    def __init__(self, action, start, frm, to, blend, face, speed, repeat):
        self.action, self.start, self.frm, self.to = action, start, frm, to
        self.blend, self.face, self.speed, self.repeat = blend, face, speed, repeat

    @property
    def span(self):
        return (self.to - self.frm) * self.repeat / self.speed

    @property
    def end(self):
        return self.start + self.span

    def local(self, scene_frame):
        """Action frame playing at a scene frame (clamped/held like the NLA strip)."""
        t = (scene_frame - self.start) * self.speed
        length = self.to - self.frm
        if t <= 0:
            return self.frm
        if t >= length * self.repeat:
            return self.to
        return self.frm + (t % length)


class Performer:
    def __init__(self, rig, scene=None):
        self.rig = rig
        self.scene = scene or bpy.context.scene
        name = rig.name + "_Root"
        self.root = bpy.data.objects.get(name)
        if self.root is None:
            self.root = bpy.data.objects.new(name, None)
            self.root.empty_display_type = "ARROWS"
            for c in rig.users_collection:
                c.objects.link(self.root)
        if rig.parent != self.root:
            rig.parent = self.root
            rig.matrix_parent_inverse = Matrix.Identity(4)
        self.clips = []
        self.x0, self.y0, self.face0 = 0.0, 0.0, 0.0

    # ------------------------------------------------------------- authoring
    def place(self, x=0.0, y=0.0, face=0.0):
        self.x0, self.y0, self.face0 = x, y, face
        return self

    def then(self, action, start=None, frm=None, to=None, length=None, blend=8, face=None,
             speed=1.0, repeat=1):
        """Queue a clip. Starts `blend` frames before the previous clip ends unless `start` is given."""
        act = bpy.data.actions[action]
        a0, a1 = act.frame_range
        frm = a0 if frm is None else frm
        to = (frm + length) if length is not None else (a1 if to is None else to)
        if start is None:
            start = self.clips[-1].end - blend if self.clips else self.scene.frame_start
        if face is None:
            face = self.clips[-1].face if self.clips else self.face0
        clip = Clip(act, start, frm, to, blend if self.clips else 0, face, speed, repeat)
        self.clips.append(clip)
        return clip

    @property
    def end(self):
        return self.clips[-1].end if self.clips else self.scene.frame_start

    # ------------------------------------------------------------- sampling
    def _hips(self, action, local_frame):
        """Hips position in root space for an action frame (root at identity)."""
        ad = self.rig.animation_data or self.rig.animation_data_create()
        ad.action = action
        ad.action_slot = action.slots[0]
        f = int(math.floor(local_frame))
        self.scene.frame_set(f, subframe=local_frame - f)
        pb = self.rig.pose.bones[HIPS]
        return self.rig.matrix_world @ pb.head

    # ------------------------------------------------------------- build
    def build(self):
        ad = self.rig.animation_data or self.rig.animation_data_create()
        for t in list(ad.nla_tracks):
            ad.nla_tracks.remove(t)
        self.root.animation_data_clear()
        self.root.location = (0, 0, 0)
        self.root.rotation_euler = (0, 0, 0)
        bpy.context.view_layer.update()

        # 1) root placement per clip (sampled with the root at identity)
        placements = [(Vector((self.x0, self.y0)), math.radians(self.clips[0].face))]
        for prev, cur in zip(self.clips, self.clips[1:]):
            mid = cur.start + cur.blend / 2.0
            p_loc, p_rot = placements[-1]
            hp = self._hips(prev.action, prev.local(mid)).xy
            hc = self._hips(cur.action, cur.local(mid)).xy
            world = p_loc + _rot(hp, p_rot)
            rot = math.radians(cur.face)
            placements.append((world - _rot(hc, rot), rot))
        ad.action = None

        # 2) NLA strips, one track per clip so later clips blend over earlier ones
        for i, c in enumerate(self.clips):
            tr = ad.nla_tracks.new()
            tr.name = f"{i:02d} {c.action.name}"
            st = tr.strips.new(c.action.name, int(c.start), c.action)
            if hasattr(st, "action_slot"):
                st.action_slot = c.action.slots[0]
            st.action_frame_start, st.action_frame_end = c.frm, c.to
            st.repeat = c.repeat
            st.scale = 1.0 / c.speed
            st.frame_start = c.start
            st.use_auto_blend = False
            st.blend_in = c.blend
            st.extrapolation = "HOLD" if i == 0 else "HOLD_FORWARD"

        # 3) root keys: hold, then glide to the new placement across each blend window
        loc0, rot0 = placements[0]
        f0 = self.clips[0].start
        anim.key(self.root, "location", f0, loc0.x, 0, "lin")
        anim.key(self.root, "location", f0, loc0.y, 1, "lin")
        anim.key(self.root, "rotation_euler", f0, rot0, 2, "lin")
        for (c, (loc, rot), (ploc, prot)) in zip(self.clips[1:], placements[1:], placements):
            a, b = c.start, c.start + max(1, c.blend)
            anim.key(self.root, "location", a, ploc.x, 0, "lin")
            anim.key(self.root, "location", a, ploc.y, 1, "lin")
            anim.key(self.root, "rotation_euler", a, prot, 2, "inout")
            anim.key(self.root, "location", b, loc.x, 0, "lin")
            anim.key(self.root, "location", b, loc.y, 1, "lin")
            anim.key(self.root, "rotation_euler", b, rot, 2, "lin")
        return self

    def root_z(self, seq):
        """Extra height for the whole character: [(frame, z, ease), ...]."""
        anim.keys(self.root, "location", seq, index=2)

    def bone_world(self, bone, frame, head_tail=0.0):
        self.scene.frame_set(int(frame))
        pb = self.rig.pose.bones[bone]
        return self.rig.matrix_world @ pb.head.lerp(pb.tail, head_tail)

    def clip_frame(self, clip, local_frame):
        """Scene frame at which `clip` plays a given action frame (first repeat)."""
        return clip.start + (local_frame - clip.frm) / clip.speed


def _rot(v2, ang):
    c, s = math.cos(ang), math.sin(ang)
    return Vector((v2.x * c - v2.y * s, v2.x * s + v2.y * c))
