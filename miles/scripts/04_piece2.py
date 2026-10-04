"""Piece 2 (~90s): Hook → Problem → Bridges → Customers leave → Bridge → Thesis tower.

    S1 Hook       drops in on a web, glances at his watch, webs LCD1 in (one yank), taps it on, shrugs
    S2 Problem    cartwheel to LCD2: "velocity" → he sprints past the screen → paper avalanche →
                  system graph; on "bugs" spiders crawl out of the screen at him → SHOCK
    S3 Bridges    review queue overflows → "human attention is still limited" (yawn)
    S4 Customers  "production risk" → 4 risk tiles pop on the spoken words → customers walk away (WORRY)
    S5 Bridge     "How do you stay competitive?" → "You need a better inspection layer."
    S6 Tower      cartwheels to open stage, webs down INSPECTION → ENGINEERS' → CUSTOMER → PRODUCT + cash,
                  yanks INSPECTION out → tower collapses, cash rains; ends on Miles, hands on head, crying

Timing is driven by the chosen voice take (assets/audio/vo_piece2/lines.json, incl. word times).
No magic: everything arrives by web-pull, walking or cartwheeling. Camera stays locked while a
screen is up; it only moves on Miles in screen-free stretches.

    python3 scripts/03b_make_screens.py
    blender -b build/character.blend --python scripts/04_piece2.py      # -> build/piece2.blend
"""
import bpy, os, sys, math, random, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mathutils import Vector
from pipeline import paths, anim, fx, shot, props
from pipeline.mixamo import Performer, ClipGroup
from pipeline.shot import L_HAND, R_HAND, HIPS

FPS = 30
sc = bpy.context.scene
SCR = os.path.join(paths.ROOT, "assets", "screens")
scr = lambda n: os.path.join(SCR, n + ".png")
seq = lambda n, length, start: ("seq", os.path.join(SCR, n, "f_0001.png"), length, int(start))

VO = json.load(open(os.path.join(paths.ROOT, "assets", "audio", "vo_piece2", "lines.json")))
dur = lambda n: VO[str(n)]["duration"]
hold = lambda n, extra=0.45, at_least=0: int(round(max(at_least, (dur(n) + extra) * FPS)))       # frames
F = lambda x: int(round(x))
word = lambda n, w: next(t for x, t in VO[str(n)]["words"] if x == w)                         # seconds into line n

rig = shot.stage(theme="dark", subject=(-2.4, 0.0), physical=True)
office = props.Office(rig)
WALK, EXPLAIN = "Walking", "CMU 18_08 conversation - explain with hand gesture"
PRESENT = ["Talking (2)", "Talking (1)", EXPLAIN]      # calm presenter gestures (review: no frantic hands)

# ------------------------------------------------------------------ performance
perf = Performer(rig).place(x=-2.6, y=0.0, face=0)
hit_pk = perf.extreme("Standing 1H Magic Attack 02", R_HAND, (1, 0, 0), 16, 40)
up_pk = perf.extreme("Standing 2H Magic Attack 01", R_HAND, (0, 0, 1), 10, 60)
_turn = [0]


def talk(length, face=5, blend=10):
    """Presenter beat facing the viewer: calm Mixamo talking cycles / energy-capped CMU explain
    windows, held on the spot (in_place) so he stays next to the screen."""
    parts, left = [], int(length)
    while left > 8:
        clip = PRESENT[_turn[0] % len(PRESENT)]
        _turn[0] += 1
        a0, a1 = bpy.data.actions[clip].frame_range
        n = min(left + (blend if parts else 0), int(a1 - a0) - 2)
        frm = perf.lively(clip, n, target=1.5) if clip == EXPLAIN else a0 + 1
        parts.append(perf.then(clip, frm=frm, length=n, blend=blend, face=face, in_place=0.7))
        left -= n - (blend if len(parts) > 1 else 0)
    return parts[0] if len(parts) == 1 else ClipGroup(parts)



