#!/usr/bin/env python3
"""
CampsCast — o Divulgador: a pauta do post da semana no LinkedIn.

O que travava a divulgação era o tempo do autor, não o texto: um post pronto
ficou cinco terças sem sair. Então o agente não escreve o post nem publica.
Ele entrega, no sábado, uma pauta: a história, os fatos com arquivo e linha, e
um rascunho de partida. O autor escreve a versão dele no domingo e agenda no
próprio LinkedIn. Na hora do post, o script lembra do primeiro comentário, que
o agendamento do LinkedIn não agenda.

Três etapas, cada uma roda sozinha:

    pauta     o agente (prompts/divulgador.md) escreve privado/divulgacao/AAAA-Www.md
    confere   sem modelo: cada fato citado está na linha da fonte, cada
              algarismo do rascunho está na tabela, e não há link no corpo
    entrega   manda a pauta ao autor (e-mail; sem SMTP, a notificação do macOS)

Uso:
    divulga.py                        # a semana que acabou, as três etapas
    divulga.py --only confere         # só uma etapa (ou várias, com vírgula)
    divulga.py --dry-run              # mostra o que faria, sem modelo e sem envio
    divulga.py --overwrite            # refaz a pauta de uma semana que já tem
    divulga.py --historia "..."       # o autor já escolheu a história
    divulga.py --lembrete             # no dia do post: o primeiro comentário
    divulga.py --marca agendado --minutos 25   # o autor agendou; quanto custou
    divulga.py --marca sem-post       # a semana ficou sem post
    divulga.py --mostra               # as semanas: saiu? quanto tempo?
    divulga.py --rotina               # o que o launchd chama: decide pelo dia

--data AAAA-MM-DD faz o script agir como se fosse esse dia; --semana AAAA-Www
escolhe a semana da pauta. A pauta fica em privado/ (fora do git); o registro,
sem número de audiência, em metricas/divulgacao.jsonl.

Sai com 1 se a conferência barrou a pauta. Ela é entregue assim mesmo, com as
ressalvas no alto: o autor vai reescrever, e é melhor saber do que não receber.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

# A ficha (config/agentes.json) repete estes três; a suíte confere.
MODELO = "claude-opus-5-5"
ESFORCO = "high"
FERRAMENTAS = ["Read", "Write", "Glob", "Grep"]

ETAPAS = ("pauta", "confere", "entrega")
SECOES = ("A história", "Por que agora", "Fatos", "Rascunho de partida", "Outras histórias")
FINAIS = ("entregue", "agendado", "sem-post")
FUSO = dt.timezone(dt.timedelta(hours=-3))
PRAZO_AGENTE_S = 30 * 60
DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


# ------------------------------------------------------------ onde ficam as coisas

def config() -> dict:
    return json.loads((ROOT / "config" / "divulgacao.json").read_text(encoding="utf-8"))


def pasta() -> pathlib.Path:
    p = pathlib.Path(os.environ.get("DIVULGACAO_DIR") or "privado/divulgacao")
    return p if p.is_absolute() else ROOT / p


def relativo(p: pathlib.Path) -> str:
    try:
        return str(p.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(p)


def registra(evento: str, semana: str, **campos) -> None:
    arq = pathlib.Path(os.environ.get("DIVULGACAO_ARQ") or ROOT / "metricas" / "divulgacao.jsonl")
    arq.parent.mkdir(parents=True, exist_ok=True)
    linha = {"quando": dt.datetime.now(FUSO).isoformat(timespec="seconds"),
             "semana": semana, "evento": evento, **campos}
    with arq.open("a", encoding="utf-8") as f:
        f.write(json.dumps(linha, ensure_ascii=False) + "\n")


# ------------------------------------------------------------------- a semana

def semana_da_pauta(d: dt.date) -> str:
    """A semana ISO que a pauta cobre: a que acabou. No sábado e no domingo
    ainda é a corrente; de segunda a sexta, a anterior."""
    ref = d if d.isoweekday() >= 6 else d - dt.timedelta(days=d.isoweekday())
    ano, sem, _ = ref.isocalendar()
    return f"{ano}-W{sem:02d}"


def limites(semana: str) -> tuple[dt.date, dt.date]:
    ano, sem = semana.split("-W")
    ini = dt.date.fromisocalendar(int(ano), int(sem), 1)
    return ini, ini + dt.timedelta(days=6)


def dia_do_post(semana: str, dia: int) -> dt.date:
    """O primeiro dia de post depois do domingo que fecha a semana."""
    fim = limites(semana)[1]
    return fim + dt.timedelta(days=(dia - fim.isoweekday()) % 7 or 7)


# -------------------------------------------------------------- o arquivo da pauta

def cabecalho(texto: str) -> tuple[dict, str]:
    m = re.match(r"---\n(.*?)\n---\n?", texto, re.S)
    if not m:
        return {}, texto
    campos = {}
    for l in m.group(1).splitlines():
        if ":" in l:
            k, v = l.split(":", 1)
            campos[k.strip()] = v.strip().strip('"')
    return campos, texto[m.end():]


def monta(campos: dict, corpo: str) -> str:
    linhas = []
    for k, v in campos.items():
        v = str(v)
        linhas.append(f'{k}: "{v.replace(chr(34), chr(39))}"' if k == "historia" else f"{k}: {v}")
    return "---\n" + "\n".join(linhas) + "\n---\n\n" + corpo.lstrip("\n")


def secoes(corpo: str) -> dict:
    partes = re.split(r"^## +(.+?)[ \t]*$", corpo, flags=re.M)
    return {partes[i].strip(): partes[i + 1].strip("\n") for i in range(1, len(partes), 2)}


def com_secao(corpo: str, titulo: str, texto: str) -> str:
    """O corpo com a seção trocada (ou acrescentada no fim)."""
    sem = re.sub(rf"^## +{re.escape(titulo)}[ \t]*\n.*?(?=^## |\Z)", "", corpo, flags=re.M | re.S)
    return sem.rstrip("\n") + f"\n\n## {titulo}\n\n{texto.strip()}\n"


def muda_estado(arq: pathlib.Path, **campos) -> dict:
    c, corpo = cabecalho(arq.read_text(encoding="utf-8"))
    c.update(campos)
    arq.write_text(monta(c, corpo), encoding="utf-8")
    return c


# ------------------------------------------------------------------ a conferência

NUMERO = re.compile(r"\d+(?:[.,\-]\d+)*")


def canonico(tok: str) -> str:
    """'5.693' e '5693' são o mesmo número; '7,9' e '7.9' também; e 'Opus 5.5'
    bate com 'claude-opus-5-5'."""
    t = re.sub(r"(?<=\d)\.(?=\d{3}(?!\d))", "", tok)
    t = re.sub(r"[,\-]", ".", t)
    return ".".join(str(int(p)) for p in t.split("."))


COLADO_EM_LETRA = re.compile(r"(?<=[^\W\d_])\d+(?:[.,\-]\d+)*")


def versoes_da_ficha() -> set[tuple[str, str]]:
    """(nome do agente em minúsculas, versão) de config/agentes.json."""
    try:
        ficha = json.loads((ROOT / "config" / "agentes.json").read_text(encoding="utf-8"))["agentes"]
    except (OSError, ValueError, KeyError):
        return set()
    return {(a.get("nome", k).lower(), h["versao"]) for k, a in ficha.items() for h in a.get("historico", [])}


def sem_nomes(texto: str) -> str:
    """O texto sem os algarismos que são nome, não quantidade: colado em letra
    ("V1", "W47", "H100") e agente com versão que existe na ficha ("Editor
    1.2"). Versão que a ficha não tem ("Editor 1.7") fica e é conferida."""
    sabidas = versoes_da_ficha()
    texto = re.sub(r"\b([^\W\d_]+)\s+(\d+\.\d+)\b",
                   lambda m: m.group(1) if (m.group(1).lower(), m.group(2)) in sabidas else m.group(0), texto)
    return COLADO_EM_LETRA.sub("", texto)


def numeros(texto: str) -> set[str]:
    return {canonico(m.group()) for m in NUMERO.finditer(sem_nomes(texto))}


def limpa(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().strip("\"“”`'").strip())


def le_fatos(tabela: str) -> tuple[list[dict], list[str]]:
    fatos, problemas = [], []
    for l in tabela.splitlines():
        l = l.strip()
        if not l.startswith("|"):
            continue
        cel = [c.strip() for c in l.strip("|").split("|")]
        if not cel[0].isdigit():
            continue                                  # o título e a régua da tabela
        if len(cel) != 5:
            problemas.append(f"fato {cel[0]}: a linha tem {len(cel)} colunas, e são 5 "
                             "(alguma célula tem barra vertical?)")
            continue
        fatos.append(dict(zip(("n", "afirmacao", "tipo", "fonte", "trecho"), cel)))
    return fatos, problemas


def confere_fato(f: dict) -> list[str]:
    n, tipo = f["n"], f["tipo"].lower().strip("` ")
    caminho, _, linha = f["fonte"].strip("` ").partition(":")
    alvo = (ROOT / caminho.strip()).resolve()
    if not alvo.is_relative_to(ROOT.resolve()) or not alvo.is_file():
        return [f"fato {n}: a fonte {caminho.strip() or '(vazia)'} não existe no repositório"]
    if tipo == "conta":
        return [] if limpa(f["trecho"]) else [f"fato {n}: conta sem dizer como contar"]
    if tipo != "citado":
        return [f"fato {n}: tipo '{f['tipo']}' — é citado ou conta"]
    if not linha.strip().isdigit():
        return [f"fato {n}: fato citado sem linha na fonte ({f['fonte']})"]
    linhas = alvo.read_text(encoding="utf-8", errors="replace").splitlines()
    i = int(linha)
    if not 1 <= i <= len(linhas):
        return [f"fato {n}: {caminho} tem {len(linhas)} linhas, e a fonte aponta a {i}"]
    trecho = limpa(f["trecho"])
    if len(trecho) < 3:
        return [f"fato {n}: trecho curto demais para conferir"]
    if trecho not in limpa(" ".join(linhas[max(0, i - 3):i + 2])):
        return [f"fato {n}: o trecho não está na linha {i} de {caminho} (nem nas duas vizinhas)"]
    fora = sorted(numeros(f["afirmacao"]) - numeros(trecho))
    return [f"fato {n}: o número {x} da afirmação não aparece no trecho citado" for x in fora]


def confere(texto: str, semana: str, limite: int) -> dict:
    """O que barra a pauta (problemas) e o que só avisa. Sem modelo."""
    campos, corpo = cabecalho(texto)
    s = secoes(corpo)
    problemas, avisos = [], []
    if campos.get("semana") != semana:
        problemas.append(f"o cabeçalho diz semana {campos.get('semana')!r}, e a pauta é da {semana}")
    for t in SECOES:
        if not s.get(t, "").strip():
            problemas.append(f"falta a seção '{t}'")
    fatos, ruins = le_fatos(s.get("Fatos", ""))
    problemas += ruins
    if "Fatos" in s and not fatos and not ruins:
        problemas.append("a tabela de fatos está vazia")
    for f in fatos:
        problemas += confere_fato(f)
    rascunho = s.get("Rascunho de partida", "")
    sabidos = set().union(*(numeros(f["afirmacao"]) for f in fatos)) if fatos else set()
    for x in sorted(numeros(rascunho) - sabidos):
        problemas.append(f"o número {x} está no rascunho e em nenhuma linha da tabela de fatos")
    if re.search(r"https?://|www\.|\b[\w-]+\.(?:com|br|io|dev|org|net|ai)\b", rascunho, re.I):
        problemas.append("o rascunho tem link ou endereço; os links vão no primeiro comentário")
    if rascunho:
        if len(rascunho) > limite:
            avisos.append(f"o rascunho tem {len(rascunho)} caracteres; o teto é {limite}")
        if "?" not in rascunho[len(rascunho) * 2 // 3:]:
            avisos.append("o rascunho não termina em pergunta")
        if len(re.findall(r"(?<!\w)#\w+", rascunho)) > 4:
            avisos.append("mais de quatro hashtags")
    contas = [f for f in fatos if f["tipo"].lower().strip("` ") == "conta"]
    return {"problemas": problemas, "avisos": avisos, "fatos": len(fatos), "contas": contas,
            "privados": sum("(privado)" in f["afirmacao"] for f in fatos)}


def texto_da_conferencia(r: dict, dia: dt.date) -> str:
    citados = r["fatos"] - len(r["contas"])
    cab = (f"**Barrada: {len(r['problemas'])} problema(s).**" if r["problemas"] else "**Conferida.**")
    l = [f"Feita pelo script em {dia.isoformat()}, sem modelo. {cab}", "",
         f"- {citados} fato(s) citado(s), cada um achado na linha da fonte."]
    if r["contas"]:
        l.append(f"- {len(r['contas'])} conta(s) que o script não refaz. Conferir à mão:")
        l += [f"  - ({f['n']}) {f['afirmacao']} — {f['trecho']} [{f['fonte']}]" for f in r["contas"]]
    if r["privados"]:
        l.append(f"- {r['privados']} fato(s) de audiência, privados: decidir se entram.")
    if r["problemas"]:
        l.append("- Problemas:")
        l += [f"  - {p}" for p in r["problemas"]]
    if r["avisos"]:
        l.append("- Avisos:")
        l += [f"  - {a}" for a in r["avisos"]]
    return "\n".join(l)


def primeiro_comentario(conf: dict) -> str:
    return "\n".join(f"{i['rotulo']}: {i['url']}" for i in conf["primeiro_comentario"])


# ----------------------------------------------------------------------- o agente

def env_do_ponto_env(chave: str) -> str:
    """Um valor do .env, sem carregar o resto: o agente não recebe os segredos.
    DIVULGA_ENV_ARQ troca o arquivo (a suíte)."""
    arq = pathlib.Path(os.environ.get("DIVULGA_ENV_ARQ") or ROOT / ".env")
    try:
        for l in arq.read_text(encoding="utf-8").splitlines():
            k, sep, v = l.strip().partition("=")
            if sep and k.strip() == chave:
                return v.strip().strip('"').strip("'")
    except OSError:
        pass
    return ""


def versao_do_agente() -> str:
    try:
        import agentes
        ag = agentes.ficha()["agentes"]["divulgador"]
        v = agentes.atual(ag)["versao"]
        return f"{v}+mudado" if agentes.divergencias("divulgador", ag) else v
    except (OSError, ValueError, KeyError):
        return "sem ficha"


def historias_usadas(semana: str) -> list[str]:
    usadas = []
    for arq in sorted(pasta().glob("20??-W??.md")):
        c, _ = cabecalho(arq.read_text(encoding="utf-8"))
        if arq.stem != semana and c.get("historia"):
            usadas.append(f"{arq.stem}: {c['historia']} ({c.get('estado', '?')})")
    return usadas


def parametros(semana: str, saida: pathlib.Path, conf: dict, historia: str) -> str:
    ini, fim = limites(semana)
    eps = [f"episodes/{(ini + dt.timedelta(days=i)).isoformat()}.md" for i in range(7)]
    eps = [e for e in eps if (ROOT / e).is_file()]
    existe = lambda p: p if (ROOT / p).is_file() else "(não existe)"
    usadas = historias_usadas(semana)
    return "\n".join([
        "## Parâmetros desta execução", "",
        f"- SEMANA: {semana}",
        f"- SEMANA_INICIO: {ini.isoformat()} (segunda)",
        f"- SEMANA_FIM: {fim.isoformat()} (domingo)",
        f"- POST_PARA: {dia_do_post(semana, conf['dia_do_post']).isoformat()} "
        f"({DIAS[conf['dia_do_post'] - 1]}, {conf['hora_do_post']})",
        f"- SAIDA: {relativo(saida)}",
        f"- LIMITE_CARACTERES: {conf['limite_caracteres']}",
        f"- EPISODIOS: {', '.join(eps) or '(nenhum episódio na semana)'}",
        f"- RELATORIO_DO_AUTOR: {existe(f'memoria/autor/{semana}.md')}",
        f"- FILA_DO_AUTOR: {existe('privado/divulgacao.md')}",
        f"- PRIVADO_AUDIENCIA: {existe('privado/audiencia.md')}",
        f"- HISTORIA_PEDIDA: {historia or '(vazia)'}",
        "- HISTORIAS_USADAS:" + ("" if usadas else " (nenhuma pauta anterior)"),
        *[f"  - {u}" for u in usadas],
    ])


def comando(prompt: str) -> list[str]:
    binario = os.environ.get("CLAUDE_BIN") or env_do_ponto_env("CLAUDE_BIN") or "claude"
    return [binario, "-p", prompt,
            "--model", os.environ.get("DIVULGADOR_MODELO") or MODELO,
            "--effort", os.environ.get("DIVULGADOR_ESFORCO") or ESFORCO,
            "--output-format", "json", "--permission-mode", "acceptEdits",
            "--allowedTools", ",".join(FERRAMENTAS),
            # Como o Editor: nada de servidores MCP nem skills da conta do autor.
            "--strict-mcp-config", "--disable-slash-commands"]


def ambiente_do_agente() -> dict:
    """O ambiente do claude -p: na assinatura Max, nunca na API.

    O token vem do .env quando não está no ambiente, como no run_episode.sh: o
    launchd não o passa, e sem ele o CLI usa o login interativo do Mac, que
    pode estar desligado (15/11). Só esse valor sai do .env; o resto não."""
    env = dict(os.environ)
    if env.pop("ANTHROPIC_API_KEY", None):
        print("AVISO: ANTHROPIC_API_KEY no ambiente; removida para a pauta rodar no Max (docs/custos.md)")
    if not env.get("CLAUDE_CODE_OAUTH_TOKEN") and (tok := env_do_ponto_env("CLAUDE_CODE_OAUTH_TOKEN")):
        env["CLAUDE_CODE_OAUTH_TOKEN"] = tok
    return env


def le_max(env: dict) -> dict | None:
    """Uma leitura do limite do Max (scripts/limites_max.py); None se desligada."""
    if os.environ.get("LIMITES_MAX", "1") != "1":
        return None
    try:
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "limites_max.py")], env=env,
                           capture_output=True, text=True, timeout=90)
        return json.loads(r.stdout)
    except (subprocess.TimeoutExpired, ValueError, OSError) as e:
        return {"erro": f"{type(e).__name__}: {e}"}


