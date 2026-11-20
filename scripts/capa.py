#!/usr/bin/env python3
"""Capa do episódio: a capa do programa, em verde, com número e data.

    python3 scripts/capa.py 2026-11-23            # grava assets/capas/2026-11-23.png
    python3 scripts/capa.py 2026-11-23 --refaz    # refaz mesmo se já existir
    python3 scripts/capa.py 2026-11-23 --saida /tmp/x.png --numero 59

O `publish.py` põe no feed a capa de quem tiver `assets/capas/AAAA-MM-DD.png`
(ou `.jpg`, como a âmbar do teste de 19/11). O Spotify e a Apple leem essa capa
do feed, e no Spotify a miniatura do programa vira a do episódio mais novo —
por isso ela é a identidade de sempre, o ">CC▮" verde da capa original, com
"ep. N · DD/MM" embaixo (decisão do autor em 19/11; ver docs/aprendizados.md).

Sem modelo e sem dependência: os pixels saem daqui e o PNG é escrito com zlib.
Os números do desenho foram medidos na capa original (`assets/cover.jpg`, de
02/09): letra em grade de 12 px, linhas de varredura a cada ~11,7 px, brilho
que cai à metade em ~30 px, núcleo verde quase branco.

Já existindo a capa do dia, não refaz sem `--refaz`: reexecutar o episódio não
troca uma capa que já foi ao ar. A âmbar de 19/11 (.jpg) também conta.
"""
from __future__ import annotations

import argparse
import math
import pathlib
import re
import struct
import sys
import zlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CAPAS = ROOT / "assets" / "capas"
EPISODIOS = ROOT / "episodes"

LADO = 1400          # o mínimo da Apple, e o tamanho da capa original
GROSSO = 4           # o brilho é calculado numa grade de 4 px e interpolado

# ---------------------------------------------------------------- o desenho
# ">CC▮" em grade de 12 px, como na capa original. Cada linha: intervalos
# [início, fim) de colunas acesas. 29 linhas de altura (o cursor).
_MAIOR = []
for _k in range(14):
    _a, _b = ((2, 3), (1, 4), (0, 5))[_k] if _k < 3 else (_k - 3, _k + 3)
    _MAIOR.append([(_a, _b)])
_MAIOR += list(reversed(_MAIOR))            # 28 linhas, ponta em 13 e 14

_C = ([[(3, 14)], [(1, 16)], [(1, 16)], [(0, 6), (12, 17)]]
      + [[(0, 4), (13, 17)]] * 3
      + [[(0, 4)]] * 11
      + [[(0, 4), (13, 17)]] * 3
      + [[(0, 6), (12, 17)], [(1, 16)], [(1, 16)], [(3, 14)]])   # 25 linhas

LOGO_U = 12                  # px por quadradinho
LOGO_COLS = 79               # > em 0, C em 21 e 42, cursor de 64 a 79
LOGO_LINHAS = 29


def _logo() -> list[tuple[int, int, int, int]]:
    """Retângulos (coluna, linha, largura, altura) do logo, em quadradinhos."""
    r = []
    for linha, ivs in enumerate(_MAIOR):
        for a, b in ivs:
            r.append((a, linha, b - a, 1))
    for x0 in (21, 42):
        for linha, ivs in enumerate(_C):
            for a, b in ivs:
                r.append((x0 + a, 2 + linha, b - a, 1))
    r.append((64, 0, 15, LOGO_LINHAS))
    return r


