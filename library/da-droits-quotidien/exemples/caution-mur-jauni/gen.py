# « Mon proprio garde ma caution pour un mur jauni » — même DA que barista-tasses (fond décor, petits persos, schémas maison, infos qui s'accumulent).
# python -I detoure.py ; python -I ../_outils/voix_ref.py ; python -I gen.py ; render ; python -I ../_outils/mix_ref.py caution-mur-jauni.mp4
import sys; sys.path.insert(0, "../_outils")
from da_pro import *
from da_pro import _n
import random; rd = random.Random(5)
G, D, Y = 300, 760, 900
def pluie(t0, t1, n, x0, x1, y0, y1, html):
    for k in range(n):
        _n[0] += 1; i = f"pl{_n[0]}"; x = rd.randint(x0, x1); d = rd.uniform(1.1, 1.8); dl = rd.uniform(0, d)
        H.append(f'<div id="{i}" style="position:absolute;left:{x}px;top:{y0}px;opacity:0;z-index:4">{html}</div>')
        rep = max(0, int((t1 - t0 - dl) / d) - 1)
        JS.append(f'tl.fromTo("#{i}", {{y:0, rotation:0, opacity:0}}, {{keyframes:[{{opacity:1, duration:{d * .15:.2f}}}, {{opacity:1, duration:{d * .6:.2f}}}, {{opacity:0, duration:{d * .25:.2f}}}], y:{y1 - y0}, rotation:{rd.choice([-1, 1]) * rd.randint(120, 300)}, duration:{d:.2f}, ease:"power1.in", repeat:{rep}, immediateRender:false}}, {round(t0 + dl, 2)});')
PIECE = '<svg width="54" height="54" viewBox="0 0 54 54"><circle cx="27" cy="27" r="24" fill="#f2c12e" stroke="#9a6c00" stroke-width="4"/><text x="27" y="36" text-anchor="middle" font-family="Lilita" font-size="26" fill="#7a5a00">€</text></svg>'
OK, KO = "<span class='rond-ok'>✔</span>", "<span class='rond-ko'>✖</span>"
def compteur_js(idd, de, a, t, suf="", d=0.8):
    JS.append(f'(() => {{ const o = {{v:{de}}}, e = document.getElementById("{idd}"); tl.fromTo(o, {{v:{de}}}, {{v:{a}, duration:{d}, ease:"power2.out", immediateRender:false, onUpdate:() => {{ e.textContent = Math.round(o.v).toLocaleString("fr-FR") + "{suf}"; }}}}, {round(t, 2)}); }})();')

# 1. les clés rendues après 3 ans
e = w("Un mois") - 0.05
img(0.0, e, "grilou-cles", 380, cx=G + 20, cy=Y, anim="net", kind=None)
img(w("studio") - 0.3, e, "immeuble", 300, cx=D, cy=Y - 10, anim="droite", kind="pop")
pill(w("3") - 0.2, e, "3 ans dans ce studio", C, 560, c="jaune", kind="pop")
# 2. un mois, deux… toujours pas de caution
a = w("Un mois"); e = w("appelle") - 0.05
img(a, e, "grilou-question", 340, cx=G, cy=Y, kind="pop")
img(a + 0.2, e, "sablier", 170, cx=D + 40, cy=Y - 40, kind=None)
CAL = ('<div class="verre" style="width:420px"><div class="tt">depuis la remise des clés</div>'
       '<div style="display:flex;gap:14px;justify-content:center;font-size:38px">'
       '<div id="mo1" style="padding:14px 18px;border-radius:14px;background:rgba(255,255,255,.08);opacity:.25">mois 1</div>'
       '<div id="mo2" style="padding:14px 18px;border-radius:14px;background:rgba(255,255,255,.08);opacity:.25">mois 2</div></div></div>')
