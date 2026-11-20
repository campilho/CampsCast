#!/usr/bin/env python3
"""Guarda o tráfego do repositório no GitHub antes que ele suma.

    python3 scripts/trafego_github.py            # lê e junta ao histórico
    python3 scripts/trafego_github.py --mostra   # só imprime o histórico guardado

O GitHub mostra só os últimos 14 dias de visitas e clones (Insights →
Traffic). Rodando toda sexta, no relatório da semana, nenhum dia se perde. O
histórico vai para `privado/dados/github-trafego.json`, fora do git: é dado de
audiência, e o relatório do autor é público.

Lê pelo `gh` (GitHub CLI, instalado em 20/11 com o Homebrew e logado na conta
do autor), sem biblioteca nova: o projeto continua sem dependências, e o `gh`
fica como o `claude`, uma ferramenta da máquina. Sem `gh` ou sem login, sai com
erro e uma linha dizendo o que faltou; o orquestrador registra e segue.

Junta por dia: para cada dia, fica o maior número já lido (um dia só cresce, e
o de hoje chega pela metade). Origens, páginas e estrelas não têm série diária
no GitHub; ficam como uma leitura por data.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
ARQ = pathlib.Path(os.environ.get("TRAFEGO_ARQ", ROOT / "privado" / "dados" / "github-trafego.json"))


class Falta(Exception):
    """O que impede a leitura, dito em uma linha."""


def gh_bin() -> str:
    for c in (os.environ.get("GH_BIN"), shutil.which("gh"), "/opt/homebrew/bin/gh", "/usr/local/bin/gh"):
        if c and pathlib.Path(c).exists():
            return c
    raise Falta("gh não encontrado (brew install gh; gh auth login)")


def repositorio() -> str:
    if os.environ.get("TRAFEGO_REPO"):
        return os.environ["TRAFEGO_REPO"]
    url = subprocess.run(["git", "-C", str(ROOT), "remote", "get-url", "origin"],
                         capture_output=True, text=True).stdout.strip()
    m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", url)
    if not m:
        raise Falta(f"remoto do git não é do GitHub: {url!r}")
    return m.group(1)


def api(gh: str, caminho: str):
    r = subprocess.run([gh, "api", caminho], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        erro = (r.stderr or r.stdout).strip().splitlines()
        raise Falta(f"gh api {caminho}: {erro[-1] if erro else 'falhou'}")
    return json.loads(r.stdout)


def le(gh: str, repo: str) -> dict:
    base = f"repos/{repo}"
    views = api(gh, f"{base}/traffic/views")
    clones = api(gh, f"{base}/traffic/clones")
    origens = api(gh, f"{base}/traffic/popular/referrers")
    paginas = api(gh, f"{base}/traffic/popular/paths")
    info = api(gh, base)
    return {"views": views, "clones": clones, "origens": origens, "paginas": paginas, "info": info}


def junta(hist: dict, lido: dict, repo: str, agora: datetime) -> dict:
    hist = {"_sobre": ("Tráfego do repositório no GitHub, guardado por scripts/trafego_github.py. "
                       "'dias': o maior número lido para cada dia (UTC). 'leituras': uma por data, "
                       "com o que o GitHub só dá somado em 14 dias."),
            "repo": repo, "dias": dict(hist.get("dias", {})), "leituras": list(hist.get("leituras", []))}
    for chave, serie, n, u in (("views", "views", "visualizacoes", "visitantes"),
                               ("clones", "clones", "clones", "clonadores")):
        for d in lido[chave].get(serie, []):
            dia = d["timestamp"][:10]
            atual = hist["dias"].setdefault(dia, {})
            atual[n] = max(atual.get(n, 0), int(d["count"]))
            atual[u] = max(atual.get(u, 0), int(d["uniques"]))
    data = agora.astimezone().date().isoformat()
    leitura = {
        "data": data,
        "em": agora.astimezone().isoformat(timespec="seconds"),
        "estrelas": lido["info"].get("stargazers_count"),
        "forks": lido["info"].get("forks_count"),
        "observadores": lido["info"].get("subscribers_count"),
        "visualizacoes_14d": lido["views"].get("count"), "visitantes_14d": lido["views"].get("uniques"),
        "clones_14d": lido["clones"].get("count"), "clonadores_14d": lido["clones"].get("uniques"),
        "origens": [[o["referrer"], o["count"], o["uniques"]] for o in lido["origens"]],
        "paginas": [[p["path"], p["count"], p["uniques"]] for p in lido["paginas"]],
    }
    hist["leituras"] = [l for l in hist["leituras"] if l.get("data") != data] + [leitura]
    hist["leituras"].sort(key=lambda l: l["data"])
    hist["dias"] = dict(sorted(hist["dias"].items()))
    return hist


def resumo(hist: dict) -> str:
    dias = hist.get("dias", {})
    if not dias:
        return "Tráfego do GitHub: nada guardado ainda."
    ult = hist["leituras"][-1] if hist.get("leituras") else {}
    total = sum(d.get("visualizacoes", 0) for d in dias.values())
    return (f"Tráfego do GitHub: {len(dias)} dias guardados ({min(dias)} a {max(dias)}), "
            f"{total} visualizações no total; nos últimos 14 dias, {ult.get('visualizacoes_14d')} "
            f"de {ult.get('visitantes_14d')} pessoas; estrelas: {ult.get('estrelas')}.")


def grava(hist: dict) -> None:
    ARQ.parent.mkdir(parents=True, exist_ok=True)
    tmp = ARQ.with_suffix(".tmp")
    tmp.write_text(json.dumps(hist, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tmp.replace(ARQ)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Guarda o tráfego do repositório no GitHub.")
    ap.add_argument("--mostra", action="store_true", help="só imprime o resumo do que está guardado")
    a = ap.parse_args(argv)
    hist = json.loads(ARQ.read_text(encoding="utf-8")) if ARQ.exists() else {}
    if a.mostra:
        print(resumo(hist))
        return 0
    try:
        repo = repositorio()
        lido = le(gh_bin(), repo)
    except (Falta, subprocess.TimeoutExpired, json.JSONDecodeError, KeyError) as e:
        print(f"Tráfego do GitHub não lido: {e}", file=sys.stderr)
        return 1
    hist = junta(hist, lido, repo, datetime.now(timezone.utc))
    grava(hist)
    print(resumo(hist))
    return 0


if __name__ == "__main__":
    sys.exit(main())
