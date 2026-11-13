# Moteur de la DA de référence TV cat (modèle : montages/gbh, validé le 05/11/2026). Importé par le gen.py de chaque vidéo.
# Temps = voix finale (words.json). Titre centré x=540 ; contenu centré x=C=515 ; largeur ≤ 760 ; y entre 250 et 1480.
import json, os, re, unicodedata
C = 515
SND = {"pop": ["plop", "pop-explainer", "pop-bulle", "pop-sec", "plop", "pop-dur"], "cadre": ["coup-sec", "whoosh-air", "swoosh-court", "coup-sec", "sweep-a"],
       "date": ["whoosh-grave", "swoosh-court", "whoosh-grave", "sweep-a"], "tampon": ["tampon-bois"], "photo": ["declic-photo"], "hit": ["basse-hit"], "check": ["clic-check", "clic-souris"],
       "boing": ["boing-montee"], "brille": ["scintillement"], "ding": ["ding"], "trait": ["griffonnage"], "slide": ["tech-slide"]}
VOL = {"pop": .6, "cadre": .5, "date": .5, "tampon": .6, "photo": .5, "hit": .5, "check": .5, "boing": .4, "brille": .3, "ding": .35, "trait": .4, "slide": .4}
H, H1, JS, SFX, BLUR, VIDS, CATL = [], [], [], [], [], [], []
LFS = set(); _k = {}; _n = [0]
def _norm(t): return "".join(c for c in unicodedata.normalize("NFD", t.lower()) if c.isalnum() and not unicodedata.combining(c))
W = json.load(open("words.json", encoding="utf8"))
AVANCE = 0.12   # 06/11 (« oyca ») : silence avant le 1er mot, sinon le décodeur AAC et les lecteurs mangent la première consonne. Reprise dans mix_ref.py.
W = [[a + AVANCE, b + AVANCE, t] for a, b, t in W]
LEN = round(sum(b - a for a, b in json.load(open("segments.json"))) + AVANCE, 2)
def _eg(m, t):   # la transcription écrit parfois 6ml pour 6 ml, ou 3 pour trois
    return m == t or (m.isdigit() and t.startswith(m)) or {"trois": "3", "deux": "2"}.get(m) == t
def w(mot, apres=0.0, fin=False):
    # temps du mot (ou de la suite de mots) après l'instant donné : les timings suivent la voix
    m = [_norm(x) for x in mot.split()]
    for i in range(len(W) - len(m) + 1):
        if W[i][0] >= apres and all(_eg(m[j], _norm(W[i + j][2])) for j in range(len(m))): return W[i + len(m) - 1][1] if fin else W[i][0]
    raise SystemExit(f"mot introuvable : {mot} après {apres}")
def son(t, kind="pop"):
    l = SND[kind]; i = _k.get(kind, 0); _k[kind] = i + 1; SFX.append((round(t, 2), l[i % len(l)], VOL[kind]))
def el(t0, t1, html, cx, cy, kind="pop", anim="pop", s=1.0, layer=None, flou=True, id=None):
    _n[0] += 1; i = id or f"e{_n[0]}"; t0, t1 = round(t0, 2), round(t1, 2)
    if t1 - t0 < 0.3: raise SystemExit(f"élément trop court ({t0} → {t1}) : {html[:60]}")
    (H if layer is None else layer).append(f'<div class="ic" style="left:{cx}px;top:{cy}px;transform:translate(-50%,-50%) scale({s})"><div id="{i}" class="it">{html}</div></div>')
    if anim == "pop": JS.append(f'tl.fromTo("#{i}", {{opacity:0, scale:0.4}}, {{opacity:1, scale:1, duration:0.26, ease:"back.out(2.2)", immediateRender:false}}, {t0});')
    elif anim == "net": JS.append(f'tl.fromTo("#{i}", {{opacity:0, scale:0.92}}, {{opacity:1, scale:1, duration:0.14, ease:"power2.out", immediateRender:false}}, {t0});')
    elif anim == "tampon": JS.append(f'tl.fromTo("#{i}", {{opacity:0, scale:2.2, rotation:-8}}, {{opacity:1, scale:1, rotation:-8, duration:0.2, ease:"power3.in", immediateRender:false}}, {t0});')
    elif anim == "glisse": JS.append(f'tl.fromTo("#{i}", {{opacity:0, x:-80}}, {{opacity:1, x:0, duration:0.26, ease:"power3.out", immediateRender:false}}, {t0});')
    JS.append(f'tl.to("#{i}", {{opacity:0, scale:0.9, duration:0.14, ease:"power2.in"}}, {round(t1 - 0.14, 2)});')
    if kind: son(t0 + (0.18 if anim == "tampon" else 0), kind)
    if flou: BLUR.append((t0, t1))
    return i
