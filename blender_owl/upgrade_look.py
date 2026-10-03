"""Quick realism pass on owl_demo.blend -> owl_demo_hq.blend.

    blender -b owl_demo.blend --python upgrade_look.py [-- test]
"""
import bpy, os, sys, math
ROOT = os.path.dirname(os.path.abspath(__file__))
sc = bpy.context.scene


def bsdf(m):
    return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def add_bump(m, scale, strength, detail=6.0, coord="Object"):
    nt = m.node_tree
    b = bsdf(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = detail
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = strength
    nt.links.new(tc.outputs[coord], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return nz


def set_in(b, name, v):
    if name in b.inputs:
        b.inputs[name].default_value = v


# --- HDRI sky (Poly Haven, kloofendal partly cloudy) ---------------------
w = sc.world
nt = w.node_tree
for n in list(nt.nodes):
    if n.type not in ("OUTPUT_WORLD",):
        nt.nodes.remove(n)
out = next(n for n in nt.nodes if n.type == "OUTPUT_WORLD")
env = nt.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(os.path.join(ROOT, "hdri", "sky.hdr"), check_existing=True)
tc = nt.nodes.new("ShaderNodeTexCoord")
mp = nt.nodes.new("ShaderNodeMapping")
mp.inputs["Rotation"].default_value = (0, 0, math.radians(200))
bg = nt.nodes.new("ShaderNodeBackground")
bg.inputs["Strength"].default_value = 1.0
nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
nt.links.new(env.outputs["Color"], bg.inputs["Color"])
nt.links.new(bg.outputs[0], out.inputs["Surface"])

sun = bpy.data.objects["Sun"]
sun.data.energy = 4.5
sun.data.angle = math.radians(2.5)
sun.data.color = (1.0, 0.93, 0.82)

# --- owl: plush / felt look ----------------------------------------------
for name in ("Owl_Body", "Owl_Feather", "Owl_FaceDisc", "Owl_Belly"):
    m = bpy.data.materials[name]
    b = bsdf(m)
    b.inputs["Roughness"].default_value = 0.85
    set_in(b, "Sheen Weight", 0.6)
    set_in(b, "Sheen Roughness", 0.35)
    set_in(b, "Sheen Tint", (1.0, 0.92, 0.8, 1))
    set_in(b, "Subsurface Weight", 0.08)
    add_bump(m, 180.0, 0.18, 2.0)
for name in ("Owl_Pupil", "Owl_Sclera"):
    b = bsdf(bpy.data.materials[name])
    b.inputs["Roughness"].default_value = 0.05
    set_in(b, "Coat Weight", 1.0)
b = bsdf(bpy.data.materials["Owl_Beak"])
b.inputs["Roughness"].default_value = 0.3
set_in(b, "Coat Weight", 0.4)
# smoother owl silhouette
body = bpy.data.objects["Owl_Body"] if "Owl_Body" in bpy.data.objects else bpy.data.objects["Body"]
body.modifiers["Bevel"].segments = 6

# --- street surfaces: wear + bump ------------------------------------------
add_bump(bpy.data.materials["Street_Paving"], 3.0, 0.25)
_br = next(n for n in bpy.data.materials["Street_Paving"].node_tree.nodes if n.type == "TEX_BRICK")
_br.inputs["Color1"].default_value = (0.50, 0.48, 0.45, 1)
_br.inputs["Color2"].default_value = (0.42, 0.40, 0.37, 1)
_br.inputs["Mortar"].default_value = (0.28, 0.27, 0.25, 1)
add_bump(bpy.data.materials["Street_Asphalt"], 40.0, 0.35)
bsdf(bpy.data.materials["Street_Asphalt"]).inputs["Roughness"].default_value = 0.75
for m in bpy.data.materials:
    if m.name.startswith("Street_Facade"):
        add_bump(m, 6.0, 0.12)
        bsdf(m).inputs["Roughness"].default_value = 0.9
for name in ("Street_Glass", "Street_Teal", "Street_Red", "Street_Yellow", "Street_Blue"):
    b = bsdf(bpy.data.materials[name])
    set_in(b, "Coat Weight", 0.8)
bsdf(bpy.data.materials["Street_Glass"]).inputs["Roughness"].default_value = 0.02
bsdf(bpy.data.materials["Street_Glass"]).inputs["Metallic"].default_value = 0.6

# --- render: raytraced EEVEE, motion blur, filmic grade --------------------
ee = sc.eevee
ee.taa_render_samples = 16
ee.use_raytracing = True
try:
    ee.ray_tracing_method = "SCREEN"
except Exception:
    pass
ee.use_shadows = True
ee.shadow_ray_count = 2
ee.shadow_step_count = 8
for attr, v in (("use_fast_gi", True), ("fast_gi_distance", 6.0)):
    if hasattr(ee, attr):
        setattr(ee, attr, v)
if hasattr(ee.ray_tracing_options, "resolution_scale"):
    ee.ray_tracing_options.resolution_scale = "2"
sc.render.use_motion_blur = True
sc.render.motion_blur_shutter = 0.5
try:
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "Medium High Contrast"
    sc.view_settings.exposure = -0.9
except TypeError:
    sc.view_settings.view_transform = "Standard"
cam = bpy.data.objects["Cam"]
cam.data.dof.aperture_fstop = 2.8

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "owl_demo_hq.blend"))
if "test" in sys.argv:
    import time
    for f in (250,):
        sc.frame_set(f)
        sc.render.filepath = os.path.join(ROOT, "tests", f"hq_{f}.png")
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print("FRAME", f, round(time.time() - t, 2), "s")
