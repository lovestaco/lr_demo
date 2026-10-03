# Frame packet — 18-answer-attention

Write exactly this one file:

    compositions/frames/18-answer-attention.html

| field | value |
| --- | --- |
| `data-composition-id` | `18-answer-attention` |
| `data-duration` | `17.5` |
| id prefix for every element | `18-answer-attention-` |
| position in the film | 169.0s -> 186.5s of 270s |
| act marker text | `VI &middot; The Inspection Layer` |
| grade stage | G1 — **do not apply it yourself**, the builder applies grades centrally after you finish |

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
Layout `answer`. Grade G1 (builder applies).

Statement (Inter 42px/600, at **0.4**):
`LiveReview ranks every hunk by blast radius and review priority.`

Window opens at **1.4**.

Product clip: `assets/clip05_blast.mp4` (8.00s), `data-start="2.0"
data-duration="8.0"`, `object-fit:contain`.

Tie-line (Playfair 26px italic, at **10.8**):
`The wall, mapped. The dangerous sections lit.`

Seal at **12.4**, Inter 40px/700: `The Attention Problem &rarr; Solved` then a
check glyph. Enter with `{opacity:0, y:14}` -> `{opacity:1, y:0, duration:.5,
ease:"power3.out"}`, then a single `scale 1 -> 1.05 -> 1` pop finishing by 14.2.
It must be fully resolved with at least 3.3s of hold left.

Slug: `LiveReview &middot; blast radius &amp; review priority` in
`rgba(232,238,255,.42)`.
