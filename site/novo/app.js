// O site do CampsCast: liga os dados ao motor de cena, o motor à cena (2D ou
// 3D) e a cena à página. Tudo o que aparece sai de estudio/elenco.json e
// estudio/ultimo.json; aqui não há número escrito à mão.

import { criaMotor, Replay, Locomocao, VELOCIDADES, campos, hhmm, hhmmss, diaMes, semana, semanaCurta, msDe, duracaoTexto, numero } from "./motor.js";
import { Cena2D } from "./cena2d.js";
import { W, H, SALA, SALAS, retSala, PARADAS } from "./planta.js";
import { sprite } from "./sprites.js";

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const cor = id => `var(--c-${id})`;
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const reduz = matchMedia("(prefers-reduced-motion: reduce)");
const grosso = matchMedia("(pointer: coarse)");
const URLP = new URLSearchParams(location.search);

const ORIGEM = { agente: "frase do agente", ferramenta: "ferramenta", log: "log", sistema: "sistema", numeros: "números do dia", agenda: "agenda", visitante: "reação do site" };
const ONDE = { redacao: "na redação", cabine: "na cabine", arquivo: "no arquivo", checagem: "na sala de vidro, em obras", portaria: "na portaria",
  cafe: "no café", tecnica: "na técnica", obras: "na ala nova, em obras", escada: "na escada" };
const SITU = { ativo: "ativo", em_parte: "em parte", em_breve: "em breve" };
const DESC = {
  NOITE: "Salas apagadas. Só o Vigia, na portaria, com o monitor aceso.",
  GRAVANDO: "Cada um no seu posto. Quem está trabalhando tem balão.",
  DIA: "A equipe no café, conversando com os números do dia. O Vigia na portaria.",
  FOLGA: "Dia sem episódio. Só o Vigia, na portaria.",
  ATRASADO: "Dia útil, depois das 08:00, e o episódio ainda não chegou.",
  REPLAY: "Não é ao vivo. O relógio mostra o horário real de cada evento.",
};
const ICONE = {
  play: '<svg class="icone" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2.5v11l9-5.5z" fill="currentColor"/></svg>',
  pausa: '<svg class="icone" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2.5h3v11H4zM9 2.5h3v11H9z" fill="currentColor"/></svg>',
  rever: '<svg class="icone" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8a5 5 0 1 0 1.5-3.6M3 2.5v2.8h2.8" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  fechar: '<svg class="icone" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
};

const S = { M: null, loc: new Locomocao(), cena: null, c2d: null, c3d: null, replay: null, sim: null, sug: null,
  ficha: null, aba: null, volta: null, seguir: true, salaFoco: "portaria", salaCam: null, pausaSeguir: 0,
  med: null, saltar: true, ult: 0, q: null, assin: {}, anunciado: 0 };
const palco = $("#palco"), camada = $("#camada"), moldura = $("#moldura"), registro = $("#registro"), lista = $("#registro-lista"), hud = $("#hud");
const CORTE = 90;    // balão com mais que isso é cortado com "…"; o texto inteiro fica no registro e na ficha

// ------------------------------------------------------------ relógio
const agoraMs = () => (S.sim ? S.sim.base + (performance.now() - S.sim.desde) : Date.now());

// ------------------------------------------------------------ medidas do palco
// Inteiro de pixel do aparelho sempre que der; no celular, a câmera mostra
// uma sala por vez.
function medidas() {
  const dpr = clamp(window.devicePixelRatio || 1, 1, 3);
  const larg = moldura.clientWidth;
  if (larg >= 720) {
    let k = Math.max(1, Math.floor(larg * dpr / W));
    if (k * W / dpr < larg * .8) k = larg * dpr / W;             // tela estreita em dpr 1: escala fracionária
    return { modo: "inteiro", k, dpr, cssW: Math.round(W * k / dpr), cssH: Math.round(H * k / dpr) };
  }
  const k = Math.max(2, Math.round(larg * dpr / 200));
  const cssH = Math.round(Math.min(innerHeight * .62, 170 * k / dpr));
  return { modo: "sala", k, dpr, cssW: larg, cssH };
}
function aplicaMedidas() {
  S.med = medidas();
  palco.style.width = S.med.cssW + "px"; palco.style.height = S.med.cssH + "px";
  S.c2d.medidas(S.med);
  if (S.c3d) S.c3d.medidas(S.med);
  for (const it of BAL.values()) it.medir = true;
  $("#sala-atual").hidden = S.med.modo === "inteiro";
  posicionaBotoesMinimapa();
  ajustaRegistro();
}
// No computador o registro fica ao lado da cena, da mesma altura; no celular, embaixo.
function ajustaRegistro() {
  const lado = getComputedStyle($(".estudio-grade")).gridTemplateColumns.split(" ").length > 1;
  registro.style.height = lado ? (S.med.cssH + hud.offsetHeight + 8) + "px" : "";
}

// ------------------------------------------------------------ carga
async function carrega() {
  const [el, dia] = await Promise.all([
    fetch("estudio/elenco.json").then(r => { if (!r.ok) throw new Error("elenco.json " + r.status); return r.json(); }),
    fetch("estudio/ultimo.json").then(r => { if (!r.ok) throw new Error("ultimo.json " + r.status); return r.json(); }),
  ]);
  S.M = criaMotor(el, dia);
  S.c2d = new Cena2D(palco); S.cena = S.c2d;
  S.c2d.configura({ pautas: dia.episodio.pautas, data: dia.data });
  montaEpisodio(); montaReplay(); criaBotoes(); criaAlvos(); montaMinimapa();
  $("#proto-dados").textContent = `dados reais da gravação de ${semana(dia.data)}, ${diaMes(dia.data)}.`;
  aplicaMedidas();
  parametros();
  requestAnimationFrame(laco);
}

function parametros() {
  const sim = URLP.get("sim");
  if (sim) simula(sim);
  if (URLP.get("tema")) tema(URLP.get("tema") === "escuro" ? "dark" : URLP.get("tema") === "claro" ? "light" : URLP.get("tema"));
  if (URLP.has("replay")) {
    abreReplay(URLP.get("vel") || "acelerado", false);
    if (URLP.get("em")) S.replay.irPara(msDe(S.M.dia.data, URLP.get("em")));
    if (URLP.has("pausa")) S.replay.pausado = true;
  }
  if (URLP.get("ficha") && S.M.porId[URLP.get("ficha")]) setTimeout(() => abreFicha(URLP.get("ficha"), URLP.get("aba")), 60);
  if (URLP.get("vista") === "3d") ver3d();
}

