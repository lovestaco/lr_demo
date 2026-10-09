"""Street part 2, S16/S17: the product, as clean full-screen 2D frames (no Spidey).

    python3 scripts/05b_street_part2_boards.py build/frames/street_part2_720p      # writes f_NNNN.jpg for the S16/S17 frames
    python3 scripts/05b_street_part2_boards.py build/frames/street_part2_b_720p street_part2_b

Frame ranges and word frames come from build/street_part2_overlays.json (written by 04_street_part2.py), so the
boards re-time with the voice-over like the 3D scenes. The 3D render skips these frames.

Layout: the board card sits on the left with the LiveReview wordmark in its blue header. Each item's media starts
in the right-hand panel and, when the item runs longer than 2 s, expands to full screen (short clips / stills stay
in the panel). An item with no clip (MCP) renders as a styled text card instead.
"""
import json, os, shutil, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from pipeline import paths
import importlib
slides = importlib.import_module("03_make_slides")

W, H = 1280, 720
DEMO = os.path.join(paths.REPO, "videos", "livereview-launch", "assets")
BG, CARD, INK, DIM = (12, 18, 32), (255, 255, 255), (15, 23, 42), (148, 163, 184)
ACCENT = {"s16": (37, 99, 235), "s17": (22, 163, 74)}
BRAND = (37, 99, 235)                              # LiveReview header blue
PANEL = (452, 70, 1252, 520)                       # demo frame in the right two-thirds
FULL = (0, 0, 1280, 720)                           # full-screen frame
EXPAND = 12                                        # frames to grow from the panel to full screen
FULL_AT = 2.0                                       # a media longer than this many seconds goes full screen

BOARDS = {
    "s16": dict(title="For your engineers: **attention + understanding**",
                items=["Issues ranked by importance", "A slide deck for every change", "A quick quiz to check understanding",
                       "Conversations right on the MR", "Livi: bot that turns your data into analysis reports and actionable items"],
                media=["blast_radius_zoom.mp4", "slide_deck.gif", "quiz.gif", "converse_in_mr.png", "demo_livi_chat_bot.mp4"],
                secs=[12.0, 5.0, 3.0, 2.0, 3.0],                       # media length -> >2 s goes full screen
                trim=[None, None, None, None, (2.0, 5.0)],            # Livi: only the 2 s-5 s section
                caption=None),
    "s17": dict(title="For your agents: **enforcement + scale**",
                items=["CI/CD Gates: Precise, Customized Merge Enforcement", "Integrations: Slack, Teams, Discord", "MCP"],
                media=["demo_cicd_gates.mp4", "demo_schedule_review.mp4", None],
                secs=[4.0, 4.0, 5.0],
                trim=[None, None, None],
                caption="MCP can be used to connect to any preferred AI Agent to operate Livi right from your agent."),
}

_cache = {}                                        # name -> (tmpdir, [frame paths]) ; only the current clip is kept


def media_frames(name, window, trim=None):
    """The media at 30 fps, cover-fitted to the full frame (loops when shorter than the on-screen window)."""
    global _cache
    if name in _cache:
        return _cache[name][1]
    for d_, _ in _cache.values():                  # one item plays at a time: drop the previous clip
        shutil.rmtree(d_, ignore_errors=True)
    _cache = {}
    d = tempfile.mkdtemp(prefix="board_")
    src = os.path.join(DEMO, name)
    ss = trim[0] if trim else 0.0
    clip_len = (trim[1] - trim[0]) if trim else None
    want = window / 30.0 + 0.1
    dur = min(want, clip_len) if clip_len else want
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{ss:.3f}", "-i", src, "-t", f"{dur:.3f}", "-vf",
                    f"fps=30,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
                    os.path.join(d, "c_%04d.png")], check=True)
    fr = sorted(os.path.join(d, f) for f in os.listdir(d))
    if not fr:                                     # a still that ffmpeg refused: load it directly
        Image.open(src).convert("RGB").save(os.path.join(d, "c_0001.png"))
        fr = [os.path.join(d, "c_0001.png")]
    _cache[name] = (d, fr)
    return fr


