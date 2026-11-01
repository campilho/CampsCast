// Camada visual 2D: o estúdio em corte, como casa de bonecas, em pixel art.
// Resolução interna fixa de 640 × 360, ampliada em múltiplos inteiros de pixel
// do aparelho. Lê o quadro do motor e as posições da locomoção; não decide
// nada sobre quem está onde. Paleta limitada, contorno escuro e uma cor
// dominante por sala; luz pela hora (cones pontilhados, sol no chão, noite azul).

import { W, H, ANDARES, SALAS, SALA, retSala, ESCADA } from "./planta.js";
import { sprite, quadroNoTempo, SW, SH, PE } from "./sprites.js";
import { escreve, placa, medeTexto, ALTURA } from "./pixelfont.js";

const A1 = ANDARES[1], A0 = ANDARES[0];
const novoCanvas = (w, h) => Object.assign(document.createElement("canvas"), { width: w, height: h });
const rgb = a => `rgb(${a[0]},${a[1]},${a[2]})`;
function R(c, x, y, w, h, cor) { c.fillStyle = cor; c.fillRect(x, y, w, h); }
function caixa(c, x, y, w, h, cor, borda = "#1c1a26") { R(c, x, y, w, h, borda); R(c, x + 1, y + 1, w - 2, h - 2, cor); }

// Paleta (limitada) ------------------------------------------------------------
const P = {
  tinta: "#1c1a26", estrutura: "#363a48", laje: "#515565", lajeC: "#6b6f80", lajeE: "#2b2d38",
  madeira: "#a87047", madeiraC: "#c08458", madeiraE: "#7a4d2d", madeiraEE: "#5e3a21",
  creme: "#e8dfcc", cremeE: "#cdbd9b", ocre: "#d8962c",
  teal: "#2c585d", tealE: "#23484c", tealC: "#3a6c71",
  kraft: "#b8894f", kraftC: "#c9a06a", kraftE: "#8a6334", papel: "#f3ead7",
  tijolo: "#a45e43", tijoloE: "#94513a", argamassa: "#b98a72", obra: "#f2c230",
  cinzaAzul: "#cfd8dc", cinzaAzulE: "#aebcc2", aco: "#b6c0c9", acoE: "#8d97a3", acoEE: "#5a6370",
  laranja: "#f0dbb6", laranjaE: "#e3c391", cafe: "#6b4426",
  vidro: "#9fc7d6", folha: "#4ea35a", folhaE: "#3f8a4b", vaso: "#b0613a",
  branco: "#f4f1ea", preto: "#20252c", tela: "#2a2f3a",
};
const MESES = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"];

// Mesas com monitor (para o brilho) e luminárias (para os cones) --------------------
const MESAS = [
  { de: "jornalista", x: 110, w: 52, a: A1, monitor: [-1], abajur: 1 },
  { de: "editor",     x: 196, w: 52, a: A1, monitor: [-1], abajur: 1 },
  { de: "roteirista", x: 282, w: 52, a: A1, monitor: [1], abajur: -1 },
  { de: "produtor",   x: 446, w: 56, a: A0, monitor: [-1, 1], abajur: 0 },
];
const LUMINARIAS = {           // luminárias de teto: x e largura do cone no chão
  redacao: [[110, 46], [196, 46], [282, 46]], cabine: [[392, 54]], arquivo: [[500, 60]], portaria: [[108, 50]],
  cafe: [[234, 54], [300, 54], [366, 44]], tecnica: [[446, 56], [524, 40]], checagem: [], obras: [],
};
const JANELAS = [];

// ------------------------------------------------------------ prédio (fundo e frente)
function montaPredio(cfg) {
  JANELAS.length = 0;
  const fundo = novoCanvas(W, H), frente = novoCanvas(W, H);
  const f = fundo.getContext("2d"), g = frente.getContext("2d");

  R(f, 0, 16, 640, 320, P.estrutura);
  // telhado: platibanda, caixa d'água, antena, letreiro
  R(f, 0, 16, 556, 8, P.laje); R(f, 0, 16, 556, 1, P.lajeC); R(f, 0, 23, 556, 1, P.lajeE);
  caixa(f, 118, 3, 28, 13, "#6c7384"); R(f, 119, 4, 26, 2, "#8a91a2"); R(f, 124, 0, 16, 3, "#5a6070");
  R(f, 492, 5, 2, 11, "#5a6070"); R(f, 482, 1, 22, 3, "#7d8495"); R(f, 486, 0, 14, 1, "#9aa1b2"); R(f, 500, 3, 8, 1, "#5a6070");
  R(f, 250, 13, 2, 3, P.lajeE); R(f, 290, 13, 2, 3, P.lajeE); caixa(f, 244, 1, 54, 13, "#0d1215");
  // lajes e base
  R(f, 0, 172, 640, 8, P.laje); R(f, 0, 172, 640, 1, P.lajeC); R(f, 0, 179, 640, 1, P.lajeE);
  R(f, 0, 328, 640, 6, P.laje); R(f, 0, 328, 640, 1, P.lajeC);
  // calçada e rua
  R(f, 0, 334, 640, 10, "#a7a6a1"); for (let x = 0; x < 640; x += 18) R(f, x, 334, 1, 10, "#8f8e89");
  R(f, 0, 344, 640, 2, "#7b7a76"); R(f, 0, 346, 640, 14, "#3a3c44");
  for (let x = 6; x < 640; x += 28) R(f, x, 353, 14, 1, "#cfc7a2");
  R(f, 176, 328, 6, 7, "#c0392b"); R(f, 175, 330, 8, 2, "#a5281c");
  R(f, 430, 331, 22, 2, "#7a5434"); R(f, 432, 333, 2, 3, "#3a3a3a"); R(f, 448, 333, 2, 3, "#3a3a3a");

  for (const s of SALAS) sala(f, g, s, cfg);
  andaimes(f, g);
  return { fundo, frente };
}

function piso(f, x0, x1, a, padrao) {
  const y0 = a.chao, y1 = a.base;
  if (padrao === "madeira") {
    for (let y = y0; y < y1; y += 2) R(f, x0, y, x1 - x0, 2, (y - y0) % 4 ? "#9a6b43" : "#a8794d");
    for (let y = y0; y < y1; y += 4) for (let x = x0 + ((y / 4) % 2) * 9; x < x1; x += 18) R(f, x, y, 1, 2, "#7f5534");
  } else if (padrao === "xadrez" || padrao === "ladrilho") {
    const [c1, c2] = padrao === "xadrez" ? ["#cdb999", "#b4a080"] : ["#9ca7ae", "#8c979e"];
    for (let y = y0; y < y1; y += 4) for (let x = x0; x < x1; x += 4) R(f, x, y, 4, 4, ((x - x0) / 4 + (y - y0) / 4) % 2 ? c1 : c2);
  } else if (padrao === "carpete") {
    R(f, x0, y0, x1 - x0, y1 - y0, "#3a3f51");
    for (let y = y0; y < y1; y += 2) for (let x = x0 + (y % 4); x < x1; x += 6) R(f, x, y, 1, 1, "#444a5e");
  } else if (padrao === "tecnico") {
    R(f, x0, y0, x1 - x0, y1 - y0, "#7e8792");
    for (let x = x0; x < x1; x += 8) R(f, x, y0, 1, y1 - y0, "#6b7480");
    R(f, x0, y0 + 8, x1 - x0, 1, "#6b7480");
  } else if (padrao === "cimento") {
    R(f, x0, y0, x1 - x0, y1 - y0, "#9b9a93");
    for (let i = 0; i < 30; i++) R(f, x0 + (i * 37) % (x1 - x0), y0 + (i * 13) % (y1 - y0), 1, 1, i % 2 ? "#8a8982" : "#aeada6");
  } else {
    R(f, x0, y0, x1 - x0, y1 - y0, "#8e887b");
    for (let x = x0; x < x1; x += 10) R(f, x, y0, 1, y1 - y0, "#7d776b");
  }
  R(f, x0, y0, x1 - x0, 1, "rgba(0,0,0,.28)");
  R(f, x0, y1 - 1, x1 - x0, 1, "rgba(0,0,0,.35)");
}

