#!/usr/bin/env bash
#
# CampsCast — smoke test da Fase 1.
# Valida estrutura, parsers, roteiro->fala e geração de feed, SEM chamar
# ElevenLabs, AWS ou a API do Claude. Não deixa resíduo no repositório.
#
#   bash tests/smoke_test.sh
#
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PASS=0; FAIL=0
FIXTURE_DATE="1970-01-01"
TMP_EP="episodes/${FIXTURE_DATE}.md"
TMP_AUDIO="audio/${FIXTURE_DATE}.mp3"
FEED_BAK=""

# O registro de execução nunca escreve no arquivo real durante o teste: toda
# execução do orquestrador aqui dentro vai para um arquivo temporário.
METRICAS_REAL_ANTES="$(shasum metricas/execucoes.jsonl 2>/dev/null || echo ausente)"
export METRICAS_ARQ="$(mktemp)"
export REGISTRO_SEM_SONO=1
# Sem isto o orquestrador publicaria estado no S3 de produção a cada teste.
export ESTADO_ARQ="$(mktemp)"

ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS+1)); }
bad()  { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL+1)); }
head_() { printf '\n\033[1m%s\033[0m\n' "$1"; }

# O abrigo dos episódios reais fica DENTRO do repositório, com nome fixo.
# Antes era um mktemp em /var/folders: quando o cleanup foi interrompido no
# meio, os episódios sumiram de episodes/ e não havia como saber onde procurar.
# Aqui é visível, previsível e recuperável na execução seguinte.
EP_BACKUP="$ROOT/.smoke-backup"

# Nome de episódio é sempre YYYY-MM-DD.md. Validar antes de mover, nos dois
# sentidos, impede que lixo vire nome de arquivo: numa execução morta por
# SIGPIPE (`smoke_test.sh | head -3`), o cleanup rodou com a saída quebrada e
# produziu episódios chamados "2026-08-31.md\n  ✓ arquivo .env.example".
nome_de_episodio_valido() {
  [[ "$1" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}\.md$ ]]
}

restaurar_episodios() {
  [[ -d "$EP_BACKUP" ]] || return 0
  local f nome
  for f in "$EP_BACKUP"/*.md; do
    [[ -e "$f" ]] || continue
    nome="${f##*/}"
    if ! nome_de_episodio_valido "$nome"; then
      printf '\033[31mAbrigo com nome inesperado, deixado intacto:\033[0m %s\n' \
        "$f" >&2
      continue
    fi
    # Nunca sobrescrever episódio que já esteja no lugar: se ele existe agora,
    # é mais recente que o abrigo.
    if [[ -e "episodes/$nome" ]]; then
      rm -f "$f"
    else
      mv "$f" "episodes/$nome"
    fi
  done
  rmdir "$EP_BACKUP" 2>/dev/null || true
}

cleanup() {
  # Apaga só o que a própria suíte criou. A versão anterior fazia
  # `rm -f episodes/*.md` antes de restaurar — uma janela em que os episódios
  # só existiam no abrigo. Morrer ali significava perdê-los de vista.
  rm -f "$TMP_EP" "$TMP_AUDIO"
  if [[ -n "$FEED_BAK" && -f "$FEED_BAK" ]]; then
    mv "$FEED_BAK" feed/feed.xml
  else
    rm -f feed/feed.xml
  fi
  restaurar_episodios
}
# INT e TERM também: Ctrl-C no meio da suíte não pode deixar episódio fora.
trap cleanup EXIT INT TERM HUP PIPE

# Auto-recuperação: se uma execução anterior morreu antes de restaurar, os
# episódios ainda estão no abrigo. Devolve antes de qualquer outra coisa.
if [[ -d "$EP_BACKUP" ]] && compgen -G "$EP_BACKUP/*.md" >/dev/null; then
  printf '\033[33mRecuperando episódios de uma execução anterior interrompida.\033[0m\n' >&2
  restaurar_episodios
fi

# A suíte move episodes/*.md para se isolar. Se um pipeline estiver gravando um
# episódio nesse intervalo, os dois se atropelam — e o episódio real pode se
# perder. Melhor recusar do que arriscar.
if pgrep -f "claude -p" >/dev/null 2>&1; then
  printf '\033[31mAbortado:\033[0m há um pipeline rodando (claude -p).\n' >&2
  printf 'A suíte isola episodes/ e atropelaria a gravação do episódio.\n' >&2
  printf 'Espere terminar — acompanhe com: python3 scripts/watch_agent.py\n' >&2
  exit 2
fi

# A suíte precisa ser hermética: episódios reais mudam o cálculo da janela e
# disparam a guarda de sobreposição. Saem de cena aqui e voltam no cleanup.
mkdir -p "$EP_BACKUP"
for f in episodes/*.md; do
  [[ -e "$f" ]] || continue
  nome="${f##*/}"
  if nome_de_episodio_valido "$nome"; then
    mv "$f" "$EP_BACKUP/$nome"
  else
    printf '\033[31mArquivo com nome inesperado em episodes/, não tocado:\033[0m %s\n' \
      "$f" >&2
  fi
done

# ---------------------------------------------------------------- 1 estrutura
head_ "1. Estrutura do repositório"
for d in config prompts episodes saved-items analysis audio scripts docs/decisions logs feed tests; do
  [[ -d "$d" ]] && ok "diretório $d/" || bad "faltando diretório $d/"
done
for f in PROJETO.md README.md .gitignore .env.example covered-index.json \
         config/briefing.md config/sources.yaml config/show.json config/tts.json \
         prompts/master.md saved-items/backlog.md \
         scripts/run_episode.sh scripts/tts.py scripts/publish.py scripts/notify.py \
         scripts/window.py scripts/watch_agent.py scripts/s3.py \
         scripts/calibrate_pace.py scripts/schedule.py scripts/set_base_url.py; do
  [[ -f "$f" ]] && ok "arquivo $f" || bad "faltando arquivo $f"
done
[[ -x scripts/run_episode.sh ]] && ok "run_episode.sh executável" || bad "run_episode.sh sem +x"

# -------------------------------------------------------------- 2 config/JSON
head_ "2. Configuração"
python3 -c "import json;json.load(open('config/show.json'))" 2>/dev/null \
  && ok "show.json é JSON válido" || bad "show.json inválido"
python3 -c "import json;json.load(open('config/tts.json'))" 2>/dev/null \
  && ok "tts.json é JSON válido" || bad "tts.json inválido"
python3 -c "import json;d=json.load(open('covered-index.json'));assert isinstance(d['items'],list)" 2>/dev/null \
  && ok "covered-index.json tem forma esperada" || bad "covered-index.json inválido"

# ------------------------------------------------------------------ 3 sintaxe
head_ "3. Sintaxe dos scripts"
bash -n scripts/run_episode.sh 2>/dev/null && ok "run_episode.sh compila" || bad "run_episode.sh com erro de sintaxe"
for p in scripts/tts.py scripts/publish.py scripts/notify.py scripts/window.py \
         scripts/watch_agent.py scripts/s3.py scripts/calibrate_pace.py \
         scripts/schedule.py scripts/set_base_url.py tests/make_silent_mp3.py; do
  python3 -m py_compile "$p" 2>/dev/null && ok "$p compila" || bad "$p com erro de sintaxe"
done

# ------------------------------------------------------------------ 4 parsers
head_ "4. Parsers (front-matter, markdown->fala, chunking)"
python3 - <<'PYEOF' && ok "parsers do roteiro" || bad "parsers do roteiro"
import sys, pathlib
sys.path.insert(0, "scripts")
from tts import strip_front_matter, to_speakable, chunk, MAX_CHARS
from publish import parse_front_matter, mp3_duration_seconds, hhmmss, duration_from_mmss

raw = pathlib.Path("tests/fixtures/sample-episode.md").read_text(encoding="utf-8")

fm = parse_front_matter(raw)
assert fm["date"] == "1970-01-01", fm
assert fm["window_end"] == "1969-12-31", fm
assert len(fm["topics"]) == 3, fm
assert fm["topics"][0]["source_name"] == "PROJETO.md", fm
assert fm["from_backlog"] == [], fm

body = to_speakable(strip_front_matter(raw))
assert "---" not in body.split("\n")[0]
assert "http" not in body, "URL vazou para o texto falado"
assert "#" not in body and "**" not in body, "markdown vazou para o texto falado"

parts = chunk(body)
assert parts and all(len(p) <= MAX_CHARS for p in parts), [len(p) for p in parts]
assert sum(len(p.split()) for p in parts) == len(body.split()), "chunking perdeu palavras"

assert hhmmss(459) == "7:39" and hhmmss(3661) == "1:01:01"
assert duration_from_mmss("7:39") == 459 and duration_from_mmss("lixo") is None
print(f"    {len(body.split())} palavras, {len(parts)} trechos")
PYEOF

# -------------------------------------------------------------- 5 tts dry-run
head_ "5. TTS (dry-run, sem chamar a API)"
if python3 scripts/tts.py --script tests/fixtures/sample-episode.md \
     --out /dev/null --dry-run >/dev/null 2>&1; then
  ok "tts.py --dry-run roda sem erro"
else
  bad "tts.py --dry-run falhou"
fi
if python3 scripts/tts.py --script tests/fixtures/nao-existe.md \
     --out /dev/null --dry-run >/dev/null 2>&1; then
  bad "tts.py deveria falhar com roteiro inexistente"
else
  ok "tts.py falha corretamente com roteiro inexistente"
fi
if python3 scripts/tts.py >/dev/null 2>&1; then
  bad "tts.py sem argumentos deveria falhar"
else
  ok "tts.py exige --script/--out ou --check"
fi
# --check sem chave não pode tentar rede nem gastar caractere.
OUT_CHK="$(ELEVENLABS_API_KEY="" python3 scripts/tts.py --check 2>&1 || true)"
if [[ "$OUT_CHK" == *"ELEVENLABS_API_KEY"* ]]; then
  ok "--check avisa sobre chave ausente antes de chamar a API"
else
  bad "--check deveria exigir a chave primeiro"
fi
# A voz configurada precisa ser real, não o placeholder.
if python3 -c "
import json,sys
v=json.load(open('config/tts.json'))['voice_id']
sys.exit(0 if v and not v.startswith('PLACEHOLDER') else 1)"; then
  ok "config/tts.json tem voice_id configurado"
