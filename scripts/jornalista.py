#!/usr/bin/env python3
"""
CampsCast — o Jornalista: subagente que lê as páginas para o agente principal.

Plano em docs/plano-leitura-por-subagente.md. Com JORNALISTA=1, o
orquestrador passa ao CLI duas coisas que saem daqui e acrescenta ao prompt do
agente principal `prompts/leitura-pelo-jornalista.md`:

    agentes --modelo M   o JSON do --agents: o Jornalista, com o prompt de
                         prompts/jornalista.md, o modelo M, WebFetch e Read
    hook                 o JSON do --settings: dois hooks PreToolUse, um que
                         barra o WebFetch de quem não for o Jornalista e outro
                         que põe os pedidos a ele em primeiro plano
    barra                o primeiro: lê a chamada no stdin; sai 2 para barrar
    espera               o segundo (1.2): devolve o pedido com
                         run_in_background false

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

Medido em 09/11/2026, no mesmo CLI, com um subagente de teste: com
`run_in_background: false`, o relatório volta como resposta da ferramenta; e um
hook PreToolUse que devolve `updatedInput` com esse campo vence o `true` que o
modelo pediu (a transcrição guarda o pedido original).

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
          f'"{NOME}", run_in_background false, os endereços, a janela e o que você precisa de cada '
          "página; o relatório volta como resposta da chamada.")


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
    """Dois ganchos antes de cada ferramenta: `barra` tira o WebFetch do agente
    principal, e `espera` (1.2) põe todo pedido ao Jornalista em primeiro plano."""
    base = f"python3 {shlex.quote(str(pathlib.Path(__file__).resolve()))}"
    gancho = lambda ferramenta, sub: {"matcher": ferramenta,
                                      "hooks": [{"type": "command", "command": f"{base} {sub}"}]}
    return {"hooks": {"PreToolUse": [gancho("WebFetch", "barra"), gancho("Agent", "espera")]}}


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


def espera(entrada: str) -> str | None:
    """Pedido ao Jornalista sem `run_in_background: false` → a entrada corrigida,
    no formato que o CLI aceita de um hook PreToolUse (`updatedInput`).

    Em segundo plano, o padrão do CLI 2.1.283 para subagente nosso, cada
    relatório chega numa notificação: o Editor segue trabalhando enquanto isso
    (no ensaio da 1.1, buscou o dobro na web) e cada notificação entra no cache
    como texto novo. Em primeiro plano, o relatório é a resposta da chamada. O
    prompt pede isso; o hook garante. A transcrição guarda o pedido como o
    Editor o fez, sem a correção."""
    try:
        d = json.loads(entrada)
    except ValueError:
        return None
    if not isinstance(d, dict) or d.get("tool_name") != "Agent":
        return None
    pedido = d.get("tool_input")
    if not isinstance(pedido, dict) or pedido.get("subagent_type") != NOME:
        return None
    if pedido.get("run_in_background") is False:
        return None
    return json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                              "updatedInput": {**pedido, "run_in_background": False}}},
                      ensure_ascii=False)


def main() -> int:
    ap = argparse.ArgumentParser(description="O Jornalista do CampsCast (plano de leitura).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("agentes")
    a.add_argument("--modelo", required=True)
    sub.add_parser("hook")
    sub.add_parser("barra")
    sub.add_parser("espera")
    args = ap.parse_args()
    if args.cmd == "agentes":
        print(json.dumps(agentes(args.modelo), ensure_ascii=False))
        return 0
    if args.cmd == "hook":
        print(json.dumps(hook(), ensure_ascii=False))
        return 0
    if args.cmd == "espera":
        saida = espera(sys.stdin.read())
        if saida:
            print(saida)
        return 0
    return barra(sys.stdin.read())


if __name__ == "__main__":
    sys.exit(main())