def roda_agente(semana: str, saida: pathlib.Path, conf: dict, historia: str) -> str | None:
    """Roda o agente; devolve o motivo da falha, ou None."""
    prompt = (ROOT / "prompts" / "divulgador.md").read_text(encoding="utf-8") \
        + "\n\n" + parametros(semana, saida, conf, historia)
    cmd = comando(prompt)
    if not shutil.which(cmd[0]):
        return f"'{cmd[0]}' não encontrado no PATH"
    env = ambiente_do_agente()
    saida.parent.mkdir(parents=True, exist_ok=True)
    max_antes = le_max(env)
    try:
        r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=PRAZO_AGENTE_S)
    except subprocess.TimeoutExpired:
        return f"o agente passou de {PRAZO_AGENTE_S // 60} minutos"
    max_depois = le_max(env)
    (ROOT / "logs").mkdir(exist_ok=True)
    (ROOT / "logs" / f"divulga-{semana}-agente.json").write_text(r.stdout, encoding="utf-8")
    try:
        d = json.loads(r.stdout)
        texto, erro = str(d.get("result") or ""), bool(d.get("is_error"))
    except ValueError:
        d, texto, erro = {}, r.stdout.strip(), False      # stub de teste ou CLI antigo
    print(f"Agente retornou: {texto[:300] or '<vazio>'} (rc={r.returncode})")
    medida = {"versao": versao_do_agente(), "modelo": cmd[cmd.index("--model") + 1],
              "custo_usd": d.get("total_cost_usd"), "turnos": d.get("num_turns"),
              "duracao_s": round(d["duration_ms"] / 1000) if d.get("duration_ms") else None}
    if max_antes is not None or max_depois is not None:
        from limites_max import delta, resumo
        medida["max"] = {"antes": max_antes, "depois": max_depois,
                         "gasto_pontos": delta(max_antes, max_depois)}
        print(resumo(max_antes, max_depois))
    motivo = None
    if r.returncode != 0 or erro:
        motivo = f"claude -p falhou (rc={r.returncode}): {texto[:200] or r.stderr.strip()[:200]}"
    elif texto.startswith("FAIL"):
        motivo = f"o agente reportou falha: {texto[:200]}"
    elif not saida.is_file():
        motivo = f"o agente não escreveu {relativo(saida)}"
    registra("pauta", semana, estado="falhou" if motivo else "ok", **medida)
    return motivo


