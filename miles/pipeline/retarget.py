"""Retarget BVH mocap (e.g. CMU) onto the Mixamo rig as a regular action.

    from pipeline import retarget
    act = retarget.bvh_to_action("02_01.bvh", rig, "CMU 02_01 walk")

Method, per frame and per mapped bone (all in world space):
    target = Ys·S(f) · (Yr·S0)⁻¹ · A⁻¹ · T0
S(f)/S0 are source pose/rest rotations, T0 the target rest rotation, Yr turns the
source rest to face like the target, Ys turns the clip to start facing the camera
(-Y), and A rotates the (yaw-corrected) source rest bone direction onto the target
rest bone direction. So every target bone points exactly where its source bone
points even though the two rest poses differ (e.g. T-pose vs Mixamo bind), and
twist comes from the source motion. Hips travel is scaled by hip height, so feet
land roughly on the floor; unmapped bones (fingers) stay at rest.
"""
import bpy, math
from mathutils import Matrix, Quaternion, Vector

# CMU / cgspeed BVH joint -> Mixamo bone (without the "mixamorig:" prefix)
CMU_TO_MIXAMO = {
    "Hips": "Hips",
    "LowerBack": "Spine", "Spine": "Spine1", "Spine1": "Spine2", "Neck": "Neck", "Head": "Head",
    "LeftShoulder": "LeftShoulder", "LeftArm": "LeftArm", "LeftForeArm": "LeftForeArm", "LeftHand": "LeftHand",
    "RightShoulder": "RightShoulder", "RightArm": "RightArm", "RightForeArm": "RightForeArm", "RightHand": "RightHand",
    "LeftUpLeg": "LeftUpLeg", "LeftLeg": "LeftLeg", "LeftFoot": "LeftFoot", "LeftToeBase": "LeftToeBase",
    "RightUpLeg": "RightUpLeg", "RightLeg": "RightLeg", "RightFoot": "RightFoot", "RightToeBase": "RightToeBase",
}
PREFIX = "mixamorig:"


# Mocap clavicles hike the shoulders up (5-8 cm over rest on Miles); keep only this share of
# the clavicle rotation. Arms are solved in world space, so arm directions are unaffected.
CLAVICLE_KEEP = 0.25
CLAVICLES = (PREFIX + "LeftShoulder", PREFIX + "RightShoulder")


def _yaw_to(vec, target=Vector((1, 0, 0))):
    """Rotation about Z turning the horizontal part of vec onto target."""
    a = math.atan2(vec.y, vec.x)
    b = math.atan2(target.y, target.x)
    return Matrix.Rotation(b - a, 3, "Z")


def import_bvh(path, fps=30):
    before = set(bpy.data.objects)
    bpy.ops.import_anim.bvh(filepath=path, axis_forward="-Z", axis_up="Y", rotate_mode="NATIVE",
                            use_fps_scale=True, update_scene_fps=False, update_scene_duration=False,
                            use_cyclic=False, global_scale=1.0)
    src = next(o for o in bpy.data.objects if o not in before and o.type == "ARMATURE")
    return src


MIXAMO_SELF = {k: k for k in CMU_TO_MIXAMO.values()} | {"Spine": "Spine", "Spine1": "Spine1", "Spine2": "Spine2"}


