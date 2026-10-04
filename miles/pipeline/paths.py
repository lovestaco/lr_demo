"""Every path the pipeline uses, in one place."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../miles
REPO = os.path.dirname(ROOT)

SOURCE_BLEND = os.path.join(ROOT, "miles.blend")                      # Sketchfab import (scratch)
MIXAMO_CLIPS = os.path.join(REPO, "blender_assets_downloaded")        # Mixamo FBX downloads
MIXAMO_BASE_CLIP = "Hanging Idle"                                     # downloaded *with skin*
MIXAMO_UPLOAD = os.path.join(ROOT, "assets", "mixamo_upload", "miles_for_mixamo.fbx")
SLIDES = os.path.join(ROOT, "assets", "slides")
LOGO_SVG = os.path.join(REPO, "livereview-web", "public", "assets", "logo.svg")

BUILD = os.path.join(ROOT, "build")
CHARACTER_BLEND = os.path.join(BUILD, "character.blend")
SCENE_BLEND = os.path.join(BUILD, "scene.blend")


def shot_blend(name):
    return os.path.join(BUILD, name + ".blend")


def slide(num):
    return os.path.join(SLIDES, f"slide_{num:02d}.png")
RENDERS = os.path.join(ROOT, "renders")


def setup_sys_path():
    import sys
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)

FONT_INTER = os.path.join(REPO, "videos", "livereview-launch", "assets", "fonts", "Inter-var.woff2")

CMU_DIR = os.path.join(MIXAMO_CLIPS, "cmu")                           # CMU mocap BVH downloads
SPIDER_GLB = os.path.join(MIXAMO_CLIPS, "sketchfab_spider", "spider.glb")   # "Spider animated character" by TheGameAssets (CC-BY)
CMU_REPO_RAW = "https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/master"
