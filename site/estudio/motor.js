// Motor de cena do CampsCast.
// Entra: o relógio (ms) e os dados de estudio/*.json. Sai: um "quadro" —
// quem está em que sala, fazendo o quê, com que balão, com que luz e que céu.
// Não toca no DOM nem desenha nada: a cena 2D, a 3D e, um dia, o CampsVerso
// leem o mesmo quadro. Nenhum balão é inventado: os da gravação são os
// eventos do JSON, com a origem deles; os de fora da gravação são a agenda e
// os números do dia, e dizem isso.

import { posto, POSTOS, rota, salaEm, PORTA, SALAS, SALA, RONDA, ANDARES } from "./planta.js";

export const FUSO = "America/Sao_Paulo";
const SEGURA = 90e3;      // um balão da gravação fica no ar até 90 s depois do evento (relógio da gravação)
const CICLO = 6500;       // fora da gravação, cada fala dura 6,5 s

export const VELOCIDADES = {
  real:      { nome: "Tempo real", k: 1,  min: 0,    max: Infinity },
  acelerado: { nome: "Acelerado",  k: 20, min: 1400, max: 4000 },
  rapido:    { nome: "Rápido",     k: 60, min: 550,  max: 1500 },
};

// ------------------------------------------------------------ relógio de São Paulo
const fmt = new Intl.DateTimeFormat("pt-BR", { timeZone: FUSO, year: "numeric", month: "2-digit", day: "2-digit",
  hour: "2-digit", minute: "2-digit", second: "2-digit", weekday: "short", hourCycle: "h23" });
export function campos(ms) {
  const p = Object.fromEntries(fmt.formatToParts(new Date(ms)).map(x => [x.type, x.value]));
  const h = +p.hour % 24, m = +p.minute, s = +p.second;
  return { data: `${p.year}-${p.month}-${p.day}`, h, m, s, min: h * 60 + m + s / 60, dia: p.weekday.replace(".", "") };
}
const dois = n => String(n).padStart(2, "0");
export const hhmmss = ms => { const c = campos(ms); return `${dois(c.h)}:${dois(c.m)}:${dois(c.s)}`; };
export const hhmm = ms => hhmmss(ms).slice(0, 5);
export const diaMes = iso => `${iso.slice(8, 10)}/${iso.slice(5, 7)}`;
export const semana = iso => new Intl.DateTimeFormat("pt-BR", { timeZone: "UTC", weekday: "long" }).format(new Date(iso + "T12:00:00Z"));
export const semanaCurta = iso => semana(iso).replace("-feira", "");
export const msDe = (iso, hm) => Date.parse(`${iso}T${hm.length === 5 ? hm + ":00" : hm}-03:00`);
const minDe = hm => +hm.slice(0, 2) * 60 + +hm.slice(3, 5);
const diaUtil = iso => { const d = new Date(iso + "T12:00:00Z").getUTCDay(); return d > 0 && d < 6; };
export function duracaoTexto(seg) {
  seg = Math.round(seg);
  const m = Math.floor(seg / 60), s = seg % 60;
  return m ? (s ? `${m} min ${s} s` : `${m} min`) : `${s} s`;
}
export const numero = n => Number(n).toLocaleString("pt-BR");

// ------------------------------------------------------------ céu da hora
// Pares (minuto do dia, cor do alto, cor do horizonte, estrelas, luz do dia).
const CEU = [
  [0,    "#0a0f2c", "#18214b", 1,   0],
  [270,  "#0c1236", "#3a2f66", 1,   0],
  [300,  "#1d2150", "#e0803f", .8,  .08],   // madrugada alaranjada
  [345,  "#36437f", "#ef9546", .3,  .3],
  [390,  "#6c9fd8", "#f5c38a", 0,   .75],
  [450,  "#5aa0e8", "#bfe1f8", 0,   1],
  [960,  "#4e95e0", "#c3e2f7", 0,   1],
  [1050, "#5b7cc4", "#f1b06a", 0,   .8],
  [1110, "#383d82", "#de6d58", .2,  .4],
  [1170, "#151946", "#3a2f66", .8,  .08],
  [1260, "#0a0f2c", "#18214b", 1,   0],
  [1440, "#0a0f2c", "#18214b", 1,   0],
];
const hex = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
const mix = (a, b, t) => a.map((v, i) => Math.round(v + (b[i] - v) * t));
export function ceu(min) {
  let i = 0;
  while (i < CEU.length - 2 && CEU[i + 1][0] <= min) i++;
  const a = CEU[i], b = CEU[i + 1], t = Math.max(0, Math.min(1, (min - a[0]) / (b[0] - a[0])));
  return {
    alto: mix(hex(a[1]), hex(b[1]), t), horizonte: mix(hex(a[2]), hex(b[2]), t),
    estrelas: a[3] + (b[3] - a[3]) * t, dia: a[4] + (b[4] - a[4]) * t, min,
    sol: min > 330 && min < 1140 ? (min - 330) / 810 : null,          // 0..1, da esquerda para a direita
    lua: min < 330 || min > 1140 ? ((min + 300) % 1440) / 630 : null,
  };
}

