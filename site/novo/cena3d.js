// Camada visual 3D (prova de conceito): o mesmo estúdio como diorama
// isométrico low-poly, montado a partir da mesma planta, lendo o mesmo quadro
// do motor e as mesmas posições da locomoção. Os balões continuam em HTML,
// posicionados pela projeção 3D. Carrega só quando alguém pede "ver em 3D".

import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { W, ANDARES, SALAS, SALA, retSala, MOVEIS, ESCADA } from "./planta.js";
import { PERSONAS } from "./sprites.js";
import { placa as placaPx, medeTexto, ALTURA } from "./pixelfont.js";

const U = 0.1;                                   // 1 px da cena 2D = 0,1 unidade
const PE0 = ANDARES[0].pe, PE1 = ANDARES[1].pe;
const X = x => (x - W / 2) * U;
const Yp = y => (PE0 - y) * U;                   // pés do térreo em 0; do andar de cima em 15,6
const PROF = 9, ZP = 0.4, ZF = -1.8;             // profundidade das salas; z de quem está na frente e no fundo
const NIVEL = { 0: 0, 1: Yp(PE1) };
const ALT_SALA = { 0: (PE0 - ANDARES[0].teto) * U, 1: (PE1 - ANDARES[1].teto) * U };

const COR_SALA = {
  redacao: ["#e5ddcc", "madeira"], cabine: ["#2c585d", "carpete"], arquivo: ["#d9cfb8", "pedra"], checagem: ["tijolo", "cimento"],
  portaria: ["#cfd8dc", "ladrilho"], cafe: ["#f0dbb6", "xadrez"], tecnica: ["#b6c0c9", "tecnico"], obras: ["tijolo", "cimento"], escada: ["#bdb6a9", "pedra"],
};

// ------------------------------------------------------------ texturas de pixel (desenhadas em código)
function textura(tipo, rx = 1, ry = 1) {
  const c = document.createElement("canvas"), n = 16; c.width = c.height = n;
  const g = c.getContext("2d"), R = (x, y, w, h, cor) => { g.fillStyle = cor; g.fillRect(x, y, w, h); };
  switch (tipo) {
    case "madeira": for (let y = 0; y < n; y += 2) R(0, y, n, 2, y % 4 ? "#9a6b43" : "#a8794d"); R(5, 0, 1, 2, "#7f5534"); R(12, 2, 1, 2, "#7f5534"); R(2, 4, 1, 2, "#7f5534"); R(9, 6, 1, 2, "#7f5534"); R(6, 8, 1, 2, "#7f5534"); R(14, 10, 1, 2, "#7f5534"); R(3, 12, 1, 2, "#7f5534"); R(10, 14, 1, 2, "#7f5534"); break;
    case "xadrez": for (let y = 0; y < n; y += 4) for (let x = 0; x < n; x += 4) R(x, y, 4, 4, (x + y) / 4 % 2 ? "#cdb999" : "#b4a080"); break;
    case "ladrilho": for (let y = 0; y < n; y += 4) for (let x = 0; x < n; x += 4) R(x, y, 4, 4, (x + y) / 4 % 2 ? "#9ca7ae" : "#8c979e"); break;
    case "carpete": R(0, 0, n, n, "#3a3f51"); for (let y = 0; y < n; y += 2) for (let x = y % 4; x < n; x += 6) R(x, y, 1, 1, "#444a5e"); break;
    case "tecnico": R(0, 0, n, n, "#7e8792"); R(0, 0, n, 1, "#6b7480"); R(0, 0, 1, n, "#6b7480"); R(8, 0, 1, n, "#6b7480"); R(0, 8, n, 1, "#6b7480"); break;
    case "cimento": R(0, 0, n, n, "#9b9a93"); for (let i = 0; i < 12; i++) R((i * 7) % n, (i * 5) % n, 1, 1, i % 2 ? "#8a8982" : "#aeada6"); break;
    case "pedra": R(0, 0, n, n, "#8e887b"); R(0, 0, 1, n, "#7d776b"); R(8, 0, 1, n, "#7d776b"); break;
    case "tijolo": R(0, 0, n, n, "#b98a72"); for (let y = 0; y < n; y += 4) for (let x = (y / 4 % 2) * 4; x < n + 4; x += 8) R(x, y, 7, 3, (x + y) % 3 ? "#a45e43" : "#94513a"); break;
    case "espuma": R(0, 0, n, n, "#2c585d"); for (let y = 0; y < n; y += 4) for (let x = (y / 4 % 2) * 2; x < n; x += 4) { R(x, y, 2, 2, "#23484c"); R(x, y, 2, 1, "#3a6c71"); } break;
    case "faixa": for (let x = 0; x < n; x++) R(x, 0, 1, n, (x % 8) < 4 ? "#f2c230" : "#1d1d1d"); break;
    case "cortica": R(0, 0, n, n, "#c39462"); for (let i = 0; i < 10; i++) R((i * 5) % n, (i * 3) % n, 1, 1, "#a87a4c"); break;
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace; t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter;
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rx, ry);
  return t;
}
function texturaPlaca(txt, op) {
  const linhas = txt.split("\n"), lh = ALTURA + 8 + (/[ÁÀÃÂÉÊÍÓÔÕÚ]/i.test(txt) ? 2 : 0);
  const w = Math.max(...linhas.map(medeTexto)) + 8, h = lh * linhas.length;
  const c = document.createElement("canvas"); c.width = w + 2; c.height = h + 2;
  linhas.forEach((l, i) => placaPx(c.getContext("2d"), l, (w + 2) / 2, 1 + i * lh, { pad: 4, ...op }));
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace; t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter;
  return { t, w: c.width, h: c.height };
}

