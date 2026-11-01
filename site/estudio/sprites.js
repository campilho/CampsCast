// Os 10 personagens em pixel art, 40 × 56, desenhados em código.
// Cabeça grande (18 × 17) para o rosto e o acessório se lerem no celular.
// Estados: parado (2 quadros), trabalhando (4), andando (4), cafe (3), congelado (1).
// Cada quadro vira um canvas pequeno, guardado em cache.

export const SW = 40, SH = 56, PE = 53;      // PE: linha dos pés dentro do sprite

export const PERSONAS = {
  produtor:   { cor: "#d8962c", pele: "#b87a4b", cabelo: "#2b1d16", estilo: "curto",    calca: "#3b4056", sapato: "#24252e", acessorio: "prancheta", passo: 240 },
  jornalista: { cor: "#2f86d0", pele: "#7c4a2d", cabelo: "#17110e", estilo: "cacheado", calca: "#2d3446", sapato: "#1f2029", acessorio: "bloco",     passo: 130 },
  editor:     { cor: "#7a5fd0", pele: "#e7b993", cabelo: "#c3c4cd", estilo: "grisalho", calca: "#40384f", sapato: "#26222e", acessorio: "oculos",    passo: 300 },
  roteirista: { cor: "#d04a78", pele: "#d49b6c", cabelo: "#4a2a1b", estilo: "longo",    calca: "#33354a", sapato: "#24232c", acessorio: "lapis",     passo: 190 },
  locutor:    { cor: "#21a184", pele: "#f1caa6", cabelo: "#6a4a2e", estilo: "lado",     calca: "#2c3a40", sapato: "#1d2427", acessorio: "fone",      passo: 170 },
  vigia:      { cor: "#56667b", pele: "#9b6341", cabelo: "#1c1c1c", estilo: "raspado",  calca: "#2a313c", sapato: "#191c22", acessorio: "bone",      passo: 320 },
  arquivista: { cor: "#8a6d3b", pele: "#e3b58b", cabelo: "#d9d6cf", estilo: "coque",    calca: "#4a4136", sapato: "#2a241f", acessorio: "caixa",     passo: 240 },
  checador:   { cor: "#b8433a", pele: "#c68d5d", cabelo: "#2a2a2a", estilo: "curto",    calca: "#3a3236", sapato: "#221d20", acessorio: "lupa",      passo: 300 },
  artista:    { cor: "#d07e1c", pele: "#8f5b3b", cabelo: "#2a1a14", estilo: "lado",     calca: "#3c3a3a", sapato: "#26201e", acessorio: "boina",     passo: 300 },
  marketing:  { cor: "#3e7fa6", pele: "#f3d1b1", cabelo: "#d6ae58", estilo: "coque",    calca: "#2f3a48", sapato: "#1e232b", acessorio: "megafone",  passo: 300 },
};

export const QUADROS = { parado: 2, trabalhando: 4, andando: 4, cafe: 3, congelado: 1 };

const CONTORNO = "#17151f", OLHO = "#1b1b2a", BOCA = "#6b2f2f", BRANCO = "#ffffff";

// ------------------------------------------------------------ cores
const hx = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
const rgb = a => "#" + a.map(v => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, "0")).join("");
export const escurece = (h, f) => rgb(hx(h).map(v => v * (1 - f)));
export const clareia = (h, f) => rgb(hx(h).map(v => v + (255 - v) * f));
const mistura = (a, b, t) => rgb(hx(a).map((v, i) => v + (hx(b)[i] - v) * t));

// ------------------------------------------------------------ grade
function grade() { return Array.from({ length: SH }, () => Array(SW).fill(null)); }
function P(g, x, y, c) { if (c && x >= 0 && x < SW && y >= 0 && y < SH) g[y][x] = c; }
function R(g, x, y, w, h, c) { for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) P(g, x + i, y + j, c); }
function apaga(g, x, y) { if (x >= 0 && x < SW && y >= 0 && y < SH) g[y][x] = null; }