# ------------------------------------------------------------------------ o envio

SMTP = ("NOTIFY_TO", "SMTP_HOST", "SMTP_USER", "SMTP_PASS")


def falta_smtp() -> list[str]:
    """O que falta no .env para a pauta sair do Mac por e-mail. Sem isso, a
    entrega é uma notificação do macOS, que ninguém vê no sábado longe do Mac."""
    return [k for k in SMTP if not (os.environ.get(k) or env_do_ponto_env(k)).strip()]


def avisa(assunto: str, corpo: str, seco: bool) -> str:
    print(assunto)
    print(corpo)
    if seco:
        print("DRY-RUN: nada foi enviado.")
        return "dry-run"
    if os.environ.get("DIVULGA_AVISO") == "0":        # a suíte: sem e-mail nem notificação
        print("Aviso desligado (DIVULGA_AVISO=0) — só o log.")
        return "log"
    if faltam := falta_smtp():
        print(f"AVISO: sem e-mail configurado ({', '.join(faltam)} vazios no .env): a pauta "
              "não sai do Mac, só a notificação do macOS. Ver docs/plano-divulgador.md.")
    import notify
    notify.load_env()
    try:
        if notify.send_smtp(assunto, corpo):
            return "e-mail"
    except Exception as e:                            # aviso nunca derruba a rotina
        print(f"AVISO: envio SMTP falhou ({e}).", file=sys.stderr)
    if notify.send_macos(assunto):
        return "macos"
    print("Nenhum canal de notificação configurado — só o log.")
    return "log"


