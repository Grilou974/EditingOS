# Regenerates the starter library (charte animations + reference demos).
# Run from editing-os/library:  python _build_library.py
import json, os

HEAD = """<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;700;800;900&family=Sora:wght@700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--ink:#0f1626;--paper:#f6f1e7;--y:#ffd23f;--r:#ff4d4d;--b:#3a86ff;--g:#2ec4b6}
html,body{width:100%;height:100%;overflow:hidden}
body{font-family:Inter,system-ui,sans-serif;display:grid;place-items:center;background:var(--bg,#0f1626);color:#fff;font-size:4vmin}
.stage{position:relative;width:100%;height:100%;display:grid;place-items:center}
%CSS%
</style></head><body><div class="stage">%HTML%</div></body></html>"""

CAT_SVG = """<svg viewBox="0 0 200 200" class="%C%"><path d="M40 70 L55 20 L85 55 Z M160 70 L145 20 L115 55 Z" fill="#f2a65a" stroke="#0f1626" stroke-width="6" stroke-linejoin="round"/><ellipse cx="100" cy="110" rx="72" ry="64" fill="#f2a65a" stroke="#0f1626" stroke-width="6"/>%FACE%<path d="M30 120 h-22 M30 132 h-20 M170 120 h22 M170 132 h20" stroke="#0f1626" stroke-width="4" stroke-linecap="round"/></svg>"""
FACE_A = '<circle cx="75" cy="100" r="9" fill="#0f1626"/><circle cx="125" cy="100" r="9" fill="#0f1626"/><path d="M88 128 q12 12 24 0" stroke="#0f1626" stroke-width="6" fill="none" stroke-linecap="round"/>'
FACE_B = '<path d="M63 96 l22 8 M137 96 l-22 8" stroke="#0f1626" stroke-width="7" stroke-linecap="round"/><ellipse cx="100" cy="135" rx="14" ry="12" fill="#0f1626"/>'

