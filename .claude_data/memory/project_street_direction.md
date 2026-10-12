---
name: project-street-direction
description: 2026-10-05 pivot of the LiveReview Spidey video to a movie-like city street tour (slides as graffiti/billboards/screens)
metadata:
  node_type: memory
  type: project
  originSessionId: f2127c4b-9447-417e-9ee3-f385fd69e341
  modified: 2026-10-05T06:55:55.867Z
---

On 2026-10-05 the user (and reviewer Shrijith) rejected the "Spidey in a dark studio pulling boards" concept as
unrealistic/"intern-made". New direction: a movie-quality Spider-Man city tour — each slide is part of the street
(graffiti wall, rooftop billboard, LED ticker, bus-stop/subway lightboxes, Times Square screen), he web-swings between
them; camera language like the films (aerial/drone tracking for swings, low-angle hero perches); <60 s if possible
(max 90 s), 720p renders, readability + per-frame quality first.

**Why:** Shrijith's shot theory — every frame communicates where/who/what/feeling non-verbally (wide = place,
medium = person, close-up = feeling); the studio had no "where".
**How to apply:** build in `miles/scripts/04_street.py` (see miles/CLAUDE.md "Street piece"); keep stylized
game-quality city (user chose over photoreal); keep badge, drop watch; finale tower stays, staged in the street.
User wants stronger Spider-Man animation — Mixamo Google sign-in popup needs the user to finish it (Claude can't
see the popup); any free mocap site with Google sign-in is approved.

Related: [[project-lr-demo-videos]], [[elevenlabs-free-tier-limits]]

**2026-10-06 v5 review rules (Shrijith + user):** max 1–2 direct location cuts in the whole film — every move is
visible travel (built that way in v5, 0 location cuts); blocks-tower finale (not the train); close-ups with feeling
(two-building over-the-shoulder shots); inverted hangs = comic tuck, not a limp body; finals at 1080p full quality.
User asked for "movie" polish: DOF, impact shakes, haze grade (`fx.cine_grade`). Plan + progress log:
`miles/plans/street_v5.md`.

**2026-10-08 part 2 split + review (user, Shrijith):** part 2 is cut into part2_a (S10–S15, `04_street_part2_a.py`,
own .blend) and part2_b (S16–S19, later; renamed part 3 = street_part3 on 2026-10-11, and 2a = part 2 = street_part2) "to go faster". Review asks that shaped 2a: shops next to each other in ONE
building with the board above both and the camera on that building only; human-only (left) and agent-only (right) in
one shot, human+agent its own shot; site A must read as a building; pedestrians must walk forward and wear different
clothes; sign copy must be grammatical; never use the word "efficiency"/"efficient" (wrong positioning — S19 line).
VO now comes from real per-line website takes (Generation 1) of the Mark voice.