el(a + 0.05, e, CAL, C, 560, kind="cadre", flotte=False)
tw("#mo1", "opacity:.25", "opacity:1", a + 0.2, 0.25); tw("#mo2", "opacity:.25", "opacity:1", w("deux") - 0.1, 0.25); son(w("deux") - 0.1, "check")
pill(w("toujours") - 0.2, e, "caution rendue : 0 €", C + 60, 1150, c="rouge", kind="hit")
# 3. le coup de fil
a = w("appelle"); e = w("Première") - 0.05
img(a, e, "grilou-gene", 330, cx=G, cy=Y + 10, kind="pop")
img(a + 0.15, e, "proprio-bras", 330, cx=D, cy=Y, anim="droite", kind="cadre")
pill(w("murs") - 0.3, e, "« les murs ont jauni »", C, 510, kind="pop")
pill(w("garde") - 0.2, e, "« je garde les 600 € »", C, 600, c="rouge", kind="pop")
img(w("600") - 0.1, e, "billets", 230, cx=C, cy=1150, kind="hit")
fleche(w("600") + 0.1, e, C + 60, 1100, D - 60, 1080, bombe=50, couleur="#ff6b75")
# 4. erreur n°1 : le délai
a = w("Première"); eD = w("Deuxième") - 0.05
lab(a, w("Loi") - 0.05, "ERREUR N°1 : <i>LE DÉLAI</i>", cy=560, fs=52, c="rouge", kind="hit")
img(a + 0.2, w("Loi") - 0.05, "sablier", 250, cx=C, cy=Y, kind="pop")
LOI = ('<div class="papier" style="width:700px"><div class="entete"><span>LOI DU 6 JUILLET 1989</span><span class="vig">EN VIGUEUR</span></div>'
       '<div style="font-size:46px;margin-bottom:10px">Article 22</div>'
       f'<div id="loix" style="font-size:40px;line-height:1.25">{lettres("Dépôt de garantie rendu sous ")}<span class="surl" id="l1m">{lettres("1 mois")}</span>{lettres(" si l’état des lieux est conforme, ")}<span class="surl" id="l2m">{lettres("2 mois")}</span>{lettres(" sinon.")}</div></div>')
lo = el(w("Loi"), eD, LOI, C, 800, kind="slide", anim="droite", flotte=False, eclat=True)
tape("#loix", w("Si", w("Loi")) - 0.1, 2.6)
surligne("#l1m", w("un mois", w("Loi")) - 0.05); surligne("#l2m", w("deux mois") - 0.05)
# frise sous la loi : remise des clés → 1 mois / 2 mois max
deplace(lo, w("il a un") - 0.1, y=-200, s=0.78)
FR = ('<div class="verre" style="width:760px"><div class="tt">le délai pour rendre la caution</div>'
      '<div style="display:flex;align-items:center;gap:14px;font-size:34px;justify-content:center">'
      '<div class="pill" style="font-size:32px">🔑 clés rendues</div><span style="font-size:44px">→</span>'
      '<div style="display:flex;flex-direction:column;gap:12px"><div id="fr1" class="pill vert" style="font-size:32px;opacity:0">1 mois · conforme</div>'
      '<div id="fr2" class="pill rouge" style="font-size:32px;opacity:0">2 mois max · dégâts</div></div></div></div>')
el(w("il a un") - 0.05, eD, FR, C, 1030, kind="cadre", flotte=False)
tw("#fr1", "opacity:0, x:-30", "opacity:1, x:0", w("il a un") + 0.2, 0.3); son(w("il a un") + 0.2, "check")
tw("#fr2", "opacity:0, x:-30", "opacity:1, x:0", w("dégâts") - 0.3, 0.3); son(w("dégâts") - 0.3, "check")
# 5. erreur n°2 : les murs → vétusté
a = w("Deuxième"); e = w("Et la vétusté") - 0.05
lab(a, e, "ERREUR N°2 : <i>LES MURS</i>", cy=530, fs=50, c="rouge", kind="hit")
img(a + 0.15, e, "mur-jauni", 330, cx=G + 20, cy=Y + 20, kind="pop")
VE = ('<div class="verre" style="width:400px"><div class="tt">3 ans de vie normale</div>'
      '<div style="height:34px;border-radius:20px;background:rgba(255,255,255,.1);overflow:hidden"><div id="vbar" style="height:100%;width:0%;border-radius:20px;background:linear-gradient(90deg,#f5f0e6,#e3c25a)"></div></div>'
      '<div style="display:flex;justify-content:space-between;font-size:28px;margin-top:8px;color:#cfc9ff"><span>an 0</span><span>an 3</span></div></div>')
