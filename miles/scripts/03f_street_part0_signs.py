"""Street part 0 (the Meta opening): the textures that hang in the 3D city (drawn with PIL). All boards are white,
black text, one size per kind of text, emphasis only in **bold** (the slide rules).

    python3 scripts/03f_street_part0_signs.py      # -> assets/street0/

    board_mr/f_NNNN.png        the volume board: Incoming MRs 12 -> 482 against Reviewed 3 -> 12, a coverage bar, two chips that
                               pop in on "twice as big" / "every dev" (the numbers climb from frame 1 to "risky")
    mr_0..5.png, mr_red.png    the change cards that pile up on the reviewers (the red one is the risky one)
    risk_g0..3.png, risk_r0..1.png   cards with a risk score (green = low, red = high) for the machine
    stamp_ok.png               the "AUTO-APPROVED" stamp (alpha)
    meta_a.png / meta_b.png    the Meta billboard: the official logo, then the logo + "risk score on every MR"
    stat1|2|3/f_NNNN.png       the three results (98 % / 30 % / 33 %), a count-up and a picture of what it means

Timing comes from the voice-over's word times (assets/audio/vo_street/lines.json, line 14; frame = 1 + seconds * 30, same as
04_street_part0.py), so a re-recorded take re-times the board. The Meta logo is the one 03e_street_part3_meta.py uses.
"""
import json, importlib, math, os, shutil, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from pipeline import paths
slides = importlib.import_module("03_make_slides")

OUT = os.path.join(paths.ROOT, "assets", "street0")
LOGO = os.path.join(paths.ROOT, "assets", "street2", "meta_logo_official.png")
VO = json.load(open(os.path.join(paths.ROOT, "assets", "audio", "vo_street", "lines.json")))["14"]
W, H = 1280, 720
WHITE, INK, MUTED = (255, 255, 255), (15, 23, 42), (100, 116, 139)
RED, GREEN, GREEN_D, AMBER = (220, 38, 38), (22, 163, 74), (22, 163, 74), (245, 158, 11)
META_BLUE = (0, 129, 251)
STAT_N = 44


def wordf(w, nth=0):
    hits = [t for x, t in VO["words"] if x == w]
    return 1 + int(round(hits[min(nth, len(hits) - 1)] * 30))


smooth = lambda x: (lambda k: k * k * (3 - 2 * k))(max(0.0, min(1.0, x)))
font = lambda size, bold=True: slides.font(size, slides.BOLD if bold else slides.REGULAR)


def rich(d, xy, text, size, fill=INK, anchor="ls", alpha=255):
    """One line with **bold** spans at a single size, left-aligned at xy (baseline)."""
    x, y = xy
    toks = slides.words(text)
    for w, b in toks:
        f = font(size, b)
        d.text((x, y), w, font=f, fill=fill + (alpha,), anchor=anchor)
        x += f.getlength(w) + f.getlength(" ")
    return x


def rich_width(text, size):
    return sum(font(size, b).getlength(w + " ") for w, b in slides.words(text)) - font(size, False).getlength(" ")


# ------------------------------------------------------------------ the volume board (an image sequence)
CHIPS = [("each MR is **2x bigger** than last year", wordf("every", 0), 600), ("every dev ships **1.5x more** MRs", wordf("every", 1), 730)]
N_BOARD = 460
F_END = wordf("risky")                                 # the counters stop climbing as "risky" is said


