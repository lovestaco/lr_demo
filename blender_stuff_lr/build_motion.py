"""
build_motion.py — Stage 2: radar sweep + aircraft traffic
Run AFTER build_scope.py (scene must exist).
Blender 5.2: fcurves live at action.layers[0].strips[0].channelbags[N].fcurves
"""
import bpy, math, random

random.seed(42)

scene = bpy.context.scene
fps           = 30
SWEEP_PERIOD  = 6.0        # seconds per full rotation
total_frames  = 150 * fps  # 4500

C_COBALT   = (0.114, 0.337, 0.941, 1.0)
C_COBALT_D = (0.015, 0.040, 0.130, 1.0)

def emissive_mat(name, color, strength=1.0):
    existing = bpy.data.materials.get(name)
    if existing:
        return existing
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    em  = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value    = color
    em.inputs['Strength'].default_value = strength
    nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    return mat

def set_linear(obj):
    """Set all keyframe interpolation to LINEAR (Blender 5.2 layered actions)."""
    if not obj.animation_data or not obj.animation_data.action:
        return
    action = obj.animation_data.action
    for layer in action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fc in cb.fcurves:
                    for kp in fc.keyframe_points:
                        kp.interpolation = 'LINEAR'

# ── Remove old motion objects ─────────────────────────────────────────────────
for name in list(bpy.data.objects.keys()):
    if name.startswith(("sweep_arm", "aircraft_", "dart_")):
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

# ── Sweep arm ─────────────────────────────────────────────────────────────────
# Thin rectangle, rotates around Z at constant rate
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 2.25, 0.002))
sweep = bpy.context.active_object
sweep.name = "sweep_arm"
sweep.scale = (0.04, 2.25, 1.0)
bpy.ops.object.transform_apply(scale=True, rotation=True, location=False)

# Gradient material: bright outer end, dim at origin
mat_sweep = bpy.data.materials.new("mat_sweep")
mat_sweep.use_nodes = True
nt = mat_sweep.node_tree; nt.nodes.clear()
out_n  = nt.nodes.new('ShaderNodeOutputMaterial')
em_n   = nt.nodes.new('ShaderNodeEmission')
grad_n = nt.nodes.new('ShaderNodeTexGradient')
coord_n= nt.nodes.new('ShaderNodeTexCoord')
ramp_n = nt.nodes.new('ShaderNodeValToRGB')
grad_n.gradient_type = 'LINEAR'
nt.links.new(coord_n.outputs['Object'], grad_n.inputs['Vector'])
ramp_n.color_ramp.elements[0].color = (*C_COBALT_D[:3], 0.0)
ramp_n.color_ramp.elements[1].color = (*C_COBALT[:3],   1.0)
nt.links.new(grad_n.outputs['Color'], ramp_n.inputs['Fac'])
nt.links.new(ramp_n.outputs['Color'], em_n.inputs['Color'])
em_n.inputs['Strength'].default_value = 4.0
nt.links.new(em_n.outputs['Emission'], out_n.inputs['Surface'])
sweep.data.materials.append(mat_sweep)

# Animate: 0 → -25 full rotations (clockwise from above)
rotations  = total_frames / (SWEEP_PERIOD * fps)
end_angle  = -rotations * 2 * math.pi
sweep.rotation_euler = (0, 0, 0)
sweep.keyframe_insert(data_path="rotation_euler", frame=1)
sweep.rotation_euler = (0, 0, end_angle)
sweep.keyframe_insert(data_path="rotation_euler", frame=total_frames)
set_linear(sweep)

print(f"Sweep: {rotations:.1f} rotations, end_angle={math.degrees(end_angle):.0f}°")

# ── Aircraft ──────────────────────────────────────────────────────────────────
# Simple arrow/dart mesh viewed from above
dart_verts = [
    ( 0.00,  0.20, 0.0),  # nose
    (-0.06, -0.10, 0.0),  # left wing tip
    ( 0.00, -0.05, 0.0),  # tail notch
    ( 0.06, -0.10, 0.0),  # right wing tip
]
dart_faces = [(0, 1, 2), (0, 2, 3)]
master_mesh = bpy.data.meshes.new("dart_master_mesh")
master_mesh.from_pydata(dart_verts, [], dart_faces)
master_mesh.update()
master_mesh.materials.append(emissive_mat("mat_blip", C_COBALT, strength=8.0))

# Master object (hidden — each aircraft uses its own mesh copy)
master_obj = bpy.data.objects.new("dart_MASTER", master_mesh)
bpy.context.collection.objects.link(master_obj)
master_obj.hide_render = True
master_obj.hide_viewport = True

NUM_AIRCRAFT = 60
kf_every = fps  # keyframe every 1s (150 keyframes per aircraft)

for i in range(NUM_AIRCRAFT):
    r      = random.uniform(0.5, 3.4)
    theta0 = random.uniform(0, 2 * math.pi)
    # mix of speeds: some fast, some slow; both directions
    speed  = random.choice([-1, 1]) * random.uniform(0.06, 0.22)

    a_mesh = master_mesh.copy()
    a_mesh.name = f"dart_mesh_{i:03d}"
    a_obj  = bpy.data.objects.new(f"aircraft_{i:03d}", a_mesh)
    bpy.context.collection.objects.link(a_obj)

    for frame in range(1, total_frames + 1, kf_every):
        t     = (frame - 1) / fps
        angle = theta0 + speed * t
        a_obj.location       = (r * math.cos(angle), r * math.sin(angle), 0.003)
        a_obj.rotation_euler = (0, 0, angle + math.pi / 2)
        a_obj.keyframe_insert(data_path="location",       frame=frame)
        a_obj.keyframe_insert(data_path="rotation_euler", frame=frame)

    set_linear(a_obj)

print(f"Aircraft: {NUM_AIRCRAFT} created, each with {total_frames//kf_every} keyframes")

# ── Frame range ───────────────────────────────────────────────────────────────
scene.frame_start = 1
scene.frame_end   = total_frames
print(f"Frame range 1–{total_frames} ({total_frames/fps:.0f}s @ {fps}fps)")
print("build_motion.py OK — ready for 5s test render")