const mats = new Map();
function mat(cor, op = {}) {
  const k = cor + JSON.stringify(op);
  if (!mats.has(k)) mats.set(k, new THREE.MeshStandardMaterial({ color: cor, roughness: .85, metalness: 0, flatShading: true, ...op }));
  return mats.get(k);
}
function caixa(w, h, d, material, x = 0, y = 0, z = 0, pai = null, sombra = true) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material);
  m.position.set(x, y, z); m.castShadow = sombra; m.receiveShadow = true;
  if (pai) pai.add(m);
  return m;
}
const cinza = hex => { const c = new THREE.Color(hex), hsl = {}; c.getHSL(hsl); return new THREE.Color().setHSL(hsl.h, .05, .35 + hsl.l * .4); };

// ------------------------------------------------------------ bonecos low-poly
function boneco(id) {
  const d = PERSONAS[id], g = new THREE.Group(), parte = {};
  const m = c => mat(c);
  const quadril = new THREE.Group(); quadril.position.y = 1.6; g.add(quadril);
  for (const [lado, nome] of [[-1, "pernaE"], [1, "pernaD"]]) {
    const p = new THREE.Group(); p.position.x = lado * .38; quadril.add(p);
    caixa(.55, 1.45, .6, m(d.calca), 0, -.72, 0, p); caixa(.62, .25, .78, m(d.sapato), 0, -1.48, .06, p);
    parte[nome] = p;
  }
  caixa(1.5, 1.85, .85, m(d.cor), 0, 2.5, 0, g);
  for (const [lado, nome] of [[-1, "bracoE"], [1, "bracoD"]]) {
    const b = new THREE.Group(); b.position.set(lado * .98, 3.3, 0); g.add(b);
    caixa(.42, 1.35, .48, m(d.cor), 0, -.62, 0, b); caixa(.4, .32, .44, m(d.pele), 0, -1.42, 0, b);
    parte[nome] = b;
  }
  const cab = new THREE.Group(); cab.position.y = 3.45; g.add(cab); parte.cabeca = cab;
  caixa(1.3, 1.3, 1.15, m(d.pele), 0, .7, 0, cab);
  const olho = mat("#1b1b2a");
  caixa(.14, .2, .05, olho, -.3, .72, .59, cab, false); caixa(.14, .2, .05, olho, .3, .72, .59, cab, false);
  // cabelo
  const hc = m(d.cabelo);
  if (d.estilo === "cacheado") { caixa(1.6, .7, 1.4, hc, 0, 1.45, -.05, cab); caixa(1.6, .9, .4, hc, 0, .95, -.55, cab); }
  else if (d.estilo === "longo") { caixa(1.42, .4, 1.27, hc, 0, 1.4, 0, cab); caixa(1.42, 1.6, .35, hc, 0, .5, -.5, cab); caixa(.2, 1.1, 1, hc, -.7, .8, -.05, cab); caixa(.2, 1.1, 1, hc, .7, .8, -.05, cab); }
  else if (d.estilo === "coque") { caixa(1.4, .38, 1.25, hc, 0, 1.4, 0, cab); caixa(.55, .45, .55, hc, 0, 1.75, -.25, cab); }
  else if (d.estilo === "raspado") caixa(1.36, .16, 1.2, hc, 0, 1.36, 0, cab);
  else if (d.estilo === "grisalho") { caixa(.2, .5, 1, hc, -.66, 1.05, -.05, cab); caixa(.2, .5, 1, hc, .66, 1.05, -.05, cab); caixa(1.36, .14, .5, hc, 0, 1.38, -.35, cab); }
  else { caixa(1.42, .4, 1.27, hc, 0, 1.4, 0, cab); caixa(1.42, .5, .3, hc, 0, 1.1, -.5, cab); }
  // acessórios
  const preto = mat("#272b36");
  switch (d.acessorio) {
    case "prancheta": parte.acc = caixa(.08, 1.1, .8, mat("#c9a96a"), .05, -.9, .35, parte.bracoE); caixa(.03, .95, .65, mat("#f6f1e3"), .08, -.9, .37, parte.bracoE, false); break;
    case "bloco": parte.acc = caixa(.6, .8, .08, mat("#fbfaf4"), 0, -1.3, .32, parte.bracoE); break;
    case "oculos": caixa(.42, .3, .05, preto, -.3, .74, .62, cab, false); caixa(.42, .3, .05, preto, .3, .74, .62, cab, false); caixa(.2, .06, .05, preto, 0, .78, .62, cab, false); break;
    case "lapis": { const l = caixa(.1, .7, .1, mat("#f2c14e"), .72, 1.05, .1, cab, false); l.rotation.z = -.5; break; }
    case "fone": caixa(1.5, .12, .25, preto, 0, 1.55, 0, cab); caixa(.18, .5, .5, preto, -.72, .75, 0, cab); caixa(.18, .5, .5, preto, .72, .75, 0, cab); break;
    case "bone": caixa(1.4, .4, 1.25, mat("#2b3545"), 0, 1.45, 0, cab); caixa(1.0, .1, .6, mat("#222b38"), 0, 1.28, .85, cab); caixa(.18, .18, .6, mat("#8a929e"), 0, -1.4, .3, parte.bracoD); break;
    case "caixa": parte.acc = caixa(1.6, .95, .9, mat("#b8894f"), 0, 2.55, .75, g); break;
    case "lupa": { const t = new THREE.Mesh(new THREE.TorusGeometry(.35, .07, 6, 12), mat("#3a2a22")); t.position.set(0, -1.75, .2); parte.bracoD.add(t); break; }
    case "boina": { const b = new THREE.Mesh(new THREE.CylinderGeometry(.82, .82, .22, 10), mat("#7a2433", {})); b.position.set(-.08, 1.48, 0); b.rotation.z = .12; b.castShadow = true; cab.add(b); break; }
    case "megafone": { const mg = new THREE.Mesh(new THREE.ConeGeometry(.45, 1.1, 10, 1, true), mat("#f4efe4", { side: THREE.DoubleSide })); mg.rotation.z = Math.PI / 2; mg.position.set(.65, -1.4, .2); parte.bracoD.add(mg); break; }
  }
  // caneca do café (aparece só no café)
  parte.caneca = caixa(.32, .42, .32, mat("#f4f1ea"), 0, -1.75, .25, parte.bracoD, false); parte.caneca.visible = false;
  g.traverse(o => { if (o.isMesh) o.userData.corOriginal = o.material; });
  return { g, ...parte, congelado: false };
}
function congela(b, sim) {
  if (b.congelado === sim) return;
  b.congelado = sim;
  b.g.traverse(o => {
    if (!o.isMesh) return;
    if (sim) { if (!o.userData.corCinza) o.userData.corCinza = new THREE.MeshStandardMaterial({ color: cinza("#" + o.userData.corOriginal.color.getHexString()), roughness: .9, flatShading: true }); o.material = o.userData.corCinza; }
    else o.material = o.userData.corOriginal;
  });
}

