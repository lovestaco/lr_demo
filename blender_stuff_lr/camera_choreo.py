"""
camera_choreo.py — Stage 4: camera choreography + collision cone + aircraft appear
Blender 5.2. Run after build_scope.py + build_motion.py (scope.blend already loaded).

Camera beats (9 keyframes across 150s):
  0-16s   top-down wide (Hook / Belief)
  30s     slight tilt (Velocity)
  47s     angled (Problems intro)
  54s     push toward cone zone (Blast problem)
  72s     close push-in (Cone fully visible)
  87s     pull back
  101s    ease toward top
  132-150s wide top-down (Close)

Collision cone: semi-transparent red, 71→75 expands, 83→87 collapses
Aircraft stagger-appear: all 60 darts bloom into view 0→15.3s
"""
import bpy, math
from mathutils import Vector

fps = 30

def to_frame(seconds):
    return max(1, int(round(seconds * fps)))

def set_linear(obj):
    if not obj.animation_data or not obj.animation_data.action:
        return
    for layer in obj.animation_data.action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fc in cb.fcurves:
                    for kp in fc.keyframe_points:
                        kp.interpolation = 'LINEAR'

def set_bezier_clamped(obj):
    if not obj.animation_data or not obj.animation_data.action:
        return
    for layer in obj.animation_data.action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fc in cb.fcurves:
                    for kp in fc.keyframe_points:
                        kp.interpolation = 'BEZIER'
                        kp.handle_left_type  = 'AUTO_CLAMPED'
                        kp.handle_right_type = 'AUTO_CLAMPED'

def look_at(cam_obj, cam_pos_tuple, target_tuple):
    """Point camera (−Z forward, +Y up) at target."""
    cam_pos = Vector(cam_pos_tuple)
    target  = Vector(target_tuple)
    direction = (target - cam_pos).normalized()
    # to_track_quat takes string axis names; fall back to 'X' when direction ≈ ±Y
    up_axis = 'Y' if abs(direction.y) < 0.99 else 'X'
    rot = direction.to_track_quat('-Z', up_axis)
    cam_obj.location       = cam_pos
    cam_obj.rotation_euler = rot.to_euler()

# ── Camera choreography ────────────────────────────────────────────────────────
cam = bpy.data.objects.get("Cam_TopDown")
if not cam:
    raise RuntimeError("Cam_TopDown not found — run build_scope.py first")
if cam.animation_data:
    cam.animation_data_clear()

cam_beats = [
    # (time_s, cam_pos,               look_at_pos)
    ( 0,   ( 0.0,  0.0,  8.5),  ( 0.0,  0.0,  0.0)),  # Hook: top-down wide
    (16,   ( 0.0,  0.0,  8.5),  ( 0.0,  0.0,  0.0)),  # Belief: hold top-down
    (30,   ( 0.0, -0.4,  7.5),  ( 0.0,  0.2,  0.0)),  # Velocity: slight tilt fwd
    (47,   ( 0.3, -1.2,  6.0),  ( 0.0, -0.3,  0.0)),  # Problems intro: angled
    (54,   ( 0.5, -0.8,  5.0),  ( 0.5, -1.3,  0.0)),  # Push toward blast zone
    (72,   ( 0.5, -0.2,  3.0),  ( 0.5, -1.3,  0.0)),  # Close push-in (cone visible)
    (87,   ( 0.0, -0.5,  7.0),  ( 0.0,  0.0,  0.0)),  # Pull back
    (101,  ( 0.0, -0.3,  7.8),  ( 0.0,  0.0,  0.0)),  # Ease toward top
    (132,  ( 0.0,  0.0,  9.5),  ( 0.0,  0.0,  0.0)),  # Close: wide pull
    (150,  ( 0.0,  0.0,  9.5),  ( 0.0,  0.0,  0.0)),  # End: hold wide
]

for t, cam_pos, tgt in cam_beats:
    f = to_frame(t)
    look_at(cam, cam_pos, tgt)
    cam.keyframe_insert(data_path="location",       frame=f)
    cam.keyframe_insert(data_path="rotation_euler", frame=f)

