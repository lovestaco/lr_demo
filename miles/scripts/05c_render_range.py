"""Render frame ranges of a built .blend to kept JPEG frames (for parallel renders and frames made elsewhere).

    blender -b build/street_part2.blend --python scripts/05c_render_range.py -- OUT_DIR 1-1200 [3036-3500 ...] [--h 720] [--samples 16]

Frames land as OUT_DIR/f_NNNN.jpg (quality 95, numbered by scene frame) and are kept. Ranges are inclusive. Defaults:
720p, 16 samples, motion blur off (the review-render settings). Already-rendered frames are skipped, so an
interrupted render can simply be restarted.
"""
import bpy, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import fx

args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
opt = lambda k, d: type(d)(args[args.index(k) + 1]) if k in args else d
height, samples = opt("--h", 720), opt("--samples", 16)
ranges = [tuple(int(v) for v in a.split("-")) for a in args[1:] if "-" in a and a[0].isdigit()]
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = height * 16 // 9, height, 100
fx.fit_vignette(sc)
sc.eevee.taa_render_samples = samples
sc.render.use_motion_blur = False
sc.render.image_settings.file_format = "JPEG"
sc.render.image_settings.quality = 95
os.makedirs(out, exist_ok=True)
n = 0
for a, b in ranges:
    for f in range(a, b + 1):
        p = os.path.join(out, f"f_{f:04d}.jpg")
        if os.path.exists(p) and os.path.getsize(p) > 0:
            continue
        sc.frame_set(f)
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        n += 1
print("DONE", ranges, n, "frames")
