#!/usr/bin/env python3
"""
CampsCast — a ficha dos agentes (config/agentes.json): versão de cada um.

Cada agente tem um histórico de versões; a última é a que está nos arquivos
agora. Uma versão diz que prompts a definem (com a impressão digital de cada
um), o modelo, as ferramentas, o que mudou e o que se mediu. O registro de
cada execução guarda que versão rodou, para custo e qualidade serem lidos por
versão; o estúdio mostra a ficha.

    ativos [--jornalista 0|1]   JSON das versões que rodam nesta execução
                                ({"editor": "1.0", ...}); prompt que mudou sem
                                versão nova sai como "1.0+mudado", com aviso
    confere                     lista o que não bate com os arquivos; sai 1
    mostra                      a ficha, para ler

Impressão digital: os 12 primeiros caracteres do SHA-256 do arquivo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def ficha() -> dict:
    caminho = pathlib.Path(os.environ.get("AGENTES_ARQ") or ROOT / "config" / "agentes.json")
    return json.loads(caminho.read_text(encoding="utf-8"))


def digital(caminho: str) -> str | None:
    try:
        return hashlib.sha256((ROOT / caminho).read_bytes()).hexdigest()[:12]
    except OSError:
        return None


def atual(agente: dict) -> dict:
    return agente["historico"][-1]


def divergencias(nome: str, agente: dict) -> list[str]:
    """Prompts da versão atual que não batem com os arquivos de agora."""
    v = atual(agente)
    return [f"{nome} {v['versao']}: {arq} mudou e a ficha não (registre a versão nova em config/agentes.json)"
            for arq, d in v.get("prompts", {}).items() if digital(arq) != d]


def ativos(jornalista: bool) -> dict:
    """Versões dos agentes que rodam nesta execução."""
    saida = {}
    for nome, ag in ficha()["agentes"].items():
        if not ag.get("producao") and not (nome == "jornalista" and jornalista):
            continue
        v = atual(ag)["versao"]
        problemas = divergencias(nome, ag)
        for p in problemas:
            print(f"Agentes — {p}", file=sys.stderr)
        saida[nome] = f"{v}+mudado" if problemas else v
    return saida


def main() -> int:
    ap = argparse.ArgumentParser(description="Ficha dos agentes (config/agentes.json).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("ativos")
    a.add_argument("--jornalista", default="0")
    sub.add_parser("confere")
    sub.add_parser("mostra")
    args = ap.parse_args()
    if args.cmd == "ativos":
        print(json.dumps(ativos(args.jornalista == "1"), ensure_ascii=False))
        return 0
    f = ficha()["agentes"]
    if args.cmd == "confere":
        problemas = [p for nome, ag in f.items() for p in divergencias(nome, ag)]
        print("\n".join(problemas) or "ficha confere com os arquivos")
        return 1 if problemas else 0
    for nome, ag in f.items():
        print(f"{ag['nome']} — {'na produção' if ag.get('producao') else 'fora da produção (' + ag.get('chave', '') + ')'}")
        for v in ag["historico"]:
            print(f"  {v['versao']:5} desde {v['desde']} · {v.get('modelo', '—')} · {v['mudou']}")
            if v.get("medido"):
                print(f"        medido: {v['medido']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
