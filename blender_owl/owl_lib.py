"""Owl action library: a keyframing "vocabulary" for the cube owl rig.

Use from Blender (MCP execute_blender_code, the Text Editor, or a headless
script) with owl_street.blend / owl_rig.blend open:

    import sys; sys.path.insert(0, "/home/lovestaco/pers/lr_demo/blender_owl")
    import importlib, owl_lib; importlib.reload(owl_lib)
    owl = owl_lib.Owl()            # rig "OwlRig", cursor at scene.frame_start
    cam = owl_lib.Cam(owl)
    owl.reset()                    # wipe old animation
    owl.place(-6)
    owl.walk_to(4); owl.skid(); owl.hop(2); owl.cartwheel(-8)
    owl.wave(); owl.talk("Hi, I'm Livi!")
    owl.finish()                   # auto-blinks + sets scene.frame_end

Every action starts at the owl's time cursor `owl.t`, keys only the channels
it uses, and moves the cursor to its end.  Pass `at=<frame>` to start
somewhere else and `advance=False` to layer it under the next action (e.g.
talk while walking).  Directions such as "left"/"right" are screen
directions as seen from the default camera (-Y looking at +Y).
"""
import bpy, math, random, re
from mathutils import Vector

FPS = 24
PROP = {"loc": "location", "rot": "rotation_euler", "scl": "scale"}
REST = {"location": 0.0, "rotation_euler": 0.0, "scale": 1.0}
FACING = {"camera": 0.0, "front": 0.0, "right": math.pi / 2, "left": -math.pi / 2,
          "away": math.pi, "back": math.pi}


# ------------------------------------------------------------- keying core
def _fcurve(id_, path, index):
    ad = id_.animation_data
    if not ad or not ad.action:
        return None
    for layer in ad.action.layers:
        for strip in layer.strips:
            cb = strip.channelbag(ad.action_slot)
            if cb:
                fc = cb.fcurves.find(path, index=index)
                if fc:
                    return fc
    return None


class _Keyer:
    """Keys (owner, property, index) channels on one ID with explicit easing.

    The interpolation given to a key controls the segment that LEAVES it.
    """

    def __init__(self, id_):
        self.id = id_

    def val(self, owner, prop, idx, frame):
        fc = _fcurve(self.id, owner.path_from_id(prop), idx)
        if fc and len(fc.keyframe_points):
            return fc.evaluate(frame)
        return getattr(owner, prop)[idx]

    def key(self, owner, prop, idx, frame, value, interp="BEZIER", easing=None, cut=False):
        getattr(owner, prop)[idx] = value
        owner.keyframe_insert(prop, index=idx, frame=frame)
        fc = _fcurve(self.id, owner.path_from_id(prop), idx)
        prev = None
        for kp in fc.keyframe_points:
            if abs(kp.co.x - frame) < 0.01:
                kp.interpolation = interp
                if easing:
                    kp.easing = easing
            elif kp.co.x < frame and (prev is None or kp.co.x > prev.co.x):
                prev = kp
        if cut and prev is not None:
            prev.interpolation = "CONSTANT"


def _ease(spec):
    """'bez' | 'lin' | 'const' | 'back' | 'elastic' | 'bounce' | 'in' | 'out' | 'inout'"""
    return {
        None: ("BEZIER", None), "bez": ("BEZIER", None), "lin": ("LINEAR", None),
        "const": ("CONSTANT", None), "back": ("BACK", "EASE_OUT"),
        "elastic": ("ELASTIC", "EASE_OUT"), "bounce": ("BOUNCE", "EASE_OUT"),
        "in": ("QUAD", "EASE_IN"), "out": ("QUAD", "EASE_OUT"),
        "inout": ("SINE", "EASE_IN_OUT"),
    }[spec]