# S1 hook
hang = perf.then("Hanging Idle", length=40)
land = perf.then("Hard Landing", to=60, speed=1.2, blend=6)
idle1 = perf.then("Breathing Idle", length=48, blend=10)                             # watch check
shot1 = perf.then("Standing 1H Magic Attack 02", frm=16, to=40, speed=1.15, blend=6)
yank = perf.then("Pull Heavy Object Stop", to=30, speed=1.1, blend=5, face=65)
tap1 = perf.then("Breathing Idle", length=34, blend=8, face=70)                      # tap LCD1 on
talk1 = talk(hold(1, 1.0, 80))
shrug = perf.then("CMU 111_25 Shrug", blend=8, face=10)
talk2 = talk(hold(2, 0.8))
# S2 problem
cart = perf.then("CMU 49_06 cartwheel", frm=20, to=112, blend=10, face=90)
w4 = perf.then(WALK, blend=8, face=90)
tap2 = perf.then("Breathing Idle", length=30, blend=8, face=70)
vo3 = int(tap2.start) + 20                                                          # = t2_on + 8
SPRINT_AT = vo3 + F(word(3, "velocity") * FPS) - 6
pre = talk(SPRINT_AT + 6 - (int(tap2.end) - 8))
sprint = perf.then("Two Cycle Sprint", start=SPRINT_AT, frm=1, to=23, blend=6, face=90)   # "velocity!" dash past the screen
stop = perf.then("Run To Stop", blend=5, face=90)
vel = talk(45, face=-5)                                                             # screen now on his left
scared = perf.then("CMU 79_73 scared", frm=20, to=120, blend=8, face=5)              # paper avalanche
stuck = perf.then("Breathing Idle", length=40, blend=8, face=5)                      # watch check in the pile
w5 = perf.then(WALK, length=16, blend=8, face=-10)                                  # two steps out of the pile, towards camera
sysA = talk(150, face=-5)                                                           # graph grows, spiders come out
shock = perf.then("CMU 120_16 Mickey Surprised", frm=140, to=262, blend=6, face=30, in_place=0.8)  # bugs! (SHOCK)
# S3 bridges
rq = talk(max(150, hold(6, 1.5)), face=-5)                                          # review queue overflows
yawn = perf.then("CMU 111_32 Stretch and yawn", frm=10, to=150, blend=10, face=10)  # human attention
# S4 customers leave
risk = talk(hold(8, 0.8), face=-5)
worry = perf.then("CMU 79_71 sad", frm=20, to=20 + hold(9, 0.6) + 96, blend=10, face=5)   # tiles + walk-away
# S5 bridge
comp = talk(hold(10, 0.8), face=-5)
layer = talk(hold(11, 1.2), face=-5)
# S6 tower
cart2 = perf.then("CMU 49_06 cartwheel", frm=20, to=112, blend=10, face=90)
w6 = perf.then(WALK, blend=8, face=90)
UP = "Standing 2H Magic Attack 01"
# S6 runs on the voice: each block lands on its label word, the yank lands on "Without inspection",
# the cascade on "everything above"; lines keep the take's natural gaps (+0.3 s for the landings).
GAP = {12: 0.44, 13: 0.74, 14: 0.48, 15: 0.24, 16: 0.38}
LAND_WORD = {12: "inspection", 13: "engineers", 14: "customers", 15: "product"}
vo_s6 = {12: max(int(layer.start) + 6 + F(dur(11) * FPS) + 18, int(w6.end) + 6)}
for n in range(13, 18):
    vo_s6[n] = vo_s6[n - 1] + F((dur(n - 1) + GAP.get(n - 1, 0.4) + 0.3) * FPS)
UP_LEAD = F(14 / 1.15)                                       # clip start -> web hit
lands = [vo_s6[n] + F(word(n, LAND_WORD[n]) * FPS) for n in (12, 13, 14, 15)]
Y1 = vo_s6[16] + F(word(16, "inspection") * FPS)           # yank INSPECTION out
builds, starts = [], [ld - 12 - UP_LEAD for ld in lands] + [Y1 - 4]
for k, st in enumerate(starts[:4]):
    if k == 0:
        perf.then("Breathing Idle", length=max(8, st + 8 - (int(w6.end) - 8)), blend=8, face=20)
    builds.append(perf.then(UP, start=st, frm=up_pk - 14, to=up_pk + 20, speed=1.15, blend=8, face=25))
    nxt = starts[k + 1]
    perf.then("Breathing Idle", length=max(8, nxt + 8 - (int(builds[-1].end) - 8)), blend=8, face=20)
