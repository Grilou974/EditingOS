// Note automatique d'une vidéo rendue (sur 10), à partir de mesures objectives faites avec ffmpeg.
// Les critères dépendent de la chaîne (cible de durée, de format, de rythme). Résultat mis en cache dans
// <projet>/editingos/score.json, recalculé seulement quand le rendu change.
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";

export const CHANNEL_TARGETS = {
  "TV Cat": { format: [1080, 1920], dur: [20, 45, 75], cutsPerMin: 60, label: "short TikTok 9:16" },
  "Coaching Master": { format: [1920, 1080], dur: [60, 180, 600], cutsPerMin: 30, label: "cours YouTube 16:9" },
  "Seleckt": { format: [1080, 1920], dur: [15, 40, 75], cutsPerMin: 55, label: "short 9:16" },
  "_": { format: null, dur: [15, 60, 300], cutsPerMin: 30, label: "vidéo" },
};

const run = (args, env) => new Promise((ok) => {
  const ch = spawn("ffmpeg", ["-hide_banner", "-nostdin", ...args], { env, windowsHide: true, stdio: ["ignore", "ignore", "pipe"] });
  let err = "";
  ch.stderr.on("data", (d) => (err += d));
  ch.on("close", () => ok(err));
  ch.on("error", () => ok(""));
});

