# Fonds LIBRES DE DROITS (13/11) : photos Wikimedia Commons de Marine Le Pen (CC0 / domaine public, zoom lent) puis vidéos Pexels
# (entretiens, CV, gens, rues de Paris, drapeau). → assets/bg-net.mp4 et bg-flou.mp4. python -I bg.py
import json, subprocess
END = float(open("fin.txt").read()) + 0.5
P, C = "src/pexels/pexels-", "src/commons/"
# (source, durée, départ dans la source, position verticale du cadrage pour les photos)
SEQ = [(C + "Marine_Le_Pen_2025_(cropped).jpg", 3.2, 0, .35), (C + "Marine_Le_Pen_in_2022.jpg", 3.0, 0, .35), (C + "Marine_Le_Pen_VIVA_24_(2).jpg", 3.0, 0, .3),
       (P + "15743404.mp4", 2.6, 1, 0), (P + "5438980.mp4", 2.6, 1, 0), (P + "5438883.mp4", 2.6, 1, 0), (P + "7247823.mp4", 2.6, 1, 0), (P + "6781990.mp4", 2.6, 1, 0),
       (P + "5438898.mp4", 2.6, 1, 0), (P + "5439073.mp4", 2.6, 1, 0), (P + "6616732.mp4", 2.6, 1, 0), (P + "3256848.mp4", 2.6, 1, 0), (P + "5896048.mp4", 2.6, 1, 0),
       (P + "5438949.mp4", 2.6, 1, 0), (P + "5439077.mp4", 2.6, 1, 0), (P + "6770049.mp4", 2.6, 1, 0), (P + "20494368.mp4", 2.6, 1, 0), (P + "9943584.mp4", 2.6, 1, 0),
       (P + "19368466.mp4", 2.6, 1, 0), (P + "20683467.mp4", 2.6, 1, 0), (P + "26834839.mp4", 2.6, 1, 0), (P + "15537623.mp4", 2.6, 1, 0), (P + "8350651.mp4", 2.6, 1, 0)]
L, t, k = [], 0, 0
while t < END:
    s = SEQ[k % len(SEQ)]; L.append(s); t += s[1]; k += 1
inp, fl = [], []
for j, (f, d, a, py) in enumerate(L):
    if f.endswith(".jpg"):
        inp += ["-loop", "1", "-framerate", "30", "-t", str(d), "-i", f]
        fl.append(f"[{j}:v]scale=1300:-2,crop=1080:1920:(iw-1080)/2:max(0\\,min(ih-1920\\,ih*{py}-960)),zoompan=z='1+0.0009*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,setsar=1,setpts=PTS-STARTPTS[v{j}]"
                  if False else f"[{j}:v]scale='if(gt(a,1080/1920),-2,1300)':'if(gt(a,1080/1920),2300,-2)',crop=1080:1920:(iw-1080)/2:'max(0,min(ih-1920,ih*{py}-960))',zoompan=z='1+0.0009*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,setsar=1,setpts=PTS-STARTPTS[v{j}]")
    else:
        inp += ["-ss", str(a), "-t", str(d), "-i", f]
        fl.append(f"[{j}:v]fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,setpts=PTS-STARTPTS[v{j}]")
fl.append("".join(f"[v{j}]" for j in range(len(L))) + f"concat=n={len(L)}:v=1:a=0,split[n][f]")
fl.append("[f]scale=270:480,gblur=sigma=9,scale=1080:1920,eq=brightness=-0.06:saturation=1.05[fo]")
open("fz/bg.txt", "w").write(";".join(fl))
subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", *inp, "-/filter_complex", "fz/bg.txt",
                "-map", "[n]", "-t", str(END), "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p", "-g", "30", "assets/bg-net.mp4",
                "-map", "[fo]", "-t", str(END), "-c:v", "libx264", "-crf", "22", "-pix_fmt", "yuv420p", "-g", "30", "assets/bg-flou.mp4"], check=True)
open("CREDITS.md", "w", encoding="utf8").write("""# Crédits des fonds
- Photos de Marine Le Pen, Wikimedia Commons : « Marine Le Pen 2025 (cropped) » (CC0, Vox España), « Marine Le Pen in 2022 » (domaine public, VOX España), « Marine Le Pen VIVA 24 (2) » (CC0, Vox España).
- Vidéos Pexels (licence Pexels, libre, sans attribution obligatoire) : """ + ", ".join(sorted({f.split('-')[-1][:-4] for f, *_ in SEQ if 'pexels' in f})) + "\n")
print("fonds ok", len(L), "plans")
