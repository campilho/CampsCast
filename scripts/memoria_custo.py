#!/usr/bin/env python3
"""
CampsCast — de onde vem o cache lido de cada execução do agente.

Quase toda a entrada do agente é leitura de cache: a cada chamada ao modelo, o
contexto inteiro até ali é lido de novo. Um trecho que entra antes da chamada k
é cache escrito em k e cache lido em todas as seguintes. Por isso o custo de
uma leitura não é o tamanho dela — é o tamanho vezes as chamadas que vêm
depois. Um índice lido no começo pesa mais que uma página lida no fim.

Este script lê a transcrição que o Claude Code grava em ~/.claude/projects/
(achada pelo session_id do logs/*-agente.json) e reparte o cache lido entre:

    base      prompt, sistema e ferramentas, presentes desde a primeira chamada
    indice    tudo que veio do covered-index.json
    backlog   saved-items/backlog.md e o histórico em saved-items/historico/
    roteiros  episodes/
    web       WebFetch e WebSearch
    outros    o resto (config, research, scripts)

Tokens por bloco são estimados pela razão caracteres/token medida na própria
execução: crescimento do contexto contra caracteres que entraram. A coluna
"expl." diz quanto do cache lido a conta explica; o que falta é sobretudo o
texto que o próprio modelo gera, que também fica no contexto.

Primeira medição em 03/10/2026: memória (índice, backlog e roteiros) era ~42%
do cache lido nos dias do Opus 5.5.

Uso:
    python3 scripts/memoria_custo.py                 # todas as execuções
    python3 scripts/memoria_custo.py --desde 2026-10-05
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATEGORIAS = ("indice", "backlog", "roteiros", "web", "outros")


def transcricoes_dir() -> pathlib.Path:
    nome = "-" + str(ROOT).strip("/").replace("/", "-")
    return pathlib.Path.home() / ".claude" / "projects" / nome


def categoria(nome: str, entrada) -> str:
    s = json.dumps(entrada, ensure_ascii=False)
    if "covered-index" in s:
        return "indice"
    if "backlog" in s or "saved-items/historico" in s:
        return "backlog"
    if re.search(r"episodes/", s):
        return "roteiros"
    if nome in ("WebFetch", "WebSearch"):
        return "web"
    return "outros"


def _texto(resultado: dict) -> str:
    t = resultado.get("content")
    if isinstance(t, list):
        t = " ".join(x.get("text", "") for x in t if isinstance(x, dict))
    return t or ""


def analisa(caminho: pathlib.Path) -> dict:
    chamadas: list[str] = []   # ids únicos de mensagem do modelo, em ordem
    uso: dict[str, dict] = {}
    pendentes: dict[str, tuple] = {}
    blocos: list[tuple[int, str, int]] = []   # (próxima chamada, categoria, chars)
    for linha in caminho.open(encoding="utf-8"):
        reg = json.loads(linha)
        if reg.get("type") == "assistant":
            msg = reg["message"]
            mid = msg.get("id")
            if mid not in uso:     # a mesma mensagem aparece uma vez por bloco
                chamadas.append(mid)
                uso[mid] = msg.get("usage", {})
            for c in msg.get("content", []):
                if c.get("type") == "tool_use":
                    pendentes[c["id"]] = (c["name"], c.get("input"))
        elif reg.get("type") == "user" and isinstance(reg["message"].get("content"), list):
            for c in reg["message"]["content"]:
                if c.get("type") == "tool_result":
                    nome, entrada = pendentes.get(c["tool_use_id"], ("?", {}))
                    blocos.append((len(chamadas), categoria(nome, entrada), len(_texto(c))))

    n = len(chamadas)
    if n < 2:
        return {}
    contexto = [uso[m].get("input_tokens", 0) + uso[m].get("cache_read_input_tokens", 0)
                + uso[m].get("cache_creation_input_tokens", 0) for m in chamadas]
    lido = sum(uso[m].get("cache_read_input_tokens", 0) for m in chamadas)
    saida = sum(uso[m].get("output_tokens", 0) for m in chamadas)
    chars = sum(b[2] for b in blocos)
    razao = chars / max(contexto[-1] - contexto[0] - saida, 1)

    contrib = dict.fromkeys(CATEGORIAS, 0.0)
    tamanho = dict.fromkeys(CATEGORIAS, 0)
    for k, cat, nchars in blocos:
        contrib[cat] += (nchars / razao) * max(n - k - 1, 0)
        tamanho[cat] += nchars
    return {"chamadas": n, "lido": lido, "razao": razao,
            "base": contexto[0] * (n - 1), "contrib": contrib, "chars": tamanho}


def main() -> int:
    ap = argparse.ArgumentParser(description="Reparte o cache lido por fonte.")
    ap.add_argument("--desde", help="ignora execuções anteriores a esta data")
    args = ap.parse_args()

    pasta = transcricoes_dir()
    print(f"{'data':10} {'cham':>4} {'lido':>6} {'base':>5}  "
          + "  ".join(f"{c:>12}" for c in CATEGORIAS) + "  expl.")
    print(f"{'':10} {'':>4} {'':>6} {'':>5}  "
          + "  ".join(f"{'lido  peso':>12}" for _ in CATEGORIAS))
    for ag in sorted((ROOT / "logs").glob("*-agente.json")):
        data = ag.name[:10]
        if args.desde and data < args.desde:
            continue
        try:
            sid = json.loads(ag.read_text(encoding="utf-8")).get("session_id")
        except (OSError, ValueError):
            continue
        transcricao = pasta / f"{sid}.jsonl"
        if not sid or not transcricao.exists():
            print(f"{data} transcrição ausente")
            continue
        r = analisa(transcricao)
        if not r or not r["lido"]:
            print(f"{data} sem chamadas suficientes")
            continue
        pct = lambda v: 100 * v / r["lido"]
        celulas = "  ".join(f"{r['chars'][c] / 1000:5.0f}K {pct(r['contrib'][c]):4.0f}%"
                            for c in CATEGORIAS)
        explicado = pct(r["base"] + sum(r["contrib"].values()))
        print(f"{data} {r['chamadas']:4} {r['lido'] / 1e6:5.1f}M {pct(r['base']):4.0f}%  "
              f"{celulas}  {explicado:4.0f}%")
    print("\nlido = caracteres que entraram no contexto; peso = parte do cache lido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
