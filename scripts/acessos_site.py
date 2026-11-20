#!/usr/bin/env python3
"""Conta os acessos ao site pelos registros do CloudFront, sem guardar quem.

    python3 scripts/acessos_site.py              # lê o bucket dos registros e junta
    python3 scripts/acessos_site.py --dir PASTA  # lê arquivos locais (testes)
    python3 scripts/acessos_site.py --mostra     # resumo do que está guardado

Desde 20/11 a distribuição manda os registros de acesso (standard logging v2)
para um bucket privado, `campscast-registros`, que apaga tudo em 7 dias. Este
script lê o que está lá e guarda em `privado/dados/site-acessos.json` só
contagens por dia: páginas vistas por gente, visitantes distintos, de onde
vieram, celular ou computador, país; robôs à parte; leituras do feed e
downloads de áudio. Nenhum IP, nenhum navegador, nenhum hash sai daqui: o
visitante distinto é contado na memória e esquecido. É o que a página de
privacidade promete.

Sem estado de leitura: a cada execução relê os 7 dias do bucket (poucos MB) e,
para cada dia, fica a contagem maior entre a guardada e a nova — o dia que
está saindo da janela de 7 dias chega pela metade e não pode apagar o que já
foi contado, e o de hoje cresce até fechar.

Aceita os formatos JSON (uma linha por pedido) e W3C/texto (com `#Fields:`),
comprimidos ou não. Os nomes de campo são os do CloudFront: `date`, `time`,
`c-ip`, `cs-uri-stem`, `sc-status`, `cs(Referer)`, `cs(User-Agent)`, `x-edge-location`
(o ponto da rede da AWS que atendeu, que indica a região; o registro não tem país).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import pathlib
import re
import sys
import urllib.parse
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

ARQ = pathlib.Path(os.environ.get("ACESSOS_ARQ", ROOT / "privado" / "dados" / "site-acessos.json"))
BRT = timezone(timedelta(hours=-3))
NOSSOS = ("campscast.com.br", "www.campscast.com.br")

ROBO = re.compile(r"bot|crawl|spider|slurp|scrap|curl|wget|python|go-http|java/|okhttp|libwww|"
                  r"headless|phantom|monitor|uptime|check|feed|fetch|preview|http-client|axios|"
                  r"node-fetch|scan|zgrab|masscan|nmap|nuclei|^-$|^$", re.I)
CELULAR = re.compile(r"mobile|android|iphone|ipad|ipod", re.I)


def campo(r: dict, *nomes: str) -> str:
    for n in nomes:
        v = r.get(n)
        if v not in (None, "", "-"):
            return urllib.parse.unquote(str(v))
    return ""


def registros(texto: str):
    """Um dicionário por pedido, de JSON por linha ou W3C com #Fields."""
    campos: list[str] | None = None
    for linha in texto.splitlines():
        if not linha.strip():
            continue
        if linha.startswith("{"):
            try:
                yield json.loads(linha)
            except json.JSONDecodeError:
                continue
        elif linha.startswith("#Fields:"):
            campos = linha.split(":", 1)[1].split()
        elif linha.startswith("#") or campos is None:
            continue
        else:
            valores = linha.split("\t") if "\t" in linha else linha.split(" ")
            if len(valores) == len(campos):
                yield dict(zip(campos, valores))


def tipo(caminho: str) -> str:
    if caminho == "/feed.xml":
        return "feed"
    if caminho.startswith("/audio/") and caminho.endswith(".mp3"):
        return "audio"
    if caminho.endswith("/") or caminho.endswith(".html") or caminho == "/studio":
        return "pagina"
    return "outro"


