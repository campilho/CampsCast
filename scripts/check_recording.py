#!/usr/bin/env python3
"""
CampsCast — avalia gravações para clonagem de voz, e compara cenários.

Clonagem aprende tudo que está no áudio: ruído de rua, chiado de aparelho, eco
do cômodo. Depois não há como separar. Este script mede antes de você gastar a
gravação inteira — e produz tabelas comparáveis entre salas, aparelhos e
distâncias, para documentar o que funciona.

    python3 scripts/check_recording.py bloco.m4a
    python3 scripts/check_recording.py silencio.m4a --sala
    python3 scripts/check_recording.py *.m4a --markdown      # tabela p/ docs
"""
from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from audio_metrics import BANDAS, analisa   # noqa: E402

PISO_BOM, PISO_OK = -60.0, -50.0
SNR_BOM, SNR_OK = 40.0, 30.0
FALA_MIN, FALA_MAX = -26.0, -14.0
REVERB_BOM, REVERB_OK = 0.4, 0.6

BLOCOS = " ░▒▓█"


def barra(fracao: float, largura: int = 28) -> str:
    cheios = int(fracao * largura)
    return "█" * cheios + "·" * (largura - cheios)


def perfil_tempo(ns: list[float], duracao: float, linhas: int = 16) -> list[str]:
    """Gráfico do nível ao longo do tempo, em blocos de densidade."""
    if not ns:
        return []
    lo, hi = min(ns), max(ns)
    faixa = max(hi - lo, 6.0)
    por_linha = max(1, len(ns) // linhas)
    saida = []
    for i in range(0, len(ns), por_linha):
        grupo = ns[i:i + por_linha]
        marcas = "".join(
            BLOCOS[min(len(BLOCOS) - 1, int((v - lo) / faixa * (len(BLOCOS) - 1)))]
            for v in grupo[:12])
        t = i * duracao / len(ns)
        saida.append(f"    {int(t)//60:d}:{int(t)%60:02d}  {marcas:<12}  "
                     f"{min(grupo):6.1f} a {max(grupo):6.1f} dBFS")
    return saida


def espectro_texto(fracoes: list[float], titulo: str) -> list[str]:
    linhas = [f"  {titulo}"]
    for (lo, hi, nome), f in zip(BANDAS, fracoes):
        faixa = f"{lo}–{hi} Hz" if hi < 11025 else f"{lo//1000}k+ Hz"
        linhas.append(f"    {nome:<12} {faixa:>12}  {f * 100:5.1f}%  {barra(f)}")
    return linhas


def relatorio_sala(m: dict) -> None:
    ns = m["niveis"]
    print(f"\n═══ {m['arquivo']} — ambiente ({m['duracao']:.0f}s) ═══\n")
    print(f"  ruído médio      : {sum(ns)/len(ns):7.1f} dBFS")
    print(f"  mais quieto      : {min(ns):7.1f} dBFS")
    print(f"  mais alto        : {max(ns):7.1f} dBFS")
    print(f"  variação         : {max(ns)-min(ns):7.1f} dB")
    print(f"  desvio no tempo  : {m['desvio_tempo']:7.1f} dB")
    if m["reverb"]:
        print(f"  reverberação     : {m['reverb']:7.2f} s  (estimativa)")

    print(f"\n  Perfil no tempo:")
    for linha in perfil_tempo(ns, m["duracao"]):
        print(linha)

    print()
    for linha in espectro_texto(m["espectro_fala"], "Espectro do ruído:"):
        print(linha)

    print()
    media = sum(ns) / len(ns)
    if media <= PISO_BOM:
        print("  ok    sala silenciosa — pode gravar")
    elif media <= PISO_OK:
        print("  ~     sala aceitável, mas já se ouve o ambiente")
    else:
        print("  X     sala barulhenta demais — procure outra hora ou cômodo")

    graves = m["espectro_fala"][0] + m["espectro_fala"][1]
    if graves > 0.6:
        print("        ruído quase todo grave — e grave atravessa porta e parede,")
        print("        por isso o microfone pega o que você não ouve")
    if m["desvio_tempo"] < 1.5:
        print("  i     CONSTANTE: aparelho ligado — ar-condicionado, geladeira,")
        print("        ventilador, computador. Desligue e remeça.")
    else:
        print(f"  i     FLUTUANTE ({m['desvio_tempo']:.1f} dB de desvio): é conteúdo,")
        print("        não máquina. TV ou som em outro cômodo, voz, trânsito.")
    if m["reverb"]:
        if m["reverb"] <= REVERB_BOM:
            print(f"  ok    pouca reverberação ({m['reverb']:.2f}s) — sala abafada, boa")
        elif m["reverb"] <= REVERB_OK:
            print(f"  ~     reverberação média ({m['reverb']:.2f}s) — aceitável")
        else:
            print(f"  X     muito eco ({m['reverb']:.2f}s) — o clone aprende a sala junto")


def veredito(m: dict) -> list[tuple[str, str]]:
    s = []
    if not m["piso_confiavel"]:
        s.append(("i", "sem silêncio para medir o ruído — o piso é um limite "
                       "superior, o real é menor. Comece o próximo bloco com "
                       "20 segundos parado."))
    else:
        if m["piso"] <= PISO_BOM:
            s.append(("ok", f"silêncio limpo ({m['piso']:.1f} dBFS)"))
        elif m["piso"] <= PISO_OK:
            s.append(("~", f"ruído de fundo audível ({m['piso']:.1f} dBFS)"))
        else:
            s.append(("X", f"ruído de fundo alto ({m['piso']:.1f} dBFS) — o clone "
                           "aprende isso junto com a voz"))
        if m["snr"] >= SNR_BOM:
            s.append(("ok", f"voz bem acima do ruído ({m['snr']:.0f} dB)"))
        elif m["snr"] >= SNR_OK:
            s.append(("~", f"margem apertada ({m['snr']:.0f} dB) — chegue mais perto"))
        else:
            s.append(("X", f"voz perto demais do ruído ({m['snr']:.0f} dB)"))

    if m["clipes"]:
        s.append(("X", f"{m['clipes']} amostras estouradas — distorção não se conserta"))
    else:
        s.append(("ok", f"sem distorção (pico {m['pico']:.1f} dBFS)"))

    if FALA_MIN <= m["fala"] <= FALA_MAX:
        s.append(("ok", f"volume da fala adequado ({m['fala']:.1f} dBFS)"))
    elif m["fala"] < FALA_MIN:
        s.append(("~", f"fala baixa ({m['fala']:.1f} dBFS) — aproxime-se"))
    else:
        s.append(("~", f"fala alta ({m['fala']:.1f} dBFS) — afaste-se"))

    if m["reverb"]:
        if m["reverb"] <= REVERB_BOM:
            s.append(("ok", f"pouca reverberação ({m['reverb']:.2f}s)"))
        elif m["reverb"] <= REVERB_OK:
            s.append(("~", f"reverberação média ({m['reverb']:.2f}s)"))
        else:
            s.append(("X", f"muito eco ({m['reverb']:.2f}s) — o clone aprende a sala"))

    if m["dinamica"] < 6:
        s.append(("~", f"pouca variação de volume na fala ({m['dinamica']:.0f} dB) — "
                       "pode ser ganho automático achatando a expressividade"))
    return s


def relatorio_voz(m: dict) -> list[str]:
    print(f"\n═══ {m['arquivo']}  ({m['duracao']:.0f}s, "
          f"{m['taxa_bits']} kbps {m['tipo_codec']}) ═══\n")
    print(f"  piso de ruído    : {m['piso']:7.1f} dBFS"
          f"{'' if m['piso_confiavel'] else '  (estimado)'}")
    print(f"  nível da fala    : {m['fala']:7.1f} dBFS")
    print(f"  relação sinal/ruído: {m['snr']:5.1f} dB")
    print(f"  pico             : {m['pico']:7.1f} dBFS")
    print(f"  fator de crista  : {m['crista']:7.1f} dB")
    print(f"  faixa dinâmica   : {m['dinamica']:7.1f} dB")
    if m["reverb"]:
        print(f"  reverberação     : {m['reverb']:7.2f} s")
    print(f"  silêncio medido  : {m['silencio_s']:7.1f} s")

    print(f"\n  Perfil no tempo:")
    for linha in perfil_tempo(m["niveis"], m["duracao"]):
        print(linha)
    print()
    for linha in espectro_texto(m["espectro_fala"], "Espectro da gravação:"):
        print(linha)
    if m["espectro_ruido"]:
        print()
        for linha in espectro_texto(m["espectro_ruido"], "Espectro só do ruído:"):
            print(linha)

    print()
    marcas = {"ok": "  ok  ", "~": "  ~   ", "X": "  X   ", "i": "  i   "}
    problemas = veredito(m)
    for nivel, texto in problemas:
        print(f"{marcas[nivel]}{texto}")
    niveis_v = [n for n, _ in problemas]
    print()
    if "X" in niveis_v:
        print("  VEREDITO: não use este material para clonagem.")
    elif "~" in niveis_v:
        print("  VEREDITO: serve, mas dá para melhorar.")
    else:
        print("  VEREDITO: material bom.")
    return niveis_v


def tabela_markdown(medidas: list[dict]) -> None:
    print("\n| Cenário | Fala | Ruído | S/R | Reverb | Crista | Codec |")
    print("|---|---|---|---|---|---|---|")
    for m in medidas:
        rev = f"{m['reverb']:.2f}s" if m["reverb"] else "—"
        piso = f"{m['piso']:.1f}" + ("" if m["piso_confiavel"] else "*")
        print(f"| {m['arquivo'].rsplit('.', 1)[0]} | {m['fala']:.1f} dBFS | "
              f"{piso} dBFS | **{m['snr']:.0f} dB** | {rev} | "
              f"{m['crista']:.0f} dB | {m['taxa_bits']} kbps |")
    if any(not m["piso_confiavel"] for m in medidas):
        print("\n`*` piso estimado: a gravação não tem silêncio sustentado, "
              "então o ruído real é menor que o indicado.")


def main() -> int:
    ap = argparse.ArgumentParser(description="Avalia gravações para clonagem.")
    ap.add_argument("arquivos", nargs="+")
    ap.add_argument("--sala", action="store_true",
                    help="a gravação é só silêncio: mede o ambiente")
    ap.add_argument("--markdown", action="store_true",
                    help="imprime tabela comparativa pronta para documentação")
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
        if args.markdown:
            continue
        if args.sala:
            relatorio_sala(m)
        else:
            relatorio_voz(m)

    if args.markdown:
        tabela_markdown(medidas)
    elif len(medidas) > 1:
        print("\n═══ comparação ═══")
        print(f"  {'arquivo':<26}{'fala':>8}{'ruído':>9}{'S/R':>7}{'reverb':>9}")
        for m in medidas:
            rev = f"{m['reverb']:.2f}s" if m["reverb"] else "—"
            print(f"  {m['arquivo'][:24]:<26}{m['fala']:>8.1f}{m['piso']:>9.1f}"
                  f"{m['snr']:>7.0f}{rev:>9}")
        tipos = {m["tipo_codec"] for m in medidas}
        if len(tipos) > 1:
            print("\n  ATENÇÃO: codificações diferentes. Compressão com perdas")
            print("  descarta som baixo demais para o ouvido, o que MELHORA o")
            print("  piso medido sem melhorar a gravação.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
