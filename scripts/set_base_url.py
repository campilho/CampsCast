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
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOW = ROOT / "config" / "show.json"

# Os três caminhos que um app de podcast realmente busca.
CAMINHOS = ["feed.xml", "cover.jpg"]


def responde(url: str) -> tuple[bool, str]:
    try:
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": "CampsCast/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return True, f"HTTP {r.status} {r.headers.get('Content-Type', '')}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, str(e)[:90]


def main() -> int:
    ap = argparse.ArgumentParser(description="Troca a base_url do feed.")
    ap.add_argument("base_url", help="ex.: https://campscast.com.br")
    ap.add_argument("--dry-run", action="store_true", help="só verifica")
    ap.add_argument("--skip-check", action="store_true",
                    help="grava sem verificar (não recomendado)")
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

        falhou = False
        for c in caminhos:
            ok, detalhe = responde(f"{base}/{c}")
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
