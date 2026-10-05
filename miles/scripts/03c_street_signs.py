"""Slides as pieces of the city (street piece): graffiti mural, rooftop billboard, LED ticker, bus-stop
and subway lightboxes, Times Square screens. Same rules as the slides: one idea per sign, one font
size, emphasis only in **bold**, readable first — the street styling lives around the text.

    python3 scripts/03c_street_signs.py        # -> assets/street/*.png (+ sequences)
"""
import importlib, math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from pipeline import paths

slides = importlib.import_module("03_make_slides")
screens = importlib.import_module("03b_make_screens")
OUT = os.path.join(paths.ROOT, "assets", "street")
INK = (12, 12, 12)


def text_block(img, text, box, fg=INK, max_size=200, min_size=40, weight_regular=None, weight_bold=None,
               shadow=None):
    """Largest single size that fits `box` (x0, y0, x1, y1); bold spans in heavier weight."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    tokens = slides.words(text)
    for size in range(max_size, min_size - 1, -4):
        fonts = {False: slides.font(size, weight_regular or slides.REGULAR), True: slides.font(size, weight_bold or slides.BOLD)}
        lines, space = slides.wrap(tokens, fonts, x1 - x0)
        lh = int(size * 1.16)
        if len(lines) * lh <= y1 - y0 and all(fonts[b].getlength(w) <= x1 - x0 for w, b in tokens):
            break
    y = y0 + (y1 - y0 - len(lines) * lh) / 2 + lh * 0.8
    for line in lines:
        x = x0
        for w, b in line:
            if shadow:
                for dx, dy, col in shadow:
                    d.text((x + dx, y + dy), w, font=fonts[b], fill=col, anchor="ls")
            d.text((x, y), w, font=fonts[b], fill=fg, anchor="ls")
            x += fonts[b].getlength(w) + space
        y += lh
    return size


def graffiti(name, text, w=2400, h=1000, seed=3):
    """Spray-painted mural: a cream paint panel with ragged edges, colour bursts + drips, black lettering
    with a two-tone spray outline. Transparent outside the paint so the brick shows around it."""
    r = random.Random(seed)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    paint = Image.new("L", (w, h), 0)
    pd = ImageDraw.Draw(paint)
    pd.rounded_rectangle([60, 70, w - 60, h - 70], radius=90, fill=255)
    for _ in range(260):                                   # ragged sprayed edge
        x = r.choice([r.uniform(30, 120), r.uniform(w - 120, w - 30), r.uniform(60, w - 60)])
        y = r.uniform(40, h - 40) if x < 130 or x > w - 130 else r.choice([r.uniform(30, 110), r.uniform(h - 110, h - 30)])
        rad = r.uniform(18, 46)
        pd.ellipse([x - rad, y - rad, x + rad, y + rad], fill=255)
    paint = paint.filter(ImageFilter.GaussianBlur(3))
    base = Image.new("RGBA", (w, h), (247, 240, 222, 255))
    img.paste(base, (0, 0), paint)
    d = ImageDraw.Draw(img)
    for col, cx, cy in (((255, 64, 129, 255), 0.08, 0.15), ((0, 200, 255, 255), 0.93, 0.82), ((255, 196, 0, 255), 0.9, 0.12)):
        for _ in range(140):                              # spray bursts in the corners
            a, rr = r.uniform(0, 2 * math.pi), abs(r.gauss(0, 70))
            x, y = cx * w + math.cos(a) * rr, cy * h + math.sin(a) * rr
            s = r.uniform(2, 7)
            d.ellipse([x - s, y - s, x + s, y + s], fill=col)
    for _ in range(9):                                    # paint drips off the bottom edge
        x = r.uniform(150, w - 150)
        L = r.uniform(40, 140)
        d.rounded_rectangle([x - 5, h - 110, x + 5, h - 110 + L], radius=5, fill=(247, 240, 222, 255))
    text_block(img, text, (170, 170, w - 170, h - 170), max_size=230,
               shadow=[(10, 10, (255, 64, 129)), (-6, -6, (0, 190, 255))])
    img.save(os.path.join(OUT, name + ".png"))


def board(name, text, w=2400, h=800, bg=(255, 255, 255), fg=INK):
    """Billboard / poster face: plain and readable."""
    img = Image.new("RGB", (w, h), bg)
    text_block(img, text, (110, 70, w - 110, h - 70), fg=fg, max_size=240)
    img.save(os.path.join(OUT, name + ".png"))


def ticker(name, text, w=3600, h=420):
    """LED ticker band: dark panel, warm white LED lettering with a dot-matrix screen and arrows."""
    img = Image.new("RGB", (w, h), (8, 8, 10))
    d = ImageDraw.Draw(img)
    for x in range(0, w, 12):                            # LED pixel grid
        d.line([(x, 0), (x, h)], fill=(18, 18, 22))
    for y in range(0, h, 12):
        d.line([(0, y), (w, y)], fill=(18, 18, 22))
    for k, x in enumerate((60, w - 160)):
        d.polygon([(x, h / 2 - 50), (x + 90, h / 2), (x, h / 2 + 50)], fill=(255, 176, 32))
    text_block(img, text, (230, 40, w - 230, h - 40), fg=(255, 236, 200), max_size=260)
    img.save(os.path.join(OUT, name + ".png"))


def facade(name, w=2400, h=340, bays=12, seed=1):
    """One storey of a city facade (for the finale building): stone band, window bays, sills."""
    r = random.Random(seed)
    img = Image.new("RGB", (w, h), (196, 186, 170))
    d = ImageDraw.Draw(img)
    for y in range(0, h, 6):                                     # faint stone coursing
        d.line([(0, y), (w, y)], fill=(188, 178, 162))
    bw = w / bays
    for k in range(bays):
        x0 = k * bw + bw * 0.18
        x1 = (k + 1) * bw - bw * 0.18
        lit = r.random() < 0.35
        d.rectangle([x0, h * 0.18, x1, h * 0.78], fill=(255, 214, 150) if lit else (54, 72, 92))
        d.line([((x0 + x1) / 2, h * 0.18), ((x0 + x1) / 2, h * 0.78)], fill=(70, 70, 72), width=6)
        d.line([(x0, h * 0.48), (x1, h * 0.48)], fill=(70, 70, 72), width=6)
        d.rectangle([x0 - 8, h * 0.78, x1 + 8, h * 0.84], fill=(222, 214, 200))      # sill
    d.rectangle([0, h - 18, w, h], fill=(150, 142, 130))                              # floor band
    img.save(os.path.join(OUT, name + ".png"))


def big_caption(d, text, y, size, x=70, w=1280 - 140):
    """Single-size caption with **bold**, shrunk to fit."""
    width = lambda sz: sum(slides.font(sz, slides.BOLD if b else slides.REGULAR).getlength(t + " ") for t, b in slides.words(text))
    while size > 40 and width(size) > w:
        size -= 2
    for t, b in slides.words(text):
        f = slides.font(size, slides.BOLD if b else slides.REGULAR)
        ImageDraw.Draw(d).text((x, y), t, font=f, fill=INK, anchor="ls") if isinstance(d, Image.Image) else d.text((x, y), t, font=f, fill=INK, anchor="ls")
        x += f.getlength(t) + f.getlength(" ")


def queue_big(name="st_queue", n=180, cap="Human review **can't keep up.**"):
    """Small-player version: huge caption + two huge counters + one bar. Nothing else."""
    d_out = os.path.join(OUT, name)
    os.makedirs(d_out, exist_ok=True)
    W, H = 1280, 720
    RED, GREEN = (220, 38, 38), (22, 163, 74)
    num = slides.font(190, slides.BOLD)
    lab = slides.font(58, slides.REGULAR)
    for i in range(n):
        t = i / (n - 1)
        img = Image.new("RGB", (W, H), (255, 255, 255))
        d = ImageDraw.Draw(img)
        big_caption(d, cap, 120, 86)
        incoming = int(12 + 470 * t ** 1.8)
        reviewed = int(3 + 9 * t)
        for x0, label, val, col in ((70, "Incoming PRs", incoming, RED), (720, "Reviewed", reviewed, INK)):
            d.text((x0, 250), label, font=lab, fill=(90, 90, 90), anchor="ls")
            d.text((x0, 450), f"{val}", font=num, fill=col, anchor="ls")
        cov = reviewed / max(1, incoming)
        d.rounded_rectangle([70, 560, 1210, 640], radius=30, fill=(214, 220, 228))
        d.rounded_rectangle([70, 560, 70 + max(60, int(1140 * min(1.0, cov))), 640], radius=30, fill=GREEN if cov > 0.15 else RED)
        img.save(os.path.join(d_out, f"f_{i + 1:04d}.png"))
    return n


TILES = [("Downtime", "_icon_server"), ("Security", "_icon_lock"), ("Slow apps", "_icon_perf"), ("Bad UI", "_icon_badui")]


def quads_big(prefix="st_quad"):
    """Small-player version of the four risks: big caption, big one/two-word tiles."""
    W, H = 1280, 720
    lab = slides.font(70, slides.BOLD)
    for k in range(len(TILES) + 1):
        img = Image.new("RGB", (W, H), (255, 255, 255))
        d = ImageDraw.Draw(img)
        big_caption(d, "Customers **walk away** over:", 110, 84)
        for q, (name, icon) in enumerate(TILES[:k]):
            col, row = q % 2, q // 2
            x0, y0 = 60 + col * 590, 160 + row * 270
            d.rounded_rectangle([x0, y0, x0 + 570, y0 + 250], radius=26, fill=(254, 226, 226), outline=(220, 38, 38), width=6)
            getattr(screens, icon)(d, x0 + 92, y0 + 125, 90)
            d.text((x0 + 185, y0 + 128), name, font=lab, fill=INK, anchor="lm")
        img.save(os.path.join(OUT, f"{prefix}_{k}.png"))
    return len(TILES) + 1


def leaving_big(name="st_leaving", prefix="st_quad", n=96):
    """The customers walk off the faded risks."""
    import math as m
    d_out = os.path.join(OUT, name)
    os.makedirs(d_out, exist_ok=True)
    W, H = 1280, 720
    base = Image.open(os.path.join(OUT, f"{prefix}_4.png")).convert("RGB")
    for i in range(n):
        img = base.copy()
        ov = Image.new("RGBA", (W, H), (255, 255, 255, int(215 * min(1, i / 16))))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, W, 140], fill=(255, 255, 255))
        big_caption(d, "...and customers **walk away.**", 110, 84)
        for k in range(7):
            px = 80 + k * 170 + max(0, i - 14) * 22
            if px > W + 80:
                continue
            y = 560 + (k % 2) * 70
            bob = 8 * m.sin((i + k * 3) * 0.6)
            d.ellipse([px - 32, y - 175 + bob, px + 32, y - 111 + bob], fill=(71, 85, 105))
            d.rounded_rectangle([px - 44, y - 102 + bob, px + 44, y + 15 + bob], radius=20, fill=(71, 85, 105))
        img.save(os.path.join(d_out, f"f_{i + 1:04d}.png"))
    return n


def car_label(name, text, bg, w=3000, h=520):
    """Train car side/roof panel: one bold line, white on colour, as big as fits."""
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    d.rectangle([12, 12, w - 12, h - 12], outline=(255, 255, 255), width=10)
    size = 300
    while slides.font(size, 850).getlength(text) > w - 160:
        size -= 6
    d.text((w / 2, h / 2 + 6), text, font=slides.font(size, 850), fill=(255, 255, 255), anchor="mm")
    img.save(os.path.join(OUT, name + ".png"))


def web_net(name="web_net", w=2400, h=900):
    """A Spider-Man web spanning the street, with INSPECTION woven into its middle (RGBA)."""
    import math as m
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = w / 2, h / 2
    ink = (250, 252, 255, 255)
    for k in range(18):                                          # radial strands
        a = 2 * m.pi * k / 18
        d.line([(cx, cy), (cx + m.cos(a) * w, cy + m.sin(a) * w * 0.6)], fill=ink, width=7)
    for r in range(1, 9):                                        # concentric rings (sagging between strands)
        pts = []
        for k in range(19):
            a = 2 * m.pi * k / 18
            rr = r * 150 * (0.96 if k % 2 else 1.0)
            pts.append((cx + m.cos(a) * rr * 1.7, cy + m.sin(a) * rr))
        d.line(pts, fill=ink, width=6)
    bw, bh = 1500, 300                                           # woven label
    d.rounded_rectangle([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2], radius=40, fill=(37, 99, 235, 255),
                        outline=ink, width=14)
    size = 230
    while slides.font(size, 850).getlength("INSPECTION") > bw - 140:
        size -= 6
    d.text((cx, cy + 8), "INSPECTION", font=slides.font(size, 850), fill=(255, 255, 255, 255), anchor="mm")
    img.save(os.path.join(OUT, name + ".png"))


def main():
    os.makedirs(OUT, exist_ok=True)
    board("wallboard_generated", "You already ship a lot of **AI-generated code.**", w=1920, h=1080)
    facade("facade_floor")
    graffiti("wall_generated", "You already ship a lot of **AI-generated code.**")
    board("billboard_inspection", "But do you do enough **code inspection?**")
    ticker("ticker_faster", "Code now ships **faster than ever.**")
    board("roof_competitive", "How do you stay **competitive?**", w=1920, h=1080)
    board("roof_layer", "You need a better **inspection layer.**", w=1920, h=1080)
    # lightbox / screen sequences (16:9), re-captioned to the street script
    screens.OUT = OUT
    print("bugs", screens.system(name="st_bugs", caps=("More code means **bigger systems**", "**Bigger systems,** more **bugs.**"),
                                 glyph="spider", cap_size=84, cap_y=115, n_nodes=24, node_r=18, edge_w=7, glyph_s=2.0,
                                 n_bugs=12, top=210), "frames")
    print("queue", queue_big(), "frames")
    print("risks", quads_big(), leaving_big(), "frames")
    car_label("car_engineers", "ENGINEERS' CONFIDENCE", (30, 41, 59))
    car_label("car_customers", "CUSTOMER CONFIDENCE", (30, 41, 59))
    car_label("car_product", "COMPETITIVE PRODUCT  $$$", (21, 128, 61))
    web_net()
    print("ok ->", OUT)


if __name__ == "__main__":
    main()
