#!/usr/bin/env python3
"""
CampsCast — prepara gravações para upload na ElevenLabs.

O app Gravador do iPhone, na qualidade "Sem perdas", grava em **ALAC** dentro de
um `.m4a`. A ElevenLabs não decodifica esse codec: ela lê duração zero e recusa
com "At least 30s of audio is required", mesmo num arquivo de um minuto. A
mensagem não menciona formato, então o erro parece ser outra coisa.

Este script converte para WAV mono 44,1 kHz — sem perdas e universalmente
aceito — e roda a checagem de qualidade em cada arquivo antes de você subir.

    python3 scripts/prep_voice_samples.py bloco1.m4a bloco2.m4a
    python3 scripts/prep_voice_samples.py *.m4a --saida amostras/
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

TAXA = 44100          # padrão de áudio; 48k também serve e ocupa 9% mais
MB_POR_MINUTO = 5.05  # mono 16 bits a 44,1 kHz


def converte(origem: pathlib.Path, destino: pathlib.Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["afconvert", "-f", "WAVE", "-d", f"LEI16@{TAXA}", "-c", "1",
         str(origem), str(destino)],
        capture_output=True)
    if r.returncode != 0 or not destino.exists():
        raise RuntimeError(r.stderr.decode("utf-8", "replace")[:200])


def main() -> int:
    ap = argparse.ArgumentParser(description="Prepara amostras de voz.")
    ap.add_argument("arquivos", nargs="+")
    ap.add_argument("--saida", default="amostras-voz",
                    help="diretório de destino (default: amostras-voz/)")
    args = ap.parse_args()

    from check_recording import analisa, veredito

    saida = pathlib.Path(args.saida)
    total_mb, total_min, reprovados = 0.0, 0.0, []

    for nome in args.arquivos:
        origem = pathlib.Path(nome)
        if not origem.exists():
            print(f"ERRO: não encontrei {origem}", file=sys.stderr)
            return 1

        destino = saida / (origem.stem + ".wav")
        print(f"\n═══ {origem.name}")
        try:
            converte(origem, destino)
        except Exception as e:
            print(f"  ERRO na conversão: {e}", file=sys.stderr)
            return 1

        mb = destino.stat().st_size / 1048576
        m = analisa(destino)
        total_mb += mb
        total_min += m["duracao"] / 60

        print(f"  -> {destino}  ({mb:.1f} MB, {m['duracao'] / 60:.1f} min)")
        marcas = {"ok": "  ok  ", "~": "  ~   ", "X": "  X   "}
        problemas = veredito(m)
        for nivel, texto in problemas:
            if nivel != "ok":
                print(f"{marcas[nivel]}{texto}")
        niveis = [n for n, _ in problemas]
        if "X" in niveis:
            reprovados.append(origem.name)
            print("  REPROVADO — regrave este bloco.")
        elif "~" not in niveis:
            print("  ok — sem ressalvas")

    print(f"\n═══ resumo ═══")
    print(f"  {total_min:.0f} minutos, {total_mb:.0f} MB em {saida}/")
    if total_min < 30:
        print(f"  Faltam {30 - total_min:.0f} minutos para o mínimo do "
              "Professional Voice Cloning.")
    else:
        print("  Acima dos 30 minutos mínimos.")
    if reprovados:
        print(f"\n  NÃO SUBA antes de regravar: {', '.join(reprovados)}")
        print("  Material ruim contamina o modelo inteiro, e não há como "
              "remover depois.")
        return 1
    print("\n  Suba os .wav como amostras separadas — a ElevenLabs aceita vários.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
