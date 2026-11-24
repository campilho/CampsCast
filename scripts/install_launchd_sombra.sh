#!/usr/bin/env bash
#
# CampsCast — instala (ou remove) o agendamento da sombra do dia no launchd.
#
# Um job à parte da produção: de segunda a sexta às 04:57 (o Mac acorda às
# 04:55; a produção começa às 05:00), scripts/sombra.py --rotina tira a foto
# do projeto, espera a produção terminar bem e roda as variantes de
# config/sombra.json uma depois da outra. Depois do "ate" da configuração, o
# job sai sem fazer nada; remova-o com --uninstall quando a semana acabar.
#
#   scripts/install_launchd_sombra.sh              # instala e carrega
#   scripts/install_launchd_sombra.sh --print      # só mostra o plist
#   scripts/install_launchd_sombra.sh --uninstall  # remove
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL="com.camps.campscast.sombra"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
UID_NUM="$(id -u)"

if [[ "${1:-}" == "--uninstall" ]]; then
  launchctl bootout "gui/$UID_NUM/$LABEL" 2>/dev/null || true
  rm -f "$PLIST"
  echo "Agendamento da sombra removido."
  exit 0
fi

# Agente do launchd não acessa ~/Documents, ~/Desktop nem ~/Downloads (TCC).
case "$ROOT" in
  "$HOME"/Documents/*|"$HOME"/Desktop/*|"$HOME"/Downloads/*)
    echo "ERRO: o projeto está em $ROOT; o launchd não roda nessas pastas." >&2
    exit 1 ;;
esac

CLAUDE_BIN="$(command -v claude || true)"
PY_BIN="$(command -v python3 || true)"
[[ -n "$PY_BIN" ]] || { echo "ERRO: 'python3' não está no PATH." >&2; exit 1; }
if [[ -z "$CLAUDE_BIN" && "${1:-}" != "--print" ]]; then
  echo "ERRO: 'claude' não está no PATH." >&2; exit 1
fi
PATH_ENTRIES="$(dirname "${CLAUDE_BIN:-/usr/local/bin/claude}"):$(dirname "$PY_BIN"):/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

gera() {
  echo '<?xml version="1.0" encoding="UTF-8"?>'
  echo '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">'
  echo "<!-- Gerado por scripts/install_launchd_sombra.sh. Não edite: regenere. -->"
  echo '<plist version="1.0"><dict>'
  echo "  <key>Label</key><string>$LABEL</string>"
  # caffeinate -i: o Mac não dorme enquanto as variantes e o verificador rodam.
  echo '  <key>ProgramArguments</key><array>'
  echo '    <string>/usr/bin/caffeinate</string><string>-i</string>'
  echo "    <string>$PY_BIN</string>"
  echo "    <string>$ROOT/scripts/sombra.py</string>"
  echo '    <string>--rotina</string>'
  echo '  </array>'
  echo "  <key>WorkingDirectory</key><string>$ROOT</string>"
  echo '  <key>EnvironmentVariables</key><dict>'
  echo "    <key>PATH</key><string>$PATH_ENTRIES</string>"
  echo '  </dict>'
  echo '  <key>StartCalendarInterval</key><array>'
  for dia in 1 2 3 4 5; do
    echo "    <dict><key>Weekday</key><integer>$dia</integer><key>Hour</key><integer>4</integer><key>Minute</key><integer>57</integer></dict>"
  done
  echo '  </array>'
  echo "  <key>StandardOutPath</key><string>$ROOT/logs/sombra.out.log</string>"
  echo "  <key>StandardErrorPath</key><string>$ROOT/logs/sombra.err.log</string>"
  echo '  <key>RunAtLoad</key><false/>'
  echo '</dict></plist>'
}

if [[ "${1:-}" == "--print" ]]; then
  gera
  exit 0
fi

mkdir -p "$HOME/Library/LaunchAgents" "$ROOT/logs"
gera > "$PLIST"
plutil -lint "$PLIST" >/dev/null || { echo "ERRO: plist inválido." >&2; exit 1; }

launchctl bootout "gui/$UID_NUM/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$UID_NUM" "$PLIST"

echo "Instalado: $PLIST"
echo "  sombra : segunda a sexta, 04:57 (até $("$PY_BIN" -c "import json;print(json.load(open('$ROOT/config/sombra.json'))['ate'])"), config/sombra.json)"
echo "Logs    : tail -f $ROOT/logs/sombra.out.log"
echo "Remover : scripts/install_launchd_sombra.sh --uninstall"
