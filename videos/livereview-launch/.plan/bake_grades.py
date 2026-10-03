#!/usr/bin/env python3
"""Bake the grade ladder into the media files and drop the runtime shaders.

Why: the media-treatment effects (grain / vignette / filmArtifacts) run as WebGL
shaders at capture time. On this machine that path is unusable — with the GPU the
context is lost and capture stalls; with SwiftShader it runs at ~0.06 fps. Every
treatment in this film is STATIC per element (no treatment animation anywhere), so
baking is equivalent in output and removes the cost entirely.

Writes graded copies beside the originals and rewrites each frame's `src` to point
at them, then strips `data-color-grading`. Originals are untouched.
"""
import json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = json.load(open(os.path.join(ROOT, ".plan/frames.json")))

# ffmpeg approximations of the five stages. Seeded noise keeps them deterministic.
CHAIN = {
 "G0": ("eq=saturation=0:contrast=0.97:brightness=0.025,"
        "curves=all='0/0.05 0.5/0.52 1/0.96',"
        "vignette=a=PI/4.4,"
        "noise=c0s=11:c0f=t+u:all_seed=20260401"),
 "G1": ("eq=saturation=0.45:contrast=0.99:brightness=0.015,"
        "colorbalance=rs=0.09:gs=0.02:bs=-0.07,"
        "curves=all='0/0.035 0.5/0.515 1/0.97',"
        "vignette=a=PI/5.0,"
        "noise=c0s=8:c0f=t+u:all_seed=20260401"),
 "G2": ("eq=saturation=0.62:contrast=1.0,"
        "colorbalance=rs=0.06:bs=-0.05,"
        "curves=all='0/0.025 0.5/0.51 1/0.98',"
        "vignette=a=PI/5.6,"
        "noise=c0s=6:c0f=t+u:all_seed=20260401"),
 "G3": ("eq=saturation=0.78:contrast=1.0,"
        "colorbalance=rs=0.035:bs=-0.03,"
        "vignette=a=PI/6.4,"
        "noise=c0s=4:c0f=t+u:all_seed=20260401"),
 "G4": ("eq=saturation=0.90:contrast=1.0,"
        "colorbalance=rs=0.018:bs=-0.015,"
        "vignette=a=PI/7.5,"
        "noise=c0s=2:c0f=t+u:all_seed=20260401"),
}

OUT_IMG = os.path.join(ROOT, "assets/plates_graded")
OUT_VID = os.path.join(ROOT, "assets/archive_graded")
os.makedirs(OUT_IMG, exist_ok=True)
os.makedirs(OUT_VID, exist_ok=True)

MEDIA = re.compile(r'<(img|video)\b([^>]*?)>', re.S)
ATTR = lambda n, s: re.search(r'\b%s="([^"]*)"' % n, s)

baked, skipped, failed = 0, 0, 0
for f in PLAN["frames"]:
    fid = "%02d-%s" % (f["n"], f["id"])
    path = os.path.join(ROOT, "compositions/frames/%s.html" % fid)
    if not os.path.exists(path):
        continue
    src_html = open(path).read()
    stage = f["grade"]
    edits = []
    for m in MEDIA.finditer(src_html):
        tag, attrs = m.group(1), m.group(2)
        if "data-color-grading" not in attrs:
            continue
        sm = ATTR("src", attrs)
        if not sm:
            continue
        rel = sm.group(1)
        chain = CHAIN.get(stage)
        if not chain:
            continue
        name = os.path.basename(rel)
        if tag == "img":
            dest_rel = "assets/plates_graded/%s" % name
            dest = os.path.join(OUT_IMG, name)
        else:
            dest_rel = "assets/archive_graded/%s" % name
            dest = os.path.join(OUT_VID, name)
        # one source can be referenced at two stages -> disambiguate by stage
        base, ext = os.path.splitext(name)
        dest_rel = dest_rel.replace(name, "%s.%s%s" % (base, stage, ext))
        dest = dest.replace(name, "%s.%s%s" % (base, stage, ext))

        if not os.path.exists(dest):
            srcfile = os.path.join(ROOT, rel)
            if not os.path.exists(srcfile):
                print("   MISSING SOURCE %s" % rel); failed += 1; continue
            if tag == "img":
                cmd = ["ffmpeg", "-v", "error", "-i", srcfile, "-vf", chain,
                       "-q:v", "3", dest, "-y"]
            else:
                cmd = ["ffmpeg", "-v", "error", "-i", srcfile, "-an", "-vf", chain,
                       "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                       "-pix_fmt", "yuv420p", dest, "-y"]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                print("   FFMPEG FAIL %s\n     %s" % (name, r.stderr[:200])); failed += 1; continue
            baked += 1
            print("   %s  %-34s -> %s" % (stage, name, os.path.basename(dest)))
        else:
            skipped += 1
        # rewrite this tag: new src, no shader payload
        na = attrs
        na = re.sub(r'\s*data-color-grading="[^"]*"', '', na)
        na = na.replace('src="%s"' % rel, 'src="%s"' % dest_rel)
        edits.append((m.start(2), m.end(2), na))
    for s, e, na in reversed(edits):
        src_html = src_html[:s] + na + src_html[e:]
    if edits:
        open(path, "w").write(src_html)

print("\nbaked %d, reused %d, failed %d" % (baked, skipped, failed))
left = 0
for f in PLAN["frames"]:
    p = os.path.join(ROOT, "compositions/frames/%02d-%s.html" % (f["n"], f["id"]))
    if os.path.exists(p):
        left += open(p).read().count("data-color-grading")
print("remaining runtime shader payloads: %d" % left)
sys.exit(1 if failed else 0)