fi
# A faixa de palavras deriva do ritmo da voz e precisa caber nos 5–10 minutos.
python3 - <<'PYEOF' && ok "faixa de palavras deriva do ritmo da voz e cabe no formato" || bad "faixa de palavras incoerente"
import sys
sys.path.insert(0, "scripts")
from tts import load_cfg, word_budget, wpm

cfg = load_cfg()
assert cfg.get("words_per_minute"), "config/tts.json não declara words_per_minute"
b = word_budget(cfg)
rate = b["wpm"]
assert b["min"] < b["target"] < b["max"], b
# O formato manda 5 a 10 minutos; a faixa tem de caber com folga nos dois lados.
assert b["min"] / rate >= 5.0, f"piso de {b['min']} palavras fica abaixo de 5 min"
assert b["max"] / rate <= 10.0, f"teto de {b['max']} palavras passa de 10 min"
assert 7.5 <= b["target"] / rate <= 8.5, "alvo longe dos 8 minutos"

# Trocar a voz precisa mover a faixa junto — é o bug que originou este teste.
lento = word_budget({"words_per_minute": 125})
rapido = word_budget({"words_per_minute": 163})
assert lento["max"] < rapido["max"], "faixa não acompanha a velocidade da voz"
print(f"    {rate} ppm -> {b['min']}-{b['max']} palavras, alvo {b['target']}")
PYEOF

# O teto de palavras não pode estourar 10 minutos ao ritmo REALMENTE medido nos
# episódios publicados. Um words_per_minute otimista passa despercebido — foi
# assim que ele foi parar em 165 com o real em 155, e o teto virou 10,1 min.
python3 - <<'PYEOF' && ok "teto de palavras cabe em 10 min ao ritmo medido" || bad "teto de palavras estoura 10 min"
import statistics, sys
sys.path.insert(0, "scripts")
from calibrate_pace import medicoes
from tts import load_cfg, word_budget

dados = medicoes("2026-09-01")
if len(dados) < 2:
    print("    (menos de 2 episódios medíveis — checagem pulada)")
    raise SystemExit(0)
medido = statistics.median(d[3] for d in dados)
teto = word_budget(load_cfg())["max"]
minutos = teto / medido
print(f"    ritmo medido {medido:.0f} ppm, teto {teto} palavras = {minutos:.2f} min")
assert minutos <= 10.0, f"teto daria {minutos:.2f} min, acima do limite rígido"
PYEOF

# O prompt não pode ter a faixa fixa no texto: ela vem por variável de ambiente.
if grep -qE '(WORD_MIN|WORD_TARGET|WORD_MAX)' prompts/master.md; then
  ok "prompt recebe a faixa por variável, sem número fixo"
else
  bad "prompt deveria referenciar WORD_MIN/WORD_TARGET/WORD_MAX"
fi

# ------------------------------------------------- 5b costura dos MP3
head_ "5b. Costura dos trechos de MP3"
python3 - <<'PYEOF' && ok "concatenação remove tags e cabeçalho Xing/Info" || bad "costura de MP3"
import sys
sys.path.insert(0, "scripts")
from tts import strip_container, _frame_len, _id3v2_len

FRAME = 417                                   # MPEG1 L3, 128 kbps, 44.1 kHz
HDR = bytes([0xFF, 0xFB, 0x90, 0x00])
frame = HDR + b"\x00" * (FRAME - 4)

assert _frame_len(frame) == FRAME, _frame_len(frame)
assert _frame_len(b"\x00\x00\x00\x00") == 0        # não é frame

# ID3v2: tamanho é synchsafe (7 bits por byte).
id3 = b"ID3\x03\x00\x00" + bytes([0, 0, 0x01, 0x00]) + b"\x00" * 128
assert _id3v2_len(id3) == 10 + 128, _id3v2_len(id3)
assert _id3v2_len(frame) == 0

# Um frame de metadados Info tem de sumir; os de áudio, não.
info = HDR + b"\x00" * 32 + b"Info" + b"\x00" * (FRAME - 40)
assert len(info) == FRAME, len(info)
saida = strip_container(id3 + info + frame + frame)
assert saida == frame + frame, f"{len(saida)} != {2*FRAME}"

# Sem Info, nada é descartado.
assert strip_container(frame + frame) == frame + frame
# ID3v1 no fim também sai.
assert strip_container(frame + b"TAG" + b"\x00" * 125) == frame

# É este o bug que truncava o episódio: concatenar quatro respostas cruas
# deixava quatro cabeçalhos Info, e o player parava no primeiro trecho.
trechos = [id3 + info + frame * 3 for _ in range(4)]
juntado = b"".join(strip_container(c) for c in trechos)
assert b"Info" not in juntado and b"Xing" not in juntado
assert len(juntado) == 12 * FRAME, len(juntado)
print(f"    4 trechos costurados: {len(juntado)} bytes, 0 cabeçalhos de metadados")
PYEOF

# Nenhum MP3 entregue pode conter cabeçalho de metadados no meio do arquivo.
python3 - <<'PYEOF' && ok "MP3 gerados não têm Xing/Info embutido" || bad "MP3 com metadados embutidos"
import pathlib
maus = []
for f in pathlib.Path("audio").glob("*.mp3"):
    d = f.read_bytes()
    if b"Xing" in d or b"Info" in d:
        maus.append(f.name)
if maus:
    print("    arquivos afetados:", ", ".join(sorted(maus)))
    raise SystemExit(1)
PYEOF

# ----------------------------------------------------------------- 6 mp3+feed
head_ "6. Duração de MP3 e geração do feed"
[[ -f feed/feed.xml ]] && { FEED_BAK="feed/feed.xml.bak"; mv feed/feed.xml "$FEED_BAK"; }

cp tests/fixtures/sample-episode.md "$TMP_EP"
python3 tests/make_silent_mp3.py "$TMP_AUDIO" 459 >/dev/null 2>&1

python3 - <<'PYEOF' && ok "duração lida do MP3 bate com o esperado" || bad "duração do MP3 divergente"
import sys, pathlib
sys.path.insert(0, "scripts")
from publish import mp3_duration_seconds
d = mp3_duration_seconds(pathlib.Path("audio/1970-01-01.mp3"))
assert d is not None and abs(d - 459) <= 1, d
print(f"    {d}s")
PYEOF

if python3 scripts/publish.py --no-upload >/dev/null 2>&1; then
  ok "publish.py gera feed.xml"
else
  bad "publish.py falhou"
fi

python3 - <<'PYEOF' && ok "feed.xml é XML válido e tem o item do episódio" || bad "feed.xml inválido"
import xml.etree.ElementTree as ET
ns = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}
root = ET.parse("feed/feed.xml").getroot()
ch = root.find("channel")
assert ch.findtext("title"), "feed sem título"
assert ch.findtext("language") == "pt-BR"
items = ch.findall("item")
assert len(items) == 1, f"esperava 1 item, achei {len(items)}"
it = items[0]
enc = it.find("enclosure")
assert enc.get("type") == "audio/mpeg" and int(enc.get("length")) > 0
assert it.findtext("itunes:duration", namespaces=ns) == "7:39", it.findtext("itunes:duration", namespaces=ns)
assert it.findtext("guid") == "campscast-1970-01-01"
assert ch.find("itunes:category", ns) is not None, "feed sem categoria iTunes"
print(f"    1 item, duração {it.findtext('itunes:duration', namespaces=ns)}")
PYEOF

# ------------------------------------------------------- 7 janela de notícias
head_ "7. Janela de notícias (window.py)"
python3 - <<'PYEOF' && ok "regras da janela" || bad "regras da janela"
import pathlib, shutil, sys, tempfile
from datetime import date
sys.path.insert(0, "scripts")
import window

EP = pathlib.Path("episodes")
backup = tempfile.mkdtemp()
existing = [p for p in EP.glob("*.md")]
for p in existing:
    shutil.move(str(p), backup)

def put(day, w_start, w_end):
    (EP / f"{day}.md").write_text(
        f"---\ndate: {day}\nwindow_start: {w_start}\nwindow_end: {w_end}\n"
        f"title: t\n---\n\ncorpo\n", encoding="utf-8")

def clear():
    for p in EP.glob("*.md"):
        p.unlink()

def w(day):
    return window.compute(date.fromisoformat(day))

try:
    # 2026-08-21 sex | 22 sáb | 23 dom | 24 seg | 25 ter
    clear()
    r = w("2026-08-23")   # partida a frio no domingo -> sexta + sábado, sem hoje
    assert (str(r["start"]), str(r["end"]), r["days"]) == ("2026-08-21", "2026-08-22", 2), r
    assert r["last_episode"] is None

    clear()
    r = w("2026-08-24")   # partida a frio na segunda -> sex + sáb + dom
    assert (str(r["start"]), str(r["end"]), r["days"]) == ("2026-08-21", "2026-08-23", 3), r

    clear()
    r = w("2026-08-25")   # partida a frio na terça -> só o dia anterior
    assert (str(r["start"]), str(r["end"]), r["days"]) == ("2026-08-24", "2026-08-24", 1), r

    clear()
    r = w("2026-08-22")   # partida a frio no sábado -> só sexta
    assert (str(r["start"]), str(r["end"])) == ("2026-08-21", "2026-08-21"), r

    # encadeamento: manual no sábado (cobriu sexta) -> segunda pega sáb + dom
    clear(); put("2026-08-22", "2026-08-21", "2026-08-21")
    r = w("2026-08-24")
    assert (str(r["start"]), str(r["end"]), r["days"]) == ("2026-08-22", "2026-08-23", 2), r
    assert r["last_episode"] == "2026-08-22"

    # e se também rodou domingo -> segunda pega só domingo
    put("2026-08-23", "2026-08-22", "2026-08-22")
    r = w("2026-08-24")
    assert (str(r["start"]), str(r["end"]), r["days"]) == ("2026-08-23", "2026-08-23", 1), r

    # nada novo a cobrir
    put("2026-08-24", "2026-08-23", "2026-08-23")
    r = w("2026-08-24")
    assert r["status"] == "empty", r

    # episódio em formato antigo (sem window_end) -> assume véspera
    clear()
    (EP / "2026-08-24.md").write_text("---\ndate: 2026-08-24\ntitle: t\n---\n\nx\n",
                                      encoding="utf-8")
    r = w("2026-08-25")
    assert (str(r["start"]), str(r["end"])) == ("2026-08-24", "2026-08-24"), r

    # parada longa -> janela truncada em 7 dias
    clear(); put("2026-06-01", "2026-05-29", "2026-05-31")
    r = w("2026-08-25")
    assert r["clamped"] and r["days"] == 7, r

    # hoje nunca entra, em nenhum cenário
    clear()
    for d in ["2026-08-21", "2026-08-22", "2026-08-23", "2026-08-24", "2026-08-25"]:
        assert str(w(d)["end"]) < d, (d, w(d))
    print("    10 cenários de janela")
