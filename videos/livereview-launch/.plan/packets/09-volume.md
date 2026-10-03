# Frame packet — 09-volume

Write exactly this one file:

    compositions/frames/09-volume.html

| field | value |
| --- | --- |
| `data-composition-id` | `09-volume` |
| `data-duration` | `9.0` |
| id prefix for every element | `09-volume-` |
| position in the film | 64.5s -> 73.5s of 270s |
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
Media: `assets/plates/p12_cofferdam.jpg`, full bleed. Water held back by fill.

Slug: `Upstream cofferdam at maximum elevation &middot; 1932`

Lines:
- **0.6** &mdash; 50px weight 400: `The higher velocity leads to`
- **2.4** &mdash; 72px weight 700: `a HUGE VOLUME of code.`
- **5.6** &mdash; 30px italic `#C9BFA8`: `And all of it is now standing behind one wall.`

**The one water-line beat in the film.** Add a 1px full-width rule,
`background:#EDE4D0`, `left:0; width:1920px; height:1px`, positioned at
`top:900px`, and translate it upward with `y: 0 -> -380` between **2.8** and
**8.2**, `ease:"none"` (so it visually rises from y=900 to y=520). Use `y`, never
`top`. Ride a 17px label on its right end &mdash; `right:96px`, same `y` tween,
`letter-spacing:.18em`, uppercase, `rgba(237,228,208,.55)`, reading `Reservoir`.
The rule and label are their own clips starting at 2.8.
