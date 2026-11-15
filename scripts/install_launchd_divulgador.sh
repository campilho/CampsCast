#!/usr/bin/env bash
#
# CampsCast — instala (ou reinstala) o agendamento do Divulgador no launchd.
#
# Um job só, à parte do episódio: a pauta do post no sábado de manhã, e o
# lembrete do primeiro comentário no dia e na hora do post. O dia e a hora saem
# de config/divulgacao.json, para não divergirem do que o script aplica.
#
#   scripts/install_launchd_divulgador.sh              # instala e carrega
#   scripts/install_launchd_divulgador.sh --print      # só mostra o plist
#   scripts/install_launchd_divulgador.sh --uninstall  # remove
#
# No sábado o Mac não acorda sozinho (o pmset do episódio é de segunda a
# sexta): se estiver dormindo às 08:00, o launchd roda o job quando ele acordar.
# As repescagens (sábado 10:00, domingo 08:00) encerram em um segundo se a
# pauta já foi entregue.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL="com.camps.campscast.divulgador"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
UID_NUM="$(id -u)"

if [[ "${1:-}" == "--uninstall" ]]; then
  launchctl bootout "gui/$UID_NUM/$LABEL" 2>/dev/null || true
  rm -f "$PLIST"
  echo "Agendamento do Divulgador removido."
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

# "dia hora minuto" do post. No launchd, 2 é terça, como no ISO; domingo é 0.
POST="$("$PY_BIN" -c "
import json, pathlib
c = json.loads(pathlib.Path('$ROOT/config/divulgacao.json').read_text())
h, m = c['hora_do_post'].split(':')
print(c['dia_do_post'] % 7, int(h), int(m))")"

gera() {
  echo '<?xml version="1.0" encoding="UTF-8"?>'
  echo '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">'
  echo "<!-- Gerado por scripts/install_launchd_divulgador.sh. Não edite: regenere. -->"
  echo '<plist version="1.0"><dict>'
  echo "  <key>Label</key><string>$LABEL</string>"
  # caffeinate -i: o Mac não dorme enquanto o agente escreve a pauta.
  echo '  <key>ProgramArguments</key><array>'
  echo '    <string>/usr/bin/caffeinate</string><string>-i</string>'
  echo "    <string>$PY_BIN</string>"
  echo "    <string>$ROOT/scripts/divulga.py</string>"
  echo '    <string>--rotina</string>'
  echo '  </array>'
  echo "  <key>WorkingDirectory</key><string>$ROOT</string>"
  echo '  <key>EnvironmentVariables</key><dict>'
  echo "    <key>PATH</key><string>$PATH_ENTRIES</string>"
  echo '  </dict>'
  echo '  <key>StartCalendarInterval</key><array>'
  for dhm in "6 8 0" "6 10 0" "0 8 0" "$POST"; do
    set -- $dhm
    echo "    <dict><key>Weekday</key><integer>$1</integer><key>Hour</key><integer>$2</integer><key>Minute</key><integer>$3</integer></dict>"
  done
  echo '  </array>'
  echo "  <key>StandardOutPath</key><string>$ROOT/logs/divulgador.out.log</string>"
  echo "  <key>StandardErrorPath</key><string>$ROOT/logs/divulgador.err.log</string>"
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

set -- $POST
echo "Instalado: $PLIST"
echo "  pauta    : sábado 08:00 (repescagem: sábado 10:00 e domingo 08:00)"
echo "  lembrete : dia $1 da semana, às $(printf '%02d:%02d' "$2" "$3") (config/divulgacao.json)"
echo
FALTA_SMTP="$(cd "$ROOT" && "$PY_BIN" -c 'import sys; sys.path.insert(0, "scripts"); import divulga; print(", ".join(divulga.falta_smtp()))' 2>/dev/null || true)"
if [[ -n "$FALTA_SMTP" ]]; then
  echo
  echo "AVISO: sem e-mail no .env ($FALTA_SMTP): a pauta de sábado não sai do Mac."
  echo "       Ver docs/plano-divulgador.md, \"Instalar\"."
fi
echo
echo "Disparar agora:  launchctl kickstart -k gui/$UID_NUM/$LABEL"
echo "Logs          :  tail -f $ROOT/logs/divulgador.out.log"
