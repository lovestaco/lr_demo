"""Generate the voice-over, one file per line, with ElevenLabs (or local Kokoro as fallback).

    python3 scripts/07_voiceover.py                        # all lines of assets/audio/vo_piece1.md
    python3 scripts/07_voiceover.py --only 3 4             # regenerate specific lines
    python3 scripts/07_voiceover.py --force                # regenerate everything

Lines come from the table in assets/audio/vo_piece1.md (column "Line"). Output:
assets/audio/vo/line_NN.mp3 + vo/lines.json (text, duration). Unchanged lines are skipped,
so editing one line only spends that line's characters. Key: ELEVEN_LABS_API_KEY in
../blender_owl/.env (gitignored).
"""
import hashlib, json, os, re, subprocess, sys, urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import paths

VOICE_ID = "UgBBYS2sOqTuMpoF3BR0"          # "Mark - Natural Conversations" (chosen by the team)
MODEL = "eleven_multilingual_v2"
SETTINGS = {"stability": 0.45, "similarity_boost": 0.8, "style": 0.25, "use_speaker_boost": True}
SCRIPT = os.path.join(paths.ROOT, "assets", "audio", "vo_piece1.md")
OUT = os.path.join(paths.ROOT, "assets", "audio", "vo")
ENV = os.path.join(paths.REPO, "blender_owl", ".env")


def api_key():
    for line in open(ENV):
        if line.startswith("ELEVEN_LABS_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit("ELEVEN_LABS_API_KEY not found in " + ENV)


def read_lines():
    rows = []
    for line in open(SCRIPT, encoding="utf-8"):
        m = re.match(r"^\|\s*(\d+)\s*\|\s*([\d.]+)s\s*\|.*\|\s*(.+?)\s*\|\s*$", line)
        if m:
            rows.append((int(m.group(1)), float(m.group(2)), m.group(3)))
    return rows


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout.strip())


def tts(text, out, key):
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128",
        data=json.dumps({"text": text, "model_id": MODEL, "voice_settings": SETTINGS}).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    with urllib.request.urlopen(req, timeout=120) as r, open(out, "wb") as fh:
        fh.write(r.read())


if __name__ == "__main__":
    args = sys.argv[1:]
    only = {int(a) for a in args[args.index("--only") + 1:] if a.isdigit()} if "--only" in args else None
    force = "--force" in args
    os.makedirs(OUT, exist_ok=True)
    meta_p = os.path.join(OUT, "lines.json")
    meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
    key = api_key()
    for num, start, text in read_lines():
        out = os.path.join(OUT, f"line_{num:02d}.mp3")
        sig = hashlib.sha1(f"{VOICE_ID}|{MODEL}|{json.dumps(SETTINGS)}|{text}".encode()).hexdigest()[:12]
        fresh = os.path.exists(out) and meta.get(str(num), {}).get("sig") == sig
        if (only and num not in only) or (fresh and not force and not only):
            continue
        tts(text, out, key)
        meta[str(num)] = {"text": text, "start": start, "duration": round(duration(out), 2), "sig": sig}
        print(f"line {num:2d}  {meta[str(num)]['duration']:5.2f}s  {text}")
    json.dump(meta, open(meta_p, "w"), indent=1)
    total = sum(len(t) for _, _, t in read_lines())
    print(f"done — script is {total} characters")