# Fonte de 5x7 para "ep. 59 · 23/11"; e e p minúsculos, p com descendente.
_FONTE = {
    "0": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": ["..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
    "e": [".....", ".....", ".###.", "#...#", "#####", "#....", ".###."],
    "p": [".....", ".....", "####.", "#...#", "#...#", "####.", "#....", "#...."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    ".": [".", ".", ".", ".", ".", ".", "#"],
    "·": [".", ".", ".", "#", ".", ".", "."],
    " ": ["..", "..", "..", "..", "..", "..", ".."],
}


def _texto(s: str) -> tuple[list[tuple[int, int, int, int]], int]:
    """Retângulos do texto em quadradinhos da fonte, e a largura total."""
    r, x = [], 0
    for i, ch in enumerate(s):
        g = _FONTE[ch]
        for linha, bits in enumerate(g):
            for col, b in enumerate(bits):
                if b == "#":
                    r.append((x + col, linha, 1, 1))
        x += len(g[0]) + (1 if i < len(s) - 1 else 0)
    return r, x


def rotulo(numero: int, data: str) -> str:
    """'ep. 59 · 23/11' para o episódio 59 de 2026-11-23."""
    a, m, d = data.split("-")
    return f"ep. {numero} · {d}/{m}"


def _arredonda(v: float) -> int:
    return int(v) // GROSSO * GROSSO


def retangulos(texto: str) -> list[tuple[int, int, int, int]]:
    """Retângulos acesos da capa, em pixels (x, y, largura, altura).

    Logo e texto centrados como um bloco; tudo em múltiplos de 4 px, para o
    brilho calculado na grade grossa cair exatamente no desenho.
    """
    t_rets, t_cols = _texto(texto)
    fonte_u = min(16, 1200 // t_cols) // GROSSO * GROSSO   # cabe até ep. 999
    logo_w, logo_h = LOGO_COLS * LOGO_U, LOGO_LINHAS * LOGO_U
    vao = 112
    bloco = logo_h + vao + 7 * fonte_u
    y_logo = _arredonda((LADO - bloco) / 2)
    x_logo = _arredonda((LADO - logo_w) / 2 + 2)
    y_txt = y_logo + logo_h + vao
    x_txt = _arredonda((LADO - t_cols * fonte_u) / 2 + 2)
    out = [(x_logo + c * LOGO_U, y_logo + l * LOGO_U, w * LOGO_U, h * LOGO_U)
           for c, l, w, h in _logo()]
    out += [(x_txt + c * fonte_u, y_txt + l * fonte_u, w * fonte_u, h * fonte_u)
            for c, l, w, h in t_rets]
    return out


# ------------------------------------------------------------------ pintura
def _borra(campo: list[list[float]], raio: int, vezes: int = 3) -> list[list[float]]:
    """Desfoque de caixa repetido (aproxima o gaussiano), linhas e colunas."""
    n = len(campo)
    larg = 2 * raio + 1

    def linha(v: list[float]) -> list[float]:
        m = len(v)
        pref = [0.0]
        for a in v:
            pref.append(pref[-1] + a)
        return [(pref[min(m, i + raio + 1)] - pref[max(0, i - raio)]) / larg
                for i in range(m)]

    for _ in range(vezes):
        campo = [linha(v) for v in campo]
    campo = [list(c) for c in zip(*campo)]
    for _ in range(vezes):
        campo = [linha(v) for v in campo]
    return [list(c) for c in zip(*campo)]


def _varredura(y: int) -> float:
    """0 a 1: a linha de varredura, medida a cada ~11,7 px na capa original."""
    return 0.5 + 0.5 * math.cos(2 * math.pi * (y - 4) / 11.7)


def pinta(rets: list[tuple[int, int, int, int]]) -> bytes:
    """RGB de LADO x LADO, linha por linha."""
    g = LADO // GROSSO
    mascara = [[0.0] * g for _ in range(g)]
    for x, y, w, h in rets:
        for gy in range(y // GROSSO, (y + h) // GROSSO):
            linha = mascara[gy]
            for gx in range(x // GROSSO, (x + w) // GROSSO):
                linha[gx] = 1.0

    # Dois brilhos, como na original: um halo curto e forte, um longo e fraco.
    perto = _borra(mascara, 5)       # ~20 px
    longe = _borra(mascara, 20)      # ~80 px
    centro = g / 2
    campo = []
    for gy in range(g):
        lin = []
        for gx in range(g):
            # névoa verde no meio da tela, que some nos cantos
            d = math.hypot(gx + .5 - centro, gy + .5 - centro) * GROSSO
            t = min(1.0, max(0.0, (d - 600) / 260))
            nevoa = 17 * (1 - t * t * (3 - 2 * t))
            lin.append(nevoa + 210 * perto[gy][gx] + 110 * longe[gy][gx])
        campo.append(lin)

    # Interpolação da grade grossa para o pixel: índices e pesos uma vez só.
    xs = []
    for x in range(LADO):
        f = (x + .5) / GROSSO - .5
        i = max(0, min(g - 1, math.floor(f)))
        j = min(g - 1, i + 1)
        xs.append((i, j, min(1.0, max(0.0, f - i))))

    # Tabela de cor por nível de varredura e de brilho.
    tabelas: dict[int, list[bytes]] = {}

    def tabela(s: float) -> list[bytes]:
        k = round(s * 31)
        if k not in tabelas:
            fator = 0.4 + 0.6 * k / 31
            tabelas[k] = [bytes((min(255, int(v * fator * .17)),
                                 min(255, int(v * fator)),
                                 min(255, int(v * fator * .30))))
                          for v in range(256)]
        return tabelas[k]

    # Intervalos acesos por linha de pixel.
    por_linha: dict[int, list[tuple[int, int]]] = {}
    for x, y, w, h in rets:
        for yy in range(y, y + h):
            por_linha.setdefault(yy, []).append((x, x + w))

    saida = bytearray()
    for y in range(LADO):
        f = (y + .5) / GROSSO - .5
        i = max(0, min(g - 1, math.floor(f)))
        j = min(g - 1, i + 1)
        t = min(1.0, max(0.0, f - i))
        a, b = campo[i], campo[j]
        col = [a[k] * (1 - t) + b[k] * t for k in range(g)]
        vals = [min(255, int(col[i0] + (col[j0] - col[i0]) * tt))
                for i0, j0, tt in xs]
        s = _varredura(y)
        linha = bytearray(b"".join(map(tabela(s).__getitem__, vals)))
        if y in por_linha:
            nucleo = bytes((int(8 + 50 * s), int(249 + 6 * s), int(50 + 40 * s)))
            for x0, x1 in por_linha[y]:
                linha[3 * x0:3 * x1] = nucleo * (x1 - x0)
        saida += linha
    return bytes(saida)


def png(largura: int, altura: int, rgb: bytes) -> bytes:
    """PNG RGB de 8 bits, sem filtro, com zlib."""
    passo = largura * 3
    cru = b"".join(b"\x00" + rgb[y * passo:(y + 1) * passo] for y in range(altura))

    def bloco(tipo: bytes, dados: bytes) -> bytes:
        return (struct.pack(">I", len(dados)) + tipo + dados
                + struct.pack(">I", zlib.crc32(tipo + dados) & 0xFFFFFFFF))

    return (b"\x89PNG\r\n\x1a\n"
            + bloco(b"IHDR", struct.pack(">IIBBBBB", largura, altura, 8, 2, 0, 0, 0))
            + bloco(b"IDAT", zlib.compress(cru, 9))
            + bloco(b"IEND", b""))


def capa(numero: int, data: str) -> bytes:
    return png(LADO, LADO, pinta(retangulos(rotulo(numero, data))))


# ------------------------------------------------------------------- CLI
def numero_do_episodio(data: str) -> int | None:
    """O número gravado no front-matter do roteiro do dia."""
    caminho = EPISODIOS / f"{data}.md"
    if not caminho.exists():
        return None
    m = re.search(r"^episode:\s*(\d+)\s*$", caminho.read_text(encoding="utf-8"), re.M)
    return int(m.group(1)) if m else None


def existente(data: str) -> pathlib.Path | None:
    for ext in (".png", ".jpg"):
        p = CAPAS / f"{data}{ext}"
        if p.exists():
            return p
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("data", help="AAAA-MM-DD")
    ap.add_argument("--numero", type=int, help="número do episódio (padrão: o do roteiro)")
    ap.add_argument("--saida", type=pathlib.Path, help="onde gravar (padrão: assets/capas/)")
    ap.add_argument("--refaz", action="store_true", help="refaz mesmo se a capa já existir")
    args = ap.parse_args()

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.data):
        print(f"capa: data inválida: {args.data}", file=sys.stderr)
        return 2
    destino = args.saida or CAPAS / f"{args.data}.png"
    ja = existente(args.data)
    if not args.saida and ja and not args.refaz:
        print(f"capa: {ja.name} já existe; nada a fazer.")
        return 0
    numero = args.numero or numero_do_episodio(args.data)
    if not numero:
        print(f"capa: sem número de episódio para {args.data} "
              f"(roteiro ausente ou sem 'episode:'); passe --numero.", file=sys.stderr)
        return 1
    dados = capa(numero, args.data)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(dados)
    print(f"capa: {rotulo(numero, args.data)} → {destino} ({len(dados) // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
