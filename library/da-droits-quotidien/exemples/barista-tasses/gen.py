# « Barista : 4 tasses cassées » v2 (13/11) — façon réf : petits persos à gauche/droite, schémas maison (fiche de paie, article, calcul, échelle,
# procédure), pastilles, flèches, un changement toutes les ≈ 1 s ; tout descendu (scène entre y 560 et 1200, sous-titres à 1330).
import sys; sys.path.insert(0, "../_outils")
from da_pro import *
from da_pro import _n
G, D, Y = 300, 760, 900          # positions perso gauche / droite et hauteur de scène

# 1. « Je suis barista, et ce matin j'ai cassé ma quatrième tasse du mois »
e1 = w("Mon patron") - 0.05
g1 = img(0.0, w("cassé") - 0.02, "grilou-tasse", 380, cx=C, cy=Y, anim="net", kind=None)
pill(0.3, w("cassé") - 0.02, "barista", C, Y - 300, c="jaune", kind=None)
g2 = img(w("cassé") - 0.05, w("Il m") - 0.05, "grilou-lache", 400, cx=C, cy=Y, anim="net", kind="hit")
deplace(g2, w("Mon patron") - 0.1, x=G - C, s=0.85)
for j in range(4):
    t = round(w("cassé") + 0.12 + 0.13 * j, 2)
    el(t, e1, f'<div class="verre" style="padding:14px 18px;font-size:46px;color:{"#ff6b75" if j == 3 else "#fff"}">{j + 1}</div>', C - 210 + 140 * j, 600, kind="pop" if j == 3 else None, flotte=False)
pill(w("quatrième") - 0.05, e1, "4<sup style='font-size:.55em'>e</sup> ce mois-ci", C, 470, c="rouge", kind="hit")

# 2. le patron pète un câble, la menace sur la paie
pa = img(w("Mon patron"), w("Mais est") - 0.05, "patron-crie", 400, cx=D, cy=Y, anim="droite", kind="cadre", miroir=True)
el(w("Il m") - 0.05, w("Mais est") - 0.05, '<img src="assets/img/grilou-gene.png" style="width:300px;display:block">', G, Y + 20, kind=None, anim="net")
pill(w("prochaine") - 0.05, w("Mais est") - 0.05, "−1 tasse = −12 € sur ta paie", C, 520, c="rouge", kind="pop")
fleche(w("prochaine") + 0.1, w("Mais est") - 0.05, D - 120, Y - 210, C + 240, 660, bombe=30)
pill(w("fois", w("paye")) - 0.15, w("Mais est") - 0.05, "la suivante : VIRÉ", C, 625, c="rouge", kind="hit")

# 3. la question
a = w("Mais est"); e = w("Alors") - 0.05
img(a, e, "grilou-question", 360, cx=C, cy=Y, kind="pop")
el(w("droit") - 0.1, e, '<div style="font-family:Lilita;font-size:150px;color:#ffd93b;-webkit-text-stroke:10px #15121f;paint-order:stroke fill">?</div>', C + 230, Y - 250, kind="boing", flotte=False)
pill(a + 0.3, e, "il a le droit ?", C, 560, kind=None)

# 4. la fiche de paie (reste à l'écran jusqu'à « exactement ça »)
a = w("Alors"); eF = w("Et ça") - 0.05
FP = ('<div class="papier" style="width:740px"><div class="entete"><span>FICHE DE PAIE · GRILOU, BARISTA</span><span>NOVEMBRE</span></div>'
      '<div class="ligne"><span>Salaire net</span><span>1 450,00 €</span></div>'
      '<div class="ligne rouge" id="lret"><span>Retenue : tasse cassée</span><span>−12,00 €</span></div>'
      '<div class="ligne net"><span>Net à payer</span><span id="netp">1 438,00 €</span></div></div>')
