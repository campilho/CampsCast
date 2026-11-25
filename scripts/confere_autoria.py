#!/usr/bin/env python3
"""
CampsCast — quem escreveu o texto que vai ao ar.

A ficha técnica diz no ar qual modelo escreveu o roteiro, e o orquestrador
tira o nome do modelo que ele pediu ao CLI. Em 25/11 o filtro de segurança
marcou a sessão ("[bio]") e o CLI passou o resto dela ao Opus 4.8 sem
perguntar. O roteiro já estava escrito pelo Opus 5.5, e o 4.8 só trocou a
contagem de palavras no cabeçalho; se a marca viesse antes da escrita, o
episódio iria ao ar dizendo "escrito pelo Claude Opus 5.5" com texto do 4.8.

Este script lê a transcrição da sessão (e as dos subagentes) e confere cada
escrita no roteiro do dia: Write, Edit e MultiEdit pelo caminho do arquivo, e
Bash que cita o arquivo, tem cara de escrita e não foi barrado. Escrita de um
modelo que não é o pedido:

- só no cabeçalho (o trecho novo aparece no front-matter do roteiro final e
  não no corpo): aviso, e segue;
- no corpo, ou onde não dá para saber (Write, trecho apagado, Bash): bloqueia.

Saída 0 com os avisos no stdout, um por linha, para o registro; saída 3 com o
motivo numa linha, e o orquestrador não publica: a pesquisa conta como
falha, e a repescagem refaz (scripts/retomada.py). Sem transcrição não há o
que conferir: uma linha no log, e segue.

Uso:
    python3 scripts/confere_autoria.py --agente logs/...-agente.json \\
        --modelo claude-opus-5-5 --roteiro episodes/2026-11-25.md
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

BLOQUEIA = 3


def escreve_pelo_shell(comando: str, nome: str) -> bool:
    """Comando de shell que escreve no roteiro: redirecionamento para ele,
    edição no lugar, tee, cópia ou movimento por cima, e escrita do Python com
    o nome do arquivo no comando (o caminho costuma ir numa variável). Ler,
    contar e procurar não contam: em 25/11 o Opus 4.8 contou palavras com awk,
    e o "c>=2" dele não é redirecionamento."""
    if nome not in comando:
        return False
    alvo = re.escape(nome)
    return bool(
        re.search(rf"(?<![<>=!0-9&])>>?\s*[\"']?[^\s\"';|&]*{alvo}", comando)
        or re.search(r"\b(sed|perl)\s+(-[a-zA-Z]*\s+)*-[a-zA-Z]*i", comando)
        or re.search(rf"\btee\b[^|;&]*{alvo}", comando)
        or re.search(rf"\b(mv|cp|rsync)\b[^|;&]*{alvo}[\"']?\s*($|[;&|])", comando)
        or re.search(r"write_text|\.write\(|open\([^)]*,\s*[\"'][wa]", comando))


def partes(texto: str) -> tuple[str, str]:
    """Cabeçalho (front-matter) e corpo do roteiro."""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", texto, re.S)
    return (m.group(1), m.group(2)) if m else ("", texto)


def do_modelo(modelo: str, pedido: str) -> bool:
    return bool(pedido) and (modelo == pedido or modelo.startswith(pedido))


def confere(transcricao: pathlib.Path, pedido: str, roteiro: pathlib.Path,
            negadas: set[str]) -> tuple[list[str], list[str]]:
    """(avisos, bloqueios)"""
    from transcricoes import entradas
    nome = f"episodes/{roteiro.name}"
    try:
        cabecalho, corpo = partes(roteiro.read_text(encoding="utf-8"))
    except OSError:
        cabecalho, corpo = "", ""
    avisos: list[str] = []
    bloqueios: list[str] = []
    # Em ordem de tempo, sessão e subagentes juntos: um Write do modelo pedido
    # depois de uma escrita alheia apaga o que ela fez.
    ordem = sorted((e for e, _ in entradas(transcricao) if isinstance(e, dict)),
                   key=lambda e: str(e.get("timestamp") or ""))
    for entrada in ordem:
        m = entrada.get("message")
        if not isinstance(m, dict):
            continue
        modelo = m.get("model") or ""
        if not modelo or modelo == "<synthetic>":
            continue
        if do_modelo(modelo, pedido):
            if any(isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == "Write"
                   and str((c.get("input") or {}).get("file_path", "")).endswith(nome)
                   for c in m.get("content") or []):
                avisos, bloqueios = [], []
            continue
        for c in m.get("content") or []:
            if not (isinstance(c, dict) and c.get("type") == "tool_use"):
                continue
            ferramenta, entrada_f = c.get("name"), c.get("input") or {}
            if ferramenta in ("Write", "Edit", "MultiEdit"):
                if not str(entrada_f.get("file_path", "")).endswith(nome):
                    continue
                if ferramenta == "Write":
                    bloqueios.append(f"{modelo} reescreveu o roteiro inteiro")
                    continue
                trechos = entrada_f.get("edits") if ferramenta == "MultiEdit" else [entrada_f]
                for t in trechos or []:
                    novo = str(t.get("new_string") or "").strip()
                    if novo and novo in cabecalho and novo not in corpo:
                        avisos.append(f"{modelo} mexeu só no cabeçalho do roteiro"
                                      f" ({novo.splitlines()[0][:60]})")
                    else:
                        bloqueios.append(f"{modelo} editou o corpo do roteiro"
                                         f" ({(novo or 'trecho apagado').splitlines()[0][:60]})")
            elif ferramenta == "Bash":
                comando = str(entrada_f.get("command", ""))
                if escreve_pelo_shell(comando, nome) and c.get("id") not in negadas:
                    bloqueios.append(f"{modelo} mexeu no roteiro pelo shell ({comando.splitlines()[0][:60]})")
    return avisos, bloqueios


def main() -> int:
    ap = argparse.ArgumentParser(description="Quem escreveu o texto que vai ao ar.")
    ap.add_argument("--agente", required=True, help="JSON final do claude -p (logs/*-agente.json)")
    ap.add_argument("--modelo", required=True, help="modelo que a ficha técnica vai dizer no ar")
    ap.add_argument("--roteiro", required=True)
    a = ap.parse_args()
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from memoria_custo import transcricoes_dir
    try:
        dados = json.loads(pathlib.Path(a.agente).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        dados = {}
    sid = dados.get("session_id")
    transcricao = transcricoes_dir() / f"{sid}.jsonl" if sid else None
    if not transcricao or not transcricao.exists():
        print("Autoria: sem transcrição da sessão; não deu para conferir quem escreveu o roteiro",
              file=sys.stderr)
        return 0
    negadas = {d.get("tool_use_id") for d in dados.get("permission_denials") or [] if isinstance(d, dict)}
    avisos, bloqueios = confere(transcricao, a.modelo, pathlib.Path(a.roteiro), negadas)
    if bloqueios:
        print(f"o roteiro não é só do {a.modelo}, que a ficha técnica diria no ar: "
              + "; ".join(dict.fromkeys(bloqueios)))
        return BLOQUEIA
    for aviso in dict.fromkeys(avisos):
        print(f"autoria: {aviso}; o texto narrado é do {a.modelo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
