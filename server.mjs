// EditingOS — atelier de montage local. Zero dependency: node server.mjs
// The file system is the source of truth: every request re-reads project folders.
import http from "node:http";
import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CONFIG_FILE = path.join(HERE, "config.json");
const DATA = path.join(HERE, "data");
const ACTIVITY = path.join(DATA, "activity.jsonl");
const LIB = path.join(HERE, "library");
const PUBLIC = path.join(HERE, "public");
fs.mkdirSync(DATA, { recursive: true });

const readJSON = (f, fallback) => { try { return JSON.parse(fs.readFileSync(f, "utf8")); } catch { return fallback; } };
const config = () => {
  const c = readJSON(CONFIG_FILE, {});
  return { port: c.port || 4321, roots: (c.roots || ["../videos"]).map((r) => path.resolve(HERE, r)), ffmpegDir: c.ffmpegDir || findFfmpeg() };
};

function findFfmpeg() {
  const base = path.join(process.env.LOCALAPPDATA || "", "Microsoft", "WinGet", "Packages");
  try {
    for (const d of fs.readdirSync(base).filter((d) => d.startsWith("Gyan.FFmpeg"))) {
      for (const b of fs.readdirSync(path.join(base, d))) {
        const bin = path.join(base, d, b, "bin");
        if (fs.existsSync(path.join(bin, "ffmpeg.exe"))) return bin;
      }
    }
  } catch {}
  return null;
}
const childEnv = () => {
  const { ffmpegDir } = config();
  return ffmpegDir ? { ...process.env, PATH: ffmpegDir + path.delimiter + process.env.PATH } : process.env;
};

// ---------- activity ----------
function logActivity(type, data = {}) {
  const ev = { at: new Date().toISOString(), type, ...data };
  fs.appendFileSync(ACTIVITY, JSON.stringify(ev) + "\n");
  return ev;
}
const readActivity = () =>
  fs.existsSync(ACTIVITY)
    ? fs.readFileSync(ACTIVITY, "utf8").split("\n").filter(Boolean).map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean).reverse()
    : [];

// ---------- project scan ----------
const SKIP = new Set(["node_modules", ".hyperframes", "renders", ".git", "editingos", ".media"]);
const idOf = (p) => crypto.createHash("sha1").update(p.toLowerCase()).digest("hex").slice(0, 10);
let index = new Map();
let lastScan = { at: null, ms: 0 };

