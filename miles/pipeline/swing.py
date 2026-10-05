"""Web-swing paths: the body follows a computed arc instead of the clip's few metres of travel.

A swing = shoot a line to an anchor high on a building → drop into a pendulum arc (fast at the bottom,
hanging from the line) → rise, let go at the top → fly → land. The clip ("Swing To Land (1)", played
in_place) supplies the pose; `follow()` moves the root so the hips trace `path(frame)`.

    p = swing.arc(start_hips, end_hips, sag=6.0)               # pendulum-ish arc between two points
    swing.follow(perf, clip, p, f0, f1)                         # after build()/square_up()/root_z()
"""
import math
import bpy
from mathutils import Vector, Matrix
from . import anim

HIPS = "mixamorig:Hips"


def ease_pendulum(t):
    """Slow at the ends, fastest through the bottom (like a pendulum)."""
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def arc(p0, p1, sag, apex=None):
    """Hips path from p0 to p1 dipping `sag` metres below the straight line at the middle (the bottom
    of the swing); `apex` (0..1) shifts where the low point is."""
    p0, p1 = Vector(p0), Vector(p1)
    k = apex or 0.5

    def fn(t):
        u = ease_pendulum(t)
        base = p0.lerp(p1, u)
        w = math.sin(math.pi * (u if k == 0.5 else (u / (2 * k) if u < k else 0.5 + (u - k) / (2 * (1 - k)))))
        return base - Vector((0, 0, sag * w))
    return fn


def hop(p0, p1, height):
    """Ballistic flight: straight in plan, parabola in height."""
    p0, p1 = Vector(p0), Vector(p1)

    def fn(t):
        t = max(0.0, min(1.0, t))
        return p0.lerp(p1, t) + Vector((0, 0, 4 * height * t * (1 - t)))
    return fn


def follow(perf, path, f0, f1, root=None):
    """Key the root (every frame f0..f1) so the hips sit on path((f - f0) / (f1 - f0))."""
    root = root or perf.root
    sc = bpy.context.scene
    rig = perf.rig
    for f in range(int(f0), int(f1) + 1):
        sc.frame_set(f)
        hips = rig.matrix_world @ rig.pose.bones[HIPS].head
        delta = hips - root.matrix_world.translation
        want = path((f - f0) / max(1, f1 - f0))
        loc = want - delta
        for i in range(3):
            anim.key(root, "location", f, loc[i], i, "lin")


def face_along(perf, path, f0, f1, offset_deg=0.0, step=2):
    """Yaw the root to face the direction of travel along the path."""
    prev = None
    for f in range(int(f0), int(f1) + 1, step):
        t = (f - f0) / max(1, f1 - f0)
        d = path(min(1.0, t + 0.02)) - path(max(0.0, t - 0.02))
        if d.xy.length < 1e-4:
            continue
        a = math.atan2(d.x, -d.y) + math.radians(offset_deg)     # face 0 = towards -Y
        if prev is not None:
            a = prev + (a - prev + math.pi) % (2 * math.pi) - math.pi
        prev = a
        anim.key(perf.root, "rotation_euler", f, a, 2, "lin")