finally:
    clear()
    for p in pathlib.Path(backup).glob("*.md"):
        shutil.move(str(p), EP)
    shutil.rmtree(backup, ignore_errors=True)
PYEOF

# --------------------------------------------------------- 8 orquestrador dry
head_ "8. Orquestrador (dry-run)"
# O feed da seção 6 já foi validado; o episódio-fixture sai de cena agora para
# não entrar no cálculo da janela (ele fingiria uma parada de 56 anos).
rm -f "$TMP_EP" "$TMP_AUDIO"

# 2026-08-24 é uma segunda-feira comum, sem feriado.
OUT_SEG="$(bash scripts/run_episode.sh --date 2026-08-24 --dry-run --skip research 2>&1)"
if [[ "$OUT_SEG" == *"Concluído"* ]]; then
  ok "run_episode.sh --dry-run completa"
else
  bad "run_episode.sh --dry-run falhou"
fi
if [[ "$OUT_SEG" == *"Janela: 2026-08-21 → 2026-08-23 (3 dia(s))"* ]]; then
  ok "segunda em partida a frio cobre sexta, sábado e domingo"
else
  bad "janela da segunda errada"
fi

# Domingo agora é barrado pelo calendário, e --force é a válvula de escape.
OUT_DOM="$(bash scripts/run_episode.sh --date 2026-08-23 --dry-run --skip research 2>&1)"
if [[ "$OUT_DOM" == *"sem episódio"* && "$OUT_DOM" == *"weekdays"* ]]; then
  ok "domingo é barrado pelo calendário"
else
  bad "domingo deveria ser barrado"
fi
OUT_DOMF="$(bash scripts/run_episode.sh --date 2026-08-23 --dry-run --force --skip research 2>&1)"
if [[ "$OUT_DOMF" == *"Concluído"* ]]; then
  ok "--force roda em dia sem episódio"
else
  bad "--force deveria rodar no domingo"
fi

OUT_TUE="$(bash scripts/run_episode.sh --date 2026-08-25 --dry-run --skip research 2>&1)"
if [[ "$OUT_TUE" == *"Janela: 2026-08-24 → 2026-08-24 (1 dia(s))"* ]]; then
  ok "dia comum cobre apenas o dia anterior"
else
  bad "janela do dia comum errada"
fi

# Guarda de sobreposição. Nota: o smoke test roda com `pipefail`, então o
# resultado é capturado numa variável — `cmd | grep` devolveria o rc do cmd.
cp tests/fixtures/sample-episode.md episodes/2026-08-25.md

OUT_DUP="$(bash scripts/run_episode.sh --date 2026-08-25 --dry-run 2>&1 || true)"
if [[ "$OUT_DUP" == *"já existe"* ]]; then
  ok "recusa sobrepor episódio existente"
else
  bad "deveria recusar sobrepor episódio existente"
fi

OUT_OVW="$(bash scripts/run_episode.sh --date 2026-08-25 --dry-run --overwrite 2>&1 || true)"
if [[ "$OUT_OVW" != *"já existe"* && "$OUT_OVW" == *"Concluído"* ]]; then
  ok "--overwrite libera a regravação"
else
  bad "--overwrite não liberou a regravação"
fi
if [[ "$OUT_OVW" == *"AVISO:"*"não encontrado no PATH"* ]]; then
  ok "dry-run avisa sobre o claude ausente em vez de abortar"
else
  ok "claude presente no PATH (aviso não se aplica)"
fi
rm -f episodes/2026-08-25.md

# Falha de autenticação: o erro mais provável na primeira execução real.
# Um CLI falso reproduz a saída exata do `claude -p` sem login.
FAKE="$(mktemp -d)"
printf '#!/bin/sh\necho "Not logged in · Please run /login"\nexit 1\n' > "$FAKE/claude"
chmod +x "$FAKE/claude"
OUT_AUTH="$(CLAUDE_BIN="$FAKE/claude" bash scripts/run_episode.sh \
             --date 2026-08-25 --only research 2>&1 || true)"
rm -rf "$FAKE"
if [[ "$OUT_AUTH" == *"não autenticado"* && "$OUT_AUTH" == *"/login"* ]]; then
  ok "diagnostica CLI sem autenticação em vez de repassar o erro cru"
else
  bad "falta de login deveria virar mensagem acionável"
fi
if [[ ! -f episodes/2026-08-25.md ]]; then
  ok "falha do agente não deixa episódio pela metade"
else
  bad "episódio não deveria ter sido criado"
fi

rm -f logs/2026-08-23.log logs/2026-08-24.log logs/2026-08-25.log

# ------------------------------------------------------ 9 acompanhamento vivo
head_ "9. Acompanhamento do agente (watch_agent.py)"
python3 - <<'PYEOF' && ok "watch_agent: slug, detecção de sessão e resumo" || bad "watch_agent"
import json, pathlib, sys, tempfile
sys.path.insert(0, "scripts")
import watch_agent as wa

# O slug do CLI troca barras E espaços por "-" ("Claude Code" -> "Claude-Code").
d = wa.session_dir()
if d is not None:
    assert " " not in d.name and "/" not in d.name, d.name

assert wa.summarize("WebSearch", {"query": "anthropic news"}) == 'buscando: "anthropic news"'
assert wa.summarize("WebFetch", {"url": "https://x.ai/news"}) == "lendo: https://x.ai/news"
assert "escrevendo" in wa.summarize("Write", {"file_path": "episodes/x.md"})
assert wa.summarize("Bash", {}) == "Bash"          # ferramenta sem resumo próprio

tmp = pathlib.Path(tempfile.mkdtemp())
head = {"message": {"role": "user", "content": "Você é o produtor e roteirista do CampsCast"}}
(tmp / "headless.jsonl").write_text(json.dumps(head) + "\n", encoding="utf-8")
(tmp / "outra.jsonl").write_text(json.dumps({"message": {"role": "user",
                                 "content": "outro assunto"}}) + "\n", encoding="utf-8")

assert wa.is_headless_run(tmp / "headless.jsonl")
assert not wa.is_headless_run(tmp / "outra.jsonl")
# Só a sessão do pipeline é escolhida, mesmo com outra mais recente ao lado.
assert wa.newest_session(tmp).name == "headless.jsonl"
# Filtro de mtime: nada antigo o suficiente passa.
assert wa.newest_session(tmp, newer_than=2**40) is None
print("    slug, detecção e resumo conferidos")
PYEOF

# O watcher não pode deixar processo órfão nem travar a etapa.
FAKE2="$(mktemp -d)"
cat > "$FAKE2/claude" <<'STUB'
#!/bin/sh
python3 -c "import time; time.sleep(2)"
cat > episodes/2026-08-25.md <<'MD'
---
date: 2026-08-25
window_start: 2026-08-24
window_end: 2026-08-24
title: teste
words: 10
estimated_duration: 0:04
topics: []
from_backlog: []
---

Corpo de teste.
MD
echo "OK episodes/2026-08-25.md 10 00:04"
STUB
chmod +x "$FAKE2/claude"
START=$(date +%s)
OUT_W="$(CLAUDE_BIN="$FAKE2/claude" bash scripts/run_episode.sh \
          --date 2026-08-25 --only research 2>&1 || true)"
ELAPSED=$(( $(date +%s) - START ))
rm -rf "$FAKE2" episodes/2026-08-25.md logs/2026-08-25.log

if [[ "$OUT_W" == *"Concluído"* ]]; then
  ok "etapa de pesquisa completa com o watcher ativo"
else
  bad "watcher quebrou a etapa de pesquisa"
fi
if [[ $ELAPSED -lt 30 ]]; then
  ok "watcher não segura a execução (${ELAPSED}s)"
else
  bad "watcher travou a execução por ${ELAPSED}s"
fi
if pgrep -f "watch_agent.py" >/dev/null 2>&1; then
  bad "watcher ficou órfão depois da etapa"
  pkill -f "watch_agent.py" 2>/dev/null || true
else
  ok "watcher encerrado sem deixar órfão"
fi

# --------------------------------------------------- 9b calendário de publicação
head_ "9b. Calendário de publicação"
python3 - <<'PYEOF' && ok "dias úteis, feriados e exceções" || bad "calendário"
import sys
from datetime import date
sys.path.insert(0, "scripts")
from schedule import avaliar, feriados_br, pascoa

# Páscoa: âncora dos feriados móveis. Valores conferidos contra calendário.
assert pascoa(2026) == date(2026, 4, 5), pascoa(2026)
assert pascoa(2027) == date(2027, 3, 28), pascoa(2027)

f26 = feriados_br(2026)
assert f26[date(2026, 9, 7)] == "Independência"
assert date(2026, 4, 3) in f26, "Sexta-feira Santa de 2026"
assert date(2026, 2, 17) in f26, "Carnaval de 2026"
assert date(2026, 6, 4) in f26, "Corpus Christi de 2026"
assert date(2026, 11, 20) in f26, "Consciência Negra"

padrao = {"weekdays": [1,2,3,4,5], "holidays": "BR",
          "skip_dates": [], "force_dates": []}
assert avaliar(date(2026, 9, 4), padrao)[0] is True,  "sexta comum"
assert avaliar(date(2026, 9, 5), padrao)[0] is False, "sábado"
assert avaliar(date(2026, 9, 7), padrao)[0] is False, "feriado"
assert "Independência" in avaliar(date(2026, 9, 7), padrao)[1]
assert avaliar(date(2026, 9, 8), padrao)[0] is True,  "terça depois do feriado"

# force_dates vence feriado e fim de semana; skip_dates vence dia útil.
forcado = {**padrao, "force_dates": ["2026-09-07", "2026-09-05"]}
assert avaliar(date(2026, 9, 7), forcado)[0] is True
assert avaliar(date(2026, 9, 5), forcado)[0] is True
pulado = {**padrao, "skip_dates": ["2026-09-08"]}
assert avaliar(date(2026, 9, 8), pulado)[0] is False