// ------------------------------------------------------------ a cena
export class Cena3D {
  constructor(palco) {
    this.tipo = "3d";
    this.palco = palco;
    this.renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping; this.renderer.toneMappingExposure = 1.05;
    this.renderer.shadowMap.enabled = !matchMedia("(pointer: coarse)").matches;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.tela = this.renderer.domElement;
    this.tela.className = "cena-tela cena-3d";
    this.tela.setAttribute("aria-hidden", "true");
    palco.prepend(this.tela);
    this.scene = new THREE.Scene();
    this.camera = new THREE.OrthographicCamera(-1, 1, 1, -1, .1, 500);
    this.alvoCentro = new THREE.Vector3(0, 14.5, 0);
    this.camera.position.set(40, 44, 108);
    this.controles = new OrbitControls(this.camera, this.tela);
    Object.assign(this.controles, { enablePan: false, enableDamping: true, dampingFactor: .08, minZoom: .85, maxZoom: 3.2,
      minAzimuthAngle: -.6, maxAzimuthAngle: .6, minPolarAngle: .95, maxPolarAngle: 1.42, rotateSpeed: .6 });
    this.controles.target.copy(this.alvoCentro); this.controles.update();
    this.bonecos = {};
    this.v = new THREE.Vector3();
    this.monta();
    this.pronto = Promise.resolve();
  }

