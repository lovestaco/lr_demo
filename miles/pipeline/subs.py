"""Burned-in subtitles for the narrated videos, built from the voice-over data (no extra files).

    cues  = subs.cues_for_shot("street_part2_b", offset=0.0)     # [(t0, t1, [(word, t_word), ...])] in video seconds
    for frame in subs.Overlay(width, height).frames(cues, n_frames): ...   # RGBA bytes, one per video frame

Timing comes from the same data that places the audio: the shot's `vo N` markers (build/<shot>_cues.json) +
the per-word times of assets/audio/vo_<shot>/lines.json, so a re-timed animation re-syncs the subtitles and
several shots joined by 06_assemble keep their offsets. One short phrase is shown at a time; the word being
spoken is bold (bright yellow), the others regular (slightly dimmer yellow). Delivery tags like [confident] are dropped.
"""
import difflib, json, os, re, sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
FPS = 30
MAX_WORDS, MAX_CHARS, MIN_WORDS = 8, 48, 3
HOLD = 0.30                                         # a phrase stays this long after its last word starts speaking + word length
WORD_LEN = 0.45                                     # the last word of a line: assumed spoken length
CANON = {"1": "one", "2": "two", "3": "three", "cause": "cuz", "livy": "livi", "models": "model", "s": ""}

tok = lambda s: [t for t in re.split(r"[^a-z0-9]+", re.sub(r"\[[^\]]*\]", " ", s).lower()) if t]
canon = lambda t: CANON.get(t, t)


def strip_px(height):
    """Height of the bottom strip reserved for subtitles (even number of pixels): the video sits above it."""
    return int(round(height * 0.07 / 2)) * 2


def vo_dir(shot):
    """assets/audio/vo_<shot>, else the longest prefix (same rule as 06_assemble)."""
    parts = shot.split("_")
    for k in range(len(parts), 0, -1):
        d = os.path.join(ROOT, "assets", "audio", "vo_" + "_".join(parts[:k]))
        if os.path.isdir(d):
            return d
    return None


def display_words(text):
    """The words as written (tags removed); a lone dash joins the previous word."""
    out = []
    for w in re.sub(r"\[[^\]]*\]", " ", text).split():
        if out and not re.search(r"[A-Za-z0-9]", w):
            out[-1] += " " + w
        else:
            out.append(w)
    return out


def word_times(text, heard, duration):
    """[(display word, start seconds in the clip)]: the written words aligned to the heard ones (whisper)."""
    disp = display_words(text)
    flat = []                                       # (token, display idx)
    for i, w in enumerate(disp):
        flat += [(canon(t), i) for t in tok(w) if canon(t)]
    heard = [(canon(w), t) for w, t in heard if canon(w)]
    sm = difflib.SequenceMatcher(None, [t for t, _ in flat], [w for w, _ in heard], autojunk=False)
    tt = [None] * len(flat)
    for a, b, n in sm.get_matching_blocks():
        for j in range(n):
            tt[a + j] = heard[b + j][1]
    # unmatched tokens: spread evenly between the neighbouring matched times
    i = 0
    while i < len(tt):
        if tt[i] is None:
            j = i
            while j < len(tt) and tt[j] is None:
                j += 1
            lo = tt[i - 1] if i > 0 else 0.0
            hi = tt[j] if j < len(tt) else max(lo, duration - WORD_LEN)
            for q in range(i, j):
                tt[q] = lo + (hi - lo) * (q - i + 1) / (j - i + 1) if i > 0 else lo + (hi - lo) * (q - i) / (j - i + 1)
            i = j
        else:
            i += 1
    start = {}
    for (t, wi), ts in zip(flat, tt):
        start.setdefault(wi, ts)
    out, last = [], 0.0
    for i, w in enumerate(disp):
        ts = max(last, start.get(i, last))
        out.append((w, ts))
        last = ts
    return out


