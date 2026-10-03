import bpy, os
ROOT = os.path.dirname(os.path.abspath(bpy.data.filepath))
sc = bpy.context.scene
end = sc.frame_end
# traffic: two cars drive through the background
def drive(name, x0, x1, y, rotz):
    ob = bpy.data.objects[name]
    ob.rotation_euler.z = rotz
    ob.location = (x0, y, -0.35); ob.keyframe_insert("location", frame=1)
    ob.location = (x1, y, -0.35); ob.keyframe_insert("location", frame=end)
    for layer in ob.animation_data.action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fc in cb.fcurves:
                    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
drive("CarTeal", -110, 160, 9.0, 0.0)
drive("CarYellow", 120, -150, 17.5, 3.14159)
# compositor bloom (Blender 5.2 API)
try:
    ng = bpy.data.node_groups.new("Compositor", 'CompositorNodeTree')
    sc.compositing_node_group = ng
    rl = ng.nodes.new('CompositorNodeRLayers')
    gl = ng.nodes.new('CompositorNodeGlare')
    gl.inputs['Type'].default_value = 'Bloom'
    gl.inputs['Threshold'].default_value = 0.8
    gl.inputs['Size'].default_value = 6.0
    gl.inputs['Strength'].default_value = 0.35
    ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    out = ng.nodes.new('NodeGroupOutput')
    ng.links.new(rl.outputs['Image'], gl.inputs['Image'])
    ng.links.new(gl.outputs[0], out.inputs[0])
    print("BLOOM OK")
except Exception as e:
    print("BLOOM SKIP", e)
sc.render.resolution_percentage = 67   # 1286x723 -> 1280x720-ish
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.eevee.taa_render_samples = 12
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "owl_demo_hq2.blend"))
sc.frame_set(150); sc.render.filepath = os.path.join(ROOT, "tests", "hq2_150.png")
import time; t=time.time(); bpy.ops.render.render(write_still=True); print("FRAME", round(time.time()-t,2))
sc.frame_set(151); t=time.time(); bpy.ops.render.render(write_still=True); print("FRAME", round(time.time()-t,2))