function parede(f, x0, x1, a, cor, rodape, lambri) {
  R(f, x0, a.teto, x1 - x0, a.chao - a.teto, cor);
  R(f, x0, a.teto, x1 - x0, 3, "rgba(0,0,0,.22)");
  if (lambri) { R(f, x0, a.chao - 30, x1 - x0, 30, lambri); R(f, x0, a.chao - 31, x1 - x0, 1, "rgba(0,0,0,.18)"); R(f, x0, a.chao - 32, x1 - x0, 1, "rgba(255,255,255,.2)"); }
  R(f, x0, a.chao - 3, x1 - x0, 3, rodape);
}

function janela(f, sala, cx, w, y0, h) {
  const x0 = Math.round(cx - w / 2);
  JANELAS.push({ sala, x: x0, y: y0, w, h });
  R(f, x0 - 3, y0 - 3, w + 6, h + 6, P.tinta); R(f, x0 - 2, y0 - 2, w + 4, h + 4, "#e9e4d8");
  R(f, x0 - 4, y0 + h + 2, w + 8, 3, "#b9b2a2"); R(f, x0 - 4, y0 + h + 2, w + 8, 1, "#d8d1c2");
  f.clearRect(x0, y0, w, h);
  R(f, x0 + Math.floor(w / 2) - 1, y0, 2, h, "#e9e4d8"); R(f, x0, y0 + Math.floor(h / 2), w, 2, "#e9e4d8");
}
function porta(f, x, a) { R(f, x, a.chao - 50, 4, 50, "#22242e"); }
function luminariaTeto(f, x, a) {
  R(f, x, a.teto, 1, 7, "#3a3a44"); caixa(f, x - 5, a.teto + 7, 11, 4, "#2f3340"); R(f, x - 3, a.teto + 11, 7, 1, "#f6e7b0");
}
function planta(f, x, y, alta = false) {
  caixa(f, x, y - 9, 10, 9, P.vaso); R(f, x + 1, y - 8, 8, 1, "#c8774a");
  const h = alta ? 26 : 14;
  R(f, x + 4, y - 9 - h, 2, h, P.folhaE);
  for (let i = 0; i < (alta ? 6 : 3); i++) { const yy = y - 12 - i * 4; R(f, x + (i % 2 ? 6 : 0), yy, 4, 3, i % 2 ? P.folha : P.folhaE); R(f, x + (i % 2 ? 7 : 1), yy, 2, 1, "#6cc077"); }
}
function caneca(c, x, y, cor = P.branco) { R(c, x, y, 4, 4, P.tinta); R(c, x + 1, y + 1, 2, 3, cor); R(c, x + 4, y + 1, 1, 2, P.tinta); }

function mesa(g, m, cfg) {
  const { x, w, a } = m, x0 = Math.round(x - w / 2), top = a.pe - 20;
  R(g, x0 - 1, top - 1, w + 2, 5, P.tinta);
  R(g, x0, top, w, 3, P.madeira); R(g, x0, top, w, 1, P.madeiraC);
  R(g, x0 + 2, top + 3, w - 4, 18, P.madeiraE); R(g, x0 + 1, top + 3, 1, 18, P.tinta); R(g, x0 + w - 2, top + 3, 1, 18, P.tinta);
  R(g, x0 + 2, top + 3, w - 4, 1, P.madeiraEE); R(g, x0 + 5, top + 9, 12, 1, P.madeiraEE); R(g, x0 + w - 17, top + 9, 12, 1, P.madeiraEE);
  R(g, x0 + 10, top + 7, 2, 1, "#c9a96a"); R(g, x0 + w - 12, top + 7, 2, 1, "#c9a96a");
  // teclado
  R(g, x - 8, top - 2, 16, 2, P.tinta); R(g, x - 7, top - 2, 14, 1, "#8a909c");
  // monitores (de costas, com pé)
  for (const lado of m.monitor || []) {
    const mx = lado < 0 ? x0 + 2 : x0 + w - 18;
    caixa(g, mx, top - 14, 16, 12, P.tela); R(g, mx + 2, top - 12, 12, 1, "#3c4352");
    R(g, mx + 7, top - 2, 2, 2, P.tela); R(g, mx + 4, top - 1, 8, 1, "#1f232b");
  }
  // luminária de mesa
  if (m.abajur) {
    const lx = m.abajur > 0 ? x0 + w - 8 : x0 + 6;
    R(g, lx - 2, top - 1, 6, 1, P.tinta); R(g, lx, top - 10, 1, 9, "#3a3a44"); R(g, lx, top - 10, 5 * m.abajur, 1, "#3a3a44");
    caixa(g, lx + 3 * m.abajur - 3, top - 13, 7, 4, "#2f6b5a"); R(g, lx + 3 * m.abajur - 2, top - 10, 5, 1, "#f6e7b0");
  }
  // objetos de cada um
  if (m.de === "jornalista") { R(g, x + 9, top - 2, 7, 2, P.tinta); R(g, x + 10, top - 2, 5, 1, "#fbfaf4"); caneca(g, x - 16, top - 4, "#2f86d0"); }
  if (m.de === "editor") { R(g, x + 8, top - 3, 9, 3, P.tinta); R(g, x + 9, top - 3, 7, 1, "#fbfaf4"); R(g, x + 9, top - 2, 7, 1, "#e6e2d6"); caneca(g, x - 15, top - 4, "#7a5fd0"); }
  if (m.de === "roteirista") { R(g, x - 16, top - 2, 9, 2, P.tinta); R(g, x - 15, top - 2, 7, 1, "#fbfaf4"); caneca(g, x + 2, top - 4, "#d04a78"); }
  if (m.de === "produtor") { R(g, x - 4, top - 3, 8, 3, P.tinta); R(g, x - 3, top - 3, 6, 1, "#c9a96a"); }
}
function cadeira(f, cx, pe) {
  caixa(f, cx - 8, pe - 38, 16, 18, "#363b4b"); R(f, cx - 6, pe - 37, 12, 1, "#4a5064"); R(f, cx - 1, pe - 20, 2, 6, "#262a35");
}

