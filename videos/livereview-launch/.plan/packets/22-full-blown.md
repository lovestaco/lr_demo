# Frame packet — 22-full-blown

Write exactly this one file:

    compositions/frames/22-full-blown.html

| field | value |
| --- | --- |
| `data-composition-id` | `22-full-blown` |
| `data-duration` | `8.0` |
| id prefix for every element | `22-full-blown-` |
| position in the film | 239.0s -> 247.0s of 270s |
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
Layout `bleed`. **Grade G5 &mdash; no treatment at all.** This is the first fully
clean, fully colour frame in the film. It has to land as a release.

Media: `assets/plates/p40_dam_today.jpg` &mdash; the completed dam today, in colour,
holding the reservoir. Ken Burns `scale 1.05 -> 1.0`.

Type switches to **Inter** here and stays Inter for the rest of the film.
Fixture colours become `rgba(232,238,255,.55)` / `rgba(232,238,255,.42)`.
Scrim gradient uses `rgba(8,11,18,...)` instead of the ink brown.

Slug: `Hoover Dam &middot; today`

Lines:
- **0.6** &mdash; 40px weight 400 `#E8EEFF`: `That's why you owe your customers, your profession and your reputation &mdash;`
- **2.8** &mdash; 62px weight 700 `#E8EEFF`, two lines: `A FULL-BLOWN AI-ASSISTED CODE INSPECTION LAYER`
