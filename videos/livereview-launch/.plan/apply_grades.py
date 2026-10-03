#!/usr/bin/env python3
"""Apply the grade ladder to archival media only. Product clips are never graded.

Usage: apply_grades.py [frame-number ...]   (default: all that exist)
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = json.load(open(os.path.join(ROOT, ".plan/frames.json")))

GRADE = {
 "G0": '{"preset":"mono-fade","intensity":1,"adjust":{"exposure":0.06,"shadows":0.18,"blacks":0.08},"details":{"vignette":0.32,"vignetteFeather":0.78,"grain":0.42,"grainSize":0.5},"effects":{"filmArtifacts":0.50}}',
 "G1": '{"preset":"vintage-wash","intensity":0.55,"details":{"vignette":0.50,"vignetteFeather":0.7,"grain":0.32,"grainSize":0.5},"effects":{"filmArtifacts":0.30}}',
 "G2": '{"preset":"vintage-wash","intensity":0.35,"details":{"vignette":0.42,"vignetteFeather":0.7,"grain":0.22,"grainSize":0.5},"effects":{"filmArtifacts":0.18}}',
 "G3": '{"preset":"vintage-wash","intensity":0.20,"details":{"vignette":0.34,"vignetteFeather":0.7,"grain":0.14,"grainSize":0.5},"effects":{"filmArtifacts":0.08}}',
 "G4": '{"preset":"vintage-wash","intensity":0.10,"details":{"vignette":0.26,"vignetteFeather":0.7,"grain":0.07,"grainSize":0.5}}',
}

# Product captures live in assets/ as clipNN_*.mp4 — never graded.
PRODUCT = re.compile(r'src="assets/(clip[0-9]|logo\.svg|brand-)', re.I)
MEDIA = re.compile(r'<(img|video)\b[^>]*\bid="([^"]+)"[^>]*>', re.I)

want = set(int(a) for a in sys.argv[1:] if a.isdigit())
applied = skipped = failed = 0

for f in PLAN["frames"]:
    if want and f["n"] not in want:
        continue
    fid = "%02d-%s" % (f["n"], f["id"])
    path = "compositions/frames/%s.html" % fid
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        print("  -- %s  (not built yet)" % fid)
        continue
    stage = f["grade"]
    if stage not in GRADE:
        print("  == %s  %s — clean, no treatment" % (fid, stage))
        continue
    src = open(full).read()
    for m in MEDIA.finditer(src):
        tag, eid = m.group(1), m.group(2)
        if PRODUCT.search(m.group(0)):
            print("     skip product clip  %s" % eid)
            skipped += 1
            continue
        r = subprocess.run(
            ["npx", "hyperframes", "media-treatment", "--file", path,
             "--selector", '[id="%s"]' % eid, "--grading", GRADE[stage],
             "--apply", "--json"],
            cwd=ROOT, capture_output=True, text=True)
        ok = '"ok": true' in r.stdout or '"ok":true' in r.stdout
        if ok:
            print("     %s  %-40s %s" % (stage, eid, tag))
            applied += 1
        else:
            err = re.search(r'"error":\s*"([^"]+)"', r.stdout + r.stderr)
            print("     FAIL %-40s %s" % (eid, err.group(1) if err else r.stdout[:120]))
            failed += 1

print("\napplied %d, skipped %d product clips, failed %d" % (applied, skipped, failed))
sys.exit(1 if failed else 0)
