# Son final = voix coupée intacte + bruitages de sfx.json + lofi (Sleepy Cat, Mixkit, -32 LUFS, fondu de fin) sur la vidéo rendue. python -I mix.py
import json, subprocess
SFX = json.load(open("sfx.json"))
END = float(open('fin.txt').read())
args = ["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", "renders/_video.mp4", "-i", "assets/voix-finale.wav"]
fl = []
for k, (t, n, v) in enumerate(SFX):
    args += ["-i", f"assets/sfx/{n}.wav"]; ms = int(t * 1000)
    fl.append(f"[{k + 2}:a]aresample=48000,volume={v},adelay={ms}|{ms}[s{k}]")
fl.append("[1:a]aresample=48000,apad[v]")
args += ["-i", "assets/musique.wav"]
fl.append(f"[{len(SFX) + 2}:a]aresample=48000,atrim=0:{END},afade=t=in:st=0.3:d=0.9,afade=t=out:st={END - 1.5}:d=1.5[m]")
fl.append("[v]" + "".join(f"[s{k}]" for k in range(len(SFX))) + f"[m]amix=inputs={len(SFX) + 2}:normalize=0:duration=longest,atrim=0:{END},alimiter=limit=0.98[a]")
args += ["-filter_complex", ";".join(fl), "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-t", str(END), "renders/gbh.mp4"]
subprocess.run(args, check=True); print(len(SFX), "sons")
