"""Join rendered shots and lay in the voice-over, sound effects and a music bed.

    python3 scripts/06_assemble.py piece1                  # renders/piece1_360p.mp4 -> renders/piece1_360p_vo.mp4
    python3 scripts/06_assemble.py piece2 --music assets/audio/music/bed_piece2.mp3
    python3 scripts/06_assemble.py act1 act2 --height 720  # several shots back to back
    (street shots get burned-in subtitles from the voice-over word times, one phrase at a time with the spoken word bold; --no-subs skips; --range 100-200 renders just those frames of the joined timeline, numbers kept)
    (every run also writes <name>_tc.mp4: frame number + timecode bottom-right, for review; --no-burnin skips it)

Each shot script marks its audio cues as timeline markers (exported to build/<shot>_cues.json
by shot.finish), so re-timing the animation re-syncs the sound:
  "vo N"               -> <vo dir>/line_NN.wav   (assets/audio/vo_<shot>/ if it exists, else assets/audio/vo/)
  "sfx name#k[@gain]"  -> assets/audio/sfx/<name>.(mp3|wav)   (shot.sfx(name, frame, gain))
Music (optional, --music or assets/audio/music/bed_<shot>.mp3): looped to length (or --music-once: played once), 1 s fade in,
2.5 s fade out, ducked under the voice (sidechain). The mix is loudness-normalised to -16 LUFS.
"""
import random, glob, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import paths, subs

AUDIO = os.path.join(paths.ROOT, "assets", "audio")
SFX_DIR = os.path.join(AUDIO, "sfx")
SFX_GAIN = 0.385         # effects sit well under the voice (review: -30 %)
MUSIC_GAIN = 0.13          # review: voice up, music down
VO_GAIN = 1.26             # +2 dB over effects/music before loudness normalisation


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