def lab(t0, t1, txt, cx=C, cy=330, c="", fs=48, **k): return el(t0, t1, f'<div class="lab {c}" style="font-size:{fs}px">{txt}</div>', cx, cy, **k)
def date(t0, t1, txt, cy=330, sub="", s=0.7, cx=C, flou=True):
    sm = f"<small>{sub}</small>" if sub else ""
    return el(t0, t1, f'<div class="carte">{sm}<b>{txt}</b></div>', cx, cy, kind="date", s=s, flou=flou)
def tampon(t0, t1, txt, cy=360, fs=60, cx=C, flou=True): return el(t0, t1, f'<div class="tampon" style="font-size:{fs}px">{txt}</div>', cx, cy, kind="tampon", anim="tampon", flou=flou)
def img1(t0, t1, img, wd, cy, cx=C, kind="cadre", leg=None):
    lg = f'<div class="leg">{leg}</div>' if leg else ""
    return el(t0, t1, f'<img class="img1" src="assets/img/{img}" style="width:{wd}px">{lg}', cx, cy, kind=kind, anim="net", layer=H1)
def logo(t0, t1, img, wd, cy, cx=C, kind="cadre", fond="#fff"): return el(t0, t1, f'<div class="plaque" style="background:{fond}"><img src="assets/img/{img}" style="width:{wd}px"></div>', cx, cy, kind=kind)
def chip(t0, t1, txt, cy, cx=C, ok=False, kind="check", anim="glisse"):
    return el(t0, t1, '<div class="chip">' + ('<span class="ok">✔</span>' if ok else "") + txt + "</div>", cx, cy, kind=kind, anim=anim)
def rapport(t0, t1, pet, gros, cy, cx=C, fs=44): return el(t0, t1, f'<div class="rapport"><small>{pet}</small><b style="font-size:{fs}px">{gros}</b></div>', cx, cy, kind="cadre")
def mini(t0, t1, txt, cy, cx=C): return el(t0, t1, f'<div class="mini">{txt}</div>', cx, cy, kind=None)
def compteur(t0, t1, de, a, suf, cy, cx=C, fs=150, kind="hit", pre=""):
    _n[0] += 1; n = f"n{_n[0]}"
    el(t0, t1, f'<div class="gros rouge" style="font-size:{fs}px">{pre}<span class="{n}">{de}</span>{suf}</div>', cx, cy, kind=kind)
    JS.append(f'(() => {{ const o = {{v:{de}}}, e = document.querySelector(".{n}"); tl.fromTo(o, {{v:{de}}}, {{v:{a}, duration:0.7, ease:"power2.out", immediateRender:false, onUpdate:() => {{ e.textContent = Math.round(o.v).toLocaleString("fr-FR"); }}}}, {round(t0, 2)}); }})();')
def lf(t0, t1, name, cx, cy, size=300, kind="pop", flou=True):
    LFS.add(name); i = el(t0, t1, f'<div class="lfa" style="width:{size}px;height:{size}px"></div>', cx, cy, kind=kind, flou=flou); d = round(t1 - t0, 2)
    JS.append(f'(() => {{ const a = lottie.loadAnimation({{container: document.querySelector("#{i} .lfa"), renderer:"svg", loop:false, autoplay:false, animationData: JSON.parse(JSON.stringify(LF["{name}"]))}}), o = {{t:0}}; '
              f'tl.fromTo(o, {{t:0}}, {{t:{d}, duration:{d}, ease:"none", immediateRender:false, onUpdate:() => a.goToAndStop((o.t * a.frameRate) % Math.max(a.totalFrames - 1, 1), true)}}, {round(t0, 2)}); }})();')
