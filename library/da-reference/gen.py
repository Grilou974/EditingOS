# « GBH » — DA « cour de récré » + vraies explications 3D (assets/scene.js, Three.js). Temps = voix coupée (couper.py).
# Couche 1 : fond (2 vidéos GBH) net quand il parle seul, flouté dès qu'on explique ; gros Grilou ; titre blanc sur halo noir ; CTA noir.
# Couche 3D : îles extrudées, chaîne bateau → panier, balance, rachat, 7 magasins, factures entre sociétés.
# Couche 2 : logos, portraits, dates, tampons, Lottie (pas d'emojis), sons de sa compil. python -I gen.py ; python -I bg.py ; render ; python -I mix.py
import json, re
OFF = 0.24   # voix démarrée 0,17 s plus tôt (attaque de « Je suis ») : tous les temps ci-dessous sont décalés d'autant à la fin
CTA = 82.80
END = 85.2
C = 515      # centre visuel : zone de sécurité TikTok (icônes à droite), largeur max ≈ 760 px
SND = {"pop": ["plop", "pop-explainer", "pop-bulle", "pop-sec", "plop", "pop-dur"],
       "cadre": ["coup-sec", "whoosh-air", "swoosh-court", "coup-sec", "sweep-a"],
       "date": ["whoosh-grave", "swoosh-court", "whoosh-grave", "sweep-a"],
       "tampon": ["tampon-bois"], "photo": ["declic-photo"], "hit": ["basse-hit"], "check": ["clic-check", "clic-souris"],
       "boing": ["boing-montee"], "brille": ["scintillement"], "ding": ["ding"], "trait": ["griffonnage"], "slide": ["tech-slide"],
       "intro": ["whoosh-grave"]}
VOL = {"pop": 0.6, "cadre": 0.5, "date": 0.5, "tampon": 0.6, "photo": 0.5, "hit": 0.5, "check": 0.5, "boing": 0.4, "brille": 0.3, "ding": 0.35,
       "trait": 0.4, "slide": 0.4, "intro": 0.42}
# repères de la scène 3D (mots de la voix)
T = dict(iles=2.15, ile1=2.24, pct37=3.38, ile2=5.72, pct40=6.42, ile3=7.20, pct42=7.96, ilesFin=8.84,
         grands=11.64, controlent=12.72, grandsFin=15.0,
         carrefour=17.76, carrefourFin=20.05,
         chaine=20.10, c1=20.40, c2=21.06, c3=21.50, c4=22.0, c5=25.30, b1=23.92, b2=24.12, b3=24.34, chaineFin=26.55,
         poids=26.64, poidsT=27.40, poidsFin=29.15,
         rachat=29.90, rachete=32.80, jumbo=32.56, score=33.16, rachatEat=33.15, rachatFin=33.62,
         autorite=33.66, sept=36.18, autoriteFin=40.75,
         martin=41.0, martinFin=46.62,
         intra=46.74, groupe=48.36, facture=49.20, ouBen=52.66, intraFin=54.56,
         paient=54.86, paientFin=58.2)
H, H1, JS, SFX, LOT, BLUR, VIDS = [], [], [], [], [], [], []
ILES = json.loads(open("assets/geo.js").read().split("=", 1)[1].strip().rstrip(";"))
def ile_svg(nom, taille, coul="#2fb24c"):
    d = "".join("M" + " L".join(f"{(x + .5) * 100:.1f} {(.5 - y) * 100:.1f}" for x, y in r) + "Z" for r in ILES[nom])
    return f'<svg width="{taille}" height="{taille}" viewBox="0 0 100 100" style="display:block;filter:drop-shadow(0 8px 14px rgba(0,0,0,.45))"><path d="{d}" fill="{coul}" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>'
MAG = '<svg viewBox="0 0 64 56" width="74" height="65"><path d="M6 4h52l5 16a8 8 0 0 1-15 2 8 8 0 0 1-16 0 8 8 0 0 1-16 0 8 8 0 0 1-15-2z" fill="#fff"/><path d="M8 28v26h48V28" fill="none" stroke="#fff" stroke-width="5"/><rect x="24" y="34" width="16" height="20" fill="#fff"/></svg>'
_k = {}
def son(t, kind="pop"):
    l = SND[kind]; i = _k.get(kind, 0); _k[kind] = i + 1; SFX.append((round(t, 2), l[i % len(l)], VOL[kind]))
_n = [0]
def el(t0, t1, html, cx, cy, kind="pop", anim="pop", s=1.0, layer=None, flou=True, id=None):
    _n[0] += 1; i = id or f"e{_n[0]}"
    (H if layer is None else layer).append(f'<div class="ic" style="left:{cx}px;top:{cy}px;transform:translate(-50%,-50%) scale({s})"><div id="{i}" class="it">{html}</div></div>')
    if anim == "pop": JS.append(f'tl.fromTo("#{i}", {{opacity:0, scale:0.4}}, {{opacity:1, scale:1, duration:0.32, ease:"back.out(2.2)"}}, {t0});')
    elif anim == "net": JS.append(f'tl.fromTo("#{i}", {{opacity:0, scale:0.92}}, {{opacity:1, scale:1, duration:0.14, ease:"power2.out"}}, {t0});')
    elif anim == "tampon": JS.append(f'tl.fromTo("#{i}", {{opacity:0, scale:2.2, rotation:-8}}, {{opacity:1, scale:1, rotation:-8, duration:0.22, ease:"power3.in"}}, {t0});')
    elif anim == "glisse": JS.append(f'tl.fromTo("#{i}", {{opacity:0, x:-80}}, {{opacity:1, x:0, duration:0.3, ease:"power3.out"}}, {t0});')
    JS.append(f'tl.to("#{i}", {{opacity:0, scale:0.9, duration:0.18, ease:"power2.in"}}, {round(t1 - 0.18, 2)});')
    if kind: son(t0 + (0.18 if anim == "tampon" else 0), kind)
    if flou: BLUR.append((t0, t1))
    return i
