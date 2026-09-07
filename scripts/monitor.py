#!/usr/bin/env python3
"""
CampsCast — monitor de gravação ao vivo.

Mostra no terminal do Mac o nível do ambiente enquanto você grava no celular:
cronômetro da tomada, firmeza da voz e aviso quando algo de fora sobe — avião,
TV, alguém entrando. Feito para gravar em tomadas curtas entre um pouso e outro.

    python3 scripts/monitor.py

Enter encerra a tomada atual e começa outra. Ctrl-C sai e mostra o resumo.

AVISO IMPORTANTE: os dBFS daqui são do microfone do Mac, e não são os mesmos
que o celular vai gravar. Ganho diferente desloca a escala inteira — é o mesmo
motivo pelo qual não se compara piso de ruído entre aparelhos. Use este medidor
para variação (o fundo subiu? a voz caiu?), nunca para alvo absoluto. Quem julga
o arquivo é o check_recording.py, depois.
"""
from __future__ import annotations

import collections
import math
import os
import pathlib
import select
import subprocess
import sys
import time

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FONTE = RAIZ / "scripts" / "monitor.swift"
BINARIO = RAIZ / ".cache" / "monitor"

JANELA_S = 20.0          # memória para estimar fundo e voz
SUBIDA_ALERTA = 6.0      # dB de subida do fundo que dispara o aviso
ACIMA_DO_FUNDO = 8.0     # dB acima do fundo para um bloco contar como voz
META_MIN = 30.0          # minutos de material que a clonagem profissional pede
SPARK = "▁▂▃▄▅▆▇█"


