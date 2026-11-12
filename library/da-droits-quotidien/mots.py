# Transcription mot à mot d'un wav. python -I mots.py voix.wav sortie.json
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel
a16 = np.frombuffer(subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", sys.argv[1], "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout, np.int16).astype(np.float32) / 32768
m = WhisperModel("medium", device="cpu", compute_type="int8")
W = []
for seg in m.transcribe(a16, language="fr", word_timestamps=True, condition_on_previous_text=False, vad_filter=False)[0]:
    W += [[round(u.start, 2), round(u.end, 2), u.word.strip()] for u in seg.words]
json.dump(W, open(sys.argv[2], "w", encoding="utf8"), ensure_ascii=False)
L = []
p = -9
for s, e, w in W:
    if s - p > 0.45 or not L: L.append(f"[{s:.2f}] ")
    L[-1] += w + " "; p = e
open(sys.argv[2].replace(".json", ".txt"), "w", encoding="utf8").write("\n".join(L))
print(len(W), "mots")
