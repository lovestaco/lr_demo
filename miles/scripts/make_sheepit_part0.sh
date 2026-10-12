#!/bin/bash
# Build, verify and test the SheepIt package for PART 0 (the Meta opening). One command per package, safe to re-run:
#
#     scripts/make_sheepit_part0.sh 360      # DRAFT for review: 360p, 16 samples, no motion blur  -> build/sheepit/street_part0_360p_sheepit.zip
#     scripts/make_sheepit_part0.sh 1080     # FINAL: 1080p, 64 samples, ray-traced reflections, motion blur -> build/sheepit/street_part0_1080p_sheepit.zip
#     SKIP_TEST_RENDER=1 scripts/make_sheepit_part0.sh 360       # skip the two test frames
#     flock /tmp/claude-1000/gpu.lock scripts/make_sheepit_part0.sh 360    # (the test renders use the GPU: take the shared lock)
#
# 1. sheepit_pack.py on build/street_part0.blend (the original is untouched; frames 1-END, END from build/street_part0_overlays.json):
#    packs images, copies the image sequences (assets/street0/board_mr, stat1-3) next to the blend with relative paths, drops sound,
#    bakes the render settings in.  2. zips the stage (blend at the zip root).  3. extracts the zip into a fresh temp dir and checks
#    it (sheepit_verify.py, or sheepit_verify_draft.py for 360p).  4. renders two test frames FROM THE EXTRACTED COPY with the baked
#    settings (TEST_FRAMES="200 700" to change) into build/sheepit/part0_<H>_tests/ (kept).
# Nothing is deleted: a previous stage/zip is moved aside to *_prev_<time>.
# Upload to SheepIt (Blender 5.2, EEVEE, animation 1-END, output PNG), then:  scripts/assemble_part0_sheepit.sh <frames.zip> <height>
set -euo pipefail
cd "$(dirname "$0")/.."
H=${1:?usage: make_sheepit_part0.sh <360|1080>}
BLENDER=${BLENDER:-/snap/bin/blender}
BLEND=${BLEND:-build/street_part0.blend}
OV=build/street_part0_overlays.json
SHEEP=build/sheepit
STAGE=$SHEEP/part0_${H}_stage
ZIP=$SHEEP/street_part0_${H}p_sheepit.zip
TESTS=$SHEEP/part0_${H}_tests
TEST_FRAMES=${TEST_FRAMES:-"200 700"}
STAMP=$(date +%Y%m%d_%H%M%S)
die() { echo "ERROR: $*" >&2; exit 1; }
case "$H" in
  360)  PACK="--draft --h 360";   VERIFY=scripts/sheepit_verify_draft.py; SAMPLES=16;;
  1080) PACK="--h 1080 --samples 64"; VERIFY=scripts/sheepit_verify.py; SAMPLES=64;;
  *) die "height must be 360 (draft) or 1080 (final)";;
esac
[ -f "$BLEND" ] || die "$BLEND not found"
[ -f "$OV" ] || die "$OV not found"
END=$(python3 -I -c "import json;print(json.load(open('$OV'))['end'])")
[ "$END" -gt 1 ] 2>/dev/null || die "bad end frame '$END' in $OV"
echo "== part 0 ${H}p package: $BLEND frames 1-$END ($SAMPLES samples)"
[ -d "$STAGE" ] && mv "$STAGE" "${STAGE}_prev_$STAMP" && echo "previous stage moved to ${STAGE}_prev_$STAMP"
[ -f "$ZIP" ] && mv "$ZIP" "${ZIP%.zip}_prev_$STAMP.zip" && echo "previous zip moved to ${ZIP%.zip}_prev_$STAMP.zip"
mkdir -p "$STAGE" "$TESTS"

echo "== 1/4 pack"
"$BLENDER" -b "$BLEND" --python scripts/sheepit_pack.py -- "$STAGE/street_part0.blend" $PACK --frames "1-$END" 2>&1 | tee "$STAGE.log" | grep -E "^SHEEP|Error|Traceback" || true
[ -f "$STAGE/street_part0.blend" ] || die "pack failed, see $STAGE.log"
if grep -q "^Traceback" "$STAGE.log"; then die "pack script raised, see $STAGE.log"; fi
grep -q "SHEEP saved" "$STAGE.log" || die "pack did not finish, see $STAGE.log"

echo "== 2/4 zip"
(cd "$STAGE" && zip -r -q -6 "$OLDPWD/$ZIP" . -x "*.blend1" -x "*.blend2")
SIZE=$(stat -c %s "$ZIP")
echo "zip: $ZIP  $((SIZE / 1000000)) MB"
[ "$SIZE" -lt 2000000000 ] || die "zip is $((SIZE / 1000000)) MB, SheepIt limit is 2 GB"
unzip -Z1 "$ZIP" | grep -qx "street_part0.blend" || die "street_part0.blend is not at the zip root"

echo "== 3/4 verify (clean extraction)"
X=$(mktemp -d "${TMPDIR:-/tmp}/sheepit0_XXXXXX")
unzip -q "$ZIP" -d "$X"
VOK=0
"$BLENDER" -b "$X/street_part0.blend" --python "$VERIFY" -- --frames "1-$END" --h "$H" --samples "$SAMPLES" >"$X/verify.log" 2>&1 || VOK=1
grep -E "^VERIFY" "$X/verify.log" || true
[ "$VOK" = 0 ] || die "verification failed (extraction kept in $X; log $X/verify.log)"

if [ -n "${SKIP_TEST_RENDER:-}" ]; then echo "== 4/4 test render skipped"; else
echo "== 4/4 test renders from the extracted copy"
for F in $TEST_FRAMES; do
  T0=$(date +%s.%N)
  "$BLENDER" -b "$X/street_part0.blend" -o "$X/t_####" -f "$F" >"$X/render_$F.log" 2>&1 || { tail -20 "$X/render_$F.log"; die "test render of frame $F failed"; }
  T1=$(date +%s.%N)
  [ -s "$X/t_$(printf %04d "$F").png" ] || die "frame $F produced no PNG (see $X/render_$F.log)"
  cp "$X/t_$(printf %04d "$F").png" "$TESTS/test_$(printf %04d "$F")_$STAMP.png"
  printf "test frame %s: %.1f s wall (blender: %s)  -> %s\n" "$F" "$(echo "$T1 - $T0" | bc)" \
    "$(grep -oE 'Time: [0-9:.]+' "$X/render_$F.log" | tail -1)" "$TESTS/test_$(printf %04d "$F")_$STAMP.png"
done
fi
rm -rf "$X" 2>/dev/null || true   # temp extraction only (the zip and stage are kept)
echo "== DONE  $ZIP  ($((SIZE / 1000000)) MB)  frames 1-$END"