function sala(f, g, s, cfg) {
  const r = retSala(s.id), a = s.andar === -1 ? null : ANDARES[s.andar];
  const x0 = r.x, x1 = r.x + r.w;
  switch (s.id) {
    case "escada": {
      R(f, x0, r.y, r.w, r.h, "#bdb6a9"); R(f, x0, r.y, r.w, 3, "rgba(0,0,0,.2)");
      for (let y = r.y + 12; y < r.y + r.h; y += 24) R(f, x0, y, r.w, 1, "#aca596");
      R(f, 28, 166, 24, 6, "#8c8475"); R(f, 28, 166, 24, 1, "#a39b8b");
      R(f, 4, 312, 48, 16, "#8c8475"); R(f, 4, 312, 48, 1, "#a39b8b");
      const lance = (p, q) => {
        for (let i = 0; i <= 48; i++) { const t = i / 48; R(f, Math.round(p.x + (q.x - p.x) * t) - 4, Math.round(p.y + (q.y - p.y) * t) + 1, 9, 6, "#7d7566"); }
        for (let i = 0; i < 10; i++) { const t = (i + .5) / 10; R(f, Math.round(p.x + (q.x - p.x) * t) - 5, Math.round(p.y + (q.y - p.y) * t), 11, 2, "#a8a090"); }
      };
      lance(ESCADA.cima, ESCADA.meio); lance(ESCADA.meio, ESCADA.baixo);
      R(f, 4, 244, 14, 4, "#8c8475"); R(f, 4, 244, 14, 1, "#a39b8b");
      for (const [p, q] of [[ESCADA.cima, ESCADA.meio], [ESCADA.meio, ESCADA.baixo]]) for (let i = 0; i <= 30; i++) { const t = i / 30; R(g, Math.round(p.x + (q.x - p.x) * t), Math.round(p.y - 14 + (q.y - p.y) * t), 1, 1, "#5b4636"); }
      // porta da rua, extintor e luz do corredor
      caixa(f, 8, 274, 20, 38, "#6b4a2e"); R(f, 11, 278, 14, 14, P.vidro); R(f, 11, 278, 14, 1, "#cfe6ee"); R(f, 23, 296, 2, 2, "#e0c070"); R(f, 6, 272, 24, 2, "#4a3322");
      caixa(f, 40, 292, 5, 10, "#c0392b"); R(f, 41, 290, 3, 2, P.tinta);
      for (const y of [40, 196]) { caixa(f, 22, y, 9, 5, "#2f3340"); R(f, 23, y + 5, 7, 1, "#f6e7b0"); }
      porta(f, 52, A1); porta(f, 52, A0);
      break;
    }
    case "redacao": {
      parede(f, x0, x1, a, P.creme, "#8f7b5e", P.cremeE);
      piso(f, x0, x1, a, "madeira");
      for (let x = x0 + 16; x < x1 - 40; x += 1) if ((x - x0) % 2 === 0) R(f, x, a.chao + 3, 1, 1, "rgba(122,95,208,.0)");
      janela(f, "redacao", 82, 34, a.teto + 20, 44);
      janela(f, "redacao", 238, 34, a.teto + 20, 44);
      // quadro de cortiça com as pautas do dia
      const qx = 130, qy = a.teto + 20, qw = 56, qh = 42;
      caixa(f, qx, qy, qw, qh, "#6b4a2e"); R(f, qx + 2, qy + 2, qw - 4, qh - 4, "#c39462");
      for (let i = 0; i < 24; i++) R(f, qx + 3 + (i * 7) % (qw - 6), qy + 3 + (i * 5) % (qh - 6), 1, 1, "#a87a4c");
      const cores = ["#ffe27a", "#9fd8ff", "#ffb3c7", "#b9f0a8"];
      const pautas = (cfg.pautas || []).slice(0, 4), cw = 14, tot = pautas.length * cw + Math.max(0, pautas.length - 1) * 4;
      pautas.forEach((p, i) => {
        const cx = Math.round(qx + (qw - tot) / 2 + i * (cw + 4)), cy = qy + 9 + (i % 2) * 3;
        caixa(f, cx, cy, cw, 22, p.do_backlog ? "#ffd08a" : cores[i % cores.length]);
        for (let l = 0; l < 4; l++) R(f, cx + 2, cy + 6 + l * 3, cw - 4 - (l === 3 ? 4 : 0), 1, "rgba(28,26,38,.35)");
        R(f, cx + 6, cy + 1, 2, 2, "#c0392b");
      });
      placa(f, "PAUTAS", qx + qw / 2, qy - 2, { fundo: "#3a2f2a", texto: "#f4efe4", pad: 2 });
      // estante de livros com planta em cima
      caixa(f, 296, a.teto + 30, 32, a.chao - a.teto - 30, "#6e5236");
      for (let i = 0; i < 4; i++) {
        const y = a.teto + 33 + i * 23; R(f, 297, y + 20, 30, 2, "#4e3a26");
        for (let x = 298; x < 326; x += 3) R(f, x, y + 4 + (x % 3), 2, 16 - (x % 3), ["#c0392b", "#2f86d0", "#e9c46a", "#3a7d5c", "#7a5fd0", "#d8962c"][(x + i) % 6]);
      }
      planta(f, 306, a.teto + 30);
      // relógio de parede e planta no chão
      caixa(f, 190, a.teto + 6, 13, 13, "#f7f3e8", "#3a3a44");
      planta(f, 60, a.chao + 6, true);
      for (const [x] of LUMINARIAS.redacao) luminariaTeto(f, x, a);
      for (const x of [110, 196, 282]) cadeira(f, x, a.pe);
      for (const m of MESAS.filter(m => m.a === A1)) mesa(g, m, cfg);
      break;
    }
    case "cabine": {
      R(f, x0, a.teto, r.w, a.chao - a.teto, P.teal);
      for (let y = a.teto + 4; y < a.chao - 4; y += 6) for (let x = x0 + ((y / 6) % 2) * 3; x < x1; x += 6) { R(f, x, y, 3, 3, P.tealE); R(f, x, y, 3, 1, P.tealC); }
      R(f, x0, a.teto, r.w, 3, "rgba(0,0,0,.3)"); R(f, x0, a.chao - 3, r.w, 3, "#1b2d30");
      piso(f, x0, x1, a, "carpete");
      // vidro para a redação
      caixa(f, x0 + 2, a.teto + 40, 15, 42, "#1d3a3e"); R(f, x0 + 3, a.teto + 41, 13, 40, "rgba(160,215,230,.35)"); R(f, x0 + 5, a.teto + 44, 1, 14, "rgba(255,255,255,.5)");
      // caixa do ON AIR e caixas de som
      caixa(f, 391, a.teto + 7, 42, 13, "#1a1416");
      for (const x of [346, 432]) { caixa(f, x, a.teto + 54, 9, 14, "#20252c"); R(f, x + 3, a.teto + 57, 3, 3, "#4a5160"); R(f, x + 3, a.teto + 62, 3, 3, "#4a5160"); }
      // fone pendurado
      R(f, 352, a.teto + 30, 6, 1, "#3a3a44"); R(f, 352, a.teto + 31, 1, 6, "#272b36"); R(f, 357, a.teto + 31, 1, 6, "#272b36"); R(f, 351, a.teto + 36, 3, 4, "#272b36"); R(f, 356, a.teto + 36, 3, 4, "#272b36");
      for (const [x] of LUMINARIAS.cabine) luminariaTeto(f, x, a);
      cadeira(f, 400, a.pe);
      mesa(g, { x: 400, w: 64, a }, cfg);
      // mesa de som (os LEDs acendem na camada dinâmica)
      caixa(g, 372, a.pe - 25, 26, 6, "#2a2f3a"); for (let x = 374; x < 396; x += 3) { R(g, x, a.pe - 24, 1, 2, "#8a909c"); R(g, x + 1, a.pe - 22, 1, 1, "#e9c46a"); }
      // microfone de braço com pop filter
      R(g, 368, a.pe - 26, 4, 6, "#4a4f5c");
      for (let i = 0; i < 12; i++) R(g, 370 + i, a.pe - 27 - Math.round(i * 1.1), 1, 1, "#8a909c");
      for (let i = 0; i < 6; i++) R(g, 382 + i, a.pe - 40 + Math.round(i * .3), 1, 1, "#8a909c");
      caixa(g, 386, a.pe - 44, 6, 10, "#2b2f3a"); R(g, 387, a.pe - 43, 4, 8, "#4a5160");
      R(g, 383, a.pe - 46, 1, 12, "rgba(30,30,40,.6)"); R(g, 382, a.pe - 45, 1, 10, "rgba(30,30,40,.4)");
      break;
    }
    case "arquivo": {
      parede(f, x0, x1, a, "#d9cfb8", "#8a7d62", null);
      piso(f, x0, x1, a, "pedra");
      caixa(f, 456, a.teto + 10, 92, a.chao - a.teto - 10, "#6e5236");
      const meses = cfg.meses || ["SET", "OUT", "NOV"];
      for (let i = 0; i < 4; i++) {
        const y = a.teto + 12 + i * 30;
        R(f, 458, y, 88, 27, "#5a4229"); R(f, 456, y + 27, 92, 3, "#7d6040");
        for (let x = 460, k = 0; x < 542; k++) {
          const w = 11 + ((k * 7 + i * 3) % 5), h = 19 + ((k + i) % 3) * 2;
          caixa(f, x, y + 27 - h, w, h, [P.kraft, P.kraftC, "#a97c45"][(k + i) % 3]);
          R(f, x + 2, y + 27 - h + 4, w - 4, 5, P.papel); R(f, x + 3, y + 27 - h + 6, w - 6, 1, "#9c8f7a");
          x += w + 1;
        }
        const mes = meses[Math.min(i, meses.length - 1)];
        if (i < 3) placa(f, mes, 470, y + 21, { fundo: "#1d1b26", texto: "#f3ead7", pad: 1 });
      }
      // escada de biblioteca no trilho e carrinho
      R(f, 456, a.teto + 9, 92, 1, "#3a3a44");
      for (let y = a.teto + 40; y < a.chao; y += 8) R(f, 488, y, 11, 1, "#9c7a52");
      R(f, 488, a.teto + 10, 1, a.chao - a.teto - 10, "#9c7a52"); R(f, 498, a.teto + 10, 1, a.chao - a.teto - 10, "#9c7a52");
      caixa(g, 524, a.pe - 16, 24, 12, "#5a6370"); R(g, 525, a.pe - 15, 22, 1, "#8d97a3"); caixa(g, 526, a.pe - 25, 10, 10, P.kraft); caixa(g, 536, a.pe - 22, 10, 7, P.kraftC);
      R(g, 526, a.pe - 4, 4, 4, P.tinta); R(g, 542, a.pe - 4, 4, 4, P.tinta); R(g, 546, a.pe - 26, 1, 12, "#8d97a3");
      for (const [x] of LUMINARIAS.arquivo) luminariaTeto(f, x, a);
      porta(f, 444, a);
      break;
    }
    case "checagem": {
      tijolos(f, x0, a.teto, r.w, a.chao - a.teto);
      piso(f, x0, x1, a, "cimento");
      const gx = 566, gy = a.teto + 30, gw = 64, gh = a.chao - gy;
      R(f, gx, gy, gw, gh, "rgba(170,222,240,.22)");
      R(f, gx, gy, gw, 2, "#a9bcc8"); for (const x of [gx, gx + 31, gx + gw - 2]) R(f, x, gy, 2, gh, "#a9bcc8");
      R(f, gx + 6, gy + 8, 1, 14, "rgba(255,255,255,.55)"); R(f, gx + 9, gy + 6, 1, 8, "rgba(255,255,255,.4)");
      for (let i = 0; i < 28; i++) { R(f, gx + 33 + i, gy + 10 + i * 2, 1, 2, i % 6 < 3 ? P.obra : "#1d1d1d"); R(f, gx + 61 - i, gy + 10 + i * 2, 1, 2, i % 6 < 3 ? P.obra : "#1d1d1d"); }
      faixaObra(f, x0, a.teto, r.w);
      R(g, 558, a.pe - 8, 8, 9, "#e86a2a"); R(g, 560, a.pe - 13, 4, 5, "#e86a2a"); R(g, 559, a.pe - 10, 6, 2, P.branco);
      break;
    }
    case "portaria": {
      parede(f, x0, x1, a, P.cinzaAzul, "#5f6d75", P.cinzaAzulE);
      piso(f, x0, x1, a, "ladrilho");
      janela(f, "portaria", 134, 26, a.teto + 22, 34);
      // quadro de chaves e relógio de parede
      caixa(f, 62, a.teto + 22, 20, 16, "#6b4a2e"); for (let i = 0; i < 6; i++) { R(f, 65 + (i % 3) * 5, a.teto + 25 + Math.floor(i / 3) * 6, 1, 2, "#c9c9c9"); R(f, 65 + (i % 3) * 5, a.teto + 27 + Math.floor(i / 3) * 6, 2, 2, "#e0c070"); }
      caixa(f, 95, a.teto + 20, 13, 13, "#f7f3e8", "#3a3a44");
      // mesinha com o monitor CRT
      R(f, 64, a.pe - 18, 34, 3, "#7a5434"); R(f, 66, a.pe - 15, 2, 17, "#4e3522"); R(f, 94, a.pe - 15, 2, 17, "#4e3522");
      caixa(f, 66, a.pe - 42, 30, 24, "#cfc6ac"); R(f, 67, a.pe - 41, 28, 1, "#e6dfc8"); R(f, 93, a.pe - 40, 2, 21, "#b0a78e");
      R(f, 69, a.pe - 39, 22, 16, "#0a1a10"); R(f, 76, a.pe - 18, 12, 2, "#b0a78e");
      // porta-guarda-chuva
      caixa(f, 150, a.pe - 14, 7, 14, "#3a4a5a"); R(f, 151, a.pe - 22, 1, 8, "#c0392b"); R(f, 154, a.pe - 20, 1, 6, "#2f86d0");
      for (const [x] of LUMINARIAS.portaria) luminariaTeto(f, x, a);
      // balcão com abajur
      R(g, 109, a.pe - 24, 46, 4, P.tinta); R(g, 110, a.pe - 23, 44, 2, "#7d8b93"); R(g, 111, a.pe - 21, 42, 23, "#46525a"); R(g, 111, a.pe - 21, 42, 1, "#5f6d75");
      R(g, 113, a.pe - 15, 38, 1, "#5f6d75"); R(g, 120, a.pe - 28, 9, 4, "#e9e4d8"); R(g, 121, a.pe - 27, 7, 1, "#9aa0ad");
      R(g, 146, a.pe - 34, 1, 10, "#3a3a44"); caixa(g, 142, a.pe - 38, 9, 5, "#c79a3a"); R(g, 143, a.pe - 34, 7, 1, "#f6e7b0");
      porta(f, 160, a);
      break;
    }
    case "cafe": {
      parede(f, x0, x1, a, P.laranja, "#9a7b54", P.laranjaE);
      for (let x = x0; x < x1; x += 6) R(f, x, a.chao - 30, 1, 27, "rgba(0,0,0,.06)");
      for (let y = a.chao - 24; y < a.chao - 3; y += 6) R(f, x0, y, r.w, 1, "rgba(0,0,0,.05)");
      piso(f, x0, x1, a, "xadrez");
      janela(f, "cafe", 338, 40, a.teto + 20, 42);
      // cartaz
      caixa(f, 252, a.teto + 22, 32, 40, "#2a2f3a"); R(f, 254, a.teto + 24, 28, 36, "#e8463b");
      escreve(f, ">CC", 259, a.teto + 28, "#fbf3e6"); R(f, 258, a.teto + 38, 20, 1, "#fbf3e6");
      R(f, 264, a.teto + 42, 8, 10, "#1c1a26"); R(f, 265, a.teto + 43, 6, 6, "#4a5160"); R(f, 267, a.teto + 52, 2, 4, "#1c1a26"); R(f, 263, a.teto + 56, 10, 1, "#1c1a26");
      // bancada, máquina de espresso, moedor, prateleira
      R(f, 168, a.pe - 37, 58, 4, P.tinta); R(f, 169, a.pe - 36, 56, 2, "#7d6550"); R(f, 170, a.pe - 33, 54, 33, "#8a6d52"); R(f, 169, a.pe - 33, 1, 33, P.tinta); R(f, 224, a.pe - 33, 1, 33, P.tinta);
      for (const x of [172, 198]) { caixa(f, x, a.pe - 29, 24, 24, "#7a5f46"); R(f, x + 11, a.pe - 20, 2, 4, "#c9b18f"); }
      caixa(f, 174, a.pe - 56, 22, 19, "#b8bec8"); R(f, 175, a.pe - 55, 20, 2, "#d8dde6"); R(f, 178, a.pe - 50, 7, 5, "#2a2f3a"); R(f, 189, a.pe - 51, 3, 3, "#e74c3c");
      R(f, 179, a.pe - 45, 1, 4, "#5a6070"); R(f, 183, a.pe - 45, 1, 4, "#5a6070"); caneca(f, 179, a.pe - 41);
      caixa(f, 200, a.pe - 52, 8, 15, "#3a3a44"); R(f, 201, a.pe - 51, 6, 5, "#6b4426");
      caneca(f, 211, a.pe - 41, "#e9c46a"); caneca(f, 217, a.pe - 41, "#9fd8ff");
      R(f, 168, a.teto + 36, 58, 2, "#7a5f46"); for (let x = 181; x < 222; x += 8) caixa(f, x, a.teto + 28, 6, 8, ["#e9c46a", "#d04a78", "#2f86d0", "#21a184"][(x / 8 | 0) % 4]);
      planta(f, 168, a.teto + 28);
      // geladeira com ímãs e planta alta
      caixa(f, 392, a.pe - 56, 18, 56, "#e8ecef"); R(f, 393, a.pe - 55, 16, 1, "#ffffff"); R(f, 393, a.pe - 36, 16, 1, "#b8bec8");
      R(f, 405, a.pe - 50, 1, 10, "#9aa1ab"); R(f, 405, a.pe - 31, 1, 10, "#9aa1ab");
      R(f, 395, a.pe - 52, 3, 3, "#e74c3c"); R(f, 399, a.pe - 47, 3, 3, "#2f86d0"); R(f, 395, a.pe - 44, 4, 2, "#f2c230");
      planta(f, 376, a.chao + 6, true);
      for (const [x] of LUMINARIAS.cafe) luminariaTeto(f, x, a);
      // mesa redonda alta e banquetas (na frente)
      R(g, 258, a.pe - 31, 54, 4, P.tinta); R(g, 259, a.pe - 30, 52, 2, "#8a6d52"); R(g, 283, a.pe - 27, 4, 26, "#3b3f4b"); R(g, 277, a.pe - 2, 16, 2, "#3b3f4b");
      caneca(g, 266, a.pe - 35); caneca(g, 296, a.pe - 35, "#e9c46a");
      for (const x of [246, 322]) { caixa(g, x - 6, a.pe - 18, 12, 3, "#c0392b"); R(g, x - 1, a.pe - 15, 2, 14, "#3b3f4b"); R(g, x - 4, a.pe - 1, 8, 1, "#3b3f4b"); }
      porta(f, 412, a);
      break;
    }
    case "tecnica": {
      parede(f, x0, x1, a, P.aco, "#56606b", null);
      for (let x = x0 + 22; x < x1; x += 22) R(f, x, a.teto + 3, 1, a.chao - a.teto - 6, "rgba(0,0,0,.07)");
      piso(f, x0, x1, a, "tecnico");
      // calha de cabos e cabos descendo
      R(f, 418, a.teto + 10, 132, 4, P.acoEE); R(f, 418, a.teto + 10, 132, 1, P.acoE);
      for (let x = 500; x < 546; x += 3) R(f, x, a.teto + 14, 1, 14 + (x % 4) * 3, ["#e74c3c", "#2f86d0", "#e9c46a", "#21a184"][x % 4]);
      // patch panel na parede
      caixa(f, 470, a.teto + 30, 26, 14, "#2d343e"); for (let i = 0; i < 8; i++) R(f, 473 + i * 3, a.teto + 34, 2, 2, "#6b7480");
      // racks (os LEDs piscam na camada dinâmica)
      for (const x of [502, 524]) {
        caixa(f, x, a.teto + 28, 20, a.chao - a.teto - 28, P.preto); R(f, x + 1, a.teto + 29, 18, 1, "#3a424d");
        for (let y = a.teto + 32; y < a.chao - 6; y += 7) { R(f, x + 2, y, 16, 5, "#2d343e"); R(f, x + 2, y, 16, 1, "#3a434f"); }
      }
      // nobreak, caixa de ferramentas e cabos no chão
      caixa(f, 420, a.pe - 22, 14, 22, "#2d343e"); R(f, 423, a.pe - 18, 3, 2, "#21a184");
      caixa(f, 480, a.pe - 8, 14, 8, "#c0392b"); R(f, 485, a.pe - 10, 4, 2, P.tinta);
      R(g, 496, a.pe + 1, 30, 1, "#e9c46a"); R(g, 500, a.pe + 3, 26, 1, "#2f86d0");
      for (const [x] of LUMINARIAS.tecnica) luminariaTeto(f, x, a);
      cadeira(f, 446, a.pe);
      mesa(g, MESAS[3], cfg);
      break;
    }
    case "obras": {
      tijolos(f, x0, a.teto, r.w, a.chao - a.teto);
      piso(f, x0, x1, a, "cimento");
      faixaObra(f, x0, a.teto, r.w);
      R(f, 600, a.teto + 30, 32, 74, "rgba(220,230,235,.55)"); for (let y = a.teto + 34; y < a.teto + 104; y += 9) R(f, 600, y, 32, 1, "rgba(255,255,255,.4)");
      caixa(g, 594, a.pe - 9, 9, 10, "#4a6fa5"); R(g, 595, a.pe - 8, 7, 2, "#d04a78");
      R(g, 628, a.pe - 13, 6, 14, "#e86a2a"); R(g, 627, a.pe - 1, 8, 2, "#e86a2a"); R(g, 629, a.pe - 9, 4, 2, P.branco);
      R(f, 584, a.teto + 56, 2, 56, "#7a5434"); R(f, 610, a.teto + 56, 2, 56, "#7a5434");
      break;
    }
  }
}

