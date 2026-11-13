# Voix DA de référence : prises.json (morceaux gardés, en s) → blancs automatiques (-38 dB) → respirations entre mots (-26 dB, calé sur les mots)
# → assets/voix-cut.wav + segments.json + words.json (mots de la voix finale). À lancer depuis le dossier du projet : python -I ../_outils/voix_ref.py
import json, os, subprocess, sys, wave
import numpy as np
from faster_whisper import WhisperModel
SEUIL, MIN, AVANT, APRES = -38, 0.16, 0.05, 0.06
APRES_MOT, AVANT_MOT, GARDE_MIN = 0.035, 0.04, 0.09
P = json.load(open("prises.json"))
w = wave.open("assets/voix-orig.wav"); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).mean(1) / 32768
h = 480; n = len(x) // h; db = 20 * np.log10(np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
def rend(S, sortie):
    f = "".join(f"[0:a]atrim={p}:{q},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={q - p - 0.008:.3f}:d=0.008[a{k}];" for k, (p, q) in enumerate(S)) + "".join(f"[a{k}]" for k in range(len(S))) + f"concat=n={len(S)}:v=0:a=1[a]"
    open("fz/filtre.txt", "w").write(f)
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", "assets/voix-orig.wav", "-/filter_complex", "fz/filtre.txt", "-map", "[a]", "-ar", "48000", "-ac", "2", sortie], check=True)
    # tete.json = [début, fin, fondu] : mot greffé devant la voix, fondu enchaîné DANS une consonne continue (sinon la soudure s'entend)
    if sortie.endswith("voix-cut.wav") and os.path.exists("tete.json"):
        t0, t1, xf = json.load(open("tete.json")); os.replace(sortie, "fz/sans-tete.wav")
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", "assets/voix-orig.wav", "-i", "fz/sans-tete.wav", "-filter_complex", f"[0:a]atrim={t0}:{t1},asetpts=PTS-STARTPTS,afade=t=in:d=0.006[h];[h][1:a]acrossfade=d={xf}:c1=qsin:c2=qsin[a]", "-map", "[a]", "-ar", "48000", "-ac", "2", sortie], check=True)
S = []
for a, b in P:
    i, j = int(a * 100), int(a * 100); c = a
    while i < int(b * 100):
        if db[i] < SEUIL:
            j = i
            while j < int(b * 100) and db[j] < SEUIL: j += 1
            if (j - i) / 100 >= MIN and i / 100 > a + .05 and j / 100 < b - .05:
                S.append([round(c, 3), round(i / 100 + AVANT, 3)]); c = j / 100 - APRES
            i = j
        else: i += 1
    S.append([round(c, 3), round(b, 3)])
