"""Goal-1 demo: the owl performs its action vocabulary on the street.

    blender -b owl_street.blend --python demo_street.py            # build + save owl_demo.blend
    blender -b owl_street.blend --python demo_street.py -- render  # ...and render frames/

Also runnable inside a live Blender session (MCP / Text Editor).
"""
import bpy, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else "/home/lovestaco/pers/lr_demo/blender_owl"
sys.path.insert(0, ROOT)
import importlib, owl_lib
importlib.reload(owl_lib)

scene = bpy.context.scene
scene.timeline_markers.clear()
for ob in ("Cam", "CamTarget"):
    bpy.data.objects[ob].animation_data_clear()

owl = owl_lib.Owl().reset()
cam = owl_lib.Cam(owl)

# 1. empty street -> owl drops from the sky
owl.place(-3, facing="camera")
cam.shot("wide", at=1, subject=(0, 0, 0))
owl.wait(14)
owl.mark("drop")
owl.fall(from_height=16)
cam.shake(owl.last_impact, amp=0.35, dur=12)
owl.wait(4)

# 2. looks around, notices the camera
owl.mark("look")
owl.look("left", dur=12)
owl.look("right", dur=14)
cam.shot("medium", at=owl.t, dur=16)
owl.look("camera", dur=8)
owl.blink()

# 3. waves and says hi
owl.mark("hi")
owl.wave(times=3, advance=False)
owl.express("happy", dur=6, advance=False)
owl.talk("Hi! I'm Livi.", at=owl.t + 6)
owl.neutral(dur=6)
owl.wait(4)

# 4. walks right, skids to a stop, hops
cam.shot("wide", at=owl.t)
owl.mark("walk")
w0 = owl.t
owl.walk_to(6, speed=6)
owl.skid(dist=2.5)
cam.follow(w0, owl.t, step=6)
owl.turn("camera")
owl.hop(2, height=1.1)

# 5. surprised -> big jump left
cam.shot("full", at=owl.t)
owl.mark("surprised")
owl.surprised(hold=12)
owl.jump(dx=-6, height=4.0)

# 6. cartwheel back to the right
cam.shot("wide", at=owl.t, subject=(owl.pos().x + 4, 0, 0))
owl.mark("cartwheel")
owl.cartwheel(8)
owl.wait(4)

# 7. thinking, confused, nod / shake
cam.shot("close", at=owl.t)
owl.mark("think")
owl.thinking(hold=36)
owl.confused(hold=16)
owl.shake_head(3)
owl.wait(4)
owl.express("happy", dur=6, advance=False)
owl.nod(2)
owl.neutral()

# 8. point at the shops, excited, flip
cam.shot("full", at=owl.t, dur=10)
owl.mark("point")
owl.point("up-right", hold=20)
owl.talk("Look over there!", at=owl.t - 26, advance=False)
owl.excited(hops=2)
owl.flip(height=4.5)

# 9. exit right
cam.shot("wide", at=owl.t)
owl.mark("exit")
owl.wave(times=2)
owl.exit_right()
owl.finish(tail=12)

print("DEMO frames", scene.frame_start, "->", scene.frame_end, f"({(scene.frame_end) / 24:.1f}s)")
for m in sorted(scene.timeline_markers, key=lambda m: m.frame):
    print("  marker", m.frame, m.name)

if bpy.app.background:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "owl_demo.blend"))
    if "render" in sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []:
        scene.render.filepath = os.path.join(ROOT, "frames", "f_")
        scene.render.image_settings.file_format = "PNG"
        bpy.ops.render.render(animation=True)
