"""Generate the sound effects that shot scripts cue with shot.sfx(name, frame) — ElevenLabs Sound Effects API.

    python3 scripts/08_sfx.py                 # every missing effect in SFX below
    python3 scripts/08_sfx.py --only web_thwip tower_crash --force

Output: assets/audio/sfx/<name>.mp3 (06_assemble.py picks them up by name). Existing files are
skipped, so only new/changed effects spend credits (~40 credits per second of audio).
Key: ELEVEN_LABS_API_KEY in ../blender_owl/.env (gitignored). Free-tier audio is non-commercial:
regenerate on a paid plan before publishing.
"""
import json, os, re, subprocess, sys, urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import paths

OUT = os.path.join(paths.ROOT, "assets", "audio", "sfx")
ENV = os.path.join(paths.REPO, "blender_owl", ".env")

# Hand-picked by the user (originals in assets/audio/sfx/source/, trimmed + levelled with normalize()):
#   web_thwip        <- spider-man-customized-web-thwip-sound-effect-1_ybmate.mp3   (peak 0.06 s in)
#   landing_thud     <- superhero-flying-landing-gfx-sounds-1-1-00-02.mp3           (impact 0.2 s in)
#   board_whoosh, cartwheel_whoosh <- superhero-flying-past-gfx-sounds-1-00-02.mp3  (peak 0.2-0.4 s in)
# Never regenerate those here. Generated ones: name: (prompt, seconds)
SFX = {
    "board_thud": ("loud heavy thump of a big monitor stand slamming onto a wooden floor, punchy impact", 1.0),
    "tv_power_on": ("CRT television power on, electric hum and soft click", 0.9),
    "paper_avalanche": ("avalanche of paper sheets pouring out and piling up, rustling flurry", 2.5),
    "bugs_skitter": ("swarm of small insects skittering and buzzing, creepy cartoon", 1.8),
    "ui_pop": ("bright punchy cartoon pop sound, bubble pop with a short click, clearly audible", 0.6),
    "block_thud": ("large foam block dropping onto a stack, muffled wooden thud", 0.7),
    "tower_crash": ("tower of heavy blocks toppling and crashing to the floor, cartoon collapse", 2.6),
    "cash_flutter": ("stack of banknotes riffling and fluttering, money shuffle", 1.2),
}


def api_key():
    for line in open(ENV):
        if line.startswith("ELEVEN_LABS_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit("ELEVEN_LABS_API_KEY not found in " + ENV)


def generate(name, prompt, seconds, key):
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128",
        data=json.dumps({"text": prompt, "duration_seconds": seconds, "prompt_influence": 0.5}).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    raw = os.path.join(OUT, name + ".raw.mp3")
    with urllib.request.urlopen(req, timeout=120) as r, open(raw, "wb") as fh:
        fh.write(r.read())
    normalize(raw, os.path.join(OUT, name + ".mp3"))
    os.remove(raw)


def normalize(src, dst, peak_db=-3.0, rms_cap_db=-16.0):
    """Peak-normalise to -3 dBFS, but never louder than -16 dB mean (buzzes/drones stay polite)."""
    st = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", "volumedetect", "-f", "null", "-"],
                        capture_output=True, text=True).stderr
    mx = float(re.search(r"max_volume: ([-0-9.]+)", st).group(1))
    mean = float(re.search(r"mean_volume: ([-0-9.]+)", st).group(1))
    gain = min(peak_db - mx, rms_cap_db - mean)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-af", f"volume={gain:.1f}dB", "-b:a", "192k", dst],
                   check=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--normalize" in args:                    # re-level files already on disk
        for name in SFX:
            p = os.path.join(OUT, name + ".mp3")
            if os.path.exists(p):
                os.replace(p, p + ".tmp.mp3")
                normalize(p + ".tmp.mp3", p)
                os.remove(p + ".tmp.mp3")
        sys.exit()
    only = set(args[args.index("--only") + 1:]) - {"--force"} if "--only" in args else None
    os.makedirs(OUT, exist_ok=True)
    key = api_key()
    for name, (prompt, sec) in SFX.items():
        exists = os.path.exists(os.path.join(OUT, name + ".mp3"))
        if (only and name not in only) or (exists and "--force" not in args):
            continue
        generate(name, prompt, sec, key)
        print(f"{name:18s} {sec:.1f}s  {prompt}")
