import bpy, math
sc=bpy.context.scene; rig=bpy.data.objects['OwlRig']; pb=rig.pose.bones
for f in range(640,720,6):
    sc.frame_set(f)
    print(f, "x", round(rig.location.x,2), "head", round(math.degrees(rig.rotation_euler.z),1), "bodyyaw", round(math.degrees(pb['body'].rotation_euler.y),1),"spin",[round(math.degrees(a)) for a in pb['spin'].rotation_euler])