// ------------------------------------------------------------ partes do corpo
function cabeloTras(g, d, u) {
  const c = escurece(d.cabelo, .18);
  if (d.estilo === "longo") { R(g, 9, 7 + u, 22, 22, c); R(g, 10, 29 + u, 20, 1, c); }
  if (d.estilo === "cacheado") R(g, 9, 6 + u, 22, 10, c);
}

function pernas(g, d, estado, f) {
  const c = d.calca, ce = escurece(c, .3), s = d.sapato, sc = clareia(s, .15);
  const perna = (x, y1, sx) => { R(g, x, 41, 6, y1 - 41 + 1, c); R(g, x + 5, 41, 1, y1 - 41 + 1, ce); R(g, sx, y1 + 1, 7, 3, s); R(g, sx + 1, y1 + 1, 3, 1, sc); };
  if ((estado === "andando" || estado === "carregando") && (f === 0 || f === 2)) {
    const esq = f === 0;
    perna(13, esq ? 50 : 47, esq ? 11 : 12);
    perna(21, esq ? 47 : 50, esq ? 21 : 22);
  } else {
    perna(13, 50, 12);
    perna(21, 50, 21);
  }
  R(g, 13, 41, 14, 3, c); R(g, 19, 44, 2, 6, null);
  for (let y = 44; y <= 50; y++) { apaga(g, 19, y); apaga(g, 20, y); }
}

function tronco(g, d, u) {
  const c = d.cor, ce = escurece(c, .22), cc = clareia(c, .22);
  R(g, 12, 23 + u, 16, 18, c);
  R(g, 25, 23 + u, 3, 18, ce); R(g, 12, 24 + u, 1, 16, cc);
  apaga(g, 12, 23 + u); apaga(g, 27, 23 + u);
  // gola em V
  R(g, 18, 23 + u, 4, 1, d.pele); R(g, 19, 24 + u, 2, 1, escurece(d.pele, .1)); P(g, 17, 23 + u, cc); P(g, 22, 23 + u, cc);
  P(g, 19, 28 + u, ce); P(g, 19, 32 + u, ce);      // botões
  R(g, 12, 40 + u, 16, 1, escurece(d.calca, .25));
}

function braco(g, d, lado, pose, u, f = 0) {
  const c = d.cor, ce = escurece(c, .3), pe = d.pele, pee = escurece(d.pele, .18);
  const x = lado < 0 ? 8 : 28, borda = lado < 0 ? x : x + 3;
  switch (pose) {
    case "baixo": case "frente": case "tras": {
      const dy = pose === "frente" ? -1 : 0, dx = pose === "frente" ? -lado : pose === "tras" ? lado : 0;
      R(g, x + dx, 24 + u + dy, 4, 13, c); R(g, borda + dx, 24 + u + dy, 1, 13, ce);
      R(g, x + dx, 37 + u + dy, 4, 3, pe); P(g, borda + dx, 39 + u + dy, pee);
      break;
    }
    case "teclado": {      // antebraço sobre a mesa, mãos no teclado
      const up = f ? -1 : 0;
      R(g, x, 24 + u, 4, 7, c); R(g, borda, 24 + u, 1, 7, ce);
      const fx = lado < 0 ? 11 : 22;
      R(g, fx, 31 + u + up, 7, 3, c); R(g, fx, 33 + u + up, 7, 1, ce);
      R(g, lado < 0 ? 17 : 20, 31 + u + up, 3, 3, pe);
      break;
    }
    case "peito": {        // segurando algo à frente do peito
      const up = f ? -1 : 0;
      R(g, x, 24 + u, 4, 6, c); R(g, borda, 24 + u, 1, 6, ce);
      const fx = lado < 0 ? 11 : 22;
      R(g, fx, 30 + u + up, 7, 3, c); R(g, fx, 32 + u + up, 7, 1, ce);
      R(g, lado < 0 ? 16 : 21, 29 + u + up, 3, 4, pe);
      break;
    }
    case "alto": {         // mão perto do rosto
      R(g, x, 21 + u, 4, 9, c); R(g, borda, 21 + u, 1, 9, ce);
      R(g, lado < 0 ? x + 1 : x - 1, 17 + u, 4, 4, pe);
      break;
    }
    case "estendido": {    // braço esticado para a frente (lanterna)
      R(g, x, 24 + u, 4, 6, c); R(g, borda, 24 + u, 1, 6, ce);
      R(g, lado < 0 ? 5 : 31, 30 + u, 5, 3, c);
      R(g, lado < 0 ? 3 : 34, 30 + u, 3, 3, pe);
      break;
    }
  }
}

