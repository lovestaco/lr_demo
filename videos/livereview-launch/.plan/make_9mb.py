#!/usr/bin/env python3
"""Two-pass encode every render down to just under a 9 MB cap.

9 MB over a 4:34 runtime is ~275 kbps all-in, so resolution has to come down with
it. The baked film grain is the enemy at this bitrate — it eats bits that should
go to the type — so a light hqdn3d pass goes in before the scale.
"""
import os, subprocess, sys, math

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RENDERS = os.path.join(HERE, "renders")
CAP_MB = 9.0
TARGET_MB = 8.75          # headroom for container overhead
AUDIO_KBPS = 48           # mono, plenty for a music bed at this size


def probe(path, entries, stream=None):
    cmd = ["ffprobe", "-v", "error"]
    if stream:
        cmd += ["-select_streams", stream]
    cmd += ["-show_entries", entries, "-of", "default=nw=1:nk=1", path]
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip().splitlines()


def pick_size(video_kbps):
    """Resolution that a given video bitrate can actually carry, 16:9."""
    for kbps, (w, h) in [(900, (1280, 720)), (420, (960, 540)),
                         (260, (854, 480)), (150, (640, 360)), (0, (512, 288))]:
        if video_kbps >= kbps:
            return w, h
    return 512, 288


results = []
for name in sorted(os.listdir(RENDERS)):
    if not name.endswith(".mp4") or name.endswith("-9mb.mp4"):
        continue
    src = os.path.join(RENDERS, name)
    dur = float(probe(src, "format=duration")[0])
    has_audio = bool(probe(src, "stream=codec_type", "a:0"))

    total_kbps = (TARGET_MB * 1024 * 1024 * 8) / dur / 1000
    abr = AUDIO_KBPS if has_audio else 0
    vbr = max(80, total_kbps - abr - 6)      # 6 kbps muxing slack
    w, h = pick_size(vbr)

    out = os.path.join(RENDERS, name[:-4] + "-9mb.mp4")
    vf = "hqdn3d=2:1.5:3:3,scale=%d:%d:flags=lanczos" % (w, h)
    passlog = "/tmp/hfpass_%s" % name.replace(".", "_")

    base = ["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", vf,
            "-c:v", "libx264", "-preset", "slow", "-b:v", "%dk" % int(vbr),
            "-pix_fmt", "yuv420p", "-passlogfile", passlog]

    print("%s  ->  %dx%d  v=%dk a=%dk" % (name, w, h, int(vbr), abr))
    r1 = subprocess.run(base + ["-pass", "1", "-an", "-f", "mp4", os.devnull],
                        capture_output=True, text=True)
    if r1.returncode != 0:
        print("   pass 1 failed: " + r1.stderr[:200]); continue
    audio_args = (["-c:a", "aac", "-b:a", "%dk" % abr, "-ac", "1", "-ar", "44100"]
                  if has_audio else ["-an"])
    r2 = subprocess.run(base + ["-pass", "2"] + audio_args +
                        ["-movflags", "+faststart", out],
                        capture_output=True, text=True)
    if r2.returncode != 0:
        print("   pass 2 failed: " + r2.stderr[:200]); continue

    mb = os.path.getsize(out) / 1048576
    ok = mb <= CAP_MB
    results.append((os.path.basename(out), mb, w, h, ok))
    print("   %s  %.2f MB  %s" % (os.path.basename(out), mb, "OK" if ok else "OVER CAP"))

    for ext in ("-0.log", "-0.log.mbtree"):
        try: os.remove(passlog + ext)
        except OSError: pass

print()
for n, mb, w, h, ok in results:
    print("%-44s %5.2f MB  %dx%d  %s" % (n, mb, w, h, "under 9 MB" if ok else "OVER"))
sys.exit(0 if all(r[4] for r in results) else 1)