# ------------------------------------------------------------------- owl
class Owl:
    def __init__(self, rig="OwlRig", scene=None, seed=1):
        self.scene = scene or bpy.context.scene
        self.rig = bpy.data.objects[rig]
        self.pb = self.rig.pose.bones
        self.k = _Keyer(self.rig)
        self.t = self.scene.frame_start
        self.zc = float(self.rig.get("body_center", 1.88))
        self.rnd = random.Random(seed)
        self.markers = []

    # ---- low level ------------------------------------------------------
    def _res(self, ch):
        b, p, i = ch
        owner = self.rig if b == "obj" else self.pb[b]
        return owner, PROP[p], i

    def get(self, ch, frame=None):
        o, p, i = self._res(ch)
        return self.k.val(o, p, i, self.t if frame is None else frame)

    def hold(self, frame, chans):
        for ch in chans:
            o, p, i = self._res(ch)
            self.k.key(o, p, i, frame, self.k.val(o, p, i, frame))

    def pose(self, frame, values, ease=None, cut=False):
        interp, easing = _ease(ease)
        for ch, v in values.items():
            o, p, i = self._res(ch)
            self.k.key(o, p, i, frame, v, interp, easing, cut)

    def seq(self, start, frames, hold=True):
        """frames: [(dt, {channel: value}, ease), ...]; holds channels at start."""
        if hold:
            chans = {ch for _, d, *_ in frames for ch in d}
            self.hold(start, chans)
        end = start
        for fr in frames:
            dt, d = fr[0], fr[1]
            ease = fr[2] if len(fr) > 2 else None
            self.pose(start + dt, d, ease)
            end = max(end, start + dt)
        return end

    def _start(self, at):
        return self.t if at is None else at

    def _done(self, end, advance):
        if advance:
            self.t = max(self.t, end)
        return end

    def rest_values(self, chans):
        return {ch: REST[PROP[ch[1]]] for ch in chans}

    def mark(self, name, frame=None):
        """Add a timeline marker (handy when syncing to narration)."""
        f = self._start(frame)
        self.scene.timeline_markers.new(name, frame=int(f))
        return f

    # ---- setup ----------------------------------------------------------
    def reset(self):
        """Remove all owl animation and return to rest pose."""
        if self.rig.animation_data:
            self.rig.animation_data_clear()
        for pb in self.pb:
            pb.location = (0, 0, 0)
            pb.rotation_euler = (0, 0, 0)
            pb.scale = (1, 1, 1)
        self.rig.location = (0, 0, 0)
        self.rig.rotation_euler = (0, 0, 0)
        self.t = self.scene.frame_start
        return self

    def wait(self, frames):
        self.t += frames
        return self.t

    def seconds(self, s):
        return int(round(s * FPS))

    def place(self, x, y=0.0, facing="camera", at=None):
        """Teleport (hard cut) the owl to (x, y) on the ground."""
        f = self._start(at)
        ang = FACING.get(facing, facing) if isinstance(facing, str) else facing
        self.pose(f, {("obj", "loc", 0): x, ("obj", "loc", 1): y, ("obj", "loc", 2): 0.0,
                      ("obj", "rot", 2): ang}, cut=True)
        return f

    def pos(self, frame=None):
        f = self._start(frame)
        return Vector((self.get(("obj", "loc", 0), f), self.get(("obj", "loc", 1), f),
                       self.get(("obj", "loc", 2), f)))

    def heading(self, frame=None):
        return self.get(("obj", "rot", 2), self._start(frame))

    def forward(self, frame=None):
        a = self.heading(frame)
        return Vector((math.sin(a), -math.cos(a), 0))

    # ---- locomotion -----------------------------------------------------
    def turn(self, facing="camera", dur=7, hop=True, at=None, advance=True):
        """Turn to 'camera' | 'left' | 'right' | 'away' | angle(rad)."""
        s = self._start(at)
        cur = self.heading(s)
        tgt = FACING.get(facing, facing) if isinstance(facing, str) else facing
        tgt = cur + ((tgt - cur + math.pi) % (2 * math.pi) - math.pi)
        if abs(tgt - cur) < 1e-3:
            return self._done(s, advance)
        frames = [(0, {("obj", "rot", 2): cur}), (dur, {("obj", "rot", 2): tgt}, None)]
        self.seq(s, frames)
        if hop:
            self.seq(s, [(0, {("root", "loc", 1): 0.0}), (dur // 2, {("root", "loc", 1): 0.35}, "in"),
                         (dur, {("root", "loc", 1): 0.0})])
        return self._done(s + dur, advance)

    def walk_to(self, x, y=None, speed=5.0, step=8, face_after=None, at=None, advance=True,
                run=False):
        """Waddle to (x, y). speed in units/sec. face_after='camera' to turn back."""
        if run:
            speed, step = max(speed, 10.0), 5
        s = self._start(at)
        p0 = self.pos(s)
        p1 = Vector((x, p0.y if y is None else y, 0.0))
        d = p1 - p0
        if d.length < 1e-3:
            return self._done(s, advance)
        ang = math.atan2(d.x, -d.y)
        s = self.turn(ang, dur=6, hop=False, at=s, advance=False) - 2
        n = max(2, round(d.length / speed * FPS / step))
        dur = n * step
        self.seq(s, [(0, {("obj", "loc", 0): p0.x, ("obj", "loc", 1): p0.y}, "lin"),
                     (dur, {("obj", "loc", 0): p1.x, ("obj", "loc", 1): p1.y})])
        sway = 0.10 if not run else 0.06
        bob = 0.18 if not run else 0.3
        leg = 0.5 if not run else 0.8
        lean = 0.0 if not run else 0.18
        chans = [("body", "rot", 2), ("root", "loc", 1), ("leg_L", "rot", 0), ("leg_R", "rot", 0),
                 ("body", "scl", 1), ("wing_L", "rot", 2), ("wing_R", "rot", 2), ("body", "rot", 0)]
        self.hold(s, chans)
        for i in range(n):
            f = s + i * step
            sg = 1 if i % 2 == 0 else -1
            self.pose(f + step // 2, {
                ("body", "rot", 2): sg * sway, ("root", "loc", 1): bob,
                ("leg_L", "rot", 0): -sg * leg, ("leg_R", "rot", 0): sg * leg,
                ("body", "scl", 1): 1.03, ("wing_L", "rot", 2): 0.12 + (0.25 if run else 0),
                ("wing_R", "rot", 2): -0.12 - (0.25 if run else 0), ("body", "rot", 0): lean})
            self.pose(f + step, {("root", "loc", 1): 0.0, ("body", "scl", 1): 0.95,
                                 ("leg_L", "rot", 0): 0.0, ("leg_R", "rot", 0): 0.0})
        end = s + dur
        self.pose(end + 4, self.rest_values(chans))
        self._done(end + 4, advance)
        if face_after:
            self.turn(face_after, at=end + 2, advance=advance)
        return end + 4

    def run_to(self, x, y=None, **kw):
        return self.walk_to(x, y, run=True, **kw)

    def hop(self, n=1, height=1.2, dx=0.0, dy=0.0, at=None, advance=True):
        """Small bunny hops in place (or travelling dx, dy per hop)."""
        s = self._start(at)
        for _ in range(n):
            p = self.pos(s)
            self.seq(s, [
                (0, {("root", "loc", 1): 0.0, ("body", "scl", 0): 1, ("body", "scl", 1): 1, ("body", "scl", 2): 1}),
                (3, {("root", "loc", 1): 0.0, ("body", "scl", 0): 1.14, ("body", "scl", 1): 0.78, ("body", "scl", 2): 1.14}, "out"),
                (6, {("body", "scl", 0): 0.9, ("body", "scl", 1): 1.15, ("body", "scl", 2): 0.9}),
                (9, {("root", "loc", 1): height, ("body", "scl", 0): 1, ("body", "scl", 1): 1, ("body", "scl", 2): 1}, "in"),
                (14, {("root", "loc", 1): 0.0, ("body", "scl", 0): 1.12, ("body", "scl", 1): 0.82, ("body", "scl", 2): 1.12}, "back"),
                (19, {("body", "scl", 0): 1, ("body", "scl", 1): 1, ("body", "scl", 2): 1}),
            ])
            self.seq(s, [(3, {("wing_L", "rot", 2): 0}), (7, {("wing_L", "rot", 2): 0.7, ("wing_R", "rot", 2): -0.7}),
                         (14, {("wing_L", "rot", 2): 0, ("wing_R", "rot", 2): 0})])
            self.seq(s, [(3, {("leg_L", "rot", 0): 0}), (8, {("leg_L", "rot", 0): 0.35, ("leg_R", "rot", 0): 0.35}),
                         (13, {("leg_L", "rot", 0): 0, ("leg_R", "rot", 0): 0})])
            if dx or dy:
                self.seq(s, [(3, {("obj", "loc", 0): p.x, ("obj", "loc", 1): p.y}, "lin"),
                             (14, {("obj", "loc", 0): p.x + dx, ("obj", "loc", 1): p.y + dy})])
            s += 17
        return self._done(s + 2, advance)

    def jump(self, dx=0.0, dy=0.0, height=3.5, flips=0, at=None, advance=True):
        """Big jump with anticipation. flips=1 front flip, -1 back flip."""
        s = self._start(at)
        p = self.pos(s)
        air = int(10 + 2.5 * height)
        up, land = 8, 8 + air
        S = lambda a, b, c: {("body", "scl", 0): a, ("body", "scl", 1): b, ("body", "scl", 2): c}
        self.seq(s, [
            (0, {("root", "loc", 1): 0.0, **S(1, 1, 1)}),
            (6, {("root", "loc", 1): 0.0, **S(1.22, 0.68, 1.22)}, "out"),
            (up, S(0.86, 1.22, 0.86)),
            (up + air // 2, {("root", "loc", 1): height, **S(1, 1, 1)}, "in"),
            (land, {("root", "loc", 1): 0.0, **S(1.25, 0.7, 1.25)}, "back"),
            (land + 8, S(1, 1, 1)),
        ])
        self.seq(s, [(0, {("wing_L", "rot", 2): 0.0, ("wing_R", "rot", 2): 0.0}),
                     (6, {("wing_L", "rot", 2): -0.25, ("wing_R", "rot", 2): 0.25}),
                     (up + 2, {("wing_L", "rot", 2): 2.4, ("wing_R", "rot", 2): -2.4}),
                     (up + air // 2, {("wing_L", "rot", 2): 1.2, ("wing_R", "rot", 2): -1.2}),
                     (land - 3, {("wing_L", "rot", 2): 2.0, ("wing_R", "rot", 2): -2.0}),
                     (land + 6, {("wing_L", "rot", 2): 0.0, ("wing_R", "rot", 2): 0.0})])
        self.seq(s, [(up, {("leg_L", "rot", 0): 0.0, ("leg_R", "rot", 0): 0.0}),
                     (up + 4, {("leg_L", "rot", 0): 0.6, ("leg_R", "rot", 0): 0.6}),
                     (land - 2, {("leg_L", "rot", 0): 0.0, ("leg_R", "rot", 0): 0.0})])
        if dx or dy:
            self.seq(s, [(up, {("obj", "loc", 0): p.x, ("obj", "loc", 1): p.y}, "lin"),
                         (land, {("obj", "loc", 0): p.x + dx, ("obj", "loc", 1): p.y + dy})])
        if flips:
            r0 = self.get(("spin", "rot", 0), s)
            self.seq(s, [(up + 1, {("spin", "rot", 0): r0}, "inout"),
                         (land - 2, {("spin", "rot", 0): r0 + flips * 2 * math.pi})])
        return self._done(s + land + 10, advance)

    def jump_to(self, x, y=None, height=3.5, **kw):
        p = self.pos(self._start(kw.get("at")))
        return self.jump(x - p.x, (0 if y is None else y - p.y), height, **kw)

    def fall(self, from_height=14.0, dur=14, at=None, advance=True):
        """Drop in from the sky and land with a big squash."""
        s = self._start(at)
        S = lambda a, b: {("body", "scl", 0): a, ("body", "scl", 1): b, ("body", "scl", 2): a}
        self.pose(s, {("root", "loc", 1): from_height, **S(0.85, 1.3)}, ease="in", cut=True)
        self.pose(s + dur, {("root", "loc", 1): 0.0})
        self.pose(s + dur, S(1.45, 0.5), ease="back")
        self.pose(s + dur + 16, S(1, 1))
        self.seq(s, [(0, {("wing_L", "rot", 2): 2.6, ("wing_R", "rot", 2): -2.6}, "lin"),
                     (4, {("wing_L", "rot", 2): 2.0, ("wing_R", "rot", 2): -2.0}, "lin"),
                     (8, {("wing_L", "rot", 2): 2.8, ("wing_R", "rot", 2): -2.8}, "lin"),
                     (dur, {("wing_L", "rot", 2): 1.0, ("wing_R", "rot", 2): -1.0}, "back"),
                     (dur + 10, {("wing_L", "rot", 2): 0.0, ("wing_R", "rot", 2): 0.0})], hold=False)
        self.seq(s, [(0, {("leg_L", "rot", 2): 0.4, ("leg_R", "rot", 2): -0.4}),
                     (dur - 1, {("leg_L", "rot", 2): 0.0, ("leg_R", "rot", 2): 0.0})], hold=False)
        self.express("surprised", dur=1, at=s, advance=False)
        self.express("neutral", dur=8, at=s + dur + 14, advance=False)
        self.last_impact = s + dur
        return self._done(s + dur + 18, advance)

    drop_in = fall

    def skid(self, dist=2.5, dur=14, at=None, advance=True):
        """Screeching stop: slide forward while leaning back, flailing."""
        s = self._start(at)
        p, fw = self.pos(s), self.forward(s)
        e = p + fw * dist
        self.seq(s, [(0, {("obj", "loc", 0): p.x, ("obj", "loc", 1): p.y}, "out"),
                     (dur, {("obj", "loc", 0): e.x, ("obj", "loc", 1): e.y})])
        self.seq(s, [(0, {("body", "rot", 0): 0.0}), (3, {("body", "rot", 0): -0.45}),
                     (dur, {("body", "rot", 0): -0.3}, "back"), (dur + 8, {("body", "rot", 0): 0.08}),
                     (dur + 14, {("body", "rot", 0): 0.0})])
        self.seq(s, [(0, {("leg_L", "rot", 0): 0.0, ("leg_R", "rot", 0): 0.0}),
                     (3, {("leg_L", "rot", 0): -0.6, ("leg_R", "rot", 0): -0.6}),
                     (dur, {("leg_L", "rot", 0): -0.6, ("leg_R", "rot", 0): -0.6}),
                     (dur + 6, {("leg_L", "rot", 0): 0.0, ("leg_R", "rot", 0): 0.0})])
        self.seq(s, [(0, {("wing_L", "rot", 2): 0.0, ("wing_R", "rot", 2): 0.0}),
                     (4, {("wing_L", "rot", 2): 1.6, ("wing_R", "rot", 2): -1.6}),
                     (7, {("wing_L", "rot", 2): 1.0, ("wing_R", "rot", 2): -1.0}),
                     (10, {("wing_L", "rot", 2): 1.7, ("wing_R", "rot", 2): -1.7}),
                     (dur + 10, {("wing_L", "rot", 2): 0.0, ("wing_R", "rot", 2): 0.0})])
        self.express("surprised", dur=3, at=s, advance=False)
        self.express("neutral", dur=8, at=s + dur + 6, advance=False)
        return self._done(s + dur + 14, advance)

    def cartwheel(self, dist=7.0, dur=22, at=None, advance=True):
        """Cartwheel sideways (dist>0 -> screen right). Faces camera first."""
        s = self._start(at)
        if abs(self.heading(s)) > 0.05:
            s = self.turn("camera", at=s, advance=False)
        p = self.pos(s)
        sp = -1 if dist > 0 else 1
        r0 = self.get(("spin", "rot", 2), s)
        a = 6  # anticipation
        self.seq(s, [(0, {("body", "scl", 0): 1, ("body", "scl", 1): 1, ("body", "scl", 2): 1}),
                     (a, {("body", "scl", 0): 1.12, ("body", "scl", 1): 0.82, ("body", "scl", 2): 1.12}),
                     (a + 3, {("body", "scl", 0): 1, ("body", "scl", 1): 1, ("body", "scl", 2): 1}),
                     (a + dur, {("body", "scl", 0): 1.12, ("body", "scl", 1): 0.85, ("body", "scl", 2): 1.12}, "back"),
                     (a + dur + 8, {("body", "scl", 0): 1, ("body", "scl", 1): 1, ("body", "scl", 2): 1})])
        self.seq(s, [(0, {("wing_L", "rot", 2): 0.0, ("wing_R", "rot", 2): 0.0}),
                     (a, {("wing_L", "rot", 2): 2.8, ("wing_R", "rot", 2): -2.8}),
                     (a + 4, {("wing_L", "rot", 2): 1.6, ("wing_R", "rot", 2): -1.6}),
                     (a + dur - 2, {("wing_L", "rot", 2): 1.6, ("wing_R", "rot", 2): -1.6}),
                     (a + dur + 8, {("wing_L", "rot", 2): 0.0, ("wing_R", "rot", 2): 0.0})])
        self.seq(s, [(a, {("leg_L", "rot", 2): 0.0, ("leg_R", "rot", 2): 0.0}),
                     (a + 4, {("leg_L", "rot", 2): 0.55, ("leg_R", "rot", 2): -0.55}),
                     (a + dur - 3, {("leg_L", "rot", 2): 0.55, ("leg_R", "rot", 2): -0.55}),
                     (a + dur, {("leg_L", "rot", 2): 0.0, ("leg_R", "rot", 2): 0.0})])
        self.seq(s, [(a, {("spin", "rot", 2): r0}, "inout"),
                     (a + dur, {("spin", "rot", 2): r0 + sp * 2 * math.pi})])
        q = dur / 4
        self.seq(s, [(a, {("root", "loc", 1): 0.0}),
                     (a + q, {("root", "loc", 1): 0.45}), (a + 2 * q, {("root", "loc", 1): 0.55}),
                     (a + 3 * q, {("root", "loc", 1): 0.45}), (a + dur, {("root", "loc", 1): 0.0})])
        self.seq(s, [(a, {("obj", "loc", 0): p.x}, "inout"), (a + dur, {("obj", "loc", 0): p.x + dist})])
        return self._done(s + a + dur + 10, advance)

    def flip(self, back=False, height=4.0, **kw):
        return self.jump(height=height, flips=-1 if back else 1, **kw)

    def spin(self, turns=1, dur=18, at=None, advance=True):
        """Pirouette around the vertical axis."""
        s = self._start(at)
        r0 = self.get(("body", "rot", 1), s)
        self.seq(s, [(0, {("body", "rot", 1): r0}, "inout"), (dur, {("body", "rot", 1): r0 + turns * 2 * math.pi})])
        self.seq(s, [(0, {("root", "loc", 1): 0.0}), (dur // 2, {("root", "loc", 1): 0.6}), (dur, {("root", "loc", 1): 0.0})])
        return self._done(s + dur, advance)

    def pop_in(self, dur=10, at=None, advance=True):
        s = self._start(at)
        self.pose(s, {("root", "scl", 0): 0.01, ("root", "scl", 1): 0.01, ("root", "scl", 2): 0.01}, ease="back", cut=True)
        self.pose(s + dur, {("root", "scl", 0): 1, ("root", "scl", 1): 1, ("root", "scl", 2): 1})
        return self._done(s + dur, advance)

    def pop_out(self, dur=8, at=None, advance=True):
        s = self._start(at)
        self.seq(s, [(0, {("root", "scl", 0): 1, ("root", "scl", 1): 1, ("root", "scl", 2): 1}),
                     (3, {("root", "scl", 0): 1.15, ("root", "scl", 1): 1.15, ("root", "scl", 2): 1.15}, "in"),
                     (dur, {("root", "scl", 0): 0.01, ("root", "scl", 1): 0.01, ("root", "scl", 2): 0.01})])
        return self._done(s + dur, advance)

    # ---- transitions ----------------------------------------------------
    def enter(self, side="left", to_x=0.0, offscreen=20.0, run=False, at=None, advance=True):
        s = self._start(at)
        cx = bpy.data.objects["Cam"].location.x if "Cam" in bpy.data.objects else 0.0
        sx = -1 if side == "left" else 1
        self.place(cx + sx * offscreen, self.pos(s).y, "right" if side == "left" else "left", at=s)
        return self.walk_to(to_x, at=s, run=run, face_after="camera", advance=advance)

    def enter_left(self, to_x=0.0, **kw):
        return self.enter("left", to_x, **kw)

    def enter_right(self, to_x=0.0, **kw):
        return self.enter("right", to_x, **kw)

    def exit(self, side="right", offscreen=22.0, run=False, at=None, advance=True):
        s = self._start(at)
        cx = bpy.data.objects["Cam"].location.x if "Cam" in bpy.data.objects else self.pos(s).x
        return self.walk_to(cx + (offscreen if side == "right" else -offscreen), at=s, run=run, advance=advance)

    def exit_left(self, **kw):
        return self.exit("left", **kw)

    def exit_right(self, **kw):
        return self.exit("right", **kw)

    # ---- attention ------------------------------------------------------
    LOOK = {"left": (-1, 0), "right": (1, 0), "up": (0, 1), "down": (0, -1),
            "camera": (0, 0), "center": (0, 0)}

    def look(self, direction="camera", dur=8, at=None, advance=True):
        """'left' 'right' 'up' 'down' 'camera', or combos like 'up-left'."""
        s = self._start(at)
        hx = hy = 0
        for part in direction.split("-"):
            dx, dy = self.LOOK[part]
            hx, hy = hx + dx, hy + dy
        eyes = {("pupil_L", "loc", 0): 0.10 * hx, ("pupil_R", "loc", 0): 0.10 * hx,
                ("pupil_L", "loc", 1): 0.08 * hy, ("pupil_R", "loc", 1): 0.08 * hy}
        face = {("face", "loc", 0): 0.06 * hx, ("face", "loc", 1): 0.05 * hy,
                ("body", "rot", 1): 0.32 * hx, ("body", "rot", 0): -0.12 * hy if hy > 0 else -0.16 * hy}
        self.seq(s, [(0, {k: self.get(k, s) for k in eyes}), (3, eyes, "back")])
        self.seq(s, [(1, face)])
        return self._done(s + dur, advance)

    def look_left(self, **kw): return self.look("left", **kw)
    def look_right(self, **kw): return self.look("right", **kw)
    def look_up(self, **kw): return self.look("up", **kw)
    def look_down(self, **kw): return self.look("down", **kw)

    def look_at(self, target, dur=8, at=None, advance=True):
        """Glance towards a world point or object (turns body, eyes lead)."""
        s = self._start(at)
        if hasattr(target, "matrix_world"):
            target = target.matrix_world.translation
        p, h = self.pos(s), self.heading(s)
        d = Vector(target) - (p + Vector((0, 0, self.zc + 0.4)))
        # into owl space (owl front = -Y)
        lx = d.x * math.cos(-h) - d.y * math.sin(-h)
        ly = d.x * math.sin(-h) + d.y * math.cos(-h)
        yaw = max(-0.7, min(0.7, math.atan2(lx, -ly)))
        pitch = max(-0.4, min(0.4, math.atan2(d.z, math.hypot(lx, ly))))
        nx, ny = yaw / 0.7, pitch / 0.4
        eyes = {("pupil_L", "loc", 0): 0.10 * nx, ("pupil_R", "loc", 0): 0.10 * nx,
                ("pupil_L", "loc", 1): 0.08 * ny, ("pupil_R", "loc", 1): 0.08 * ny}
        self.seq(s, [(0, {k: self.get(k, s) for k in eyes}), (3, eyes, "back")])
        self.seq(s, [(1, {("body", "rot", 1): yaw * 0.6, ("body", "rot", 0): -pitch * 0.4,
                          ("face", "loc", 0): 0.06 * nx, ("face", "loc", 1): 0.05 * ny})])
        return self._done(s + dur, advance)

    # ---- expressions ----------------------------------------------------
    EXPR_CHANNELS = [("brow_L", "loc", 1), ("brow_R", "loc", 1), ("brow_L", "rot", 2), ("brow_R", "rot", 2),
                     ("eye_L", "scl", 0), ("eye_L", "scl", 1), ("eye_R", "scl", 0), ("eye_R", "scl", 1),
                     ("pupil_L", "scl", 0), ("pupil_L", "scl", 1), ("pupil_R", "scl", 0), ("pupil_R", "scl", 1),
                     ("jaw", "rot", 0), ("beak", "rot", 0), ("tuft_L", "rot", 2), ("tuft_R", "rot", 2)]
    EXPRESSIONS = {
        "neutral": {},
        "surprised": {"brow": (0.14, 0.0, 0.0), "eye": (1.22, 1.25, 1.22, 1.25), "pupil": (0.7, 0.7),
                      "jaw": 0.7, "beak": -0.12, "tuft": (0.25, 0.25)},
        "happy": {"brow": (0.07, -0.12, 0.12), "eye": (1.05, 0.45, 1.05, 0.45), "pupil": (1, 1), "jaw": 0.35,
                  "tuft": (0.1, 0.1)},
        "excited": {"brow": (0.12, -0.1, 0.1), "eye": (1.15, 1.18, 1.15, 1.18), "pupil": (1.2, 1.2),
                    "jaw": 0.55, "beak": -0.08, "tuft": (0.2, 0.2)},
        "sad": {"brow": (0.02, -0.32, 0.32), "eye": (1.0, 0.8, 1.0, 0.8), "pupil": (1.15, 1.15),
                "tuft": (-0.55, -0.55)},
        "angry": {"brow": (-0.07, 0.38, -0.38), "eye": (1.0, 0.72, 1.0, 0.72), "pupil": (0.85, 0.85),
                  "jaw": 0.1, "tuft": (0.35, 0.35)},
        "confused": {"brow_L": (0.13, 0.12), "brow_R": (-0.05, 0.15), "eye": (1.12, 1.12, 0.95, 0.75),
                     "pupil": (0.9, 0.9), "tuft": (0.3, -0.3)},
        "thinking": {"brow_L": (0.1, -0.1), "brow_R": (-0.04, 0.05), "eye": (1.0, 1.0, 1.0, 0.65),
                     "tuft": (0.0, 0.0)},
        "sleepy": {"brow": (-0.03, 0.0, 0.0), "eye": (1.0, 0.25, 1.0, 0.25), "tuft": (-0.3, -0.3)},
    }

    def _expr_values(self, name):
        e = self.EXPRESSIONS[name]
        v = self.rest_values(self.EXPR_CHANNELS)
        if "brow" in e:
            y, rl, rr = e["brow"]
            v.update({("brow_L", "loc", 1): y, ("brow_R", "loc", 1): y, ("brow_L", "rot", 2): rl, ("brow_R", "rot", 2): rr})
        for side in ("L", "R"):
            if f"brow_{side}" in e:
                y, r = e[f"brow_{side}"]
                v.update({(f"brow_{side}", "loc", 1): y, (f"brow_{side}", "rot", 2): r if side == "L" else -r})
        if "eye" in e:
            a, b, c, d = e["eye"]
            v.update({("eye_L", "scl", 0): a, ("eye_L", "scl", 1): b, ("eye_R", "scl", 0): c, ("eye_R", "scl", 1): d})
        if "pupil" in e:
            for side in ("L", "R"):
                v.update({(f"pupil_{side}", "scl", 0): e["pupil"][0], (f"pupil_{side}", "scl", 1): e["pupil"][1]})
        v[("jaw", "rot", 0)] = e.get("jaw", 0.0)
        v[("beak", "rot", 0)] = e.get("beak", 0.0)
        if "tuft" in e:
            # positive = perk up/inwards, negative = droop outwards
            v.update({("tuft_L", "rot", 2): e["tuft"][0], ("tuft_R", "rot", 2): -e["tuft"][1]})
        return v

    def express(self, name="neutral", dur=6, at=None, advance=True, ease="back"):
        """Blend the face to a named expression (see EXPRESSIONS)."""
        s = self._start(at)
        self.hold(s, self.EXPR_CHANNELS)
        self.pose(s + dur, self._expr_values(name))
        # ease the outgoing segment of the start keys
        if ease:
            interp, easing = _ease(ease)
            for ch in self.EXPR_CHANNELS:
                o, p, i = self._res(ch)
                fc = _fcurve(self.rig, o.path_from_id(p), i)
                for kp in fc.keyframe_points:
                    if abs(kp.co.x - s) < 0.01:
                        kp.interpolation, kp.easing = interp, easing
        return self._done(s + dur, advance)

    def neutral(self, dur=8, **kw):
        return self.express("neutral", dur=dur, **kw)

    def _with_reset(self, s, end, hold, reset, chans_body):
        if hold:
            end += hold
        if reset:
            self.express("neutral", dur=8, at=end, advance=False)
            if chans_body:
                self.seq(end, [(0, {}), (10, self.rest_values(chans_body))])
            end += 10
        return end

    def surprised(self, hold=18, reset=True, at=None, advance=True):
        s = self._start(at)
        self.express("surprised", dur=4, at=s, advance=False)
        S = lambda a, b: {("body", "scl", 0): a, ("body", "scl", 1): b, ("body", "scl", 2): a}
        self.seq(s, [(0, {("root", "loc", 1): 0.0, **S(1, 1)}), (2, S(1.1, 0.85)),
                     (6, {("root", "loc", 1): 0.6, **S(0.9, 1.15)}, "in"),
                     (11, {("root", "loc", 1): 0.0, **S(1, 1)}, "back")])
        self.seq(s, [(0, {("wing_L", "rot", 2): 0.0, ("wing_R", "rot", 2): 0.0}),
                     (5, {("wing_L", "rot", 2): 0.9, ("wing_R", "rot", 2): -0.9}, "back")])
        end = self._with_reset(s, s + 11, hold, reset, [("wing_L", "rot", 2), ("wing_R", "rot", 2)])
        return self._done(end, advance)

    def happy(self, hold=24, reset=True, at=None, advance=True):
        s = self._start(at)
        self.express("happy", dur=6, at=s, advance=False)
        self.hop(1, height=0.5, at=s + 2, advance=False)
        end = self._with_reset(s, s + 20, hold, reset, [])
        return self._done(end, advance)

    def sad(self, hold=30, reset=True, at=None, advance=True):
        s = self._start(at)
        self.express("sad", dur=12, at=s, advance=False, ease=None)
        chans = {("body", "scl", 1): 0.9, ("body", "rot", 0): 0.12,
                 ("wing_L", "rot", 2): -0.15, ("wing_R", "rot", 2): 0.15}
        self.seq(s, [(0, {}), (14, chans)])
        self.look("down", at=s + 4, advance=False)
        end = self._with_reset(s, s + 14, hold, reset, list(chans))
        if reset:
            self.look("camera", at=end - 10, advance=False)
        return self._done(end, advance)

    def angry(self, hold=24, reset=True, at=None, advance=True):
        s = self._start(at)
        self.express("angry", dur=5, at=s, advance=False)
        chans = {("body", "rot", 0): 0.14, ("body", "scl", 0): 1.06, ("body", "scl", 2): 1.06,
                 ("wing_L", "rot", 2): 0.3, ("wing_R", "rot", 2): -0.3}
        self.seq(s, [(0, {}), (6, chans, "back")])
        # angry shiver
        for i in range(6):
            self.pose(s + 7 + i * 2, {("body", "rot", 2): 0.03 * (1 if i % 2 else -1)}, ease="lin")
        self.pose(s + 19, {("body", "rot", 2): 0.0})
        end = self._with_reset(s, s + 20, hold, reset, list(chans))
        return self._done(end, advance)

    def confused(self, hold=24, reset=True, at=None, advance=True):
        s = self._start(at)
        self.express("confused", dur=6, at=s, advance=False)
        chans = {("body", "rot", 2): 0.22, ("wing_L", "rot", 2): 0.55, ("wing_R", "rot", 2): -0.55}
        self.seq(s, [(0, {}), (8, chans, "back")])
        self.look("up-right", at=s + 3, advance=False)
        end = self._with_reset(s, s + 12, hold, reset, list(chans))
        if reset:
            self.look("camera", at=end - 10, advance=False)
        return self._done(end, advance)

    def thinking(self, hold=36, reset=True, at=None, advance=True):
        """Wing to chin, eyes up, tapping."""
        s = self._start(at)
        self.express("thinking", dur=8, at=s, advance=False)
        self.look("up-left", at=s + 2, advance=False)
        chin = {("wing_R", "rot", 0): -1.62, ("wing_R", "rot", 1): 0.72, ("wing_R", "scl", 1): 1.5,
                ("body", "rot", 2): -0.1}
        self.seq(s, [(0, {}), (10, chin, "back")])
        for i in range(max(1, hold // 12)):
            self.pose(s + 14 + i * 12, {("wing_R", "rot", 0): -1.48})
            self.pose(s + 20 + i * 12, {("wing_R", "rot", 0): -1.62})
        end = self._with_reset(s, s + 12, hold, reset, list(chin))
        if reset:
            self.look("camera", at=end - 10, advance=False)
        return self._done(end, advance)

    def excited(self, hops=3, at=None, advance=True, reset=True):
        s = self._start(at)
        self.express("excited", dur=4, at=s, advance=False)
        self.hop(hops, height=0.9, at=s, advance=False)
        self.flap(times=hops * 2 + 1, at=s + 2, advance=False)
        end = s + 17 * hops + 2
        if reset:
            self.express("neutral", dur=8, at=end, advance=False)
        return self._done(end + 8, advance)

    def celebrate(self, at=None, advance=True):
        s = self._start(at)
        self.express("excited", dur=4, at=s, advance=False)
        e = self.jump(height=3.0, at=s, advance=False)
        self.spin(1, dur=16, at=s + 9, advance=False)
        self.express("happy", dur=6, at=e - 6, advance=False)
        self.express("neutral", dur=8, at=e + 16, advance=False)
        return self._done(e + 16, advance)

    def sleepy(self, hold=40, reset=True, at=None, advance=True):
        s = self._start(at)
        self.express("sleepy", dur=16, at=s, advance=False, ease=None)
        self.seq(s, [(0, {}), (16, {("body", "rot", 0): 0.15, ("body", "rot", 2): 0.08})])
        end = self._with_reset(s, s + 16, hold, reset, [("body", "rot", 0), ("body", "rot", 2)])
        return self._done(end, advance)

    # ---- communication --------------------------------------------------
    def _wing(self, direction):
        # screen-right gestures use the owl's LEFT wing (it faces the camera)
        return ("wing_L", 1) if direction in ("right", "up-right") else ("wing_R", -1)

    def point(self, direction="right", hold=24, at=None, advance=True):
        """Point with a wing: 'right' | 'left' | 'up-right' | 'up-left'."""
        s = self._start(at)
        w, sg = self._wing(direction)
        ang = 1.55 if not direction.startswith("up") else 2.35
        chans = {(w, "rot", 2): sg * ang, (w, "scl", 1): 1.2, ("body", "rot", 2): -sg * 0.08}
        self.seq(s, [(0, {}), (2, {(w, "rot", 2): -sg * 0.15}), (8, chans, "back")])
        self.look(direction, at=s + 2, advance=False)
        end = s + 8 + hold
        self.seq(end, [(0, {}), (10, self.rest_values(chans))])
        self.look("camera", at=end, advance=False)
        return self._done(end + 10, advance)

    def wave(self, times=3, side="right", at=None, advance=True):
        """Wave hello with the wing on the given screen side."""
        s = self._start(at)
        w, sg = self._wing(side)
        self.seq(s, [(0, {(w, "rot", 2): self.get((w, "rot", 2), s), ("body", "rot", 2): 0.0}),
                     (7, {(w, "rot", 2): sg * 2.5, ("body", "rot", 2): -sg * 0.1}, "back")])
        f = s + 7
        for i in range(times):
            self.pose(f + 4, {(w, "rot", 2): sg * 2.95})
            self.pose(f + 8, {(w, "rot", 2): sg * 2.35})
            f += 8
        self.pose(f + 9, {(w, "rot", 2): 0.0, ("body", "rot", 2): 0.0})
        return self._done(f + 9, advance)

    def flap(self, times=4, speed=4, at=None, advance=True):
        s = self._start(at)
        self.hold(s, [("wing_L", "rot", 2), ("wing_R", "rot", 2)])
        for i in range(times):
            self.pose(s + i * speed * 2 + speed, {("wing_L", "rot", 2): 1.3, ("wing_R", "rot", 2): -1.3})
            self.pose(s + i * speed * 2 + speed * 2, {("wing_L", "rot", 2): 0.15, ("wing_R", "rot", 2): -0.15})
        e = s + times * speed * 2
        self.pose(e + 4, {("wing_L", "rot", 2): 0.0, ("wing_R", "rot", 2): 0.0})
        return self._done(e + 4, advance)

    def nod(self, times=2, at=None, advance=True):
        s = self._start(at)
        self.hold(s, [("body", "rot", 0)])
        for i in range(times):
            self.pose(s + i * 10 + 5, {("body", "rot", 0): 0.2})
            self.pose(s + i * 10 + 10, {("body", "rot", 0): -0.03})
        self.pose(s + times * 10 + 5, {("body", "rot", 0): 0.0})
        return self._done(s + times * 10 + 5, advance)

    def shake_head(self, times=3, at=None, advance=True):
        s = self._start(at)
        self.hold(s, [("body", "rot", 1)])
        for i in range(times):
            self.pose(s + i * 8 + 4, {("body", "rot", 1): 0.3})
            self.pose(s + i * 8 + 8, {("body", "rot", 1): -0.3})
        self.pose(s + times * 8 + 6, {("body", "rot", 1): 0.0})
        return self._done(s + times * 8 + 6, advance)

    def shrug(self, hold=12, at=None, advance=True):
        s = self._start(at)
        chans = {("wing_L", "rot", 2): 1.1, ("wing_R", "rot", 2): -1.1, ("body", "rot", 2): 0.1,
                 ("brow_L", "loc", 1): 0.1, ("brow_R", "loc", 1): 0.1, ("root", "loc", 1): 0.15}
        self.seq(s, [(0, {}), (6, chans, "back"), (6 + hold, chans), (16 + hold, self.rest_values(chans))])
        self.pose(s + 16 + hold, {("root", "loc", 1): 0.0})
        return self._done(s + 16 + hold, advance)

    def bow(self, hold=10, at=None, advance=True):
        s = self._start(at)
        self.seq(s, [(0, {("body", "rot", 0): 0.0}), (8, {("body", "rot", 0): 0.55}),
                     (8 + hold, {("body", "rot", 0): 0.55}), (18 + hold, {("body", "rot", 0): 0.0}, None)])
        return self._done(s + 18 + hold, advance)

    @staticmethod
    def syllables(text):
        out = []
        for tok in re.findall(r"[A-Za-z']+|[.,!?;:—-]", text):
            if not tok[0].isalpha():
                out.append(("pause", 8 if tok in ".!?" else 5, tok == "!"))
                continue
            n = max(1, len(re.findall(r"[aeiouy]+", tok.lower())) - (1 if tok.lower().endswith("e") and len(tok) > 3 else 0))
            out += [("syl", 5, False)] * n
            out.append(("gap", 1, False))
        return out

    def talk(self, text=None, frames=None, energy=1.0, at=None, advance=True):
        """Beak chatter. Give text (rough syllable timing) or a frame count."""
        s = self._start(at)
        if text is None:
            n = max(1, (frames or 48) // 5)
            plan = [("syl", 5, False)] * n
        else:
            plan = self.syllables(text)
        self.hold(s, [("jaw", "rot", 0), ("beak", "rot", 0), ("body", "scl", 1), ("brow_L", "loc", 1), ("brow_R", "loc", 1)])
        f = s
        for i, (kind, dur, emph) in enumerate(plan):
            if kind == "syl":
                amp = self.rnd.uniform(0.35, 0.8) * energy
                self.pose(f + 2, {("jaw", "rot", 0): amp, ("beak", "rot", 0): -0.1 * amp})
                self.pose(f + dur, {("jaw", "rot", 0): 0.05, ("beak", "rot", 0): 0.0})
                if self.rnd.random() < 0.3:
                    self.pose(f + 2, {("body", "scl", 1): 1.04})
                    self.pose(f + dur + 2, {("body", "scl", 1): 1.0})
            elif kind == "pause" and emph:
                self.pose(f, {("brow_L", "loc", 1): 0.1, ("brow_R", "loc", 1): 0.1})
                self.pose(f + dur + 6, {("brow_L", "loc", 1): 0.0, ("brow_R", "loc", 1): 0.0})
            f += dur
        self.pose(f + 2, {("jaw", "rot", 0): 0.0, ("beak", "rot", 0): 0.0})
        return self._done(f + 2, advance)

    # ---- idle / life ----------------------------------------------------
    def idle(self, frames=48, at=None, advance=True):
        """Breathing + tiny weight shifts."""
        s = self._start(at)
        self.hold(s, [("body", "scl", 1), ("body", "rot", 2)])
        f, sg = s, 1
        while f + 24 <= s + frames:
            self.pose(f + 12, {("body", "scl", 1): 1.025, ("body", "rot", 2): 0.02 * sg})
            self.pose(f + 24, {("body", "scl", 1): 1.0, ("body", "rot", 2): 0.0})
            f += 24
            sg = -sg
        return self._done(s + frames, advance)

    def blink(self, at=None):
        f = self._start(at)
        for side in ("L", "R"):
            self.seq(f, [(0, {(f"blink_{side}", "scl", 1): 1.0}), (2, {(f"blink_{side}", "scl", 1): 0.08}),
                         (3, {(f"blink_{side}", "scl", 1): 0.08}), (6, {(f"blink_{side}", "scl", 1): 1.0})])
        return f + 6

    def auto_blink(self, start=None, end=None, every=(55, 110)):
        f = (self.scene.frame_start if start is None else start) + self.rnd.randint(10, 40)
        end = self.t if end is None else end
        while f < end - 6:
            self.blink(at=f)
            f += self.rnd.randint(*every)

    def finish(self, tail=24, blinks=True):
        """Add natural blinks and fit the scene frame range to the performance."""
        if blinks:
            self.auto_blink()
        self.scene.frame_end = int(self.t + tail)
        return self.scene.frame_end


# ---------------------------------------------------------------- camera
class Cam:
    """Camera director: a camera tracking the empty 'CamTarget'."""
    FRAMING = {  # distance, camera height, look-at height (relative to owl)
        "extreme_wide": (40, 8, 4.0), "wide": (24, 5, 3.0), "full": (14, 3.2, 1.9),
        "medium": (9.5, 2.8, 1.9), "close": (6.0, 2.4, 2.1), "extreme_close": (3.6, 2.3, 2.3),
        "low": (8.0, 0.4, 2.2), "high": (11, 9, 1.5),
    }

    def __init__(self, owl, cam="Cam", target="CamTarget"):
        self.owl = owl
        self.cam = bpy.data.objects[cam]
        self.tgt = bpy.data.objects[target]
        self.kc, self.kt = _Keyer(self.cam), _Keyer(self.tgt)

    def _set(self, frame, cam_loc, tgt_loc, ease=None, cut=False):
        interp, easing = _ease(ease)
        for i in range(3):
            self.kc.key(self.cam, "location", i, frame, cam_loc[i], interp, easing, cut)
            self.kt.key(self.tgt, "location", i, frame, tgt_loc[i], interp, easing, cut)

    def _cur(self, frame):
        return (Vector([self.kc.val(self.cam, "location", i, frame) for i in range(3)]),
                Vector([self.kt.val(self.tgt, "location", i, frame) for i in range(3)]))

    def shot(self, framing="medium", at=None, dur=0, subject=None, side=0.0, ease="inout"):
        """Frame the owl (or a point). dur=0 is a hard cut, otherwise a move."""
        f = self.owl.t if at is None else at
        dist, ch, th = self.FRAMING[framing]
        p = Vector(subject) if subject is not None else self.owl.pos(f)
        cam = Vector((p.x + side, p.y - dist, ch))
        tgt = Vector((p.x, p.y, th))
        if dur:
            c0, t0 = self._cur(f)
            self._set(f, c0, t0, ease)
            self._set(f + dur, cam, tgt)
        else:
            self._set(f, cam, tgt, cut=True)
        return f + dur

    def follow(self, start, end, framing=None, step=6, lag=4):
        """Pan with the owl on X between start and end (keeps current framing)."""
        c0, t0 = self._cur(start)
        off_c = c0.x - self.owl.pos(start).x
        off_t = t0.x - self.owl.pos(start).x
        f = start
        while f <= end:
            ox = self.owl.pos(max(start, f - lag)).x
            for kk, ob, v in ((self.kc, self.cam, ox + off_c), (self.kt, self.tgt, ox + off_t)):
                kk.key(ob, "location", 0, f, v)
            f += step
        return end

    def push_in(self, amount=0.3, dur=48, at=None):
        """Dolly towards the target by a fraction of the distance."""
        f = self.owl.t if at is None else at
        c0, t0 = self._cur(f)
        self._set(f, c0, t0, "inout")
        self._set(f + dur, c0.lerp(t0, amount), t0)
        return f + dur

    def orbit(self, degrees=30, dur=48, at=None):
        f = self.owl.t if at is None else at
        c0, t0 = self._cur(f)
        steps = 6
        for i in range(steps + 1):
            a = math.radians(degrees) * i / steps
            d = c0 - t0
            c = Vector((t0.x + d.x * math.cos(a) - d.y * math.sin(a),
                        t0.y + d.x * math.sin(a) + d.y * math.cos(a), c0.z))
            for j in range(3):
                self.kc.key(self.cam, "location", j, f + dur * i / steps, c[j])
        return f + dur

    def shake(self, at, amp=0.25, dur=10, seed=3):
        r = random.Random(seed)
        for i in range(dur):
            c, t = self._cur(at + i)
            k = amp * (1 - i / dur)
            jitter = Vector((r.uniform(-k, k), 0, r.uniform(-k, k)))
            for j in range(3):
                self.kt.key(self.tgt, "location", j, at + i, t[j] + jitter[j], "LINEAR")
        return at + dur