fp = el(a, eF, FP, C, 820, kind="cadre", flotte=False, eclat=True)
tw("#lret", "opacity:0, x:-40", "opacity:1, x:0", w("paye", a) - 0.05, 0.3)
lab(w("paye", a), w("Article") - 0.05, "LA <i>FICHE DE PAIE</i>", cy=560, fs=54)
deplace(fp, w("Article") - 0.05, x=-245, y=-150, s=0.52)
AR = ('<div class="papier" style="width:680px"><div class="entete"><span>CODE DU TRAVAIL</span><span class="vig">EN VIGUEUR</span></div>'
      '<div style="font-size:46px;margin-bottom:10px">Article L1331-2</div>'
      f'<div id="artx" style="font-size:44px;line-height:1.25">{lettres("Les amendes ou autres sanctions pécuniaires ")}<span class="surl" id="artsu">{lettres("sont interdites.")}</span></div>'
      '<div id="annot" style="font-family:Marker;color:#d0242b;font-size:36px;margin-top:12px;transform:rotate(-3deg);opacity:0">→ même pour une tasse</div></div>')
ar = el(w("Article") + 0.05, eF, AR, C + 90, 930, anim="droite", kind="slide", flotte=False, eclat=True)
tape("#artx", w("les amendes"), 1.8)
surligne("#artsu", w("interdites") - 0.05)
tw("#annot", "opacity:0, x:-20", "opacity:1, x:0", w("interdites") + 0.4, 0.3)
deplace(ar, w("Me retirer") - 0.05, x=150, y=170, s=0.6)
JS.append(f'tl.to("#{ar}", {{opacity:0.35, duration:0.3}}, {round(w("Me retirer"), 2)});')
deplace(fp, w("Me retirer") - 0.05, x=0, y=-60, s=1.0)
fleche(w("exactement") - 0.4, eF, C + 250, 1080, C + 200, 820, bombe=60, couleur="#ffd93b")
tampon(w("exactement") - 0.1, eF, "INTERDIT", cx=C + 170, cy=775, fs=56)
JS.append(f'tl.to("#lret", {{textDecoration:"line-through", opacity:0.5, duration:0.1}}, {round(w("exactement"), 2)});')
JS.append(f'(() => {{ const o = {{v:1438}}, e = document.getElementById("netp"); tl.fromTo(o, {{v:1438}}, {{v:1450, duration:0.6, ease:"power2.out", immediateRender:false, onUpdate:() => {{ e.textContent = Math.round(o.v).toLocaleString("fr-FR") + ",00 €"; }}}}, {round(w("exactement") + 0.2, 2)}); }})();')

# 5. l'amende : pour le patron
a = w("Et ça"); e = w("Mais c") - 0.05
AM = '<div class="verre" style="width:560px;text-align:center"><div class="tt">sanction pour l\'employeur</div><div style="font-size:120px;color:#ff6b75;line-height:1">jusqu\'à<br><span id="amn">0</span> €</div></div>'
el(a + 0.05, e, AM, C - 90, 740, kind="hit", flotte=False, eclat=True)
JS.append(f'(() => {{ const o = {{v:0}}, e = document.getElementById("amn"); tl.fromTo(o, {{v:0}}, {{v:3750, duration:0.8, ease:"power2.out", immediateRender:false, onUpdate:() => {{ e.textContent = Math.round(o.v).toLocaleString("fr-FR"); }}}}, {round(w("3750") - 0.2, 2)}); }})();')
img(w("3750") + 0.3, e, "patron-bras", 270, cx=D + 40, cy=1090, anim="droite", kind="pop")
pill(w("3750") + 0.5, e, "pour lui →", D - 290, 1090, c="rouge", kind="pop")

# 6. « c'est bien moi qui ai cassé la vaisselle, non ? »
a = w("Mais c"); e = w("Eh ben") - 0.04
img(a, e, "grilou-gene", 360, cx=G + 40, cy=Y, kind="pop")
img(a + 0.3, e, "tasse-tombe", 230, cx=D - 20, cy=Y + 60, anim="bas", kind=None)
pill(a + 0.6, e, "c'est moi qui l'ai cassée…", C, 560, kind=None)

