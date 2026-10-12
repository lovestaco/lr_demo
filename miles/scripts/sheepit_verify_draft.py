"""sheepit_verify.py for the 360p DRAFT packages (sheepit_pack.py --draft: no motion blur, no full-resolution ray tracing, 16 samples).

    blender -b EXTRACTED/street_part0.blend --python scripts/sheepit_verify_draft.py -- --frames 1-1101 --h 360 --samples 16

Runs the unchanged sheepit_verify.py with the three final-quality expectations (ray tracing at full resolution, motion blur on)
swapped for the draft ones (motion blur off; the ray-tracing settings are not checked: the draft keeps the file's own).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "sheepit_verify.py")).read()
for old, new in ((' ("use_raytracing", e.use_raytracing, True),\n       ("ray_tracing resolution_scale", e.ray_tracing_options.resolution_scale, "1"), ("use_motion_blur", r.use_motion_blur, True),',
                  ' ("use_motion_blur", r.use_motion_blur, False),'),):
    assert old in src, "sheepit_verify.py changed: update this wrapper"
    src = src.replace(old, new)
exec(compile(src, os.path.join(HERE, "sheepit_verify.py"), "exec"), {"__name__": "__main__", "__file__": os.path.join(HERE, "sheepit_verify.py")})
