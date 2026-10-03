"""Fast clip previews: render N evenly spaced frames of each action into one labelled sheet.

    from pipeline import preview
    preview.clip_sheet(rig, ["Hard Landing", "Landing"], "/tmp/landings.png")
"""
import bpy, os, subprocess, tempfile
from mathutils import Vector


def _cam(scene, loc, target):
    cam = bpy.data.objects.get("_PreviewCam")
    if cam is None:
        cam = bpy.data.objects.new("_PreviewCam", bpy.data.cameras.new("_PreviewCam"))
        scene.collection.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 28
    scene.camera = cam
    return cam


def clip_sheet(rig, actions, out_png, frames_per_clip=6, size=(320, 400), side=False):
    """Render each action at evenly spaced frames; one row per action."""
    sc = bpy.context.scene
    prev_engine = sc.render.engine
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"
    sc.display.shading.color_type = "SINGLE"          # flat grey reads motion better than the black suit
    sc.display.shading.single_color = (0.8, 0.8, 0.8)
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    if sc.world is None:
        sc.world = bpy.data.worlds.new("_PreviewWorld")
    sc.world.color = (0.18, 0.2, 0.24)
    loc = (4.2, 0, 1.3) if side else (0, -4.6, 1.3)
    _cam(sc, loc, (0, 0, 1.0))
    tmp = tempfile.mkdtemp()
    rows = []
    for ai, name in enumerate(actions):
        act = bpy.data.actions[name]
        rig.animation_data.action = act
        rig.animation_data.action_slot = act.slots[0]
        f0, f1 = (int(v) for v in act.frame_range)
        tiles = []
        for i in range(frames_per_clip):
            f = round(f0 + (f1 - f0) * i / max(1, frames_per_clip - 1))
            sc.frame_set(f)
            p = os.path.join(tmp, f"{ai:02d}_{i}.png")
            sc.render.filepath = p
            bpy.ops.render.render(write_still=True)
            lab = f"{name} f{f}".replace(":", "").replace("'", "")
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", p, "-vf",
                            f"drawtext=text='{lab}':x=4:y=4:fontsize=14:fontcolor=white:box=1:boxcolor=black@0.6",
                            p.replace(".png", "_l.png")])
            tiles.append(p.replace(".png", "_l.png"))
        row = os.path.join(tmp, f"row{ai:02d}.png")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *sum((["-i", t] for t in tiles), []),
                        "-filter_complex", f"hstack=inputs={len(tiles)}", row])
        rows.append(row)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *sum((["-i", r] for r in rows), []),
                    "-filter_complex", f"vstack=inputs={len(rows)}" if len(rows) > 1 else "null", out_png])
    sc.render.engine = prev_engine
    return out_png
