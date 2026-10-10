"""Signs for street part 2 (why inspection wins: human + agent): two rival shops, three building sites, the
scoreboard, the engineers / agents boards, the new floors of the rebuilt building, the LiveReview demo screen.
Same slide rules as part 1: one idea per sign, one font size, emphasis only in **bold**.

    python3 scripts/03d_street_part2_signs.py            # -> assets/street2/*.png (+ sequences)
    python3 scripts/03d_street_part2_signs.py v2           # the reworked part 2 (shops, banner, site boards, labels, demo)
    python3 scripts/03d_street_part2_signs.py v2a          # part 2a: the board over the two shops, site A's line fixed
    python3 scripts/03d_street_part2_signs.py blooper DIR  # (v1) the movie-screen sequence from rendered blooper frames
"""
import importlib, math, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from pipeline import paths

slides = importlib.import_module("03_make_slides")
signs = importlib.import_module("03c_street_signs")
OUT = os.path.join(paths.ROOT, "assets", "street2")
INK = (12, 12, 12)
RED, GREEN, GREY = (220, 38, 38), (22, 163, 74), (100, 116, 139)
DEMO = os.path.join(paths.REPO, "videos", "livereview-launch", "assets", "demo_all_features_navigation.mp4")
text_block, ticker, big_caption = signs.text_block, signs.ticker, signs.big_caption


def save(img, name):
    img.save(os.path.join(OUT, name + ".png"))


def board(name, text, w=1920, h=1080, bg=(255, 255, 255), fg=INK, box=None):
    img = Image.new("RGB", (w, h), bg)
    text_block(img, text, box or (120, 90, w - 120, h - 90), fg=fg, max_size=220)
    save(img, name)
    return img


def shop_banner(name, text, bg, fg=(255, 255, 255), w=2400, h=520, mark=None):
    """A shop's fascia: flat colour, the shop's line in one size, an optional mark (✓) on the right."""
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    right = w - 70
    if mark == "check":
        cx, cy, r = w - 300, h // 2, 170
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255))
        d.line([(cx - 90, cy + 5), (cx - 25, cy + 75), (cx + 100, cy - 80)], fill=GREEN, width=46, joint="curve")
        right = cx - r - 60
    text_block(img, text, (90, 60, right, h - 60), fg=fg, max_size=190)
    save(img, name)


def hoarding_counter(name="site_human", n=150):
    """Site A hoarding: the line, and an 'Incoming code' counter climbing far past what the team can check."""
    d_out = os.path.join(OUT, name)
    os.makedirs(d_out, exist_ok=True)
    W, H = 1280, 720
    num, lab = slides.font(190, slides.BOLD), slides.font(56, slides.REGULAR)
    for i in range(n):
        t = i / (n - 1)
        img = Image.new("RGB", (W, H), (255, 255, 255))
        d = ImageDraw.Draw(img)
        big_caption(d, "**Human only.** Careful, but it doesn't scale.", 120, 76)
        incoming = int(40 + 442 * t ** 1.5)
        checked = int(4 + 8 * t)
        for x0, label, val, col in ((70, "Incoming code", incoming, RED), (760, "Checked", checked, INK)):
            d.text((x0, 270), label, font=lab, fill=(90, 90, 90), anchor="ls")
            d.text((x0, 470), f"{val}", font=num, fill=col, anchor="ls")
        cov = checked / max(1, incoming)
        d.rounded_rectangle([70, 570, 1210, 640], radius=30, fill=(214, 220, 228))
        d.rounded_rectangle([70, 570, 70 + max(60, int(1140 * min(1.0, cov * 3))), 640], radius=30, fill=RED)
        img.save(os.path.join(d_out, f"f_{i + 1:04d}.png"))
    return n


def bug_tag(name, text, w=1100, h=300):
    """A little red warning tag stuck on the agent-only tower."""
    img = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=RED, width=18)
    d.polygon([(70, h - 70), (150, 70), (230, h - 70)], fill=RED)
    d.text((150, h - 100), "!", font=slides.font(110, slides.BOLD), fill=(255, 255, 255), anchor="ms")
    text_block(img, text, (270, 40, w - 50, h - 40), fg=INK, max_size=110)
    save(img, name)


