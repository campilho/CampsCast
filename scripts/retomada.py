#!/usr/bin/env python3
"""
CampsCast — o episódio do dia que parou no meio recomeça de onde parou.

Em 25/11 o filtro de segurança do Opus 5.5 cortou uma resposta do agente
depois de ele escrever o roteiro; o agente parou com FAIL, e o roteiro pela
metade ficou em episodes/. Às 06:00 e às 07:00 a repescagem viu o arquivo,
leu o window_end dele, concluiu que o dia já estava coberto e não fez nada.
Valia o mesmo para qualquer falha depois do roteiro (narração, publicação,
aviso) e para o Mac desligado no meio: o dia ficava parado, e as duas
repescagens não serviam para nada.

Agora o orquestrador marca cada etapa em logs/AAAA-MM-DD-etapas.json, no
começo e no fim, e a execução seguinte do mesmo dia decide por ele:

- pesquisa que começou e não terminou: o que o agente deixou (roteiro, log de
  pesquisa e a memória que ele mexeu) vai para logs/AAAA-MM-DD-interrompido-
  HHMMSS/, a memória volta à foto tirada antes do agente, e a pesquisa
  recomeça do zero, com a mesma janela;
- pesquisa terminada: recomeça na primeira etapa que não terminou (narração,
  publicação ou aviso), sem chamar o agente de novo;
- tudo terminado: nada a fazer.

Sem arquivo de etapas (episódio de antes desta mudança, ou feito à mão), nada
muda: vale a janela, como antes. Nada se apaga: o que sai de episodes/,
research/ e da memória fica guardado em logs/.

Uso (pelo orquestrador):
    python3 scripts/retomada.py comeca  --data 2026-11-25 --etapa pesquisa
    python3 scripts/retomada.py termina --data 2026-11-25 --etapa pesquisa
    python3 scripts/retomada.py decide  --data 2026-11-25   # saída para eval
    python3 scripts/retomada.py desfaz  --data 2026-11-25
"""
from __future__ import annotations

import argparse
import datetime as dt
import filecmp
import json
import os
import pathlib
import shlex
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

ETAPAS = ["pesquisa", "narracao", "publicacao", "aviso"]
# Etapas do orquestrador (--skip) que já terminaram quando a retomada começa
# em cada ponto.
PULA = {"narracao": "research", "publicacao": "research,tts",
        "aviso": "research,tts,publish"}
NOMES = {"narracao": "narração", "publicacao": "publicação", "aviso": "aviso"}
# O que o agente pode mexer além do roteiro e do log de pesquisa (prompts/
# master.md): o índice de pautas, o backlog e o histórico dele, e a memória.
MEMORIA = ["covered-index.json", "saved-items", "memoria"]


def agora() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def logs() -> pathlib.Path:
    return ROOT / "logs"


def arq_etapas(data: str) -> pathlib.Path:
    return logs() / f"{data}-etapas.json"


def foto_dir(data: str) -> pathlib.Path:
    return logs() / f"{data}-antes-da-pesquisa"


def le(data: str) -> dict | None:
    p = arq_etapas(data)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def grava(data: str, etapas: dict) -> None:
    p = arq_etapas(data)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(etapas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, p)


def arquivos(base: pathlib.Path) -> set[str]:
    """Caminhos relativos de todos os arquivos de MEMORIA sob base."""
    achados: set[str] = set()
    for nome in MEMORIA:
        p = base / nome
        if p.is_file():
            achados.add(nome)
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.is_file():
                    achados.add(str(f.relative_to(base)))
    return achados


def tira_foto(data: str) -> int:
    destino = foto_dir(data)
    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)
    rels = arquivos(ROOT)
    for rel in rels:
        alvo = destino / rel
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, alvo)
    return len(rels)


def comeca(data: str, etapa: str) -> None:
    etapas = le(data) or {}
    if etapa == "pesquisa":
        # Pesquisa nova invalida o que veio depois dela numa tentativa anterior.
        etapas = {}
        n = tira_foto(data)
        print(f"Retomada: foto da memória antes do agente ({n} arquivos).")
    etapas[etapa] = {"comecou": agora(), "terminou": None}
    grava(data, etapas)


def termina(data: str, etapa: str) -> None:
    etapas = le(data) or {}
    etapas.setdefault(etapa, {"comecou": None})
    etapas[etapa]["terminou"] = agora()
    grava(data, etapas)


