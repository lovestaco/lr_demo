#!/bin/bash
# Part 0 after the render farm: SheepIt frames (zip) -> the one review video with audio, subtitles and frame numbers.
#
#     scripts/assemble_part0_sheepit.sh <frames.zip> <height>        # height 360 (draft) or 1080 (final)
#
#   a. tests the zip and extracts it into a NEW folder  build/frames/street_part0_sheepit_<height>p_raw/  (must not exist or be empty)
#   b. checks the frames: exactly END (build/street_part0_overlays.json, = 1101) images, numbered 1..END, no gaps, no extras, every
#      one decodes at <height*16/9> x <height>, none black (an all-black frame = a failed worker); the cue sheet must be for END frames too
#   c. makes the numbered set  build/frames/street_part0_sheepit_<height>p/f_NNNN.png  with hard links (no copies)
#   d. encodes the base video with ffmpeg (30 fps, libx264 -preset medium -crf 18 for 360p / 14 for 1080p, yuv420p, +faststart)
#      -> renders/street_part0_<height>p.mp4
#   e. 06_assemble.py street_part0 --height <height> --music assets/audio/music/bed_street.mp3 --music-once   (VO line 14 + SFX + music +
#      subtitles + frame-number burn-in; reads build/street_part0_cues.json)
#   f. moves the silent base and the clean mix to build/intermediate/ and leaves exactly ONE file: renders/street_part0_<height>p_mix_tc.mp4
# Nothing is deleted; a leftover renders/street_part0_<height>p* from an earlier run is moved to build/intermediate/ first.
# Test hooks (env): NAME, OV (overlays json), CUES, FRAMES (frames root), RENDERS (output folder), STOP_AFTER=extract|check|set|encode,
# DRY=1 (print d-f instead of running 06_assemble and the moves).
set -euo pipefail
cd "$(dirname "$0")/.."
ZIP=${1:?usage: assemble_part0_sheepit.sh <frames.zip> <height 360|1080>}
H=${2:?usage: assemble_part0_sheepit.sh <frames.zip> <height 360|1080>}
NAME=${NAME:-street_part0}
OV=${OV:-build/${NAME}_overlays.json}
CUES=${CUES:-build/${NAME}_cues.json}
FRAMES=${FRAMES:-build/frames}
RENDERS=${RENDERS:-renders}
die() { echo "ERROR: $*" >&2; exit 1; }
case "$H" in 360) CRF=18;; 1080) CRF=14;; *) die "height must be 360 or 1080, got '$H'";; esac
[ -f "$ZIP" ] || die "$ZIP not found"
[ -f "$OV" ] || die "$OV not found"
[ -f "$CUES" ] || die "$CUES not found (06_assemble needs the cue sheet of the build)"
RAW=$FRAMES/${NAME}_sheepit_${H}p_raw
SET=$FRAMES/${NAME}_sheepit_${H}p
END=$(python3 -I -c "import json;print(json.load(open('$OV'))['end'])")
CEND=$(python3 -I -c "import json;print(json.load(open('$CUES'))['frames'])")
[ "$END" -gt 1 ] 2>/dev/null || die "bad end frame '$END' in $OV"
[ "$CEND" = "$END" ] || die "the cue sheet $CUES is for $CEND frames, the overlays say $END (rebuild first)"
STAMP=$(date +%Y%m%d_%H%M%S)
echo "== part 0 ${H}p: frames 1-$END from $ZIP"

# ---- a. test + extract (into a new empty folder; -j: no sub-folders, nothing can land outside it)
unzip -tq "$ZIP" > /dev/null || die "the zip is damaged ($ZIP)"
[ -e "$RAW" ] && [ -n "$(ls -A "$RAW" 2>/dev/null)" ] && die "$RAW exists and is not empty (move it aside first)"
mkdir -p "$RAW"
unzip -q -j "$ZIP" -d "$RAW"
[ -z "$(find "$RAW" ! -type f ! -type d)" ] || die "the zip holds links or special files: $(find "$RAW" ! -type f ! -type d | head -3)"
echo "extracted: $(ls "$RAW" | wc -l) files into $RAW"
[ "${STOP_AFTER:-}" = extract ] && exit 0

# ---- b. frame count, size, gaps, extras, black frames
python3 -I - "$RAW" "$END" "$H" <<'PY' || die "frame check failed (see above)"
import os, re, sys
from PIL import Image, ImageStat
raw, end, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
w = h * 16 // 9
have, extra = {}, []
for n in sorted(os.listdir(raw)):
    m = re.fullmatch(r"(?:.*?)(\d+)\.(png|jpg|jpeg)", n, re.I)
    if not m:
        extra.append(n)
        continue
    have[int(m.group(1))] = n
