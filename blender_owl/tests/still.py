import bpy, sys, math
from mathutils import Vector
sc=bpy.context.scene
cam=bpy.data.objects['Cam']; tgt=bpy.data.objects['CamTarget']
sc.render.resolution_percentage=50
def shot(name, camloc, tloc):
    cam.location=camloc; tgt.location=tloc
    sc.render.filepath=f"//tests/{name}.png"
    bpy.ops.render.render(write_still=True)
#shot("wide",(0,-24,5),(0,4,3.0))
shot("close",(2.5,-8,3.0),(0,0,1.9))
rig=bpy.data.objects['OwlRig']; pb=rig.pose.bones
pb['wing_L'].rotation_euler.z=1.57   # should point to screen right
pb['wing_R'].rotation_euler.z=-2.6  # wave up on screen left
pb['jaw'].rotation_euler.x=0.5
pb['brow_L'].rotation_euler.z=0.35; pb['brow_R'].rotation_euler.z=-0.35
pb['pupil_L'].location.x=-0.09; pb['pupil_R'].location.x=-0.09
pb['body'].scale=(1.15,0.8,1.15)
pb['body'].rotation_euler.y=-0.3
shot("pose",(0,-9,2.8),(0,0,1.7))
pb['body'].scale=(1,1,1); pb['body'].rotation_euler.y=0
shot("mouth",(0.6,-5.5,2.2),(0,0,1.8))
