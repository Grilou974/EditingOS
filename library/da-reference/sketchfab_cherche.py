# Cherche des modèles téléchargeables sur Sketchfab (API publique), licences libres (CC0 / CC-BY), et fait une planche d'aperçu.
# Depuis le projet : python -I ../_outils/sketchfab_cherche.py "container ship" "supermarket" … → fz/skf.jpg + src/skf/index.json
import io, json, os, sys, urllib.parse, urllib.request
from PIL import Image, ImageDraw
UA = {"User-Agent": "Mozilla/5.0"}
os.makedirs("src/skf", exist_ok=True)
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
idx = {}; cells = []
for q in sys.argv[1:]:
    u = "https://api.sketchfab.com/v3/search?" + urllib.parse.urlencode({"type": "models", "q": q, "downloadable": "true", "count": 12, "sort_by": "-likeCount", "max_face_count": 400000})
    n = 0
    for r in json.loads(get(u))["results"]:
        lic = (r.get("license") or {}).get("label", "") if isinstance(r.get("license"), dict) else str(r.get("license"))
        if "Attribution" not in lic and "CC0" not in lic and "Public" not in lic: continue
        if "NonCommercial" in lic or "NoDerivatives" in lic: continue
        if n >= 8: break
        im = sorted(r["thumbnails"]["images"], key=lambda i: abs(i["width"] - 256))[0]["url"]
        nom = f"{q.replace(' ', '-')}_{n}"; n += 1
        idx[nom] = {"uid": r["uid"], "titre": r["name"], "licence": lic, "auteur": r["user"]["displayName"], "url": r["viewerUrl"], "faces": r.get("faceCount")}
        try: th = Image.open(io.BytesIO(get(im))).convert("RGB")
        except Exception: th = None
        cells.append((nom, lic, th))
    print(q, n)
json.dump(idx, open("src/skf/index.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
T, cols = 240, 8
S = Image.new("RGB", (cols * T, ((len(cells) + cols - 1) // cols) * (T // 2 + 96)), (70, 70, 85)); d = ImageDraw.Draw(S)
for k, (n, l, th) in enumerate(cells):
    x, y = (k % cols) * T, (k // cols) * (T // 2 + 96)
    if th: th = th.resize((T, T * th.height // th.width)); S.paste(th, (x, y))
    d.text((x + 2, y + T // 2 + 66), n[:34], fill="yellow"); d.text((x + 2, y + T // 2 + 80), l[:30], fill="white")
S.save("fz/skf.jpg"); print(len(cells))
