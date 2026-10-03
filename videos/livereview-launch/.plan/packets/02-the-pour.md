# Frame packet — 02-the-pour

Write exactly this one file:

    compositions/frames/02-the-pour.html

| field | value |
| --- | --- |
| `data-composition-id` | `02-the-pour` |
| `data-duration` | `7.0` |
| id prefix for every element | `02-the-pour-` |
| position in the film | 8.5s -> 15.5s of 270s |
| act marker text | `I &middot; The River` |
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
Media: `assets/archive/v_pour_bucket.mp4` (7.10s) in the gate, `data-start="0" data-duration="7.0"`.

Slug: `Placing concrete &middot; Boulder Dam &middot; 1933`

Lines (all stay once shown):
- **0.5** &mdash; 54px weight 400: `Day and night, the pouring never stopped.`
- **3.0** &mdash; 64px weight 700: `Neither does yours.`

Two lines only. Let the shot breathe; the bucket swinging is the point.
