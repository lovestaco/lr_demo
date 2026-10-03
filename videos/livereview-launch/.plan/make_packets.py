#!/usr/bin/env python3
"""Emit one bounded dispatch packet per frame into .plan/packets/."""
import json, os, textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = json.load(open(os.path.join(ROOT, ".plan/frames.json")))
OUT = os.path.join(ROOT, ".plan/packets")
os.makedirs(OUT, exist_ok=True)

ACTS = {"I": "I &middot; The River", "II": "II &middot; The Belief",
        "III": "III &middot; The Rising Water", "IV": "IV &middot; The Cracks",
        "V": "V &middot; Four Questions", "VI": "VI &middot; The Inspection Layer",
        "VII": "VII &middot; The Dam Holds"}

GEO = {
"bleed": """`bleed` — one `<img>` plate, `position:absolute; inset:0; width:1920px;
height:1080px; object-fit:cover`, wrapped in nothing. Ken Burns `scale 1.055 -> 1.0`
over the whole frame, `ease:"none"`, `transform-origin:50% 50%`.
Bottom scrim div: `position:absolute; inset:0; width:1920px; height:1080px;
background: linear-gradient(180deg, rgba(11,10,8,0) 34%, rgba(11,10,8,.9) 100%);`
Text block: `left:140px; width:1400px`, lines stacked so the LAST line's baseline
region ends near `top:880px`. Work upward from there.""",

"film-bleed": """`film-bleed` — an archive `<video>` that is natively 1440x1080.
Wrap it in a gate div at `left:240px; top:0; width:1440px; height:1080px; overflow:hidden`,
with the video at `left:0; top:0; width:1440px; height:1080px; object-fit:cover`.
Root background `#0b0a08` fills the pillarbox columns.
Two 1px gate hairlines, `background: rgba(237,228,208,.20)`, full height, at
`left:240px` and `left:1679px`.
Same bottom scrim and text block as `bleed`. Ken Burns on the video element.""",

"split-right": """`split-right` — portrait plate `<img>` at
`left:1020px; top:0; width:900px; height:1080px; object-fit:cover`.
Left field is root background `#0b0a08` (0 -> 1020).
1px `#8A7F68` hairline, full height, at `left:1020px`.
Text block `left:140px; width:780px`, left-aligned, vertically composed around
the frame's mid-line (roughly `top:340px` to `top:760px`).
Ken Burns on the plate: `scale 1.05 -> 1.0`.
No bottom scrim needed (text sits on the dark field) — but DO keep the slug and
act marker.""",

"split-left": """`split-left` — mirror of split-right. Plate `<img>` at
`left:0; top:0; width:900px; height:1080px; object-fit:cover`.
1px `#8A7F68` hairline at `left:899px`.
Text block `left:1060px; width:760px`, left-aligned, composed around the mid-line.
Ken Burns on the plate. Keep slug and act marker.""",

"card-then-film": """`card-then-film` — TWO `<video>` elements in the same 1440x1080
gate as `film-bleed`, stacked, each its own `clip`:
  1. the found 1931 intertitle card — plays ALONE with NO overlay text (it reads
     itself). Give it `data-start="0"` and the stated duration.
  2. the live-action clip — starts slightly BEFORE the card ends so they
     cross-dissolve (card `opacity 1 -> 0` and film `0 -> 1` over 0.5s, overlapping).
Only after the dissolve does your single gloss line appear over the film.
Gate hairlines, scrim, slug and act marker exactly as `film-bleed`.""",

"card-then-bleed": """`card-then-bleed` — same two-element cross-dissolve as
`card-then-film`, except element 2 is a full-bleed `<img>` plate at
`inset:0; width:1920px; height:1080px; object-fit:cover` (NOT in the gate), and
element 1 is the 1440x1080 intertitle video in the gate.
When the card dissolves out, the gate hairlines must dissolve out with it —
give them the same `data-start`/`data-duration` as the card.""",

"problem-quad": """`problem-quad` — ONE frame holding four 8.0s sub-beats.
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
The SLUG changes per beat — four slug elements, each gated to its beat.""",

"answer": """`answer` — the modern layout. Root background `#0B0A08`.
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
opacity:1, duration:.5, ease:"power3.out"}`; `transform-origin:50% 50%`.""",

"recap": """`recap` — no media at all. Root background `#0B0A08`.
Heading `left:0; width:1920px; text-align:center; top:286px`, Inter 42px weight
500, `#E8EEFF`.
Four rows centred as a block: give the block `left:560px; width:800px`, rows at
`top:420/500/580/660px`, each 44px Inter weight 500 `#E8EEFF`, left-aligned, with
a 30px `#3B82F6` check glyph at `left:-52px` relative to the row.
Rows enter one at a time and all stay.""",
}


def esc(s):
    return s

def packet(f, body):
    p = os.path.join(OUT, "%02d-%s.md" % (f["n"], f["id"]))
    fid = "%02d-%s" % (f["n"], f["id"])
    head = textwrap.dedent("""\
    # Frame packet — {fid}

    Write exactly this one file:

        compositions/frames/{fid}.html

    | field | value |
    | --- | --- |
    | `data-composition-id` | `{fid}` |
    | `data-duration` | `{dur}` |
    | id prefix for every element | `{fid}-` |
    | position in the film | {start}s -> {end}s of 270s |
    | act marker text | `{act}` |
    | grade stage | {grade} — **do not apply it yourself**, the builder applies grades centrally after you finish |

    ## Layout

    {geo}

    ## Content
    """).format(fid=fid, dur=f["dur"], start=f["start"],
                end=round(f["start"] + f["dur"], 2), act=ACTS[f["act"]],
                grade=f["grade"], geo=GEO[f["layout"]])
    open(p, "w").write(head + body.rstrip() + "\n")
    return p


CONTENT = json.load(open(os.path.join(ROOT, ".plan/content.json")))
written = []
for f in PLAN["frames"]:
    if f["n"] == 1:
        continue  # reference frame, hand-built
    written.append(packet(f, CONTENT["%02d" % f["n"]]))
print("wrote %d packets" % len(written))
for w in written:
    print("  " + os.path.relpath(w, ROOT))
