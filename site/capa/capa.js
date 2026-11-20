// CampsCast — a capa.
// Os números do "como funciona" e o último episódio saem de /estudio/ultimo.json,
// o mesmo arquivo que o estúdio lê. Sem os dados, a página continua de pé: o
// cartão do episódio some e os passos ficam só com o texto.

const $ = s => document.querySelector(s);
const num = n => new Intl.NumberFormat("pt-BR").format(n);
const diaMes = iso => iso.slice(8, 10) + "/" + iso.slice(5, 7);
const semana = iso => {
  const [a, m, d] = iso.split("-").map(Number);
  return new Intl.DateTimeFormat("pt-BR", { weekday: "long" }).format(new Date(a, m - 1, d));
};
const hhmm = isoHora => isoHora.slice(11, 16);
const duracao = s => `${Math.floor(s / 60)} min ${String(Math.round(s % 60)).padStart(2, "0")} s`;
const poe = (sel, txt) => { const el = $(sel); if (el && txt) el.textContent = txt; };

async function carrega() {
  const r = await fetch("/estudio/ultimo.json");
  if (!r.ok) throw new Error("ultimo.json " + r.status);
  const d = await r.json(), ep = d.episodio, ex = d.execucao || {}, pq = d.pesquisa || {};
  const n = ep.pautas.length;

  poe("#ep-num", `Episódio ${ep.numero}`);
  poe("#ep-titulo", ep.titulo);
  poe("#ep-meta", [`${semana(d.data)}, ${diaMes(d.data)}`, ex.audio_s && duracao(ex.audio_s), `${n} ${n === 1 ? "pauta" : "pautas"}`].filter(Boolean).join(" · "));
  if (ep.roteiro_url) $("#ep-roteiro").href = ep.roteiro_url;
  capaDoEpisodio(d.data, ep.numero);
  if (ep.mp3) player(ep.mp3, ex.audio_s);
  $("#episodio").hidden = false;

  poe("#como-fonte", `Os números são da última gravação, ${semana(d.data)}, ${diaMes(d.data)}.`);
  const [ja, jb] = ep.janela || [];
  if (ex.inicio && ja) poe("#n-janela", `${hhmm(ex.inicio)} · notícias ${ja === jb ? "de " + diaMes(ja) : `de ${diaMes(ja)} a ${diaMes(jb)}`}`);
  if (pq.paginas) poe("#n-pesquisa", `${num(pq.paginas)} páginas em ${num(pq.sites)} sites · ${num(pq.buscas)} buscas`);
  if (pq.pautas_avaliadas) poe("#n-editor", `${num(pq.pautas_avaliadas)} avaliadas · ${n} no ar`);
  if (ep.palavras) poe("#n-roteiro", `${num(ep.palavras)} palavras`);
  if (ex.audio_s) poe("#n-voz", `${duracao(ex.audio_s)} de áudio`);
  if (ex.fim) poe("#n-publica", `no ar às ${hhmm(ex.fim)}`);
}

// Capa do episódio: a do dia (desde 23/11, .png; a âmbar de 19/11, .jpg) ou a
// do programa. Fora do site publicado (prévia local), as imagens vêm de lá.
function capaDoEpisodio(data, numero) {
  const base = location.hostname.endsWith("campscast.com.br") ? "" : "https://campscast.com.br";
  const img = $("#ep-capa"), tentativas = [`${base}/capas/${data}.png`, `${base}/capas/${data}.jpg`, `${base}/cover.jpg`];
  const proxima = () => { if (tentativas.length) img.src = tentativas.shift(); else img.onerror = null; };
  img.onerror = proxima;
  img.alt = `Capa do episódio ${numero}`;
  proxima();
}

