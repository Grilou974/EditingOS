# Transcription isolée PRÉCISE de fenêtres (décode tout le fichier puis découpe, pas de -ss imprécis sur MP3).
# Usage : python -I iso_w.py fichier a-b [a-b ...]
import sys, subprocess, numpy as np
from faster_whisper import WhisperModel
f = sys.argv[1]
x = np.frombuffer(subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", f, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout, np.int16).astype(np.float32) / 32768
m = WhisperModel("medium", device="cpu", compute_type="int8")
for r in sys.argv[2:]:
    a, b = map(float, r.split("-"))
    seg = x[int(a * 16000):int(b * 16000)]
    out = []
    for s in m.transcribe(seg, language="fr", word_timestamps=True, condition_on_previous_text=False)[0]:
        out += [f"{w.word.strip()}[{a + w.start:.2f}-{a + w.end:.2f}]" for w in s.words]
    print(f"== {r} :", " ".join(out), flush=True)
