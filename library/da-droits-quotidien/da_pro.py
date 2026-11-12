# Moteur DA « explication pro » (12/11/2026) : fond noir aux lueurs douces, éléments 3D pâte à modeler détourés qui entrent et flottent,
# sous-titres mot à mot en bas (Lilita One, mots-clés jaunes), PAS de chat 2D. Réf : montages/_refs/style-explication-pro/ref.mp4.
# Temps = voix finale (words.json + AVANCE). Contenu centré x = C = 515 ; illustrations entre y 260 et 1180 ; sous-titres vers y 1300.
import json, os, unicodedata
C = 515
AVANCE = 0.12
SND = {"pop": ["plop", "pop-explainer", "pop-bulle", "pop-sec", "plop", "pop-dur"], "cadre": ["coup-sec", "whoosh-air", "swoosh-court", "coup-sec", "sweep-a"],
       "date": ["whoosh-grave", "swoosh-court", "sweep-a"], "tampon": ["tampon-bois"], "hit": ["basse-hit"], "check": ["clic-check", "clic-souris"],
       "boing": ["boing-montee"], "brille": ["scintillement"], "ding": ["ding"], "trait": ["griffonnage"], "slide": ["tech-slide"], "photo": ["declic-photo"]}
VOL = {"pop": .5, "cadre": .45, "date": .45, "tampon": .55, "hit": .45, "check": .45, "boing": .35, "brille": .3, "ding": .3, "trait": .4, "slide": .35, "photo": .45}
H, JS, SFX = [], [], []
_k = {}; _n = [0]
def _norm(t): return "".join(c for c in unicodedata.normalize("NFD", t.lower()) if c.isalnum() and not unicodedata.combining(c))
W = [[a + AVANCE, b + AVANCE, t] for a, b, t in json.load(open("words.json", encoding="utf8"))]
LEN = round(sum(b - a for a, b in json.load(open("segments.json"))) + AVANCE, 2)
def _eg(m, t): return m == t or (m.isdigit() and t.startswith(m)) or {"trois": "3", "deux": "2", "quatre": "4"}.get(m) == t
def w(mot, apres=0.0, fin=False):
    m = [_norm(x) for x in mot.split()]
    for i in range(len(W) - len(m) + 1):
        if W[i][0] >= apres and all(_eg(m[j], _norm(W[i + j][2])) for j in range(len(m))): return W[i + len(m) - 1][1] if fin else W[i][0]
    raise SystemExit(f"mot introuvable : {mot} après {apres}")
def son(t, kind="pop"):
    l = SND[kind]; i = _k.get(kind, 0); _k[kind] = i + 1; SFX.append((round(t, 2), l[i % len(l)], VOL[kind]))
ENTREES = {"pop": ("opacity:0, scale:0.35, y:40", "opacity:1, scale:1, y:0", 0.34, "back.out(1.9)"),
           "gauche": ("opacity:0, x:-260, rotation:-6", "opacity:1, x:0, rotation:0", 0.38, "power3.out"),
           "droite": ("opacity:0, x:260, rotation:6", "opacity:1, x:0, rotation:0", 0.38, "power3.out"),
           "bas": ("opacity:0, y:220", "opacity:1, y:0", 0.36, "power3.out"),
           "tampon": ("opacity:0, scale:2.3, rotation:-10", "opacity:1, scale:1, rotation:-6", 0.2, "power3.in"),
           "net": ("opacity:0, scale:0.94", "opacity:1, scale:1", 0.16, "power2.out")}
