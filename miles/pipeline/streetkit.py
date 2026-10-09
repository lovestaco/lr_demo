"""Shared street-scene kit (the v8 street rules, reusable): read shots, web zips, landings, travel paths, cameras.

    from pipeline import streetkit
    k = streetkit.Kit(c, rig, perf, vo)            # c = city.load(), vo = lines.json dict
    cam_loc, tgt, lens = k.presenter(board_c, normal, w, h, spot, floor)
    z = k.zip_(dist, face); l = k.touch(face, spot)              # pull along the line, feet-first landing
    perf.build(); ...; k.web_zip(z, l, anchor)                     # after build: key the path + one-angle lean
    k.camera(); k.read_shot(f0, f1, shot)                          # static read: whole slide, him at its left edge

Rules it encodes (review of v7): web travel is a straight pull on the line, the body at ONE angle (no spins);
explaining = upright, facing the camera; him right next to each slide at its LEFT edge; no hangs.
"""
import math
import bpy
from mathutils import Vector, Euler, Matrix
from . import anim, fx, swing
from .mixamo import ClipGroup
from .shot import HIPS, R_HAND

FPS = 30
PAD = 0.35
Z = Vector((0, 0, 1))
first = lambda g: g.cycles[0] if hasattr(g, "cycles") else g
final = lambda g: g.cycles[-1] if hasattr(g, "cycles") else g
face_to = lambda a, b: math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1])))     # `face` for standing at a, facing b
HANG = "Hanging Idle"                         # both hands up, gripping: the pose on a web line
SHOOT = "Standing 1H Magic Attack 02"
EXPLAIN = "CMU 18_08 conversation - explain with hand gesture"
PRESENT = ["Talking (2)", "Talking (1)", EXPLAIN]


