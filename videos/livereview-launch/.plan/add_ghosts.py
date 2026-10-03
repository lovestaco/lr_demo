#!/usr/bin/env python3
"""Insert the archival 'ghost' backdrop into each answer frame (18-21).

Each answer frame carries the SAME plate as its matching problem beat in frame
15, at low opacity behind the product window. The grade ladder acts on it, so
the gradual vintage->modern restoration is actually visible during the answers,
and each answer visually rhymes back to the problem it solves.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GHOST = {
    "18-answer-attention":     ("p16_cleavage",    17.5),
    "19-answer-understanding": ("p18_drillbit",    17.5),
    "20-answer-enforcement":   ("p11_recorders",   17.5),
    "21-answer-control":       ("p19_controltower", 17.5),
}

CSS = '''
    /* ---- archival ghost: the problem's own plate, recovering colour ---- */
    [id="{fid}-ghost"] {{
      position: absolute;
      inset: 0;
      width: 1920px;
      height: 1080px;
      object-fit: cover;
      opacity: 0.26;
      transform-origin: 50% 50%;
    }}
    [id="{fid}-ghostscrim"] {{
      position: absolute;
      inset: 0;
      width: 1920px;
      height: 1080px;
      background: radial-gradient(ellipse at 50% 52%,
        rgba(11, 10, 8, 0.86) 0%, rgba(11, 10, 8, 0.96) 72%);
    }}
'''

MARKUP = '''    <img id="{fid}-ghost" class="clip" data-start="0" data-duration="{dur}" data-track-index="0" src="assets/plates/{plate}.jpg" alt="">
    <div id="{fid}-ghostscrim" class="clip" data-start="0" data-duration="{dur}" data-track-index="0"></div>
'''

TWEEN = '''      /* Ghost backdrop drifts slowly; it is atmosphere, never a focal point. */
      tl.fromTo($("ghost"), {{ scale: 1.06 }}, {{ scale: 1.0, duration: {dur}, ease: "none" }}, 0);

'''

done = []
for fid, (plate, dur) in GHOST.items():
    path = os.path.join(ROOT, "compositions/frames/%s.html" % fid)
    if not os.path.exists(path):
        print("  -- %s not built yet" % fid)
        continue
    src = open(path).read()
    if "-ghost\"" in src:
        print("  == %s already has a ghost" % fid)
        continue

    # CSS: append just before the closing </style>
    src = src.replace("  </style>", CSS.format(fid=fid) + "  </style>", 1)

    # Markup: immediately after the opening #root div, so it sits behind everything
    m = re.search(r'(<div\b[^>]*\bid="root"[^>]*>\n)', src)
    if not m:
        print("  !! %s: could not find #root" % fid)
        continue
    src = src[:m.end()] + MARKUP.format(fid=fid, dur=dur, plate=plate) + src[m.end():]

    # Tween: just before the timeline registration
    m2 = re.search(r'(\n\s*window\.__timelines = window\.__timelines)', src)
    if not m2:
        print("  !! %s: could not find timeline registration" % fid)
        continue
    src = src[:m2.start()] + "\n" + TWEEN.format(dur=dur) + src[m2.start():].lstrip("\n")

    open(path, "w").write(src)
    print("  ++ %s  <- %s" % (fid, plate))
    done.append(fid)

print("\npatched %d answer frame(s)" % len(done))
