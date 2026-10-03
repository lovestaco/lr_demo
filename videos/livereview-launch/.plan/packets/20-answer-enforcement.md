# Frame packet — 20-answer-enforcement

Write exactly this one file:

    compositions/frames/20-answer-enforcement.html

| field | value |
| --- | --- |
| `data-composition-id` | `20-answer-enforcement` |
| `data-duration` | `17.5` |
| id prefix for every element | `20-answer-enforcement-` |
| position in the film | 204.0s -> 221.5s of 270s |
| act marker text | `VI &middot; The Inspection Layer` |
| grade stage | G3 — **do not apply it yourself**, the builder applies grades centrally after you finish |

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
Layout `answer`. Grade G3.

Statement at **0.4**: `LiveReview reviews at commit, push, PR, CI/CD and on schedule &mdash; enforcing your rules.`
(42px may need to wrap to two lines &mdash; allow it, keep `line-height:1.25`.)

Window opens at **1.4**.

TWO product clips, distinct ids:
- `assets/clip08_schedule.mp4` (4.00s) &mdash; `data-start="2.0" data-duration="4.0"`
- `assets/clip10_cicd.mp4` (6.67s) &mdash; `data-start="6.0" data-duration="4.7"`,
  with `data-playback-rate="1.4191"` so it finishes exactly at 10.7.

Tie-line at **10.9**: `Not a promise to inspect. A gate that will not open.`

Seal at **12.4**: `The Enforcement Problem &rarr; Solved` + check.

Slug: `LiveReview &middot; scheduled reviews &amp; CI/CD gates`
