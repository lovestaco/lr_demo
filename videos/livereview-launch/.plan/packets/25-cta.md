# Frame packet — 25-cta

Write exactly this one file:

    compositions/frames/25-cta.html

| field | value |
| --- | --- |
| `data-composition-id` | `25-cta` |
| `data-duration` | `7.5` |
| id prefix for every element | `25-cta-` |
| position in the film | 262.5s -> 270.0s of 270s |
| act marker text | `VII &middot; The Dam Holds` |
| grade stage | G5 — **do not apply it yourself**, the builder applies grades centrally after you finish |

## Layout

`bleed` — one `<img>` plate, `position:absolute; inset:0; width:1920px;
height:1080px; object-fit:cover`, wrapped in nothing. Ken Burns `scale 1.055 -> 1.0`
over the whole frame, `ease:"none"`, `transform-origin:50% 50%`.
Bottom scrim div: `position:absolute; inset:0; width:1920px; height:1080px;
background: linear-gradient(180deg, rgba(11,10,8,0) 34%, rgba(11,10,8,.9) 100%);`
Text block: `left:140px; width:1400px`, lines stacked so the LAST line's baseline
region ends near `top:880px`. Work upward from there.

## Content
Layout `bleed`. Inter. Grade G5 (no treatment). **The last frame.**

Media: `assets/plates/p41_lake_today.jpg` &mdash; the reservoir today, in colour, calm.
The water is still there; it is simply being held. Ken Burns `scale 1.04 -> 1.0`.

Slug: `Lake Mead &middot; the water, put to work`

Content, composed as a centred block (`left:0; width:1920px; text-align:center`):
- **0.8** &mdash; `assets/logo.svg` as an `<img>`, `height:64px; width:auto`, centred,
  at about `top:406px`. Fade in over 0.7s.
- **2.2** &mdash; 70px weight 700 `#E8EEFF`, centred at about `top:512px`:
  `hexmos.com/livereview`
- **4.4** &mdash; 30px italic `#C9BFA8`, centred at about `top:628px`:
  `The water still comes. Now something is watching the wall.`

That last line is the payoff of the whole allegory. Give it a clean 0.7s fade,
no blur, no stagger &mdash; it should arrive calmly.
