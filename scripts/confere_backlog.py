#!/usr/bin/env python3
"""
CampsCast — confere se o backlog guarda só pauta ativa.

Até 02/10 o agente mantinha, dentro do próprio saved-items/backlog.md, o
registro de tudo que saía — "Podados na execução de…", "Saiu na execução
de…". Ninguém pediu; o prompt só mandava podar os vencidos. Eram 28 dos 39 KB
do arquivo, relidos a cada execução. O histórico foi para
saved-items/historico/AAAA-MM.md, e o prompt diz onde cada saída é anotada.

Este script confere o resultado depois da execução. Não bloqueia: imprime uma
linha por problema, e o orquestrador grava no registro junto com os avisos do
roteiro. Dois problemas:

- item com validade anterior à data do episódio, que deveria ter sido podado;
- texto fora do formato de item depois do cabeçalho — sinal de que o
  histórico voltou para dentro do arquivo.

O cabeçalho vai até a primeira linha "---"; dali em diante, cada item começa
em "## " e só tem campos ("- ") e continuação recuada.

Uso:
    python3 scripts/confere_backlog.py saved-items/backlog.md --data 2026-10-05
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

VALIDADE = re.compile(r"^- validade:\s*(\d{4}-\d{2}-\d{2})")


def confere(texto: str, data: str) -> list[str]:
    linhas = texto.splitlines()
    try:
        inicio = linhas.index("---") + 1
    except ValueError:
        inicio = 0
    avisos, fora = [], []
    titulo = None
    for linha in linhas[inicio:]:
        if linha.startswith("## "):
            titulo = linha[3:].strip()
            continue
        if not linha.strip():
            continue
        if titulo and (linha.startswith("- ") or linha.startswith("  ")):
            m = VALIDADE.match(linha)
            if m and m[1] < data:
                avisos.append(f"backlog: item vencido em {m[1]} continua no arquivo: {titulo[:70]}")
            continue
        fora.append(linha)
        titulo = None   # o que vem depois de texto solto não é mais item
    if fora:
        primeira = next((l for l in fora if l.strip() != "---"), fora[0])
        avisos.append(f"backlog: {len(fora)} linhas fora do formato de item, a primeira: "
                      f"{primeira.strip()[:70]}")
    return avisos


def main() -> int:
    ap = argparse.ArgumentParser(description="Confere o backlog depois da execução.")
    ap.add_argument("arquivo")
    ap.add_argument("--data", required=True, help="data do episódio (AAAA-MM-DD)")
    a = ap.parse_args()
    try:
        texto = pathlib.Path(a.arquivo).read_text(encoding="utf-8")
    except OSError as e:
        print(f"backlog: não foi possível ler ({e})")
        return 0
    for aviso in confere(texto, a.data):
        print(aviso)
    return 0


if __name__ == "__main__":
    sys.exit(main())
