// Contrôle des chevauchements (14/11) : à coller dans la console d'un navigateur sur index.html (serveur local http.server sur montages/).
// Parcourt la vidéo tous les 0,2 s et liste chaque paire d'éléments visibles (cartes, images, pastilles, titres, sous-titres) qui se recouvrent.
await new Promise(r => setTimeout(r, 2500));
const tl = window.__timelines.main; const END = tl.duration();
function vis(el){ let o=1, e=el; while(e && e.id!=='root'){ const s=getComputedStyle(e); o*=parseFloat(s.opacity); e=e.parentElement;} return o; }
const out = []; const seen = new Set();
for (let t = 0.2; t < END - 3.5; t += 0.2) {
  tl.seek(t, false);
  const items = [...document.querySelectorAll('#fx .it, #c1 .it, .st')].filter(e => vis(e) > 0.3).map(e => { const inner = e.classList.contains('it') ? (e.querySelector('.fl > *')||e) : e; const r = inner.getBoundingClientRect(); const txt = ((e.innerText||'').trim().replace(/\n/g,' ').slice(0,30)) || (e.querySelector('img')?.getAttribute('src')||e.tagName).split('/').pop(); return {r, txt}; });
  for (let i=0;i<items.length;i++) for (let j=i+1;j<items.length;j++){ const a=items[i].r,b=items[j].r; const w=Math.min(a.right,b.right)-Math.max(a.left,b.left), h=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top); if(w>4&&h>4){ const k=items[i].txt+'|'+items[j].txt; if(!seen.has(k)){ seen.add(k); out.push(`${t.toFixed(1)} ${items[i].txt} X ${items[j].txt} (${Math.round(w)}x${Math.round(h)})`);} } }
}
out.join('\n') || 'aucun chevauchement'
