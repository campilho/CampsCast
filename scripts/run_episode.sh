#!/usr/bin/env bash
#
# CampsCast — orquestrador de episódio.
# Tick determinístico (launchd) -> execução agêntica (claude -p headless).
#
# Uso:
#   scripts/run_episode.sh                       # pipeline completo, data = hoje
#   scripts/run_episode.sh --date 2026-08-24     # data específica
#   scripts/run_episode.sh --only research       # só uma etapa
#   scripts/run_episode.sh --skip publish,notify # pula etapas
#   scripts/run_episode.sh --dry-run             # mostra o que faria, não executa
#   scripts/run_episode.sh --overwrite           # regrava um episódio existente
#   scripts/run_episode.sh --force               # roda em dia sem episódio
#
# Janela de notícias: calculada por scripts/window.py a partir do último dia já
# coberto por algum episódio. Rodar no sábado ou no domingo é permitido e não
# duplica pauta — a execução seguinte simplesmente começa de onde esta parou.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# ---------- .env ----------
# Uma variável já presente no ambiente TEM PRECEDÊNCIA sobre o .env. Isso
# importa: `source .env` com `set -a` sobrescreveria um CLAUDE_BIN passado na
# linha de comando, e os testes (que injetam um CLI falso) acabariam chamando
# o Claude de verdade. Mesma semântica do os.environ.setdefault dos scripts .py.
if [[ -f .env ]]; then
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%$'\r'}"
    if [[ -z "${line// }" || "$line" == \#* || "$line" != *=* ]]; then
      continue
    fi
    key="${line%%=*}"
    val="${line#*=}"
    key="${key// }"
    if [[ -z "$key" ]]; then continue; fi
    val="${val%\"}"; val="${val#\"}"
    val="${val%\'}"; val="${val#\'}"
    if [[ -z "${!key:-}" ]]; then export "$key=$val"; fi
  done < .env
fi

CLAUDE_BIN="${CLAUDE_BIN:-claude}"

# ---------- args ----------
EPISODE_DATE=""
DRY_RUN=0
OVERWRITE=0
FORCE_DAY=0
ONLY=""
SKIP=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --date)    EPISODE_DATE="$2"; shift 2 ;;
    --only)    ONLY="$2"; shift 2 ;;
    --skip)    SKIP="$2"; shift 2 ;;
    --dry-run)   DRY_RUN=1; shift ;;
    --overwrite) OVERWRITE=1; shift ;;
    --force)     FORCE_DAY=1; shift ;;
    -h|--help)   sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "Argumento desconhecido: $1" >&2; exit 2 ;;
  esac
done

EPISODE_DATE="${EPISODE_DATE:-$(date +%F)}"

# ---------- manter o Mac acordado ----------
# O episódio leva uns 8 minutos. `pmset -c sleep 0` impede o sono por
# inatividade, mas não o sono por tampa fechada — e o despertar agendado do
# pmset devolve a máquina para o sono pouco depois se nada a segurar. Sem isto,
# a execução pode ser cortada no meio, deixando episódio ou upload pela metade.
# O caffeinate morre junto com este script (-w $$), então nada fica preso.
if command -v caffeinate >/dev/null 2>&1; then
  caffeinate -i -m -s -w $$ &
fi

# ---------- logging ----------
mkdir -p logs
LOG="logs/${EPISODE_DATE}.log"
log() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*" | tee -a "$LOG"; }
die() { log "ERRO: $*"; exit 1; }

stage_enabled() {
  local s="$1"
  if [[ -n "$ONLY" ]]; then [[ ",$ONLY," == *",$s,"* ]] && return 0 || return 1; fi
  [[ ",$SKIP," == *",$s,"* ]] && return 1 || return 0
}

run() {
  if [[ $DRY_RUN -eq 1 ]]; then log "DRY-RUN: $*"; return 0; fi
  "$@"
}

# ---------- há episódio hoje? ----------
# Dias úteis, feriados e exceções vivem em config/schedule.json, não aqui:
# quem clonar o projeto pode estar em outro país, ou querer publicar no sábado.
# Pular um dia não perde notícia — a janela do episódio seguinte cobre o buraco.
if [[ $FORCE_DAY -eq 0 ]]; then
  if ! MOTIVO="$(python3 scripts/schedule.py --date "$EPISODE_DATE" 2>/dev/null)"; then
    mkdir -p logs
    printf '[%s] %s\n' "$(date +%H:%M:%S)" "${MOTIVO:-sem episódio hoje}" \
      | tee -a "logs/${EPISODE_DATE}.log"
    printf '[%s] Nada a fazer. Use --force para rodar assim mesmo.\n' \
      "$(date +%H:%M:%S)" | tee -a "logs/${EPISODE_DATE}.log"
    exit 0
  fi