LFS = set()
def lf(t0, t1, name, cx, cy, size=260, kind="pop", flou=True):   # animation LottieFiles jouée depuis son début
    LFS.add(name); i = el(t0, t1, f'<div class="lfa" style="width:{size}px;height:{size}px"></div>', cx, cy, kind=kind, flou=flou); d = round(t1 - t0, 2)
    JS.append(f'(() => {{ const a = lottie.loadAnimation({{container: document.querySelector("#{i} .lfa"), renderer:"svg", loop:false, autoplay:false, animationData: JSON.parse(JSON.stringify(LF["{name}"]))}}), o = {{t:0}}; '
              f'tl.fromTo(o, {{t:0}}, {{t:{d}, duration:{d}, ease:"none", immediateRender:false, onUpdate:() => a.goToAndStop((o.t * a.frameRate) % Math.max(a.totalFrames - 1, 1), true)}}, {t0}); }})();')
    return i
def lab(t0, t1, txt, cx, cy, c="", fs=48, **k): return el(t0, t1, f'<div class="lab {c}" style="font-size:{fs}px">{txt}</div>', cx, cy, **k)
def date(t0, t1, txt, cx, cy, sub="", s=1.0, flou=True):
    sm = f"<small>{sub}</small>" if sub else ""
    return el(t0, t1, f'<div class="carte">{sm}<b>{txt}</b></div>', cx, cy, kind="date", s=s, flou=flou)
def tampon(t0, t1, txt, cx, cy, fs=60): return el(t0, t1, f'<div class="tampon" style="font-size:{fs}px">{txt}</div>', cx, cy, kind="tampon", anim="tampon")
def img1(t0, t1, img, w, cy, cx=540, kind="cadre", leg=None, bord=""):
    lg = f'<div class="leg">{leg}</div>' if leg else ""
    return el(t0, t1, f'<img class="img1 {bord}" src="assets/img/{img}" style="width:{w}px">{lg}', cx, cy, kind=kind, anim="net", layer=H1)
def logo(t0, t1, img, w, cx, cy, kind="cadre"): return el(t0, t1, f'<div class="plaque"><img src="assets/img/{img}" style="width:{w}px"></div>', cx, cy, kind=kind)
def zone3d(t0, t1): BLUR.append((t0, t1))
def video(t0, t1, src, cx, cy, w, h, kind="cadre"):
    _n[0] += 1; i = f"v{_n[0]}"
    VIDS.append(f'<video id="{i}" class="clip cadrev" src="assets/clips/{src}" muted playsinline data-start="{t0}" data-duration="{round(t1 - t0, 2)}" data-track-index="{20 + len(VIDS)}" style="left:{cx - w // 2}px;top:{cy - h // 2}px;width:{w}px;height:{h}px"></video>')
    JS.append(f'tl.fromTo("#{i}", {{opacity:0, scale:0.8}}, {{opacity:1, scale:1, duration:0.3, ease:"back.out(1.8)"}}, {t0});'); JS.append(f'tl.to("#{i}", {{opacity:0, duration:0.18}}, {round(t1 - 0.18, 2)});')
    if kind: son(t0, kind)
    BLUR.append((t0, t1))

# ---- Grilou : présent seulement quand il parle sur le fond net ou quand l'illustration est petite. Gros plan = pas de chat (retour du 05/11).
# une expression toutes les ≈ 2 s, quand le propos change (05/11 : « deux fois moins, il y a un juste milieu »)
CAT = [(0.00, "c21", "G"), (1.40, "c31", "G"), (2.15, None, None),
       (8.84, "x-perplexe", "G"), (10.04, "x-enerve", "G"), (11.64, None, None),
       (37.20, "x-perplexe", "P"), (39.04, "x-surpris", "P"), (40.88, "c31", "P"), (42.5, None, None),
       (58.34, "c27", "G"), (59.72, "c25", "G"),
       (61.32, "c13", "P"), (63.20, "c19", "P"), (65.36, "c25", "P"), (67.68, "x-blase", "P"), (68.82, "x-rire", "P"),
       (69.68, "x-enerve", "P"), (71.46, "c28", "P"), (72.96, "x-gene", "P"), (74.26, "x-wtf", "P"),
       (75.24, "c30", "P"), (77.36, "c22", "P"), (79.22, "c27", "G"), (80.60, "c26", "G")]
POSES = sorted({p for _, p, _ in CAT if p})
TAILLE = {"G": 1.05, "P": 0.68}
for j, (t, p, g) in enumerate(CAT):
    if j == 0:
        JS.append(f'tl.fromTo("#cat", {{x:-90, y:60, scale:0.96, rotation:-3}}, {{x:0, y:0, scale:{TAILLE[g]}, rotation:0, duration:0.16, ease:"power3.out"}}, 0);')
        continue
    JS.append(f'tl.set("#cat img", {{opacity:0}}, {t});')
    if p:
        JS.append(f'tl.set("#cat .{p}", {{opacity:1}}, {t});')
        prev = CAT[j - 1][2]
        JS.append(f'tl.fromTo("#cat", {{scale:{TAILLE[g] * (0.97 if prev == g else 1.0):.3f}, y:{60 if prev is None else 0}}}, {{scale:{TAILLE[g]}, y:0, duration:{0.12 if prev == g else 0.2}, ease:"back.out(2)", immediateRender:false}}, {t});')

def tw(sel, de, vers, t, d=0.4, ease="power3.out"):
    JS.append(f'tl.fromTo("{sel}", {{{de}}}, {{{vers}, duration:{d}, ease:"{ease}", immediateRender:false}}, {t});')
def fin(sel, t): JS.append(f'tl.to("{sel}", {{opacity:0, duration:0.18}}, {round(t - 0.18, 2)});')

# ---- intro (whoosh avant la voix : il ne recouvre plus « Je suis »)
el(0.0, 2.15, '<div class="halo"></div><div class="titre">Pourquoi tout est si cher<br>dans les îles ?</div>', 540, 530, kind=None, anim="net", flou=False)