def compila() -> pathlib.Path:
    if BINARIO.exists() and BINARIO.stat().st_mtime > FONTE.stat().st_mtime:
        return BINARIO
    if not (swiftc := _acha("swiftc")):
        sys.exit("swiftc não encontrado. Instale as ferramentas de linha de "
                 "comando do Xcode: xcode-select --install")
    BINARIO.parent.mkdir(exist_ok=True)
    print("compilando o capturador (uma vez só)...", file=sys.stderr)
    r = subprocess.run([swiftc, "-O", "-o", str(BINARIO), str(FONTE)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"falha ao compilar:\n{r.stderr[:400]}")
    return BINARIO


def _acha(nome: str) -> str | None:
    for d in os.environ.get("PATH", "").split(":"):
        p = pathlib.Path(d) / nome
        if p.exists():
            return str(p)
    return None


def percentil(vs: list[float], p: float) -> float:
    if not vs:
        return -120.0
    o = sorted(vs)
    return o[min(len(o) - 1, max(0, int(len(o) * p)))]


def barra(v: float, lo: float = -70.0, hi: float = -5.0, largura: int = 34) -> str:
    f = max(0.0, min(1.0, (v - lo) / (hi - lo)))
    n = int(f * largura)
    return "█" * n + "░" * (largura - n)


def relogio(s: float) -> str:
    return f"{int(s) // 60:02d}:{int(s) % 60:02d}"


def main() -> int:
    binario = compila()
    proc = subprocess.Popen([str(binario)], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, bufsize=1)

    memoria: collections.deque[float] = collections.deque(maxlen=int(JANELA_S / 0.05))
    traco: collections.deque[float] = collections.deque(maxlen=46)
    piso_ref = None
    inicio_tomada = time.time()
    tomadas: list[tuple[float, float, float]] = []   # duração, voz, S/R
    ultimo_desenho = 0.0
    ouve_teclado = sys.stdin.isatty()
    linhas_desenhadas = 0
    alertando = False

    print("\n  Enter encerra a tomada e começa outra. Ctrl-C sai.\n")
    try:
        while True:
            fontes = [proc.stdout] + ([sys.stdin] if ouve_teclado else [])
            prontos, _, _ = select.select(fontes, [], [], 0.2)

            if sys.stdin in prontos:
                if not sys.stdin.readline():   # EOF: pára de ouvir o teclado
                    ouve_teclado = False
                    continue
                dur = time.time() - inicio_tomada
                vs = list(memoria)
                if not vs or dur < 1.0:       # tomada vazia não vira registro
                    inicio_tomada = time.time()
                    continue
                piso = percentil(vs, 0.20)
                voz = [v for v in vs if v > piso + ACIMA_DO_FUNDO]
                mediana = percentil(voz, 0.5) if voz else piso
                tomadas.append((dur, mediana, mediana - piso))
                inicio_tomada = time.time()
                sys.stdout.write("\033[2K")
                print(f"\n  ── tomada {len(tomadas)} encerrada: {relogio(dur)}, "
                      f"voz {mediana:.1f} dBFS, S/R {mediana - piso:.0f} dB\n")
                linhas_desenhadas = 0
                continue

            if proc.stdout in prontos:
                linha = proc.stdout.readline()
                if not linha:
                    break
                try:
                    db = float(linha.split()[0])
                except (ValueError, IndexError):
                    continue
                memoria.append(db)
                traco.append(db)

            agora = time.time()
            if agora - ultimo_desenho < 0.15 or len(memoria) < 20:
                continue
            ultimo_desenho = agora

            vs = list(memoria)
            piso = percentil(vs, 0.20)
            voz = [v for v in vs if v > piso + ACIMA_DO_FUNDO]
            tem_voz = len(voz) > len(vs) * 0.15
            mediana = percentil(voz, 0.5) if tem_voz else None
            if tem_voz and len(voz) > 5:
                m = sum(voz) / len(voz)
                firmeza = math.sqrt(sum((v - m) ** 2 for v in voz) / len(voz))
            else:
                firmeza = None

            if piso_ref is None or piso < piso_ref:
                piso_ref = piso
            subida = piso - piso_ref if piso_ref is not None else 0.0
            alertando = subida >= SUBIDA_ALERTA

            lo, hi = min(traco), max(traco)
            spark = "".join(
                SPARK[min(7, int((v - lo) / (hi - lo + 1e-9) * 8))] for v in traco)

            saida = []
            saida.append(f"  ⏱  {relogio(agora - inicio_tomada)}   tomada "
                         f"{len(tomadas) + 1}      {barra(vs[-1])}  {vs[-1]:6.1f} dBFS")
            saida.append("")
            if mediana is not None:
                q = ("firme" if firmeza is not None and firmeza < 3.0 else
                     "oscilando" if firmeza is not None else "")
                f_txt = f"±{firmeza:.1f} dB  {q}" if firmeza is not None else ""
                saida.append(f"  voz     {mediana:6.1f} dBFS   {f_txt}")
                saida.append(f"  fundo   {piso:6.1f} dBFS   melhor {piso_ref:.1f}   "
                             f"S/R {mediana - piso:.0f} dB")
            else:
                saida.append(f"  voz        —          (silêncio)")
                saida.append(f"  fundo   {piso:6.1f} dBFS   melhor {piso_ref:.1f}")
            saida.append("")
            saida.append(f"  {spark}")
            saida.append("")
            if alertando:
                saida.append(f"  \033[1;31m⚠  FUNDO SUBIU {subida:.0f} dB — "
                             f"pare a gravação\033[0m")
            else:
                saida.append(f"  \033[32m✓\033[0m  ambiente estável"
                             f"{'' if mediana is None else ' — pode falar'}")
            bruto = sum(d for d, _, _ in tomadas)
            saida.append(f"     {len(tomadas)} tomadas, {relogio(bruto)} gravados "
                         f"de {META_MIN:.0f}:00 que a clonagem pede")

            if linhas_desenhadas:
                sys.stdout.write(f"\033[{linhas_desenhadas}A")
            for l in saida:
                sys.stdout.write("\033[2K" + l + "\n")
            linhas_desenhadas = len(saida)
            sys.stdout.flush()

    except KeyboardInterrupt:
        pass
    finally:
        proc.terminate()

    print("\n\n  Resumo das tomadas\n")
    if not tomadas:
        print("  nenhuma tomada encerrada com Enter\n")
        return 0
    for i, (d, v, s) in enumerate(tomadas, 1):
        print(f"   {i:2d}.  {relogio(d)}   voz {v:6.1f} dBFS   S/R {s:.0f} dB")
    total = sum(d for d, _, _ in tomadas)
    print(f"\n  total {relogio(total)} de {META_MIN:.0f}:00\n")
    print("  Lembre: estes números são do microfone do Mac, não do celular.")
    print("  Avalie os arquivos de verdade com:\n")
    print("      python3 scripts/prep_voice_samples.py <pasta ou arquivos>\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
