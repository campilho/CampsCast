#!/usr/bin/env bash
#
# CampsCast — instala (ou reinstala) o agendamento no launchd.
#
# Gera o plist com os caminhos REAIS desta máquina em vez de pedir edição
# manual: o launchd não herda o PATH do shell, e um caminho errado só aparece
# às 5h50, sem ninguém por perto.
#
#   scripts/install_launchd.sh              # instala e carrega
#   scripts/install_launchd.sh --uninstall  # remove
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL="com.camps.campscast"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
UID_NUM="$(id -u)"

if [[ "${1:-}" == "--uninstall" ]]; then
  launchctl bootout "gui/$UID_NUM/$LABEL" 2>/dev/null || true
  rm -f "$PLIST"
  echo "Agendamento removido."
  exit 0
fi

# --- pastas protegidas pelo TCC ---
# Agente do launchd não acessa ~/Documents, ~/Desktop nem ~/Downloads. O erro
# é "Operation not permitted" (rc=126) e não diz nada sobre permissão de disco.
case "$ROOT" in
  "$HOME"/Documents/*|"$HOME"/Desktop/*|"$HOME"/Downloads/*)
    echo "ERRO: o projeto está em $ROOT." >&2
    echo "O macOS bloqueia agentes do launchd nessas pastas (TCC). Mova o" >&2
    echo "projeto para fora delas — por exemplo ~/CampsCast — e rode de novo." >&2
    exit 1 ;;
esac

CLAUDE_BIN="$(command -v claude || true)"
PY_BIN="$(command -v python3 || true)"
[[ -n "$CLAUDE_BIN" ]] || { echo "ERRO: 'claude' não está no PATH." >&2; exit 1; }
[[ -n "$PY_BIN" ]] || { echo "ERRO: 'python3' não está no PATH." >&2; exit 1; }

PATH_ENTRIES="$(dirname "$CLAUDE_BIN"):$(dirname "$PY_BIN"):/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

mkdir -p "$HOME/Library/LaunchAgents" "$ROOT/logs"

{
  echo '<?xml version="1.0" encoding="UTF-8"?>'
  echo "<!-- Gerado por scripts/install_launchd.sh. Não edite: regenere. -->"
  echo '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">'
  echo '<plist version="1.0"><dict>'
  echo "  <key>Label</key><string>$LABEL</string>"
  echo '  <key>ProgramArguments</key><array>'
  echo '    <string>/bin/bash</string>'
  echo "    <string>$ROOT/scripts/run_episode.sh</string>"
  echo '  </array>'
  echo "  <key>WorkingDirectory</key><string>$ROOT</string>"
  echo '  <key>EnvironmentVariables</key><dict>'
  echo "    <key>PATH</key><string>$PATH_ENTRIES</string>"
  echo '  </dict>'
  # Três horários por dia, não um. O launchd nunca roda duas instâncias do
  # mesmo job em paralelo, e a invariante da janela torna a repescagem
  # inofensiva: se o episódio do dia já saiu, a execução seguinte encerra em
  # um segundo com "nada novo a cobrir". Se a primeira falhou — máquina
  # dormindo, rede fora, fonte no ar — a segunda ou a terceira pega.
  echo '  <key>StartCalendarInterval</key><array>'
  for d in 1 2 3 4 5; do
    for hm in "5 50" "6 20" "7 00"; do
      set -- $hm
      echo "    <dict><key>Weekday</key><integer>$d</integer><key>Hour</key><integer>$1</integer><key>Minute</key><integer>$2</integer></dict>"
    done
  done
  echo '  </array>'
  echo "  <key>StandardOutPath</key><string>$ROOT/logs/launchd.out.log</string>"
  echo "  <key>StandardErrorPath</key><string>$ROOT/logs/launchd.err.log</string>"
  echo '  <key>RunAtLoad</key><false/>'
  echo '</dict></plist>'
} > "$PLIST"

plutil -lint "$PLIST" >/dev/null || { echo "ERRO: plist inválido." >&2; exit 1; }

launchctl bootout "gui/$UID_NUM/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$UID_NUM" "$PLIST"

echo "Instalado: $PLIST"
echo "  projeto : $ROOT"
echo "  claude  : $CLAUDE_BIN"
echo "  python3 : $PY_BIN"
echo "  horário : segunda a sexta, 05:50 (repescagem 06:20 e 07:00)"
echo
echo "Disparar agora:  launchctl kickstart -k gui/$UID_NUM/$LABEL"
echo "Ver status    :  launchctl list | grep campscast"
echo "Logs          :  tail -f $ROOT/logs/launchd.out.log"
