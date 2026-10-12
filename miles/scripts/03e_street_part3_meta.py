"""Street part 3, the Meta callback: the screens that hang in the 3D city (textures, drawn with PIL). All boards are white.

    python3 scripts/03e_street_part3_meta.py            # needs build/meta/timing.json (written by 04_street_part3.py)

04_street_part3.py calls this by itself when the timing changed, so a normal build needs nothing by hand.

Writes into build/meta/ (gitignored, regenerated), everything 1920x1080:
    sign/f_NNNN.jpg     the Meta billboard at the end of the avenue, ONE sequence: the big Meta logo on a white board (nothing
                        else), then (at the start of the bridge line) LiveReview's risk-score footage, cropped to the board's
                        16:9 so it fills the whole face (no white bars, no border). Frame 1 = scene frame timing["sign"][0]
    stat/f_NNNN.png     the ONE results board on the west tower: three rows (98% / 30% / 33%) popping in quick succession
                        (frame 1 = the frame the first row is spoken; the rows start timing["stats"] frames apart)
    stamp.json          the timing these were drawn for

The Meta logo: assets/street2/meta_logo_official.png (the full logo, symbol + wordmark, transparent PNG made from
videos/livereview-launch/assets/Meta-Logo.png). Until it exists a plain "Meta" wordmark is drawn so the layout can be judged.
"""
import json, os, sys, shutil, subprocess
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import importlib
from pipeline import paths
B = importlib.import_module("05b_street_part3_boards")          # the board kit: fonts, easing, colours, the demo-clip folder
slides, smooth = B.slides, B.smooth
W, H = 1920, 1080                                                # the textures are drawn at 1080p (the boards fill most of the frame)

OUT = os.path.join(paths.ROOT, "build", "meta")
LOGO = os.path.join(paths.ROOT, "assets", "street2", "meta_logo_official.png")
RED = B.RED
GREEN_D = (22, 163, 74)                                          # the green that reads on white
WHITE, INK, MUTED = (255, 255, 255), (15, 23, 42), (100, 116, 139)
META_BLUE = (0, 129, 251)
FOOTAGE = "risk-score_risk-score-demo-compressed.mp4"           # 1600x758
FOOT_FROM = 23.0                                                 # the part of it that is shown (seconds)
FOOT_CROP = "1348:758:16:0"                                      # 16:9 out of the 2.1:1 clip: file list (left) + the risk ring (right) stay
FADE = 6                                                         # frames the footage takes to replace the logo
STAT_N = 48                                                      # frames of the results animation (the last one holds)
ROWS = [("98%", "fewer production incidents"), ("30%", "fewer rollbacks"), ("33%", "lower wait time")]


def font(size, bold=True):
    return slides.font(size, slides.BOLD if bold else slides.REGULAR)


def white_panel():
    return Image.new("RGBA", (W, H), WHITE + (255,))


def border(img, col, width):
    ImageDraw.Draw(img).rectangle([0, 0, W - 1, H - 1], outline=col + (255,), width=width)
    return img


def logo_layer(width):
    """The Meta logo as an RGBA image `width` px wide."""
    if os.path.exists(LOGO):
        im = Image.open(LOGO).convert("RGBA")
        return im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    im = Image.new("RGBA", (width, int(width * 0.36)), (0, 0, 0, 0))                                      # placeholder
    ImageDraw.Draw(im).text((width / 2, im.height / 2), "Meta", font=font(int(width * 0.34)), fill=META_BLUE + (255,), anchor="mm")
    return im