def rich(d, x, y, text, size, fill, max_w):
    """Wrapped text with **bold** spans; returns the y after it."""
    tokens = slides.words(text)
    fonts = {False: slides.font(size, slides.REGULAR), True: slides.font(size, slides.BOLD)}
    lines, space = slides.wrap(tokens, fonts, max_w)
    lh = int(size * 1.22)
    for line in lines:
        cx = x
        for wd, b in line:
            d.text((cx, y + size), wd, font=fonts[b], fill=fill, anchor="ls")
            cx += fonts[b].getlength(wd) + space
        y += lh
    return y


def rich_center(d, cx, y, text, size, fill, max_w):
    tokens = slides.words(text)
    fonts = {False: slides.font(size, slides.REGULAR), True: slides.font(size, slides.BOLD)}
    lines, space = slides.wrap(tokens, fonts, max_w)
    lh = int(size * 1.35)
    for line in lines:
        width = sum(fonts[b].getlength(wd) + space for wd, b in line)
        x = cx - width / 2
        for wd, b in line:
            d.text((x, y + size), wd, font=fonts[b], fill=fill, anchor="ls")
            x += fonts[b].getlength(wd) + space
        y += lh
    return y


def box_lerp(k):
    return tuple(PANEL[j] + (FULL[j] - PANEL[j]) * k for j in range(4))


def brand_header(d, x0, y0, x1, h=68):
    """The blue header on the board card: LiveReview in white, the URL in light grey."""
    d.rounded_rectangle([x0, y0, x1, y0 + h], radius=22, fill=BRAND + (255,))
    d.rectangle([x0, y0 + h - 22, x1, y0 + h], fill=BRAND + (255,))
    d.text((x0 + 24, y0 + 30), "LiveReview", font=slides.font(28, slides.BOLD), fill=(255, 255, 255, 255), anchor="ls")
    d.text((x0 + 24, y0 + 52), "hexmos.com/livereview", font=slides.font(15, slides.REGULAR), fill=(214, 224, 245, 255), anchor="ls")
    return y0 + h


def board_layer(key, f, title_f, item_fs, slide):
    """The left card: brand header, title, numbered items (the one being spoken highlighted)."""
    b = BOARDS[key]
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = 28 + slide, 40, 430 + slide, 682
    d.rounded_rectangle([x0, y0, x1, y1], radius=22, fill=CARD + (255,))
    y = brand_header(d, x0, y0, x1)
    if f >= title_f:
        a = min(1.0, (f - title_f + 1) / 6)
        y = rich(d, x0 + 26, y + 20, b["title"], 29, INK + (int(255 * a),), x1 - x0 - 52)
    y = max(y, y0 + 168) + 6
    cur = max((i for i, fi in enumerate(item_fs) if f >= fi), default=-1)
    for i, (txt, fi) in enumerate(zip(b["items"], item_fs)):
        if f < fi:
            break
        t = min(1.0, (f - fi + 1) / 7)
        pop = 0.7 + 0.3 * (1 - (1 - t) ** 3) + 0.06 * max(0.0, 1 - abs(t * 2 - 1.4))        # a small overshoot
        size = int(24 * pop)
        hi = i == cur
        if hi:
            tint = {"s16": (219, 234, 254), "s17": (220, 252, 231)}[key]
            fonts = {False: slides.font(size, slides.REGULAR), True: slides.font(size, slides.BOLD)}
            lines_n = max(1, len(slides.wrap(slides.words(txt), fonts, x1 - x0 - 90)[0]))
            d.rounded_rectangle([x0 + 14, y - 8, x1 - 14, y + int(size * 1.22) * lines_n + 10], radius=12, fill=tint + (255,))
        d.ellipse([x0 + 24, y + 2, x0 + 54, y + 32], fill=(ACCENT[key] if hi else DIM) + (255,))
        d.text((x0 + 39, y + 17), str(i + 1), font=slides.font(18, slides.BOLD), fill=(255, 255, 255, 255), anchor="mm")
        y = rich(d, x0 + 66, y, txt, size, (INK if hi else (100, 116, 139)) + (255,), x1 - x0 - 90)
        y += 22
    return layer