function cabeca(g, d, u, { olhos = "abertos", boca = "fechada", vira = 0 } = {}) {
  const pe = d.pele, pee = escurece(d.pele, .16), pec = clareia(d.pele, .14);
  R(g, 17, 21 + u, 6, 2, pee);                     // pescoço
  R(g, 11, 4 + u, 18, 17, pe);
  R(g, 27, 6 + u, 2, 13, pee); R(g, 12, 20 + u, 16, 1, pee);
  R(g, 12, 6 + u, 1, 6, pec);
  for (const [x, y] of [[11, 4], [12, 4], [11, 5], [27, 4], [28, 4], [28, 5], [11, 20], [28, 20], [11, 19], [28, 19]]) apaga(g, x, y + u);
  R(g, 10, 11 + u, 1, 4, pe); R(g, 29, 11 + u, 1, 4, pee); P(g, 10, 12 + u, pee);     // orelhas
  const v = vira;
  // sobrancelhas
  const sb = escurece(d.cabelo === "#d9d6cf" || d.cabelo === "#c3c4cd" ? "#8a8a92" : d.cabelo, .1);
  R(g, 14 + v, 10 + u, 4, 1, sb); R(g, 22 + v, 10 + u, 4, 1, sb);
  // olhos
  if (olhos === "fechados") { R(g, 14 + v, 14 + u, 3, 1, OLHO); R(g, 22 + v, 14 + u, 3, 1, OLHO); }
  else {
    R(g, 15 + v, 12 + u, 2, 3, OLHO); R(g, 23 + v, 12 + u, 2, 3, OLHO);
    P(g, 15 + v, 12 + u, BRANCO); P(g, 23 + v, 12 + u, BRANCO);
  }
  R(g, 19 + v, 16 + u, 2, 1, pee);                                  // nariz
  const bochecha = mistura(pe, "#e0636b", .3);
  R(g, 13 + v, 16 + u, 2, 1, bochecha); R(g, 25 + v, 16 + u, 2, 1, bochecha);
  if (boca === "aberta") { R(g, 18 + v, 18 + u, 4, 2, BOCA); R(g, 19 + v, 19 + u, 2, 1, "#c45a5a"); }
  else if (boca === "meia") { R(g, 18 + v, 18 + u, 4, 1, BOCA); }
  else if (boca === "sorriso") { P(g, 17 + v, 17 + u, BOCA); R(g, 18 + v, 18 + u, 4, 1, BOCA); P(g, 22 + v, 17 + u, BOCA); }
  else R(g, 18 + v, 18 + u, 4, 1, mistura(pe, BOCA, .6));
}