# A — les prix : barres 2D au-dessus, îles dessous, caddie 3D tout en bas (jamais dans les barres)
zone3d(T["iles"], T["ilesFin"])
lab(2.46, T["ilesFin"], "LES <i>COURSES</i> PAR RAPPORT À LA MÉTROPOLE", C, 262, fs=36, kind=None)
BASE, HG = 860, 300
for j, (nom, ile_, cx, p, tb, ta) in enumerate([("La Réunion", "reunion", C - 255, 37, 2.46, 3.56), ("Martinique", "martinique", C, 40, 5.72, 6.42), ("Guadeloupe", "guadeloupe", C + 255, 42, 7.2, 7.96)]):
    hr = round(HG * p / 100)
    H.append(f'<div id="bg{j}" class="barre gris" style="left:{cx - 70}px;top:{BASE - HG}px;height:{HG}px"></div><div id="br{j}" class="barre rouge" style="left:{cx - 70}px;top:{BASE - HG - hr}px;height:{hr}px"></div>')
    H.append(f'<div id="bp{j}" class="pct" style="left:{cx - 100}px;top:{BASE - HG - hr - 74}px">+{p} %</div>')
    H.append(f'<div id="bi{j}" class="ilep" style="left:{cx - 85}px;top:{BASE + 12}px">{ile_svg(ile_, 170)}<span>{nom}</span></div>')
    tw(f"#bg{j}", "scaleY:0", "scaleY:1", tb, 0.4); tw(f"#bi{j}", "opacity:0, y:30", "opacity:1, y:0", tb, 0.3)
    tw(f"#br{j}", "scaleY:0", "scaleY:1", ta, 0.45); tw(f"#bp{j}", "opacity:0, scale:0.5", "opacity:1, scale:1", ta + 0.15, 0.3, "back.out(2.5)")
    for s_ in (f"#bg{j}", f"#br{j}", f"#bp{j}", f"#bi{j}"): fin(s_, T["ilesFin"])
    son(tb, "pop"); son(ta + 0.12, "hit")
el(6.2, T["ilesFin"], '<div class="mini">gris : prix en métropole · rouge : le supplément · INSEE 2022</div>', C, 330, kind=None)

# gros problème (fond net, gros Grilou)
tampon(10.70, 11.55, "GROS PROBLÈME", C, 360, fs=62); BLUR.pop()

# B — quelques grandes entreprises : grille de magasins, quelques-uns prennent toute la place
zone3d(T["grands"], T["grandsFin"])
lab(11.98, T["grandsFin"], "QUELQUES <i>GRANDES</i> ENTREPRISES", C, 330, fs=44, kind=None); son(11.70, "slide"); son(12.76, "boing")
GROS = {(1, 1), (3, 2), (0, 3)}
for x in range(4):
    for y in range(4):
        i = f"tb{x}{y}"; g_ = (x, y) in GROS
        H.append(f'<div id="{i}" class="tuile" style="left:{C - 330 + x * 170}px;top:{500 + y * 170}px"></div>')
        tw(f"#{i}", "opacity:0, scale:0.5", "opacity:1, scale:1", round(T["grands"] + 0.02 * (x + y * 4), 2), 0.28, "back.out(2)")
        if g_: tw(f"#{i}", "scale:1, backgroundColor:'#e9e6ef'", "scale:1.34, backgroundColor:'#e5242b'", T["controlent"], 0.45, "back.out(2)")
        else: tw(f"#{i}", "scale:1, opacity:1", "scale:0.72, opacity:0.55", T["controlent"], 0.45)
        fin(f"#{i}", T["grandsFin"])

# C — GBH + Bernard Hayot (gros plan, pas de chat)
logo(15.14, 17.46, "gbh.png", 520, C, 370)
img1(15.90, 17.46, "bernard.jpg", 600, 830, cx=C, leg="BERNARD HAYOT, le fondateur", kind="photo", bord="rouge")

# Carrefour : de vraies images
video(17.76, 20.05, "carrefour.mp4", C, 760, 760, 475)
logo(18.86, 20.05, "carrefour.png", 230, C, 370)
lab(17.86, 20.05, "À LA RÉUNION", C, 1090, c="sombre", fs=44, kind=None)

# D — la chaîne : une ligne qui serpente, les étapes À CÔTÉ (dessins détourés de la vidéo essence, bateau et colis Fluent 3D), le caddie 3D au bout
zone3d(T["chaine"], T["chaineFin"])
lab(20.20, 22.5, "L'<i>APPROVISIONNEMENT</i>", C, 280, fs=46, kind=None)
lab(23.0, 25.3, "PLUSIEURS <i>ÉTAPES</i>", C, 280, c="rouge", fs=50)
SERP = "M500 350 C 650 420, 650 520, 500 600 S 350 750, 500 830 S 650 980, 500 1060 S 350 1210, 490 1300"
H.append(f'<svg id="ser" width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0;opacity:0"><path id="serp" transform="translate(20 0)" d="{SERP}" fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000" style="filter:drop-shadow(0 4px 10px rgba(0,0,0,.5))"/></svg>')
JS.append(f'tl.set("#ser", {{opacity:1}}, {T["chaine"]});'); fin("#ser", T["chaineFin"])
JS.append(f'tl.fromTo("#serp", {{attr:{{"stroke-dashoffset":1000}}}}, {{attr:{{"stroke-dashoffset":0}}, duration:{round(T["c5"] - T["chaine"], 2)}, ease:"none", immediateRender:false}}, {T["chaine"]});')
for t, img_, w, x, y, nom, kd in [(T["c1"], "bateau.png", 300, 245, 480, "Bateau", "pop"), (T["c2"], "bat-entrepot.png", 340, 765, 660, "Entrepôt", "pop"), (T["c3"], "veh-camion.png", 300, 245, 880, "Camion", "pop"), (T["c4"], "bat-centre-commercial.png", 340, 765, 1090, "Magasin", "pop")]:
    el(t, T["chaineFin"], f'<img src="assets/img/{img_}" style="width:{w}px;display:block;filter:drop-shadow(0 10px 18px rgba(0,0,0,.45))"><div class="etq">{nom}</div>', x, y, kind=kd)
el(T["c5"] + 0.1, T["chaineFin"], '<div class="etq">Votre panier</div>', 255, 1440, kind=None); son(T["c5"], "ding")
for t, x, y in [(T["b1"], 850, 478), (T["b2"], 170, 705), (T["b3"], 850, 900)]:
    el(t, T["chaineFin"], '<div class="pgbh">GBH</div>', x, y, kind="tampon", anim="tampon")
H.append('<img id="colis" src="assets/img/colis.png" style="position:absolute;left:0;top:0;width:84px;opacity:0">')
JS.append(f'(() => {{ const p = document.getElementById("serp"), e = document.getElementById("colis"), L = p.getTotalLength(), o = {{u:0}}; tl.set(e, {{opacity:1}}, {T["c1"]}); tl.fromTo(o, {{u:0}}, {{u:1, duration:{round(T["c5"] - T["c1"], 2)}, ease:"none", immediateRender:false, onUpdate:() => {{ const q = p.getPointAtLength(o.u * L); e.style.transform = `translate(${{q.x - 22}}px, ${{q.y - 50}}px)`; }}}}, {T["c1"]}); tl.set(e, {{opacity:0}}, {T["c5"] + 0.3}); }})();')

