"""Cut scenes out of the ALREADY RENDERED part 1 (no Blender): frames -> cues -> base video -> audio/subs/burn-in.

    python3 scripts/cut_part1.py                         # the CUTS below
    python3 scripts/cut_part1.py --cut 1-63,335-588,811-1091
    python3 scripts/cut_part1.py --no-assemble           # only frames + cues + base video
    python3 scripts/cut_part1.py --assemble-only         # frames/cues/base already done

Cut ranges are INCLUSIVE frame numbers of the OLD timeline (build/frames/street_part_1_final_suitfix_1080p/f_NNNN.png =
the "f NNNN" burn-in of the old film). Everything else is kept in order and renumbered 1..N. Steps:
  1. hard links of the kept frames -> build/frames/street_part_1_cut_1080p/f_0001.png ... (originals untouched; stale links removed)
  2. build/street_part_1_cut_cues.json: the old cues (build/street_part_1_final_cues.json) with every marker inside a cut
     range dropped (vo N, sfx, scene labels) and every kept marker shifted by the frames removed before it
  3. renders/street_part_1_cut_1080p.mp4 (H.264 CRF 14, 30 fps, +faststart; written to a .part file, verified, then renamed)
  4. 06_assemble.py street_part_1_cut --height 1080 (VO lines from assets/audio/vo_street/ by the name prefix rule, SFX of the kept
     markers, ducked music bed, word-timed subtitles, frame-number burn-in) -> renders/street_part_1_cut_1080p_mix_tc.mp4
  5. the silent base + clean mix go to build/intermediate/; the old renders/street_part_1_final_1080p_mix_tc.mp4 is moved to
     build/intermediate/street_part_1_final_1080p_mix_tc_before_cut.mp4 (first run only). renders/ keeps ONE part 1 file.
Music: the bed (70.2 s) is played once if the film is longer than it, else looped/faded out as usual (--music-once forces once).
"""
import argparse, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD, RENDERS = os.path.join(ROOT, "build"), os.path.join(ROOT, "renders")
INTER = os.path.join(BUILD, "intermediate")

# S0 aerial (he lands on the mural ledge, line 1 starts at old f 76), S3 LED ticker (from his jump off the billboard to the
# first clean frame before the bus-stop cut), S5 subway lightbox (from the end of the spider gag to the screen cut).
CUTS = "1-63,335-588,811-1091"
SRC = "street_part_1_final"
SRC_FRAMES = os.path.join(BUILD, "frames", "street_part_1_final_suitfix_1080p")
NAME = "street_part_1_cut"
MUSIC = os.path.join(ROOT, "assets", "audio", "music", "bed_street.mp3")
MUSIC_LEN = 70.2


def parse_cuts(s):
    out = []
    for part in s.split(","):
        a, _, b = part.strip().partition("-")
        out.append((int(a), int(b or a)))
    out.sort()
    for (a, b), (c, d) in zip(out, out[1:]):
        if c <= b:
            raise SystemExit(f"cut ranges overlap: {a}-{b} / {c}-{d}")
    return out


def kept_ranges(cuts, total):
    kept, pos = [], 1
    for a, b in cuts:
        if a > pos:
            kept.append((pos, a - 1))
        pos = b + 1
    if pos <= total:
        kept.append((pos, total))
    return kept


def link_frames(kept, outdir):
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):                      # stale links of an earlier cut list (hard links: the originals stay)
        if f.startswith("f_") and f.endswith(".png"):
            os.unlink(os.path.join(outdir, f))
    n = 0
    for a, b in kept:
        for f in range(a, b + 1):
            n += 1
            os.link(os.path.join(SRC_FRAMES, f"f_{f:04d}.png"), os.path.join(outdir, f"f_{n:04d}.png"))
    return n