def video(t0, t1, src, cx, cy, wd, hg, kind="cadre"):
    _n[0] += 1; i = f"v{_n[0]}"; t0, t1 = round(t0, 2), round(t1, 2)
    VIDS.append(f'<video id="{i}" class="clip cadrev" src="assets/clips/{src}" muted playsinline data-start="{t0}" data-duration="{round(t1 - t0, 2)}" data-track-index="{20 + len(VIDS)}" style="left:{cx - wd // 2}px;top:{cy - hg // 2}px;width:{wd}px;height:{hg}px"></video>')
    JS.append(f'tl.fromTo("#{i}", {{opacity:0, scale:0.8}}, {{opacity:1, scale:1, duration:0.26, ease:"back.out(1.8)", immediateRender:false}}, {t0});'); JS.append(f'tl.to("#{i}", {{opacity:0, duration:0.14}}, {round(t1 - 0.14, 2)});')
    if kind: son(t0, kind)
    BLUR.append((t0, t1))
def titre(t1, txt):
    el(0.0, t1, f'<div class="halo"></div><div class="titre">{txt}</div>', 540, 530, kind=None, anim=None, flou=False, id="ttl"); H.append('<style>#ttl{opacity:1}</style>')
def tw(sel, de, vers, t, d=0.4, ease="power3.out"): JS.append(f'tl.fromTo("{sel}", {{{de}}}, {{{vers}, duration:{d}, ease:"{ease}", immediateRender:false}}, {round(t, 2)});')
def fin(sel, t): JS.append(f'tl.to("{sel}", {{opacity:0, duration:0.14}}, {round(t - 0.14, 2)});')
def rond(t0, t1, txt, x, y, d, c="rouge", s0=0.4):
    _n[0] += 1; i = f"r{_n[0]}"; H.append(f'<div id="{i}" class="rond {c}" style="left:{x - d // 2}px;top:{y - d // 2}px;width:{d}px;height:{d}px;font-size:{max(26, d // 5)}px">{txt}</div>')
    tw(f"#{i}", f"opacity:0, scale:{s0}", "opacity:1, scale:1", t0, 0.34, "back.out(1.8)"); fin(f"#{i}", t1); BLUR.append((t0, t1)); return i
def expressions(L):
    # L = [(t, pose ou None, "G"/"P")] : une expression toutes les ≈ 2 s ; pas de chat sur les gros plans
    CATL[:] = L; T_ = {"G": 1.05, "P": 0.68}
    for j, (t, p, g) in enumerate(L):
        t = round(t, 2)
        if j == 0:
            JS.append(f'tl.fromTo("#cat", {{x:-90, y:60, scale:0.96, rotation:-3}}, {{x:0, y:0, scale:{T_[g]}, rotation:0, duration:0.15, ease:"power3.out"}}, 0);'); continue
        JS.append(f'tl.set("#cat img", {{opacity:0}}, {t});')
        if p:
            prev = L[j - 1][2]
            JS.append(f'tl.set("#cat .{p}", {{opacity:1}}, {t});')
            JS.append(f'tl.fromTo("#cat", {{scale:{T_[g] * (0.97 if prev == g else 1.0):.3f}, y:{60 if prev is None else 0}}}, {{scale:{T_[g]}, y:0, duration:{0.12 if prev == g else 0.2}, ease:"back.out(2)", immediateRender:false}}, {t});')
