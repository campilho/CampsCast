#!/usr/bin/env python3
"""
CampsCast — troca o endereço público do feed, com verificação antes.

Trocar `base_url` para um domínio que ainda não responde publica um feed cujos
episódios apontam para o nada — e, se isso acontecer depois da submissão aos
diretórios, os apps dos ouvintes passam a falhar o download em silêncio. Por
isso este script confere antes de gravar.

    python3 scripts/set_base_url.py https://campscast.com.br
    python3 scripts/set_base_url.py https://campscast.com.br --dry-run
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import http.client
import socket
import ssl
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOW = ROOT / "config" / "show.json"

# Os três caminhos que um app de podcast realmente busca.
CAMINHOS = ["feed.xml", "cover.jpg"]


def responde(url: str, resolve_ip: str | None = None) -> tuple[bool, str]:
    """HEAD na URL. Com resolve_ip, conecta nesse IP mantendo Host e SNI.

    O `--resolve` existe por causa de cache negativo de DNS. O SOA de uma zona
    nova costuma trazer TTL negativo de 24 horas: quem consultou o nome ANTES do
    registro existir guarda "não existe" por um dia inteiro. O domínio funciona
    para o mundo e não funciona para você — e é justamente você que precisa
    verificar antes de trocar a base_url.
    """
    partes = urllib.parse.urlparse(url)
    host, caminho = partes.hostname, partes.path or "/"

    if not resolve_ip:
        try:
            req = urllib.request.Request(url, method="HEAD",
                                         headers={"User-Agent": "CampsCast/1.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return True, f"HTTP {r.status} {r.headers.get('Content-Type', '')}"
        except urllib.error.HTTPError as e:
            return False, f"HTTP {e.code}"
        except Exception as e:
            return False, str(e)[:90]

    try:
        ctx = ssl.create_default_context()
        conexao = http.client.HTTPSConnection(host, 443, timeout=20)
        # Conecta no IP informado, mas com Host e SNI do domínio: é o que
        # valida o certificado e a rota de verdade.
        conexao.sock = ctx.wrap_socket(
            socket.create_connection((resolve_ip, 443), 20), server_hostname=host)
        conexao.request("HEAD", caminho, headers={"Host": host,
                                                  "User-Agent": "CampsCast/1.0"})
        r = conexao.getresponse()
        ok = 200 <= r.status < 300
        return ok, f"HTTP {r.status} {r.getheader('Content-Type', '')}"
    except Exception as e:
        return False, str(e)[:90]
    finally:
        try:
            conexao.close()
        except Exception:
            pass


def main() -> int:
    ap = argparse.ArgumentParser(description="Troca a base_url do feed.")
    ap.add_argument("base_url", help="ex.: https://campscast.com.br")
    ap.add_argument("--dry-run", action="store_true", help="só verifica")
    ap.add_argument("--skip-check", action="store_true",
                    help="grava sem verificar (não recomendado)")
    ap.add_argument("--resolve", metavar="IP",
                    help="conecta neste IP em vez de usar o DNS local, mantendo "
                         "Host e SNI. Útil quando o resolvedor guardou cache "
                         "negativo de antes do domínio existir "
                         "(dig +short @8.8.8.8 <dominio>)")
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    if not base.startswith("https://"):
        print("ERRO: use https. Apps de podcast recusam feed em http.",
              file=sys.stderr)
        return 2

    show = json.loads(SHOW.read_text(encoding="utf-8"))
    print(f"atual : {show['base_url']}")
    print(f"novo  : {base}\n")

    if not args.skip_check:
        # O episódio mais recente entra na checagem: é o que os apps vão baixar.
        caminhos = list(CAMINHOS)
        episodios = sorted((ROOT / "episodes").glob("*.md"))
        if episodios:
            caminhos.append(f"audio/{episodios[-1].stem}.mp3")

        if args.resolve:
            print(f"  (conectando em {args.resolve}, ignorando o DNS local)\n")
        falhou = False
        for c in caminhos:
            ok, detalhe = responde(f"{base}/{c}", args.resolve)
            print(f"  {'ok  ' if ok else 'FALHA'}  {base}/{c}  —  {detalhe}")
            falhou |= not ok
        print()
        if falhou:
            print("Não gravei nada. O domínio ainda não serve todos os arquivos —\n"
                  "verifique certificado, CloudFront e DNS antes de trocar.",
                  file=sys.stderr)
            return 1

    if args.dry_run:
        print("(dry-run: nada foi alterado)")
        return 0

    show["base_url"] = base
    show["link"] = show.get("link") or base
    show["cover_url"] = f"{base}/cover.jpg"
    SHOW.write_text(json.dumps(show, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    print(f"config/show.json atualizado.\n"
          f"Agora republique:  python3 scripts/publish.py --date $(date +%F)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
