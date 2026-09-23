#!/usr/bin/env python3
"""Build "LiveReview - Find The Danger" — dark brand redesign with embedded demo clips.

One layout spec is rendered twice:
  * .pptx  via python-pptx  (the deliverable)
  * .png   via Pillow       (preview; uses real Arial metrics, so overflow QA is honest)

Run:  python3 build_deck.py
"""
import os, math, subprocess, glob
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
SP   = "/tmp/claude-1000/-home-taco-pers-demo/ecc6a308-c432-4a39-8c19-4bf3ad0bddc1/scratchpad"
VID  = f"{SP}/deckvid"
POST = f"{SP}/posters"
GEN  = f"{SP}/gen";   os.makedirs(GEN, exist_ok=True)
PREV = f"{SP}/preview"; os.makedirs(PREV, exist_ok=True)
OUT  = os.path.join(HERE, "LiveReview - Find The Danger v2.pptx")

# ---------------------------------------------------------------- brand
BG      = "05070B"   # near-black page
SURFACE = "0E1322"   # card
BORDER  = "1A2440"   # hairline
BLUE    = "1D56F0"   # brand primary
BLUE_LT = "6F93FF"
ICE     = "E8EEFC"
MUTED   = "8B99B8"
WHITE   = "FFFFFF"
RED     = "DC2626"   # danger
GREEN   = "059669"

SW, SH = 13.3333, 7.5          # slide, inches
SCALE  = 120                   # preview px per inch

F_REG  = "/mnt/c/Windows/Fonts/arial.ttf"
F_BOLD = "/mnt/c/Windows/Fonts/arialbd.ttf"
F_MONO = "/mnt/c/Windows/Fonts/cour.ttf"
F_MONOB= "/mnt/c/Windows/Fonts/courbd.ttf"
PPT_SANS, PPT_MONO = "Arial", "Courier New"

def rgb(h): return RGBColor.from_string(h)
def tup(h): return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
_fc = {}
def pil_font(path, pt):
    k = (path, round(pt, 2))
    if k not in _fc: _fc[k] = ImageFont.truetype(path, max(1, int(round(pt * SCALE / 72))))
    return _fc[k]

def text_w(s, path, pt, spc=0.0):
    """Width in inches of `s` at `pt`, with `spc` points of extra letterspacing."""
    f = pil_font(path, pt)
    w = f.getlength(s) / SCALE
    return w + (len(s) - 1) * spc / 72 if len(s) > 1 and spc else w

def wrap(s, path, pt, max_w, spc=0.0):
    out, cur = [], ""
    for word in s.split():
        t = word if not cur else cur + " " + word
        if text_w(t, path, pt, spc) <= max_w or not cur: cur = t
        else: out.append(cur); cur = word
    if cur: out.append(cur)
    return out

# ---------------------------------------------------------------- assets
def make_logo(size=1024):
    """LiveReview 'eye' mark, redrawn from livereview-web/public/assets/logo.svg."""
    p = f"{GEN}/logo.png"
    if os.path.exists(p): return p
    S, im = size * 4, None
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c, u = S / 2, S / 512.0
    def circ(r, fill=None, outline=None, w=0, a=255):
        box = [c - r * u, c - r * u, c + r * u, c + r * u]
        d.ellipse(box, fill=(fill + (a,)) if fill else None,
                  outline=(outline + (a,)) if outline else None, width=int(w * u))
    circ(240, fill=tup("1E429F"), a=51)
    circ(200, fill=tup("111827"))
    circ(200, outline=tup("3B82F6"), w=16)
    circ(220, outline=tup("93C5FD"), w=4, a=153)
    circ(100, fill=tup("60A5FA"))
    circ(50,  fill=tup("1E40AF"))
    r = 15 * u; cx, cy = 220 * u, 220 * u
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 204))
    im.resize((size, size), Image.LANCZOS).save(p)
    return p

