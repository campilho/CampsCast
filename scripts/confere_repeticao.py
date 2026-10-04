#!/usr/bin/env python3
"""
CampsCast — confere se alguma pauta do dia repete o link de uma pauta antiga.

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

Uso:
    python3 scripts/confere_repeticao.py episodes/2026-10-05.md --data 2026-10-05
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


def main() -> int:
    ap = argparse.ArgumentParser(description="Confere repetição de pauta por link.")
    ap.add_argument("roteiro")
    ap.add_argument("--data", required=True)
    ap.add_argument("--indice", default=str(ROOT / "covered-index.json"))
    a = ap.parse_args()
    try:
        roteiro = pathlib.Path(a.roteiro).read_text(encoding="utf-8")
        itens = json.loads(pathlib.Path(a.indice).read_text(encoding="utf-8")).get("items", [])
    except (OSError, ValueError) as e:
        print(f"repetição: não foi possível conferir ({e})")
        return 0
    for aviso in confere(roteiro, itens, a.data):
        print(aviso)
    return 0


if __name__ == "__main__":
    sys.exit(main())
