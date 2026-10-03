# Frame packet — 17-heres-how

Write exactly this one file:

    compositions/frames/17-heres-how.html

| field | value |
| --- | --- |
| `data-composition-id` | `17-heres-how` |
| `data-duration` | `5.0` |
| id prefix for every element | `17-heres-how-` |
| position in the film | 164.0s -> 169.0s of 270s |
| act marker text | `VI &middot; The Inspection Layer` |
| grade stage | G0 — **do not apply it yourself**, the builder applies grades centrally after you finish |

## Layout

`bleed` — one `<img>` plate, `position:absolute; inset:0; width:1920px;
height:1080px; object-fit:cover`, wrapped in nothing. Ken Burns `scale 1.055 -> 1.0`
over the whole frame, `ease:"none"`, `transform-origin:50% 50%`.
Bottom scrim div: `position:absolute; inset:0; width:1920px; height:1080px;
background: linear-gradient(180deg, rgba(11,10,8,0) 34%, rgba(11,10,8,.9) 100%);`
Text block: `left:140px; width:1400px`, lines stacked so the LAST line's baseline
region ends near `top:880px`. Work upward from there.

## Content
**The pivot. Last frame of the 1931 world.** Only 5.0s &mdash; keep it spare.

Media: `assets/plates/p02_first_water.jpg`, full bleed &mdash; a lone figure before a
tunnel portal as the first water comes through.

Slug: `First water through the diversion tunnels &middot; 1932`

Content:
- **0.6** &mdash; 62px weight 700, `#EDE4D0`: `Here's HOW LiveReview solves them all:`
- **3.0** &mdash; `assets/logo.svg` as an `<img>`, `height:44px; width:auto`,
  positioned at `left:140px` directly beneath the line. Fade `opacity 0 -> 1`
  over 0.6s. This is the mark's FIRST appearance in the film &mdash; do not put it
  anywhere earlier.
