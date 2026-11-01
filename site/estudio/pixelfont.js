// Fonte de pixel 5×7 para as placas da cena (maiúsculas, números e acentos
// do português). Desenhada em código, sem arquivo de fonte.

const G = {
  A: [14, 17, 17, 31, 17, 17, 17], B: [30, 17, 17, 30, 17, 17, 30], C: [14, 17, 16, 16, 16, 17, 14],
  D: [30, 17, 17, 17, 17, 17, 30], E: [31, 16, 16, 30, 16, 16, 31], F: [31, 16, 16, 30, 16, 16, 16],
  G: [14, 17, 16, 23, 17, 17, 15], H: [17, 17, 17, 31, 17, 17, 17], I: [14, 4, 4, 4, 4, 4, 14],
  J: [7, 2, 2, 2, 2, 18, 12], K: [17, 18, 20, 24, 20, 18, 17], L: [16, 16, 16, 16, 16, 16, 31],
  M: [17, 27, 21, 21, 17, 17, 17], N: [17, 17, 25, 21, 19, 17, 17], O: [14, 17, 17, 17, 17, 17, 14],
  P: [30, 17, 17, 30, 16, 16, 16], Q: [14, 17, 17, 17, 21, 18, 13], R: [30, 17, 17, 30, 20, 18, 17],
  S: [15, 16, 16, 14, 1, 1, 30], T: [31, 4, 4, 4, 4, 4, 4], U: [17, 17, 17, 17, 17, 17, 14],
  V: [17, 17, 17, 17, 17, 10, 4], W: [17, 17, 17, 21, 21, 21, 10], X: [17, 17, 10, 4, 10, 17, 17],
  Y: [17, 17, 10, 4, 4, 4, 4], Z: [31, 1, 2, 4, 8, 16, 31],
  0: [14, 17, 19, 21, 25, 17, 14], 1: [4, 12, 4, 4, 4, 4, 14], 2: [14, 17, 1, 2, 4, 8, 31],
  3: [31, 2, 4, 2, 1, 17, 14], 4: [2, 6, 10, 18, 31, 2, 2], 5: [31, 16, 30, 1, 1, 17, 14],
  6: [6, 8, 16, 30, 17, 17, 14], 7: [31, 1, 2, 4, 8, 8, 8], 8: [14, 17, 17, 14, 17, 17, 14],
  9: [14, 17, 17, 15, 1, 2, 12],
  ":": [0, 6, 6, 0, 6, 6, 0], ".": [0, 0, 0, 0, 0, 6, 6], ",": [0, 0, 0, 0, 6, 2, 4],
  "/": [1, 1, 2, 4, 8, 16, 16], "-": [0, 0, 0, 14, 0, 0, 0], "·": [0, 0, 0, 6, 6, 0, 0],
  ">": [16, 8, 4, 2, 4, 8, 16], "!": [4, 4, 4, 4, 4, 0, 4], "_": [0, 0, 0, 0, 0, 0, 31],
  "?": [14, 17, 1, 2, 4, 0, 4], "&": [12, 18, 20, 8, 21, 18, 13], " ": [0, 0, 0, 0, 0, 0, 0],
};
const ACENTO = { agudo: [2, 4], grave: [8, 4], til: [13, 22], circ: [4, 10] };
const COMPOSTOS = { "Á": ["A", "agudo"], "À": ["A", "grave"], "Ã": ["A", "til"], "Â": ["A", "circ"], "É": ["E", "agudo"],
  "Ê": ["E", "circ"], "Í": ["I", "agudo"], "Ó": ["O", "agudo"], "Ô": ["O", "circ"], "Õ": ["O", "til"], "Ú": ["U", "agudo"] };

export const ALTURA = 7, AVANCO = 6;
const larg = ch => (ch === " " ? 3 : ch === ":" || ch === "." || ch === "," || ch === "·" || ch === "!" ? 4 : AVANCO);

export function medeTexto(txt) {
  let w = 0;
  for (const ch of txt.toUpperCase()) w += larg(ch);
  return Math.max(0, w - 1);
}

// Desenha em (x, y) = canto de cima à esquerda do corpo das letras.
export function escreve(ctx, txt, x, y, cor, s = 1) {
  ctx.fillStyle = cor;
  let cx = Math.round(x);
  for (const ch0 of txt.toUpperCase()) {
    let ch = ch0, ac = null, ced = false;
    if (COMPOSTOS[ch]) [ch, ac] = COMPOSTOS[ch];
    if (ch === "Ç") { ch = "C"; ced = true; }
    const g = G[ch] || G["?"];
    const off = ch === ":" || ch === "." || ch === "," || ch === "·" || ch === "!" ? -1 : 0;
    for (let r = 0; r < 7; r++) for (let b = 0; b < 5; b++) if (g[r] & (16 >> b)) ctx.fillRect(cx + (b + off) * s, y + r * s, s, s);
    if (ac) { const a = ACENTO[ac]; for (let r = 0; r < 2; r++) for (let b = 0; b < 5; b++) if (a[r] & (16 >> b)) ctx.fillRect(cx + b * s, y + (r - 3) * s, s, s); }
    if (ced) { ctx.fillRect(cx + 2 * s, y + 7 * s, s, s); ctx.fillRect(cx + 1 * s, y + 8 * s, s, s); }
    cx += larg(ch0 === ch ? ch : ch0) * s;
  }
  return cx - x;
}

// Placa: fundo, borda de 1 px e texto centralizado.
export function placa(ctx, txt, cx, y, { fundo = "#1d1b26", texto = "#efe9dc", borda = null, pad = 3 } = {}) {
  const w = medeTexto(txt) + pad * 2, h = ALTURA + pad * 2 + (/[ÁÀÃÂÉÊÍÓÔÕÚ]/i.test(txt) ? 2 : 0);
  const x = Math.round(cx - w / 2);
  if (borda) { ctx.fillStyle = borda; ctx.fillRect(x - 1, y - 1, w + 2, h + 2); }
  ctx.fillStyle = fundo; ctx.fillRect(x, y, w, h);
  escreve(ctx, txt, x + pad, y + h - pad - ALTURA, texto);
  return { x, y, w, h };
}
