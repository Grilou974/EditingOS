# Fond : plans utiles des deux vidéos (manifs, rayons, port, Stéphane Hayot) — sans journalistes face caméra ni cartons, recadrés 9:16 AU-DESSUS
# des sous-titres / bandeaux incrustés. Deux versions : nette et floutée. + contours des îles (france-geojson) → assets/geo.js
# python -I bg.py
import json, subprocess
A, V = "src/antilles.mp4", "src/vindemia.mp4"
CLIPS = [(A, 88.4, 2.7), (A, 94.9, 2.4), (A, 192.0, 3.4), (A, 196.0, 4.5), (A, 45.2, 2.6), (A, 9.2, 2.5), (A, 6.3, 2.5), (A, 15.0, 3.6), (V, 3.5, 3.0), (V, 6.5, 3.5),
         (V, 76.8, 1.7), (V, 78.6, 1.4), (V, 82.9, 2.3), (V, 85.3, 2.1), (A, 240.3, 3.5), (A, 244.0, 2.5), (V, 88.6, 2.1), (V, 90.8, 2.4), (A, 133.3, 3.8), (A, 137.5, 3.8),
         (V, 34.8, 2.7), (V, 37.6, 3.4), (A, 201.0, 3.0), (A, 164.7, 2.0), (V, 10.0, 4.0), (A, 297.4, 2.8), (V, 41.8, 2.8), (A, 39.0, 3.0), (A, 129.0, 2.0), (V, 69.2, 2.2), (A, 141.0, 3.0)]
print("durée fond", round(sum(c[2] for c in CLIPS), 1), "s")
inp, fl = [], []
for i, (f, a, d) in enumerate(CLIPS):
    inp += ["-ss", str(a), "-t", str(d), "-i", f]
    # on garde le haut de l'image : sous-titres HuffPost vers y≈985/1080, bandeau Vindémia vers y≈640/720
    crop = "crop=495:880:712:0" if f == A else "crop=349:620:465:0"
    fl.append(f"[{i}:v]fps=30,{crop},scale=1080:1920:flags=lanczos,setsar=1,setpts=PTS-STARTPTS[v{i}]")
fl.append("".join(f"[v{i}]" for i in range(len(CLIPS))) + f"concat=n={len(CLIPS)}:v=1:a=0,split[n][f]")
fl.append("[f]scale=270:480,gblur=sigma=9,scale=1080:1920,eq=brightness=-0.06:saturation=1.05[fo]")
open("fz/bg.txt", "w").write(";".join(fl))
subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", *inp, "-/filter_complex", "fz/bg.txt",
                "-map", "[n]", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-g", "30", "assets/bg-net.mp4",
                "-map", "[fo]", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-g", "30", "assets/bg-flou.mp4"], check=True)

def anneaux(f, n=2):
    g = json.load(open(f, encoding="utf8"))["geometry"]
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    rings = sorted((p[0] for p in polys), key=len, reverse=True)[:n]
    return rings
out = {}
for nom, f, n in [("reunion", "assets/geo/974-la-reunion.json", 1), ("martinique", "assets/geo/972-martinique.json", 1), ("guadeloupe", "assets/geo/971-guadeloupe.json", 2)]:
    R = anneaux(f, n); xs = [p[0] for r in R for p in r]; ys = [p[1] for r in R for p in r]
    cx, cy, k = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(max(xs) - min(xs), max(ys) - min(ys))
    st = lambda r: max(1, len(r) // 160)
    out[nom] = [[[round((p[0] - cx) / k, 4), round((p[1] - cy) / k, 4)] for p in r[::st(r)]] for r in R]
open("assets/geo.js", "w").write("export const ILES = " + json.dumps(out, separators=(",", ":")) + ";\n")
print("ok")