  medidas(m) {
    this.m = m;
    this.renderer.setPixelRatio(Math.min(m.dpr, 2));
    this.renderer.setSize(m.cssW, m.cssH, false);
    this.tela.style.width = m.cssW + "px"; this.tela.style.height = m.cssH + "px";
    const asp = m.cssW / m.cssH, alt = Math.max(40, 76 / asp);
    Object.assign(this.camera, { left: -alt * asp / 2, right: alt * asp / 2, top: alt / 2, bottom: -alt / 2 });
    this.camera.updateProjectionMatrix();
    const celular = m.modo !== "inteiro";
    this.controles.enabled = !celular;                 // no celular, deslizar troca de sala
    this.tela.style.touchAction = celular ? "pan-y" : "none";
    if (celular) { this.camera.zoom = 2.4; this.camera.updateProjectionMatrix(); }
  }
  mostra(sim) { this.tela.hidden = !sim; }

  segue(x, y) {
    if (!this.m || this.m.modo === "inteiro" || x == null) return;
    this.alvoSeguir = new THREE.Vector3(X(x), Yp(y) + 3.5, 0);
  }

  // ---------------------------------------------------------- montagem
  monta() {
    const s = this.scene;
    s.background = new THREE.Color("#0a0f2c");
    this.hemi = new THREE.HemisphereLight("#bfe1f8", "#4a4036", 1); s.add(this.hemi);
    this.amb = new THREE.AmbientLight("#c8d0e0", .7); s.add(this.amb);
    this.sol = new THREE.DirectionalLight("#fff1d6", 2);
    this.sol.position.set(-30, 60, 50); this.sol.castShadow = true;
    Object.assign(this.sol.shadow.camera, { left: -40, right: 40, top: 40, bottom: -10, near: 1, far: 200 });
    this.sol.shadow.mapSize.set(1024, 1024); this.sol.shadow.bias = -.0008;
    this.sol.target.position.set(0, 10, 0); s.add(this.sol, this.sol.target);

    // rua e calçada
    caixa(90, .4, 30, mat("#3a3c44"), 0, -.9, 14, s, false);
    caixa(70, .3, 4, mat("#a7a6a1"), 0, -.55, PROF / 2 + 2, s, false);
    for (let x = -40; x < 40; x += 4) caixa(2, .02, .2, mat("#cfc7a2"), x, -.69, 16, s, false);

    // salas
    this.luzes = {};
    for (const sl of SALAS) this.sala(sl);
    // laje entre andares e telhado
    caixa(64.4, 1.4, PROF, mat("#666b7e"), 0, ALT_SALA[0] + .7, 0, s);
    caixa(55.6, 1.2, .8, mat("#666b7e"), X(278), NIVEL[1] + ALT_SALA[1] + .6, -PROF / 2 - .1, s);   // platibanda (sem telhado: casa de bonecas)
    caixa(64.4, .6, PROF + .4, mat("#666b7e"), 0, -.3, 0, s);
    // paredes externas e divisórias
    const divisa = (x, y0, h) => caixa(.4, h, PROF, mat("#5d6275"), X(x), y0 + h / 2, 0, s);
    // divisórias tiradas da planta (paredes entre as salas de cada andar)
    for (const a of [0, 1]) {
      const xs = new Set([2, 638, 54]);
      for (const sl of SALAS.filter(s => s.andar === a)) { xs.add(sl.x0 - 2); xs.add(sl.x1 + 2); }
      for (const x of xs) divisa(x, NIVEL[a], ALT_SALA[a]);
    }
    // escada
    const escada = (a, b, n = 10) => {
      for (let i = 0; i < n; i++) {
        const t = (i + .5) / n, x = a.x + (b.x - a.x) * t, y = a.y + (b.y - a.y) * t;
        caixa(.6, .3, 3, mat("#8c8475"), X(x), Yp(y) - .15, ZP, s);
      }
    };
    escada(ESCADA.cima, ESCADA.meio); escada(ESCADA.meio, ESCADA.baixo);
    caixa(1.6, .3, 3, mat("#8c8475"), X(10), Yp(ESCADA.meio.y) - .15, ZP, s);
    caixa(2.4, .3, 3.2, mat("#8c8475"), X(40), NIVEL[1] - .15, ZP, s);
    caixa(2.2, 3.6, .2, mat("#6b4a2e"), X(18), 1.8, -PROF / 2 + .25, s);   // porta da rua

    for (const m of MOVEIS) this.movel(m);
    this.letreiro();
    this.andaimes();
  }

