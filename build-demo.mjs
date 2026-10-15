// Builds the static showcase (GitHub Pages) into docs/ from a running EditingOS.
// Usage: node server.mjs  (in another terminal), then: node build-demo.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(HERE, "docs");
const BASE = process.env.EOS_URL || "http://localhost:4321";
const get = async (u) => { const r = await fetch(BASE + u); if (!r.ok) throw new Error(u + " → " + r.status); return r.json(); };
const write = (rel, data) => { const f = path.join(OUT, rel); fs.mkdirSync(path.dirname(f), { recursive: true }); fs.writeFileSync(f, typeof data === "string" ? data : JSON.stringify(data)); };
// never publish local absolute paths
const hide = (p) => "…\\videos\\" + path.basename(p);

fs.rmSync(OUT, { recursive: true, force: true });
const overview = await get("/api/overview");
overview.stats.roots = ["…\\videos"];
for (const p of overview.projects) {
  const src = p.path;
  p.path = hide(src);
  p.feedbackOpen = 0; p.feedbackTotal = 0;
  write(`api/projects/${p.id}/timeline.json`, await get(`/api/projects/${p.id}/timeline`));
  for (const r of p.renders) {
    const dst = path.join(OUT, "media", p.id, r.file);
    fs.mkdirSync(path.dirname(dst), { recursive: true });
    fs.copyFileSync(path.join(src, r.file), dst);
  }
}
write("api/overview.json", overview);
write("api/library.json", await get("/api/library"));
write("api/activity.json", [{ at: new Date().toISOString(), type: "install", projects: overview.projects.length }]);
fs.cpSync(path.join(HERE, "library"), path.join(OUT, "library"), { recursive: true, filter: (f) => !f.endsWith(".py") });
for (const f of ["app.css", "app.js"]) fs.copyFileSync(path.join(HERE, "public", f), path.join(OUT, f));
write("index.html", fs.readFileSync(path.join(HERE, "public", "index.html"), "utf8").replace("<script src=\"app.js\">", "<script>window.EOS_STATIC = true;</script>\n    <script src=\"app.js\">"));
write(".nojekyll", "");
console.log(`docs/ prêt — ${overview.projects.length} projet(s)`);
