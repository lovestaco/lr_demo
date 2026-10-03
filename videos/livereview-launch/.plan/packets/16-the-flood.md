# Frame packet — 16-the-flood

Write exactly this one file:

    compositions/frames/16-the-flood.html

| field | value |
| --- | --- |
| `data-composition-id` | `16-the-flood` |
| `data-duration` | `9.5` |
| id prefix for every element | `16-the-flood-` |
| position in the film | 154.5s -> 164.0s of 270s |
| act marker text | `V &middot; Four Questions` |
| grade stage | G0 — **do not apply it yourself**, the builder applies grades centrally after you finish |

## Layout

`card-then-bleed` — same two-element cross-dissolve as
`card-then-film`, except element 2 is a full-bleed `<img>` plate at
`inset:0; width:1920px; height:1080px; object-fit:cover` (NOT in the gate), and
element 1 is the 1440x1080 intertitle video in the gate.
When the card dissolves out, the gate hairlines must dissolve out with it —
give them the same `data-start`/`data-duration` as the card.

## Content
**The darkest beat in the film.** Layout `card-then-bleed`.

Media:
1. `assets/archive/t_menace_card.mp4` (4.50s) in the 1440x1080 gate,
   `data-start="0" data-duration="3.6"`. An original 1931 intertitle reading
   *"&mdash; its turbid floods, an ever present menace to life and property &mdash;"*.
   **No overlay text on it.** Let it land on its own.
2. `assets/plates/p21_flood_portal.jpg` FULL BLEED (`inset:0; 1920x1080;
   object-fit:cover`), `data-start="3.4" data-duration="6.1"`. Workers scrambling
   in water and wreckage. Cross-dissolve at 3.4 over 0.5s; the gate hairlines
   dissolve out with the card.
   Ken Burns on the plate: `scale 1.0 -> 1.08` from 3.4 to 9.5, `ease:"none"`.

Slug: swap at 3.4 from `Boulder Dam: The Official Picture &middot; 1931` to
`Flash flood &middot; outlet portal, diversion tunnel No. 2` (two slug clips).

Lines over the plate:
- **4.2** &mdash; 72px weight 700, `#C2703A`: `AUGUST 31, 1932`
- **6.0** &mdash; 38px weight 400, `#EDE4D0`: `The water found the gap. Nobody was watching that section.`