  sala(sl) {
    const s = this.scene, [corParede, piso] = COR_SALA[sl.id];
    const andares = sl.andar === -1 ? [0, 1] : [sl.andar];
    for (const a of andares) {
      const w = (sl.x1 - sl.x0) * U, cx = X((sl.x0 + sl.x1) / 2), y0 = NIVEL[a], h = ALT_SALA[a];
      const chao = new THREE.Mesh(new THREE.BoxGeometry(w, .3, PROF), new THREE.MeshStandardMaterial({ map: textura(piso, w / 3, PROF / 3), roughness: .9 }));
      chao.position.set(cx, y0 - .15, 0); chao.receiveShadow = true; s.add(chao);
      const paredeMat = corParede === "tijolo"
        ? new THREE.MeshStandardMaterial({ map: textura("tijolo", w / 3, h / 3), roughness: .95 })
        : sl.id === "cabine" ? new THREE.MeshStandardMaterial({ map: textura("espuma", w / 2, h / 2), roughness: .95 })
        : mat(corParede);
      const p = new THREE.Mesh(new THREE.BoxGeometry(w, h, .3), paredeMat);
      p.position.set(cx, y0 + h / 2, -PROF / 2); p.receiveShadow = true; s.add(p);
      if (corParede !== "tijolo" && sl.id !== "cabine") caixa(w, 2.6, .2, mat(sl.id === "cafe" ? "#e3c391" : sl.id === "portaria" ? "#aebcc2" : sl.id === "redacao" ? "#cfc0a0" : corParede), cx, y0 + 1.3, -PROF / 2 + .2, s, false);
      if (sl.ala) { const f = new THREE.Mesh(new THREE.BoxGeometry(w, .5, .32), new THREE.MeshBasicMaterial({ map: textura("faixa", w / 1.6, 1) })); f.position.set(cx, y0 + h - .6, -PROF / 2 + .1); s.add(f); }
      // luz da sala
      if (sl.id !== "escada") {
        const l = new THREE.PointLight(sl.id === "portaria" ? "#ffd89a" : "#fff0d8", 0, w * .8 + 4, 1.3);
        l.position.set(cx, y0 + h * .55, 1.5); s.add(l); this.luzes[sl.id] = l;
        caixa(1.6, .25, .9, mat("#2f3340"), cx, y0 + h - .4, 0, s, false);
      }
    }
    // placa com o nome, em fonte de pixel
    const nomes = { redacao: "REDAÇÃO", cabine: "CABINE", arquivo: "ARQUIVO", portaria: "PORTARIA", cafe: "CAFÉ", tecnica: "TÉCNICA", checagem: "CHECAGEM E\nCOMPLIANCE", obras: "ALA NOVA\nEM OBRAS" };
    if (nomes[sl.id]) {
      const op = sl.ala ? { fundo: "#f2c230", texto: "#1d1d1d" } : sl.id === "cabine" ? { fundo: "#132a2d", texto: "#cfe9e6" } : {};
      const { t, w, h } = texturaPlaca(nomes[sl.id], op), a = sl.andar;
      const pl = new THREE.Mesh(new THREE.PlaneGeometry(w * U, h * U), new THREE.MeshBasicMaterial({ map: t, transparent: true }));
      pl.position.set(X(sl.x0) + w * U / 2 + .8, NIVEL[a] + ALT_SALA[a] - (a === 0 ? 3.4 : 1.4) - h * U / 2, -PROF / 2 + .25); this.scene.add(pl);
    }
  }

