#!/bin/bash
# Build, verify and test the SheepIt package for part 2b (FINAL 1080p). One command, safe to re-run:
#
#     scripts/make_sheepit_2b.sh              # from anywhere
#     SKIP_TEST_RENDER=1 scripts/make_sheepit_2b.sh   # skip the two ~10 s test frames
#     BLEND=build/other.blend scripts/make_sheepit_2b.sh
#
# 1. sheepit_pack.py on build/street_part2_b.blend (the original is untouched): packs images, copies the Meta image
#    sequences (build/meta/...) next to the blend with relative paths, drops sound, bakes 1920x1080 @100%, 64 samples,
#    full-resolution ray-traced reflections, motion blur, PNG RGB 8-bit, frame range 1418-<"end" of
#    build/street_part2_b_overlays.json>  (frames 1-1417 are the 2D S16/S17 boards, made by 05b, not rendered in Blender).
#    -> build/sheepit/part2b_final_stage/street_part2_b.blend (+ build/meta/...)
# 2. zips the stage (blend at the zip root, deflate) -> build/sheepit/street_part2_b_1080p_final_sheepit.zip
# 3. extracts the zip into a fresh temp dir and checks it with sheepit_verify.py (relative+existing paths, no sound,
#    1920x1080 100%, 64 samples, ray tracing, motion blur, PNG RGB, frame range)
# 4. renders two test frames FROM THE EXTRACTED COPY with the baked settings (S18 rebuild ~1450, Meta ~2100; override
#    with TEST_FRAMES="1450 2100") into build/sheepit/part2b_final_tests/ (kept) and prints their render times.
# Stops with an error message on any failure. Nothing is deleted: a previous stage/zip is moved aside to *_prev_<time>.
# Upload the zip to SheepIt (Blender 5.2, EEVEE, animation 1418-END, output PNG), download the frames, then copy them to
# build/frames/street_part2_b_1080p_final/ next to the 2D boards (f_NNNN.png).
set -euo pipefail
cd "$(dirname "$0")/.."
BLENDER=${BLENDER:-/snap/bin/blender}
BLEND=${BLEND:-build/street_part2_b.blend}
OV=build/street_part2_b_overlays.json
SHEEP=build/sheepit
STAGE=$SHEEP/part2b_final_stage
ZIP=$SHEEP/street_part2_b_1080p_final_sheepit.zip
TESTS=$SHEEP/part2b_final_tests
FIRST=1418
TEST_FRAMES=${TEST_FRAMES:-"1450 2100"}
STAMP=$(date +%Y%m%d_%H%M%S)
die() { echo "ERROR: $*" >&2; exit 1; }

[ -f "$BLEND" ] || die "$BLEND not found"
[ -f "$OV" ] || die "$OV not found"
END=$(python3 -c "import json;print(json.load(open('$OV'))['end'])")
[ "$END" -gt "$FIRST" ] 2>/dev/null || die "bad end frame '$END' in $OV"
echo "== part 2b FINAL package: $BLEND frames $FIRST-$END (1920x1080, 64 samples)"

# keep (never delete) what was there before
[ -d "$STAGE" ] && mv "$STAGE" "${STAGE}_prev_$STAMP" && echo "previous stage moved to ${STAGE}_prev_$STAMP"
[ -f "$ZIP" ] && mv "$ZIP" "${ZIP%.zip}_prev_$STAMP.zip" && echo "previous zip moved to ${ZIP%.zip}_prev_$STAMP.zip"
mkdir -p "$STAGE" "$TESTS"

echo "== 1/4 pack"
"$BLENDER" -b "$BLEND" --python scripts/sheepit_pack.py -- "$STAGE/street_part2_b.blend" --h 1080 --samples 64 --frames "$FIRST-$END" 2>&1 | tee "$STAGE.log" | grep -E "^SHEEP|Error|Traceback" || true
[ -f "$STAGE/street_part2_b.blend" ] || die "pack failed, see $STAGE.log"
if grep -q "^Traceback" "$STAGE.log"; then die "pack script raised, see $STAGE.log"; fi
grep -q "SHEEP saved" "$STAGE.log" || die "pack did not finish, see $STAGE.log"

echo "== 2/4 zip"
(cd "$STAGE" && zip -r -q -6 "$OLDPWD/$ZIP" . -x "*.blend1" -x "*.blend2")
SIZE=$(stat -c %s "$ZIP")
echo "zip: $ZIP  $((SIZE / 1000000)) MB"
[ "$SIZE" -lt 2000000000 ] || die "zip is $((SIZE / 1000000)) MB, SheepIt limit is 2 GB"
LIST=$(unzip -Z1 "$ZIP"); echo "$LIST" | grep -qx "street_part2_b.blend" || die "street_part2_b.blend is not at the zip root"

echo "== 3/4 verify (clean extraction)"
X=$(mktemp -d "${TMPDIR:-/tmp}/sheepit2b_XXXXXX")
unzip -q "$ZIP" -d "$X"
VOK=0
"$BLENDER" -b "$X/street_part2_b.blend" --python scripts/sheepit_verify.py -- --frames "$FIRST-$END" --h 1080 --samples 64 >"$X/verify.log" 2>&1 || VOK=1
grep -E "^VERIFY" "$X/verify.log" || true
[ "$VOK" = 0 ] || die "verification failed (extraction kept in $X; log $X/verify.log)"

if [ -n "${SKIP_TEST_RENDER:-}" ]; then echo "== 4/4 test render skipped"; else
echo "== 4/4 test renders from the extracted copy"
for F in $TEST_FRAMES; do
  T0=$(date +%s.%N)
  "$BLENDER" -b "$X/street_part2_b.blend" -o "$X/t_####" -f "$F" >"$X/render_$F.log" 2>&1 || { tail -20 "$X/render_$F.log"; die "test render of frame $F failed"; }
  T1=$(date +%s.%N)
  [ -s "$X/t_$(printf %04d "$F").png" ] || die "frame $F produced no PNG (see $X/render_$F.log)"
  cp "$X/t_$(printf %04d "$F").png" "$TESTS/test_$(printf %04d "$F")_$STAMP.png"
  printf "test frame %s: %.1f s wall (blender: %s)  -> %s\n" "$F" "$(echo "$T1 - $T0" | bc)" \
    "$(grep -oE 'Time: [0-9:.]+' "$X/render_$F.log" | tail -1)" "$TESTS/test_$(printf %04d "$F")_$STAMP.png"
done
fi
rm -rf "$X" 2>/dev/null || true   # temp extraction only (the zip and stage are kept)
echo "== DONE  $ZIP  ($((SIZE / 1000000)) MB)  frames $FIRST-$END"
