"""Find and download Sketchfab models (glb) for set dressing.

    python3 scripts/09_sketchfab_fetch.py search "low poly car" [--animated] [--max-faces 60000]
    python3 scripts/09_sketchfab_fetch.py get <uid> <folder_name>      # -> ../blender_assets_downloaded/<folder>/model.glb + CREDITS.txt

Token: SKETCHFAB_API_TOKEN in ../blender_owl/.env (gitignored; never printed). Only downloadable models with a
CC / Free Standard licence are listed; the credit line is written next to the model (CC-BY needs attribution).
"""
import io, json, os, sys, urllib.parse, urllib.request, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(os.path.dirname(ROOT), "blender_assets_downloaded")
ENV = os.path.join(os.path.dirname(ROOT), "blender_owl", ".env")


def token():
    for line in open(ENV):
        if line.startswith("SKETCHFAB_API_TOKEN"):
            return line.split("=", 1)[1].strip().strip('"\'')
    sys.exit("no SKETCHFAB_API_TOKEN in blender_owl/.env")


def api(url, auth=True):
    req = urllib.request.Request(url, headers={"Authorization": f"Token {token()}"} if auth else {})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def search(q, animated=False, max_faces=None, count=24):
    params = {"type": "models", "q": q, "downloadable": "true", "count": count, "sort_by": "-likeCount"}
    if animated:
        params["animated"] = "true"
    if max_faces:
        params["max_face_count"] = max_faces
    res = api("https://api.sketchfab.com/v3/search?" + urllib.parse.urlencode(params), auth=False)
    for m in res.get("results", []):
        lic = (m.get("license") or {}).get("label", "?")
        print(f"{m['uid']}  faces={m.get('faceCount')}  anim={m.get('animationCount')}  [{lic}]  {m['name']}  by {m['user']['username']}")


def get(uid, folder):
    info = api(f"https://api.sketchfab.com/v3/models/{uid}", auth=False)
    dl = api(f"https://api.sketchfab.com/v3/models/{uid}/download")
    out = os.path.join(ASSETS, folder)
    os.makedirs(out, exist_ok=True)
    if "glb" in dl:
        with urllib.request.urlopen(dl["glb"]["url"], timeout=300) as r:
            open(os.path.join(out, "model.glb"), "wb").write(r.read())
    else:                                                     # gltf zip
        with urllib.request.urlopen(dl["gltf"]["url"], timeout=300) as r:
            zipfile.ZipFile(io.BytesIO(r.read())).extractall(out)
    lic = (info.get("license") or {}).get("label", "?")
    with open(os.path.join(out, "CREDITS.txt"), "w") as fh:
        fh.write(f"\"{info['name']}\" by {info['user']['username']} ({info['viewerUrl']}), licensed {lic}.\n")
    print("SAVED", out, "|", lic)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "search":
        mf = int(a[a.index("--max-faces") + 1]) if "--max-faces" in a else None
        search(a[1], animated="--animated" in a, max_faces=mf)
    elif a and a[0] == "get":
        get(a[1], a[2])
    else:
        print(__doc__)