def make_glow(name, cx, cy, radius, color, peak=0.42, w=2400, h=1350):
    """Full-bleed background: page colour + one soft radial brand glow."""
    import numpy as np
    p = f"{GEN}/{name}.png"
    if os.path.exists(p): return p
    ys, xs = np.mgrid[0:h, 0:w]
    dist = np.sqrt(((xs / w - cx) * 1.0) ** 2 + ((ys / h - cy) * (h / w)) ** 2)
    g = np.clip(1 - dist / radius, 0, 1) ** 2.2 * peak
    base = np.array(tup(BG), dtype=float)
    top  = np.array(tup(color), dtype=float)
    arr  = base[None, None, :] * (1 - g[..., None]) + top[None, None, :] * g[..., None]
    Image.fromarray(arr.astype("uint8")).save(p)
    return p

# ---------------------------------------------------------------- canvas
class Deck:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Inches(SW), Inches(SH)
        self.blank = self.prs.slide_layouts[6]
        self.slides = []
        self.boxes = []
    def _rec(self, kind, x, y, w, h, label=""):
        self.boxes[-1].append((kind, x, y, w, h, label))
    def new(self, bg_img=None, bg=BG):
        s = self.prs.slides.add_slide(self.blank)
        self.boxes.append([])
        im = Image.new("RGB", (int(SW * SCALE), int(SH * SCALE)), tup(bg))
        self.slides.append((s, im, ImageDraw.Draw(im, "RGBA")))
        if bg_img:
            self.image(bg_img, 0, 0, SW, SH)
        else:
            self.rect(0, 0, SW, SH, fill=bg)
        return s
    @property
    def cur(self): return self.slides[-1]

    # ---- primitives ----
    def rect(self, x, y, w, h, fill=None, line=None, lw=1.0, radius=0.0, alpha=255):
        s, im, d = self.cur
        shp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
                                 Inches(x), Inches(y), Inches(w), Inches(h))
        if radius:
            shp.adjustments[0] = min(0.5, radius / (min(w, h) / 2.0)) * 0.5
        if fill: shp.fill.solid(); shp.fill.fore_color.rgb = rgb(fill)
        else:    shp.fill.background()
        if line: shp.line.color.rgb = rgb(line); shp.line.width = Pt(lw)
        else:    shp.line.fill.background()
        shp.shadow.inherit = False
        shp.text_frame.text = ""
        box = [x * SCALE, y * SCALE, (x + w) * SCALE, (y + h) * SCALE]
        kw = dict(fill=(tup(fill) + (alpha,)) if fill else None,
                  outline=tup(line) if line else None, width=int(max(1, lw * SCALE / 72)))
        if radius: d.rounded_rectangle(box, radius=radius * SCALE, **kw)
        else:      d.rectangle(box, **kw)
        return shp

    def ellipse(self, x, y, w, h, fill=None, line=None, lw=1.0):
        s, im, d = self.cur
        shp = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(w), Inches(h))
        if fill: shp.fill.solid(); shp.fill.fore_color.rgb = rgb(fill)
        else:    shp.fill.background()
        if line: shp.line.color.rgb = rgb(line); shp.line.width = Pt(lw)
        else:    shp.line.fill.background()
        shp.shadow.inherit = False
        shp.text_frame.text = ""
        d.ellipse([x * SCALE, y * SCALE, (x + w) * SCALE, (y + h) * SCALE],
                  fill=tup(fill) if fill else None, outline=tup(line) if line else None,
                  width=int(max(1, lw * SCALE / 72)))
        return shp

    def image(self, path, x, y, w, h):
        s, im, d = self.cur
        s.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
        src = Image.open(path).convert("RGBA").resize((max(1, int(w * SCALE)), max(1, int(h * SCALE))), Image.LANCZOS)
        im.paste(src, (int(x * SCALE), int(y * SCALE)), src)

    def text(self, lines, x, y, w, pt, color=WHITE, bold=False, mono=False,
             lh=1.18, spc=0.0, align="l", caps=False):
        """Pre-wrapped lines, one paragraph each -> identical breaks in PowerPoint and preview."""
        if isinstance(lines, str): lines = [lines]
        if caps: lines = [l.upper() for l in lines]
        path = (F_MONOB if bold else F_MONO) if mono else (F_BOLD if bold else F_REG)
        s, im, d = self.cur
        line_h = pt * lh / 72.0
        h = line_h * len(lines)
        tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h + 0.12))
        tf = tb.text_frame
        tf.word_wrap = True; tf.auto_size = MSO_AUTO_SIZE.NONE
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.TOP
        for i, ln in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]
            p.line_spacing = lh
            r = p.add_run(); r.text = ln
            f = r.font
            f.name = PPT_MONO if mono else PPT_SANS
            f.size = Pt(pt); f.bold = bold; f.color.rgb = rgb(color)
            if spc:
                r._r.get_or_add_rPr().set("spc", str(int(round(spc * 100))))
        # preview
        fnt = pil_font(path, pt)
        asc, desc = fnt.getmetrics()
        for i, ln in enumerate(lines):
            ty = (y + i * line_h) * SCALE + (line_h * SCALE - (asc + desc)) / 2
            lw_in = text_w(ln, path, pt, spc)
            tx = x * SCALE if align == "l" else (
                 (x + (w - lw_in) / 2) * SCALE if align == "c" else (x + w - lw_in) * SCALE)
            if spc:
                cx = tx
                for ch in ln:
                    d.text((cx, ty), ch, font=fnt, fill=tup(color))
                    cx += fnt.getlength(ch) + spc * SCALE / 72
            else:
                d.text((tx, ty), ln, font=fnt, fill=tup(color))
        mw = max(text_w(l, path, pt, spc) for l in lines) if lines else 0
        bx = x if align == "l" else (x + (w - mw) / 2 if align == "c" else x + w - mw)
        self._rec("text", bx, y, mw, h, lines[0][:38] if lines else "")
        return h

    def video(self, key, x, y, w):
        """Embed the clip; preview draws its poster frame. Returns height in inches."""
        s, im, d = self.cur
        vid, post = f"{VID}/{key}.mp4", f"{POST}/{key}.jpg"
        pw, ph = Image.open(post).size
        h = w * ph / pw
        pad = 0.035
        self.rect(x - pad, y - pad, w + 2 * pad, h + 2 * pad, fill=None, line=BORDER, lw=1.25, radius=0.10)
        s.shapes.add_movie(vid, Inches(x), Inches(y), Inches(w), Inches(h),
                           poster_frame_image=post, mime_type="video/mp4")
        src = Image.open(post).convert("RGB").resize((int(w * SCALE), int(h * SCALE)), Image.LANCZOS)
        im.paste(src, (int(x * SCALE), int(y * SCALE)))
        self._rec("video", x - pad, y - pad, w + 2 * pad, h + 2 * pad, key)
        return h

    def save(self):
        self.prs.save(OUT)
        for f in glob.glob(f"{PREV}/*.png"): os.remove(f)
        for i, (_, im, _) in enumerate(self.slides, 1):
            im.save(f"{PREV}/slide-{i:02d}.png")

