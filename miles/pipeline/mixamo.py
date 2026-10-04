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
        self.in_place = 0.0            # 0..1: share of the clip's own hips travel cancelled by the root
        self.drift = {}                # scene frame -> hips xy offset from the clip's anchor (root space)

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


class ClipGroup:
    """Several back-to-back cycles of one clip, used like a single Clip (start/end/span/local...)."""

    def __init__(self, cycles):
        self.cycles = cycles
        first = cycles[0]
        self.action, self.frm, self.to, self.speed = first.action, first.frm, first.to, first.speed
        self.blend, self.face, self.repeat = first.blend, first.face, len(cycles)

    @property
    def start(self):
        return self.cycles[0].start

    @property
    def end(self):
        return self.cycles[-1].end

    @property
    def span(self):
        return self.end - self.start

    def local(self, scene_frame):
        for c in reversed(self.cycles):
            if scene_frame >= c.start:
                return c.local(scene_frame)
        return self.cycles[0].local(scene_frame)


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
             speed=1.0, repeat=1, cycle_blend=4, in_place=0.0):
        """Queue a clip. Starts `blend` frames before the previous clip ends unless `start` is given.

        repeat > 1 queues the clip that many times back to back (crossfading `cycle_blend`
        frames between cycles) and re-stitches root motion each cycle, so travel accumulates.
        (An NLA strip repeat would replay the hips from the start every cycle: walking on the spot.)
        in_place (0..1) cancels that share of the clip's own travel (emotes that stumble/jump
        far, e.g. a surprised step back); feet slide a little, the character stays on its mark.
        Returns the clip, or a ClipGroup spanning all cycles.
        """
        act = bpy.data.actions[action]
        a0, a1 = act.frame_range
        frm = a0 if frm is None else frm
        to = (frm + length) if length is not None else (a1 if to is None else to)
        if face is None:
            face = self.clips[-1].face if self.clips else self.face0
        cycles = []
        for k in range(max(1, repeat)):
            b = blend if k == 0 else cycle_blend
            s = start if (k == 0 and start is not None) else (self.clips[-1].end - b if self.clips else self.scene.frame_start)
            clip = Clip(act, s, frm, to, b if self.clips else 0, face, speed, 1)
            clip.in_place = float(in_place)
            self.clips.append(clip)
            cycles.append(clip)
        return cycles[0] if len(cycles) == 1 else ClipGroup(cycles)

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

    def extreme(self, action, bone, direction=(1, 0, 0), frm=None, to=None):
        """Action frame where `bone` reaches furthest from the hips along `direction`
        (root space, 0° facing). E.g. the hit frame of a punch/web-shot towards screen right."""
        act = bpy.data.actions[action]
        a0, a1 = act.frame_range
        frm, to = int(frm or a0), int(to or a1)
        d = Vector(direction).normalized()
        self.root.animation_data_clear()
        self.root.matrix_world = Matrix.Identity(4)
        best, best_f = -1e9, frm
        for f in range(frm, to + 1):
            hips = self._hips(act, f)
            pb = self.rig.pose.bones[bone]
            v = (self.rig.matrix_world @ pb.head - hips).dot(d)
            if v > best:
                best, best_f = v, f
        self.rig.animation_data.action = None
        return best_f

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
        nxt = {id(c): n.start for c, n in zip(self.clips, self.clips[1:])}
        for c in self.clips:
            if c.in_place > 0:
                anchor = self._hips(c.action, c.local(c.start + c.blend / 2.0)).xy
                c.drift = {f: (self._hips(c.action, c.local(f)).xy - anchor) * c.in_place
                           for f in range(int(c.start), int(nxt.get(id(c), c.end)) + 2, 2)}
        placements = [(Vector((self.x0, self.y0)), math.radians(self.clips[0].face))]
        for prev, cur in zip(self.clips, self.clips[1:]):
            mid = cur.start + cur.blend / 2.0
            p_loc, p_rot = placements[-1]
            hp = self._hips(prev.action, prev.local(mid)).xy - self._drift(prev, mid)
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
        for (prev, c, (loc, rot), (ploc, prot)) in zip(self.clips, self.clips[1:], placements[1:], placements):
            a, b = c.start, c.start + max(1, c.blend)
            pa = ploc - _rot(self._drift(prev, a), prot)
            anim.key(self.root, "location", a, pa.x, 0, "lin")
            anim.key(self.root, "location", a, pa.y, 1, "lin")
            anim.key(self.root, "rotation_euler", a, prot, 2, "inout")
            anim.key(self.root, "location", b, loc.x, 0, "lin")
            anim.key(self.root, "location", b, loc.y, 1, "lin")
            anim.key(self.root, "rotation_euler", b, rot, 2, "lin")
        for c, (loc, rot) in zip(self.clips, placements):          # in-place clips: counter their travel
            n = nxt.get(id(c), c.end)
            for f in sorted(c.drift):
                if c.start + max(1, c.blend) < f < n:
                    v = loc - _rot(c.drift[f], rot)
                    anim.key(self.root, "location", f, v.x, 0, "lin")
                    anim.key(self.root, "location", f, v.y, 1, "lin")
        return self

    @staticmethod
    def _drift(c, f):
        if not c.drift:
            return Vector((0.0, 0.0))
        k = min(c.drift, key=lambda x: abs(x - f))
        return c.drift[k]

    # ------------------------------------------------------------- polish passes
    FEET = ("mixamorig:LeftToeBase", "mixamorig:RightToeBase", "mixamorig:LeftFoot", "mixamorig:RightFoot")
    HANDS = ("mixamorig:LeftHand", "mixamorig:RightHand")
    PALM = 0.03                    # wrist height above the floor when a hand is planted

    def ground_lock(self, start, end, skip=(), taper=8, smooth=3, limit=0.2, step=2):
        """Keep the feet on the floor (z=0) between start and end.

        Retargeted mocap often hovers a few cm (hip-height scaling). Samples the lowest foot/toe
        every frame, smooths it, and keys a root-Z correction. `skip` = clips (or (a, b) frame
        ranges) that are meant to be airborne (hang, landing, cartwheel...); the correction tapers
        to 0 around them. Call after build() and after any root_z() keys (which must end before
        `start`).
        """
        ranges = [(c.start, c.end) if hasattr(c, "start") else c for c in skip]
        frames = list(range(int(start), int(end) + 1))
        low = []
        for f in frames:
            self.scene.frame_set(f)
            low.append(min(min((self.rig.matrix_world @ self.rig.pose.bones[b].head).z for b in self.FEET),
                           min((self.rig.matrix_world @ self.rig.pose.bones[b].head).z for b in self.HANDS) - self.PALM))
        # foot bones sit above the sole: calibrate against the rest pose's lowest foot point
        sole = getattr(self, "_sole", None)
        if sole is None:
            self.rig.data.pose_position = "REST"
            bpy.context.view_layer.update()
            sole = min((self.rig.matrix_world @ self.rig.data.bones[b].head_local).z for b in self.FEET) \
                - (self.root.matrix_world.translation.z)
            self.rig.data.pose_position = "POSE"
            bpy.context.view_layer.update()
            self._sole = sole = max(0.0, sole)
        corr = []
        for f, z in zip(frames, low):
            w = 1.0
            for a, b in ranges:
                d = max(a - f, f - b, 0) if not (a <= f <= b) else 0
                w = min(w, 0.0 if a <= f <= b else min(1.0, d / taper))
            corr.append(max(-limit, min(limit, (sole - z) * w)))
        sm = [sum(corr[max(0, i - smooth):i + smooth + 1]) / len(corr[max(0, i - smooth):i + smooth + 1])
              for i in range(len(corr))]
        base = {f: self.root.location.z for f in frames}
        fc = anim.fcurve(self.root, "location", 2)
        if fc:
            base = {f: fc.evaluate(f) for f in frames}
        for i in range(0, len(frames), step):
            f = frames[i]
            anim.key(self.root, "location", f, base[f] + sm[i], 2, "lin")
        return max(abs(c) for c in corr) if corr else 0.0

    def gesture_energy(self, action, length, stride=10, hands=("mixamorig:LeftHand", "mixamorig:RightHand")):
        """[(frm, energy)] — total wrist travel (relative to hips) for every `length`-frame window."""
        cache = self.__dict__.setdefault("_energy", {})
        key = (action, length, stride)
        if key in cache:
            return cache[key]
        act = bpy.data.actions[action]
        a0, a1 = (int(v) for v in act.frame_range)
        self.root.animation_data_clear()
        self.root.matrix_world = Matrix.Identity(4)
        pos = {}
        for f in range(a0, a1 + 1, 2):
            h = self._hips(act, f)
            pos[f] = [self.rig.matrix_world @ self.rig.pose.bones[b].head - h for b in hands]
        self.rig.animation_data.action = None
        fs = sorted(pos)
        speed = {fs[i]: sum((pos[fs[i]][k] - pos[fs[i - 1]][k]).length for k in range(len(hands))) for i in range(1, len(fs))}
        out = []
        for w0 in range(a0, max(a0 + 1, a1 - length), stride):
            out.append((w0, sum(v for f, v in speed.items() if w0 <= f < w0 + length)))
        cache[key] = out
        return out

    def lively(self, action, length, target=None):
        """Start frame of an unused `length`-frame window of `action` for a talk beat.

        target=None picks the most animated window; target=<energy per 60 frames> picks the window
        closest to that level (≈1.5 reads as a natural presenter; >4 looks frantic)."""
        used = self.__dict__.setdefault("_lively_used", {}).setdefault(action, [])
        rank = (lambda x: -x[1]) if target is None else (lambda x: abs(x[1] * 60 / length - target))
        for frm, e in sorted(self.gesture_energy(action, length), key=rank):
            if all(frm + length <= a or frm >= b for a, b in used):
                used.append((frm, frm + length))
                return frm
        return self.gesture_energy(action, length)[0][0]

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
