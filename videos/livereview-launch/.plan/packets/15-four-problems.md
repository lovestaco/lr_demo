# Frame packet — 15-four-problems

Write exactly this one file:

    compositions/frames/15-four-problems.html

| field | value |
| --- | --- |
| `data-composition-id` | `15-four-problems` |
| `data-duration` | `32.0` |
| id prefix for every element | `15-four-problems-` |
| position in the film | 122.5s -> 154.5s of 270s |
| act marker text | `V &middot; Four Questions` |
| grade stage | G0 — **do not apply it yourself**, the builder applies grades centrally after you finish |

## Layout

`problem-quad` — ONE frame holding four 8.0s sub-beats.
Four full-bleed `<img>` plates, each its own `clip` with its own
`data-start`/`data-duration`, cross-dissolving 0.5s into the next (overlap their
windows by 0.5s so there is no black gap).
Bottom scrim spans the whole frame (`data-start="0"`, full duration).
Per beat: a numeral+title line (26px, `letter-spacing:.22em`, `#C2703A`,
uppercase) and a question line (52px, weight 600, `#EDE4D0`, wraps to at most two
lines), both `left:140px; width:1500px`, question ending near `top:880px`.
Each beat's text is its own `clip` gated to that beat's window.
TALLY: at `right:96px; top:150px`, four 28x3px marks in a row with 10px gaps,
`background: rgba(237,228,208,.22)`. One mark per beat turns `#C2703A` when that
beat starts and STAYS — implement as four separate absolutely-positioned filled
marks, each a `clip` whose `data-start` is its beat's start and whose
`data-duration` runs to the END of the frame.
The SLUG changes per beat — four slug elements, each gated to its beat.

## Content
**Four 8.0s sub-beats in one 32.0s frame.** Follow the `problem-quad` geometry
above exactly.

| beat | window | plate | slug |
| --- | --- | --- | --- |
| 1 | 0.0 &ndash; 8.5 | `assets/plates/p16_cleavage.jpg` | `Pressure cleavage in the canyon wall &middot; 1932` |
| 2 | 8.0 &ndash; 16.5 | `assets/plates/p18_drillbit.jpg` | `Diamond drill bit lost in hole D200 W147 &middot; 1922` |
| 3 | 16.0 &ndash; 24.5 | `assets/plates/p11_recorders.jpg` | `Concrete control &middot; testing laboratory &middot; 1933` |
| 4 | 24.0 &ndash; 32.0 | `assets/plates/p19_controltower.jpg` | `From the head tower of the 150-ton cableway &middot; 1934` |

(Plate windows overlap by 0.5s so the cross-dissolve has something to dissolve
into. Slugs do NOT overlap &mdash; swap them cleanly at 8.0 / 16.0 / 24.0.)

Per beat, numeral+title enters at `beat+0.6`, question at `beat+1.8`, both hold
until the beat ends:

1. `&numero; 1 &middot; The Attention Problem` / `Which changes deserve your engineers' scarce attention?`
2. `&numero; 2 &middot; The Understanding Problem` / `How can your engineers keep intellectual control of the system?`
3. `&numero; 3 &middot; The Enforcement Problem` / `How do you make good review happen every time &mdash; without slowing the team down?`
4. `&numero; 4 &middot; The Control &amp; Improve Problem` / `How do you own your IP, your code, your data, your model interactions?`

If `&numero;` does not render, use `No.` &mdash; do not substitute a `#`.

The tally in the top-right is the viewer's map through this 32 seconds. Get it
right: four marks, one lighting per beat, none ever going out.
