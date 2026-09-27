#!/usr/bin/env python3
"""
CampsCast — confere se o roteiro diz o que não pode deixar de dizer.

Abertura e encerramento variam de um dia para o outro por decisão de projeto:
o agente escreve no tom, não num texto fixo. O que não varia são os
compromissos de transparência — o número do episódio, "sou um agente de IA",
quem escreveu, que a voz é sintética — e duas regras de forma: despedir com
"até o próximo episódio" (não há episódio no fim de semana) e não usar o
apelido do autor.

Não bloqueia nada. Imprime uma linha por regra que caiu, e o orquestrador
grava no registro. É a medição do experimento: com liberdade, quantas vezes o
agente deixa cair uma regra? Se começar a cair, a regra endurece.

Uso:
    python3 scripts/confere_roteiro.py episodes/2026-09-28.md \
        --numero 22 --agente "Claude Opus 5.5"
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

UNIDADES = ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete",
            "oito", "nove", "dez", "onze", "doze", "treze", "catorze", "quinze",
            "dezesseis", "dezessete", "dezoito", "dezenove"]
DEZENAS = ["", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta",
           "setenta", "oitenta", "noventa"]
CENTENAS = ["", "cento", "duzentos", "trezentos", "quatrocentos", "quinhentos",
            "seiscentos", "setecentos", "oitocentos", "novecentos"]

# A abertura fica nas primeiras palavras e a ficha nas últimas; procurar no
# texto inteiro aceitaria "agente de IA" dito numa pauta sobre agentes.
INICIO, FIM = 220, 160


def extenso(n: int) -> str:
    """0 a 999, em português, como o agente fala o número do episódio."""
    if n < 20:
        return UNIDADES[n]
    if n < 100:
        d, u = divmod(n, 10)
        return DEZENAS[d] + (f" e {UNIDADES[u]}" if u else "")
    if n == 100:
        return "cem"
    c, r = divmod(n, 100)
    return CENTENAS[c] + (f" e {extenso(r)}" if r else "")


def falado(nome: str) -> str:
    """"Claude Opus 5.5" -> "Claude Opus cinco ponto cinco"."""
    # Decimal primeiro: trocar os inteiros antes comeria o "5" depois do ponto.
    s = re.sub(r"(\d+)\.(\d+)",
               lambda m: f"{extenso(int(m[1]))} ponto {extenso(int(m[2]))}", nome)
    return re.sub(r"\d+", lambda m: extenso(int(m[0])), s)


def corpo(texto: str) -> str:
    partes = texto.split("---", 2)
    return partes[2] if texto.startswith("---") and len(partes) == 3 else texto


# A chamada é "siga o CampsCast", "seguir o podcast"... — e não qualquer "segue",
# que aparece à toa em frase de transição.
CHAMADA = re.compile(r"\b(siga|sigam|seguir|segue)\b( a gente| o| a)? (campscast|podcast|programa)")


def confere(texto: str, numero: int | None, agente: str | None,
            chamada: str | None = None) -> list[str]:
    palavras = corpo(texto).lower().replace("quatorze", "catorze").split()
    inicio, fim = " ".join(palavras[:INICIO]), " ".join(palavras[-FIM:])
    tudo = " ".join(palavras)
    faltas = []
    if numero is not None and not re.search(
            rf"episódio (n[º°o]\.? )?({re.escape(extenso(numero))}|{numero})\b", inicio):
        faltas.append(f"abertura sem o número do episódio ({extenso(numero)})")
    if not re.search(r"agente de (ia|inteligência artificial)\b", inicio):
        faltas.append("abertura sem 'agente de IA'")
    if agente and agente.lower() not in fim and falado(agente).lower() not in fim:
        faltas.append(f"ficha sem o nome de quem escreveu ({agente})")
    if "sintétic" not in fim:
        faltas.append("ficha sem dizer que a voz é sintética")
    if "até o próximo episódio" not in fim:
        faltas.append("encerramento sem 'até o próximo episódio'")
    if "até amanhã" in fim:
        faltas.append("encerramento promete 'até amanhã'")
    if chamada == "sim" and not CHAMADA.search(tudo):
        faltas.append("dia de chamada para seguir, e ela não apareceu")
    if chamada == "não" and CHAMADA.search(tudo):
        faltas.append("chamada para seguir fora dos dias dela")
    if re.search(r"\bcamps\b", tudo):
        faltas.append("usa o apelido 'Camps' — o autor é Fernando Campilho")
    return faltas


def main() -> int:
    ap = argparse.ArgumentParser(description="Confere o roteiro.")
    ap.add_argument("roteiro")
    ap.add_argument("--numero", type=int)
    ap.add_argument("--agente")
    ap.add_argument("--chamada", choices=["sim", "não"])
    a = ap.parse_args()
    try:
        texto = pathlib.Path(a.roteiro).read_text(encoding="utf-8")
    except OSError as e:
        print(f"não consegui ler o roteiro ({e})")
        return 0
    for f in confere(texto, a.numero, a.agente or None, a.chamada):
        print(f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