pull = perf.then("Pull Heavy Object Stop", start=Y1 - 4, to=30, speed=1.0, blend=8, face=75)  # yank INSPECTION out
fear = perf.then("CMU 79_72 crying", frm=18, to=170, blend=8, face=5)               # hands on head over the rubble
perf.build()

HANG_Z = 2.44 - 1.15
perf.root_z([(1, 5.0, "cubic_out"), (int(hang.start) + 30, HANG_Z, "lin"),
             (int(land.start), HANG_Z, "lin"), (int(land.start) + land.blend, 0.0, "lin")])
IMPACT = perf.clip_frame(land, 30)
SHOT_HIT = perf.clip_frame(shot1, hit_pk)
Y0 = int(yank.start)
END = max(int(fear.end), vo_s6[16] + F((dur(16) + 1.8) * FPS)) + 10
sc.frame_end = END
hips = lambda f: perf.bone_world(HIPS, int(f))

# ------------------------------------------------------------------ timeline (frames) derived from voice + clips
TVW, STAND = 2.6, 0.75
TVH = TVW * 9 / 16
TVZ = STAND + TVH / 2
t1_on = int(tap1.start) + 14
s2_at = int(shrug.start) + 16
t2_on = int(tap2.start) + 12                              # (vo3 = t2_on + 8)
pour0 = int(scared.start) - 4
sys_at = int(sysA.start) - 4
bugs_at = sys_at + 130                                    # p2_system: bugs appear at sequence frame 130
rq_at = int(rq.start) + 2
att_at = int(yawn.start) + 6
risk_at = int(risk.start) + 2
q_at = int(worry.start) + 4
leave_at = q_at + hold(9, 0.6)
comp_at = int(comp.start) + 2
layer_at = int(layer.start) + 2
VO_CUES = {1: t1_on + 6, 2: s2_at + 4, 3: t2_on + 8, 4: pour0 + 4,
           5: bugs_at - F(word(5, "bugs") * FPS) + 6, 6: rq_at + 8, 7: att_at + 8, 8: risk_at + 4, 9: q_at,
           10: comp_at + 4, 11: layer_at + 4}

# ------------------------------------------------------------------ LCD1 (hook)
cl0 = hips(talk1.start)
TV1 = Vector((cl0.x + 0.55 + TVW / 2, cl0.y + 0.72, TVZ))         # screen edge ~0.55 m from him
tv1 = fx.Board("LCD1", [scr("p2_s01"), scr("p2_s02")], width=TVW, frame="tv", power=True, glow=0.38,
               stand_height=STAND, coll=fx.collection("LCD1"))
tv1.base_z = TVZ
anim.keys(tv1.root, "location", [(1, Vector((TV1.x + 9, TV1.y, TVZ)), "const"),
                                 (Y0 + 2, Vector((TV1.x + 9, TV1.y, TVZ)), "expo_out"),
                                 (Y0 + 14, Vector((TV1.x - 0.25, TV1.y, TVZ)), "back"), (Y0 + 22, TV1, "bez")])
anim.keys(tv1.root, "rotation_euler", [(Y0 + 2, 0.0, "expo_out"), (Y0 + 12, -0.05, "back"), (Y0 + 20, 0.0)], index=1)
tv1.power_on(t1_on)
tv1.show(1, 0)
tv1.show(s2_at, 1)
tv1.flicker(s2_at - 2, n=2)
tv1.power_off(int(cart.start) + 20)

# ------------------------------------------------------------------ LCD2 (problem → bridge)
cl = hips(w4.end)
TV2 = Vector((cl.x + 0.55 + TVW / 2, cl.y + 0.55, TVZ))
tiles = [q_at + F(word(9, w) * FPS) for w in ("downtime", "security", "performance", "bad")]
lcd2 = [(seq("velocity", 150, t2_on), 1), (scr("s05_volume"), pour0 - 4), (seq("p2_system", 210, sys_at), sys_at),
        (seq("p2_review_queue", 180, rq_at), rq_at), (scr("p2_attention"), att_at), (scr("p2_risk"), risk_at),
        (scr("p2_quad_0"), q_at)] + [(scr(f"p2_quad_{k + 1}"), f) for k, f in enumerate(tiles)] + [
        (seq("p2_leaving", 96, leave_at), leave_at), (scr("p2_competitive"), comp_at), (scr("p2_layer"), layer_at)]
