#!/usr/bin/env python3
"""
CampsCast — mede o ritmo de fala real e confere a faixa de palavras.

`words_per_minute` em config/tts.json decide quantas palavras cabem nos 5 a 10
minutos do formato. Se ele estiver otimista, o agente escreve roteiros longos
demais e o episódio estoura o teto.

Este script mede o ritmo a partir dos episódios já publicados — palavras do
front-matter contra duração real do MP3 — em vez de depender de alguém digitar
um número. Foi assim que o valor foi para 165 quando o real era 155: uma
contagem de palavras errada num script improvisado.

    python3 scripts/calibrate_pace.py            # relatório
    python3 scripts/calibrate_pace.py --apply    # grava em config/tts.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

FLOOR_MIN, TARGET_MIN, CEILING_MIN = 5.5, 8.0, 9.5
LIMITE_RIGIDO_MIN = 10.0


def medicoes(desde: str | None = None) -> list[tuple[str, int, int, float]]:
    from publish import mp3_duration_seconds, parse_front_matter

    saida = []
    for f in sorted((ROOT / "episodes").glob("*.md")):
        if desde and f.stem < desde:
            continue
        mp3 = ROOT / "audio" / f"{f.stem}.mp3"
        if not mp3.exists():
            continue
        fm = parse_front_matter(f.read_text(encoding="utf-8"))
        try:
            palavras = int(fm.get("words", 0))
        except ValueError:
            continue
        segundos = mp3_duration_seconds(mp3)
        if not palavras or not segundos:
            continue
        saida.append((f.stem, palavras, segundos, palavras / (segundos / 60)))
    return saida


def main() -> int:
    ap = argparse.ArgumentParser(description="Calibra o ritmo de fala.")
    ap.add_argument("--desde", help="ignora episódios anteriores a esta data "
                                    "(use ao trocar de voz ou de modelo)")
    ap.add_argument("--apply", action="store_true",
                    help="grava o valor medido em config/tts.json")
    args = ap.parse_args()

    from tts import load_cfg, word_budget

    dados = medicoes(args.desde)
    if len(dados) < 2:
        print("Menos de dois episódios com áudio — amostra insuficiente.",
              file=sys.stderr)
        return 1

    for data, palavras, segundos, ppm in dados:
        print(f"  {data}: {palavras:>5} palavras / {segundos:>4}s = {ppm:6.1f} ppm")

    taxas = [d[3] for d in dados]
    # Mediana, não média: um episódio atípico não deve mover a calibração.
    medido = round(statistics.median(taxas))
    print(f"\n  mediana : {medido} ppm   (n={len(taxas)}, "
          f"faixa {min(taxas):.0f}–{max(taxas):.0f})")

    cfg = load_cfg()
    atual = word_budget(cfg)
    print(f"  config  : {atual['wpm']} ppm")

    if atual["wpm"] != medido:
        erro = (atual["wpm"] / medido - 1) * 100
        print(f"  desvio  : {erro:+.0f}%")

    teto_atual_min = atual["max"] / medido
    print(f"\n  Teto de {atual['max']} palavras, ao ritmo real, dá "
          f"{teto_atual_min:.2f} min")
    if teto_atual_min > LIMITE_RIGIDO_MIN:
        print(f"  ALERTA: acima do limite rígido de {LIMITE_RIGIDO_MIN:.0f} minutos.")

    novo = {
        "min": round(FLOOR_MIN * medido),
        "target": round(TARGET_MIN * medido),
        "max": round(CEILING_MIN * medido),
    }
    print(f"\n  Faixa correta a {medido} ppm: "
          f"{novo['min']}–{novo['max']}, alvo {novo['target']}")

    if not args.apply:
        print("\n  (nada foi alterado; use --apply para gravar)")
        return 0

    caminho = ROOT / "config" / "tts.json"
    dados_cfg = json.loads(caminho.read_text(encoding="utf-8"))
    dados_cfg["words_per_minute"] = medido
    dados_cfg["_nota_ritmo"] = (
        f"Medido por scripts/calibrate_pace.py em {len(taxas)} episódios: "
        f"mediana {medido} ppm. Trocar de voz OU de modelo exige remedir — "
        "rode com --desde a partir do primeiro episódio da configuração nova."
    )
    caminho.write_text(json.dumps(dados_cfg, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    print(f"\n  config/tts.json atualizado: words_per_minute = {medido}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