def dm(d: dt.date) -> str:
    return f"{d.day:02d}/{d.month:02d}"


# ------------------------------------------------------------------------ comandos

def cmd_semana(a, hoje: dt.date) -> int:
    conf = config()
    semana = a.semana or semana_da_pauta(hoje)
    arq = pasta() / f"{semana}.md"
    post = dia_do_post(semana, conf["dia_do_post"])
    etapas = [e.strip() for e in a.only.split(",")] if a.only else list(ETAPAS)
    if ruins := [e for e in etapas if e not in ETAPAS]:
        print(f"ERRO: etapa desconhecida: {', '.join(ruins)} (pauta, confere, entrega)", file=sys.stderr)
        return 2
    estado = cabecalho(arq.read_text(encoding="utf-8"))[0].get("estado") if arq.is_file() else None
    print(f"Divulgador — semana {semana}, post para {DIAS[post.isoweekday() - 1]} {dm(post)}, "
          f"pauta em {relativo(arq)}" + (f" (estado: {estado})" if estado else ""))
    if estado in FINAIS and not a.overwrite and not a.only:
        print("Nada a fazer: a pauta desta semana já foi entregue.")
        return 0

    if "pauta" in etapas:
        if arq.is_file() and not a.overwrite:
            print("Pauta já existe; --overwrite refaz.")
        elif a.dry_run:
            print("DRY-RUN: " + " ".join(comando("<prompts/divulgador.md + parâmetros>")))
            print(parametros(semana, arq, conf, a.historia))
        else:
            if motivo := roda_agente(semana, arq, conf, a.historia):
                print(f"ERRO: {motivo}", file=sys.stderr)
                return 3

    barrada = False
    if "confere" in etapas:
        if not arq.is_file():
            if a.dry_run:
                print("DRY-RUN: sem pauta para conferir.")
                return 0
            print(f"ERRO: não há pauta em {relativo(arq)}.", file=sys.stderr)
            return 3
        texto = arq.read_text(encoding="utf-8")
        r = confere(texto, semana, conf["limite_caracteres"])
        barrada = bool(r["problemas"])
        relato = texto_da_conferencia(r, hoje)
        print(relato)
        if not a.dry_run:
            campos, corpo = cabecalho(texto)
            corpo = com_secao(corpo, "Primeiro comentário", primeiro_comentario(conf))
            corpo = com_secao(corpo, "Conferência", relato)
            campos.update(conferencia="barrada" if barrada else "ok")
            if campos.get("estado") not in FINAIS:
                campos["estado"] = "barrada" if barrada else "conferida"
            arq.write_text(monta(campos, corpo), encoding="utf-8")
            registra("conferencia", semana, resultado="barrada" if barrada else "ok",
                     fatos=r["fatos"], contas=len(r["contas"]),
                     problemas=len(r["problemas"]), avisos=len(r["avisos"]))

    if "entrega" in etapas:
        if not arq.is_file():
            if a.dry_run:
                print("DRY-RUN: sem pauta para entregar.")
                return 0
            print(f"ERRO: não há pauta em {relativo(arq)}.", file=sys.stderr)
            return 3
        texto = arq.read_text(encoding="utf-8")
        campos, _ = cabecalho(texto)
        barrada = barrada or campos.get("conferencia") == "barrada"
        assunto = f"CampsCast — pauta do post de {DIAS[post.isoweekday() - 1]}, {dm(post)}" \
            + (" (com ressalvas)" if barrada else "")
        corpo = "\n".join([
            f"História: {campos.get('historia', '?')}",
            f"Agendar para {DIAS[post.isoweekday() - 1]}, {dm(post)}, às {conf['hora_do_post']}.",
            f"Arquivo: {relativo(arq)}", "",
            "Depois de agendar (ou de desistir da semana):",
            f"  python3 scripts/divulga.py --semana {semana} --marca agendado --minutos N",
            f"  python3 scripts/divulga.py --semana {semana} --marca sem-post",
            "", "-" * 60, "", texto])
        canal = avisa(assunto, corpo, a.dry_run)
        if not a.dry_run:
            if campos.get("estado") not in FINAIS:
                muda_estado(arq, estado="entregue")
            registra("entrega", semana, canal=canal, ressalvas=barrada)
    return 1 if barrada else 0


