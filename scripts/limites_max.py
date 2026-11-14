#!/usr/bin/env python3
"""Quanto do limite do plano Max está usado agora: a janela de 5 horas e a
semana. O orquestrador lê antes e depois do agente, e a diferença é o que o
episódio gastou do Max (docs/custos.md).

Não há leitura oficial fora do app. O Claude CLI, com --output-format
stream-json, manda um evento rate_limit_event com a utilização das duas janelas
a cada chamada; uma chamada mínima ao Haiku, sem ferramentas e sem gravar
sessão, basta para ler. Ela mesma gasta uma fração desprezível do limite.

Uso:
    limites_max.py           # imprime um JSON com a leitura; nunca falha
    limites_max.py --prazo 60
    limites_max.py --resumo ANTES.json DEPOIS.json   # uma linha para o log

Saída: {"lido_em", "cinco_horas", "semana", "reset_cinco_horas",
"reset_semana", "status"} com utilização de 0 a 1, ou {"lido_em", "erro"}.
Sem assinatura (chave de API no ambiente), o CLI não manda o evento, e a saída
diz isso. Código de saída 0 sempre: medir não pode derrubar o episódio.
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile

FUSO = dt.timezone(dt.timedelta(hours=-3))


def agora() -> str:
    return dt.datetime.now(FUSO).isoformat(timespec="seconds")


def quando(ts) -> str | None:
    try:
        return dt.datetime.fromtimestamp(float(ts), FUSO).isoformat(timespec="minutes")
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def interpreta(linhas) -> dict | None:
    """O último rate_limit_event da saída, em português; None se não houver."""
    leitura = None
    for linha in linhas:
        try:
            d = json.loads(linha)
        except ValueError:
            continue
        if not isinstance(d, dict) or d.get("type") != "rate_limit_event":
            continue
        info = d.get("rate_limit_info") or {}
        janelas = info.get("unifiedWindows") or {}
        cinco, semana = janelas.get("five_hour") or {}, janelas.get("seven_day") or {}
        if "utilization" not in cinco and "utilization" not in semana:
            continue
        leitura = {
            "cinco_horas": cinco.get("utilization"),
            "semana": semana.get("utilization"),
            "reset_cinco_horas": quando(cinco.get("resetsAt")),
            "reset_semana": quando(semana.get("resetsAt")),
            "status": info.get("status"),
        }
    return leitura


def le(prazo: float) -> dict:
    claude = os.environ.get("CLAUDE_BIN") or "claude"
    cmd = [claude, "-p", "responda só: ok", "--model", "claude-haiku-4-5",
           "--output-format", "stream-json", "--verbose", "--tools", "",
           "--no-session-persistence", "--strict-mcp-config", "--disable-slash-commands"]
    # Fora da pasta do projeto: a leitura não pode cair entre as transcrições
    # que o watch_agent.py e o registro procuram.
    with tempfile.TemporaryDirectory() as pasta:
        try:
            r = subprocess.run(cmd, cwd=pasta, capture_output=True, text=True, timeout=prazo)
        except FileNotFoundError:
            return {"lido_em": agora(), "erro": f"{claude} não encontrado"}
        except subprocess.TimeoutExpired:
            return {"lido_em": agora(), "erro": f"sem resposta em {prazo:.0f} s"}
    leitura = interpreta(r.stdout.splitlines())
    if leitura is None:
        motivo = "o CLI não mandou a utilização"
        if os.environ.get("ANTHROPIC_API_KEY"):
            motivo += " (há ANTHROPIC_API_KEY no ambiente: o CLI cobra na API, sem limite do Max)"
        elif r.returncode != 0:
            motivo += f" (rc={r.returncode})"
        return {"lido_em": agora(), "erro": motivo}
    return {"lido_em": agora(), **leitura}


def delta(antes: dict | None, depois: dict | None) -> dict:
    """Pontos percentuais gastos em cada janela entre duas leituras. None quando
    falta leitura; "reiniciou" quando a janela virou no meio (a conta não vale)."""
    saida = {}
    for chave, reset in (("cinco_horas", "reset_cinco_horas"), ("semana", "reset_semana")):
        a, d = (antes or {}).get(chave), (depois or {}).get(chave)
        if not isinstance(a, (int, float)) or not isinstance(d, (int, float)):
            saida[chave] = None
        elif (antes or {}).get(reset) != (depois or {}).get(reset):
            saida[chave] = "reiniciou"
        else:
            saida[chave] = round((d - a) * 100)
    return saida


def resumo(antes: dict | None, depois: dict | None) -> str:
    """Uma linha para o log: "Max: 5 h 9% → 12% (+3) · semana 18% → 20% (+2)"."""
    if not depois or "erro" in depois or not antes or "erro" in antes:
        erro = (depois or {}).get("erro") or (antes or {}).get("erro") or "sem leitura"
        return f"Max: sem leitura ({erro})"
    d = delta(antes, depois)
    pct = lambda v: f"{round(v * 100)}%" if isinstance(v, (int, float)) else "?"
    partes = []
    for nome, chave in (("5 h", "cinco_horas"), ("semana", "semana")):
        dv = d[chave]
        txt = "janela reiniciou" if dv == "reiniciou" else (f"{dv:+d}" if dv is not None else "?")
        partes.append(f"{nome} {pct(antes.get(chave))} → {pct(depois.get(chave))} ({txt})")
    return "Max: " + " · ".join(partes)


def _carrega(caminho: str) -> dict | None:
    try:
        d = json.loads(open(caminho, encoding="utf-8").read())
        return d if isinstance(d, dict) else None
    except (OSError, ValueError):
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--prazo", type=float, default=60)
    ap.add_argument("--resumo", nargs=2, metavar=("ANTES", "DEPOIS"),
                    help="não lê: compara duas leituras gravadas e imprime uma linha")
    a = ap.parse_args()
    if a.resumo:
        print(resumo(_carrega(a.resumo[0]), _carrega(a.resumo[1])))
        return 0
    try:
        print(json.dumps(le(a.prazo), ensure_ascii=False))
    except Exception as e:  # medir nunca derruba o episódio
        print(json.dumps({"lido_em": agora(), "erro": f"{type(e).__name__}: {e}"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