want = range(1, end + 1)
gaps = [f for f in want if f not in have]
outside = sorted(f for f in have if f not in want)
bad = []
if gaps:
    bad.append(f"{len(gaps)} missing frame(s): {gaps[:12]}{' ...' if len(gaps) > 12 else ''}")
if outside or extra:
    bad.append(f"not exactly {end} frames: extra numbers {outside[:8]}, other files {extra[:5]}")
exts = {n.rsplit('.', 1)[1].lower() for n in have.values()}
if len(exts) > 1:
    bad.append(f"mixed frame formats {sorted(exts)}")
wrong, black = [], []
for f in want:
    if f not in have:
        continue
    try:
        im = Image.open(os.path.join(raw, have[f]))
        im.load()
    except Exception:                                                  # truncated / corrupt download
        wrong.append((f, "unreadable"))
        continue
    if im.size != (w, h):
        wrong.append((f, im.size))
    elif ImageStat.Stat(im.convert("L")).extrema[0][1] < 8:
        black.append(f)
if wrong:
    bad.append(f"{len(wrong)} frame(s) with the wrong size/unreadable (want {w}x{h}): {wrong[:6]}")
if black:
    bad.append(f"{len(black)} black frame(s): {black[:12]}")
print(f"frames: {len(want) - len(gaps)}/{end}; outside the range: {len(outside)}; other files: {extra[:5]}")
for b in bad:
    print("FAIL", b)
print("FRAME CHECK", "FAILED" if bad else "PASSED")
sys.exit(1 if bad else 0)
PY
[ "${STOP_AFTER:-}" = check ] && exit 0

# ---- c. the numbered set (hard links)
[ -e "$SET" ] && [ -n "$(ls -A "$SET" 2>/dev/null)" ] && die "$SET exists and is not empty (move it aside first)"
mkdir -p "$SET"
python3 -I - "$RAW" "$SET" "$END" <<'PY' || die "linking the frames failed"
import os, re, sys
raw, dst, end = sys.argv[1], sys.argv[2], int(sys.argv[3])
have = {}
for n in os.listdir(raw):
    m = re.fullmatch(r"(?:.*?)(\d+)\.(png|jpg|jpeg)", n, re.I)
    if m:
        have[int(m.group(1))] = n
ext = have[1].rsplit(".", 1)[1].lower()
for f in range(1, end + 1):
    os.link(os.path.join(raw, have[f]), os.path.join(dst, f"f_{f:04d}.{ext}"))
PY
echo "set: $(ls "$SET" | wc -l) frames in $SET"
[ "$(ls "$SET" | wc -l)" -eq "$END" ] || die "the set has $(ls "$SET" | wc -l) frames, expected $END"
[ "${STOP_AFTER:-}" = set ] && exit 0

# ---- d. the base video
EXT=$(ls "$SET" | sed -n '1s/.*\.//p')   # (not "| head -1": ls dies of SIGPIPE and pipefail+set -e aborts the script)
mkdir -p build/intermediate "$RENDERS"
for f in "$RENDERS/${NAME}_${H}p.mp4" "$RENDERS/${NAME}_${H}p_mix.mp4" "$RENDERS/${NAME}_${H}p_mix_tc.mp4"; do
  [ -f "$f" ] && { mv "$f" "build/intermediate/$(basename "${f%.mp4}")_prev_$STAMP.mp4"; echo "earlier $f moved to build/intermediate/"; }
done
ffmpeg -loglevel error -y -framerate 30 -i "$SET/f_%04d.$EXT" -c:v libx264 -preset medium -crf "$CRF" -pix_fmt yuv420p -movflags +faststart \
  "$RENDERS/${NAME}_${H}p.mp4" || die "ffmpeg encode failed"
echo "base video: $RENDERS/${NAME}_${H}p.mp4 ($(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$RENDERS/${NAME}_${H}p.mp4") frames)"
[ "${STOP_AFTER:-}" = encode ] && exit 0

# ---- e-f. audio, subtitles, frame numbers, one file
run() { if [ -n "${DRY:-}" ]; then echo "DRY: $*"; else "$@"; fi; }
run python3 scripts/06_assemble.py "$NAME" --height "$H" --music assets/audio/music/bed_street.mp3 --music-once
run mv "renders/${NAME}_${H}p.mp4" "build/intermediate/${NAME}_${H}p.mp4"
run mv "renders/${NAME}_${H}p_mix.mp4" "build/intermediate/${NAME}_${H}p_mix.mp4"
echo "== DONE"; ls -la "renders/${NAME}_${H}p_mix_tc.mp4" 2>/dev/null || true
