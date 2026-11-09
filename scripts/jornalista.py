#!/usr/bin/env python3
"""
CampsCast — o Jornalista: subagente que lê as páginas para o agente principal.

Plano em docs/plano-leitura-por-subagente.md. Com JORNALISTA=1, o
orquestrador passa ao CLI duas coisas que saem daqui e acrescenta ao prompt do
agente principal `prompts/leitura-pelo-jornalista.md`:

    agentes --modelo M   o JSON do --agents: o Jornalista, com o prompt de
                         prompts/jornalista.md, o modelo M, WebFetch e Read
    hook                 o JSON do --settings: um hook PreToolUse que barra o
                         WebFetch de quem não for o Jornalista
    barra                o hook em si: lê a chamada no stdin; sai 2 para barrar

Medido em 08/11/2026, no CLI 2.1.283:
- o `--tools` tira a ferramenta também dos subagentes: com o WebFetch fora
  do agente principal, o Jornalista nasceu sem ferramenta e não rodou. Daí o
  hook, que distingue os dois pelo `agent_id` (só vem quando quem chama é um
  subagente) e pelo `agent_type`;
- o WebFetch do Jornalista devolve o resumo do modelo pequeno do CLI, como o
  do agente principal até 04/11. A página crua só chega ao "web-fetch"
  embutido: no código do CLI, `isBuiltIn` e o nome "web-fetch" (ADR 0013);
- subagente que não é o embutido roda em segundo plano, a menos que a chamada
  peça o contrário; o `-p` espera os relatórios chegarem antes de terminar.

O hook não pode derrubar a pesquisa do dia: entrada que não se entende passa.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shlex
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from transcricoes import BARRADA  # noqa: E402

NOME = "jornalista"
PROMPT = ROOT / "prompts" / "jornalista.md"
DESCRICAO = ("Lê páginas da web para o CampsCast. Recebe endereços, a janela de notícias e o que se precisa "
             "de cada página; devolve, por endereço lido, o resultado (200, 403…), a data de publicação, o "
             "tipo de fonte, os fatos com números, as citações literais e uma nota para o log de pesquisa. "
             "Tenta sozinho as outras portas de uma página fechada. É a única forma de ler páginas nesta "
             "execução.")
# A frase volta ao agente principal como resposta do WebFetch barrado; o
# pedaço BARRADA é o que as medições procuram para não contá-la.
MOTIVO = (f"Nesta execução as páginas são {BARRADA}. Chame a ferramenta Agent com subagent_type "
          f'"{NOME}", os endereços, a janela e o que você precisa de cada página; um pedido por vez, '
          "o próximo depois que o relatório do anterior chegar.")


def agentes(modelo: str) -> dict:
    return {NOME: {
        "description": DESCRICAO,
        "prompt": PROMPT.read_text(encoding="utf-8"),
        "tools": ["WebFetch", "Read"],
        "model": modelo,
        # Teto de voltas por pedido: um pedido de seis endereços, com portas
        # fechadas e cópias do arquivo, cabe com folga.
        "maxTurns": 25,
        # O CLAUDE.md é para quem mexe no código, não para quem lê notícia.
        "omitClaudeMd": True,
    }}


def hook() -> dict:
    cmd = f"python3 {shlex.quote(str(pathlib.Path(__file__).resolve()))} barra"
    return {"hooks": {"PreToolUse": [{"matcher": "WebFetch", "hooks": [{"type": "command", "command": cmd}]}]}}


def barra(entrada: str) -> int:
    try:
        d = json.loads(entrada)
    except ValueError:
        return 0
    if not isinstance(d, dict) or d.get("tool_name") != "WebFetch":
        return 0
    if d.get("agent_id") and d.get("agent_type") == NOME:
        return 0
    print(MOTIVO, file=sys.stderr)
    return 2


def main() -> int:
    ap = argparse.ArgumentParser(description="O Jornalista do CampsCast (plano de leitura).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("agentes")
    a.add_argument("--modelo", required=True)
    sub.add_parser("hook")
    sub.add_parser("barra")
    args = ap.parse_args()
    if args.cmd == "agentes":
        print(json.dumps(agentes(args.modelo), ensure_ascii=False))
        return 0
    if args.cmd == "hook":
        print(json.dumps(hook(), ensure_ascii=False))
        return 0
    return barra(sys.stdin.read())


if __name__ == "__main__":
    sys.exit(main())
