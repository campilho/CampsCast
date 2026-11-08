#!/usr/bin/env python3
"""Transcrição de uma sessão do agente, com as dos subagentes que ela chamou.

Desde 05/11/2026 o agente não lê páginas com o WebFetch: o Claude Code passou
a oferecer, no lugar, um subagente "web-fetch", sem mudança de versão do CLI.
As leituras ficam na transcrição do subagente, numa pasta com o nome da
sessão, ao lado da principal:

    <sessao>.jsonl
    <sessao>/subagents/agent-<id>.jsonl   (e um agent-<id>.meta.json)

Quem lia só a principal contou zero leituras em 05 e 06/11, com 46 e 68
páginas lidas de fato. Todo script que mede o que o agente fez lê por aqui.

Com o Jornalista ligado (scripts/jornalista.py), um hook barra o WebFetch do
agente principal, e a tentativa fica na transcrição como erro de ferramenta.
Ela não é leitura nem porta fechada: sai daqui, para que nenhuma medição a
conte. Quem quer contá-las usa `barradas()`.
"""
from __future__ import annotations

import json
import pathlib
from typing import Iterator

# Pedaço da resposta do hook do Jornalista (scripts/jornalista.py, MOTIVO).
BARRADA = "lidas pelo Jornalista"


def subagentes(principal: pathlib.Path) -> list[pathlib.Path]:
    """As transcrições dos subagentes desta sessão, em ordem de nome."""
    return sorted((principal.parent / principal.stem / "subagents").glob("agent-*.jsonl"))


def arquivos(principal: pathlib.Path) -> list[pathlib.Path]:
    return [principal, *subagentes(principal)]


def _linhas(f: pathlib.Path) -> Iterator[dict]:
    try:
        linhas = f.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return
    for linha in linhas:
        try:
            d = json.loads(linha)
        except ValueError:
            continue
        if isinstance(d, dict):
            yield d


def _blocos(d: dict) -> list:
    c = (d.get("message") or {}).get("content") if isinstance(d.get("message"), dict) else None
    return c if isinstance(c, list) else []


def barradas(principal: pathlib.Path) -> set[str]:
    """Os ids das chamadas que o hook do Jornalista barrou."""
    ids = set()
    for f in arquivos(principal):
        for d in _linhas(f):
            for c in _blocos(d):
                if not isinstance(c, dict) or c.get("type") != "tool_result" or not c.get("is_error"):
                    continue
                t = c.get("content")
                if isinstance(t, list):
                    t = " ".join(x.get("text", "") for x in t if isinstance(x, dict))
                if isinstance(t, str) and BARRADA in t:
                    ids.add(c.get("tool_use_id"))
    return ids


def entradas(principal: pathlib.Path) -> Iterator[tuple[dict, bool]]:
    """Cada entrada da sessão e dos subagentes, com a marca de quem é do
    subagente. Primeiro a principal inteira, depois cada subagente: quem
    precisa de ordem no tempo ordena pelo timestamp. As chamadas barradas pelo
    hook do Jornalista, e a resposta delas, ficam de fora."""
    fora = barradas(principal)
    for f in arquivos(principal):
        for d in _linhas(f):
            if fora and _blocos(d):
                blocos = [c for c in _blocos(d) if not (isinstance(c, dict) and (
                    (c.get("type") == "tool_use" and c.get("id") in fora)
                    or (c.get("type") == "tool_result" and c.get("tool_use_id") in fora)))]
                d = {**d, "message": {**d["message"], "content": blocos}}
            yield d, f != principal
