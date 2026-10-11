"""Verify a packed SheepIt .blend (run by make_sheepit_part3.sh on a CLEAN extraction of the zip).

    blender -b EXTRACTED/street_part3.blend --python scripts/sheepit_verify.py -- --frames 1418-2763 [--h 1080] [--samples 64]

Prints "VERIFY ok ..." lines and "VERIFY FAIL ..." for each problem, and exits with status 1 if there was any.
Checks: every external path is relative (//...), stays inside the blend's folder and exists (sequences: the folder holds
frames); no sound strips / sounds / libraries; resolution, percentage, samples, ray tracing (full-res), motion blur,
PNG RGB, frame range.
"""
import bpy, os, sys

args = sys.argv[sys.argv.index("--") + 1:]
opt = lambda k, d: type(d)(args[args.index(k) + 1]) if k in args else d
H = opt("--h", 1080)
samples = opt("--samples", 64)
fa, fb = (int(v) for v in opt("--frames", "0-0").split("-"))
sc = bpy.context.scene
base = os.path.realpath(os.path.dirname(bpy.data.filepath))
bad = []


def fail(msg):
    bad.append(msg)
    print("VERIFY FAIL", msg)


n_ext = n_pack = 0
for c in (bpy.data.images, bpy.data.movieclips, bpy.data.sounds, bpy.data.fonts, bpy.data.libraries, bpy.data.cache_files):
    for d in c:
        fp = getattr(d, "filepath", "")
        if not fp or fp.startswith("<"):
            continue
        if getattr(d, "packed_file", None):
            n_pack += 1
            continue
        n_ext += 1
        kind = f"{type(d).__name__} '{d.name}'"
        if not fp.startswith("//"):
            fail(f"{kind}: absolute path {fp[:100]}")
            continue
        ab = os.path.realpath(bpy.path.abspath(fp))
        if not (ab == base or ab.startswith(base + os.sep)):
            fail(f"{kind}: path leaves the zip folder {fp[:100]}")
        if not os.path.exists(ab):
            fail(f"{kind}: missing file {fp[:100]}")
        elif getattr(d, "source", "") == "SEQUENCE":
            n = len([f for f in os.listdir(os.path.dirname(ab)) if os.path.splitext(f)[1].lower() in (".png", ".jpg", ".jpeg", ".exr", ".tif")])
            print(f"VERIFY ok sequence {fp} ({n} frames in folder)")
            if n < 2:
                fail(f"{kind}: sequence folder has {n} frame(s)")
        else:
            print(f"VERIFY ok file {fp}")
print(f"VERIFY external {n_ext} (all relative+existing unless FAIL above), packed {n_pack}")
for im in bpy.data.images:                                       # an image with no data and no file would render pink
    if im.source == "FILE" and not im.packed_file and not im.filepath.startswith("<") and not im.has_data and im.users:
        if not os.path.exists(bpy.path.abspath(im.filepath)):
            fail(f"Image '{im.name}': used but its file is missing")

se = sc.sequence_editor
strips = list(getattr(se, "strips_all", None) or getattr(se, "sequences_all", [])) if se else []
snd = [s for s in strips if s.type == "SOUND"]
if snd or len(bpy.data.sounds):
    fail(f"sound left: {len(snd)} strips, {len(bpy.data.sounds)} sounds")
else:
    print("VERIFY ok no sound strips / sounds")
if len(bpy.data.libraries):
    fail(f"linked libraries: {[l.filepath for l in bpy.data.libraries]}")
if len(bpy.data.texts):
    print("VERIFY note: text blocks present (not run by SheepIt):", [t.name for t in bpy.data.texts])

r, e, im = sc.render, sc.eevee, sc.render.image_settings
chk = [("resolution_x", r.resolution_x, H * 16 // 9), ("resolution_y", r.resolution_y, H), ("resolution_percentage", r.resolution_percentage, 100),
       ("taa_render_samples", e.taa_render_samples, samples), ("use_raytracing", e.use_raytracing, True),
       ("ray_tracing resolution_scale", e.ray_tracing_options.resolution_scale, "1"), ("use_motion_blur", r.use_motion_blur, True),
       ("file_format", im.file_format, "PNG"), ("color_mode", im.color_mode, "RGB"), ("color_depth", im.color_depth, "8"),
       ("frame_start", sc.frame_start, fa), ("frame_end", sc.frame_end, fb), ("fps", r.fps, 30), ("engine", r.engine, "BLENDER_EEVEE")]
for name, got, want in chk:
    if got != want:
        fail(f"{name} = {got!r}, expected {want!r}")
    else:
        print(f"VERIFY ok {name} = {got!r}")
print("VERIFY RESULT", "FAILED" if bad else "PASSED", len(bad), "problem(s)")
sys.stdout.flush()
os._exit(1 if bad else 0)