// ------------------------------------------------------------ o motor
export function criaMotor(elencoJson, dia) {
  const elenco = elencoJson.personagens;
  const porId = Object.fromEntries(elenco.map(p => [p.id, p]));
  const eventos = dia.eventos.map((e, i) => ({ ...e, i, ms: Date.parse(e.t) }));
  const INI = Date.parse(dia.execucao.inicio), FIM = Date.parse(dia.execucao.fim);
  const corrida = eventos.filter(e => e.ms <= FIM + 60e3);
  const capitulos = dia.capitulos.map(c => ({ ...c, ms: Date.parse(c.t) }));
  const equipe = elenco.filter(p => p.situacao !== "em_breve").map(p => p.id);
  const emBreve = elenco.filter(p => p.situacao === "em_breve").map(p => p.id);
  const doLocutor = corrida.filter(e => e.quem === "locutor");
  const narracao = doLocutor.length > 1 ? [doLocutor[0].ms, doLocutor[doLocutor.length - 1].ms] : null;
  const ag = dia.agenda, ep = dia.episodio;
  const GRAV = minDe(ag.gravacao), NOITE = minDe(ag.noite), VIGIA = minDe(ag.vigia);
  const ultimoProximo = ag.proximos[ag.proximos.length - 1] || dia.data;
  const nomeDe = id => (porId[id] || { nome: id }).nome;
  const salaDoEvento = e => (POSTOS.trabalho[e.quem] || {}).sala;

  function temEpisodio(iso) {
    if (iso === dia.data || ag.proximos.includes(iso)) return true;
    if (ag.folgas[iso]) return false;
    return iso > ultimoProximo && diaUtil(iso);     // além da agenda publicada, vale o dia útil
  }
  function periodo(ms) {
    const c = campos(ms), noite = c.min < GRAV || c.min >= NOITE;
    if (!temEpisodio(c.data)) return { nome: "folga", noite, c, motivo: ag.folgas[c.data] || semana(c.data) };
    if (noite) return { nome: "noite", noite, c };
    if (c.data === dia.data) return { nome: ms < FIM ? "gravando" : "dia", noite, c };
    if (c.data < dia.data) return { nome: "dia", noite, c, antigo: true };
    return { nome: c.min < 480 ? "gravando-sem-dados" : "atrasado", noite, c };
  }
  function proximaGravacao(c) {
    const cand = [dia.data, ...ag.proximos].filter(d => d > c.data || (d === c.data && c.min < GRAV));
    return cand[0] || null;
  }

  const balaoDe = (e, sala) => ({ chave: `e${e.i}`, sala, quem: e.quem, origem: e.origem, texto: e.texto,
    nota: e.nota || null, url: e.url || null, ms: e.ms, acao: e.acao, ok: e.ok });
  const fala = (quem, texto, origem, sala) => ({ chave: `${origem}:${quem}:${texto}`, sala, quem, origem, texto, ms: null });

  function luzes(modo) {
    const l = {};
    for (const s of SALAS) l[s.id] = s.ala ? "obra" : modo;
    return l;
  }

  // ---------------------------------------------------------- o quadro
  function quadro(ms, op = {}) {
    const per = op.replay ? { nome: op.fimReplay ? "dia" : "gravando", c: campos(ms), replay: true } : periodo(ms);
    const c = per.c;
    const q = { ms, per: per.nome, rotulo: "", replay: !!op.replay, min: c.min, ceu: ceu(c.min), pessoas: {}, baloes: [],
      onair: false, luz: {}, estado: "", placa: null, fita: [], fitaRotulo: "No estúdio agora", fitaNota: "", ativa: null };
    for (const id of emBreve) q.pessoas[id] = { ...posto(id, "trabalho"), estado: "congelado", situ: "em breve" };

    const prox = proximaGravacao(c);
    const proxLongo = prox ? `${semana(prox)}, ${diaMes(prox)}, às ${ag.gravacao}` : "";
    const proxCurto = prox ? `${semanaCurta(prox)}, ${diaMes(prox)}, às ${ag.gravacao}` : "";
    const ciclo = Math.floor(ms / CICLO);
    const vigiaNaPortaria = (estado = "parado", situ = "de plantão") => { q.pessoas.vigia = { ...posto("vigia", "trabalho"), estado, situ }; };
    const sug = op.sugestao;   // ms desde que o visitante enviou, ou null

    // ---- gravando (ao vivo com dados, ou replay)
    if (per.nome === "gravando") {
      q.rotulo = op.replay ? "REPLAY" : "GRAVANDO";
      q.luz = luzes("acesa");
      for (const id of equipe) q.pessoas[id] = { ...posto(id, "trabalho"), estado: "parado", situ: "aguardando" };
      let n = 0;
      while (n < corrida.length && corrida[n].ms <= ms) n++;
      const vistos = corrida.slice(0, n), ult = vistos[n - 1];
      const porSala = {};
      for (const e of vistos) { const s = salaDoEvento(e); if (s) porSala[s] = e; }
      for (const [sala, e] of Object.entries(porSala)) {
        if (e === ult || ms - e.ms < SEGURA) {
          q.baloes.push(balaoDe(e, sala));
          Object.assign(q.pessoas[e.quem], { estado: "trabalhando", situ: "trabalhando", fala: e.origem === "agente" });
        }
      }
      if (!ult) q.pessoas.produtor.situ = "chegando";
      q.ativa = ult ? salaDoEvento(ult) : "tecnica";
      q.onair = !!narracao && ms >= narracao[0] && ms < narracao[1];
      q.fita = vistos.slice(-8).reverse().map(e => balaoDe(e, salaDoEvento(e)));
      q.fitaRotulo = op.replay ? "Na gravação" : "Gravando agora";
      q.estado = op.replay ? `Replay da gravação de ${diaMes(dia.data)}. Não é ao vivo.` : "Gravando agora.";
      if (sug != null && !op.replay && sug < 12e3) {
        q.baloes = q.baloes.filter(b => b.sala !== "portaria");
        q.baloes.push(fala("vigia", "Chegou uma sugestão de tema pelo site. Fica com o Produtor até o fim da gravação.", "visitante", "portaria"));
      }
      return q;
    }

    // ---- dia: equipe no café, vigia na portaria
    if (per.nome === "dia") {
      q.rotulo = op.replay ? "REPLAY" : "DIA";
      q.luz = luzes("penumbra"); q.luz.cafe = "acesa"; q.luz.portaria = "acesa";
      vigiaNaPortaria();
      for (const id of equipe) if (POSTOS.cafe[id]) q.pessoas[id] = { ...posto(id, "cafe"), estado: "cafe", situ: "no café" };
      q.ativa = "cafe";
      const conv = dia.conversa.filter(e => q.pessoas[e.quem]);
      if (conv.length) {
        const e = conv[ciclo % conv.length];
        q.baloes.push(fala(e.quem, e.texto, e.origem, "cafe"));
        q.pessoas[e.quem].fala = true;
        q.fita = conv.map(x => ({ ...fala(x.quem, x.texto, x.origem, "cafe"), atual: x === e }));
      }
      q.fitaRotulo = "Conversa no café";
      q.fitaNota = `Conversa montada com os números da gravação de ${diaMes(dia.data)}.`;
      if (!op.replay && c.min >= VIGIA && c.min < VIGIA + 10 && c.data === dia.data) {
        q.baloes.push(fala("vigia", `${ag.vigia}: hora de conferir se o episódio de hoje está no ar.`, "agenda", "portaria"));
        q.pessoas.vigia.estado = "trabalhando"; q.pessoas.vigia.situ = "conferindo";
      } else {
        q.baloes.push(fala("vigia", `No ar desde as ${hhmm(FIM)}: episódio ${ep.numero}.`, "numeros", "portaria"));
      }
      q.estado = op.replay ? "Fim do replay. A equipe vai para o café." : `Episódio ${ep.numero} no ar desde as ${hhmm(FIM)}. A equipe está no café.`;
      if (per.antigo) q.estado = `Último episódio: ${ep.numero}, de ${diaMes(dia.data)}.`;
      if (sug != null && !op.replay && sug < 12e3) {
        q.baloes = q.baloes.filter(b => b.sala !== "cafe");
        const primeiro = sug < 5e3;
        q.baloes.push(primeiro ? fala("produtor", "Chegou uma sugestão de tema pelo site. Levo ao Editor.", "visitante", "cafe")
                               : fala("editor", "Recebi a sugestão. Vou avaliar.", "visitante", "cafe"));
        for (const id of ["produtor", "editor"]) if (q.pessoas[id]) q.pessoas[id].fala = false;
        q.pessoas[primeiro ? "produtor" : "editor"].fala = true;
      }
      return q;
    }

    // ---- gravando sem dados (ao vivo, antes de o replay sair)
    if (per.nome === "gravando-sem-dados") {
      q.rotulo = "GRAVANDO";
      q.luz = luzes("acesa");
      for (const id of equipe) q.pessoas[id] = { ...posto(id, "trabalho"), estado: "trabalhando", situ: "trabalhando" };
      q.baloes.push(fala("vigia", "Gravando agora. Os detalhes aparecem quando o episódio sair.", "agenda", "portaria"));
      q.estado = "Gravando agora. O replay sai junto com o episódio.";
      q.ativa = "redacao";
      return q;
    }

    // ---- atrasado: dia útil, depois das 08:00, sem episódio
    if (per.nome === "atrasado") {
      q.rotulo = "ATRASADO";
      q.luz = luzes("penumbra"); q.luz.portaria = "acesa";
      vigiaNaPortaria("trabalhando", "de olho");
      const t = `A gravação de hoje ainda não chegou ao site. A última é de ${diaMes(dia.data)}.`;
      q.baloes.push(fala("vigia", t, "agenda", "portaria"));
      q.fita = [fala("vigia", t, "agenda", "portaria")];
      q.fitaRotulo = "Na portaria";
      q.estado = "A gravação de hoje ainda não chegou.";
      q.ativa = "portaria";
      return q;
    }

    // ---- noite e folga: só o vigia
    const folga = per.nome === "folga";
    q.rotulo = folga ? "FOLGA" : "NOITE";
    q.luz = luzes(per.noite ? "apagada" : "penumbra"); q.luz.portaria = "acesa";
    vigiaNaPortaria();
    // de noite, o Vigia faz a ronda de lanterna: portaria → café → técnica → café → portaria
    let naRonda = false;
    if (per.noite && !(sug != null && sug < 12e3)) {
      const fase = (ms / 1000) % 64;
      const parada = fase < 36 ? null : fase < 46 ? RONDA[0] : fase < 54 ? RONDA[1] : fase < 60 ? RONDA[2] : null;
      if (parada) { naRonda = true; Object.assign(q.pessoas.vigia, { sala: parada.sala, x: parada.x, y: ANDARES[SALA[parada.sala].andar].pe, situ: "de ronda" }); }
    }
    q.ativa = "portaria";
    let falas = folga
      ? [fala("vigia", `Hoje é ${per.motivo}: não tem episódio.`, "agenda", "portaria"),
         fala("vigia", `A equipe volta ${proxCurto}.`, "agenda", "portaria"),
         fala("vigia", `No ar: episódio ${ep.numero}, de ${diaMes(dia.data)}.`, "numeros", "portaria")]
      : [fala("vigia", "Tudo quieto no estúdio.", "agenda", "portaria"),
         fala("vigia", `Próxima gravação: ${proxLongo}.`, "agenda", "portaria"),
         fala("vigia", `No ar: episódio ${ep.numero}, de ${diaMes(dia.data)}.`, "numeros", "portaria")];
    if (ms < INI) falas.pop();          // antes da gravação destes dados, o episódio deles ainda não existe
    const atual = falas[ciclo % falas.length];
    if (!naRonda) q.baloes.push(atual);
    q.fita = falas.map(f => ({ ...f, atual: f === atual }));
    q.fitaRotulo = "Na portaria";
    q.estado = folga ? `Folga: ${per.motivo}. A equipe volta ${proxCurto}.` : `Estúdio fechado. Próxima gravação: ${proxLongo}.`;
    if (folga && prox) q.placa = `A equipe volta ${proxCurto}`;
    if (sug != null && sug < 12e3) {
      q.baloes = [fala("vigia", "Chegou uma sugestão de tema pelo site. Guardo para o Produtor.", "visitante", "portaria")];
    }
    if (per.noite) q.pessoas.vigia.lanterna = true;
    return q;
  }

  return { elenco, porId, dia, eventos, corrida, capitulos, INI, FIM, equipe, emBreve, nomeDe, salaDoEvento,
    periodo, proximaGravacao, quadro };
}