def el(t0, t1, html, cx, cy, kind="pop", anim="pop", flotte=True, z=5, id=None, eclat=False):
    _n[0] += 1; i = id or f"e{_n[0]}"; t0, t1 = round(t0, 2), round(t1, 2)
    if t1 - t0 < 0.3: raise SystemExit(f"élément trop court ({t0} → {t1}) : {html[:70]}")
    carte = any(c in html[:80] for c in ('class="verre', 'class="papier', 'class="pill'))
    if carte and eclat:   # reflet qui balaie la carte : SEULEMENT sur quelques cartes clés (13/11 : « pas partout, pas beau »)
        p = html.index(">"); html = html[:p + 1] + '<i class="eclat"></i>' + html[p + 1:]
    H.append(f'<div class="ic" style="left:{cx}px;top:{cy}px;z-index:{z}"><div id="{i}" class="it"><div class="fl">{html}</div></div></div>')
    de, vers, d, e = ENTREES[anim]
    JS.append(f'tl.fromTo("#{i}", {{{de}}}, {{{vers}, duration:{d}, ease:"{e}", immediateRender:false}}, {t0});')
    if flotte and t1 - t0 > 1.2:
        n = max(1, int((t1 - t0 - 0.4) / 1.5))
        JS.append(f'tl.fromTo("#{i} > .fl", {{y:0, rotation:0}}, {{y:-12, rotation:0.8, duration:1.5, ease:"sine.inOut", repeat:{n}, yoyo:true, immediateRender:false}}, {round(t0 + 0.35, 2)});')
    if carte and t1 - t0 > 1.0:
        n = max(0, int((t1 - t0 - 0.6) / 2.4))
        if eclat: JS.append(f'tl.fromTo("#{i} .eclat", {{xPercent:-160, opacity:1}}, {{xPercent:420, opacity:1, duration:0.8, ease:"power2.inOut", repeat:{n}, repeatDelay:1.6, immediateRender:false}}, {round(t0 + 0.4, 2)});')
        if not flotte and t1 - t0 > 1.6:
            k = max(1, int((t1 - t0 - 0.5) / 1.2))
            JS.append(f'tl.fromTo("#{i} > .fl", {{scale:1}}, {{scale:1.025, duration:1.2, ease:"sine.inOut", repeat:{k}, yoyo:true, immediateRender:false}}, {round(t0 + 0.4, 2)});')
        if 'pill rouge' in html or 'pill jaune' in html:
            k = max(1, int((t1 - t0 - 0.4) / 0.7))
            coul = "255,77,94" if 'pill rouge' in html else "255,217,59"
            JS.append(f'tl.fromTo("#{i} .pill", {{boxShadow:"0 14px 30px rgba(0,0,0,.45), 0 0 0px rgba({coul},0)"}}, {{boxShadow:"0 14px 30px rgba(0,0,0,.45), 0 0 34px rgba({coul},.75)", duration:0.7, ease:"sine.inOut", repeat:{k}, yoyo:true, immediateRender:false}}, {round(t0 + 0.3, 2)});')
    JS.append(f'tl.to("#{i}", {{opacity:0, scale:0.86, duration:0.16, ease:"power2.in"}}, {round(t1 - 0.16, 2)});')
    if kind: son(t0 + (0.17 if anim == "tampon" else 0), kind)
    return i
ECH = 1.0    # 13/11 : tailles choisies scène par scène (petits persos à gauche/droite + schémas, pas tout en gros plan)
def img(t0, t1, nom, larg, cx=C, cy=700, anim="pop", kind="pop", miroir=False, **k):
    # miroir=True : image retournée (ex. le patron qui doit pointer vers Grilou)
    larg = min(860, int(larg * ECH)); mi = "transform:scaleX(-1);" if miroir else ""
    return el(t0, t1, f'<img src="assets/img/{nom}.png" style="width:{larg}px;display:block;{mi}filter:drop-shadow(0 26px 34px rgba(0,0,0,.6))">', cx, cy, kind=kind, anim=anim, **k)
def rangee(t1, items, cy, cx=C, fs=40, gap=18, kind="pop"):
    # pastilles alignées automatiquement (jamais l'une sur l'autre) : items = [(t, html, couleur)], chacune apparaît à son temps
    _n[0] += 1; r = f"rg{_n[0]}"
    inner = "".join(f'<div id="{r}p{j}" class="pill {c}" style="font-size:{fs}px;opacity:0">{h}</div>' for j, (t, h, c) in enumerate(items))
    el(min(t for t, _, _ in items), t1, f'<div style="display:flex;gap:{gap}px;justify-content:center;flex-wrap:wrap;max-width:900px">{inner}</div>', cx, cy, kind=None, anim="net", flotte=False, z=7)
    for j, (t, h, c) in enumerate(items):
        tw(f"#{r}p{j}", "opacity:0, scale:0.4, y:20", "opacity:1, scale:1, y:0", t, 0.3, "back.out(2)")
        if kind: son(t, kind)