// ------------------------------------------------------------ laço
function laco(t) {
  requestAnimationFrame(laco);
  if (document.hidden) return;
  const passou = t - S.ult;
  if (grosso.matches && passou < 1000 / 31) return;              // 30 quadros por segundo no celular
  S.ult = t;
  const dt = clamp(passou, 0, 100);
  if (S.replay) S.replay.avanca(dt);
  const ms = S.replay ? S.replay.ms() : agoraMs();
  const fimReplay = !!S.replay && S.replay.fim && S.replay.parado > 2600;
  const q = S.M.quadro(ms, { replay: !!S.replay, fimReplay, sugestao: S.sug != null ? t - S.sug : null });
  S.q = q;
  const salto = S.saltar || reduz.matches;
  S.loc.define(q.pessoas, salto);
  S.loc.atualiza(salto ? 0 : dt);
  camera(q, salto);
  S.saltar = false;
  S.cena.desenha({ q, pessoas: S.loc.ordem(), t, ms, dt, semMovimento: reduz.matches });
  atualizaCamada(q);
  textos(q, ms, t);
  if (S.med.modo !== "inteiro") desenhaMinimapa(q);
}
document.addEventListener("visibilitychange", () => { S.ult = performance.now(); });

// ------------------------------------------------------------ câmera (celular)
function camera(q, salto) {
  if (S.med.modo === "inteiro") { if (S.cena.tipo === "3d") S.cena.segue(null); return; }
  if (!S.seguir && performance.now() > S.pausaSeguir) S.seguir = true;
  const sala = S.seguir ? (q.ativa || "portaria") : S.salaFoco;
  if (sala !== S.salaCam) { S.salaCam = sala; $("#sala-nome").textContent = SALA[sala].nome; }
  $("#btn-seguir").hidden = S.seguir;
  const r = retSala(sala);
  let x = r.x + r.w / 2;
  const b = q.baloes.find(b => b.sala === sala), p = b && S.loc.p[b.quem];
  if (p && !arrasto) x = p.x;
  if (!arrasto) S.cena.segue(x, r.y + r.h / 2 + 2, salto);
}
function irSala(delta) {
  const i = PARADAS.indexOf(S.salaCam), n = PARADAS.length;
  S.salaFoco = PARADAS[((i < 0 ? 0 : i) + delta + n) % n];
  S.seguir = false; S.pausaSeguir = performance.now() + 25e3;
}
function vaiSala(id) { S.salaFoco = id; S.seguir = false; S.pausaSeguir = performance.now() + 25e3; }
let arrasto = null;
palco.addEventListener("pointerdown", e => {
  if (S.med.modo === "inteiro") return;
  arrasto = { x: e.clientX, y: e.clientY, cam: S.cena.tipo === "2d" ? S.c2d.cam.x : 0, ativo: false, id: e.pointerId };
});
palco.addEventListener("pointermove", e => {
  if (!arrasto || e.pointerId !== arrasto.id) return;
  const dx = e.clientX - arrasto.x, dy = e.clientY - arrasto.y;
  if (!arrasto.ativo && Math.abs(dx) > 12 && Math.abs(dx) > Math.abs(dy)) { arrasto.ativo = true; palco.setPointerCapture(e.pointerId); }
  if (arrasto.ativo && S.cena.tipo === "2d") { S.c2d.cam.alvoX = S.c2d.cam.x = arrasto.cam - dx / S.c2d.escala(); }
});
const soltar = e => {
  if (!arrasto) return;
  const dx = e.clientX - arrasto.x, ativo = arrasto.ativo;
  arrasto = null;
  if (ativo && Math.abs(dx) > 40) irSala(dx < 0 ? 1 : -1);
};
palco.addEventListener("pointerup", soltar);
palco.addEventListener("pointercancel", () => { arrasto = null; });
$("#sala-ant").addEventListener("click", () => irSala(-1));
$("#sala-prox").addEventListener("click", () => irSala(1));
$("#btn-seguir").addEventListener("click", () => { S.seguir = true; });

// ------------------------------------------------------------ minimapa
const mini = $("#minimapa-canvas"), miniCaixa = $("#minimapa");
const Y0 = 16, Y1 = 334;      // faixa do prédio
function miniEscala() {
  const w = mini.width, h = mini.height, s = Math.min(w / W, h / (Y1 - Y0));
  return { s, ox: (w - W * s) / 2, oy: (h - (Y1 - Y0) * s) / 2 };
}
function montaMinimapa() {
  for (const id of PARADAS) {
    const b = document.createElement("button");
    b.type = "button"; b.dataset.sala = id; b.setAttribute("aria-label", `Ver ${SALA[id].nome}`);
    b.addEventListener("click", () => vaiSala(id));
    miniCaixa.append(b);
  }
}
function posicionaBotoesMinimapa() {
  const r = miniCaixa.getBoundingClientRect(), dpr = clamp(devicePixelRatio || 1, 1, 3);
  if (!r.width) return;
  mini.width = Math.round(r.width * dpr); mini.height = Math.round(r.height * dpr);
  const { s, ox, oy } = miniEscala();
  for (const b of $$("button", miniCaixa)) {
    const q = retSala(b.dataset.sala);
    Object.assign(b.style, { left: (ox + q.x * s) / dpr + "px", top: (oy + (q.y - Y0) * s) / dpr + "px", width: q.w * s / dpr + "px", height: q.h * s / dpr + "px" });
  }
}
function desenhaMinimapa(q) {
  const c = mini.getContext("2d"), { s, ox, oy } = miniEscala();
  c.fillStyle = "#0b0e12"; c.fillRect(0, 0, mini.width, mini.height);
  const comBalao = new Set(q.baloes.map(b => b.sala));
  for (const sl of SALAS) {
    if (sl.id === "escada") continue;
    const r = retSala(sl.id), x = ox + r.x * s, y = oy + (r.y - Y0) * s, w = r.w * s, h = r.h * s;
    const l = q.luz[sl.id];
    c.fillStyle = l === "acesa" ? "#e9dcc0" : l === "penumbra" ? "#7a8292" : l === "obra" ? "#5a4a30" : "#262b36";
    c.fillRect(x + 1, y + 1, w - 2, h - 2);
    if (comBalao.has(sl.id)) { c.strokeStyle = "#39ff6a"; c.lineWidth = 2; c.strokeRect(x + 2, y + 2, w - 4, h - 4); }
    if (sl.id === S.salaCam) { c.strokeStyle = "#ffffff"; c.lineWidth = 3; c.strokeRect(x + 1.5, y + 1.5, w - 3, h - 3); }
  }
  for (const p of Object.values(S.loc.p)) {
    c.fillStyle = getComputedStyle(document.documentElement).getPropertyValue(`--c-${p.id}`) || "#fff";
    const x = ox + p.x * s, y = oy + (p.y - Y0 - 12) * s;
    c.beginPath(); c.arc(x, y, Math.max(2.5, s * 5), 0, Math.PI * 2); c.fill();
  }
}

