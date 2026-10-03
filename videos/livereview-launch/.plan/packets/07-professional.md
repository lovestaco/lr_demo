# Frame packet — 07-professional

Write exactly this one file:

    compositions/frames/07-professional.html

| field | value |
| --- | --- |
| `data-composition-id` | `07-professional` |
| `data-duration` | `8.5` |
| id prefix for every element | `07-professional-` |
| position in the film | 48.0s -> 56.5s of 270s |
| act marker text | `II &middot; The Belief` |
| grade stage | G0 — **do not apply it yourself**, the builder applies grades centrally after you finish |

## Layout

`split-left` — mirror of split-right. Plate `<img>` at
`left:0; top:0; width:900px; height:1080px; object-fit:cover`.
1px `#8A7F68` hairline at `left:899px`.
Text block `left:1060px; width:760px`, left-aligned, composed around the mid-line.
Ken Burns on the plate. Keep slug and act marker.

## Content
Media: `assets/plates/p10_concrete_ctrl.jpg` (portrait) on the LEFT.
It is a 1933 group portrait captioned *"Personnel of concrete testing laboratory"* &mdash;
the inspection team. Frame it so the people are visible (`object-position: 50% 30%`).

Slug: `Concrete testing laboratory &middot; personnel &middot; 1933`

Lines, in the right field (`left:1060px; width:760px`):
- **0.6** &mdash; 48px weight 400: `If you are professional &mdash;`
- **2.4** &mdash; 62px weight 700: `you must adopt it.`
- **4.8** &mdash; 38px weight 400: `For the sake of your business reputation.`