def lab(t0, t1, txt, cx=C, cy=300, c="", fs=48, kind=None, anim="pop", **k): return el(t0, t1, f'<div class="lab {c}" style="font-size:{fs}px">{txt}</div>', cx, cy, kind=kind, anim=anim, flotte=False, **k)
def tampon(t0, t1, txt, cx=C, cy=300, fs=56, **k): return el(t0, t1, f'<div class="tampon" style="font-size:{fs}px">{txt}</div>', cx, cy, kind="tampon", anim="tampon", flotte=False, z=8, **k)
def anneau(t0, t1, cx, cy, l, h, kind="check"):
    # cadre lumineux qui pointe une zone d'une image
    return el(t0, t1, f'<div class="anneau" style="width:{l}px;height:{h}px"></div>', cx, cy, kind=kind, anim="net", flotte=False, z=9)
def pill(t0, t1, txt, cx, cy, c="", kind="pop", anim="pop", **k): return el(t0, t1, f'<div class="pill {c}">{txt}</div>', cx, cy, kind=kind, anim=anim, flotte=False, z=7, **k)
def fleche(t0, t1, x1, y1, x2, y2, bombe=60, d=0.35, couleur="#fff"):
    # flèche dessinée (trait qui se trace) d'un élément à l'autre
    _n[0] += 1; i = f"f{_n[0]}"; mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - bombe
    import math
    ang = math.atan2(y2 - my, x2 - mx); a1 = (x2 - 26 * math.cos(ang - .5), y2 - 26 * math.sin(ang - .5)); a2 = (x2 - 26 * math.cos(ang + .5), y2 - 26 * math.sin(ang + .5))
    H.append(f'<svg id="{i}" class="fleche" width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0;z-index:6;opacity:0"><path pathLength="1000" style="stroke:{couleur}" d="M{x1} {y1} Q{mx} {my} {x2} {y2} M{a1[0]:.0f} {a1[1]:.0f} L{x2} {y2} L{a2[0]:.0f} {a2[1]:.0f}"/></svg>')
    JS.append(f'tl.set("#{i}", {{opacity:1}}, {round(t0, 2)}); tl.fromTo("#{i} path", {{attr:{{"stroke-dashoffset":1000}}}}, {{attr:{{"stroke-dashoffset":0}}, duration:{d}, ease:"power2.out", immediateRender:false}}, {round(t0, 2)}); tl.to("#{i}", {{opacity:0, duration:0.15}}, {round(t1 - 0.15, 2)});')
    son(t0, "trait")
def tape(sel, t, d):
    # texte tapé lettre par lettre (les lettres sont des <b class="ch">)
    JS.append(f'tl.fromTo("{sel} .ch", {{opacity:0}}, {{opacity:1, duration:0.01, stagger:{{amount:{d}}}, immediateRender:false}}, {round(t, 2)});')