def stamp(name="stamp_ok", s=512):
    """Green 'inspected' stamp (transparent around it)."""
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([16, 16, s - 16, s - 16], outline=GREEN + (255,), width=34, fill=(255, 255, 255, 235))
    d.line([(s * 0.27, s * 0.52), (s * 0.43, s * 0.68), (s * 0.74, s * 0.33)], fill=GREEN + (255,), width=56, joint="curve")
    save(img, name)


ROWS = ["Headcount: same or less", "Code shipped: more", "Quality bar: higher"]
COLS = ["Human only", "Agent only", "Human + agent"]
MARKS = [[False, True, True], [False, True, True], [True, False, True]]      # rows x cols


def scoreboard(prefix="score"):
    """LED scoreboard, one image per reveal: empty grid -> row by row ✓/✗ -> the winning column lit."""
    W, H = 1920, 1080
    head, cell = slides.font(50, slides.BOLD), slides.font(56, slides.REGULAR)
    x_lab, col_x = 80, [930, 1310, 1690]
    row_y = [470, 650, 830]

    def mark(d, cx, cy, ok):
        if ok:
            d.line([(cx - 50, cy), (cx - 15, cy + 40), (cx + 55, cy - 45)], fill=(74, 222, 128), width=24, joint="curve")
        else:
            for a, b in (((-42, -42), (42, 42)), ((-42, 42), (42, -42))):
                d.line([(cx + a[0], cy + a[1]), (cx + b[0], cy + b[1])], fill=(248, 113, 113), width=24)

    for k in range(len(ROWS) + 2):
        img = Image.new("RGB", (W, H), (10, 12, 16))
        d = ImageDraw.Draw(img)
        for x in range(0, W, 10):
            d.line([(x, 0), (x, H)], fill=(18, 20, 26))
        for y in range(0, H, 10):
            d.line([(0, y), (W, y)], fill=(18, 20, 26))
        if k == len(ROWS) + 1:                                 # the winner's column glows
            d.rounded_rectangle([col_x[2] - 170, 250, col_x[2] + 170, 920], radius=30, fill=(20, 83, 45))
        title = "Only one setup **wins all three.**"
        text_block(img, title, (80, 40, W - 80, 200), fg=(255, 244, 214), max_size=110)
        for c, name in enumerate(COLS):
            d.text((col_x[c], 330), name, font=head, fill=(255, 236, 200), anchor="mm")
        for r, name in enumerate(ROWS):
            d.text((x_lab, row_y[r] + 20), name, font=cell, fill=(226, 232, 240), anchor="ls")
            if r < k:
                for c in range(3):
                    mark(d, col_x[c], row_y[r], MARKS[r][c])
        save(img, f"{prefix}_{k}")
    return len(ROWS) + 2


ENGINEERS = ["Issues ranked by importance", "A slide deck for every change", "A quick quiz to check understanding",
             "Conversations right on the MR", "Live refinements"]
AGENTS = ["Your repository rules, every time", "Integrations", "Your data sources", "MCP"]


def tool_board(prefix, title, items, footer=None, accent=(37, 99, 235)):
    """Title + items popping in one by one (+ an optional footer line on the last image)."""
    W, H = 1920, 1080
    f = slides.font(84, slides.REGULAR)
    n = len(items) + (2 if footer else 1)
    for k in range(n):
        img = Image.new("RGB", (W, H), (255, 255, 255))
        d = ImageDraw.Draw(img)
        big_caption(d, title, 170, 100, x=110, w=W - 220)
        y = 340
        step = min(150, int(600 / len(items)))
        for i, it in enumerate(items[:k]):
            d.ellipse([110, y + i * step - 32, 174, y + i * step + 32], fill=accent)
            d.text((142, y + i * step + 2), str(i + 1), font=slides.font(44, slides.BOLD), fill=(255, 255, 255), anchor="mm")
            d.text((210, y + i * step + 30), it, font=f, fill=INK, anchor="ls")
        if footer and k == n - 1:
            d.rectangle([0, H - 170, W, H], fill=(240, 253, 244))
            big_caption(d, footer, H - 62, 76, x=110, w=W - 220)
        save(img, f"{prefix}_{k}")
    return n


def floor_label(name, text, bg):
    img = Image.new("RGB", (1600, 400), bg)
    d = ImageDraw.Draw(img)
    size = 150
    while slides.font(size, 850).getlength(text) > 1480:
        size -= 4
    d.text((800, 200), text, font=slides.font(size, 850), fill=(255, 255, 255), anchor="mm")
    save(img, name)


