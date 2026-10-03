#!/usr/bin/env bash
# complete_atc.sh — runs after encode_plate.sh finishes
# Verifies plate-atc-150.mp4, then renders the ATC video
set -euo pipefail

PROJ="/home/lovestaco/pers/lr_demo/videos/livereview-launch"
PLATE="$PROJ/assets/plate-atc-150.mp4"
NPX="/home/lovestaco/.nvm/versions/node/v22.17.0/bin/npx"

echo "=== Waiting for ffmpeg to finish (PID 1050977) ==="
while kill -0 1050977 2>/dev/null; do
  sleep 5
done
echo "=== ffmpeg done. Verifying plate... ==="

# Verify the plate is valid
if ! ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$PLATE" > /dev/null 2>&1; then
  echo "ERROR: $PLATE is still corrupt. Exiting."
  exit 1
fi

DURATION=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$PLATE")
echo "Plate OK: duration=${DURATION}s, size=$(du -h "$PLATE" | cut -f1)"

echo "=== Starting ATC video render ==="
cd "$PROJ"
$NPX hyperframes@0.8.92 render \
  --composition index-atc.html \
  --output renders/livereview-atc.mp4 \
  --quality delivery \
  2>&1 | tee /tmp/hf_atc_render.log

echo "=== ATC render complete. Output: $PROJ/renders/livereview-atc.mp4 ==="
