#!/usr/bin/env python3
"""
CampsCast — confere se alguma pauta do dia repete uma pauta antiga: pelo link,
ou pelo fio que volta no episódio seguinte.

Para não repetir pauta, o agente recebe no prompt a lista do que já foi ao ar
(scripts/pautas.py). Quando essa lista tiver teto de 90 dias (ADR 0008), o que
for mais antigo só aparece se o agente buscar no índice. Esta conferência é a
rede de segurança determinística: compara o link de cada pauta do roteiro com
o de todas as pautas anteriores do covered-index.json.

Não bloqueia. Desdobramento legítimo costuma ter fonte nova; link igual merece
um olhar. As pautas do próprio dia já foram acrescentadas ao índice pelo agente
e ficam fora da comparação.

O link é comparado sem esquema, sem "www.", sem barra no fim e sem parâmetros.
Página de listagem — um changelog, a página de notícias de um laboratório —
fica de fora: serve de fonte para notícias diferentes em dias diferentes, e na
primeira passada sobre os 26 episódios foi o único aviso, falso.

A segunda conferência é a do fio que volta no episódio seguinte. Em 26/11 a
prova de Riemann abriu o segundo episódio seguido (61 e 62), por um
desdobramento que não respondia à pergunta do fio F-047 (sai versão legível por
gente?), e a matemática feita por IA abriu três seguidos. O prompt proíbe
repetir pauta "salvo desdobramento novo", sem tamanho mínimo. Daí o aviso:
fio (aberto, fechado ou expirado) com acontecimento no episódio de hoje e no
anterior, com a pauta que o carregou (a nota do covered-index cita o fio) e se
ela abriu o episódio. Conta episódio, não dia: a segunda vem depois da sexta.
Na primeira passada, sobre os 62 episódios até 26/11, foram 12 pares, 6 deles
nos episódios 58 a 62; em 3 a pauta abriu os dois. Quando a nota não cita o
fio, o aviso diz que não se sabe a pauta (2 dos 12). Repetição que não passa
por fio nem por link não aparece aqui.

Uso:
    python3 scripts/confere_repeticao.py episodes/2026-10-05.md --data 2026-10-05 \
        [--indice covered-index.json] [--fios memoria/fios.md]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent


# Último trecho do caminho que indica página de listagem, não de notícia.
LISTAGENS = {"changelog", "news", "newsroom", "blog", "research", "releases",
             "updates", "index", "announcements", "press"}


def normaliza(url: str) -> str:
    p = urllib.parse.urlparse((url or "").strip())
    host = p.netloc.lower().removeprefix("www.")
    return f"{host}{p.path.rstrip('/')}" if host else ""


def links_do_roteiro(texto: str) -> list[str]:
    if not texto.startswith("---"):
        return []
    cabecalho = texto.split("---", 2)[1]
    return [m.strip().strip("\"'") for m in re.findall(r"source_url:\s*(\S+)", cabecalho)]


def confere(roteiro: str, itens: list[dict], data: str) -> list[str]:
    anteriores: dict[str, dict] = {}
    for i in itens:
        if str(i.get("episode", "")) < data:
            chave = normaliza(i.get("source_url", ""))
            if chave:
                anteriores.setdefault(chave, i)
    avisos = []
    for url in links_do_roteiro(roteiro):
        chave = normaliza(url)
        if not chave or chave.rsplit("/", 1)[-1] in LISTAGENS or "/" not in chave:
            continue
        antiga = anteriores.get(chave)
        if antiga:
            avisos.append(f"repetição: link já usado em {antiga.get('episode')}: "
                          f"{str(antiga.get('title', ''))[:70]} ({url})")
    return avisos


# "- aberto: 2026-11-25 (ep. 61)", "  - 2026-11-26 (ep. 62) — ...", "- fechado: ..."
ACONTECIMENTO = re.compile(r"^\s*-\s+(aberto:\s*|fechado:\s*)?(\d{4}-\d{2}-\d{2}) \(ep\. (\d+)\)", re.M)


def fios(ativos: pathlib.Path) -> dict[str, tuple[str, dict[int, tuple[str, str]]]]:
    """F-NNN -> (título, {episódio: (data, "aberto" | "marco" | "fechado")}),
    dos fios em aberto e dos que moram ao lado, em fios-fechados/ e
    fios-expirados/."""
    arquivos = [ativos, *sorted(ativos.parent.glob("fios-fechados/*.md")),
                *sorted(ativos.parent.glob("fios-expirados/*.md"))]
    saida: dict[str, tuple[str, dict[int, tuple[str, str]]]] = {}
    for arq in arquivos:
        try:
            texto = arq.read_text(encoding="utf-8")
        except OSError:
            continue
        for bloco in re.split(r"(?m)^(?=## F-\d+)", texto):
            m = re.match(r"## (F-\d+)\s*·\s*(.*)", bloco)
            if not m:
                continue
            eventos = {int(n): (d, (tipo.split(":")[0] or "marco"))
                       for tipo, d, n in ACONTECIMENTO.findall(bloco)}
            saida[m[1]] = (m[2].strip(), eventos)
    return saida


def episodio(texto: str) -> int | None:
    m = re.search(r"^episode:\s*(\d+)\s*$", texto.split("---", 2)[1] if texto.startswith("---") else "", re.M)
    return int(m[1]) if m else None


def pauta_do_fio(fio: str, data: str, itens: list[dict], links: list[str] | None) -> str:
    """"abriu", "dentro" (outra posição) ou "" quando a nota do índice daquele
    dia não cita o fio; sem o roteiro do dia para saber a ordem, "dentro"."""
    cita = re.compile(rf"\b{re.escape(fio)}\b")
    do_fio = [normaliza(i.get("source_url", "")) for i in itens
              if str(i.get("episode", "")) == data
              and cita.search(" ".join(str(i.get(k, "")) for k in ("note", "summary", "title")))]
    if not do_fio:
        return ""
    return "abriu" if links and normaliza(links[0]) in do_fio else "dentro"


def seguidas(roteiro: str, itens: list[dict], data: str, ativos: pathlib.Path,
             episodios: pathlib.Path) -> list[str]:
    """Fio com acontecimento hoje e no episódio anterior."""
    n = episodio(roteiro)
    if n is None:
        return []
    avisos = []
    for fio, (titulo, eventos) in sorted(fios(ativos).items()):
        if n not in eventos or n - 1 not in eventos:
            continue
        data_antes = eventos[n - 1][0]
        try:
            links_antes = links_do_roteiro((episodios / f"{data_antes}.md").read_text(encoding="utf-8"))
        except OSError:
            links_antes = None
        hoje = pauta_do_fio(fio, data, itens, links_do_roteiro(roteiro))
        antes = pauta_do_fio(fio, data_antes, itens, links_antes)
        if not hoje:
            como = "; a nota do índice de hoje não diz em que pauta"
        elif hoje == "abriu" and antes == "abriu":
            como = ", e a pauta abriu os dois episódios"
        elif hoje == "abriu":
            como = ", e a pauta abriu o de hoje"
        elif antes == "abriu":
            como = ", e a pauta tinha aberto o anterior"
        else:
            como = ""
        if eventos[n][1] == "fechado":
            como += "; o fio fechou hoje"
        if len(titulo) > 60:
            titulo = titulo[:60].rsplit(" ", 1)[0].rstrip(",:;") + "…"
        avisos.append(f"repetição: {fio} ({titulo}) volta do episódio anterior ({n - 1}){como}")
    return avisos


def main() -> int:
    ap = argparse.ArgumentParser(description="Confere repetição de pauta por link e por fio.")
    ap.add_argument("roteiro")
    ap.add_argument("--data", required=True)
    ap.add_argument("--indice", default=str(ROOT / "covered-index.json"))
    ap.add_argument("--fios", default=str(ROOT / "memoria" / "fios.md"),
                    help="fios em aberto; os fechados e expirados são lidos das pastas ao lado")
    a = ap.parse_args()
    try:
        roteiro = pathlib.Path(a.roteiro).read_text(encoding="utf-8")
        itens = json.loads(pathlib.Path(a.indice).read_text(encoding="utf-8")).get("items", [])
    except (OSError, ValueError) as e:
        print(f"repetição: não foi possível conferir ({e})")
        return 0
    for aviso in confere(roteiro, itens, a.data):
        print(aviso)
    for aviso in seguidas(roteiro, itens, a.data, pathlib.Path(a.fios),
                          pathlib.Path(a.roteiro).resolve().parent):
        print(aviso)
    return 0


if __name__ == "__main__":
    sys.exit(main())