# 7. l'échelle des fautes, faite maison
a = w("Eh ben"); e = w("Une tasse", w("employeur")) - 0.05
rows = [("Faute simple", "simple"), ("Faute grave", "grave"), ("Faute lourde", "lourde")]
EC = '<div class="verre" style="width:700px"><div class="tt">payer de sa poche ?</div>' + "".join(
    f'<div id="r{k}" style="display:flex;justify-content:space-between;align-items:center;font-size:52px;padding:18px 14px;border-radius:16px;margin-top:8px;background:rgba(255,255,255,.05)">'
    f'<span>{n}</span><span id="m{k}" class="{"rond-ok" if k == "lourde" else "rond-ko"}" style="opacity:0">{"✔" if k == "lourde" else "✖"}</span></div>' for n, k in rows) + '</div>'
el(a + 0.1, e, EC, C, 800, kind="cadre", flotte=False)
tw("#msimple", "opacity:0, scale:0.3", "opacity:1, scale:1", w("salarié") + 0.1, 0.25, "back.out(2)"); tw("#mgrave", "opacity:0, scale:0.3", "opacity:1, scale:1", w("salarié") + 0.45, 0.25, "back.out(2)")
son(w("salarié") + 0.1, "check"); son(w("salarié") + 0.45, "check")
JS.append(f'tl.to("#rlourde", {{background:"rgba(255,217,59,.22)", boxShadow:"0 0 0 4px #ffd93b", duration:0.25}}, {round(w("faute lourde") - 0.05, 2)});')
tw("#mlourde", "opacity:0, scale:0.3", "opacity:1, scale:1", w("lourde") + 0.05, 0.3, "back.out(2.5)"); son(w("lourde"), "ding")
pill(w("dire", a) - 0.3, e, "= vouloir nuire au patron", C, 1130, c="jaune", kind="pop")

# 8. un accident, pas une intention de nuire
a = w("Une tasse", w("employeur")); e = w("La casse") - 0.05
img(a, e, "grilou-lache", 380, cx=G + 30, cy=Y, kind="pop")
pill(a + 0.5, e, "accident", D - 20, 700, c="vert", kind="pop")
pill(w("pas", a) - 0.1, e, "<span class='rond-ko'>✖</span>intention de nuire", C + 150, 1110, c="rouge", kind="pop")
# 9. le risque de l'entreprise
a = w("La casse"); e = w("Et alors") - 0.05
img(a, e, "tasse-tombe", 220, cx=G, cy=Y + 40, kind="pop")
img(a + 0.25, e, "patron-bras", 330, cx=D, cy=Y, anim="droite", kind="cadre")
fleche(w("risque") - 0.3, e, G + 110, Y - 40, D - 150, Y - 60, bombe=80, couleur="#ffd93b")
pill(a + 0.5, e, "risque de l'entreprise", C, 560, c="jaune", kind="pop")

# 10. et me virer ?
a = w("Et alors"); e = w("Eh ben pour") - 0.04
img(a, e, "grilou-desespoir", 380, cx=C, cy=Y, kind="pop")
pill(a, e, "et me virer ?", C, 560, c="rouge", kind="pop")