function cabeloFrente(g, d, u) {
  const c = d.cabelo, cc = clareia(c, .25), ce = escurece(c, .2);
  const topo = () => { R(g, 14, 2 + u, 12, 1, c); R(g, 12, 3 + u, 16, 1, c); R(g, 11, 4 + u, 18, 3, c); R(g, 15, 3 + u, 4, 1, cc); R(g, 13, 4 + u, 3, 1, cc); };
  switch (d.estilo) {
    case "curto":
      topo(); R(g, 11, 7 + u, 3, 4, c); R(g, 26, 7 + u, 3, 4, c); R(g, 14, 7 + u, 5, 1, c); R(g, 24, 5 + u, 4, 2, ce); break;
    case "lado":
      topo(); R(g, 11, 7 + u, 3, 5, c); R(g, 26, 7 + u, 3, 3, c); R(g, 14, 7 + u, 9, 1, c); R(g, 14, 8 + u, 5, 1, c); R(g, 15, 7 + u, 3, 1, cc); break;
    case "raspado":
      R(g, 13, 3 + u, 14, 1, c); R(g, 11, 4 + u, 18, 2, c); R(g, 11, 6 + u, 1, 4, c); R(g, 28, 6 + u, 1, 4, c); break;
    case "grisalho":
      R(g, 15, 3 + u, 10, 1, cc); R(g, 11, 5 + u, 4, 3, c); R(g, 25, 5 + u, 4, 3, c); R(g, 15, 4 + u, 10, 1, cc); R(g, 12, 4 + u, 3, 1, c); R(g, 25, 4 + u, 3, 1, c);
      R(g, 11, 8 + u, 2, 6, c); R(g, 27, 8 + u, 2, 6, c); break;
    case "cacheado":
      R(g, 14, 0 + u, 12, 1, c); R(g, 11, 1 + u, 18, 1, c); R(g, 10, 2 + u, 20, 2, c); R(g, 9, 4 + u, 22, 4, c);
      R(g, 9, 8 + u, 4, 4, c); R(g, 27, 8 + u, 4, 4, c); R(g, 13, 8 + u, 14, 1, c);
      for (const [x, y] of [[13, 1], [17, 2], [21, 1], [25, 3], [11, 4], [15, 5], [19, 4], [23, 6], [27, 5], [10, 7], [29, 8], [10, 10], [28, 10]]) P(g, x, y + u, cc);
      apaga(g, 9, 4 + u); apaga(g, 30, 4 + u); apaga(g, 10, 1 + u); apaga(g, 29, 1 + u); break;
    case "longo":
      topo(); R(g, 10, 7 + u, 3, 16, c); R(g, 27, 7 + u, 3, 16, c); R(g, 13, 7 + u, 6, 1, c); R(g, 13, 8 + u, 3, 1, c); R(g, 10, 8 + u, 1, 12, cc); break;
    case "coque":
      topo(); R(g, 16, 0 + u, 8, 3, c); R(g, 17, 0 + u, 3, 1, cc); R(g, 11, 7 + u, 3, 3, c); R(g, 26, 7 + u, 3, 3, c); R(g, 20, 7 + u, 6, 1, c); break;
  }
}

