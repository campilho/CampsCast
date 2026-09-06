#!/usr/bin/env python3
"""
CampsCast — avalia se uma gravação serve para clonagem de voz.

Clonagem aprende tudo que está no áudio, inclusive o que você não queria: ruído
de rua, chiado do ar-condicionado, eco do cômodo. Depois não há como separar.
Meia hora gravada num lugar ruim vira um clone ruim, e o erro só aparece no
episódio.

Este script mede antes de gastar a gravação inteira. Aceita qualquer formato
que o afconvert leia — m4a do iPhone, wav, mp3.

    python3 scripts/check_recording.py amostra.m4a
    python3 scripts/check_recording.py iphone.m4a mac.m4a     # compara
"""
from __future__ import annotations

import argparse
import array
import math
import os
import pathlib
import subprocess
import sys
import tempfile
import wave

TAXA = 22050          # suficiente para medir voz e ruído, e leve na memória
JANELA = 0.25         # segundos por janela de análise

# Limiares para material de clonagem, do exigente ao aceitável.
PISO_RUIDO_BOM, PISO_RUIDO_OK = -60.0, -50.0
SNR_BOM, SNR_OK = 40.0, 30.0
FALA_MIN, FALA_MAX = -26.0, -14.0
GRAVE_ALERTA = 0.35   # fração da energia abaixo de ~150 Hz


def para_wav(caminho: pathlib.Path) -> pathlib.Path:
    saida = pathlib.Path(tempfile.mkdtemp()) / "a.wav"
    r = subprocess.run(
        ["afconvert", "-f", "WAVE", "-d", f"LEI16@{TAXA}", "-c", "1",
         str(caminho), str(saida)],
        capture_output=True)
    if r.returncode != 0 or not saida.exists():
        raise RuntimeError(f"não consegui converter {caminho.name}: "
                           f"{r.stderr.decode('utf-8', 'replace')[:200]}")
    return saida


def dbfs(rms: float) -> float:
    return 20 * math.log10(rms / 32768) if rms > 0 else -120.0