def decide(data: str) -> dict:
    """O que a execução seguinte do dia deve fazer. Não mexe em nada."""
    etapas = le(data) or {}
    roteiro = ROOT / "episodes" / f"{data}.md"
    pesquisa = etapas.get("pesquisa") or {}
    if not pesquisa.get("comecou"):
        # Sem pesquisa marcada: episódio de antes desta mudança, ou feito à mão.
        if roteiro.exists():
            return {"RETOMADA": "legado", "RETOMADA_PULA": "",
                    "RETOMADA_MSG": "Episódio do dia sem registro da pesquisa: vale a janela, como antes."}
        return {"RETOMADA": "nova", "RETOMADA_PULA": "", "RETOMADA_MSG": ""}
    if not pesquisa.get("terminou"):
        return {"RETOMADA": "refaz", "RETOMADA_PULA": "",
                "RETOMADA_MSG": ("A pesquisa de hoje começou às "
                                 f"{pesquisa['comecou'][11:16]} e não terminou: "
                                 "recomeça do zero, com a memória de antes dela.")}
    for etapa in ETAPAS[1:]:
        if not (etapas.get(etapa) or {}).get("terminou"):
            return {"RETOMADA": etapa, "RETOMADA_PULA": PULA[etapa],
                    "RETOMADA_MSG": (f"Retomando da {NOMES[etapa]}: a pesquisa terminou às "
                                     f"{pesquisa['terminou'][11:16]}, e o roteiro fica como está.")}
    return {"RETOMADA": "completo", "RETOMADA_PULA": "",
            "RETOMADA_MSG": "Todas as etapas de hoje terminaram."}


def desfaz(data: str) -> list[str]:
    """Guarda o que a pesquisa interrompida deixou e devolve a memória à foto.
    Só age se a pesquisa começou e não terminou; repetir não muda nada."""
    etapas = le(data)
    pesquisa = (etapas or {}).get("pesquisa") or {}
    if not pesquisa.get("comecou") or pesquisa.get("terminou"):
        return []
    guarda = logs() / f"{data}-interrompido-{dt.datetime.now():%H%M%S}"
    linhas: list[str] = []

    def guarda_copia(rel: str, mover: bool) -> None:
        alvo = guarda / rel
        alvo.parent.mkdir(parents=True, exist_ok=True)
        (shutil.move if mover else shutil.copy2)(str(ROOT / rel), str(alvo))

    for rel in (f"episodes/{data}.md", f"research/{data}.md"):
        if (ROOT / rel).exists():
            guarda_copia(rel, mover=True)
            linhas.append(f"Retomada: {rel} guardado em {guarda.relative_to(ROOT)}/")

    foto = foto_dir(data)
    if foto.is_dir():
        antes, depois = arquivos(foto), arquivos(ROOT)
        mudou = sorted(r for r in antes & depois
                       if not filecmp.cmp(foto / r, ROOT / r, shallow=False))
        novos = sorted(depois - antes)
        sumiram = sorted(antes - depois)
        for rel in mudou + novos:
            guarda_copia(rel, mover=rel in novos)
        for rel in mudou + sumiram:
            (ROOT / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(foto / rel, ROOT / rel)
        if mudou or novos or sumiram:
            linhas.append("Retomada: memória de volta à foto de antes do agente "
                          f"({len(mudou)} alterado(s), {len(novos)} novo(s), "
                          f"{len(sumiram)} apagado(s)): " + ", ".join(mudou + novos + sumiram))
    elif linhas:
        linhas.append("AVISO: sem foto da memória; o índice, o backlog e a memória ficam como o agente deixou.")

    pesquisa["desfeita"] = agora()
    if linhas:
        pesquisa["guardado_em"] = str(guarda.relative_to(ROOT))
    grava(data, etapas)
    return linhas


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("acao", choices=["comeca", "termina", "decide", "desfaz"])
    ap.add_argument("--data", required=True)
    ap.add_argument("--etapa", choices=ETAPAS)
    a = ap.parse_args()
    dt.date.fromisoformat(a.data)
    if a.acao in ("comeca", "termina"):
        if not a.etapa:
            ap.error("--etapa é obrigatória para comeca e termina")
        (comeca if a.acao == "comeca" else termina)(a.data, a.etapa)
    elif a.acao == "decide":
        for k, v in decide(a.data).items():
            print(f"{k}={shlex.quote(v)}")
    else:
        for linha in desfaz(a.data):
            print(linha)
    return 0


if __name__ == "__main__":
    sys.exit(main())