// ------------------------------------------------------------ personagens e balões (HTML sobre a cena)
const BOT = {}, BAL = new Map();
function criaBotoes() {
  for (const p of S.M.elenco) {
    const b = document.createElement("button");
    b.type = "button"; b.className = "pers"; b.dataset.id = p.id; b.hidden = true;
    b.innerHTML = `<span class="tag">${esc(p.nome)}</span>`;
    b.addEventListener("click", () => abreFicha(p.id, null, b));
    camada.append(b); BOT[p.id] = b;
  }
}
// Outros pontos clicáveis da cena (o quadro de pautas abre a ficha do Editor).
const ALVOS = [];
function criaAlvos() {
  for (const a of S.c2d.alvos()) {
    const b = document.createElement("button");
    b.type = "button"; b.className = "alvo"; b.setAttribute("aria-label", a.rotulo);
    b.addEventListener("click", () => abreFicha("editor", "pautas", b));
    camada.prepend(b); ALVOS.push({ ...a, el: b });
  }
}
function atualizaCamada(q) {
  const pw = S.med.cssW, ph = S.med.cssH;
  for (const a of ALVOS) {
    const ok = S.cena.tipo === "2d";
    const p0 = S.cena.projeta(a.x, a.y), p1 = S.cena.projeta(a.x + a.w, a.y + a.h);
    const fora = !ok || p1.x < 0 || p0.x > pw || p1.y < 0 || p0.y > ph;
    if (a.el.hidden !== fora) a.el.hidden = fora;
    if (!fora) { a.el.style.transform = `translate(${p0.x.toFixed(1)}px, ${p0.y.toFixed(1)}px)`; a.el.style.width = (p1.x - p0.x).toFixed(1) + "px"; a.el.style.height = (p1.y - p0.y).toFixed(1) + "px"; }
  }
  // botões
  for (const p of S.M.elenco) {
    const b = BOT[p.id], s = S.loc.p[p.id];
    if (!s) { if (!b.hidden) b.hidden = true; continue; }
    const pe = S.cena.projeta(s.x, s.y, 0), cab = S.cena.projeta(s.x, s.y, 54);
    const h = Math.max(24, pe.y - cab.y), w = Math.max(24, h * .48);
    const fora = pe.x < -w || pe.x > pw + w || cab.y > ph || pe.y < 0;
    if (b.hidden !== fora) b.hidden = fora;
    if (fora) continue;
    b.style.transform = `translate(${(pe.x - w / 2).toFixed(1)}px, ${cab.y.toFixed(1)}px)`;
    b.style.width = w.toFixed(1) + "px"; b.style.height = h.toFixed(1) + "px";
    const inf = s.info || {}, onde = s.andando ? "andando" : ONDE[s.sala] || "no estúdio";
    const rot = `${p.nome}, ${onde}${inf.situ && !s.andando ? `, ${inf.situ}` : ""}. Abrir a ficha.`;
    if (b.getAttribute("aria-label") !== rot) b.setAttribute("aria-label", rot);
  }
  // balões
  const vivos = new Set();
  for (const bl of q.baloes) {
    const s = S.loc.p[bl.quem];
    if (!s || s.andando || s.sala !== bl.sala || (s.opacidade ?? 1) < .9) continue;
    const r = S.cena.retSala(bl.sala);
    const visW = Math.min(r.x + r.w, pw) - Math.max(r.x, 0), visH = Math.min(r.y + r.h, ph) - Math.max(r.y, 0);
    if (visW < Math.min(r.w * .6, 150) || visH < Math.min(r.h * .6, 120)) continue;     // sala quase fora da câmera: o texto fica na lista
    let it = BAL.get(bl.chave);
    if (!it) { it = { el: criaBalao(bl), medir: true }; camada.append(it.el); BAL.set(bl.chave, it); }
    vivos.add(bl.chave);
    const cab = S.cena.projeta(s.x, s.y, 56);
    const x0 = Math.max(r.x + 4, 4), x1 = Math.min(r.x + r.w - 4, pw - 4), topo = Math.max(r.y + 4, 4);
    const disp = Math.round(cab.y - 12 - topo);
    const maxW = Math.round(clamp(x1 - x0, 110, 290));
    if (it.medir || it.maxW !== maxW || Math.abs((it.disp ?? 0) - disp) > 10) {
      it.el.style.setProperty("--max", maxW + "px");
      it.el.style.setProperty("--linhas", 8);
      it.w = it.el.offsetWidth; it.h = it.el.offsetHeight;
      if (it.h > disp && disp > 40) {
        const linhas = clamp(Math.floor((disp - (it.h - it.el.querySelector(".balao-txt").offsetHeight) - 4) / 18), 1, 8);
        it.el.style.setProperty("--linhas", linhas);
        it.h = it.el.offsetHeight;
      }
      it.medir = false; it.maxW = maxW; it.disp = disp;
    }
    const left = clamp(cab.x - it.w / 2, x0, Math.max(x0, x1 - it.w));
    const top = Math.max(topo, cab.y - 12 - it.h);
    it.el.style.transform = `translate(${left.toFixed(1)}px, ${top.toFixed(1)}px)`;
    it.el.style.setProperty("--rabo", clamp(cab.x - left, 14, it.w - 14).toFixed(1) + "px");
  }
  for (const [k, it] of BAL) if (!vivos.has(k)) { it.el.remove(); BAL.delete(k); }
  // placa da folga, na parede do café
  placaFolga(q);
}
function criaBalao(b) {
  const el = document.createElement("div");
  el.className = `balao o-${b.origem}`;
  el.style.setProperty("--cor", cor(b.quem));
  el.setAttribute("aria-hidden", "true");     // o mesmo texto está na lista "No estúdio agora"
  const pe = b.origem === "numeros" ? (b.sala === "cafe" ? "conversa montada com os números do dia" : "montado com os números do dia") : b.origem === "visitante" ? "reação do site à sua mensagem" : "";
  el.innerHTML = `<div class="balao-cab"><span class="ponto"></span>${esc(S.M.nomeDe(b.quem))}<span class="origem">· ${esc(ORIGEM[b.origem] || b.origem)}</span></div>`
    + `<p class="balao-txt">${esc(corta(b.texto))}</p>`
    + (b.nota ? `<span class="balao-nota"><b>no log</b>${esc(b.nota)}</span>` : "")
    + (pe ? `<span class="balao-pe">${pe}</span>` : "");
  return el;
}
// Corta sem reescrever: até ~90 caracteres, no último espaço, com "…".
function corta(txt, n = CORTE) {
  txt = String(txt);
  if (txt.length <= n) return txt;
  let c = txt.slice(0, n);
  const esp = c.lastIndexOf(" ");
  if (esp > n - 24) c = c.slice(0, esp);
  return c.replace(/[\s,;:.\-–—]+$/, "") + "…";
}
let placaEl = null;
function placaFolga(q) {
  if (!q.placa) { if (placaEl) { placaEl.remove(); placaEl = null; } return; }
  if (!placaEl) { placaEl = document.createElement("div"); placaEl.className = "placa-folga"; placaEl.setAttribute("role", "note"); camada.append(placaEl); }
  const txt = `<small>FOLGA · AVISO DA PORTARIA</small>${esc(q.placa.toLowerCase())}`;
  if (placaEl.dataset.t !== q.placa) { placaEl.innerHTML = txt; placaEl.dataset.t = q.placa; }
  const r = S.cena.retSala("cafe"), w = placaEl.offsetWidth;
  const vis = r.x + r.w > 0 && r.x < S.med.cssW;
  placaEl.hidden = !vis;
  placaEl.style.transform = `translate(${(r.x + r.w / 2 - w / 2).toFixed(1)}px, ${(r.y + r.h * .3).toFixed(1)}px)`;
}

