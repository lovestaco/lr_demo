# LiveReview — standalone web player

The launch film as **real HTML + JS animation** — not a video, and not a slideshow of stills.

Each scene is the original HyperFrames composition (its own `<style>` and its own GSAP timeline).
This project mounts all 19 of them, nests their timelines into one master clock, applies the scene
transitions, and keeps the product-footage videos in sync with that clock.

## Run it

```bash
npm install
npm run dev          # http://127.0.0.1:5173
```

Build a static copy you can host anywhere:

```bash
npm run build        # -> dist/
npm run preview      # serves dist/ at http://127.0.0.1:4173
```

> It has to be **served over http** — opening `index.html` as a `file://` URL will not work,
> because the player `fetch()`es each scene and browsers block that on the file protocol.
> `npm run dev` is the one-liner.

## Controls

| Input | Action |
| --- | --- |
| `Space` / Play button | Play / pause |
| `←` `→` | Skip 5 seconds |
| `F` | Full screen |
| Scrubber | Seek anywhere |
| Ticks on the scrubber | Jump to a scene — tall blue ticks are the act boundaries |
| `?t=90` | Deep-link a moment, in seconds |
| `?t=90&play=1` | Deep-link and start playing |

## Layout

```
index.html            player shell + chrome
src/player.js         the runtime: mount scenes, nest timelines, sync video
src/spec.json         frame windows + video cues, extracted from the built composition
src/transitions.js    the scene transitions, verbatim from the composition
public/frames/        the 19 scene compositions, exactly as authored
public/assets/        fonts, logos, stills, product footage
public/capture/       landing-page assets referenced by some scenes
```

## How it works

1. For each scene, fetch its HTML and clone the `<template>` into a positioned `.scene` div.
2. Re-create its inline `<script>` nodes so they execute (cloned scripts never run), which
   registers that scene's timeline on `window.__timelines[<id>]`.
3. Unpause each scene timeline and nest it into the master at its start time. **A paused child
   never advances inside a parent** — that is the single easiest thing to get wrong here.
4. Gate each scene's `visibility` to its own window, so it cannot fight the transition tweens,
   which animate `opacity` / `scale` / `x` / `filter`.
5. Drive everything from one `requestAnimationFrame` clock; videos are seeked to match and only
   corrected when they drift more than ~0.18s.

## Notes

- **Silent by design.** The film carries its meaning visually; there is no audio track at all.
- **1920x1080**, scaled to fit the window. The stage is a fixed size, so the layout is identical
  to the rendered MP4.
- The scenes under `public/frames/` are the same files the MP4 renders from. Edit one and reload —
  it is the real composition, not an export of it.