def demo_screen(name="demo", seconds=6.0, fps=30):
    """The closing big screen: LiveReview's own feature tour, with the address under it."""
    d_out = os.path.join(OUT, name)
    os.makedirs(d_out, exist_ok=True)
    tmp = tempfile.mkdtemp()
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", DEMO, "-t", str(seconds), "-vf", f"fps={fps},scale=1280:-2",
                    os.path.join(tmp, "d_%04d.png")], check=True)
    W, H = 1280, 720
    frames = sorted(os.listdir(tmp))
    for i, fn in enumerate(frames):
        img = Image.new("RGB", (W, H), (255, 255, 255))
        shot = Image.open(os.path.join(tmp, fn)).convert("RGB")
        img.paste(shot, (0, 40))
        d = ImageDraw.Draw(img)
        big_caption(d, "**LiveReview** · hexmos.com/livereview", H - 50, 64)
        img.save(os.path.join(d_out, f"f_{i + 1:04d}.jpg"), quality=92)
    return len(frames)


def url_screen(name="billboard_url"):
    """The closing billboard: just the LiveReview name and its address (no demo footage)."""
    W, H = 1920, 1080
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 26], fill=(37, 99, 235))
    d.text((W / 2, 440), "LiveReview", font=slides.font(250, slides.BOLD), fill=INK, anchor="mm")
    size = 120
    while slides.font(size, slides.BOLD).getlength("hexmos.com/livereview") > W - 240:
        size -= 4
    d.text((W / 2, 660), "hexmos.com/livereview", font=slides.font(size, slides.BOLD), fill=(37, 99, 235), anchor="mm")
    save(img, name)
    return name


def blooper(src_dir, name="blooper", n=330):
    """S15 movie screen: the old spinning web swing on loop; a reviewer's red circle + note appear; caption."""
    d_out = os.path.join(OUT, name)
    os.makedirs(d_out, exist_ok=True)
    src = sorted(f for f in os.listdir(src_dir) if f.endswith((".png", ".jpg")))
    W, H = 1280, 720
    note_f = slides.font(50, slides.BOLD)
    for i in range(n):
        img = Image.open(os.path.join(src_dir, src[i % len(src)])).convert("RGB").resize((W, H))
        if i >= 90:                                            # the reviewer marks it up
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            grow = min(1.0, (i - 90) / 14)
            cx, cy, rx, ry = W * 0.5, H * 0.46, 250, 210
            pts = [(cx + rx * math.cos(a) * (1 + 0.04 * math.sin(3 * a)), cy + ry * math.sin(a))
                   for a in [2 * math.pi * k / 90 * grow - 1.2 for k in range(91)]]
            d.line(pts, fill=(239, 68, 68, 255), width=14, joint="curve")
            if i >= 108:
                d.rounded_rectangle([W * 0.56, H * 0.08, W * 0.97, H * 0.22], radius=18, fill=(255, 255, 255, 235))
                d.text((W * 0.765, H * 0.15), "He's spinning: fix it", font=note_f, fill=(220, 38, 38, 255), anchor="mm")
            img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        d = ImageDraw.Draw(img)
        d.rectangle([0, H - 120, W, H], fill=(255, 255, 255))
        big_caption(d, "Common sense isn't in the **training data.**", H - 38, 64)
        img.save(os.path.join(d_out, f"f_{i + 1:04d}.jpg"), quality=90)
    return n


def site_sign(name, label, states, w=1920, h=1080, accent=(234, 88, 12)):
    """Site board: an orange 'SITE X' band on top, then the line(s) for each state (title -> line -> line + line)."""
    for k, text in enumerate(states):
        img = Image.new("RGB", (w, h), (255, 255, 255))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, w, 190], fill=accent)
        d.text((80, 95), label, font=slides.font(110, slides.BOLD), fill=(255, 255, 255), anchor="lm")
        text_block(img, text, (110, 250, w - 110, h - 90), fg=INK, max_size=170)
        save(img, f"{name}_{k}")


def shop_sign(name, text, bg=(30, 41, 59), fg=(255, 255, 255), w=2400, h=520):
    """The two shops' fascias are identical: same colour, same size, only the line differs."""
    img = Image.new("RGB", (w, h), bg)
    text_block(img, text, (90, 60, w - 90, h - 60), fg=fg, max_size=200)
    save(img, name)


