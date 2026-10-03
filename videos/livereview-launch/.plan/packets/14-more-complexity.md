# Frame packet — 14-more-complexity

Write exactly this one file:

    compositions/frames/14-more-complexity.html

| field | value |
| --- | --- |
| `data-composition-id` | `14-more-complexity` |
| `data-duration` | `8.5` |
| id prefix for every element | `14-more-complexity-` |
| position in the film | 114.0s -> 122.5s of 270s |
| act marker text | `IV &middot; The Cracks` |
| grade stage | G0 — **do not apply it yourself**, the builder applies grades centrally after you finish |

## Layout

`split-left` — mirror of split-right. Plate `<img>` at
`left:0; top:0; width:900px; height:1080px; object-fit:cover`.
1px `#8A7F68` hairline at `left:899px`.
Text block `left:1060px; width:760px`, left-aligned, composed around the mid-line.
Ken Burns on the plate. Keep slug and act marker.

## Content
Media: `assets/plates/p17_pothole.jpg` (portrait) on the LEFT &mdash; deeply fissured,
eroded rock found inside the foundation. Hidden decay, discovered.

Slug: `Pot-hole erosion disclosed in the foundation &middot; 1933`

Lines, right field (`left:1060px; width:760px`):
- **0.6** &mdash; 48px weight 400: `More code means &mdash;`
- **2.4** &mdash; 60px weight 700, wraps: `more complexity, more bugs, more issues.`
- **5.2** &mdash; 30px italic `#C2703A`: `And there are deeper consequences to take care of.`

That last line is the hinge into the four problems. Give it the oxide colour so
it reads as a warning, not a caption.