def make_cues(kept, n_new, cuts_arg):
    src = os.path.join(BUILD, f"{SRC}_cues.json")
    if not os.path.exists(src):
        alt = os.path.join(BUILD, f"{SRC}_cues_before_opening.json")
        print(f"NOTE: {src} missing, using {alt}")
        src = alt
    meta = json.load(open(src))
    fps = meta.get("fps", 30)
    cues, dropped = {}, []
    for label, t in meta["cues"].items():
        f = round(t * fps) + 1                         # marker frame in the old timeline (frame 1 = t 0)
        base = 0
        for a, b in kept:
            if a <= f <= b:
                cues[label] = round((f - a + base) / fps, 6)       # new frame (f - a + base + 1) -> t = (new - 1) / fps
                break
            base += b - a + 1
        else:
            dropped.append(f"{label}@{f}")
    if "end" in cues or "end" in meta["cues"]:
        cues["end"] = round(n_new / fps, 6)
    out = {**meta, "frames": n_new, "duration": round(n_new / fps, 6), "cues": cues, "cut": cuts_arg, "end_state": {}}
    json.dump(out, open(os.path.join(BUILD, f"{NAME}_cues.json"), "w"), indent=1)
    return cues, dropped


def encode_base(framedir, n):
    out = os.path.join(RENDERS, f"{NAME}_1080p.mp4")
    tmp = os.path.join(RENDERS, f"{NAME}_1080p.part.mp4")
    cmd = ["nice", "-n", "10", "ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-framerate", "30", "-i",
           os.path.join(framedir, "f_%04d.png"), "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p",
           "-r", "30", "-movflags", "+faststart", "-f", "mp4", tmp]
    subprocess.run(cmd, check=True)
    p = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                        "stream=nb_read_frames,width,height", "-of", "csv=p=0", tmp], capture_output=True, text=True)
    w, h, got = p.stdout.strip().split(",")[:3]
    if int(got) != n or (w, h) != ("1920", "1080"):
        raise SystemExit(f"base video incomplete or wrong size: {p.stdout.strip()} (expected 1920,1080,{n})")
    os.replace(tmp, out)
    return out


def assemble(n, music_once):
    cmd = ["nice", "-n", "10", "python3", os.path.join(ROOT, "scripts", "06_assemble.py"), NAME, "--height", "1080",
           "--music", MUSIC]
    if music_once or n / 30 > MUSIC_LEN:
        cmd.append("--music-once")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True, cwd=ROOT)


def tidy(keep_old):
    os.makedirs(INTER, exist_ok=True)
    old = os.path.join(RENDERS, f"{SRC}_1080p_mix_tc.mp4")
    dst = os.path.join(INTER, f"{SRC}_1080p_mix_tc_before_cut.mp4")
    if os.path.exists(old) and not keep_old:
        if os.path.exists(dst):
            raise SystemExit(f"{dst} already exists; not overwriting the old film")
        shutil.move(old, dst)
        print("moved", old, "->", dst)
    for f in (f"{NAME}_1080p.mp4", f"{NAME}_1080p_mix.mp4"):
        p = os.path.join(RENDERS, f)
        if os.path.exists(p):
            os.replace(p, os.path.join(INTER, f))
            print("moved", f, "-> build/intermediate/")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cut", default=CUTS, help="inclusive old-frame ranges to remove, e.g. 1-63,335-588,811-1091")
    ap.add_argument("--no-assemble", action="store_true")
    ap.add_argument("--assemble-only", action="store_true", help="skip frames/cues/base (reuse the existing ones)")
    ap.add_argument("--music-once", action="store_true")
    ap.add_argument("--keep-old", action="store_true", help="do not move the old film out of renders/")
    a = ap.parse_args()
    cuts = parse_cuts(a.cut)
    total = len([f for f in os.listdir(SRC_FRAMES) if f.startswith("f_")])
    kept = kept_ranges(cuts, total)
    n_new = sum(b - a_ + 1 for a_, b in kept)
    print(f"old {total} frames; cut {cuts}; keep {kept}; new {n_new} frames = {n_new / 30:.2f} s")
    framedir = os.path.join(BUILD, "frames", f"{NAME}_1080p")
    if not a.assemble_only:
        link_frames(kept, framedir)
        cues, dropped = make_cues(kept, n_new, a.cut)
        print("dropped markers:", ", ".join(dropped))
        joins, pos = [], 0
        for _, b in kept[:-1]:
            pos += b - _ + 1
            joins.append(pos)
        print("joins: last kept frame before each cut (new numbering):", joins, "-> next frame", [j + 1 for j in joins])
        print("base video:", encode_base(framedir, n_new))
    if not a.no_assemble:
        assemble(n_new, a.music_once)
        tidy(a.keep_old)
