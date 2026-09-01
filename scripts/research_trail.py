#!/usr/bin/env python3
"""
CampsCast — reconstrói o rastro de pesquisa de um episódio.

A partir da transcrição que o Claude Code grava em ~/.claude/projects/, mostra
tudo que o agente buscou e leu, e cruza com o que sobreviveu no episódio e no
backlog. Serve para episódios gerados antes de `research/` existir, e como
auditoria independente do log que o próprio agente escreve — a transcrição é
registro de máquina, não relato.

    python3 scripts/research_trail.py --date 2026-08-31
    python3 scripts/research_trail.py --date 2026-08-31 --save
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def sessions_dir() -> pathlib.Path | None:
    from watch_agent import session_dir
    return session_dir()


def session_for(date: str) -> pathlib.Path | None:
    """A sessão headless que gerou este episódio.

    Identificada pelo prompt-mestre mais a data do episódio no conteúdo — várias
    execuções convivem no mesmo diretório.
    """
    from watch_agent import is_headless_run
    d = sessions_dir()
    if d is None or not d.is_dir():
        return None

    candidatas = []
    for f in sorted(d.glob("*.jsonl"), key=lambda p: p.stat().st_mtime):
        # is_headless_run olha só as primeiras linhas: o prompt-mestre precisa
        # ser a mensagem de abertura. Buscar o texto em qualquer lugar casaria
        # com sessões interativas que só falam sobre o pipeline.
        if not is_headless_run(f):
            continue
        if f"episodes/{date}.md" in f.read_text(encoding="utf-8", errors="replace"):
            candidatas.append(f)
    return candidatas[-1] if candidatas else None


def trail(path: pathlib.Path) -> dict:
    buscas: list[str] = []
    lidas: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = d.get("message")
        if not isinstance(msg, dict) or msg.get("role") != "assistant":
            continue
        for b in msg.get("content") or []:
            if not isinstance(b, dict) or b.get("type") != "tool_use":
                continue
            inp = b.get("input") or {}
            if b.get("name") == "WebSearch" and inp.get("query"):
                buscas.append(inp["query"])
            elif b.get("name") == "WebFetch" and inp.get("url"):
                lidas.append(inp["url"])
    return {"buscas": buscas, "lidas": lidas}


def dominio(url: str) -> str:
    return (urlparse(url).netloc or url).replace("www.", "")


def relatorio(date: str, t: dict) -> str:
    ep = ROOT / "episodes" / f"{date}.md"
    usadas: set[str] = set()
    titulos: list[str] = []
    if ep.exists():
        from publish import parse_front_matter
        fm = parse_front_matter(ep.read_text(encoding="utf-8"))
        for topico in fm.get("topics", []):
            if isinstance(topico, dict):
                titulos.append(topico.get("title", ""))
                if topico.get("source_url"):
                    usadas.add(topico["source_url"])

    por_dominio: dict[str, list[str]] = {}
    for u in t["lidas"]:
        por_dominio.setdefault(dominio(u), []).append(u)

    linhas = [f"# Rastro de pesquisa — {date}", "",
              "Reconstruído da transcrição do Claude Code. É registro do que a",
              "máquina fez, não do que o agente diz ter feito.", "",
              f"- buscas na web: **{len(t['buscas'])}**",
              f"- páginas lidas: **{len(t['lidas'])}** "
              f"em {len(por_dominio)} domínios", ""]

    if titulos:
        linhas += ["## Pautas que entraram no episódio", ""]
        linhas += [f"{i}. {x}" for i, x in enumerate(titulos, 1)]
        linhas.append("")

    linhas += ["## Páginas lidas, por domínio", ""]
    for dom, urls in sorted(por_dominio.items(), key=lambda kv: -len(kv[1])):
        marca = " ⭐" if any(u in usadas for u in urls) else ""
        linhas.append(f"- **{dom}** ({len(urls)}){marca}")
        for u in dict.fromkeys(urls):
            linhas.append(f"  - {'**' if u in usadas else ''}{u}"
                          f"{'** ← citada no episódio' if u in usadas else ''}")
    linhas.append("")

    linhas += ["## Buscas realizadas", ""]
    linhas += [f"{i}. `{q}`" for i, q in enumerate(t["buscas"], 1)]
    linhas += ["", "---", "",
               "Este arquivo mostra **o que foi visitado**, não o motivo de cada",
               "descarte. O porquê fica em `research/` — escrito pelo agente na",
               "hora da decisão, para episódios de 31/08/2026 em diante."]
    return "\n".join(linhas)


def main() -> int:
    ap = argparse.ArgumentParser(description="Rastro de pesquisa de um episódio.")
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--save", action="store_true",
                    help="grava em research/<data>-rastro.md")
    args = ap.parse_args()

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        print(f"ERRO: data inválida: {args.date}", file=sys.stderr)
        return 2

    sess = session_for(args.date)
    if sess is None:
        print(f"Nenhuma transcrição encontrada para {args.date}.\n"
              "As sessões ficam em ~/.claude/projects/ e não são eternas — "
              "episódios antigos podem já não ter rastro.", file=sys.stderr)
        return 1

    texto = relatorio(args.date, trail(sess))
    if args.save:
        out = ROOT / "research" / f"{args.date}-rastro.md"
        out.parent.mkdir(exist_ok=True)
        out.write_text(texto + "\n", encoding="utf-8")
        print(f"OK {out.relative_to(ROOT)}")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
