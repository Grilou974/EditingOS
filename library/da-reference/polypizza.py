# Cherche des modèles 3D sur Poly Pizza (licence affichée par modèle : CC0 ou CC-BY à créditer), récupère le .glb + l'aperçu.
# Depuis le projet : python -I ../_outils/polypizza.py "shopping cart" "cargo ship" …  → src/poly/<theme>_<n>.glb + src/poly/index.json + fz/poly.jpg
import io, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
from PIL import Image, ImageDraw
UA = {"User-Agent": "Mozilla/5.0"}
os.makedirs("src/poly", exist_ok=True)
def get(u):
    for essai in range(5):
        time.sleep(1.5)
        try: return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(20)
    raise RuntimeError("429 " + u)
idx = json.load(open("src/poly/index.json", encoding="utf8")) if os.path.exists("src/poly/index.json") else {}
cells = []
for q in sys.argv[1:]:
    page = get("https://poly.pizza/search/" + urllib.parse.quote(q)).decode("utf8", "ignore")
    ids = list(dict.fromkeys(re.findall(r"/m/([A-Za-z0-9_-]{8,})", page)))[:8]
    for n, i in enumerate(ids):
        nom = f"{q.replace(' ', '-')}_{n}"
        try:
            t = get("https://poly.pizza/m/" + i).decode("utf8", "ignore")
            glb = re.search(r"https://static\.poly\.pizza/[0-9a-f-]+\.glb", t).group(0)
            lic = (re.search(r"CC[- ]?BY[- ]?[\d.]*|CC0|Public Domain", t, re.I) or [""])[0]
            titre = re.search(r"<title[^>]*>(.*?)</title>", t, re.S).group(1).strip()[:70]
            img = re.search(r'https://static\.poly\.pizza/[0-9a-f-]+\.(?:webp|png|jpg)', t)
            if not os.path.exists(f"src/poly/{nom}.glb"): open(f"src/poly/{nom}.glb", "wb").write(get(glb))
            th = None
            if img:
                th = Image.open(io.BytesIO(get(img.group(0)))).convert("RGB")
            idx[nom] = {"id": i, "titre": titre, "licence": lic, "url": "https://poly.pizza/m/" + i, "glb": glb}
            cells.append((nom, lic, th))
        except Exception as e: print(nom, "KO", e)
    print(q, len(ids))
json.dump(idx, open("src/poly/index.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
T, cols = 200, 8
S = Image.new("RGB", (cols * T, ((len(cells) + cols - 1) // cols) * (T + 34)), (70, 70, 85)); d = ImageDraw.Draw(S)
for k, (n, l, th) in enumerate(cells):
    x, y = (k % cols) * T, (k // cols) * (T + 34)
    if th: th.thumbnail((T, T)); S.paste(th, (x, y))
    d.text((x + 2, y + T + 2), n[:30], fill="yellow"); d.text((x + 2, y + T + 16), l, fill="white")
S.save("fz/poly.jpg"); print(len(cells), "modèles")
