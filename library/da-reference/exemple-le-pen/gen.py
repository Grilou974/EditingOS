# « La France, pays le moins raciste du monde ? » — DA de référence (GBH). Fonds libres (Commons + Pexels, bg.py).
# python -I ../_outils/voix_ref.py ; python -I gen.py ; python -I bg.py ; chevauchements ; render ; python -I ../_outils/mix_ref.py le-pen-moins-raciste.mp4
import sys; sys.path.insert(0, "../_outils")
from da_ref import *
titre(w("et oui") - 0.05, "La France, pays le moins<br>raciste du monde ?")

# Marine Le Pen sur CBS (gros plan photo, pas de chat)
a = w("et oui"); e = w("Elle a dit") - 0.04
img1(w("Marine") - 0.1, e, "lepen.jpg", 520, 760, kind="photo", leg="Marine Le Pen")
date(w("américaine") - 0.6, e, "8 NOV. 2026", cy=300, sub="sur CBS, aux États-Unis")
a = w("Elle a dit"); e = w("Alors") - 0.04
rapport(a + 0.1, e, "selon la traduction de CBS", "« Le pays le moins raciste du monde »", 400, fs=38)
tampon(w("discrimination") - 0.5, e, "« PAS DE DISCRIMINATION »", cy=640, fs=50)
a = w("Alors"); e = w("Fin") - 0.04
lab(a, e, "ALORS J'AI REGARDÉ <i>LES CHIFFRES</i>", cy=350, fs=46, flou=False)

# l'étude
a = w("Fin"); e = w("Les mêmes") - 0.04
date(a, e, "FIN 2021", cy=300)
rapport(w("ministère") - 0.1, e, "Ministère du Travail (Dares)", "Une étude par testing", 520, fs=48)
compteur(w("10") - 0.2, e, 0, 10000, "", 760, fs=130, pre="≈ ")
lab(w("candidatures") - 0.1, e, "<i>CANDIDATURES</i> ENVOYÉES", cy=900, fs=40, kind=None)

# deux CV identiques, seul le nom change
a = w("Les mêmes"); e = w("Résultat") - 0.04
def cv(nom, ident):
    return (f'<div class="papier-cv"><div class="nm" id="{ident}">{nom}</div>'
            '<div class="ln" id="' + ident + 'a">Master — même diplôme</div><div class="ln" id="' + ident + 'b">3 ans d\'expérience</div><div class="ln" id="' + ident + 'c">Mêmes compétences</div></div>')
el(a, e, cv("Thomas Martin", "cv1"), C - 190, 700, kind="cadre")
el(a + 0.15, e, cv("Karim Benali", "cv2"), C + 190, 700, kind="cadre")
for k, mot in enumerate(["diplômes", "expérience"]):
    t = w(mot, a) - 0.2
    for c_ in ("cv1", "cv2"):
        JS.append(f'tl.to("#{c_}{"ab"[k]}", {{backgroundColor:"rgba(47,178,76,.25)", duration:0.2}}, {round(t, 2)});')
    son(t, "check")
JS.append(f'tl.to("#cv1a, #cv2a", {{backgroundColor:"rgba(47,178,76,.25)", duration:0.2}}, {round(a + 0.3, 2)});')
JS.append(f'tl.to("#cv1c, #cv2c", {{backgroundColor:"rgba(47,178,76,.25)", duration:0.2}}, {round(w("expérience", a) + 0.3, 2)});')
t = w("change", a) + 0.25
JS.append(f'tl.to("#cv1, #cv2", {{backgroundColor:"#ffd93b", scale:1.08, duration:0.25}}, {round(t, 2)});'); son(t, "hit")
lab(w("Une seule") - 0.05, e, "SEULE DIFFÉRENCE : <i>LE NOM</i>", cy=1030, fs=42, kind=None)

# résultat : −31,5 %
a = w("Résultat"); e = w("Pour") - 0.04
lab(a, e, "NOM D'ORIGINE <i>MAGHRÉBINE</i>", cy=320, fs=46)
el(w("31") - 0.2, e, '<div class="gros rouge" style="font-size:140px">−<span id="p315">0</span> %</div>', C, 560, kind="hit")
JS.append(f'(() => {{ const o = {{v:0}}, el = document.getElementById("p315"); tl.fromTo(o, {{v:0}}, {{v:31.5, duration:0.8, ease:"power2.out", immediateRender:false, onUpdate:() => {{ el.textContent = o.v.toLocaleString("fr-FR", {{minimumFractionDigits:1, maximumFractionDigits:1}}); }}}}, {round(w("31") - 0.2, 2)}); }})();')
lab(w("chance") - 0.2, e, "DE CHANCES D'ÊTRE <i>RAPPELÉ</i>", cy=760, fs=46, kind=None)

