#!/usr/bin/env python3
"""
CampsCast — mudanças no próprio podcast a anunciar na abertura.

Quando algo muda no programa — o modelo que escreve, a voz, um requisito novo —
quem ouve de vez em quando merece saber. Uma frase só, na abertura, durante uma
janela de dias. A janela tem data de fim no próprio arquivo para o anúncio
sumir sozinho: aviso que ninguém lembra de tirar vira ruído no terceiro mês.

Lê config/novidades.json e imprime o que está ativo numa data. Vazio quando não
há nada; o orquestrador passa o resultado ao agente em NOVIDADES.

NOVIDADES_ARQ troca o arquivo — é o que o smoke test usa, para não depender
do conteúdo real, que muda e expira.

Uso:
    python3 scripts/novidades.py 2026-09-28
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ARQUIVO = ROOT / "config" / "novidades.json"


def ativas(data: str, arquivo: pathlib.Path | None = None) -> list[dict]:
    """Novidades cuja janela contém a data. Datas ISO comparam como texto."""
    arquivo = arquivo or pathlib.Path(os.environ.get("NOVIDADES_ARQ") or ARQUIVO)
    try:
        itens = json.loads(arquivo.read_text(encoding="utf-8")).get("novidades", [])
    except FileNotFoundError:
        return []
    return [i for i in itens if i["desde"] <= data <= i["ate"]]


def texto(data: str, arquivo: pathlib.Path | None = None) -> str:
    linhas = []
    for i in ativas(data, arquivo):
        quando = ("primeiro dia do anúncio" if data == i["desde"]
                  else f"anúncio em curso desde {i['desde']}")
        linhas.append(f"- {i['fato']} ({quando}). Como dizer: {i.get('como_dizer', '')}")
    return "\n".join(linhas)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        sys.exit(2)
    print(texto(sys.argv[1]))