# Quem clonar pode querer publicar todo dia, ou ignorar feriados brasileiros.
todo_dia = {**padrao, "weekdays": [1,2,3,4,5,6,7], "holidays": None}
assert avaliar(date(2026, 9, 5), todo_dia)[0] is True, "sábado liberado"
assert avaliar(date(2026, 9, 7), todo_dia)[0] is True, "feriado ignorado"
print("    Páscoa, feriados móveis, fim de semana e exceções conferidos")
PYEOF

# O feriado não pode fazer a notícia sumir: o dia seguinte tem de cobri-lo.
python3 - <<'PYEOF' && ok "dia pulado é coberto pela janela seguinte" || bad "notícia perdida no feriado"
import pathlib, shutil, sys, tempfile
from datetime import date
sys.path.insert(0, "scripts")
import window

EP = pathlib.Path("episodes")
abrigo = tempfile.mkdtemp()
for p in EP.glob("*.md"):
    shutil.move(str(p), abrigo)
try:
    # Sexta 04/09 cobriu até quinta 03/09. Segunda 07/09 é feriado.
    linhas = ["---", "date: 2026-09-04", "window_start: 2026-09-03",
              "window_end: 2026-09-03", "title: t", "---", "", "x"]
    (EP / "2026-09-04.md").write_text(chr(10).join(linhas) + chr(10),
                                      encoding="utf-8")
    r = window.compute(date(2026, 9, 8))       # terça seguinte
    assert str(r["start"]) == "2026-09-04", r
    assert str(r["end"]) == "2026-09-07", r    # inclui o feriado
    assert r["days"] == 4, r
    print(f"    terça cobre {r['start']} a {r['end']} — o feriado entra")
finally:
    for p in EP.glob("*.md"):
        p.unlink()
    for p in pathlib.Path(abrigo).glob("*.md"):
        shutil.move(str(p), EP)
    shutil.rmtree(abrigo, ignore_errors=True)
PYEOF

# O launchd tem de disparar exatamente nos dias de config/schedule.json.
python3 - <<'PYEOF' && ok "launchd e schedule.json concordam nos dias" || bad "launchd diverge do schedule"
import json, os, pathlib, plistlib, sys
cfg = json.loads(pathlib.Path("config/schedule.json").read_text(encoding="utf-8"))
esperados = set(cfg.get("weekdays") or [1,2,3,4,5])
plist = pathlib.Path(os.path.expanduser("~/Library/LaunchAgents/com.camps.campscast.plist"))
if not plist.exists():
    print("    (agendamento não instalado — checagem pulada)")
    raise SystemExit(0)
d = plistlib.loads(plist.read_bytes())
achados = {e["Weekday"] for e in d["StartCalendarInterval"]}
assert achados == esperados, f"plist dispara em {sorted(achados)}, config diz {sorted(esperados)}"
print(f"    dias {sorted(achados)} em ambos")
PYEOF

# ------------------------------------------------------- 10 assinatura AWS S3
head_ "10. Upload S3 (assinatura SigV4, sem AWS CLI)"
python3 - <<'PYEOF' && ok "SigV4: vetor oficial da AWS, encoding e requisição canônica" || bad "SigV4"
import sys
sys.path.insert(0, "scripts")
from s3 import (Credentials, S3Error, authorization_header, canonical_request,
                signing_key, uri_encode)

# Vetor de teste publicado pela AWS na documentação do SigV4. Valida a cadeia
# HMAC inteira (data -> região -> serviço -> aws4_request), que é a parte mais
# fácil de errar e a mais difícil de depurar contra o S3 de verdade.
k = signing_key("wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY",
                "20150830", "us-east-1", "iam")
assert k.hex() == "c4afb1cc5771d871763a393e44b703571b55cc28424d1a5e86da6ed3c154a4b9", k.hex()

# Percent-encoding do SigV4: maiúsculas, e ~ - _ . nunca escapados.
assert uri_encode("audio/2026-08-24.mp3", encode_slash=False) == "audio/2026-08-24.mp3"
assert uri_encode("a b") == "a%20b"
assert uri_encode("a/b") == "a%2Fb"
assert uri_encode("a/b", encode_slash=False) == "a/b"
assert uri_encode("~-_.") == "~-_."
assert uri_encode("ção") == "%C3%A7%C3%A3o"        # UTF-8, dois bytes por char

# Requisição canônica: cabeçalhos minúsculos, ordenados, valores normalizados.
creq, signed = canonical_request(
    "PUT", "/feed.xml", "",
    {"Host": "b.s3.us-east-1.amazonaws.com", "X-Amz-Date": "20260824T000000Z",
     "Content-Type": "application/rss+xml", "x-amz-content-sha256": "abc"},
    "abc")
assert signed == "content-type;host;x-amz-content-sha256;x-amz-date", signed
linhas = creq.split("\n")
assert linhas[0] == "PUT", linhas
assert linhas[1] == "/feed.xml", linhas
assert linhas[2] == "", "query string vazia deve virar linha vazia"
assert linhas[3:7] == [
    "content-type:application/rss+xml",
    "host:b.s3.us-east-1.amazonaws.com",
    "x-amz-content-sha256:abc",
    "x-amz-date:20260824T000000Z",
], linhas
# O bloco de cabeçalhos termina em \n e o join acrescenta outra: a linha em
# branco entre os cabeçalhos e a lista de assinados é exigida pela especificação.
assert linhas[7] == "", "falta a linha em branco depois dos cabeçalhos"
assert linhas[8] == signed
assert linhas[9] == "abc"
assert len(linhas) == 10, linhas

# Espaços internos colapsam, conforme a especificação.
creq2, _ = canonical_request("PUT", "/x", "", {"a": "  1   2  "}, "h")
assert "a:1 2\n" in creq2, creq2

# A assinatura precisa ser determinística para as mesmas entradas.
c = Credentials("AKIDEXAMPLE", "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY")
a1 = authorization_header(c, "us-east-1", "20260824T000000Z", "20260824", creq, signed)
a2 = authorization_header(c, "us-east-1", "20260824T000000Z", "20260824", creq, signed)
assert a1 == a2
assert a1.startswith("AWS4-HMAC-SHA256 Credential=AKIDEXAMPLE/20260824/us-east-1/s3/aws4_request")
assert f"SignedHeaders={signed}" in a1
# Trocar qualquer entrada tem de mudar a assinatura.
a3 = authorization_header(c, "sa-east-1", "20260824T000000Z", "20260824", creq, signed)
assert a3 != a1
print("    vetor AWS confere; encoding e canonical request corretos")
PYEOF

# Bucket com ponto no nome quebra HTTPS no endereço virtual do S3 — tem de ser
# recusado antes da requisição, não virar erro de certificado confuso.
python3 - <<'PYEOF' && ok "recusa bucket com ponto no nome" || bad "bucket com ponto deveria ser recusado"
import sys
sys.path.insert(0, "scripts")
from s3 import Credentials, S3Error, put_object
try:
    put_object("meu.bucket", "k", b"x", "text/plain",
               region="us-east-1", creds=Credentials("A", "B"))
except S3Error as e:
    assert "ponto no nome" in str(e), e
else:
    raise AssertionError("deveria ter recusado")
PYEOF

# Sem bucket ou sem credenciais, o upload é pulado — nunca explode.
python3 - <<'PYEOF' && ok "publish pula o upload sem bucket ou sem credenciais" || bad "publish deveria pular o upload"
import os, sys
sys.path.insert(0, "scripts")
import publish

os.environ["S3_BUCKET"] = ""
assert publish.upload("2026-08-24", {"base_url": "https://x"}) is False

# Com bucket mas sem credencial nenhuma, também pula em vez de estourar.
os.environ["S3_BUCKET"] = "bucket-de-teste"
os.environ["AWS_ACCESS_KEY_ID"] = ""
os.environ["AWS_SECRET_ACCESS_KEY"] = ""
os.environ["AWS_PROFILE"] = "perfil-que-nao-existe-campscast"
assert publish.upload("2026-08-24", {"base_url": "https://x"}) is False
PYEOF

# A AWS CLI não pode voltar a ser pré-requisito.
if grep -qE '(shutil\.which\("aws"\)|subprocess.*"aws")' scripts/publish.py; then
  bad "publish.py voltou a depender da AWS CLI"
else
  ok "publish.py não depende da AWS CLI"
fi

# As policies geradas precisam referenciar o bucket real: ARN divergente é o
# que produz o "Policy has invalid resource" do console.
python3 - <<'PYEOF' && ok "policies geradas usam o bucket configurado" || bad "policies com bucket errado"
import json, sys
sys.path.insert(0, "scripts")
from s3 import bucket_policy, iam_policy, resolve_bucket

bucket = resolve_bucket(None)
assert bucket, "S3_BUCKET não resolvido a partir do .env"
assert "SEU-BUCKET" not in json.dumps(bucket_policy(bucket))

bp = bucket_policy("meu-bucket")
recursos = bp["Statement"][0]["Resource"]
assert recursos == [
    "arn:aws:s3:::meu-bucket/feed.xml",
    "arn:aws:s3:::meu-bucket/estado.json",
    "arn:aws:s3:::meu-bucket/cover.jpg",
    "arn:aws:s3:::meu-bucket/audio/*",
    "arn:aws:s3:::meu-bucket/referencias/*",
], recursos
assert all(r.startswith("arn:aws:s3:::") for r in recursos), "ARN mal formado"
assert not any("s3://" in r for r in recursos), "ARN não usa esquema s3://"
assert bp["Statement"][0]["Principal"] == "*"
assert bp["Statement"][0]["Action"] == "s3:GetObject", "leitura apenas"

ip = iam_policy("meu-bucket")
assert ip["Statement"][0]["Action"] == "s3:PutObject", "upload só escreve"
assert ip["Statement"][0]["Resource"] == "arn:aws:s3:::meu-bucket/*"
assert "Principal" not in ip["Statement"][0], "policy de IAM não leva Principal"
print(f"    bucket resolvido do .env: {bucket}")
PYEOF

