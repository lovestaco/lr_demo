"""Split one full voice-over take (e.g. downloaded from the ElevenLabs website) into per-line clips.

    python3 scripts/07b_split_take.py assets/audio/vo/piece1_vo_gen2.mp3
    python3 scripts/07b_split_take.py TAKE.mp3 --script assets/audio/vo_piece2.md --out assets/audio/vo_piece2

Transcribes the take with faster-whisper (word timestamps), matches the words against the
lines in assets/audio/vo_piece1.md in order, cuts in the middle of the real pause nearest each
sentence boundary (whisper's own word edges clip syllables), and writes assets/audio/vo/line_NN.wav plus
vo/lines.json {num: text, start (cue in the cut), duration, take, src_start, src_end}.

Per-line takes (one website generation per line, named take_NN.mp3):
    python3 scripts/07b_split_take.py --lines assets/audio/vo_street_part2/takes --script assets/audio/vo_street_part2.md --out assets/audio/vo_street_part2
converts each to line_NN.wav, transcribes its word times and merges it into <out>/lines.json (other lines,
e.g. estimated ones, are kept).
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


def silences(path, db=-42, min_len=0.12):
    """[(start, end)] of the pauses in the take (ffmpeg silencedetect)."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=n={db}dB:d={min_len}",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", err)]
    en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", err)]
    return list(zip(st, en))


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout)


def main(take):
    words = transcribe(take)
    lines = script_lines()
    # whisper word times place each line roughly; its starts run late and ends early, so the actual
    # cut goes in the middle of the real pause nearest each boundary (never through a word)
    spans, i = [], 0
    for num, cue, text in lines:
        n = len(tok(text))
        spans.append((words[i][1], words[min(i + n, len(words)) - 1][2], i, i + n))
        i += n
    gaps = silences(take)
    total = duration(take)
    cuts = [0.0]
    for (s0, e0, _, _), (s1, e1, _, _) in zip(spans, spans[1:]):
        mid = (e0 + s1) / 2
        near = [g for g in gaps if g[1] > e0 - 0.5 and g[0] < s1 + 0.5]
        g = min(near, key=lambda g: abs((g[0] + g[1]) / 2 - mid)) if near else (mid, mid)
        cuts.append((g[0] + g[1]) / 2)
    cuts.append(total)
    meta = {}
    for k, (num, cue, text) in enumerate(lines):
        a, b = cuts[k], cuts[k + 1]
        out = os.path.join(OUT, f"line_{num:02d}.wav")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", take, "-ss", f"{a:.3f}", "-to", f"{b:.3f}",
                        "-af", "afade=t=in:d=0.02,areverse,afade=t=in:d=0.06,areverse", "-ar", "44100", out], check=True)
        line_words = [(w, round(ws - a, 3)) for w, ws, we in words[spans[k][2]:spans[k][3]]]
        meta[str(num)] = {"text": re.sub(r"\[[^\]]*\]\s*", "", text), "start": cue, "duration": round(b - a, 2),
                          "take": os.path.basename(take), "src_start": round(a, 3), "src_end": round(b, 3),
                          "words": line_words}                 # [word, seconds from clip start]
        print(f"line {num:2d}  {a:6.2f}-{b:6.2f}  ({b - a:4.2f}s)  {text}")
    json.dump(meta, open(os.path.join(OUT, "lines.json"), "w"), indent=1)


def per_line(folder):
    path = os.path.join(OUT, "lines.json")
    meta = json.load(open(path)) if os.path.exists(path) else {}
    text = {num: t for num, cue, t in script_lines()}
    for f in sorted(os.listdir(folder)):
        m = re.match(r"take_(\d+)\.(mp3|wav)$", f)
        if not m:
            continue
        num, take = int(m.group(1)), os.path.join(folder, f)
        out = os.path.join(OUT, f"line_{num:02d}.wav")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", take, "-ar", "44100", out], check=True)
        words = transcribe(out)
        want = tok(text[num])
        if [w for w, _, _ in words] != want:
            print(f"  line {num}: whisper heard {' '.join(w for w, _, _ in words)!r}")
        meta[str(num)] = {"text": re.sub(r"\[[^\]]*\]\s*", "", text[num]), "duration": round(duration(out), 2),
                          "take": f, "words": [(w, round(s, 3)) for w, s, e in words]}
        print(f"line {num:2d}  {duration(out):5.2f}s  {len(words)} words")
    json.dump(meta, open(path, "w"), indent=1)


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--script" in args:
        SCRIPT = os.path.abspath(args[args.index("--script") + 1])
    if "--out" in args:
        OUT = os.path.abspath(args[args.index("--out") + 1])
        os.makedirs(OUT, exist_ok=True)
    if "--lines" in args:
        per_line(os.path.abspath(args[args.index("--lines") + 1]))
    else:
        main(os.path.abspath(args[0]))