ITEMS = [
 ("titre-section", "Titre de section", "Structure", "Étiquette « chapitre » puis titre qui entre derrière un aplat jaune.", """
.lab{position:absolute;top:34%;left:10%;background:var(--y);color:var(--ink);font-weight:900;letter-spacing:.15em;font-size:3.2vmin;padding:1.2vmin 2.4vmin;border-radius:1vmin;animation:lab 4s infinite}
.t{position:absolute;top:44%;left:10%;font-family:Sora;font-weight:800;font-size:11vmin;line-height:1;overflow:hidden}
.t span{display:block;animation:up 4s infinite}
.wipe{position:absolute;top:44%;left:10%;height:11vmin;width:70%;background:var(--y);transform-origin:left;animation:wipe 4s infinite;z-index:2}
@keyframes lab{0%{opacity:0;transform:translateX(-4vmin)}10%,85%{opacity:1;transform:none}100%{opacity:0}}
@keyframes wipe{0%,8%{transform:scaleX(0);transform-origin:left}20%{transform:scaleX(1);transform-origin:left}21%{transform:scaleX(1);transform-origin:right}34%,100%{transform:scaleX(0);transform-origin:right}}
@keyframes up{0%,20%{opacity:0}21%,85%{opacity:1}100%{opacity:0}}""",
  """<div class="lab">CHAPITRE 2</div><div class="wipe"></div><div class="t"><span>La réforme</span></div>"""),
 ("texte-surligne", "Texte surligné", "Texte", "Les mots apparaissent un à un, puis un feutre jaune surligne le mot clé.", """
body{--bg:#f6f1e7;color:var(--ink)}
p{font-family:Sora;font-weight:800;font-size:8vmin;line-height:1.25;width:80%}
p span{opacity:0;display:inline-block;animation:w 4s infinite}
p span:nth-child(2){animation-delay:.15s}p span:nth-child(3){animation-delay:.3s}p span:nth-child(4){animation-delay:.45s}
.k{position:relative;z-index:0}
.k::before{content:"";position:absolute;z-index:-1;left:-1vmin;right:-1vmin;bottom:.6vmin;height:4.4vmin;background:var(--y);transform:scaleX(0);transform-origin:left;animation:hl 4s infinite}
@keyframes w{0%{opacity:0;transform:translateY(2vmin)}8%,88%{opacity:1;transform:none}100%{opacity:0}}
@keyframes hl{0%,30%{transform:scaleX(0)}42%,100%{transform:scaleX(1)}}""",
  """<p><span>Le</span> <span>budget</span> <span>est</span> <span class="k">rejeté.</span></p>"""),
 ("bandeau-actu", "Bandeau actu « DIRECT »", "Actu", "Pastille DIRECT qui pulse et titre d'actu qui défile sur un bandeau.", """
.bar{position:absolute;left:0;right:0;top:40%;height:14vmin;background:#fff;color:var(--ink);display:flex;align-items:center;overflow:hidden;animation:in 4s infinite}
.live{flex:none;background:var(--r);color:#fff;font-weight:900;height:100%;display:flex;align-items:center;gap:1.4vmin;padding:0 3vmin;letter-spacing:.1em;font-size:4vmin;z-index:1}
.dot{width:2vmin;height:2vmin;border-radius:50%;background:#fff;animation:p 1s infinite}
.tk{white-space:nowrap;font-weight:800;font-size:5vmin;padding-left:4vmin;animation:tk 4s linear infinite}
@keyframes p{50%{opacity:.2}}
@keyframes tk{from{transform:translateX(30%)}to{transform:translateX(-40%)}}
@keyframes in{0%{transform:translateX(-100%)}10%,90%{transform:none}100%{transform:translateX(100%)}}""",
  """<div class="bar"><div class="live"><span class="dot"></span>DIRECT</div><div class="tk">Assemblée nationale : vote attendu ce soir sur le texte · Assemblée nationale : vote attendu ce soir</div></div>"""),
 ("chiffre-cle", "Chiffre clé (count-up)", "Données", "Le nombre monte jusqu'à sa valeur, avec la source en petit dessous.", """
.n{font-family:Sora;font-weight:800;font-size:22vmin;color:var(--y);font-variant-numeric:tabular-nums}
.l{font-size:4.6vmin;font-weight:700;margin-top:1vmin}.s{font-size:2.6vmin;opacity:.6;margin-top:2vmin}
.w{text-align:center;animation:in 4s infinite}
@keyframes in{0%{opacity:0;transform:scale(.8)}8%,90%{opacity:1;transform:none}100%{opacity:0}}""",
  """<div class="w"><div class="n" id="n">0</div><div class="l">exemple de chiffre clé</div><div class="s">Source : à citer à l'écran</div></div>
<script>const n=document.getElementById('n');const t0=performance.now();(function f(t){const u=((t-t0)%4000)/4000,k=Math.min(1,Math.max(0,(u-.08)/.3));n.textContent=Math.round(577*(1-Math.pow(1-k,3)));requestAnimationFrame(f)})(t0)</script>"""),
 ("zoom-zone", "Zoom sur zone", "Partage d'écran", "Capture d'article : un spot isole une ligne puis la caméra zoome dessus.", """
body{--bg:#1b2333}
.doc{width:62%;background:#fff;border-radius:2vmin;padding:4vmin;color:var(--ink);animation:z 4s infinite;transform-origin:50% 62%}
.doc h4{font-family:Sora;font-size:4.4vmin;margin-bottom:2vmin}
.ln{height:2.2vmin;background:#d8dbe2;border-radius:1vmin;margin:1.6vmin 0}
.ln.k{background:var(--y)}
.sp{position:absolute;inset:0;background:radial-gradient(ellipse 34% 10% at 50% 58%,transparent 60%,rgba(0,0,0,.65) 100%);opacity:0;animation:sp 4s infinite}
@keyframes z{0%,25%{transform:none}50%,85%{transform:scale(1.9)}100%{transform:none}}
@keyframes sp{0%,15%{opacity:0}30%,85%{opacity:1}100%{opacity:0}}""",
  """<div class="doc"><h4>Article de presse</h4><div class="ln"></div><div class="ln" style="width:80%"></div><div class="ln k"></div><div class="ln" style="width:70%"></div><div class="ln"></div></div><div class="sp"></div>"""),
 ("chat-expressions", "Chat qui parle (expressions)", "Personnage", "Le chat change d'expression à chaque idée et une bulle apparaît. Le dessin sera remplacé par tes images 2D.", """
body{--bg:#3a86ff}
.c{position:absolute;bottom:6%;left:8%;width:46vmin;height:46vmin;animation:bob .5s ease-in-out infinite alternate}
.c svg{position:absolute;inset:0;width:100%;height:100%}
.a{animation:sw 2s steps(1) infinite}.b{animation:sw 2s steps(1) infinite;animation-delay:-1s}
@keyframes sw{0%{opacity:1}50%{opacity:0}}
@keyframes bob{to{transform:translateY(-1.2vmin) rotate(-1deg)}}
.bub{position:absolute;top:18%;right:8%;max-width:48%;background:#fff;color:var(--ink);font-family:Sora;font-weight:800;font-size:5vmin;padding:3vmin;border-radius:4vmin;animation:pop 2s infinite;transform-origin:10% 100%}
.bub::after{content:"";position:absolute;left:12%;bottom:-4.6vmin;border:2vmin solid transparent;border-top:3vmin solid #fff}
@keyframes pop{0%{transform:scale(0)}12%{transform:scale(1.08)}18%,85%{transform:scale(1)}100%{transform:scale(0)}}""",
  '<div class="c">' + CAT_SVG.replace("%C%", "a").replace("%FACE%", FACE_A) + CAT_SVG.replace("%C%", "b").replace("%FACE%", FACE_B) + '</div><div class="bub">Attends… quoi ?!</div>'),
 ("barres-sondage", "Barres de sondage", "Données", "Trois barres poussent l'une après l'autre avec leur pourcentage.", """
.w{width:74%}.r{display:flex;align-items:center;gap:2vmin;margin:3vmin 0;font-weight:800;font-size:4vmin}
.r b{width:22%}.r i{display:block;height:6vmin;border-radius:1.2vmin;transform-origin:left;animation:g 4s infinite}
.r:nth-child(2) i{animation-delay:.2s}.r:nth-child(3) i{animation-delay:.4s}
@keyframes g{0%{transform:scaleX(0)}20%,88%{transform:scaleX(1)}100%{transform:scaleX(0)}}""",
  """<div class="w"><div class="r"><b>Oui</b><i style="width:52%;background:var(--g)"></i>52 %</div><div class="r"><b>Non</b><i style="width:38%;background:var(--r)"></i>38 %</div><div class="r"><b>NSP</b><i style="width:10%;background:#8a94a6"></i>10 %</div><p style="font-size:2.4vmin;opacity:.6">Valeurs d'exemple</p></div>"""),
 ("citation", "Citation", "Texte", "Guillemets géants, phrase citée et auteur qui glisse en dessous.", """
body{--bg:#f6f1e7;color:var(--ink)}
.q{width:78%;position:relative;animation:in 4s infinite}
.q::before{content:"\\201C";position:absolute;top:-14vmin;left:-2vmin;font-family:Sora;font-size:30vmin;color:var(--r);line-height:1}
.q p{font-family:Sora;font-weight:800;font-size:7vmin;line-height:1.2}
.q small{display:block;margin-top:3vmin;font-weight:700;font-size:3.6vmin;opacity:.7}
@keyframes in{0%{opacity:0;transform:translateY(3vmin)}10%,88%{opacity:1;transform:none}100%{opacity:0}}""",
  """<div class="q"><p>Une phrase forte à citer ici.</p><small>— Nom, fonction</small></div>"""),
 ("transition-whip", "Transition « whip »", "Transition", "Balayage rapide avec flou de mouvement entre deux plans.", """
.p{position:absolute;inset:0;display:grid;place-items:center;font-family:Sora;font-weight:800;font-size:12vmin}
.p1{background:var(--b);animation:a 2.4s infinite cubic-bezier(.7,0,.3,1)}.p2{background:var(--r);animation:b 2.4s infinite cubic-bezier(.7,0,.3,1)}
@keyframes a{0%,40%{transform:none;filter:none}55%{transform:translateX(-100%);filter:blur(2vmin)}56%,100%{transform:translateX(-100%)}}
@keyframes b{0%,40%{transform:translateX(100%)}55%{transform:none;filter:blur(2vmin)}62%,100%{transform:none;filter:none}}""",
  """<div class="p p1">PLAN A</div><div class="p p2">PLAN B</div>"""),
 ("lower-third", "Lower third", "Structure", "Nom et fonction d'une personne, en deux bandes qui glissent.", """
body{--bg:#1b2333}
.lt{position:absolute;left:8%;bottom:16%}
.n,.f{display:block;width:max-content;padding:1.4vmin 2.6vmin;font-weight:900;animation:in 4s infinite}
.n{background:#fff;color:var(--ink);font-size:5.4vmin}.f{background:var(--y);color:var(--ink);font-size:3.4vmin;font-weight:700;animation-delay:.12s}
@keyframes in{0%{clip-path:inset(0 100% 0 0)}12%,85%{clip-path:inset(0 0 0 0)}100%{clip-path:inset(0 0 0 100%)}}""",
  """<div class="lt"><span class="n">Prénom Nom</span><span class="f">Fonction · Parti</span></div>"""),
]

