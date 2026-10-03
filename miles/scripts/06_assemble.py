"""Join rendered acts into one video and cue voice-over lines to slides.

    python3 scripts/06_assemble.py [height]        # default 360 -> renders/acts1-2_360p.mp4

Each act script writes build/<act>_cues.json with the second each slide becomes
readable. Voice-over lines (start/end inside the recording) are cut out and placed
at their slide's cue, so the voice follows the board even if the recording's
order or pacing differs from the edit.
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import paths

ACTS = ["act1", "act2"]
VO = os.path.join(paths.ROOT, "assets", "audio", "vo_acts1-2.wav")
# slide -> (start, end) of its line inside the VO recording (from a whisper transcript)
VO_LINES = {
    1: (3.40, 5.55),    # "You already do a lot of AI-assisted code generation."
    2: (0.00, 2.95),    # "But do you do enough of AI-assisted code inspection?"  (recorded first)
    3: (6.15, 7.10),    # "Here's what we believe."
    4: (7.50, 11.95),   # "You owe your users and customers to adopt an AI-assisted inspection layer."
    5: (12.15, 15.75),  # "If you're a professional, you must adopt an AI-assisted inspection layer."
    6: (15.90, 19.90),  # "For the sake of your business reputation, consider an AI-assisted inspection layer."
}
LEAD = 0.15             # speak a beat after the slide lands

height = int(sys.argv[1]) if len(sys.argv) > 1 else 360
videos, cues, offset = [], {}, 0.0
for act in ACTS:
    videos.append(os.path.join(paths.RENDERS, f"{act}_{height}p.mp4"))
    meta = json.load(open(os.path.join(paths.BUILD, f"{act}_cues.json")))
    for label, t in meta["cues"].items():
        if label.startswith("slide "):
            cues[int(label.split()[1])] = offset + t
    offset += meta["duration"]
total = offset

inputs = sum((["-i", v] for v in videos), []) + ["-i", VO]
vo = len(videos)
fc = "".join(f"[{i}:v]" for i in range(len(videos))) + f"concat=n={len(videos)}:v=1:a=0[v];"
labels = []
for slide, (a, b) in sorted(VO_LINES.items()):
    if slide not in cues:
        continue
    d = int((cues[slide] + LEAD) * 1000)
    fc += f"[{vo}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={b - a - 0.06}:d=0.06,adelay={d}|{d}[l{slide}];"
    labels.append(f"[l{slide}]")
    print(f"slide {slide}: on screen {cues[slide]:5.2f}s  voice {cues[slide] + LEAD:5.2f}-{cues[slide] + LEAD + b - a:5.2f}s")
fc += "".join(labels) + f"amix=inputs={len(labels)}:normalize=0,apad,atrim=0:{total:.3f}[a]"
out = os.path.join(paths.RENDERS, f"acts1-2_{height}p.mp4")
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "160k", out], check=True)
print("VIDEO", out, f"({total:.1f}s)")