tv2 = fx.Board("LCD2", [s for s, _ in lcd2], width=TVW, frame="tv", power=True, glow=0.38,
               stand_height=STAND, coll=fx.collection("LCD2"))
tv2.root.location = TV2
tv2.power_on(t2_on)
for i, (_, f) in enumerate(lcd2):
    tv2.show(f, i)
for f in (pour0 - 4, sys_at, rq_at, att_at, risk_at, q_at, leave_at, comp_at, layer_at):
    tv2.flicker(f - 2, n=2)
tv2.power_off(int(cart2.start) + 6)

# paper avalanche around his feet
mid_p = hips(scared.start + 30)
r = random.Random(4)
fx.paper_pour("CodePages", scr("code_paper"),
              lambda i: TV2 + Vector((r.uniform(-1.0, 1.0), -0.08, r.uniform(-0.55, 0.55))),
              (mid_p.x + 0.3, mid_p.y - 0.1), count=170, start=pour0, dur=70, spread=(1.2, 0.8))

# spiders: on "bugs" they crawl out of LCD2's screen, drop to the floor and swarm him; after the
# shock they scatter off-stage
spiders = fx.Spiders(paths.SPIDER_GLB, size=0.45)
rs = random.Random(11)
SP0 = bugs_at + 6
him = hips(shock.start + 12)
for k in range(12):
    f0 = SP0 + k * 3
    out_ = Vector((TV2.x + rs.uniform(-1.0, 1.0), TV2.y - 0.12, TVZ + rs.uniform(-0.45, 0.4)))
    drop = Vector((out_.x + rs.uniform(-0.2, 0.2), TV2.y - 0.45, 0.0))
    ang = rs.uniform(-2.9, -0.3)                         # arc in FRONT of him (camera side, clear of the paper pile)
    near = Vector((him.x + 0.95 * math.cos(ang) * rs.uniform(0.8, 1.2), him.y - 0.35 + 0.75 * math.sin(ang), 0.0))
    flee = Vector((him.x + rs.choice((-1, 1)) * rs.uniform(3.5, 4.5), him.y - rs.uniform(0.2, 1.5), 0.0))
    t_near = int(shock.start) + 14 + rs.randint(0, 10)
    spiders.add([(f0, out_), (f0 + 8, (out_ + drop) / 2 + Vector((0, -0.15, 0.05))), (f0 + 14, drop),
                 (t_near, near), (t_near + 22, near + Vector((rs.uniform(-0.1, 0.1), rs.uniform(-0.1, 0.1), 0))),
                 (t_near + 22 + rs.randint(26, 40), flee)], walk_speed=3.0)

# ------------------------------------------------------------------ S6 tower: webbed down block by block
arrive = hips(builds[0].start)
TX = max(arrive.x + 2.3, TV2.x + TVW / 2 + 1.8)            # clear of LCD2 (powered off, still standing)
TY = arrive.y + 0.5
BLOCKS = [("INSPECTION", 2.2, 1.0, 0.72, (0.15, 0.39, 0.92)), ("ENGINEERS' CONFIDENCE", 2.0, 0.95, 0.66, (0.12, 0.16, 0.23)),
          ("CUSTOMER CONFIDENCE", 1.8, 0.9, 0.66, (0.12, 0.16, 0.23)), ("COMPETITIVE PRODUCT", 1.6, 0.85, 0.66, (0.12, 0.16, 0.23))]
tcoll = fx.collection("Tower")