# Placeholder em comando de shell é inofensivo (o leitor substitui e vê o erro
# na hora). Dentro de um bloco JSON de policy, não: gera o "Policy has invalid
# resource", que não diz o que houve. Esse é o caso que o teste veda.
python3 - <<'PYEOF' && ok "nenhuma policy JSON na doc com placeholder" || bad "policy JSON com placeholder"
import pathlib, re, sys
doc = pathlib.Path("docs/setup-s3.md").read_text(encoding="utf-8")
for bloco in re.findall(r"```json\n(.*?)```", doc, re.S):
    if "arn:aws:s3:::" in bloco and "SEU-BUCKET" in bloco:
        print("    bloco problemático:", bloco.strip()[:80])
        sys.exit(1)
PYEOF

# s3.py roda como script além de biblioteca: sozinho, precisa ler o .env por
# conta própria — antes só o publish.py fazia isso, e o CLI ficava sem credencial.
python3 - <<'PYEOF' && ok "s3.py lê o .env quando roda como script" || bad "s3.py não carrega o .env"
import os, pathlib, sys, tempfile
sys.path.insert(0, "scripts")
import s3

original = s3.ROOT
tmp = pathlib.Path(tempfile.mkdtemp())
(tmp / ".env").write_text(
    "# comentário\nAWS_ACCESS_KEY_ID=AKIDOENV\n"
    'AWS_SECRET_ACCESS_KEY="segredo-do-env"\n', encoding="utf-8")
for k in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
    os.environ.pop(k, None)
try:
    s3.ROOT = tmp
    c = s3.load_credentials()
    assert c.access_key == "AKIDOENV", c.access_key
    assert c.secret_key == "segredo-do-env", c.secret_key   # aspas removidas

    # Ambiente explícito continua vencendo o .env.
    os.environ["AWS_ACCESS_KEY_ID"] = "DO-AMBIENTE"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "s"
    assert s3.load_credentials().access_key == "DO-AMBIENTE"
finally:
    s3.ROOT = original
    for k in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"):
        os.environ.pop(k, None)
PYEOF

# Coerência entre S3_PREFIX e base_url: divergência gera feed apontando para
# objetos inexistentes, e isso só apareceria no app do ouvinte.
python3 - <<'PYEOF' && ok "recusa S3_PREFIX incoerente com base_url" || bad "coerência de prefixo"
import os, sys
sys.path.insert(0, "scripts")
import publish

os.environ["S3_BUCKET"] = "campscast"
os.environ["AWS_ACCESS_KEY_ID"] = "AKIDEXAMPLE"
os.environ["AWS_SECRET_ACCESS_KEY"] = "segredo"

# Prefixo declarado, base_url sem ele -> tem de recusar antes de subir nada.
os.environ["S3_PREFIX"] = "podcast"
assert publish.upload("2026-08-24", {
    "base_url": "https://campscast.s3.us-east-1.amazonaws.com"}) is False

# Prefixo e base_url coerentes: passa da checagem (falha depois, na rede).
os.environ["S3_PREFIX"] = ""
show = {"base_url": "https://campscast.s3.us-east-1.amazonaws.com"}
PYEOF

# O feed publicado precisa apontar para o bucket configurado.
python3 - <<'PYEOF' && ok "show.json e .env descrevem o mesmo destino" || bad "show.json e .env divergem"
import json, pathlib, re, sys

show = json.loads(pathlib.Path("config/show.json").read_text(encoding="utf-8"))
base = show["base_url"].rstrip("/")
assert not base.startswith("https://exemplo.invalid"), "base_url ainda é de exemplo"

env = pathlib.Path(".env")
if env.exists():
    vals = dict(
        ln.split("=", 1) for ln in env.read_text(encoding="utf-8").splitlines()
        if "=" in ln and not ln.strip().startswith("#")
    )
    bucket = vals.get("S3_BUCKET", "").strip()
    prefix = vals.get("S3_PREFIX", "").strip().strip("/")
    if bucket:
        assert bucket in base, f"base_url {base} não menciona o bucket {bucket}"
        if prefix:
            assert base.endswith(prefix), f"base_url não termina no prefixo {prefix}"
    # A capa referenciada no feed precisa estar sob a mesma base.
    assert show["cover_url"].startswith(base), "cover_url fora da base_url"
print(f"    {base}")
PYEOF

# set_base_url só grava se o domínio já servir os arquivos. Trocar antes disso
# publica um feed cujos episódios apontam para o nada — e depois da submissão
# aos diretórios isso vira download falhando em silêncio no app do ouvinte.
OUT_BU="$(python3 scripts/set_base_url.py https://dominio-que-nao-existe-campscast.invalid --dry-run 2>&1 || true)"
if [[ "$OUT_BU" == *"Não gravei nada"* ]]; then
  ok "set_base_url recusa domínio que não responde"
else
  bad "set_base_url deveria recusar domínio inexistente"
fi
python3 - <<'PYEOF' && ok "set_base_url exige https" || bad "set_base_url deveria exigir https"
import subprocess, sys
r = subprocess.run([sys.executable, "scripts/set_base_url.py", "http://campscast.com.br"],
                   capture_output=True, text=True)
assert r.returncode == 2, r.returncode
assert "https" in r.stderr
PYEOF
python3 -c "
import json,pathlib,sys
s=json.loads(pathlib.Path('config/show.json').read_text(encoding='utf-8'))
sys.exit(0 if s['base_url'].startswith('https://') else 1)"   && ok "base_url do projeto usa https" || bad "base_url não usa https"

# ----------------------------------------------------- 11 precedência do .env
head_ "11. Precedência de variáveis (.env vs ambiente)"
# Um CLAUDE_BIN no .env não pode sobrescrever o que veio do ambiente: era assim
# que um teste com CLI falso acabava chamando o Claude de verdade.
ENV_BAK=""
if [[ -f .env ]]; then ENV_BAK="$(mktemp)"; cp .env "$ENV_BAK"; fi
printf 'CLAUDE_BIN=/bin/echo\n' >> .env

STUB_DIR="$(mktemp -d)"
printf '#!/bin/sh\necho "STUB-VENCEU"\nexit 1\n' > "$STUB_DIR/claude"
chmod +x "$STUB_DIR/claude"
OUT_PREC="$(CLAUDE_BIN="$STUB_DIR/claude" bash scripts/run_episode.sh \
             --date 2026-08-25 --only research 2>&1 || true)"
rm -rf "$STUB_DIR"
if [[ -n "$ENV_BAK" ]]; then mv "$ENV_BAK" .env; else rm -f .env; fi
rm -f logs/2026-08-25.log

if [[ "$OUT_PREC" == *"STUB-VENCEU"* ]]; then
  ok "variável do ambiente vence o .env"
else
  bad "o .env sobrescreveu uma variável passada no ambiente"
fi

# Um .env em branco não pode virar CLAUDE_BIN vazio nem quebrar o parse.
if grep -qE '^\s*CLAUDE_BIN=' .env.example 2>/dev/null; then
  bad ".env.example define CLAUDE_BIN sem comentário — é armadilha"
else
  ok ".env.example deixa CLAUDE_BIN comentado"
fi

# ------------------------------------------------- 12 métricas de áudio
head_ "12. Métricas de áudio (ganho e codec)"
# Dois bugs achados comparando MacBook e iPhone gravando o mesmo minuto:
#  - o limiar de silêncio era absoluto (-50 dBFS), então o aparelho de ganho
#    maior era julgado "sem silêncio" só por amplificar mais;
#  - o codec era adivinhado pelo bitrate, e ALAC mono de 16 bits comprime tanto
#    que caía abaixo do corte e era rotulado "com perdas".
AUD_DIR="$(mktemp -d)"
python3 - "$AUD_DIR" <<'PY'
import math, random, struct, sys, wave, pathlib
saida = pathlib.Path(sys.argv[1])
TAXA = 44100
random.seed(7)

def escreve(caminho, ganho_db, ruido=40, silencio_s=4, dur_s=12):
    g = 10 ** (ganho_db / 20)
    quadros = []
    for i in range(TAXA * dur_s):
        t = i / TAXA
        r = random.gauss(0, ruido)              # piso constante
        if t > silencio_s:                      # silêncio, depois "fala"
            fase = 2 * math.pi * 180 * t
            voz = 4000 * math.sin(fase) * (0.6 + 0.4 * math.sin(2 * math.pi * 3 * t))
        else:
            voz = 0.0
        v = max(-32000, min(32000, int((voz + r) * g)))
        quadros.append(v)
    with wave.open(str(caminho), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(TAXA)
        w.writeframes(b"".join(struct.pack("<h", v) for v in quadros))

escreve(saida / "baixo.wav", 0)
escreve(saida / "ruidoso.wav", 0, ruido=900)   # mesmo eco, S/R baixo
escreve(saida / "quase_tudo_fala.wav", 0, silencio_s=3, dur_s=33)
escreve(saida / "alto.wav", 14)    # mesmo conteúdo, 14 dB de ganho a mais
                                   # (piso vai a -44 dBFS, acima do antigo limiar fixo)
PY

# ALAC mono de 16 bits: bitrate baixo, mas sem perdas.
afconvert -f m4af -d alac "$AUD_DIR/baixo.wav" "$AUD_DIR/baixo.m4a" 2>/dev/null

MET="$(python3 - "$AUD_DIR" <<'PY'
import sys, pathlib
sys.path.insert(0, "scripts")
from audio_metrics import analisa
d = pathlib.Path(sys.argv[1])
b = analisa(d / "baixo.wav")
a = analisa(d / "alto.wav")
m = analisa(d / "baixo.m4a")
n = analisa(d / "ruidoso.wav")
q = analisa(d / "quase_tudo_fala.wav")
print(f"{b['silencio_s']:.1f} {a['silencio_s']:.1f} {b['snr']:.1f} {a['snr']:.1f} "
      f"{m['tipo_codec']} {m['taxa_bits']} {int(b['reverb_confiavel'])} "
      f"{int(n['reverb_confiavel'])} {n['snr']:.1f} {q['piso']:.1f}")
PY
)" || MET=""
read -r SIL_B SIL_A SNR_B SNR_A CODEC1 CODEC2 KBPS REV_OK REV_RUIM SNR_N PISO_Q <<< "$MET"
rm -rf "$AUD_DIR"

if [[ -z "$MET" ]]; then
  bad "analisa() falhou nos arquivos sintéticos"