set_bezier_clamped(cam)
print(f"Camera: {len(cam_beats)} keyframes set with BEZIER easing")

# ── Collision cone (blast radius, 72–87s) ─────────────────────────────────────
for name in list(bpy.data.objects.keys()):
    if name.startswith("cone_blast"):
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

# Cone tip aims FROM origin TOWARD (0.5, -1.3) direction (one PR → blast zone)
# Center the cone at radius 1.3 from origin, axis along that radius
cone_dir    = Vector((0.5, -1.3, 0)).normalized()
cone_center = cone_dir * 1.3          # midpoint of cone depth on the radar
cone_depth  = 1.6
cone_tip_v  = cone_center + cone_dir * (cone_depth / 2)   # tip outward
# We want cone +Z (tip) to point outward → track +Z to cone_dir
rot_q = cone_dir.to_track_quat('Z', 'X')

bpy.ops.mesh.primitive_cone_add(
    vertices=32, radius1=0.85, radius2=0.0, depth=cone_depth,
    location=(cone_center.x, cone_center.y, 0.015)
)
cone = bpy.context.active_object
cone.name = "cone_blast_radius"
cone.rotation_euler = rot_q.to_euler()

mat_cone = bpy.data.materials.new("mat_cone_blast")
mat_cone.use_nodes = True
mat_cone.blend_method = 'BLEND'
nt = mat_cone.node_tree
nt.nodes.clear()
out_n = nt.nodes.new('ShaderNodeOutputMaterial')
em_n  = nt.nodes.new('ShaderNodeEmission')
tr_n  = nt.nodes.new('ShaderNodeBsdfTransparent')
mix_n = nt.nodes.new('ShaderNodeMixShader')
em_n.inputs['Color'].default_value     = (0.86, 0.15, 0.15, 1.0)   # alert red
em_n.inputs['Strength'].default_value  = 2.5
mix_n.inputs['Fac'].default_value      = 0.42   # mostly visible
nt.links.new(tr_n.outputs['BSDF'],     mix_n.inputs[1])
nt.links.new(em_n.outputs['Emission'], mix_n.inputs[2])
nt.links.new(mix_n.outputs['Shader'],  out_n.inputs['Surface'])
cone.data.materials.append(mat_cone)

# Scale animation: collapsed before blast window, expands, holds, collapses
cone.scale = (0.0, 0.0, 0.0)
cone.keyframe_insert(data_path="scale", frame=to_frame(71))
cone.scale = (1.0, 1.0, 1.0)
cone.keyframe_insert(data_path="scale", frame=to_frame(75))
cone.scale = (1.0, 1.0, 1.0)
cone.keyframe_insert(data_path="scale", frame=to_frame(83))
cone.scale = (0.0, 0.0, 0.0)
cone.keyframe_insert(data_path="scale", frame=to_frame(87))
set_linear(cone)
print("Collision cone: placed and animated 71→75→83→87s")

# ── Aircraft stagger-appear (bloom 0 → 15.3s) ─────────────────────────────────
aircraft_objs = sorted(
    [o for o in bpy.data.objects if o.name.startswith("aircraft_")],
    key=lambda o: o.name
)
n = len(aircraft_objs)
APPEAR_WINDOW = to_frame(15.3)   # frame 459
FADE_FRAMES   = 10

for i, obj in enumerate(aircraft_objs):
    appear_f = 1 + int((i / n) * (APPEAR_WINDOW - 1))
    obj.scale = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path="scale", frame=1)
    obj.scale = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path="scale", frame=appear_f)
    obj.scale = (1.0, 1.0, 1.0)
    obj.keyframe_insert(data_path="scale", frame=appear_f + FADE_FRAMES)
    obj.scale = (1.0, 1.0, 1.0)
    obj.keyframe_insert(data_path="scale", frame=4500)
    set_linear(obj)

print(f"Aircraft stagger-appear: {n} aircraft bloom over 0→15.3s")

# ── Save ───────────────────────────────────────────────────────────────────────
bpy.ops.wm.save_mainfile()
print("camera_choreo.py OK — scope.blend saved")