def conta(textos) -> dict[str, dict]:
    """Contagens por dia (horário de Brasília) de todos os registros dados."""
    dias: dict[str, dict] = defaultdict(lambda: {
        "pedidos": 0, "paginas_gente": 0, "paginas_robo": 0, "visitantes": 0,
        "paginas": Counter(), "origens": Counter(), "dispositivo": Counter(), "paises": Counter(),
        "bordas": Counter(),
        "feed_leituras": 0, "feed_leitores": 0, "audio_downloads": Counter()})
    visitantes: dict[str, set] = defaultdict(set)
    leitores: dict[str, set] = defaultdict(set)
    baixados: dict[str, set] = defaultdict(set)
    for texto in textos:
        for r in registros(texto):
            data, hora = campo(r, "date"), campo(r, "time")
            if not data:
                continue
            try:
                quando = datetime.fromisoformat(f"{data}T{hora or '00:00:00'}+00:00").astimezone(BRT)
            except ValueError:
                continue
            dia = quando.date().isoformat()
            d = dias[dia]
            d["pedidos"] += 1
            caminho = campo(r, "cs-uri-stem") or "/"
            status = campo(r, "sc-status")
            ua = campo(r, "cs(User-Agent)", "cs-user-agent")
            quem = hashlib.sha256(f"{campo(r, 'c-ip')}|{ua}".encode()).hexdigest()  # só na memória
            t = tipo(caminho)
            if t == "feed":
                d["feed_leituras"] += 1
                leitores[dia].add(quem)
            elif t == "audio" and status in ("200", "206"):
                baixados[dia].add((quem, caminho))
            elif t == "pagina" and status in ("200", "304"):
                if ROBO.search(ua):
                    d["paginas_robo"] += 1
                    continue
                d["paginas_gente"] += 1
                d["paginas"][caminho] += 1
                visitantes[dia].add(quem)
                d["dispositivo"]["celular" if CELULAR.search(ua) else "computador"] += 1
                pais = campo(r, "c-country")
                if pais:
                    d["paises"][pais] += 1
                # Ponto da rede da AWS que atendeu (GRU = São Paulo, GIG = Rio): o
                # registro do CloudFront não tem país, e este é o que mais se parece.
                borda = campo(r, "x-edge-location")[:3].upper()
                if borda:
                    d["bordas"][borda] += 1
                ref = urllib.parse.urlsplit(campo(r, "cs(Referer)", "cs-referer")).hostname or ""
                ref = ref.removeprefix("www.")
                if ref and f"www.{ref}" not in NOSSOS and ref not in NOSSOS:
                    d["origens"][ref] += 1
                elif not ref:
                    d["origens"]["(direto)"] += 1
    saida = {}
    for dia, d in dias.items():
        d["visitantes"] = len(visitantes[dia])
        d["feed_leitores"] = len(leitores[dia])
        for _, arquivo in baixados[dia]:
            d["audio_downloads"][arquivo.rsplit("/", 1)[-1]] += 1
        saida[dia] = {k: (dict(v.most_common()) if isinstance(v, Counter) else v) for k, v in d.items()}
    return saida


def junta(guardado: dict, novo: dict) -> dict:
    """Para cada dia, fica a leitura com mais pedidos: um dia só cresce."""
    dias = dict(guardado.get("dias", {}))
    for dia, d in novo.items():
        if d["pedidos"] >= dias.get(dia, {}).get("pedidos", -1):
            dias[dia] = d
    return {"_sobre": ("Acessos ao site contados pelos registros do CloudFront (scripts/acessos_site.py). "
                       "Só contagens por dia, no horário de Brasília; nenhum IP nem navegador."),
            "dias": dict(sorted(dias.items()))}


def textos_do_bucket():
    import s3
    bucket = s3.bucket_registros(s3.resolve_bucket(None) or "campscast")
    for obj in s3.list_objects(bucket):
        dados = s3.get_object(bucket, obj["key"])
        yield (gzip.decompress(dados) if dados[:2] == b"\x1f\x8b" else dados).decode("utf-8", "replace")


def textos_da_pasta(pasta: pathlib.Path):
    for p in sorted(pasta.rglob("*")):
        if p.is_file():
            dados = p.read_bytes()
            yield (gzip.decompress(dados) if dados[:2] == b"\x1f\x8b" else dados).decode("utf-8", "replace")


def resumo(hist: dict) -> str:
    dias = hist.get("dias", {})
    if not dias:
        return "Acessos ao site: nada guardado ainda."
    ult = list(dias)[-7:]
    pag = sum(dias[d]["paginas_gente"] for d in ult)
    vis = sum(dias[d]["visitantes"] for d in ult)
    aud = sum(sum(dias[d]["audio_downloads"].values()) for d in ult)
    return (f"Acessos ao site: {len(dias)} dias guardados ({min(dias)} a {max(dias)}); nos últimos "
            f"{len(ult)}, {pag} páginas vistas por gente, ~{vis} visitantes por dia somados, "
            f"{aud} downloads de áudio direto do site.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Conta os acessos ao site pelos registros do CloudFront.")
    ap.add_argument("--dir", type=pathlib.Path, help="ler registros desta pasta, não do bucket")
    ap.add_argument("--mostra", action="store_true")
    a = ap.parse_args(argv)
    hist = json.loads(ARQ.read_text(encoding="utf-8")) if ARQ.exists() else {}
    if a.mostra:
        print(resumo(hist))
        return 0
    try:
        novo = conta(textos_da_pasta(a.dir) if a.dir else textos_do_bucket())
    except Exception as e:  # noqa: BLE001 — falha vira aviso no orquestrador
        print(f"Acessos ao site não lidos: {e}", file=sys.stderr)
        return 1
    hist = junta(hist, novo)
    ARQ.parent.mkdir(parents=True, exist_ok=True)
    tmp = ARQ.with_suffix(".tmp")
    tmp.write_text(json.dumps(hist, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tmp.replace(ARQ)
    print(resumo(hist))
    return 0


if __name__ == "__main__":
    sys.exit(main())