# E — le poids de GBH face aux concurrents : des cercles, simple et net
zone3d(T["poids"], T["poidsFin"])
lab(27.74, T["poidsFin"], "UN POIDS <i>CONSIDÉRABLE</i>", C, 330, fs=48, kind=None); son(T["poids"], "cadre"); son(T["poidsT"], "boing")
H.append(f'<div id="rg" class="rond rouge" style="left:{C - 300}px;top:520px;width:430px;height:430px">GBH</div>')
tw("#rg", "opacity:0, scale:0.35", "opacity:1, scale:0.5", T["poids"], 0.3); tw("#rg", "scale:0.5", "scale:1, opacity:1", T["poidsT"], 0.6, "back.out(1.6)"); fin("#rg", T["poidsFin"])
for j, (x, y) in enumerate([(C + 170, 540), (C + 170, 700), (C + 170, 860)]):
    H.append(f'<div id="rc{j}" class="rond petit" style="left:{x}px;top:{y}px;width:130px;height:130px"></div>')
    tw(f"#rc{j}", "opacity:0, scale:0.4", "opacity:1, scale:1", round(T["poids"] + 0.1 * j, 2), 0.3, "back.out(2)"); tw(f"#rc{j}", "scale:1", "scale:0.7, opacity:1", T["poidsT"], 0.5); fin(f"#rc{j}", T["poidsFin"])
lab(28.3, T["poidsFin"], "les concurrents", C + 215, 1060, c="sombre", fs=34, kind=None)

# F — 2020 : le rachat, avec de vraies images de magasins
date(29.34, 33.60, "2020", C, 330, s=0.7)
video(30.20, 33.60, "magasins.mp4", C, 700, 760, 430)
el(30.46, 33.60, '<div class="rachat"><b>GBH</b><span>rachète</span><b class="bleu">VINDÉMIA</b></div>', C, 1010, kind="boing")
el(32.56, 33.60, '<div class="chip">Jumbo</div>', C - 130, 1140); el(33.16, 33.60, '<div class="chip">Score</div>', C + 130, 1140)

# G — 7 magasins à revendre
zone3d(T["autorite"], T["autoriteFin"])
logo(33.70, 36.1, "adlc.png", 340, C, 350)
tampon(36.40, 38.9, "7 MAGASINS À REVENDRE", C, 350, fs=44)
SEPT = {2, 5, 8, 11, 12, 16, 19}; k7 = 0
for n in range(20):
    x, y = n % 5, n // 5; i = f"mg{n}"
    H.append(f'<div id="{i}" class="mag" style="left:{C - 355 + x * 145}px;top:{500 + y * 118}px">{MAG}</div>')
    tw(f"#{i}", "opacity:0, scale:0.5", "opacity:1, scale:1", round(T["autorite"] + 0.02 * n, 2), 0.26, "back.out(2)")
    if n in SEPT:
        a = round(T["sept"] + 0.14 * k7, 2); k7 += 1
        JS.append(f'tl.to("#{i}", {{y:-140, opacity:0, scale:0.8, duration:0.4, ease:"power2.in"}}, {a});')
        if k7 % 2: son(a, "pop")
    fin(f"#{i}", T["autoriteFin"])
lab(39.0, T["autoriteFin"], "TROP DE <i>POUVOIR</i>", C, 350, c="rouge", fs=56)

# H — Martinique (2D)
lab(41.0, 42.5, "ÇA DÉPASSE <i>LA RÉUNION</i>", C, 340, fs=50)
zone3d(41.0, T["martinFin"])
el(42.6, T["martinFin"], ile_svg("martinique", 560), C, 800, kind="cadre")
date(42.62, T["martinFin"], "FÉVRIER 2026", C, 340, s=0.6)
el(44.48, T["martinFin"], '<div class="rapport"><small>Autorité de la concurrence</small><b>Rapport sur la vie chère</b></div>', C, 1230, kind="cadre")

# I — les factures entre sociétés d'un même groupe : schéma 2D limpide
zone3d(T["intra"], T["intraFin"]); son(T["intra"], "cadre"); son(T["groupe"], "pop")
PA, PB, PC = (C - 215, 660), (C + 215, 660), (C, 1040)
el(48.36, T["intraFin"], '<div class="boite"><span>UN MÊME GROUPE</span></div>', C, 830, kind=None)
H.append(f'<svg id="flx" width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0;opacity:0"><g fill="none" stroke="#fff" stroke-width="6" stroke-dasharray="14 12">'
         f'<line x1="{PA[0]}" y1="{PA[1]}" x2="{PB[0]}" y2="{PB[1]}"/><line x1="{PB[0]}" y1="{PB[1]}" x2="{PC[0]}" y2="{PC[1]}"/><line x1="{PC[0]}" y1="{PC[1]}" x2="{PA[0]}" y2="{PA[1]}"/></g></svg>')
tw("#flx", "opacity:0", "opacity:1", T["facture"] - 0.2, 0.3); fin("#flx", T["intraFin"])
for j, ((x, y), nom, c_) in enumerate([(PA, "Société A", "bl"), (PB, "Société B", "vi"), (PC, "Magasin", "ro")]):
    el(T["intra"] + 0.12 * j, T["intraFin"], f'<div class="noeud {c_}">{nom}</div>', x, y, kind="pop")
# les pièces passent d'une société à l'autre
TR = [(PA, PB), (PB, PC), (PC, PA), (PA, PC), (PC, PB), (PB, PA)]
for j, ((x0, y0), (x1, y1)) in enumerate(TR):
    t = round(T["facture"] + 0.5 * j, 2); i = f"pc{j}"
    H.append(f'<div id="{i}" class="piece">€</div>')
    JS.append(f'tl.fromTo("#{i}", {{x:{x0 - 34}, y:{y0 - 34}, opacity:1}}, {{x:{x1 - 34}, y:{y1 - 34}, duration:0.55, ease:"sine.inOut", immediateRender:false}}, {t}); tl.set("#{i}", {{opacity:0}}, {round(t + 0.56, 2)});')
    if j % 2 == 0: son(t, "check")