// ------------------------------------------------------------ textos da página
function muda(chave, valor, fn) { if (S.assin[chave] !== valor) { S.assin[chave] = valor; fn(valor); } }
function textos(q, ms, t) {
  const c = campos(ms);
  muda("dia", `${c.dia} ${diaMes(c.data)}`, v => { $("#hora-dia").textContent = v; });
  muda("hora", S.replay ? hhmmss(ms) : hhmm(ms), v => { $("#hora-hhmm").textContent = v; });
  muda("fuso", S.replay ? "Horário real da gravação" : S.sim ? "São Paulo · simulado" : "Horário de São Paulo", v => { $("#hora-fuso").textContent = v; });
  muda("estado", q.estado, v => { $("#estado").textContent = v; });
  muda("chip", q.rotulo, v => { $("#chip").textContent = v; $("#chip").dataset.p = v; $("#periodo-desc").textContent = DESC[v] || ""; });
  palco.classList.toggle("em-replay", !!S.replay);
  registroRender(q, ms, t);
  hudRender(q, ms);
  if (S.replay) textosReplay(ms);
  if (S.ficha && S.aba === "hoje") muda("agora", agoraDe(S.ficha, q), v => { const el = $("#agora-txt"); if (el) el.innerHTML = v; });
}
// ------------------------------------------------------------ registro de eventos
// Na gravação (ao vivo ou replay): os eventos até o momento, o mais recente em
// cima. Fora dela: o que se diz agora no café ou na portaria.
const MAX_REG = 80;
function vistosAte(ms) { const c = S.M.corrida; let n = 0; while (n < c.length && c[n].ms <= ms) n++; return n; }
function registroRender(q, ms, t) {
  const gravando = q.per === "gravando";
  let itens, chave;
  if (gravando) {
    const n = vistosAte(ms);
    itens = S.M.corrida.slice(Math.max(0, n - MAX_REG), n).reverse().map((e, i) => ({ ...e, chave: "e" + e.i, atual: i === 0 }));
    chave = "g" + n + (S.replay ? "r" : "");
  } else {
    itens = q.fita; chave = q.fitaRotulo + itens.map(e => e.chave + (e.atual ? "*" : "")).join("|");
  }
  muda("registro", chave, () => {
    $("#registro-sub").textContent = S.replay ? (q.per === "gravando" ? "No replay, até agora" : "Fim do replay") : q.fitaRotulo;
    lista.innerHTML = itens.map(itemRegistro).join("") || `<li class="ev ev-sem-hora"><div class="ev-linha"><span class="ev-txt">Nada acontecendo agora.</span></div></li>`;
    $("#registro-nota").textContent = q.fitaNota || (gravando ? (S.replay ? "Clique num evento para levar a linha do tempo até ele." : "O mais recente em cima.") : "");
    if (S.replay && itens[0] && itens[0].ms && t - S.anunciado > 4000 && S.replay.vel !== "rapido") {
      const e = itens[0]; S.anunciado = t;
      $("#anuncio").textContent = `${hhmmss(e.ms)}, ${S.M.nomeDe(e.quem)}: ${e.texto}`;
    }
  });
}
function itemRegistro(e) {
  const tag = ORIGEM_CURTA[e.origem] || e.origem;
  const corpo = `${e.ms ? `<time>${hhmmss(e.ms)}</time>` : ""}<span class="ev-cab"><span class="ev-tag">${esc(tag)}</span><span class="ev-quem"><span class="ponto" style="--cor:${cor(e.quem)}"></span>${esc(S.M.nomeDe(e.quem))}</span></span>`
    + `<span class="ev-txt">${esc(e.texto)}</span>${e.nota ? `<span class="ev-nota"><b>no log</b>${esc(e.nota)}</span>` : ""}`;
  const cls = `ev o-${e.origem}${e.atual ? " atual" : ""}${e.ms ? "" : " ev-sem-hora"}`;
  return S.replay && e.ms
    ? `<li class="${cls}"><button type="button" class="ev-linha" data-ms="${e.ms}" aria-label="Ir para ${hhmmss(e.ms)}: ${esc(S.M.nomeDe(e.quem))}, ${esc(tag)}. ${esc(e.texto)}">${corpo}</button></li>`
    : `<li class="${cls}"><div class="ev-linha">${corpo}</div></li>`;
}
const ORIGEM_CURTA = { agente: "agente", ferramenta: "ferramenta", log: "log", sistema: "sistema", numeros: "números", agenda: "agenda", visitante: "site" };
lista.addEventListener("click", e => { const b = e.target.closest("[data-ms]"); if (b && S.replay) irPara(+b.dataset.ms); });

// ------------------------------------------------------------ barra de status (só dado real)
function emQuanto(ms, alvo) {
  let min = Math.max(0, Math.round((alvo - ms) / 60000));
  const d = Math.floor(min / 1440); min -= d * 1440; const h = Math.floor(min / 60); min -= h * 60;
  return d ? `em ${d} d ${h} h` : h ? (min ? `em ${h} h ${min} min` : `em ${h} h`) : `em ${min} min`;
}
function hudRender(q, ms) {
  const M = S.M, d = M.dia, ep = d.episodio, it = [];
  const item = (rot, val, cls = "") => `<span${cls ? ` class="${cls}"` : ""}><span class="rot">${rot}</span><b>${val}</b></span>`;
  if (q.per === "gravando" || (S.replay && q.per === "dia")) {
    const n = vistosAte(ms), ev = M.corrida.slice(0, n);
    const cap = M.capitulos.filter(c => c.ms <= ms).pop();
    it.push(item("capítulo", esc(cap ? cap.titulo : "—")));
    const fech = ev.filter(e => e.acao === "fechada").length;           // cada página fechada tem antes um "Lendo …"
    it.push(item("páginas lidas", numero(ev.filter(e => e.acao === "le" && e.url).length - fech)));
    if (fech) it.push(item("não abriram", numero(fech)));
    it.push(item("buscas", numero(ev.filter(e => e.acao === "busca").length)));
    if (ms >= M.FIM) {
      const e = d.execucao;
      if (e.custo_claude_usd != null) it.push(item("modelo", "US$ " + e.custo_claude_usd.toFixed(2).replace(".", ",")));
      if (e.creditos_elevenlabs != null) it.push(item("voz", numero(e.creditos_elevenlabs) + " créditos"));
    }
  } else if (q.per === "gravando-sem-dados") {
    it.push(item("gravando", "os números saem com o episódio"));
  } else {
    const c = campos(ms), prox = M.proximaGravacao(c);
    if (prox) it.push(item("próxima gravação", `${esc(semanaCurta(prox))}, ${diaMes(prox)}, às ${esc(d.agenda.gravacao)} · ${emQuanto(ms, msDe(prox, d.agenda.gravacao))}`, "fosforo"));
    if (ms >= M.FIM) it.push(item("no ar desde", `${c.data === d.data ? "" : diaMes(d.data) + ", "}${hhmm(M.FIM)} · episódio ${ep.numero}`));
  }
  muda("hud", it.join(""), v => { hud.innerHTML = v; ajustaRegistro(); });
}