function tijolos(f, x, y, w, h) {
  R(f, x, y, w, h, P.argamassa);
  for (let j = 0; j < h; j += 5) for (let i = ((j / 5) % 2) * 5; i < w; i += 10) R(f, x + i, y + j, 9, 4, (i + j) % 3 ? P.tijolo : P.tijoloE);
  R(f, x, y, w, 3, "rgba(0,0,0,.25)");
}
function faixaObra(f, x, y, w) { for (let i = 0; i < w; i++) R(f, x + i, y + 3, 1, 4, ((i + 400) % 10) < 5 ? P.obra : "#1d1d1d"); }
function andaimes(f, g) {
  for (const x of [554, 595, 634]) { R(f, x, 0, 3, 328, "#8d97a3"); R(f, x, 0, 1, 328, "#b0b9c4"); }
  for (const y of [4, 14]) R(f, 554, y, 83, 2, "#8d97a3");
  R(f, 556, 8, 80, 4, "#c9a96a"); R(f, 556, 8, 80, 1, "#e0c48e");
  for (const y of [100, 256]) { R(g, 556, y, 80, 3, "#c9a96a"); R(g, 556, y, 80, 1, "#e0c48e"); R(g, 556, y + 3, 80, 1, "rgba(0,0,0,.3)"); }
}