rend(S, "assets/voix-p1.wav")
w = wave.open("assets/voix-p1.wav"); y = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).mean(1) / 32768
n = len(y) // h; db = 20 * np.log10(np.sqrt((y[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
m = WhisperModel("medium", device="cpu", compute_type="int8")
def trans(f):
    a16 = np.frombuffer(subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", f, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout, np.int16).astype(np.float32) / 32768
    o = []
    for seg in m.transcribe(a16, language="fr", word_timestamps=True, condition_on_previous_text=False)[0]: o += [[round(u.start, 2), round(u.end, 2), u.word.strip()] for u in seg.words]
    return o
M = trans("assets/voix-p1.wav")
# 2e passe PRUDENTE (05/11, mots mangés à -26 dB sur Joyca) : vrai creux sous -32 dB d'au moins 0,18 s entre deux mots, marges de 0,05 s.
SE = -32
def coupes():
    C = []
    for (a0, a1, _), (b0, b1, _) in zip(M, M[1:]):
        if b0 - a1 < 0.06: continue
        c = min(int(((a1 + b0) / 2) * 100), n - 1)
        if db[c] > SE: continue
        i = j = c
        while i > 0 and db[i - 1] < SE: i -= 1
        while j < n - 1 and db[j + 1] < SE: j += 1
        if (j - i) / 100 < 0.18: continue
        a, b = i / 100 + 0.05, j / 100 - 0.05
        if b - a >= 0.05 and (not C or a > C[-1][1]): C.append((round(a, 2), round(b, 2)))
    return C
cum = []; o = 0
for p, q in S: cum.append((o, p, q)); o += q - p
def monte(C):
    N, a = [], 0.0
    for c0, c1 in C + [(o, None)]:
        for o0, p, q in cum:
            d, f = max(a, o0), min(c0, o0 + q - p)
            if f - d > 0.03: N.append([round(p + d - o0, 3), round(p + f - o0, 3)])
        a = c1
    return N
import difflib, unicodedata
nm = lambda t: "".join(c for c in unicodedata.normalize("NFD", t.lower()) if c.isalnum() and not unicodedata.combining(c))
C = coupes()
for tour in range(3):
    N = monte(C); rend(N, "assets/voix-cut.wav"); W = trans("assets/voix-cut.wav")
    A, B = [nm(x[2]) for x in M], [nm(x[2]) for x in W]; perdu = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
        if op in ("delete", "replace") and i2 - i1 > j2 - j1: perdu.append((M[i1][0], M[i2 - 1][1], " ".join(A[i1:i2])))
    print("tour", tour, len(C), "coupes, mots perdus :", perdu)
    if not perdu: break
    C = [c for c in C if not any(p0 - 0.5 < c[1] and c[0] < p1 + 0.5 for p0, p1, _ in perdu)]
# 3e passe RYTHME (13/11, « un tout petit peu plus de rythme ») : les pauses de plus de 0,2 s entre deux mots, si elles sont vraiment
# silencieuses ou juste une respiration (< -27 dB pendant au moins 0,22 s), sont ramenées à ≈ 0,11 s (0,06 s après le mot, 0,05 s avant le suivant). Jamais dans un mot ; contrôle des mots perdus.
if "--rythme" in sys.argv:
    w2 = wave.open("assets/voix-cut.wav"); y2 = np.frombuffer(w2.readframes(w2.getnframes()), np.int16).reshape(-1, 2).mean(1) / 32768
    n2 = len(y2) // h; d2 = 20 * np.log10(np.sqrt((y2[:n2 * h].reshape(n2, h) ** 2).mean(1)) + 1e-9)
    C3 = []
    for (a0, a1, _), (b0, b1, _) in zip(W, W[1:]):
        if b0 - a1 <= 0.2: continue
        i0, i1 = int((a1 - 0.08) * 100), int((b0 + 0.08) * 100)   # la vraie zone calme peut déborder un peu des bornes des mots
        best, k = (0, 0), i0
        while k < i1:
            if d2[k] < -22:
                j = k
                while j < i1 and d2[j] < -22: j += 1
                if j - k > best[1] - best[0]: best = (k, j)
                k = j
            else: k += 1
        if (best[1] - best[0]) / 100 >= 0.24: C3.append((round(best[0] / 100 + 0.06, 2), round(best[1] / 100 - 0.06, 2)))
    cum = []; o = 0
    for p, q in N: cum.append((o, p, q)); o += q - p
    A = [nm(x[2]) for x in W]
    N3 = monte(C3); rend(N3, "assets/voix-cut.wav"); W3 = trans("assets/voix-cut.wav")
    B = [nm(x[2]) for x in W3]
    perdu = [op for op in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes() if op[0] in ("delete", "replace") and op[2] - op[1] > op[4] - op[3]]
    if perdu: print("rythme : mots perdus, on garde la version d'avant", perdu); rend(N, "assets/voix-cut.wav")
    else: print("rythme :", len(C3), "pauses raccourcies, gain", round(sum(b - a for a, b in C3), 2), "s"); N, W = N3, W3
if os.path.exists("tete.json"):
    t0, t1, xf = json.load(open("tete.json")); N = [[t0, round(t1 - xf, 3)]] + N
json.dump(N, open("segments.json", "w")); json.dump(W, open("words.json", "w", encoding="utf8"), ensure_ascii=False)
L = [""]
for s_, e, t in W:
    if len(L[-1]) > 95: L.append("")
    L[-1] += f"{t}[{s_:.2f}] " if t[-1:] in ".,?!" else f"{t} "
open("words.txt", "w", encoding="utf8").write("\n".join(L))
print(len(N), "morceaux, durée", round(sum(q - p for p, q in N), 2), "s (avant", round(sum(b - a for a, b in P), 2), ")")
