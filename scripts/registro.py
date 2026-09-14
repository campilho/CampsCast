#!/usr/bin/env python3
"""
CampsCast — registro diário de execução e custo.

Uma linha JSON por execução do pipeline em `metricas/execucoes.jsonl`: quando
começou e terminou, quanto durou cada etapa, se o Mac dormiu no meio, quantos
tokens o Claude usou e quantos créditos a ElevenLabs cobrou. Guarda unidades
brutas, não dinheiro: preço muda, token não. É a matéria-prima do relatório de
FinOps da Fase 3.

Também anota o tamanho do que o agente lê de memória a cada execução — índice
de pautas, backlog, roteiros anteriores —, para que um custo que sobe possa ser
posto ao lado do que está crescendo.

    python3 scripts/registro.py mostra                 # últimas execuções
    python3 scripts/registro.py reconstroi             # histórico, a partir dos logs
    python3 scripts/registro.py fecha ...              # chamado pelo run_episode.sh
    python3 scripts/registro.py indicadores --data D   # tamanho da memória do agente
    python3 scripts/registro.py resultado ARQ.json     # texto final do agente

O destino pode ser trocado por METRICAS_ARQ — é o que o smoke test faz, para
nunca escrever no registro real.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import platform
import re
import subprocess
import sys
import time

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PADRAO = RAIZ / "metricas" / "execucoes.jsonl"
TRANSCRICOES = pathlib.Path.home() / ".claude" / "projects"
_DATA = re.compile(r"\d{4}-\d{2}-\d{2}")


def arquivo() -> pathlib.Path:
    return pathlib.Path(os.environ.get("METRICAS_ARQ") or PADRAO)


def registra(linha: dict, destino: pathlib.Path | None = None) -> None:
    destino = destino or arquivo()
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("a", encoding="utf-8") as f:
        f.write(json.dumps(linha, ensure_ascii=False) + "\n")


def le(destino: pathlib.Path | None = None) -> list[dict]:
    destino = destino or arquivo()
    if not destino.exists():
        return []
    linhas = []
    for l in destino.read_text(encoding="utf-8").splitlines():
        if l.strip():
            try:
                linhas.append(json.loads(l))
            except json.JSONDecodeError:
                pass
    return linhas


def _json(caminho) -> dict | None:
    try:
        d = json.loads(pathlib.Path(caminho).read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else None
    except Exception:
        return None


def _recente(caminho, desde: float) -> bool:
    p = pathlib.Path(caminho) if caminho else None
    return bool(p and p.exists() and p.stat().st_mtime >= desde - 5)


# ------------------------------------------------------------- indicadores
def indicadores(data: str, raiz: pathlib.Path = RAIZ) -> dict:
    """Tamanho do que o agente lê de memória antes de pesquisar."""
    indice = raiz / "covered-index.json"
    itens = None
    try:
        d = json.loads(indice.read_text(encoding="utf-8"))
        lista = d.get("items") if isinstance(d, dict) else d
        itens = len(lista) if isinstance(lista, list) else None
    except Exception:
        pass
    anteriores = sorted(p for p in (raiz / "episodes").glob("*.md")
                        if _DATA.fullmatch(p.stem) and p.stem < data)[-5:]
    tamanho = lambda p: p.stat().st_size if p.exists() else None
    return {
        "indice_pautas_bytes": tamanho(indice),
        "indice_pautas_itens": itens,
        "backlog_bytes": tamanho(raiz / "saved-items" / "backlog.md"),
        "roteiros_lidos_bytes": sum(p.stat().st_size for p in anteriores),
        "prompt_bytes": tamanho(raiz / "prompts" / "master.md"),
    }


# -------------------------------------------------------------------- sono
def calcula_sono(texto: str, inicio: dt.datetime, fim: dt.datetime) -> dict | None:
    """Tempo que o Mac passou sem estar plenamente acordado, pelo `pmset -g log`.

    Parado é só o trecho entre "Entering Sleep" e o próximo despertar. Duas
    leituras erradas vieram antes desta, ambas desmentidas pelos próprios dados:
    - "Wake Requests" é um pedido de despertar agendado, não um despertar.
      Tratado como despertar, as falhas de 10 e 11/09 apareciam com 3 s de sono.
    - "DarkWake" é o sistema acordado com a tela apagada, e processos rodam. O
      caffeinate segura o Mac nesse estado — mas `-s` só vale na tomada. Contado
      como sono, o episódio de 09/09 aparecia dormindo a execução inteira e,
      mesmo assim, concluído com 68 chamadas ao modelo.
    A execução de 10/09 começou num DarkWake de manutenção e voltou a dormir dois
    segundos depois: o launchd aproveitou a janela para rodar o que tinha perdido.

    Devolve None quando o log não alcança o início — sem isso, "não dormiu" e
    "não há registro" ficariam iguais.
    """
    rx = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) [+-]\d{4}\s+(\S+)\s+(.*)$")
    eventos, primeiro = [], None
    for l in texto.splitlines():
        m = rx.match(l)
        if not m:
            continue
        tipo, resto = m[2], m[3].strip()
        if tipo == "Sleep" and resto.startswith("Entering Sleep"):
            novo = "dormindo"
        elif tipo == "DarkWake" or (tipo == "Wake" and resto.startswith("Wake from")):
            novo = "acordado"
        else:
            continue
        t = dt.datetime.strptime(m[1], "%Y-%m-%d %H:%M:%S")
        primeiro = primeiro or t
        if t <= fim:
            eventos.append((t, novo))
    if primeiro is None or primeiro > inicio:
        return None
    estado, desde, total, vezes = "acordado", None, 0.0, 0
    for t, novo in eventos:
        if novo == "dormindo" and estado == "acordado":
            estado, desde = "dormindo", t
        elif novo == "acordado" and estado == "dormindo":
            a, b = max(desde, inicio), min(t, fim)
            if b > a:
                total += (b - a).total_seconds()
                vezes += 1
            estado, desde = "acordado", None
    if estado == "dormindo" and fim > max(desde, inicio):
        total += (fim - max(desde, inicio)).total_seconds()
        vezes += 1
    return {"vezes": vezes, "segundos": int(total)}


def sono(inicio: dt.datetime, fim: dt.datetime) -> dict | None:
    if platform.system() != "Darwin" or os.environ.get("REGISTRO_SEM_SONO"):
        return None
    try:
        saida = subprocess.run(["pmset", "-g", "log"], capture_output=True,
                               text=True, timeout=60).stdout
    except Exception:
        return None
    return calcula_sono(saida, inicio, fim)


# ------------------------------------------------------------------ claude
def contagem_transcricao(caminho: pathlib.Path) -> dict | None:
    """Chamadas, tokens e ferramentas lidos da transcrição da sessão."""
    ids, ferramentas = set(), {}
    tot = {"entrada": 0, "cache_escrito": 0, "cache_lido": 0, "saida": 0}
    try:
        linhas = caminho.read_text(errors="ignore").splitlines()
    except Exception:
        return None
    for l in linhas:
        try:
            m = json.loads(l).get("message") or {}
        except Exception:
            continue
        if not isinstance(m, dict) or m.get("model") == "<synthetic>":
            continue
        for c in m.get("content") or []:
            if isinstance(c, dict) and c.get("type") == "tool_use":
                ferramentas[c.get("name")] = ferramentas.get(c.get("name"), 0) + 1
        u, mid = m.get("usage"), m.get("id")
        if u and mid and mid not in ids:
            ids.add(mid)
            tot["entrada"] += u.get("input_tokens", 0)
            tot["cache_escrito"] += u.get("cache_creation_input_tokens", 0)
            tot["cache_lido"] += u.get("cache_read_input_tokens", 0)
            tot["saida"] += u.get("output_tokens", 0)
    if not ids:
        return None
    return {"chamadas": len(ids), **tot,
            "buscas": ferramentas.get("WebSearch", 0),
            "leituras": ferramentas.get("WebFetch", 0)}


def resumo_claude(dados: dict | None, modelo: str | None) -> dict | None:
    """Totais do JSON final do `claude -p --output-format json`."""
    if not isinstance(dados, dict) or "usage" not in dados:
        return None
    u = dados.get("usage") or {}
    servidor = u.get("server_tool_use") or {}
    por_modelo = dados.get("modelUsage") or {}
    if por_modelo:
        soma = lambda k: sum((v or {}).get(k, 0) for v in por_modelo.values())
        tokens = {"entrada": soma("inputTokens"), "cache_escrito": soma("cacheCreationInputTokens"),
                  "cache_lido": soma("cacheReadInputTokens"), "saida": soma("outputTokens")}
    else:
        tokens = {"entrada": u.get("input_tokens"), "cache_escrito": u.get("cache_creation_input_tokens"),
                  "cache_lido": u.get("cache_read_input_tokens"), "saida": u.get("output_tokens")}
    return {
        "modelo": modelo or next(iter(por_modelo), None),
        "turnos": dados.get("num_turns"),
        **tokens,
        "buscas_servidor": servidor.get("web_search_requests"),
        "custo_estimado_usd": dados.get("total_cost_usd"),
        "duracao_api_s": round((dados.get("duration_api_ms") or 0) / 1000) or None,
        "com_erro": bool(dados.get("is_error")),
        "sessao": dados.get("session_id"),
    }


def _transcricao_da_sessao(sessao: str | None) -> pathlib.Path | None:
    if not sessao:
        return None
    return next(iter(TRANSCRICOES.glob(f"*/{sessao}.jsonl")), None)


# ---------------------------------------------------------------- episódio
def episodio(data: str, raiz: pathlib.Path = RAIZ) -> dict | None:
    roteiro = raiz / "episodes" / f"{data}.md"
    if not roteiro.exists():
        return None
    m = re.match(r"\A---\n(.*?)\n---\n", roteiro.read_text(encoding="utf-8"), re.S)
    campo = lambda k: (re.search(rf"^{k}:\s*(\d+)\s*$", m.group(1), re.M) if m else None)
    numero, palavras = campo("episode"), campo("words")
    audio = raiz / "audio" / f"{data}.mp3"
    duracao = None
    if audio.exists():
        try:
            sys.path.insert(0, str(raiz / "scripts"))
            from publish import mp3_duration_seconds
            duracao = round(mp3_duration_seconds(audio) or 0) or None
        except Exception:
            pass
    return {"numero": int(numero[1]) if numero else None,
            "palavras": int(palavras[1]) if palavras else None,
            "audio_s": duracao}


def _etapas(marcos: list[tuple[str, float | None]], fim: float) -> dict:
    presentes = [(n, t) for n, t in marcos if t]
    saida = {}
    for i, (nome, t) in enumerate(presentes):
        proximo = presentes[i + 1][1] if i + 1 < len(presentes) else fim
        saida[nome] = int(proximo - t)
    return saida


# --------------------------------------------------------------- comandos
def cmd_fecha(a) -> int:
    inicio = float(a.inicio)
    fim = float(a.fim) if a.fim else time.time()
    num = lambda v: float(v) if v not in (None, "") else None
    marcos = [("pesquisa", num(a.pesquisa)), ("narracao", num(a.narracao)),
              ("publicacao", num(a.publicacao)), ("aviso", num(a.aviso))]
    agente = _json(a.agente) if _recente(a.agente, inicio) else None
    claude = resumo_claude(agente, a.modelo or None)
    transcricao = None
    if claude and (arq := _transcricao_da_sessao(claude.get("sessao"))):
        transcricao = contagem_transcricao(arq)
    tts = _json(a.tts) if _recente(a.tts, inicio) else None
    ind = _json(a.indicadores) if _recente(a.indicadores, inicio) else None
    di, df = dt.datetime.fromtimestamp(inicio), dt.datetime.fromtimestamp(fim)
    linha = {
        "data": a.data,
        "origem": "registrado",
        "estado": a.estado,
        "inicio": di.isoformat(timespec="seconds"),
        "fim": df.isoformat(timespec="seconds"),
        "duracao_s": int(fim - inicio),
        "etapas_s": _etapas(marcos, fim),
        "mac_dormiu": sono(di, df),
        "claude": claude,
        "claude_transcricao": transcricao,
        "elevenlabs": tts,
        "episodio": episodio(a.data),
        "indicadores": ind,
        "erro": a.erro or None,
    }
    registra(linha)
    print(f"Registro: {a.estado}, {linha['duracao_s']} s → {arquivo()}")
    return 0


def cmd_resultado(a) -> int:
    d = _json(a.arquivo)
    if d is None or "result" not in d:
        return 3                                   # não é JSON do claude -p
    print(d.get("result") or "")
    return 4 if d.get("is_error") else 0


def cmd_indicadores(a) -> int:
    print(json.dumps(indicadores(a.data), ensure_ascii=False))
    return 0


def cmd_reconstroi(a) -> int:
    """Uma vez: execuções anteriores ao registro, a partir de logs e transcrições.

    Os créditos da ElevenLabs saem da linha "Custo:" do log, que antes era
    estimada pelo contador de cota — por isso ficam marcados como não exatos.
    """
    marca = re.compile(r"^\[(\d{2}):(\d{2}):(\d{2})\] (.*)$")
    execucoes = []
    for f in sorted((RAIZ / "logs").glob("20??-??-??.log")):
        dia, atual = dt.date.fromisoformat(f.stem), None
        for l in f.read_text(errors="ignore").splitlines():
            m = marca.match(l)
            if not m:
                c = re.match(r"^Custo: (\d+) créditos", l.strip())
                if c and atual:
                    atual["creditos"] = int(c[1])
                continue
            h = dt.datetime.combine(dia, dt.time(int(m[1]), int(m[2]), int(m[3])))
            msg = m[4]
            if msg.startswith("════ CampsCast — episódio"):
                atual = {"data": f.stem, "inicio": h, "marcos": {}, "estado": None}
                execucoes.append(atual)
            elif atual is None:
                continue
            elif msg.startswith("── [") and "PULADA" not in msg:
                atual["marcos"][msg[4]] = h
            elif "MODO DRY-RUN" in msg or msg.startswith("Nada a fazer") or "sem episódio" in msg:
                atual["estado"] = "ignorar"
            elif msg.startswith("ERRO") and atual["estado"] is None:
                atual["estado"], atual["fim"], atual["erro"] = "falhou", h, msg[6:]
            elif "Concluído" in msg and atual["estado"] is None:
                atual["estado"], atual["fim"] = "ok", h
    sessoes = []
    for f in TRANSCRICOES.glob("*/*.jsonl"):
        if f.stat().st_size > 3_000_000:
            continue
        txt = f.read_text(errors="ignore")
        if "produtor e roteirista do CampsCast" not in txt:
            continue
        ts = []
        for l in txt.splitlines():
            try:
                t = json.loads(l).get("timestamp")
            except Exception:
                continue
            if t:
                ts.append(dt.datetime.fromisoformat(t.replace("Z", "+00:00")).astimezone().replace(tzinfo=None))
        if ts:
            sessoes.append((min(ts), f))
    ja = {(l.get("data"), l.get("inicio")) for l in le()}
    novas = 0
    for e in execucoes:
        if e["estado"] not in ("ok", "falhou") or not e["marcos"]:
            continue
        inicio = e["inicio"].isoformat(timespec="seconds")
        if (e["data"], inicio) in ja:
            continue
        fim = e["fim"]
        ordem = [("pesquisa", "1"), ("narracao", "2"), ("publicacao", "3"), ("aviso", "4")]
        marcos = [(n, e["marcos"][k].timestamp() if k in e["marcos"] else None) for n, k in ordem]
        pesquisa = e["marcos"].get("1")
        transcricao = None
        if pesquisa:
            arq = next((f for t, f in sessoes if abs((t - pesquisa).total_seconds()) < 240), None)
            transcricao = contagem_transcricao(arq) if arq else None
        registra({
            "data": e["data"],
            "origem": "reconstruido",
            "estado": e["estado"],
            "inicio": inicio,
            "fim": fim.isoformat(timespec="seconds"),
            "duracao_s": int((fim - e["inicio"]).total_seconds()),
            "etapas_s": _etapas(marcos, fim.timestamp()),
            "mac_dormiu": sono(e["inicio"], fim),
            "claude": None,
            "claude_transcricao": transcricao,
            "elevenlabs": ({"creditos": e["creditos"], "creditos_exatos": False}
                           if e.get("creditos") else None),
            "episodio": episodio(e["data"]) if e["estado"] == "ok" else None,
            "indicadores": None,
            "erro": e.get("erro"),
        })
        novas += 1
    print(f"{novas} execução(ões) reconstruída(s) → {arquivo()}")
    return 0


def cmd_mostra(a) -> int:
    linhas = le()[-a.ultimas:]
    if not linhas:
        print(f"Sem registros em {arquivo()}")
        return 0
    mmss = lambda s: f"{int(s) // 60}:{int(s) % 60:02d}" if s is not None else "—"
    print(f"{'data':11}{'estado':8}{'total':>7}{'pesquisa':>9}{'narração':>9}{'dormiu':>8}"
          f"{'chamadas':>9}{'cache lido':>12}{'saída':>8}{'créditos':>9}{'US$ est.':>9}{'índice':>8}")
    for l in linhas:
        et, tr, cl = l.get("etapas_s") or {}, l.get("claude_transcricao") or {}, l.get("claude") or {}
        el, ind, so = l.get("elevenlabs") or {}, l.get("indicadores") or {}, l.get("mac_dormiu")
        cred = el.get("creditos")
        cred_txt = (f"{cred}" + ("" if el.get("creditos_exatos") else "~")) if cred else "—"
        usd = cl.get("custo_estimado_usd")
        print(f"{l['data']:11}{l['estado']:8}{mmss(l.get('duracao_s')):>7}{mmss(et.get('pesquisa')):>9}"
              f"{mmss(et.get('narracao')):>9}{(mmss(so['segundos']) if so else '?'):>8}"
              f"{tr.get('chamadas', '—'):>9}{(f'{tr[chr(99)+chr(97)+chr(99)+chr(104)+chr(101)+chr(95)+chr(108)+chr(105)+chr(100)+chr(111)]:,}' if tr.get('cache_lido') is not None else '—'):>12}"
              f"{(f'{tr[chr(115)+chr(97)+chr(105)+chr(100)+chr(97)]:,}' if tr.get('saida') is not None else '—'):>8}"
              f"{cred_txt:>9}{(f'{usd:.2f}' if isinstance(usd, (int, float)) and usd else '—'):>9}"
              f"{(str(round(ind['indice_pautas_bytes'] / 1024)) + ' KB' if ind.get('indice_pautas_bytes') else '—'):>8}")
    print("\n~ créditos estimados pelo contador de cota, anteriores ao registro exato")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fecha")
    for campo in ("data", "estado", "inicio"):
        f.add_argument(f"--{campo}", required=True)
    for campo in ("fim", "pesquisa", "narracao", "publicacao", "aviso",
                  "agente", "tts", "indicadores", "modelo", "erro"):
        f.add_argument(f"--{campo}", default="")
    r = sub.add_parser("resultado"); r.add_argument("arquivo")
    i = sub.add_parser("indicadores"); i.add_argument("--data", required=True)
    sub.add_parser("reconstroi")
    m = sub.add_parser("mostra"); m.add_argument("--ultimas", type=int, default=15)
    a = ap.parse_args()
    return {"fecha": cmd_fecha, "resultado": cmd_resultado, "indicadores": cmd_indicadores,
            "reconstroi": cmd_reconstroi, "mostra": cmd_mostra}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
