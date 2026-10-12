#!/bin/bash
# Part 0 draft render on this machine (no render farm): 360p, 8 samples, no ray-traced reflections, JPEG frames kept in
# build/frames/street_part0_360p/, then video + VO + SFX + music + subtitles + frame-number burn-in (renders/street_part0_360p_mix_tc.mp4).
#   flock /tmp/claude-1000/gpu.lock scripts/render_part0_local.sh > /tmp/part0_local.log 2>&1 &
# Resumable: frames that exist are skipped. Frames 1..END, two Blender workers (split by cost: MID).
# BLEND defaults to build/street_part0.blend; override:  BLEND=build/other.blend scripts/render_part0_local.sh
export PATH=/home/lovestaco/.local/bin:$PATH
cd "$(dirname "$0")/.." || exit 1
NAME=street_part0
BLEND=${BLEND:-build/street_part0.blend}
H=${H:-360}
OUT=build/frames/${NAME}_${H}p
BL=/snap/bin/blender
END=$(python3 -c "import json;print(json.load(open('build/${NAME}_overlays.json'))['end'])")
MID=${MID:-$((END / 2))}                                                                                  # split by cost (measured; see the report)
mkdir -p "$OUT"
echo "== $(date +%T) frames 1-$END (workers: 1-$MID | $((MID+1))-$END), blend $BLEND, ${H}p"
FLAGS="--h $H --fast"
$BL -b "$BLEND" --python scripts/05c_render_range.py -- "$OUT" 1-$MID $FLAGS > /tmp/part0_w1.log 2>&1 &
P1=$!
$BL -b "$BLEND" --python scripts/05c_render_range.py -- "$OUT" $((MID+1))-$END $FLAGS > /tmp/part0_w2.log 2>&1 &
P2=$!
wait $P1 $P2
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
