#!/usr/bin/env python3
"""Fix the three structural lint error classes across every frame.

1. root_missing_dimensions     -> add data-width/data-height to each frame #root
2. media_missing_data_start    -> every <img>/<video> gets class="clip" + timing
3. video_nested_in_timed_element / nested_media_start_basis_ambiguous
                               -> any wrapper holding timed media is pinned to
                                  data-start="0" for the frame's full duration,
                                  so the child's data-start needs no offset.
                                  The wrapper's own reveal stays a GSAP tween.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = json.load(open(os.path.join(ROOT, ".plan/frames.json")))

TAG = re.compile(r'<(div|img|video)\b([^>]*?)(/?)>', re.S)
ATTR = lambda name, s: re.search(r'\b%s="([^"]*)"' % name, s)


def set_attr(attrs, name, value):
    m = ATTR(name, attrs)
    if m:
        return attrs[:m.start(1)] + value + attrs[m.end(1):]
    return attrs.rstrip() + ' %s="%s"' % (name, value)


def has_class_clip(attrs):
    m = ATTR("class", attrs)
    return bool(m and "clip" in m.group(1).split())


def add_class_clip(attrs):
    m = ATTR("class", attrs)
    if m:
        if "clip" in m.group(1).split():
            return attrs
        return attrs[:m.start(1)] + (m.group(1) + " clip").strip() + attrs[m.end(1):]
    return attrs.rstrip() + ' class="clip"'


changed_files = 0
for f in PLAN["frames"]:
    fid = "%02d-%s" % (f["n"], f["id"])
    path = os.path.join(ROOT, "compositions/frames/%s.html" % fid)
    if not os.path.exists(path):
        print("  -- %s not built" % fid)
        continue
    src = open(path).read()
    orig = src
    dur = str(f["dur"])
    notes = []

    # --- 1. root dimensions -------------------------------------------------
    m = re.search(r'<div\b([^>]*\bid="root"[^>]*)>', src)
    if m and not ATTR("data-width", m.group(1)):
        new = set_attr(set_attr(m.group(1), "data-width", "1920"), "data-height", "1080")
        src = src[:m.start(1)] + new + src[m.end(1):]
        notes.append("root-dims")

    # --- 2/3. media + wrappers ---------------------------------------------
    # Which element ids are wrappers that contain timed media? Find <video>/<img>
    # that sit inside a <div ...> that itself carries data-start.
    # Simplest robust pass: any div whose data-start is non-zero AND which
    # contains a media tag before its matching close gets pinned to 0/full.
    out = []
    pos = 0
    media_seen = 0
    for mt in TAG.finditer(src):
        tag, attrs = mt.group(1), mt.group(2)
        newattrs = attrs
        if tag in ("img", "video"):
            media_seen += 1
            if not has_class_clip(newattrs):
                newattrs = add_class_clip(newattrs)
                notes.append("clip+%s" % (ATTR("id", attrs).group(1) if ATTR("id", attrs) else tag))
            if not ATTR("data-start", newattrs):
                newattrs = set_attr(newattrs, "data-start", "0")
                newattrs = set_attr(newattrs, "data-duration", dur)
                notes.append("start+%s" % (ATTR("id", attrs).group(1) if ATTR("id", attrs) else tag))
            if not ATTR("data-track-index", newattrs):
                newattrs = set_attr(newattrs, "data-track-index", "0")
        if newattrs != attrs:
            out.append((mt.start(2), mt.end(2), newattrs))
    for s, e, new in reversed(out):
        src = src[:s] + new + src[e:]

    # Pin wrappers: a div carrying data-start that also wraps media.
    def pin_wrappers(text):
        hits = []
        for mt in re.finditer(r'<div\b([^>]*?)>', text):
            a = mt.group(1)
            ds = ATTR("data-start", a)
            if not ds:
                continue
            # does a media tag follow before the next </div> at this nesting?
            tail = text[mt.end():mt.end() + 6000]
            if not re.search(r'<(video|img)\b', tail.split("</div>")[0] if "</div>" in tail else tail):
                continue
            if ds.group(1) != "0" or (ATTR("data-duration", a) and ATTR("data-duration", a).group(1) != dur):
                na = set_attr(set_attr(a, "data-start", "0"), "data-duration", dur)
                hits.append((mt.start(1), mt.end(1), na))
        for s, e, na in reversed(hits):
            text = text[:s] + na + text[e:]
            notes.append("pin-wrapper")
        return text

    src = pin_wrappers(src)

    if src != orig:
        open(path, "w").write(src)
        changed_files += 1
        print("  ++ %-24s %s" % (fid, ", ".join(sorted(set(notes)))))
    else:
        print("  == %-24s ok" % fid)

print("\nchanged %d file(s)" % changed_files)