def cmd_lembrete(a, hoje: dt.date) -> int:
    conf = config()
    for arq in sorted(pasta().glob("20??-W??.md")):
        campos, _ = cabecalho(arq.read_text(encoding="utf-8"))
        if campos.get("post_para") != hoje.isoformat() or campos.get("estado") == "sem-post":
            continue
        corpo = "\n".join(["O agendamento do LinkedIn não agenda comentário. Cole este, logo depois de o post sair:",
                           "", primeiro_comentario(conf), "",
                           "A primeira hora é para responder comentários.",
                           f"História: {campos.get('historia', '?')}"])
        canal = avisa(f"CampsCast — o post sai às {conf['hora_do_post']}: o primeiro comentário", corpo, a.dry_run)
        if not a.dry_run:
            registra("lembrete", arq.stem, canal=canal, estado=campos.get("estado"))
        return 0
    print(f"Sem post para hoje ({hoje.isoformat()}).")
    return 0


def cmd_marca(a, hoje: dt.date) -> int:
    semana = a.semana or semana_da_pauta(hoje)
    arq = pasta() / f"{semana}.md"
    if not arq.is_file():
        print(f"ERRO: não há pauta em {relativo(arq)}.", file=sys.stderr)
        return 3
    extra = {"minutos": a.minutos} if a.minutos is not None else {}
    muda_estado(arq, estado=a.marca, **extra)
    registra("marca", semana, estado=a.marca, **extra)
    print(f"{semana}: {a.marca}" + (f", {a.minutos} min do autor" if a.minutos is not None else ""))
    return 0