def finir(nom, like=1.22):
    # CTA violet : voix-cta.wav démarre 0,10 s après la fin de la voix ; le texte tombe pile sur « like » (like = instant du mot dans voix-cta.wav)
    # 13/11 : la fin suit la VRAIE durée de voix-cta.wav (fz/cta-duree.txt), sinon « abonne-toi à TV4 » était coupé
    dur = float(open("fz/cta-duree.txt").read()) if os.path.exists("fz/cta-duree.txt") else 2.70
    CTAF = round(LEN + 0.10, 2); LIKE = round(CTAF + like, 2); END = round(CTAF + dur + 0.75, 2); open("fin.txt", "w").write(str(END))
    B = sorted(BLUR); fu = []
    for a, b in B:
        if fu and a - fu[-1][1] < 0.6: fu[-1][1] = max(fu[-1][1], b)
        else: fu.append([a, b])
    for a, b in fu:
        JS.append(f'tl.to("#net", {{opacity:0, duration:0.2, ease:"power1.inOut"}}, {round(max(a - 0.05, 0), 2)});')
        if b < CTAF - 0.1: JS.append(f'tl.to("#net", {{opacity:1, duration:0.24, ease:"power1.inOut"}}, {round(b, 2)});')
    JS.append(f'tl.set("#cat img", {{opacity:0}}, {CTAF}); tl.set("#cta", {{opacity:1}}, {CTAF});')
    JS.append(f'tl.fromTo("#cta-cat", {{opacity:0, scale:0.7, y:90}}, {{opacity:1, scale:1, y:0, duration:0.4, ease:"back.out(1.8)", immediateRender:false}}, {CTAF});')
    JS.append(f'tl.fromTo(".ctat", {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.32, ease:"back.out(2.4)", immediateRender:false}}, {LIKE});')
    SFX.extend([(CTAF, "scintillement", 0.4), (LIKE, "ding", 0.3)])
    nb = lambda h: h.replace("« ", "«&nbsp;").replace(" »", "&nbsp;»").replace(" ?", "&nbsp;?").replace(" !", "&nbsp;!")
    Hh, H1h = [nb(h) for h in H], [nb(h) for h in H1]
    S = sorted(SFX); o = []
    for x in S:
        if not o or x[0] - o[-1][0] >= 0.12: o.append(x)
    json.dump(o, open("sfx.json", "w"))
    LFJS = ",".join(f'"{n}": ' + open(f"assets/lottie/{n}.json", encoding="utf8").read() for n in sorted(LFS))
    PO = sorted({p for _, p, _ in CATL if p}); cats = "".join(f'<img class="{p}" src="assets/chat/{p}.png"' + (' style="opacity:1"' if p == CATL[0][1] else "") + ">" for p in PO)
    css = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "da_ref.css.txt"), encoding="utf8").read()
    nl = chr(10)
    html = f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js"></script>
    <style>{css}</style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920">
      <video id="flou" class="clip bg" src="assets/bg-flou.mp4" muted playsinline data-start="0" data-duration="{END}" data-track-index="0"></video>
      <video id="net" class="clip bg" src="assets/bg-net.mp4" muted playsinline data-start="0" data-duration="{END}" data-track-index="1"></video>
      <div id="c1" class="clip couche" data-start="0" data-duration="{END}" data-track-index="2" data-layout-allow-overflow>
{nl.join("        " + h for h in H1h)}
      </div>
{nl.join("      " + v for v in VIDS)}
      <div id="cat" class="clip" data-start="0" data-duration="{END}" data-track-index="3" data-layout-allow-overflow>{cats}</div>
      <div id="fx" class="clip couche" data-start="0" data-duration="{END}" data-track-index="4" data-layout-allow-overflow>
{nl.join("        " + h for h in Hh)}
      </div>
      <div id="cta" class="clip" data-start="0" data-duration="{END}" data-track-index="9"><div class="ctat">Like et<br><i>abonne-toi</i> <u>&lt;3</u></div><div id="cta-cat"><img src="assets/chat/c04.png"></div></div>
    </div>
    <script>const LF = {{{LFJS}}};</script>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
{nl.join("      " + j for j in JS)}
      tl.set({{}}, {{}}, {END});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    open("index.html", "w", encoding="utf8").write(html)
    print(f"{nom} : fin {END} s, {len(H) + len(H1)} éléments, {len(o)} sons, net : {[(round(fu[i][1], 2), round(fu[i + 1][0], 2)) for i in range(len(fu) - 1)]}")
