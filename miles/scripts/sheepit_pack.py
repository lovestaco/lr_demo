"""Make a self-contained SheepIt project from a built street .blend (the original is not touched).

    blender -b build/street_part_1_final.blend --python scripts/sheepit_pack.py -- OUT.blend [--h 1080] [--samples 64] [--frames A-B] [--draft]

OUT.blend is written into its own folder (the "stage"): image SEQUENCES cannot be packed, so their folders are copied next to it
(assets/...) and the paths made relative; zip the whole stage folder for SheepIt (blend at the zip root).

Packs every external file that exists into the .blend, drops missing texture images that feed nothing, bakes the render
settings in (SheepIt cannot run our scripts): --h resolution, --samples, ray-traced reflections at full resolution, motion blur,
PNG RGB 8-bit, vignette fitted to the size. --draft = 360p/16 samples/no blur/no raytrace-quality bump for quick tests.
"""
import bpy, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import fx

args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
opt = lambda k, d: type(d)(args[args.index(k) + 1]) if k in args else d
draft = "--draft" in args
height = opt("--h", 360 if draft else 1080)
samples = opt("--samples", 16 if draft else 64)
sc = bpy.context.scene
print("SHEEP file:", os.path.basename(bpy.data.filepath), "| texts", [t.name for t in bpy.data.texts], "| scripted drivers",
      sum(1 for ob in bpy.data.objects if ob.animation_data for d in ob.animation_data.drivers if d.driver.type == 'SCRIPTED'),
      "| libraries", [l.filepath for l in bpy.data.libraries])

# audio (voice-over / sfx sound strips) is mixed later by 06_assemble.py and is not needed to render frames: remove it so
# SheepIt does not report missing sound files
se = sc.sequence_editor
n_snd = 0
if se:
    strips = getattr(se, "strips_all", None) or getattr(se, "sequences_all", [])
    for st in list(strips):
        if st.type == "SOUND":
            (getattr(se, "strips", None) or se.sequences).remove(st); n_snd += 1
for snd in list(bpy.data.sounds):
    bpy.data.sounds.remove(snd)
print("SHEEP removed sound strips:", n_snd, "| sounds left:", len(bpy.data.sounds), "| remaining strips:", len(list(getattr(se, "strips_all", []) or [])) if se else 0)
colls = (bpy.data.images, bpy.data.sounds, bpy.data.movieclips, bpy.data.fonts)
ext = lambda d: getattr(d, "filepath", "") and not d.filepath.startswith("<") and not getattr(d, "packed_file", None)
import shutil
MILES = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
stage = os.path.dirname(os.path.abspath(out))
os.makedirs(stage, exist_ok=True)
packed = dropped = seqs = 0
for c in colls:
    for d in list(c):
        if not ext(d):
            continue
        if getattr(d, "source", "") == "SEQUENCE" and os.path.exists(bpy.path.abspath(d.filepath)):
            src = os.path.dirname(os.path.realpath(bpy.path.abspath(d.filepath)))
            rel = os.path.relpath(src, os.path.realpath(MILES))
            if rel.startswith(".."):                       # outside miles/: keep it inside the stage anyway (never an escaping path)
                rel = os.path.join("external", os.path.basename(src))
            dst = os.path.join(stage, rel)
            if not os.path.isdir(dst):
                shutil.copytree(src, dst)
            d.filepath = os.path.join(dst, os.path.basename(d.filepath)); seqs += 1
        elif os.path.exists(bpy.path.abspath(d.filepath)):
            d.pack(); packed += 1
        elif isinstance(d, bpy.types.Image):
            used = [n for m in bpy.data.materials if m.node_tree for n in m.node_tree.nodes if getattr(n, "image", None) == d]
            if all(not any(o.is_linked for o in n.outputs) for n in used):      # feeds nothing: safe to drop
                for n in used:
                    n.image = None
                bpy.data.images.remove(d); dropped += 1
print("SHEEP packed", packed, "| sequences copied", seqs, "| dropped unused missing images", dropped)
left = [(d.name, d.filepath[:70]) for c in colls for d in c if ext(d)]
print("SHEEP still external:", len(left), left[:4])

sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = height * 16 // 9, height, 100
fx.fit_vignette(sc)
sc.eevee.taa_render_samples = samples
sc.render.use_motion_blur = not draft
if not draft and hasattr(sc.eevee, "ray_tracing_options"):
    sc.eevee.use_raytracing = True
    sc.eevee.ray_tracing_options.resolution_scale = "1"
    sc.eevee.ray_tracing_options.screen_trace_quality = 0.5
im = sc.render.image_settings
im.file_format, im.color_mode, im.color_depth, im.compression = "PNG", "RGB", "8", 15
if "--frames" in args:
    a, b = args[args.index("--frames") + 1].split("-")
    sc.frame_start, sc.frame_end = int(a), int(b)
bpy.context.preferences.filepaths.save_version = 0       # no .blend1 backup next to the blend (it would be zipped)
bpy.ops.wm.save_as_mainfile(filepath=out, compress=True, relative_remap=False)
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_mainfile(compress=True)
print("SHEEP saved", out, os.path.getsize(out) // 1000000, "MB | res", sc.render.resolution_x, sc.render.resolution_y, f"{sc.render.resolution_percentage}%",
      "| samples", sc.eevee.taa_render_samples, "| frames", sc.frame_start, sc.frame_end, "| fps", sc.render.fps,
      "| raytracing", getattr(sc.eevee, "use_raytracing", None), "| motion blur", sc.render.use_motion_blur, "|", im.file_format, im.color_mode)
