#!/usr/bin/env python3
"""
CampsCast — a sombra do dia: variantes do agente em fila, depois da produção.

    python3 scripts/sombra.py --rotina              # o que o launchd chama às 04:57
    python3 scripts/sombra.py --data D --foto PASTA # retoma um dia de uma foto já tirada
    python3 scripts/sombra.py --dry-run             # mostra o plano, sem rodar nada
    python3 scripts/sombra.py --compara --data D    # refaz só a comparação do dia
    python3 scripts/sombra.py --semana              # junta os dias da sombra

Às 04:57 (o Mac acorda às 04:55 nos dias úteis; a produção começa às 05:00)
tira uma foto do projeto: os arquivos que o git conhece mais os novos que ele
não ignora, do jeito que estão, com o que ainda não foi commitado. É o estado
que a produção vai ver. Depois espera a produção do dia terminar bem; se ela
falhar e as repescagens também, a sombra não roda: a produção tem a vez.

Então roda as variantes de `config/sombra.json`, **uma depois da outra**,
nunca juntas: execuções ao mesmo tempo batem nos mesmos sites, e o arquivo
público já recusou o Jornalista por isso. A web mudar entre uma e outra é
risco aceito, e menor. Cada variante é um `scripts/ensaio.sh --estado FOTO`,
numa cópia fora do repositório, sem S3 e sem aviso: nada da sombra vai ao ar.

Depois passa o Verificador (Opus, rubrica v1, `prompts/verificador-sombra.md`)
no roteiro da produção e no de cada variante, também em fila, pela chave de
API do verificador e com teto de gasto por roteiro. Por fim escreve a
comparação em `logs/sombra-AAAA-MM-DD.md` (e uma cópia na pasta do dia).

Pastas e arquivos trocáveis para os testes: SOMBRA_DIR (onde ficam os dias,
padrão ~/CampsCast-ensaios/sombra), SOMBRA_CONFIG, SOMBRA_ORIGEM (o projeto
fotografado), SOMBRA_ENSAIO (o script de ensaio), METRICAS_ARQ (o registro da
produção), SOMBRA_INTERVALO (segundos entre olhadas na produção) e
SOMBRA_ESPERA_ATE (troca o "espera_producao_ate" da configuração).
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
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

ORIGEM = pathlib.Path(os.environ.get("SOMBRA_ORIGEM") or ROOT)
CONFIG = pathlib.Path(os.environ.get("SOMBRA_CONFIG") or ROOT / "config" / "sombra.json")
BASE = pathlib.Path(os.environ.get("SOMBRA_DIR") or pathlib.Path.home() / "CampsCast-ensaios" / "sombra")
ENSAIO = pathlib.Path(os.environ.get("SOMBRA_ENSAIO") or ROOT / "scripts" / "ensaio.sh")
METRICAS = pathlib.Path(os.environ.get("METRICAS_ARQ") or ORIGEM / "metricas" / "execucoes.jsonl")
CODIGO = ("scripts", "prompts", "config", "tests", ".claude", "CLAUDE.md")
# Variáveis que mudam o agente: cada variante parte do ambiente limpo delas,
# para a chave de uma não vazar para a seguinte.
CHAVES_DE_VARIANTE = ("BUSCA", "PARALLEL_MODO", "ANTHROPIC_DEFAULT_HAIKU_MODEL",
                      "JORNALISTA", "JORNALISTA_MODELO", "CLAUDE_BIN")


def diz(msg: str) -> None:
    print(f"[{dt.datetime.now():%H:%M:%S}] {msg}", flush=True)


def config() -> dict:
    c = json.loads(CONFIG.read_text(encoding="utf-8"))
    for v in c.get("variantes", []):
        for k in ("sobrepoe", "cli"):
            if v.get(k):
                v[k] = str(pathlib.Path(v[k]).expanduser())
    return c


def pasta_do_dia(dia: str) -> pathlib.Path:
    return BASE / dia


# ------------------------------------------------------------------ a foto

def tira_foto(destino: pathlib.Path) -> int:
    """Copia o que o git conhece e o que ele não ignora, como está agora."""
    r = subprocess.run(["git", "-C", str(ORIGEM), "ls-files", "-co", "--exclude-standard", "-z"],
                       capture_output=True, check=True)
    n = 0
    for nome in filter(None, r.stdout.decode().split("\0")):
        orig = ORIGEM / nome
        if not orig.is_file():  # apagado e ainda não commitado
            continue
        alvo = destino / nome
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(orig, alvo)
        n += 1
    return n


# ------------------------------------------------------------- a produção

def producao_ok(dia: str) -> bool:
    try:
        linhas = METRICAS.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    for l in linhas:
        try:
            r = json.loads(l)
        except ValueError:
            continue
        if r.get("data") == dia and r.get("estado") == "ok" and r.get("origem", "registrado") == "registrado":
            return True
    return False


def espera_producao(dia: str, ate: str) -> bool:
    h, m = (int(x) for x in ate.split(":"))
    limite = dt.datetime.combine(dt.date.fromisoformat(dia), dt.time(h, m))
    intervalo = float(os.environ.get("SOMBRA_INTERVALO", "60"))
    avisou = False
    while True:
        if producao_ok(dia):
            return True
        if dt.datetime.now() >= limite:
            return False
        if not avisou:
            diz(f"esperando a produção de {dia} terminar bem (até {ate})")
            avisou = True
        time.sleep(intervalo)


# ------------------------------------------------------------- variantes

def monta_codigo(v: dict, dia_dir: pathlib.Path) -> pathlib.Path:
    """O código da produção com os arquivos da variante por cima."""
    sobre = pathlib.Path(v["sobrepoe"])
    if not sobre.is_dir():
        raise SystemExit(f"sombra: variante {v['id']}: {sobre} não existe")
    dest = dia_dir / f"codigo-{v['id']}"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    ignora = shutil.ignore_patterns("__pycache__", "*.pyc", "launch.json", "settings.local.json")
    for item in CODIGO:
        orig = ROOT / item
        if orig.is_dir():
            shutil.copytree(orig, dest / item, ignore=ignora)
        elif orig.is_file():
            shutil.copy2(orig, dest / item)
    shutil.copytree(sobre, dest, dirs_exist_ok=True, ignore=ignora)
    return dest


def comando(v: dict, dia: str, foto: pathlib.Path, dia_dir: pathlib.Path, codigo: pathlib.Path | None):
    cmd = [str(ENSAIO), "--data", dia, "--estado", str(foto), "--pasta", str(dia_dir / v["id"])]
    if codigo:
        cmd += ["--codigo", str(codigo)]
    if v.get("cli"):
        cmd += ["--cli", v["cli"]]
    return cmd


def ambiente(v: dict) -> dict:
    env = {k: val for k, val in os.environ.items() if k not in CHAVES_DE_VARIANTE}
    env.update({k: str(val) for k, val in (v.get("env") or {}).items()})
    return env


def roda_variante(v: dict, dia: str, foto: pathlib.Path, dia_dir: pathlib.Path) -> dict:
    if v.get("cli") and not os.access(v["cli"], os.X_OK):
        diz(f"variante {v['id']}: CLI {v['cli']} não existe; pulada")
        return {"id": v["id"], "rc": None, "erro": "CLI não existe"}
    codigo = monta_codigo(v, dia_dir) if v.get("sobrepoe") else None
    cmd = comando(v, dia, foto, dia_dir, codigo)
    diz(f"variante {v['id']} ({v['nome']}): começa")
    inicio = time.time()
    with open(dia_dir / f"{v['id']}.out", "w", encoding="utf-8") as saida:
        rc = subprocess.run(cmd, stdout=saida, stderr=subprocess.STDOUT, env=ambiente(v), cwd=ROOT).returncode
    fim = time.time()
    diz(f"variante {v['id']}: terminou em {(fim - inicio) / 60:.1f} min (rc={rc})")
    return {"id": v["id"], "rc": rc, "inicio": inicio, "fim": fim}


# ------------------------------------------------------------- verificador

def chave_verificador() -> str:
    try:
        for l in (ORIGEM / ".env").read_text(encoding="utf-8").splitlines():
            if l.startswith("ANTHROPIC_API_KEY_VERIFICADOR="):
                return l.split("=", 1)[1].strip().strip("'\"")
    except OSError:
        pass
    return ""


def verifica(alvo: str, roteiro: pathlib.Path, log: pathlib.Path, dia_dir: pathlib.Path, cv: dict) -> dict:
    w = dia_dir / f"verif-{alvo}"
    if (w / "afirmacoes.jsonl").exists():
        return placar(w)
    if not roteiro.exists():
        return {"erro": "sem roteiro"}
    chave = chave_verificador()
    if not chave:
        diz("verificador: sem ANTHROPIC_API_KEY_VERIFICADOR no .env; pulado")
        return {"erro": "sem chave"}
    w.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "prompts" / "verificador-rubrica.md", w / "verificador-rubrica.md")
    shutil.copy2(roteiro, w / "ROTEIRO.md")
    if log.exists():
        shutil.copy2(log, w / "LOG.md")
    claude = os.environ.get("CLAUDE_BIN_VERIFICADOR") or shutil.which("claude") or "claude"
    env = {"HOME": str(pathlib.Path.home()), "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
           "ANTHROPIC_API_KEY": chave}
    diz(f"verificador: {alvo}")
    with open(w / "resultado.json", "w") as out, open(w / "erro.txt", "w") as err:
        subprocess.run([claude, "-p", (ROOT / "prompts" / "verificador-sombra.md").read_text(encoding="utf-8"),
                        "--model", cv.get("modelo", "claude-opus-5-5"), "--output-format", "json",
                        "--permission-mode", "acceptEdits",
                        "--allowedTools", "Read,Write,WebFetch,WebSearch",
                        "--strict-mcp-config", "--disable-slash-commands",
                        "--max-budget-usd", str(cv.get("teto_usd_por_roteiro", 5))],
                       stdout=out, stderr=err, env=env, cwd=w, stdin=subprocess.DEVNULL)
    return placar(w)


def placar(w: pathlib.Path) -> dict:
    p = {"verificaveis": 0, "erros": 0, "errados": 0, "regra8": 0}
    try:
        for l in (w / "afirmacoes.jsonl").read_text(encoding="utf-8").splitlines():
            try:
                a = json.loads(l)
            except ValueError:
                continue
            s = a.get("situacao")
            if s in ("confirmado", "impreciso", "errado"):
                p["verificaveis"] += 1
            if s in ("impreciso", "errado"):
                p["erros"] += 1
                p["errados"] += s == "errado"
                p["regra8"] += str(a.get("regra")) == "8"
    except OSError:
        p["erro"] = "sem afirmações"
    try:
        p["custo_usd"] = round(json.loads((w / "resultado.json").read_text()).get("total_cost_usd", 0), 2)
    except (OSError, ValueError):
        pass
    return p


# ------------------------------------------------------------- comparação

def resumo_execucao(raiz: pathlib.Path, dia: str, metricas: pathlib.Path | None = None) -> dict:
    """Custo, tempo, buscas, pautas e conferência de uma execução (produção ou cópia)."""
    r: dict = {}
    try:
        linhas = (metricas or raiz / "metricas" / "execucoes.jsonl").read_text(encoding="utf-8").splitlines()
        reg = [json.loads(l) for l in linhas if l.strip() and json.loads(l).get("data") == dia]
        if reg:
            x = reg[-1]
            c, t = x.get("claude") or {}, x.get("claude_transcricao") or {}
            r.update(estado=x.get("estado"), custo=c.get("custo_estimado_usd"), turnos=c.get("turnos"),
                     minutos=round((x.get("etapas_s") or {}).get("pesquisa", x.get("duracao_s", 0)) / 60, 1),
                     cli=x.get("claude_cli"), buscas=t.get("buscas"), buscas_parallel=t.get("buscas_parallel"),
                     leituras=t.get("leituras"), leituras_parallel=t.get("leituras_parallel"))
    except (OSError, ValueError):
        pass
    ep = raiz / "episodes" / f"{dia}.md"
    if ep.exists():
        texto = ep.read_text(encoding="utf-8")
        cab = texto.split("---")[1] if texto.startswith("---") else ""
        m = re.search(r"^words:\s*(\d+)", cab, re.M)
        r["palavras"] = int(m.group(1)) if m else None
        r["pautas"] = [t.strip().strip('"') for t in re.findall(r"^\s*-\s*title:\s*(.+)$", cab, re.M)]
    pesq = raiz / "research" / f"{dia}.md"
    if pesq.exists():
        sec = re.search(r"^## Conferência da certeza\n(.*?)(?=^## |\Z)", pesq.read_text(encoding="utf-8"), re.M | re.S)
        if sec:
            linhas = [l for l in sec.group(1).splitlines() if l.startswith("- ")]
            r["conferencia"] = len(linhas)
            r["corrigidas"] = sum("corrigida" in l for l in linhas)
    return r


def compara(dia: str, cfg: dict) -> str:
    dia_dir = pasta_do_dia(dia)
    precos = cfg.get("parallel_usd", {})
    linhas_exec = [("A", "Produção", resumo_execucao(ORIGEM, dia, METRICAS), dia_dir / "verif-A")]
    for v in cfg["variantes"]:
        linhas_exec.append((v["id"], v["nome"], resumo_execucao(dia_dir / v["id"], dia), dia_dir / f"verif-{v['id']}"))
    fmt = lambda x, nd=2: "—" if x is None else (f"{x:.{nd}f}" if isinstance(x, float) else str(x))
    out = [f"# Sombra de {dia}", "",
           "Produção (A) e variantes da sombra, no mesmo dia, a partir do mesmo estado; "
           "as variantes rodaram uma depois da outra, depois da produção. Nada da sombra foi ao ar.", "",
           "| | Variante | Estado | Custo | Pesquisa (min) | Turnos | Buscas | Leituras | Parallel (US$) "
           "| Palavras | Conferência (corrigidas) | Verificáveis | Erros | Regra 8 | Errado | Verificador (US$) |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    dados = {}
    for vid, nome, r, w in linhas_exec:
        p = placar(w) if (w / "afirmacoes.jsonl").exists() else {}
        bp, lp = r.get("buscas_parallel") or 0, r.get("leituras_parallel") or 0
        par = round(bp * precos.get("busca", 0) + lp * precos.get("leitura", 0), 3) if (bp or lp) else None
        buscas = f"{r.get('buscas') or 0}" + (f" + {bp} Parallel" if bp else "")
        leituras = f"{r.get('leituras') or 0}" + (f" + {lp} Parallel" if lp else "")
        taxa = f" ({100 * p['erros'] / p['verificaveis']:.1f}%)" if p.get("verificaveis") else ""
        out.append(f"| {vid} | {nome} | {fmt(r.get('estado'))} | {fmt(r.get('custo'))} | {fmt(r.get('minutos'), 1)} "
                   f"| {fmt(r.get('turnos'))} | {buscas} | {leituras} | {fmt(par, 3)} | {fmt(r.get('palavras'))} "
                   f"| {fmt(r.get('conferencia'))} ({fmt(r.get('corrigidas'))}) | {fmt(p.get('verificaveis'))} "
                   f"| {fmt(p.get('erros'))}{taxa} | {fmt(p.get('regra8'))} | {fmt(p.get('errados'))} "
                   f"| {fmt(p.get('custo_usd'))} |")
        dados[vid] = {"nome": nome, **r, "parallel_usd": par, "verificador": p}
    out += ["", "## Pautas", ""]
    for vid, nome, r, _ in linhas_exec:
        out.append(f"**{vid} · {nome}**")
        out += [f"- {t}" for t in r.get("pautas", [])] or ["- (sem roteiro)"]
        out.append("")
    texto = "\n".join(out) + "\n"
    (dia_dir / "comparacao.md").write_text(texto, encoding="utf-8")
    (dia_dir / "resumo.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    logs = ORIGEM / "logs"
    logs.mkdir(exist_ok=True)
    (logs / f"sombra-{dia}.md").write_text(texto, encoding="utf-8")
    return texto


def semana() -> str:
    """Soma os dias: erros por afirmação verificável e custo médio por variante."""
    tot: dict = {}
    dias = sorted(p.parent.name for p in BASE.glob("*/resumo.json"))
    for d in dias:
        for vid, x in json.loads((BASE / d / "resumo.json").read_text()).items():
            t = tot.setdefault(vid, {"nome": x["nome"], "dias": 0, "custo": 0.0, "ver": 0, "err": 0, "r8": 0, "errado": 0})
            t["dias"] += 1
            t["custo"] += x.get("custo") or 0
            p = x.get("verificador") or {}
            t["ver"] += p.get("verificaveis", 0); t["err"] += p.get("erros", 0)
            t["r8"] += p.get("regra8", 0); t["errado"] += p.get("errados", 0)
    out = [f"# Sombra: {len(dias)} dia(s) ({', '.join(dias)})", "",
           "| | Variante | Dias | Custo médio | Verificáveis | Erros | Regra 8 | Errado |", "|---|---|---|---|---|---|---|---|"]
    for vid, t in sorted(tot.items()):
        taxa = lambda n: f"{n} ({100 * n / t['ver']:.1f}%)" if t["ver"] else str(n)
        out.append(f"| {vid} | {t['nome']} | {t['dias']} | {t['custo'] / max(t['dias'], 1):.2f} | {t['ver']} "
                   f"| {taxa(t['err'])} | {taxa(t['r8'])} | {t['errado']} |")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ rotina

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="A sombra do dia: variantes em fila, depois da produção.")
    ap.add_argument("--rotina", action="store_true", help="o launchd: hoje, se houver episódio e a sombra valer")
    ap.add_argument("--data", help="AAAA-MM-DD (padrão: hoje)")
    ap.add_argument("--foto", type=pathlib.Path, help="usar uma foto já tirada")
    ap.add_argument("--so", help="só estas variantes, por id (B,E)")
    ap.add_argument("--sem-verificador", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--compara", action="store_true", help="só refaz a comparação do dia")
    ap.add_argument("--semana", action="store_true", help="junta os dias da sombra")
    a = ap.parse_args(argv)
    cfg = config()
    if a.semana:
        print(semana())
        return 0
    dia = a.data or dt.date.today().isoformat()
    if a.compara:
        print(compara(dia, cfg))
        return 0
    if a.rotina:
        if dia > cfg.get("ate", "9999-12-31"):
            diz(f"sombra encerrada em {cfg['ate']} (config/sombra.json); nada a fazer")
            return 0
        import schedule
        tem, motivo = schedule.avaliar(dt.date.fromisoformat(dia))
        if not tem:
            diz(f"sem episódio em {dia} ({motivo}); sem sombra")
            return 0
    variantes = [v for v in cfg["variantes"] if not a.so or v["id"] in a.so.split(",")]
    dia_dir = pasta_do_dia(dia)
    foto = a.foto or dia_dir / "foto"
    if a.dry_run:
        print(f"Sombra de {dia}: foto de {ORIGEM} em {foto}; espera a produção até "
              f"{os.environ.get('SOMBRA_ESPERA_ATE') or cfg['espera_producao_ate']}")
        for v in variantes:
            cod = dia_dir / f"codigo-{v['id']}" if v.get("sobrepoe") else None
            env = " ".join(f"{k}={val}" for k, val in (v.get("env") or {}).items())
            print(f"  {v['id']}: {env + ' ' if env else ''}{' '.join(comando(v, dia, foto, dia_dir, cod))}")
        print(f"  verificador: {'ligado' if cfg['verificador']['ligado'] and not a.sem_verificador else 'desligado'}"
              f" (A e {', '.join(v['id'] for v in variantes)}), um por vez")
        return 0

    dia_dir.mkdir(parents=True, exist_ok=True)
    trava = dia_dir / ".rodando"
    if trava.exists():
        diz(f"sombra de {dia} já está rodando ({trava}); saindo")
        return 0
    trava.write_text(str(os.getpid()))
    try:
        if not a.foto:
            if foto.exists():
                diz(f"foto de {dia} já existe; usando a que está lá")
            elif (ORIGEM / "logs" / f"{dia}.log").exists() or (ORIGEM / "episodes" / f"{dia}.md").exists():
                diz("a produção começou antes da foto: o estado já não é o de antes dela; sem sombra hoje")
                return 1
            else:
                n = tira_foto(foto)
                diz(f"foto tirada: {n} arquivos em {foto}")
        if not espera_producao(dia, os.environ.get("SOMBRA_ESPERA_ATE") or cfg["espera_producao_ate"]):
            diz("a produção não terminou bem até o limite; a sombra não roda (a produção tem a vez)")
            return 1
        diz("produção ok; começam as variantes, uma de cada vez")
        estado = [roda_variante(v, dia, foto, dia_dir) for v in variantes]
        (dia_dir / "sombra.json").write_text(json.dumps(estado, indent=1), encoding="utf-8")
        cv = cfg.get("verificador", {})
        if cv.get("ligado") and not a.sem_verificador:
            verifica("A", ORIGEM / "episodes" / f"{dia}.md", ORIGEM / "research" / f"{dia}.md", dia_dir, cv)
            for v in variantes:
                cop = dia_dir / v["id"]
                verifica(v["id"], cop / "episodes" / f"{dia}.md", cop / "research" / f"{dia}.md", dia_dir, cv)
        compara(dia, cfg)
        diz(f"comparação em logs/sombra-{dia}.md")
        return 0
    finally:
        trava.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