def lettres(txt): return "".join(f'<b class="ch" style="font-weight:inherit">{c}</b>' for c in txt)
def surligne(sel, t, d=0.45): JS.append(f'tl.fromTo("{sel}", {{backgroundSize:"0% 100%"}}, {{backgroundSize:"100% 100%", duration:{d}, ease:"power2.out", immediateRender:false}}, {round(t, 2)});'); son(t, "trait")
def tw(sel, de, vers, t, d=0.4, ease="power3.out"): JS.append(f'tl.fromTo("{sel}", {{{de}}}, {{{vers}, duration:{d}, ease:"{ease}", immediateRender:false}}, {round(t, 2)});')
def pulse(i, t, s=1.08): JS.append(f'tl.to("#{i}", {{scale:{s}, duration:0.14, ease:"power2.out", yoyo:true, repeat:1}}, {round(t, 2)});')
def deplace(i, t, x=0, y=0, s=1.0, d=0.45): JS.append(f'tl.to("#{i}", {{x:{x}, y:{y}, scale:{s}, duration:{d}, ease:"power3.inOut"}}, {round(t, 2)});')
def sous_titres(cles, fin=None, maxmots=3):
    # sous-titres mot à mot : groupes de 1 à 3 mots, coupés sur la ponctuation et les pauses ; mots-clés en jaune
    cles = {_norm(c) for c in cles}; G, cur = [], []
    FIX = {"lacasse": "la casse"}
    WW = []
    for a, b, t in W:   # « l » + « 'assumer » → « l'assumer » ; « L1331 » + « -2 » → « L1331-2 »
        t = FIX.get(t.lower().strip(".,!?"), t)
        if WW and t[:1] in "'-": WW[-1] = (WW[-1][0], b, WW[-1][2] + t)
        else: WW.append((a, b, t))
    for k, (a, b, t) in enumerate(WW):
        cur.append((a, b, t))
        nxt = WW[k + 1][0] if k + 1 < len(WW) else 1e9
        if len(cur) >= maxmots or t[-1:] in ".,?!:" or nxt - b > 0.25: G.append(cur); cur = []
    if cur: G.append(cur)
    for j, g in enumerate(G):
        t0 = g[0][0]; t1 = G[j + 1][0][0] if j + 1 < len(G) else (fin or g[-1][1] + 0.3)
        t1 = min(t1, g[-1][1] + 0.6)
        if fin: t1 = min(t1, fin)
        if t1 - t0 < 0.12: t1 = t0 + 0.12
        mots = " ".join((f"<i>{x.rstrip('.,!?:')}</i>" if any(_norm(p) in cles for p in x.replace("'", " ").replace("-", " ").split()) else x.rstrip(".,!?:")) for _, _, x in g)
        mots = mots.replace(" '", "'").replace("j 'ai", "j'ai")
        _n[0] += 1; i = f"s{_n[0]}"
        H.append(f'<div id="{i}" class="st">{mots}</div>')
        JS.append(f'tl.fromTo("#{i}", {{opacity:0, scale:0.8, y:16}}, {{opacity:1, scale:1, y:0, duration:0.12, ease:"back.out(2.5)", immediateRender:false}}, {round(t0, 2)});')
        JS.append(f'tl.set("#{i}", {{opacity:0}}, {round(t1, 2)});')
