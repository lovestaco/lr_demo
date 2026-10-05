"""Shared shot setup: stage, character look, framing, save. Used by every act script."""
import bpy, json, math, os
from . import paths, fx

FPS = 30
L_HAND, R_HAND, HIPS = "mixamorig:LeftHand", "mixamorig:RightHand", "mixamorig:Hips"


def stage(theme="light", subject=(-2.4, 0.0), physical=True):
    """Studio + masked Miles (physical=False keeps the model's original toon shading). Returns the rig."""
    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.frame_start = 1
    fx.studio(theme=theme, subject=subject)
    if physical:
        fx.physical_shading(bpy.data.objects["MilesMasked"], lift=1.45, sheen=0.5)
    return bpy.data.objects["MilesRig"]


SFX = []          # [(label, frame)] collected by sfx(); finish() turns them into "sfx <name>#<n>" cues


def sfx(name, frame, gain=1.0):
    """Mark a sound effect at a frame (06_assemble.py places assets/audio/sfx/<name>.* there)."""
    SFX.append((f"sfx {name}#{len(SFX)}" + (f"@{gain:g}" if gain != 1.0 else ""), int(frame)))
    return frame


def hold_camera(cam, start, end, c, t):
    """Locked framing while a screen is up: no pans/zooms between start and end."""
    cam.at(int(start), c, t, "lin")
    cam.at(int(end), c, t, "inout")


def frame_span(left, right, plane_y, lens_mm=32, pad=1.02, cam_z=1.85, target_z=1.7):
    """Camera + target that fit world x-range [left, right] at depth plane_y."""
    cx = (left + right) / 2
    dist = (right - left) * pad / 2 / math.tan(math.atan(18 / lens_mm))
    return (cx, plane_y - dist, cam_z), (cx, plane_y * 0.5, target_z)


def finish(name, markers=(), exposure=-0.55, samples=24, end_state=None, cameras=(), view="Standard", grade=None):
    sc = bpy.context.scene
    fx.look(samples=samples, exposure=exposure, view=view, grade=grade)
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 33
    sc.timeline_markers.clear()
    markers = list(markers) + SFX
    for label, f in markers:
        sc.timeline_markers.new(label, frame=int(f))
    for f, cam_ob in cameras:                  # camera switches (marker-bound), e.g. POV / close-up / snorricam
        sc.timeline_markers.new(f"cam {cam_ob.name}", frame=int(f)).camera = cam_ob
    if cameras:
        sc.camera = min(cameras, key=lambda c: c[0])[1]
    preview_audio(name, markers)
    sc.frame_set(1)
    os.makedirs(paths.BUILD, exist_ok=True)
    out = paths.shot_blend(name)
    bpy.ops.wm.save_as_mainfile(filepath=out)
    # cue sheet for assembly (voice-over sync etc.): label -> seconds
    with open(os.path.join(paths.BUILD, name + "_cues.json"), "w") as fh:
        json.dump({"fps": FPS, "frames": sc.frame_end, "duration": sc.frame_end / FPS,
                   "cues": {label: int(f) / FPS for label, f in markers},
                   "end_state": end_state or {}}, fh, indent=1)


def vo_folder(name):
    """assets/audio/vo_<name>, else the longest prefix (piece2_cine -> vo_piece2), else assets/audio/vo."""
    audio = os.path.join(paths.ROOT, "assets", "audio")
    parts = name.split("_")
    for k in range(len(parts), 0, -1):
        d = os.path.join(audio, "vo_" + "_".join(parts[:k]))
        if os.path.isdir(d):
            return d
    return os.path.join(audio, "vo")


SFX_PREVIEW_GAIN = 0.385          # keep in step with SFX_GAIN in scripts/06_assemble.py


def preview_audio(name, markers):
    """Lay the voice lines + sound effects into the .blend's sequencer at their cue markers, so
    viewport playback (Space) is in sync with sound. Final mixing still happens in 06_assemble."""
    import glob
    sc = bpy.context.scene
    audio = os.path.join(paths.ROOT, "assets", "audio")
    vo_dir = vo_folder(name)
    se = sc.sequence_editor_create()
    strips = se.strips if hasattr(se, "strips") else se.sequences
    for st in list(strips):
        strips.remove(st)
    for label, f in markers:
        if label.startswith("vo "):
            path, ch, vol = os.path.join(vo_dir, f"line_{int(label.split()[1]):02d}.wav"), 1, 1.0
        elif label.startswith("sfx "):
            nm, _, gain = label[4:].partition("@")
            hits = sorted(glob.glob(os.path.join(audio, "sfx", nm.split("#")[0] + ".*")))
            path, ch, vol = (hits[0] if hits else ""), 2 + len(strips) % 3, SFX_PREVIEW_GAIN * float(gain or 1.0)
        else:
            continue
        if os.path.exists(path):
            st = strips.new_sound(label, path, ch, int(f))
            st.volume = vol
    sc.sync_mode = "AUDIO_SYNC"          # playback keeps real time and stays in sync with the sound


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
