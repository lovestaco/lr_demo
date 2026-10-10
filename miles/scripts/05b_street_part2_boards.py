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
    "s16": dict(title="**ATTENTION** goes where **RISK** is",
                items=["Issues ranked by importance", "A slide deck for every change", "A quick quiz to check understanding",
                       "Conversations right on the MR", "Livi: bot that turns your data into analysis reports and actionable items"],
                media=["blast_radius_zoom.mp4", "slide_deck.gif", "quiz.gif", "converse_in_mr.png", "demo_livi_chat_bot.mp4"],
                secs=[12.0, 5.0, 3.0, 2.0, 3.0],                       # media length -> >2 s goes full screen
                trim=[None, None, None, None, (2.0, 5.0)],            # Livi: only the 2 s-5 s section
                caption=None),
    "s17": dict(title="For your agents: **enforcement + scale**",
                items=["CI/CD Gates: Precise, Customized Merge Enforcement", "Integrations: Microsoft Teams, Slack", "MCP"],
                media=["demo_cicd_gates.mp4", "seq", None],                 # "seq": the stills in cfg["s17_seq"] (Teams 1 s, Slack 2 s)
                secs=[4.0, 2.0, 5.0],
                trim=[None, None, None],
                caption="MCP can be used to connect to any preferred AI Agent to operate Livi right from your agent."),
}

_cache = {}                                        # name -> (tmpdir, [frame paths]) ; only the current clip is kept


def media_frames(name, window, trim=None, contain=False):
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
                    (f"fps=30,scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x111827" if contain
                     else f"fps=30,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"),
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
        if media == "seq":                                       # stills one after another, each at its own frames (panel only)
            hit = next((q for q in cfg.get(f"{key}_seq", []) if q[0] <= f < q[2]), None)
            media = hit[1] if hit else "none"
            if hit:
                start, end = hit[0], hit[2]
        elif media is not None and b["secs"][cur] > FULL_AT:
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
        elif media != "none":
            fr = media_frames(media, end - start, b["trim"][cur], contain=media.endswith(".png") and b["media"][cur] == "seq")
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


# ------------------------------------------------------------------ the Meta section (2D, after "he goes up")
META_ROWS = [("docs/README.md", 9), ("payments/charge.go", 91), ("ui/button.css", 14), ("auth/session.ts", 78),
             ("config/flags.yaml", 22), ("db/migrate_042.sql", 64)]
GREEN, AMBER, RED, GREY = (34, 197, 94), (245, 158, 11), (220, 38, 38), (100, 116, 139)
smooth = lambda t: (lambda u: u * u * (3 - 2 * u))(max(0.0, min(1.0, t)))


def gradient_bg():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for yy in range(H):
        c = int(10 * yy / H)
        d.line([(0, yy), (W, yy)], fill=(BG[0] + c, BG[1] + c, BG[2] + c + 4))
    return img


def headline(out, f, items, y=64, size=60):
    """items = [(from_frame, text)]: the latest started one shows, fading in over 6 frames."""
    cur = max((i for i, (f0, _) in enumerate(items) if f >= f0), default=-1)
    if cur < 0:
        return
    f0, text = items[cur]
    a = min(1.0, (f - f0 + 1) / 6)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(layer)
    d = ImageDraw.Draw(layer)
    rich_center(d, W / 2, y + (1 - a) * 14, text, size, (255, 255, 255, int(255 * a)), W - 160)
    out.alpha_composite(layer)


