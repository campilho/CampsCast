#!/usr/bin/env python3
"""
CampsCast — páginas do roteiro e do log de pesquisa para o site.

Até 03/11 o "Ler o roteiro" e o "log de pesquisa" do site iam para o arquivo
no GitHub, que só existe depois do commit da noite: das 05:15 até lá davam
404. O estudio.py chama este módulo e grava uma cópia de cada um em
site/estudio/roteiros/ e site/estudio/pesquisa/, e o publica_site.py sobe
junto com os dados do dia.

O conversor de Markdown é nosso, sem dependências, e cobre só o que os logs
usam: títulos, parágrafos, listas com continuação e aninhamento, negrito,
código e endereços soltos. Tudo o que vem do texto é escapado: o log traz
títulos e trechos de páginas de fora.
"""
from __future__ import annotations

import datetime as dt
import html
import re

URL = re.compile(r"https?://[^\s<>\"'`]+")
ITEM = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")
TITULO = re.compile(r"^(#{1,6})\s+(.*)$")
DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def _endereco(url: str) -> str:
    # Pontuação colada no fim é da frase, não do endereço; o ")" só fica se
    # fechar um "(" do próprio endereço.
    while url and (url[-1] in ".,;:!?" or (url[-1] == ")" and url.count("(") < url.count(")"))):
        url = url[:-1]
    return url


def _texto(t: str) -> str:
    partes, i = [], 0
    for m in URL.finditer(t):
        url = _endereco(m.group(0))
        if not url:
            continue
        partes.append(re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(t[i:m.start()])))
        partes.append(f'<a href="{esc(url)}">{esc(url)}</a>')
        i = m.start() + len(url)
    partes.append(re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(t[i:])))
    return "".join(partes)


def inline(t: str) -> str:
    return "".join(f"<code>{esc(p[1:-1])}</code>" if len(p) > 1 and p[0] == p[-1] == "`" else _texto(p)
                   for p in re.split(r"(`[^`]+`)", t))


def _lista(itens: list[tuple[int, str, str]], i: int = 0) -> tuple[str, int]:
    """Os itens a partir de i com o mesmo recuo; os de recuo maior entram no item anterior."""
    recuo, tag = itens[i][0], itens[i][1]
    partes = [f"<{tag}>"]
    while i < len(itens) and itens[i][0] == recuo:
        texto = inline(itens[i][2])
        i += 1
        filhos = ""
        while i < len(itens) and itens[i][0] > recuo:
            h, i = _lista(itens, i)
            filhos += h
        partes.append(f"<li>{texto}{filhos}</li>")
    partes.append(f"</{tag}>")
    return "".join(partes), i


def md_html(md: str) -> str:
    blocos, para, itens = [], [], []

    def fecha():
        if para:
            blocos.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()
        i = 0
        while i < len(itens):
            h, i = _lista(itens, i)
            blocos.append(h)
        itens.clear()

    for linha in md.splitlines():
        if not linha.strip():
            fecha()
        elif m := TITULO.match(linha):
            fecha()
            n = len(m.group(1))
            blocos.append(f"<h{n}>{inline(m.group(2).strip())}</h{n}>")
        elif m := ITEM.match(linha):
            if para:
                fecha()
            itens.append((len(m.group(1).expandtabs(2)), "ol" if m.group(2)[0].isdigit() else "ul", m.group(3).strip()))
        elif itens:
            # Continuação do item aberto, recuada ou não.
            r, tag, texto = itens[-1]
            itens[-1] = (r, tag, f"{texto} {linha.strip()}")
        else:
            para.append(linha.strip())
    fecha()
    return "\n".join(blocos)


def pagina(titulo: str, descricao: str, corpo: str) -> str:
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(titulo)} · CampsCast</title>
<meta name="description" content="{esc(descricao)}">
<meta name="theme-color" content="#07090c">
<link rel="stylesheet" href="/fontes/fontes.css">
<link rel="stylesheet" href="/capa/capa.css">
</head>
<body>