async function measure(file, env) {
  // 1 passe audio (loudness + silences + attaque), 1 passe image (changements de plan) en basse définition
  const a = await run(["-i", file, "-af", "ebur128=peak=true:framelog=quiet,silencedetect=noise=-38dB:d=0.35", "-f", "null", "-"], env);
  const v = await run(["-i", file, "-vf", "scale=240:-2,select='gt(scene,0.08)',showinfo", "-an", "-f", "null", "-"], env);
  const dur = +(a.match(/Duration: (\d+):(\d+):([\d.]+)/) || []).slice(1).reduce((s, x, i) => s + [3600, 60, 1][i] * x, 0) || 0;
  const res = a.match(/Stream #.*Video:.*?(\d{3,5})x(\d{3,5})/);
  const lufs = +((a.match(/I:\s+(-?[\d.]+) LUFS/g) || []).pop() || "").replace(/[^-\d.]/g, "") || null;
  const peak = +((a.match(/Peak:\s+(-?[\d.]+) dBFS/g) || []).pop() || "").replace(/[^-\d.]/g, "") || null;
  let silent = 0;
  for (const m of a.matchAll(/silence_duration: ([\d.]+)/g)) silent += +m[1];
  const starts = [...a.matchAll(/silence_start: ([\d.]+)/g)].map((m) => +m[1]);
  const ends = [...a.matchAll(/silence_end: ([\d.]+)/g)].map((m) => +m[1]);
  const firstSound = starts.length && starts[0] < 0.05 ? (ends[0] ?? 0) : 0;
  const cuts = (v.match(/Parsed_showinfo.*n:\s*\d+/g) || []).length;
  return { dur, w: res ? +res[1] : 0, h: res ? +res[2] : 0, lufs, peak, silent, firstSound, cuts };
}

const clamp = (x) => Math.max(0, Math.min(1, x));
function grade(m, channel, extra) {
  const T = CHANNEL_TARGETS[channel] || CHANNEL_TARGETS._;
  const C = [];
  const add = (key, label, pts, ratio, detail, tip) => C.push({ key, label, max: pts, pts: Math.round(pts * clamp(ratio) * 10) / 10, detail, tip: ratio < 0.85 ? tip : "" });
  // format
  const fmtOk = !T.format || (m.w === T.format[0] && m.h === T.format[1]);
  add("format", "Format", 10, fmtOk ? 1 : m.w && m.h && (m.w > m.h) === (T.format[0] > T.format[1]) ? 0.6 : 0.2, `${m.w}×${m.h}${T.format ? ` (attendu ${T.format.join("×")})` : ""}`, "Rendre au format de la chaîne.");
  // durée
  const [lo, ideal, hi] = T.dur;
  const dr = m.dur < lo ? m.dur / lo : m.dur > hi ? hi / m.dur : 1 - 0.25 * Math.abs(m.dur - ideal) / Math.max(ideal - lo, hi - ideal);
  add("duree", "Durée", 15, dr, `${m.dur.toFixed(1)} s (idéal ~${ideal} s pour un ${T.label})`, m.dur > ideal ? "Raccourcir : couper les phrases moins utiles." : "Un peu court : développer une idée.");
  // son
  const lr = m.lufs == null ? 0.5 : 1 - Math.abs(m.lufs - -14) / 8;
  const clip = m.peak != null && m.peak > -0.3 ? 0.7 : 1;
  add("son", "Volume / mixage", 15, lr * clip, m.lufs == null ? "non mesuré" : `${m.lufs.toFixed(1)} LUFS (cible −14)${m.peak != null ? `, crête ${m.peak.toFixed(1)} dBFS` : ""}`, m.lufs != null && m.lufs < -16 ? "Monter le volume général." : "Baisser le mix / éviter la saturation.");
  // rythme visuel
  const cpm = m.dur ? (m.cuts / m.dur) * 60 : 0;
  add("rythme", "Rythme des plans", 20, cpm / T.cutsPerMin, `${cpm.toFixed(0)} changements visuels / min (cible ${T.cutsPerMin})`, "Plus de changements de plan / d'images.");
  // silences
  const sp = m.dur ? m.silent / m.dur : 0;
  add("blancs", "Blancs", 15, 1 - Math.max(0, sp - 0.02) / 0.12, `${(sp * 100).toFixed(1)} % de silences de plus de 0,35 s`, "Resserrer les blancs entre les phrases.");
  // accroche
  add("accroche", "Accroche", 10, 1 - Math.max(0, m.firstSound - 0.3) / 1.5, m.firstSound > 0.05 ? `le son démarre à ${m.firstSound.toFixed(2)} s` : "le son démarre tout de suite", "Démarrer la voix immédiatement.");
  // suivi
  add("retours", "Retours traités", 10, 1 - extra.feedbackOpen * 0.34, extra.feedbackOpen ? `${extra.feedbackOpen} retour(s) encore ouvert(s)` : "aucun retour en attente", "Traiter les retours ouverts.");
  add("ajour", "Rendu à jour", 5, extra.state === "rendu" ? 1 : 0.3, extra.state === "rendu" ? "dernier rendu à jour" : "les sources ont changé depuis", "Relancer le rendu.");
  const total = C.reduce((s, c) => s + c.pts, 0);
  return { note: Math.round(total) / 10, total: Math.round(total), criteria: C };
}

const cacheFile = (p) => path.join(p.path, "editingos", "score.json");
export function cachedScore(p) {
  const r = p.renders[0];
  if (!r) return null;
  let c;
  try { c = JSON.parse(fs.readFileSync(cacheFile(p), "utf8")); } catch { return null; }
  if (c.file !== r.file || c.mtime !== r.mtime || !c.measure || c.v !== 2) return null;
  return { ...grade(c.measure, p.channel, p), file: r.file, at: c.at };
}

const queue = [];
let busy = false;
export function queueScore(p, env, onDone) {
  if (!p.renders[0] || cachedScore(p) || queue.some((q) => q.p.id === p.id)) return;
  queue.push({ p, env, onDone });
  pump();
}
async function pump() {
  if (busy || !queue.length) return;
  busy = true;
  const { p, env, onDone } = queue.shift();
  try {
    const r = p.renders[0];
    const m = await measure(path.join(p.path, r.file), env);
    if (m.dur) {
      fs.mkdirSync(path.dirname(cacheFile(p)), { recursive: true });
      fs.writeFileSync(cacheFile(p), JSON.stringify({ v: 2, file: r.file, mtime: r.mtime, at: new Date().toISOString(), measure: m }, null, 2));
      onDone && onDone(p);
    }
  } catch {}
  busy = false;
  pump();
}