# ---------------------------------------------------------------- chrome
LOGO = make_logo()

def chrome(dk, act=None, tag=None):
    """Top rail: eye mark + wordmark on the left, act tag on the right."""
    dk.image(LOGO, 0.62, 0.42, 0.30, 0.30)
    dk.text("LiveReview", 1.00, 0.455, 2.2, 12.5, color=ICE, bold=True, spc=0.3)
    if act:
        label = f"{act}  —  {tag}"
        w = text_w(label.upper(), F_BOLD, 10.5, 1.6) + 0.02
        dk.text(label, SW - 0.62 - w, 0.475, w, 10.5, color=MUTED, bold=True, spc=1.6, caps=True, align="r")

M       = 0.62                 # page margin
CONTENT = SW - 2 * M

# ---------------------------------------------------------------- slide types
TOP, BOT = 1.00, 6.98          # content band (chrome above, 0.52 margin below)

def _h(lines, pt, lh):  return pt * lh / 72.0 * len(lines)

def slide_title(dk):
    dk.new(bg_img=make_glow("bg_title", 0.30, 0.34, 0.92, BLUE, peak=0.40))
    dk.image(LOGO, M, 1.58, 0.86, 0.86)
    dk.text("LiveReview", M + 1.06, 1.82, 4.0, 19, color=ICE, bold=True, spc=0.9)
    ty = 2.86
    th = dk.text(["Find the", "danger."], M, ty, 11.0, 78, color=WHITE, bold=True, lh=1.06)
    dk.text("Rank the risk. Enforce the standard. Keep the code yours.",
            M, ty + th + 0.34, 11.0, 17.5, color=MUTED)
    agenda = [("01", "ATTENTION"), ("02", "CONSISTENCY"), ("03", "CONTROL")]
    cw, gap = 2.58, 0.30
    x0 = SW - M - (cw * 3 + gap * 2)
    for i, (n, t) in enumerate(agenda):
        x = x0 + i * (cw + gap)
        dk.rect(x, 6.14, cw, 0.80, fill=SURFACE, line=BORDER, lw=1.0, radius=0.10)
        dk.text(n, x + 0.26, 6.32, 0.6, 15, color=BLUE_LT, bold=True)
        dk.text(t, x + 0.80, 6.37, cw - 1.0, 10.5, color=MUTED, bold=True, spc=1.4, caps=True)

