# Récupère les animations GRATUITES de LottieFiles (Lottie Simple License, usage commercial libre) par thème,
# extrait le JSON de chaque .lottie et fabrique une planche d'aperçu HyperFrames pour choisir.
# Depuis le dossier du projet : python -I ../_outils/lottiefiles.py theme1 theme2 …  → src/lf/<theme>_<n>.json + fz/lfprev/index.html
import io, json, os, re, sys, urllib.request, zipfile
UA = {"User-Agent": "Mozilla/5.0"}
os.makedirs("src/lf", exist_ok=True); os.makedirs("fz/lfprev", exist_ok=True)
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
cells = []
for th in sys.argv[1:]:
    try: page = get(f"https://lottiefiles.com/free-animations/{th}").decode("utf8", "ignore")
    except Exception as e: print(th, "page KO", e); continue
    urls = list(dict.fromkeys(re.findall(r"https://assets-v2\.lottiefiles\.com/a/[^\"'\s\\)]*\.lottie", page)))[:12]
    for n, u in enumerate(urls):
        out = f"src/lf/{th}_{n}.json"
        if not os.path.exists(out):
            try:
                z = zipfile.ZipFile(io.BytesIO(get(u)))
                anim = [f for f in z.namelist() if f.startswith("animations/") and f.endswith(".json")][0]
                d = json.loads(z.read(anim))
                for a in d.get("assets", []):   # images embarquées dans le .lottie → data URI
                    if a.get("p") and not str(a["p"]).startswith("data:"):
                        cand = [f for f in z.namelist() if f.endswith("/" + a["p"]) or f == a["p"]]
                        if cand:
                            ext = a["p"].rsplit(".", 1)[-1]; import base64
                            a["u"] = ""; a["p"] = f"data:image/{ext};base64," + base64.b64encode(z.read(cand[0])).decode(); a["e"] = 1
                json.dump(d, open(out, "w"))
                open(out + ".src", "w").write(u)
            except Exception as e: print(u, "KO", e); continue
        cells.append(f"{th}_{n}")
    print(th, len(urls))
cols, S = 6, 260
html = "".join(f'<div class="c" style="left:{(k % cols) * (S + 10)}px;top:{(k // cols) * (S + 40)}px"><div class="lot" data-src="../../src/lf/{c}.json"></div><p>{c}</p></div>' for k, c in enumerate(cells))
H = ((len(cells) + cols - 1) // cols) * (S + 40)
open("fz/lfprev/index.html", "w", encoding="utf8").write(f"""<!doctype html><html><head><meta charset="UTF-8">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js"></script>
<style>html,body{{margin:0;width:{cols * (S + 10)}px;height:{H}px;background:#556}} .c{{position:absolute;width:{S}px}} .lot{{width:{S}px;height:{S}px;background:#778}} p{{margin:4px;color:#fff;font:16px sans-serif}}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="3" data-width="{cols * (S + 10)}" data-height="{H}">{html}</div>
<script>window.__hfLottie=[];document.querySelectorAll(".lot").forEach(d=>window.__hfLottie.push(lottie.loadAnimation({{container:d,renderer:"svg",loop:true,autoplay:false,path:d.dataset.src}})));
window.__timelines={{}};const tl=gsap.timeline({{paused:true}});tl.set({{}},{{}},3);window.__timelines["main"]=tl;</script></body></html>""")
print(len(cells), "animations")
