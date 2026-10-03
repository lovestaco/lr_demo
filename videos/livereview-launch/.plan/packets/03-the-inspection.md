# Frame packet — 03-the-inspection

Write exactly this one file:

    compositions/frames/03-the-inspection.html

| field | value |
| --- | --- |
| `data-composition-id` | `03-the-inspection` |
| `data-duration` | `9.5` |
| id prefix for every element | `03-the-inspection-` |
| position in the film | 15.5s -> 25.0s of 270s |
| act marker text | `I &middot; The River` |
| grade stage | G0 — **do not apply it yourself**, the builder applies grades centrally after you finish |

## Layout

`split-right` — portrait plate `<img>` at
`left:1020px; top:0; width:900px; height:1080px; object-fit:cover`.
Left field is root background `#0b0a08` (0 -> 1020).
1px `#8A7F68` hairline, full height, at `left:1020px`.
Text block `left:140px; width:780px`, left-aligned, vertically composed around
the frame's mid-line (roughly `top:340px` to `top:760px`).
Ken Burns on the plate: `scale 1.05 -> 1.0`.
No bottom scrim needed (text sits on the dark field) — but DO keep the slug and
act marker.

## Content
Media: `assets/plates/p07_highscaler2.jpg` (portrait) on the RIGHT.

Slug: `High scalers &middot; Arizona abutment &middot; 1932`

Lines, left-aligned in the left field (`left:140px; width:780px`):
- **0.6** &mdash; 50px weight 400: `But do you do enough of &mdash;`
- **2.6** &mdash; 68px weight 700, wraps to two lines: `AI-ASSISTED CODE INSPECTION?`
- **5.6** &mdash; 30px italic, colour `#C9BFA8`: `Two men. A mile of wall. One rope each.`

Compose the three so the block sits centred on the frame's mid-line (roughly
`top:352px` for the first line). This frame answers frame 01 &mdash; same sentence
shape, opposite verb. Keep the type sizes in that relationship.