def v2_signs():
    shop_sign("shopL", "Ships without inspection")
    shop_sign("shopR", "Inspects every change")
    shop_sign("shopL_closed", "**CLOSED**", bg=(60, 20, 20))
    banner = lambda n, t: board(n, t, w=3000, h=480)
    banner("banner_a", "You don't inspect. **Your competitor does.**")
    banner("banner_b", "Who wins **the customer?**")
    ticker("led_a", "Customers pick **the better product.**")
    ticker("led_b", "Skip inspection, and **your competitor's product beats yours.**")
    for n in ("led_a", "led_b"):
        os.replace(os.path.join(signs.OUT, n + ".png"), os.path.join(OUT, n + ".png"))
    site_sign("siteA", "SITE A", ["**Human only**", "**Human only.** Careful and high standards, but shipping features can't keep up."])
    site_sign("siteB", "SITE B", ["**Agent only**", "**Agent only.** Fast, but nobody catches what's subtly broken.",
                                  "**Agent only.** Fast, but nobody catches what's subtly broken. **The most refined product wins.**"])
    site_sign("siteC", "SITE C", ["**Human + agent**", "**Human + agent.** Beats both."])
    floor_label("floor_scale", "AGENTS: SCALE", (30, 41, 59))
    floor_label("floor_judgment", "HUMANS: JUDGMENT", (30, 41, 59))
    stamp()
    crack = Image.new("RGBA", (512, 512), (0, 0, 0, 0))       # a crack decal (the broken item, the INSPECTION floor)
    cd = ImageDraw.Draw(crack)
    pts = [(40, 60), (150, 170), (120, 240), (260, 300), (230, 380), (400, 470)]
    cd.line(pts, fill=(20, 20, 20, 255), width=14, joint="curve")
    cd.line([(150, 170), (250, 130), (330, 160)], fill=(20, 20, 20, 255), width=8)
    cd.line([(260, 300), (360, 280)], fill=(20, 20, 20, 255), width=7)
    save(crack, "crack")
    print("demo", demo_screen(), "frames")


def v2a_signs():
    """Part 2a: the two shops share one building; one board over both carries the S10 / S10.1 lines (same size)."""
    for n, t in (("board_a", "You don't inspect. **Your competitor does.**"), ("board_b", "Who wins **the customer?**"),
                 ("board_c", "Customers pick **the better product.**"),
                 ("board_d", "Skip inspection, and **your competitor's product beats yours.**")):
        board(n, t, w=3000, h=560, box=(110, 70, 2890, 490))
    site_sign("siteA", "SITE A", ["**Human only**", "**Human only.** Careful, with high standards, but it can't keep up with the pace."])
    shop_interior("shopR_interior")
    neon("open_neon", "OPEN")
    for n, t, bg in (("banner_headcount", "SAME HEADCOUNT", (30, 64, 175)), ("banner_results", "MORE RESULTS", (21, 128, 61)),
                     ("banner_product", "BETTER PRODUCT", (234, 88, 12))):
        tall_banner(n, t, bg)


