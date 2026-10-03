import bpy
sc=bpy.context.scene; sc.render.resolution_percentage=40; sc.eevee.taa_render_samples=8
import sys
frames=[int(x) for x in sys.argv[sys.argv.index('--')+1].split(',')]
for f in frames:
    sc.frame_set(f); sc.render.filepath=f"//tests/sheet/f{f:04d}.png"; bpy.ops.render.render(write_still=True)
