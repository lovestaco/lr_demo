#!/bin/bash
# FINAL render of part 1 (street_part_1_final): EEVEE 1080p, 64 samples, full-res ray-traced reflections, motion blur,
# lossless PNG (RGB). Frames are kept in build/frames/street_part_1_final_1080p_final/f_NNNN.png.
# Resumable: re-run this script and it only renders the frames that are missing. ~10.5 s/frame measured (~6.7 h for 2295 frames).
#   run in the background:   nohup scripts/render_final_part1.sh > /tmp/part1_final.log 2>&1 &
#   progress:                ls build/frames/street_part_1_final_1080p_final | wc -l     (of 2295)
cd "$(dirname "$0")/.." || exit 1
OUT=build/frames/street_part_1_final_1080p_final
/snap/bin/blender -b build/street_part_1_final.blend --python scripts/05c_render_range.py -- "$OUT" 1-2295 --final
echo "frames: $(ls $OUT | wc -l) of 2295   $(date)"
