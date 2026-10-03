#!/usr/bin/env bash
# encode_plate.sh — encode PNG sequence → assets/plate-atc-150.mp4
# Run after all 4500 frames are rendered.
#
# Usage: ./encode_plate.sh
#   Optional: QUALITY=20 ./encode_plate.sh (lower = better, default 18)

set -euo pipefail

FRAMES_DIR="/home/lovestaco/pers/lr_demo/blender_stuff_lr/frames"
OUT="/home/lovestaco/pers/lr_demo/videos/livereview-launch/assets/plate-atc-150.mp4"
QUALITY=${QUALITY:-18}

# Sanity: confirm all 4500 frames exist
FRAME_COUNT=$(ls "$FRAMES_DIR"/frame_*.png 2>/dev/null | wc -l)
echo "Frames found: $FRAME_COUNT / 4500"
if [ "$FRAME_COUNT" -lt 4500 ]; then
  echo "ERROR: Not all frames rendered yet. Aborting." >&2
  exit 1
fi

echo "Encoding $FRAME_COUNT frames → $OUT  (CRF $QUALITY)"

ffmpeg -y \
  -framerate 30 \
  -i "$FRAMES_DIR/frame_%04d.png" \
  -c:v libx264 \
  -crf "$QUALITY" \
  -preset slow \
  -pix_fmt yuv420p \
  -movflags +faststart \
  "$OUT"

echo "Done. Output: $OUT"
ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$OUT" | \
  xargs -I{} echo "Duration: {}s"