def block(i, w, d, h, col):
    import bmesh
    root = fx.empty(f"Block{i}", coll=tcoll, size=0.2)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w, d, h), verts=bm.verts)
    me = bpy.data.meshes.new(f"Block{i}_Mesh")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(f"Block{i}_Body", me)
    tcoll.objects.link(ob)
    ob.parent = root
    ob.data.materials.append(fx.material(f"Block{i}_Mat", col, rough=0.45))
    bev = ob.modifiers.new("Bevel", "BEVEL")
    bev.width, bev.segments = 0.03, 3
    # label on the front face
    lm = bpy.data.meshes.new(f"Block{i}_Label")
    lw, lh = w * 0.94, h * 0.8
    lm.from_pydata([(-lw / 2, -d / 2 - 0.004, -lh / 2), (lw / 2, -d / 2 - 0.004, -lh / 2), (lw / 2, -d / 2 - 0.004, lh / 2),
                    (-lw / 2, -d / 2 - 0.004, lh / 2)], [], [(0, 1, 2, 3)])
    uv = lm.uv_layers.new()
    for li, loop in enumerate(lm.loops):
        uv.data[li].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][loop.vertex_index]
    lo = bpy.data.objects.new(f"Block{i}_LabelObj", lm)
    tcoll.objects.link(lo)
    lo.parent = root
    m = bpy.data.materials.new(f"Block{i}_LabelMat")
    if m.node_tree is None:
        m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    tex = m.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(scr(f"tower_{i}"), check_existing=True)
    m.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    m.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 0.35
    lm.materials.append(m)
    top = fx.empty(f"Block{i}_Top", (0, 0, h / 2), tcoll, 0.08)
    top.parent = root
    return root, top


webs = fx.WebShots(rig, fx.collection("Webs"))
stack_z, roots = 0.0, []
VO_CUES.update({n: vo_s6[n] for n in (12, 13, 14, 15, 16)})
for i, ((label, w, d, h, col), b) in enumerate(zip(BLOCKS, builds)):
    root, top = block(i, w, d, h, col)
    zc = stack_z + h / 2
    stack_z += h
    hit = int(perf.clip_frame(b, up_pk))
    land_f = hit + 12
    rest = Vector((TX + (0.04 if i % 2 else -0.03), TY, zc))
    anim.visible(root, [(1, False), (hit - 6, True)])
    for ch in root.children:
        anim.visible(ch, [(1, False), (hit - 6, True)])
    anim.keys(root, "location", [(1, rest + Vector((0, 0, 7.5)), "const"), (hit, rest + Vector((0, 0, 7.5)), "in"),
                                 (land_f, rest, "out"), (land_f + 3, rest + Vector((0, 0, 0.05)), "in"), (land_f + 6, rest)])
    webs.shot(f"Web_BlockL{i}", L_HAND, (lambda t: (lambda f: t.matrix_world.translation))(top), hit - 4, hit, land_f)
    webs.shot(f"Web_BlockR{i}", R_HAND, (lambda t: (lambda f: t.matrix_world.translation))(top), hit - 4, hit, land_f)
    shot.sfx("web_thwip", hit - 3)
    shot.sfx("block_thud", land_f)
    roots.append((root, rest, land_f))

# cash stacks on the top block (arrive with COMPETITIVE PRODUCT, "and the money coming in")
top_root, top_rest, top_land = roots[-1]
cash_mat = fx.material("CashSide", (0.29, 0.6, 0.38), rough=0.6)
cash_f = int(VO_CUES[15] + word(15, "money") * FPS)
cash = []
for k, (cx, cy) in enumerate([(-0.45, -0.15), (-0.15, 0.1), (0.15, -0.12), (0.45, 0.12), (0.0, 0.0)]):
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.38, 0.18, 0.14 + 0.05 * (k % 2)), verts=bm.verts)
    me = bpy.data.meshes.new(f"Cash{k}")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(f"Cash{k}", me)
    tcoll.objects.link(ob)
    ob.data.materials.append(cash_mat)
    rest = top_rest + Vector((cx, cy, BLOCKS[-1][3] / 2 + 0.07))
    anim.visible(ob, [(1, False), (cash_f - 4, True)])
    anim.keys(ob, "location", [(1, rest + Vector((0, 0, 3.0)), "const"), (cash_f + k * 2, rest + Vector((0, 0, 3.0)), "in"),
                               (cash_f + k * 2 + 9, rest, "back"), (cash_f + k * 2 + 13, rest)])
    cash.append((ob, rest))
shot.sfx("cash_flutter", cash_f)

