"""Render build/scene.blend.

    blender -b build/scene.blend --python scripts/05_render.py -- sheet          # contact sheet of markers + samples
    blender -b build/scene.blend --python scripts/05_render.py -- full [pct] [from_frame]   # -> renders/<name>.mp4
        pct: 33 = 360p preview (default, fast), 67 = 720p, 100 = 1080p final
        from_frame: re-render only from that frame on, reusing the earlier frames (same pct!)
        --samples N: override EEVEE samples (8 = quick draft, 24 = default)
        --fast: draft quality (no ray-traced reflections, no motion blur, 8 samples) ~2x faster

Frames go to build/frames/ (gitignored); the encoded video to renders/.
"""
import bpy, os, sys, subprocess, shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import paths, fx

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["sheet"]
samples = None
fast = "--fast" in args                        # draft: no ray tracing, no motion blur, 8 samples
if fast:
    args.remove("--fast")
if "--samples" in args:                      # e.g. -- full 33 --samples 8   (quick draft quality)
    i = args.index("--samples")
    samples = int(args[i + 1])
    del args[i:i + 2]
mode = args[0]
sc = bpy.context.scene
name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]

if mode == "sheet":
    out_dir = os.path.join(paths.BUILD, "sheet")
    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(out_dir)
    sc.render.resolution_percentage = 25
    fx.fit_vignette(sc)
    sc.eevee.taa_render_samples = 8
    frames = sorted({int(m.frame) for m in sc.timeline_markers} |
                    set(range(sc.frame_start, sc.frame_end + 1, max(1, (sc.frame_end - sc.frame_start) // 34))))
    for f in frames:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(out_dir, f"f{f:04d}.png")
        bpy.ops.render.render(write_still=True)
    cols = 5
    rows = -(-len(frames) // cols)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-pattern_type", "glob", "-i", os.path.join(out_dir, "*.png"),
                    "-vf", f"drawtext=text='%{{metadata\\:lavf.image2dec.source_basename}}':x=6:y=6:fontsize=16:"
                    f"fontcolor=white:box=1:boxcolor=black@0.6,tile={cols}x{rows}",
                    "-frames:v", "1", os.path.join(paths.BUILD, f"{name}_sheet.png")])
    print("SHEET", os.path.join(paths.BUILD, f"{name}_sheet.png"))

elif mode == "full":
    pct = int(args[1]) if len(args) > 1 else 33
    sc.render.resolution_percentage = pct
    fx.fit_vignette(sc)
    if samples:
        sc.eevee.taa_render_samples = samples
    if fast:
        sc.eevee.taa_render_samples = samples or 8
        if hasattr(sc.eevee, "use_raytracing"):
            sc.eevee.use_raytracing = False
        sc.render.use_motion_blur = False
    frames_dir = os.path.join(paths.BUILD, "frames", name)
    if len(args) > 2:
        sc.frame_start = int(args[2])
    else:
        shutil.rmtree(frames_dir, ignore_errors=True)
    os.makedirs(frames_dir, exist_ok=True)
    sc.render.filepath = os.path.join(frames_dir, "f_")
    sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(animation=True)
    os.makedirs(paths.RENDERS, exist_ok=True)
    raw_h = sc.render.resolution_y * pct / 100
    h = min((270, 360, 540, 720, 1080, 1440, 2160), key=lambda s: abs(s - raw_h))   # snap to a standard height
    out = os.path.join(paths.RENDERS, f"{name}_{h}p.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(sc.render.fps), "-i",
                    os.path.join(frames_dir, "f_%04d.png"), "-vf", f"scale=-2:{h}",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], check=True)
    print("VIDEO", out)
