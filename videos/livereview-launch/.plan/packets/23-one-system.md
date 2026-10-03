# Frame packet — 23-one-system

Write exactly this one file:

    compositions/frames/23-one-system.html

| field | value |
| --- | --- |
| `data-composition-id` | `23-one-system` |
| `data-duration` | `7.5` |
| id prefix for every element | `23-one-system-` |
| position in the film | 247.0s -> 254.5s of 270s |
| act marker text | `VII &middot; The Dam Holds` |
| grade stage | G5 — **do not apply it yourself**, the builder applies grades centrally after you finish |

## Layout

`answer` — the modern layout. Root background `#0B0A08`.
App window shell div: `left:230px; top:346px; width:1460px; height:658px;`
`background:#0E1322; border:1.5px solid #1A2440; border-radius:12px; overflow:hidden`.
A 31px top bar inside it: `left:0; top:0; width:100%; height:31px;`
`background:#0E1322; border-bottom:1px solid #1A2440` — put three 8px dots in it
at `left:14/32/50px, top:11px`, `background:#1A2440`, `border-radius:50%`.
Product `<video>` inside the shell at `left:2px; top:33px; width:1456px;
height:623px; object-fit:contain; background:#0E1322`.
  *** object-fit MUST be `contain` — these clips are 2520x1080 (21:9) product UI
      and cropping them is not acceptable. ***
Statement card ABOVE the window: `left:230px; top:196px; width:1460px`,
Inter 42px weight 600, `#E8EEFF`.
Allegory tie-line BELOW: `left:230px; top:1022px; width:1000px`, 26px italic
Playfair, `rgba(237,228,208,.62)`.
Seal: `right:230px; top:1016px`, right-aligned, Inter 40px weight 700, `#E8EEFF`,
reading `The <N> Problem &rarr; Solved` followed by a check glyph. The words come
BEFORE the check, always.
Window opens at its stated time with `{scale:.965, opacity:0}` -> `{scale:1,
opacity:1, duration:.5, ease:"power3.out"}`; `transform-origin:50% 50%`.

## Content
Layout `answer`, Inter throughout, grade G5 (no treatment).

Statement at **0.4**: `The only platform that solves all four &mdash; in one unified system.`

Window opens at **1.0**; product clip `assets/clip13_dashboard.mp4` (7.07s),
`data-start="1.4" data-duration="6.1"`.

No tie-line, no seal on this frame &mdash; the recap frame that follows does that job.

Slug: `LiveReview &middot; one unified system`
