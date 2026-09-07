#!/usr/bin/env python3
"""
CampsCast — avalia gravações para clonagem de voz, e compara cenários.

Clonagem aprende tudo que está no áudio: ruído de rua, chiado de aparelho, eco
do cômodo. Depois não há como separar. Este script mede antes de você gastar a
gravação inteira — e produz tabelas comparáveis entre salas, aparelhos e
distâncias, para documentar o que funciona.

    python3 scripts/check_recording.py bloco.m4a
    python3 scripts/check_recording.py silencio.m4a --sala
    python3 scripts/check_recording.py bloco.m4a --detalhe   # perfil linha a linha
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
SPARK = "▁▂▃▄▅▆▇█"


def barra(fracao: float, largura: int = 28) -> str:
    cheios = int(fracao * largura)
    return "█" * cheios + "·" * (largura - cheios)


def sparkline(ns: list[float], largura: int = 56) -> tuple[str, float, float]:
    """O perfil inteiro numa linha só. Cada caractere é um trecho do tempo."""
    if not ns:
        return "", 0.0, 0.0
    lo, hi = min(ns), max(ns)
    faixa = max(hi - lo, 6.0)
    por_col = max(1, len(ns) / largura)
    colunas = []
    i = 0.0
    while int(i) < len(ns):
        grupo = ns[int(i):max(int(i) + 1, int(i + por_col))]
        v = sum(grupo) / len(grupo)
        colunas.append(SPARK[min(len(SPARK) - 1,
                                 int((v - lo) / faixa * (len(SPARK) - 1)))])
        i += por_col
    return "".join(colunas), lo, hi


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


def espectro_compacto(fracoes: list[float]) -> str:
    partes = []
    for (lo, hi, nome), f in zip(BANDAS, fracoes):
        if f >= 0.05:
            partes.append(f"{nome} {f*100:.0f}% {'█' * max(1, int(f * 14))}")
    resto = sum(f for f in fracoes if f < 0.05)
    if resto >= 0.01:
        partes.append(f"resto {resto*100:.0f}%")
    return "   ".join(partes)


def relatorio_sala(m: dict, detalhe: bool = False) -> None:
    ns = m["niveis"]
    media = sum(ns) / len(ns)
    print(f"\n═══ {m['arquivo']} — ambiente ({m['duracao']:.0f}s) ═══\n")
    print(f"  ruído   médio {media:6.1f}   min {min(ns):6.1f}   "
          f"max {max(ns):6.1f}   variação {max(ns)-min(ns):5.1f} dB")
    linha_tempo = f"  tempo   desvio {m['desvio_tempo']:.1f} dB"
    linha_tempo += ("  ->  CONSTANTE (aparelho ligado)" if m["desvio_tempo"] < 1.5
                    else "  ->  FLUTUANTE (conteúdo: TV, voz, trânsito)")
    print(linha_tempo)
    if m["reverb"]:
        marca = "" if m.get("reverb_confiavel", True) else "?"
        print(f"  sala    reverberação {m['reverb']:.2f}s{marca}")

    spark, lo, hi = sparkline(ns)
    print(f"\n  {spark}")
    rotulo_fim = f"{m['duracao']:.0f}s"
    preenche = max(1, len(spark) - 2 - len(rotulo_fim))
    print(f"  0s{' ' * preenche}{rotulo_fim}"
          f"      escala {lo:.0f} a {hi:.0f} dBFS")

    print(f"\n  espectro  {espectro_compacto(m['espectro_fala'])}")

    print()
    if media <= PISO_BOM:
        print("  ok    sala silenciosa — pode gravar")
    elif media <= PISO_OK:
        print("  ~     sala aceitável, mas já se ouve o ambiente")
    else:
        print("  X     sala barulhenta demais — procure outra hora ou cômodo")

    graves = m["espectro_fala"][0] + m["espectro_fala"][1]
    if graves > 0.6:
        print("        ruído quase todo grave — atravessa porta e parede, por isso")
        print("        o microfone pega o que você não ouve")
    if m["reverb"] and m["reverb"] > REVERB_OK and m.get("reverb_confiavel", True):
        print(f"  X     muito eco ({m['reverb']:.2f}s) — o clone aprende a sala junto")

    if detalhe:
        print(f"\n  Perfil detalhado:")
        for linha in perfil_tempo(ns, m["duracao"]):
            print(linha)
        print()
        for linha in espectro_texto(m["espectro_fala"], "Espectro completo:"):
            print(linha)


def veredito(m: dict) -> list[tuple[str, str]]:
    s = []
    if not m["piso_confiavel"]:
        s.append(("i", "sem silêncio para medir o ruído — o piso é um limite "
                       "superior, o real é menor. Comece o próximo bloco com "
                       "10 segundos parado."))
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

    if m["reverb"] and not m.get("reverb_confiavel", True):
        s.append(("i", f"reverberação ({m['reverb']:.2f}s) não é confiável com S/R de "
                       f"{m['snr']:.0f} dB — o ruído infla a medida; melhore o S/R antes"))
    elif m["reverb"]:
        if m["reverb"] <= REVERB_BOM:
            s.append(("ok", f"pouca reverberação ({m['reverb']:.2f}s)"))
        elif m["reverb"] <= REVERB_OK:
            s.append(("~", f"reverberação média ({m['reverb']:.2f}s)"))
        else:
            s.append(("X", f"muito eco ({m['reverb']:.2f}s) — o clone aprende a sala"))

    # A dinâmica é contada a partir do piso; com piso não confiável ela vira
    # alarme falso. Num arquivo sem silêncio nenhum acusou 0,0 dB de variação
    # numa fala perfeitamente expressiva.
    if m["dinamica"] < 6 and m["piso_confiavel"]:
        s.append(("~", f"pouca variação de volume na fala ({m['dinamica']:.0f} dB) — "
                       "pode ser ganho automático achatando a expressividade"))
    return s


def relatorio_voz(m: dict, detalhe: bool = False) -> list[str]:
    print(f"\n═══ {m['arquivo']}  ({m['duracao']:.0f}s, "
          f"{m['taxa_bits']} kbps {m['tipo_codec']}) ═══\n")
    est = "" if m["piso_confiavel"] else "*"
    print(f"  níveis  fala {m['fala']:6.1f}   ruído {m['piso']:6.1f}{est}   "
          f"S/R {m['snr']:5.1f} dB   pico {m['pico']:6.1f}")
    rev = f"{m['reverb']:.2f}s" if m["reverb"] else "—"
    print(f"  sala    reverberação {rev}     dinâmica {m['dinamica']:.1f} dB     "
          f"crista {m['crista']:.1f} dB")
    print(f"  medido  {m['silencio_s']:.0f}s de silêncio sustentado" +
          ("" if m["piso_confiavel"] else "  (nenhum — ruído é limite superior)"))

    spark, lo, hi = sparkline(m["niveis"])
    print(f"\n  {spark}")
    rotulo = f"{m['duracao']:.0f}s"
    print(f"  0s{' ' * max(1, len(spark) - 2 - len(rotulo))}{rotulo}"
          f"      escala {lo:.0f} a {hi:.0f} dBFS")

    print(f"\n  voz       {espectro_compacto(m['espectro_fala'])}")
    if m["espectro_ruido"]:
        print(f"  ruído     {espectro_compacto(m['espectro_ruido'])}")

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
    elif not m["piso_confiavel"]:
        # Sem silêncio não há S/R, e S/R é a métrica que mais importa para
        # clonagem. Aprovar sem ela seria aprovar pelo que sobrou de medir.
        print("  VEREDITO: o que dá para medir está bom, mas sem silêncio no")
        print("            começo não dá para verificar o S/R.")
    else:
        print("  VEREDITO: material bom.")

    if detalhe:
        print(f"\n  Perfil detalhado:")
        for linha in perfil_tempo(m["niveis"], m["duracao"]):
            print(linha)
        print()
        for linha in espectro_texto(m["espectro_fala"], "Espectro da gravação:"):
            print(linha)
        if m["espectro_ruido"]:
            print()
            for linha in espectro_texto(m["espectro_ruido"], "Espectro só do ruído:"):
                print(linha)
    return niveis_v


def tabela_markdown(medidas: list[dict]) -> None:
    """Tabela markdown com colunas alinhadas — válida no GitHub e legível crua."""
    cab = ["Cenário", "Fala", "Ruído", "S/R", "Reverb", "Crista", "Codec"]
    linhas = []
    for m in medidas:
        linhas.append([
            m["arquivo"].rsplit(".", 1)[0],
            f"{m['fala']:.1f} dBFS",
            f"{m['piso']:.1f}{'' if m['piso_confiavel'] else '*'} dBFS",
            f"**{m['snr']:.0f} dB**",
            f"{m['reverb']:.2f}s" if m["reverb"] else "—",
            f"{m['crista']:.0f} dB",
            f"{m['taxa_bits']} kbps",
        ])

    larg = [max(len(cab[i]), *(len(l[i]) for l in linhas)) for i in range(len(cab))]
    def linha(campos, preencher=" "):
        return "| " + " | ".join(c.ljust(larg[i], preencher)
                                 for i, c in enumerate(campos)) + " |"

    print()
    print(linha(cab))
    print(linha(["-" * larg[i] for i in range(len(cab))], "-"))
    for l in linhas:
        print(linha(l))
    if any(not m["piso_confiavel"] for m in medidas):
        print("\n`*` piso estimado: a gravação não tem silêncio sustentado, "
              "então o ruído real é menor que o indicado.")


def main() -> int:
    ap = argparse.ArgumentParser(description="Avalia gravações para clonagem.")
    ap.add_argument("arquivos", nargs="+")
    ap.add_argument("--sala", action="store_true",
                    help="a gravação é só silêncio: mede o ambiente")
    ap.add_argument("--detalhe", action="store_true",
                    help="perfil linha a linha e espectro completo")
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
            relatorio_sala(m, args.detalhe)
        else:
            relatorio_voz(m, args.detalhe)

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
