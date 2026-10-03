# Frame packet — 08-velocity

Write exactly this one file:

    compositions/frames/08-velocity.html

| field | value |
| --- | --- |
| `data-composition-id` | `08-velocity` |
| `data-duration` | `8.0` |
| id prefix for every element | `08-velocity-` |
| position in the film | 56.5s -> 64.5s of 270s |
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
Media: `assets/archive/v_cableway_car.mp4` (8.10s) in the gate,
`data-start="0" data-duration="8.0"`. A loaded bucket riding a cable across the
canyon &mdash; delivery in motion.

Slug: `Eight-yard bucket on the cableway &middot; 1933`

Lines:
- **0.4** &mdash; kicker, 24px `.34em` uppercase `rgba(237,228,208,.7)`: `Here is why`
- **1.6** &mdash; 68px weight 700: `Code accumulates at great VELOCITY`
- **4.6** &mdash; 30px italic `#C9BFA8`: `Eight cubic yards at a time. Every few minutes. For two years.`
