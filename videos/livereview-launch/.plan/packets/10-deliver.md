# Frame packet — 10-deliver

Write exactly this one file:

    compositions/frames/10-deliver.html

| field | value |
| --- | --- |
| `data-composition-id` | `10-deliver` |
| `data-duration` | `7.0` |
| id prefix for every element | `10-deliver-` |
| position in the film | 73.5s -> 80.5s of 270s |
| act marker text | `III &middot; The Rising Water` |
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
Media: `assets/plates/p13_ranch_res.jpg`, full bleed &mdash; a reservoir on an
irrigated ranch downstream: the people the water is actually *for*.

Slug: `Irrigated ranch below the dam &middot; 1935`

Lines:
- **0.6** &mdash; 46px weight 400: `And you still need to deliver to your customers &mdash;`
- Then three words landing in sequence on ONE line, 64px weight 700, with a
  visible gap between them: `faster,` at **2.4**, `safer,` at **3.1**,
  `higher quality.` at **3.8**. Lay them out as three inline-block spans in one
  container so they sit on a shared baseline; animate each span separately.
  All three stay to the end.
