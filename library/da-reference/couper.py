# Voix GBH : on garde la DERNIÈRE prise de chaque phrase, puis on resserre TOUS les blancs (v2, 29/10 : « ça enchaîne trop lentement »)
# sans toucher aux débuts / fins de mots (marges autour de chaque silence). python -I couper.py → assets/voix-cut.wav + segments.json
import json, subprocess, wave
import numpy as np
MANUEL = [(0, 4.80), (5.78, 10.16),   # « Je suis réunionnais » de la 2e prise : attaque complète (1re et 3e coupées net) ; suite dans la 3e
                           # 2 prises ratées de « Je suis réunionnais… »
          (27.72, 32.60),            # 1re prise de « à la Réunion il possède notamment… »
          (63.90, 68.60),            # 1re prise de « Elle explique que… »
          (94.50, 111.20),           # 1re prise de « Parce que 37 %… » (on garde « dans les îles »)
          (117.05, 123.02)]          # reprises de « Et quand de grands groupes… »
END = 130.85
SEUIL, MIN, AVANT, APRES = -38, 0.16, 0.05, 0.06   # v3 (29/10, « encore plus serré ») : silence < -38 dB d au moins 0,16 s → reste ≈ 0,11 s
w = wave.open("assets/voix-orig.wav"); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).mean(1) / 32768
h = 480; n = len(x) // h; db = 20 * np.log10(np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
AUTO, i = [], 0
while i < n:
    if db[i] < SEUIL:
        j = i
        while j < n and db[j] < SEUIL: j += 1
        a, b = i * 0.01, j * 0.01
        if b - a >= MIN and a > 0.5: AUTO.append((round(a + AVANT, 2), round(b - APRES, 2)))
        i = j
    else: i += 1
AUTO = [c for c in AUTO if c[0] > 9.6]   # on garde le blanc d'attaque avant « Je suis » (0,25 s) : le whoosh ne doit pas le recouvrir
CUTS = sorted(MANUEL + [c for c in AUTO if not any(m0 - 0.05 <= c[0] and c[1] <= m1 + 0.05 for m0, m1 in MANUEL)])
fu = []
for a, b in CUTS:
    if fu and a <= fu[-1][1]: fu[-1][1] = max(fu[-1][1], b)
    else: fu.append([a, b])
S, a = [], 0
for c0, c1 in fu:
    if c0 > a: S.append((a, c0))
    a = c1
S.append((a, END))
S = [s for s in S if s[1] - s[0] > 0.02]
f = "".join(f"[0:a]atrim={p}:{q},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={q - p - 0.008:.3f}:d=0.008" + (",volume='if(lt(t,0.46),1.7,1)':eval=frame" if k == 0 else "") + f"[a{k}];" for k, (p, q) in enumerate(S)) \
    + "".join(f"[a{k}]" for k in range(len(S))) + f"concat=n={len(S)}:v=0:a=1[a]"
open("fz/filtre.txt", "w").write(f)
subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", "assets/voix-orig.wav", "-/filter_complex", "fz/filtre.txt", "-map", "[a]", "-ar", "48000", "-ac", "2", "assets/voix-cut.wav"], check=True)
json.dump(S, open("segments.json", "w")); print(len(AUTO), "blancs resserrés ; durée", round(sum(q - p for p, q in S), 2), "s")
