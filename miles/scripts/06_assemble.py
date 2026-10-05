"""Join rendered shots and lay in the voice-over, sound effects and a music bed.

    python3 scripts/06_assemble.py piece1                  # renders/piece1_360p.mp4 -> renders/piece1_360p_vo.mp4
    python3 scripts/06_assemble.py piece2 --music assets/audio/music/bed_piece2.mp3
    python3 scripts/06_assemble.py act1 act2 --height 720  # several shots back to back

Each shot script marks its audio cues as timeline markers (exported to build/<shot>_cues.json
by shot.finish), so re-timing the animation re-syncs the sound:
  "vo N"               -> <vo dir>/line_NN.wav   (assets/audio/vo_<shot>/ if it exists, else assets/audio/vo/)
  "sfx name#k[@gain]"  -> assets/audio/sfx/<name>.(mp3|wav)   (shot.sfx(name, frame, gain))
Music (optional, --music or assets/audio/music/bed_<shot>.mp3): looped to length, 1 s fade in,
2.5 s fade out, ducked under the voice (sidechain). The mix is loudness-normalised to -16 LUFS.
"""
import glob, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import paths

AUDIO = os.path.join(paths.ROOT, "assets", "audio")
SFX_DIR = os.path.join(AUDIO, "sfx")
SFX_GAIN = 0.385         # effects sit well under the voice (review: -30 %)
MUSIC_GAIN = 0.22


def vo_dir(shot):
    """vo_<shot>, else the longest prefix (piece2_cine -> vo_piece2), else vo/ (same rule as shot.vo_folder)."""
    parts = shot.split("_")
    for k in range(len(parts), 0, -1):
        d = os.path.join(AUDIO, "vo_" + "_".join(parts[:k]))
        if os.path.isdir(d):
            return d
    return os.path.join(AUDIO, "vo")


def sfx_file(name):
    hits = sorted(glob.glob(os.path.join(SFX_DIR, name + ".*")))
    return hits[0] if hits else None


def main(shots, height=360, music=None):
    videos, vo, sfx, offset = [], [], [], 0.0
    for shot in shots:
        videos.append(os.path.join(paths.RENDERS, f"{shot}_{height}p.mp4"))
        meta = json.load(open(os.path.join(paths.BUILD, f"{shot}_cues.json")))
        for label, t in meta["cues"].items():
            if label.startswith("vo "):
                vo.append((offset + t, os.path.join(vo_dir(shot), f"line_{int(label.split()[1]):02d}.wav")))
            elif label.startswith("sfx "):
                name, _, gain = label[4:].partition("@")
                sfx.append((offset + t, name.split("#")[0], float(gain or 1.0)))
        offset += meta["duration"]
    total = offset
    if music is None and len(shots) == 1:
        guess = os.path.join(AUDIO, "music", f"bed_{shots[0]}.mp3")
        music = guess if os.path.exists(guess) else None

    inputs = sum((["-i", v] for v in videos), [])
    fc = "".join(f"[{i}:v]" for i in range(len(videos))) + f"concat=n={len(videos)}:v=1:a=0[v];"
    k = len(videos)

    def place(path, t, gain, tag):
        nonlocal fc, k
        inputs.extend(["-i", path])
        d = max(0, int(t * 1000))
        fc += f"[{k}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={gain:.3f},adelay={d}|{d}[{tag}];"
        k += 1
        return f"[{tag}]"

    vo_l = [place(p, t, 1.0, f"v{i}") for i, (t, p) in enumerate(sorted(vo)) if os.path.exists(p)]
    missing = sorted({n for _, n, _ in sfx if not sfx_file(n)})
    sfx_l = [place(sfx_file(n), t, SFX_GAIN * g, f"s{i}") for i, (t, n, g) in enumerate(sorted(sfx)) if sfx_file(n)]
    print(f"voice {len(vo_l)}/{len(vo)} lines, sfx {len(sfx_l)}/{len(sfx)} cues" + (f" (missing: {', '.join(missing)})" if missing else ""))

    trim = f"apad,atrim=0:{total:.3f}"
    fc += "".join(vo_l) + f"amix=inputs={len(vo_l)}:normalize=0,{trim},asplit=2[vo][key];"
    bus = ["[vo]"]
    if sfx_l:
        fc += "".join(sfx_l) + f"amix=inputs={len(sfx_l)}:normalize=0,{trim}[fx];"
        bus.append("[fx]")
    if music:
        inputs.extend(["-stream_loop", "-1", "-i", music])
        fc += (f"[{k}:a]aformat=sample_rates=44100:channel_layouts=stereo,atrim=0:{total:.3f},volume={MUSIC_GAIN},"
               f"afade=t=in:d=1,afade=t=out:st={max(0, total - 2.5):.3f}:d=2.5[mu];"
               f"[mu][key]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[duck];")
        bus.append("[duck]")
        k += 1
    else:
        fc += "[key]anullsink;"
    fc += "".join(bus) + f"amix=inputs={len(bus)}:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,{trim}[a]"
    name = "-".join(shots) if len(shots) > 1 else shots[0]
    out = os.path.join(paths.RENDERS, f"{name}_{height}p_{'mix' if (sfx_l or music) else 'vo'}.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
                    "-ar", "44100", "-shortest", out], check=True)
    print("VIDEO", out, f"({total:.1f}s)" + (f"  music: {os.path.basename(music)}" if music else ""))


if __name__ == "__main__":
    args = sys.argv[1:]
    h = int(args[args.index("--height") + 1]) if "--height" in args else 360
    mu = os.path.abspath(args[args.index("--music") + 1]) if "--music" in args else None
    skip = {args.index(f) + 1 for f in ("--height", "--music") if f in args}
    shots = [a for i, a in enumerate(args) if not a.startswith("--") and i not in skip]
    main(shots or ["piece1"], h, mu)
