# 2e passe (05/11, « trop de blanc entre chaque idée ») : retire aussi les respirations entre les phrases, en se calant sur les mots transcrits.
# Ne coupe que dans les zones sous -26 dB situées ENTRE deux mots, avec des marges autour de la voix. Reste ≈ 0,07 s entre deux idées.
# python -I affiner.py → segments-v3.json (avant) ; segments.json + assets/voix-cut.wav (après)
import json, subprocess, wave
import numpy as np
from faster_whisper import WhisperModel
APRES_MOT, AVANT_MOT, GARDE_MIN = 0.035, 0.04, 0.09
S = json.load(open("segments.json")); json.dump(S, open("segments-v3.json", "w"))
w = wave.open("assets/voix-cut.wav"); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).mean(1) / 32768
h = 480; n = len(x) // h; db = 20 * np.log10(np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
m = WhisperModel("medium", device="cpu", compute_type="int8")
a16 = np.frombuffer(subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", "assets/voix-cut.wav", "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout, np.int16).astype(np.float32) / 32768
mots = []
for seg in m.transcribe(a16, language="fr", word_timestamps=True, condition_on_previous_text=False)[0]:
    mots += [(u.start, u.end, u.word.strip()) for u in seg.words]
print(len(mots), "mots")
coupes = []
for (a0, a1, t0), (b0, b1, t1) in zip(mots, mots[1:]):
    # on cherche la zone calme autour de la frontière entre les deux mots
    c = int(((a1 + b0) / 2) * 100); i = j = c
    if db[c] > -26:
        z = [k for k in range(max(0, c - 18), min(n, c + 18)) if db[k] < -26]
        if not z: continue
        c = min(z, key=lambda k: abs(k - c)); i = j = c
    while i > 0 and db[i - 1] < -26: i -= 1
    while j < n - 1 and db[j + 1] < -26: j += 1
    a, b = i / 100 + APRES_MOT, j / 100 - AVANT_MOT
    if b - a < 0.05 or (j - i) / 100 < GARDE_MIN + 0.03: continue
    if not coupes or a > coupes[-1][1]: coupes.append((round(a, 2), round(b, 2)))
print(len(coupes), "coupes, gain", round(sum(b - a for a, b in coupes), 2), "s")
# temps de la voix coupée → temps d'origine
cum = []; o = 0
for p, q in S: cum.append((o, p, q)); o += q - p
def orig(t):
    for o0, p, q in reversed(cum):
        if t >= o0: return p + t - o0
N, a = [], 0.0
for c0, c1 in coupes + [(cum[-1][0] + cum[-1][2] - cum[-1][1], None)]:
    # morceaux gardés [a, c0], éventuellement à cheval sur plusieurs segments
    for o0, p, q in cum:
        d, f = max(a, o0), min(c0, o0 + q - p)
        if f - d > 0.03: N.append([round(p + d - o0, 3), round(p + f - o0, 3)])
    a = c1
N = [s for s in N if s[1] > 5.05]; N[0][0] = 5.00   # on démarre juste avant l attaque de « Je suis » : plus de temps mort au début
f = "".join(f"[0:a]atrim={p}:{q},asetpts=PTS-STARTPTS,afade=t=in:d=0.006,afade=t=out:st={q - p - 0.006:.3f}:d=0.006" + (",volume='if(lt(t,0.26),1.7,1)':eval=frame" if k == 0 else "") + f"[a{k}];" for k, (p, q) in enumerate(N)) \
    + "".join(f"[a{k}]" for k in range(len(N))) + f"concat=n={len(N)}:v=0:a=1[a]"
open("fz/filtre.txt", "w").write(f)
subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", "assets/voix-orig.wav", "-/filter_complex", "fz/filtre.txt", "-map", "[a]", "-ar", "48000", "-ac", "2", "assets/voix-cut.wav"], check=True)
json.dump(N, open("segments.json", "w")); print("durée", round(sum(q - p for p, q in N), 2))