def finir(nom, like=1.22, cta_img="grilou-victoire", fond=None):
    # fond=image : décor (ex. intérieur de café) assombri pour que persos et cartes ressortent, avec un lent zoom
    CTAF = round(LEN + 0.10, 2); LIKE = round(CTAF + like, 2)
    dur_cta = float(open("fz/cta-duree.txt").read()) if os.path.exists("fz/cta-duree.txt") else 2.70
    END = round(CTAF + dur_cta + 0.6, 2); open("fin.txt", "w").write(str(END))
    JS.append(f'tl.set("#cta", {{opacity:1}}, {CTAF});')
    JS.append(f'tl.fromTo("#cta-cat", {{opacity:0, scale:0.7, y:90}}, {{opacity:1, scale:1, y:0, duration:0.4, ease:"back.out(1.8)", immediateRender:false}}, {CTAF});')
    JS.append(f'tl.fromTo(".ctat", {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.32, ease:"back.out(2.4)", immediateRender:false}}, {LIKE});')
    SFX.extend([(CTAF, "scintillement", 0.35), (LIKE, "ding", 0.3)])
    nb = lambda h: h.replace("« ", "«&nbsp;").replace(" »", "&nbsp;»").replace(" ?", "&nbsp;?").replace(" !", "&nbsp;!")
    S = sorted(SFX); o = []
    for x in S:
        if not o or x[0] - o[-1][0] >= 0.12: o.append(x)
    json.dump(o, open("sfx.json", "w"))
    css = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "da_ref.css.txt"), encoding="utf8").read()
    nl = chr(10)
    FOND = ""
    if fond:
        FOND = (f'<img id="decor" src="{fond}" style="position:absolute;left:-20px;top:-20px;width:1120px;height:1960px;object-fit:cover">'
                '<div style="position:absolute;inset:0;background:linear-gradient(180deg, rgba(10,6,20,.55) 0%, rgba(10,6,20,.45) 35%, rgba(10,6,20,.62) 65%, rgba(8,5,16,.85) 100%)"></div>'
                '<div style="position:absolute;inset:0;background:radial-gradient(70% 55% at 50% 48%, transparent 30%, rgba(0,0,0,.55) 100%)"></div>')
        JS.insert(0, f'tl.fromTo("#decor", {{scale:1.0}}, {{scale:1.07, duration:{END}, ease:"none", immediateRender:false}}, 0);')
    # poussières lumineuses qui montent doucement (fond vivant)
    import random; rd = random.Random(7); PAR = ""
    for k in range(34):
        x, y, t, d = rd.randint(20, 1060), rd.randint(300, 1900), rd.uniform(3, 7), rd.uniform(6, 14)
        PAR += f'<div id="pa{k}" class="par" style="left:{x}px;top:{y}px;width:{t:.0f}px;height:{t:.0f}px;opacity:0"></div>'
        rep = int(END / d) + 1
        JS.insert(0, f'tl.fromTo("#pa{k}", {{y:0, opacity:0}}, {{keyframes:[{{opacity:{rd.uniform(.25, .6):.2f}, duration:{d * .3:.2f}}}, {{opacity:0, duration:{d * .7:.2f}}}], y:-{rd.randint(260, 520)}, duration:{d:.2f}, ease:"none", repeat:{rep}, immediateRender:false}}, {rd.uniform(0, d):.2f});')
    html = f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>{css}
      html, body, #root {{ background: #05040a; }}
      #fond {{ position: absolute; inset: 0; background: radial-gradient(70% 40% at 50% 8%, rgba(88,58,170,.42), transparent 70%), radial-gradient(80% 35% at 50% 98%, rgba(20,120,110,.30), transparent 70%), radial-gradient(120% 80% at 50% 50%, #0b0a18 0%, #05040a 70%); }}
      .lueur {{ position: absolute; border-radius: 50%; filter: blur(90px); opacity: .35; }}
      #l1 {{ left: -200px; top: 120px; width: 760px; height: 560px; background: #3b2a8f; }}
      #l2 {{ right: -260px; bottom: 140px; width: 820px; height: 600px; background: #0f5c63; }}
      #grain {{ position: absolute; inset: 0; opacity: .06; background-image: radial-gradient(rgba(255,255,255,.7) 1px, transparent 1px); background-size: 4px 4px; }}
      .ic {{ transform: translate(-50%, -50%); }}
      .anneau {{ border: 7px solid #ffd93b; border-radius: 18px; box-shadow: 0 0 0 6px rgba(21,18,31,.85), 0 0 40px rgba(255,217,59,.55); }}
      .st {{ position: absolute; left: 0; top: 1330px; width: 1030px; text-align: center; font-family: "Lilita"; font-size: 66px; line-height: 1.05; color: #fff; text-transform: uppercase; letter-spacing: .01em;
             -webkit-text-stroke: 10px #15121f; paint-order: stroke fill; text-shadow: 5px 7px 0 #15121f; opacity: 0; z-index: 20; }}
      .st i {{ font-style: normal; color: #ffd93b; }}
      /* 13/11 : composants maison façon réf (verre sombre, papier, pastilles, flèches) avec nos polices */
      .verre {{ padding: 26px 30px; border-radius: 30px; background: linear-gradient(160deg, rgba(58,48,120,.72), rgba(22,18,48,.82)); border: 2px solid rgba(255,255,255,.14); box-shadow: 0 30px 60px rgba(0,0,0,.55), inset 0 1px 0 rgba(255,255,255,.12); color: #fff; font-family: "Lilita"; }}
      .verre .tt {{ display: inline-block; padding: 8px 20px; border-radius: 30px; background: rgba(255,255,255,.1); font-size: 34px; color: #cfc9ff; letter-spacing: .03em; margin-bottom: 14px; }}
      .papier {{ padding: 30px 34px; border-radius: 16px; background: #f5f0e6; color: #1d1a2b; box-shadow: 0 30px 60px rgba(0,0,0,.55); font-family: "Lilita"; }}
      .papier .entete {{ display: flex; justify-content: space-between; align-items: center; font-size: 27px; color: #6b6478; letter-spacing: .06em; border-bottom: 3px solid #e2dacb; padding-bottom: 10px; margin-bottom: 14px; }}
      .papier .vig {{ padding: 2px 12px; border: 3px solid #2fa35a; color: #2fa35a; border-radius: 8px; font-size: 20px; transform: rotate(3deg); }}
      .papier .ligne {{ display: flex; justify-content: space-between; font-size: 42px; padding: 10px 4px; border-bottom: 2px dashed #ddd3c2; white-space: nowrap; gap: 30px; }}
      .papier .ligne.rouge {{ color: #d0242b; background: rgba(229,36,43,.1); border-radius: 8px; }}
      .papier .net {{ font-size: 48px; border-bottom: 0; padding-top: 16px; }}
      .surl {{ background: linear-gradient(transparent 55%, #ffd93b 55%); background-size: 0% 100%; background-repeat: no-repeat; }}
      .pill {{ display: inline-flex; align-items: center; gap: 12px; padding: 12px 26px; border-radius: 60px; background: rgba(24,20,48,.9); border: 2px solid rgba(255,255,255,.18); color: #fff; font-family: "Lilita"; font-size: 46px; white-space: nowrap; box-shadow: 0 14px 30px rgba(0,0,0,.45); }}
      .pill.vert {{ border-color: #36d07a; color: #8ff0b8; }} .pill.rouge {{ border-color: #ff4d5e; color: #ff9aa4; }} .pill.jaune {{ border-color: #ffd93b; color: #ffe27a; }}
      .rond-ok, .rond-ko {{ width: 52px; height: 52px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 32px; color: #fff; flex: none; }}
      .rond-ok {{ background: #2fb860; }} .rond-ko {{ background: #e5242b; }}
      .verre, .papier, .pill {{ position: relative; overflow: hidden; }}
      .eclat {{ position: absolute; top: -20%; left: 0; opacity: 0; width: 28%; height: 140%; background: linear-gradient(100deg, transparent, rgba(255,255,255,.28), transparent); transform: skewX(-18deg); pointer-events: none; z-index: 3; }}
      .papier .eclat {{ background: linear-gradient(100deg, transparent, rgba(255,255,255,.75), transparent); }}
      .par {{ position: absolute; border-radius: 50%; background: #cfc9ff; }}
      .fleche path {{ fill: none; stroke: #fff; stroke-width: 7; stroke-linecap: round; stroke-dasharray: 1000; stroke-dashoffset: 1000; filter: drop-shadow(0 4px 10px rgba(0,0,0,.6)); }}
      #cta-cat img {{ filter: drop-shadow(0 0 40px rgba(150,130,255,.6)) !important; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920">
      <div id="bg" class="clip couche" data-start="0" data-duration="{END}" data-track-index="0"><div id="fond"></div>{FOND}<div id="l1" class="lueur"></div><div id="l2" class="lueur"></div><div id="grain"></div>{PAR}</div>
      <div id="fx" class="clip couche" data-start="0" data-duration="{END}" data-track-index="4" data-layout-allow-overflow>
{nl.join("        " + nb(h) for h in H)}
      </div>
      <div id="cta" class="clip" data-start="0" data-duration="{END}" data-track-index="9"><div class="ctat">Like et<br><i>abonne-toi</i> <u>&lt;3</u></div><div id="cta-cat"><img src="assets/img/{cta_img}.png"></div></div>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#l1", {{x:0, y:0}}, {{x:160, y:120, duration:{round(END / 2, 2)}, ease:"sine.inOut", yoyo:true, repeat:1, immediateRender:false}}, 0);
      tl.fromTo("#l2", {{x:0, y:0}}, {{x:-140, y:-160, duration:{round(END / 2, 2)}, ease:"sine.inOut", yoyo:true, repeat:1, immediateRender:false}}, 0);
{nl.join("      " + j for j in JS)}
      tl.set({{}}, {{}}, {END});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    open("index.html", "w", encoding="utf8").write(html)
    print(f"{nom} : fin {END} s, {len(H)} éléments, {len(o)} sons")