else
  # O arquivo com mais ganho tem que achar silêncio igual ao outro.
  if awk -v a="$SIL_A" 'BEGIN{exit !(a >= 1.5)}'; then
    ok "silêncio detectado apesar do ganho maior (${SIL_A}s)"
  else
    bad "ganho maior escondeu o silêncio (${SIL_A}s contra ${SIL_B}s) — limiar absoluto"
  fi
  # S/R é uma razão: não pode mudar quando só o ganho muda.
  if awk -v x="$SNR_B" -v y="$SNR_A" 'BEGIN{exit !((x-y < 2) && (y-x < 2))}'; then
    ok "S/R não muda com o ganho (${SNR_B} contra ${SNR_A} dB)"
  else
    bad "S/R mudou só por causa do ganho (${SNR_B} contra ${SNR_A} dB)"
  fi
  # Reverberação medida com pouco S/R é ruído, não sala: precisa se declarar
  # não confiável. Somar ruído branco à mesma gravação levava a estimativa de
  # 0,48s para 0,95s sem que a sala mudasse.
  if [[ "$REV_OK" == "1" && "$REV_RUIM" == "0" ]]; then
    ok "reverberação se declara não confiável com S/R baixo (${SNR_N} dB)"
  else
    bad "reverberação não distingue S/R alto de baixo (${REV_OK}/${REV_RUIM})"
  fi
  # Arquivo 90% falado: o piso tem que sair dos 3s de silêncio (-58 dBFS),
  # não das pausas entre palavras. Um limiar por percentil caía dentro da fala
  # e media a voz — deu -41,8 dBFS onde a sala estava a -54.
  if awk -v p="$PISO_Q" 'BEGIN{exit !(p < -50)}'; then
    ok "piso vem do trecho mais silencioso, não das pausas (${PISO_Q} dBFS)"
  else
    bad "piso medido nas pausas da fala (${PISO_Q} dBFS, esperado < -50)"
  fi
  # Sem silêncio, a dinâmica é contada a partir de um piso errado e acusa 0 dB
  # de variação numa fala expressiva. Não pode virar alarme.
  SEMSIL="$(python3 - <<'PYSIL'
import importlib.util, pathlib, sys
sys.path.insert(0, "scripts")
spec = importlib.util.spec_from_file_location("cr", "scripts/check_recording.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
falso = {"dinamica": 0.0, "piso_confiavel": False, "snr": 7.0, "piso": -29.5,
         "fala": -22.1, "pico": -4.6, "clipes": 0, "crista": 20.3, "reverb": 0.7,
         "reverb_confiavel": False, "silencio_s": 0.0, "taxa_bits": 1440,
         "tipo_codec": "sem perdas", "duracao": 115.0}
avisos = " ".join(txt for _, txt in m.veredito(falso))
print("limpo" if "ganho automático" not in avisos else "alarme falso")
PYSIL
)" || SEMSIL="falhou"
if [[ "$SEMSIL" == "limpo" ]]; then
  ok "dinâmica não vira alarme quando o piso não é confiável"
else
  bad "alarme de ganho automático com piso não confiável ($SEMSIL)"
fi
  # Exportar a mesma gravação duas vezes dá contêineres com metadados
  # diferentes: tamanho igual ao byte, hash de arquivo diferente, áudio igual.
  # Só o PCM denuncia, e amostra repetida entra no treino com peso dobrado.
  DUP="$(python3 - <<'PYDUP'
import sys, pathlib, shutil, struct, wave, random, tempfile, importlib.util
sys.path.insert(0, "scripts")
spec = importlib.util.spec_from_file_location("pvs", "scripts/prep_voice_samples.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
d = pathlib.Path(tempfile.mkdtemp())
def grava(nome, semente):
    random.seed(semente)
    q = b"".join(struct.pack("<h", random.randint(-9000, 9000)) for _ in range(44100))
    with wave.open(str(d / nome), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(44100); w.writeframes(q)
grava("a.wav", 1); grava("outro.wav", 2)
shutil.copy(d / "a.wav", d / "copia.wav")
a, b = m._impressao(d / "a.wav"), m._impressao(d / "copia.wav")
c = m._impressao(d / "outro.wav")
shutil.rmtree(d)
print("ok" if a == b and a != c else "falhou")
PYDUP
)" || DUP="erro"
if [[ "$DUP" == "ok" ]]; then
  ok "duplicata é detectada pelo áudio, não pelo arquivo"
else
  bad "detector de duplicata não distingue cópia de original ($DUP)"
fi
  # Voz sintética não faz pausa de 2s: exigir isso mede fala e achata o piso.
  # Com o arquivo sintético (4s de silêncio + tom), pedir 0,5s e pedir 2s têm
  # que dar o mesmo piso; o que não pode é a exigência longa piorar a medida.
  PAUSA="$(python3 - <<'PYPAUSA'
import sys, math, struct, wave, random, tempfile, pathlib
sys.path.insert(0, "scripts")
from audio_metrics import analisa
d = pathlib.Path(tempfile.mkdtemp())
random.seed(11)
TAXA = 44100
q = []
for i in range(TAXA * 10):
    t = i / TAXA
    voz = 0.0 if (t % 2.0) < 0.6 else 4000 * math.sin(2 * math.pi * 180 * t)
    q.append(max(-32000, min(32000, int(voz + random.gauss(0, 40)))))
caminho = d / "curto.wav"
with wave.open(str(caminho), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(TAXA)
    w.writeframes(b"".join(struct.pack("<h", v) for v in q))
curto = analisa(caminho, pausa_min=0.5)["piso"]
longo = analisa(caminho, pausa_min=2.0)["piso"]
print("ok" if curto < longo - 5 else f"falhou curto={curto:.1f} longo={longo:.1f}")
PYPAUSA
)" || PAUSA="erro"
if [[ "$PAUSA" == "ok" ]]; then
  ok "--pausa curta acha o piso onde a pausa longa não cabe"
else
  bad "pausa curta não melhora a medida em áudio sem silêncio longo ($PAUSA)"
fi
  # ALAC é sem perdas mesmo saindo abaixo de 400 kbps.
  if [[ "$CODEC1 $CODEC2" == "sem perdas" ]]; then
    ok "ALAC reconhecido como sem perdas (${KBPS} kbps)"
  else
    bad "ALAC de ${KBPS} kbps rotulado '$CODEC1 $CODEC2' — corte por bitrate"
  fi
fi

# ------------------------------------------------ 13 monitor de gravação
head_ "13. Monitor de gravação"
# Não dá para testar captura de microfone offline, mas o que quebra sem microfone
# é o resto: as funções puras e o aviso sobre comparar dBFS entre aparelhos.
MON="$(python3 - <<'PYMON'
import importlib.util
spec = importlib.util.spec_from_file_location("mon", "scripts/monitor.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
erros = []
if m.percentil([], 0.5) != -120.0: erros.append("percentil vazio")
if m.percentil([-60, -50, -40], 0.5) != -50: erros.append("percentil mediana")
if m.relogio(125) != "02:05": erros.append("relogio")
if len(m.barra(-40)) != 30: erros.append("largura da barra")
if m.barra(-100) != chr(9617)*30: erros.append("barra no piso")
linhas = m.analisador([-12.0] + [-90.0]*7, [-12.0] + [-90.0]*7)
if len(linhas) != m.ALTURA + 2: erros.append("altura do analisador")
if linhas[0].count(chr(9608)) != 3: erros.append("banda alta não chega ao topo")
if chr(9608) in linhas[m.ALTURA - 1].replace(linhas[m.ALTURA-1][:4], "", 1)[4:]:
    erros.append("banda baixa acendeu coluna errada")
print(";".join(erros) if erros else "ok")
PYMON
)" || MON="import falhou"
if [[ "$MON" == "ok" ]]; then
  ok "funções do monitor conferem"
else
  bad "monitor: $MON"
fi
if grep -q "não descrevem o arquivo dela" scripts/monitor.py; then
  ok "monitor avisa que os dBFS não valem para outro aparelho"
else
  bad "monitor não avisa sobre comparar dBFS entre aparelhos"
fi
if grep -q "localizedName" scripts/monitor.swift; then
  ok "monitor identifica de qual microfone está lendo"
else
  bad "monitor não diz de qual microfone vêm os números"
fi
# Separar voz de ruído por nível é impossível; por banda funciona. Os casos
# abaixo são os medidos nas gravações reais: avião e moto sobem os graves e
# deixam a banda de voz intacta, e a fala faz o contrário.
CLS="$(python3 - <<'PYCLS'
import importlib.util
spec = importlib.util.spec_from_file_location("mon", "scripts/monitor.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
BG, BV = -70.9, -81.1                      # quarto calmo, calibração
casos = [
    ("silêncio",  [-70.9] * 20, [-81.1] * 20, False, False),
    ("fala",      [-31.2] * 20, [-37.8] * 20, True,  True),
    ("avião",     [-56.5] * 20, [-80.0] * 20, False, True),
    ("moto",      [-41.6] * 20, [-79.9] * 20, False, True),
]
erros = []
for nome, g, v, voz_esp, ruido_esp in casos:
    voz, ruido, _ = m.classifica(g, v, BG, BV)
    if voz != voz_esp or ruido != ruido_esp:
        erros.append(f"{nome}(voz={voz},ruido={ruido})")
print(";".join(erros) if erros else "ok")
PYCLS
)" || CLS="erro"
if [[ "$CLS" == "ok" ]]; then
  ok "voz e ruído externo separados por banda, não por nível"
else
  bad "classificação por banda errou: $CLS"
fi

# ------------------------------------------ 14 silêncio, velocidade, pronúncia
head_ "14. Silêncio entre episódios, velocidade e pronúncia"
# Sem folga no fim, o Spotify emenda um episódio no anterior e parece o mesmo.
# O silêncio é montado à mão a partir do cabeçalho real; precisa ter a duração
# pedida e ser lido como MP3 válido pelo mesmo parser do feed.
SIL="$(python3 - <<'PYSIL'
import importlib.util, pathlib, sys, tempfile
sys.path.insert(0, "scripts")
spec = importlib.util.spec_from_file_location("tts", "scripts/tts.py")
tts = importlib.util.module_from_spec(spec); spec.loader.exec_module(tts)
from publish import mp3_duration_seconds
erros = []
ref = bytes.fromhex("fffb90c4") + bytes(413)          # quadro mono 128 kbps 44,1 kHz
s = tts.silencio_mp3(ref, 1.0)
if len(s) != 38 * 417: erros.append(f"tamanho {len(s)}")
if s[:4] != bytes.fromhex("fffb90c4"): erros.append("cabeçalho")
if any(s[k:k+4] != s[:4] for k in range(0, len(s), 417)): erros.append("quadro fora do passo")
arq = pathlib.Path(tempfile.mkdtemp()) / "s.mp3"; arq.write_bytes(s * 3)
d = mp3_duration_seconds(arq)
if not d or abs(d - 3.0) > 0.1: erros.append(f"duração {d}")
if tts.silencio_mp3(b"nao sou mp3", 1.0) != b"": erros.append("formato desconhecido não degradou")
if tts.silencio_mp3(ref, 0) != b"": erros.append("zero segundos gerou quadros")
m = {"Anthropic": "Antrópic"}
if tts.aplica_pronuncia("A Anthropic e a Anthropics.", m) != "A Antrópic e a Anthropics.":
    erros.append("pronúncia não respeita palavra inteira")
print(";".join(erros) if erros else "ok")
PYSIL
)" || SIL="import falhou"
if [[ "$SIL" == "ok" ]]; then
  ok "silêncio MP3 com duração certa e pronúncia por palavra inteira"
