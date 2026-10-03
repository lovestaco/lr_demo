# Frame packet — 12-attention-limited

Write exactly this one file:

    compositions/frames/12-attention-limited.html

| field | value |
| --- | --- |
| `data-composition-id` | `12-attention-limited` |
| `data-duration` | `10.5` |
| id prefix for every element | `12-attention-limited-` |
| position in the film | 95.0s -> 105.5s of 270s |
| act marker text | `III &middot; The Rising Water` |
| grade stage | G0 — **do not apply it yourself**, the builder applies grades centrally after you finish |

## Layout

`film-bleed` — an archive `<video>` that is natively 1440x1080.
Wrap it in a gate div at `left:240px; top:0; width:1440px; height:1080px; overflow:hidden`,
with the video at `left:0; top:0; width:1440px; height:1080px; object-fit:cover`.
Root background `#0b0a08` fills the pillarbox columns.
Two 1px gate hairlines, `background: rgba(237,228,208,.20)`, full height, at
`left:240px` and `left:1679px`.
Same bottom scrim and text block as `bleed`. Ken Burns on the video element.

## Content
Media: `assets/archive/v_scalers.mp4` (10.70s) in the gate,
`data-start="0" data-duration="10.5"`. Men on ropes against a huge rock face.
**This is the hero frame of the problem act.**

Slug: `High scalers &middot; 1,000-foot cliffs &middot; 1932`

Lines:
- **0.8** &mdash; 48px weight 400: `And let's remember &mdash;`
- **2.8** &mdash; 80px weight 700, two lines: `HUMAN ATTENTION IS STILL LIMITED`
- **7.6** &mdash; 28px italic `#C9BFA8`: `Two lamps. One thousand feet of rock.`

**The lamp beat.** At **5.4**, show how little of the wall is covered:
- A darkening field over the gate only (`left:240px; top:0; width:1440px;
  height:1080px`), `background: rgba(11,10,8,.55)`, fading `opacity 0 -> 1` over
  0.8s at 5.4.
- Two lamp pools ON TOP of that field, each a 184x184px div,
  `background: radial-gradient(circle, rgba(237,228,208,.26) 0%, rgba(237,228,208,0) 70%)`,
  at `left:560px; top:300px` and `left:1180px; top:620px`. Fade them
  `opacity 0 -> 1` over 0.8s at 5.4 alongside the field.
The visual point is that two small pools cover almost none of the frame. Do not
make them bigger or brighter.
