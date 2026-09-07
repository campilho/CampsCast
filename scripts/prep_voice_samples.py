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
import hashlib
import pathlib
import subprocess
import sys
import wave

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

TAXA = 44100          # padrão de áudio; 48k também serve e ocupa 9% mais
MB_POR_MINUTO = 5.05  # mono 16 bits a 44,1 kHz


SNR_MINIMO = 30.0


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
        marcas = {"ok": "  ok  ", "~": "  ~   ", "X": "  X   ", "i": "  i   "}
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

    # Auditoria da PASTA INTEIRA, não só do que acabou de ser convertido. Quem
    # sobe seleciona a pasta, não a lista desta execução: uma sessão anterior
    # deixou 4,7 minutos com piso a -31,6 dBFS convivendo com material bom, e o
    # resumo anunciava só os minutos recém-processados.
    return audita_pasta(saida)


def _impressao(wav: pathlib.Path) -> str:
    """Hash do áudio decodificado, não do arquivo.

    Exportar a mesma gravação duas vezes gera contêineres com metadados
    diferentes: tamanho igual ao byte, hash de arquivo diferente. Só o PCM
    denuncia. Amostra repetida entra no treino com peso dobrado.
    """
    with wave.open(str(wav)) as f:
        return hashlib.sha256(f.readframes(f.getnframes())).hexdigest()


def audita_pasta(saida: pathlib.Path, mover: bool = True) -> int:
    from check_recording import analisa

    quarentena = saida / "reprovadas"
    aprovados, recusados = [], []
    vistos: dict[str, str] = {}
    for w in sorted(saida.glob("*.wav")):
        try:
            digital = _impressao(w)
        except Exception:
            digital = None
        if digital and digital in vistos:
            recusados.append((w, f"áudio idêntico a {vistos[digital]}"))
            continue
        if digital:
            vistos[digital] = w.name
        try:
            m = analisa(w)
        except Exception as e:
            recusados.append((w, f"não deu para analisar: {e}"))
            continue
        if not m["piso_confiavel"]:
            recusados.append((w, "sem silêncio para medir o S/R"))
        elif m["snr"] < SNR_MINIMO:
            recusados.append((w, f"S/R {m['snr']:.1f} dB, abaixo de {SNR_MINIMO:.0f}"))
        else:
            aprovados.append((w, m))

    print(f"\n═══ o que está em {saida}/ ═══\n")
    for w, m in aprovados:
        print(f"  ✓  {w.name:34} {m['duracao']/60:5.1f} min   "
              f"S/R {m['snr']:5.1f} dB   fala {m['fala']:6.1f} dBFS")
    for w, motivo in recusados:
        print(f"  ✗  {w.name:34} {motivo}")

    bons = sum(m["duracao"] for _, m in aprovados) / 60
    print(f"\n  {bons:.1f} minutos aprovados de {30:.0f}")
    if bons < 30:
        print(f"  Faltam {30 - bons:.1f} minutos.")

    if not recusados:
        print("\n  Suba os .wav como amostras separadas — a ElevenLabs aceita vários.")
        return 0

    if mover:
        quarentena.mkdir(exist_ok=True)
        for w, _ in recusados:
            w.rename(quarentena / w.name)
        print(f"\n  {len(recusados)} arquivo(s) movido(s) para {quarentena}/ para que")
        print("  não subam por engano. Nada foi apagado.")
    print("  Material ruim contamina o modelo inteiro, e não há como remover depois.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
