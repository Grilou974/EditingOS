# Télécharge une liste d'URL de vidéos Pexels (récupérées via le navigateur, la recherche étant protégée par Cloudflare),
# les réduit (≤ 1920 de haut, 15 s, sans son) et fait une planche. python -I dl_pexels.py urls.txt dossier etiquette
import os, subprocess, sys
from PIL import Image, ImageDraw
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
U = [l.strip() for l in open(sys.argv[1]) if l.strip()]; D = sys.argv[2]; tag = sys.argv[3]; os.makedirs(D, exist_ok=True)
T = []
for u in U:
    i = u.split("/")[4]; out = f"{D}/pexels-{i}.mp4"
    if not os.path.exists(out):
        subprocess.run(["curl", "-sL", "-A", UA, "-m", "180", "-o", f"{D}/_brut.mp4", u])
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", f"{D}/_brut.mp4", "-t", "15", "-an", "-vf", "scale=-2:'min(1920,ih)'", "-c:v", "libx264", "-crf", "21", "-pix_fmt", "yuv420p", out])
        if os.path.exists(f"{D}/_brut.mp4"): os.remove(f"{D}/_brut.mp4")
    j = f"{D}/_t{i}.jpg"; subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-ss", "2", "-i", out, "-frames:v", "1", "-vf", "scale=180:-2", j])
    try: T.append((i, Image.open(j).convert("RGB")))
    except Exception: print("échec", i)
if T:
    P = Image.new("RGB", (len(T) * 184, max(t.height for _, t in T) + 18), "white"); d = ImageDraw.Draw(P)
    for k, (i, t) in enumerate(T): P.paste(t, (k * 184, 0)); d.text((k * 184 + 3, t.height + 3), i, fill="black")
    P.save(f"{D}/_planche-{tag}.jpg")
print(len(T), "clips")