else
  bad "silêncio/pronúncia: $SIL"
fi
if python3 scripts/tts.py --script tests/fixtures/sample-episode.md --speed 1.5 --dry-run >/dev/null 2>&1; then
  bad "tts.py aceitou --speed fora do limite da API"
else
  ok "tts.py recusa --speed fora de 0.7–1.2"
fi
if python3 -c "import json;c=json.load(open('config/tts.json'));assert c['silence_end_s']>=1" 2>/dev/null; then
  ok "config/tts.json tem folga de silêncio no fim"
else
  bad "config/tts.json sem silence_end_s"
fi

# ---------------------------------------- 15 número do episódio e ficha técnica
head_ "15. Número do episódio e nomes da ficha técnica"
# A ficha técnica disse "Flash 2.5" por quatro episódios depois da troca para o
# Multilingual v2, porque o nome falado era um campo mantido à mão.
NOM="$(python3 - <<'PYNOM'
import importlib.util, json, pathlib, tempfile
spec = importlib.util.spec_from_file_location("nomes", "scripts/nomes.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
erros = []
for k, v in {"claude-opus-5": "Claude Opus 5", "claude-fable-5-1": "Claude Fable 5.1",
             "claude-haiku-4-5-20251001": "Claude Haiku 4.5"}.items():
    if m.nome_agente(k) != v: erros.append(f"agente {k} -> {m.nome_agente(k)}")
for k, v in {"eleven_multilingual_v2": "ElevenLabs Multilingual v2",
             "eleven_flash_v2_5": "ElevenLabs Flash v2.5", "eleven_v3": "ElevenLabs v3"}.items():
    if m.nome_tts(k) != v: erros.append(f"tts {k} -> {m.nome_tts(k)}")
if "_nome_falado" in json.load(open("config/tts.json")):
    erros.append("_nome_falado voltou ao config")
d = pathlib.Path(tempfile.mkdtemp())
def ep(data, n=None):
    (d / f"{data}.md").write_text(f"---\ndate: {data}\n" + (f"episode: {n}\n" if n else "") + "---\nx\n")
ep("2026-01-01", 1); ep("2026-01-02", 2)
if m.proximo_numero("2026-01-05", d) != 3: erros.append("próximo não é o maior + 1")
if m.proximo_numero("2026-01-02", d) != 2: erros.append("reexecução renumerou")
(d / "2026-01-01.md").unlink()
if m.proximo_numero("2026-01-05", d) != 3: erros.append("apagar episódio renumerou")
e = pathlib.Path(tempfile.mkdtemp()); (e / "2026-01-01.md").write_text("---\ndate: 2026-01-01\n---\n")
if m.proximo_numero("2026-01-02", e) != 2: erros.append("sem número gravado não contou os anteriores")
reais = sorted(p for p in pathlib.Path("episodes").glob("*.md") if p.stem[:4].isdigit())
nums = [m._numero_gravado(p) for p in reais]
if None in nums or any(b <= a for a, b in zip(nums, nums[1:])):
    erros.append(f"episódios reais sem número crescente: {nums}")
print(";".join(erros) if erros else "ok")
PYNOM
)" || NOM="import falhou"
if [[ "$NOM" == "ok" ]]; then
  ok "nomes da ficha derivados dos ids; número não renumera"
else
  bad "nomes/número: $NOM"
fi
PUB="$(python3 - <<'PYPUB'
import json, pathlib, sys
sys.path.insert(0, "scripts")
import publish
show = json.load(open("config/show.json"))
base = {"date": "2026-09-14", "title": "t", "topics": ["a"], "audio_path": pathlib.Path("audio/x.mp3"),
        "size": 1, "duration": 60}
com = publish.build_feed(show, [{**base, "episode": "12"}])
sem = publish.build_feed(show, [base])
print("ok" if "<itunes:episode>12</itunes:episode>" in com and "<itunes:episode>" not in sem else "falhou")
PYPUB
)" || PUB="erro"
if [[ "$PUB" == "ok" ]]; then
  ok "feed leva <itunes:episode> quando o roteiro tem número"
else
  bad "feed sem <itunes:episode> ($PUB)"
fi
if grep -q "EPISODE_NUMBER" prompts/master.md && grep -q "AGENTE_NOME" prompts/master.md \
   && ! grep -qi "observar hoje: " prompts/master.md && ! grep -q "recap em três frases" prompts/master.md; then
  ok "prompt: número na abertura, encerramento só com a ficha"
else
  bad "prompt sem número, sem AGENTE_NOME, ou ainda com recap"
fi
LOG14="logs/2026-09-14.log"; JA_EXISTIA=0; [[ -f "$LOG14" ]] && JA_EXISTIA=1
DRY="$(bash scripts/run_episode.sh --date 2026-09-14 --dry-run 2>&1 || true)"
[[ $JA_EXISTIA -eq 0 ]] && rm -f "$LOG14"
if [[ "$DRY" == *"--model claude-opus-5"* && "$DRY" == *"Episódio nº "* ]]; then
  ok "orquestrador fixa o modelo e anuncia o número"
else
  bad "dry-run sem --model ou sem número do episódio"
fi

# ----------------------------------------------- 16 registro de execução e custo
# A ficha técnica falada já anunciou o modelo errado por quatro episódios. A
# descrição pública do podcast repetiu o mesmo erro por mais tempo, porque
# ninguém a relê. Nome de versão em texto que não é derivado do config vira
# mentira na primeira troca: proíbe-se.
if python3 - <<'FIM'
import json, re, sys
d = json.load(open("config/show.json"))
alvo = d["description"] + " " + d.get("subtitle", "")
proibido = re.findall(r"(?i)(flash\s*v?2\.?5|multilingual\s*v?2|turbo\s*v?2|eleven_[a-z0-9_]+)", alvo)
if proibido:
    print("versão de modelo na descrição pública:", proibido)
    sys.exit(1)
FIM
then
  ok "descrição pública não cita versão de modelo de TTS"
else
  bad "descrição pública cita versão de modelo — vira mentira na próxima troca"
fi

head_ "16. Registro de execução e custo"
REG="$(python3 - <<'PYREG'
import json, os, pathlib, subprocess, sys, tempfile, time
erros = []
d = pathlib.Path(tempfile.mkdtemp())
def grava(nome, obj):
    p = d / nome
    p.write_text(obj if isinstance(obj, str) else json.dumps(obj))
    return p
def resultado(p):
    return subprocess.run([sys.executable, "scripts/registro.py", "resultado", str(p)],
                          capture_output=True, text=True)
r = resultado(grava("ok.json", {"result": "OK episodes/x.md 1 00:01", "is_error": False, "usage": {}}))
if r.returncode != 0 or r.stdout.strip() != "OK episodes/x.md 1 00:01": erros.append("resultado ok")
if resultado(grava("erro.json", {"result": "Failed to authenticate", "is_error": True, "usage": {}})).returncode != 4:
    erros.append("is_error não virou falha")
if resultado(grava("texto.json", "OK episodes/x.md 1 00:01")).returncode != 3:
    erros.append("texto puro não caiu no reserva")
inicio = time.time() - 100
agente = grava("agente.json", {"result": "OK", "is_error": False, "num_turns": 7, "total_cost_usd": 1.5,
    "duration_api_ms": 60000, "session_id": "sem-transcricao", "usage": {"input_tokens": 9},
    "modelUsage": {"claude-opus-5": {"inputTokens": 10, "outputTokens": 20, "cacheReadInputTokens": 300, "cacheCreationInputTokens": 40},
                   "claude-haiku": {"inputTokens": 1, "outputTokens": 2, "cacheReadInputTokens": 3, "cacheCreationInputTokens": 4}}})
tts = grava("tts.json", {"creditos": 4600, "creditos_exatos": True, "caracteres": 8300})
velho = grava("velho.json", {"indice_pautas_bytes": 1})
os.utime(velho, (inicio - 3600, inicio - 3600))
destino = d / "execucoes.jsonl"
subprocess.run([sys.executable, "scripts/registro.py", "fecha", "--data", "2026-01-02", "--estado", "ok",
    "--inicio", str(inicio), "--pesquisa", str(inicio + 10), "--narracao", str(inicio + 80),
    "--agente", str(agente), "--tts", str(tts), "--indicadores", str(velho), "--modelo", "claude-opus-5"],
    env={**os.environ, "METRICAS_ARQ": str(destino)}, capture_output=True, check=True)
l = json.loads(destino.read_text().splitlines()[-1])
if l["claude"]["cache_lido"] != 303: erros.append(f"soma entre modelos: {l['claude']['cache_lido']}")
if l["claude"]["custo_estimado_usd"] != 1.5: erros.append("custo estimado")
if l["elevenlabs"]["creditos"] != 4600: erros.append("créditos")
if l["indicadores"] is not None: erros.append("aproveitou arquivo de outra execução")
if set(l["etapas_s"]) != {"pesquisa", "narracao"} or l["etapas_s"]["pesquisa"] != 70:
    erros.append(f"etapas {l['etapas_s']}")
print(";".join(erros) if erros else "ok")
PYREG
)" || REG="import falhou"
if [[ "$REG" == "ok" ]]; then
  ok "registro lê o JSON do agente, soma modelos e ignora arquivo de outra execução"
else
  bad "registro: $REG"
