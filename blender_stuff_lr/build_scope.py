"""
build_scope.py — LiveReview "Separation" radar scope
Static geometry + bloom compositor. Run to reset the scene.
"""
import bpy, math

C_COBALT   = (0.114, 0.337, 0.941, 1.0)
C_COBALT_D = (0.015, 0.040, 0.130, 1.0)
C_BG       = (0.031, 0.043, 0.070, 1.0)

def emissive_mat(name, color, strength=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    em  = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = color
    em.inputs['Strength'].default_value = strength
    nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    return mat

def make_ring(name, radius, tube=0.012, mat=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=tube,
        major_segments=128, minor_segments=8, location=(0,0,0))
    obj = bpy.context.active_object; obj.name = name
    if mat: obj.data.materials.clear(); obj.data.materials.append(mat)
    return obj

def make_bar(name, length, width=0.008, rz=0.0, cx=0.0, cy=0.0, z=0.0, mat=None):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(cx, cy, z))
    obj = bpy.context.active_object; obj.name = name
    obj.scale = (width, length/2.0, 1.0); obj.rotation_euler = (0,0,rz)
    bpy.ops.object.transform_apply(scale=True, rotation=True, location=False)
    if mat: obj.data.materials.clear(); obj.data.materials.append(mat)
    return obj

# Clean
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
for d in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.node_groups):
    for x in list(d): d.remove(x)

# World
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = C_BG; bg.inputs['Strength'].default_value = 0.0
bpy.context.scene.world = world

# Materials
mat_ring  = emissive_mat("mat_ring",  C_COBALT,   4.0)
mat_outer = emissive_mat("mat_outer", C_COBALT,   6.0)
mat_dim   = emissive_mat("mat_dim",   C_COBALT_D, 1.2)
mat_tick  = emissive_mat("mat_tick",  C_COBALT,   3.0)
mat_grid  = emissive_mat("mat_grid",  C_COBALT_D, 0.6)
mat_ctr   = emissive_mat("mat_ctr",   C_COBALT,   12.0)
mat_blip  = emissive_mat("mat_blip",  C_COBALT,   8.0)

# Rings
for r in [1.0, 2.0, 3.0]:
    make_ring(f"ring_{r}", radius=r, tube=0.007, mat=mat_dim)
make_ring("ring_4", radius=4.0, tube=0.020, mat=mat_outer)

# Bearing ticks every 30deg
for i in range(12):
    angle = math.radians(i*30); r_mid = 3.865
    make_bar(f"tick_{i*30}", length=0.26, width=0.022, rz=angle,
             cx=math.cos(angle)*r_mid, cy=math.sin(angle)*r_mid, z=0.001, mat=mat_tick)

# Radial spokes every 45deg
for i in range(8):
    make_bar(f"spoke_{i*45}", length=8.0, width=0.005,
             rz=math.radians(i*45), cx=0, cy=0, z=0.0, mat=mat_grid)

# Centre dot
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, segments=16, ring_count=10, location=(0,0,0))
bpy.context.active_object.name = "scope_centre"
bpy.context.active_object.data.materials.append(mat_ctr)

# Sample blips (will be replaced by GeoNodes in Stage 2)
for idx, pos in enumerate([(1.4,2.1,0),(-2.3,0.8,0),(3.1,-1.0,0),(-0.5,3.4,0),(2.5,2.5,0),(-1.8,-2.2,0)]):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, segments=8, ring_count=6, location=pos)
    b = bpy.context.active_object; b.name = f"blip_{idx:02d}"
    b.data.materials.append(mat_blip)

# Camera top-down
bpy.ops.object.camera_add(location=(0,0,8))
cam = bpy.context.active_object; cam.name = "Cam_TopDown"
cam.rotation_euler = (0,0,0); cam.data.type = 'PERSP'; cam.data.lens = 35
bpy.context.scene.camera = cam

# Render settings
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920; scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.frame_start = 1; scene.frame_end = 1
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = '/home/lovestaco/pers/lr_demo/blender_stuff_lr/render.png'

# Compositor: Bloom
scene.use_nodes = True
ng = bpy.data.node_groups.new("Compositor", 'CompositorNodeTree')
ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
scene.compositing_node_group = ng
rl    = ng.nodes.new('CompositorNodeRLayers')
glare = ng.nodes.new('CompositorNodeGlare')
out   = ng.nodes.new('NodeGroupOutput')
glare.inputs['Type'].default_value      = 'Bloom'
glare.inputs['Threshold'].default_value = 0.3
glare.inputs['Size'].default_value      = 8.0
glare.inputs['Strength'].default_value  = 0.6
glare.inputs['Saturation'].default_value= 1.0
ng.links.new(rl.outputs['Image'],    glare.inputs['Image'])
ng.links.new(glare.outputs['Image'], out.inputs['Image'])

print(f"build_scope.py OK: {len(bpy.data.objects)} objects, engine={scene.render.engine}")