function findProjects(root, depth = 0, out = []) {
  let ents;
  try { ents = fs.readdirSync(root, { withFileTypes: true }); } catch { return out; }
  if (ents.some((e) => e.isFile() && e.name === "hyperframes.json")) { out.push(root); return out; }
  if (depth >= 3) return out;
  for (const e of ents) if (e.isDirectory() && !SKIP.has(e.name) && !e.name.startsWith(".")) findProjects(path.join(root, e.name), depth + 1, out);
  return out;
}
function newestSource(dir, depth = 0) {
  let m = 0;
  let ents;
  try { ents = fs.readdirSync(dir, { withFileTypes: true }); } catch { return 0; }
  for (const e of ents) {
    if (SKIP.has(e.name) || e.name.startsWith(".")) continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) { if (depth < 4) m = Math.max(m, newestSource(p, depth + 1)); }
    else if (/\.(html|js|css|json|md|wav|mp3|png|jpe?g|svg|webp|mp4|mov|woff2?)$/i.test(e.name) && !/^(FEEDBACK\.md|editingos\.json)$/.test(e.name)) {
      m = Math.max(m, fs.statSync(p).mtimeMs);
    }
  }
  return m;
}
function frontmatter(file) {
  try {
    const t = fs.readFileSync(file, "utf8");
    const m = t.match(/^---\r?\n([\s\S]*?)\r?\n---/);
    if (!m) return {};
    return Object.fromEntries(m[1].split(/\r?\n/).map((l) => l.match(/^([\w-]+):\s*(.*)$/)).filter(Boolean).map(([, k, v]) => [k, v.replace(/^["']|["']$/g, "")]));
  } catch { return {}; }
}
const TYPE_LABEL = { "faceless-explainer": "Explainer", "general-video": "Vidéo", "motion-graphics": "Motion", "product-launch-video": "Ads", "talking-head-recut": "talking-head", "embedded-captions": "talking-head", "music-to-video": "Musique", "pr-to-video": "PR", slideshow: "Slides" };
function formatOf(w, h) {
  if (!w || !h) return "—";
  const r = w / h;
  if (Math.abs(r - 9 / 16) < 0.02) return "9:16";
  if (Math.abs(r - 16 / 9) < 0.02) return "16:9";
  if (Math.abs(r - 1) < 0.02) return "1:1";
  if (Math.abs(r - 4 / 5) < 0.02) return "4:5";
  return `${w}×${h}`;
}
function listRenders(dir) {
  const rd = path.join(dir, "renders");
  try {
    return fs.readdirSync(rd).filter((f) => /\.(mp4|mov|webm)$/i.test(f)).map((f) => {
      const st = fs.statSync(path.join(rd, f));
      return { file: `renders/${f}`, name: f, size: st.size, mtime: st.mtimeMs };
    }).sort((a, b) => b.mtime - a.mtime);
  } catch { return []; }
}
function readProject(dir) {
  const meta = readJSON(path.join(dir, "meta.json"), {});
  const eos = readJSON(path.join(dir, "editingos.json"), {});
  const brief = frontmatter(path.join(dir, "BRIEF.md"));
  let w = 0, h = 0;
  try {
    const head = fs.readFileSync(path.join(dir, "index.html"), "utf8").slice(0, 200000);
    const m = head.match(/data-composition-id="[^"]*"[^>]*?data-width="(\d+)"[^>]*?data-height="(\d+)"/) || head.match(/data-width="(\d+)"[^>]*data-height="(\d+)"/);
    if (m) { w = +m[1]; h = +m[2]; }
  } catch {}
  if (!w && brief.aspect) { const m = brief.aspect.match(/(\d+)x(\d+)/); if (m) { w = +m[1]; h = +m[2]; } }
  const renders = listRenders(dir);
  const src = newestSource(dir);
  const latest = renders[0];
  const state = !latest ? "brouillon" : src > latest.mtime + 5000 ? "perime" : "rendu";
  const fb = readJSON(path.join(dir, "editingos", "feedback.json"), []);
  const slug = path.basename(dir);
  let created = 0;
  try { created = fs.statSync(path.join(dir, "hyperframes.json")).birthtimeMs || fs.statSync(path.join(dir, "hyperframes.json")).mtimeMs; } catch {}
  return {
    id: idOf(dir), slug, path: dir,
    title: eos.title || meta.name && meta.name !== slug && meta.name || slug.replace(/-/g, " ").replace(/^./, (c) => c.toUpperCase()),
    family: eos.family || "Sans famille",
    type: eos.type || TYPE_LABEL[brief.workflow] || "Vidéo",
    tags: eos.tags || [],
    utility: !!eos.utility,
    format: formatOf(w, h), width: w, height: h,
    workflow: brief.workflow || null, message: brief.message || eos.description || "", language: brief.language || null, length: brief.length || null,
    renders, state,
    created, modified: Math.max(src, latest ? latest.mtime : 0),
    feedbackOpen: fb.filter((f) => f.status !== "fait").length, feedbackTotal: fb.length,
  };
}
function scan() {
  const t0 = performance.now();
  const next = new Map();
  for (const root of config().roots) for (const dir of findProjects(root)) { const p = readProject(dir); next.set(p.id, p); }
  index = next;
  lastScan = { at: new Date().toISOString(), ms: Math.round(performance.now() - t0) };
  return [...index.values()];
}
const project = (id) => { if (!index.has(id)) scan(); return index.get(id); };

function stats(list) {
  const all = list;
  const vis = all.filter((p) => !p.utility);
  const diskActive = all.reduce((s, p) => s + p.renders.reduce((a, r) => a + r.size, 0), 0);
  const tidy = all.reduce((s, p) => s + p.renders.slice(1).reduce((a, r) => a + r.size, 0), 0);
  return { projects: vis.length, utilityHidden: all.length - vis.length, withRender: vis.filter((p) => p.renders.length).length, stale: vis.filter((p) => p.state === "perime").length, disk: diskActive, tidy, scan: lastScan, roots: config().roots };
}

// ---------- feedback ----------
const fbFile = (p) => path.join(p.path, "editingos", "feedback.json");
const fmtT = (s) => `${String(Math.floor(s / 60)).padStart(2, "0")}:${(s % 60).toFixed(1).padStart(4, "0")}`;
function writeFeedback(p, items) {
  fs.mkdirSync(path.dirname(fbFile(p)), { recursive: true });
  fs.writeFileSync(fbFile(p), JSON.stringify(items, null, 2));
  const open = items.filter((i) => i.status !== "fait"), done = items.filter((i) => i.status === "fait");
  const line = (i) => `- [${i.status === "fait" ? "x" : " "}] **${fmtT(i.time)}${i.end != null ? "–" + fmtT(i.end) : ""}** · ${i.category} · ${i.note}${i.render ? ` _(sur ${i.render})_` : ""}`;
  fs.writeFileSync(path.join(p.path, "FEEDBACK.md"),
    `# Retours pour le monteur IA — ${p.title}\n\nÉcrit par TV Cat Editing. Chaque ligne = un retour horodaté sur le rendu indiqué.\nTraiter les retours ouverts, puis les cocher dans TV Cat Editing (ou passer \`status\` à \`fait\` dans editingos/feedback.json).\n\n## À faire (${open.length})\n\n${open.map(line).join("\n") || "_Rien._"}\n\n## Fait (${done.length})\n\n${done.map(line).join("\n") || "_Rien._"}\n`);
}

// ---------- jobs (render / studio / timeline) ----------
const jobs = new Map();
function runJob(kind, p, args) {
  const id = crypto.randomUUID().slice(0, 8);
  const job = { id, kind, project: p.id, title: p.title, status: "en cours", log: "", started: Date.now(), ended: null };
  jobs.set(id, job);
  const child = spawn("npx", ["hyperframes", ...args], { cwd: p.path, env: childEnv(), shell: true });
  const push = (d) => { job.log = (job.log + d.toString()).slice(-20000); };
  child.stdout.on("data", push); child.stderr.on("data", push);
  child.on("close", (code) => {
    job.status = code === 0 ? "terminé" : "échec"; job.ended = Date.now();
    logActivity(kind === "render" ? (code === 0 ? "render_done" : "render_failed") : kind + "_" + (code === 0 ? "ok" : "failed"), { project: p.id, title: p.title, seconds: Math.round((job.ended - job.started) / 1000) });
  });
  return job;
}
const timelineCache = new Map();
function timeline(p) {
  const key = p.id + ":" + p.modified;
  if (timelineCache.has(key)) return Promise.resolve(timelineCache.get(key));
  return new Promise((resolve) => {
    const child = spawn("npx", ["hyperframes", "timeline", "--json"], { cwd: p.path, env: childEnv(), shell: true });
    let out = "";
    child.stdout.on("data", (d) => (out += d));
    child.on("close", () => {
      try {
        const j = JSON.parse(out.slice(out.indexOf("{")));
        const tracks = (j.timeline?.tracks || []).map((t) => ({ kind: t.kind, rows: (t.rows || []).map((r) => ({ id: r.id, kind: r.kind, start: r.absStart ?? r.start, end: r.absEnd ?? r.end, src: r.src })) }));
        const res = { duration: j.timeline?.duration || 0, tracks };
        timelineCache.set(key, res); resolve(res);
      } catch { resolve({ duration: 0, tracks: [], error: "Timeline illisible (le projet passe-t-il `npx hyperframes check` ?)" }); }
    });
  });
}

// ---------- http ----------
const MIME = { ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8", ".json": "application/json; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".mp4": "video/mp4", ".webm": "video/webm", ".mov": "video/quicktime", ".wav": "audio/wav", ".mp3": "audio/mpeg", ".woff2": "font/woff2", ".md": "text/markdown; charset=utf-8" };
const send = (res, code, body, type = "application/json; charset=utf-8") => { res.writeHead(code, { "Content-Type": type, "Cache-Control": "no-store" }); res.end(typeof body === "string" || Buffer.isBuffer(body) ? body : JSON.stringify(body)); };
const body = (req) => new Promise((r) => { let b = ""; req.on("data", (d) => (b += d)); req.on("end", () => { try { r(b ? JSON.parse(b) : {}); } catch { r({}); } }); });
function serveFile(req, res, file) {
  let st;
  try { st = fs.statSync(file); if (!st.isFile()) throw 0; } catch { return send(res, 404, { error: "introuvable" }); }
  const type = MIME[path.extname(file).toLowerCase()] || "application/octet-stream";
  const range = req.headers.range;
  if (range) {
    const [a, b] = range.replace("bytes=", "").split("-");
    const start = +a || 0, end = b ? +b : st.size - 1;
    res.writeHead(206, { "Content-Type": type, "Accept-Ranges": "bytes", "Content-Range": `bytes ${start}-${end}/${st.size}`, "Content-Length": end - start + 1 });
    return fs.createReadStream(file, { start, end }).pipe(res);
  }
  res.writeHead(200, { "Content-Type": type, "Content-Length": st.size, "Accept-Ranges": "bytes", "Cache-Control": "no-store" });
  fs.createReadStream(file).pipe(res);
}
const inside = (base, rel) => { const f = path.resolve(base, rel); return f.startsWith(path.resolve(base) + path.sep) ? f : null; };

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://x");
  const parts = url.pathname.split("/").filter(Boolean).map(decodeURIComponent);
  try {
    if (parts[0] === "api") {
      const [, a, id, b, c] = parts;
      if (a === "overview") { const list = scan(); return send(res, 200, { stats: stats(list), projects: list }); }
      if (a === "refresh" && req.method === "POST") { const list = scan(); logActivity("refresh", { projects: list.length, ms: lastScan.ms }); return send(res, 200, { stats: stats(list), projects: list }); }
      if (a === "activity") return send(res, 200, readActivity().slice(0, 300));
      if (a === "jobs") return send(res, 200, id ? jobs.get(id) || null : [...jobs.values()].reverse());
      if (a === "library") {
        if (req.method === "POST" && ["formats", "references"].includes(id)) {
          const f = path.join(LIB, id + ".json"), list = readJSON(f, []), item = await body(req);
          item.id = (item.name || "item").toLowerCase().normalize("NFD").replace(/[^\w]+/g, "-").replace(/^-|-$/g, "") + "-" + Date.now().toString(36);
          item.custom = true; list.push(item); fs.writeFileSync(f, JSON.stringify(list, null, 2));
          logActivity("library_add", { kind: id, name: item.name });
          return send(res, 200, item);
        }
        return send(res, 200, { formats: readJSON(path.join(LIB, "formats.json"), []), charte: readJSON(path.join(LIB, "charte.json"), []), references: readJSON(path.join(LIB, "references.json"), []) });
      }
      if (a === "tidy" && req.method === "POST") {
        let moved = 0, bytes = 0;
        for (const p of scan()) for (const r of p.renders.slice(1)) {
          const dst = path.join(p.path, "renders", "_archive"); fs.mkdirSync(dst, { recursive: true });
          fs.renameSync(path.join(p.path, r.file), path.join(dst, r.name)); moved++; bytes += r.size;
        }
        logActivity("tidy", { moved, bytes });
        return send(res, 200, { moved, bytes });
      }
      if (a === "projects" && id) {
        const p = project(id);
        if (!p) return send(res, 404, { error: "projet introuvable" });
        if (!b) return send(res, 200, p);
        if (b === "timeline") return send(res, 200, await timeline(p));
        if (b === "feedback") {
          const items = readJSON(fbFile(p), []);
          if (req.method === "GET") return send(res, 200, items);
          if (req.method === "POST") {
            const it = await body(req);
            const item = { id: crypto.randomUUID().slice(0, 8), time: +it.time || 0, end: it.end != null && it.end !== "" ? +it.end : null, category: it.category || "Autre", note: String(it.note || "").trim(), status: "à faire", render: it.render || null, createdAt: new Date().toISOString() };
            if (!item.note) return send(res, 400, { error: "note vide" });
            items.push(item); items.sort((x, y) => x.time - y.time); writeFeedback(p, items);
            logActivity("feedback", { project: p.id, title: p.title, time: item.time, category: item.category, note: item.note });
            return send(res, 200, item);
          }
          if (req.method === "PATCH" && c) { const it = items.find((i) => i.id === c); if (it) Object.assign(it, await body(req)); writeFeedback(p, items); if (it?.status === "fait") logActivity("feedback_done", { project: p.id, title: p.title, note: it.note }); return send(res, 200, it || null); }
          if (req.method === "DELETE" && c) { writeFeedback(p, items.filter((i) => i.id !== c)); return send(res, 200, { ok: true }); }
        }
        if (b === "meta" && req.method === "POST") {
          const f = path.join(p.path, "editingos.json"), cur = readJSON(f, {}), patch = await body(req);
          fs.writeFileSync(f, JSON.stringify({ ...cur, ...patch }, null, 2)); scan();
          return send(res, 200, project(id));
        }
        if (b === "render" && req.method === "POST") {
          const n = p.renders.length + 1;
          const job = runJob("render", p, ["render", "--output", `renders/${p.slug}-v${n}.mp4`]);
          logActivity("render_start", { project: p.id, title: p.title, job: job.id });
          return send(res, 200, job);
        }
        if (b === "studio" && req.method === "POST") {
          const port = 3002 + (parseInt(p.id.slice(0, 4), 16) % 200);
          const job = runJob("studio", p, ["preview", "--background", "--no-open", `--port=${port}`]);
          logActivity("studio_open", { project: p.id, title: p.title, port });
          return send(res, 200, { job: job.id, url: `http://localhost:${port}` });
        }
        if (b === "reveal" && req.method === "POST") {
          const target = c === "render" && p.renders[0] ? path.join(p.path, p.renders[0].file) : p.path;
          if (process.platform === "win32") spawn("explorer.exe", c === "render" ? ["/select,", target] : [target], { detached: true });
          else spawn(process.platform === "darwin" ? "open" : "xdg-open", [p.path], { detached: true });
          return send(res, 200, { ok: true });
        }
      }
      return send(res, 404, { error: "route inconnue" });
    }
    if (parts[0] === "media") { const p = project(parts[1]); const f = p && inside(p.path, parts.slice(2).join("/")); return f ? serveFile(req, res, f) : send(res, 404, { error: "introuvable" }); }
    if (parts[0] === "library") { const f = inside(LIB, parts.slice(1).join("/")); return f ? serveFile(req, res, f) : send(res, 404, {}); }
    const f = parts.length ? inside(PUBLIC, parts.join("/")) : path.join(PUBLIC, "index.html");
    return serveFile(req, res, f || path.join(PUBLIC, "index.html"));
  } catch (e) {
    return send(res, 500, { error: String(e.message || e) });
  }
});

const { port } = config();
server.listen(port, "127.0.0.1", () => {
  const list = scan();
  console.log(`TV Cat Editing → http://localhost:${port}  (${list.length} projet(s), scan ${lastScan.ms} ms)`);
  if (!fs.existsSync(ACTIVITY)) logActivity("install", { projects: list.length });
});
