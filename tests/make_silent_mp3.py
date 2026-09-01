#!/usr/bin/env python3
"""Gera um MP3 silencioso válido (MPEG1 Layer III, 128 kbps, 44.1 kHz).

Serve para o smoke test exercitar publish.py sem chamar a ElevenLabs.
"""
import pathlib
import sys

FRAME_LEN = 144 * 128_000 // 44_100          # 417 bytes
FRAME_SECS = 1152 / 44_100                    # ~26,12 ms
HEADER = bytes([0xFF, 0xFB, 0x90, 0x00])      # MPEG1 L3 128k 44.1k, sem padding


def make(seconds: float) -> bytes:
    frames = int(seconds / FRAME_SECS)
    body = HEADER + b"\x00" * (FRAME_LEN - 4)
    return body * frames


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1])
    secs = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(make(secs))
    print(f"{out} — {out.stat().st_size} bytes, ~{secs:.0f}s")
