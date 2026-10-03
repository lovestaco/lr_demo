"""Search the CMU mocap index and download matching BVH clips (no account, no clicking).

    python3 scripts/00_cmu_fetch.py jump                 # list matches
    python3 scripts/00_cmu_fetch.py jump --get 5         # download the first 5 matches
    python3 scripts/00_cmu_fetch.py --ids 02_01 13_29    # download specific clips

Source: CMU Graphics Lab Motion Capture Database (free for any use), BVH
conversion by B. Hahne / cgspeed, mirrored at github.com/una-dinosauria/cmu-mocap.
Files land in blender_assets_downloaded/cmu/<id>.bvh with an index.json of descriptions.
"""
import json, os, re, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import paths

INDEX = os.path.join(paths.CMU_DIR, "cmu-mocap-index-text.txt")


def load_index():
    os.makedirs(paths.CMU_DIR, exist_ok=True)
    if not os.path.exists(INDEX):
        urllib.request.urlretrieve(paths.CMU_REPO_RAW + "/cmu-mocap-index-text.txt", INDEX)
    clips = {}
    for line in open(INDEX, encoding="utf-8", errors="ignore"):
        m = re.match(r"^(\d+_\d+)\s+(.*)$", line.strip())
        if m:
            clips[m.group(1)] = m.group(2).strip()
    return clips


def fetch(cid, desc):
    subj = cid.split("_")[0].zfill(3)
    out = os.path.join(paths.CMU_DIR, f"{cid}.bvh")
    if not os.path.exists(out):
        urllib.request.urlretrieve(f"{paths.CMU_REPO_RAW}/data/{subj}/{cid}.bvh", out)
    meta_p = os.path.join(paths.CMU_DIR, "index.json")
    meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
    meta[cid] = desc
    json.dump(meta, open(meta_p, "w"), indent=1, sort_keys=True)
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    clips = load_index()
    if "--ids" in args:
        ids = args[args.index("--ids") + 1:]
        for cid in ids:
            print("got", fetch(cid, clips.get(cid, "")), "-", clips.get(cid, ""))
        sys.exit()
    n = int(args[args.index("--get") + 1]) if "--get" in args else 0
    terms = [a.lower() for a in args if not a.startswith("--") and not a.isdigit()]
    hits = [(cid, d) for cid, d in clips.items() if all(t in d.lower() for t in terms)]
    for i, (cid, d) in enumerate(hits):
        if i < n:
            print("got", fetch(cid, d), "-", d)
        else:
            print(f"{cid}\t{d}")
    print(f"{len(hits)} matches" + (f", downloaded {min(n, len(hits))}" if n else " (add --get N to download)"))
