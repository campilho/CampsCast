#!/usr/bin/env python3
"""
CampsCast — lista compacta de tudo que já foi ao ar, uma linha por pauta.

O agente precisa saber o que já foi coberto para não repetir pauta. Até 02/10
isso vinha de ler o covered-index.json inteiro, e o arquivo deixou de caber: a
ferramenta Read do Claude Code recusa mais de 25 mil tokens por chamada, e cada
pauta passou de ~750 bytes para 3 a 5 KB de resumo e notas. Medido nas
transcrições: o Opus 5 lia em quatro ou cinco pedaços; o Opus 5.5, em quatro de
cinco dias, leu só o começo, um Grep dos títulos e o fim — o meio do período
ficava fora da memória.

Para não repetir, bastam data, título e fonte. Esta lista é derivada do índice
a cada execução, não armazenada: se fosse um arquivo mantido à parte, as duas
cópias acabariam divergindo. O orquestrador a escreve no prompt, ao lado dos
parâmetros, para que chegue inteira todo dia sem depender de o agente ler.

O detalhe continua no covered-index.json, consultado por busca quando uma
candidata parecer ligada a algo da lista. A última linha diz onde o índice
termina, porque o Edit só aceita arquivo lido na sessão: o agente lê o final e
acrescenta as pautas do dia ali.

PAUTAS_INDICE troca o arquivo — é o que o smoke test usa.

Uso:
    python3 scripts/pautas.py
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDICE = ROOT / "covered-index.json"
# Linhas do fim do índice que o agente lê antes de acrescentar: o bastante para
# pegar a última pauta inteira e o fechamento da lista.
FOLGA_LEITURA = 40


def dominio(url: str) -> str:
    host = urllib.parse.urlparse(url or "").netloc
    return host.removeprefix("www.") or "sem fonte"


def texto(indice: pathlib.Path | None = None) -> str:
    indice = indice or pathlib.Path(os.environ.get("PAUTAS_INDICE") or INDICE)
    conteudo = indice.read_text(encoding="utf-8")
    itens = json.loads(conteudo).get("items", [])
    linhas = [f"- {i.get('episode', '?')} | {i.get('title', '?').strip()} | "
              f"{dominio(i.get('source_url', ''))}" for i in itens]
    total_linhas = conteudo.count("\n") + (0 if conteudo.endswith("\n") else 1)
    inicio = max(1, total_linhas - FOLGA_LEITURA)
    linhas.append("")
    linhas.append(f"{len(itens)} pautas. O covered-index.json tem {total_linhas} "
                  f"linhas: para acrescentar as de hoje, leia a partir da linha "
                  f"{inicio}.")
    return "\n".join(linhas)


if __name__ == "__main__":
    try:
        print(texto())
    except (OSError, ValueError) as e:
        print(f"pautas.py: {e}", file=sys.stderr)
        sys.exit(1)