def _build_fit(rows):
    """Pick type sizes so rows 1-2 and the bottom-anchored card never collide."""
    tw, cw = CONTENT - 0.33, CONTENT - 1.10
    for pt1 in (37, 34, 31, 28, 26):
        for pt3 in (25, 23, 21):
            l1 = wrap(rows[0][2], F_BOLD, pt1, tw)
            l2 = wrap(rows[1][2], F_BOLD, 27, tw)
            l3 = wrap(rows[2][2], F_BOLD, pt3, cw)
            h1, h2, h3 = _h(l1, pt1, 1.16), _h(l2, 27, 1.16), _h(l3, pt3, 1.18)
            r1_txt = 1.60
            r2_lab = r1_txt + h1 + 0.52
            r2_end = r2_lab + 0.34 + h2
            card_h = 0.56 + h3 + 0.44
            card_y = 6.88 - card_h
            if card_y - r2_end >= 0.34:
                return pt1, pt3, l1, l2, l3, h1, r2_lab, card_y, card_h
    raise SystemExit("build slide will not fit")

def slide_build(dk, act_no, act_tag, rows, upto):
    """Progressive statement build; anchors are identical across an act's three builds."""
    pt1, pt3, l1, l2, l3, h1, r2_lab, card_y, card_h = _build_fit(rows)
    dk.new()
    chrome(dk, f"ACT {act_no}", act_tag)
    tx, tw = 0.95, CONTENT - 0.33
    if upto >= 1:
        dk.ellipse(M, 1.26 + 0.028, 0.115, 0.115, fill=RED)
        dk.text(rows[0][1], tx, 1.26, 6.0, 10.5, color=RED, bold=True, spc=1.7, caps=True)
        dk.text(l1, tx, 1.60, tw, pt1, color=WHITE, bold=True, lh=1.16)
    if upto >= 2:
        dk.ellipse(M, r2_lab + 0.028, 0.115, 0.115, fill=BLUE_LT)
        dk.text(rows[1][1], tx, r2_lab, 6.0, 10.5, color=BLUE_LT, bold=True, spc=1.7, caps=True)
        dk.text(l2, tx, r2_lab + 0.34, tw, 27, color=ICE, bold=True, lh=1.16)
    if upto >= 3:
        dk.rect(M, card_y, CONTENT, card_h, fill=SURFACE, line=BLUE, lw=1.1, radius=0.12)
        dk.ellipse(M + 0.42, card_y + 0.40, 0.115, 0.115, fill=BLUE_LT)
        dk.text(rows[2][1], M + 0.75, card_y + 0.372, 6.0, 10.5, color=BLUE_LT, bold=True, spc=1.7, caps=True)
        dk.text(l3, M + 0.75, card_y + 0.72, CONTENT - 1.10, pt3, color=WHITE, bold=True, lh=1.18)

def _aspect(key):
    w, h = Image.open(f"{POST}/{key}.jpg").size
    return w / h