# 11. la procédure : 3 étapes qui s'allument
a = w("Eh ben pour"); e = w("Quatre") - 0.05
lab(a, e, "POUR <i>LICENCIER</i>", cy=560, fs=56)
ICO = {"cause": '<svg viewBox="0 0 64 64" width="96" height="96"><path d="M32 8v44M14 52h36M12 20h40M18 20l-8 16h16zM46 20l-8 16h16z" fill="none" stroke="#ffd93b" stroke-width="4" stroke-linejoin="round"/></svg>',
       "entretien": '<svg viewBox="0 0 64 64" width="96" height="96"><circle cx="20" cy="22" r="8" fill="#cfc9ff"/><circle cx="44" cy="22" r="8" fill="#cfc9ff"/><path d="M6 50c2-12 26-12 28 0M30 50c2-12 26-12 28 0" fill="#cfc9ff"/></svg>',
       "lettre": '<svg viewBox="0 0 64 64" width="96" height="96"><rect x="8" y="14" width="48" height="36" rx="4" fill="none" stroke="#fff" stroke-width="4"/><path d="M8 18l24 18 24-18" fill="none" stroke="#fff" stroke-width="4"/></svg>'}
ET = [("cause", "Cause réelle<br>et sérieuse", w("cause")), ("entretien", "Entretien<br>préalable", w("entretien")), ("lettre", "Lettre de<br>licenciement", w("lettre"))]
for k, (n, txt, t) in enumerate(ET):
    el(t - 0.1, e, f'<div class="verre" style="width:262px;height:320px;text-align:center;font-size:38px;padding:20px 12px">{ICO[n]}<div style="margin-top:12px">{txt}</div></div>', C - 280 + 280 * k, 820, kind="pop", flotte=False)
    if k: fleche(t - 0.15, e, C - 280 + 280 * (k - 1) + 120, 990, C - 280 + 280 * k - 120, 990, bombe=-30, d=0.25)

# 12. quatre tasses par maladresse : la jauge « faute sérieuse ? »
a = w("Quatre"); e = w("Et s") - 0.05
img(a, e, "tasses-1234", 520, cx=C, cy=610, kind="pop")
JA = ('<div class="verre" style="width:560px;text-align:center"><div class="tt">faute sérieuse ?</div>'
      '<svg viewBox="0 0 200 110" width="440" height="242"><path d="M20 100 A80 80 0 0 1 180 100" fill="none" stroke="#2fb860" stroke-width="18"/>'
      '<path d="M100 20 A80 80 0 0 1 180 100" fill="none" stroke="#e5242b" stroke-width="18"/><g id="aig" transform="rotate(10 100 100)"><path d="M100 100 L100 32" stroke="#fff" stroke-width="7" stroke-linecap="round"/></g><circle cx="100" cy="100" r="9" fill="#fff"/></svg>'
      '<div style="display:flex;justify-content:space-between;font-size:30px;margin-top:-6px"><span style="color:#8ff0b8">maladresse</span><span style="color:#ff9aa4">faute</span></div></div>')
el(w("ça ressemble") - 0.1, e, JA, C, 1000, kind="cadre", flotte=False)
JS.append(f'(() => {{ const o = {{a:10}}, g = document.getElementById("aig"); tl.fromTo(o, {{a:10}}, {{a:-55, duration:0.7, ease:"back.out(1.6)", immediateRender:false, onUpdate:() => g.setAttribute("transform", `rotate(${{o.a}} 100 100)`)}}, {round(w("rarement") - 0.1, 2)}); }})();')
pill(w("ça ressemble") + 0.4, e, "rarement", C, 765, c="vert", kind="pop")

# 13. les prud'hommes
a = w("Et s"); e = w("Serveur") - 0.05
img(a + 0.1, w("prud") - 0.05, "grilou-reflechit", 300, cx=C, cy=Y, kind="pop")
img(w("prud") - 0.15, e, "prudhommes", 520, cx=C, cy=Y - 20, kind="cadre")
rangee(e, [(w("gratuit") - 0.1, "<span class='rond-ok'>✔</span>0 € · gratuit", "vert"), (w("obligatoire") - 0.5, "<span class='rond-ok'>✔</span>avocat facultatif", "vert")], 1160)