el(w("Après", w("Deuxième")) - 0.05, e, VE, D - 30, 780, kind="cadre", flotte=False)
JS.append(f'tl.fromTo("#vbar", {{width:"0%"}}, {{width:"100%", duration:1.4, ease:"power1.inOut", immediateRender:false}}, {round(w("Après", w("Deuxième")) + 0.1, 2)});')
pill(w("vétusté") - 0.3, e, "= la vétusté", D - 30, 980, c="jaune", kind="pop")
pill(w("usure") - 0.2, e, "usure normale du temps", D - 60, 1090, kind="pop")
# 6. jamais retenue au locataire : usure ≠ dégât
a = w("Et la vétusté"); e = w("Pour chaque") - 0.05
CA = lambda im, txt, coul: f'<div class="verre" style="width:330px;height:430px;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;padding:18px"><img src="assets/img/{im}.png" style="width:250px;margin-bottom:16px"><div class="pill {coul}" style="font-size:30px">{txt}</div></div>'
el(a, e, CA("mur-jauni", OK + "usure : 0 €", "vert"), C - 180, 830, kind="cadre", flotte=False)
el(a + 0.4, e, CA("mur-trou", KO + "dégât : payant", "rouge"), C + 180, 830, anim="droite", kind="cadre", flotte=False)
lab(w("jamais") - 0.2, e, "JAMAIS AU <i>LOCATAIRE</i>", cy=540, fs=52)
# 7. les justificatifs
a = w("Pour chaque"); e = w("et voilà") - 0.05
img(a, e, "documents", 300, cx=C - 170, cy=Y - 10, kind="cadre")
img(a + 0.3, e, "grilou-loupe", 320, cx=D, cy=Y + 20, anim="droite", kind=None)
lab(a, e, "CHAQUE RETENUE = <i>UNE PREUVE</i>", cy=540, fs=46)
rangee(e, [(w("justificatifs") + 0.3, "devis", "jaune"), (w("factures") - 0.1, "factures", "jaune"), (w("photos") - 0.1, "photos", "jaune")], 1160, fs=40)
# 8. la meilleure partie : 10 % par mois de retard
a = w("et voilà"); e = w("2 mois") - 0.05
img(a, e, "grilou-victoire", 320, cx=G, cy=Y + 20, kind="boing")
pill(a + 0.1, e, "la meilleure partie", C, 520, c="jaune", kind="pop")
PE = ('<div class="verre" style="width:440px;text-align:center"><div class="tt">par mois de retard commencé</div>'
      '<div style="font-size:34px;color:#cfc9ff">10 % du loyer hors charges</div>'
      '<div style="font-size:96px;color:#8ff0b8;line-height:1.05">+<span id="pen">0</span> €</div><div style="font-size:28px;color:#cfc9ff">(loyer 600 €)</div></div>')
el(w("Chaque", w("voilà")) - 0.05, e, PE, D - 40, 820, kind="cadre", flotte=False)
compteur_js("pen", 0, 60, w("10") - 0.1)
img(w("verser") - 0.6, e, "proprio-hausse", 300, cx=D - 30, cy=1110, anim="bas", kind="pop")
pluie(w("10"), e, 7, 560, 920, 650, 1200, PIECE)
# 9. 2 mois et 5 jours = 3 mois → 180 €
a = w("2 mois"); e = w("Alors") - 0.05
CL = ('<div class="verre" style="width:700px"><div class="tt">mon retard</div><div style="display:flex;gap:16px;justify-content:center;font-size:36px">'
      + "".join(f'<div id="c{k}" style="width:190px;padding:16px 0;text-align:center;border-radius:16px;background:rgba(255,255,255,.07);opacity:.3">{t}</div>' for k, t in enumerate(["mois 1", "mois 2", "+ 5 jours"]))
      + '</div><div style="text-align:center;font-size:34px;margin-top:14px;color:#ffe27a;opacity:0" id="c3t">= 3 mois commencés</div></div>')