class Kit:
    def __init__(self, c, rig, perf, vo):
        self.c, self.rig, self.perf, self.vo = c, rig, perf, vo
        self.mine = {o.name for o in rig.children_recursive} | {rig.name}
        self.travels, self._turn, self.cam = [], [0], None
        self.hit_pk = perf.extreme(SHOOT, R_HAND, (1, 0, 0), 16, 40)

    # ------------------------------------------------------------ voice-over timing
    def dur(self, n):
        return self.vo[str(n)]["duration"]

    def hold(self, n, extra=0.45, at_least=0):
        return int(round(max(at_least, (self.dur(n) - PAD + extra) * FPS)))

    ALIAS = {"one": "1", "two": "2", "three": "3", "cuz": "cause", "model": "models", "livi": "livy"}   # how whisper spells them

    def word(self, n, w, nth=0):
        hits = [t for x, t in self.vo[str(n)]["words"] if x == w] or \
               [t for x, t in self.vo[str(n)]["words"] if x == self.ALIAS.get(w)]
        return hits[min(nth, len(hits) - 1)]

    # ------------------------------------------------------------ geometry checks
    def ray(self, a, d, dist):
        return self.c.ray(a, d, dist)

    def clear_view(self, cam_loc, pts, slack=0.35):
        for p in pts:
            d = Vector(p) - Vector(cam_loc)
            h = self.c.ray(cam_loc, d, d.length + 1.0)
            if h is None or (h.point - Vector(cam_loc)).length < d.length - slack:
                return False
        return True

    def open_to(self, a, b, slack=0.3):
        """Nothing between a and b (b may be in open air, e.g. where he will stand)."""
        d = Vector(b) - Vector(a)
        h = self.c.ray(a, d, d.length)
        return h is None or (h.point - Vector(a)).length >= d.length - slack

    @staticmethod
    def board_pts(centre, normal, w, h):
        n = Vector(normal).normalized()
        side = n.cross(Z).normalized()
        grid = [k / 20.0 - 0.975 for k in range(40)]
        return [Vector(centre) + side * (w / 2 * a) + Vector((0, 0, h / 2 * b)) + n * 0.05 for a in grid for b in (-0.8, -0.4, 0, 0.4, 0.8)]

    @staticmethod
    def fit(loc, pts, margin=1.12):
        """Aim + focal length (36 mm sensor) that just fit `pts` in a 16:9 frame from `loc`."""
        loc = Vector(loc)
        ds = [Vector(p) - loc for p in pts]
        yaws = [math.atan2(d.x, d.y) for d in ds]
        mean = math.atan2(sum(math.sin(a) for a in yaws), sum(math.cos(a) for a in yaws))
        rel = [(a - mean + math.pi) % (2 * math.pi) - math.pi for a in yaws]
        pit = [math.atan2(d.z, d.xy.length) for d in ds]
        yc, pc = mean + (min(rel) + max(rel)) / 2, (min(pit) + max(pit)) / 2
        hy, hv = (max(rel) - min(rel)) / 2 * margin, (max(pit) - min(pit)) / 2 * margin
        lens = min(18.0 / math.tan(max(hy, 1e-3)), 10.125 / math.tan(max(hv, 1e-3)))
        tgt = loc + Vector((math.sin(yc) * math.cos(pc), math.cos(yc) * math.cos(pc), math.sin(pc))) * 10.0
        return tgt, lens

    def presenter(self, bc, normal, w, h, spot, floor, lens_min=26.0, offset=0.05, eye=None, extra=()):
        """Static read shot: the whole slide straight-on, him standing at its left edge, both in frame (+ `extra`
        points that must be in frame too). Steps back along the normal until the lens is >= lens_min and clear."""
        n = Vector((normal[0], normal[1], 0)).normalized()
        right = (-n).cross(Z).normalized()
        bc = Vector(bc)
        sp = Vector((spot[0], spot[1], floor))
        pts = [bc + right * (w / 2 * a) + Z * (h / 2 * b) for a in (-1, 1) for b in (-1, 1)]
        pts += [sp + right * dx + Z * dz for dx in (-0.45, 0.45) for dz in (0.0, 1.9)] + [Vector(p) for p in extra]
        us = [(p - bc).dot(right) for p in pts]
        mid = bc + right * ((min(us) + max(us)) / 2)
        eye = (min(p.z for p in pts) + max(p.z for p in pts)) / 2 if eye is None else eye
        first_ok = None
        loc = tgt = lens = None
        for k in range(8, 90):
            D = k * 0.5
            for side in (0.0, 0.5, -0.5, 1.0, -1.0):
                loc = mid + n * D + right * side
                loc.z = eye
                tgt, lens = self.fit(loc, pts)
                if lens < lens_min:
                    break
                first_ok = first_ok or (loc, tgt, lens)
                if all(self.open_to(loc, p) for p in self.board_pts(bc + n * offset, n, w, h) + [sp + Z * dz for dz in (0.3, 1.0, 1.6)]):
                    print("PRESENTER", tuple(round(v, 1) for v in loc), f"{lens:.0f}mm D{D}")
                    return loc, tgt, lens
        print("PRESENTER blocked, using", first_ok)
        return first_ok or (loc, tgt, lens)

    @staticmethod
    def gesture_side(point, him, cam_loc):
        """His arm on the slide's side: slide to camera-right of him -> his left arm (he faces the camera)."""
        d = Vector(him) - Vector(cam_loc)
        right = Vector((d.y, -d.x))
        return "L" if (Vector(point).xy - Vector(him).xy).dot(right) > 0 else "R"

    def floor_at(self, x, y, top=1.0):
        h = self.c.ray(Vector((x, y, top)), Vector((0, 0, -1)), top + 3.0)
        return h.point.z if h is not None else 0.0

    # ------------------------------------------------------------ clips (queue before build)
    def talk(self, length, face=0, blend=10, at=None, cut_blend=0, clips=PRESENT):
        perf, parts, left = self.perf, [], int(length)
        while left > 8:
            clip = clips[self._turn[0] % len(clips)]
            self._turn[0] += 1
            a0, a1 = bpy.data.actions[clip].frame_range
            n = min(left + (blend if parts else 0), int(a1 - a0) - 2)
            frm = perf.lively(clip, n, target=1.5) if clip == EXPLAIN else a0 + 1
            parts.append(perf.then(clip, frm=frm, length=n, blend=blend, face=face, in_place=0.7,
                                   at=at if not parts else None, cut_blend=cut_blend))
            left -= n - (blend if len(parts) > 1 else 0)
        return parts[0] if len(parts) == 1 else ClipGroup(parts)

    def talk_until(self, f, face, blend=10, clips=PRESENT):
        """Explain (upright, to the camera) until scene frame f."""
        return self.talk(max(14, int(f) - int(self.perf.end) + blend), face=face, blend=blend, clips=clips)

    def shoot(self, face, blend=8, at=None):
        """Fires the line (right hand) towards where he's going."""
        return self.perf.then(SHOOT, frm=16, to=40, speed=1.1, blend=blend, face=face, in_place=1.0, at=at)

    def zip_(self, dist, face, blend=6, cap=72):
        """Pulled along the web line: hands up on it, body straight (lean() angles him along it). No flips."""
        return self.perf.then(HANG, frm=20, length=min(cap, int(16 + dist * 1.15)), face=face, in_place=1.0, blend=blend)

    def touch(self, face, at):
        """Lets go just above the spot: feet-first landing, a crouch, up to standing (no roll)."""
        return self.perf.then("Hard Landing", frm=14, to=64, speed=1.6, face=face, in_place=1.0, at=at, cut_blend=5)

    def stride(self, action, frm=None, to=None):
        """A clip's own ground speed (m / frame), measured on its hips with the root at identity."""
        act = bpy.data.actions[action]
        a0, a1 = act.frame_range
        frm, to = frm or a0, to or a1
        self.perf.root.animation_data_clear()
        self.perf.root.matrix_world = Matrix.Identity(4)
        d = (self.perf._hips(act, to).xy - self.perf._hips(act, frm).xy).length
        self.rig.animation_data.action = None
        return d / max(1, to - frm)

    # ------------------------------------------------------------ after build: paths
    def hp(self, f):
        return self.perf.bone_world(HIPS, f)

    def travel(self, path, f0, f1, axes=(0, 1, 2), name=""):
        """Key the root (every frame f0..f1) so the hips sit on path(t), then restore the root after f1."""
        perf, rig, sc = self.perf, self.rig, bpy.context.scene
        f0, f1 = int(f0), int(f1)
        keep = []
        for i in axes:
            fc = anim.fcurve(perf.root, "location", i)
            prior = [k for k in fc.keyframe_points if k.co.x <= f1 + 1] if fc else []
            gov = max(prior, key=lambda k: k.co.x) if prior else None
            keep.append((i, fc.evaluate(f1 + 1) if fc else perf.root.location[i],
                         "const" if gov is not None and gov.interpolation == "CONSTANT" else "lin"))
        for f in range(f0, f1 + 1):
            sc.frame_set(f)
            delta = (rig.matrix_world @ rig.pose.bones[HIPS].head) - perf.root.matrix_world.translation
            want = path((f - f0) / max(1, f1 - f0))
            for i in axes:
                anim.key(perf.root, "location", f, want[i] - delta[i], i, "lin")
        for i, v, ease in keep:
            anim.key(perf.root, "location", f1 + 1, v, i, ease)
        self.travels.append((f0, f1, name))

    def path_hits(self, f0, f1, name, ignore=("Web",)):
        bad = []
        for f in range(int(f0), int(f1)):
            a, b = self.hp(f), self.hp(f + 1)
            d = b - a
            if d.length > 1e-3:
                h = self.c.ray(a, d, d.length + 0.3)
                if h is not None and h.obj.name not in self.mine and not h.obj.name.startswith(ignore):
                    bad.append((f, h.obj.name))
        print(f"PATH {name} f{int(f0)}-{int(f1)} hits", bad[:12])
        return bad

    @staticmethod
    def zip_path(p0, p1, lift=0.0):
        """Near-straight pull along the line: accelerates off the start, eases into the release."""
        p0, p1 = Vector(p0), Vector(p1)
        ctrl = (p0 + p1) / 2 + Z * lift

        def fn(t):
            u = 0.6 * (t * t * (3 - 2 * t)) + 0.4 * t
            return (1 - u) ** 2 * p0 + 2 * (1 - u) * u * ctrl + u * u * p1
        return fn

    @staticmethod
    def bez(p0, p1, p2, p3):
        p0, p1, p2, p3 = (Vector(v) for v in (p0, p1, p2, p3))

        def fn(t):
            u = swing.ease_pendulum(t) * 0.6 + t * 0.4
            return (1 - u) ** 3 * p0 + 3 * (1 - u) ** 2 * u * p1 + 3 * (1 - u) * u * u * p2 + u ** 3 * p3
        return fn

    def find_anchor(self, p0, p1, fallback, min_up=3.0, reach=45.0):
        """A real place for the web to stick: a facade / roof edge above the end of the zip, ahead of him."""
        p0, p1 = Vector(p0), Vector(p1)
        mid = p0.lerp(p1, 0.75)
        run = (p1 - p0).xy
        best = None
        for el in (35, 45, 55, 65, 75, 85):
            for az in range(0, 360, 10):
                ce = math.cos(math.radians(el))
                d = Vector((math.cos(math.radians(az)) * ce, math.sin(math.radians(az)) * ce, math.sin(math.radians(el))))
                h_ = self.c.ray(mid, d, reach)
                if h_ is None or h_.obj.name in self.mine or h_.point.z < max(p0.z, p1.z) + min_up:
                    continue
                along = (h_.point.xy - p0.xy).dot(run) / max(1e-6, run.length_squared)
                if not 0.7 <= along <= 1.4:
                    continue
                off = abs((h_.point.xy - p0.xy).cross(run)) / max(1e-6, run.length)
                if off > 8.0:
                    continue
                score = (h_.point.xy - p1.xy).length + 0.4 * off
                if best is None or score < best[0]:
                    best = (score, h_.point.copy())
        print("ANCHOR", tuple(round(v, 1) for v in (best[1] if best else Vector(fallback))), "found" if best else "fallback")
        return best[1] if best else Vector(fallback)

    def lean(self, f0, f1, direction, max_deg=48.0, ramp=6):
        """Body at ONE angle along the line for the whole pull: sample the root rotation first (keying frame f
        changes how f + 1 evaluates: re-reading it compounds the tilt into a spin)."""
        root = self.perf.root
        fcs = [anim.fcurve(root, "rotation_euler", i) for i in range(3)]
        ev = lambda f: Euler([fc.evaluate(f) if fc else 0.0 for fc in fcs], "XYZ")
        f0, f1 = int(f0), int(f1)
        keep = ev(f1 + 1)
        bases = {f: ev(f) for f in range(f0, f1 + 1)}
        u = Vector(direction).normalized()
        axis = Z.cross(u)
        full = min(math.acos(max(-1.0, min(1.0, u.z))), math.radians(max_deg))
        prev = None
        for f in range(f0, f1 + 1):
            w = max(0.0, min(1.0, (f - f0) / ramp, (f1 - f) / ramp))
            w = w * w * (3 - 2 * w)
            base = bases[f]
            e = base if (axis.length < 1e-6 or full * w < 1e-4) else \
                (Matrix.Rotation(full * w, 3, axis.normalized()) @ base.to_matrix()).to_euler("XYZ", prev or base)
            for i in range(3):
                anim.key(root, "rotation_euler", f, e[i], i, "lin")
            prev = e
        for i in range(3):
            anim.key(root, "rotation_euler", f1 + 1, keep[i], i, "lin")

    def web_zip(self, zclip, lclip, anchor, p0=None, lift=0.6, name="", path=None, start=None):
        """Zip from where he is (or `p0`) to where the landing starts, body angled at the anchor the whole way."""
        f0, f1 = int(start if start is not None else zclip.start), int(lclip.start) - 1
        a = Vector(p0) if p0 is not None else self.hp(f0 - 1)
        b = self.hp(f1 + 1)
        path = path or self.zip_path(a, b, lift=lift)
        self.lean(int(zclip.start) + 1, f1 - 2, Vector(anchor) - path(0.5))
        self.travel(path, f0, f1, name=name)
        return path

    # ------------------------------------------------------------ cameras
    def camera(self, lens=28, fstop=4.0):
        self.cam = fx.CameraRig(lens=lens, fstop=fstop)
        self.cam.cam.data.clip_end = 800.0
        return self.cam

    def at(self, f, loc, tgt, ease="inout", cut=False):
        self.cam.at(int(f), loc, tgt, ease, cut=cut)

    def arm(self, base, offset, pad=0.8):
        off = Vector(offset)
        h = self.c.ray(base, off, off.length + pad)
        if h is not None and h.obj.name not in self.mine:
            return base + off.normalized() * max(1.2, (h.point - base).length - pad)
        return base + off

    def ride(self, f0, f1, offset, lead=6, step=2, smooth=5, look=Vector()):
        """Tracking shot: camera at the (smoothed) hips + offset (collision arm), aimed a little ahead."""
        pts = {f: self.hp(f) for f in range(int(f0) - smooth - 5, int(f1) + lead + smooth + 6)}
        sm = lambda f: sum((pts[k] for k in range(f - smooth, f + smooth + 1)), Vector()) / (2 * smooth + 1)
        raw = {f: self.arm(sm(f), offset) for f in range(int(f0) - 4, int(f1) + 5)}
        cams = {f: sum((raw[k] for k in range(f - 4, f + 5)), Vector()) / 9 for f in range(int(f0), int(f1) + 1)}
        for f in range(int(f0), int(f1) + 1, step):
            self.cam.at(f, cams[f], sm(f + lead) + look, "lin", cut=(f == int(f0)))

    def pan(self, f0, f1, loc, lead=4, smooth=4, step=2, look=Vector()):
        """Fixed camera panning with him."""
        pts = {f: self.hp(f) for f in range(int(f0) - smooth, int(f1) + lead + smooth + 1)}
        sm = lambda f: sum((pts[k] for k in range(f - smooth, f + smooth + 1)), Vector()) / (2 * smooth + 1)
        for f in range(int(f0), int(f1) + 1, step):
            self.cam.at(f, Vector(loc), sm(f + lead) + look, "lin", cut=(f == int(f0)))

    def head(self, f, up=0.05):
        return self.perf.bone_world("mixamorig:Head", f) + Vector((0, 0, up))

    def read_shot(self, f0, f1, shot_, drift=0.15):
        """Static presenter shot for a read (a slow, tiny push in; the slide never leaves the frame)."""
        loc, tgt, lens = shot_
        self.cam.lens(int(f0), round(lens), "const")
        self.at(f0, loc, tgt, "lin", cut=True)
        self.at(f1, Vector(loc).lerp(Vector(tgt), drift / max(1.0, (Vector(tgt) - Vector(loc)).length)), tgt, "lin")

    def visible_report(self, end, skip=("Web", "Bills", "Spider", "Cash", "Dust", "Chunk", "Confetti")):
        bad = []
        sc = bpy.context.scene
        for f in range(1, end, 6):
            sc.frame_set(f)
            cl = self.cam.cam.matrix_world.translation
            h = self.hp(f)
            d = h - cl
            ok, loc, nor, i, ob, m = sc.ray_cast(bpy.context.evaluated_depsgraph_get(), cl, d.normalized(), distance=d.length - 0.6)
            if ok and ob.name not in self.mine and not ob.name.startswith(skip):
                bad.append((f, ob.name))
        print("OCCLUDED", bad)
        return bad