// ------------------------------------------------------------ padrões de luz (pontilhado)
function padrao(ctx, cor, densa = false) {
  const c = novoCanvas(2, 2), x = c.getContext("2d");
  x.fillStyle = cor; x.fillRect(0, 0, 1, 1); x.fillRect(1, 1, 1, 1);
  if (densa) x.fillRect(1, 0, 1, 1);
  return ctx.createPattern(c, "repeat");
}

// ------------------------------------------------------------ a cena
export class Cena2D {
  constructor(palco) {
    this.palco = palco;
    this.tipo = "2d";
    this.buf = novoCanvas(W, H);
    this.b = this.buf.getContext("2d");
    this.cfg = { pautas: [], meses: ["SET", "OUT", "NOV"] };
    this.predio = montaPredio(this.cfg);
    this.tela = novoCanvas(W, H);
    this.tela.className = "cena-tela cena-2d";
    this.tela.setAttribute("aria-hidden", "true");
    palco.prepend(this.tela);
    this.t = this.tela.getContext("2d");
    this.cam = { x: W / 2, y: H / 2, k: 2, modo: "inteiro", alvoX: W / 2, alvoY: H / 2 };
    this.estrelas = Array.from({ length: 70 }, (_, i) => ({ x: (i * 97 + 13) % 640, y: (i * 53 + 7) % 120, f: (i * 31) % 100 }));
    this.pQuente = padrao(this.b, "rgba(255,214,140,.5)");
    this.pSol = padrao(this.b, "rgba(255,240,190,.55)");
    this.pAzul = padrao(this.b, "rgba(120,190,255,.55)");
    this.pVerde = padrao(this.b, "rgba(57,255,106,.45)");
    this.pLanterna = padrao(this.b, "rgba(255,246,200,.7)", true);
    this.pVermelho = padrao(this.b, "rgba(255,80,60,.5)");
  }

