# Cube Owl: a character you can direct from Blender MCP

Goal 1 from the mascot plan: import a cube-owl model, put it in a street, and
make it move on command. The owl (Livi) is fully rigged, and every move in the
"owl action library" is one Python call.

## Files

| file | what |
|---|---|
| `source/owl1.blend` | original Sketchfab model ("Low poly default cube owl (Rigged)") |
| `build_owl.py` | rebuilds `owl_rig.blend` (owl only) + `owl_street.blend` (owl + street + camera) |
| `owl_lib.py` | **the action library**: `Owl` (moves/expressions) + `Cam` (shots) |
| `demo_street.py` | 33s demo that uses most actions → `owl_demo.blend` |
| `owl_demo_preview.mp4` | rendered preview of the demo |

```bash
blender -b --factory-startup --python build_owl.py         # rebuild assets
blender -b owl_street.blend --python demo_street.py        # build demo scene
blender -b owl_street.blend --python demo_street.py -- render
```

## Driving it from MCP (or Blender's Python console)

Open `owl_street.blend`, then send this through `execute_blender_code`:

```python
import sys; sys.path.insert(0, "/home/lovestaco/pers/lr_demo/blender_owl")
import importlib, owl_lib; importlib.reload(owl_lib)
owl = owl_lib.Owl().reset(); cam = owl_lib.Cam(owl)

owl.place(-6)                       # stand at x=-6 facing camera
cam.shot("wide", at=1)
owl.walk_to(3); owl.skid()          # waddle right, screech to a stop
owl.turn("camera"); owl.wave()
owl.talk("Hi, I'm Livi!")
owl.cartwheel(-6)
owl.finish()                        # adds blinks, sets frame range
```

Every action starts at the cursor `owl.t` and moves it forward, so calls play
**in sequence**. To layer actions, pass `advance=False` (e.g.
`owl.talk("...", advance=False); owl.walk_to(8)` talks while walking). To start
an action at a specific frame, pass `at=frame`. Left and right are screen
directions as seen from the default camera.

### Owl vocabulary

| group | calls |
|---|---|
| Locomotion | `walk_to(x)`, `run_to(x)`, `hop(n, height, dx)`, `jump(dx, height, flips)`, `jump_to(x)`, `fall(from_height)` / `drop_in`, `skid(dist)`, `cartwheel(dist)`, `flip(back=)`, `spin(turns)`, `turn("left"/"right"/"camera"/"away")`, `place(x, y, facing)` |
| Attention | `look("left"/"right"/"up"/"down"/"up-left"/"camera")`, `look_left()` … `look_down()`, `look_at(obj_or_point)` |
| Expression | `express(name)` with neutral, surprised, happy, excited, sad, angry, confused, thinking, sleepy. Acted versions with body motion: `surprised()`, `happy()`, `sad()`, `angry()`, `confused()`, `thinking()`, `excited()`, `celebrate()`, `sleepy()` |
| Communication | `talk(text)` (syllable-timed beak), `point("right"/"up-left"…)`, `wave(times, side)`, `nod()`, `shake_head()`, `shrug()`, `bow()`, `flap()` |
| Transitions | `enter_left(to_x)`, `enter_right()`, `exit_left()`, `exit_right()`, `pop_in()`, `pop_out()` |
| Life | `idle(frames)`, `blink()`, `auto_blink()`, `wait(frames)`, `mark("label")` (timeline marker for syncing to narration) |

### Camera

`cam.shot(framing, at=, dur=0)` with framings: `extreme_wide`, `wide`, `full`,
`medium`, `close`, `extreme_close`, `low`, `high`. `dur=0` is a hard cut and
`dur>0` is a smooth move. Other moves: `cam.follow(start, end)` pans with the
owl, `cam.push_in(0.3, dur)`, `cam.orbit(30, dur)`, and `cam.shake(frame)`.

## The rig (`OwlRig`)

```
root ─ spin ─ body ─┬─ face ─┬─ eye_L ─ blink_L ─ pupil_L   (and _R)
 (hop     (flips,   │        ├─ brow_L / brow_R
  height)  wheels)  │        ├─ beak, jaw (talking)
                    ├─ tuft_L / tuft_R   (ear tufts: emotion)
                    ├─ wing_L / wing_R   (L = owl's left = screen right)
                    ├─ leg_L / leg_R     (don't inherit squash)
                    └─ tail
```

All bones point +Z with roll 0, so the pose channels work like this:
- `loc.x` moves right, `loc.y` moves up, and `loc.z` moves towards the camera.
- `rot.x` pitches (positive nods forward) and `rot.y` yaws (positive looks screen-right).
- `rot.z` rolls in the face plane. On `wing_L`, +1.57 points the wing screen-right.

`body.scale` gives squash and stretch, pivoting at the bottom of the body. World
travel and facing direction live on the armature object (`location`,
`rotation_euler.z`).

## Extending

A new move is a method that calls `self.seq(start, [(dt, {channel: value}, ease), ...])`.
A channel is `(bone, "loc"|"rot"|"scl", axis)` or `("obj", ...)`, and the ease
can be `bez`, `lin`, `const`, `back`, `in`, `out`, `inout` or `bounce`. Avoid
`elastic` on keys whose value doesn't change: Blender's elastic easing still
oscillates there.
