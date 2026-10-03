#!/usr/bin/env bash
# rekey_sources.sh — re-encode all render source videos with -g 30 keyframes
# Fixes "sparse keyframes" warnings that cause seek freezing in HyperFrames render
set -euo pipefail

ASSETS="/home/lovestaco/pers/lr_demo/videos/livereview-launch/assets"
PLATE="/home/lovestaco/pers/lr_demo/blender_stuff_lr"
KF_FLAGS="-c:v libx264 -r 30 -g 30 -keyint_min 30 -sc_threshold 0 -movflags +faststart -pix_fmt yuv420p -crf 18"

reencode() {
  local src="$1"
  local tmp="${src}.tmp.mp4"
  echo "  Re-keying: $(basename $src)"
  ffmpeg -y -i "$src" $KF_FLAGS "$tmp" 2>/dev/null
  mv "$tmp" "$src"
  echo "  Done: $(basename $src)"
}

echo "=== Re-encoding plate-atc-150.mp4 (48MB, ~3 min) ==="
reencode "$ASSETS/plate-atc-150.mp4"

echo "=== Re-encoding product clips ==="
for clip in clip05_blast clip11_quiz clip11_slides clip08_schedule clip10_cicd clip13_dashboard; do
  [ -f "$ASSETS/${clip}.mp4" ] && reencode "$ASSETS/${clip}.mp4" || echo "  Skip (not found): $clip"
done

echo "=== All done. Keyframe interval now 1s (30 frames) on all sources. ==="
