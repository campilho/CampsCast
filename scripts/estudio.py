#!/usr/bin/env python3
"""
CampsCast — monta os dados do estúdio: quem fez o quê, e a que horas.

O site mostra o estúdio com os personagens trabalhando (docs/site.md). Hoje um
só agente pesquisa, escolhe e escreve; este script separa o trabalho dele pelo
que ele estava fazendo em cada momento, lendo a transcrição — registro de
máquina, não relato — e junta o log do orquestrador, o registro de execução, o
roteiro, o log de pesquisa e a memória do dia.

Nada inventado: cada balão é uma frase do próprio agente, a descrição de uma
ferramenta que ele usou ou uma linha do log. A conversa do café é montada com
os números do dia e sai marcada como tal (`origem: "numeros"`).

Saída, no contrato `campscast.estudio/1`:
    site/estudio/elenco.json        os personagens e as instruções de cada um
    site/estudio/AAAA-MM-DD.json    a execução do dia, evento a evento
    site/estudio/ultimo.json        cópia da execução mais recente

Uso:
    python3 scripts/estudio.py --date 2026-10-30
    python3 scripts/estudio.py --orfaos      # passos do prompt sem personagem

ESTUDIO_DIR troca a pasta de saída; TRANSCRICOES_DIR, a das transcrições.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import os
import pathlib
import re
import sys
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

CONTRATO = "campscast.estudio/1"
FUSO = ZoneInfo("America/Sao_Paulo")
REPO = "https://github.com/campilho/CampsCast/blob/main"

# Quem é quem. `por_tras` diz o que de fato faz o trabalho hoje — o site mostra
# isso ao clicar no personagem, para que a separação não pareça mais do que é.
ELENCO = [
    {"id": "produtor", "nome": "Produtor", "estacao": "tecnica",
     "papel": "Abre o estúdio às 05:00, chama cada um na ordem, publica e avisa.",
     "por_tras": "scripts/run_episode.sh, um programa sem IA, chamado pelo agendador do Mac"},
    {"id": "editor", "nome": "Editor", "estacao": "redacao",
     "papel": "Lê a memória do programa, escolhe as pautas e atualiza temas, fios e backlog.",
     "por_tras": "Claude, o mesmo agente do Jornalista e do Roteirista"},
    {"id": "jornalista", "nome": "Jornalista", "estacao": "redacao",
     "papel": "Percorre as fontes, lê as páginas e anota o que achou.",
     "por_tras": "Claude, o mesmo agente do Editor e do Roteirista"},
    {"id": "roteirista", "nome": "Roteirista", "estacao": "redacao",
     "papel": "Escreve o roteiro na faixa de palavras que cabe na voz.",
     "por_tras": "Claude, o mesmo agente do Jornalista e do Editor"},
    {"id": "locutor", "nome": "Locutor", "estacao": "cabine",
     "papel": "Narra o roteiro com a cópia sintética da voz do autor.",
     "por_tras": "ElevenLabs, chamado por scripts/tts.py"},
    {"id": "vigia", "nome": "Vigia", "estacao": "portaria",
     "papel": "Arquiva fios parados, confere o roteiro e, às 07:30, confere se o episódio está no ar.",
     "por_tras": "conferências em Python no Mac e uma rotina do Claude na nuvem"},
]
AGENTE = ("jornalista", "editor", "roteirista")

# De que personagem é cada passo de prompts/master.md. Passo novo sem dono faz
# o teste falhar: é aqui que se decide quem o site mostra fazendo aquilo.
PASSOS = {1: "editor", 2: "editor", 3: "editor", 4: "jornalista", 5: "editor",
          6: "roteirista", 7: "editor", 8: "jornalista", 9: "roteirista"}
SECOES = {"Contexto de execução": AGENTE, "Formato do roteiro": ("roteirista",), "Guardrails": AGENTE}
PROCESSO = "Processo"


def rel(caminho: str) -> str:
    """Caminho do repositório, sem a parte da máquina (o arquivo é público).

    Tenta também o caminho resolvido: no macOS /var é atalho para /private/var,
    e a raiz daqui vem resolvida.
    """
    p = pathlib.Path(caminho)
    for c in (p, p.resolve()):
        try:
            return str(c.relative_to(ROOT))
        except ValueError:
            pass
    return p.name


def curta(url: str, n: int = 52) -> str:
    u = urlparse(url)
    s = (u.netloc.removeprefix("www.") + u.path).rstrip("/")
    return s if len(s) <= n else s[: n - 1] + "…"


def data_br(iso: str) -> str:
    return f"{iso[8:10]}/{iso[5:7]}"


def milhar(n: int) -> str:
    return f"{n:,}".replace(",", ".")


# ------------------------------------------------------------------ instruções

def secoes_master(texto: str | None = None) -> dict:
    """O prompt em pedaços: {"intro": str, "secoes": {título: str}, "passos": {n: str}}."""
    texto = texto if texto is not None else (ROOT / "prompts" / "master.md").read_text(encoding="utf-8")
    partes = re.split(r"^## ", texto, flags=re.M)
    secoes = {}
    for p in partes[1:]:
        titulo, _, corpo = p.partition("\n")
        # "Guardrails (invioláveis)" vira "Guardrails": o parêntese é comentário
        secoes[re.sub(r" \(.*", "", titulo.strip())] = corpo.strip()
    passos = {}
    for m in re.finditer(r"^(\d+)\. (.*?)(?=^\d+\. |\Z)", secoes.get(PROCESSO, ""), flags=re.M | re.S):
        passos[int(m.group(1))] = m.group(2).strip()
    return {"intro": partes[0].strip(), "secoes": secoes, "passos": passos}


def orfaos(pedacos: dict | None = None) -> list[str]:
    pedacos = pedacos or secoes_master()
    faltam = [f"passo {n}" for n in pedacos["passos"] if n not in PASSOS]
    faltam += [f"seção '{s}'" for s in pedacos["secoes"] if s != PROCESSO and s not in SECOES]
    return faltam


def doc(script: str) -> str:
    """Docstring do script, até o "Uso:"."""
    d = ast.get_docstring(ast.parse((ROOT / "scripts" / script).read_text(encoding="utf-8"))) or ""
    return d.split("\nUso:")[0].split("\n    python3")[0].strip()


def cabecalho_sh(script: str) -> str:
    linhas = []
    for l in (ROOT / "scripts" / script).read_text(encoding="utf-8").splitlines()[1:]:
        if not l.startswith("#"):
            break
        linhas.append(l[2:] if l.startswith("# ") else "")
    return "\n".join(linhas).strip()


def instrucoes(pid: str) -> list[dict]:
    p = secoes_master()
    mp = "prompts/master.md"
    if pid in AGENTE:
        out = [{"titulo": "Quem eu sou", "origem": mp, "texto": p["intro"]}]
        for n, quem in PASSOS.items():
            if quem == pid and n in p["passos"]:
                primeira = re.split(r"(?<=[.:])\s", p["passos"][n], maxsplit=1)[0]
                out.append({"titulo": f"Passo {n} · {primeira[:70]}", "origem": mp,
                            "texto": f"{n}. {p['passos'][n]}"})
        for s, quem in SECOES.items():
            if pid in quem and s in p["secoes"]:
                out.append({"titulo": s, "origem": mp, "texto": p["secoes"][s],
                            "compartilhada": len(quem) > 1})
        return out
    if pid == "locutor":
        tts = json.loads((ROOT / "config" / "tts.json").read_text(encoding="utf-8"))
        from nomes import nome_tts
        cfg = (f"Modelo: {nome_tts(tts.get('model_id', ''))}\n"
               f"Voz: {tts.get('_voz_falada', '')}\n"
               f"Ritmo medido: {tts.get('words_per_minute')} palavras por minuto\n"
               f"Ajustes: {json.dumps(tts.get('voice_settings', {}), ensure_ascii=False)}\n"
               f"Silêncio: {tts.get('silence_start_s')} s no começo, {tts.get('silence_end_s')} s no fim")
        return [{"titulo": "Como narra", "origem": "scripts/tts.py", "texto": doc("tts.py")},
                {"titulo": "Ajustes da voz", "origem": "config/tts.json", "texto": cfg}]
    if pid == "produtor":
        return [{"titulo": "A ordem do dia", "origem": "scripts/run_episode.sh", "texto": cabecalho_sh("run_episode.sh")},
                {"titulo": "Que dia tem episódio", "origem": "scripts/schedule.py", "texto": doc("schedule.py")},
                {"titulo": "Publicar", "origem": "scripts/publish.py", "texto": doc("publish.py")},
                {"titulo": "Avisar", "origem": "scripts/notify.py", "texto": doc("notify.py")}]
    if pid == "vigia":
        return [{"titulo": "Antes do agente: arquivar fios parados", "origem": "scripts/expira_fios.py", "texto": doc("expira_fios.py")},
                {"titulo": "Depois do roteiro: conferir o que não pode faltar", "origem": "scripts/confere_roteiro.py", "texto": doc("confere_roteiro.py")},
                {"titulo": "No fim: deixar o estado à vista", "origem": "scripts/estado.py", "texto": doc("estado.py")},
                {"titulo": "Às 07:30, na nuvem", "origem": "rotina do Claude na nuvem",
                 "texto": "Nos dias úteis, às 07:30, uma rotina do Claude na nuvem lê o estado.json e o feed "
                          "publicados e avisa o autor por e-mail e no celular se o episódio não estiver no ar. "
                          "Na sexta, lembra do relatório da semana."}]
    return []


# --------------------------------------------------------------- transcrição

def transcricao(data: str, sessao: str | None) -> pathlib.Path | None:
    base = os.environ.get("TRANSCRICOES_DIR")
    if base and sessao:
        f = pathlib.Path(base) / f"{sessao}.jsonl"
        return f if f.exists() else None
    if sessao:
        from watch_agent import session_dir
        d = session_dir()
        if d and (d / f"{sessao}.jsonl").exists():
            return d / f"{sessao}.jsonl"
    from research_trail import session_for
    return session_for(data)


def hora(ts: str) -> str:
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(FUSO).isoformat(timespec="seconds")


LEITURAS = [  # (início do caminho, quem, balão)
    ("config/briefing.md", "editor", "Relendo o contrato editorial"),
    ("config/sources.yaml", "jornalista", "Conferindo a lista de fontes"),
    ("saved-items/backlog.md", "editor", "Lendo o backlog: o que ficou de fora"),
    ("saved-items/historico", "editor", "Anotando no histórico do backlog"),
    ("memoria/temas-sugeridos.md", "editor", "Lendo as sugestões de tema"),
    ("memoria/temas.md", "editor", "Lendo os temas que o programa acompanha"),
    ("memoria/fios-fechados", "editor", "Fechando um fio que teve desfecho"),
    ("memoria/fios.md", "editor", "Lendo os fios em aberto"),
    ("covered-index.json", "editor", "Consultando o índice do que já foi ao ar"),
    ("research/", "jornalista", "Escrevendo o log de pesquisa"),
    ("episodes/", "roteirista", "Escrevendo o roteiro"),
    ("logs/cabecalho", "roteirista", "Contando as palavras da abertura"),
]
EDICOES = {"covered-index.json": "Registrando as pautas de hoje no índice",
           "saved-items/backlog.md": "Atualizando o backlog",
           "memoria/fios.md": "Atualizando os fios em aberto",
           "memoria/temas.md": "Atualizando o estado dos temas",
           "episodes/": "Ajustando o roteiro",
           "research/": "Revisando o log de pesquisa"}


def de_quem(caminho: str) -> tuple[str, str]:
    for prefixo, quem, balao in LEITURAS:
        if caminho.startswith(prefixo):
            return quem, balao
    return "editor", f"Lendo {caminho}"


def evento_ferramenta(nome: str, inp: dict, anterior: str) -> dict | None:
    if nome == "WebFetch":
        url = inp.get("url", "")
        return {"quem": "jornalista", "texto": f"Lendo {curta(url)}", "url": url, "acao": "le"}
    if nome == "WebSearch":
        return {"quem": "jornalista", "texto": f"Buscando “{inp.get('query', '')}”", "acao": "busca"}
    if nome in ("Read", "Write", "Edit"):
        c = rel(inp.get("file_path", ""))
        quem, balao = de_quem(c)
        if nome == "Read":
            if c.startswith("episodes/"):
                quem, balao = "editor", f"Relendo o episódio de {data_br(pathlib.Path(c).stem)}"
            elif c.startswith("research/"):
                quem, balao = "editor", f"Relendo o log de pesquisa de {data_br(pathlib.Path(c).stem)}"
        elif nome == "Edit":
            balao = next((b for p, b in EDICOES.items() if c.startswith(p)), balao)
        acao = {"Read": "le", "Write": "escreve", "Edit": "edita"}[nome]
        return {"quem": quem, "texto": balao, "arquivo": c, "acao": acao}
    if nome == "Grep":
        c = rel(inp.get("path", ""))
        onde = "nos episódios antigos" if "episodes" in c else "no índice" if "covered" in c else f"em {c}"
        termo = inp.get("pattern", "")
        if re.search(r"[\\^$()\[\]*+?{}]", termo):  # expressão regular não vira balão
            return {"quem": "editor", "texto": f"Conferindo {onde.removeprefix('em ')}", "acao": "le"}
        termo = "” ou “".join(termo.split("|"))
        return {"quem": "editor", "texto": f"Procurando “{termo}” {onde}", "acao": "le"}
    if nome == "Bash":
        cmd = inp.get("command", "")
        if "fios-fechados" in cmd:
            return {"quem": "editor", "texto": "Fechando um fio que teve desfecho", "acao": "edita"}
        if cmd.startswith("ls"):
            return {"quem": "editor", "texto": "Vendo o que já existe: episódios, logs e memória", "acao": "le"}
        if "wc -w" in cmd:
            return {"quem": "roteirista", "texto": "Contando as palavras do roteiro", "acao": "confere"}
        if "plutil" in cmd or "json" in cmd:
            return {"quem": "editor", "texto": "Conferindo se o índice continua válido", "acao": "confere"}
        if "historico" in cmd:
            return {"quem": "editor", "texto": "Olhando o histórico do backlog", "acao": "le"}
        return {"quem": anterior, "texto": "Conferindo um detalhe no terminal", "acao": "confere"}
    return None  # ToolSearch e afins: bastidor do CLI, não trabalho


EDITOR_FALA = re.compile(r"pauta[s]? (definida|firme)|pautas firmes|pesquisa encerrada|três pautas|decid", re.I)
ROTEIRO_FALA = re.compile(r"writing the script|escrevo o roteiro\b(?!.*índice)|roteiro pronto", re.I)


def de_quem_fala(texto: str, anterior: str) -> str:
    if EDITOR_FALA.search(texto):
        return "editor"
    if ROTEIRO_FALA.search(texto):
        return "roteirista"
    return anterior


def eventos_agente(path: pathlib.Path) -> list[dict]:
    eventos: list[dict] = []
    por_id: dict[str, dict] = {}
    anterior = "editor"
    for linha in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            d = json.loads(linha)
        except json.JSONDecodeError:
            continue
        ts = d.get("timestamp")
        if d.get("type") == "system" and "safeguards" in str(d.get("content", "")) and ts:
            eventos.append({"t": hora(ts), "quem": anterior, "origem": "sistema", "acao": "interrompido",
                            "texto": "O filtro de segurança do modelo interrompeu uma resposta; o agente retomou."})
            continue
        if d.get("type") not in ("assistant", "user") or not ts:
            continue
        conteudo = (d.get("message") or {}).get("content")
        if not isinstance(conteudo, list):
            continue
        for x in conteudo:
            tipo = x.get("type")
            if d["type"] == "assistant" and tipo == "tool_use":
                ev = evento_ferramenta(x.get("name", ""), x.get("input") or {}, anterior)
                if ev:
                    ev = {"t": hora(ts), "origem": "ferramenta", **ev}
                    eventos.append(ev)
                    por_id[x.get("id", "")] = ev
                    anterior = ev["quem"]
            elif d["type"] == "assistant" and tipo == "text":
                txt = x.get("text", "").strip()
                if not txt or txt.startswith(("OK ", "FAIL ")):
                    continue
                anterior = de_quem_fala(txt, anterior)
                eventos.append({"t": hora(ts), "quem": anterior, "origem": "agente", "acao": "fala", "texto": txt})
            elif d["type"] == "user" and tipo == "tool_result":
                ev = por_id.get(x.get("tool_use_id", ""))
                if not ev or ev.get("acao") != "le" or "url" not in ev:
                    continue
                corpo = x.get("content")
                corpo = corpo if isinstance(corpo, str) else json.dumps(corpo, ensure_ascii=False)
                m = re.search(r"HTTP (\d{3})", corpo[:300])
                ev["ok"] = not (x.get("is_error") or m)
                if not ev["ok"]:
                    cod = m.group(1) if m else "erro"
                    ev["status"] = cod
                    eventos.append({"t": hora(ts), "quem": "jornalista", "origem": "ferramenta", "acao": "fechada",
                                    "url": ev["url"], "texto": f"{curta(ev['url'], 40)} não abriu ({cod})"})
    return eventos


# ----------------------------------------------------------- log do orquestrador

def eventos_log(data: str, tts: dict) -> list[dict]:
    log = ROOT / "logs" / f"{data}.log"
    if not log.exists():
        return []
    regras = [
        (r"════ CampsCast — episódio", "produtor", lambda m, l: "Abrindo o estúdio"),
        (r"^Janela: (\S+) → (\S+)", "produtor",
         lambda m, l: f"Janela de notícias: {data_br(m.group(1))} a {data_br(m.group(2))}"),
        (r"^Roteiro: (\d+)–(\d+) palavras, alvo (\d+)", "produtor",
         lambda m, l: f"Pedido: roteiro de {milhar(int(m.group(1)))} a {milhar(int(m.group(2)))} palavras"),
        (r"^── \[1/4\]", "produtor", lambda m, l: "Chamando a redação"),
        (r"^Rede respondeu|^Sem rede", "produtor", lambda m, l: l),
        (r"^Agente retornou: OK \S+ (\d+) (\d\d:\d\d)", "produtor",
         lambda m, l: f"Roteiro entregue: {milhar(int(m.group(1)))} palavras, {m.group(2)}"),
        (r"^Roteiro conferido: (.*)", "vigia", lambda m, l: f"Conferi o roteiro: {m.group(1)}"),
        (r"^Roteiro com avisos?: (.*)", "vigia", lambda m, l: f"Anotei no roteiro: {m.group(1)}"),
        (r"^── \[2/4\]", "locutor",
         lambda m, l: f"Narrando: {milhar(tts.get('caracteres', 0))} caracteres em {tts.get('trechos', '?')} trechos"
         if tts else "Narrando"),
        (r"^Áudio: ", "locutor",
         lambda m, l: f"Narração pronta: {tts['audio_s'] // 60} min {tts['audio_s'] % 60:02d} s"
         if tts.get("audio_s") else "Narração pronta"),
        (r"^── \[3/4\]", "produtor", lambda m, l: "Subindo o MP3 e o feed"),
        (r"^── \[4/4\]", "produtor", lambda m, l: "No ar. Avisando o autor"),
        (r"════ Concluído", "produtor", lambda m, l: "Gravação concluída"),
        (r"^Relatório do autor", "produtor", lambda m, l: "Deixei o relatório da semana para o autor"),
        (r"^Nada novo a cobrir", "produtor", lambda m, l: "Repescagem: o episódio de hoje já saiu, nada a fazer"),
        (r"^(ERRO|Falhou|FAIL)", "produtor", lambda m, l: l),
    ]
    eventos = []
    for linha in log.read_text(encoding="utf-8", errors="replace").splitlines():
        m0 = re.match(r"^\[(\d\d:\d\d:\d\d)\] (.*)", linha)
        if not m0:
            continue
        t = dt.datetime.fromisoformat(f"{data}T{m0.group(1)}").replace(tzinfo=FUSO).isoformat()
        corpo = m0.group(2).strip()
        for padrao, quem, texto in regras:
            m = re.search(padrao, corpo)
            if m:
                eventos.append({"t": t, "quem": quem, "origem": "log", "acao": "etapa", "texto": texto(m, corpo)})
                break
    return eventos


# --------------------------------------------------------------- o resto do dia

def registro(data: str) -> dict:
    arq = pathlib.Path(os.environ.get("METRICAS_ARQ", ROOT / "metricas" / "execucoes.jsonl"))
    achado = {}
    if arq.exists():
        for l in arq.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            if r.get("data") == data:
                achado = r
    return achado


def pesquisa(data: str) -> dict:
    arq = ROOT / "research" / f"{data}.md"
    if not arq.exists():
        return {}
    t = arq.read_text(encoding="utf-8")
    num = lambda rotulo: int(m.group(1)) if (m := re.search(rotulo + r"[^*]*\*\*(\d+)\*\*", t)) else None
    descartadas = []
    bloco = t.split("## Descartadas", 1)[1].split("\n## ", 1)[0] if "## Descartadas" in t else ""
    for m in re.finditer(r"^### (.+)\n((?:- .*\n?)+)", bloco, flags=re.M):
        motivo = re.search(r"motivo: (.+)", m.group(2))
        descartadas.append({"titulo": m.group(1).strip(), "motivo": motivo.group(1).strip() if motivo else ""})
    return {"paginas": num("Páginas abertas"), "fechadas": num("Fechadas"), "sites": num("Sites distintos"),
            "buscas": num("Buscas na web"), "pautas_avaliadas": num("Pautas avaliadas"),
            "descartadas": descartadas, "url": f"{REPO}/research/{data}.md"}


def memoria() -> dict:
    temas = []
    t = (ROOT / "memoria" / "temas.md").read_text(encoding="utf-8")
    for m in re.finditer(r"^## (T-\d+) · (.+)\n(.*?)(?=^## |\Z)", t, flags=re.M | re.S):
        est = re.search(r"^- estado \((\S+)\): (.+)$", m.group(3), flags=re.M)
        temas.append({"id": m.group(1), "titulo": m.group(2).strip(),
                      "estado_em": est.group(1) if est else None, "estado": est.group(2).strip() if est else ""})
    f = (ROOT / "memoria" / "fios.md").read_text(encoding="utf-8")
    fios = [{"id": m.group(1), "titulo": m.group(2).strip()}
            for m in re.finditer(r"^## (F-\d+) · (.+)$", f, flags=re.M)]
    b = (ROOT / "saved-items" / "backlog.md").read_text(encoding="utf-8").split("\n---\n", 1)[-1]
    backlog = []
    for m in re.finditer(r"^## (.+)\n(.*?)(?=^## |\Z)", b, flags=re.M | re.S):
        val = re.search(r"validade: (\S+)", m.group(2))
        backlog.append({"titulo": m.group(1).strip(), "validade": val.group(1) if val else None})
    return {"temas": temas, "fios": fios, "backlog": backlog,
            "urls": {"temas": f"{REPO}/memoria/temas.md", "fios": f"{REPO}/memoria/fios.md",
                     "backlog": f"{REPO}/saved-items/backlog.md"}}


def parecido(a: str, b: str) -> bool:
    """O título do backlog e o da pauta raramente são iguais; basta metade das palavras."""
    pa, pb = ({w for w in re.findall(r"\w{4,}", x.lower())} for x in (a, b))
    return bool(pa) and len(pa & pb) / len(pa) >= 0.5


def episodio(data: str) -> dict:
    from publish import parse_front_matter
    texto = (ROOT / "episodes" / f"{data}.md").read_text(encoding="utf-8")
    fm = parse_front_matter(texto)
    corpo = texto.lstrip().split("---", 2)[2].strip() if texto.lstrip().startswith("---") else texto
    show = json.loads((ROOT / "config" / "show.json").read_text(encoding="utf-8"))
    do_backlog = set(fm.get("from_backlog") or [])
    return {"numero": int(fm.get("episode", 0) or 0), "titulo": fm.get("title", ""),
            "janela": [fm.get("window_start"), fm.get("window_end")],
            "palavras": int(fm.get("words", 0) or 0),
            "pautas": [{"titulo": p.get("title", ""), "fonte": p.get("source_name", ""), "url": p.get("source_url", ""),
                        "do_backlog": any(parecido(b, p.get("title", "")) for b in do_backlog)}
                       for p in fm.get("topics") or [] if isinstance(p, dict)],
            "roteiro": [p.strip() for p in corpo.split("\n\n") if p.strip()],
            "roteiro_url": f"{REPO}/episodes/{data}.md",
            "mp3": f"{show.get('base_url', '').rstrip('/')}/audio/{data}.mp3"}


def agenda(data: str) -> dict:
    from schedule import avaliar
    d0 = dt.date.fromisoformat(data)
    dias = [(str(d), *avaliar(d)) for d in (d0 + dt.timedelta(days=i) for i in range(1, 15))]
    return {"gravacao": "05:00", "repescagem": ["06:00", "07:00"], "vigia": "07:30", "noite": "19:00",
            "proximos": [d for d, tem, _ in dias if tem][:5],
            "folgas": {d: folga(motivo) for d, tem, motivo in dias if not tem}}


def folga(motivo: str) -> str:
    """"feriado nacional: Finados" vira "feriado de Finados"; "sábado não está…", "sábado"."""
    if ":" in motivo:
        return f"feriado de {motivo.split(':', 1)[1].strip()}"
    return motivo.split()[0]


def capitulos(eventos: list[dict]) -> list[dict]:
    caps, vistos = [], set()

    def marca(i: int, titulo: str) -> None:
        if titulo not in vistos:
            vistos.add(titulo)
            caps.append({"t": eventos[i]["t"], "quem": eventos[i]["quem"], "titulo": titulo})

    escreveu = False
    for i, e in enumerate(eventos):
        q = e["quem"]
        if q == "produtor" and not caps:
            marca(i, "O Produtor abre o estúdio")
        elif q == "editor" and e["origem"] == "ferramenta" and not escreveu:
            marca(i, "O Editor lê a memória")
        elif q == "jornalista" and e.get("acao") in ("le", "busca") and "url" in e or e.get("acao") == "busca":
            marca(i, "O Jornalista pesquisa")
        elif q == "roteirista" and e.get("acao") == "escreve":
            escreveu = True
            marca(i, "O Roteirista escreve")
        elif q == "editor" and escreveu and e.get("acao") == "edita":
            marca(i, "O Editor atualiza a memória")
        elif q == "locutor":
            marca(i, "O Locutor narra")
        elif q == "produtor" and "Subindo" in e["texto"]:
            marca(i, "O Produtor publica")
    return caps


def conversa(ep: dict, pq: dict, reg: dict, leituras: list[dict]) -> list[dict]:
    """O café: frases montadas com os números do dia. Nada aqui é fala gravada."""
    fechadas = [e for e in leituras if e.get("ok") is False]
    openai = sum(1 for e in fechadas if "openai.com" in e.get("url", ""))
    linhas = []
    if pq.get("paginas"):
        frase = f"Abri {pq['paginas']} páginas em {pq['sites']} sites e fiz {pq['buscas']} buscas."
        if fechadas:
            frase += f" {len(fechadas)} portas fecharam na minha cara" + (f", {openai} da OpenAI." if openai else ".")
        linhas.append({"quem": "jornalista", "texto": frase})
    if pq.get("pautas_avaliadas"):
        n_back = sum(1 for p in ep["pautas"] if p["do_backlog"])
        linhas.append({"quem": "editor", "texto":
                       f"Avaliamos {pq['pautas_avaliadas']} pautas e ficaram {len(ep['pautas'])}"
                       + (f", uma delas do backlog." if n_back == 1 else ".")})
    ind = reg.get("indicadores") or {}
    if ind.get("fios_abertos"):
        linhas.append({"quem": "editor", "texto":
                       f"Estou acompanhando {ind['fios_abertos']} fios em aberto e {ind.get('temas', 0)} temas."})
    if ep.get("palavras"):
        linhas.append({"quem": "roteirista", "texto": f"O roteiro saiu com {milhar(ep['palavras'])} palavras."})
    el = reg.get("elevenlabs") or {}
    if el.get("audio_s"):
        linhas.append({"quem": "locutor", "texto":
                       f"Deu {el['audio_s'] // 60} minutos e {el['audio_s'] % 60} segundos de voz, em {el.get('trechos')} trechos."})
    if reg.get("fim"):
        custo = (reg.get("claude") or {}).get("custo_estimado_usd")
        linhas.append({"quem": "produtor", "texto":
                       f"Abri o estúdio às {reg['inicio'][11:16]} e o episódio entrou no ar às {reg['fim'][11:16]}."
                       + (f" A redação gastou uns {custo:.2f} dólares de modelo.".replace(f"{custo:.2f}", f"{custo:.2f}".replace(".", ","))
                          if custo else "")})
    return [{**l, "origem": "numeros"} for l in linhas]


# --------------------------------------------------------------------- montagem

def monta(data: str) -> dict:
    reg = registro(data)
    tts = {}
    for f in sorted((ROOT / "logs").glob(f"{data}-*-tts.json")):
        tts = json.loads(f.read_text(encoding="utf-8"))
    sessao = (reg.get("claude") or {}).get("sessao")
    tr = transcricao(data, sessao)
    eventos = sorted(eventos_log(data, tts) + (eventos_agente(tr) if tr else []), key=lambda e: e["t"])
    ep = episodio(data)
    pq = pesquisa(data)
    leituras = [e for e in eventos if e.get("acao") == "le" and "url" in e]
    buscas = [e["texto"].removeprefix("Buscando ") for e in eventos if e.get("acao") == "busca"]
    claude = reg.get("claude") or {}
    return {
        "contrato": CONTRATO,
        "data": data,
        "fuso": "America/Sao_Paulo",
        "gerado_em": dt.datetime.now(FUSO).isoformat(timespec="seconds"),
        "episodio": ep,
        "execucao": {
            "estado": reg.get("estado"),
            "inicio": eventos[0]["t"] if eventos else None,
            "fim": next((e["t"] for e in eventos if e["texto"] == "Gravação concluída"), eventos[-1]["t"] if eventos else None),
            "etapas_s": reg.get("etapas_s", {}),
            "modelo": claude.get("modelo"),
            "custo_claude_usd": round(claude["custo_estimado_usd"], 2) if claude.get("custo_estimado_usd") else None,
            "creditos_elevenlabs": (reg.get("elevenlabs") or {}).get("creditos"),
            "audio_s": (reg.get("elevenlabs") or {}).get("audio_s"),
            "transcricao": bool(tr),
        },
        "eventos": eventos,
        "capitulos": capitulos(eventos),
        "pesquisa": {**pq, "leituras": [{"url": e["url"], "ok": e.get("ok", True), "status": e.get("status")}
                                        for e in leituras], "buscas_feitas": buscas},
        "memoria": memoria(),
        "conversa": conversa(ep, pq, reg, leituras),
        "agenda": agenda(data),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--date", help="AAAA-MM-DD (padrão: o episódio mais recente)")
    ap.add_argument("--orfaos", action="store_true", help="lista passos do prompt sem personagem e sai")
    a = ap.parse_args()

    if a.orfaos:
        faltam = orfaos()
        print("\n".join(faltam) if faltam else "todos os passos e seções têm personagem")
        return 1 if faltam else 0

    data = a.date or sorted(p.stem for p in (ROOT / "episodes").glob("????-??-??.md"))[-1]
    saida = pathlib.Path(os.environ.get("ESTUDIO_DIR", ROOT / "site" / "estudio"))
    saida.mkdir(parents=True, exist_ok=True)

    elenco = {"contrato": CONTRATO, "personagens": [{**p, "instrucoes": instrucoes(p["id"])} for p in ELENCO]}
    dia = monta(data)
    escreve = lambda nome, obj: (saida / nome).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n",
                                                          encoding="utf-8")
    escreve("elenco.json", elenco)
    escreve(f"{data}.json", dia)
    escreve("ultimo.json", dia)
    faltam = orfaos()
    if faltam:
        print(f"aviso: sem personagem no site: {', '.join(faltam)}", file=sys.stderr)
    print(f"{data}: {len(dia['eventos'])} eventos, {len(dia['capitulos'])} capítulos"
          + ("" if dia["execucao"]["transcricao"] else " (sem transcrição: só o log)") + f" → {rel(str(saida))}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
