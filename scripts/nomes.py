#!/usr/bin/env python3
"""
CampsCast — nomes falados na ficha técnica e número do episódio.

A ficha técnica diz em voz alta quem escreveu e quem narrou. Esses nomes saem
dos ids realmente em uso, nunca de um campo mantido à mão: o antigo
`_nome_falado` continuou dizendo "Flash 2.5" por quatro episódios depois da
troca para o Multilingual v2.

    python3 scripts/nomes.py agente claude-opus-5   -> Claude Opus 5
    python3 scripts/nomes.py tts                    -> ElevenLabs Multilingual v2
    python3 scripts/nomes.py numero 2026-09-14      -> 12
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
EPISODIOS = RAIZ / "episodes"
TTS = RAIZ / "config" / "tts.json"
_FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def nome_agente(modelo: str) -> str:
    """claude-opus-5 -> Claude Opus 5; descarta sufixo de data (AAAAMMDD)."""
    partes = [p for p in modelo.strip().split("-")
              if p and not re.fullmatch(r"\d{8}", p)]
    if partes and partes[0].lower() == "claude":
        partes = partes[1:]
    palavras = [p.capitalize() for p in partes if not p.isdigit()]
    numeros = [p for p in partes if p.isdigit()]
    nome = " ".join(palavras) + (" " + ".".join(numeros) if numeros else "")
    return ("Claude " + nome.strip()).strip()


def nome_tts(model_id: str) -> str:
    """eleven_multilingual_v2 -> ElevenLabs Multilingual v2; v2_5 -> v2.5."""
    partes = model_id.strip().split("_")
    if partes and partes[0] == "eleven":
        partes = partes[1:]
    saida, i = [], 0
    while i < len(partes):
        p = partes[i]
        if re.fullmatch(r"v\d+", p):
            versao = [p[1:]]
            while i + 1 < len(partes) and partes[i + 1].isdigit():
                i += 1
                versao.append(partes[i])
            saida.append("v" + ".".join(versao))
        else:
            saida.append(p.capitalize())
        i += 1
    return "ElevenLabs " + " ".join(saida)


def _numero_gravado(caminho: pathlib.Path) -> int | None:
    m = _FRONT_MATTER.match(caminho.read_text(encoding="utf-8"))
    if not m:
        return None
    n = re.search(r"^episode:\s*(\d+)\s*$", m.group(1), re.M)
    return int(n.group(1)) if n else None


def proximo_numero(data: str, pasta: pathlib.Path = EPISODIOS) -> int:
    """Número do episódio de `data`.

    Se o episódio já existe com número, devolve o mesmo — reexecutar não
    renumera. Senão, o maior número gravado antes dessa data, mais um. Nunca
    conta arquivos quando há número gravado: apagar um episódio renumeraria
    todos os seguintes.
    """
    proprio = pasta / f"{data}.md"
    if proprio.exists() and (n := _numero_gravado(proprio)):
        return n
    anteriores = [p for p in pasta.glob("*.md")
                  if re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.stem) and p.stem < data]
    gravados = [n for p in anteriores if (n := _numero_gravado(p))]
    return max(gravados) + 1 if gravados else len(anteriores) + 1


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in ("agente", "tts", "numero"):
        print(__doc__, file=sys.stderr)
        return 2
    if sys.argv[1] == "agente":
        print(nome_agente(sys.argv[2]))
    elif sys.argv[1] == "tts":
        print(nome_tts(json.loads(TTS.read_text())["model_id"]))
    else:
        print(proximo_numero(sys.argv[2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
