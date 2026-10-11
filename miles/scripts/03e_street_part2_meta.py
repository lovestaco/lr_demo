"""Street part 2b, the Meta section: the screens that hang in the 3D city (textures, drawn with PIL).

    python3 scripts/03e_street_part2_meta.py            # needs build/meta/timing.json (written by 04_street_part2_b.py)

04_street_part2_b.py calls this by itself when the timing changed, so a normal build needs nothing by hand.

Writes into build/meta/ (gitignored, regenerated):
    sign/f_NNNN.png     the Meta billboard at the end of the avenue, one sequence: the logo first, then (as "risk-first" is said)
                        the change cards sorting by risk. Frame 1 = scene frame timing["sign"][0]
    stat1|2|3/f_NNNN.png  the three results, popping in with a count-up (frame 1 = the frame the number is spoken)
    demo/f_NNNN.jpg     LiveReview's risk-score footage for the billboard (frame 1 = timing["demo"][0])
    stamp.json          the timing these were drawn for

The Meta logo: drop the official file at assets/street2/meta_logo_official.png (transparent PNG, any size). Until
it exists a plain "Meta" wordmark is drawn so the layout can be judged.
"""
import json, os, sys, shutil
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import importlib
from pipeline import paths
B = importlib.import_module("05b_street_part2_boards")          # the board kit: fonts, rows layer, easing, media frames
slides, smooth, W, H = B.slides, B.smooth, B.W, B.H

OUT = os.path.join(paths.ROOT, "build", "meta")
LOGO = os.path.join(paths.ROOT, "assets", "street2", "meta_logo_official.png")
GREEN, RED, AMBER = B.GREEN, B.RED, B.AMBER
NAVY, INK = (9, 13, 24), (226, 232, 240)
META_BLUE = (0, 129, 251)
STAT_N = 44                                                      # frames of each stat animation (the last one holds)


def font(size, bold=True):
    return slides.font(size, slides.BOLD if bold else slides.REGULAR)


def panel(top=(14, 20, 36), bottom=(6, 9, 18)):
    img = Image.new("RGB", (W, H), bottom)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img


def logo_layer(width):
    """The Meta logo as an RGBA image `width` px wide: the official file if present, else a plain wordmark."""
    if os.path.exists(LOGO):
        im = Image.open(LOGO).convert("RGBA")
        h = int(im.height * width / im.width)
        return im.resize((width, h), Image.LANCZOS)
    im = Image.new("RGBA", (width, int(width * 0.36)), (0, 0, 0, 0))                      # placeholder wordmark
    ImageDraw.Draw(im).text((width / 2, im.height / 2), "Meta", font=font(int(width * 0.34)), fill=META_BLUE + (255,), anchor="mm")
    return im