def slide_demo_wide(dk, key, act_no, act_tag, head, cap):
    dk.new()
    chrome(dk, f"ACT {act_no}", act_tag)
    hl = wrap(head, F_BOLD, 26, CONTENT)
    cl = wrap(cap,  F_REG, 13.5, CONTENT)
    hh, ch = _h(hl, 26, 1.16), _h(cl, 13.5, 1.34)
    dk.text(hl, M, TOP, CONTENT, 26, color=WHITE, bold=True, lh=1.16)
    dk.text(cl, M, TOP + hh + 0.15, CONTENT, 13.5, color=MUTED, lh=1.34)
    vy = TOP + hh + 0.15 + ch + 0.28
    vw = min(10.6, CONTENT, (BOT - vy) * _aspect(key))
    dk.video(key, (SW - vw) / 2, vy, vw)

def slide_demo_split(dk, key, act_no, act_tag, head, cap, stats):
    dk.new()
    chrome(dk, f"ACT {act_no}", act_tag)
    rail_w, gap = 3.62, 0.52
    vx = M + rail_w + gap
    vw = SW - M - vx
    vh = vw / _aspect(key)
    hl = wrap(head, F_BOLD, 25, rail_w)
    cl = wrap(cap,  F_REG, 13.5, rail_w)
    hh, ch = _h(hl, 25, 1.16), _h(cl, 13.5, 1.35)
    rows = []
    for val, sub in (stats or []):
        sl = wrap(sub, F_REG, 11.5, rail_w - 0.30)
        rows.append((val, sl, 0.30 + _h(sl, 11.5, 1.28) + 0.20))
    total = hh + 0.24 + ch + (0.34 + sum(r[2] for r in rows) if rows else 0)
    band_h = BOT - TOP
    y = TOP + max(0.0, (band_h - total) / 2)
    dk.text(hl, M, y, rail_w, 25, color=WHITE, bold=True, lh=1.16)
    dk.text(cl, M, y + hh + 0.24, rail_w, 13.5, color=MUTED, lh=1.35)
    sy = y + hh + 0.24 + ch + 0.34
    for val, sl, rh in rows:
        dk.ellipse(M + 0.015, sy + 0.075, 0.105, 0.105, fill=BLUE)
        dk.text(wrap(val, F_BOLD, 15, rail_w - 0.30), M + 0.30, sy, rail_w - 0.30, 15, color=ICE, bold=True)
        dk.text(sl, M + 0.30, sy + 0.30, rail_w - 0.30, 11.5, color=MUTED, lh=1.28)
        sy += rh
    dk.video(key, vx, TOP + (band_h - vh) / 2, vw)

def slide_close(dk, answers):
    dk.new(bg_img=make_glow("bg_close", 0.72, 0.68, 0.95, BLUE, peak=0.34))
    chrome(dk)
    dk.text("Three problems. One reviewer.", M, 1.22, 11.5, 38, color=WHITE, bold=True)
    cw, gap = 3.764, 0.40
    bodies = [wrap(b, F_REG, 13.5, cw - 0.72) for _, _, b in answers]
    card_h = 1.02 + max(_h(b, 13.5, 1.38) for b in bodies) + 0.40
    cy = 2.60
    for i, (n, t, _) in enumerate(answers):
        x = M + i * (cw + gap)
        dk.rect(x, cy, cw, card_h, fill=SURFACE, line=BORDER, lw=1.0, radius=0.12)
        dk.text(n, x + 0.36, cy + 0.32, 1.0, 14, color=BLUE_LT, bold=True, spc=1.0)
        dk.text(t, x + 0.36, cy + 0.64, cw - 0.72, 17, color=WHITE, bold=True)
        dk.text(bodies[i], x + 0.36, cy + 1.02, cw - 0.72, 13.5, color=MUTED, lh=1.38)
    ly = cy + card_h + 0.52
    dk.image(LOGO, M, ly, 0.42, 0.42)
    dk.text("hexmos.com/livereview", M + 0.58, ly + 0.115, 6.0, 14, color=ICE, bold=True)

