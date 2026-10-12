#!/bin/bash
# Part 3 (v2) after the render farm: SheepIt frames (zip) + the 2D boards -> the one review video with audio, subtitles and frame numbers.
#
#     scripts/assemble_part3_sheepit.sh <frames.zip> <height>        # height 360 (draft) or 1080 (final)
#
#   a. tests the zip and extracts it into a NEW folder  build/frames/street_part3_v2_sheepit_<height>p_raw/  (must not exist or be empty)
#   b. checks the 3D frames: exactly B..END present (B = first 3D frame, END from build/street_part3_overlays.json), no gaps,
#      every PNG decodes at the right size (<height*16/9> x <height>), none black (an all-black frame = a failed worker)
#   c. builds the numbered set  build/frames/street_part3_v2_<height>p/f_NNNN.*  : the 2D boards 1..B-1 (S16/S17, from
#      build/frames/street_part3_v2_boards_{720|1080}/, made by 05b; 360p uses the 720 boards, 06c scales them) + the farm's frames
#      B..END, all hard links (no copies)
#   d. encodes the base video (06c: renders/street_part3_<height>p.mp4)
#   e. 06_assemble.py street_part3 --height <height> --music assets/audio/music/bed_street.mp3 --music-once  (VO + SFX + music +
#      subtitles + frame-number burn-in)
#   f. moves the silent base and the clean mix to build/intermediate/ (named ..._v2_...); leaves exactly ONE file:
#      renders/street_part3_v2_<height>p_mix_tc.mp4. (renders/street_part3_720p_mix_tc.mp4, the old one, is never touched.)
# Nothing is deleted; a leftover renders/street_part3_<height>p* from an earlier run is moved to build/intermediate/ first.
# Test hooks (env): NAME, OV (overlays json), FRAMES (frames root), STOP_AFTER=extract|check|set|encode, DRY=1 (print d-f instead of running).
set -euo pipefail
cd "$(dirname "$0")/.."
ZIP=${1:?usage: assemble_part3_sheepit.sh <frames.zip> <height 360|1080>}
H=${2:?usage: assemble_part3_sheepit.sh <frames.zip> <height 360|1080>}
NAME=${NAME:-street_part3}
OV=${OV:-build/${NAME}_overlays.json}
FRAMES=${FRAMES:-build/frames}
die() { echo "ERROR: $*" >&2; exit 1; }
case "$H" in 360|1080) ;; *) die "height must be 360 or 1080 (the old 720p video stays as it is), got '$H'";; esac
[ -f "$ZIP" ] || die "$ZIP not found"
[ -f "$OV" ] || die "$OV not found"
BH=720; [ "$H" = 1080 ] && BH=1080
RAW=$FRAMES/${NAME}_v2_sheepit_${H}p_raw
SET=$FRAMES/${NAME}_v2_${H}p
BOARDS=$FRAMES/${NAME}_v2_boards_${BH}
read -r B0 END < <(python3 -I -c "import json;o=json.load(open('$OV'));print(o['boards']['s17'][1]+1, o['end'])")
[ "$END" -gt "$B0" ] 2>/dev/null || die "bad frame range $B0-$END in $OV"
STAMP=$(date +%Y%m%d_%H%M%S)
echo "== part 3 v2 ${H}p: 3D frames $B0-$END from $ZIP, boards 1-$((B0 - 1)) from $BOARDS"

# ---- a. test + extract (into a new empty folder; -j: no sub-folders, nothing can land outside it)
unzip -tq "$ZIP" > /dev/null || die "the zip is damaged ($ZIP)"
[ -e "$RAW" ] && [ -n "$(ls -A "$RAW" 2>/dev/null)" ] && die "$RAW exists and is not empty (move it aside first)"
mkdir -p "$RAW"
unzip -q -j "$ZIP" -d "$RAW"
[ -z "$(find "$RAW" ! -type f ! -type d)" ] || die "the zip holds links or special files: $(find "$RAW" ! -type f ! -type d | head -3)"
echo "extracted: $(ls "$RAW" | wc -l) files into $RAW"
[ "${STOP_AFTER:-}" = extract ] && exit 0

