#!/usr/bin/env python3
"""
CampsCast — publica o estado da última execução num arquivo público.

Por que existe: quando o episódio não sai, quem precisa saber costuma estar
longe do Mac. Aviso nativo do macOS morre na tela de casa e e-mail depende de
SMTP configurado. O S3 já tem credencial e já é consultado de qualquer lugar,
então o próprio pipeline deixa lá um `estado.json` dizendo como terminou —
inclusive quando terminou mal. Um vigia externo lê esse arquivo e avisa.

O arquivo é público, então não leva caminho de máquina, nome de usuário nem
variável de ambiente: o motivo da falha é higienizado e truncado.

Nunca derruba o pipeline: qualquer problema aqui sai com rc=0.

ESTADO_ARQ troca o S3 por um arquivo local — é o que o smoke test usa, para
que teste nenhum encoste no bucket de produção.

Uso:
    python3 scripts/estado.py --data 2026-09-14 --estado ok --etapa concluido
    python3 scripts/estado.py --data 2026-09-14 --estado falhou \
        --etapa pesquisa --motivo "claude -p falhou (rc=1)"
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

CHAVE = "estado.json"
LIMITE_MOTIVO = 240


def higieniza(motivo: str) -> str:
    """Tira do motivo o que não pode virar página pública."""
    texto = " ".join(motivo.split())
    if not texto:
        return ""
    # Caminho de casa vira ~, e qualquer /Users/<alguem> vira /Users/<usuario>.
    texto = texto.replace(str(pathlib.Path.home()), "~")
    texto = re.sub(r"/Users/[^/\s]+", "/Users/<usuario>", texto)
    # Nada que pareça chave: sequências longas de caractere de token.
    texto = re.sub(r"\b[A-Za-z0-9_\-]{32,}\b", "<omitido>", texto)
    if len(texto) > LIMITE_MOTIVO:
        texto = texto[: LIMITE_MOTIVO - 1].rstrip() + "…"
    return texto


def monta(data: str, estado: str, etapa: str, motivo: str,
          agora: dt.datetime | None = None) -> dict:
    agora = agora or dt.datetime.now().astimezone()
    corpo = {
        "data": data,
        "estado": estado,
        "etapa": etapa,
        "motivo": higieniza(motivo) if estado != "ok" else "",
        "quando": agora.isoformat(timespec="seconds"),
    }
    if estado == "ok":
        try:
            show = json.loads((ROOT / "config" / "show.json").read_text(encoding="utf-8"))
            base = show.get("base_url", "").rstrip("/")
            if base:
                corpo["episodio"] = f"{base}/audio/{data}.mp3"
        except Exception:
            pass
    return corpo


def publica(corpo: dict) -> str | None:
    from s3 import load_env, put_object, resolve_bucket

    load_env()
    bucket = resolve_bucket(None)
    if not bucket:
        print("AVISO: sem bucket configurado; estado não foi publicado.", file=sys.stderr)
        return None

    prefixo = os.environ.get("S3_PREFIX", "").strip("/")
    chave = f"{prefixo}/{CHAVE}" if prefixo else CHAVE
    dados = json.dumps(corpo, ensure_ascii=False, indent=1).encode("utf-8")
    # no-cache é o ponto todo: um vigia que lê versão velha não serve para nada.
    return put_object(bucket, chave, dados, "application/json",
                      cache_control="no-cache, max-age=0")


def main() -> int:
    ap = argparse.ArgumentParser(description="Publica o estado da execução.")
    ap.add_argument("--data", required=True)
    ap.add_argument("--estado", required=True, choices=["ok", "falhou"])
    ap.add_argument("--etapa", default="")
    ap.add_argument("--motivo", default="")
    ap.add_argument("--saida", help="grava num arquivo local em vez de subir")
    args = ap.parse_args()

    corpo = monta(args.data, args.estado, args.etapa, args.motivo)
    texto = json.dumps(corpo, ensure_ascii=False, indent=1)

    destino = args.saida or os.environ.get("ESTADO_ARQ")
    if destino:
        pathlib.Path(destino).write_text(texto + "\n", encoding="utf-8")
        print(texto)
        return 0

    try:
        url = publica(corpo)
        if url:
            print(f"Estado publicado: {url} ({corpo['estado']}/{corpo['etapa']})")
    except Exception as e:                      # aviso nunca derruba o pipeline
        print(f"AVISO: não consegui publicar o estado ({e}).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
