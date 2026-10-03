# Frame packet — 06-you-owe

Write exactly this one file:

    compositions/frames/06-you-owe.html

| field | value |
| --- | --- |
| `data-composition-id` | `06-you-owe` |
| `data-duration` | `8.5` |
| id prefix for every element | `06-you-owe-` |
| position in the film | 39.5s -> 48.0s of 270s |
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
Media: `assets/plates/p09_city_pano.jpg`, full bleed. This is the town that
lives below the dam &mdash; it is standing in for production and for users.

Slug: `Boulder City &middot; the town below the dam &middot; 1932`

Lines:
- **0.6** &mdash; 50px weight 400: `You owe your users and customers &mdash;`
- **2.6** &mdash; 70px weight 700: `AN AI-ASSISTED INSPECTION LAYER`
- **5.4** &mdash; 30px italic `#C9BFA8`: `Everything downstream is built on the assumption that it holds.`
