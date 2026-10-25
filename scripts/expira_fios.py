#!/usr/bin/env python3
"""
CampsCast — expiração de fios parados.

Fio sem marco há 30 dias sai da leitura diária: é movido inteiro de
memoria/fios.md para memoria/fios-expirados/AAAA.md, com a situação
"expirado" e uma linha dizendo desde quando estava parado. Nada se apaga. Se a
notícia voltar, o agente traz o fio de volta, com o marco novo.

Por quê: em três semanas (05 a 25/10) o agente abriu onze fios e fechou um, e a
lista bateu no teto. Perguntas se abrem mais rápido do que se resolvem; sem
saída automática, qualquer teto enche. A conta é feita aqui, e não pelo agente,
porque dado calculado é melhor que dado lembrado (docs/aprendizados.md).

"Parado" conta a partir do dia mais recente entre a abertura e os marcos.

Uso:
    python3 scripts/expira_fios.py --data 2026-10-26            # move e lista
    python3 scripts/expira_fios.py --data 2026-10-26 --dry-run  # só lista

Imprime os fios movidos, separados por espaço (nada, se nenhum). A variável
FIOS_ARQ troca o arquivo de fios (o smoke test usa); o cemitério fica ao lado,
em fios-expirados/.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIAS = 30
DATA = re.compile(r"\d{4}-\d{2}-\d{2}")
INICIO_FIO = re.compile(r"(?m)^(?=## F-\d{3} · )")
CABECALHO_CEMITERIO = """# Fios expirados — {ano}

Fios que ficaram {dias} dias sem marco e saíram da leitura diária. Movidos
inteiros de `memoria/fios.md`, com a linha de expiração no fim. Não estão
encerrados: se a notícia voltar, o fio volta para `memoria/fios.md` com o marco
novo e a situação "aberto". Revisão uma vez por mês, no relatório mensal.

---
"""


def ultima_atividade(bloco: str) -> dt.date | None:
    """Dia mais recente entre a abertura e os marcos do fio."""
    datas = []
    m = re.search(r"(?m)^- aberto:\s*(\d{4}-\d{2}-\d{2})", bloco)
    if m:
        datas.append(m[1])
    datas += re.findall(r"(?m)^\s+- (\d{4}-\d{2}-\d{2})", bloco)
    return dt.date.fromisoformat(max(datas)) if datas else None


def expira(fios: pathlib.Path, hoje: dt.date, dias: int = DIAS,
           simular: bool = False) -> list[str]:
    texto = fios.read_text(encoding="utf-8")
    partes = INICIO_FIO.split(texto)
    cabecalho, blocos = partes[0], partes[1:]
    ficam, saem = [], []
    for b in blocos:
        ultima = ultima_atividade(b)
        if ultima is not None and (hoje - ultima).days >= dias:
            saem.append((b, ultima))
        else:
            ficam.append(b)
    if not saem or simular:
        return [re.match(r"## (F-\d{3})", b)[1] for b, _ in saem]

    destino = fios.parent / "fios-expirados" / f"{hoje.year}.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    atual = (destino.read_text(encoding="utf-8") if destino.exists()
             else CABECALHO_CEMITERIO.format(ano=hoje.year, dias=dias))
    for b, ultima in saem:
        b = re.sub(r"(?m)^- situação:.*$", "- situação: expirado", b.rstrip("\n"))
        b += (f"\n- expirado: {hoje.isoformat()} — sem marco desde "
              f"{ultima.isoformat()} ({(hoje - ultima).days} dias)\n")
        atual = atual.rstrip("\n") + "\n\n" + b
    # O cemitério é gravado antes de o fio sair do arquivo de leitura: se algo
    # falhar no meio, o fio fica nos dois lugares, nunca em nenhum.
    destino.write_text(atual, encoding="utf-8")
    restante = cabecalho + "".join(ficam)
    fios.write_text(restante.rstrip("\n") + "\n", encoding="utf-8")
    return [re.match(r"## (F-\d{3})", b)[1] for b, _ in saem]


def main() -> int:
    ap = argparse.ArgumentParser(description="Move fios parados para fios-expirados/.")
    ap.add_argument("--data", required=True, help="data do episódio (AAAA-MM-DD)")
    ap.add_argument("--dias", type=int, default=DIAS)
    ap.add_argument("--dry-run", action="store_true", help="só lista, não move")
    a = ap.parse_args()
    fios = pathlib.Path(os.environ.get("FIOS_ARQ") or ROOT / "memoria" / "fios.md")
    if not fios.exists():
        return 0
    print(" ".join(expira(fios, dt.date.fromisoformat(a.data), a.dias, a.dry_run)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