  movel(mv) {
    const s = this.scene, sl = SALA[mv.sala], y0 = NIVEL[sl.andar], x = X(mv.x), w = (mv.w || 20) * U;
    const zFundo = -PROF / 2 + .4;
    switch (mv.tipo) {
      case "mesa": {
        const zm = ZP + 1.7;
        caixa(w, .25, 2.2, mat("#a87047"), x, y0 + 1.7, zm, s);
        caixa(w - .3, 1.45, .15, mat("#7a4d2d"), x, y0 + .85, zm + 1, s);
        for (const dx of [-w / 2 + .2, w / 2 - .2]) caixa(.2, 1.6, 2, mat("#5e3a21"), x + dx, y0 + .8, zm, s);
        if (mv.de && mv.sala !== "cabine") {
          const lado = mv.de === "roteirista" || mv.de === "produtor" ? 1 : -1;
          const mon = new THREE.Group(); mon.position.set(x + lado * (w / 2 - .9), y0 + 2.5, zm); mon.rotation.y = -lado * .55; s.add(mon);
          caixa(1.5, 1.05, .14, mat("#2a2f3a"), 0, 0, 0, mon);
          const tela = new THREE.Mesh(new THREE.PlaneGeometry(1.3, .85), new THREE.MeshStandardMaterial({ color: "#0d1a2a", emissive: "#7fc4ff", emissiveIntensity: 0 }));
          tela.position.z = -.08; tela.rotation.y = Math.PI; mon.add(tela);
          caixa(.15, .5, .15, mat("#1f232b"), 0, -.7, 0, mon);
          (this.telas ||= {})[mv.de] = tela.material;
          caixa(.9, 1.6, .9, mat("#363b4b"), x, y0 + 1.9, ZP - .9, s);            // encosto da cadeira
        }
        break;
      }
      case "quadro": {
        const q = new THREE.Mesh(new THREE.BoxGeometry(w, 4, .2), new THREE.MeshStandardMaterial({ map: textura("cortica", 2, 2) }));
        q.position.set(x, y0 + 8.6, zFundo); s.add(q);
        const notas = ["#ffe27a", "#9fd8ff", "#ffb3c7", "#b9f0a8", "#ffd08a", "#9fd8ff"];
        notas.forEach((c, i) => caixa(.7, .7, .05, mat(c), x - 1.4 + (i % 3) * 1.4, y0 + 9.4 - Math.floor(i / 3) * 1.4, zFundo + .14, s, false));
        break;
      }
      case "janela": {
        const h = sl.andar === 1 ? 4.4 : 3.6, yc = y0 + (sl.andar === 1 ? 8.6 : 9.2);
        caixa(w + .4, h + .4, .1, mat("#e9e4d8"), x, yc, zFundo - .02, s, false);
        const v = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: "#88b8e8" }));
        v.position.set(x, yc, zFundo + .05); s.add(v); (this.vidros ||= []).push(v.material);
        caixa(.15, h, .12, mat("#e9e4d8"), x, yc, zFundo + .08, s, false); caixa(w, .15, .12, mat("#e9e4d8"), x, yc, zFundo + .08, s, false);
        break;
      }
      case "mic": {
        caixa(.15, 2.2, .15, mat("#8a909c"), x, y0 + 2.9, ZP + 1.3, s);
        const braco = caixa(1.6, .12, .12, mat("#8a909c"), x + .7, y0 + 4, ZP + 1.1, s); braco.rotation.z = .2;
        caixa(.35, .6, .35, mat("#2b2f3a"), x + 1.4, y0 + 3.9, ZP + 1, s);
        break;
      }
      case "onair": {
        this.onairMat = new THREE.MeshStandardMaterial({ color: "#3a1e20", emissive: "#ff3b2b", emissiveIntensity: 0 });
        const { t, w: tw, h: th } = texturaPlaca("ON AIR", { fundo: "#e5392b", texto: "#fff4e8" });
        caixa(tw * U + .3, th * U + .3, .3, this.onairMat, X(412), y0 + ALT_SALA[1] - 1.8, zFundo, s, false);
        this.onairTxt = new THREE.MeshBasicMaterial({ map: t, transparent: true, opacity: .35 });
        const pl = new THREE.Mesh(new THREE.PlaneGeometry(tw * U, th * U), this.onairTxt);
        pl.position.set(X(412), y0 + ALT_SALA[1] - 1.8, zFundo + .17); s.add(pl);
        break;
      }
      case "estante": {
        caixa(w, 11.5, 2, mat("#6e5236"), x, y0 + 5.8, zFundo + 1, s);
        for (let i = 0; i < 4; i++) for (let k = 0; k < 6; k++) caixa(1.1 + (k % 2) * .3, 1.8 + ((k + i) % 3) * .3, 1.5, mat(["#b8894f", "#c29a62", "#a97c45"][(k + i) % 3]), x - w / 2 + 1 + k * 1.45, y0 + 1.2 + i * 2.9, zFundo + 1.4, s);
        break;
      }
      case "balcao": caixa(w, 2.2, 1.6, mat("#46525a"), x, y0 + 1.1, ZP + 1.8, s); caixa(w + .2, .2, 1.8, mat("#7d8b93"), x, y0 + 2.25, ZP + 1.8, s); break;
      case "crt": {
        caixa(3.2, .25, 2, mat("#7a5434"), x, y0 + 1.8, -1.6, s);
        caixa(2.8, 2.2, 2.2, mat("#cfc6ac"), x, y0 + 3.05, -1.6, s);
        this.crtMat = new THREE.MeshBasicMaterial({ map: texturaPlaca(">CC", { fundo: "#0b2414", texto: "#39ff6a" }).t });
        const t = new THREE.Mesh(new THREE.PlaneGeometry(2.1, 1.5), this.crtMat); t.position.set(x, y0 + 3.15, -1.6 + 1.11); s.add(t);
        const l = new THREE.PointLight("#39ff6a", 3, 8, 2); l.position.set(x, y0 + 3.2, 0); s.add(l);
        break;
      }
      case "bancada":
        caixa(w, 3.2, 2, mat("#8a6d52"), x, y0 + 1.6, zFundo + 1, s); caixa(w, .2, 2.2, mat("#5f4a38"), x, y0 + 3.3, zFundo + 1, s);
        caixa(1.8, 1.6, 1.4, mat("#b8bec8"), x - 1, y0 + 4.2, zFundo + 1, s); break;
      case "mesa-redonda": {
        const tp = new THREE.Mesh(new THREE.CylinderGeometry(w / 2, w / 2, .2, 14), mat("#5f4a38")); tp.position.set(x, y0 + 2.8, ZP - .6); tp.castShadow = tp.receiveShadow = true; s.add(tp);
        caixa(.35, 2.7, .35, mat("#3b3f4b"), x, y0 + 1.4, ZP - .6, s);
        break;
      }
      case "rack": {
        caixa(w, 8.4, 2.4, mat("#20252c"), x, y0 + 4.2, zFundo + 1.4, s);
        this.leds ||= [];
        for (let i = 0; i < 9; i++) {
          const m = new THREE.MeshBasicMaterial({ color: "#45ff7a" });
          const l = new THREE.Mesh(new THREE.BoxGeometry(.25, .12, .05), m); l.position.set(x + .6, y0 + .8 + i * .85, zFundo + 2.62); s.add(l); this.leds.push(m);
        }
        break;
      }
      case "vidro": {
        const v = new THREE.Mesh(new THREE.BoxGeometry(w, 12, 5), new THREE.MeshStandardMaterial({ color: "#aadef0", transparent: true, opacity: .18, roughness: .1 }));
        v.position.set(x, y0 + 6, -1.5); s.add(v);
        for (const dx of [-w / 2, 0, w / 2]) caixa(.2, 12, .2, mat("#a9bcc8"), x + dx, y0 + 6, 1, s);
        break;
      }
    }
  }

  letreiro() {
    const { t } = texturaPlaca(">CC", { fundo: "#11161a", texto: "#39ff6a" });
    this.neon = new THREE.MeshBasicMaterial({ map: t });
    const p = new THREE.Mesh(new THREE.PlaneGeometry(5.4, 2.2), this.neon); p.position.set(X(271), NIVEL[1] + ALT_SALA[1] + 2.2, -PROF / 2 + .5); this.scene.add(p);
  }
  andaimes() {
    for (const x of [554, 595, 634]) for (const z of [PROF / 2 - .2]) caixa(.2, 32, .2, mat("#8d97a3"), X(x), 16, z, this.scene);
    for (const y of [ALT_SALA[0] + 1.4, NIVEL[1] + ALT_SALA[1] + .4]) caixa(8.2, .25, .9, mat("#c9a96a"), X(596), y, PROF / 2 - .2, this.scene);
  }

  // ---------------------------------------------------------- posição de quem está na cena
  // Dada a posição 2D (x, y), devolve o ponto 3D dos pés. Quem está 6 px acima
  // da linha do andar (o fundo do café) fica mais para trás, no mesmo piso.
  pes(x, y) {
    for (const a of [0, 1]) {
      const pe = a ? PE1 : PE0;
      if (y <= pe + .5 && y >= pe - 8) return this.v.set(X(x), NIVEL[a], ZP + (ZF - ZP) * ((pe - y) / 6));
    }
    return this.v.set(X(x), Yp(y), ZP);
  }

  projeta(x, y, alt = 0) {
    const p = this.pes(x, y).clone(); p.y += alt * U;
    p.project(this.camera);
    return { x: (p.x + 1) / 2 * this.m.cssW, y: (1 - p.y) / 2 * this.m.cssH };
  }
  escala() { return 1; }
  retSala(id) {
    const sl = SALA[id], a = sl.andar === -1 ? 0 : sl.andar, y0 = NIVEL[a], h = ALT_SALA[a];
    let x0 = Infinity, y0s = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (const xx of [X(sl.x0), X(sl.x1)]) for (const yy of [y0, y0 + h]) for (const zz of [-PROF / 2, PROF / 2]) {
      const p = new THREE.Vector3(xx, yy, zz).project(this.camera);
      const sx = (p.x + 1) / 2 * this.m.cssW, sy = (1 - p.y) / 2 * this.m.cssH;
      x0 = Math.min(x0, sx); x1 = Math.max(x1, sx); y0s = Math.min(y0s, sy); y1 = Math.max(y1, sy);
    }
    return { x: x0, y: y0s, w: x1 - x0, h: y1 - y0s };
  }

  // ---------------------------------------------------------- quadro
  desenha(e) {
    const { q, pessoas, t } = e, c = q.ceu;
    // céu e luz do dia
    const alto = new THREE.Color(`rgb(${c.alto.join(",")})`), hor = new THREE.Color(`rgb(${c.horizonte.join(",")})`);
    this.scene.background = alto;
    this.hemi.color.copy(hor).lerp(new THREE.Color("#ffffff"), .3);
    const escuro = Object.values(q.luz).filter(v => v === "apagada").length > 3;
    this.hemi.intensity = (escuro ? .12 : .4) + c.dia * 1.05;
    this.amb.intensity = (escuro ? .1 : .5) + c.dia * .4;
    this.sol.intensity = c.dia * 2.4;
    this.sol.color.copy(hor).lerp(new THREE.Color("#fff6e0"), .6);
    if (c.sol != null) this.sol.position.set(-60 + c.sol * 120, 20 + Math.sin(c.sol * Math.PI) * 60, 50);
    for (const v of this.vidros || []) v.color.copy(hor).lerp(alto, .4);
    // luzes das salas
    for (const [id, l] of Object.entries(this.luzes)) {
      const modo = q.luz[id];
      l.intensity = modo === "acesa" ? (id === "portaria" && c.dia < .3 ? 45 : 80) : modo === "obra" ? 14 : modo === "penumbra" ? 6 : 0;
    }
    // ON AIR, telas, LEDs, letreiro
    this.onairMat.emissiveIntensity = q.onair ? 2.2 : 0; this.onairTxt.opacity = q.onair ? 1 : .35;
    for (const [id, m] of Object.entries(this.telas || {})) { const p = q.pessoas[id]; m.emissiveIntensity = p && p.estado === "trabalhando" ? 1.6 : p && q.luz[p.sala] === "acesa" ? .4 : 0; }
    const tec = pessoas.some(p => p.id === "produtor" && p.info && p.info.estado === "trabalhando");
    (this.leds || []).forEach((m, i) => m.color.set(e.semMovimento || Math.sin(t / (tec ? 90 : 400) + i * 1.7) > -.2 ? (i % 5 ? "#45ff7a" : "#ffb347") : "#1d4a2a"));
    // pessoas
    const vivos = new Set();
    for (const p of pessoas) {
      vivos.add(p.id);
      let b = this.bonecos[p.id];
      if (!b) { b = this.bonecos[p.id] = boneco(p.id); this.scene.add(b.g); }
      const inf = p.info || {}, est = p.andando ? "andando" : inf.estado || "parado";
      congela(b, est === "congelado");
      b.g.visible = (p.opacidade ?? 1) > .3;
      b.g.position.copy(this.pes(p.x, p.y));
      const ry = p.andando ? (p.dir < 0 ? -Math.PI / 2 : Math.PI / 2) : 0;
      b.g.rotation.y += (ry - b.g.rotation.y) * Math.min(1, (e.dt || 16) / 120);
      const k = e.semMovimento ? 0 : 1, f = t / 1000;
      let pe = 0, be = 0, bd = 0, cab = 0;
      if (est === "andando") { pe = Math.sin(f * 9) * .7 * k; be = -pe; bd = pe; }
      else if (est === "trabalhando") { be = -1.1 + Math.sin(f * 11) * .2 * k; bd = -1.1 - Math.sin(f * 11) * .2 * k; cab = Math.sin(f * 3) * .05 * k; }
      else if (est === "cafe") { bd = -1.5 - (Math.floor(f * 1.1 + p.id.length) % 6 === 5 ? .9 : 0); }
      if (inf.fala && !p.andando) cab += Math.sin(f * 14) * .06 * k;
      if (b.acc && PERSONAS[p.id].acessorio === "caixa") b.acc.position.y = 2.55 + (est === "trabalhando" ? Math.abs(Math.sin(f * 3)) * .3 * k : 0);
      b.pernaE.rotation.x = pe; b.pernaD.rotation.x = -pe; b.bracoE.rotation.x = be; b.bracoD.rotation.x = bd; b.cabeca.rotation.x = cab;
      b.caneca.visible = est === "cafe";
    }
    for (const [id, b] of Object.entries(this.bonecos)) if (!vivos.has(id)) b.g.visible = false;

    // câmera: no celular segue a sala ativa
    if (this.m.modo !== "inteiro" && this.alvoSeguir) {
      this.controles.target.lerp(this.alvoSeguir, e.semMovimento ? 1 : .08);
      this.camera.position.set(this.controles.target.x + 30, this.controles.target.y + 34, 100);
      this.camera.lookAt(this.controles.target);
    } else this.controles.update();
    this.renderer.render(this.scene, this.camera);
  }

  desmonta() { this.renderer.dispose(); this.tela.remove(); }
}
