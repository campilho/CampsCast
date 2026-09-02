#!/usr/bin/env python3
"""
CampsCast — gera feed.xml a partir de episodes/ + audio/ e sobe para o S3.

Sem dependências externas e sem AWS CLI: o upload usa `scripts/s3.py`, que
assina as requisições em SigV4 com a biblioteca padrão. Quem clona o repositório
precisa de Python e nada mais.

Uso:
    python3 scripts/publish.py --date 2026-08-24
    python3 scripts/publish.py --date 2026-08-24 --no-upload   # só gera o feed
    python3 scripts/publish.py --rebuild                       # refaz o feed inteiro
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request
from email.utils import format_datetime
from datetime import datetime, timezone
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
EPISODES = ROOT / "episodes"
AUDIO = ROOT / "audio"
FEED_OUT = ROOT / "feed" / "feed.xml"

# Hub público de WebSub (PubSubHubbub). Serve para avisar agregadores de que o
# feed mudou, em vez de depender de eles voltarem sozinhos.
WEBSUB_HUB = "https://pubsubhubbub.appspot.com/"

BITRATES = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]
SAMPLE_RATES = [44100, 48000, 32000, 0]


# ----------------------------------------------------------------- utilidades
def load_env() -> None:
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def load_show() -> dict:
    return json.loads((ROOT / "config" / "show.json").read_text(encoding="utf-8"))


def parse_front_matter(text: str) -> dict:
    """Parser mínimo para o front-matter que prompts/master.md especifica.

    Cobre escalares `chave: valor`, listas de escalares e listas de mapas com
    indentação de dois espaços. Não é YAML completo — é o suficiente para o
    contrato do roteiro, e evita uma dependência.
    """
    if not text.lstrip().startswith("---"):
        return {}
    block = text.lstrip().split("---", 2)[1]

    data: dict = {}
    key_stack: str | None = None
    current_map: dict | None = None

    for raw in block.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()

        if indent == 0:
            key_stack, current_map = None, None
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            k, v = k.strip(), v.strip()
            if v in ("", "[]", "{}"):
                data[k] = [] if v != "{}" else {}
                key_stack = k
            else:
                data[k] = v.strip('"').strip("'")
        elif key_stack:
            target = data.setdefault(key_stack, [])
            if not isinstance(target, list):
                continue
            if line.startswith("- "):
                item = line[2:].strip()
                if ":" in item:
                    k, v = item.split(":", 1)
                    current_map = {k.strip(): v.strip().strip('"').strip("'")}
                    target.append(current_map)
                else:
                    current_map = None
                    target.append(item.strip('"').strip("'"))
            elif current_map is not None and ":" in line:
                k, v = line.split(":", 1)
                current_map[k.strip()] = v.strip().strip('"').strip("'")
    return data


def mp3_duration_seconds(path: pathlib.Path) -> int | None:
    """Duração de um MP3 CBR/VBR somando os frames. Python puro, sem ffprobe."""
    try:
        data = path.read_bytes()
    except OSError:
        return None

    i = 0
    # Pula tag ID3v2, se houver.
    if data[:3] == b"ID3" and len(data) > 10:
        size = ((data[6] & 0x7F) << 21 | (data[7] & 0x7F) << 14
                | (data[8] & 0x7F) << 7 | (data[9] & 0x7F))
        i = 10 + size

    total = 0.0
    n = len(data)
    while i + 4 <= n:
        if data[i] != 0xFF or (data[i + 1] & 0xE0) != 0xE0:
            i += 1
            continue
        h1, h2, h3 = data[i + 1], data[i + 2], data[i + 3]
        version_bits = (h1 >> 3) & 0x03      # 3 = MPEG1
        layer_bits = (h1 >> 1) & 0x03        # 1 = Layer III
        bitrate_idx = (h2 >> 4) & 0x0F
        rate_idx = (h2 >> 2) & 0x03
        padding = (h2 >> 1) & 0x01
        if version_bits != 3 or layer_bits != 1 or bitrate_idx in (0, 15) or rate_idx == 3:
            i += 1
            continue
        bitrate = BITRATES[bitrate_idx] * 1000
        rate = SAMPLE_RATES[rate_idx]
        frame_len = int(144 * bitrate / rate) + padding
        if frame_len <= 4:
            i += 1
            continue
        total += 1152 / rate
        i += frame_len
        _ = h3

    return int(round(total)) if total > 0 else None


def hhmmss(seconds: int) -> str:
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"


def duration_from_mmss(text: str) -> int | None:
    m = re.fullmatch(r"(\d+):(\d{2})", (text or "").strip())
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None


# ------------------------------------------------------------------ episódios
def collect_episodes() -> list[dict]:
    eps = []
    for path in sorted(EPISODES.glob("*.md"), reverse=True):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", path.stem):
            continue
        text = path.read_text(encoding="utf-8")
        fm = parse_front_matter(text)
        audio_path = AUDIO / f"{path.stem}.mp3"

        if not audio_path.exists():
            print(f"  · {path.stem}: sem áudio ainda — fora do feed.")
            continue

        secs = mp3_duration_seconds(audio_path) or duration_from_mmss(
            fm.get("estimated_duration", "")
        )
        topics = [t.get("title", "") for t in fm.get("topics", [])
                  if isinstance(t, dict)]

        eps.append({
            "date": fm.get("date", path.stem),
            "title": fm.get("title") or f"Briefing de {path.stem}",
            "topics": topics,
            "audio_path": audio_path,
            "size": audio_path.stat().st_size,
            "duration": secs,
        })
    return eps


def build_feed(show: dict, eps: list[dict]) -> str:
    base = show["base_url"].rstrip("/")
    now = format_datetime(datetime.now(timezone.utc))

    items = []
    for ep in eps:
        pub = datetime.strptime(ep["date"], "%Y-%m-%d").replace(
            hour=6, tzinfo=timezone.utc)
        summary = (
            "Pautas de hoje: " + "; ".join(ep["topics"]) + "."
            if ep["topics"] else show["subtitle"]
        )
        dur = f"    <itunes:duration>{hhmmss(ep['duration'])}</itunes:duration>\n" if ep["duration"] else ""
        url = f"{base}/audio/{ep['audio_path'].name}"
        items.append(
            "  <item>\n"
            f"    <title>{escape(ep['title'])}</title>\n"
            f"    <description>{escape(summary)}</description>\n"
            f"    <itunes:summary>{escape(summary)}</itunes:summary>\n"
            f"    <pubDate>{format_datetime(pub)}</pubDate>\n"
            f"    <guid isPermaLink=\"false\">campscast-{ep['date']}</guid>\n"
            f"    <enclosure url=\"{escape(url)}\" length=\"{ep['size']}\" type=\"audio/mpeg\"/>\n"
            f"{dur}"
            f"    <itunes:explicit>{'true' if show['explicit'] else 'false'}</itunes:explicit>\n"
            "  </item>"
        )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"\n'
        '     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"\n'
        '     xmlns:atom="http://www.w3.org/2005/Atom"\n'
        '     xmlns:content="http://purl.org/rss/1.0/modules/content/">\n'
        "<channel>\n"
        f"  <title>{escape(show['title'])}</title>\n"
        f"  <link>{escape(show['link'])}</link>\n"
        f"  <description>{escape(show['description'])}</description>\n"
        f"  <language>{escape(show['language'])}</language>\n"
        f"  <copyright>{escape(show['copyright'])}</copyright>\n"
        f"  <lastBuildDate>{now}</lastBuildDate>\n"
        f'  <atom:link href="{escape(base)}/feed.xml" rel="self" type="application/rss+xml"/>\n'
        # ttl: sugere ao agregador de quanto em quanto tempo repassar o feed.
        # Nem todos honram, mas quem honra passa a checar de hora em hora em vez
        # de usar o intervalo interno, que para feed pouco assinado é longo.
        f"  <ttl>60</ttl>\n"
        # WebSub: em vez de esperar o agregador voltar, o hub avisa que mudou.
        # Declarar o hub é metade; a outra é o ping, em notify_hub().
        f'  <atom:link rel="hub" href="{escape(WEBSUB_HUB)}"/>\n'
        f"  <itunes:author>{escape(show['author'])}</itunes:author>\n"
        f"  <itunes:subtitle>{escape(show['subtitle'])}</itunes:subtitle>\n"
        f"  <itunes:summary>{escape(show['description'])}</itunes:summary>\n"
        f"  <itunes:explicit>{'true' if show['explicit'] else 'false'}</itunes:explicit>\n"
        "  <itunes:owner>\n"
        f"    <itunes:name>{escape(show['author'])}</itunes:name>\n"
        f"    <itunes:email>{escape(show['email'])}</itunes:email>\n"
        "  </itunes:owner>\n"
        f'  <itunes:image href="{escape(show["cover_url"])}"/>\n'
        f'  <itunes:category text="{escape(show["category"])}">\n'
        f'    <itunes:category text="{escape(show["subcategory"])}"/>\n'
        "  </itunes:category>\n"
        + "\n".join(items) + "\n"
        "</channel>\n</rss>\n"
    )


def upload(date: str, show: dict) -> bool:
    sys.path.insert(0, str(ROOT / "scripts"))
    from s3 import S3Error, load_credentials, put_object

    bucket = os.environ.get("S3_BUCKET", "").strip()
    if not bucket:
        print("S3_BUCKET não definido — upload pulado (feed gerado localmente).")
        return False

    try:
        creds = load_credentials()
    except S3Error as e:
        print(f"Upload pulado: {e}")
        return False

    prefix = os.environ.get("S3_PREFIX", "").strip("/")
    region = os.environ.get("AWS_REGION", "us-east-1")

    # base_url e S3_PREFIX têm de descrever o mesmo lugar. Se divergirem, o
    # upload funciona e o feed fica apontando para objetos que não existem —
    # falha silenciosa que só aparece no app do ouvinte.
    base = show["base_url"].rstrip("/")
    if prefix and not base.endswith(f"/{prefix}"):
        print(f"ERRO: S3_PREFIX é '{prefix}', mas base_url termina em "
              f"'{base.rsplit('/', 1)[-1]}'. O feed apontaria para o lugar errado.",
              file=sys.stderr)
        return False
    if not prefix and bucket not in base:
        print(f"AVISO: base_url ({base}) não menciona o bucket '{bucket}'. "
              "Só faz sentido se houver CloudFront ou domínio próprio na frente.")

    def key_for(name: str) -> str:
        return f"{prefix}/{name}" if prefix else name

    # O áudio sobe antes do feed: um feed que aponta para um MP3 inexistente
    # deixa o app de podcast com erro na tela do ouvinte.
    jobs = []
    audio_file = AUDIO / f"{date}.mp3"
    if audio_file.exists():
        jobs.append((audio_file, key_for(f"audio/{audio_file.name}"),
                     "audio/mpeg", "max-age=31536000"))
    else:
        print(f"AVISO: {audio_file.name} não existe — subindo só o feed.")
    jobs.append((FEED_OUT, key_for("feed.xml"),
                 "application/rss+xml", "max-age=300"))

    for path, key, ctype, cache in jobs:
        size = path.stat().st_size
        print(f"  → s3://{bucket}/{key}  ({size / 1_000_000:.2f} MB)")
        try:
            put_object(bucket, key, path.read_bytes(), ctype,
                       region=region, cache_control=cache, creds=creds)
        except S3Error as e:
            print(f"ERRO: {e}", file=sys.stderr)
            return False

    feed_url = f"{show['base_url'].rstrip('/')}/feed.xml"
    print(f"Feed publicado: {feed_url}")
    notify_hub(feed_url)
    return True


def notify_hub(feed_url: str) -> None:
    """Avisa o hub WebSub que o feed mudou. Best-effort: nunca derruba o pipeline.

    Agregadores que assinam o hub recebem o aviso na hora, em vez de descobrir
    na próxima varredura — que, para um feed com poucos assinantes, pode levar
    horas. Quem não usa WebSub simplesmente ignora, e nada muda.
    """
    import urllib.parse
    dados = urllib.parse.urlencode({
        "hub.mode": "publish",
        "hub.url": feed_url,
    }).encode("ascii")
    req = urllib.request.Request(
        WEBSUB_HUB, data=dados,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            print(f"WebSub: hub avisado (HTTP {resp.status}).")
    except urllib.error.HTTPError as e:
        print(f"WebSub: hub respondeu HTTP {e.code} — seguindo mesmo assim.")
    except Exception as e:
        print(f"WebSub: não consegui avisar o hub ({e}) — seguindo mesmo assim.")


def main() -> int:
    ap = argparse.ArgumentParser(description="Gera e publica o feed do CampsCast.")
    ap.add_argument("--date", help="data do episódio a subir (YYYY-MM-DD)")
    ap.add_argument("--no-upload", action="store_true", help="apenas gera feed/feed.xml")
    ap.add_argument("--rebuild", action="store_true", help="refaz o feed sem subir nada")
    args = ap.parse_args()

    load_env()
    show = load_show()

    print("Coletando episódios…")
    eps = collect_episodes()
    if not eps:
        print("Nenhum episódio com áudio. Feed não gerado.")
        return 0

    FEED_OUT.parent.mkdir(parents=True, exist_ok=True)
    FEED_OUT.write_text(build_feed(show, eps), encoding="utf-8")
    print(f"feed.xml gerado com {len(eps)} episódio(s): {FEED_OUT.relative_to(ROOT)}")

    if show["base_url"].startswith("https://exemplo.invalid"):
        print("AVISO: config/show.json ainda usa a base_url de exemplo — "
              "as URLs do feed não vão resolver.")

    if args.rebuild or args.no_upload:
        return 0
    if not args.date:
        print("Sem --date: feed gerado, upload pulado.")
        return 0

    upload(args.date, show)
    return 0


if __name__ == "__main__":
    sys.exit(main())
