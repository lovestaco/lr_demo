#!/bin/bash
# Publish the render copy of lr_demo to the shared folder (/mnt/spidey/lr_demo) for the Flamenco farm.
# Everything except .git and secret .env files is copied; the three street .blend files then get relative
# asset paths (so they open on any worker). Run after rebuilding a .blend:   scripts/publish_to_spidey.sh [part ...]
# Parts: street_part_1_final street_part2 street_part3 (default: all three).
set -e
SRC=/home/lovestaco/pers/lr_demo
DST=/mnt/spidey/lr_demo
PARTS=("$@"); [ ${#PARTS[@]} -eq 0 ] && PARTS=(street_part_1_final street_part2 street_part3)
mkdir -p "$DST"
# frames written by the workers live in the share only: never overwrite or delete them
rsync -a --exclude='.git/' --exclude='.env' --exclude='miles/build/frames' "$SRC"/ "$DST"/
for p in "${PARTS[@]}"; do
    /snap/bin/blender -b "$DST/miles/build/$p.blend" --python "$SRC/miles/scripts/spidey_fixpaths.py" 2>&1 | grep -E "FIXPATHS (street|MISSING)" | grep -v "Fortnite" || true
done
echo "published: ${PARTS[*]} -> $DST"
