# Son final = voix + 0,10 s + voix-cta + bruitages sfx.json + musique discrète. python -I ../_outils/mix_ref.py sortie.mp4
import json, subprocess, sys
SFX = json.load(open("sfx.json")); END = float(open("fin.txt").read())
subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", "assets/voix-cut.wav", "-f", "lavfi", "-t", "0.10", "-i", "anullsrc=r=48000:cl=stereo", "-i", "assets/voix-cta.wav", "-filter_complex", "[0:a]aresample=48000,aformat=channel_layouts=stereo,adelay=120:all=1[a];[2:a]aresample=48000,aformat=channel_layouts=stereo[c];[a][1:a][c]concat=n=3:v=0:a=1[o]", "-map", "[o]", "assets/voix-finale.wav"], check=True)
args = ["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", "renders/_video.mp4", "-i", "assets/voix-finale.wav"]; fl = []
for k, (t, n, v) in enumerate(SFX):
    args += ["-i", f"assets/sfx/{n}.wav"]; ms = int(t * 1000); fl.append(f"[{k + 2}:a]aresample=48000,volume={v},adelay={ms}|{ms}[s{k}]")
fl.append("[1:a]aresample=48000,apad[v]"); args += ["-i", "assets/musique.wav"]
fl.append(f"[{len(SFX) + 2}:a]aresample=48000,atrim=0:{END},afade=t=in:st=0.3:d=0.9,afade=t=out:st={END - 1.5}:d=1.5[m]")
fl.append("[v]" + "".join(f"[s{k}]" for k in range(len(SFX))) + f"[m]amix=inputs={len(SFX) + 2}:normalize=0:duration=longest,atrim=0:{END},alimiter=limit=0.98[a]")
open("fz/mix.txt", "w").write(";".join(fl))
args += ["-/filter_complex", "fz/mix.txt", "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-t", str(END), "renders/" + sys.argv[1]]
subprocess.run(args, check=True); print(len(SFX), "sons")