// ------------------------------------------------------------ acessórios
function acessorio(g, d, estado, f, u) {
  const trab = estado === "trabalhando", cafe = estado === "cafe", anda = estado === "andando";
  switch (d.acessorio) {
    case "prancheta": {                              // âmbar · prancheta
      if (cafe) { R(g, 4, 25 + u, 4, 14, "#c9a96a"); R(g, 4, 25 + u, 4, 1, "#5d5f6a"); break; }
      const y = 28 + u - (trab && f % 2 ? 1 : 0);
      R(g, 2, y, 10, 14, "#c9a96a"); R(g, 3, y + 2, 8, 11, "#f6f1e3");
      for (let i = 0; i < 4; i++) { R(g, 6, y + 4 + i * 3, 4, 1, "#9aa0ad"); P(g, 4, y + 4 + i * 3, trab && i <= f ? "#21a184" : "#9aa0ad"); }
      R(g, 5, y - 1, 4, 2, "#5d5f6a");
      if (trab) { P(g, 9 + (f % 2), y + 3 + f * 3, "#2b2f3a"); P(g, 10 + (f % 2), y + 2 + f * 3, "#2b2f3a"); }
      break;
    }
    case "bloco": {                                  // azul · bloco de notas
      if (trab) break;                               // digitando: o bloco fica na mesa
      const x = cafe ? 2 : 3, y = cafe ? 33 : 31;
      R(g, x, y + u, 7, 9, "#fbfaf4"); R(g, x, y + u, 7, 2, "#c0392b"); for (let i = 0; i < 3; i++) R(g, x + 1, y + 3 + u + i * 2, 5, 1, "#8fb3d9");
      for (let i = 0; i < 3; i++) P(g, x + 1 + i * 2, y - 1 + u, "#9aa0ad");
      break;
    }
    case "oculos": {                                 // violeta · óculos
      const k = "#2a2433", l = "#d6ebff";
      for (const x0 of [13, 21]) { R(g, x0, 11 + u, 6, 5, k); R(g, x0 + 1, 12 + u, 4, 3, l); }
      R(g, 19, 12 + u, 2, 1, k); R(g, 11, 12 + u, 2, 1, k); R(g, 27, 12 + u, 2, 1, k);
      if (estado !== "parado" || true) { R(g, 15, 12 + u, 2, 3, OLHO); R(g, 23, 12 + u, 2, 3, OLHO); P(g, 15, 12 + u, BRANCO); P(g, 23, 12 + u, BRANCO); }
      if (trab) {                                    // folheando
        const y = 29 + u;
        R(g, 13, y, 14, 8, "#fbfaf4"); R(g, 13, y + 7, 14, 1, "#c9ced8"); for (let i = 0; i < 3; i++) R(g, 15, y + 2 + i * 2, 10, 1, "#a7adb9");
        R(g, 19, y, 1, 8, "#c9ced8");
        if (f === 1) { R(g, 21, y - 3, 5, 3, "#ffffff"); R(g, 20, y - 1, 2, 1, "#ffffff"); }
        if (f === 2) { R(g, 19, y - 6, 2, 6, "#ffffff"); }
        if (f === 3) { R(g, 14, y - 3, 5, 3, "#ffffff"); R(g, 18, y - 1, 2, 1, "#ffffff"); }
      }
      break;
    }
    case "lapis": {                                  // rosa · lápis atrás da orelha
      P(g, 32, 4 + u, "#f08ca0"); P(g, 32, 5 + u, "#f08ca0"); P(g, 31, 6 + u, "#c8c8c8");
      R(g, 31, 7 + u, 1, 2, "#f2c14e"); R(g, 30, 9 + u, 1, 2, "#f2c14e"); P(g, 29, 11 + u, "#e8c79a"); P(g, 29, 12 + u, "#3a2a20");
      if (trab) {                                    // escrevendo: lápis na mão direita
        const dx = [0, 1, 2, 1][f];
        R(g, 23 + dx, 26 + u, 1, 5, "#f2c14e"); P(g, 23 + dx, 25 + u, "#f08ca0"); P(g, 23 + dx, 31 + u, "#3a2a20");
      }
      break;
    }
    case "fone": {                                   // verde-água · fone de ouvido
      const k = "#272b36";
      R(g, 13, 1 + u, 14, 1, k); R(g, 11, 2 + u, 2, 1, k); R(g, 27, 2 + u, 2, 1, k); R(g, 10, 3 + u, 1, 7, k); R(g, 29, 3 + u, 1, 7, k);
      R(g, 7, 10 + u, 4, 7, k); R(g, 29, 10 + u, 4, 7, k); R(g, 8, 12 + u, 2, 3, d.cor); R(g, 30, 12 + u, 2, 3, d.cor);
      break;
    }
    case "bone": {                                   // ardósia · boné e lanterna
      const k = "#2b3545", kc = "#3d4a5e";
      R(g, 13, 1 + u, 14, 1, k); R(g, 11, 2 + u, 18, 5, k); R(g, 14, 2 + u, 6, 1, kc); R(g, 11, 7 + u, 22, 2, escurece(k, .25)); R(g, 29, 7 + u, 4, 1, kc);
      R(g, 18, 3 + u, 4, 3, "#e9c46a"); P(g, 19, 4 + u, "#b38b2a");
      if (cafe) break;
      if (anda || d.lanternaAlta) { R(g, 34, 29 + u, 5, 3, "#8a929e"); R(g, 34, 29 + u, 5, 1, "#a8b0bc"); R(g, 39, 29 + u, 1, 3, "#fff2b0"); }
      else { R(g, 29, 37 + u, 3, 6, "#8a929e"); R(g, 29, 37 + u, 1, 6, "#5c636e"); R(g, 29, 43 + u, 3, 1, "#fff2b0"); }
      break;
    }
    case "caixa": {                                  // marrom · caixa de arquivo
      if (cafe) { R(g, 1, 45, 9, 8, "#b8894f"); R(g, 1, 45, 9, 2, "#8a6334"); R(g, 3, 48, 5, 3, "#f3ead7"); break; }
      const y = 27 + u - (trab ? [0, 2, 3, 2][f] : 0);
      R(g, 10, y, 20, 12, "#b8894f"); R(g, 10, y, 20, 2, "#8a6334"); R(g, 27, y + 2, 3, 10, "#9c7240");
      R(g, 15, y + 4, 9, 5, "#f3ead7"); R(g, 16, y + 5, 7, 1, "#9c8f7a"); R(g, 16, y + 7, 5, 1, "#9c8f7a");
      R(g, 7, y + 3, 3, 4, d.pele); R(g, 30, y + 3, 3, 4, d.pele);
      break;
    }
    case "lupa": {                                   // vermelho · lupa
      const k = "#3a2a22";
      R(g, 30, 13 + u, 8, 1, k); R(g, 30, 21 + u, 8, 1, k); R(g, 29, 14 + u, 1, 7, k); R(g, 38, 14 + u, 1, 7, k);
      R(g, 30, 14 + u, 8, 7, "#d6efff"); R(g, 31, 15 + u, 2, 2, "#ffffff"); R(g, 28, 22 + u, 2, 5, "#7a4a2a");
      break;
    }
    case "boina": {                                  // laranja · boina e pincel
      const k = "#7a2433";
      R(g, 12, 1 + u, 14, 1, k); R(g, 9, 2 + u, 19, 4, k); R(g, 10, 2 + u, 6, 1, clareia(k, .25)); P(g, 18, 0 + u, k);
      R(g, 31, 27 + u, 2, 11, "#7a4a2a"); R(g, 31, 25 + u, 2, 2, "#b0b6c0"); R(g, 31, 22 + u, 2, 3, "#e9e1d0"); R(g, 31, 21 + u, 2, 1, "#d4507a");
      break;
    }
    case "megafone": {                               // azul-petróleo · megafone
      const b = "#f4efe4", r = "#d0453a";
      R(g, 27, 17 + u, 2, 3, b); R(g, 29, 16 + u, 2, 5, b); R(g, 31, 15 + u, 2, 7, b); R(g, 33, 14 + u, 2, 9, b); R(g, 35, 13 + u, 2, 11, b);
      R(g, 31, 15 + u, 1, 7, r); R(g, 37, 13 + u, 1, 11, "#c9c2b4"); R(g, 30, 21 + u, 1, 4, "#3a3a3a");
      break;
    }
  }
}