def meta_rows_layer(f, w):
    """The change cards: they appear on "Meta", sort by risk on "risk-first", the low-risk ones slip away on "skip"."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, rw, rh, gap, y0 = 300, 680, 64, 16, 190
    order = sorted(range(len(META_ROWS)), key=lambda i: -META_ROWS[i][1])
    ks = smooth((f - w["risk"]) / 14)                              # 0 = as they came, 1 = sorted
    kk = smooth((f - w["skip"]) / 16)                              # the low-risk ones leave
    ka = smooth((f - w["attention"]) / 10)
    for i, (name, score) in enumerate(META_ROWS):
        t_in = smooth((f - (w["meta"] + i * 3)) / 8)
        if t_in <= 0:
            continue
        y_unsorted = y0 + i * (rh + gap)
        y_sorted = y0 + order.index(i) * (rh + gap)
        y = y_unsorted + (y_sorted - y_unsorted) * ks
        x = x0 - (1 - t_in) * 60
        a = t_in
        low = score < 30
        if low:
            x += kk * 260
            a *= (1 - kk)
        if a <= 0.01:
            continue
        col = RED if score >= 70 else (AMBER if score >= 30 else GREY)
        dim = low and kk > 0.0
        d.rounded_rectangle([x, y, x + rw, y + rh], radius=14, fill=(30, 41, 59, int(255 * a)),
                            outline=((AMBER + (int(255 * a * ka),)) if not low else None), width=4)
        d.text((x + 24, y + rh / 2), name, font=slides.font(26, slides.REGULAR), fill=(226, 232, 240, int(255 * a)), anchor="lm")
        pill = f"RISK {score}"
        pf = slides.font(22, slides.BOLD)
        pw = d.textlength(pill, font=pf) + 30
        d.rounded_rectangle([x + rw - pw - 16, y + 14, x + rw - 16, y + rh - 14], radius=12, fill=col + (int(255 * a),))
        d.text((x + rw - pw / 2 - 16, y + rh / 2), pill, font=pf, fill=(255, 255, 255, int(255 * a)), anchor="mm")
        if low and kk > 0.15:
            d.text((x - 26, y + rh / 2), "SKIPPED", font=slides.font(22, slides.BOLD), fill=GREY + (int(255 * a),), anchor="rm")
    return layer


def meta_frame(f, cfg):
    w = cfg["meta_words"]
    a0, a1 = cfg["meta_a"]
    b0, b1 = cfg["meta_b"]
    c0, c1 = cfg["meta_c"]
    out = gradient_bg().convert("RGBA")
    if f <= a1:                                                   # the idea
        headline(out, f, [(a0 + 2, "Inspection is a **big deal.**"), (w["meta"] - 2, "**Meta** saw it too."),
                          (w["risk"] - 3, "**Risk-first** review."), (w["low"] - 2, "Low-risk changes **skip the line.**"),
                          (w["attention"] - 3, "**ATTENTION** goes where **RISK** is.")])
        out.alpha_composite(meta_rows_layer(f, w))
    elif f <= b1:                                                 # the results
        headline(out, f, [(b0 + 2, "Meta's **results**")], y=70)
        cards = [(w["n1"], "1/50", "production incidents"), (w["n2"], "1/3", "deploy reverts"), (w["n3"], "33%", "lower wait time")]
        for i, (fr, big, label) in enumerate(cards):
            t = smooth((f - fr) / 9)
            if t <= 0:
                continue
            ov = 1 + 0.08 * max(0.0, 1 - abs(t * 2 - 1.3))
            cw, ch = int(360 * (0.7 + 0.3 * t) * ov), int(320 * (0.7 + 0.3 * t) * ov)
            cx, cy = 250 + i * 390, 400
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(layer)
            d.rounded_rectangle([cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2], radius=26, fill=(17, 24, 39, int(255 * t)),
                                outline=GREEN + (int(255 * t),), width=5)
            size = int(150 * (0.7 + 0.3 * t))
            d.text((cx, cy - 22), big, font=slides.font(size, slides.BOLD), fill=GREEN + (int(255 * t),), anchor="mm")
            d.text((cx, cy + ch / 2 - 56), label, font=slides.font(int(30 * (0.7 + 0.3 * t)), slides.REGULAR),
                   fill=(226, 232, 240, int(255 * t)), anchor="mm")
            out.alpha_composite(layer)
    else:                                                         # the same with LiveReview: its own risk-score footage, full screen
        fr = media_frames("risk-score_risk-score-demo-compressed.mp4", c1 - c0 + 1, (23.0, 23.0 + (c1 - c0) / 30.0 + 0.4), contain=True)
        shot = Image.open(fr[(f - c0) % len(fr)]).convert("RGB")
        out.paste(shot, (0, 0))
        d2 = ImageDraw.Draw(out)
        d2.rounded_rectangle([18, 16, 214, 58], radius=12, fill=(8, 12, 22, 170))
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
    if "meta" in cfg:
        for f in range(cfg["meta"][0], cfg["meta"][1] + 1):
            meta_frame(f, cfg).save(os.path.join(out, f"f_{f:04d}.jpg"), quality=92)
            n += 1
    print("BOARDS", n, "frames", cfg["s16"], cfg["s17"], cfg.get("meta"))