// ------------------------------------------------------------ último episódio
function montaEpisodio() {
  const d = S.M.dia, ep = d.episodio;
  $("#ep-num").textContent = `Episódio ${ep.numero}`;
  $("#ep-meta").textContent = `${semana(d.data)}, ${diaMes(d.data)} · ${duracaoTexto(d.execucao.audio_s)} · ${ep.pautas.length} pautas`;
  $("#ep-titulo").textContent = ep.titulo;
  $("#ep-pautas").innerHTML = ep.pautas.map(p => `<li>${esc(p.titulo)}${p.do_backlog ? ' <span class="tag-mini">do backlog</span>' : ""}</li>`).join("");
  $("#ep-roteiro").addEventListener("click", e => abreFicha("roteirista", "roteiro", e.currentTarget));
}

// ------------------------------------------------------------ replay
function montaReplay() {
  const M = S.M, r = new Replay(M);
  $("#velocidades").innerHTML = Object.entries(VELOCIDADES).map(([k, v]) =>
    `<button type="button" data-vel="${k}" aria-pressed="false">${v.nome}<small>${duracaoTexto(r.duracao(k) / 1000)}</small></button>`).join("");
  $("#capitulos").innerHTML = M.capitulos.map((c, i) => `<li><button type="button" data-i="${i}" style="--cor:${cor(c.quem)}"><span class="ponto"></span>${esc(c.titulo)}</button></li>`).join("");
  $("#cap-select").innerHTML = M.capitulos.map((c, i) => `<option value="${i}">${hhmm(c.ms)} · ${esc(c.titulo)}</option>`).join("");
  $("#marcas").innerHTML = M.capitulos.map(c => `<i style="left:${(100 * (c.ms - M.INI) / (M.FIM - M.INI)).toFixed(2)}%"></i>`).join("");
  $("#replay-quando").innerHTML = `<b>Gravado em ${semana(M.dia.data)}, ${diaMes(M.dia.data)}, das ${hhmm(M.INI)} às ${hhmm(M.FIM)}.</b> <span class="longo">Não é ao vivo: o relógio mostra o horário real de cada evento.</span>`;
  $("#velocidades").addEventListener("click", e => { const b = e.target.closest("[data-vel]"); if (b && S.replay) { S.replay.vel = b.dataset.vel; marcaVel(); } });
  $("#capitulos").addEventListener("click", e => { const b = e.target.closest("[data-i]"); if (b) irPara(M.capitulos[+b.dataset.i].ms); });
  $("#cap-select").addEventListener("change", e => irPara(M.capitulos[+e.target.value].ms));
  $("#trilha").addEventListener("input", e => irPara(M.INI + (M.FIM - M.INI) * e.target.value / 1000));
  $("#btn-play").addEventListener("click", () => {
    if (!S.replay) return;
    if (S.replay.fim) { S.replay.recomeca(); S.saltar = true; } else S.replay.pausado = !S.replay.pausado;
  });
  $("#btn-replay").addEventListener("click", () => abreReplay());
  $("#btn-sair").addEventListener("click", saiReplay);
}
function abreReplay(vel = "acelerado", rolar = true) {
  if (S.replay) { S.replay.recomeca(); S.saltar = true; return; }
  S.replay = new Replay(S.M, VELOCIDADES[vel] ? vel : "acelerado");
  $("#faixa-replay").hidden = false;
  const b = $("#btn-replay"); b.setAttribute("aria-pressed", "true"); $(".rotulo-replay", b).textContent = "Recomeçar o replay";
  marcaVel(); S.saltar = true; S.seguir = true;
  if (rolar) window.scrollTo({ top: 0, behavior: reduz.matches ? "auto" : "smooth" });
  $("#btn-play").focus({ preventScroll: true });
}
function saiReplay() {
  S.replay = null;
  $("#faixa-replay").hidden = true;
  const b = $("#btn-replay"); b.setAttribute("aria-pressed", "false"); $(".rotulo-replay", b).textContent = "Replay da gravação";
  b.focus({ preventScroll: true });
}
function irPara(ms) { if (!S.replay) return; S.replay.irPara(ms); S.saltar = true; }
function marcaVel() { $$("[data-vel]").forEach(b => b.setAttribute("aria-pressed", String(!!S.replay && b.dataset.vel === S.replay.vel))); }
function textosReplay(ms) {
  const r = S.replay, M = S.M;
  muda("rhora", hhmmss(ms), v => { $("#replay-hora").textContent = v; $("#trilha").setAttribute("aria-valuetext", v); });
  const tr = $("#trilha");
  if (document.activeElement !== tr) tr.value = Math.round(1000 * clamp(r.progresso(), 0, 1));
  const estado = r.fim ? "rever" : r.pausado ? "play" : "pausa";
  muda("play", estado, v => { const b = $("#btn-play"); b.innerHTML = ICONE[v]; b.setAttribute("aria-label", v === "rever" ? "Rever do começo" : v === "play" ? "Continuar" : "Pausar"); });
  const atual = M.capitulos.filter(c => c.ms <= ms).length - 1;
  muda("cap", atual, v => {
    $$("#capitulos button").forEach((b, i) => b.setAttribute("aria-current", String(i === v)));
    if (v >= 0) $("#cap-select").value = String(v);
  });
}

// ------------------------------------------------------------ ficha do personagem
const ficha = $("#ficha");
const ABA_PROPRIA = { jornalista: ["leituras", "Leituras"], editor: ["pautas", "Pautas e memória"], roteirista: ["roteiro", "Roteiro"],
  locutor: ["episodio", "Episódio"], produtor: ["etapas", "Etapas"], vigia: ["plantao", "Plantão"] };
const AGENTE = ["jornalista", "editor", "roteirista"];

