"""Screen content for the 60s piece (slides 1-19): static slides + animated sequences.

    python3 scripts/03b_make_screens.py          # -> assets/screens/*.png and assets/screens/<seq>/f_####.png

Rules: black on white, one font size per screen, emphasis via **bold** only; animations
carry the idea (velocity, checklist, growing system) instead of extra text. Every screen
must be self-contained (no "it/this/that"): viewers miss slides, so each one repeats the
key term — **inspection** — in bold (keep it simple: no "AI-assisted" every time).
"""
import importlib, math, os, random, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from pipeline import paths

slides = importlib.import_module("03_make_slides")          # reuse layout(), font(), words()
OUT = os.path.join(paths.ROOT, "assets", "screens")
W, H = 1280, 720
INK, MUTED, BLUE, RED, GREEN = (12, 12, 12), (110, 110, 110), (37, 99, 235), (220, 38, 38), (22, 163, 74)
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

STATIC = {
    "s01_generation": "You already ship a lot of **AI-generated code.**",
    "s02_inspect": "But do you do enough **inspection?**",
    "s03a_users": "Your users deserve **inspection.**",
    "s03b_profession": "Your profession demands **inspection.**",
    "s03c_reputation": "Your reputation depends on **inspection.**",
    "s04_layer": "Every team needs an **inspection layer.**",
    "s05_volume": "Fast shipping creates a **huge volume of code.**",
    "s06_attention": "But **human attention** is still limited.",
    "s07_deeper": "More code also brings **deeper consequences…**",
}


def text_screen(text, size=None):
    """A slide rendered at 1920x1080 by 03_make_slides, scaled to the screen size."""
    tmp = os.path.join(OUT, "_tmp.png")
    old = slides.paths.SLIDES
    slides.paths.SLIDES = OUT
    out, _ = slides.slide(0, text)
    slides.paths.SLIDES = old
    return Image.open(out).convert("RGB").resize((W, H), Image.LANCZOS)


def caption(d, text, y, size=54):
    """One-line caption with **bold** spans (single size, shrunk to fit the screen width)."""
    width = lambda sz: sum(slides.font(sz, slides.BOLD if b else slides.REGULAR).getlength(w + " ")
                           for w, b in slides.words(text))
    while size > 30 and width(size) > W - 140:
        size -= 2
    x = 70
    for w, b in slides.words(text):
        f = slides.font(size, slides.BOLD if b else slides.REGULAR)
        d.text((x, y), w, font=f, fill=INK, anchor="ls")
        x += f.getlength(w) + f.getlength(" ")


def seq_dir(name):
    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)
    return d


