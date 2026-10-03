"""Build build/character.blend: masked Miles on the Mixamo skeleton + every Mixamo clip as an action.

    blender -b --factory-startup --python scripts/02_build_character.py

- Base character: "Hanging Idle.fbx" (downloaded with skin) -> armature "MilesRig".
- Masked look: the masked T-pose suit (root.002 in miles.blend) is aligned to the
  Mixamo bind pose and gets Mixamo's skin weights by nearest-surface interpolation.
  The unmasked Mixamo mesh is kept, hidden, as "MilesUnmasked".
- Every other FBX in blender_assets_downloaded/ becomes an action named after the
  file (fake user, so it survives saving).
"""
import bpy, bmesh, os, glob, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import paths
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

DL = paths.MIXAMO_CLIPS
SRC = paths.SOURCE_BLEND
OUT = paths.CHARACTER_BLEND

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ---------------------------------------------------------------- base rig
bpy.ops.import_scene.fbx(filepath=os.path.join(DL, paths.MIXAMO_BASE_CLIP + ".fbx"))
rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
unmasked = next(o for o in bpy.data.objects if o.type == "MESH")
rig.name, rig.data.name = "MilesRig", "MilesRig"
unmasked.name = "MilesUnmasked"
base_action = rig.animation_data.action
base_action.name = paths.MIXAMO_BASE_CLIP
base_action.use_fake_user = True

# ------------------------------------------------- masked suit from miles.blend
with bpy.data.libraries.load(SRC, link=False) as (src, dst):
    dst.objects = [n for n in src.objects if n in (
        "root.002", "40_Suit_1_0_0.002",            # masked, T-pose
        "root.003", "40_Suit_1_0_0.003",            # unmasked, T-pose (for alignment)
        "40_-Mask.material01.Mask.material01_1_0_0.003", "40_-Mask.material01.Mask.material01_1_0_0.004",
        "40_-Mask.material01.Mask.material01_1_0_0.005", "40_-Mask.material01.Mask.material01_1_0_0.007",
        "40_-Mask.material03.Mask.material03_1_0_0.001")]
tmp = bpy.data.collections.new("tmp")
sc.collection.children.link(tmp)
for o in dst.objects:
    tmp.objects.link(o)
    if o.type == "ARMATURE":
        o.data.pose_position = "REST"   # ignore any posing done in miles.blend
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()


def baked_verts(o):
    me = o.evaluated_get(dg).to_mesh()
    vs = [o.matrix_world @ v.co for v in me.vertices]
    o.evaluated_get(dg).to_mesh_clear()
    return vs


# same centring as export_for_mixamo.py (computed on the unmasked T-pose parts)
un_parts = [o for o in dst.objects if o.type == "MESH" and o.name != "40_Suit_1_0_0.002"]
pts = [v for o in un_parts for v in baked_verts(o)]
T = Matrix.Translation((-(min(p.x for p in pts) + max(p.x for p in pts)) / 2,
                        -(min(p.y for p in pts) + max(p.y for p in pts)) / 2,
                        -min(p.z for p in pts)))
# map masked-rig space onto unmasked-rig space (both share the same rest T-pose),
# so it doesn't matter where either rig was moved/rotated in miles.blend
shift = bpy.data.objects["root.003"].matrix_world @ bpy.data.objects["root.002"].matrix_world.inverted()

suit_src = bpy.data.objects["40_Suit_1_0_0.002"]
me = bpy.data.meshes.new_from_object(suit_src.evaluated_get(dg))
me.transform(T @ shift @ suit_src.matrix_world)
masked = bpy.data.objects.new("MilesMasked", me)
sc.collection.objects.link(masked)
for o in list(tmp.objects):
    bpy.data.objects.remove(o)
bpy.data.collections.remove(tmp)

# ------------------------------------------- transfer Mixamo weights (rest pose)
rig.data.pose_position = "REST"
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
src_eval = unmasked.evaluated_get(dg)
src_me = src_eval.to_mesh()
mw = unmasked.matrix_world
bm = bmesh.new()
bm.from_mesh(src_me)
bm.transform(mw)
bmesh.ops.triangulate(bm, faces=bm.faces)
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()
bvh = BVHTree.FromBMesh(bm)
# source weights per vertex: {group_name: w}
names = [g.name for g in unmasked.vertex_groups]
src_w = [{names[g.group]: g.weight for g in v.groups if g.weight > 1e-4} for v in unmasked.data.vertices]
groups = {n: masked.vertex_groups.new(name=n) for n in names}
far = 0
for v in masked.data.vertices:
    loc, nrm, fi, dist = bvh.find_nearest(v.co)
    if fi is None:
        continue
    far += dist > 0.05
    tri = bm.faces[fi].verts
    a, b, c = (t.co for t in tri)
    # barycentric weights of loc inside triangle
    bc = barycentric_transform(loc, a, b, c, Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))
    acc = {}
    for wgt, tv in zip(bc, tri):
        for n, w in src_w[tv.index].items():
            acc[n] = acc.get(n, 0.0) + max(0.0, wgt) * w
    tot = sum(acc.values()) or 1.0
    for n, w in acc.items():
        if w / tot > 0.002:
            groups[n].add([v.index], w / tot, "REPLACE")
bm.free()
src_eval.to_mesh_clear()
print(f"weights transferred to {len(masked.data.vertices)} verts ({far} farther than 5cm)")

masked.parent = rig
masked.matrix_parent_inverse = rig.matrix_world.inverted()
mod = masked.modifiers.new("Armature", "ARMATURE")
mod.object = rig
rig.data.pose_position = "POSE"
unmasked.hide_set(True)
unmasked.hide_render = True

# ------------------------------------------------------------ import actions
before_actions = set(bpy.data.actions)
for f in sorted(glob.glob(os.path.join(DL, "*.fbx"))):
    name = os.path.splitext(os.path.basename(f))[0]
    if name == paths.MIXAMO_BASE_CLIP:
        continue
    existing = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=f)
    new_objs = [o for o in bpy.data.objects if o not in existing]
    arm = next((o for o in new_objs if o.type == "ARMATURE"), None)
    if arm and arm.animation_data and arm.animation_data.action:
        act = arm.animation_data.action
        act.name = name
        act.use_fake_user = True
    for o in new_objs:
        data = o.data
        bpy.data.objects.remove(o)
        if data is not None and data.users == 0:
            if isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)
            elif isinstance(data, bpy.types.Armature):
                bpy.data.armatures.remove(data)
for m in list(bpy.data.materials):
    if m.users == 0:
        bpy.data.materials.remove(m)

rig.animation_data.action = base_action
rig.animation_data.action_slot = base_action.slots[0]
acts = sorted(a.name for a in bpy.data.actions)
print("ACTIONS", len(acts))
sc.render.fps = 30
sc.frame_end = int(base_action.frame_range[1])
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", OUT)
