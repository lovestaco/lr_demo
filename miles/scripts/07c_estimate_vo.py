"""Estimated voice-over timing (no audio): line lengths + per-word times from the text, so a scene can be built
and timed before the real take exists.

    python3 scripts/07c_estimate_vo.py assets/audio/vo_street_part2.md assets/audio/vo_street_part2

Writes <out>/lines.json in the same shape 07b_split_take.py writes ({num: text, duration, words: [[word, t]],
estimated: true}). Pace is measured on part 1's real take (Mark): ~0.31 s a word, pauses at punctuation.
Never overwrites a lines.json that came from a real take (no "estimated" flag) unless --force.
"""
import json, os, re, sys

WORD = 0.31                      # s per word (part 1: 24 words in 6.6 s incl. pauses ≈ 0.27 + pauses)
PAUSE = {".": 0.38, "?": 0.38, "!": 0.38, ":": 0.28, ",": 0.16, ";": 0.2}
LEAD, TAIL = 0.25, 0.35          # breath before the first word, after the last (07b clips carry ~0.35 s)
tok = lambda s: [t for t in re.split(r"[^a-z0-9]+", re.sub(r"\[[^\]]*\]", " ", s).lower()) if t]


def lines(md):
    rows = []
    for line in open(md, encoding="utf-8"):
        m = re.match(r"^\|\s*(\d+)\s*\|\s*([\d.]+)s\s*\|.*\|\s*(.+?)\s*\|\s*$", line)
        if m:
            rows.append((int(m.group(1)), float(m.group(2)), m.group(3)))
    return rows


def estimate(text):
    t, words = LEAD, []
    for chunk in re.findall(r"[^\s]+", re.sub(r"\[[^\]]*\]", " ", text)):
        for w in tok(chunk):
            words.append([w, round(t, 2)])
            t += WORD * (0.6 if len(w) <= 2 else 1.0 + 0.04 * max(0, len(w) - 7))
        t += PAUSE.get(chunk[-1], 0.0)
    return round(t + TAIL, 2), words


if __name__ == "__main__":
    md, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, "lines.json")
    if os.path.exists(p) and not json.load(open(p)).get("1", {}).get("estimated") and "--force" not in sys.argv:
        sys.exit(f"{p} comes from a real take; not overwriting (use --force)")
    meta = {}
    for num, start, text in lines(md):
        d, words = estimate(text)
        meta[str(num)] = {"text": text, "start": start, "duration": d, "words": words, "estimated": True}
        print(f"line {num}  {d:5.2f}s  {len(words)} words")
    json.dump(meta, open(p, "w"), indent=1)
    print("total", round(sum(v["duration"] for v in meta.values()), 1), "s ->", p)
