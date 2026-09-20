#!/usr/bin/env bash
# Re-assembly is DESTRUCTIVE: assemble-index.mjs hoists each frame's <video> into
# index.html and writes the stripped frame back to disk. Assembling twice therefore
# drops all footage silently. Always restore the source-of-truth copies first.
set -euo pipefail
cd "$(dirname "$0")/.."
for f in .hyperframes/frames-with-video/*.html; do
  cp "$f" "compositions/frames/$(basename "$f")"
done
echo "restored $(ls .hyperframes/frames-with-video/*.html | wc -l) frame(s) carrying <video>"
node /home/taco/.claude/skills/product-launch-video/scripts/assemble-index.mjs --storyboard ./STORYBOARD.md --hyperframes . 2>&1 | sed 's/\x1b\[[0-9;]*[A-Za-z]//g' | head -10
node /home/taco/.claude/skills/product-launch-video/scripts/transitions.mjs inject --storyboard ./STORYBOARD.md --hyperframes . >/dev/null 2>&1
node /home/taco/.claude/skills/product-launch-video/scripts/transitions.mjs verify --storyboard ./STORYBOARD.md --index ./index.html 2>&1 | sed 's/\x1b\[[0-9;]*[A-Za-z]//g' | tail -2
echo "videos in index.html: $(grep -c '<video' index.html)/8"
