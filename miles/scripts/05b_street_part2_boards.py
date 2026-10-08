"""Street part 2, S16/S17: the product, as clean full-screen 2D frames (no Spidey): LiveReview's own demo footage on
the right two-thirds, a board on the left third whose items pop in on their words in the VO.

    python3 scripts/05b_street_part2_boards.py build/frames/street_part2_720p      # writes f_NNNN.jpg for the S16/S17 frames

Frame ranges and word frames come from build/street_part2_overlays.json (written by 04_street_part2.py), so the
boards re-time with the voice-over like the 3D scenes. The 3D render skips these frames.
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from pipeline import paths
import importlib
slides = importlib.import_module("03_make_slides")

W, H = 1280, 720
DEMO = os.path.join(paths.REPO, "videos", "livereview-launch", "assets")
LOGOS = os.path.join(paths.ROOT, "assets", "street2", "logos")
BG, CARD, INK, DIM = (12, 18, 32), (255, 255, 255), (15, 23, 42), (148, 163, 184)
ACCENT = {"s16": (37, 99, 235), "s17": (22, 163, 74)}
BOARDS = {
    "s16": dict(title="For your engineers: **attention + understanding**",
                items=["Issues ranked by importance", "A slide deck for every change", "A quick quiz to check understanding",
                       "Conversations right on the MR", "Livi: bot that turns your data into analysis reports and actionable items"],
                clips=["git-lrc_issue-navigator-compressed.mp4", "git-lrc_summary-deck-compressed.mp4",
                       "quiz-coverage_quiz-coverage-demo-compressed.mp4", "clip05_blast.mp4", "demo_livi_chat_bot.mp4"]),
    "s17": dict(title="For your agents: **enforcement + scale**",
                items=["Custom repository rules checked on every pre-commit", "Integrations: Slack, Teams, Discord", "MCP"],
                clips=["demo_cicd_gates.mp4", "demo_schedule_review.mp4", "clip14_nav.mp4"]),
}
VID = (452, 70, 1252, 520)                        # demo frame box on the right two-thirds (16:9-ish, letterboxed)


def clip_frames(name, n, cache={}):
    """The clip's frames at 30 fps, fitted into the video box (looped when it is shorter than needed)."""
    if name in cache:
        return cache[name]
    d = tempfile.mkdtemp()
    w, h = VID[2] - VID[0], VID[3] - VID[1]
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", os.path.join(DEMO, name), "-t", str(n / 30 + 0.5), "-vf",
                    f"fps=30,scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0x0c1220",
                    os.path.join(d, "c_%04d.png")], check=True)
    cache[name] = sorted(os.path.join(d, f) for f in os.listdir(d))
    return cache[name]


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


def board_layer(key, f, title_f, item_fs, slide):
    """The left-third card at frame f (slide: px offset for the S16 -> S17 swap)."""
    b = BOARDS[key]
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = 28 + slide, 40, 420 + slide, 680
    d.rounded_rectangle([x0, y0, x1, y1], radius=22, fill=CARD + (255,))
    d.rounded_rectangle([x0, y0, x1, y0 + 10], radius=5, fill=ACCENT[key] + (255,))
    if f >= title_f:
        a = min(1.0, (f - title_f + 1) / 6)
        rich(d, x0 + 26, y0 + 30, b["title"], 30, INK + (int(255 * a),), x1 - x0 - 52)
    y = y0 + 150
    cur = max((i for i, fi in enumerate(item_fs) if f >= fi), default=-1)
    for i, (txt, fi) in enumerate(zip(b["items"], item_fs)):
        if f < fi:
            break
        t = min(1.0, (f - fi + 1) / 7)
        pop = 0.7 + 0.3 * (1 - (1 - t) ** 3) + 0.06 * max(0.0, 1 - abs(t * 2 - 1.4))        # a small overshoot
        size = int(25 * pop)
        hi = i == cur
        if hi:
            tint = {"s16": (219, 234, 254), "s17": (220, 252, 231)}[key]       # the item being spoken
            lines_n = max(1, len(slides.wrap(slides.words(txt), {False: slides.font(size, slides.REGULAR), True: slides.font(size, slides.BOLD)},
                                             x1 - x0 - 90)[0]))
            d.rounded_rectangle([x0 + 14, y - 8, x1 - 14, y + int(size * 1.22) * lines_n + 10], radius=12, fill=tint + (255,))
        d.ellipse([x0 + 24, y + 2, x0 + 54, y + 32], fill=(ACCENT[key] if hi else DIM) + (255,))
        d.text((x0 + 39, y + 17), str(i + 1), font=slides.font(18, slides.BOLD), fill=(255, 255, 255, 255), anchor="mm")
        y = rich(d, x0 + 66, y, txt, size, (INK if hi else (100, 116, 139)) + (255,), x1 - x0 - 90)
        if key == "s17" and i == 1:                               # Slack, Teams, Discord in a row
            for kk, n in enumerate(("slack", "teams", "discord")):
                p = os.path.join(LOGOS, n + ".png")
                if os.path.exists(p):
                    lg = Image.open(p).convert("RGBA").resize((44, 44))
                    layer.alpha_composite(lg, (x0 + 66 + kk * 58, y + 4))
            y += 56
        y += 22
    return layer