fi

# ---------- janela de notícias ----------
# Regra: cobre do dia seguinte ao último dia já coberto até ontem. Hoje nunca
# entra. Ver scripts/window.py — inclusive para o comportamento de partida a frio.
WINDOW_EVAL="$(python3 scripts/window.py --date "$EPISODE_DATE")" \
  || die "Falha ao calcular a janela de notícias para $EPISODE_DATE."
eval "$WINDOW_EVAL"

# ---------- tamanho do roteiro ----------
# Derivado do ritmo da voz configurada: trocar de voz muda quantas palavras
# cabem nos 5 a 10 minutos do formato.
BUDGET_EVAL="$(python3 scripts/tts.py --budget 2>/dev/null)" || BUDGET_EVAL=""
if [[ -n "$BUDGET_EVAL" ]]; then eval "$BUDGET_EVAL"; fi

# ---------- ficha técnica do encerramento ----------
# O agente cita o que narra o episódio. Sai da config, não de memória dele:
# trocar de voz ou de modelo muda o texto falado sem ninguém editar o prompt.
TTS_NOME="$(python3 -c "
import json;d=json.load(open('config/tts.json'))
print(d.get('_nome_falado', d['model_id']))" 2>/dev/null || echo "")"
TTS_VOZ="$(python3 -c "
import json;d=json.load(open('config/tts.json'))
print(d.get('_voz_falada','uma voz sintetizada'))" 2>/dev/null || echo "")"

SCRIPT_PATH="episodes/${EPISODE_DATE}.md"
AUDIO_PATH="audio/${EPISODE_DATE}.mp3"

DOW="$(date -j -f %Y-%m-%d "$EPISODE_DATE" +%u)"

log "════ CampsCast — episódio ${EPISODE_DATE} ════"
if [[ $DRY_RUN -eq 1 ]]; then log "MODO DRY-RUN — nada será executado de verdade."; fi
if [[ "$DOW" -ge 6 ]]; then
  log "Fim de semana: execução manual. A janela abaixo já evita duplicar pauta."
fi

log "Último episódio: ${LAST_EPISODE:-nenhum} — ${WINDOW_ORIGIN}"

# A janela só governa a etapa de pesquisa. Renarrar ou republicar um episódio
# que já existe não depende dela — e bloquear isso impediria retomar um
# pipeline que falhou no meio.
if [[ "$WINDOW_STATUS" != "ok" ]]; then
  if stage_enabled research; then
    log "$NEWS_WINDOW"
    log "Nada a fazer. Para forçar assim mesmo, apague ou ajuste o episódio anterior."
    exit 0
  fi
  log "Janela vazia, mas a etapa de pesquisa está fora desta execução — seguindo."
fi

if [[ "$WINDOW_STATUS" == "ok" ]]; then
  log "Janela: ${WINDOW_START} → ${WINDOW_END} (${WINDOW_DAYS} dia(s))"
fi
if [[ -n "${WORD_TARGET:-}" ]]; then
  log "Roteiro: ${WORD_MIN}–${WORD_MAX} palavras, alvo ${WORD_TARGET} (voz a ${WORDS_PER_MINUTE} ppm)"
fi
if [[ "$WINDOW_CLAMPED" == "1" ]]; then
  log "AVISO: janela truncada em 7 dias após uma parada longa."
fi

# Não sobrepor um episódio que já existe.
if [[ -f "$SCRIPT_PATH" && $OVERWRITE -eq 0 ]] && stage_enabled research; then
  die "$SCRIPT_PATH já existe. Use --overwrite para regravar, ou --skip research para reaproveitá-lo."
fi

