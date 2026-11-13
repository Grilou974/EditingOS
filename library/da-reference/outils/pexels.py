# Recherche de vidéos Pexels (licence Pexels : libre, sans attribution obligatoire) sans clé d'API, via la page de recherche.
# python -I pexels.py "requête" dossier [n]  → dossier/pexels-<id>.mp4 (version HD verticale si possible) + planche dossier/_planche-<requête>.jpg
import os, re, subprocess, sys, urllib.parse, urllib.request
from PIL import Image, ImageDraw
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
q, D = sys.argv[1], sys.argv[2]; N = int(sys.argv[3]) if len(sys.argv) > 3 else 8
os.makedirs(D, exist_ok=True)
curl = lambda u, o=None: subprocess.run(["curl", "-sL", "-A", UA["User-Agent"], "-m", "120", u] + (["-o", o] if o else []), capture_output=True).stdout
h = curl("https://www.pexels.com/search/videos/" + urllib.parse.quote(q) + "/?orientation=portrait").decode("utf8", "ignore").replace(chr(92) + "u002F", "/")
if "video-files" not in h: print("bloqué (Cloudflare) ou rien trouvé"); sys.exit(1)
files = re.findall(r"https://videos\.pexels\.com/video-files/(\d+)/[^\"' ]+?\.mp4", h)
ids = list(dict.fromkeys(files))[:N]
T = []
for i in ids:
    c = sorted(set(re.findall(rf"https://videos\.pexels\.com/video-files/{i}/{i}-(?:hd|sd|uhd)_(\d+)_(\d+)_\d+fps\.mp4", h)), key=lambda x: int(x[0]))
    vert = [x for x in c if int(x[1]) > int(x[0])]
    choix = next((x for x in vert if 700 <= int(x[0]) <= 1100), (vert or c or [None])[-1])
    if not choix: continue
    url = next(u for u in re.findall(rf"https://videos\.pexels\.com/video-files/{i}/{i}-[a-z]+_{choix[0]}_{choix[1]}_\d+fps\.mp4", h))
    out = f"{D}/pexels-{i}.mp4"
    if not os.path.exists(out):
        curl(url, f"{D}/_brut.mp4")   # souvent l'UHD seul est listé : on réduit à 1080 de haut max, sans le son
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", f"{D}/_brut.mp4", "-t", "20", "-an", "-vf", "scale=-2:'min(1920,ih)'", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", out])
        os.remove(f"{D}/_brut.mp4")
    j = f"{D}/_t{i}.jpg"; subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-ss", "1", "-i", out, "-frames:v", "1", "-vf", "scale=200:-2", j])
    try: T.append((i, Image.open(j).convert("RGB")))
    except Exception: pass
    print(i, choix, url.split("/")[-1])
if T:
    P = Image.new("RGB", (len(T) * 204, max(t.height for _, t in T) + 20), "white"); d = ImageDraw.Draw(P)
    for k, (i, t) in enumerate(T): P.paste(t, (k * 204, 0)); d.text((k * 204 + 3, t.height + 3), str(i), fill="black")
    P.save(f"{D}/_planche-{q.replace(' ', '-')}.jpg")