# collapse: web-yank INSPECTION out (towards Miles), everything above tumbles down; cash rains
C = vo_s6[16] + F(word(16, "everything") * FPS) - 6                                                                # inspection block gone
webs.shot("Web_Yank2", R_HAND, (lambda t: (lambda f: t.matrix_world.translation))(roots[0][0]), Y1 - 4, Y1, Y1 + 8)
shot.sfx("web_thwip", Y1 - 3)
shot.sfx("tower_crash", C + 4)
rr = random.Random(9)
# INSPECTION skids out towards Miles (stops short of him); the rest land around it without overlapping
fallen = [Vector((max(TX - 0.9, arrive.x + 1.45), TY - 1.15, BLOCKS[0][3] / 2)), Vector((TX + 0.35, TY - 0.0, BLOCKS[1][3] / 2)),
          Vector((TX + 2.1, TY + 0.5, BLOCKS[2][3] / 2)), Vector((TX + 1.5, TY - 1.2, BLOCKS[3][3] / 2))]
for i, ((root, rest, _), end) in enumerate(zip(roots, fallen)):
    s0 = Y1 + 2 if i == 0 else C + (i - 1) * 3          # base yanked out; upper blocks hang a beat, then fall
    mid = (rest + end) / 2 + Vector((0, 0, 0.35 + 0.15 * i))
    anim.keys(root, "location", [(s0, rest, "in" if i else "expo_out"), (s0 + 7 + i, mid, "in"), (s0 + 14 + 2 * i, end, "back"),
                                 (s0 + 20 + 2 * i, end)])
    spin = Vector((rr.uniform(-0.6, 0.6), rr.uniform(-1.2, 1.2), rr.uniform(-0.8, 0.8))) if i else Vector((0, 0, 0.35))
    anim.keys(root, "rotation_euler", [(s0, Vector((0, 0, 0)), "in"), (s0 + 7 + i, spin * 1.8, "out"),
                                       (s0 + 14 + 2 * i, Vector((0, 0, spin.z)), "bez")])
for k, (ob, rest) in enumerate(cash):
    end = Vector((TX + rr.uniform(-1.6, 1.6), TY + rr.uniform(-1.2, 0.3), 0.07))
    anim.keys(ob, "location", [(C + 4, rest, "out"), (C + 12 + k, rest + Vector((rr.uniform(-0.8, 0.8), -0.3, 1.0)), "in"),
                               (C + 24 + k, end, "bez")])
    anim.keys(ob, "rotation_euler", [(C + 4, Vector((0, 0, 0))), (C + 24 + k, Vector((0, 0, rr.uniform(-2, 2))))])
fx.paper_pour("Bills", scr("cash_bill"), lambda i: top_rest + Vector((rr.uniform(-0.5, 0.5), 0, 0.3)),
              (TX, TY - 0.4), count=70, start=C + 6, dur=40, spread=(2.2, 1.1), size=(0.24, 0.104), arc=(1.0, 2.2))


# ------------------------------------------------------------------ S1 webs + overlays
top = hips(hang.start + 20)
sky = Vector((top.x, top.y, 14.0))
RELEASE = int(land.start) + 3
webs.shot("Web_HangL", L_HAND, lambda f: sky, 1, 1, RELEASE)
webs.shot("Web_HangR", R_HAND, lambda f: sky, 1, 1, RELEASE)
hook1 = lambda f: tv1.nearest_hook(webs.hand(R_HAND))
webs.shot("Web_Shot", R_HAND, hook1, SHOT_HIT - 4, SHOT_HIT, Y0 + 16)
webs.shot("Web_Yank", L_HAND, hook1, Y0, Y0, Y0 + 16)
for o in fx.collection("Webs").objects:
    if o.type == "MESH":
        o.data.materials[0] = fx.material("Web_Dark", (0.92, 0.95, 1.0), rough=0.4, emit=1.6)