def cmd_mostra() -> int:
    arqs = sorted(pasta().glob("20??-W??.md"))
    if not arqs:
        print("Nenhuma pauta ainda.")
        return 0
    com_post = 0
    for arq in arqs:
        c, _ = cabecalho(arq.read_text(encoding="utf-8"))
        com_post += c.get("estado") == "agendado"
        minutos = f"{c['minutos']} min" if c.get("minutos") else "—"
        print(f"{arq.stem}  post {c.get('post_para', '?')}  {c.get('estado', '?'):10} "
              f"conferência {c.get('conferencia', '—'):8} {minutos:>7}  {c.get('historia', '')}")
    print(f"{com_post} de {len(arqs)} semanas com post agendado.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="O Divulgador: a pauta do post da semana.")
    ap.add_argument("--data", help="age como se fosse este dia (AAAA-MM-DD)")
    ap.add_argument("--semana", help="semana ISO da pauta, como 2026-W47")
    ap.add_argument("--only", help="etapas, com vírgula: pauta, confere, entrega")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--historia", default="", help="a história que o autor já escolheu")
    ap.add_argument("--lembrete", action="store_true")
    ap.add_argument("--marca", choices=["agendado", "sem-post"])
    ap.add_argument("--minutos", type=int, help="com --marca agendado: quanto tempo o autor gastou")
    ap.add_argument("--mostra", action="store_true")
    ap.add_argument("--rotina", action="store_true", help="o launchd: lembrete no dia do post, pauta nos outros")
    a = ap.parse_args()
    hoje = dt.date.fromisoformat(a.data) if a.data else dt.datetime.now(FUSO).date()
    if a.mostra:
        return cmd_mostra()
    if a.marca:
        return cmd_marca(a, hoje)
    if a.lembrete or (a.rotina and hoje.isoweekday() == config()["dia_do_post"]):
        return cmd_lembrete(a, hoje)
    return cmd_semana(a, hoje)


if __name__ == "__main__":
    sys.exit(main())
