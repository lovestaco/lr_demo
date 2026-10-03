# Frame packet — 24-four-checks

Write exactly this one file:

    compositions/frames/24-four-checks.html

| field | value |
| --- | --- |
| `data-composition-id` | `24-four-checks` |
| `data-duration` | `8.0` |
| id prefix for every element | `24-four-checks-` |
| position in the film | 254.5s -> 262.5s of 270s |
| act marker text | `VII &middot; The Dam Holds` |
| grade stage | G5 — **do not apply it yourself**, the builder applies grades centrally after you finish |

## Layout

`recap` — no media at all. Root background `#0B0A08`.
Heading `left:0; width:1920px; text-align:center; top:286px`, Inter 42px weight
500, `#E8EEFF`.
Four rows centred as a block: give the block `left:560px; width:800px`, rows at
`top:420/500/580/660px`, each 44px Inter weight 500 `#E8EEFF`, left-aligned, with
a 30px `#3B82F6` check glyph at `left:-52px` relative to the row.
Rows enter one at a time and all stay.

## Content
Layout `recap`. No media. Inter throughout. Grade G5.

- **0.4** &mdash; heading, 42px weight 500 `#E8EEFF`, centred: `Here's what LiveReview solves:`
- Four rows entering at **1.4 / 2.4 / 3.4 / 4.4**, all staying:
  1. `The attention problem`
  2. `The understanding problem`
  3. `The enforcement problem`
  4. `The control and improve problem`
- Each row gets a `#3B82F6` check glyph to its left. Row enters with
  `{opacity:0, x:-16}` -> `{opacity:1, x:0, duration:.44, ease:"power3.out"}`;
  the check fades in 0.12s after its row.

Act marker only &mdash; no slug on this frame.
