# Détoure chaque élément de la planche fournie (fond noir) → assets/img/<nom>.png (transparent, ×2). python -I detoure.py
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
B = {"grilou-debout": (0, 0, 240, 535), "grilou-sourire": (285, 0, 515, 250), "grilou-question": (560, 0, 790, 250), "grilou-gene": (810, 0, 1050, 250),
     "grilou-desespoir": (1055, 0, 1300, 250), "grilou-tasse": (1320, 0, 1536, 250), "grilou-lache": (225, 250, 505, 525), "tasse-tombe": (490, 295, 656, 520),
     "patron-bras": (720, 250, 905, 525), "patron-crie": (910, 255, 1195, 525), "patron-grilou": (1205, 250, 1536, 525), "tasses-1234": (10, 545, 470, 712),
     "fiche-paie": (475, 530, 780, 745), "code-travail": (775, 525, 1025, 765), "article": (1000, 525, 1320, 745), "amende": (1318, 545, 1536, 710),
     "echelle-fautes": (0, 740, 285, 965), "grilou-reflechit": (280, 740, 470, 1024), "chemin-licenciement": (485, 755, 945, 1024),
     "prudhommes": (950, 735, 1262, 1024), "grilou-victoire": (1260, 735, 1536, 1024)}
im = Image.open("src/assets-planche.webp").convert("RGB")
for nom, b in B.items():
    c = im.crop(b); A = np.asarray(c).astype(int); mx = A.max(2)
    m = mx > 16
    m = ndimage.binary_opening(m, iterations=1); m = ndimage.binary_closing(m, iterations=2); m = ndimage.binary_fill_holes(m)
    lab, n = ndimage.label(m); taille = ndimage.sum(m, lab, range(1, n + 1))
    garde = np.isin(lab, [i + 1 for i, t in enumerate(taille) if t >= max(120, 0.004 * m.size, 0.012 * taille.max())])
    if nom == "grilou-lache":   # on garde la main et sa tasse, pas la tasse qui tombe de l'élément voisin
        sl = ndimage.find_objects(lab)
        garde &= ~np.isin(lab, [i + 1 for i, q in enumerate(sl) if q is not None and q[1].start > 258])
    # 13/11 : tout morceau qui touche le bord du cadre et qui est petit vient d'un élément voisin → supprimé
    sl = ndimage.find_objects(lab); H_, W_ = m.shape
    bord = [i + 1 for i, q in enumerate(sl) if q is not None and (q[0].start == 0 or q[1].start == 0 or q[0].stop == H_ or q[1].stop == W_) and taille[i] < 0.15 * taille.max()]
    garde &= ~np.isin(lab, bord)
    # morceaux voisins repérés à l'œil sur la planche de contrôle (13/11)
    EXCL = {"tasse-tombe": lambda q: q[1].stop < 30, "prudhommes": lambda q: q[0].stop < 40 or q[1].start > 285}
    if nom in EXCL:
        garde &= ~np.isin(lab, [i + 1 for i, q in enumerate(sl) if q is not None and EXCL[nom](q)])
    al = Image.fromarray((garde * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    # adoucit le bord sombre : l'alpha suit la luminosité sur le liseré
    a = np.minimum(np.asarray(al).astype(float), np.where(ndimage.binary_erosion(garde, iterations=2), 255, np.clip(mx * 6, 0, 255)))
    o = c.convert("RGBA"); o.putalpha(Image.fromarray(a.astype(np.uint8)))
    bb = o.getbbox(); o = o.crop(bb)
    o = o.resize((o.width * 2, o.height * 2), Image.LANCZOS)
    o.save(f"assets/img/{nom}.png"); print(nom, o.size)
# planche de contrôle sur fond gris
T = [(n, Image.open(f"assets/img/{n}.png")) for n in B]
W = 6; S = 300; P = Image.new("RGB", (W * S, ((len(T) - 1) // W + 1) * S), (90, 90, 110))
for k, (n, i) in enumerate(T):
    i = i.copy(); i.thumbnail((S - 10, S - 10)); P.paste(i, ((k % W) * S + 5, (k // W) * S + 5), i)
P.save("fz/detoure.jpg")