  // Dados que mudam o desenho fixo: as pautas do dia no quadro e os meses do arquivo.
  configura({ pautas = [], data = null } = {}) {
    let meses = this.cfg.meses;
    if (data) { const m = +data.slice(5, 7) - 1; meses = [MESES[(m + 11) % 12], MESES[m], MESES[(m + 1) % 12]]; }
    this.cfg = { pautas, meses };
    this.predio = montaPredio(this.cfg);
  }

  // Pontos clicáveis da cena além dos personagens (em px da cena).
  alvos() {
    return [{ id: "pautas", x: 130, y: A1.teto + 7, w: 56, h: 56, rotulo: `Quadro de pautas do dia (${this.cfg.pautas.length}). Abrir a ficha do Editor.` }];
  }

  medidas(m) {
    this.cam.modo = m.modo; this.cam.k = m.k; this.dpr = m.dpr;
    this.tela.width = Math.round(m.cssW * m.dpr); this.tela.height = Math.round(m.cssH * m.dpr);
    this.tela.style.width = m.cssW + "px"; this.tela.style.height = m.cssH + "px";
    if (m.modo === "inteiro") { this.cam.x = this.cam.alvoX = W / 2; this.cam.y = this.cam.alvoY = H / 2; }
  }
  segue(x, y, instantaneo = false) {
    if (this.cam.modo === "inteiro" || x == null) return;
    const vw = this.tela.width / this.cam.k, vh = this.tela.height / this.cam.k;
    this.cam.alvoX = Math.max(vw / 2, Math.min(W - vw / 2, x));
    this.cam.alvoY = Math.max(vh / 2, Math.min(H - vh / 2, y));
    if (instantaneo) { this.cam.x = this.cam.alvoX; this.cam.y = this.cam.alvoY; }
  }
  get origem() {
    const k = this.cam.k, vw = this.tela.width / k, vh = this.tela.height / k;
    return { x: Math.round((this.cam.x - vw / 2) * k) / k, y: Math.round((this.cam.y - vh / 2) * k) / k };
  }
  projeta(x, y, alt = 0) {
    const o = this.origem, s = this.cam.k / this.dpr;
    return { x: (x - o.x) * s, y: (y - alt - o.y) * s };
  }
  escala() { return this.cam.k / this.dpr; }
  retSala(id) {
    const r = retSala(id), a = this.projeta(r.x, r.y), s = this.escala();
    return { x: a.x, y: a.y, w: r.w * s, h: r.h * s };
  }
  visao() { const o = this.origem, k = this.cam.k; return { x: o.x, y: o.y, w: this.tela.width / k, h: this.tela.height / k }; }

  // ---------------------------------------------------------- quadro
  desenha(e) {
    const { q, pessoas, t } = e, b = this.b, parado = e.semMovimento;
    const sua = parado ? 1 : Math.min(1, (e.dt || 16) / 220);
    this.cam.x += (this.cam.alvoX - this.cam.x) * sua; this.cam.y += (this.cam.alvoY - this.cam.y) * sua;

    this.ceu(q.ceu, t, parado);
    b.drawImage(this.predio.fundo, 0, 0);
    for (const j of JANELAS) { b.fillStyle = "rgba(255,255,255,.16)"; for (let i = 0; i < j.h; i++) { const x = j.x + Math.round(j.w * .15) + Math.round((j.h - i) * .5); if (x < j.x + j.w - 2) b.fillRect(x, j.y + i, 3, 1); } }
    this.relogio(e.ms, 196, A1.teto + 12); this.relogio(e.ms, 101, A0.teto + 26);
    this.vapor(q, t, parado);
    this.luzesAntes(q, t, pessoas, parado);
    this.pessoas(pessoas, t, parado, q);
    b.drawImage(this.predio.frente, 0, 0);
    this.escuro(q);
    this.luzesDepois(q, t, pessoas, parado);
    this.placas(q);
    this.blit();
  }

  ceu(c, t, parado) {
    const b = this.b, gr = b.createLinearGradient(0, 0, 0, 300);
    gr.addColorStop(0, rgb(c.alto)); gr.addColorStop(1, rgb(c.horizonte));
    b.fillStyle = gr; b.fillRect(0, 0, W, H);
    if (c.estrelas > .05) for (const s of this.estrelas) {
      const pis = parado ? 1 : (Math.sin(t / 700 + s.f) + 1) / 2;
      b.fillStyle = `rgba(255,255,240,${(.35 + .65 * pis) * c.estrelas})`; b.fillRect(s.x, s.y, 1, 1);
    }
    if (c.sol != null) { const x = Math.round(40 + c.sol * 560), y = Math.round(40 - Math.sin(c.sol * Math.PI) * 34); b.fillStyle = "rgba(255,236,170,.35)"; b.fillRect(x - 6, y - 6, 13, 13); b.fillStyle = "#fff1b8"; b.fillRect(x - 4, y - 4, 9, 9); b.fillRect(x - 5, y - 3, 11, 7); }
    if (c.lua != null) { const x = Math.round(60 + c.lua * 520), y = 10; b.fillStyle = "#f2f0e2"; b.fillRect(x - 3, y - 3, 7, 7); b.fillRect(x - 4, y - 2, 9, 5); b.fillStyle = rgb(c.alto); b.fillRect(x, y - 3, 4, 5); }
  }

