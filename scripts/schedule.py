#!/usr/bin/env python3
"""
CampsCast — decide se determinado dia tem episódio.

O podcast é para ouvir no carro a caminho do trabalho, então o padrão é dias
úteis. Mas "dia útil" depende de onde a pessoa está: feriado nacional aqui não
é feriado lá fora, e quem clonar o projeto pode querer publicar aos sábados.
Por isso a regra mora em config/schedule.json, não no código.

Pular um dia não perde notícia: a janela do episódio seguinte cobre desde o
último dia já coberto (scripts/window.py). O feriado é lido no dia seguinte.

    python3 scripts/schedule.py --date 2026-09-07
    python3 scripts/schedule.py --proximos 14
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import date, timedelta

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "schedule.json"

DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
        "sexta-feira", "sábado", "domingo"]


def pascoa(ano: int) -> date:
    """Domingo de Páscoa pelo algoritmo de Gauss/Meeus (calendário gregoriano)."""
    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes, dia = divmod(h + l - 7 * m + 114, 31)
    return date(ano, mes, dia + 1)


def feriados_br(ano: int) -> dict[date, str]:
    """Feriados nacionais brasileiros, incluindo os móveis.

    Os móveis derivam da Páscoa, então são calculados em vez de listados — uma
    lista fixa vira dívida todo mês de janeiro.
    """
    p = pascoa(ano)
    fixos = {
        date(ano, 1, 1): "Confraternização Universal",
        date(ano, 4, 21): "Tiradentes",
        date(ano, 5, 1): "Dia do Trabalho",
        date(ano, 9, 7): "Independência",
        date(ano, 10, 12): "Nossa Senhora Aparecida",
        date(ano, 11, 2): "Finados",
        date(ano, 11, 15): "Proclamação da República",
        date(ano, 11, 20): "Consciência Negra",
        date(ano, 12, 25): "Natal",
    }
    moveis = {
        p - timedelta(days=48): "Carnaval (segunda)",
        p - timedelta(days=47): "Carnaval (terça)",
        p - timedelta(days=2): "Sexta-feira Santa",
        p + timedelta(days=60): "Corpus Christi",
    }
    return {**fixos, **moveis}


def carregar() -> dict:
    if not CONFIG.exists():
        return {"weekdays": [1, 2, 3, 4, 5], "holidays": "BR",
                "skip_dates": [], "force_dates": []}
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def avaliar(d: date, cfg: dict | None = None) -> tuple[bool, str]:
    """(tem episódio?, motivo legível)."""
    cfg = cfg or carregar()
    iso = d.isoformat()

    # force_dates vence tudo: é a válvula de escape para casos pontuais.
    if iso in (cfg.get("force_dates") or []):
        return True, "data forçada em config/schedule.json"

    if iso in (cfg.get("skip_dates") or []):
        return False, "data na lista de exceções de config/schedule.json"

    permitidos = cfg.get("weekdays") or [1, 2, 3, 4, 5]
    if (d.weekday() + 1) not in permitidos:
        return False, f"{DIAS[d.weekday()]} não está em weekdays"

    if (cfg.get("holidays") or "").upper() == "BR":
        nome = feriados_br(d.year).get(d)
        if nome:
            return False, f"feriado nacional: {nome}"

    return True, "dia de publicação"


def main() -> int:
    ap = argparse.ArgumentParser(description="Há episódio nesta data?")
    ap.add_argument("--date", help="YYYY-MM-DD (default: hoje)")
    ap.add_argument("--proximos", type=int, metavar="N",
                    help="mostra os próximos N dias")
    ap.add_argument("--quiet", action="store_true",
                    help="sem saída; só o código de retorno (0=sim, 1=não)")
    args = ap.parse_args()

    hoje = date.fromisoformat(args.date) if args.date else date.today()
    cfg = carregar()

    if args.proximos:
        for i in range(args.proximos):
            d = hoje + timedelta(days=i)
            ok, motivo = avaliar(d, cfg)
            marca = "episódio" if ok else "—       "
            print(f"  {d.isoformat()}  {DIAS[d.weekday()][:5]:<6} {marca}  "
                  f"{'' if ok else motivo}")
        return 0

    ok, motivo = avaliar(hoje, cfg)
    if not args.quiet:
        print(f"{hoje.isoformat()} ({DIAS[hoje.weekday()]}): "
              f"{'episódio' if ok else 'sem episódio'} — {motivo}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
