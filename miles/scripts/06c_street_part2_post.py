"""Street part 2 post: frames -> video, with the lower-third captions laid over (no extra frames written to disk).

    python3 scripts/06c_street_part2_post.py build/frames/street_part2_720p     # -> renders/street_part2_720p.mp4
    python3 scripts/06c_street_part2_post.py build/frames/street_part2_a_720p street_part2_a   # part 2a (its own overlays)
    python3 scripts/06_assemble.py street_part2 --height 720 --music assets/audio/music/bed_street.mp3

Captions come from build/street_part2_overlays.json ({f0, f1, text, row}); captions that end on the same frame are
one line that builds up phrase by phrase (S14's three things). Each fades in over 6 frames. **bold** in yellow.
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from pipeline import paths
import importlib
slides = importlib.import_module("03_make_slides")
W, H, FPS = 1280, 720, 30
FADE = 6


def caption(img, parts, alpha):
    """A lower third: dark rounded band, white text, bold in warm yellow; parts = [(text, alpha), ...] on one line."""
    size = 34
    tokens = []
    for text, a in parts:
        if tokens:
            tokens.append(("   ", False, a))
        tokens += [(w, b, a) for w, b in slides.words(text)]
    fonts = {False: slides.font(size, slides.REGULAR), True: slides.font(size, slides.BOLD)}
    while size > 20:
        fonts = {False: slides.font(size, slides.REGULAR), True: slides.font(size, slides.BOLD)}
        width = sum(fonts[b].getlength(w) + fonts[False].getlength(" ") for w, b, _ in tokens)
        if width < W - 160:
            break
        size -= 2
    width = sum(fonts[b].getlength(w) + fonts[False].getlength(" ") for w, b, _ in tokens)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0 = (W - width) / 2
    y = H - 92
    d.rounded_rectangle([x0 - 28, y - 18, x0 + width + 20, y + size + 18], radius=16, fill=(8, 12, 22, int(190 * alpha)))
    x = x0
    for w, b, a in tokens:
        col = (255, 214, 102) if b else (255, 255, 255)
        d.text((x, y + size * 0.85), w, font=fonts[b], fill=col + (int(255 * a * alpha),), anchor="ls")
        x += fonts[b].getlength(w) + fonts[False].getlength(" ")
    out = img.convert("RGBA")
    out.alpha_composite(layer)
    return out.convert("RGB")


if __name__ == "__main__":
    src = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else "street_part2"
    ov = json.load(open(os.path.join(paths.ROOT, "build", f"{name}_overlays.json")))
    caps = ov["captions"]
    end = ov["end"]
    out = os.path.join(paths.RENDERS, f"{name}_720p.mp4")
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], stdin=subprocess.PIPE)
    missing = 0
    for f in range(1, end + 1):
        p = os.path.join(src, f"f_{f:04d}.jpg")
        if not os.path.exists(p):
            missing += 1
            img = Image.new("RGB", (W, H), (0, 0, 0))
        else:
            img = Image.open(p).convert("RGB")
            if img.size != (W, H):
                img = img.resize((W, H))
        live = [c for c in caps if c["f0"] <= f <= c["f1"]]
        if live:
            groups = {}
            for c in live:
                groups.setdefault(c["f1"], []).append(c)
            g = max(groups.values(), key=lambda cs: max(c["f0"] for c in cs))      # the newest line wins
            g.sort(key=lambda c: c["row"])
            parts = [(c["text"], min(1.0, (f - c["f0"] + 1) / FADE)) for c in g]
            band = min(1.0, (f - min(c["f0"] for c in g) + 1) / FADE, (g[0]["f1"] - f + 1) / FADE)
            img = caption(img, parts, band)
        ff.stdin.write(img.tobytes())
    ff.stdin.close()
    ff.wait()
    print("VIDEO", out, f"frames 1-{end}", f"missing {missing}")