  relogio(ms, cx, cy) {
    if (ms == null) return;
    const b = this.b, sp = new Date(new Date(ms).toLocaleString("en-US", { timeZone: "America/Sao_Paulo" }));
    const ah = ((sp.getHours() % 12) + sp.getMinutes() / 60) / 12 * Math.PI * 2, am = sp.getMinutes() / 60 * Math.PI * 2;
    b.fillStyle = "#1c1a26";
    for (let i = 0; i <= 3; i++) b.fillRect(Math.round(cx + Math.sin(ah) * i), Math.round(cy - Math.cos(ah) * i), 1, 1);
    for (let i = 0; i <= 5; i++) b.fillRect(Math.round(cx + Math.sin(am) * i), Math.round(cy - Math.cos(am) * i), 1, 1);
    b.fillStyle = "#c0392b"; b.fillRect(cx, cy, 1, 1);
  }

  vapor(q, t, parado) {
    if (q.luz.cafe === "apagada") return;
    const b = this.b;
    for (let i = 0; i < 4; i++) {
      const fase = parado ? i * .25 : ((t / 1400) + i * .25) % 1, y = Math.round(A0.pe - 58 - fase * 22), x = 181 + Math.round(Math.sin(fase * 6 + i) * 2);
      b.fillStyle = `rgba(255,255,255,${(.6 * (1 - fase)).toFixed(2)})`; b.fillRect(x, y, 2, 2);
    }
  }

  pessoas(pessoas, t, parado, q) {
    const b = this.b;
    for (const p of pessoas) {
      const inf = p.info || {};
      const est = p.andando ? "andando" : inf.estado || "parado";
      const seed = p.id.length * 7 + p.id.charCodeAt(0);
      const f = parado && est !== "andando" ? 0 : quadroNoTempo(est, t, seed, p.id);
      const fala = inf.fala && !p.andando && !parado ? Math.floor(t / 170) % 2 === 1 : false;
      const op = p.id === "vigia" && inf.lanterna && p.andando ? { lanternaAlta: true } : {};
      const spr = sprite(p.id, est, est === "cafe" && inf.fala ? (fala ? 1 : 0) : f, est !== "cafe" && est !== "trabalhando" && fala, op);
      const x = Math.round(p.x), y = Math.round(p.y);
      b.globalAlpha = p.opacidade ?? 1;
      b.fillStyle = "rgba(10,10,20,.28)"; b.fillRect(x - 10, y, 21, 2); b.fillRect(x - 7, y + 2, 15, 1);
      if (p.andando && p.dir < 0) { b.save(); b.translate(x + 20, y - PE); b.scale(-1, 1); b.drawImage(spr, 0, 0); b.restore(); }
      else b.drawImage(spr, x - 20, y - PE);
      b.globalAlpha = 1;
    }
  }

  // Escuro por sala: noite azul; de dia, sem luz acesa, uma penumbra leve.
  escuro(q) {
    const b = this.b, dia = q.ceu.dia, noite = dia < .3;
    for (const s of SALAS) {
      const modo = q.luz[s.id] || "acesa", r = retSala(s.id);
      let a = 0;
      if (modo === "apagada") a = .8 - dia * .45;
      else if (modo === "penumbra") a = .1 + (1 - dia) * .5;
      else if (modo === "obra") a = .08 + (1 - dia) * .45;
      else if (modo === "acesa") a = noite ? .32 : (1 - dia) * .2;
      if (s.id === "escada") a = Math.max(a, .12 + (1 - dia) * .55);
      if (a > .01) { b.fillStyle = `rgba(8,12,38,${a.toFixed(3)})`; b.fillRect(r.x, r.y, r.w, r.h); }
    }
    if (dia < .5) { b.fillStyle = `rgba(8,12,34,${((.5 - dia) * .9).toFixed(3)})`; b.fillRect(0, 328, W, 32); }
  }

  cone(x, yTopo, larguraTopo, yChao, larguraChao, padrao, alfa) {
    const b = this.b;
    b.save(); b.globalAlpha = alfa;
    b.beginPath();
    b.moveTo(x - larguraTopo / 2, yTopo); b.lineTo(x + larguraTopo / 2, yTopo);
    b.lineTo(x + larguraChao / 2, yChao); b.lineTo(x - larguraChao / 2, yChao); b.closePath();
    b.fillStyle = padrao; b.fill();
    b.globalAlpha = alfa * .25; b.fillStyle = "rgba(255,220,150,.3)"; b.fill();
    b.restore();
  }
  poca(x, y, w, h, padrao, alfa) {      // poça de luz no chão
    const b = this.b; b.save(); b.globalAlpha = alfa; b.fillStyle = padrao;
    b.fillRect(Math.round(x - w / 2), y, Math.round(w), h); b.fillRect(Math.round(x - w / 2 + 4), y - 1, Math.round(w - 8), 1); b.fillRect(Math.round(x - w / 2 + 4), y + h, Math.round(w - 8), 1);
    b.restore();
  }

  // Luz que fica atrás das pessoas: sol, cones das luminárias, brilho das telas na parede.
  luzesAntes(q, t, pessoas, parado) {
    const b = this.b, dia = q.ceu.dia, noite = dia < .3, A = { 1: A1, 0: A0 };
    if (q.ceu.sol != null && dia > .35) {
      const desvio = Math.round((.5 - q.ceu.sol) * 46);
      for (const j of JANELAS) {
        const a = A[SALA[j.sala].andar], alfa = (dia - .3) * .9;
        b.save(); b.fillStyle = this.pSol;
        b.beginPath(); b.moveTo(j.x, j.y + j.h + 5); b.lineTo(j.x + j.w, j.y + j.h + 5); b.lineTo(j.x + j.w + desvio, a.chao + 2); b.lineTo(j.x + desvio, a.chao + 2); b.closePath();
        b.globalAlpha = alfa * .22; b.fill();
        b.globalAlpha = alfa * .9; b.fillRect(j.x + desvio, a.chao + 3, j.w + 2, 9);
        b.restore();
      }
    }
    const intens = noite ? 1 : .45 + (1 - dia) * .5;
    for (const s of SALAS) {
      if (q.luz[s.id] !== "acesa" || dia > .85) continue;
      const a = A[s.andar]; if (!a) continue;
      for (const [x, w] of LUMINARIAS[s.id] || []) this.cone(x, a.teto + 12, 8, a.chao + 8, w, this.pQuente, .5 * intens);
    }
    for (const m of MESAS) {
      if (!m.abajur || q.luz[m.a === A1 ? "redacao" : "tecnica"] !== "acesa") continue;
      const x0 = Math.round(m.x - m.w / 2), lx = m.abajur > 0 ? x0 + m.w - 5 : x0 + 3, top = m.a.pe - 20;
      this.cone(lx, top - 9, 4, top, 18, this.pQuente, .9 * intens);
    }
    // brilho das telas na parede atrás do monitor
    for (const m of MESAS) {
      const p = pessoas.find(p => p.id === m.de), sala = m.a === A1 ? "redacao" : "tecnica";
      const forte = p && !p.andando && p.info && p.info.estado === "trabalhando";
      if (!forte && q.luz[sala] !== "acesa") continue;
      const x0 = Math.round(m.x - m.w / 2), top = m.a.pe - 20;
      for (const lado of m.monitor) {
        const mx = lado < 0 ? x0 + 2 : x0 + m.w - 18;
        b.save(); b.globalAlpha = forte ? .85 : .4; b.fillStyle = this.pAzul;
        b.fillRect(mx - 2, top - 17, 20, 3); b.fillRect(mx - 3, top - 14, 22, 10); b.fillRect(mx - 1, top - 4, 18, 2);
        b.restore();
      }
    }
    // luz do corredor (escada), acesa de noite
    if (dia < .45) {
      const al = noite ? 1 : (.45 - dia) * 4;
      this.cone(26, 46, 6, A1.pe, 30, this.pQuente, .35 * al);
      this.cone(26, 202, 6, A0.pe - 40, 30, this.pQuente, .35 * al);
    }
  }