def text_card(img, box, caption):
    """An item with no clip: a dark card with the sentence centred."""
    x0, y0, x1, y1 = (int(v) for v in box)
    pad = 26
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=(17, 24, 39, 255))
    d.rounded_rectangle([x0, y0, x0 + 8, y1], radius=4, fill=BRAND + (255,))
    size = 30
    while size > 18:
        fonts = {False: slides.font(size, slides.REGULAR), True: slides.font(size, slides.BOLD)}
        lines, space = slides.wrap(slides.words(caption), fonts, x1 - x0 - 2 * pad)
        if len(lines) * int(size * 1.35) < (y1 - y0) - 2 * pad:
            break
        size -= 2
    y = (y0 + y1) / 2 - len(lines) * int(size * 1.35) / 2
    rich_center(d, (x0 + x1) / 2, y, caption, size, (226, 232, 240, 255), x1 - x0 - 2 * pad)
    return card


def frame(key, f, cfg):
    b = BOARDS[key]
    title_f = cfg[f"{key}_title"]
    item_fs = cfg[f"{key}_items"]
    a0, a1 = cfg[key]
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for yy in range(H):                                          # a soft vertical gradient
        c = int(10 * yy / H)
        d.line([(0, yy), (W, yy)], fill=(BG[0] + c, BG[1] + c, BG[2] + c + 4))

    cur = max((i for i, fi in enumerate(item_fs) if f >= fi), default=-1)
    k = 0.0                                                      # 0 = panel, 1 = full screen
    media, start, end = None, None, None
    if cur >= 0:
        start = item_fs[cur]
        end = item_fs[cur + 1] if cur + 1 < len(item_fs) else a1
        media = b["media"][cur]
        if media is not None and b["secs"][cur] > FULL_AT:
            t = max(0.0, (f - start) / EXPAND)
            k = min(1.0, t) * min(1.0, t) * (3 - 2 * min(1.0, t))     # smoothstep out of the panel
    box = box_lerp(k)

    slide = 0
    if key == "s16" and f > a1 - 10:                             # the S16 board slides out ...
        slide = -int(460 * ((f - (a1 - 10)) / 10) ** 2)
    if key == "s17" and f < a0 + 10:                             # ... and the S17 board slides in
        slide = -int(460 * (1 - (f - a0) / 10) ** 2)
    out = img.convert("RGBA")
    out.alpha_composite(board_layer(key, f, title_f, item_fs, slide))

    if cur >= 0:
        bx0, by0, bx1, by1 = (int(v) for v in box)
        bw, bh = bx1 - bx0, by1 - by0
        if media is None:
            out.alpha_composite(text_card(img, box, b["caption"]))
        else:
            fr = media_frames(media, end - start, b["trim"][cur])
            shot = Image.open(fr[(f - start) % len(fr)]).convert("RGB").resize((bw, bh))
            radius = int(16 * (1 - k))
            if radius > 1:
                sh = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
                ImageDraw.Draw(sh).rounded_rectangle([20, 20, bw + 20, bh + 20], radius=radius + 4, fill=(0, 0, 0, 170))
                out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)), (bx0 - 20, by0 - 20))
            mask = Image.new("L", (bw, bh), 0)
            ImageDraw.Draw(mask).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=radius, fill=255)
            out.paste(shot, (bx0, by0), mask)

    if k > 0.55:                                                 # full screen: keep a small wordmark top-left
        d2 = ImageDraw.Draw(out)
        d2.rounded_rectangle([18, 16, 214, 58], radius=12, fill=(8, 12, 22, 150))
        d2.text((32, 40), "LiveReview", font=slides.font(22, slides.BOLD), fill=(255, 255, 255, 235), anchor="ls")
        d2.text((150, 40), "· hexmos.com/livereview", font=slides.font(14, slides.REGULAR), fill=(206, 214, 230, 220), anchor="ls")
    return out.convert("RGB")


if __name__ == "__main__":
    out = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else "street_part2"
    ov = json.load(open(os.path.join(paths.ROOT, "build", f"{name}_overlays.json")))
    cfg = ov["boards"]
    os.makedirs(out, exist_ok=True)
    n = 0
    for key in ("s16", "s17"):
        a0, a1 = cfg[key]
        for f in range(a0, a1 + 1):
            frame(key, f, cfg).save(os.path.join(out, f"f_{f:04d}.jpg"), quality=92)
            n += 1
    print("BOARDS", n, "frames", cfg["s16"], cfg["s17"])
