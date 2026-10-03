"""Shared shot setup: stage, character look, framing, save. Used by every act script."""
import bpy, json, math, os
from . import paths, fx

FPS = 30
L_HAND, R_HAND, HIPS = "mixamorig:LeftHand", "mixamorig:RightHand", "mixamorig:Hips"


def stage(theme="light", subject=(-2.4, 0.0)):
    """Light studio + physically shaded masked Miles. Returns the rig."""
    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.frame_start = 1
    fx.studio(theme=theme, subject=subject)
    fx.physical_shading(bpy.data.objects["MilesMasked"], lift=1.45, sheen=0.5)
    return bpy.data.objects["MilesRig"]


def frame_span(left, right, plane_y, lens_mm=32, pad=1.02, cam_z=1.85, target_z=1.7):
    """Camera + target that fit world x-range [left, right] at depth plane_y."""
    cx = (left + right) / 2
    dist = (right - left) * pad / 2 / math.tan(math.atan(18 / lens_mm))
    return (cx, plane_y - dist, cam_z), (cx, plane_y * 0.5, target_z)


def finish(name, markers=(), exposure=-0.55, samples=24, end_state=None):
    sc = bpy.context.scene
    fx.look(samples=samples, exposure=exposure)
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 33
    sc.timeline_markers.clear()
    for label, f in markers:
        sc.timeline_markers.new(label, frame=int(f))
    sc.frame_set(1)
    os.makedirs(paths.BUILD, exist_ok=True)
    out = paths.shot_blend(name)
    bpy.ops.wm.save_as_mainfile(filepath=out)
    # cue sheet for assembly (voice-over sync etc.): label -> seconds
    with open(os.path.join(paths.BUILD, name + "_cues.json"), "w") as fh:
        json.dump({"fps": FPS, "frames": sc.frame_end, "duration": sc.frame_end / FPS,
                   "cues": {label: int(f) / FPS for label, f in markers},
                   "end_state": end_state or {}}, fh, indent=1)


def load_end_state(name):
    """What a previous act ended on (character/board/camera), for a seamless continuation."""
    with open(os.path.join(paths.BUILD, name + "_cues.json")) as fh:
        return json.load(fh)["end_state"]


def world_bone(rig, bone, frame):
    bpy.context.scene.frame_set(int(frame))
    return list(rig.matrix_world @ rig.pose.bones[bone].head)


def world(obj, frame):
    bpy.context.scene.frame_set(int(frame))
    return list(obj.matrix_world.translation)
    print(f"SHOT {name}: frames 1-{sc.frame_end} ({sc.frame_end / FPS:.1f}s) -> {out}")
    return out