# ---- b. frame count, size, gaps, black frames
python3 -I - "$RAW" "$B0" "$END" "$H" <<'PY' || die "frame check failed (see above)"
import os, re, sys
from PIL import Image, ImageStat
raw, b0, end, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
w = h * 16 // 9
have, extra = {}, []
for n in sorted(os.listdir(raw)):
    m = re.fullmatch(r"(?:.*?)(\d+)\.(png|jpg|jpeg)", n, re.I)
    if not m:
        extra.append(n)
        continue
    have[int(m.group(1))] = n
want = range(b0, end + 1)
gaps = [f for f in want if f not in have]
outside = sorted(f for f in have if f not in want)
bad = []
if gaps:
    bad.append(f"{len(gaps)} missing frame(s): {gaps[:12]}{' ...' if len(gaps) > 12 else ''}")
wrong, black = [], []
for f in want:
    if f not in have:
        continue
    try:
        im = Image.open(os.path.join(raw, have[f]))
        im.load()
    except Exception as e:                                             # truncated / corrupt download
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
print(f"frames: {len(want) - len(gaps)}/{len(want)} of {b0}-{end}; outside the range (ignored): {len(outside)} {outside[:5]}; other files: {extra[:5]}")
for b in bad:
    print("FAIL", b)
print("FRAME CHECK", "FAILED" if bad else "PASSED")
sys.exit(1 if bad else 0)
PY
[ "${STOP_AFTER:-}" = check ] && exit 0

# ---- c. the numbered set: boards 1..B-1 + the farm's B..END (hard links)
[ -e "$SET" ] && [ -n "$(ls -A "$SET" 2>/dev/null)" ] && die "$SET exists and is not empty (move it aside first)"
mkdir -p "$SET"
for ((f = 1; f < B0; f++)); do
  printf -v p "$BOARDS/f_%04d.jpg" "$f"
  [ -s "$p" ] || die "board frame $p is missing (run scripts/05b_street_part3_boards.py $BOARDS $NAME --h $BH)"
  ln "$p" "$SET/$(basename "$p")"
done
python3 -I - "$RAW" "$SET" "$B0" "$END" <<'PY' || die "linking the farm's frames failed"
import os, re, sys
raw, dst, b0, end = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
have = {}
for n in os.listdir(raw):
    m = re.fullmatch(r"(?:.*?)(\d+)\.(png|jpg|jpeg)", n, re.I)
    if m:
        have[int(m.group(1))] = n
for f in range(b0, end + 1):
    os.link(os.path.join(raw, have[f]), os.path.join(dst, f"f_{f:04d}.{have[f].rsplit('.', 1)[1].lower()}"))
PY
echo "set: $(ls "$SET" | wc -l) frames in $SET"
[ "$(ls "$SET" | wc -l)" -eq "$END" ] || die "the set has $(ls "$SET" | wc -l) frames, expected $END"
[ "${STOP_AFTER:-}" = set ] && exit 0

# ---- d-f. video, audio, one file
run() { if [ -n "${DRY:-}" ]; then echo "DRY: $*"; else "$@"; fi; }
mkdir -p build/intermediate
for f in renders/${NAME}_${H}p.mp4 renders/${NAME}_${H}p_mix.mp4 renders/${NAME}_${H}p_mix_tc.mp4; do
  [ -f "$f" ] && { run mv "$f" "build/intermediate/$(basename "${f%.mp4}")_prev_$STAMP.mp4"; echo "earlier $f moved to build/intermediate/"; }
done
run python3 scripts/06c_street_part2_3_post.py "$SET" "$NAME" --height "$H"
[ "${STOP_AFTER:-}" = encode ] && exit 0
run python3 scripts/06_assemble.py "$NAME" --height "$H" --music assets/audio/music/bed_street.mp3 --music-once
run mv "renders/${NAME}_${H}p.mp4" "build/intermediate/${NAME}_v2_${H}p.mp4"
run mv "renders/${NAME}_${H}p_mix.mp4" "build/intermediate/${NAME}_v2_${H}p_mix.mp4"
run mv "renders/${NAME}_${H}p_mix_tc.mp4" "renders/${NAME}_v2_${H}p_mix_tc.mp4"
echo "== DONE"; ls -la "renders/${NAME}_v2_${H}p_mix_tc.mp4" 2>/dev/null || true
