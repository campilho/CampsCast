#!/usr/bin/env bash
#
# CampsCast — ensaio de um dia de episódio, numa cópia isolada.
#
# Roda a etapa do agente para um dia, com o repositório como estava antes
# daquele dia e o código de agora (ou de outra pasta), no ambiente do launchd.
# É a régua do ADR 0010: comparar variantes do agente sem tocar na produção.
#
# Uso:
#   scripts/ensaio.sh --data 2026-10-29                # estado do último commit antes do dia
#   scripts/ensaio.sh --data 2026-10-29 --de b54818b   # estado de um commit escolhido
#   scripts/ensaio.sh --data 2026-10-29 --codigo DIR   # scripts, prompts e config de outra pasta
#   scripts/ensaio.sh --data 2026-10-29 --dry-run      # monta a cópia e mostra o que rodaria
#   scripts/ensaio.sh --data 2026-10-29 --pasta DIR    # onde montar (padrão ~/CampsCast-ensaios/)
#   scripts/ensaio.sh --data 2026-11-02 --force        # dia sem episódio
#   JORNALISTA=1 scripts/ensaio.sh --data 2026-11-06   # com o Jornalista (plano de leitura)
#
# A cópia é a árvore de um commit (episódios, memória, backlog, índice) com o
# código por cima: scripts/, prompts/, config/, tests/, .claude/ e CLAUDE.md da
# pasta de código. Fica fora do repositório — dentro dele, o Claude Code
# carregaria também o CLAUDE.md da pasta de cima. Leva do .env só o token do
# Claude: sem chave da AWS, da ElevenLabs nem do e-mail. O upload ao S3 e o
# aviso são trocados por versões que recusam, e o estado vai para um arquivo
# local. Roda só a etapa do agente, com `env -i` e o PATH do plist.
#
# Os commits juntam vários dias, então só o dia seguinte a um commit tem o
# estado exato. Nos outros a janela de notícias sai diferente da que a produção
# teve, e o ensaio avisa. Para comparar duas variantes entre si, basta que as
# duas partam do mesmo commit.
#
# Diferenças conhecidas da produção: a web é a de hoje, não a do dia; e a
# memória automática do Claude Code (MEMORY.md), que a produção carrega por
# morar na pasta do projeto, não existe na cópia.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

DATA=""; REF=""; CODIGO="$ROOT"; PASTA=""; DRY_RUN=0; FORCE=0
# Dados vêm do git desta pasta; o teste aponta para um repositório de mentira.
ORIGEM="${ENSAIO_ORIGEM:-$ROOT}"
ENV_ARQ="${ENSAIO_ENV:-$ROOT/.env}"
PLIST="${ENSAIO_PLIST:-$HOME/Library/LaunchAgents/com.camps.campscast.plist}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --data)    DATA="$2"; shift 2 ;;
    --de)      REF="$2"; shift 2 ;;
    --codigo)  CODIGO="$(cd "$2" && pwd)"; shift 2 ;;
    --pasta)   PASTA="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --force)   FORCE=1; shift ;;
    -h|--help) sed -n '2,34p' "$0"; exit 0 ;;
    *) echo "Argumento desconhecido: $1" >&2; exit 2 ;;
  esac
done

die() { echo "ensaio: $*" >&2; exit 1; }

[[ -n "$DATA" ]] || die "falta --data AAAA-MM-DD."
python3 -c "import datetime, sys; datetime.date.fromisoformat(sys.argv[1])" "$DATA" 2>/dev/null \
  || die "data inválida: $DATA"

# ---------- de que commit parte ----------
episodios_em() {
  git -C "$ORIGEM" ls-tree --name-only "$1" episodes/ \
    | sed -n 's|^episodes/\([0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}\)\.md$|\1|p' | sort
}
# O commit já tem o episódio do dia (ou um posterior)? Então o agente acharia
# o dia feito, e a janela não faria sentido.
tem_a_partir() {
  local d
  while IFS= read -r d; do
    [[ "$d" > "$DATA" || "$d" == "$DATA" ]] && return 0
  done < <(episodios_em "$1")
  return 1
}

if [[ -z "$REF" ]]; then
  for c in $(git -C "$ORIGEM" rev-list HEAD); do
    if ! tem_a_partir "$c"; then REF="$c"; break; fi
  done
  [[ -n "$REF" ]] || die "nenhum commit sem episódio em $DATA ou depois."
else
  REF="$(git -C "$ORIGEM" rev-parse --verify --quiet "${REF}^{commit}")" || die "commit não encontrado."
  if tem_a_partir "$REF"; then
    die "o commit já tem episódio em $DATA ou depois; escolha um anterior."
  fi
fi

ULTIMO="$(episodios_em "$REF" | tail -1)"
ANTERIOR="$(episodios_em HEAD | awk -v d="$DATA" '$0 < d' | tail -1)"
EXATO=1
[[ "$ULTIMO" == "$ANTERIOR" ]] || EXATO=0

