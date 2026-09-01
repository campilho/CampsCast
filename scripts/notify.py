#!/usr/bin/env python3
"""
CampsCast — notificação de episódio publicado.

Manda um e-mail curto via SMTP. Se SMTP não estiver configurado, cai para a
notificação nativa do macOS (osascript) e, no pior caso, só imprime no log.
Nunca derruba o pipeline: falha de notificação sai com rc=0.

Uso:
    python3 scripts/notify.py --date 2026-08-24 \
        --script episodes/2026-08-24.md --audio audio/2026-08-24.mp3
"""
from __future__ import annotations

import argparse
import os
import pathlib
import smtplib
import subprocess
import sys
from email.message import EmailMessage

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def load_env() -> None:
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def build_body(date: str, script: pathlib.Path, audio: pathlib.Path) -> tuple[str, str]:
    from publish import mp3_duration_seconds, hhmmss, parse_front_matter

    title = f"Briefing de {date}"
    topics: list[str] = []
    if script.exists():
        fm = parse_front_matter(script.read_text(encoding="utf-8"))
        title = fm.get("title", title)
        topics = [t.get("title", "") for t in fm.get("topics", []) if isinstance(t, dict)]

    if audio.exists():
        secs = mp3_duration_seconds(audio)
        dur = hhmmss(secs) if secs else "duração desconhecida"
        size = f"{audio.stat().st_size / 1_000_000:.1f} MB"
    else:
        dur, size = "sem áudio", "—"

    subject = f"CampsCast {date} publicado ({dur})"
    lines = [title, "", f"Duração: {dur}   Tamanho: {size}", ""]
    if topics:
        lines.append("Pautas:")
        lines += [f"  {i}. {t}" for i, t in enumerate(topics, 1)]
        lines.append("")
    lines.append(f"Roteiro: {script}")
    return subject, "\n".join(lines)


def send_smtp(subject: str, body: str) -> bool:
    host = os.environ.get("SMTP_HOST", "").strip()
    to = os.environ.get("NOTIFY_TO", "").strip()
    user = os.environ.get("SMTP_USER", "").strip()
    password = os.environ.get("SMTP_PASS", "").strip()
    if not (host and to and user and password):
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ.get("NOTIFY_FROM", user)
    msg["To"] = to
    msg.set_content(body)

    port = int(os.environ.get("SMTP_PORT", "587"))
    with smtplib.SMTP(host, port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(msg)
    print(f"E-mail enviado para {to}.")
    return True


def send_macos(subject: str) -> bool:
    if sys.platform != "darwin":
        return False
    script = f'display notification "{subject}" with title "CampsCast"'
    return subprocess.run(["osascript", "-e", script]).returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Notifica que o episódio saiu.")
    ap.add_argument("--date", required=True)
    ap.add_argument("--script", required=True)
    ap.add_argument("--audio", required=True)
    args = ap.parse_args()

    load_env()
    subject, body = build_body(
        args.date, ROOT / args.script, ROOT / args.audio
    )
    print(subject)
    print(body)

    try:
        if send_smtp(subject, body):
            return 0
    except Exception as e:                      # notificação nunca derruba o pipeline
        print(f"AVISO: envio SMTP falhou ({e}).", file=sys.stderr)

    if send_macos(subject):
        print("Notificação nativa do macOS enviada.")
    else:
        print("Nenhum canal de notificação configurado — só o log.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
