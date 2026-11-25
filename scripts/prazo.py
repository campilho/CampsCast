#!/usr/bin/env python3
"""
CampsCast — roda um comando com prazo, contado em tempo de Mac acordado.

O agente não tinha prazo. Um agente travado prende o job do launchd, e
enquanto o job roda as repescagens das 06:00 e 07:00 não disparam. O prazo
conta só o tempo em que o Mac está acordado: time.monotonic, que no macOS é o
mach_absolute_time e para durante o sono. As execuções longas medidas até
25/11 eram o Mac dormindo, não o agente travado: em 28/10, 266 dos 267 minutos
de pesquisa foram sono; em 11/11, 97 de 110, e aquela terminou bem e foi ao
ar. Um prazo de relógio teria matado a de 11/11 à toa. A pesquisa mais longa
acordada foi a de 23/11, 21 minutos, com dez deles presos em duas páginas.

Passado o prazo, o grupo de processos do comando recebe SIGTERM e, 15 s
depois, SIGKILL, e a saída é 124, como a do timeout do GNU. SIGTERM, SIGINT e
SIGHUP recebidos aqui vão para o grupo inteiro. Entrada, saída padrão e saída
de erro passam direto.

Uso:
    python3 scripts/prazo.py SEGUNDOS comando [argumentos...]
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time

ESTOUROU = 124
CARENCIA_S = 15


def encerra(p: subprocess.Popen) -> None:
    try:
        os.killpg(p.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        p.wait(timeout=CARENCIA_S)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        p.wait()


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__.strip().splitlines()[-1].strip(), file=sys.stderr)
        return 2
    prazo = float(argv[0])
    comando = argv[1:]
    # Grupo de processos próprio: o claude abre filhos (node, ripgrep, servidores
    # MCP), e o prazo tem de levar todos.
    p = subprocess.Popen(comando, start_new_session=True)

    def repassa(sinal, _quadro):
        try:
            os.killpg(p.pid, sinal)
        except ProcessLookupError:
            pass

    for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(s, repassa)

    fim = time.monotonic() + prazo
    while True:
        falta = fim - time.monotonic()
        if falta <= 0:
            break
        try:
            rc = p.wait(timeout=min(5.0, falta))
            return rc if rc >= 0 else 128 - rc
        except subprocess.TimeoutExpired:
            continue
    quanto = f"{prazo / 60:.0f} min" if prazo >= 120 else f"{prazo:.0f} s"
    print(f"prazo: {os.path.basename(comando[0])} passou de {quanto} de Mac acordado; encerrando",
          file=sys.stderr)
    encerra(p)
    return ESTOUROU


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
