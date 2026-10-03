# Frame packet — 04-the-scalers

Write exactly this one file:

    compositions/frames/04-the-scalers.html

| field | value |
| --- | --- |
| `data-composition-id` | `04-the-scalers` |
| `data-duration` | `8.0` |
| id prefix for every element | `04-the-scalers-` |
| position in the film | 25.0s -> 33.0s of 270s |
| act marker text | `I &middot; The River` |
| grade stage | G0 — **do not apply it yourself**, the builder applies grades centrally after you finish |

## Layout

`card-then-film` — TWO `<video>` elements in the same 1440x1080
gate as `film-bleed`, stacked, each its own `clip`:
  1. the found 1931 intertitle card — plays ALONE with NO overlay text (it reads
     itself). Give it `data-start="0"` and the stated duration.
  2. the live-action clip — starts slightly BEFORE the card ends so they
     cross-dissolve (card `opacity 1 -> 0` and film `0 -> 1` over 0.5s, overlapping).
Only after the dissolve does your single gloss line appear over the film.
Gate hairlines, scrim, slug and act marker exactly as `film-bleed`.

## Content
Media, both in the gate, cross-dissolving:
1. `assets/archive/t_scalers_card.mp4` (4.20s) &mdash; `data-start="0" data-duration="3.6"`.
   It is an original 1931 intertitle reading *"High scalers swarmed over the
   1,000-foot cliffs preparing abutments for the dam."* &mdash; **no overlay text on it.**
2. `assets/archive/v_scalers_b.mp4` (5.00s) &mdash; `data-start="3.4" data-duration="4.6"`.
   Dissolve: card `opacity 1->0` at 3.4 over 0.5s, film `0->1` at 3.4 over 0.5s.

Slug: `Boulder Dam: The Official Picture &middot; 1931`

One gloss line only, over the film:
- **4.4** &mdash; 40px weight 400: `Somebody has to walk the wall before the concrete goes in.`

The bottom scrim should fade in with the film (`data-start="3.4"`), not sit over
the intertitle &mdash; the card is already black.
