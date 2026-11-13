# Découpe la voix en blocs séparés par des silences et transcrit CHAQUE bloc seul (révèle les prises que la transcription globale avale).
# python -I blocs.py voix.wav sortie.txt
import subprocess, sys
import numpy as np
from faster_whisper import WhisperModel
a = np.frombuffer(subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", sys.argv[1], "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout, np.int16).astype(np.float32) / 32768
h = 160; n = len(a) // h; db = 20 * np.log10(np.sqrt((a[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
B, i = [], 0; v = db > -36
while i < n:
    if v[i]:
        j = i; g = 0
        while j < n and g < 28:
            g = 0 if v[j] else g + 1; j += 1
        B.append((i / 100, (j - g) / 100)); i = j
    else: i += 1
m = WhisperModel("medium", device="cpu", compute_type="int8")
o = open(sys.argv[2], "w", encoding="utf8")
for s, e in B:
    if e - s < 0.15: continue
    x = np.concatenate([np.zeros(4000, np.float32), a[int(s * 16000):int(e * 16000)], np.zeros(4000, np.float32)])
    t = " ".join(u.text.strip() for u in m.transcribe(x, language="fr", condition_on_previous_text=False, vad_filter=False)[0])
    o.write(f"{s:7.2f}-{e:7.2f}  {t}\n")