function abreFicha(id, aba, origem, focoAba = false) {
  const p = S.M.porId[id], breve = p.situacao === "em_breve";
  const abas = (breve ? [["embreve", "Em breve"], p.instrucoes.length && ["instrucoes", "Instruções"]]
                      : [["hoje", "Hoje"], ABA_PROPRIA[id], p.instrucoes.length && ["instrucoes", "Instruções"]]).filter(Boolean);
  if (!abas.some(a => a[0] === aba)) aba = abas[0][0];
  if (S.ficha && S.ficha !== id && BOT[S.ficha]) BOT[S.ficha].classList.remove("aberta");
  if (!ficha.open || S.ficha !== id) S.volta = origem || document.activeElement;
  S.ficha = id; S.aba = aba; S.assin.agora = null;
  ficha.style.setProperty("--cor", cor(id));
  ficha.innerHTML = `
    <div class="ficha-topo">
      <canvas class="ficha-retrato" width="32" height="36" aria-hidden="true"></canvas>
      <div><h2 id="ficha-nome" tabindex="-1">${esc(p.nome)} <span class="situ ${p.situacao}">${SITU[p.situacao] || p.situacao}</span></h2><p>${esc(p.papel)}</p></div>
      <button class="fechar" type="button" aria-label="Fechar a ficha">${ICONE.fechar}</button>
    </div>
    <div class="abas" role="tablist" aria-label="Seções da ficha">${abas.map(([k, n]) =>
      `<button role="tab" type="button" id="aba-${k}" data-aba="${k}" aria-controls="ficha-corpo" aria-selected="${k === aba}" tabindex="${k === aba ? 0 : -1}">${n}</button>`).join("")}</div>
    <div class="ficha-corpo" id="ficha-corpo" role="tabpanel" aria-labelledby="aba-${aba}" tabindex="0">${corpoFicha(p, aba)}</div>`;
  const rc = $(".ficha-retrato", ficha).getContext("2d");
  rc.imageSmoothingEnabled = false;
  rc.drawImage(sprite(id, breve ? "congelado" : "parado", 0), 0, 0, 32, 36, 0, 0, 32, 36);
  $(".fechar", ficha).addEventListener("click", fechaFicha);
  const tabs = $$("[role=tab]", ficha);
  tabs.forEach((b, i) => {
    b.addEventListener("click", () => abreFicha(id, b.dataset.aba, null, true));
    b.addEventListener("keydown", e => {
      const d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
      if (d) { e.preventDefault(); abreFicha(id, tabs[(i + d + tabs.length) % tabs.length].dataset.aba, null, true); }
    });
  });
  const sug = $("[data-acao=sugerir]", ficha);
  if (sug) sug.addEventListener("click", () => { fechaFicha(); $("#tema").focus(); $("#sugira").scrollIntoView({ behavior: reduz.matches ? "auto" : "smooth", block: "center" }); });
  const lr = $("[data-acao=roteiro]", ficha);
  if (lr) lr.addEventListener("click", () => abreFicha("roteirista", "roteiro", null, true));
  if (!ficha.open) {
    if (S.med.modo === "inteiro") { document.body.classList.add("com-ficha"); ficha.show(); aplicaMedidas(); }
    else ficha.showModal();
  }
  BOT[id].classList.add("aberta");
  if (focoAba) $(`#aba-${aba}`, ficha).focus(); else $("#ficha-nome", ficha).focus();
  if (aba === "hoje" && S.q) { const el = $("#agora-txt"); if (el) el.innerHTML = agoraDe(id, S.q); }
}
function fechaFicha() { if (ficha.open) ficha.close(); }
ficha.addEventListener("close", () => {
  if (document.body.classList.contains("com-ficha")) { document.body.classList.remove("com-ficha"); aplicaMedidas(); }
  if (S.ficha && BOT[S.ficha]) BOT[S.ficha].classList.remove("aberta");
  S.ficha = null;
  const v = S.volta; S.volta = null;
  // o palco muda de tamanho ao fechar a ficha; devolve o foco depois que a camada se reposiciona
  if (v && document.contains(v)) requestAnimationFrame(() => requestAnimationFrame(() => { if (!v.hidden) v.focus({ preventScroll: true }); }));
});
ficha.addEventListener("keydown", e => { if (e.key === "Escape" && !ficha.matches(":modal")) { e.preventDefault(); fechaFicha(); } });
ficha.addEventListener("click", e => { if (e.target === ficha && ficha.matches(":modal")) fechaFicha(); });

function agoraDe(id, q) {
  const p = S.M.porId[id], s = S.loc.p[id];
  if (p.situacao === "em_breve") return `${esc(ONDE[(q.pessoas[id] || {}).sala] || "na ala nova")}, congelado. Ainda não trabalha na gravação.`;
  if (!s) {
    const prox = S.M.proximaGravacao(campos(q.ms));
    return `Fora do estúdio.${prox ? ` Volta ${esc(semanaCurta(prox))}, ${diaMes(prox)}, às ${esc(S.M.dia.agenda.gravacao)}.` : ""}`;
  }
  if (s.andando) return "Andando pelo estúdio.";
  const b = q.baloes.find(b => b.quem === id);
  const onde = ONDE[s.sala] || "no estúdio";
  const quando = q.replay ? ` <span class="nota">(replay, ${hhmmss(q.ms)})</span>` : "";
  if (b) return `${esc(onde[0].toUpperCase() + onde.slice(1))}: <span class="o-${b.origem}" style="${b.origem === "agente" ? "font-style:italic" : ""}">${b.origem === "agente" ? "“" : ""}${esc(b.texto)}${b.origem === "agente" ? "”" : ""}</span>${quando}`;
  return `${esc(onde[0].toUpperCase() + onde.slice(1))}, ${esc((s.info || {}).situ || "parado")}.${quando}`;
}