def frame(key, f, ov, cfg):
    b = BOARDS[key]
    title_f = cfg[f"{key}_title"]
    item_fs = cfg[f"{key}_items"]
    a0, a1 = cfg[key]
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for yy in range(H):                                          # a soft vertical gradient
        c = int(10 * yy / H)
        d.line([(0, yy), (W, yy)], fill=(BG[0] + c, BG[1] + c, BG[2] + c + 4))
    cur = max((i for i, fi in enumerate(item_fs) if f >= fi), default=0)
    clip = b["clips"][cur]
    start = item_fs[cur] if f >= item_fs[0] else a0
    fr = clip_frames(clip, max(60, a1 - a0 + 30))
    shot = Image.open(fr[(f - start) % len(fr)]).convert("RGB")
    sh = Image.new("RGBA", (VID[2] - VID[0] + 40, VID[3] - VID[1] + 40), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([20, 20, sh.width - 20, sh.height - 20], radius=18, fill=(0, 0, 0, 160))
    img.paste(sh.filter(ImageFilter.GaussianBlur(12)), (VID[0] - 20, VID[1] - 12), sh.filter(ImageFilter.GaussianBlur(12)))
    mask = Image.new("L", shot.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, shot.width, shot.height], radius=16, fill=255)
    img.paste(shot, (VID[0], VID[1]), mask)
    d.text((VID[0], VID[3] + 40), "LiveReview", font=slides.font(30, slides.BOLD), fill=(226, 232, 240))
    d.text((VID[0] + 175, VID[3] + 44), "· hexmos.com/livereview", font=slides.font(24, slides.REGULAR), fill=DIM)
    slide = 0
    if key == "s16" and f > a1 - 10:                             # the S16 board slides out ...
        slide = -int(460 * ((f - (a1 - 10)) / 10) ** 2)
    if key == "s17" and f < a0 + 10:                             # ... and the S17 board slides in
        slide = -int(460 * (1 - (f - a0) / 10) ** 2)
    out = img.convert("RGBA")
    out.alpha_composite(board_layer(key, f, title_f, item_fs, slide))
    return out.convert("RGB")


if __name__ == "__main__":
    out = sys.argv[1]
    ov = json.load(open(os.path.join(paths.ROOT, "build", "street_part2_overlays.json")))
    cfg = ov["boards"]
    os.makedirs(out, exist_ok=True)
    n = 0
    for key in ("s16", "s17"):
        a0, a1 = cfg[key]
        for f in range(a0, a1 + 1):
            frame(key, f, ov, cfg).save(os.path.join(out, f"f_{f:04d}.jpg"), quality=92)
            n += 1
    print("BOARDS", n, "frames", cfg["s16"], cfg["s17"])