# ---------------------------------------------------------------- content
ACTS = [
    dict(no="01", tag="Attention", rows=[
        ("p", "The problem",  "AI lets your team produce more code than it can inspect."),
        ("q", "The question", "So which changes deserve your engineers' scarce attention?"),
        ("a", "LiveReview",   "LiveReview ranks every hunk by blast radius and review priority."),
    ]),
    dict(no="02", tag="Consistency", rows=[
        ("p", "The problem",  "A standard is useless when every engineer must remember to enforce it."),
        ("q", "The question", "How do you make good review happen every time without slowing the team down?"),
        ("a", "LiveReview",   "LiveReview reviews at commit, push, PR, CI/CD, and on schedule, enforcing your rules."),
    ]),
    dict(no="03", tag="Control", rows=[
        ("p", "The problem", "Other reviewers send your code outside your infrastructure, and seat-based monthly pricing can get expensive."),
        ("q", "The answer",  "Keep your code in your infrastructure and choose which AI models inspect it."),
        ("a", "And also",    "Adaptive Reviews cut AI cost; Livi learns from reviews; CLI, IDE, MCP and API fit your workflow."),
    ]),
]

DEMOS = {
 "dashboard": ("S", "01", "Attention", "Every review, one dashboard",
    "Volume, issue mix and quality trends across every stage a review can run at.",
    [("177 pre-commit reviews", "2,143 issues found"),
     ("3 merge / pull requests", "54 issues found"),
     ("5 API / MCP runs", "34 issues found")]),
 "list_reviews": ("W", "01", "Attention", "Every run lands in one queue",
    "Branch, repository, source and status for each review — GitHub, GitLab, or straight from the CLI.", None),
 "review_blast_radius": ("S", "01", "Attention", "Blast radius tells you what to read first",
    "Each hunk is scored from measurable signals, so the riskiest change sits at the top of the review.",
    [("Risk 71 — high", "blast radius 51, review priority 100"),
     ("9 signals, all visible", "complexity, test coverage, fan-out"),
     ("Open breakdown", "see exactly why a hunk scored")]),
 "review_slides": ("W", "02", "Consistency", "The review reads like a briefing",
    "Findings become slides — technical highlights per file, with auto-play for a walkthrough.", None),
 "review_quiz": ("S", "02", "Consistency", "Check the review actually landed",
    "A short quiz per review turns a skim into understanding.",
    [("5 questions per review", "graded against the diff"),
     ("Slides · Text · Quiz", "three ways to read one review")]),
 "cicd_gates": ("W", "02", "Consistency", "A gate your pipeline can call",
    "Write a jq rule over a review's findings, save it, and call one URL from any CI/CD pipeline to block or allow the build.", None),
 "schedule_review": ("S", "02", "Consistency", "Reviews that run without being asked",
    "Point LiveReview at a repository's default branch and set a time.",
    [("Per-repository schedules", "GitHub, GitLab and more"),
     ("Runs on the default branch", "main or master, your choice")]),
 "livi_chat_bot": ("W", "03", "Control", "Ask Livi about your own codebase",
    "Reviews, trends, adoption and billing — answered from your data, inside your infrastructure.", None),
 "onboarding_report": ("S", "03", "Control", "Onboarding, measured",
    "A generated report on how your organisation actually adopted LiveReview.",
    [("7 sections", "adoption, repositories, engineers, quality"),
     ("Cost & efficiency", "what review actually costs you"),
     ("Engagement & trust", "are findings being acted on")]),
 "all_features_navigation": ("W", "03", "Control", "Everything from one top bar",
    "Reviews, Explore, Providers, Reports and Settings — start a review from the UI, CLI, MCP or chatbot.", None),
}

ORDER = [
    ("title", None),
    ("build", (0, 1)), ("build", (0, 2)), ("build", (0, 3)),
    ("demo", "dashboard"), ("demo", "list_reviews"), ("demo", "review_blast_radius"),
    ("build", (1, 1)), ("build", (1, 2)), ("build", (1, 3)),
    ("demo", "review_slides"), ("demo", "review_quiz"),
    ("demo", "cicd_gates"), ("demo", "schedule_review"),
    ("build", (2, 1)), ("build", (2, 2)), ("build", (2, 3)),
    ("demo", "livi_chat_bot"), ("demo", "onboarding_report"),
    ("demo", "all_features_navigation"),
    ("close", None),
]

CLOSE = [("01", "Attention",   "Every hunk ranked by blast radius and review priority."),
         ("02", "Consistency", "Reviews at commit, push, PR, CI/CD and on schedule, enforcing your rules."),
         ("03", "Control",     "Your code stays in your infrastructure, and you pick the AI models that inspect it.")]