// ------------------------------------------------------------ montagem
function monta(id, estado, f, abre = false, op = {}) {
  const d = { ...PERSONAS[id], ...op }, g = grade();
  const andando = estado === "andando";
  const carrega = estado === "trabalhando" && d.acessorio === "caixa";
  const u = (estado === "parado" && f === 1) || (andando && (f === 1 || f === 3)) || (carrega && (f === 1 || f === 3)) ? 1 : 0;
  cabeloTras(g, d, u);
  pernas(g, d, carrega ? "carregando" : estado, f);
  tronco(g, d, u);

  let esq = "baixo", dir = "baixo";
  if (andando) { esq = f === 0 ? "frente" : f === 2 ? "tras" : "baixo"; dir = f === 0 ? "tras" : f === 2 ? "frente" : "baixo"; }
  if (estado === "trabalhando") {
    switch (d.acessorio) {
      case "bloco": esq = "teclado"; dir = "teclado"; break;                    // digitando
      case "oculos": esq = "peito"; dir = "peito"; break;                       // folheando
      case "lapis": esq = "teclado"; dir = "peito"; break;                      // escrevendo
      case "fone": esq = f === 1 || f === 2 ? "alto" : "baixo"; dir = "baixo"; break;  // falando ao microfone
      case "prancheta": esq = "baixo"; dir = "peito"; break;
      case "caixa": esq = dir = "nenhum"; break;
      default: esq = "peito"; dir = "peito";
    }
  }
  if (d.acessorio === "caixa" && estado !== "cafe") esq = dir = "nenhum";
  if (d.acessorio === "megafone" || d.acessorio === "lupa") dir = "alto";
  if (d.acessorio === "bone" && (andando || d.lanternaAlta) && estado !== "cafe") dir = "estendido";
  if (estado === "cafe") dir = f === 2 ? "alto" : "peito";
  const fb = estado === "trabalhando" && d.acessorio === "bloco" ? f % 2 : estado === "trabalhando" && d.acessorio === "lapis" ? 0 : 0;
  if (esq !== "nenhum") braco(g, d, -1, esq, u, fb);
  if (dir !== "nenhum") braco(g, d, 1, dir, u, estado === "trabalhando" && d.acessorio === "bloco" ? (f + 1) % 2 : 0);

  const piscando = estado === "parado" && f === 1;
  let boca = "fechada";
  if (abre) boca = "aberta";
  else if (estado === "trabalhando" && d.acessorio === "fone") boca = ["fechada", "aberta", "meia", "aberta"][f];
  else if (estado === "cafe") boca = f === 1 ? "aberta" : "sorriso";
  const vira = estado === "trabalhando" && d.acessorio === "fone" ? -1 : 0;
  cabeca(g, d, u, { olhos: piscando ? "fechados" : "abertos", boca, vira });
  cabeloFrente(g, d, u);
  acessorio(g, d, estado, f, u);

  if (estado === "cafe") {                                         // caneca na mão direita
    if (f === 2) { R(g, 22, 17 + u, 5, 6, "#f4f1ea"); R(g, 27, 18 + u, 1, 3, "#f4f1ea"); R(g, 22, 17 + u, 5, 1, "#6b4426"); }
    else {
      R(g, 17, 28 + u, 5, 6, "#f4f1ea"); R(g, 16, 29 + u, 1, 3, "#f4f1ea"); R(g, 17, 28 + u, 5, 1, "#6b4426"); R(g, 18, 31 + u, 3, 1, d.cor);
      P(g, 18, 26 + u - (f ? 1 : 0), "#d8dde6"); P(g, 20, 25 + u, "#d8dde6"); P(g, 19, 24 + u - (f ? 1 : 0), "#d8dde6");
    }
  }
  return g;
}

