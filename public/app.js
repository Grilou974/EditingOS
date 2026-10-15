// EditingOS front — vanilla, hash routed.
const $ = (s, el = document) => el.querySelector(s);
const view = $("#view");
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const api = async (url, opts = {}) => {
  const r = await fetch(url, { headers: { "Content-Type": "application/json" }, ...opts, body: opts.body ? JSON.stringify(opts.body) : undefined });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.error || r.statusText);
  return j;
};
const store = { get: (k, d) => { try { return JSON.parse(localStorage.getItem("eos:" + k)) ?? d; } catch { return d; } }, set: (k, v) => { try { localStorage.setItem("eos:" + k, JSON.stringify(v)); } catch {} } };
const toast = (m) => { const t = $("#toast"); t.textContent = m; t.classList.add("on"); clearTimeout(toast.h); toast.h = setTimeout(() => t.classList.remove("on"), 2400); };
const size = (b) => (b >= 1e9 ? (b / 1e9).toFixed(1) + " GB" : b >= 1e6 ? Math.round(b / 1e6) + " MB" : Math.round(b / 1e3) + " KB");
const date = (ms) => (ms ? new Date(ms).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" }) : "—");
const ago = (iso) => {
  if (!iso) return "jamais";
  const s = (Date.now() - new Date(iso).getTime()) / 1000;
  if (s < 45) return "à l'instant";
  if (s < 3600) return `il y a ${Math.round(s / 60)} min`;
  if (s < 86400) return `il y a ${Math.round(s / 3600)} h`;
  return `il y a ${Math.round(s / 86400)} j`;
};
const tc = (s) => `${String(Math.floor(s / 60)).padStart(2, "0")}:${(s % 60).toFixed(1).padStart(4, "0")}`;
const parseTc = (v) => { const m = String(v).trim().match(/^(?:(\d+):)?(\d+(?:[.,]\d+)?)$/); return m ? (+(m[1] || 0)) * 60 + parseFloat(m[2].replace(",", ".")) : null; };
const media = (p, file) => `/media/${p.id}/${file.split("/").map(encodeURIComponent).join("/")}`;
const STATE = { rendu: "Rendu à jour", perime: "Rendu périmé", brouillon: "Brouillon" };

let data = { stats: null, projects: [] };
async function load(refresh = false) {
  data = await api(refresh ? "/api/refresh" : "/api/overview", refresh ? { method: "POST" } : {});
  renderStats();
  return data;
}
function renderStats() {
  const s = data.stats;
  $("#stats").innerHTML = `
    <div class="stat"><div class="v">${s.projects}</div><div class="k">Projets</div><div class="s">${s.utilityHidden} utilitaire masqué${s.utilityHidden > 1 ? "s" : ""}</div></div>
    <div class="stat"><div class="v y">${s.withRender}</div><div class="k">Avec un rendu</div><div class="s">sur ${s.projects} projet${s.projects > 1 ? "s" : ""}</div></div>
    <div class="stat"><div class="v r">${s.stale}</div><div class="k">Rendus périmés</div><div class="s">${s.stale ? "à re-rendre" : "tout est à jour"}</div></div>
    <div class="stat"><div class="v">${size(s.disk)}</div><div class="k">Disque rendus</div>${s.tidy ? `<button class="chipbtn" id="tidy" title="Déplace les anciennes versions dans renders/_archive">Ranger ${size(s.tidy)}</button>` : `<div class="s">rien à ranger</div>`}</div>`;
  const tidy = $("#tidy");
  if (tidy) tidy.onclick = async () => { const r = await api("/api/tidy", { method: "POST" }); toast(`${r.moved} ancienne(s) version(s) archivée(s)`); await load(); route(); };
}

// ---------- router ----------
function route() {
  let [r, a] = location.hash.replace(/^#\/?/, "").split("/");
  r = r || "projets";
  document.querySelectorAll("#nav a").forEach((x) => x.classList.toggle("on", x.dataset.r === (r === "p" ? "projets" : r)));
  if (r === "p" && a) return pageProject(a);
  if (r === "studio") return pageStudio(a);
  if (r === "bibliotheques") return pageLibrary(a || "formats");
  if (r === "activite") return pageActivity();
  return pageProjects();
}
window.addEventListener("hashchange", route);
$("#refresh").onclick = async (e) => { e.target.disabled = true; await load(true); e.target.disabled = false; toast(`Relevé en ${data.stats.scan.ms} ms`); route(); };

// ---------- Projets ----------
function pageProjects() {
  const f = store.get("filters", { q: "", family: "", type: "", format: "", state: "", sort: "modified", stale: false, hideUtility: true });
  const opts = (key) => [...new Set(data.projects.map((p) => p[key]))].sort();
  const sel = (id, label, key, values, map = (v) => v) => `<select class="inp" id="${id}"><option value="">${label}</option>${values.map((v) => `<option value="${esc(v)}" ${f[key] === v ? "selected" : ""}>${esc(map(v))}</option>`).join("")}</select>`;
  view.innerHTML = `
    <div class="h1"><h1>Projets</h1><span class="cnt" id="cnt"></span></div>
    <p class="lead">Le système de fichiers fait foi. Relevé ${ago(data.stats.scan.at)} en ${data.stats.scan.ms} ms · <code title="${esc(data.stats.roots.join(" · "))}">${esc(data.stats.roots.map((r) => "…\\" + r.split(/[\\/]/).slice(-2).join("\\")).join(" · "))}</code></p>
    <div class="filters">
      <input class="inp search" id="q" placeholder="Chercher un nom ou un slug" value="${esc(f.q)}" />
      ${sel("family", "Toutes les familles", "family", opts("family"))}
      ${sel("type", "Tous les types", "type", opts("type"))}
      ${sel("format", "Tous les formats", "format", opts("format"))}
      ${sel("state", "Tous les états", "state", ["rendu", "perime", "brouillon"], (v) => STATE[v])}
      <select class="inp" id="sort"><option value="modified">Modifié récemment</option><option value="created" ${f.sort === "created" ? "selected" : ""}>Créé récemment</option><option value="title" ${f.sort === "title" ? "selected" : ""}>Nom (A→Z)</option></select>
      <label class="check"><input type="checkbox" id="stale" ${f.stale ? "checked" : ""}/>Périmés seuls</label>
      <label class="check"><input type="checkbox" id="hideUtility" ${f.hideUtility ? "checked" : ""}/>Masquer l'utilitaire</label>
    </div>
    <div id="list"></div>`;
  const paint = () => {
    let list = data.projects.filter((p) =>
      (!f.q || (p.title + " " + p.slug).toLowerCase().includes(f.q.toLowerCase())) && (!f.family || p.family === f.family) && (!f.type || p.type === f.type) &&
      (!f.format || p.format === f.format) && (!f.state || p.state === f.state) && (!f.stale || p.state === "perime") && (!f.hideUtility || !p.utility));
    list.sort((a, b) => (f.sort === "title" ? a.title.localeCompare(b.title, "fr") : b[f.sort] - a[f.sort]));
    $("#cnt").textContent = `${list.length} / ${data.projects.filter((p) => !p.utility || !f.hideUtility).length}`;
    $("#list").innerHTML = !data.projects.length
      ? `<div class="emptystate"><h3>Aucun projet pour l'instant</h3>Les projets HyperFrames créés dans <code>${esc(data.stats.roots[0])}</code> apparaîtront ici automatiquement.</div>`
      : !list.length ? `<div class="emptystate"><h3>Rien ne correspond</h3>Modifie les filtres.</div>`
      : `<div class="grid">${list.map(card).join("")}</div>`;
    document.querySelectorAll(".card").forEach((c) => (c.onclick = () => (location.hash = "#/p/" + c.dataset.id)));
    store.set("filters", f);
  };
  ["q", "family", "type", "format", "state", "sort"].forEach((k) => ($("#" + k).oninput = (e) => { f[k] = e.target.value; paint(); }));
  ["stale", "hideUtility"].forEach((k) => ($("#" + k).onchange = (e) => { f[k] = e.target.checked; paint(); }));
  paint();
}
function card(p) {
  const r = p.renders[0];
  const src = r && media(p, r.file) + "#t=2.5";
  return `<article class="card" data-id="${p.id}">
    <div class="hd"><div><h3>${esc(p.title)}</h3><div class="date">${date(p.modified)}</div></div>
      <div class="tags"><span class="pill fam">${esc(p.family)}</span><span class="pill">${esc(p.type)}</span></div></div>
    <div class="thumb">${r ? `<video class="blur" src="${src}" muted preload="metadata"></video><video class="front" src="${src}" muted preload="metadata"></video>` : `<div class="empty">Pas encore de rendu</div>`}
      <div class="meta"><span>${esc(p.format)}</span><span class="${p.state === "perime" ? "r" : ""}">${STATE[p.state]}</span>${p.renders.length > 1 ? `<span>${p.renders.length} vidéos</span>` : ""}${p.feedbackOpen ? `<span class="y">${p.feedbackOpen} retour${p.feedbackOpen > 1 ? "s" : ""}</span>` : ""}</div></div>
  </article>`;
}

// ---------- Projet ----------
async function pageProject(id, opts = {}) {
  const p = data.projects.find((x) => x.id === id) || (await api("/api/projects/" + id).catch(() => null));
  if (!p) { view.innerHTML = `<a class="back" href="#/projets">← Projets</a><div class="emptystate"><h3>Projet introuvable</h3></div>`; return; }
  let feedback = await api(`/api/projects/${id}/feedback`);
  let current = p.renders[0];
  let fbOpen = opts.fbOpen ?? store.get("fbOpen", false);
  view.innerHTML = `
    <a class="back" href="#/projets">← Projets</a>
    <div class="proj">
      <div class="player">${current ? `<video id="vid" controls preload="metadata" src="${media(p, current.file)}"></video><div class="markers" id="markers"></div>` : `<div class="thumb"><div class="empty">Pas encore de rendu — lance « Rendre la vidéo »</div></div>`}</div>
      <div class="side">
        <h2>${esc(p.title)}</h2>
        <div class="row"><span class="pill fam">${esc(p.family)}</span><span class="pill">${esc(p.type)}</span><span class="pill">${esc(p.format)}</span><span class="pill st-${p.state}">${STATE[p.state]}</span>${p.tags.map((t) => `<span class="pill">${esc(t)}</span>`).join("")}</div>
        ${p.message ? `<p class="msg">${esc(p.message)}</p>` : ""}
        <div class="actions">
          <button class="btn primary" id="fbToggle">✎ Apporter des modifications</button>
          <button class="btn" id="render">↻ Rendre la vidéo</button>
          <a class="btn" href="#/studio/${p.id}">Ouvrir dans le Studio</a>
        </div>
        <div id="fbwrap"></div>
        <div class="box"><h4>Fichier sur l'ordinateur</h4>
          <div class="path"><code id="fpath">${esc(current ? p.path + "\\" + current.file.replace(/\//g, "\\") : p.path)}</code><button class="btn sm" id="copy">Copier</button><button class="btn sm" id="reveal">Ouvrir le dossier</button></div></div>
        ${p.renders.length ? `<div class="box"><h4>Vidéos du projet (${p.renders.length})</h4><div class="versions">${p.renders.map((r, i) => `<button data-i="${i}" class="${i === 0 ? "on" : ""}"><b>${esc(r.name)}</b><span>${size(r.size)} · ${date(r.mtime)}</span></button>`).join("")}</div></div>` : ""}
        <div class="box"><h4>Détails</h4><div class="lead" style="margin:0">Créé le ${date(p.created)} · modifié le ${date(p.modified)}${p.workflow ? ` · workflow <code>${esc(p.workflow)}</code>` : ""}${p.length ? ` · ${esc(p.length)}` : ""}</div>
          <div class="actions" style="margin-top:12px"><button class="btn sm" id="editMeta">Modifier titre / famille / type</button></div></div>
      </div>
    </div>`;
  const vid = $("#vid");
  const paintMarkers = () => {
    const m = $("#markers"); if (!m || !vid) return;
    const d = vid.duration || 1;
    m.innerHTML = feedback.map((f) => `<i class="${f.status === "fait" ? "done" : ""}" style="left:${(f.time / d) * 100}%" title="${tc(f.time)} · ${esc(f.note)}" data-t="${f.time}"></i>`).join("");
    m.querySelectorAll("i").forEach((i) => (i.onclick = () => { vid.currentTime = +i.dataset.t; vid.pause(); }));
  };
  if (vid) vid.addEventListener("loadedmetadata", paintMarkers);
  const paintFb = () => {
    const w = $("#fbwrap");
    if (!fbOpen) { w.innerHTML = ""; return; }
    const open = feedback.filter((f) => f.status !== "fait").length;
    w.innerHTML = `<div class="fbpanel">
      <h3>Retours au monteur IA</h3>
      <p class="hint">Mets la vidéo en pause au bon moment, décris le problème. Chaque retour est écrit dans <code>FEEDBACK.md</code> du projet : demande ensuite à Claude « traite les retours d'EditingOS ».</p>
      <div class="fbform">
        <span class="tc"><input class="inp" id="t0" value="${tc(vid ? vid.currentTime : 0)}" title="Début (mm:ss.s)"/><button class="btn sm" id="now" title="Prendre le temps actuel de la vidéo">⏱</button></span>
        <span class="tc">→ <input class="inp" id="t1" placeholder="fin" title="Fin (optionnel)"/></span>
        <select class="inp" id="cat">${["Cut", "Sous-titre", "Texte", "Animation", "Audio / voix", "Rythme", "Couleur", "Autre"].map((c) => `<option>${c}</option>`).join("")}</select>
        <textarea id="note" placeholder="Ex. : à 00:12, le titre sort trop tôt, le garder 1 s de plus."></textarea>
      </div>
      <div class="actions" style="margin-top:12px"><button class="btn primary" id="send">Envoyer au monteur</button><button class="btn" id="prompt">Copier la consigne pour Claude</button><span class="lead" style="margin:0 0 0 auto">${open} ouvert${open > 1 ? "s" : ""} · ${feedback.length} au total</span></div>
      <div class="fblist">${feedback.map((f) => `<div class="fbi ${f.status === "fait" ? "done" : ""}" data-id="${f.id}">
        <span class="t" data-t="${f.time}">${tc(f.time)}${f.end != null ? "–" + tc(f.end) : ""}</span><span class="cat">${esc(f.category)}</span><span class="note">${esc(f.note)}</span>
        <span class="ops"><button class="iconbtn" data-op="done" title="${f.status === "fait" ? "Rouvrir" : "Marquer fait"}">${f.status === "fait" ? "↺" : "✓"}</button><button class="iconbtn" data-op="del" title="Supprimer">✕</button></span></div>`).join("")}</div>
    </div>`;
    $("#now").onclick = () => vid && ($("#t0").value = tc(vid.currentTime));
    $("#send").onclick = async () => {
      const note = $("#note").value.trim(); if (!note) return toast("Écris le retour d'abord");
      const time = parseTc($("#t0").value); if (time == null) return toast("Temps invalide (mm:ss.s)");
      const end = $("#t1").value ? parseTc($("#t1").value) : null;
      await api(`/api/projects/${p.id}/feedback`, { method: "POST", body: { time, end, category: $("#cat").value, note, render: current?.name } });
      feedback = await api(`/api/projects/${p.id}/feedback`); paintFb(); paintMarkers(); toast("Retour envoyé au monteur");
    };
    $("#prompt").onclick = () => {
      const txt = `Traite les retours EditingOS du projet « ${p.title} » : lis ${p.path}\\FEEDBACK.md, applique chaque retour ouvert dans la composition HyperFrames, re-rends la vidéo, puis passe les retours traités à « fait » dans editingos\\feedback.json.`;
      navigator.clipboard.writeText(txt).then(() => toast("Consigne copiée"), () => toast(txt));
    };
    w.querySelectorAll(".fbi .t").forEach((el) => (el.onclick = () => vid && ((vid.currentTime = +el.dataset.t), vid.pause())));
    w.querySelectorAll(".fbi .iconbtn").forEach((b) => (b.onclick = async () => {
      const fid = b.closest(".fbi").dataset.id, f = feedback.find((x) => x.id === fid);
      if (b.dataset.op === "done") await api(`/api/projects/${p.id}/feedback/${fid}`, { method: "PATCH", body: { status: f.status === "fait" ? "à faire" : "fait" } });
      else await api(`/api/projects/${p.id}/feedback/${fid}`, { method: "DELETE" });
      feedback = await api(`/api/projects/${p.id}/feedback`); paintFb(); paintMarkers();
    }));
    if (vid) vid.ontimeupdate = () => { if (vid.paused) $("#t0").value = tc(vid.currentTime); };
    if (vid) vid.onpause = vid.onseeked = () => ($("#t0").value = tc(vid.currentTime));
  };
  $("#fbToggle").onclick = () => { fbOpen = !fbOpen; store.set("fbOpen", fbOpen); paintFb(); };
  paintFb();
  $("#copy").onclick = () => navigator.clipboard.writeText($("#fpath").textContent).then(() => toast("Chemin copié"));
  $("#reveal").onclick = () => api(`/api/projects/${p.id}/reveal/${current ? "render" : ""}`, { method: "POST" }).then(() => toast("Dossier ouvert dans l'Explorateur"));
  view.querySelectorAll(".versions button").forEach((b) => (b.onclick = () => {
    current = p.renders[+b.dataset.i]; vid.src = media(p, current.file);
    $("#fpath").textContent = p.path + "\\" + current.file.replace(/\//g, "\\");
    view.querySelectorAll(".versions button").forEach((x) => x.classList.toggle("on", x === b));
  }));
  $("#render").onclick = async (e) => { e.target.disabled = true; const job = await api(`/api/projects/${p.id}/render`, { method: "POST" }); toast("Rendu lancé — suivi dans le Studio"); location.hash = `#/studio/${p.id}?job=${job.id}`; };
  $("#editMeta").onclick = () => modal("Projet", [["title", "Titre", p.title], ["family", "Famille (ex. Politique, Ads, Éducation)", p.family], ["type", "Type (ex. Short, Explainer, talking-head)", p.type], ["tags", "Tags (séparés par des virgules)", p.tags.join(", ")]], async (v) => {
    v.tags = v.tags.split(",").map((s) => s.trim()).filter(Boolean);
    await api(`/api/projects/${p.id}/meta`, { method: "POST", body: v }); await load(); pageProject(id, { fbOpen });
  });
}

// ---------- Studio ----------
let studioPoll;
async function pageStudio(idq) {
  clearInterval(studioPoll);
  const [id, q] = (idq || "").split("?");
  const jobId = new URLSearchParams(q || "").get("job");
  const list = data.projects.filter((p) => !p.utility);
  const p = list.find((x) => x.id === id) || list[0];
  view.innerHTML = `<div class="h1"><h1>Studio</h1><span class="cnt">${p ? esc(p.slug) : ""}</span></div>
    <p class="lead">La timeline réelle du projet, ses retours et les rendus en cours. L'édition fine se fait dans le Studio HyperFrames.</p>
    ${!p ? `<div class="emptystate"><h3>Aucun projet</h3></div>` : `
    <div class="filters"><select class="inp" id="pick">${list.map((x) => `<option value="${x.id}" ${x.id === p.id ? "selected" : ""}>${esc(x.title)}</option>`).join("")}</select>
      <button class="btn" id="hf">Lancer le Studio HyperFrames</button><button class="btn primary" id="rd">↻ Rendre la vidéo</button><a class="btn" href="#/p/${p.id}">Fiche projet</a></div>
    <div class="studio">
      <div class="player">${p.renders[0] ? `<video id="svid" controls preload="metadata" src="${media(p, p.renders[0].file)}"></video>` : `<div class="thumb"><div class="empty">Pas encore de rendu</div></div>`}</div>
      <div><div class="tl" id="tl"><div class="lead" style="margin:0">Lecture de la timeline…</div></div><div id="jobs"></div></div>
    </div>`}`;
  if (!p) return;
  $("#pick").onchange = (e) => (location.hash = "#/studio/" + e.target.value);
  $("#hf").onclick = async (e) => {
    e.target.disabled = true; const r = await api(`/api/projects/${p.id}/studio`, { method: "POST" });
    toast("Studio en démarrage…"); setTimeout(() => { window.open(r.url, "_blank"); e.target.disabled = false; }, 6000);
  };
  $("#rd").onclick = async (e) => { e.target.disabled = true; const j = await api(`/api/projects/${p.id}/render`, { method: "POST" }); location.hash = `#/studio/${p.id}?job=${j.id}`; };
  const [tl, fb] = await Promise.all([api(`/api/projects/${p.id}/timeline`), api(`/api/projects/${p.id}/feedback`)]);
  const D = tl.duration || 1;
  const step = D > 120 ? 30 : D > 40 ? 10 : 5;
  const rows = tl.tracks.flatMap((t) => t.rows.map((r) => ({ ...r, tk: t.kind })));
  $("#tl").innerHTML = tl.error ? `<div class="lead" style="margin:0">${esc(tl.error)}</div>` : `
    <div class="ruler">${Array.from({ length: Math.floor(D / step) + 1 }, (_, i) => `<span style="left:${((i * step) / D) * 100}%">${tc(i * step).slice(0, 5)}</span>`).join("")}</div>
    <div class="fbmarks">${fb.map((f) => `<i style="left:${(f.time / D) * 100}%" title="${tc(f.time)} · ${esc(f.note)}"></i>`).join("")}</div>
    <div class="tlbody">${rows.map((r) => `<div class="lane"><div class="ln" title="${esc(r.id)}">${esc(r.id || r.kind)}</div><div class="tr"><div class="clip ${["graphics", "audio", "video"].includes(r.tk) ? r.tk : "other"}" style="left:${(r.start / D) * 100}%;width:${Math.max(0.6, ((r.end - r.start) / D) * 100)}%">${esc(r.id || "")}</div></div></div>`).join("")}
      <div class="playhead" id="ph" style="left:130px"></div></div>
    <div class="lead" style="margin:10px 0 0">${rows.length} clips · ${tc(D)} · ${fb.filter((f) => f.status !== "fait").length} retour(s) ouvert(s)</div>`;
  const sv = $("#svid"), ph = $("#ph"), body = $(".tlbody");
  if (sv && ph) sv.ontimeupdate = () => { const w = body.clientWidth - 130; ph.style.left = 130 + (sv.currentTime / D) * w + "px"; };
  const pollJobs = async () => {
    const jobs = (await api("/api/jobs")).filter((j) => j.project === p.id);
    $("#jobs").innerHTML = jobs.map((j) => `<div class="box"><h4>${j.kind === "render" ? "Rendu" : "Studio"} · <span class="${j.status === "échec" ? "r" : j.status === "terminé" ? "g" : "y"}">${j.status}</span> · ${new Date(j.started).toLocaleTimeString("fr-FR")}</h4><div class="log">${esc(j.log.slice(-4000)) || "…"}</div></div>`).join("");
    const running = jobs.some((j) => j.status === "en cours");
    if (!running) { clearInterval(studioPoll); if (jobId && jobs.find((j) => j.id === jobId && j.status === "terminé")) { await load(); toast("Rendu terminé"); } }
  };
  await pollJobs();
  studioPoll = setInterval(() => (location.hash.startsWith("#/studio") ? pollJobs() : clearInterval(studioPoll)), 2000);
}

// ---------- Bibliothèques ----------
let lib;
async function pageLibrary(tab) {
  lib = await api("/api/library");
  const tabs = { formats: "Formats", charte: "Ma charte graphique", references: "Références" };
  view.innerHTML = `<div class="h1"><h1>Bibliothèques</h1><span class="cnt">${lib.formats.length + lib.charte.length + lib.references.length} éléments</span></div>
    <p class="lead">Ce que le monteur IA consulte avant de monter : la disposition de tes formats, tes animations maison et les styles de référence. Les fichiers sont dans <code>editing-os/library/</code>.</p>
    <nav class="subnav">${Object.entries(tabs).map(([k, v]) => `<a href="#/bibliotheques/${k}" class="${k === tab ? "on" : ""}">${v}</a>`).join("")}</nav><div id="lib"></div>`;
  const el = $("#lib");
  if (tab === "formats") {
    el.innerHTML = `<div class="actions"><button class="btn" id="addF">+ Nouveau format</button></div><div class="fgrid">${lib.formats.map((f) => `
      <div class="fcard"><div class="phone ${f.ratio === "16:9" ? "r169" : ""}">${(f.zones || []).map((z) => `<div class="zone ${z.kind}" style="left:${z.x}%;top:${z.y}%;width:${z.w}%;height:${z.h}%">${esc(z.label)}</div>`).join("")}</div>
        <div><h4>${esc(f.name)}</h4><div class="u">${esc(f.ratio)} · ${esc(f.usage || "")}</div><p>${esc(f.description || "")}</p>${f.rules?.length ? `<ul>${f.rules.map((r) => `<li>${esc(r)}</li>`).join("")}</ul>` : ""}</div></div>`).join("")}</div>`;
    $("#addF").onclick = () => modal("Nouveau format", [["name", "Nom", ""], ["ratio", "Ratio (9:16, 16:9, 1:1…)", "9:16"], ["usage", "Usage", ""], ["description", "Disposition des éléments à l'écran", "", true], ["rules", "Règles (une par ligne)", "", true]], async (v) => {
      v.rules = v.rules.split("\n").map((s) => s.trim()).filter(Boolean); v.zones = [];
      await api("/api/library/formats", { method: "POST", body: v }); pageLibrary("formats");
    });
  }
  if (tab === "charte") {
    const cats = [...new Set(lib.charte.map((c) => c.category))];
    let cur = store.get("charteCat", "");
    const paint = () => {
      el.innerHTML = `<div class="chips"><button data-c="" class="${!cur ? "on" : ""}">Tout</button>${cats.map((c) => `<button data-c="${esc(c)}" class="${cur === c ? "on" : ""}">${esc(c)}</button>`).join("")}</div>
        <div class="lgrid">${lib.charte.filter((c) => !cur || c.category === cur).map((c) => `<div class="lcard"><iframe loading="lazy" src="/library/${c.file}" title="${esc(c.name)}"></iframe><div class="bd"><h4>${esc(c.name)}</h4><p>${esc(c.description)}</p><div class="foot"><code>${esc(c.file)}</code><span class="pill">${esc(c.category)}</span><a class="btn sm" target="_blank" href="/library/${c.file}">Ouvrir</a></div></div></div>`).join("")}</div>`;
      el.querySelectorAll(".chips button").forEach((b) => (b.onclick = () => { cur = b.dataset.c; store.set("charteCat", cur); paint(); }));
    };
    paint();
  }
  if (tab === "references") {
    el.innerHTML = `<div class="actions"><button class="btn" id="addR">+ Nouvelle référence</button></div><div class="lgrid">${lib.references.map((r) => `<div class="lcard">${r.demo ? `<iframe loading="lazy" src="/library/${r.demo}" title="${esc(r.name)}"></iframe>` : ""}<div class="bd"><h4>${esc(r.name)}</h4><span class="lead" style="margin:0;font-size:13px">${esc(r.platform || "")}</span>
      <div class="traits">${(r.traits || []).map((t) => `<span class="pill">${esc(t)}</span>`).join("")}</div><p>${esc(r.notes || "")}</p>
      <div class="foot"><code>${esc(r.id)}</code>${r.url ? `<a class="btn sm" target="_blank" rel="noopener" href="${esc(r.url)}">Chaîne ↗</a>` : ""}</div></div></div>`).join("")}</div>`;
    $("#addR").onclick = () => modal("Nouvelle référence", [["name", "Nom de la chaîne / du style", ""], ["platform", "Plateforme", "YouTube"], ["url", "Lien", ""], ["traits", "Traits de style (séparés par des virgules)", ""], ["notes", "Ce que je veux en reprendre", "", true]], async (v) => {
      v.traits = v.traits.split(",").map((s) => s.trim()).filter(Boolean);
      await api("/api/library/references", { method: "POST", body: v }); pageLibrary("references");
    });
  }
}

// ---------- Activité ----------
const EV = {
  install: ["◆", "EditingOS installé", (e) => `${e.projects} projet(s) trouvé(s)`],
  refresh: ["↻", "Actualisation", (e) => `${e.projects} projet(s) relevé(s) en ${e.ms} ms`],
  feedback: ["✎", "Retour envoyé au monteur", (e) => `${e.title} · ${tc(e.time)} · ${e.category} — ${e.note}`],
  feedback_done: ["✓", "Retour traité", (e) => `${e.title} — ${e.note}`],
  render_start: ["▶", "Rendu lancé", (e) => e.title],
  render_done: ["●", "Rendu terminé", (e) => `${e.title} · ${e.seconds} s`],
  render_failed: ["!", "Rendu en échec", (e) => `${e.title} — voir le journal dans le Studio`],
  studio_open: ["◧", "Studio HyperFrames ouvert", (e) => `${e.title} · port ${e.port}`],
  tidy: ["▤", "Rangement des rendus", (e) => `${e.moved} version(s) archivée(s) · ${size(e.bytes || 0)}`],
  library_add: ["+", "Bibliothèque enrichie", (e) => `${e.kind === "formats" ? "Format" : "Référence"} : ${e.name}`],
};
async function pageActivity() {
  const evs = await api("/api/activity");
  view.innerHTML = `<div class="h1"><h1>Activité</h1><span class="cnt">${evs.length}</span></div><p class="lead">Tout ce qui s'est passé dans l'atelier, du plus récent au plus ancien.</p>
    <div class="act">${evs.map((e) => { const d = EV[e.type] || ["·", e.type, () => ""]; return `<div class="ev"><span class="when">${ago(e.at)}</span><span class="ic ${/failed/.test(e.type) ? "r" : /done|feedback_done/.test(e.type) ? "g" : "y"}">${d[0]}</span><div class="what"><b>${d[1]}</b><small>${esc(d[2](e))}</small></div></div>`; }).join("") || `<div class="emptystate"><h3>Rien pour l'instant</h3></div>`}</div>`;
}

// ---------- modal ----------
function modal(title, fields, onOk) {
  const m = document.createElement("div");
  m.className = "modal";
  m.innerHTML = `<div class="in"><h3>${esc(title)}</h3>${fields.map(([k, l, v, big]) => `<label>${esc(l)}${big ? `<textarea class="inp" data-k="${k}">${esc(v)}</textarea>` : `<input class="inp" data-k="${k}" value="${esc(v)}"/>`}</label>`).join("")}
    <div class="acts"><button class="btn" data-x>Annuler</button><button class="btn primary" data-ok>Enregistrer</button></div></div>`;
  document.body.append(m);
  const close = () => m.remove();
  m.onclick = (e) => e.target === m && close();
  $("[data-x]", m).onclick = close;
  $("[data-ok]", m).onclick = async () => { const v = {}; m.querySelectorAll("[data-k]").forEach((i) => (v[i.dataset.k] = i.value)); try { await onOk(v); close(); toast("Enregistré"); } catch (e) { toast(e.message); } };
  $("[data-k]", m)?.focus();
}

load().then(route).catch((e) => (view.innerHTML = `<div class="emptystate"><h3>Serveur injoignable</h3>${esc(e.message)}</div>`));