// ------------------------------------------------------------ replay
// Anda pela gravação evento a evento. O relógio mostra sempre o horário real;
// as velocidades encurtam as esperas, nunca mudam a ordem.
export class Replay {
  constructor(motor, vel = "acelerado") {
    this.c = motor.corrida; this.INI = motor.INI; this.FIM = motor.FIM;
    this.i = 0; this.p = 0; this.vel = vel; this.pausado = false; this.parado = 0;
  }
  passo(i, vel = this.vel) {
    const a = this.c[i], b = this.c[i + 1];
    if (!b) return Infinity;
    const gap = b.ms - a.ms, v = VELOCIDADES[vel];
    return vel === "real" ? gap : Math.max(v.min, Math.min(v.max, gap / v.k));
  }
  get fim() { return this.i >= this.c.length - 1; }
  avanca(dt) {
    if (this.pausado) return;
    if (this.fim) { this.parado += dt; return; }
    while (dt > 0 && !this.fim) {
      const d = this.passo(this.i), resta = (1 - this.p) * d;
      if (dt < resta) { this.p += dt / d; dt = 0; } else { dt -= resta; this.i++; this.p = 0; }
    }
  }
  ms() {
    const a = this.c[this.i], b = this.c[this.i + 1];
    return b ? a.ms + (b.ms - a.ms) * this.p : a.ms;
  }
  irPara(ms) {
    let i = 0;
    while (i < this.c.length - 1 && this.c[i + 1].ms <= ms) i++;
    const a = this.c[i], b = this.c[i + 1];
    this.i = i; this.p = b && b.ms > a.ms ? Math.max(0, Math.min(.999, (ms - a.ms) / (b.ms - a.ms))) : 0;
    this.parado = 0;
  }
  recomeca() { this.i = 0; this.p = 0; this.parado = 0; this.pausado = false; }
  duracao(vel) { let s = 0; for (let i = 0; i < this.c.length - 1; i++) s += this.passo(i, vel); return s; }
  progresso() { return (this.ms() - this.INI) / Math.max(1, this.FIM - this.INI); }
}

