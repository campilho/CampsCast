#!/usr/bin/env python3
"""
CampsCast — cálculo da janela de notícias de um episódio.

Invariante única:

    O episódio do dia D cobre do dia seguinte ao último dia já coberto
    até D-1. Hoje (D) NUNCA entra — o dia ainda não acabou.

Isso substitui a regra fixa "segunda pega sexta+sábado+domingo", que quebra
assim que existe uma execução manual no fim de semana: se você rodou no sábado
e cobriu a sexta, a segunda-feira passa a cobrir só sábado e domingo.

Partida a frio (nenhum episódio anterior, como na primeira execução):
  - segunda, sábado ou domingo -> começa na sexta-feira mais recente até D-1
  - terça a sexta              -> cobre apenas D-1

Uso:
    python3 scripts/window.py --date 2026-08-23            # KEY=VALUE p/ eval
    python3 scripts/window.py --date 2026-08-23 --human    # legível
"""
from __future__ import annotations

import argparse
import pathlib
import re
import shlex
import sys
from datetime import date, timedelta

ROOT = pathlib.Path(__file__).resolve().parent.parent
EPISODES = ROOT / "episodes"

# Nenhum episódio cobre mais que isso, mesmo depois de uma parada longa.
MAX_WINDOW_DAYS = 7

WEEKDAYS_PT = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
               "sexta-feira", "sábado", "domingo"]
MONTHS_PT = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
             "agosto", "setembro", "outubro", "novembro", "dezembro"]


def pt_day(d: date) -> str:
    return f"{WEEKDAYS_PT[d.weekday()]}, {d.day} de {MONTHS_PT[d.month - 1]}"


def last_covered_day(before: date) -> tuple[date | None, str | None]:
    """Último dia de notícia já coberto por algum episódio, e qual episódio.

    Lê `window_end` do front-matter. Episódio de formato antigo, sem esse
    campo, é interpretado de forma conservadora como tendo coberto até a
    véspera da sua própria data.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    from publish import parse_front_matter

    best: date | None = None
    best_ep: str | None = None

    for path in sorted(EPISODES.glob("*.md")):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", path.stem):
            continue
        try:
            ep_date = date.fromisoformat(path.stem)
        except ValueError:
            continue
        if ep_date > before:
            continue                      # episódio do futuro: ignora

        fm = parse_front_matter(path.read_text(encoding="utf-8"))
        raw = (fm.get("window_end") or "").strip()
        try:
            covered = date.fromisoformat(raw)
        except ValueError:
            covered = ep_date - timedelta(days=1)   # formato antigo

        if best is None or covered > best:
            best, best_ep = covered, path.stem

    return best, best_ep


def cold_start(end: date, episode_date: date) -> date:
    """Início da janela quando não há episódio anterior."""
    if episode_date.weekday() in (0, 5, 6):        # segunda, sábado, domingo
        start = end
        while start.weekday() != 4:                # recua até a sexta-feira
            start -= timedelta(days=1)
        return start
    return end


def describe(start: date, end: date) -> str:
    days = (end - start).days + 1
    if days == 1:
        return (f"Cobrir as notícias de {pt_day(end)} ({end.isoformat()}). "
                f"Nada publicado hoje entra neste episódio.")
    listed = "; ".join(
        f"{pt_day(start + timedelta(days=i))} ({(start + timedelta(days=i)).isoformat()})"
        for i in range(days)
    )
    return (f"Cobrir as notícias de {days} dias: {listed}. "
            f"Nada publicado hoje entra neste episódio.")


def compute(episode_date: date) -> dict:
    end = episode_date - timedelta(days=1)
    last, last_ep = last_covered_day(episode_date)

    if last is not None:
        start = last + timedelta(days=1)
        origin = f"após o episódio {last_ep} (que cobriu até {last.isoformat()})"
    else:
        start = cold_start(end, episode_date)
        origin = "partida a frio (nenhum episódio anterior)"

    clamped = False
    if (end - start).days + 1 > MAX_WINDOW_DAYS:
        start = end - timedelta(days=MAX_WINDOW_DAYS - 1)
        clamped = True

    if start > end:
        return {
            "status": "empty",
            "start": None, "end": None, "days": 0,
            "origin": origin, "last_episode": last_ep, "clamped": False,
            "text": (f"Nada novo a cobrir: o último dia de notícia disponível "
                     f"({end.isoformat()}) já foi coberto pelo episódio {last_ep}."),
        }

    return {
        "status": "ok",
        "start": start, "end": end, "days": (end - start).days + 1,
        "origin": origin, "last_episode": last_ep, "clamped": clamped,
        "text": describe(start, end),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Calcula a janela de notícias.")
    ap.add_argument("--date", required=True, help="data do episódio (YYYY-MM-DD)")
    ap.add_argument("--human", action="store_true", help="saída legível")
    args = ap.parse_args()

    try:
        episode_date = date.fromisoformat(args.date)
    except ValueError:
        print(f"ERRO: data inválida: {args.date}", file=sys.stderr)
        return 2

    w = compute(episode_date)

    if args.human:
        print(f"Episódio      : {episode_date.isoformat()} ({pt_day(episode_date)})")
        print(f"Último coberto: {w['last_episode'] or '—'}")
        print(f"Origem        : {w['origin']}")
        if w["status"] == "empty":
            print("Janela        : VAZIA")
        else:
            print(f"Janela        : {w['start']} → {w['end']}  ({w['days']} dia(s))"
                  + ("  [truncada]" if w["clamped"] else ""))
        print(f"Texto         : {w['text']}")
        return 0

    print(f"WINDOW_STATUS={w['status']}")
    print(f"WINDOW_START={w['start'] or ''}")
    print(f"WINDOW_END={w['end'] or ''}")
    print(f"WINDOW_DAYS={w['days']}")
    print(f"WINDOW_CLAMPED={'1' if w['clamped'] else '0'}")
    print(f"LAST_EPISODE={w['last_episode'] or ''}")
    print(f"WINDOW_ORIGIN={shlex.quote(w['origin'])}")
    print(f"NEWS_WINDOW={shlex.quote(w['text'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