def sign_png():
    """The logo board (also saved as sign.png): white, the logo big and centred, nothing else, the blue border."""
    img = white_panel()
    lg = logo_layer(1530)
    img.alpha_composite(lg, ((W - lg.width) // 2, (H - lg.height) // 2))
    border(img, META_BLUE, 9)
    img = img.convert("RGB")
    img.save(os.path.join(OUT, "sign.png"))
    return img


def sign_frames(t):
    """The billboard at the end of the avenue: the Meta logo, then LiveReview's footage from t["demo"][0] (crossfade over FADE
    frames). The footage is cut to the board's 16:9 and fills the whole face; frames are JPEG (a PNG sequence of this length
    would be huge), 4:4:4 so the small UI text stays crisp."""
    s0, s1 = t["sign"]
    d0, _ = t["demo"]
    logo = sign_png()
    d_ = os.path.join(OUT, "sign")
    shutil.rmtree(d_, ignore_errors=True)
    os.makedirs(d_)
    foot_dir = os.path.join(OUT, "_footage")
    shutil.rmtree(foot_dir, ignore_errors=True)
    os.makedirs(foot_dir)
    n_foot = s1 - d0 + 1
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{FOOT_FROM:.3f}", "-i", os.path.join(B.DEMO, FOOTAGE), "-t", f"{n_foot / 30.0 + 0.2:.3f}",
                    "-vf", f"fps=30,crop={FOOT_CROP},scale={W}:{H}:flags=lanczos", "-pix_fmt", "yuvj444p", "-q:v", "2", os.path.join(foot_dir, "c_%04d.jpg")], check=True)
    foot = sorted(os.listdir(foot_dir))
    assert len(foot) >= n_foot, (len(foot), n_foot)
    logo.save(os.path.join(foot_dir, "logo.jpg"), quality=95, subsampling=0)
    for i, f in enumerate(range(s0, s1 + 1)):
        dst = os.path.join(d_, f"f_{i + 1:04d}.jpg")
        if f < d0:
            os.link(os.path.join(foot_dir, "logo.jpg"), dst)
        elif f - d0 < FADE:
            im = Image.blend(logo, Image.open(os.path.join(foot_dir, foot[f - d0])).convert("RGB"), smooth((f - d0 + 1) / FADE))
            im.save(dst, quality=95, subsampling=0)
        else:
            os.link(os.path.join(foot_dir, foot[f - d0]), dst)
    return s1 - s0 + 1


def stat_frames(starts):
    """The ONE results board (white, green border): three rows, each a big green number and what it means, popping in
    (scale + fade) at the frames `starts` (relative to the first). One label size for all rows."""
    d_ = os.path.join(OUT, "stat")
    shutil.rmtree(d_, ignore_errors=True)
    os.makedirs(d_)
    lab = 84
    while max(font(lab, False).getlength(txt) for _, txt in ROWS) > 940:         # one size that fits the longest label
        lab -= 2
    num = 260
    pitch = (H - 80) / 3
    for i in range(STAT_N):
        out = white_panel()
        ImageDraw.Draw(out).rectangle([0, 0, W - 1, H - 1], outline=GREEN_D + (255,), width=12)
        for r, ((big, txt), s) in enumerate(zip(ROWS, starts)):
            k = smooth((i - s) / 9.0)
            if k <= 0:
                continue
            cy = 40 + pitch * (r + 0.5)
            if r:                                                                  # a thin rule between the rows
                ImageDraw.Draw(out).line([(120, cy - pitch / 2), (W - 120, cy - pitch / 2)], fill=(226, 232, 240, 255), width=4)
            ov = 1 + 0.06 * max(0.0, 1 - abs(k * 2 - 1.3))
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(layer)
            d.text((740, cy), big, font=font(int(num * (0.75 + 0.25 * k) * ov)), fill=GREEN_D + (int(255 * k),), anchor="rm")
            d.text((800, cy), txt, font=font(lab, False), fill=INK + (int(255 * k),), anchor="lm")
            out.alpha_composite(layer)
        out.convert("RGB").save(os.path.join(d_, f"f_{i + 1:04d}.png"))


if __name__ == "__main__":
    t = json.load(open(os.path.join(OUT, "timing.json")))
    os.makedirs(OUT, exist_ok=True)
    nr = sign_frames(t)
    shutil.rmtree(os.path.join(OUT, "_footage"), ignore_errors=True)
    st = t["stats"]
    stat_frames([f - st[0] for f in st])
    for old in ("stat1", "stat2", "stat3", "demo"):                    # (older layouts: three result boards)
        shutil.rmtree(os.path.join(OUT, old), ignore_errors=True)
    json.dump(dict(t, sign_n=nr, stat_n=STAT_N, logo=os.path.exists(LOGO)), open(os.path.join(OUT, "stamp.json"), "w"))
    print(f"META assets: {nr} sign frames (jpg), 1 x {STAT_N} stat frames; official logo: {os.path.exists(LOGO)}")