function corpoFicha(p, aba) {
  const id = p.id, M = S.M, d = M.dia, ep = d.episodio, agente = AGENTE.includes(id);
  const porTras = `<p class="costura"><b>Por trás:</b> ${esc(p.por_tras)}.</p>`;
  const costura = agente ? `<p class="costura"><b>A costura:</b> hoje Jornalista, Editor e Roteirista são o mesmo agente, com um prompt só. O site separa o trabalho pelo que ele estava fazendo em cada momento.</p>` : "";
  switch (aba) {
    case "embreve":
      return `<div class="agora"><p class="rotulo">O que vai fazer</p><p>${esc(p.em_breve)}</p></div>${porTras}
        <p class="nota">Fica congelado na ala nova, em obras, até estrear. Ninguém de lá aparece trabalhando no replay.</p>`;
    case "hoje": {
      const meus = M.eventos.filter(e => e.quem === id);
      return `<div class="agora"><p class="rotulo">Agora</p><p id="agora-txt">—</p></div>${costura}${porTras}
        ${p.em_breve ? `<p class="costura"><b>Em breve:</b> ${esc(p.em_breve)}</p>` : ""}
        <h3>Na gravação de ${semana(d.data)}, ${diaMes(d.data)} <span class="nota">· ${meus.length} registros</span></h3>
        <ol class="fita">${meus.map(e => `<li><time>${hhmmss(e.ms)}</time><span class="t o-${e.origem}">${esc(e.texto)}${e.url && e.acao !== "fechada" ? ` <a href="${esc(e.url)}" target="_blank" rel="noopener">abrir</a>` : ""}${e.nota ? `<span class="nota-log"><b>no log</b>${esc(e.nota)}</span>` : ""}</span></li>`).join("")
          || `<li><span></span><span class="t">Nada registrado nesta gravação.</span></li>`}</ol>`;
    }
    case "instrucoes":
      return `<p class="nota" style="margin:0">O texto que o ${esc(p.nome)} recebe como instrução, tirado dos arquivos do projeto.${agente ? " Os três papéis do agente leem um arquivo só, separado aqui por passo." : ""}</p>
        ${p.instrucoes.map((s, i) => `<details class="bloco"${i === 0 ? " open" : ""}><summary><span>${esc(s.titulo)}</span>${s.compartilhada ? '<span class="mudo">vale para os três</span>' : ""}</summary>
          <p class="origem-arq">${esc(s.origem)}</p><div class="instr">${esc(s.texto)}</div></details>`).join("")}`;
    case "leituras": {
      const pq = d.pesquisa, notas = pq.notas || [], comNota = notas.filter(n => n.nota).length, notaNaLeitura = pq.leituras.some(l => l.nota);
      return `<div class="numeros"><div><b>${numero(pq.paginas)}</b><span>páginas</span></div><div><b>${numero(pq.sites)}</b><span>sites</span></div>
          <div><b>${numero(pq.buscas)}</b><span>buscas</span></div><div><b class="fechada">${numero(pq.fechadas)}</b><span>fechadas</span></div></div>
        <p class="nota" style="margin:0">Contagem do próprio agente, no <a href="${esc(pq.url)}" target="_blank" rel="noopener">log de pesquisa</a>. A lista abaixo vem da transcrição, na ordem em que ele abriu (${pq.leituras.length} leituras).</p>
        <h3>Páginas</h3>
        <ol class="lista">${pq.leituras.map(l => `<li><span><a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.url.replace(/^https?:\/\/(www\.)?/, "").replace(/\/$/, ""))}</a>${l.ok ? "" : `<span class="fechada-tag">não abriu${l.status ? ` · ${esc(l.status)}` : ""}</span>`}${l.nota ? `<span class="nota-log" style="display:block"><b>no log</b>${esc(l.nota)}</span>` : ""}</span></li>`).join("")}</ol>
        ${!notaNaLeitura && notas.length ? `<details class="bloco"><summary><span>Notas do log de pesquisa</span><span class="mudo">${comNota} com nota, de ${notas.length}</span></summary>
          <ul class="lista">${notas.map(n => `<li><b class="mono" style="font-size:12.5px">${esc(n.endereco)}</b><br><span class="${n.nota ? "" : "nota"}">${n.nota ? esc(n.nota) : "sem nota"}</span></li>`).join("")}</ul>
          <p class="nota">Como o Jornalista escreveu no fim da gravação, na ordem do log. Nesta gravação as notas ainda não vêm ligadas a cada página.</p></details>` : ""}
        <h3>Buscas <span class="nota">· ${pq.buscas_feitas.length}</span></h3>
        <ol class="lista">${pq.buscas_feitas.map(b => `<li><span>${esc(b)}</span></li>`).join("")}</ol>`;
    }
    case "pautas": {
      const m = d.memoria, esc_ = d.pesquisa.escolhas || [];
      const tema = t => { const [titulo, ...resto] = String(t.titulo).split("\n"); return `<li><details class="tema"><summary><span class="tema-id">${esc(t.id)}</span><span class="tema-tit">${esc(titulo)}</span>${t.estado_em ? `<span class="tema-data">estado em ${diaMes(t.estado_em)}</span>` : ""}</summary>${t.estado ? `<p>${esc(t.estado)}</p>` : `<p class="nota">Sem estado registrado.</p>`}${resto.length ? `<div class="instr" style="max-height:240px">${esc(resto.join("\n"))}</div>` : ""}</details></li>`; };
      const escolha = x => typeof x === "string" ? esc(x)
        : esc([x.ficou || x.escolhida || x.x, x.perdeu || x.preterida || x.y].filter(Boolean).join(" em vez de ") + (x.motivo || x.porque ? ` — ${x.motivo || x.porque}` : ""));
      return `<button class="btn btn-acao" type="button" data-acao="sugerir" style="justify-self:start">Sugerir um tema</button>
        <h3>Entraram <span class="nota">· ${ep.pautas.length}</span></h3>
        <ol class="lista">${ep.pautas.map(x => `<li><span><b>${esc(x.titulo)}</b>${x.do_backlog ? ' <span class="tag-mini">do backlog</span>' : ""}<br><span class="nota">${esc(x.fonte)}</span> <a href="${esc(x.url)}" target="_blank" rel="noopener">fonte</a></span></li>`).join("")}</ol>
        <h3>Escolhas</h3>
        ${esc_.length ? `<ul class="lista">${esc_.map(x => `<li>${escolha(x)}</li>`).join("")}</ul>` : `<p class="nota" style="margin:0">O log desta gravação não registra escolhas entre candidatas.</p>`}
        <details class="bloco"><summary><span>Descartadas</span><span class="mudo">${d.pesquisa.descartadas.length} de ${numero(d.pesquisa.pautas_avaliadas)} avaliadas</span></summary>
          <ul class="lista">${d.pesquisa.descartadas.map(x => `<li><b>${esc(x.titulo)}</b><br><span class="nota">${esc(x.motivo)}</span></li>`).join("")}</ul></details>
        <details class="bloco" open><summary><span>Temas que o programa acompanha</span><span class="mudo">${m.temas.length}</span></summary>
          <ul class="lista temas">${m.temas.map(tema).join("")}</ul><p class="nota"><a href="${esc(m.urls.temas)}" target="_blank" rel="noopener">temas.md no GitHub</a></p></details>
        <details class="bloco"><summary><span>Fios em aberto</span><span class="mudo">${m.fios.length} no arquivo de hoje</span></summary>
          <ul class="lista">${m.fios.map(f => `<li><b class="mono" style="font-size:12.5px">${esc(f.id)}</b> ${esc(f.titulo)}</li>`).join("")}</ul><p class="nota"><a href="${esc(m.urls.fios)}" target="_blank" rel="noopener">fios.md no GitHub</a></p></details>
        <details class="bloco"><summary><span>Backlog</span><span class="mudo">${m.backlog.length}</span></summary>
          <ul class="lista">${m.backlog.map(b => `<li>${esc(b.titulo)}${b.validade ? ` <span class="nota">· vale até ${diaMes(b.validade)}</span>` : ""}</li>`).join("") || "<li class='nota'>Vazio nesta gravação.</li>"}</ul>
          <p class="nota"><a href="${esc(m.urls.backlog)}" target="_blank" rel="noopener">backlog.md no GitHub</a></p></details>`;
    }
    case "roteiro":
      return `<p class="nota" style="margin:0">Episódio ${ep.numero} · ${numero(ep.palavras)} palavras · <a href="${esc(ep.roteiro_url)}" target="_blank" rel="noopener">o arquivo no GitHub</a></p>
        <h3 style="font-size:18px;line-height:1.3">${esc(ep.titulo)}</h3><div class="roteiro">${ep.roteiro.map(x => `<p>${esc(x)}</p>`).join("")}</div>`;
    case "episodio": {
      const e = d.execucao;
      return `<div class="numeros"><div><b>${duracaoTexto(e.audio_s).replace(" min ", ":").replace(" s", "")}</b><span>de voz (${duracaoTexto(e.audio_s)})</span></div>
          <div><b>${numero(e.creditos_elevenlabs)}</b><span>créditos de voz</span></div></div>
        <audio class="player" controls preload="none" src="${esc(ep.mp3)}"></audio>
        <p class="nota" style="margin:0">Episódio ${ep.numero}: ${esc(ep.titulo)}. Se o player não tocar aqui, <a href="${esc(ep.mp3)}" target="_blank" rel="noopener">abra o MP3</a> ou ouça no Spotify.</p>
        <button class="btn btn-sec" type="button" data-acao="roteiro" style="justify-self:start">Ler o roteiro</button>`;
    }
    case "etapas": {
      const e = d.execucao, nomes = { pesquisa: "Pesquisa e roteiro", narracao: "Narração", publicacao: "Publicação", aviso: "Aviso" };
      const total = Object.values(e.etapas_s).reduce((a, b) => a + b, 0) || 1;
      return `<div class="numeros"><div><b>${hhmm(M.INI)}</b><span>abriu o estúdio</span></div><div><b>${hhmm(M.FIM)}</b><span>no ar</span></div>
          <div><b>${e.custo_claude_usd != null ? "US$ " + e.custo_claude_usd.toFixed(2).replace(".", ",") : "—"}</b><span>de modelo</span></div>
          <div><b>${e.creditos_elevenlabs != null ? numero(e.creditos_elevenlabs) : "—"}</b><span>créditos de voz</span></div></div>
        <div class="etapas">${Object.entries(e.etapas_s).map(([k, v]) => `<div class="etapa"><span>${esc(nomes[k] || k)}</span><span class="barra"><i style="width:${Math.max(1, 100 * v / total).toFixed(1)}%"></i></span><span class="mono">${duracaoTexto(v)}</span></div>`).join("")}</div>
        <p class="nota" style="margin:0">Modelo: <span class="mono">${esc(e.modelo)}</span>. Repescagem às ${d.agenda.repescagem.map(esc).join(" e ")}: se a gravação das ${esc(d.agenda.gravacao)} falhar, o Produtor tenta de novo.</p>`;
    }
    case "plantao": {
      const ag = d.agenda, conf = M.eventos.find(e => e.quem === "vigia");
      return `<ul class="lista"><li><b>Estado da última gravação:</b> ${esc(d.execucao.estado)}</li>
          <li><b>Conferência do roteiro:</b> ${conf ? `${esc(conf.texto)} <span class="nota">(${hhmmss(conf.ms)})</span>` : "—"}</li>
          <li><b>Às ${esc(ag.vigia)}:</b> confere, da nuvem, se o episódio está no ar.</li></ul>
        <h3>Próximas gravações</h3><ul class="lista">${ag.proximos.map(x => `<li>${esc(semana(x))}, ${diaMes(x)}, às ${esc(ag.gravacao)}</li>`).join("")}</ul>
        <h3>Dias sem episódio</h3><ul class="lista">${Object.entries(ag.folgas).map(([x, m]) => `<li>${diaMes(x)}: ${esc(m)}</li>`).join("")}</ul>`;
    }
  }
  return "";
}

