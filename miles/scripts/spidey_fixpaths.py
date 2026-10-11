import bpy, os
OLD = "/home/lovestaco/pers/lr_demo/"
NEW = "/mnt/spidey/lr_demo/"
colls = [bpy.data.images, bpy.data.sounds, bpy.data.movieclips, bpy.data.fonts, bpy.data.libraries, bpy.data.cache_files]
fixed = 0
for c in colls:
    for d in c:
        fp = getattr(d, "filepath", "")
        if not fp or fp.startswith("<") or getattr(d, "packed_file", None):
            continue
        a = bpy.path.abspath(fp)
        if a.startswith(OLD):
            d.filepath = NEW + a[len(OLD):]
            fixed += 1
bpy.ops.wm.save_mainfile(relative_remap=True)       # keep paths valid for the file's own location
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_mainfile()
rel = abs_ = miss = 0
for c in colls:
    for d in c:
        fp = getattr(d, "filepath", "")
        if not fp or fp.startswith("<") or getattr(d, "packed_file", None):
            continue
        if fp.startswith("//"): rel += 1
        else: abs_ += 1
        if not os.path.exists(bpy.path.abspath(fp)): miss += 1; print("FIXPATHS MISSING", fp)
print(f"FIXPATHS {os.path.basename(bpy.data.filepath)}: remapped {fixed}, relative {rel}, absolute {abs_}, missing {miss}")
