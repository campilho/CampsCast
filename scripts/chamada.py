#!/usr/bin/env python3
"""
CampsCast — decide se o episódio de uma data leva a chamada para seguir.

A chamada — "se está gostando, siga o podcast para ser avisado do episódio
novo" — entra depois da primeira pauta, e só em alguns dias da semana. Depois
da primeira pauta porque, no Spotify, só uns 18% ouvem até o fim, mas o consumo
médio é de dois terços do episódio: no encerramento ela alcançaria pouca gente,
e na abertura pediria compromisso antes de entregar qualquer coisa. Em poucos
dias porque, repetida todo dia, vira ruído para quem ouve sempre.

Os dias ficam em config/show.json, em "chamada_para_seguir"; o texto é livre,
escrito pelo agente. Imprime "sim" ou "não".

Uso:
    python3 scripts/chamada.py 2026-09-29
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOW = ROOT / "config" / "show.json"
DIAS = {"segunda": 1, "terça": 2, "quarta": 3, "quinta": 4, "sexta": 5,
        "sábado": 6, "domingo": 7}


def chamada_para_seguir(data: str, arquivo: pathlib.Path = SHOW) -> bool:
    try:
        regra = json.loads(arquivo.read_text(encoding="utf-8")).get("chamada_para_seguir")
    except (FileNotFoundError, json.JSONDecodeError):
        return False
    if not regra or data < regra.get("desde", "9999"):
        return False
    dias = {DIAS[d] for d in regra.get("dias", []) if d in DIAS}
    return dt.date.fromisoformat(data).isoweekday() in dias


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        sys.exit(2)
    print("sim" if chamada_para_seguir(sys.argv[1]) else "não")