REF_DEMOS = {
 "vox-explainer": ("""body{--bg:#efe7d6;color:#1a1a1a}
.paper{width:70%;background:#fbf6ea;padding:4vmin;box-shadow:0 2vmin 4vmin rgba(0,0,0,.2);transform:rotate(-2deg);animation:in 4s infinite}
.paper p{font-family:Georgia,serif;font-size:4.6vmin;line-height:1.5}
mark{background:linear-gradient(#ffe14d,#ffe14d) no-repeat 0 85%/0% 60%;animation:m 4s infinite;color:inherit}
@keyframes m{0%,25%{background-size:0% 60%}45%,90%{background-size:100% 60%}}
@keyframes in{0%{opacity:0;transform:rotate(-2deg) translateY(4vmin)}10%,90%{opacity:1;transform:rotate(-2deg)}100%{opacity:0}}""",
  """<div class="paper"><p>Document d'archive : <mark>la phrase importante</mark> ressort au surligneur.</p></div>"""),
 "flat-vectoriel": ("""body{--bg:#18204a}
.s{position:absolute;border-radius:50%;animation:b 2s ease-in-out infinite alternate}
@keyframes b{to{transform:translateY(-6vmin) scale(1.05)}}""",
  """<div class="s" style="width:30vmin;height:30vmin;background:#ff6b6b;left:20%;top:35%"></div><div class="s" style="width:18vmin;height:18vmin;background:#ffd23f;left:55%;top:30%;animation-delay:.4s"></div><div class="s" style="width:12vmin;height:12vmin;background:#2ec4b6;left:62%;top:58%;animation-delay:.8s"></div>"""),
 "carte-trajet": ("""body{--bg:#dfe9d8}
svg{width:80%;height:80%}
.r{stroke-dasharray:600;stroke-dashoffset:600;animation:d 4s infinite}
.pin{animation:p 4s infinite;transform-origin:center;transform-box:fill-box}
@keyframes d{0%,15%{stroke-dashoffset:600}60%,90%{stroke-dashoffset:0}}
@keyframes p{0%,55%{transform:scale(0)}65%,90%{transform:scale(1)}}""",
  """<svg viewBox="0 0 400 300"><path d="M40 220 C 80 120, 160 260, 210 150 S 330 60, 360 90" fill="none" stroke="#c0392b" stroke-width="6" stroke-linecap="round" class="r"/><circle cx="40" cy="220" r="10" fill="#1a1a1a"/><g class="pin"><circle cx="360" cy="90" r="16" fill="#c0392b"/><circle cx="360" cy="90" r="6" fill="#fff"/></g></svg>"""),
}

