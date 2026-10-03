# Frame packet — 13-bigger-systems

Write exactly this one file:

    compositions/frames/13-bigger-systems.html

| field | value |
| --- | --- |
| `data-composition-id` | `13-bigger-systems` |
| `data-duration` | `8.5` |
| id prefix for every element | `13-bigger-systems-` |
| position in the film | 105.5s -> 114.0s of 270s |
| act marker text | `IV &middot; The Cracks` |
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
1. `assets/archive/t_blocks_card.mp4` (4.20s) &mdash; `data-start="0" data-duration="3.8"`.
   An original 1931 intertitle reading *"The Dam was constructed of an intricate
   pattern of individual blocks &mdash; each keyed to the next."* &mdash; **no overlay text.**
2. `assets/archive/v_blocks.mp4` (5.00s) &mdash; `data-start="3.6" data-duration="4.9"`.
   The actual block grid on the dam face. Dissolve as in frame 04.

Slug: `Boulder Dam: The Official Picture &middot; 1931`

One gloss line, over the film:
- **4.6** &mdash; 44px weight 400: `More code means bigger systems &mdash; and more interconnections.`

Scrim fades in with the film (`data-start="3.6"`).
