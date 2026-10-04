"""Split one full voice-over take (e.g. downloaded from the ElevenLabs website) into per-line clips.

    python3 scripts/07b_split_take.py assets/audio/vo/piece1_vo_gen2.mp3
    python3 scripts/07b_split_take.py TAKE.mp3 --script assets/audio/vo_piece2.md --out assets/audio/vo_piece2

Transcribes the take with faster-whisper (word timestamps), matches the words against the
lines in assets/audio/vo_piece1.md in order, and writes assets/audio/vo/line_NN.wav plus
vo/lines.json {num: text, start (cue in the cut), duration, take, src_start, src_end}.
"""
import json, os, re, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import paths

ROOT = paths.ROOT
SCRIPT = os.path.join(ROOT, "assets", "audio", "vo_piece1.md")
OUT = os.path.join(ROOT, "assets", "audio", "vo")
# words only: drop v4 audio tags like [sighs] (performance direction, not spoken)
tok = lambda s: [t for t in re.split(r"[^a-z0-9]+", re.sub(r"\[[^\]]*\]", " ", s).lower()) if t]


def script_lines():
    rows = []
    for line in open(SCRIPT, encoding="utf-8"):
        m = re.match(r"^\|\s*(\d+)\s*\|\s*([\d.]+)s\s*\|.*\|\s*(.+?)\s*\|\s*$", line)
        if m:
            rows.append((int(m.group(1)), float(m.group(2)), m.group(3)))
    return rows


def transcribe(path):
    """Word timings via faster-whisper, run in an isolated uv env."""
    raw = tempfile.mktemp(suffix=".raw")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", path, "-ac", "1", "-ar", "16000", "-f", "s16le", raw], check=True)
    code = ("import numpy as np, json, sys\nfrom faster_whisper import WhisperModel\n"
            "a = np.frombuffer(open(sys.argv[1],'rb').read(), dtype=np.int16).astype(np.float32)/32768\n"
            "segs,_ = WhisperModel('base.en', device='cpu', compute_type='int8').transcribe(a, word_timestamps=True)\n"
            "print(json.dumps([[w.word, w.start, w.end] for s in segs for w in s.words]))\n")
    r = subprocess.run(["uv", "run", "--quiet", "--with", "faster-whisper", "--with", "numpy", "python", "-c", code, raw],
                       capture_output=True, text=True, check=True)
    os.remove(raw)
    out = []
    for w, s, e in json.loads(r.stdout.strip().splitlines()[-1]):
        for t in tok(w):
            out.append((t, s, e))
    return out


def main(take):
    words = transcribe(take)
    lines = script_lines()
    meta, i = {}, 0
    for num, cue, text in lines:
        want = tok(text)
        start = words[i][1]
        i += len(want)                       # transcript tokens track the script 1:1
        end = words[min(i, len(words)) - 1][2]
        nxt = words[i][1] if i < len(words) else end + 0.6
        a, b = max(0.0, start - 0.06), min(nxt - 0.04, end + 0.3)
        out = os.path.join(OUT, f"line_{num:02d}.wav")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", take, "-ss", f"{a:.3f}", "-to", f"{b:.3f}",
                        "-af", "afade=t=in:d=0.02,areverse,afade=t=in:d=0.06,areverse", "-ar", "44100", out], check=True)
        line_words = [(w, round(ws - a, 3)) for w, ws, we in words[i - len(want):i]]
        meta[str(num)] = {"text": re.sub(r"\[[^\]]*\]\s*", "", text), "start": cue, "duration": round(b - a, 2), "take": os.path.basename(take),
                          "src_start": round(a, 3), "src_end": round(b, 3),
                          "words": line_words}                 # [word, seconds from clip start]
        print(f"line {num:2d}  {a:6.2f}-{b:6.2f}  ({b - a:4.2f}s)  {text}")
    json.dump(meta, open(os.path.join(OUT, "lines.json"), "w"), indent=1)


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--script" in args:
        SCRIPT = os.path.abspath(args[args.index("--script") + 1])
    if "--out" in args:
        OUT = os.path.abspath(args[args.index("--out") + 1])
        os.makedirs(OUT, exist_ok=True)
    main(os.path.abspath(args[0]))