function contorna(g, cor) {
  const out = g.map(r => r.slice());
  for (let y = 0; y < SH; y++) for (let x = 0; x < SW; x++) {
    if (g[y][x]) continue;
    const viz = (g[y - 1] && g[y - 1][x]) || (g[y + 1] && g[y + 1][x]) || g[y][x - 1] || g[y][x + 1];
    if (viz) out[y][x] = cor;
  }
  return out;
}

function cinza(g) {
  return g.map(r => r.map(c => {
    if (!c) return c;
    const [r_, g_, b] = hx(c), l = .3 * r_ + .59 * g_ + .11 * b, v = 74 + l * .55;
    return rgb([v * .96, v * .98, v * 1.04]);
  }));
}

const cache = new Map();
// op.lanternaAlta: Vigia de ronda, com a lanterna para a frente.
export function sprite(id, estado = "parado", f = 0, abre = false, op = {}) {
  const n = QUADROS[estado] || 1;
  f = ((f % n) + n) % n;
  if (estado === "congelado") abre = false;
  const k = `${id}|${estado}|${f}|${abre ? 1 : 0}|${op.lanternaAlta ? 1 : 0}`;
  if (cache.has(k)) return cache.get(k);
  let g = estado === "congelado" ? cinza(monta(id, "parado", 0)) : monta(id, estado, f, abre, op);
  g = contorna(g, estado === "congelado" ? "#55545c" : CONTORNO);
  const cv = typeof OffscreenCanvas !== "undefined" ? new OffscreenCanvas(SW, SH) : Object.assign(document.createElement("canvas"), { width: SW, height: SH });
  const ctx = cv.getContext("2d");
  for (let y = 0; y < SH; y++) for (let x = 0; x < SW; x++) if (g[y][x]) { ctx.fillStyle = g[y][x]; ctx.fillRect(x, y, 1, 1); }
  cache.set(k, cv);
  return cv;
}

// Quadro da animação a partir do tempo (ms) — cada personagem tem seu ritmo.
export function quadroNoTempo(estado, t, semente = 0, id = null) {
  if (estado === "andando") return Math.floor(t / 140) % 4;
  if (estado === "trabalhando") return Math.floor((t + semente * 97) / ((PERSONAS[id] || {}).passo || 220)) % 4;
  if (estado === "cafe") { const c = Math.floor((t + semente * 331) / 900) % 6; return c === 5 ? 2 : 0; }
  if (estado === "parado") return ((t + semente * 613) % 3400) < 150 ? 1 : 0;
  return 0;
}