def sign_png():
    """The logo panel (also saved as sign.png)."""
    img = panel((16, 24, 44), (5, 8, 16)).convert("RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lg = logo_layer(760)
    pos = ((W - lg.width) // 2, (H - lg.height) // 2 - 36)
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gl.paste(lg, pos, lg)
    gl = gl.filter(ImageFilter.GaussianBlur(26))
    img.alpha_composite(gl)                                         # soft halo behind the logo
    img.alpha_composite(gl)
    img.paste(lg, pos, lg)
    d = ImageDraw.Draw(img)
    d.text((W / 2, pos[1] + lg.height + 70), "risk-first code review", font=font(46, False), fill=INK + (235,), anchor="mm")
    d.rectangle([0, 0, W - 1, H - 1], outline=META_BLUE + (255,), width=6)
    img = img.convert("RGB")
    img.save(os.path.join(OUT, "sign.png"))
    return img


def rows_img(f, w, r_in, r0):
    out = panel().convert("RGBA")
    B.headline(out, f, [(r0, "Changes **waiting for review**"), (w["risk"] - 3, "**Risk-first** review"),
                        (w["low"] - 2, "Low-risk changes **skip the line**"),
                        (w["attention"] - 3, "**ATTENTION** goes where **RISK** is")], y=62, size=50)
    out.alpha_composite(B.meta_rows_layer(f, dict(w, meta=r_in)))
    lg = logo_layer(170)                                            # the brand stays on the board
    out.alpha_composite(lg, (W - lg.width - 36, 30))
    ImageDraw.Draw(out).rectangle([0, 0, W - 1, H - 1], outline=META_BLUE + (255,), width=6)
    return out.convert("RGB")


def sign_frames(t):
    """The billboard at the end of the avenue: the Meta logo, then the change cards. The cards come in 14 frames before
    "risk" (crossfade over 10 frames), sort on it, the low-risk ones leave on "skip", the survivors get an amber ring on
    "attention"; the header line follows the voice-over."""
    w = dict(t["words"])
    s0, s1 = t["sign"]
    r_in = w["risk"] - 14
    logo = sign_png()
    d_ = os.path.join(OUT, "sign")
    shutil.rmtree(d_, ignore_errors=True)
    os.makedirs(d_)
    for i, f in enumerate(range(s0, s1 + 1)):
        if f < r_in:
            im = logo
        else:
            k = smooth((f - r_in) / 10.0)
            im = rows_img(f, w, r_in, r_in)
            if k < 1.0:
                im = Image.blend(logo, im, k)
        im.save(os.path.join(d_, f"f_{i + 1:04d}.png"))
    return s1 - s0 + 1


def stat_frames(n, big, label, kind):
    """One result: pops in (scale + fade), the number counts up, and a small picture of what it means."""
    d_ = os.path.join(OUT, f"stat{n}")
    shutil.rmtree(d_, ignore_errors=True)
    os.makedirs(d_)
    for i in range(STAT_N):
        k = smooth(i / 10.0)
        out = panel().convert("RGBA")
        d = ImageDraw.Draw(out)
        d.rectangle([0, 0, W - 1, H - 1], outline=GREEN + (255,), width=8)
        d.text((W / 2, 70), "Meta's results", font=font(40, False), fill=(148, 163, 184, 255), anchor="mm")
        size = int(250 * (0.75 + 0.25 * k) * (1 + 0.06 * max(0.0, 1 - abs(k * 2 - 1.3))))
        text = big
        if kind == "pct":                                          # 33% counts up
            text = f"{int(round(33 * smooth(i / 26.0)))}%"
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((W / 2, 300), text, font=font(size), fill=GREEN + (int(255 * k),), anchor="mm")
        out.alpha_composite(layer)
        d = ImageDraw.Draw(out)
        d.text((W / 2, 470), label, font=font(66, False), fill=INK + (int(255 * k),), anchor="mm")
        # what it means, in shapes
        if kind == "dots":                                         # 1 in 50: fifty squares, one red
            for j in range(50):
                a = smooth((i - 6 - j * 0.35) / 6.0)
                x, y = 250 + (j % 25) * 31, 560 + (j // 25) * 48
                col = RED if j == 37 else (34, 90, 62)
                d.rounded_rectangle([x, y, x + 24, y + 38], radius=6, fill=col + (int(255 * a),))
        elif kind == "thirds":                                     # 1 in 3: three deploys, one rolled back
            for j in range(3):
                a = smooth((i - 8 - j * 3) / 6.0)
                x = 430 + j * 150
                col = RED if j == 1 else (34, 90, 62)
                d.rounded_rectangle([x, 560, x + 110, 650], radius=14, fill=col + (int(255 * a),))
                if j == 1:
                    for sx in (-1, 1):                                    # a white cross: rolled back
                        d.line([(x + 55 - 22, 605 - 22 * sx), (x + 55 + 22, 605 + 22 * sx)], fill=(255, 255, 255, int(255 * a)), width=9)
        else:                                                      # 33% lower wait: the bar is a third shorter
            a = smooth((i - 8) / 6.0)
            cut = smooth((i - 14) / 14.0)
            d.rounded_rectangle([250, 570, 1030, 610], radius=12, fill=(51, 65, 85, int(255 * a)))
            d.rounded_rectangle([250, 570, 250 + int(780 * (1 - 0.33 * cut)), 610], radius=12, fill=GREEN + (int(255 * a),))
            d.text((250, 645), "wait before", font=font(30, False), fill=(148, 163, 184, int(255 * a)), anchor="lm")
            d.text((1030, 645), "after", font=font(30, False), fill=(148, 163, 184, int(255 * a)), anchor="rm")
        out.convert("RGB").save(os.path.join(d_, f"f_{i + 1:04d}.png"))


def demo_frames(t):
    d_ = os.path.join(OUT, "demo")
    shutil.rmtree(d_, ignore_errors=True)
    os.makedirs(d_)
    a, b = t["demo"]
    n = b - a + 1
    fr = B.media_frames("risk-score_risk-score-demo-compressed.mp4", n, (23.0, 23.0 + n / 30.0 + 0.4), contain=True)
    for i in range(n):
        Image.open(fr[i % len(fr)]).convert("RGB").save(os.path.join(d_, f"f_{i + 1:04d}.jpg"), quality=90)
    return n


if __name__ == "__main__":
    t = json.load(open(os.path.join(OUT, "timing.json")))
    os.makedirs(OUT, exist_ok=True)
    nr = sign_frames(t)
    stat_frames(1, "1/50", "production incidents", "dots")
    stat_frames(2, "1/3", "deploy reverts", "thirds")
    stat_frames(3, "33%", "lower wait time", "pct")
    nd = demo_frames(t)
    json.dump(dict(t, sign_n=nr, stat_n=STAT_N, demo_n=nd, logo=os.path.exists(LOGO)), open(os.path.join(OUT, "stamp.json"), "w"))
    print(f"META assets: {nr} sign frames, 3 x {STAT_N} stat frames, {nd} demo frames; official logo: {os.path.exists(LOGO)}")