lab(49.20, 52.5, "ILS SE <i>FACTURENT</i> ENTRE EUX", C, 330, fs=44)
lab(52.66, T["intraFin"], "OÙ EST LE <i>BÉNÉFICE</i> ?", C, 330, c="rouge", fs=52)
for j, (x, y) in enumerate((PA, PB, PC)):
    el(round(T["ouBen"] + 0.14 * j, 2), T["intraFin"], '<div class="quest">?</div>', x, y - 110, kind="pop" if j == 0 else None)

# J — les habitants paient (caddie 3D)
zone3d(T["paient"], T["paientFin"]); son(T["paient"], "cadre")
lab(55.5, T["paientFin"], "ET LES HABITANTS <i>PAIENT</i>", C, 330, fs=46, kind=None)

# Ce que l'État pourrait faire
lab(61.32, 67.3, "L'ÉTAT <i>POURRAIT</i>", C, 320, fs=52)
for j, (t, txt) in enumerate([(62.06, "exiger des comptes transparents"), (64.0, "contrôler les prix à chaque étape"), (65.36, "empêcher les rachats")]):
    el(t, 67.3, f'<div class="chip"><span class="ok">✔</span>{txt}</div>', C, 470 + 125 * j, kind="check", anim="glisse")
# Macron (sans prout, retour du 05/11)
img1(67.68, 69.5, "macron.jpg", 420, 640, cx=C, leg="ENFIN… PAS DANS LA FRANCE À MACRON", bord="rouge")
# 37 %
el(69.92, 75.2, '<div class="gros rouge">+<span class="n37">0</span> %</div>', C, 400, kind="hit")
JS.append('(() => { const o = {v:0}, e = document.querySelector(".n37"); tl.fromTo(o, {v:0}, {v:37, duration:0.7, ease:"power2.out", immediateRender:false, onUpdate:() => { e.textContent = Math.round(o.v); }}, 69.92); })();')
lab(71.1, 75.2, "pour se <i>nourrir</i>", C, 560, fs=52)
tampon(73.9, 75.2, "PAS TOUS MILLIONNAIRES", C, 720, fs=44)
# fin : GBH doit rendre des comptes
logo(76.30, 79.1, "gbh.png", 420, C, 400)
tampon(79.7, CTA - 0.02, "RENDRE DES COMPTES", C, 330, fs=50)
lab(81.1, CTA - 0.02, "SUR LA FORMATION DES PRIX", C, 470, c="sombre", fs=42)

BLUR.sort(); fu = []
for a, b in BLUR:
    if fu and a - fu[-1][1] < 0.6: fu[-1][1] = max(fu[-1][1], b)
    else: fu.append([a, b])
for a, b in fu:
    JS.append(f'tl.to("#net", {{opacity:0, duration:0.25, ease:"power1.inOut"}}, {round(max(a - 0.05, 0), 2)});')
    if b < CTA - 0.1: JS.append(f'tl.to("#net", {{opacity:1, duration:0.3, ease:"power1.inOut"}}, {round(b, 2)});')
def _cum(S):
    c, o = [], 0
    for a, b in S: c.append((o, a, b)); o += b - a
    return c, o
_V3, _L3 = _cum(json.load(open("segments-v3.json"))); _V4, _L4 = _cum(json.load(open("segments.json")))
def _map(t):   # temps sur l'ancienne voix (v3) → temps sur la voix resserrée
    if t >= _L3: return _L4 + t - _L3
    o, a, b = next(s for s in reversed(_V3) if s[0] <= t); x = a + t - o
    for o4, a4, b4 in _V4:
        if x < b4: return o4 + max(x - a4, 0)
    return _L4
_T = lambda t: t if t <= 0.01 else round(_map(t + OFF), 2)
JS = [re.sub(r",\s*(\d+(?:\.\d+)?)\);", lambda m: f", {_T(float(m.group(1)))});", j) for j in JS]
VIDS = [re.sub(r'data-start="([\d.]+)" data-duration="([\d.]+)"', lambda m: f'data-start="{_T(float(m.group(1)))}" data-duration="{round(_T(float(m.group(1)) + float(m.group(2))) - _T(float(m.group(1))), 2)}"', v) for v in VIDS]
SFX = [(_T(t), n, v) for t, n, v in SFX]
T = {k: _T(v) for k, v in T.items()}
# CTA : l'écran violet arrive sur « Si la vidéo t'a plu », le texte pile sur « like » ; voix reprise de l'enregistrement RN (assets/voix-cta.wav)
CTAF = round(_L4 + 0.10, 2); LIKE = round(CTAF + 1.22, 2); END = round(CTAF + 2.70 + 0.75, 2); open("fin.txt", "w").write(str(END))
JS.append(f'tl.set("#cat img", {{opacity:0}}, {CTAF}); tl.set("#cta", {{opacity:1}}, {CTAF});')
JS.append(f'tl.fromTo("#cta-cat", {{opacity:0, scale:0.7, y:90}}, {{opacity:1, scale:1, y:0, duration:0.4, ease:"back.out(1.8)", immediateRender:false}}, {CTAF});')
JS.append(f'tl.fromTo(".ctat", {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.32, ease:"back.out(2.4)", immediateRender:false}}, {LIKE});')
SFX += [(CTAF, "scintillement", 0.4), (LIKE, "ding", 0.3)]
# drapeau de La Réunion : de « réunionnais » à « et sur mon île » (temps réels de la voix finale)
H.append(f'<img id="drapre" src="assets/img/drapeau-reunion.png" style="position:absolute;left:{C - 135}px;top:215px;width:270px;opacity:0;border:7px solid #15121f;border-radius:10px;box-shadow:8px 9px 0 #15121f;transform:rotate(-3deg)">')
JS.append('tl.fromTo("#drapre", {opacity:0, scale:0.4, rotation:-12}, {opacity:1, scale:1, rotation:-3, duration:0.24, ease:"back.out(2.4)", immediateRender:false}, 0.28);')
JS.append('tl.to("#drapre", {opacity:0, scale:0.8, duration:0.16, ease:"power2.in"}, 1.60);')
SFX += [(0.28, "plop", 0.5)]
H = [h.replace("« ", "«&nbsp;").replace(" »", "&nbsp;»") for h in H]; H1 = [h.replace("« ", "«&nbsp;").replace(" »", "&nbsp;»") for h in H1]
SFX.sort(); _s = []
for x in SFX:
    if not _s or x[0] - _s[-1][0] >= 0.12: _s.append(x)