def board_frames():
    d_out = os.path.join(OUT, "board_mr")
    shutil.rmtree(d_out, ignore_errors=True)
    os.makedirs(d_out)
    num, lab = font(190), font(58, False)
    for i in range(N_BOARD):
        f = i + 1
        t = min(1.0, (f - 1) / (F_END - 1))
        img = Image.new("RGBA", (W, H), WHITE + (255,))
        d = ImageDraw.Draw(img)
        incoming, reviewed = int(12 + 470 * t ** 1.8), int(3 + 9 * t)
        for x0, label, val, col in ((70, "Incoming MRs", incoming, RED), (720, "Reviewed", reviewed, INK)):
            d.text((x0, 125), label, font=lab, fill=(90, 90, 90, 255), anchor="ls")
            d.text((x0, 305), f"{val}", font=num, fill=col + (255,), anchor="ls")
        cov = reviewed / max(1, incoming)
        d.rounded_rectangle([70, 345, 1210, 405], radius=26, fill=(214, 220, 228, 255))
        d.rounded_rectangle([70, 345, 70 + max(56, int(1140 * min(1.0, cov))), 405], radius=26, fill=(GREEN if cov > 0.15 else RED) + (255,))
        for text, f0, y in CHIPS:                      # chips pop in (fade + a short slide up)
            k = smooth((f - f0) / 8.0)
            if k <= 0:
                continue
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            dl = ImageDraw.Draw(lay)
            yy = y - 150 + int(24 * (1 - k))
            dl.rounded_rectangle([70, yy, 1210, yy + 100], radius=30, fill=(254, 242, 242, int(255 * k)), outline=RED + (int(255 * k),), width=5)
            rich(dl, (110, yy + 71), text, 56, alpha=int(255 * k))
            img.alpha_composite(lay)
        ImageDraw.Draw(img).rectangle([0, 0, W - 1, H - 1], outline=INK + (255,), width=6)
        img.convert("RGB").save(os.path.join(d_out, f"f_{f:04d}.png"))
    return N_BOARD


# ------------------------------------------------------------------ cards
def card(name, title, sub, accent, score=None, w=512, h=360, high=False):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([4, 4, w - 5, h - 5], radius=34, fill=(255, 255, 255, 255), outline=accent + (255,), width=14 if high else 8)
    d.rounded_rectangle([4, 4, w - 5, 92], radius=34, fill=accent + (255,))
    d.rectangle([4, 60, w - 5, 92], fill=accent + (255,))
    d.text((34, 66), title, font=font(54), fill=(255, 255, 255, 255), anchor="ls")
    if score is not None:                                      # one big risk score
        d.text((w / 2, 232), score, font=font(124), fill=accent + (255,), anchor="mm")
        d.text((w / 2, 322), sub, font=font(40, False), fill=MUTED + (255,), anchor="mm")
    else:
        for j, ln in enumerate((0.8, 0.62, 0.7)):
            d.rounded_rectangle([34, 130 + j * 44, 34 + int((w - 68) * ln), 154 + j * 44], radius=10, fill=(214, 220, 228, 255))
        d.text((34, 322), sub, font=font(46), fill=accent + (255,), anchor="ls")
    img.save(os.path.join(OUT, name + ".png"))


def cards():
    GREY = (71, 85, 105)
    for i, (n, sub) in enumerate((("4821", "+842  -317"), ("4822", "+1.2k  -96"), ("4823", "+310  -45"), ("4824", "+2.4k  -780"),
                                  ("4825", "+590  -203"), ("4826", "+1.7k  -411"))):
        card(f"mr_{i}", f"MR #{n}", sub, GREY)
    card("mr_red", "MR #4903", "auth + payments", RED, high=True)
    for i, s in enumerate((9, 14, 23, 6)):
        card(f"risk_g{i}", f"MR #{4930 + i}", "low risk", GREEN_D, score=f"RISK {s}")
    for i, s in enumerate((91, 87)):
        card(f"risk_r{i}", f"MR #{4940 + i}", "HIGH RISK", RED, score=f"RISK {s}", high=True)
    st = Image.new("RGBA", (560, 190), (0, 0, 0, 0))
    d = ImageDraw.Draw(st)
    d.rounded_rectangle([8, 8, 552, 182], radius=28, outline=GREEN_D + (235,), width=12, fill=(240, 253, 244, 215))
    d.text((280, 95), "AUTO-APPROVED", font=font(60), fill=GREEN_D + (255,), anchor="mm")
    st.save(os.path.join(OUT, "stamp_ok.png"))


# ------------------------------------------------------------------ the Meta billboard (white, the official logo)
def logo(width):
    im = Image.open(LOGO).convert("RGBA")
    return im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)


