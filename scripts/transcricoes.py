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
"""
from __future__ import annotations

import json
import pathlib
from typing import Iterator


def subagentes(principal: pathlib.Path) -> list[pathlib.Path]:
    """As transcrições dos subagentes desta sessão, em ordem de nome."""
    return sorted((principal.parent / principal.stem / "subagents").glob("agent-*.jsonl"))


def arquivos(principal: pathlib.Path) -> list[pathlib.Path]:
    return [principal, *subagentes(principal)]


def entradas(principal: pathlib.Path) -> Iterator[tuple[dict, bool]]:
    """Cada entrada da sessão e dos subagentes, com a marca de quem é do
    subagente. Primeiro a principal inteira, depois cada subagente: quem
    precisa de ordem no tempo ordena pelo timestamp."""
    for f in arquivos(principal):
        try:
            linhas = f.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for linha in linhas:
            try:
                d = json.loads(linha)
            except ValueError:
                continue
            if isinstance(d, dict):
                yield d, f != principal