SFX = _s
json.dump(SFX, open("sfx.json", "w"))
LFJS = ",".join(f'"{n}": ' + open(f"assets/lottie/lf-{n}.json", encoding="utf8").read() for n in sorted(LFS))
cats = "".join(f'<img class="{p}" src="assets/chat/{p}.png"' + (' style="opacity:1"' if p == CAT[0][1] else "") + '>' for p in POSES)
html = f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js"></script>
    <script type="importmap">{{ "imports": {{ "three": "https://cdn.jsdelivr.net/npm/three@0.181.2/build/three.module.js", "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.181.2/examples/jsm/" }} }}</script>
    <style>
      @font-face {{ font-family: "Inter"; src: url("assets/fonts/inter-latin-600-normal.woff2") format("woff2"); font-weight: 600; }}
      @font-face {{ font-family: "Inter"; src: url("assets/fonts/inter-latin-800-normal.woff2") format("woff2"); font-weight: 800; }}
      @font-face {{ font-family: "Montserrat"; src: url("assets/fonts/montserrat-latin-500.woff2") format("woff2"); font-weight: 500; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; font-family: "Inter", sans-serif; }}
      .bg {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      .couche {{ position: absolute; inset: 0; }}
      #t3d {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }}
      #cat {{ position: absolute; left: -100px; top: 544px; width: 1086px; height: 1436px; transform-origin: 0% 100%; }}
      #cat img {{ position: absolute; left: 0; top: 0; width: 1086px; height: 1436px; opacity: 0; }}
      #cta {{ position: absolute; inset: 0; background: #000; opacity: 0; }}
      #cta img {{ position: absolute; left: 50%; bottom: -40px; height: 1400px; transform: translateX(-50%); opacity: 0; }}
      .ctat {{ position: absolute; top: 410px; width: 100%; text-align: center; color: #fff; font-family: "Montserrat"; font-weight: 500; font-size: 62px; opacity: 0; }}
      .ic {{ position: absolute; width: max-content; height: max-content; }}
      .it {{ position: relative; opacity: 0; display: flex; flex-direction: column; align-items: center; }}
      .halo {{ position: absolute; left: 50%; top: 50%; width: 1080px; height: 440px; transform: translate(-50%,-50%); border-radius: 50%;
               background: radial-gradient(ellipse at center, rgba(0,0,0,.96) 0%, rgba(0,0,0,.88) 50%, rgba(0,0,0,0) 80%); filter: blur(30px); }}
      .cadrev {{ position: absolute; object-fit: cover; border: 8px solid #fff; border-radius: 24px; box-shadow: 0 18px 36px rgba(0,0,0,.45); opacity: 0; background: #222; }}
      .barre {{ position: absolute; width: 140px; transform-origin: 50% 100%; transform: scaleY(0); }} .barre.gris {{ background: #e9e6ef; border-radius: 0 0 14px 14px; }} .barre.rouge {{ background: #e5242b; border-radius: 14px 14px 0 0; }}
      .pct {{ position: absolute; width: 200px; text-align: center; color: #fff; font-weight: 800; font-size: 56px; text-shadow: 0 4px 14px rgba(0,0,0,.7); opacity: 0; }}
      .ilep {{ position: absolute; width: 170px; display: flex; flex-direction: column; align-items: center; opacity: 0; }}
      .ilep span {{ margin-top: 2px; padding: 6px 14px; border-radius: 14px; background: #fff; color: #2b2550; font-weight: 800; font-size: 30px; white-space: nowrap; }}
      .tuile {{ position: absolute; width: 150px; height: 150px; border-radius: 22px; background: #e9e6ef; box-shadow: 0 10px 22px rgba(0,0,0,.35); opacity: 0; }}
      .mag {{ position: absolute; width: 120px; height: 100px; border-radius: 16px; background: #e5242b; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 18px rgba(0,0,0,.4); opacity: 0; }}
      .rond {{ position: absolute; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; color: #fff; box-shadow: 0 16px 36px rgba(0,0,0,.45); opacity: 0; }}
      .rond.rouge {{ background: #e5242b; font-size: 120px; }} .rond.petit {{ background: #e9e6ef; }}
      .rachat {{ display: flex; align-items: center; gap: 18px; font-weight: 800; font-size: 42px; color: #fff; text-shadow: 0 3px 10px rgba(0,0,0,.7); }}
      .rachat b {{ padding: 10px 24px; border-radius: 16px; background: #e5242b; font-size: 52px; }} .rachat b.bleu {{ background: #2f6fd8; }}
      .boite {{ position: relative; width: 760px; height: 720px; border: 5px solid rgba(255,255,255,.85); border-radius: 36px; background: rgba(20,18,40,.45); }}
      .boite span {{ position: absolute; left: 50%; top: -34px; transform: translateX(-50%); padding: 10px 28px; border-radius: 16px; background: #2b2550; color: #fff; font-weight: 800; font-size: 40px; white-space: nowrap; }}
      .noeud {{ width: 260px; padding: 34px 0; border-radius: 22px; text-align: center; color: #fff; font-weight: 800; font-size: 44px; box-shadow: 0 12px 28px rgba(0,0,0,.45); }}
      .noeud.bl {{ background: #2f6fd8; }} .noeud.vi {{ background: #7a4fd0; }} .noeud.ro {{ background: #e5242b; }}
      .piece {{ position: absolute; left: 0; top: 0; width: 68px; height: 68px; border-radius: 50%; background: #f2c12e; border: 5px solid #fff; color: #7a5a00; font-weight: 800; font-size: 38px; display: flex; align-items: center; justify-content: center; opacity: 0; box-shadow: 0 6px 14px rgba(0,0,0,.4); }}
      .quest {{ width: 84px; height: 84px; border-radius: 50%; background: #ffe14d; color: #2b2550; font-weight: 800; font-size: 56px; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 18px rgba(0,0,0,.4); }}
      .etq {{ margin-top: 6px; padding: 8px 20px; border-radius: 16px; background: #fff; color: #2b2550; font-weight: 800; font-size: 34px; white-space: nowrap; box-shadow: 0 8px 18px rgba(0,0,0,.35); }}
      .pgbh {{ padding: 8px 20px; border-radius: 40px; background: #e5242b; border: 4px solid #fff; color: #fff; font-weight: 800; font-size: 36px; box-shadow: 0 8px 18px rgba(0,0,0,.4); }}
      .titre {{ position: relative; font-family: "Montserrat"; font-weight: 500; color: #fff; text-align: center; line-height: 1.12; white-space: nowrap; font-size: 60px;
                text-shadow: 0 0 4px #000, 0 0 14px #000, 0 0 28px #000, 2px 3px 0 #000; }}
      .img1 {{ display: block; box-shadow: 0 10px 30px rgba(0,0,0,.45); }} .img1.rouge {{ border: 9px solid #e5484d; }}
      .leg {{ padding: 8px 18px; background: #000; color: #fff; font-weight: 800; font-size: 30px; white-space: nowrap; }}
      .plaque {{ padding: 20px 34px; border-radius: 24px; background: #fff; box-shadow: 0 14px 30px rgba(0,0,0,.45); }} .plaque img {{ display: block; }}
      .mini {{ padding: 6px 16px; border-radius: 12px; background: rgba(0,0,0,.65); color: #fff; font-weight: 600; font-size: 26px; white-space: nowrap; }}
      .lab {{ position: relative; padding: 14px 30px; border-radius: 22px; background: #fff; color: #2b2550; font-weight: 800; text-align: center; box-shadow: 0 12px 28px rgba(0,0,0,.35); white-space: nowrap; line-height: 1.1; }}
      .lab i {{ font-style: normal; color: #e5484d; }}
      .lab.sombre {{ background: #2b2550; color: #fff; }} .lab.rouge {{ background: #e5484d; color: #fff; }}
      .lab.rouge i, .lab.sombre i {{ color: #ffe14d; }}
      .carte {{ padding: 22px 46px; border-radius: 30px; background: #fff; box-shadow: 0 18px 40px rgba(0,0,0,.4); text-align: center; color: #2b2550; }}
      .carte small {{ display: block; font-size: 32px; font-weight: 600; color: #7a6f8a; margin-bottom: 4px; }}
      .carte b {{ font-size: 120px; font-weight: 800; color: #e5484d; line-height: 1; white-space: nowrap; }}
      .rapport {{ padding: 26px 40px; border-radius: 12px; background: #fff; border-left: 14px solid #e5484d; box-shadow: 0 16px 36px rgba(0,0,0,.45); color: #2b2550; }}
      .rapport small {{ display: block; font-size: 30px; font-weight: 600; color: #7a6f8a; }} .rapport b {{ font-size: 50px; font-weight: 800; white-space: nowrap; }}
      .tampon {{ padding: 8px 26px; border: 8px solid #e5484d; border-radius: 16px; color: #e5484d; font-weight: 800; letter-spacing: .04em; background: rgba(255,255,255,.92); white-space: nowrap; }}
      .gros {{ padding: 10px 40px; border-radius: 26px; background: #fff; color: #2b2550; font-weight: 800; font-size: 150px; line-height: 1.05; white-space: nowrap; box-shadow: 0 18px 40px rgba(0,0,0,.45); }}
      .gros.rouge {{ background: #e5484d; color: #fff; border: 8px solid #fff; }}
      .chip {{ display: flex; align-items: center; padding: 14px 28px; border-radius: 20px; background: #fff; color: #2b2550; font-weight: 800; font-size: 40px; white-space: nowrap; box-shadow: 0 10px 24px rgba(0,0,0,.35); }}
      .ok {{ flex: none; width: 56px; height: 56px; border-radius: 50%; background: #2fb24c; color: #fff; display: flex; align-items: center; justify-content: center; margin-right: 16px; font-size: 32px; }}
      /* style « miniature YouTube » coloré (05/11) : Lilita One + contour noir + ombre BD ; bandeaux penchés au feutre (Permanent Marker) */
      @font-face {{ font-family: "Lilita"; src: url("assets/fonts/lilita-one.woff2") format("woff2"); }}
      @font-face {{ font-family: "Marker"; src: url("assets/fonts/permanent-marker.woff2") format("woff2"); }}
      #root {{ font-family: "Lilita", sans-serif; --n: #15121f; }}
      .titre, .ctat {{ font-family: "Lilita"; font-weight: 400; letter-spacing: .01em; }}
      .titre {{ font-size: 68px; -webkit-text-stroke: 10px var(--n); paint-order: stroke fill; text-shadow: 5px 7px 0 var(--n); }}
      .ctat {{ position: absolute; top: 330px; left: 0; width: 1030px; text-align: center; color: #fff; font-size: 108px; line-height: 1.06; -webkit-text-stroke: 12px var(--n); paint-order: stroke fill; text-shadow: 6px 8px 0 var(--n); opacity: 0; }}
      .ctat i {{ font-style: normal; color: #ffd93b; }} .ctat u {{ text-decoration: none; color: #ff5d8f; }}
      #cta {{ background: radial-gradient(80% 55% at 50% 70%, #3b2a8f 0%, #170f3d 55%, #07060f 100%); }}
      #cta-cat {{ position: absolute; left: 0; width: 1030px; bottom: -40px; height: 1200px; display: flex; justify-content: center; align-items: flex-end; opacity: 0; transform-origin: 50% 100%; }}
      #cta #cta-cat img {{ position: static; height: 100%; width: auto; transform: none; opacity: 1; filter: drop-shadow(0 0 34px rgba(150,130,255,.75)) drop-shadow(0 0 4px rgba(255,255,255,.5)); }}
      .lab {{ zoom: 1.2; }}
      .lab {{ padding: 0; background: none; box-shadow: none; color: #fff; font-weight: 400; text-transform: uppercase; letter-spacing: .01em; -webkit-text-stroke: 9px var(--n); paint-order: stroke fill; text-shadow: 4px 6px 0 var(--n); }}
      .lab i {{ color: #ffd93b; }}
      .lab.rouge {{ padding: 10px 26px; border-radius: 10px; background: #e5242b; border: 6px solid var(--n); box-shadow: 7px 8px 0 var(--n); -webkit-text-stroke: 0; text-shadow: none; transform: rotate(-2deg); }}
      .lab.rouge i {{ color: #ffd93b; }}
      .lab.sombre {{ padding: 6px 22px; border-radius: 6px; background: #fff; color: var(--n); border: 5px solid var(--n); box-shadow: 6px 7px 0 var(--n); font-family: "Marker"; text-transform: none; -webkit-text-stroke: 0; text-shadow: none; transform: rotate(-2deg); }}
      .leg, .etq, .ilep span {{ padding: 4px 16px; border-radius: 6px; background: #fff; color: var(--n); border: 4px solid var(--n); box-shadow: 4px 5px 0 var(--n); font-family: "Marker"; font-weight: 400; transform: rotate(-2deg); }}
      .leg {{ margin-top: -16px; font-size: 30px; position: relative; }}
      .etq {{ font-size: 32px; }} .ilep span {{ font-size: 25px; }}
      .mini {{ padding: 0; background: none; color: #fff; font-family: "Marker"; font-weight: 400; font-size: 26px; -webkit-text-stroke: 6px var(--n); paint-order: stroke fill; }}
      .plaque {{ border: 6px solid var(--n); border-radius: 14px; box-shadow: 8px 9px 0 var(--n); transform: rotate(-1.5deg); }}
      .carte {{ padding: 16px 40px; border-radius: 14px; background: #ffd93b; border: 7px solid var(--n); box-shadow: 9px 10px 0 var(--n); transform: rotate(-2deg); color: var(--n); }}
      .carte small {{ font-family: "Marker"; font-weight: 400; color: var(--n); }} .carte b {{ font-weight: 400; color: var(--n); }}
      .rapport {{ border-radius: 8px; border: 6px solid var(--n); box-shadow: 8px 9px 0 var(--n); transform: rotate(-1.5deg); }}
      .rapport small {{ font-family: "Marker"; font-weight: 400; color: var(--n); }} .rapport b {{ font-weight: 400; }}
      .tampon {{ padding: 8px 26px; border-radius: 10px; background: #ffd93b; color: var(--n); border: 6px solid var(--n); box-shadow: 7px 8px 0 var(--n); font-weight: 400; letter-spacing: .01em; }}
      .gros {{ border-radius: 14px; border: 7px solid var(--n); box-shadow: 9px 10px 0 var(--n); font-weight: 400; }} .gros.rouge {{ background: #e5242b; border: 7px solid var(--n); }}
      .chip {{ border-radius: 10px; background: #fff; border: 5px solid var(--n); box-shadow: 6px 7px 0 var(--n); font-weight: 400; font-size: 42px; }}
      .ok {{ border: 4px solid var(--n); }}
      .pct {{ color: #ffd93b; font-weight: 400; font-size: 62px; -webkit-text-stroke: 8px var(--n); paint-order: stroke fill; text-shadow: 3px 5px 0 var(--n); }}
      .barre.gris {{ background: #fff; border: 5px solid var(--n); border-top: 0; }} .barre.rouge {{ background: #e5242b; border: 5px solid var(--n); border-bottom: 0; }}
      .rond {{ font-weight: 400; border: 7px solid var(--n); box-shadow: 8px 9px 0 var(--n); }} .rond.rouge {{ background: #e5242b; }} .rond.petit {{ background: #ffd93b; }}
      .tuile {{ border: 5px solid var(--n); box-shadow: 5px 6px 0 var(--n); }}
      .mag {{ border: 4px solid var(--n); box-shadow: 4px 5px 0 var(--n); }}
      .rachat {{ font-weight: 400; font-family: "Marker"; -webkit-text-stroke: 6px var(--n); paint-order: stroke fill; }}
      .rachat b {{ font-family: "Lilita"; font-weight: 400; -webkit-text-stroke: 0; border: 5px solid var(--n); box-shadow: 5px 6px 0 var(--n); }}
      .boite {{ border: 6px solid var(--n); background: rgba(255,255,255,.14); border-radius: 22px; box-shadow: 9px 10px 0 var(--n); }}
      .boite span {{ font-weight: 400; background: #ffd93b; color: var(--n); border: 5px solid var(--n); border-radius: 10px; }}
      .noeud {{ font-weight: 400; border: 6px solid var(--n); border-radius: 14px; box-shadow: 7px 8px 0 var(--n); }}
      .quest {{ font-weight: 400; border: 5px solid var(--n); }}
      .pgbh {{ font-weight: 400; border: 5px solid var(--n); box-shadow: 4px 5px 0 var(--n); }}
      .piece {{ font-weight: 400; border: 5px solid var(--n); }}
      .cadrev {{ border: 7px solid var(--n); border-radius: 14px; box-shadow: 9px 10px 0 var(--n); }}
      .img1 {{ border: 7px solid var(--n); box-shadow: 9px 10px 0 var(--n); }} .img1.rouge {{ border: 7px solid var(--n); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920">
      <video id="flou" class="clip bg" src="assets/bg-flou.mp4" muted playsinline data-start="0" data-duration="{END}" data-track-index="0"></video>
      <video id="net" class="clip bg" src="assets/bg-net.mp4" muted playsinline data-start="0" data-duration="{END}" data-track-index="1"></video>
      <div id="c1" class="clip couche" data-start="0" data-duration="{END}" data-track-index="2" data-layout-allow-overflow>
{chr(10).join("        " + h for h in H1)}
      </div>
      <canvas id="t3d" width="1080" height="1920"></canvas>
{chr(10).join("      " + v for v in VIDS)}
      <div id="cat" class="clip" data-start="0" data-duration="{END}" data-track-index="3" data-layout-allow-overflow>{cats}</div>
      <div id="fx" class="clip couche" data-start="0" data-duration="{END}" data-track-index="4" data-layout-allow-overflow>
{chr(10).join("        " + h for h in H)}
      </div>
      <div id="cta" class="clip" data-start="0" data-duration="{END}" data-track-index="9"><div class="ctat">Like et<br><i>abonne-toi</i> <u>&lt;3</u></div><div id="cta-cat"><img src="assets/chat/c04.png"></div></div>
    </div>
    <script>window.__T3D = {json.dumps(T)};</script>
    <script type="module" src="assets/scene.js"></script>
    <script>const LF = {{{LFJS}}};</script>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join("      " + j for j in JS)}
      tl.set({{}}, {{}}, {END});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open("index.html", "w", encoding="utf8").write(html)
print(f"index.html : {len(H) + len(H1)} éléments, {len(SFX)} sons, {len(fu)} zones floues")
print("net :", [(round(fu[i][1], 2), round(fu[i + 1][0], 2)) for i in range(len(fu) - 1)])
