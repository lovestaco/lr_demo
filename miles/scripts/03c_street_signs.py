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
                                 glyph="spider"), "frames")
    print("queue", screens.review_queue(name="st_queue", cap="Human review **can't keep up.**"), "frames")
    screens.QUADS[:] = [("Downtime", screens._icon_server), ("Security holes", screens._icon_lock),
                        ("Slow apps", screens._icon_perf), ("Bad UI", screens._icon_badui)]
    print("risks", screens.quadrants(prefix="st_quad"), screens.leaving(prefix="st_quad", name="st_leaving"))
    print("ok ->", OUT)


if __name__ == "__main__":
    main()
