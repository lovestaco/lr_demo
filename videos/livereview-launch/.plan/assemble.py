#!/usr/bin/env python3
"""Assemble index.html from .plan/frames.json. Idempotent — safe to re-run."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = json.load(open(os.path.join(ROOT, ".plan/frames.json")))
FR = PLAN["frames"]
TOTAL = PLAN["total"]

missing = []
for f in FR:
    fid = "%02d-%s" % (f["n"], f["id"])
    if not os.path.exists(os.path.join(ROOT, "compositions/frames/%s.html" % fid)):
        missing.append(fid)
if missing:
    print("MISSING %d frame file(s):" % len(missing))
    for m in missing:
        print("   " + m)
    if "--force" not in sys.argv:
        sys.exit(1)

scenes = []
for i, f in enumerate(FR):
    fid = "%02d-%s" % (f["n"], f["id"])
    scenes.append(
        '      <div id="el-{fid}" class="scene" data-composition-id="{fid}"\n'
        '           data-composition-src="compositions/frames/{fid}.html"\n'
        '           data-start="{s}" data-duration="{d}" data-track-index="{t}"></div>'
        .format(fid=fid, s=f["start"], d=f["dur"], t=i % 2))

html = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1920, height=1080">
    <title>LiveReview — The Inspection Layer</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js" integrity="sha384-sG0Hv1tP1lZCk9KQmrIbY/XNwi+OY84GQqhMscbnsoBFqAz8KNCil1kvfL3Hbbk2" crossorigin="anonymous"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body {
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: #000;
      }
      #root {
        position: relative;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: #0b0a08;
      }
      .scene {
        position: absolute;
        inset: 0;
        width: 100%%;
        height: 100%%;
      }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="%(total)s"
         data-width="1920" data-height="1080">
%(scenes)s

      <audio id="el-bgm" src="assets/bgm/bed-274.mp3"
             data-start="0" data-duration="%(total)s" data-track-index="9" data-volume="0.92"></audio>
    </div>

    <script>
      // Root timeline. Frame-to-frame handoffs are hard cuts by design: this is
      // an archival documentary, not a montage. The only job here is to register
      // the master timeline and anchor its full span so Studio and the renderer
      // both see 270s.
      window.__timelines = window.__timelines || {};
      (function () {
        var tl = gsap.timeline({ paused: true });
        tl.to({}, { duration: %(total)s }, 0);
        window.__timelines["main"] = tl;
      })();
    </script>
  </body>
</html>
''' % {"total": TOTAL, "scenes": "\n\n".join(scenes)}

open(os.path.join(ROOT, "index.html"), "w").write(html)
print("assembled index.html — %d scenes, %.1fs" % (len(FR), TOTAL))
last = FR[-1]
print("last scene ends at %.1f (root duration %.1f)" % (last["start"] + last["dur"], TOTAL))
