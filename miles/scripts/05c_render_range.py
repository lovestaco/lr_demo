"""Render frame ranges of a built .blend to kept JPEG frames (for parallel renders and frames made elsewhere).

    blender -b build/street_part2.blend --python scripts/05c_render_range.py -- OUT_DIR 1-1200 [3036-3500 ...] [--h 720] [--samples 16] [--fast] [--final] [--png] [--motion-blur]

Frames land as OUT_DIR/f_NNNN.jpg (quality 95, numbered by scene frame) and are kept. Ranges are inclusive. Defaults:
720p, 16 samples, motion blur off (the review-render settings). Already-rendered frames are skipped, so an
interrupted render can simply be restarted. --fast = draft quality: no ray-traced reflections, no motion blur,
8 samples (unless --samples overrides), matching 05_render.py --fast.
--final = the finished-film look: 1080p, 64 samples, full-resolution ray-traced reflections, motion blur, lossless
PNG (RGB, compression 15). Individual flags (--png, --motion-blur, --h, --samples) can be used on their own.
Each run of missing frames is rendered as one animation call (faster than a render call per frame).
"""
import bpy, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import fx

args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
flag = lambda k: (k in args) and (args.remove(k) or True)
fast = flag("--fast")
final = flag("--final")
png = flag("--png") or final
motion_blur = flag("--motion-blur") or final
opt = lambda k, d: type(d)(args[args.index(k) + 1]) if k in args else d
height = opt("--h", 1080 if final else 720)
samples = int(args[args.index("--samples") + 1]) if "--samples" in args else (64 if final else 8 if fast else 16)
ranges = [tuple(int(v) for v in a.split("-")) for a in args[1:] if "-" in a and a[0].isdigit()]
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = height * 16 // 9, height, 100
fx.fit_vignette(sc)
sc.eevee.taa_render_samples = samples
sc.render.use_motion_blur = motion_blur
if fast and hasattr(sc.eevee, "use_raytracing"):
    sc.eevee.use_raytracing = False
if final and hasattr(sc.eevee, "ray_tracing_options"):
    sc.eevee.use_raytracing = True
    sc.eevee.ray_tracing_options.resolution_scale = "1"           # reflections at full resolution (the file has 1/2)
    sc.eevee.ray_tracing_options.screen_trace_quality = 0.5
EXT = "png" if png else "jpg"
if png:
    im = sc.render.image_settings
    im.file_format, im.color_mode, im.color_depth, im.compression = "PNG", "RGB", "8", 15
else:
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 95
os.makedirs(out, exist_ok=True)


def missing_runs(a, b):
    """Contiguous runs of frames in a..b that have no kept file yet."""
    runs, start = [], None
    for f in range(a, b + 2):
        todo = f <= b and not (os.path.exists(os.path.join(out, f"f_{f:04d}.{EXT}")) and os.path.getsize(os.path.join(out, f"f_{f:04d}.{EXT}")) > 0)
        if todo and start is None:
            start = f
        elif not todo and start is not None:
            runs.append((start, f - 1))
            start = None
    return runs


# one animation render per run of missing frames: Blender sets up once instead of once per frame (~20% faster)
n = 0
for a, b in ranges:
    for ra, rb in missing_runs(a, b):
        sc.frame_start, sc.frame_end = ra, rb
        sc.render.filepath = os.path.join(out, "f_####")
        bpy.ops.render.render(animation=True)
        n += rb - ra + 1
print("DONE", ranges, n, "frames")
