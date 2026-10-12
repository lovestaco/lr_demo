---
name: blender-52-api-quirks
description: Blender 5.2 API changes that break code from older tutorials — essential for any Blender MCP work in this project
metadata: 
  node_type: memory
  type: project
  originSessionId: e822d076-33f9-4bf4-b620-4fb098ae9f1f
  modified: 2026-09-30T19:27:14.683Z
---

**Blender version:** 5.2 LTS via snap (`/snap/bin/blender`). MCP server: `uvx mcp-for-blender`.

**Critical API differences from Blender 3.x / 4.x:**

1. **Compositor**: `scene.node_tree` is gone. Use `scene.compositing_node_group` (a `CompositorNodeTree` node group).
   - Create: `ng = bpy.data.node_groups.new("Compositor", 'CompositorNodeTree')`
   - Assign: `scene.compositing_node_group = ng`
   - Output node: `ng.nodes.new('NodeGroupOutput')` + `ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')`
   - NOT `CompositorNodeComposite` (removed)

2. **Glare node**: All parameters are socket inputs, not properties.
   - `glare.inputs['Type'].default_value = 'Bloom'` (valid: 'Bloom', 'Ghosts', 'Streaks', 'Fog Glow', 'Simple Star', 'Sun Beams', 'Kernel')
   - `glare.inputs['Threshold'].default_value = 0.3`
   - `glare.inputs['Size'].default_value = 8.0`
   - `glare.inputs['Strength'].default_value = 0.6`
   - NOT `glare.glare_type`, `glare.threshold`, etc.

3. **Layered actions (fcurves)**: `action.fcurves` is gone. Path:
   ```python
   action.layers[0].strips[0].channelbags[0].fcurves
   ```
   Iterate: `for layer in action.layers: for strip in layer.strips: for cb in strip.channelbags: for fc in cb.fcurves:`

4. **Curve handles**: `BezierSplinePoint.handle_type` renamed. Avoid; use mesh torus for rings instead.

5. **Rendering**: EEVEE only (GTX 1650 Mobile, 4GB VRAM). ~1.04s/frame warm. Cycles not viable (25-75h).

6. **Render engine string**: `scene.render.engine = 'BLENDER_EEVEE'`

7. **NLA strips made via the API evaluate at influence 0** (seen 2026-10-07): set `strip.use_animated_influence = True`
   and keyframe `strip.influence` (ramps), or the strip silently does nothing.

8. **Legacy IK solver weighs every IK constraint on a chain, even at influence 0**: mute unused IK constraints
   (`con.mute = True`) or the hand gets dragged toward their targets. A 2-bone IK on a Mixamo arm also won't lift the
   hand above the shoulder reliably — use a mocap clip pose for raised-hand gestures.

9. **`matrix_world` of a just-placed object reads identity** until `bpy.context.view_layer.update()` — update before
   parenting with a computed `matrix_parent_inverse`.

**Why:** These all caused runtime errors during the ATC radar build. Using old API patterns will fail silently or crash.

**How to apply:** Always use these patterns in any Blender MCP script for this project. Don't use node properties, use socket inputs.