# ---------------------------------------------------------------- media timing
NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}

AUTOPLAY_TIMING = (
 '<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
 '<p:childTnLst>'
 '<p:seq concurrent="1" nextAc="seek">'
 '<p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
 '<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst><p:childTnLst>'
 '<p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
 '<p:par><p:cTn id="5" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="withEffect">'
 '<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
 '<p:cmd type="call" cmd="playFrom(0.0)"><p:cBhvr><p:cTn id="6" dur="1" fill="hold"/>'
 '<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:cmd>'
 '</p:childTnLst></p:cTn></p:par>'
 '</p:childTnLst></p:cTn></p:par>'
 '</p:childTnLst></p:cTn></p:par>'
 '</p:childTnLst></p:cTn>'
 '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
 '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
 '</p:seq>'
 '<p:video><p:cMediaNode vol="80000"><p:cTn id="7" fill="hold" display="0" repeatCount="indefinite">'
 '<p:stCondLst><p:cond delay="indefinite"/></p:stCondLst></p:cTn>'
 '<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cMediaNode></p:video>'
 '</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')

def autoplay_media(path):
    """Rewrite each media slide's timing tree so the clip starts on slide entry and loops."""
    import zipfile, shutil, re
    tmp = path + ".tmp"
    zin, n = zipfile.ZipFile(path), 0
    zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        data = zin.read(item.filename)
        if re.match(r"ppt/slides/slide\d+\.xml$", item.filename) and b"<p:video>" in data:
            x = data.decode("utf-8")
            spid = re.search(r'<p:video>.*?<p:spTgt spid="(\d+)"/>', x, re.S).group(1)
            x2 = re.sub(r"<p:timing>.*</p:timing>", AUTOPLAY_TIMING.format(spid=spid), x, flags=re.S)
            if x2 != x:
                n += 1
                data = x2.encode("utf-8")
        zout.writestr(item, data)
    zin.close(); zout.close(); shutil.move(tmp, path)
    return n

# ---------------------------------------------------------------- qa
def qa(dk):
    """Geometry check: slide-edge margins and text/video collisions."""
    bad = 0
    for i, boxes in enumerate(dk.boxes, 1):
        for kind, x, y, w, h, lab in boxes:
            if x < 0.55 or y < 0.35 or x + w > SW - 0.55 or y + h > SH - 0.45:
                print(f"  ! slide {i:02d} {kind} out of margin: "
                      f"x={x:.2f} y={y:.2f} r={x+w:.2f} b={y+h:.2f}  {lab!r}"); bad += 1
        for a in range(len(boxes)):
            for b in range(a + 1, len(boxes)):
                k1, x1, y1, w1, h1, l1 = boxes[a]
                k2, x2, y2, w2, h2, l2 = boxes[b]
                ox = min(x1 + w1, x2 + w2) - max(x1, x2)
                oy = min(y1 + h1, y2 + h2) - max(y1, y2)
                if ox > 0.02 and oy > 0.02:
                    print(f"  ! slide {i:02d} overlap {l1!r} x {l2!r} "
                          f"({ox:.2f}in x {oy:.2f}in)"); bad += 1
    print("  QA: clean" if not bad else f"  QA: {bad} issue(s)")
    return bad

# ---------------------------------------------------------------- main
def main():
    dk = Deck()
    for kind, arg in ORDER:
        if kind == "title": slide_title(dk)
        elif kind == "close": slide_close(dk, CLOSE)
        elif kind == "build":
            ai, upto = arg; a = ACTS[ai]
            slide_build(dk, a["no"], a["tag"], a["rows"], upto)
        else:
            lay, no, tag, head, cap, stats = DEMOS[arg]
            (slide_demo_split if lay == "S" else slide_demo_wide)(
                dk, arg, no, tag, head, cap, *( [stats] if lay == "S" else [] ))
    dk.save()
    qa(dk)
    n = autoplay_media(OUT)
    print(f"wrote {OUT}  ({len(dk.slides)} slides, {os.path.getsize(OUT)/1e6:.1f} MB, {n} media slides set to autoplay)")
    print(f"previews: {PREV}/slide-XX.png")

if __name__ == "__main__":
    main()