def phrases(words):
    """Split [(word, t)] into short on-screen phrases: sentences, then commas/dashes, then even pieces of <= MAX_WORDS."""
    sentences, cur = [], []
    for w, t in words:
        cur.append((w, t))
        if re.search(r"[.?!:;]$", w):
            sentences.append(cur)
            cur = []
    if cur:
        sentences.append(cur)
    out = []
    for sen in sentences:
        need = 2 if len(sen) > MAX_WORDS else MIN_WORDS            # a long sentence may break after a short clause
        parts, cur = [], []
        for k, (w, t) in enumerate(sen):
            cur.append((w, t))
            if re.search(r"[,—–]$", w) and len(cur) >= need and len(sen) - k - 1 >= 2:
                parts.append(cur)
                cur = []
        if cur:
            parts.append(cur)
        for part in parts:
            chars = sum(len(w) + 1 for w, _ in part)
            n = max(-(-len(part) // MAX_WORDS), -(-chars // MAX_CHARS))
            size = -(-len(part) // n)                                # even pieces, no stranded word
            out += [part[i:i + size] for i in range(0, len(part), size)]
    return out


def cues_for_shot(shot, offset=0.0):
    """[(t0, t1, [(word, t_word)])] in seconds of the (joined) video; empty if the shot has no voice-over data."""
    d = vo_dir(shot)
    cf = os.path.join(ROOT, "build", f"{shot}_cues.json")
    if not d or not os.path.exists(os.path.join(d, "lines.json")) or not os.path.exists(cf):
        return []
    lines = json.load(open(os.path.join(d, "lines.json"), encoding="utf-8"))
    markers = json.load(open(cf))["cues"]
    out = []
    for label, t in markers.items():
        if not label.startswith("vo "):
            continue
        n = label.split()[1]
        if n not in lines or not lines[n].get("words"):
            continue
        L = lines[n]
        base = offset + t
        ws = word_times(L["text"], L["words"], L["duration"])
        for ch in phrases(ws):
            t0 = base + ch[0][1]
            t1 = base + min(L["duration"], ch[-1][1] + WORD_LEN) + HOLD
            out.append((t0, t1, [(w, base + ts) for w, ts in ch]))
    out.sort(key=lambda c: c[0])
    for i in range(len(out) - 1):                   # never run into the next phrase
        a, b = out[i], out[i + 1]
        if a[1] > b[0]:
            out[i] = (a[0], b[0], a[2])
    return out


class Overlay:
    """Draws the subtitle band as an RGBA frame (cached per state: phrase + spoken word)."""

    def __init__(self, width, height):
        import importlib
        self.slides = importlib.import_module("03_make_slides")
        self.W, self.H = width, height
        s = self.s = height / 720.0
        self.strip = strip_px(height)
        self.size = max(11, int(round(self.strip * 0.72)))            # text fills the strip
        self.fonts = {}
        self.cache = {}
        self.blank = bytes(width * height * 4)

    def band(self, words, cur):
        key = (tuple(w for w, _ in words), cur)
        if key in self.cache:
            return self.cache[key]
        s, W, H = self.s, self.W, self.H
        size = self.size
        while True:
            if size not in self.fonts:
                self.fonts[size] = (self.slides.font(size, self.slides.REGULAR), self.slides.font(size, self.slides.BOLD))
            fr, fb = self.fonts[size]
            space = fr.getlength(" ")
            slots = [max(fr.getlength(w), fb.getlength(w)) for w, _ in words]       # fixed slot: no jitter when a word goes bold
            width = sum(slots) + space * (len(words) - 1)
            if width <= W - 40 * s or size <= 12:
                break
            size -= 1
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        x0 = (W - width) / 2
        y = H - self.strip + (self.strip - size * 1.0) / 2 - size * 0.12     # vertically centred in the strip (no band: the strip is black)
        x = x0
        for i, ((w, _), slot) in enumerate(zip(words, slots)):
            on = i == cur
            f = fb if on else fr
            col = (255, 214, 102, 255) if on else (226, 186, 88, 255)      # yellow; the spoken word bold + a touch brighter
            d.text((x + (slot - f.getlength(w)) / 2, y + size * 0.88), w, font=f, fill=col, anchor="ls")
            x += slot + space
        data = layer.tobytes()
        if len(self.cache) > 600:
            self.cache.clear()
        self.cache[key] = data
        return data

    def frames(self, cues, n_frames):
        """Yield n_frames RGBA byte strings (video frame i shows time i / FPS)."""
        ci = 0
        for i in range(n_frames):
            t = i / FPS
            while ci < len(cues) and cues[ci][1] <= t:
                ci += 1
            if ci < len(cues) and cues[ci][0] <= t:
                words = cues[ci][2]
                cur = max(k for k, (_, tw) in enumerate(words) if tw <= t + 1e-6)
                yield self.band(words, cur)
            else:
                yield self.blank
