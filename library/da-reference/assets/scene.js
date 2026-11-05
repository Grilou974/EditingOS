// 3D volontairement limitée (retour du 05/11 : « trop de 3D, ça fait PlayStation 2 ») : le caddie seulement.
// Tout le reste est en 2D dans gen.py. Piloté par le temps HyperFrames (hf-seek). Crédits : CREDITS.md
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

const W = 1080, H = 1920, GAUCHE = 45;   // tout décalé vers la gauche : zone de sécurité TikTok (colonne d'icônes à droite)
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById("t3d"), alpha: true, antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H, false); renderer.setPixelRatio(1); renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
const scene = new THREE.Scene();
scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
const camera = new THREE.PerspectiveCamera(30, W / H, 0.1, 200);
const sun = new THREE.DirectionalLight(0xffffff, 1.6); sun.position.set(4, 9, 6); scene.add(sun);

const OR = 0xf2c12e;
const c01 = (x) => Math.min(1, Math.max(0, x));
const outBack = (x) => { x = c01(x); const c = 1.70158; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
const io = (x) => { x = c01(x); return x * x * (3 - 2 * x); };
const pop = (t, a, d = 0.35) => outBack((t - a) / d);

const M = {};
const loader = new GLTFLoader();
async function charge(nom, taille) {
  const g = await loader.loadAsync(`assets/3d/${nom}.glb`), r = g.scene, b = new THREE.Box3().setFromObject(r), v = b.getSize(new THREE.Vector3()), c = b.getCenter(new THREE.Vector3());
  r.position.set(-c.x, -b.min.y, -c.z); const w = new THREE.Group(); w.add(r); w.scale.setScalar(taille / Math.max(v.x, v.y, v.z)); w.userData.s = w.scale.x; M[nom] = w;
}
const copie = (nom) => { const c = M[nom].clone(true); c.userData.s = M[nom].userData.s; return c; };

const SHOTS = [];
function shot(t0, t1, cam, build) { const grp = new THREE.Group(); grp.visible = false; scene.add(grp); SHOTS.push({ t0, t1, cam, grp, maj: build(grp) }); }

function construire() {
  // A — le caddie sous les barres (jamais dedans)
  shot(T.iles, T.ilesFin, () => ({ p: [0, 1.3, 9.2], c: [0, 0.5, 0], up: -290 }), (g) => {
    const c = copie("caddie"); g.add(c); const s = c.userData.s;
    return (t) => { c.scale.setScalar(s * Math.max(pop(t, T.ile1, 0.4), 0.001)); c.rotation.y = 0.55 + Math.sin(t * 0.9) * 0.3; };
  });

  // D — le caddie au bout de la chaîne (le reste de la chaîne est en 2D dans gen.py)
  shot(T.c5, T.chaineFin, () => ({ p: [0, 1.3, 13], c: [0, 0.5, 0], up: -330, x: 205 }), (g) => {
    const c = copie("caddie"); g.add(c); const s = c.userData.s;
    return (t) => { c.scale.setScalar(s * Math.max(pop(t, T.c5, 0.4), 0.001)); c.rotation.y = 0.55 + Math.sin(t * 0.9) * 0.3; };
  });

  // J — le caddie, et ce sont les habitants qui paient
  shot(T.paient, T.paientFin, () => ({ p: [0, 2.2, 11.5], c: [0, 0.8, 0], up: 30 }), (g) => {
    const c = copie("caddie"); const s = c.userData.s * 2.3; g.add(c);
    const pcs = Array.from({ length: 18 }, (_, i) => { const m = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 0.045, 28), new THREE.MeshStandardMaterial({ color: OR, metalness: 0.8, roughness: 0.3 })); g.add(m); return { m, x: Math.sin(i * 2.4) * 0.8, z: Math.cos(i * 1.7) * 0.4, d: T.paient + 0.17 * i, r: i }; });
    return (t) => {
      c.scale.setScalar(s * Math.max(pop(t, T.paient, 0.35), 0.001)); c.rotation.y = 0.7 + (t - T.paient) * 0.4;
      for (const p of pcs) { const u = (t - p.d) / 0.9; p.m.visible = u > 0 && u < 1; p.m.position.set(p.x, 3.7 - 2.9 * u * u, p.z); p.m.rotation.set(t * 3 + p.r, t * 2, 0); }
    };
  });
}

function rendre(t) {
  let actif = null;
  for (const s of SHOTS) { const v = t >= s.t0 && t < s.t1; s.grp.visible = v; if (v) { actif = s; s.maj(t); } }
  renderer.domElement.style.opacity = actif ? 1 : 0;
  if (actif) {
    const c = actif.cam(t); camera.fov = c.fov || 30; camera.position.set(...c.p); camera.lookAt(...c.c);
    camera.setViewOffset(W, H, GAUCHE + (c.x || 0), c.up || 0, W, H); camera.updateProjectionMatrix();
    renderer.render(scene, camera);
  } else renderer.clear();
}

window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {};
const T = window.__T3D;
window.__hf.buildReady["scene-gbh"] = (async () => {
  await document.fonts.load("800 60px Inter");
  await charge("caddie", 1.05);
  construire(); rendre(window.__hfThreeTime || 0);
})();
window.addEventListener("hf-seek", (e) => { if (SHOTS.length) rendre(e.detail.time); });
