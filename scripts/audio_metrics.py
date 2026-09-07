#!/usr/bin/env python3
"""
CampsCast — métricas de áudio reutilizáveis.

Separado de check_recording.py para que a análise possa ser usada em
comparações e relatórios sem duplicar código. Tudo em biblioteca padrão:
decodificação via afconvert, FFT própria, sem numpy.
"""
from __future__ import annotations

import array
import cmath
import math
import os
import pathlib
import subprocess
import tempfile
import wave

TAXA = 22050
JANELA = 0.25
SNR_PARA_REVERB = 35.0   # abaixo disto a reverberação medida é ruído, não sala
                         # (a 30 dB o viés medido ainda é de ~0,12s: alto demais
                         #  para julgar contra um alvo de 0,4s)
JANELA_CURTA = 0.05        # para medir decaimento de reverberação

BANDAS = [
    (0, 60, "sub"),         # ronco puro: trânsito, estrutura
    (60, 120, "grave"),     # fundamental de voz masculina
    (120, 250, "médio-grave"),
    (250, 1000, "médio"),   # corpo e inteligibilidade
    (1000, 4000, "agudo"),
    (4000, 11025, "brilho"),  # sibilância
]


def para_wav(caminho: pathlib.Path, taxa: int = TAXA) -> pathlib.Path:
    saida = pathlib.Path(tempfile.mkdtemp()) / "a.wav"
    r = subprocess.run(
        ["afconvert", "-f", "WAVE", "-d", f"LEI16@{taxa}", "-c", "1",
         str(caminho), str(saida)], capture_output=True)
    if r.returncode != 0 or not saida.exists():
        raise RuntimeError(r.stderr.decode("utf-8", "replace")[:200])
    return saida


SEM_PERDAS = ("alac", "lpcm", "flac", "aiff")


def taxa_de_bits(caminho: pathlib.Path) -> tuple[int, str]:
    """Taxa de bits e se a codificação preserva o original.

    O tipo vem do nome do codec, nunca do bitrate: ALAC mono de 16 bits comprime
    o silêncio a ponto de sair abaixo de 200 kbps, e um corte por bitrate o
    rotularia "com perdas" — foi o que aconteceu com a gravação do MacBook.
    """
    kbps, tipo = 0, "?"
    try:
        r = subprocess.run(["afinfo", str(caminho)], capture_output=True, text=True)
        for linha in r.stdout.splitlines():
            baixa = linha.lower()
            if "bit rate" in baixa:
                kbps = int(int(linha.split(":")[1].strip().split()[0]) / 1000)
            elif "data format" in baixa:
                tipo = ("sem perdas" if any(c in baixa for c in SEM_PERDAS)
                        else "com perdas")
    except Exception:
        pass
    return kbps, tipo


def dbfs(rms: float) -> float:
    return 20 * math.log10(rms / 32768) if rms > 0 else -120.0