REFS = [
 {"id": "vox-explainer", "name": "Vox Explainer", "platform": "YouTube", "url": "https://www.youtube.com/@Vox", "demo": "references/vox-explainer.html",
  "traits": ["Textures papier et coupures d'archives", "Surligneur sur les documents", "Cartes et zooms", "Rythme posé, voix off"],
  "notes": "Inspiration pour les passages « preuve » : capture d'article + surlignage."},
 {"id": "carte-trajet", "name": "Récit sur carte", "platform": "YouTube", "url": "", "demo": "references/carte-trajet.html",
  "traits": ["Tracés animés sur carte", "Épingles qui apparaissent", "Caméra qui suit le tracé"],
  "notes": "Pour l'actu internationale : situer un événement en 2 secondes."},
 {"id": "flat-vectoriel", "name": "Flat vectoriel coloré", "platform": "YouTube", "url": "", "demo": "references/flat-vectoriel.html",
  "traits": ["Formes géométriques simples", "Couleurs saturées sur fond sombre", "Mouvements rebondis"],
  "notes": "Ambiance ludique pour les transitions et les fonds."},
 {"id": "mascotte-actu", "name": "Mascotte qui commente l'actu (type « Trash »)", "platform": "YouTube / Shorts", "url": "", "demo": "charte/chat-expressions.html",
  "traits": ["Personnage 2D, une image par expression", "Expressions qui changent à chaque idée", "Coupes rapides, ton jeune mais pro", "Pas de sous-titres"],
  "notes": "Référence citée pour mes shorts politiques avec le chat. À compléter : lien de la chaîne + 2–3 vidéos modèles."},
]

os.makedirs("charte", exist_ok=True)
os.makedirs("references", exist_ok=True)
meta = []
for slug, name, cat, desc, css, html in ITEMS:
    open(f"charte/{slug}.html", "w", encoding="utf8").write(HEAD.replace("%CSS%", css).replace("%HTML%", html))
    meta.append({"id": slug, "name": name, "category": cat, "description": desc, "file": f"charte/{slug}.html", "origin": "Ma charte"})
json.dump(meta, open("charte.json", "w", encoding="utf8"), ensure_ascii=False, indent=2)
for k, (css, html) in REF_DEMOS.items():
    open(f"references/{k}.html", "w", encoding="utf8").write(HEAD.replace("%CSS%", css).replace("%HTML%", html))
if not os.path.exists("references.json"):
    json.dump(REFS, open("references.json", "w", encoding="utf8"), ensure_ascii=False, indent=2)
print(len(meta), "animations,", len(REF_DEMOS), "démos de références")