# ---------- 1. pesquisa + roteiro (agente) ----------
if stage_enabled research; then
  log "── [1/4] Pesquisa e roteiro (claude -p headless)"

  if ! command -v "$CLAUDE_BIN" >/dev/null 2>&1; then
    MSG="'$CLAUDE_BIN' não encontrado no PATH. Instale o Claude Code CLI (npm i -g @anthropic-ai/claude-code) ou defina CLAUDE_BIN no .env."
    # Em dry-run isso é só um aviso: a etapa não vai rodar mesmo.
    if [[ $DRY_RUN -eq 1 ]]; then log "AVISO: $MSG"; else die "$MSG"; fi
  fi

  [[ -f prompts/master.md ]] || die "prompts/master.md não encontrado."

  export EPISODE_DATE NEWS_WINDOW WINDOW_START WINDOW_END WINDOW_DAYS
  export WORD_MIN WORD_TARGET WORD_MAX WORDS_PER_MINUTE
  export TTS_NOME TTS_VOZ

  if [[ $DRY_RUN -eq 1 ]]; then
    log "DRY-RUN: $CLAUDE_BIN -p \"\$(cat prompts/master.md)\" --permission-mode acceptEdits"
  else
    # A etapa demora vários minutos e a saída do CLI só chega no fim, porque
    # precisa ser capturada inteira para ser validada. Sem isso o terminal fica
    # mudo e parece travado. O watcher lê a transcrição que o próprio CLI grava
    # e espelha a atividade no terminal e no log, em segundo plano.
    # stdout fica solto de propósito: é ele que aparece no terminal ao vivo.
    python3 scripts/watch_agent.py --newer-than "$(date +%s)" \
      --log "$LOG" --prefix "           " --quiet 2>/dev/null &
    WATCHER_PID=$!

    set +e
    AGENT_OUT="$(
      "$CLAUDE_BIN" -p "$(cat prompts/master.md)" \
        --permission-mode acceptEdits \
        --allowedTools "Read,Write,Edit,Glob,Grep,WebSearch,WebFetch" \
        2>>"$LOG"
    )"
    AGENT_RC=$?
    set -e

    if [[ -n "$WATCHER_PID" ]]; then
      kill "$WATCHER_PID" 2>/dev/null || true
      wait "$WATCHER_PID" 2>/dev/null || true
    fi
    log "Agente retornou: ${AGENT_OUT:-<vazio>} (rc=$AGENT_RC)"

    # Falta de login é o tropeço mais comum na primeira execução: instalar o
    # CLI não autentica, e o armazenamento de credenciais dele é separado do
    # app desktop. Vale diagnosticar em vez de repassar o erro cru.
    if [[ "$AGENT_OUT" == *"Not logged in"* || "$AGENT_OUT" == *"/login"* \
          || "$AGENT_OUT" == *"Invalid API key"* || "$AGENT_OUT" == *"authentication"* ]]; then
      log "──────────────────────────────────────────────────────────────"
      log "O Claude Code CLI está instalado mas não autenticado."
      log "Rode uma vez, no Terminal (é interativo):"
      log "    claude"
      log "e dentro dele: /login  — depois /exit."
      log "Instalar o CLI não autentica, e o login do app desktop não vale"
      log "para o CLI: são armazenamentos de credenciais diferentes."
      log "──────────────────────────────────────────────────────────────"
      die "Agente não autenticado."
    fi

    if [[ $AGENT_RC -ne 0 ]]; then die "claude -p falhou (rc=$AGENT_RC). Veja $LOG."; fi
    if [[ "$AGENT_OUT" == FAIL* ]]; then die "Agente reportou falha: $AGENT_OUT"; fi
  fi

  if [[ $DRY_RUN -eq 0 && ! -f "$SCRIPT_PATH" ]]; then
    die "Roteiro não foi criado em $SCRIPT_PATH."
  fi
  log "Roteiro: $SCRIPT_PATH"
else
  log "── [1/4] Pesquisa — PULADA"
fi

# ---------- 2. TTS ----------
if stage_enabled tts; then
  log "── [2/4] TTS (ElevenLabs)"
  if [[ $DRY_RUN -eq 0 && ! -f "$SCRIPT_PATH" ]]; then
    die "Sem roteiro em $SCRIPT_PATH para narrar."
  fi
  run python3 scripts/tts.py --script "$SCRIPT_PATH" --out "$AUDIO_PATH" 2>&1 | tee -a "$LOG"
  log "Áudio: $AUDIO_PATH"
else
  log "── [2/4] TTS — PULADA"
fi

# ---------- 3. publicação ----------
if stage_enabled publish; then
  log "── [3/4] Publicação (feed.xml + S3)"
  run python3 scripts/publish.py --date "$EPISODE_DATE" 2>&1 | tee -a "$LOG"
else
  log "── [3/4] Publicação — PULADA"
fi

# ---------- 4. notificação ----------
if stage_enabled notify; then
  log "── [4/4] Notificação"
  run python3 scripts/notify.py --date "$EPISODE_DATE" --script "$SCRIPT_PATH" --audio "$AUDIO_PATH" 2>&1 | tee -a "$LOG"
else
  log "── [4/4] Notificação — PULADA"
fi

log "════ Concluído ════"