def burnin_filter(total, height, start=0, strip=0):
    """Bottom-right review overlay: Blender frame number (frame 1 = first frame) + time / total duration.
    start = first frame of a --range preview (numbers keep the full video's); strip = subtitle strip px (sits above it)."""
    fs = max(14, height // 24)
    tot = f"00\\:{int(total // 60):02d}\\:{total % 60:06.3f}"            # same HH:MM:SS.mmm as the running time
    return (f"drawtext=text='f %{{eif\\:n+{start + 1}\\:d\\:4}}   %{{pts\\:hms\\:{start / 30:.3f}}} / {tot}':x=w-tw-12:y=h-th-10-{strip}:"
            f"fontsize={fs}:fontcolor=white:box=1:boxcolor=black@0.55:boxborderw=6")


def main(shots, height=360, music=None, burnin=False, music_once=False, subtitles=None, frame_range=None):
    videos, vo, sfx, offset, sub_cues = [], [], [], 0.0, []
    if subtitles is None:                          # default: on for the street films (their voice-over has word times)
        subtitles = all(sh.startswith("street") for sh in shots)
    for shot in shots:
        videos.append(os.path.join(paths.RENDERS, f"{shot}_{height}p.mp4"))
        meta = json.load(open(os.path.join(paths.BUILD, f"{shot}_cues.json")))
        for label, t in meta["cues"].items():
            if label.startswith("vo "):
                vo.append((offset + t, os.path.join(vo_dir(shot), f"line_{int(label.split()[1]):02d}.wav")))
            elif label.startswith("sfx "):
                name, _, gain = label[4:].partition("@")
                sfx.append((offset + t, name.split("#")[0], float(gain or 1.0)))
        if subtitles:
            sub_cues += subs.cues_for_shot(shot, offset)
        offset += meta["duration"]
    total = offset
    if music is None and len(shots) == 1:
        guess = os.path.join(AUDIO, "music", f"bed_{shots[0]}.mp3")
        music = guess if os.path.exists(guess) else None

    inputs = sum((["-i", v] for v in videos), [])
    fc = "".join(f"[{i}:v]" for i in range(len(videos))) + f"concat=n={len(videos)}:v=1:a=0[vcat];"
    k = len(videos)
    width = round(height * 16 / 9)
    strip = subs.strip_px(height) if sub_cues else 0          # bottom strip reserved for the subtitles
    if sub_cues:                                   # subtitles: RGBA frames piped in as one more video input
        inputs += ["-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{width}x{height}", "-r", "30", "-i", "-"]
        sub_idx = k
        k += 1

    def place(path, t, gain, tag, pitch=1.0):
        nonlocal fc, k
        inputs.extend(["-i", path])
        d = max(0, int(t * 1000))
        vary = f"asetrate={44100 * pitch:.0f},aresample=44100," if abs(pitch - 1.0) > 1e-3 else ""
        fc += f"[{k}:a]aformat=sample_rates=44100:channel_layouts=stereo,{vary}volume={gain:.3f},adelay={d}|{d}[{tag}];"
        k += 1
        return f"[{tag}]"

    # repeated effects shouldn't sound like one sample: each cue gets its own pitch (= size) and level, deterministic
    vary_rng = random.Random(7)
    varied = lambda: (vary_rng.uniform(0.88, 1.12), vary_rng.uniform(0.84, 1.08))

    vo_l = [place(p, t, VO_GAIN, f"v{i}") for i, (t, p) in enumerate(sorted(vo)) if os.path.exists(p)]
    missing = sorted({n for _, n, _ in sfx if not sfx_file(n)})
    sfx_l = []
    for i, (t, n, g) in enumerate(sorted(sfx)):
        if sfx_file(n):
            pr, gv = varied()
            sfx_l.append(place(sfx_file(n), t, SFX_GAIN * g * gv, f"s{i}", pitch=pr))
    print(f"voice {len(vo_l)}/{len(vo)} lines, sfx {len(sfx_l)}/{len(sfx)} cues" + (f" (missing: {', '.join(missing)})" if missing else ""))

    trim = f"apad,atrim=0:{total:.3f}"
    if vo_l:
        fc += "".join(vo_l) + f"amix=inputs={len(vo_l)}:normalize=0,{trim},asplit=2[vo][key];"
    else:                                              # no take yet (estimated timing): a silent voice bus
        fc += f"anullsrc=r=44100:cl=stereo,{trim},asplit=2[vo][key];"
    bus = ["[vo]"]
    if sfx_l:
        fc += "".join(sfx_l) + f"amix=inputs={len(sfx_l)}:normalize=0,{trim}[fx];"
        bus.append("[fx]")
    if music:
        inputs.extend((["-stream_loop", "-1"] if not music_once else []) + ["-i", music])
        # --music-once: the bed plays through once and ends on its own (no restart of an opener under the outro)
        fade = "" if music_once else f",afade=t=out:st={max(0, total - 2.5):.3f}:d=2.5"
        fc += (f"[{k}:a]aformat=sample_rates=44100:channel_layouts=stereo,apad,atrim=0:{total:.3f},volume={MUSIC_GAIN},"
               f"afade=t=in:d=1{fade}[mu];"
               f"[mu][key]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=400[duck];")
        bus.append("[duck]")
        k += 1
    else:
        fc += "[key]anullsink;"
    fc += "".join(bus) + f"amix=inputs={len(bus)}:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,{trim}[a];"
    if sub_cues:                                   # the video shrinks into the area above the strip; subtitles go in the strip
        h2 = height - strip
        w2 = round(h2 * 16 / 9 / 2) * 2
        fc += (f"[vcat]scale={w2}:{h2}:flags=lanczos,pad={width}:{height}:{(width - w2) // 2}:0:black[vs];"
               f"[vs][{sub_idx}:v]overlay=format=auto:eof_action=pass[v]")
    else:
        fc += "[vcat]null[v]"
    name = "-".join(shots) if len(shots) > 1 else shots[0]
    tag = f"_f{frame_range[0]:04d}-{frame_range[1]:04d}" if frame_range else ""
    out = os.path.join(paths.RENDERS, f"{name}_{height}p_{'mix' if (sfx_l or music) else 'vo'}{tag}.mp4")
    start = frame_range[0] - 1 if frame_range else 0
    cut = ["-ss", f"{start / 30:.4f}", "-t", f"{(frame_range[1] - start) / 30:.4f}"] if frame_range else []
    cmd = ["ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
           "-ar", "44100", *cut, "-shortest", out]
    if sub_cues:
        print(f"subtitles: {len(sub_cues)} phrases")
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        try:
            for fr in subs.Overlay(width, height).frames(sub_cues, (frame_range[1] if frame_range else int(round(total * 30))) + 1):
                proc.stdin.write(fr)
        except BrokenPipeError:
            pass
        proc.stdin.close()
        if proc.wait():
            raise SystemExit("ffmpeg failed")
    else:
        subprocess.run(cmd, check=True)
    print("VIDEO", out, f"({total:.1f}s)" + (f"  music: {os.path.basename(music)}" if music else ""))
    if burnin:                                         # review copy: frame number + time / total, bottom-right
        tc = out[:-4] + "_tc.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", out, "-vf", burnin_filter(total, height, start, strip),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "copy", tc], check=True)
        print("REVIEW", tc)


if __name__ == "__main__":
    args = sys.argv[1:]
    h = int(args[args.index("--height") + 1]) if "--height" in args else 360
    mu = os.path.abspath(args[args.index("--music") + 1]) if "--music" in args else None
    skip = {args.index(f) + 1 for f in ("--height", "--music", "--range") if f in args}
    shots = [a for i, a in enumerate(args) if not a.startswith("--") and i not in skip]
    main(shots or ["piece1"], h, mu, burnin="--no-burnin" not in args, music_once="--music-once" in args,
         subtitles=False if "--no-subs" in args else (True if "--subs" in args else None),
         frame_range=tuple(int(x) for x in args[args.index("--range") + 1].split("-")) if "--range" in args else None)
