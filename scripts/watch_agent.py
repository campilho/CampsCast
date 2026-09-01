#!/usr/bin/env python3
"""
CampsCast — acompanha ao vivo o que o agente está fazendo.

A etapa de pesquisa demora vários minutos e não imprime nada enquanto roda:
o `run_episode.sh` captura a saída do `claude -p` para poder validá-la. Este
script resolve isso lendo a transcrição que o próprio CLI grava em
~/.claude/projects/<projeto>/<sessao>.jsonl e mostrando cada ferramenta usada.

Funciona com uma execução já em andamento — é só abrir outro terminal:

    python3 scripts/watch_agent.py            # segue a sessão mais recente
    python3 scripts/watch_agent.py --once     # imprime o que já houve e sai

O run_episode.sh também o dispara em segundo plano durante a etapa 1, com
--newer-than e --log, para que o progresso apareça no terminal e no log sem
precisar de um segundo terminal.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import signal
import sys
import time
import typing

ROOT = pathlib.Path(__file__).resolve().parent.parent
POLL_SECONDS = 1.0


def session_dir() -> pathlib.Path | None:
    """Diretório de transcrições do CLI para este projeto.

    O slug troca tudo que não é alfanumérico por `-`, inclusive as barras e os
    espaços do caminho ("Claude Code" vira "Claude-Code").
    """
    base = pathlib.Path.home() / ".claude" / "projects"
    slug = re.sub(r"[^A-Za-z0-9]", "-", str(ROOT))
    exact = base / slug
    if exact.is_dir():
        return exact
    # Fallback: casa pelo nome do projeto, caso a regra do slug mude.
    matches = [d for d in base.glob(f"*{ROOT.name}") if d.is_dir()]
    return matches[0] if len(matches) == 1 else None


# Trecho do prompt-mestre que só aparece numa sessão headless do pipeline.
# Serve para não confundir a execução do run_episode.sh com uma sessão
# interativa aberta no mesmo projeto — as duas convivem no mesmo diretório.
MARKER = "produtor e roteirista do CampsCast"


def is_headless_run(path: pathlib.Path) -> bool:
    """A primeira mensagem do usuário é o prompt-mestre inteiro."""
    try:
        with path.open(encoding="utf-8", errors="replace") as fh:
            for _ in range(5):
                line = fh.readline()
                if not line:
                    return False
                if MARKER in line:
                    return True
    except OSError:
        return False
    return False


def newest_session(d: pathlib.Path, newer_than: float = 0.0) -> pathlib.Path | None:
    files = [f for f in d.glob("*.jsonl") if f.stat().st_mtime >= newer_than]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    for f in files:
        if is_headless_run(f):
            return f
    if files and not newer_than:
        print("AVISO: nenhuma sessão do pipeline encontrada; seguindo a mais recente.",
              file=sys.stderr)
        return files[0]
    return None


def await_session(d: pathlib.Path, newer_than: float, timeout: float = 120.0
                  ) -> pathlib.Path | None:
    """Espera a sessão headless nascer — ela só existe depois que o CLI sobe."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        found = newest_session(d, newer_than)
        if found is not None:
            return found
        time.sleep(POLL_SECONDS)
    return None


def summarize(tool: str, inp: dict) -> str:
    """Uma linha curta descrevendo a chamada de ferramenta."""
    if not isinstance(inp, dict):
        return tool
    if tool == "WebSearch":
        return f'buscando: "{inp.get("query", "")}"'
    if tool == "WebFetch":
        url = inp.get("url", "")
        return f"lendo: {url[:90]}"
    if tool in ("Read", "Write", "Edit"):
        path = str(inp.get("file_path", ""))
        try:
            path = str(pathlib.Path(path).relative_to(ROOT))
        except ValueError:
            pass
        verb = {"Read": "lendo", "Write": "escrevendo", "Edit": "editando"}[tool]
        return f"{verb}: {path}"
    if tool == "Grep":
        return f'grep: {inp.get("pattern", "")}'
    if tool == "Glob":
        return f'glob: {inp.get("pattern", "")}'
    if tool == "TodoWrite":
        todos = inp.get("todos", [])
        doing = [t.get("content", "") for t in todos
                 if isinstance(t, dict) and t.get("status") == "in_progress"]
        return f"plano: {doing[0]}" if doing else f"plano: {len(todos)} itens"
    return tool


