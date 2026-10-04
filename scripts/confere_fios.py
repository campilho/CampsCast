#!/usr/bin/env python3
"""
CampsCast — confere o arquivo de fios em aberto (memoria/fios.md).

Fios são preocupações, promessas e previsões que apareceram no ar e ainda não
tiveram desfecho (ADR 0008). O agente abre, acrescenta marcos e fecha. O
arquivo é lido inteiro todo dia, então tem teto: 20 fios abertos, 3 marcos por
fio, ~10 KB — um fio com três marcos tem uns 500 bytes.

Não bloqueia: imprime uma linha por problema, e o orquestrador grava no
registro junto com os avisos do roteiro. Confere:

- campos de cada fio (aberto, pergunta, situação, rever até) e id único;
- situação dentro da lista; fio que não está mais aberto deveria ter ido
  para memoria/fios-fechados/;
- data de revisão vencida;
- episódio citado (na abertura ou num marco) que não existe;
- mais de 3 marcos, mais de 20 fios, arquivo acima do teto;
- texto fora do formato depois do cabeçalho.

Com --temas, confere também memoria/temas.md: as questões de fundo que nunca
fecham (desacelerar a fronteira, a busca pela AGI...). Tema é linha editorial,
criado pelo autor; o agente só reescreve o estado e os episódios recentes.
Teto de 10 temas e 3 recentes. Tema criado pelo autor antes de ter episódio
diz "(criado pelo autor)" no lugar do número. O fio aponta para os temas
("- temas: T-01, T-02"); a lista de fios de um tema é calculada a partir daí,
não armazenada — e fio que aponta para tema inexistente vira aviso.

Com --sugestoes, confere memoria/temas-sugeridos.md: temas que o agente (e,
no futuro, ouvintes) sugere e o autor decide — pendente, aprovado ou recusado.
Acima de 10 pendentes, o agente deveria parar de sugerir e esperar decisão.

Uso:
    python3 scripts/confere_fios.py memoria/fios.md --temas memoria/temas.md \
        --data 2026-10-05
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITUACOES = {"aberto", "cumprido", "desmentido", "resolvido", "arquivado"}
MAX_FIOS, MAX_MARCOS, TETO_BYTES = 20, 3, 10 * 1024
MAX_TEMAS, MAX_RECENTES = 10, 3
MAX_PENDENTES = 10
SITUACOES_SUGESTAO = {"pendente", "aprovado", "recusado"}

TITULO = re.compile(r"^## (F-\d{3})\b")
TITULO_TEMA = re.compile(r"^## (T-\d{2})\b")
TITULO_SUGESTAO = re.compile(r"^## (S-\d{3})\b")
# "estado (2026-10-02): ..." vira o campo "estado"; o que está entre parênteses
# no nome do campo é anotação, não parte dele.
CAMPO = re.compile(r"^- ([^:(]+?)\s*(?:\([^)]*\))?:\s*(.*)$")
MARCO = re.compile(r"^\s+- (\d{4}-\d{2}-\d{2})\b")
DATA = re.compile(r"\d{4}-\d{2}-\d{2}")


def _fios(linhas: list[str], titulo: re.Pattern = TITULO) -> tuple[list[dict], list[str]]:
    fios, fora, atual = [], [], None
    for linha in linhas:
        m = titulo.match(linha)
        if m:
            atual = {"id": m[1], "campos": {}, "marcos": []}
            fios.append(atual)
            continue
        if not linha.strip():
            continue
        if atual is None:
            fora.append(linha)
            continue
        if MARCO.match(linha):
            atual["marcos"].append(MARCO.match(linha)[1])
        elif CAMPO.match(linha):
            c = CAMPO.match(linha)
            atual["campos"][c[1].strip()] = c[2].strip()
        elif not linha.startswith("  "):
            fora.append(linha)
    return fios, fora


def confere(texto: str, data: str, episodios: pathlib.Path) -> list[str]:
    linhas = texto.splitlines()
    try:
        linhas = linhas[linhas.index("---") + 1:]
    except ValueError:
        pass
    fios, fora = _fios(linhas)
    avisos, vistos = [], set()
    existe = lambda d: (episodios / f"{d}.md").exists()
    for f in fios:
        i, c = f["id"], f["campos"]
        if i in vistos:
            avisos.append(f"fios: {i} repetido")
        vistos.add(i)
        faltando = [k for k in ("aberto", "pergunta", "situação", "rever até") if k not in c]
        if faltando:
            avisos.append(f"fios: {i} sem {', '.join(faltando)}")
        situacao = c.get("situação", "")
        if situacao and situacao not in SITUACOES:
            avisos.append(f"fios: {i} com situação desconhecida: {situacao}")
        elif situacao and situacao != "aberto":
            avisos.append(f"fios: {i} está {situacao}, mas não foi fechado — "
                          "mover para memoria/fios-fechados/")
        revisar = DATA.search(c.get("rever até", ""))
        if revisar and revisar[0] < data:
            avisos.append(f"fios: {i} passou do rever até {revisar[0]}")
        if len(f["marcos"]) > MAX_MARCOS:
            avisos.append(f"fios: {i} com mais de {MAX_MARCOS} marcos ({len(f['marcos'])})")
        abertura = DATA.search(c.get("aberto", ""))
        for d in ([abertura[0]] if abertura else []) + f["marcos"]:
            if not existe(d):
                avisos.append(f"fios: {i} cita episódio de {d}, que não existe")
    abertos = sum(1 for f in fios if f["campos"].get("situação") == "aberto")
    if abertos > MAX_FIOS:
        avisos.append(f"fios: {abertos} fios abertos, acima do teto de {MAX_FIOS}")
    tamanho = len(texto.encode("utf-8"))
    if tamanho > TETO_BYTES:
        avisos.append(f"fios: arquivo com {tamanho // 1024} KB, acima do teto de "
                      f"{TETO_BYTES // 1024} KB")
    if fora:
        avisos.append(f"fios: {len(fora)} linhas fora do formato, a primeira: "
                      f"{fora[0].strip()[:70]}")
    return avisos


def _depois_do_cabecalho(texto: str) -> list[str]:
    linhas = texto.splitlines()
    try:
        return linhas[linhas.index("---") + 1:]
    except ValueError:
        return linhas


def confere_temas(texto: str, fios_texto: str, episodios: pathlib.Path) -> list[str]:
    temas, fora = _fios(_depois_do_cabecalho(texto), TITULO_TEMA)
    avisos, vistos = [], set()
    existe = lambda d: (episodios / f"{d}.md").exists()
    for t in temas:
        i, c = t["id"], t["campos"]
        if i in vistos:
            avisos.append(f"temas: {i} repetido")
        vistos.add(i)
        faltando = [k for k in ("desde", "pergunta de fundo", "estado") if k not in c]
        if faltando:
            avisos.append(f"temas: {i} sem {', '.join(faltando)}")
        recentes = DATA.findall(c.get("recentes", ""))
        if len(recentes) > MAX_RECENTES:
            avisos.append(f"temas: {i} com mais de {MAX_RECENTES} recentes ({len(recentes)})")
        desde = c.get("desde", "")
        citados = (DATA.findall(desde)[:1] if "ep." in desde else []) + recentes
        for d in citados:
            if not existe(d):
                avisos.append(f"temas: {i} cita episódio de {d}, que não existe")
    if len(temas) > MAX_TEMAS:
        avisos.append(f"temas: {len(temas)} temas, acima do teto de {MAX_TEMAS}")
    if fora:
        avisos.append(f"temas: {len(fora)} linhas fora do formato, a primeira: "
                      f"{fora[0].strip()[:70]}")
    for f in _fios(_depois_do_cabecalho(fios_texto))[0]:
        for ref in re.findall(r"T-\d{2}", f["campos"].get("temas", "")):
            if ref not in vistos:
                avisos.append(f"fios: {f['id']} aponta para {ref}, que não existe em temas")
    return avisos


def sugestoes(texto: str) -> list[dict]:
    return _fios(_depois_do_cabecalho(texto), TITULO_SUGESTAO)[0]


def confere_sugestoes(texto: str, episodios: pathlib.Path) -> list[str]:
    itens, fora = _fios(_depois_do_cabecalho(texto), TITULO_SUGESTAO)
    avisos, vistos = [], set()
    for s in itens:
        i, c = s["id"], s["campos"]
        if i in vistos:
            avisos.append(f"sugestões: {i} repetida")
        vistos.add(i)
        faltando = [k for k in ("sugerido", "pergunta de fundo", "por quê", "situação") if k not in c]
        if faltando:
            avisos.append(f"sugestões: {i} sem {', '.join(faltando)}")
        situacao = c.get("situação", "")
        if situacao and situacao not in SITUACOES_SUGESTAO:
            avisos.append(f"sugestões: {i} com situação desconhecida: {situacao}")
        sugerido = c.get("sugerido", "")
        if "ep." in sugerido:
            for d in DATA.findall(sugerido)[:1]:
                if not (episodios / f"{d}.md").exists():
                    avisos.append(f"sugestões: {i} cita episódio de {d}, que não existe")
    pendentes = sum(1 for s in itens if s["campos"].get("situação") == "pendente")
    if pendentes > MAX_PENDENTES:
        avisos.append(f"sugestões: {pendentes} pendentes, acima de {MAX_PENDENTES}")
    if fora:
        avisos.append(f"sugestões: {len(fora)} linhas fora do formato, a primeira: "
                      f"{fora[0].strip()[:70]}")
    return avisos


def contagem_temas(texto: str) -> int:
    return len(_fios(_depois_do_cabecalho(texto), TITULO_TEMA)[0])


def contagem(texto: str) -> int:
    """Fios abertos — para o registro de execução."""
    linhas = texto.splitlines()
    try:
        linhas = linhas[linhas.index("---") + 1:]
    except ValueError:
        pass
    return sum(1 for f in _fios(linhas)[0] if f["campos"].get("situação") == "aberto")


def main() -> int:
    ap = argparse.ArgumentParser(description="Confere memoria/fios.md.")
    ap.add_argument("arquivo")
    ap.add_argument("--data", required=True, help="data do episódio (AAAA-MM-DD)")
    ap.add_argument("--temas", help="memoria/temas.md, conferido junto")
    ap.add_argument("--sugestoes", help="memoria/temas-sugeridos.md, conferido junto")
    ap.add_argument("--episodios", default=str(ROOT / "episodes"))
    a = ap.parse_args()
    try:
        texto = pathlib.Path(a.arquivo).read_text(encoding="utf-8")
    except OSError as e:
        print(f"fios: não foi possível ler ({e})")
        return 0
    avisos = confere(texto, a.data, pathlib.Path(a.episodios))
    if a.temas:
        try:
            temas = pathlib.Path(a.temas).read_text(encoding="utf-8")
            avisos += confere_temas(temas, texto, pathlib.Path(a.episodios))
        except OSError as e:
            avisos.append(f"temas: não foi possível ler ({e})")
    if a.sugestoes:
        try:
            sug = pathlib.Path(a.sugestoes).read_text(encoding="utf-8")
            avisos += confere_sugestoes(sug, pathlib.Path(a.episodios))
        except OSError as e:
            avisos.append(f"sugestões: não foi possível ler ({e})")
    for aviso in avisos:
        print(aviso)
    return 0


if __name__ == "__main__":
    sys.exit(main())