def tall_banner(name, text, bg, w=3000, h=600):
    """A building banner (S14): white text reading top to bottom on a coloured cloth, a light hem at both ends."""
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    size = 330
    f = slides.font(size, slides.BOLD)
    while f.getlength(text) > w - 260 and size > 120:
        size -= 10
        f = slides.font(size, slides.BOLD)
    d.text((w // 2, h // 2), text, font=f, fill=(255, 255, 255), anchor="mm")
    d.rectangle([0, 0, 40, h], fill=(240, 240, 235))
    d.rectangle([w - 40, 0, w, h], fill=(240, 240, 235))
    save(img.rotate(-90, expand=True), name)


def shop_interior(name, w=1500, h=1050):
    """The competitor's shop seen through its window: warm light, full shelves, pendant lamps, a counter."""
    import random
    r = random.Random(4)
    img = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(img)
    for y in range(h):                                      # warm wall, brighter towards the lamps
        t = y / h
        d.line([(0, y), (w, y)], fill=(int(250 - 40 * t), int(222 - 50 * t), int(170 - 60 * t)))
    d.rectangle([0, int(h * 0.82), w, h], fill=(150, 98, 60))                     # wooden floor
    cols = [(220, 60, 50), (40, 120, 200), (250, 190, 40), (60, 170, 110), (240, 120, 40), (150, 80, 180), (240, 240, 235)]
    for sy in (0.28, 0.46, 0.64):                           # three shelves of products
        y = int(h * sy)
        d.rectangle([40, y, w - 40, y + 14], fill=(120, 78, 45))
        x = 60
        while x < w - 90:
            bw, bh = r.randint(40, 80), r.randint(50, 110)
            d.rectangle([x, y - bh, x + bw, y], fill=r.choice(cols), outline=(60, 40, 30), width=2)
            x += bw + r.randint(8, 22)
    for lx in (0.2, 0.5, 0.8):                              # pendant lamps
        cx = int(w * lx)
        d.line([(cx, 0), (cx, 70)], fill=(40, 30, 20), width=4)
        d.pieslice([cx - 60, 40, cx + 60, 150], 180, 360, fill=(255, 236, 170))
        d.ellipse([cx - 22, 80, cx + 22, 124], fill=(255, 252, 230))
    d.rectangle([int(w * 0.55), int(h * 0.7), int(w * 0.95), int(h * 0.86)], fill=(110, 70, 40))     # the counter
    d.rectangle([int(w * 0.55), int(h * 0.7), int(w * 0.95), int(h * 0.72)], fill=(200, 160, 100))
    save(img.filter(ImageFilter.GaussianBlur(1.2)), name)


def neon(name, text, w=900, h=360, col=(255, 70, 120)):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = slides.font(220, slides.BOLD)
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(glow).text((w // 2, h // 2), text, font=f, fill=col + (200,), anchor="mm")
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(img).text((w // 2, h // 2), text, font=f, fill=(255, 225, 235, 255), anchor="mm")
    save(img, name)


def main():
    os.makedirs(OUT, exist_ok=True)
    ticker("shops_tick_a", "You don't inspect. **Your competitor does.**")
    ticker("shops_tick_b", "Who wins **the customer?**")
    for name, src in (("shops_tick_a", "shops_tick_a"), ("shops_tick_b", "shops_tick_b")):     # ticker() writes to street/
        os.replace(os.path.join(signs.OUT, src + ".png"), os.path.join(OUT, name + ".png"))
    shop_banner("shop_you", "**YOU** · ships without inspection", (100, 108, 120))
    shop_banner("shop_rival", "**COMPETITOR** · inspects every change", (21, 128, 61), mark="check")
    print("site A", hoarding_counter(), "frames")
    board("site_agent", "**Agent only.** Fast, but nobody cares about the details.")
    board("site_both", "**Human + agent.** Scale and quality.")
    bug_tag("bug_select", "Text selection broken")
    bug_tag("bug_button", "Button does nothing")
    bug_tag("bug_door", "Door to nowhere")
    stamp()
    print("scoreboard", scoreboard(), "images")
    print("engineers", tool_board("eng", "For your engineers: **attention + understanding**", ENGINEERS), "images")
    print("agents", tool_board("agt", "For your agents: **enforcement**", AGENTS, footer="Every review makes **both better.**",
                               accent=(22, 163, 74)), "images")
    floor_label("floor_judgment", "HUMANS: JUDGMENT", (30, 41, 59))
    floor_label("floor_scale", "AGENTS: SCALE", (30, 41, 59))
    board("roof_holds", "Inspection **holds it all up.**", w=2400, h=800)
    blank = Image.new("RGB", (1920, 1080), (36, 72, 54))           # a plain site hoarding (no text: one focal point)
    bd = ImageDraw.Draw(blank)
    for x in range(0, 1920, 240):
        bd.rectangle([x, 0, x + 6, 1080], fill=(30, 62, 46))
    save(blank, "site_blank")
    print("demo", demo_screen(), "frames")
    print("ok ->", OUT)


if __name__ == "__main__":
    if sys.argv[1:2] == ["v2"]:
        os.makedirs(OUT, exist_ok=True)
        v2_signs()
    elif sys.argv[1:2] == ["v2a"]:
        os.makedirs(OUT, exist_ok=True)
        v2a_signs()
    elif sys.argv[1:2] == ["url"]:
        os.makedirs(OUT, exist_ok=True)
        print("url", url_screen())
        floor_label("floor_risk", "RISK", (153, 27, 27))
        floor_label("floor_attention", "ATTENTION", (180, 83, 9))
        print("floor labels: risk, attention")
    elif sys.argv[1:2] == ["blooper"]:
        os.makedirs(OUT, exist_ok=True)
        print("blooper", blooper(sys.argv[2]), "frames")
    else:
        main()
