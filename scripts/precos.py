#!/usr/bin/env python3
"""
CampsCast — preço dos modelos, para quando o CLI não sabe.

O CLI 2.1.283 calcula o custo de cada modelo da sessão (`costUSD` no
`modelUsage` do JSON final), mas só dos que conhece: o Haiku 5.5 e o Sonnet
5.5 saem com `costBasis: "unknown"` e preço de Opus 5.5 (ADR 0013). O registro
recalcula esses por esta tabela; os outros ficam com a conta do CLI, que bate
até o centavo com a tabela oficial.

Preço oficial por milhão de tokens, US$, conferido em 08/11/2026 (skill
claude-api da Anthropic). Leitura de cache a 10% da entrada quando a tabela
não traz; escrita de cache a 1,25× (5 minutos, a dos subagentes) ou 2× (1
hora, a da sessão principal). O Haiku 5.5 cobra 0,50/2,50 quando o prompt
passa de 100 mil tokens; o `modelUsage` soma a sessão inteira e não diz o
tamanho de cada pedido, então a conta usa a faixa de baixo — a de um
Jornalista, que lê resumos e não páginas inteiras.
"""
from __future__ import annotations

PRECOS = {  # modelo canônico → entrada, saída, cache lido
    "claude-opus-5-5": {"in": 4.0, "out": 20.0, "lido": 0.20},
    "claude-sonnet-5-5": {"in": 2.0, "out": 10.0, "lido": 0.20},
    "claude-haiku-5-5": {"in": 0.10, "out": 0.50, "lido": 0.01},
    "claude-haiku-4-5": {"in": 1.0, "out": 5.0, "lido": 0.10},
}
HAIKU55_ACIMA_DE_100K = {"in": 0.50, "out": 2.50, "lido": 0.05}


def canonico(modelo: str) -> str | None:
    """'claude-haiku-4-5-20251001' → 'claude-haiku-4-5'; desconhecido → None."""
    for nome in sorted(PRECOS, key=len, reverse=True):
        if modelo == nome or modelo.startswith(nome + "-"):
            return nome
    return None


def custo(modelo: str, uso: dict, escrita: float = 1.25, faixa: dict | None = None) -> float | None:
    """Custo em US$ de um modelo, com os campos do `modelUsage` do CLI
    (inputTokens, outputTokens, cacheReadInputTokens, cacheCreationInputTokens).
    `escrita` é o multiplicador da escrita de cache. None se o modelo não
    estiver na tabela."""
    nome = canonico(modelo)
    if nome is None:
        return None
    p = faixa or PRECOS[nome]
    g = lambda k: (uso or {}).get(k) or 0
    return (g("inputTokens") * p["in"] + g("cacheCreationInputTokens") * p["in"] * escrita
            + g("cacheReadInputTokens") * p["lido"] + g("outputTokens") * p["out"]) / 1e6