<header class="nav gutter">
  <div class="largura nav-linha">
    <a class="marca" href="/" aria-label="CampsCast, início"><span class="cc" aria-hidden="true">&gt;CC<i></i></span><strong>CampsCast</strong></a>
    <nav aria-label="Principal">
      <a class="nav-link" href="/">Início</a>
      <a class="nav-link" href="/sugestao/">Sugerir</a>
      <a class="btn btn-crt btn-p" href="/estudio/">Estúdio</a>
    </nav>
  </div>
</header>

<main class="gutter">
  <article class="texto">
{corpo}
  </article>
</main>

<footer class="rodape gutter">
  <div class="largura">
    <p><span class="cc cc-p" aria-hidden="true">&gt;CC</span> CampsCast, de Fernando Campilho · <a href="mailto:contato@campscast.com.br">contato@campscast.com.br</a></p>
    <p>Código em <a href="https://github.com/campilho/CampsCast">github.com/campilho/CampsCast</a>. Sem cookies e sem rastreamento.</p>
  </div>
</footer>
</body>
</html>
"""


def _dia(data: str) -> str:
    d = dt.date.fromisoformat(data)
    return f"{DIAS[d.weekday()].capitalize()}, {d:%d/%m/%Y}"


def roteiro(data: str, ep: dict, com_pesquisa: bool) -> str:
    """Página do roteiro, a partir do episódio que o estudio.py já leu."""
    janela = ep.get("janela") or [None, None]
    meta = [_dia(data)]
    if janela[0] and janela[1]:
        meta.append(f"notícias de {janela[0][8:10]}/{janela[0][5:7]} a {janela[1][8:10]}/{janela[1][5:7]}")
    if ep.get("palavras"):
        meta.append(f"{ep['palavras']:,} palavras".replace(",", "."))
    botoes = [f'<a class="btn btn-crt btn-p" href="{esc(ep["mp3"])}">Ouvir</a>'] if ep.get("mp3") else []
    if com_pesquisa:
        botoes.append(f'<a class="btn btn-linha btn-p" href="/estudio/pesquisa/{data}.html">Log de pesquisa</a>')
    botoes.append('<a class="btn btn-linha btn-p" href="/estudio/">Ver a gravação</a>')
    fontes = "".join(
        f'<li><b>{esc(p["titulo"])}</b>' + (f'<br><a href="{esc(p["url"])}">{esc(p["url"])}</a>' if p.get("url") else "")
        + "</li>" for p in ep.get("pautas") or [])
    corpo = "\n".join([
        f'    <p class="rotulo">Roteiro · episódio {ep.get("numero", "")}</p>',
        f'    <h1>{esc(ep.get("titulo", ""))}</h1>',
        f'    <p class="nota">{esc(" · ".join(meta))}</p>',
        f'    <p class="botoes">{" ".join(botoes)}</p>',
        *(f"    <p>{esc(p)}</p>" for p in ep.get("roteiro") or []),
        *([f"    <h2>Fontes</h2>\n    <ol>{fontes}</ol>"] if fontes else []),
        f'    <p class="nota">O texto que o Locutor narrou, como o agente escreveu, no arquivo '
        f'<code>episodes/{data}.md</code> do projeto.</p>',
    ])
    return pagina(f"Roteiro do episódio {ep.get('numero', '')}", ep.get("titulo", ""), corpo)


def pesquisa(data: str, md: str, numero: int | str = "") -> str:
    """Página do log de pesquisa, com o Markdown que o agente escreveu."""
    corpo = "\n".join([
        f'    <p class="rotulo">Log de pesquisa · episódio {numero}</p>',
        md_html(md),
        f'    <p class="botoes"><a class="btn btn-linha btn-p" href="/estudio/roteiros/{data}.html">Ler o roteiro</a> '
        '<a class="btn btn-linha btn-p" href="/estudio/">Ver a gravação</a></p>',
        f'    <p class="nota">O que o Jornalista leu, buscou e decidiu, como o agente escreveu, no arquivo '
        f'<code>research/{data}.md</code> do projeto.</p>',
    ])
    return pagina(f"Log de pesquisa do episódio {numero}", f"O que o agente leu e decidiu para o episódio de {_dia(data)}.",
                  corpo)