// ------------------------------------------------------------ sugestão de tema
const form = $("#form-tema");
$("#tema").addEventListener("input", e => { $("#tema-conta").textContent = `${numero(e.target.value.length)} / ${numero(1000)}`; });
form.addEventListener("submit", e => {
  e.preventDefault();
  const r = $("#resposta"), txt = $("#tema").value.trim();
  r.hidden = false; r.classList.remove("erro");
  if ($("#site").value) { r.textContent = "Recebido."; return; }        // robô
  if (!txt) { r.classList.add("erro"); r.textContent = "Escreva o tema antes de enviar."; $("#tema").focus(); return; }
  if (!$("#privacidade").checked) { r.classList.add("erro"); r.textContent = "Marque a concordância com a política de privacidade para enviar."; $("#privacidade").focus(); return; }
  if (S.replay) { r.textContent = "Protótipo: nada foi enviado. Você está no replay; volte ao vivo para ver o estúdio reagir."; return; }
  S.sug = performance.now(); S.seguir = true;
  r.textContent = "Protótipo: nada foi enviado. No site de verdade, o Produtor recebe e leva ao Editor, que avalia. Repare no estúdio.";
  $("#palco").scrollIntoView({ behavior: reduz.matches ? "auto" : "smooth", block: "center" });
});

// ------------------------------------------------------------ simulação de horário (só no protótipo)
function simula(v) {
  const d = S.M.dia;
  if (v === "agora") S.sim = null;
  else if (v === "folga") S.sim = { base: msDe(Object.keys(d.agenda.folgas)[0], "14:00"), desde: performance.now() };
  else S.sim = { base: msDe(d.data, v), desde: performance.now() };
  if (S.replay) saiReplay();
  S.saltar = true; S.seguir = true;
  $$("[data-sim]").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.sim === v)));
}
$$("[data-sim]").forEach(b => b.addEventListener("click", () => simula(b.dataset.sim)));

// ------------------------------------------------------------ tema
function tema(v) {
  if (v === "light" || v === "dark") document.documentElement.dataset.theme = v; else delete document.documentElement.dataset.theme;
  $$("[data-tema]").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.tema === (v === "light" || v === "dark" ? v : "auto"))));
}
$$("[data-tema]").forEach(b => b.addEventListener("click", () => tema(b.dataset.tema)));

// ------------------------------------------------------------ 2D ↔ 3D
function semWebGL() {
  if (URLP.has("forca3d")) return null;
  const c = document.createElement("canvas");
  if (!(c.getContext("webgl2") || c.getContext("webgl"))) return "Este navegador não tem WebGL. O estúdio fica no 2D.";
  if ((navigator.deviceMemory && navigator.deviceMemory < 3) || (grosso.matches && navigator.hardwareConcurrency && navigator.hardwareConcurrency < 4))
    return "Este aparelho é modesto para o 3D. O estúdio fica no 2D.";
  return null;
}
function aviso(txt) { const a = $("#aviso-3d"); a.hidden = !txt; if (txt) a.textContent = txt; }
async function ver3d() {
  if (S.cena && S.cena.tipo === "3d") return;
  const motivo = semWebGL();
  if (motivo) { aviso(motivo); setTimeout(() => aviso(null), 4500); return; }
  aviso("Montando o estúdio em 3D…");
  try {
    if (!S.c3d) { const mod = await import("./cena3d.js"); S.c3d = new mod.Cena3D(palco); await S.c3d.pronto; }
    S.c3d.medidas(S.med); S.c3d.mostra(true);
    S.c2d.tela.hidden = true; S.cena = S.c3d;
    for (const it of BAL.values()) it.medir = true;
    $("#ver-2d").hidden = false;
    aviso(null);
  } catch (err) {
    console.error(err);
    aviso("Não deu para abrir o 3D aqui. O estúdio continua em 2D.");
    setTimeout(() => aviso(null), 4500);
  }
}
function ver2d() {
  if (S.cena === S.c2d) return;
  S.cena = S.c2d; S.c2d.tela.hidden = false;
  if (S.c3d) S.c3d.mostra(false);
  for (const it of BAL.values()) it.medir = true;
}
$("#ver-2d").addEventListener("click", () => { ver2d(); $("#ver-2d").hidden = true; });

// ------------------------------------------------------------ início
let espera;
window.addEventListener("resize", () => { clearTimeout(espera); espera = setTimeout(aplicaMedidas, 80); });
carrega().catch(err => {
  console.error(err);
  $("#estado").textContent = "Não consegui ler os dados do estúdio (estudio/elenco.json e estudio/ultimo.json).";
});

window.__estudio = S;   // para depurar no console
