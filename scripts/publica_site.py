#!/usr/bin/env python3
"""
CampsCast — sobe o site para o S3.

Sobe as páginas, os estilos, os scripts, as imagens e as fontes de site/, mais
os dois arquivos de dados que o estúdio e a capa leem (estudio/elenco.json e
estudio/ultimo.json). Não toca no podcast: feed.xml, cover.jpg, estado.json,
audio/ e referencias/ são do publish.py e do estado.py, e uma chave do site
que caísse num deles faz o script parar antes de subir qualquer coisa.

As páginas, os estilos, os scripts e os dados sobem com cache de 5 minutos,
como o feed; imagens e fontes, com um dia. Assim uma mudança aparece sem
precisar limpar o cache do CloudFront. O HTML sobe por último, para nenhuma
página apontar para um arquivo que ainda não chegou.

O run_episode.sh chama este script no fim de cada episódio publicado.
SITE_ARQ troca o S3 por um arquivo local com as chaves que subiriam, como o
ESTADO_ARQ do estado.py: é o que o smoke test usa.

Uso:
    python3 scripts/estudio.py               # gera os dados do estúdio
    python3 scripts/publica_site.py --dry-run   # lista o que subiria
    python3 scripts/publica_site.py             # sobe
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT / "scripts"))

CURTO, LONGO = "max-age=300", "max-age=86400"
TIPOS = {
    ".html": ("text/html; charset=utf-8", CURTO),
    ".css": ("text/css; charset=utf-8", CURTO),
    ".js": ("text/javascript; charset=utf-8", CURTO),
    ".json": ("application/json; charset=utf-8", CURTO),
    ".jpg": ("image/jpeg", LONGO),
    ".png": ("image/png", LONGO),
    ".svg": ("image/svg+xml", LONGO),
    ".woff2": ("font/woff2", LONGO),
    ".txt": ("text/plain; charset=utf-8", LONGO),
}
# O que é do podcast, não do site.
DO_PODCAST = {"feed.xml", "cover.jpg", "estado.json"}
PREFIXOS_DO_PODCAST = ("audio/", "referencias/")
# Ferramentas e notas de desenvolvimento, e a execução de cada dia: o site só
# lê o ultimo.json.
FORA = {"estudio/folha.html"}
DIA = re.compile(r"^estudio/\d{4}-\d{2}-\d{2}\.json$")
DADOS = ("estudio/elenco.json", "estudio/ultimo.json")


class Recusa(RuntimeError):
    pass


def lista(site: pathlib.Path = SITE) -> list[tuple[pathlib.Path, str, str, str]]:
    """(arquivo, chave, tipo, cache) de tudo o que sobe, com o HTML no fim."""
    itens = []
    for p in sorted(site.rglob("*")):
        if not p.is_file() or any(parte.startswith(".") for parte in p.relative_to(site).parts):
            continue
        chave = p.relative_to(site).as_posix()
        if chave in DO_PODCAST or chave.startswith(PREFIXOS_DO_PODCAST):
            raise Recusa(f"site/{chave} cairia em cima do podcast ({chave}); nada foi enviado.")
        if chave in FORA or DIA.match(chave) or p.suffix not in TIPOS:
            continue
        tipo, cache = TIPOS[p.suffix]
        itens.append((p, chave, tipo, cache))
    faltam = [d for d in DADOS if d not in {c for _, c, _, _ in itens}]
    if faltam:
        raise Recusa(f"faltam {', '.join(faltam)}; rode antes: python3 scripts/estudio.py")
    # O HTML por último, e a capa por último de todos.
    return sorted(itens, key=lambda i: (i[1].endswith(".html"), i[1] == "index.html", i[1]))


def publica(itens, put, bucket: str) -> int:
    for p, chave, tipo, cache in itens:
        put(bucket, chave, p.read_bytes(), tipo, cache_control=cache)
        print(f"  → s3://{bucket}/{chave}")
    return len(itens)


def main() -> int:
    ap = argparse.ArgumentParser(description="Sobe o site para o S3, sem tocar no podcast.")
    ap.add_argument("--dry-run", action="store_true", help="só lista o que subiria")
    ap.add_argument("--site", type=pathlib.Path, default=SITE, help=argparse.SUPPRESS)
    args = ap.parse_args()

    try:
        itens = lista(args.site)
    except Recusa as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1
    total = sum(p.stat().st_size for p, _, _, _ in itens)

    if args.dry_run:
        for p, chave, tipo, cache in itens:
            print(f"  {chave:56} {p.stat().st_size / 1000:7.1f} kB  {tipo.split(';')[0]:24} {cache}")
        print(f"{len(itens)} arquivos, {total / 1_000_000:.2f} MB. Nada foi enviado (--dry-run).")
        return 0

    destino = os.environ.get("SITE_ARQ")
    if destino:
        pathlib.Path(destino).write_text("".join(f"{c}\n" for _, c, _, _ in itens), encoding="utf-8")
        print(f"Site: {len(itens)} chaves em {destino}, nada no S3 (SITE_ARQ).")
        return 0

    from s3 import S3Error, load_credentials, load_env, put_object, resolve_bucket
    load_env()
    bucket = resolve_bucket(None)
    if not bucket:
        print("ERRO: S3_BUCKET não definido no .env.", file=sys.stderr)
        return 1
    if os.environ.get("S3_PREFIX", "").strip("/"):
        print("ERRO: com S3_PREFIX o feed mora numa subpasta, e o site é feito para a raiz do domínio.",
              file=sys.stderr)
        return 1
    region = os.environ.get("AWS_REGION", "us-east-1")
    try:
        creds = load_credentials()
        put = lambda b, k, d, t, cache_control: put_object(b, k, d, t, region=region,
                                                          cache_control=cache_control, creds=creds)
        n = publica(itens, put, bucket)
    except S3Error as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1
    print(f"Site publicado: {n} arquivos, {total / 1_000_000:.2f} MB.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
