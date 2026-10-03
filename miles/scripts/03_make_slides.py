"""Render the presentation slides shown on the board (plain Python + Pillow, no Blender).

    python3 scripts/03_make_slides.py

Rules (attention management): one idea per slide, black on white, ONE font size
so it reads left-to-right, top-to-bottom; emphasis only via **bold**. Text is wrapped and auto-sized to fill
the slide. Output: assets/slides/slide_<NN>.png (NN = slide number in the deck,
see ../ppt/LiveReview-Presentation-slides.md).
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import paths

W, H = 1920, 1080
MARGIN_X, MARGIN_Y = 150, 150
INK = (12, 12, 12)
REGULAR, BOLD = 560, 820

# **double asterisks** mark bold — emphasis by weight only, never by size
SLIDES = {
    # Act 1 — The Hook
    1: "You already do a lot of **AI-assisted code generation.**",
    2: "But do you do enough of **AI-assisted code inspection?**",
    # Act 2 — The Belief
    3: "Here's what we **believe:**",
    4: "You owe your users and customers an **AI-assisted inspection layer.**",
    5: "If you are a professional, you must adopt an **AI-assisted inspection layer.**",
    6: "For the sake of your business reputation, consider an **AI-assisted inspection layer.**",
}


def font(size, weight):
    f = ImageFont.truetype(paths.FONT_INTER, size)
    f.set_variation_by_axes([weight])
    return f


def words(text):
    """[(word, bold)] from text with **bold** spans."""
    out, bold = [], False
    for i, part in enumerate(text.split("**")):
        bold = i % 2 == 1
        out += [(w, bold) for w in part.split()]
    return out


def wrap(tokens, fonts, max_w):
    space = fonts[False].getlength(" ")
    lines, cur, cur_w = [], [], 0.0
    for w, b in tokens:
        ww = fonts[b].getlength(w)
        add = ww if not cur else space + ww
        if cur and cur_w + add > max_w:
            lines.append(cur)
            cur, cur_w = [(w, b)], ww
        else:
            cur.append((w, b))
            cur_w += add
    lines.append(cur)
    return lines, space


def layout(text, max_size=170, min_size=60):
    """Largest single font size whose wrapped text fits the safe area."""
    max_w, max_h = W - 2 * MARGIN_X, H - 2 * MARGIN_Y
    tokens = words(text)
    for size in range(max_size, min_size - 1, -4):
        fonts = {False: font(size, REGULAR), True: font(size, BOLD)}
        lines, space = wrap(tokens, fonts, max_w)
        line_h = int(size * 1.18)
        if len(lines) * line_h <= max_h and all(fonts[b].getlength(w) <= max_w for w, b in tokens):
            return fonts, lines, space, line_h, size
    raise ValueError(f"text does not fit: {text}")


def slide(num, text):
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    fonts, lines, space, line_h, size = layout(text)
    y = (H - len(lines) * line_h) / 2 + line_h * 0.8
    for line in lines:
        x = MARGIN_X
        for i, (w, b) in enumerate(line):
            d.text((x, y), w, font=fonts[b], fill=INK, anchor="ls")
            x += fonts[b].getlength(w) + space
        y += line_h
    out = os.path.join(paths.SLIDES, f"slide_{num:02d}.png")
    img.save(out)
    return out, size


if __name__ == "__main__":
    os.makedirs(paths.SLIDES, exist_ok=True)
    for num, text in SLIDES.items():
        out, size = slide(num, text)
        print(f"wrote {out} ({size}px)")