office.check_watch(int(idle1.start) + 6, hold=18)
office.reach(int(tap1.start) + 6, (TV1.x - TVW / 2 + 0.12, TV1.y - 0.05, TVZ - 0.25))
office.reach(int(tap2.start) + 4, (TV2.x - TVW / 2 + 0.12, TV2.y - 0.05, TVZ - 0.25))
office.check_watch(int(stuck.start) + 4, hold=16)
office.check_watch(int(yawn.end) - 32, hold=10)
# presenter gestures towards the near edge of the screen whenever a new slide lands
for f, tv in ((t1_on + 8, TV1), (s2_at + 6, TV1), (int(vel.start) + 8, TV2), (sys_at + 10, TV2), (rq_at + 10, TV2),
              (risk_at + 8, TV2), (comp_at + 6, TV2), (layer_at + 6, TV2)):
    x = hips(f).x
    edge = tv.x - TVW / 2 + 0.35 if x < tv.x else tv.x + TVW / 2 - 0.35
    office.present_to(f, (edge, tv.y - 0.3, TVZ + 0.1), x)          # gesture in front of the glass

# SFX for S1–S5
shot.sfx("landing_thud", IMPACT - 6)                     # impact sits 0.2 s into the sound
shot.sfx("web_thwip", SHOT_HIT - 3)
shot.sfx("board_whoosh", Y0 - 1)                         # fly-by peaks ~0.3 s in, mid-flight
shot.sfx("board_thud", Y0 + 14)
shot.sfx("tv_power_on", t1_on)
shot.sfx("tv_power_on", t2_on)
shot.sfx("cartwheel_whoosh", int(cart.start) + 36)       # over the top ~45 frames in
shot.sfx("cartwheel_whoosh", int(cart2.start) + 36)
shot.sfx("cartwheel_whoosh", SPRINT_AT + 2)               # the dash
shot.sfx("paper_avalanche", pour0)
shot.sfx("bugs_skitter", bugs_at)
for f in tiles:
    shot.sfx("ui_pop", f)

webs.bake(range(1, END + 1))

# ------------------------------------------------------------------ lights
fx.follow_spot(rig, energy=380)
for i, p in enumerate((TV1, TV2, Vector((TX, TY, 0)))):
    fx.spot(f"ScreenTop{i + 1}", (p.x, p.y - 2.2, 4.6), (p.x, p.y - 1.4, 0.0), energy=650, angle=60)

# ------------------------------------------------------------------ polish: feet on the floor
airborne = [hang, land]                                   # cartwheels stay locked: planted hands count as floor
lock_err = perf.ground_lock(int(land.end), END, skip=airborne)

# ------------------------------------------------------------------ camera: locked while a screen is up
cam = fx.CameraRig(lens=30, fstop=3.2)
h = hips(IMPACT)


def frame_on(tv, f, margin=0.9, pad=1.15):
    m = hips(f)
    left, right = min(m.x - margin, tv.x - TVW / 2 - 0.4), max(m.x + margin, tv.x + TVW / 2 + 0.5)
    return shot.frame_span(left, right, (tv.y + m.y) / 2, lens_mm=30, pad=pad, cam_z=1.75, target_z=1.4)


def screen_close(tv):
    return shot.frame_span(tv.x - TVW / 2 - 0.9, tv.x + TVW / 2 + 0.25, tv.y, lens_mm=30, pad=1.1, cam_z=1.7,
                           target_z=TVZ - 0.05)


def locked(a, b, ct, cut=True):
    cam.at(int(a), ct[0], ct[1], "lin", cut=cut)
    cam.at(int(b), ct[0], ct[1], "lin")


cam.lens(1, 22, "const")
cam.at(1, (h.x + 0.8, -6.0, 0.4), (h.x, 0, 3.0))                                       # free: descent
cam.at(int(hang.end) - 2, (h.x + 0.6, -5.4, 0.5), (h.x, 0, 2.4))
cam.lens(int(land.start) + 2, 30, "const")
cam.at(int(land.start) + 2, (h.x + 0.9, h.y - 4.0, 0.95), (h.x, h.y, 0.95), cut=True)
cam.at(int(idle1.end), (h.x + 0.9, h.y - 3.4, 1.25), (h.x, h.y, 1.2), "inout")           # free: watch check
c1 = frame_on(TV1, int(talk1.start))
cam.at(int(SHOT_HIT) + 4, (c1[0][0] + 1.0, c1[0][1] - 1.5, 1.8), (c1[1][0] + 0.8, c1[1][1], 1.4), "expo_out")
locked(Y0 + 22, int(cart.start) + 4, frame_on(TV1, int(talk2.start)), cut=False)             # LCD1 up: locked
_xs = [hips(f).x for f in (w4.end, vel.start, stuck.end, w5.end, sysA.start)]
_l, _r = min(_xs), max(_xs)                                                                 # both sides: the dash
w2s = shot.frame_span(min(_l, _r) - 0.9, max(_l, _r) + 0.9, (TV2.y + hips(vel.start).y) / 2, lens_mm=30, pad=1.12,
                      cam_z=1.75, target_z=1.4)