def _fft(x: list[complex]) -> list[complex]:
    n = len(x)
    if n == 1:
        return x
    par, impar = _fft(x[0::2]), _fft(x[1::2])
    saida = [0j] * n
    for k in range(n // 2):
        t = cmath.exp(-2j * math.pi * k / n) * impar[k]
        saida[k] = par[k] + t
        saida[k + n // 2] = par[k] - t
    return saida


def espectro(amostras: list[int], taxa: int, n: int = 2048) -> list[float]:
    """Fração de energia por banda. Média de até 24 quadros, para não pesar."""
    quadros = min(24, max(1, len(amostras) // n))
    energia = [0.0] * len(BANDAS)
    passo = max(n, len(amostras) // quadros)
    janela_hann = [0.5 * (1 - math.cos(2 * math.pi * i / (n - 1))) for i in range(n)]
    for q in range(quadros):
        ini = q * passo
        bloco = amostras[ini:ini + n]
        if len(bloco) < n:
            break
        X = _fft([complex(bloco[i] * janela_hann[i], 0) for i in range(n)])
        for k in range(n // 2):
            f = k * taxa / n
            p = abs(X[k]) ** 2
            for i, (lo, hi, _) in enumerate(BANDAS):
                if lo <= f < hi:
                    energia[i] += p
                    break
    total = sum(energia) or 1.0
    return [e / total for e in energia]


def niveis(amostras: list[int], taxa: int, janela: float = JANELA) -> list[float]:
    passo = int(taxa * janela)
    saida = []
    for i in range(0, len(amostras) - passo, passo):
        b = amostras[i:i + passo]
        saida.append(dbfs(math.sqrt(sum(float(x) * x for x in b) / len(b))))
    return saida


def reverberacao(amostras: list[int], taxa: int) -> float | None:
    """Estimativa grosseira do tempo de decaimento (estilo RT60), em segundos.

    Procura quedas de nível logo depois da fala parar e mede a inclinação em
    dB/s, extrapolando para 60 dB. Não substitui medição acústica com estímulo
    controlado — serve para comparar salas entre si.
    """
    ns = niveis(amostras, taxa, JANELA_CURTA)
    if len(ns) < 40:
        return None
    inclinacoes = []
    for i in range(len(ns) - 6):
        # começo alto seguido de queda contínua por 5 janelas (250 ms)
        if ns[i] < -30:
            continue
        trecho = ns[i:i + 6]
        if not all(trecho[j] > trecho[j + 1] for j in range(5)):
            continue
        queda = trecho[0] - trecho[-1]
        if queda < 6:
            continue
        inclinacoes.append(queda / (5 * JANELA_CURTA))   # dB por segundo
    if len(inclinacoes) < 3:
        return None
    inclinacoes.sort()
    mediana = inclinacoes[len(inclinacoes) // 2]
    return 60.0 / mediana if mediana > 0 else None


def analisa(caminho: pathlib.Path) -> dict:
    """Todas as métricas de um arquivo."""
    wav = para_wav(caminho)
    w = wave.open(str(wav))
    taxa, n = w.getframerate(), w.getnframes()
    dados = array.array("h")
    dados.frombytes(w.readframes(n))
    w.close()
    os.remove(wav)
    os.rmdir(wav.parent)

    amostras = list(dados)
    if len(amostras) < taxa * 3:
        raise RuntimeError("gravação curta demais (mínimo 3s)")

    ns = niveis(amostras, taxa)
    pico = max(abs(x) for x in amostras)
    clipes = sum(1 for x in amostras if abs(x) >= 32700)
    rms_total = math.sqrt(sum(float(x) * x for x in amostras) / len(amostras))

    ordenados = sorted(ns)
    corte = max(1, len(ns) // 10)
    fala = sum(ordenados[-corte * 3:]) / (corte * 3)

    # O piso sai do trecho contínuo de 2s MAIS SILENCIOSO do arquivo, e não de
    # todas as janelas abaixo de um limiar. Limiar — fixo ou relativo — falha
    # quando quase todo o arquivo é fala: o corte cai dentro das pausas entre
    # palavras e passa a medir a voz. Numa gravação 87% falada isso deu -41,8
    # dBFS de "ruído" onde a sala estava a -54.
    # Usa-se o máximo dentro da janela, não a média: exige silêncio o tempo
    # todo, senão uma pausa longa com um estalo no meio passaria.
    MIN = int(2.0 / JANELA)
    idx_sil = []
    if len(ns) >= MIN:
        mais_silencioso = min(max(ns[i:i + MIN]) for i in range(len(ns) - MIN + 1))
        LIMIAR = mais_silencioso + 3.0
        idx_sil = [i for i, v in enumerate(ns) if v <= LIMIAR]

    if idx_sil:
        piso = sum(ns[i] for i in idx_sil) / len(idx_sil)
        # Silêncio de verdade fica bem abaixo da fala. Se não ficar, o que se
        # achou foi fala baixa, e o piso é um limite superior.
        confiavel = (fala - piso) >= 12.0
        passo = int(taxa * JANELA)
        amostras_sil = []
        for i in idx_sil:
            amostras_sil.extend(amostras[i * passo:(i + 1) * passo])
    else:
        piso = ordenados[max(0, len(ordenados) // 100)]
        confiavel = False
        amostras_sil = []

    kbps, tipo = taxa_de_bits(caminho)
    media = sum(ns) / len(ns)
    desvio = math.sqrt(sum((v - media) ** 2 for v in ns) / len(ns))

    # faixa dinâmica da fala: entre os trechos falados mais altos e mais baixos
    falados = sorted(v for v in ns if v > piso + 10)
    dinamica = (falados[-max(1, len(falados)//20)] - falados[max(0, len(falados)//10)]
                ) if len(falados) > 20 else 0.0

    return {
        "arquivo": caminho.name,
        "duracao": len(amostras) / taxa,
        "taxa_bits": kbps,
        "tipo_codec": tipo,
        "piso": piso,
        "piso_confiavel": confiavel,
        "fala": fala,
        "snr": fala - piso,
        "pico": dbfs(pico),
        "clipes": clipes,
        "crista": dbfs(pico) - dbfs(rms_total),
        "dinamica": dinamica,
        "desvio_tempo": desvio,
        "silencio_s": len(idx_sil) * JANELA,
        "niveis": ns,
        "espectro_fala": espectro(amostras, taxa),
        "espectro_ruido": espectro(amostras_sil, taxa) if amostras_sil else None,
        "reverb": reverberacao(amostras, taxa),
        # A estimativa de reverberação só vale com sinal bem acima do ruído:
        # o decaimento afunda no piso e o rabo achatado lê como eco longo.
        # Medido somando ruído branco à mesma gravação, sala inalterada:
        # S/R 39 dB -> 0,48s;  29 dB -> 0,61s;  20 dB -> 0,73s;  14 dB -> 0,95s.
        "reverb_confiavel": (fala - piso) >= SNR_PARA_REVERB,
        "taxa": taxa,
    }