def emit(line: str, log: "typing.TextIO | None") -> None:
    print(line, flush=True)
    if log is not None:
        log.write(line + "\n")
        log.flush()


def render(raw: str, started: float, counters: dict, prefix: str = "",
           log: "typing.TextIO | None" = None) -> None:
    try:
        d = json.loads(raw)
    except json.JSONDecodeError:
        return
    msg = d.get("message")
    if not isinstance(msg, dict) or msg.get("role") != "assistant":
        return

    elapsed = int(time.time() - started)
    stamp = f"[{elapsed // 60:02d}:{elapsed % 60:02d}]"

    for block in msg.get("content") or []:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "tool_use":
            tool = block.get("name", "?")
            counters[tool] = counters.get(tool, 0) + 1
            counters["_total"] = counters.get("_total", 0) + 1
            emit(f"{prefix}{stamp} {counters['_total']:>3}. "
                 f"{summarize(tool, block.get('input', {}))}", log)
        elif block.get("type") == "text":
            text = (block.get("text") or "").strip()
            if text:
                first = text.splitlines()[0][:100]
                emit(f"{prefix}{stamp}      ↳ {first}", log)


def main() -> int:
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

    ap = argparse.ArgumentParser(description="Acompanha o agente ao vivo.")
    ap.add_argument("--once", action="store_true", help="não fica seguindo o arquivo")
    ap.add_argument("--file", help="caminho de um .jsonl específico")
    ap.add_argument("--newer-than", type=float, default=0.0,
                    help="só considera sessões com mtime >= este epoch; espera aparecer")
    ap.add_argument("--log", help="também acrescenta a saída neste arquivo")
    ap.add_argument("--prefix", default="", help="prefixo de cada linha")
    ap.add_argument("--quiet", action="store_true", help="sem cabeçalho nem resumo")
    args = ap.parse_args()

    if args.file:
        path = pathlib.Path(args.file)
    else:
        d = session_dir()
        if d is None or not d.is_dir():
            print("Nenhuma transcrição encontrada para este projeto em "
                  "~/.claude/projects/. O agente já rodou alguma vez daqui?",
                  file=sys.stderr)
            return 1
        if args.newer_than:
            path = await_session(d, args.newer_than)
        else:
            path = newest_session(d)
        if path is None:
            if not args.quiet:
                print(f"Nenhuma sessão do pipeline em {d}", file=sys.stderr)
            return 1

    log = open(args.log, "a", encoding="utf-8") if args.log else None

    if not args.quiet:
        emit(f"{args.prefix}acompanhando {path.name}", log)

    started = time.time()
    counters: dict = {}
    pos = 0

    while True:
        try:
            with path.open(encoding="utf-8", errors="replace") as fh:
                fh.seek(pos)
                # readline() em vez de `for line in fh`: iterar desabilita
                # tell(), e aqui a posição é justamente o que precisa persistir
                # entre as passadas para não reprocessar o arquivo inteiro.
                while True:
                    line = fh.readline()
                    if not line:
                        break
                    if not line.endswith("\n"):
                        break               # linha ainda sendo escrita
                    render(line, started, counters, args.prefix, log)
                    pos = fh.tell()
        except FileNotFoundError:
            pass

        if args.once:
            break
        try:
            time.sleep(POLL_SECONDS)
        except KeyboardInterrupt:
            break

    total = counters.pop("_total", 0)
    if total and not args.quiet:
        detail = ", ".join(f"{k} {v}" for k, v in sorted(counters.items()))
        emit(f"{args.prefix}{total} chamadas de ferramenta — {detail}", log)
    if log is not None:
        log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