# 1,5 fois plus de candidatures
a = w("Pour"); e = w("Ce n") - 0.04
ENV = '<svg viewBox="0 0 40 30" width="44" height="33"><rect x="1" y="1" width="38" height="28" rx="3" fill="#fff" stroke="#15121f" stroke-width="2"/><path d="M2 3l18 13 18-13" fill="none" stroke="#15121f" stroke-width="2"/></svg>'
for r, (nom, n, y) in enumerate([("Thomas", 10, 520), ("Karim", 15, 700)]):
    el(a + 0.2 + 0.3 * r, e, f'<div class="chip" style="font-size:36px">{nom}</div>', C - 330, y, kind="pop")
    for k in range(n):
        x = C - 200 + (k % 8) * 62; yy = y - 30 + (k // 8) * 62
        el(round(a + 0.4 + 0.3 * r + 0.06 * k, 2), e, ENV, x, yy, kind=None, anim="net")
lab(w("une fois") - 0.1, e, "× 1,5 CANDIDATURES <i>POUR LE MÊME RÉSULTAT</i>", cy=330, fs=36, kind=None)
chip(w("qualifiés") - 0.6, e, "Encore pire sur les emplois peu qualifiés", 900, kind="pop")

# une étude d'État
a = w("Ce n"); e = w("Alors on") - 0.04
chip(a, e, "✖ un ressenti", 480, kind="pop"); chip(w("tweet") - 0.2, e, "✖ un tweet", 600, kind="pop")
tampon(w("étude", a) - 0.2, e, "UNE ÉTUDE D'ÉTAT", cy=780, fs=58)

# aimer son pays (fond net, gros Grilou)
a = w("Alors on"); e = w("Le racisme") - 0.04
lab(a, w("Mais aimer") - 0.04, "ON PEUT AIMER <i>LA FRANCE</i>", cy=350, fs=50, flou=False)
lab(w("Mais aimer"), e, "REGARDER CE QUI <i>NE VA PAS</i>", cy=350, fs=48, flou=False)
tampon(w("pas dire") - 0.1, e, "PAS LE NIER", cy=480, fs=50, flou=False)
a = w("Le racisme"); e = LEN - 0.02
tampon(a, e, "LE RACISME NE DISPARAÎT PAS", cy=350, fs=46, flou=False)
lab(w("décide") - 0.2, e, "QUAND ON <i>FERME LES YEUX</i>", cy=490, fs=44, kind=None, flou=False)

expressions([(0, "c21", "G"), (1.0, "x-wtf", "G"), (w("et oui"), None, None), (w("Alors"), "x-perplexe", "G"), (w("Fin"), "c13", "P"), (w("testing") - 0.2, "x-perplexe", "P"), (w("10") + 0.4, "c19", "P"),
             (w("Les mêmes"), None, None), (w("Résultat"), "x-surpris", "P"), (w("31") - 0.1, "x-wtf", "P"), (w("être", w("31")) - 0.6, "x-enerve", "P"), (w("Pour"), "c28", "P"), (w("une fois") - 0.1, "x-blase", "P"), (w("écart") - 0.1, "x-gene", "P"), (w("qualifiés") - 0.4, "x-enerve", "P"),
             (w("Ce n"), "c13", "P"), (w("étude", w("Ce n")) - 0.2, "c27", "P"), (w("Alors on"), "c25", "G"), (w("aime") - 0.1, "c22", "G"), (w("Mais aimer"), "c19", "G"),
             (w("pas dire") - 0.1, "x-perplexe", "G"), (w("Le racisme"), "x-enerve", "G"), (w("décide") - 0.1, "c30", "G")])
# style des CV
H.append('<style>.papier-cv{width:330px;padding:20px 22px;border-radius:12px;background:#f5f0e6;border:6px solid #15121f;box-shadow:8px 9px 0 #15121f;color:#15121f;font-family:Lilita}'
         '.papier-cv .nm{font-size:38px;padding:6px 10px;border-radius:8px;margin-bottom:10px;text-align:center}.papier-cv .ln{font-size:28px;padding:6px 10px;border-radius:8px;margin-top:6px;background:rgba(0,0,0,.05)}</style>')
finir("le-pen", like=round(103.37 - 100.98, 2))
