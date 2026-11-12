# Planche fournie DÉJÀ transparente : découpe par cadres, suppression des morceaux voisins, ×2 → assets/img/<nom>.png. python -I detoure.py
import numpy as np
from PIL import Image
from scipy import ndimage
B = {"grilou-debout": (6, 0, 200, 400), "grilou-cles": (219, 2, 456, 231), "proprio-bras": (456, 2, 648, 230), "immeuble": (649, 0, 868, 232),
     "grilou-question": (896, 0, 1118, 244), "calendriers": (181, 232, 372, 404), "sablier": (372, 248, 462, 385), "grilou-gene": (462, 232, 655, 412),
     "billets": (640, 255, 790, 405), "mur-jauni": (792, 235, 950, 410), "mur-trou": (955, 240, 1118, 410), "grilou-loupe": (15, 400, 250, 580),
     "photos": (240, 410, 412, 565), "etat-lieux": (418, 412, 552, 572), "etat-lieux-x": (552, 412, 682, 572), "documents": (680, 416, 802, 562),
     "proprio-hausse": (800, 398, 1118, 576), "grilou-ordi": (15, 578, 260, 750), "lettre": (260, 595, 466, 750), "balance": (469, 581, 660, 748),
     "tribunal": (662, 570, 880, 750), "grilou-victoire": (880, 556, 1118, 750)}
im = Image.open("src/assets-planche.webp").convert("RGBA")
for nom, b in B.items():
    c = im.crop(b); A = np.asarray(c).copy(); m = A[..., 3] > 40
    lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=2)); taille = ndimage.sum(m, lab, range(1, n + 1)); sl = ndimage.find_objects(lab); H_, W_ = m.shape
    jette = [i + 1 for i, q in enumerate(sl) if q is not None and (taille[i] < 0.004 * m.size or ((q[0].start == 0 or q[1].start == 0 or q[0].stop == H_ or q[1].stop == W_) and taille[i] < 0.15 * taille.max()))]
    A[np.isin(lab, jette), 3] = 0
    EFF = {"grilou-victoire": (0, 0, 165, 24), "sablier": (0, 0, 10, 999)}   # morceaux voisins vus sur la planche de contrôle
    if nom in EFF: x0, y0, x1, y1 = EFF[nom]; A[y0:y1, x0:x1, 3] = 0
    o = Image.fromarray(A); o = o.crop(o.getbbox()); o = o.resize((o.width * 2, o.height * 2), Image.LANCZOS)
    o.save(f"assets/img/{nom}.png"); print(nom, o.size)
T = [(n, Image.open(f"assets/img/{n}.png")) for n in B]
S = 300; P = Image.new("RGB", (6 * S, 4 * S), (235, 235, 240))
for k, (n, i) in enumerate(T):
    i = i.copy(); i.thumbnail((S - 10, S - 10)); P.paste(i, ((k % 6) * S + 5, (k // 6) * S + 5), i)
P.save("fz/verif-detour.jpg")