def import_fbx(path):
    """A Mixamo FBX (any character): armature with the 'mixamorig*:' prefix stripped from bone names."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path, automatic_bone_orientation=False)
    new = [o for o in bpy.data.objects if o not in before]
    src = next(o for o in new if o.type == "ARMATURE")
    for o in new:
        if o is not src and o.type == "MESH":
            bpy.data.objects.remove(o, do_unlink=True)
    for b in src.data.bones:
        b.name = b.name.split(":")[-1]           # renames the action's channels too
    return src


def fbx_to_action(path, rig, name, trim=None):
    """Mixamo clip downloaded on another character -> action on our rig (same solver as the mocap)."""
    return bvh_to_action(path, rig, name, mapping=MIXAMO_SELF, trim=trim, source="fbx")


def bvh_to_action(path, rig, name, mapping=CMU_TO_MIXAMO, trim=None, source="bvh"):
    sc = bpy.context.scene
    src = import_bvh(path) if source == "bvh" else import_fbx(path)
    act_src = src.animation_data.action
    f0, f1 = (int(math.ceil(act_src.frame_range[0])), int(act_src.frame_range[1]))
    if source == "bvh":
        f0 += 1                      # CMU/cgspeed files start with a T-pose calibration frame
    if trim:
        f0, f1 = max(f0, trim[0]), min(f1, trim[1])
    pairs = [(s, PREFIX + t) for s, t in mapping.items()
             if s in src.data.bones and PREFIX + t in rig.data.bones]

    src_mw3, tgt_mw3 = src.matrix_world.to_3x3(), rig.matrix_world.to_3x3()
    sb, tb = src.data.bones, rig.data.bones
    # rest facing: source lateral (right->left hip) to target lateral
    lat = lambda bones, mw, l, r: (mw @ bones[l].head_local) - (mw @ bones[r].head_local)
    Yr = _yaw_to(lat(sb, src.matrix_world, "LeftUpLeg", "RightUpLeg"),
                 lat(tb, rig.matrix_world, PREFIX + "LeftUpLeg", PREFIX + "RightUpLeg"))
    S0 = {s: Yr @ src_mw3 @ sb[s].matrix_local.to_3x3() for s, _ in pairs}
    T0 = {t: tgt_mw3 @ tb[t].matrix_local.to_3x3() for _, t in pairs}
    A_inv = {}
    for s, t in pairs:
        ds = (Yr @ src_mw3 @ sb[s].matrix_local.to_3x3() @ Vector((0, 1, 0))).normalized()
        dt = (T0[t] @ Vector((0, 1, 0))).normalized()
        A_inv[s] = ds.rotation_difference(dt).to_matrix().inverted()
    tgt_hip_h = (rig.matrix_world @ tb[PREFIX + "Hips"].head_local).z

    # sample the source
    frames = list(range(f0, f1 + 1))
    S, H, floor = [], [], 1e9
    feet = [b for b in ("LeftToeBase", "RightToeBase", "LeftFoot", "RightFoot") if b in sb]
    for f in frames:
        sc.frame_set(f)
        pose = {s: src.matrix_world @ src.pose.bones[s].matrix for s, _ in pairs}
        floor = min([floor] + [(src.matrix_world @ src.pose.bones[b].head).z for b in feet])
        S.append({s: Yr @ m.to_3x3() for s, m in pose.items()})
        H.append(Yr @ pose["Hips"].translation)
        if f == f0:
            l = Yr @ (src.matrix_world @ src.pose.bones["LeftUpLeg"].head)
            r = Yr @ (src.matrix_world @ src.pose.bones["RightUpLeg"].head)
            Ys = _yaw_to(l - r)          # start facing -Y (left hip towards +X)
    origin = Vector((H[0].x, H[0].y, 0))
    # BVH rest puts the hips at the origin, so measure hip height above the clip's lowest foot
    scale = tgt_hip_h / max(1e-6, H[0].z - floor)

    # solve target pose per frame (parents before children)
    order = [b.name for b in rig.data.bones]     # Blender lists parents first
    mapped = {t: s for s, t in pairs}
    inv_tgt = rig.matrix_world.inverted().to_3x3()
    rows = {b: [] for b in order}
    hip_loc = []
    for i, f in enumerate(frames):
        arm = {}
        for bname in order:
            bone = tb[bname]
            rest = bone.matrix_local.to_3x3()
            if bname in mapped:
                s = mapped[bname]
                world = Ys @ S[i][s] @ S0[s].inverted() @ A_inv[s] @ T0[bname]
                arm_rot = inv_tgt @ world
            else:
                arm_rot = None
            if bone.parent:
                prest = bone.parent.matrix_local.to_3x3()
                rest_rel = prest.inverted() @ rest
                parent_arm = arm[bone.parent.name]
                if arm_rot is None:
                    arm_rot = parent_arm @ rest_rel
                basis = (parent_arm @ rest_rel).inverted() @ arm_rot
                if bname in CLAVICLES:
                    basis = Quaternion().slerp(basis.to_quaternion(), CLAVICLE_KEEP).to_matrix()
                    arm_rot = parent_arm @ rest_rel @ basis
            else:
                if arm_rot is None:
                    arm_rot = rest
                basis = rest.inverted() @ arm_rot
            arm[bname] = arm_rot
            rows[bname].append(basis.to_quaternion())
        # hips travel
        p = Ys @ (H[i] - origin)
        world_pos = Vector((p.x * scale, p.y * scale, (H[i].z - floor) * scale))
        hb = tb[PREFIX + "Hips"]
        arm_pos = rig.matrix_world.inverted() @ world_pos
        hip_loc.append(hb.matrix_local.to_3x3().inverted() @ (arm_pos - hb.head_local))

    # write the action directly (fast) with continuous quaternions
    act = bpy.data.actions.get(name) or bpy.data.actions.new(name)
    for layer in list(act.layers):
        act.layers.remove(layer)
    for slot in list(act.slots):
        act.slots.remove(slot)
    slot = act.slots.new(id_type="OBJECT", name=rig.name)
    strip = act.layers.new("Layer").strips.new(type="KEYFRAME")
    cb = strip.channelbag(slot, ensure=True)

    def curve(path, idx, values, interp=None):
        fc = cb.fcurves.new(path, index=idx)
        fc.keyframe_points.add(len(values))
        co = []
        for k, v in enumerate(values):
            co += [k + 1, v]
        fc.keyframe_points.foreach_set("co", co)
        fc.keyframe_points.foreach_set("interpolation", interp or [1] * len(values))   # LINEAR (dense samples)
        fc.update()

    for bname in order:
        qs, prev = [], None
        for q in rows[bname]:
            if prev is not None and prev.dot(q) < 0:
                q = -q
            qs.append(q)
            prev = q
        if all(abs(q.w - 1) < 1e-5 for q in qs):
            continue                       # untouched bone
        # Keep every key in the w >= 0 hemisphere so NLA crossfades (which mix quaternion channels
        # linearly) never take the long way round — a clip that spins >180° (cartwheel) otherwise
        # ends on -q and the blend into the next clip whips the body through a full turn. Where the
        # sign flips (same rotation, other hemisphere) the key is CONSTANT, so no in-between is drawn.
        sign = [1 if q.w >= 0 else -1 for q in qs]
        qs = [q * sg for q, sg in zip(qs, sign)]
        interp = [0 if k + 1 < len(qs) and sign[k] != sign[k + 1] else 1 for k in range(len(qs))]
        path = f'pose.bones["{bname}"].rotation_quaternion'
        for c in range(4):
            curve(path, c, [q[c] for q in qs], interp)
    hpath = f'pose.bones["{PREFIX}Hips"].location'
    for c in range(3):
        curve(hpath, c, [v[c] for v in hip_loc])
    act.use_fake_user = True

    # clean up the imported source
    data = src.data
    bpy.data.objects.remove(src)
    bpy.data.armatures.remove(data)
    bpy.data.actions.remove(act_src)
    return act
