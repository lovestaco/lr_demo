"""Keyframe helpers that work with Blender 5.x layered actions."""
import bpy

EASE = {  # name -> (interpolation, easing)
    "bez": ("BEZIER", None), "lin": ("LINEAR", None), "const": ("CONSTANT", None),
    "in": ("QUAD", "EASE_IN"), "out": ("QUAD", "EASE_OUT"), "inout": ("SINE", "EASE_IN_OUT"),
    "back": ("BACK", "EASE_OUT"), "expo_out": ("EXPO", "EASE_OUT"), "cubic_out": ("CUBIC", "EASE_OUT"),
}


def fcurve(id_, path, index=0):
    ad = id_.animation_data
    if not ad or not ad.action:
        return None
    for layer in ad.action.layers:
        for strip in layer.strips:
            cb = strip.channelbag(ad.action_slot)
            if cb:
                fc = cb.fcurves.find(path, index=index)
                if fc:
                    return fc
    return None


def key(owner, prop, frame, value, index=-1, ease="bez"):
    """Set owner.prop (or one component) and key it. `ease` shapes the segment LEAVING this key."""
    cur = getattr(owner, prop)
    if index >= 0:
        cur[index] = value
        indices = [index]
    elif hasattr(cur, "__len__"):
        setattr(owner, prop, value)
        indices = range(len(cur))
    else:
        setattr(owner, prop, value)
        indices = [0]
    owner.keyframe_insert(prop, index=index, frame=frame)
    interp, easing = EASE[ease]
    for i in indices:
        fc = fcurve(owner.id_data, owner.path_from_id(prop), i)
        if fc is None:
            continue
        for kp in fc.keyframe_points:
            if abs(kp.co.x - frame) < 1e-3:
                kp.interpolation = interp
                if easing:
                    kp.easing = easing


def keys(owner, prop, seq, index=-1):
    """seq: [(frame, value, ease), ...]"""
    for item in seq:
        f, v = item[0], item[1]
        key(owner, prop, f, v, index, item[2] if len(item) > 2 else "bez")


def visible(obj, frames_on_off):
    """frames_on_off: [(frame, bool), ...] -> hide_render/hide_viewport with constant steps."""
    for f, on in frames_on_off:
        key(obj, "hide_render", f, not on, ease="const")
        key(obj, "hide_viewport", f, not on, ease="const")