cam.at(int(w4.end), w2s[0], w2s[1], "inout")                                              # free: truck with cartwheel
locked(int(w4.end), sys_at - 1, w2s, cut=False)
close2 = screen_close(TV2)
locked(sys_at, int(shock.start) + 4, close2)                                              # read the graph
swarm = shot.frame_span(TV2.x - TVW / 2 - 0.2, him.x + 1.5, (TV2.y + him.y) / 2 - 0.4, lens_mm=30, pad=1.12,
                       cam_z=1.45, target_z=0.95)                                       # floor in view: the spiders
locked(int(shock.start) + 5, rq_at - 1, swarm)                                           # SHOCK: him + the swarm
locked(rq_at, att_at - 1, close2)                                                        # review queue
locked(att_at, risk_at - 1, frame_on(TV2, att_at + 30))                                   # yawn
locked(risk_at, q_at - 1, frame_on(TV2, risk_at + 10))
locked(q_at, leave_at + 96, close2)                                                      # tiles + walk away
locked(leave_at + 97, int(cart2.start) + 2, frame_on(TV2, comp_at + 20))                  # bridge
TOWER_H = sum(b[3] for b in BLOCKS)
tw = shot.frame_span(arrive.x - 1.0, TX + BLOCKS[0][1] / 2 + 0.8, (TY + arrive.y) / 2, lens_mm=30, pad=1.2,
                     cam_z=1.75, target_z=(TOWER_H + 0.3) * 0.5 + 0.15)                    # whole tower + cash in frame
cam.at(int(w6.end) + 4, tw[0], tw[1], "inout")                                            # free: to the tower
cam.at(int(pull.start) - 4, (tw[0][0], tw[0][1] + 0.15, tw[0][2]), tw[1])                      # barely drift while building
rub = shot.frame_span(arrive.x - 1.0, TX + 2.9, (TY + arrive.y) / 2, lens_mm=30, pad=1.1, cam_z=1.6, target_z=0.7)
cam.at(C + 30, rub[0], rub[1])                                                             # pull back: the rubble
last = shot.frame_span(hips(fear.start + 40).x - 1.1, TX + 2.3, (TY + arrive.y) / 2, lens_mm=30, pad=1.06,
                      cam_z=1.5, target_z=0.8)
cam.at(END, last[0], last[1])                                                              # slow push: Miles + the rubble
office.face_camera(cam.cam, [(c.start + 4, c.end - 2) for c in (talk1, talk2, pre, vel, sysA, rq, risk, comp, layer)])
cam.shake(int(IMPACT), amp=0.06, dur=8)
cam.shake(C + 2, amp=0.08, dur=14)

shot.finish("piece2", exposure=0.0, markers=[(f"vo {n}", f) for n, f in VO_CUES.items()] + [
    ("S1 hook", 1), ("S2 problem", int(cart.start)), ("S2 bugs", bugs_at), ("S3 bridges", rq_at),
    ("S4 customers", risk_at), ("S5 bridge", comp_at), ("S6 tower", int(cart2.start)), ("S6 collapse", C),
    ("S6 end", END)])
cues = sorted(VO_CUES.items())
for (a, fa), (b, fb) in zip(cues, cues[1:]):
    if fa + dur(a) * FPS > fb:
        print(f"VO OVERLAP {a}->{b}: {(fa + dur(a) * FPS - fb) / FPS:.2f}s")
print(f"PIECE2 frames 1-{END} ({END / FPS:.1f}s)  ground-lock max correction {lock_err * 100:.1f} cm")