def analisa(caminho: pathlib.Path) -> dict:
    wav = para_wav(caminho)
    w = wave.open(str(wav))
    total = w.getnframes()
    passo = int(TAXA * JANELA)

    niveis, graves, picos, clipes = [], [], 0, 0
    # Filtro passa-baixa de um polo, ~150 Hz. Grosseiro de propósito: serve para
    # detectar ronco de trânsito e motor, não para análise fina.
    alfa = math.exp(-2 * math.pi * 150 / TAXA)

    for _ in range(total // passo):
        b = array.array("h")
        b.frombytes(w.readframes(passo))
        if not b:
            break
        soma = soma_grave = 0.0
        y = 0.0
        for x in b:
            soma += float(x) * x
            y = alfa * y + (1 - alfa) * x
            soma_grave += y * y
            if abs(x) >= 32700:
                clipes += 1
            if abs(x) > picos:
                picos = abs(x)
        n = len(b)
        niveis.append(dbfs(math.sqrt(soma / n)))
        graves.append(soma_grave / soma if soma > 0 else 0.0)
    w.close()
    os.remove(wav)
    os.rmdir(wav.parent)

    if len(niveis) < 8:
        raise RuntimeError("gravação curta demais para medir (mínimo ~5s)")

    ordenados = sorted(niveis)
    corte = max(1, len(ordenados) // 10)
    piso = sum(ordenados[:corte]) / corte            # 10% mais silenciosos
    fala = sum(ordenados[-corte * 3:]) / (corte * 3)  # 30% mais altos
    return {
        "arquivo": caminho.name,
        "duracao": len(niveis) * JANELA,
        "piso": piso,
        "fala": fala,
        "snr": fala - piso,
        "pico": dbfs(picos),
        "clipes": clipes,
        "grave": sum(graves) / len(graves),
    }


def veredito(m: dict) -> list[tuple[str, str]]:
    saida = []

    if m["piso"] <= PISO_RUIDO_BOM:
        saida.append(("ok", f"silêncio limpo ({m['piso']:.1f} dBFS)"))
    elif m["piso"] <= PISO_RUIDO_OK:
        saida.append(("~", f"ruído de fundo audível ({m['piso']:.1f} dBFS) — "
                           "aceitável, mas melhoraria em hora mais silenciosa"))
    else:
        saida.append(("X", f"ruído de fundo alto ({m['piso']:.1f} dBFS) — o clone "
                           "vai aprender isso junto com a sua voz"))

    if m["snr"] >= SNR_BOM:
        saida.append(("ok", f"voz bem acima do ruído ({m['snr']:.0f} dB)"))
    elif m["snr"] >= SNR_OK:
        saida.append(("~", f"margem apertada entre voz e ruído ({m['snr']:.0f} dB) — "
                           "fale mais perto do microfone"))
    else:
        saida.append(("X", f"voz perto demais do ruído ({m['snr']:.0f} dB) — "
                           "não use para clonagem"))

    if m["clipes"] > 0:
        saida.append(("X", f"{m['clipes']} amostras estouradas — afaste-se do "
                           "microfone ou baixe o ganho; distorção não se conserta"))
    elif m["pico"] > -1.0:
        saida.append(("~", f"picos muito perto do teto ({m['pico']:.1f} dBFS)"))
    else:
        saida.append(("ok", f"sem distorção (pico {m['pico']:.1f} dBFS)"))

    if FALA_MIN <= m["fala"] <= FALA_MAX:
        saida.append(("ok", f"volume da fala adequado ({m['fala']:.1f} dBFS)"))
    elif m["fala"] < FALA_MIN:
        saida.append(("~", f"fala baixa ({m['fala']:.1f} dBFS) — aproxime-se"))
    else:
        saida.append(("~", f"fala alta ({m['fala']:.1f} dBFS) — afaste-se um pouco"))

    if m["grave"] > GRAVE_ALERTA:
        saida.append(("~", f"muita energia grave ({m['grave']:.0%}) — costuma ser "
                           "trânsito, ar-condicionado ou vento no microfone"))
    else:
        saida.append(("ok", f"pouco ronco de baixa frequência ({m['grave']:.0%})"))

    return saida


def main() -> int:
    ap = argparse.ArgumentParser(description="Avalia gravação para clonagem.")
    ap.add_argument("arquivos", nargs="+")
    args = ap.parse_args()

    medidas = []
    for nome in args.arquivos:
        caminho = pathlib.Path(nome)
        if not caminho.exists():
            print(f"ERRO: não encontrei {caminho}", file=sys.stderr)
            return 1
        try:
            m = analisa(caminho)
        except Exception as e:
            print(f"ERRO em {caminho.name}: {e}", file=sys.stderr)
            return 1
        medidas.append(m)

        print(f"\n═══ {m['arquivo']}  ({m['duracao']:.0f}s) ═══")
        print(f"  piso de ruído : {m['piso']:7.1f} dBFS")
        print(f"  nível da fala : {m['fala']:7.1f} dBFS")
        print(f"  relação S/R   : {m['snr']:7.1f} dB")
        print(f"  pico          : {m['pico']:7.1f} dBFS")
        print()
        marcas = {"ok": "  ok  ", "~": "  ~   ", "X": "  X   "}
        for nivel, texto in veredito(m):
            print(f"{marcas[nivel]}{texto}")
        ruins = [n for n, _ in veredito(m)]
        print()
        if "X" in ruins:
            print("  VEREDITO: não use este material para clonagem.")
        elif "~" in ruins:
            print("  VEREDITO: serve, mas dá para melhorar. Veja os pontos acima.")
        else:
            print("  VEREDITO: material bom. Pode gravar os 30 minutos assim.")

    if len(medidas) > 1:
        print(f"\n═══ comparação ═══")
        print(f"  {'arquivo':<24}{'piso':>9}{'S/R':>8}{'fala':>9}")
        for m in medidas:
            print(f"  {m['arquivo'][:22]:<24}{m['piso']:>8.1f}{m['snr']:>8.0f}"
                  f"{m['fala']:>9.1f}")
        melhor = max(medidas, key=lambda x: x["snr"])
        print(f"\n  Melhor relação sinal/ruído: {melhor['arquivo']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
