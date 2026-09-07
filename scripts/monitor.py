#!/usr/bin/env python3
"""
CampsCast — monitor de gravação ao vivo.

Acompanha o ambiente no terminal enquanto você grava em outro aparelho:
cronômetro da tomada, firmeza da voz e aviso quando algo de fora sobe.

    python3 scripts/monitor.py

Enter encerra a tomada e começa outra. "c" e Enter recalibra. Ctrl-C sai.

COMO ELE SEPARA VOZ DE RUÍDO. Por nível é impossível — qualquer coisa mais alta
que o fundo pareceria fala. Por banda funciona, e os limiares saíram de medição
nas gravações deste projeto:

    voz de perto      razão 300-3400 Hz sobre <200 Hz    -6,4 dB
    avião passando                                      -23,5 dB
    moto na rua                                         -38,3 dB

Avião e trânsito quase não tocam a banda de voz: -80 dBFS contra -81 do quarto
em silêncio. Então a voz é detectada por subida na banda de 300-3400 Hz sobre a
calibração, e o alarme de ruído externo por subida abaixo de 200 Hz.

CALIBRAÇÃO. Os primeiros oito segundos precisam ser de silêncio: é deles que
saem as duas referências. Sem calibrar não há como saber o que é "normal" nesta
sala, nesta hora, neste microfone.

DE QUAL MICROFONE SÃO OS NÚMEROS. Do dispositivo de entrada padrão do sistema,
cujo nome aparece no cabeçalho. Se você grava em outro aparelho, os dBFS daqui
não são os de lá: ganho diferente desloca a escala inteira. Vale para variação,
não como alvo absoluto — quem julga o arquivo é o check_recording.py.

Vários programas podem ler o mesmo microfone ao mesmo tempo no macOS, então dá
para gravar num aplicativo e monitorar aqui.
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

CALIBRACAO_S = 8.0
JANELA_S = 15.0
VOZ_ACIMA = 12.0       # dB na banda de voz que indicam alguém falando
RUIDO_ACIMA = 10.0     # dB nos graves que indicam fonte externa entrando
META_MIN = 30.0
SPARK = "▁▂▃▄▅▆▇█"


def compila() -> pathlib.Path:
    if BINARIO.exists() and BINARIO.stat().st_mtime > FONTE.stat().st_mtime:
        return BINARIO
    swiftc = next((str(p) for d in os.environ.get("PATH", "").split(":")
                   if (p := pathlib.Path(d) / "swiftc").exists()), None)
    if not swiftc:
        sys.exit("swiftc não encontrado. Instale as ferramentas de linha de "
                 "comando do Xcode: xcode-select --install")
    BINARIO.parent.mkdir(exist_ok=True)
    print("compilando o capturador (uma vez só)...", file=sys.stderr)
    r = subprocess.run([swiftc, "-O", "-o", str(BINARIO), str(FONTE)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"falha ao compilar:\n{r.stderr[:400]}")
    return BINARIO


def percentil(vs, p: float) -> float:
    if not vs:
        return -120.0
    o = sorted(vs)
    return o[min(len(o) - 1, max(0, int(len(o) * p)))]


def barra(v: float, lo: float = -70.0, hi: float = -5.0, largura: int = 30) -> str:
    n = int(max(0.0, min(1.0, (v - lo) / (hi - lo))) * largura)
    return "█" * n + "░" * (largura - n)


def classifica(graves: list[float], vozes: list[float],
               base_grave: float, base_voz: float) -> tuple[bool, bool, float]:
    """Decide, a partir das duas bandas, se há voz e se entrou ruído externo.

    Separado do desenho para poder ser testado sem microfone. Limiares medidos
    nas gravações do projeto: avião e moto sobem os graves 14 a 29 dB sobre o
    quarto calmo e deixam a banda de voz praticamente intacta, 1 dB.
    """
    subida = percentil(graves, 0.5) - base_grave
    falando = [v for v in vozes if v > base_voz + VOZ_ACIMA]
    tem_voz = len(falando) > len(vozes) * 0.20 if vozes else False
    return tem_voz, subida >= RUIDO_ACIMA, subida


def relogio(s: float) -> str:
    return f"{int(s) // 60:02d}:{int(s) % 60:02d}"


def main() -> int:
    proc = subprocess.Popen([str(compila())], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, bufsize=1)
    cabecalho = proc.stdout.readline().strip().lstrip("# ")

    print(f"\n  CampsCast — monitor de gravação")
    print(f"  lendo de: {cabecalho}\n")
    print("  Fique em silêncio pelos primeiros 8 segundos: é a calibração.")
    print("  Enter encerra a tomada.  'c' e Enter recalibra.  Ctrl-C sai.\n")

    mem = collections.deque(maxlen=int(JANELA_S / 0.05))
    traco = collections.deque(maxlen=44)
    base_grave = base_voz = None
    cal: list[tuple[float, float]] = []
    inicio_cal = time.time()
    inicio_tomada = None
    tomadas: list[tuple[float, float, float]] = []
    desenhadas = 0
    ultimo = 0.0
    teclado = sys.stdin.isatty()

    def calibra_de_novo():
        nonlocal base_grave, base_voz, cal, inicio_cal
        base_grave = base_voz = None
        cal = []
        inicio_cal = time.time()

    try:
        while True:
            fontes = [proc.stdout] + ([sys.stdin] if teclado else [])
            prontos, _, _ = select.select(fontes, [], [], 0.2)

            if sys.stdin in prontos:
                linha = sys.stdin.readline()
                if not linha:
                    teclado = False
                elif linha.strip().lower() == "c":
                    sys.stdout.write("\033[2K")
                    print("\n  recalibrando — silêncio por 8 segundos\n")
                    desenhadas = 0
                    calibra_de_novo()
                elif inicio_tomada is not None:
                    dur = time.time() - inicio_tomada
                    if dur >= 1.0 and mem:
                        vs = [v for v, _, _ in mem]
                        vz = [v for _, _, v in mem]
                        falando = [a for a, b in zip(vs, vz) if b > base_voz + VOZ_ACIMA]
                        nivel = percentil(falando, 0.5) if falando else percentil(vs, 0.5)
                        tomadas.append((dur, nivel, nivel - percentil(vs, 0.15)))
                        sys.stdout.write("\033[2K")
                        print(f"\n  ── tomada {len(tomadas)}: {relogio(dur)}, "
                              f"voz {nivel:.1f} dBFS\n")
                        desenhadas = 0
                    inicio_tomada = time.time()
                continue

            if proc.stdout in prontos:
                dado = proc.stdout.readline()
                if not dado:
                    break
                try:
                    total, _pico, grave, voz = (float(x) for x in dado.split())
                except ValueError:
                    continue
                if base_voz is None:
                    cal.append((grave, voz))
                    if time.time() - inicio_cal >= CALIBRACAO_S and len(cal) > 40:
                        base_grave = percentil([g for g, _ in cal], 0.5)
                        base_voz = percentil([v for _, v in cal], 0.5)
                        inicio_tomada = time.time()
                        sys.stdout.write("\033[2K")
                        print(f"  calibrado: graves {base_grave:.1f} dBFS, "
                              f"voz {base_voz:.1f} dBFS — pode começar\n")
                        desenhadas = 0
                    else:
                        falta = CALIBRACAO_S - (time.time() - inicio_cal)
                        sys.stdout.write(f"\r\033[2K  calibrando... {max(0, falta):.0f}s ")
                        sys.stdout.flush()
                    continue
                mem.append((total, grave, voz))
                traco.append(total)

            agora = time.time()
            if base_voz is None or agora - ultimo < 0.15 or len(mem) < 20:
                continue
            ultimo = agora

            totais = [t for t, _, _ in mem]
            graves = [g for _, g, _ in mem]
            vozes = [v for _, _, v in mem]

            tem_voz, alerta, subida = classifica(graves, vozes, base_grave, base_voz)
            falando = [t for t, v in zip(totais, vozes) if v > base_voz + VOZ_ACIMA]
            if tem_voz and len(falando) > 5:
                med = sum(falando) / len(falando)
                firmeza = math.sqrt(sum((x - med) ** 2 for x in falando) / len(falando))
                nivel = percentil(falando, 0.5)
            else:
                firmeza = nivel = None

            lo, hi = min(traco), max(traco)
            spark = "".join(SPARK[min(7, int((v - lo) / (hi - lo + 1e-9) * 8))]
                            for v in traco)

            out = [
                f"  ⏱  {relogio(agora - inicio_tomada)}   tomada {len(tomadas) + 1}"
                f"      {barra(totais[-1])} {totais[-1]:6.1f} dBFS",
                "",
            ]
            if nivel is not None:
                q = "firme" if firmeza < 3.0 else "oscilando"
                out.append(f"  voz     {nivel:6.1f} dBFS   ±{firmeza:.1f} dB {q}")
            else:
                out.append(f"  voz        —          (ninguém falando)")
            out.append(f"  graves  {subida:+6.1f} dB sobre a calibração"
                       f"   (base {base_grave:.1f})")
            out.append("")
            out.append(f"  {spark}")
            out.append("")
            out.append(f"  \033[1;31m⚠  RUÍDO EXTERNO ENTRANDO — pare\033[0m"
                       if alerta else "  \033[32m✓\033[0m  ambiente estável")
            out.append(f"     {len(tomadas)} tomadas, "
                       f"{relogio(sum(d for d, _, _ in tomadas))} de "
                       f"{relogio(META_MIN * 60)}")

            if desenhadas:
                sys.stdout.write(f"\033[{desenhadas}A")
            for l in out:
                sys.stdout.write("\033[2K" + l + "\n")
            desenhadas = len(out)
            sys.stdout.flush()

    except KeyboardInterrupt:
        pass
    finally:
        proc.terminate()

    print("\n\n  Resumo\n")
    for i, (d, v, _s) in enumerate(tomadas, 1):
        print(f"   {i:2d}.  {relogio(d)}   voz {v:6.1f} dBFS")
    if tomadas:
        print(f"\n  total {relogio(sum(d for d, _, _ in tomadas))}")
    print(f"\n  Números do microfone \"{cabecalho}\", não do aparelho onde você")
    print("  gravou. Avalie os arquivos de verdade com:\n")
    print("      python3 scripts/prep_voice_samples.py <arquivos>\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
