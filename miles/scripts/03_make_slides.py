"""Render the presentation slides shown on the board (plain Python + Pillow, no Blender).

    python3 scripts/03_make_slides.py

Edit SLIDES below to change copy; output goes to assets/slides/slide_XX.png (1920x1080).
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import paths

W, H = 1920, 1080
BG = (11, 18, 32)            # #0B1220
INK = (241, 245, 249)
MUTED = (148, 163, 184)
BLUE = (59, 130, 246)        # #3B82F6
BLUE_LT = (96, 165, 250)     # #60A5FA
NAVY = (30, 64, 175)         # #1E40AF
DARK = (17, 24, 39)          # #111827

# (kicker, headline line 1, headline line 2 [blue])
SLIDES = [
    ("You already do a lot of…", "AI-assisted", "code generation"),
    ("But do you do enough of…", "AI-assisted", "code inspection?"),
]


def font(size, weight):
    f = ImageFont.truetype(paths.FONT_INTER, size)
    f.set_variation_by_axes([weight])
    return f


def draw_logo(img, cx, cy, r):
    """LiveReview eye (mirrors livereview-web/public/assets/logo.svg)."""
    s = r / 200.0
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([cx - 240 * s, cy - 240 * s, cx + 240 * s, cy + 240 * s], fill=(30, 66, 159, 110))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18 * s)))
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 220 * s, cy - 220 * s, cx + 220 * s, cy + 220 * s], outline=(147, 197, 253, 150), width=max(1, int(4 * s)))
    d.ellipse([cx - 200 * s, cy - 200 * s, cx + 200 * s, cy + 200 * s], fill=DARK, outline=BLUE, width=max(2, int(16 * s)))
    d.ellipse([cx - 100 * s, cy - 100 * s, cx + 100 * s, cy + 100 * s], fill=BLUE_LT)
    d.ellipse([cx - 50 * s, cy - 50 * s, cx + 50 * s, cy + 50 * s], fill=NAVY)
    d.ellipse([cx - 51 * s, cy - 51 * s, cx - 21 * s, cy - 21 * s], fill=(255, 255, 255, 205))


def slide(i, kicker, line1, line2):
    """Minimal black-on-white: one small lead-in line, one big statement, tiny logo."""
    img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((150, 360), kicker, font=font(88, 500), fill=(90, 90, 90), anchor="ls")
    d.text((140, 590), line1, font=font(186, 800), fill=(10, 10, 10), anchor="ls")
    d.text((140, 820), line2, font=font(186, 800), fill=(10, 10, 10), anchor="ls")
    draw_logo(img, 172, H - 110, 26)
    d.text((212, H - 110), "LiveReview", font=font(38, 600), fill=(60, 60, 60), anchor="lm")
    out = os.path.join(paths.SLIDES, f"slide_{i + 1:02d}.png")
    img.convert("RGB").save(out)
    return out


if __name__ == "__main__":
    os.makedirs(paths.SLIDES, exist_ok=True)
    for i, s in enumerate(SLIDES):
        print("wrote", slide(i, *s))