# 14. pour tout le monde + les deux cartes de fin
a = w("Serveur"); e = LEN - 0.02
rangee(e, [(w(m, a) - 0.05, f"<span class='rond-ok'>✔</span>{m}", "vert") for m in ["serveur", "plongeur", "caissier"]], 560, fs=40)
CA = lambda im, txt, coul: f'<div class="verre" style="width:330px;height:470px;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;padding:18px"><img src="assets/img/{im}.png" style="width:270px;margin-bottom:16px"><div class="pill {coul}" style="font-size:30px">{txt}</div></div>'
el(w("lacasse", a) - 0.1, e, CA("grilou-tasse", "LA TASSE", "vert"), C - 180, 880, kind="cadre", flotte=False)
el(w("patron", a) - 0.15, e, CA("patron-bras", "LA CASSE", "rouge"), C + 180, 880, anim="droite", kind="cadre", flotte=False)
pill(w("patron", a) - 0.1, e, "c'est au patron d'assumer", C, 1180, c="jaune", kind="pop")

# --- vie en plus (13/11, « trop statique ») : rien ne bouge côté persos, ce sont les objets et effets qui vivent
import random; rd = random.Random(3)
def pluie(t0, t1, n, x0, x1, y0, y1, html):
    # objets qui tombent en boucle derrière une carte (pièces, éclats…)
    for k in range(n):
        _n[0] += 1; i = f"pl{_n[0]}"; x = rd.randint(x0, x1); d = rd.uniform(1.1, 1.8); dl = rd.uniform(0, d)
        H.append(f'<div id="{i}" style="position:absolute;left:{x}px;top:{y0}px;opacity:0;z-index:4">{html}</div>')
        rep = max(0, int((t1 - t0 - dl) / d) - 1)
        JS.append(f'tl.fromTo("#{i}", {{y:0, rotation:0, opacity:0}}, {{keyframes:[{{opacity:1, duration:{d * .15:.2f}}}, {{opacity:1, duration:{d * .6:.2f}}}, {{opacity:0, duration:{d * .25:.2f}}}], y:{y1 - y0}, rotation:{rd.choice([-1, 1]) * rd.randint(120, 300)}, duration:{d:.2f}, ease:"power1.in", repeat:{rep}, immediateRender:false}}, {round(t0 + dl, 2)});')
PIECE = '<svg width="54" height="54" viewBox="0 0 54 54"><circle cx="27" cy="27" r="24" fill="#f2c12e" stroke="#9a6c00" stroke-width="4"/><text x="27" y="36" text-anchor="middle" font-family="Lilita" font-size="26" fill="#7a5a00">€</text></svg>'
ECLAT = '<svg width="34" height="28" viewBox="0 0 34 28"><path d="M2 20 L14 2 L32 10 L22 26 Z" fill="#e9dcc3" stroke="#8a7a60" stroke-width="2"/></svg>'
# pièces qui tombent pendant l'amende
pluie(w("3750") - 0.1, w("Mais c") - 0.05, 12, 180, 860, 480, 1250, PIECE)
# éclats de tasse qui retombent quand la tasse casse et quand on parle de la casse accidentelle
pluie(w("cassé"), w("Mon patron") - 0.05, 7, 300, 760, 640, 1200, ECLAT)
pluie(w("La casse"), w("Et alors") - 0.05, 6, 160, 480, 760, 1220, ECLAT)
# les 4 cases tremblent sur « quatrième »
JS.append(f'tl.to(".ic .verre", {{x:"+=6", duration:0.05, repeat:7, yoyo:true}}, {round(w("quatrième"), 2)});')
# le point d'interrogation se balance
sous_titres(["quatrième", "virer", "droit", "paye", "L1331", "interdites", "3750", "euros", "lourde", "nuire", "risque", "licencier", "cause", "réelle", "sérieuse",
             "entretien", "lettre", "rarement", "prud", "hommes", "gratuit", "obligatoire", "patron", "assumer"], fin=LEN + 0.05)
finir("barista", like=round(153.61 - 151.92, 2), fond="assets/img/fond-cafe.jpg")
