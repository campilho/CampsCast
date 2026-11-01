// Planta do estúdio, em pixels da cena 2D (640 × 360).
// É a fonte única do espaço: a cena 2D desenha a partir dela, a 3D monta os
// volumes a partir dela, e o motor usa os postos e as rotas. Nada aqui é dado
// da gravação; dados vêm só de estudio/*.json.

export const W = 640, H = 360;

// Dois andares. "teto" e "base" limitam a sala; "pe" é a linha dos pés.
export const ANDARES = {
  1: { teto: 24, chao: 156, pe: 166, base: 172 },   // superior
  0: { teto: 180, chao: 312, pe: 322, base: 328 },  // térreo
};

// Salas: retângulos internos. "ala" agrupa a ala nova (em obras).
export const SALAS = [
  { id: "escada",   nome: "Escada",               andar: -1, x0: 4,   x1: 52  },
  { id: "redacao",  nome: "Redação",              andar: 1,  x0: 56,  x1: 332 },
  { id: "cabine",   nome: "Cabine",               andar: 1,  x0: 336, x1: 444 },
  { id: "arquivo",  nome: "Arquivo",              andar: 1,  x0: 448, x1: 552 },
  { id: "checagem", nome: "Checagem e Compliance", andar: 1, x0: 556, x1: 636, ala: "obras" },
  { id: "portaria", nome: "Portaria",             andar: 0,  x0: 56,  x1: 160 },
  { id: "cafe",     nome: "Café",                 andar: 0,  x0: 164, x1: 412 },
  { id: "tecnica",  nome: "Técnica",              andar: 0,  x0: 416, x1: 552 },
  { id: "obras",    nome: "Ala nova · em obras",  andar: 0,  x0: 556, x1: 636, ala: "obras" },
];
export const SALA = Object.fromEntries(SALAS.map(s => [s.id, s]));

export function retSala(id) {
  const s = SALA[id];
  if (s.andar === -1) return { x: s.x0, y: ANDARES[1].teto, w: s.x1 - s.x0, h: ANDARES[0].base - ANDARES[1].teto };
  const a = ANDARES[s.andar];
  return { x: s.x0, y: a.teto, w: s.x1 - s.x0, h: a.base - a.teto };
}

// Ordem das paradas da câmera no celular (deslizar entre salas).
export const PARADAS = ["portaria", "cafe", "tecnica", "redacao", "cabine", "arquivo", "checagem", "obras"];

// Postos de cada personagem. "trabalho" = durante a gravação (e, para quem
// está em obras, sempre). "cafe" = depois da gravação.
export const POSTOS = {
  trabalho: {
    jornalista: { sala: "redacao", x: 110 },
    editor:     { sala: "redacao", x: 196 },
    roteirista: { sala: "redacao", x: 282 },
    locutor:    { sala: "cabine",  x: 400 },
    arquivista: { sala: "arquivo", x: 506 },
    vigia:      { sala: "portaria", x: 128 },
    produtor:   { sala: "tecnica", x: 446 },
    checador:   { sala: "checagem", x: 598 },
    artista:    { sala: "obras",   x: 578 },
    marketing:  { sala: "obras",   x: 616 },
  },
  cafe: {
    arquivista: { sala: "cafe", x: 202 },
    produtor:   { sala: "cafe", x: 234 },
    editor:     { sala: "cafe", x: 268, fundo: true },
    locutor:    { sala: "cafe", x: 302, fundo: true },
    jornalista: { sala: "cafe", x: 336 },
    roteirista: { sala: "cafe", x: 368 },
  },
};

// Ronda do Vigia à noite: da portaria ao café, à técnica e de volta.
export const RONDA = [{ sala: "cafe", x: 292 }, { sala: "tecnica", x: 486 }, { sala: "cafe", x: 226 }];

export function posto(id, tipo) {
  const p = POSTOS[tipo][id];
  if (!p) return null;
  const a = ANDARES[SALA[p.sala].andar];
  return { sala: p.sala, x: p.x, y: a.pe - (p.fundo ? 6 : 0), fundo: !!p.fundo };
}

// Porta da rua (na escada, no térreo) e a escada em dois lances.
export const PORTA = { x: 18, y: ANDARES[0].pe };
const ESC_CIMA = { x: 44, y: ANDARES[1].pe }, ESC_MEIO = { x: 12, y: 244 }, ESC_BAIXO = { x: 44, y: ANDARES[0].pe };

export const andarDe = y => (y <= ANDARES[1].base ? 1 : y >= ANDARES[0].chao ? 0 : -1);

// Rota a pé entre dois pontos: no mesmo andar, em linha reta; senão, pela escada.
export function rota(de, para) {
  const a = andarDe(de.y), b = andarDe(para.y), fim = { x: para.x, y: para.y };
  if (a === b && a !== -1) return [fim];
  if (a === 1) return [ESC_CIMA, ESC_MEIO, ESC_BAIXO, fim];
  if (a === 0) return [ESC_BAIXO, ESC_MEIO, ESC_CIMA, fim];
  return b === 1 ? [ESC_MEIO, ESC_CIMA, fim] : [ESC_MEIO, ESC_BAIXO, fim];  // no meio da escada
}
export const ESCADA = { cima: ESC_CIMA, meio: ESC_MEIO, baixo: ESC_BAIXO };

// Em que sala está um ponto.
export function salaEm(x, y) {
  if (x < 52) return "escada";
  const andar = y <= ANDARES[1].base ? 1 : 0;
  const s = SALAS.find(s => s.andar === andar && x >= s.x0 && x <= s.x1);
  return s ? s.id : null;
}

// Móveis principais, para a 2D e a 3D desenharem no mesmo lugar.
export const MOVEIS = [
  { tipo: "mesa", sala: "redacao", x: 110, w: 52, de: "jornalista" },
  { tipo: "mesa", sala: "redacao", x: 196, w: 52, de: "editor" },
  { tipo: "mesa", sala: "redacao", x: 282, w: 52, de: "roteirista" },
  { tipo: "quadro", sala: "redacao", x: 158, w: 56 },
  { tipo: "janela", sala: "redacao", x: 82, w: 34 },
  { tipo: "janela", sala: "redacao", x: 238, w: 34 },
  { tipo: "mic", sala: "cabine", x: 374 },
  { tipo: "mesa", sala: "cabine", x: 400, w: 64, de: "locutor" },
  { tipo: "onair", sala: "cabine", x: 412, w: 40 },
  { tipo: "estante", sala: "arquivo", x: 500, w: 92 },
  { tipo: "balcao", sala: "portaria", x: 132, w: 44 },
  { tipo: "crt", sala: "portaria", x: 82 },
  { tipo: "janela", sala: "portaria", x: 134, w: 26 },
  { tipo: "bancada", sala: "cafe", x: 196, w: 56 },
  { tipo: "mesa-redonda", sala: "cafe", x: 285, w: 52 },
  { tipo: "janela", sala: "cafe", x: 338, w: 40 },
  { tipo: "mesa", sala: "tecnica", x: 446, w: 56, de: "produtor" },
  { tipo: "rack", sala: "tecnica", x: 512, w: 20 },
  { tipo: "rack", sala: "tecnica", x: 534, w: 20 },
  { tipo: "vidro", sala: "checagem", x: 598, w: 66 },
];
