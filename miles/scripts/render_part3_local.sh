#!/bin/bash
# Part 3 review render on this machine (no render farm): 720p, 16 samples, ray-traced reflections, motion blur, JPEG frames kept in
# build/frames/street_part3_720p/, then video + VO + SFX + music + subtitles + frame-number burn-in (renders/street_part3_720p_mix_tc.mp4).
#   nohup scripts/render_part3_local.sh > /tmp/part3_local.log 2>&1 &
# Resumable: frames that exist are skipped. Frames 1..B-1 are the 2D S16/S17 boards (05b), B..END the 3D (two Blender workers).
# BLEND defaults to the suit-fix copy; override:  BLEND=build/street_part3.blend scripts/render_part3_local.sh
export PATH=/home/lovestaco/.local/bin:$PATH
cd "$(dirname "$0")/.." || exit 1
NAME=street_part3
BLEND=${BLEND:-build/street_part3_suitfix.blend}
H=${H:-720}
OUT=build/frames/${NAME}_${H}p
BL=/snap/bin/blender
END=$(python3 -c "import json;print(json.load(open('build/${NAME}_overlays.json'))['end'])")
B0=$(python3 -c "import json;print(json.load(open('build/${NAME}_overlays.json'))['boards']['s17'][1]+1)")   # first 3D frame
MID=${MID:-2065}                                                                                           # split by cost: S18 is the heaviest stretch
mkdir -p "$OUT"
echo "== $(date +%T) 3D frames $B0-$END (workers: $B0-$MID | $((MID+1))-$END), boards 1-$((B0-1)), blend $BLEND"
FLAGS="--h $H --samples 16 --motion-blur"
python3 scripts/05b_street_part3_boards.py "$OUT" $NAME > /tmp/part3_boards.log 2>&1 &
PB=$!
$BL -b "$BLEND" --python scripts/05c_render_range.py -- "$OUT" $B0-$MID $FLAGS > /tmp/part3_w1.log 2>&1 &
P1=$!
$BL -b "$BLEND" --python scripts/05c_render_range.py -- "$OUT" $((MID+1))-$END $FLAGS > /tmp/part3_w2.log 2>&1 &
P2=$!
wait $PB $P1 $P2
echo "== $(date +%T) render processes done"
miss=0
for ((f=1; f<=END; f++)); do printf -v p "$OUT/f_%04d.jpg" "$f"; [ -s "$p" ] || { echo "MISSING $f"; miss=$((miss+1)); }; done
[ "$miss" -eq 0 ] || { echo "INCOMPLETE: $miss frames missing (re-run this script to fill them)"; exit 1; }
echo "== all $END frames present"
python3 scripts/06c_street_part2_3_post.py "$OUT" $NAME --height $H || exit 1
python3 scripts/06_assemble.py $NAME --height $H --music assets/audio/music/bed_street.mp3 --music-once || exit 1
# one deliverable: the frame-numbered file with audio; the rest are intermediates
mkdir -p build/intermediate
for f in renders/${NAME}_${H}p.mp4 renders/${NAME}_${H}p_mix.mp4; do [ -f "$f" ] && mv "$f" build/intermediate/; done
ls -la renders/${NAME}_${H}p_mix_tc.mp4
echo "== $(date +%T) DONE"