  // Luz que fica na frente: poças no chão, telas, LEDs, ON AIR, CRT, lanterna, letreiro.
  luzesDepois(q, t, pessoas, parado) {
    const b = this.b, dia = q.ceu.dia, noite = dia < .3, A = { 1: A1, 0: A0 };
    const intens = noite ? 1 : .45 + (1 - dia) * .5;
    for (const s of SALAS) {
      if (q.luz[s.id] !== "acesa" || dia > .85) continue;
      const a = A[s.andar]; if (!a) continue;
      for (const [x, w] of LUMINARIAS[s.id] || []) this.poca(x, a.chao + 6, w * .85, 5, this.pQuente, .6 * intens);
    }
    // telas: a borda do monitor brilha e o rosto de quem trabalha pega a luz azul
    for (const m of MESAS) {
      const p = pessoas.find(p => p.id === m.de), sala = m.a === A1 ? "redacao" : "tecnica";
      const forte = p && !p.andando && p.info && p.info.estado === "trabalhando";
      if (!forte && q.luz[sala] !== "acesa") continue;
      const x0 = Math.round(m.x - m.w / 2), top = m.a.pe - 20;
      for (const lado of m.monitor) {
        const mx = lado < 0 ? x0 + 2 : x0 + m.w - 18;
        R(b, mx + 1, top - 15, 14, 1, forte ? "#bfe3ff" : "#7fb0d8");
        if (forte) { b.save(); b.globalAlpha = .35; b.fillStyle = this.pAzul; b.fillRect(m.x + (lado < 0 ? -9 : 1), m.a.pe - 49, 8, 15); b.restore(); }
      }
    }
    if (q.onair) {
      b.save(); b.globalAlpha = .8; b.fillStyle = this.pVermelho; b.fillRect(384, A1.teto + 2, 56, 24); b.restore();
      R(b, 392, A1.teto + 8, 40, 11, "#e5392b"); escreve(b, "ON AIR", 395, A1.teto + 10, "#fff4e8");
    } else { R(b, 392, A1.teto + 8, 40, 11, "#3a1e20"); escreve(b, "ON AIR", 395, A1.teto + 10, "#7a4a48"); }
    for (let i = 0; i < 8; i++) {
      const h = q.onair && !parado ? 1 + Math.floor((Math.sin(t / 90 + i * 1.3) + 1) * 2) : 1;
      for (let k = 0; k < h; k++) R(b, 374 + i * 3, A1.pe - 26 - k, 2, 1, k > 2 ? "#e74c3c" : k > 1 ? "#f2c230" : "#45ff7a");
    }
    const tec = pessoas.some(p => p.id === "produtor" && p.info && p.info.estado === "trabalhando" && !p.andando);
    for (const x of [502, 524]) for (let i = 0, y = A0.teto + 33; y < A0.chao - 6; y += 7, i++) {
      const on = parado ? i % 3 !== 1 : Math.sin(t / (tec ? 70 : 500) + i * 1.7 + x) > -.2;
      R(b, x + 15, y + 2, 2, 1, on ? (i % 5 === 0 ? "#ffb347" : "#45ff7a") : "#1d4a2a");
      if (i % 4 === 2) R(b, x + 12, y + 2, 1, 1, on ? "#7dd3ff" : "#1d3a4a");
    }
    const cy = A0.pe - 39;
    b.save(); b.globalAlpha = noite ? .7 : .3; b.fillStyle = this.pVerde; b.fillRect(62, cy - 6, 38, 30); b.restore();
    R(b, 69, cy, 22, 16, "#0b2414"); escreve(b, ">CC", 71, cy + 4, "#39ff6a");
    if (parado || Math.floor(t / 530) % 2) R(b, 88, cy + 10, 2, 1, "#39ff6a");
    for (let y = cy; y < cy + 16; y += 2) R(b, 69, y, 22, 1, "rgba(0,0,0,.25)");
    if (dia < .45) {
      const al = noite ? 1 : (.45 - dia) * 4;
      this.cone(146, A0.pe - 33, 6, A0.pe - 24, 22, this.pQuente, .9 * al);
      this.poca(28, A0.pe + 2, 34, 4, this.pQuente, .5 * al);
      const v = pessoas.find(p => p.id === "vigia");
      if (v && v.info && v.info.lanterna && v.andando) {
        const d = v.dir < 0 ? -1 : 1, hx = Math.round(v.x) + d * 20, hy = Math.round(v.y) - 23, sw = parado ? 0 : Math.sin(t / 500) * 3;
        b.save(); b.globalAlpha = .85; b.fillStyle = this.pLanterna;
        b.beginPath(); b.moveTo(hx, hy - 1); b.lineTo(hx + d * 46, hy - 10 + sw); b.lineTo(hx + d * 46, hy + 20 + sw); b.lineTo(hx, hy + 2); b.closePath(); b.fill();
        b.restore();
        this.poca(hx + d * 40, Math.round(v.y) - 1, 24, 3, this.pLanterna, .7);
      }
    }
    const neon = .55 + (1 - dia) * .45;
    b.save(); b.globalAlpha = .5 * neon; b.fillStyle = this.pVerde; b.fillRect(240, 0, 62, 16); b.restore();
    escreve(b, ">CC", 256, 4, `rgba(57,255,106,${neon.toFixed(2)})`);
    if (parado || Math.floor(t / 550) % 2) { b.fillStyle = `rgba(57,255,106,${neon.toFixed(2)})`; b.fillRect(276, 4, 4, 7); }
  }

  placas(q) {
    const b = this.b, escuro = id => q.luz[id] === "apagada";
    const p = (txt, cx, y, id, op = {}) => { b.globalAlpha = escuro(id) ? .65 : 1; placa(b, txt, cx, y, op); b.globalAlpha = 1; };
    p("REDAÇÃO", 92, A1.teto + 6, "redacao");
    p("CABINE", 364, A1.teto + 7, "cabine", { fundo: "#132a2d", texto: "#cfe9e6" });
    p("ARQUIVO", 500, A1.teto + 1, "arquivo");
    p("PORTARIA", 90, A0.teto + 6, "portaria");
    p("CAFÉ", 200, A0.teto + 8, "cafe");
    p("TÉCNICA", 444, A0.teto + 18, "tecnica");
    b.globalAlpha = .95;
    placa(b, "CHECAGEM E", 597, A1.teto + 12, { fundo: "#e8f4f8", texto: "#25414d", pad: 2 });
    placa(b, "COMPLIANCE", 597, A1.teto + 23, { fundo: "#e8f4f8", texto: "#25414d", pad: 2 });
    placa(b, "ALA NOVA", 580, A0.teto + 12, { fundo: P.obra, texto: "#1d1d1d", pad: 2 });
    placa(b, "EM OBRAS", 580, A0.teto + 23, { fundo: "#1d1d1d", texto: P.obra, pad: 2 });
    placa(b, "EM BREVE", 597, A0.teto + 46, { fundo: "#fbf7ec", texto: "#b8433a", borda: "#7a5434", pad: 2 });
    b.globalAlpha = 1;
  }

  blit() {
    const k = this.cam.k, o = this.origem, t = this.t;
    t.imageSmoothingEnabled = false;
    t.fillStyle = "#0b0e12"; t.fillRect(0, 0, this.tela.width, this.tela.height);
    t.drawImage(this.buf, -Math.round(o.x * k), -Math.round(o.y * k), W * k, H * k);
  }

  desmonta() { this.tela.remove(); }
}