def meta_boards():
    for name, text in (("meta_a", None), ("meta_b", "a **risk score** on every MR")):
        img = Image.new("RGBA", (W, H), WHITE + (255,))
        lg = logo(1020)
        img.alpha_composite(lg, ((W - lg.width) // 2, (H - lg.height) // 2 - (70 if text else 0)))
        d = ImageDraw.Draw(img)
        if text:
            x = (W - rich_width(text, 66)) / 2
            rich(d, (x, 600), text, 66)
        d.rectangle([0, 0, W - 1, H - 1], outline=META_BLUE + (255,), width=10)
        img.convert("RGB").save(os.path.join(OUT, name + ".png"))


# ------------------------------------------------------------------ the three results (white boards, count-up)
def stat_frames(n, value, label, kind):
    d_ = os.path.join(OUT, f"stat{n}")
    shutil.rmtree(d_, ignore_errors=True)
    os.makedirs(d_)
    for i in range(STAT_N):
        k = smooth(i / 10.0)
        out = Image.new("RGBA", (W, H), WHITE + (255,))
        d = ImageDraw.Draw(out)
        d.rectangle([0, 0, W - 1, H - 1], outline=GREEN_D + (255,), width=8)
        d.text((W / 2, 70), "At Meta", font=font(40, False), fill=MUTED + (255,), anchor="mm")
        size = int(250 * (0.75 + 0.25 * k) * (1 + 0.06 * max(0.0, 1 - abs(k * 2 - 1.3))))
        text = f"{int(round(value * smooth(i / 26.0)))}%"
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((W / 2, 300), text, font=font(size), fill=GREEN_D + (int(255 * k),), anchor="mm")
        out.alpha_composite(layer)
        d = ImageDraw.Draw(out)
        d.text((W / 2, 470), label, font=font(66, False), fill=INK + (int(255 * k),), anchor="mm")
        if kind == "dots":                                     # 98 % fewer incidents: of fifty, one is left
            for j in range(50):
                a = smooth((i - 6 - j * 0.35) / 6.0)
                x, y = 250 + (j % 25) * 31, 560 + (j // 25) * 48
                d.rounded_rectangle([x, y, x + 24, y + 38], radius=6, fill=(RED if j == 37 else GREEN_D) + (int(255 * a),))
        elif kind == "tenths":                                 # 30 % fewer rollbacks: of ten deploys, three never roll back
            for j in range(10):
                a = smooth((i - 8 - j * 2) / 6.0)
                x = 160 + j * 100
                if j < 3:
                    d.rounded_rectangle([x, 570, x + 76, 650], radius=12, outline=GREEN_D + (int(255 * a),), width=6)
                else:
                    d.rounded_rectangle([x, 570, x + 76, 650], radius=12, fill=(214, 220, 228, int(255 * a)))
        else:                                                  # 33 % lower wait: the bar is a third shorter
            a = smooth((i - 8) / 6.0)
            cut = smooth((i - 14) / 14.0)
            d.rounded_rectangle([250, 570, 1030, 610], radius=12, fill=(226, 232, 240, int(255 * a)))
            d.rounded_rectangle([250, 570, 250 + int(780 * (1 - 0.33 * cut)), 610], radius=12, fill=GREEN_D + (int(255 * a),))
            d.text((250, 645), "wait before", font=font(30, False), fill=MUTED + (int(255 * a),), anchor="lm")
            d.text((1030, 645), "after", font=font(30, False), fill=MUTED + (int(255 * a),), anchor="rm")
        out.convert("RGB").save(os.path.join(d_, f"f_{i + 1:04d}.png"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    n = board_frames()
    cards()
    meta_boards()
    stat_frames(1, 98, "fewer production incidents", "dots")
    stat_frames(2, 30, "fewer rollbacks", "tenths")
    stat_frames(3, 33, "lower wait time", "pct")
    print(f"part 0 signs -> {OUT}: board {n} frames (counters stop at f {F_END}), chips at", [c[1] for c in CHIPS], ", cards, Meta boards, 3 x", STAT_N, "stat frames")