# ---------------------------------------------------------------- velocity: code scrolling faster and faster
def velocity(n=150):
    r = random.Random(3)
    kws = ["def", "return", "if", "for", "await", "class", "import", "const", "let", "fn"]
    names = ["review", "diff", "hunk", "commit", "merge", "deploy", "cache", "user", "token", "retry", "parse"]
    lines = []
    for i in range(600):
        indent = "    " * r.randint(0, 3)
        lines.append((indent, f"{r.choice(kws)} {r.choice(names)}_{r.choice(names)}({r.choice(names)}):", r.random()))
    mono = ImageFont.truetype(MONO, 26)
    d_out = seq_dir("velocity")
    off = 0.0
    for i in range(n):
        t = i / (n - 1)
        speed = 2 + 140 * t ** 2.2                       # px per frame, accelerating
        off += speed
        img = Image.new("RGB", (W, H), (255, 255, 255))
        d = ImageDraw.Draw(img)
        caption(d, "Code now ships at **great velocity.**", 90)
        d.rounded_rectangle([60, 130, W - 60, H - 40], radius=18, fill=(15, 23, 42))
        ed = Image.new("RGB", (W - 120, H - 170), (15, 23, 42))
        de = ImageDraw.Draw(ed)
        lh = 34
        first = int(off // lh)
        for k in range(ed.height // lh + 2):
            ind, txt, c = lines[(first + k) % len(lines)]
            y = k * lh - (off % lh) + 10
            col = (148, 163, 184) if c < 0.5 else (125, 211, 252) if c < 0.8 else (134, 239, 172)
            de.text((60 + len(ind) * 14, y), txt, font=mono, fill=col)
            de.text((12, y), f"{first + k + 1:4d}", font=ImageFont.truetype(MONO, 18), fill=(71, 85, 105))
        if t > 0.35:                                      # motion smear as it speeds up
            from PIL import ImageFilter
            ed = ed.filter(ImageFilter.BoxBlur(min(6, int((t - 0.35) * 14))))
        img.paste(ed, (60, 130))
        img.save(os.path.join(d_out, f"f_{i + 1:04d}.png"))
    return n


# ---------------------------------------------------------------- checklist: "you still must" ticks in
CHECK = ["Reduce **production incidents**", "Reduce **security incidents**",
         "Reduce **performance regressions**", "Deliver **stellar customer experiences**"]


def checklist(n=300, first=20, every=62):
    d_out = seq_dir("checklist")
    for i in range(n):
        img = Image.new("RGB", (W, H), (255, 255, 255))
        d = ImageDraw.Draw(img)
        caption(d, "And you **still** must:", 120)
        for k, item in enumerate(CHECK):
            t = (i - first - k * every) / 10.0
            if t < 0:
                continue
            a = min(1.0, t)
            y = 230 + k * 115
            x0 = 90
            # checkbox + tick
            d.rounded_rectangle([x0, y - 50, x0 + 56, y + 6], radius=10, outline=INK, width=5)
            if t > 0.6:
                d.line([(x0 + 12, y - 22), (x0 + 25, y - 8), (x0 + 48, y - 42)], fill=GREEN, width=9)
            # text slides in
            shift = int((1 - a) * 60)
            x = x0 + 90 + shift
            for w, b in slides.words(item):
                f = slides.font(54, slides.BOLD if b else slides.REGULAR)
                col = tuple(int(255 - (255 - c) * a) for c in INK)
                d.text((x, y), w, font=f, fill=col, anchor="ls")
                x += f.getlength(w) + f.getlength(" ")
        img.save(os.path.join(d_out, f"f_{i + 1:04d}.png"))
    return n


# ---------------------------------------------------------------- system: graph grows, then bugs crawl in
def system(n=210, grow=110, name="system",
           caps=("More code means **bigger systems**", "More code means **more complexity, more bugs.**"), glyph="bug"):
    r = random.Random(11)
    nodes = [(W / 2, H / 2 + 40)]
    edges = []
    for k in range(1, 46):
        a, rad = r.uniform(0, 2 * math.pi), r.uniform(80, 330)
        p = (W / 2 + math.cos(a) * rad * 1.6, H / 2 + 40 + math.sin(a) * rad * 0.8)
        p = (min(W - 70, max(70, p[0])), min(H - 50, max(170, p[1])))
        near = sorted(range(len(nodes)), key=lambda j: (nodes[j][0] - p[0]) ** 2 + (nodes[j][1] - p[1]) ** 2)
        nodes.append(p)
        edges += [(near[0], k)] + ([(near[1], k)] if len(near) > 1 and r.random() < 0.6 else [])
    bugs = [(r.randrange(len(edges)), r.random(), r.uniform(0.004, 0.012)) for _ in range(22)]
    d_out = seq_dir(name)
    for i in range(n):
        img = Image.new("RGB", (W, H), (255, 255, 255))
        d = ImageDraw.Draw(img)
        shown = 1 + int(min(1.0, i / grow) * (len(nodes) - 1))
        caption(d, caps[0] if i < grow + 20 else caps[1], 100)
        for a, b in edges:
            if a < shown and b < shown:
                d.line([nodes[a], nodes[b]], fill=(180, 190, 205), width=3)
        for k in range(shown):
            x, y = nodes[k]
            rr = 14 if k == 0 else 9
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=BLUE)
        if i >= grow + 20:
            m = i - grow - 20
            for j, (e, p0, sp) in enumerate(bugs[: min(len(bugs), 2 + m // 3)]):
                a, b = edges[e]
                t = (p0 + sp * m) % 1.0
                x = nodes[a][0] + (nodes[b][0] - nodes[a][0]) * t
                y = nodes[a][1] + (nodes[b][1] - nodes[a][1]) * t
                (spider if glyph == "spider" else bug)(d, x, y, i + j * 7)
        img.save(os.path.join(d_out, f"f_{i + 1:04d}.png"))
    return n


def bug(d, x, y, phase):
    d.ellipse([x - 10, y - 13, x + 10, y + 13], fill=RED)
    for s in (-1, 1):
        for lg in (-8, 0, 8):
            d.line([(x, y + lg), (x + s * 17, y + lg - 4)], fill=RED, width=3)


def spider(d, x, y, phase):
    """Black spider with a red mark; legs twitch with `phase` so the swarm looks alive."""
    ink = (24, 24, 30)
    for s in (-1, 1):
        for k, ang in enumerate((-50, -18, 14, 44)):
            a = math.radians(ang + 7 * math.sin(phase * 0.9 + k * 1.7 + s))
            kx, ky = x + s * 15 * math.cos(a), y + 15 * math.sin(a) - 7      # knee (raised)
            fx_, fy = x + s * 27 * math.cos(a), y + 27 * math.sin(a) + 6     # foot
            d.line([(x + s * 5, y), (kx, ky), (fx_, fy)], fill=ink, width=3, joint="curve")
    d.ellipse([x - 11, y - 4, x + 11, y + 18], fill=ink)                    # abdomen
    d.ellipse([x - 7, y - 13, x + 7, y + 1], fill=ink)                      # head
    d.polygon([(x, y + 3), (x - 4, y + 8), (x, y + 13), (x + 4, y + 8)], fill=RED)


# ================================================================ piece 2
STATIC2 = {
    "p2_s01": "You already ship a lot of **AI-generated code.**",
    "p2_s02": "But do you do enough **code inspection?**",
    "p2_attention": "Because **human attention** is still limited.",
    "p2_risk": "Broken review means **production risk** and **lost customers.**",
    "p2_competitive": "How do you stay **competitive?**",
    "p2_layer": "You need a better **inspection layer.**",
    "p2_end": "**Inspect properly.** Keep production stable. Keep customers happy. **Keep your dollars.**",
}


def review_queue(n=180):
    """Incoming PRs race up, reviewed crawls, coverage bar drains red."""
    d_out = seq_dir("p2_review_queue")
    big = slides.font(96, slides.BOLD)
    lab = slides.font(40, slides.REGULAR)
    for i in range(n):
        t = i / (n - 1)
        img = Image.new("RGB", (W, H), (255, 255, 255))
        d = ImageDraw.Draw(img)
        caption(d, "Traditional code review **can't keep up.**", 95)
        incoming = int(12 + 470 * t ** 1.8)
        reviewed = int(3 + 9 * t)
        for x0, label, val, col in ((90, "Incoming PRs", incoming, RED), (690, "Reviewed", reviewed, INK)):
            d.text((x0, 210), label, font=lab, fill=MUTED, anchor="ls")
            d.text((x0, 320), f"{val}", font=big, fill=col, anchor="ls")
        # stack of incoming PR cards piling up on the left
        cards = min(40, int(incoming / 12))
        for k in range(cards):
            x = 90 + (k % 8) * 62
            y = 560 - (k // 8) * 34
            d.rounded_rectangle([x, y, x + 54, y + 28], radius=5, fill=(248, 113, 113), outline=RED, width=3)
        for k in range(min(8, reviewed)):
            x = 690 + k * 62
            d.rounded_rectangle([x, 560, x + 54, 588], radius=5, fill=(74, 222, 128), outline=GREEN, width=3)
        # coverage bar
        cov = reviewed / max(1, incoming)
        d.text((90, 650), "Review coverage", font=lab, fill=MUTED, anchor="ls")
        d.rounded_rectangle([470, 620, 1190, 660], radius=12, fill=(203, 213, 225))
        w = int(720 * min(1.0, cov))
        d.rounded_rectangle([470, 620, 470 + max(24, w), 660], radius=12, fill=GREEN if cov > 0.15 else RED)
        d.text((1190, 700), f"{cov * 100:.0f}%", font=lab, fill=RED if cov < 0.15 else INK, anchor="rs")
        img.save(os.path.join(d_out, f"f_{i + 1:04d}.png"))
    return n


def _icon_server(d, cx, cy, s):
    for k in range(3):
        y = cy - s * 0.55 + k * s * 0.38
        d.rounded_rectangle([cx - s * 0.6, y, cx + s * 0.6, y + s * 0.3], radius=8, fill=(51, 65, 85))
        d.ellipse([cx + s * 0.38, y + s * 0.1, cx + s * 0.48, y + s * 0.2], fill=RED)
    d.line([(cx - s * 0.75, cy - s * 0.75), (cx + s * 0.75, cy + s * 0.75)], fill=RED, width=int(s * 0.12))
    d.line([(cx + s * 0.75, cy - s * 0.75), (cx - s * 0.75, cy + s * 0.75)], fill=RED, width=int(s * 0.12))


def _icon_lock(d, cx, cy, s):
    d.rounded_rectangle([cx - s * 0.5, cy - s * 0.1, cx + s * 0.5, cy + s * 0.6], radius=10, fill=RED)
    d.arc([cx - s * 0.32, cy - s * 0.75, cx + s * 0.32, cy - s * 0.1 + s * 0.1], 180, 300, fill=(51, 65, 85), width=int(s * 0.12))
    d.ellipse([cx - s * 0.08, cy + s * 0.12, cx + s * 0.08, cy + s * 0.28], fill=(255, 255, 255))
    d.line([(cx, cy + s * 0.25), (cx, cy + s * 0.42)], fill=(255, 255, 255), width=int(s * 0.07))


def _icon_perf(d, cx, cy, s):
    d.line([(cx - s * 0.7, cy + s * 0.65), (cx + s * 0.75, cy + s * 0.65)], fill=(148, 163, 184), width=4)
    d.line([(cx - s * 0.7, cy + s * 0.65), (cx - s * 0.7, cy - s * 0.7)], fill=(148, 163, 184), width=4)
    pts = [(-0.6, -0.5), (-0.3, -0.35), (0.0, -0.45), (0.25, 0.05), (0.45, 0.2), (0.65, 0.55)]
    d.line([(cx + x * s, cy + y * s) for x, y in pts], fill=RED, width=int(s * 0.1), joint="curve")
    d.polygon([(cx + 0.72 * s, cy + 0.68 * s), (cx + 0.5 * s, cy + 0.62 * s), (cx + 0.68 * s, cy + 0.42 * s)], fill=RED)


def _icon_badui(d, cx, cy, s):
    d.rounded_rectangle([cx - s * 0.75, cy - s * 0.6, cx + s * 0.75, cy + s * 0.65], radius=10, outline=(51, 65, 85), width=5)
    d.rectangle([cx - s * 0.75, cy - s * 0.6, cx + s * 0.75, cy - s * 0.38], fill=(51, 65, 85))
    d.rectangle([cx - s * 0.55, cy - s * 0.25, cx + s * 0.15, cy - s * 0.05], fill=(203, 213, 225))   # misaligned blocks
    d.rectangle([cx - s * 0.2, cy - s * 0.12, cx + s * 0.6, cy + s * 0.12], fill=(254, 202, 202))
    d.rectangle([cx - s * 0.65, cy + s * 0.2, cx - s * 0.05, cy + s * 0.5], fill=(203, 213, 225))
    d.rectangle([cx + s * 0.1, cy + s * 0.3, cx + s * 0.95, cy + s * 0.48], fill=RED)                # overflowing button


QUADS = [("Downtime", _icon_server), ("Security issues", _icon_lock),
         ("Performance regressions", _icon_perf), ("Bad UI", _icon_badui)]


def quadrants():
    """p2_quad_0..4: caption + 0..4 risk tiles (2x2)."""
    lab = slides.font(52, slides.BOLD)
    for k in range(len(QUADS) + 1):
        img = Image.new("RGB", (W, H), (255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((70, 82), "Customers walk away when there's:", font=slides.font(52, slides.REGULAR), fill=INK, anchor="ls")
        for q, (name, icon) in enumerate(QUADS[:k]):
            col, row = q % 2, q // 2
            x0, y0 = 70 + col * 580, 120 + row * 290
            d.rounded_rectangle([x0, y0, x0 + 560, y0 + 270], radius=22, fill=(254, 226, 226), outline=RED, width=5)
            icon(d, x0 + 105, y0 + 135, 90)
            parts = [name] if name == "Bad UI" else name.split(" ", 1)
            for j, part in enumerate(parts):
                d.text((x0 + 200, y0 + 135 + (j - (len(parts) - 1) / 2) * 60), part, font=lab, fill=INK, anchor="lm")
        img.save(os.path.join(OUT, f"p2_quad_{k}.png"))
    return len(QUADS) + 1


def leaving(n=96):
    """Customers walk out of frame (after the 4 risks)."""
    d_out = seq_dir("p2_leaving")
    base = Image.open(os.path.join(OUT, "p2_quad_4.png")).convert("RGB")
    for i in range(n):
        img = base.copy()
        ov = Image.new("RGBA", (W, H), (255, 255, 255, int(215 * min(1, i / 16))))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, W, 112], fill=(255, 255, 255))                 # replace the caption cleanly
        x = d.text((70, 82), "…and customers ", font=slides.font(52, slides.REGULAR), fill=INK, anchor="ls") or \
            70 + slides.font(52, slides.REGULAR).getlength("…and customers ")
        d.text((x, 82), "walk away.", font=slides.font(52, slides.BOLD), fill=INK, anchor="ls")
        for k in range(9):
            px = 70 + k * 135 + max(0, i - 14) * 20
            if px > W + 60:
                continue
            y = 500 + (k % 2) * 60
            bob = 6 * math.sin((i + k * 3) * 0.6)
            d.ellipse([px - 22, y - 120 + bob, px + 22, y - 76 + bob], fill=(71, 85, 105))
            d.rounded_rectangle([px - 30, y - 70 + bob, px + 30, y + 10 + bob], radius=14, fill=(71, 85, 105))
        img.save(os.path.join(d_out, f"f_{i + 1:04d}.png"))
    return n


def tower_labels():
    """Front faces for the thesis tower blocks."""
    blocks = [("INSPECTION", (37, 99, 235)), ("ENGINEERS' CONFIDENCE", (30, 41, 59)),
              ("CUSTOMER CONFIDENCE", (30, 41, 59)), ("COMPETITIVE PRODUCT", (30, 41, 59))]
    for i, (text, bg) in enumerate(blocks):
        img = Image.new("RGB", (1600, 400), bg)
        d = ImageDraw.Draw(img)
        size = 150
        while slides.font(size, 850).getlength(text) > 1480:
            size -= 4
        d.text((800, 200), text, font=slides.font(size, 850), fill=(255, 255, 255), anchor="mm")
        img.save(os.path.join(OUT, f"tower_{i}.png"))
    bill = Image.new("RGB", (600, 260), (74, 155, 98))
    d = ImageDraw.Draw(bill)
    d.rounded_rectangle([14, 14, 586, 246], radius=16, outline=(214, 240, 220), width=6)
    d.ellipse([220, 50, 380, 210], outline=(214, 240, 220), width=6)
    d.text((300, 132), "$", font=slides.font(130, 850), fill=(236, 252, 240), anchor="mm")
    d.text((60, 70), "100", font=slides.font(44, 800), fill=(214, 240, 220), anchor="mm")
    d.text((540, 195), "100", font=slides.font(44, 800), fill=(214, 240, 220), anchor="mm")
    bill.save(os.path.join(OUT, "cash_bill.png"))


def code_paper():
    """A printed page of code (texture for the paper avalanche)."""
    r = random.Random(5)
    img = Image.new("RGB", (420, 594), (250, 250, 247))
    d = ImageDraw.Draw(img)
    mono = ImageFont.truetype(MONO, 15)
    y = 24
    while y < 570:
        ind = r.randint(0, 3) * 18
        n = r.randint(8, 30)
        col = (40, 40, 40) if r.random() < 0.7 else (37, 99, 235)
        d.text((24 + ind, y), "".join(r.choice("abcdefghijklmnopqrstuvwxyz_().:=") for _ in range(n)), font=mono, fill=col)
        y += 21
    out = os.path.join(OUT, "code_paper.png")
    img.save(out)
    return out


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("wrote", code_paper())
    for name, text in STATIC.items():
        text_screen(text).save(os.path.join(OUT, name + ".png"))
        print("wrote", name)
    print("velocity", velocity(), "frames")
    print("checklist", checklist(), "frames")
    print("system", system(), "frames")
    for name, text in STATIC2.items():
        text_screen(text).save(os.path.join(OUT, name + ".png"))
    print("p2 statics", len(STATIC2))
    print("p2_system", system(name="p2_system", caps=("More code means **bigger systems**",
                                                       "**Higher complexity,** potentially **more bugs.**"),
                              glyph="spider"), "frames")
    print("p2_review_queue", review_queue(), "frames")
    print("p2_quads", quadrants())
    print("p2_leaving", leaving(), "frames")
    tower_labels()
    print("tower labels + cash")
    tmp = os.path.join(OUT, "slide_00.png")
    if os.path.exists(tmp):
        os.remove(tmp)
