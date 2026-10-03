# Frame packet — 11-you-still-must

Write exactly this one file:

    compositions/frames/11-you-still-must.html

| field | value |
| --- | --- |
| `data-composition-id` | `11-you-still-must` |
| `data-duration` | `14.5` |
| id prefix for every element | `11-you-still-must-` |
| position in the film | 80.5s -> 95.0s of 270s |
| act marker text | `III &middot; The Rising Water` |
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
Media: `assets/plates/p14_grouting.jpg` (portrait) on the RIGHT &mdash; a grouting
crew sealing the rock. Duration 14.5s: the longest vintage frame, so give it air.

Slug: `Grouting crew &middot; Arizona abutment &middot; 1934`

Left field content (`left:140px; width:780px`):
- **0.3** &mdash; kicker, 24px `.34em` uppercase `rgba(237,228,208,.7)`: `You still must`
- Four ledger rows, 38px weight 400 `#EDE4D0`, entering at **1.2 / 4.2 / 7.0 / 9.8**,
  all staying to the end. Rows at `top: 330 / 430 / 530 / 630` (px):
  1. `Reduce production incidents`
  2. `Reduce security incidents`
  3. `Reduce performance regressions`
  4. `Deliver stellar customer experiences`
- Each row is preceded by an **empty, unticked** box at `left:0` relative to the
  row: 22x22px, `border:2px solid #C2703A`, `background:transparent`. They must
  NEVER tick &mdash; these are unmet obligations. Row text starts at `left:46px`.
- A 1px `#8A7F68` divider at `opacity:.45` under rows 1-3 (`top: 396 / 496 / 596`),
  each entering with its row.