el(a, e, CL, C, 600, kind="cadre", flotte=False)
for k, t in enumerate([a + 0.1, w("et 5") - 0.2 if True else a, w("jours") - 0.1]):
    tw(f"#c{k}", "opacity:.3", "opacity:1, background:'rgba(255,217,59,.22)'", t, 0.25); son(t, "check")
tw("#c3t", "opacity:0, y:10", "opacity:1, y:0", w("3 mois") - 0.2, 0.3)
TO = ('<div class="verre" style="width:640px;text-align:center"><div class="tt">ce qu’il me doit</div>'
      '<div style="font-size:58px">600 € <span style="color:#cfc9ff">+</span> <span style="color:#8ff0b8">3 × 60 €</span></div>'
      '<div style="font-size:110px;color:#8ff0b8;line-height:1.05"><span id="tot">600</span> €</div></div>')
el(w("soit") - 0.1, e, TO, C, 1040, kind="hit", flotte=False, eclat=True)
compteur_js("tot", 600, 780, w("180") - 0.1)
pluie(w("180"), e, 9, 200, 880, 760, 1250, PIECE)
# 10. la lettre recommandée
a = w("Alors"); e = w("Et si") - 0.05
img(a, e, "grilou-ordi", 320, cx=G - 20, cy=1080, kind="pop")
LE = ('<div class="papier" style="width:640px"><div class="entete"><span>LETTRE RECOMMANDÉE A/R</span><span>À MON PROPRIO</span></div>'
      '<div style="font-size:36px;margin-bottom:8px">Objet : ma caution</div>'
      + "".join(f'<div id="lt{k}" class="ligne" style="opacity:0;justify-content:flex-start;gap:14px;font-size:38px"><span class="rond-ok">✔</span><span>{t}</span></div>' for k, t in enumerate(["Délai dépassé", "Vétusté non imputable", "Pénalités dues"])) + '</div>')
el(a + 0.1, e, LE, C + 80, 720, anim="droite", kind="cadre", flotte=False)
for k, t in enumerate([w("dépassé") - 0.4, w("imputable") - 0.4, w("due") - 0.4]):
    tw(f"#lt{k}", "opacity:0, x:-30", "opacity:1, x:0", t, 0.3); son(t, "check")
img(w("recommandée") - 0.3, e, "lettre", 220, cx=D + 20, cy=1110, kind="pop")
# 11. la commission de conciliation
a = w("Et si"); e = w("Locataire", w("conciliation")) - 0.05
img(a + 0.1, e, "tribunal", 420, cx=C, cy=Y - 40, kind="cadre")
img(w("commission") - 0.3, e, "balance", 200, cx=D + 20, cy=Y + 130, kind="pop")
lab(a, e, "SI ÇA <i>BLOQUE</i>", cy=530, fs=56)
rangee(e, [(w("gratuitement") - 0.1, OK + "gratuit", "vert"), (w("commission") - 0.1, "commission de conciliation", "jaune")], 1160, fs=38)
# 12. fin : c'est le temps
a = w("Locataire", w("conciliation")); e = w("Y") - 0.05 if False else w("beaucoup") - 0.4
el(a, e, CA("mur-jauni", "LE MUR", "vert"), C - 180, 830, kind="cadre", flotte=False)
el(w("vieillit") - 0.2, e, CA("sablier", "LE TEMPS", "jaune"), C + 180, 830, anim="droite", kind="cadre", flotte=False)
pill(w("faute") - 0.3, e, "pas votre faute", C, 1150, c="vert", kind="pop")
a = w("beaucoup") - 0.35; e = LEN - 0.02
img(a, e, "grilou-debout", 300, cx=C, cy=Y, kind="pop")
pill(a + 0.1, e, "trop de gens se font avoir", C, 560, c="rouge", kind="hit")

sous_titres(["3", "ans", "caution", "jauni", "600", "délai", "1989", "22", "mois", "dégâts", "murs", "vétusté", "usure", "jamais", "locataire", "justificatifs", "factures", "photos",
             "meilleure", "10", "retard", "180", "recommandée", "imputable", "gratuitement", "conciliation", "faute", "temps", "avoir"], fin=LEN + 0.05)
finir("caution", like=round(116.47 - 115.24, 2), fond="assets/img/fond-appart.jpg")
