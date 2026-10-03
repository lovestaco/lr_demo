"""Export the unmasked T-pose Miles (armature root.003) as a single textured mesh FBX for Mixamo."""
import bpy, os
ROOT = os.path.dirname(bpy.data.filepath)
OUT = os.path.join(ROOT, "mixamo", "miles_for_mixamo.fbx")
arm = bpy.data.objects["root.003"]
parts = [o for o in bpy.data.objects if o.type == "MESH" and
         any(m.type == "ARMATURE" and m.object == arm for m in o.modifiers)]
print("parts:", [p.name for p in parts])
dg = bpy.context.evaluated_depsgraph_get()
new = []
for o in parts:
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))   # bakes current (T-)pose
    me.transform(o.matrix_world)
    ob = bpy.data.objects.new("Miles_" + o.name[-6:], me)
    bpy.context.scene.collection.objects.link(ob)
    new.append(ob)
for o in list(bpy.data.objects):
    if o not in new:
        bpy.data.objects.remove(o)
bpy.ops.object.select_all(action="DESELECT")
for o in new:
    o.select_set(True)
bpy.context.view_layer.objects.active = new[0]
bpy.ops.object.join()
miles = bpy.context.view_layer.objects.active
miles.name = "Miles"
# centre on origin, feet on the floor
xs = [v.co.x for v in miles.data.vertices]; ys = [v.co.y for v in miles.data.vertices]
zmin = min(v.co.z for v in miles.data.vertices)
from mathutils import Matrix
miles.data.transform(Matrix.Translation((-(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2, -zmin)))
dims = miles.dimensions
print("faces", len(miles.data.polygons), "verts", len(miles.data.vertices), "dims", tuple(round(d, 2) for d in dims))
for img in bpy.data.images:
    if img.source == "FILE" and not img.packed_file and os.path.exists(bpy.path.abspath(img.filepath)):
        img.pack()
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, object_types={"MESH"},
                         path_mode="COPY", embed_textures=True, apply_unit_scale=True,
                         apply_scale_options="FBX_SCALE_ALL", mesh_smooth_type="FACE")
print("EXPORTED", OUT, os.path.getsize(OUT) // 1024, "KB")
