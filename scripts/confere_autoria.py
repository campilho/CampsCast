#!/usr/bin/env python3
"""
CampsCast — quem escreveu o texto que vai ao ar.

A ficha técnica diz no ar qual modelo escreveu o roteiro, e o orquestrador
tira o nome do modelo que ele pediu ao CLI. Em 25/11 o filtro de segurança
marcou a sessão ("[bio]") e o CLI passou o resto dela ao Opus 4.8 sem
perguntar. Na produção, o roteiro já estava escrito pelo Opus 5.5 e o 4.8 só
trocou a contagem de palavras no cabeçalho. Na sombra do mesmo dia, as quatro
variantes foram cortadas também; em três o corte veio no meio da pesquisa, e
o 4.8 escreveu o roteiro inteiro.

Este script lê a transcrição da sessão (e as dos subagentes) e confere cada
escrita no roteiro do dia: Write, Edit e MultiEdit pelo caminho do arquivo, e
Bash que cita o arquivo, tem cara de escrita e não foi barrado. Daí sai quem
escreveu o corpo, em ordem:

- só o modelo pedido: segue; outro modelo só no cabeçalho (o trecho novo
  aparece no front-matter do roteiro final e não no corpo) vira aviso;
- outro modelo no corpo: a ficha diria um nome falso. Com --corrige, o script
  reescreve o nome de quem escreveu na frase da ficha ("Escrito pelo Claude
  Opus cinco ponto cinco e terminado pelo Claude Opus quatro ponto oito,
  depois que o filtro de segurança interrompeu a sessão, e narrado...") e o
  episódio sai com a pauta que o agente escolheu (decisão do autor, 26/11):
  refazer a pesquisa, no dia de uma pauta que o filtro corta, tende a ser
  cortado de novo. Sem a frase para corrigir, ou sem --corrige, bloqueia.

Saída 0 com os avisos no stdout, um por linha, para o registro; saída 3 com o
motivo numa linha, e o orquestrador não publica: a pesquisa conta como
falha, e a repescagem refaz (scripts/retomada.py). Sem transcrição não há o
que conferir: uma linha no log, e segue.

Uso:
    python3 scripts/confere_autoria.py --agente logs/...-agente.json \\
        --modelo claude-opus-5-5 --roteiro episodes/2026-11-25.md [--corrige]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

BLOQUEIA = 3
# "Opus 5.5's safeguards stopped the response above", "... flagged this session"
FILTRO = "safeguards"


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
            negadas: set[str]) -> tuple[list[str], list[str], list[str], bool]:
    """(avisos, quem escreveu o corpo em ordem, o que os outros modelos fizeram
    no corpo, se o filtro de segurança cortou a sessão)"""
    from transcricoes import entradas
    nome = f"episodes/{roteiro.name}"
    try:
        cabecalho, corpo = partes(roteiro.read_text(encoding="utf-8"))
    except OSError:
        cabecalho, corpo = "", ""
    avisos: list[str] = []
    autores: list[str] = []
    feitos: list[str] = []
    filtro = False

    def escreveu(modelo: str, o_que: str) -> None:
        if modelo not in autores:
            autores.append(modelo)
        if not do_modelo(modelo, pedido):
            feitos.append(f"{modelo} {o_que}")

    # Em ordem de tempo, sessão e subagentes juntos: um Write depois de outras
    # escritas apaga o que elas fizeram.
    ordem = sorted((e for e, _ in entradas(transcricao) if isinstance(e, dict)),
                   key=lambda e: str(e.get("timestamp") or ""))
    for entrada in ordem:
        if entrada.get("type") == "system":
            filtro = filtro or FILTRO in str(entrada.get("content") or "").lower()
            continue
        m = entrada.get("message")
        if not isinstance(m, dict):
            continue
        modelo = m.get("model") or ""
        if not modelo or modelo == "<synthetic>":
            continue
        alheio = not do_modelo(modelo, pedido)
        for c in m.get("content") or []:
            if not (isinstance(c, dict) and c.get("type") == "tool_use"):
                continue
            ferramenta, entrada_f = c.get("name"), c.get("input") or {}
            if ferramenta in ("Write", "Edit", "MultiEdit"):
                if not str(entrada_f.get("file_path", "")).endswith(nome):
                    continue
                if ferramenta == "Write":
                    avisos, feitos = [], []
                    autores.clear()
                    escreveu(modelo, "reescreveu o roteiro inteiro")
                    continue
                trechos = entrada_f.get("edits") if ferramenta == "MultiEdit" else [entrada_f]
                for t in trechos or []:
                    novo = str(t.get("new_string") or "").strip()
                    if novo and novo in cabecalho and novo not in corpo:
                        if alheio:
                            avisos.append(f"{modelo} mexeu só no cabeçalho do roteiro"
                                          f" ({novo.splitlines()[0][:60]})")
                    else:
                        escreveu(modelo, f"editou o corpo do roteiro"
                                         f" ({(novo or 'trecho apagado').splitlines()[0][:60]})")
            elif ferramenta == "Bash":
                comando = str(entrada_f.get("command", ""))
                if escreve_pelo_shell(comando, nome) and c.get("id") not in negadas:
                    escreveu(modelo, f"mexeu no roteiro pelo shell ({comando.splitlines()[0][:60]})")
    return avisos, autores, feitos, filtro


def _nomes(modelo: str) -> tuple[str, str]:
    """claude-opus-4-8 -> ("Claude Opus 4.8", "Claude Opus quatro ponto oito")."""
    from confere_roteiro import falado
    from nomes import nome_agente
    escrito = nome_agente(modelo)
    return escrito, falado(escrito)


def quem_escreveu(autores: list[str], pedido: str, filtro: bool) -> str:
    """O trecho da ficha depois de "Escrito pelo", como se fala."""
    falados = [_nomes(a)[1] for a in autores]
    frase = falados[0] + "".join(f" e terminado pelo {f}" for f in falados[1:])
    if filtro:
        de_quem = f" do {_nomes(pedido)[1]}" if len(falados) == 1 else ""
        frase += f", depois que o filtro de segurança{de_quem} interrompeu a sessão"
    return frase


def corrige_ficha(roteiro: pathlib.Path, autores: list[str], pedido: str,
                  filtro: bool) -> tuple[str, str]:
    """Reescreve na ficha o nome de quem escreveu. ("corrigida", trecho novo),
    ("ja", trecho) quando o agente já citou mais de um modelo ali, ou
    ("sem_frase", "") quando não há "Escrito pelo <modelo>" no corpo."""
    texto = roteiro.read_text(encoding="utf-8")
    _, corpo = partes(texto)
    inicio = len(texto) - len(corpo)
    formas = {f for m in [pedido, *autores] for f in _nomes(m)}
    nomes_re = "|".join(r"\s+".join(map(re.escape, f.split()))
                        for f in sorted(formas, key=len, reverse=True))
    achados = list(re.finditer(rf"(escrit[oa]\s+(?:pel[oa]|por)\s+(?:o\s+)?)({nomes_re})",
                               texto[inicio:], re.I))
    if not achados:
        return "sem_frase", ""
    m = achados[-1]
    depois = texto[inicio + m.end():]
    # O próprio agente já disse que foram dois modelos: não se escreve por cima.
    if re.match(rf"[^.]{{0,80}}?({nomes_re})", depois, re.I):
        return "ja", (m.group(2) + depois.split(".")[0])[:160]
    trecho = quem_escreveu(autores, pedido, filtro)
    if "," in trecho or len(autores) > 1:
        if re.match(r"\s+e\s", depois):
            trecho += ","
    novo_corpo = texto[inicio:inicio + m.start(2)] + trecho + texto[inicio + m.end(2):]
    cabecalho = texto[:inicio]
    # A contagem do cabeçalho é do agente; soma só o que a correção acrescentou.
    delta = len(novo_corpo.split()) - len(corpo.split())
    cabecalho = re.sub(r"^(words:\s*)(\d+)\s*$", lambda w: f"{w[1]}{int(w[2]) + delta}",
                       cabecalho, count=1, flags=re.M)
    roteiro.write_text(cabecalho + novo_corpo, encoding="utf-8")
    return "corrigida", trecho


def main() -> int:
    ap = argparse.ArgumentParser(description="Quem escreveu o texto que vai ao ar.")
    ap.add_argument("--agente", required=True, help="JSON final do claude -p (logs/*-agente.json)")
    ap.add_argument("--modelo", required=True, help="modelo que a ficha técnica vai dizer no ar")
    ap.add_argument("--roteiro", required=True)
    ap.add_argument("--corrige", action="store_true",
                    help="outro modelo escreveu no corpo: reescreve na ficha quem escreveu, em vez de bloquear")
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
    roteiro = pathlib.Path(a.roteiro)
    avisos, autores, feitos, filtro = confere(transcricao, a.modelo, roteiro, negadas)
    if any(not do_modelo(m, a.modelo) for m in autores):
        motivo = "; ".join(dict.fromkeys(feitos))
        if not a.corrige:
            print(f"o roteiro não é só do {a.modelo}, que a ficha técnica diria no ar: {motivo}")
            return BLOQUEIA
        estado, trecho = corrige_ficha(roteiro, autores, a.modelo, filtro)
        if estado == "sem_frase":
            print(f"o roteiro não é só do {a.modelo}, e a ficha técnica não tem a frase de quem"
                  f" escreveu para corrigir: {motivo}")
            return BLOQUEIA
        corte = "o filtro de segurança cortou a sessão e " if filtro else ""
        if estado == "ja":
            print(f"autoria: {corte}{motivo}; a ficha já diz \"{trecho}\", e ficou como o agente escreveu")
        else:
            print(f"autoria: {corte}{motivo}; ficha técnica corrigida para \"Escrito pelo {trecho.rstrip(',')}\"")
        return 0
    for aviso in dict.fromkeys(avisos):
        print(f"autoria: {aviso}; o texto narrado é do {a.modelo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
