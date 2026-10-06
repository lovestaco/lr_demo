"""Expressive mask lenses (Spider-Verse style): the white eye lenses widen, squint, angle and blink.

The masked mesh's lens faces use the "E Y E S" material. Shape keys move only those vertices, in the mesh's own
rest space, around each lens centre:
    Wide    surprised / excited (taller, a little wider)
    Squint  focus / smug / blink (lids close towards the middle)
    Angry   inner corners down (determined)
    Sad     inner corners up (worried)

    eyes = face.Lenses(bpy.data.objects["MilesMasked"])
    eyes.set(frame, Wide=0.8, Squint=0.0, ramp=6)       # ease every key to these weights
    eyes.blinks(start, end, every=95)                  # natural blinks (lids snap shut and open)
"""
import math, random
import bpy
from mathutils import Vector
from . import anim

KEYS = ("Wide", "Squint", "Angry", "Sad")


class Lenses:
    def __init__(self, ob, material="E Y E S"):
        self.ob = ob
        me = ob.data
        mi = next(i for i, m in enumerate(me.materials) if m and m.name.startswith(material))
        verts = sorted({v for p in me.polygons if p.material_index == mi for v in p.vertices})
        co = [me.vertices[i].co.copy() for i in verts]
        # axes from the mesh itself: height = the body's longest extent, lateral = the line between the lenses
        allv = [v.co for v in me.vertices]
        ext = [max(v[k] for v in allv) - min(v[k] for v in allv) for k in range(3)]
        up_i = max(range(3), key=lambda k: ext[k])
        mid = sum(co, Vector()) / len(co)
        lat_i = max((k for k in range(3) if k != up_i), key=lambda k: max(v[k] for v in co) - min(v[k] for v in co))
        side = {i: (c[lat_i] > mid[lat_i]) for i, c in zip(verts, co)}
        centre = {}
        for s in (True, False):
            pts = [c for i, c in zip(verts, co) if side[i] == s]
            centre[s] = sum(pts, Vector()) / len(pts)
        h = {s: max(c[up_i] for i, c in zip(verts, co) if side[i] == s) - min(c[up_i] for i, c in zip(verts, co) if side[i] == s)
             for s in (True, False)}
        if not me.shape_keys:
            ob.shape_key_add(name="Basis", from_mix=False)
        self.kb = {}
        for name in KEYS:
            kb = me.shape_keys.key_blocks.get(name) or ob.shape_key_add(name=name, from_mix=False)
            for i, c in zip(verts, co):
                s = side[i]
                d = c - centre[s]
                lat = d[lat_i]
                inward = lat if s is False else -lat           # + towards the nose
                ver = d[up_i]
                nv, nl = ver, lat
                if name == "Wide":
                    nv, nl = ver * 1.28, lat * 1.08
                elif name == "Squint":
                    nv = ver * 0.12 - h[s] * 0.08              # lids meet a little below the middle
                elif name == "Angry":
                    nv = ver * 0.72 - math.tan(math.radians(24)) * inward
                elif name == "Sad":
                    nv = ver * 0.85 + math.tan(math.radians(20)) * inward
                new = c.copy()
                new[up_i] = centre[s][up_i] + nv
                new[lat_i] = centre[s][lat_i] + nl
                kb.data[i].co = new
            kb.value = 0.0
            self.kb[name] = kb
        self.state = {k: 0.0 for k in KEYS}

    def set(self, frame, ramp=6, **w):
        """Ease to the given weights over `ramp` frames ending at `frame` (others keep their value)."""
        f = int(frame)
        for k, v in w.items():
            kb = self.kb[k]
            anim.key(kb, "value", f - ramp, self.state[k], ease="inout")
            anim.key(kb, "value", f, v, ease="inout")
            self.state[k] = v

    def blinks(self, start, end, every=95, seed=3, skip=()):
        """Quick blinks (2 frames shut) on the Squint key, irregular spacing, none inside `skip` spans."""
        r = random.Random(seed)
        kb = self.kb["Squint"]
        fc = None
        f = int(start) + r.randint(10, every)
        while f < end - 6:
            if not any(a - 8 <= f <= b + 8 for a, b in skip):
                base = self._value_at(kb, f - 2)
                anim.key(kb, "value", f - 2, base, ease="inout")
                anim.key(kb, "value", f, 1.0, ease="const")
                anim.key(kb, "value", f + 2, 1.0, ease="out")
                anim.key(kb, "value", f + 5, base, ease="inout")
            f += int(every * r.uniform(0.6, 1.4))

    @staticmethod
    def _value_at(kb, f):
        fc = anim.fcurve(kb.id_data, kb.path_from_id("value"), 0)
        return fc.evaluate(f) if fc else kb.value
