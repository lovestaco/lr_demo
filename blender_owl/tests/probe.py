import bpy
sc=bpy.context.scene; rig=bpy.data.objects['OwlRig']; pb=rig.pose.bones
for f in (26,28,29,30,31,32,34,40):
    sc.frame_set(f)
    print(f, "obj", tuple(round(v,2) for v in rig.location), "root", tuple(round(v,2) for v in pb['root'].location), tuple(round(v,2) for v in pb['root'].scale), "body scl", tuple(round(v,2) for v in pb['body'].scale), "spin", tuple(round(v,2) for v in pb['spin'].rotation_euler))