fi

# Sono pelo pmset: trecho real das falhas de 11/09. "Wake Requests" não é
# despertar (o primeiro cálculo registrou 3 s onde houve 14 min), e DarkWake é
# sistema acordado de tela apagada (o segundo pôs para dormir uma execução que
# concluiu). Parado é só de "Entering Sleep" até o próximo despertar.
SONO="$(python3 - <<'PYSONO'
import datetime as dt, importlib.util
spec = importlib.util.spec_from_file_location("registro", "scripts/registro.py")
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
log = """2026-09-11 06:50:00 -0300 Wake                	Wake from Normal Sleep [CDNVA] : due to lid
2026-09-11 06:55:00 -0300 Sleep               	Entering Sleep state due to 'Clamshell Sleep'
2026-09-11 07:06:39 -0300 DarkWake            	DarkWake from Deep Idle [CDNP] : due to NUB.SPMI0
2026-09-11 07:06:41 -0300 Sleep               	Entering Sleep state due to 'Sleep Service Back to Sleep'
2026-09-11 07:06:44 -0300 Wake Requests       	[*process=dasd request=SleepService deltaSecs=915]
2026-09-11 07:21:20 -0300 Wake                	Wake from Deep Idle [CDNVA] : due to lid
"""
D = lambda s: dt.datetime.fromisoformat("2026-09-11T" + s)
erros = []
s = r.calcula_sono(log, D("07:06:39"), D("07:21:21"))
if s != {"vezes": 1, "segundos": 879}: erros.append(f"falha real: {s}")
segurado = """2026-09-09 05:40:00 -0300 Sleep               	Entering Sleep state due to 'Clamshell Sleep'
2026-09-09 05:50:00 -0300 DarkWake            	DarkWake from Deep Idle [CDNP] : due to RTC Using AC
"""
s = r.calcula_sono(segurado, dt.datetime.fromisoformat("2026-09-09T05:50:02"), dt.datetime.fromisoformat("2026-09-09T06:08:39"))
if s != {"vezes": 0, "segundos": 0}: erros.append(f"DarkWake segurado pelo caffeinate: {s}")
s = r.calcula_sono(log, D("06:51:00"), D("06:54:00"))
if s != {"vezes": 0, "segundos": 0}: erros.append(f"acordado: {s}")
if r.calcula_sono(log, D("06:00:00"), D("06:10:00")) is not None: erros.append("antes do log não é None")
print(";".join(erros) if erros else "ok")
PYSONO
)" || SONO="import falhou"
if [[ "$SONO" == "ok" ]]; then
  ok "sono: Wake Requests não acorda; DarkWake é acordado de tela apagada"
else
  bad "cálculo de sono: $SONO"
fi

# Ponta a ponta: o orquestrador com um agente falso que responde em JSON.
FAKE_REG="$(mktemp -d)"
cat > "$FAKE_REG/claude" <<'STUB'
#!/bin/sh
cat > episodes/2026-08-25.md <<'MD'
---
date: 2026-08-25
window_start: 2026-08-24
window_end: 2026-08-24
title: teste
words: 10
estimated_duration: 0:04
topics: []
from_backlog: []
---

Corpo de teste.
MD
printf '%s' '{"type":"result","is_error":false,"result":"OK episodes/2026-08-25.md 10 00:04","num_turns":3,"total_cost_usd":0.25,"session_id":"sem-transcricao","usage":{"input_tokens":1},"modelUsage":{"claude-opus-5":{"inputTokens":1,"outputTokens":2,"cacheReadInputTokens":30,"cacheCreationInputTokens":4}}}'
STUB
chmod +x "$FAKE_REG/claude"
OUT_REG="$(CLAUDE_BIN="$FAKE_REG/claude" bash scripts/run_episode.sh --date 2026-08-25 --only research 2>&1 || true)"
ULTIMA="$(tail -1 "$METRICAS_ARQ" 2>/dev/null)"
rm -f episodes/2026-08-25.md
if [[ "$OUT_REG" == *"Concluído"* && "$ULTIMA" == *'"estado": "ok"'* && "$ULTIMA" == *'"cache_lido": 30'* ]]; then
  ok "orquestrador lê a saída em JSON e grava a execução no registro"
else
  bad "execução com agente em JSON não foi registrada como ok"
fi

# Login expirado sai com código 0 e só a mensagem denuncia. Foi assim em 13/09.
cat > "$FAKE_REG/claude" <<'STUB'
#!/bin/sh
printf '%s' '{"type":"result","is_error":true,"result":"Failed to authenticate: OAuth session expired and could not be refreshed","usage":{}}'
exit 0
STUB
OUT_EXP="$(CLAUDE_BIN="$FAKE_REG/claude" bash scripts/run_episode.sh --date 2026-08-25 --only research 2>&1 || true)"
ULTIMA="$(tail -1 "$METRICAS_ARQ" 2>/dev/null)"
printf '#!/bin/sh\necho "Failed to authenticate: OAuth session expired and could not be refreshed"\nexit 0\n' > "$FAKE_REG/claude"
OUT_TXT="$(CLAUDE_BIN="$FAKE_REG/claude" bash scripts/run_episode.sh --date 2026-08-25 --only research 2>&1 || true)"
rm -rf "$FAKE_REG"
if [[ "$OUT_EXP" == *"não autenticado"* && "$OUT_TXT" == *"não autenticado"* && "$ULTIMA" == *'"estado": "falhou"'* ]]; then
  ok "login expirado com código 0 vira diagnóstico, em JSON e em texto, e falha registrada"
else
  bad "login expirado com código 0 passou despercebido"
fi
rm -f episodes/2026-08-25.md logs/2026-08-25.log logs/2026-08-2[345]-*.json

if [[ "$(shasum metricas/execucoes.jsonl 2>/dev/null || echo ausente)" == "$METRICAS_REAL_ANTES" ]]; then
  ok "smoke test não tocou no registro real"
else
  bad "smoke test escreveu em metricas/execucoes.jsonl"
fi

# --------------------------------------------- 17. estado público da execução
head_ "17. Estado público da execução"

EST_TMP="$(mktemp)"
python3 scripts/estado.py --data 2026-09-14 --estado falhou --etapa pesquisa \
  --motivo "falhou em /Users/alguem/CampsCast/logs/x.log com sk_abcdefghijklmnopqrstuvwxyz012345" \
  --saida "$EST_TMP" >/dev/null 2>&1
EST="$(cat "$EST_TMP")"
if [[ "$EST" != *"/Users/alguem"* && "$EST" != *"sk_abcdefghijklmnopqrstuvwxyz012345"* \
      && "$EST" == *"<usuario>"* && "$EST" == *"<omitido>"* ]]; then
  ok "estado público não vaza caminho de usuário nem token"
else
  bad "estado público vazou caminho ou token: $EST"
fi

python3 scripts/estado.py --data 2026-09-14 --estado ok --etapa concluido \
  --saida "$EST_TMP" >/dev/null 2>&1
EST_OK="$(cat "$EST_TMP")"
if [[ "$EST_OK" == *'"episodio"'* && "$EST_OK" == *'"motivo": ""'* ]]; then
  ok "estado de sucesso aponta o episódio e não carrega motivo"
else
  bad "estado de sucesso saiu errado: $EST_OK"
fi

# Motivo longo não pode virar um objeto público de tamanho imprevisível.
LONGO="$(python3 -c 'print("erro " * 200)')"
python3 scripts/estado.py --data 2026-09-14 --estado falhou --etapa narracao \
  --motivo "$LONGO" --saida "$EST_TMP" >/dev/null 2>&1
if [[ $(wc -c < "$EST_TMP") -lt 600 ]]; then
  ok "motivo longo é truncado"
else
  bad "motivo longo passou inteiro ($(wc -c < "$EST_TMP") bytes)"
fi
rm -f "$EST_TMP"

# O estado só serve se for legível de fora; a policy tem de incluí-lo.
if python3 scripts/s3.py --print-policy --bucket exemplo 2>/dev/null | grep -q "exemplo/estado.json"; then
  ok "bucket policy publica o estado.json"
else
  bad "bucket policy não inclui estado.json — o vigia externo receberia 403"
fi

# ESTADO_ARQ existe justamente para que o teste seguinte não suba nada.
EST_RUN="$(mktemp)"
FAKE_EST="$(mktemp -d)"
printf '#!/bin/sh\nexit 7\n' > "$FAKE_EST/claude"
chmod +x "$FAKE_EST/claude"
ESTADO_ARQ="$EST_RUN" CLAUDE_BIN="$FAKE_EST/claude" \
  bash scripts/run_episode.sh --date 2026-08-26 --only research >/dev/null 2>&1 || true
EST_FALHA="$(cat "$EST_RUN" 2>/dev/null)"
rm -rf "$FAKE_EST"; rm -f "$EST_RUN"
rm -f episodes/2026-08-26.md logs/2026-08-26.log logs/2026-08-26-*.json
if [[ "$EST_FALHA" == *'"estado": "falhou"'* && "$EST_FALHA" == *'"etapa": "pesquisa"'* ]]; then
  ok "falha na pesquisa publica estado com a etapa onde parou"
else
  bad "falha na pesquisa não publicou estado: ${EST_FALHA:-<vazio>}"
fi

# espera_rede nunca pode abortar o pipeline, mesmo sem resolver nada.
SAIDA_REDE="$(
  set +e
  source /dev/stdin <<'FIM' 2>&1
log() { printf '%s\n' "$*"; }
espera_rede() {
  local tentativas=${1:-12} i
  for ((i = 1; i <= tentativas; i++)); do
    if python3 -c "import socket; socket.getaddrinfo('nao.existe.invalid', 443)" 2>/dev/null; then
      return 0
    fi
    sleep 0
  done
  log "AVISO: DNS não resolveu; seguindo assim mesmo."
  return 0
}
espera_rede 1
echo "rc=$?"
FIM
)"
if [[ "$SAIDA_REDE" == *"rc=0"* && "$SAIDA_REDE" == *"AVISO"* ]]; then
  ok "espera de rede avisa e segue em vez de abortar"
else
  bad "espera de rede não seguiu: $SAIDA_REDE"
fi

# ------------------------------------------------------------------- resultado
printf '\n\033[1m%s\033[0m\n' "Resultado: $PASS ok, $FAIL falha(s)"
[[ $FAIL -eq 0 ]] || exit 1