// ------------------------------------------------------------ locomoção
// Quem anda de um posto para outro. Fica fora das cenas para que a troca
// 2D ↔ 3D não perca ninguém no meio do caminho.
export class Locomocao {
  constructor() { this.p = {}; this.vel = 62; }   // px da cena por segundo
  define(pessoas, instantaneo = false) {
    const ids = new Set([...Object.keys(this.p), ...Object.keys(pessoas)]);
    for (const id of ids) {
      const alvo = pessoas[id];
      let s = this.p[id];
      if (!alvo) {
        if (!s || s.saindo) continue;
        if (instantaneo) { delete this.p[id]; continue; }
        s.saindo = true; s.chave = "porta"; s.rota = rota(s, PORTA); s.info = { ...s.info, fala: false };
        continue;
      }
      const chave = `${alvo.sala}:${alvo.x}:${alvo.y}`;
      if (!s) {
        s = this.p[id] = { id, x: instantaneo ? alvo.x : PORTA.x, y: instantaneo ? alvo.y : PORTA.y, dir: 1, rota: [],
          chave: null, opacidade: instantaneo ? 1 : 0, tempo: 0 };
      }
      s.saindo = false; s.info = alvo;
      if (s.chave !== chave) {
        s.chave = chave;
        if (instantaneo) { s.x = alvo.x; s.y = alvo.y; s.rota = []; }
        else s.rota = rota(s, alvo);
      }
    }
  }
  atualiza(dt) {
    for (const [id, s] of Object.entries(this.p)) {
      let passo = this.vel * dt / 1000;
      while (passo > 0 && s.rota.length) {
        const a = s.rota[0], dx = a.x - s.x, dy = a.y - s.y, d = Math.hypot(dx, dy);
        if (Math.abs(dx) > .01) s.dir = Math.sign(dx);
        if (d <= passo) { s.x = a.x; s.y = a.y; s.rota.shift(); passo -= d; }
        else { s.x += dx / d * passo; s.y += dy / d * passo; passo = 0; }
      }
      s.andando = s.rota.length > 0;
      s.tempo += dt;
      s.opacidade = s.saindo && s.rota.length < 2 ? Math.max(0, s.opacidade - dt / 500) : Math.min(1, s.opacidade + dt / 400);
      s.sala = salaEm(s.x, s.y);
      if (s.saindo && !s.andando) delete this.p[id];
    }
  }
  // Ordem de desenho: de trás para a frente.
  ordem() { return Object.values(this.p).sort((a, b) => a.y - b.y || a.x - b.x); }
}

export { SALA };
