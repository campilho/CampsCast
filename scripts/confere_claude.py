#!/usr/bin/env python3
"""
CampsCast — vigia do Claude Code: experimentos da Anthropic e o que a sessão fez.

De 05 a 08/11/2026 um experimento da Anthropic (o interruptor remoto
`tengu_clever_orbit`) tirou o WebFetch do agente e pôs no lugar um subagente
"web-fetch", sem mudança de versão do CLI. O episódio ficou 57% mais caro e as
medições ficaram cegas; ninguém viu por quatro dias (ADR 0013). O orquestrador
agora fixa CLAUDE_CODE_WEB_FETCH_AGENT=0, e este script avisa se o experimento
voltar, mesmo com a variável no lugar. Registra, não bloqueia.

    antes    o estado dos interruptores vigiados no cache do CLI (~/.claude.json)
             e quais interruptores mudaram desde a execução anterior.
    depois   o que a sessão de fato fez, pela transcrição: chamadas ao subagente
             web-fetch, página crua no lugar do resumo, modelo inesperado.

O cache é só indício: em 08/11 ele dizia "desligado" enquanto uma sessão aberta
recebia o subagente. Quem confirma é o "depois".

Avisos saem no stdout, um por linha, e vão para o registro (e daí para o
relatório da semana). O resto sai no stderr, que o orquestrador põe no log.

CLAUDE_JSON e INTERRUPTORES_ARQ trocam o cache do CLI e a foto da execução
anterior; TRANSCRICOES_DIR, a pasta das transcrições. É o que o smoke test usa.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Interruptor vigiado → o que ele faz. Entra aqui todo experimento que já mexeu
# no podcast; o nome vem do próprio CLI (strings do binário e o cache).
VIGIADOS = {
    "tengu_clever_orbit": "subagente web-fetch no lugar do WebFetch, de 05 a 08/11/2026; ADR 0013",
}
# O modelo "pequeno" do CLI resume as páginas do WebFetch e faz as buscas.
# Trocar de modelo pequeno muda custo e qualidade da leitura: vira aviso.
PEQUENOS = ("claude-haiku-4-5",)


def cache_cli() -> dict:
    caminho = pathlib.Path(os.environ.get("CLAUDE_JSON") or pathlib.Path.home() / ".claude.json")
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def foto_arq() -> pathlib.Path:
    return pathlib.Path(os.environ.get("INTERRUPTORES_ARQ") or ROOT / "logs" / "claude-interruptores.json")


def antes() -> int:
    feats = cache_cli().get("cachedGrowthBookFeatures") or {}
    variavel = os.environ.get("CLAUDE_CODE_WEB_FETCH_AGENT")
    for nome, oque in VIGIADOS.items():
        ligado = bool(feats.get(nome))
        print(f"Claude Code — {nome}: {'ligado' if ligado else 'desligado'} no cache do CLI ({oque})",
              file=sys.stderr)
        if ligado:
            neutro = (f"; CLAUDE_CODE_WEB_FETCH_AGENT={variavel} deve neutralizar, e a conferência"
                      " depois do agente diz se neutralizou") if variavel is not None else ""
            print(f"claude code: experimento {nome} ligado na conta ({oque}){neutro}")
    # Qualquer interruptor que mudou fica no log: o próximo experimento pode ter
    # outro nome. A foto anterior fica em logs/, fora do git.
    arq = foto_arq()
    try:
        anterior = json.loads(arq.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        anterior = None
    if anterior is not None:
        mudaram = sorted(k for k in set(feats) | set(anterior) if feats.get(k) != anterior.get(k))
        if mudaram:
            n = len(mudaram)
            print(f"Claude Code — {n} interruptor{'es mudaram' if n > 1 else ' mudou'} desde a execução"
                  f" anterior: {', '.join(mudaram[:30])}{' …' if n > 30 else ''}", file=sys.stderr)
    try:
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(json.dumps(feats, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    except OSError:
        pass
    return 0


def depois(agente: pathlib.Path, modelo: str) -> int:
    from memoria_custo import transcricoes_dir
    from transcricoes import entradas
    try:
        dados = json.loads(agente.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0
    sid = dados.get("session_id")
    chamadas = cruas = 0
    if sid and (t := transcricoes_dir() / f"{sid}.jsonl").exists():
        for r, _ in entradas(t):
            conteudo = (r.get("message") or {}).get("content")
            for c in conteudo if isinstance(conteudo, list) else []:
                if c.get("type") == "tool_use" and c.get("name") in ("Agent", "Task") \
                        and (c.get("input") or {}).get("subagent_type") == "web-fetch":
                    chamadas += 1
                if c.get("type") == "tool_result":
                    texto = c.get("content")
                    if isinstance(texto, list):
                        texto = " ".join(x.get("text", "") for x in texto if isinstance(x, dict))
                    if isinstance(texto, str) and texto.startswith("Fetched ") and "(HTTP " in texto[:300]:
                        cruas += 1
    variavel = os.environ.get("CLAUDE_CODE_WEB_FETCH_AGENT")
    apesar = f", apesar de CLAUDE_CODE_WEB_FETCH_AGENT={variavel}" if variavel is not None else ""
    if chamadas or cruas:
        partes = [f"{chamadas} vez{'es' if chamadas != 1 else ''} pelo subagente web-fetch"] if chamadas else []
        partes += [f"{cruas} página{'s' if cruas != 1 else ''} crua{'s' if cruas != 1 else ''} no lugar do resumo"] if cruas else []
        print(f"claude code: a sessão leu {' e '.join(partes)}{apesar} (ADR 0013)")
    inesperados = sorted(m for m in (dados.get("modelUsage") or {})
                         if m != modelo and not m.startswith(PEQUENOS))
    for m in inesperados:
        print(f"claude code: modelo inesperado: {m} (o principal é {modelo or '?'};"
              f" o pequeno do CLI, {PEQUENOS[0]})")
    print(f"Claude Code — sessão: web-fetch {chamadas}, páginas cruas {cruas},"
          f" modelos {', '.join(sorted(dados.get('modelUsage') or {})) or '—'}", file=sys.stderr)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Vigia do Claude Code (ADR 0013).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("antes")
    d = sub.add_parser("depois")
    d.add_argument("--agente", required=True, help="JSON final do claude -p (logs/*-agente.json)")
    d.add_argument("--modelo", default="", help="modelo principal pedido ao CLI")
    a = ap.parse_args()
    if a.cmd == "antes":
        return antes()
    return depois(pathlib.Path(a.agente), a.modelo)


if __name__ == "__main__":
    sys.exit(main())