PASTA="${PASTA:-$HOME/CampsCast-ensaios/${DATA}-$(date +%Y%m%d-%H%M%S)}"
[[ "$PASTA" == /* ]] || PASTA="$PWD/$PASTA"
[[ ! -e "$PASTA" ]] || die "$PASTA já existe."
case "$PASTA/" in
  "$ROOT"/*|"$ORIGEM"/*|"$CODIGO"/*) die "a cópia precisa ficar fora do repositório e da pasta de código." ;;
esac

echo "Ensaio de $DATA"
echo "  estado:  $(git -C "$ORIGEM" log -1 --format='%h de %ad · %s' --date=format:'%d/%m %H:%M' "$REF")"
echo "  último episódio no estado: ${ULTIMO:-nenhum}; na produção, antes de $DATA: ${ANTERIOR:-nenhum}"
if [[ $EXATO -eq 0 ]]; then
  echo "  AVISO: estado inexato. A janela vai sair diferente da que a produção teve;"
  echo "         serve para comparar variantes entre si, não com o episódio publicado."
fi
echo "  código:  $CODIGO"
echo "  cópia:   $PASTA"

# ---------- monta a cópia ----------
umask 077
mkdir -p "$PASTA"
git -C "$ORIGEM" archive "$REF" | tar -x -C "$PASTA"

for item in scripts prompts config tests .claude CLAUDE.md; do
  [[ -e "$CODIGO/$item" ]] || continue
  rm -rf "${PASTA:?}/$item"
  rsync -a --exclude '__pycache__' --exclude '*.pyc' --exclude 'launch.json' \
    --exclude 'settings.local.json' "$CODIGO/$item" "$PASTA/"
done

# Nada sai daqui: o S3 recusa na importação, e o aviso só escreve na tela.
cat > "$PASTA/scripts/s3.py" <<'PY'
"""Ensaio (scripts/ensaio.sh): o upload ao S3 está desligado nesta cópia."""
raise SystemExit("ensaio: upload ao S3 desligado nesta cópia")
PY
cat > "$PASTA/scripts/notify.py" <<'PY'
"""Ensaio (scripts/ensaio.sh): o aviso está desligado nesta cópia."""
print("ensaio: aviso desligado nesta cópia")
PY

# Do .env, só o que o agente precisa para rodar como na produção.
: > "$PASTA/.env"
if [[ -f "$ENV_ARQ" ]]; then
  grep -E '^[[:space:]]*(CLAUDE_CODE_OAUTH_TOKEN|CLAUDE_BIN)=' "$ENV_ARQ" > "$PASTA/.env" || true
fi
mkdir -p "$PASTA/logs" "$PASTA/audio" "$PASTA/feed" "$PASTA/metricas"

PATH_LAUNCHD="$(plutil -extract EnvironmentVariables.PATH raw -o - "$PLIST" 2>/dev/null || true)"
if [[ -z "$PATH_LAUNCHD" ]]; then
  # Sem o plist instalado, o mesmo PATH que scripts/install_launchd.sh montaria.
  PATH_LAUNCHD="$(dirname "$(command -v claude || echo /usr/local/bin/claude)"):$(dirname "$(command -v python3)"):/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
fi

CODIGO_COMMIT="$(git -C "$CODIGO" rev-parse --short HEAD 2>/dev/null || echo "")"
CODIGO_SUJO="$(git -C "$CODIGO" status --porcelain -- scripts prompts config 2>/dev/null | head -1 || true)"
DATA="$DATA" REF="$REF" ULTIMO="$ULTIMO" ANTERIOR="$ANTERIOR" EXATO="$EXATO" CODIGO="$CODIGO" \
CODIGO_COMMIT="$CODIGO_COMMIT" CODIGO_SUJO="$CODIGO_SUJO" PATH_LAUNCHD="$PATH_LAUNCHD" \
python3 - "$PASTA/ENSAIO.json" <<'PY'
import datetime, json, os, sys
e = os.environ
json.dump({
    "data": e["DATA"], "estado_commit": e["REF"], "ultimo_no_estado": e["ULTIMO"] or None,
    "anterior_na_producao": e["ANTERIOR"] or None, "estado_exato": e["EXATO"] == "1",
    "codigo": e["CODIGO"], "codigo_commit": e["CODIGO_COMMIT"] or None,
    "codigo_com_mudancas": bool(e["CODIGO_SUJO"]), "path": e["PATH_LAUNCHD"],
    "montado_em": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
}, open(sys.argv[1], "w"), ensure_ascii=False, indent=2)
PY

# Repositório próprio: o agente vê um git como na produção, e o diff depois
# mostra tudo o que ele escreveu.
git -C "$PASTA" init -q -b main
git -C "$PASTA" add -A
git -C "$PASTA" -c user.name=ensaio -c user.email=ensaio@localhost \
  commit -q -m "Estado de $(git -C "$ORIGEM" rev-parse --short "$REF") com o código de $CODIGO"

# ---------- roda, no ambiente do launchd ----------
ARGS=(--date "$DATA" --only research)
[[ $DRY_RUN -eq 1 ]] && ARGS+=(--dry-run)
[[ $FORCE -eq 1 ]] && ARGS+=(--force)
# As variáveis com que a suíte roda sem rede e sem ler o pmset passam, se
# existirem. Fora do teste nenhuma existe, e o ambiente é o do launchd.
TESTE=()
for v in REDE_HOST REDE_ESPERA_S REGISTRO_SEM_SONO; do
  [[ -n "${!v:-}" ]] && TESTE+=("$v=${!v}")
done
# As chaves das variantes em comparação também passam, se vierem: é assim que
# se ensaia o Jornalista (JORNALISTA=1 scripts/ensaio.sh --data …) e o modelo
# pequeno do CLI, que resume as páginas e faz as buscas
# (ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-haiku-5-5 scripts/ensaio.sh --data …).
for v in JORNALISTA JORNALISTA_MODELO ANTHROPIC_DEFAULT_HAIKU_MODEL; do
  [[ -n "${!v:-}" ]] && TESTE+=("$v=${!v}")
done
# A varredura dos feeds (scripts/varredura.py) lê os feeds de agora, não os do
# dia ensaiado: num dia passado, a lista não seria a que a produção teria
# visto. Desligada no ensaio, a menos que se peça (VARREDURA=1).
TESTE+=("VARREDURA=${VARREDURA:-0}")
# A leitura do limite do Max (scripts/limites_max.py) mede a produção; no
# ensaio fica desligada, a menos que se peça (LIMITES_MAX=1).
TESTE+=("LIMITES_MAX=${LIMITES_MAX:-0}")
echo
set +e
env -i HOME="$HOME" USER="${USER:-}" LOGNAME="${LOGNAME:-${USER:-}}" SHELL="${SHELL:-/bin/zsh}" \
  TMPDIR="${TMPDIR:-/tmp}" PATH="$PATH_LAUNCHD" ESTADO_ARQ="$PASTA/logs/estado.json" \
  ${TESTE[@]+"${TESTE[@]}"} /bin/bash "$PASTA/scripts/run_episode.sh" "${ARGS[@]}"
RC=$?
set -e

# ---------- resumo, lado a lado com a produção ----------
echo
python3 - "$PASTA" "$ORIGEM" "$ROOT" "$DATA" <<'PY'
import json, pathlib, subprocess, sys
pasta, origem, raiz, data = (pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]),
                             pathlib.Path(sys.argv[3]), sys.argv[4])
sys.path.insert(0, str(raiz / "scripts"))
from publish import parse_front_matter

def execucao(arq):
    # A última execução do dia que deu certo; sem nenhuma, a última que houve.
    do_dia = []
    if arq.exists():
        for l in arq.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            if r.get("data") == data:
                do_dia.append(r)
    ok = [r for r in do_dia if r.get("estado") == "ok"]
    return (ok or do_dia or [{}])[-1]

def episodio(arq):
    if not arq.exists():
        return {}
    fm = parse_front_matter(arq.read_text(encoding="utf-8"))
    return {"palavras": fm.get("words"), "titulo": fm.get("title"),
            "pautas": [t.get("title", "") for t in fm.get("topics") or [] if isinstance(t, dict)]}

def linha(r, ep):
    c = r.get("claude") or {}
    custo = c.get("custo_estimado_usd")
    return [r.get("estado", "—"), c.get("turnos", "—"),
            f"{custo:.2f}" if isinstance(custo, (int, float)) else "—",
            f"{(c.get('cache_lido') or 0) / 1e6:.1f} M" if c else "—",
            f"{(c.get('saida') or 0) / 1e3:.0f} mil" if c else "—",
            f"{(r.get('etapas_s') or {}).get('pesquisa', 0) / 60:.1f}" if r else "—",
            ep.get("palavras", "—")]

ens = linha(execucao(pasta / "metricas" / "execucoes.jsonl"), episodio(pasta / "episodes" / f"{data}.md"))
prod = linha(execucao(origem / "metricas" / "execucoes.jsonl"), episodio(origem / "episodes" / f"{data}.md"))
print(f"{'':16}{'ensaio':>12}{'produção':>12}")
for nome, a, b in zip(["estado", "turnos", "custo (US$)", "cache lido", "saída", "minutos", "palavras"], ens, prod):
    print(f"{nome:16}{str(a):>12}{str(b):>12}")
for quem, arq in (("ensaio", pasta), ("produção", origem)):
    ep = episodio(arq / "episodes" / f"{data}.md")
    if ep.get("pautas"):
        print(f"\nPautas — {quem}:")
        for t in ep["pautas"]:
            print(f"  · {t}")
mudou = subprocess.run(["git", "-C", str(pasta), "status", "--short"], capture_output=True, text=True).stdout
if mudou.strip():
    print("\nO que o agente escreveu na cópia (git -C <cópia> diff para ver):")
    print("".join(f"  {l}\n" for l in mudou.splitlines()), end="")
PY
echo
echo "Cópia: $PASTA (log em logs/$DATA.log; apague a pasta quando não precisar mais)"
exit $RC
