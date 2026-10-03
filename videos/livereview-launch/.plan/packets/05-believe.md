# Frame packet — 05-believe

Write exactly this one file:

    compositions/frames/05-believe.html

| field | value |
| --- | --- |
| `data-composition-id` | `05-believe` |
| `data-duration` | `6.5` |
| id prefix for every element | `05-believe-` |
| position in the film | 33.0s -> 39.5s of 270s |
| act marker text | `II &middot; The Belief` |
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
Media: `assets/plates/p05_first_bucket.jpg`, full bleed.

Slug: `First concrete placed &middot; June 6, 1933`

Lines:
- **0.4** &mdash; kicker, 24px, `letter-spacing:.34em`, uppercase, `rgba(237,228,208,.7)`: `Here is what we believe`
- **1.2** &mdash; 58px weight 700, `#EDE4D0`: `The river was never the problem.`
- **3.4** &mdash; 58px weight 700, `#C2703A`: `The unwatched wall was.`

The two statements are a matched pair &mdash; identical size and weight, stacked,
only the colour differs. Do not make the second one bigger.