// Player: o MP3 do próprio site, o mesmo do feed. Nada de terceiros na página
// (é o que a página de privacidade promete); só baixa quando a pessoa aperta.
function player(mp3, segundos) {
  const audio = $("#ep-audio"), botao = $("#player-botao"), barra = $("#player-barra"), icone = $("#player-icone");
  const mmss = s => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
  const total = () => audio.duration || segundos || 0;
  const mostra = () => {
    $("#player-tempo").textContent = `${mmss(audio.currentTime)} / ${mmss(total())}`;
    if (total()) barra.value = Math.round(1000 * audio.currentTime / total());
  };
  audio.src = mp3;
  botao.addEventListener("click", () => (audio.paused ? audio.play() : audio.pause()));
  audio.addEventListener("play", () => { icone.setAttribute("d", "M4 2.5h3v11H4zM9 2.5h3v11H9z"); botao.setAttribute("aria-label", "Pausar"); });
  audio.addEventListener("pause", () => { icone.setAttribute("d", "M4 2.5v11l9-5.5z"); botao.setAttribute("aria-label", "Tocar o episódio"); });
  audio.addEventListener("timeupdate", mostra);
  audio.addEventListener("loadedmetadata", mostra);
  barra.addEventListener("input", () => { if (total()) audio.currentTime = total() * barra.value / 1000; });
  mostra();
  $("#player").hidden = false;
}

// Os personagens do "como funciona", desenhados pelo mesmo código do estúdio
// (/estudio/sprites.js). Animam só enquanto aparecem na tela, e não animam para
// quem pediu menos movimento. Se o módulo não carregar, os cartões ficam só com texto.
async function avatares() {
  const { sprite, quadroNoTempo } = await import("/estudio/sprites.js");
  const itens = [...document.querySelectorAll(".passos li[data-persona]")];
  const parado = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const desenha = (li, t, i) => {
    const cv = li.querySelector(".avatar"), ctx = cv.getContext("2d");
    const estado = li.dataset.estado || "parado";
    ctx.clearRect(0, 0, cv.width, cv.height);
    ctx.drawImage(sprite(li.dataset.persona, estado, parado ? 0 : quadroNoTempo(estado, t, i, li.dataset.persona)), 0, 0);
  };
  itens.forEach((li, i) => desenha(li, 0, i));
  $(".passos").classList.add("com-avatar");
  if (parado) return;
  let visivel = false;
  new IntersectionObserver(e => { visivel = e[0].isIntersecting; }).observe($(".passos"));
  const anima = t => { if (visivel) itens.forEach((li, i) => desenha(li, t, i)); requestAnimationFrame(anima); };
  requestAnimationFrame(anima);
}

$("#rss-copiar").addEventListener("click", async e => {
  const url = $("#rss-url").textContent.trim();
  try { await navigator.clipboard.writeText(url); e.target.textContent = "Copiado"; }
  catch { getSelection().selectAllChildren($("#rss-url")); e.target.textContent = "Selecionado"; }
  setTimeout(() => { e.target.textContent = "Copiar"; }, 2500);
});

// Fale com o estúdio. Até o envio de verdade (etapa S4 do docs/site.md), o
// botão abre o e-mail de quem visita com o tema pronto; o limite de 500
// caracteres é porque alguns aplicativos cortam mensagens longas vindas de link.
const tema = $("#fale-tema"), resposta = $("#fale-resposta");
tema.addEventListener("input", () => { $("#fale-conta").textContent = `${num(tema.value.length)} / ${num(500)}`; });
$("#fale-form").addEventListener("submit", e => {
  e.preventDefault();
  const txt = tema.value.trim();
  resposta.hidden = false;
  if (!txt) {
    resposta.classList.add("erro");
    resposta.textContent = "Escreva o tema antes de enviar.";
    tema.focus();
    return;
  }
  resposta.classList.remove("erro");
  const q = new URLSearchParams({ subject: "Sugestão de tema para o CampsCast", body: `Tema: ${txt}\n` }).toString().replace(/\+/g, "%20");
  location.href = `mailto:contato@campscast.com.br?${q}`;
  resposta.textContent = "Abrimos o seu e-mail com a sugestão pronta; falta só enviar por lá. Se nada abriu, escreva para contato@campscast.com.br.";
});

carrega().catch(err => console.warn("capa sem dados do estúdio:", err.message));
avatares().catch(err => console.warn("capa sem os personagens:", err.message));
