#!/usr/bin/env python3
"""
CampsCast — narração do roteiro via ElevenLabs.

Lê episodes/YYYY-MM-DD.md, descarta o front-matter YAML, quebra o corpo em
trechos que cabem numa requisição e concatena o MP3 resultante.

Sem dependências externas: usa apenas a stdlib.

Uso:
    python3 scripts/tts.py --script episodes/2026-08-24.md --out audio/2026-08-24.mp3
    python3 scripts/tts.py --script ... --out ... --dry-run   # não chama a API
    python3 scripts/tts.py --check                            # valida chave, voz e cota
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
API_ROOT = "https://api.elevenlabs.io/v1"
API_BASE = f"{API_ROOT}/text-to-speech"
MAX_CHARS = 2400          # folga confortável para o Flash v2.5
# Ritmo de fala. É propriedade da VOZ, não do projeto: no mesmo roteiro, a voz
# Carla rendeu 125 palavras por minuto e a Paulo, 163 — dois minutos de
# diferença. Por isso o valor real mora em config/tts.json, junto do voice_id.
# Este é só o fallback para configurações antigas.
WORDS_PER_MINUTE = 140

# Limites do formato, em minutos (PROJETO.md §2). As margens existem porque o
# agente não acerta a contagem de palavras na mosca.
FLOOR_MIN, TARGET_MIN, CEILING_MIN = 5.5, 8.0, 9.5


# ----------------------------------------------------------------- utilidades
def load_env() -> None:
    """Carrega .env sem sobrescrever variáveis já presentes no ambiente."""
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def load_cfg() -> dict:
    return json.loads((ROOT / "config" / "tts.json").read_text(encoding="utf-8"))


def wpm(cfg: dict) -> int:
    return int(cfg.get("words_per_minute") or WORDS_PER_MINUTE)


def word_budget(cfg: dict) -> dict:
    """Faixa de palavras que cabe no formato, dada a velocidade desta voz."""
    rate = wpm(cfg)
    return {
        "min": round(FLOOR_MIN * rate),
        "target": round(TARGET_MIN * rate),
        "max": round(CEILING_MIN * rate),
        "wpm": rate,
    }


def strip_front_matter(text: str) -> str:
    """Remove o bloco YAML `---...---` do topo, se houver."""
    if text.lstrip().startswith("---"):
        parts = text.lstrip().split("---", 2)
        if len(parts) >= 3:
            return parts[2].lstrip()
    return text


MARKDOWN_NOISE = [
    (re.compile(r"^#{1,6}\s*", re.M), ""),          # títulos
    (re.compile(r"\*\*(.+?)\*\*", re.S), r"\1"),    # negrito
    (re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", re.S), r"\1"),  # itálico
    (re.compile(r"`([^`]*)`"), r"\1"),              # code inline
    (re.compile(r"\[([^\]]+)\]\([^)]+\)"), r"\1"),  # links
    (re.compile(r"^\s*[-*+]\s+", re.M), ""),        # bullets
    (re.compile(r"^\s*>\s?", re.M), ""),            # citação
    (re.compile(r"https?://\S+"), ""),              # URLs soltas
    (re.compile(r"\n{3,}"), "\n\n"),
]


def to_speakable(body: str) -> str:
    """Rede de segurança: o roteiro já deveria vir sem markdown."""
    for pattern, repl in MARKDOWN_NOISE:
        body = pattern.sub(repl, body)
    return body.strip()


def chunk(text: str, limit: int = MAX_CHARS) -> list[str]:
    """Quebra por parágrafo; parágrafo grande demais é quebrado por frase."""
    chunks: list[str] = []
    buf = ""
    for para in [p.strip() for p in text.split("\n\n") if p.strip()]:
        if len(para) > limit:
            for sent in re.split(r"(?<=[.!?])\s+", para):
                if len(buf) + len(sent) + 1 > limit and buf:
                    chunks.append(buf.strip())
                    buf = ""
                buf += sent + " "
            continue
        if len(buf) + len(para) + 2 > limit and buf:
            chunks.append(buf.strip())
            buf = ""
        buf += para + "\n\n"
    if buf.strip():
        chunks.append(buf.strip())
    return chunks


SSL_HINT = (
    "Falha de certificado TLS. O Python instalado do python.org no macOS não usa\n"
    "  o repositório de certificados do sistema. Rode uma vez:\n"
    '      "/Applications/Python 3.13/Install Certificates.command"\n'
    "  (ajuste a versão para a sua). Ele instala o certifi e cria o link do cert.pem."
)


def explain_network_error(e: Exception) -> str:
    text = str(e)
    if "CERTIFICATE_VERIFY_FAILED" in text:
        return SSL_HINT
    return text


def api_get(path: str, api_key: str) -> dict:
    req = urllib.request.Request(
        f"{API_ROOT}/{path}",
        headers={"xi-api-key": api_key, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def settled_character_count(api_key: str, timeout: float = 90.0) -> int | None:
    """Cota consumida, depois que o contador para de subir.

    O contador da ElevenLabs é assíncrono: logo após uma síntese ele ainda não
    reflete o consumo. Ler cedo demais produz números absurdamente baixos — numa
    medição chegou a reportar 609 créditos onde o valor real eram 2.074, o que
    quase virou uma conclusão errada sobre custo no ADR.
    """
    deadline = time.time() + timeout
    previous, stable = None, 0
    while time.time() < deadline:
        try:
            current = api_get("user/subscription", api_key).get("character_count")
        except Exception:
            return None
        if current == previous:
            stable += 1
            if stable >= 3:           # três leituras iguais seguidas
                return current
        else:
            stable = 0
        previous = current
        time.sleep(3)
    return previous


def try_api_get(path: str, api_key: str, needed_scope: str) -> dict | None:
    """GET opcional: uma chave só com Text to Speech não enxerga estes endpoints."""
    try:
        return api_get(path, api_key)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            print(f"          (sem permissão para ler — habilite '{needed_scope}' "
                  "na chave se quiser este dado)")
        elif e.code == 404:
            print("          (não encontrado)")
        else:
            print(f"          (HTTP {e.code})")
        return None
    except Exception:
        return None


def check(cfg: dict, api_key: str) -> int:
    """Valida credencial, voz e modelo.

    Uma chave criada só com o escopo "Text to Speech" não consegue ler cota nem
    metadados de voz — por isso esses dois são opcionais, e a validação de
    verdade é uma síntese minúscula, de poucos caracteres.
    """
    print(f"Voz     : {cfg['voice_id']}")
    print(f"Modelo  : {cfg['model_id']}")

    sub = try_api_get("user/subscription", api_key, "User (read)")
    used_before = None
    if sub:
        used_before = sub.get("character_count", 0)
        limit = sub.get("character_limit", 0)
        print(f"Conta   : plano {sub.get('tier', '?')}")
        print(f"Cota    : {used_before} de {limit} usados — "
              f"restam {max(0, limit - used_before)}")
    else:
        print("Cota    : indisponível com o escopo atual da chave.")

    voice = try_api_get(f"voices/{cfg['voice_id']}", api_key, "Voices (read)")
    if voice:
        labels = voice.get("labels") or {}
        print(f"Nome    : {voice.get('name', '?')}")
        if labels:
            print("          " + ", ".join(f"{k}={v}" for k, v in labels.items()))
        lang = str(labels.get("language", "")).lower()
        if lang and not lang.startswith(("pt", "portug")):
            print(f"AVISO: voz rotulada como '{labels.get('language')}'. O Flash v2.5 "
                  "é multilíngue, mas ouça um trecho antes do episódio inteiro.")

    # Prova real: sintetizar uma frase curta. Custa ~20 caracteres e valida de
    # uma vez chave, escopo, voz e modelo — o que os GETs acima não garantem.
    probe = "Teste de voz do CampsCast."
    print(f"Teste   : sintetizando {len(probe)} caracteres…")
    try:
        audio = synthesize(probe, cfg, api_key, None, None)
    except RuntimeError as e:
        msg = str(e)
        if "402" in msg or "paid_plan_required" in msg:
            print("ERRO: a conta Free não usa vozes da Voice Library pela API.",
                  file=sys.stderr)
            print("  Duas saídas:", file=sys.stderr)
            print("  1) Assinar o Starter (US$ 5/mês) — libera a voz de catálogo "
                  "escolhida.\n     É o caminho previsto no orçamento do projeto.",
                  file=sys.stderr)
            print("  2) Usar uma voz 'premade' (as padrão da ElevenLabs), que a "
                  "conta Free\n     acessa. Habilite 'Voices (read)' na chave e "
                  "rode: python3 scripts/tts.py --list-voices", file=sys.stderr)
        elif "401" in msg or "403" in msg:
            print("ERRO: chave rejeitada. Confira se ela tem o escopo "
                  "'Text to Speech' habilitado.", file=sys.stderr)
        elif "404" in msg:
            print(f"ERRO: voz {cfg['voice_id']} não encontrada. Confira o id em "
                  "https://elevenlabs.io/app/voice-library", file=sys.stderr)
        elif "CERTIFICATE_VERIFY_FAILED" in msg:
            print(f"ERRO: {SSL_HINT}", file=sys.stderr)
        else:
            print(f"ERRO: {msg}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERRO: {explain_network_error(e)}", file=sys.stderr)
        return 1

    if not audio:
        print("ERRO: a API respondeu sem áudio.", file=sys.stderr)
        return 1

    print(f"OK      : {len(audio)} bytes de MP3 recebidos. Chave, voz e modelo válidos.")

    # Mede o custo real por caractere. Modelos Flash/Turbo costumam ter desconto,
    # e essa taxa é o que decide qual plano aguenta um episódio por dia útil.
    if used_before is not None:
        after = try_api_get("user/subscription", api_key, "User (read)")
        if after:
            spent = after.get("character_count", 0) - used_before
            if spent > 0:
                rate = spent / len(probe)
                print(f"Custo   : {spent} créditos por {len(probe)} caracteres "
                      f"= {rate:.2f} crédito(s)/caractere")
                report_plan_fit(rate)
            else:
                print("Custo   : não medido — o contador de cota não registra uma "
                      "amostra tão pequena.\n          A tarifa real aparece ao "
                      "gerar o episódio inteiro.")
    return 0


BUSINESS_DAYS = 22
PLANS = [("Starter", 6, 30_000), ("Creator", 22, 121_000)]


def report_plan_fit(rate: float) -> None:
    """Traduz a taxa medida em episódios por mês, por plano."""
    episode_chars = 6_600            # tamanho típico de um roteiro do CampsCast
    per_episode = episode_chars * rate
    monthly = per_episode * BUSINESS_DAYS
    print(f"          um episódio (~{episode_chars} chars) ≈ {per_episode:,.0f} créditos; "
          f"{BUSINESS_DAYS} dias úteis ≈ {monthly:,.0f}/mês".replace(",", "."))
    for name, price, quota in PLANS:
        episodes = quota / per_episode
        verdict = "cobre" if episodes >= BUSINESS_DAYS else "NÃO cobre"
        print(f"          {name:<8} US$ {price:>2}/mês → {episodes:4.1f} episódios/mês  {verdict}")


# ------------------------------------------------- costura dos trechos de MP3
BITRATES = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]
SAMPLE_RATES = [44100, 48000, 32000, 0]


def _id3v2_len(data: bytes) -> int:
    if data[:3] == b"ID3" and len(data) >= 10:
        size = ((data[6] & 0x7F) << 21 | (data[7] & 0x7F) << 14
                | (data[8] & 0x7F) << 7 | (data[9] & 0x7F))
        return 10 + size
    return 0


def _frame_len(data: bytes) -> int:
    """Tamanho do frame MPEG1 Layer III que começa em data[0], ou 0."""
    if len(data) < 4 or data[0] != 0xFF or (data[1] & 0xE0) != 0xE0:
        return 0
    if (data[1] >> 3) & 0x03 != 3 or (data[1] >> 1) & 0x03 != 1:
        return 0                                  # não é MPEG1 Layer III
    bitrate_idx = (data[2] >> 4) & 0x0F
    rate_idx = (data[2] >> 2) & 0x03
    if bitrate_idx in (0, 15) or rate_idx == 3:
        return 0
    return int(144 * BITRATES[bitrate_idx] * 1000 / SAMPLE_RATES[rate_idx]) \
        + ((data[2] >> 1) & 0x01)


def strip_container(data: bytes) -> bytes:
    """Deixa só os frames de áudio, sem tags nem cabeçalho Xing/Info.

    Cada resposta da API é um MP3 completo, com tag ID3 e um frame de metadados
    Xing/Info que declara quantos frames o arquivo tem. Concatenar os arquivos
    crus produz um MP3 que os players truncam: eles leem o Info do primeiro
    trecho, acreditam que o episódio inteiro tem a duração daquele trecho, e
    param ali. Um episódio de oito minutos tocava dois.

    O somatório de frames (publish.mp3_duration_seconds) não via o problema
    porque varre o arquivo inteiro — só um player revelava.
    """
    start = _id3v2_len(data)
    end = len(data)
    if end - start >= 128 and data[end - 128:end - 125] == b"TAG":
        end -= 128                                # tag ID3v1 no fim
    body = data[start:end]

    length = _frame_len(body)
    if length and (b"Xing" in body[:length] or b"Info" in body[:length]):
        body = body[length:]                      # frame de metadados
    return body


_BITRATES_MPEG1_L3 = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320]
_TAXAS_MPEG1 = [44100, 48000, 32000]


def silencio_mp3(referencia: bytes, segundos: float) -> bytes:
    """Quadros MP3 de silêncio no mesmo formato do áudio de referência.

    Sem folga entre episódios, o Spotify emenda o fim de um no começo do
    anterior e parece o mesmo episódio. Não há codificador MP3 sem dependência,
    então o silêncio é montado à mão: cabeçalho copiado do primeiro quadro real
    e corpo zerado, que decodifica como amostras nulas. Só MPEG-1 Layer III;
    qualquer outro formato devolve vazio em vez de arriscar um arquivo inválido.
    """
    if segundos <= 0:
        return b""
    i = next((k for k in range(len(referencia) - 3)
              if referencia[k] == 0xFF and referencia[k + 1] & 0xFE == 0xFA), None)
    if i is None:
        return b""
    h = bytearray(referencia[i:i + 4])
    indice_bitrate, indice_taxa = h[2] >> 4, (h[2] >> 2) & 3
    if not 0 < indice_bitrate < 15 or indice_taxa > 2:
        return b""
    h[2] &= 0xFD                                   # sem byte de enchimento
    taxa = _TAXAS_MPEG1[indice_taxa]
    tamanho = 144 * _BITRATES_MPEG1_L3[indice_bitrate] * 1000 // taxa
    quadros = max(1, round(segundos * taxa / 1152))
    return (bytes(h) + bytes(tamanho - 4)) * quadros


PRONUNCIA = ROOT / "config" / "pronuncia.json"


def carrega_pronuncia(caminho: pathlib.Path = PRONUNCIA) -> dict:
    try:
        return json.loads(caminho.read_text(encoding="utf-8")).get("substituicoes", {})
    except FileNotFoundError:
        return {}


def aplica_pronuncia(texto: str, mapa: dict) -> str:
    """Troca a grafia só no texto enviado ao sintetizador.

    O roteiro, a contagem de palavras e o feed continuam com a grafia original.
    A voz clonada aprende timbre, não como ler cada palavra: quem decide a
    leitura de "Anthropic" é o modelo base, com as regras do português.
    """
    for escrito, falado in mapa.items():
        texto = re.sub(rf"\b{re.escape(escrito)}\b", falado, texto)
    return texto


# Custo exato de cada trecho, lido do cabeçalho character-cost. Antes o custo
# saía da diferença do contador de cota da conta, que atualiza com atraso: os
# logs registraram de 0,14 a 0,55 crédito por caractere para o mesmo modelo.
CUSTOS_TRECHOS: list[int] = []


def synthesize(part: str, cfg: dict, api_key: str,
               previous_text: str | None, next_text: str | None) -> bytes:
    url = f"{API_BASE}/{cfg['voice_id']}?output_format={cfg['output_format']}"
    payload = {
        "text": part,
        "model_id": cfg["model_id"],
        "voice_settings": cfg["voice_settings"],
    }
    # Continuidade de prosódia entre trechos.
    if previous_text:
        payload["previous_text"] = previous_text[-500:]
    if next_text:
        payload["next_text"] = next_text[:500]

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )
    last_err: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                custo = (resp.headers.get("character-cost") or "").strip()
                if custo.isdigit():
                    CUSTOS_TRECHOS.append(int(custo))
                return resp.read()
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:400]
            last_err = RuntimeError(f"HTTP {e.code}: {detail}")
            if e.code in (400, 401, 403, 404, 422):
                raise last_err          # erro de config: não adianta repetir
        except Exception as e:          # rede instável
            last_err = e
            if "CERTIFICATE_VERIFY_FAILED" in str(e):
                raise RuntimeError(f"CERTIFICATE_VERIFY_FAILED — {SSL_HINT}")
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"ElevenLabs falhou após 3 tentativas: {last_err}")


# ---------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description="Narra um roteiro do CampsCast.")
    ap.add_argument("--script", help="caminho do episodes/*.md")
    ap.add_argument("--out", help="caminho do .mp3 de saída")
    ap.add_argument("--check", action="store_true",
                    help="valida chave, voz e modelo (custa ~26 caracteres)")
    ap.add_argument("--voice", help="usa esta voz em vez da de config/tts.json "
                                    "(útil para comparar antes de decidir)")
    ap.add_argument("--model", help="usa este modelo em vez do de config/tts.json")
    ap.add_argument("--metricas", help="grava caracteres, créditos e duração num JSON")
    ap.add_argument("--speed", type=float,
                    help="velocidade da fala, de 0.7 a 1.2; sobrescreve config/tts.json")
    ap.add_argument("--budget", action="store_true",
                    help="imprime a faixa de palavras desta voz (KEY=VALUE)")
    ap.add_argument("--voice-status", metavar="ID", nargs="?", const="",
                    help="estado do treino de uma voz clonada (default: a de config)")
    ap.add_argument("--list-voices", action="store_true",
                    help="lista as vozes disponíveis na conta (precisa de 'Voices (read)')")
    ap.add_argument("--dry-run", action="store_true",
                    help="não chama a API; só relata trechos e duração estimada")
    args = ap.parse_args()

    load_env()
    cfg = load_cfg()
    if args.voice:
        cfg = {**cfg, "voice_id": args.voice}
        # O ritmo da config pertence à voz configurada, não a esta.
        cfg.pop("words_per_minute", None)
        print(f"(voz sobrescrita: {args.voice})")
    if args.model:
        cfg = {**cfg, "model_id": args.model}
        print(f"(modelo sobrescrito: {args.model})")
    if args.speed is not None:
        if not 0.7 <= args.speed <= 1.2:
            print("ERRO: --speed precisa ficar entre 0.7 e 1.2, o limite da API.",
                  file=sys.stderr)
            return 2
        cfg = {**cfg, "voice_settings": {**cfg["voice_settings"], "speed": args.speed}}
        print(f"(velocidade sobrescrita: {args.speed})")

    if args.voice_status is not None:
        api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
        if not api_key:
            print("ERRO: ELEVENLABS_API_KEY não definida.", file=sys.stderr)
            return 1
        vid = args.voice_status or cfg["voice_id"]
        try:
            v = api_get(f"voices/{vid}", api_key)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                print("ERRO: a chave não tem o escopo 'Voices (read)'.", file=sys.stderr)
            elif e.code == 404:
                print(f"ERRO: voz {vid} não encontrada.", file=sys.stderr)
            else:
                print(f"ERRO: HTTP {e.code}.", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"ERRO: {explain_network_error(e)}", file=sys.stderr)
            return 1

        print(f"Voz     : {v.get('name')}  ({vid})")
        print(f"Tipo    : {v.get('category')}")
        amostras = v.get("samples") or []
        total_mb = sum(a.get("size_bytes", 0) for a in amostras) / 1048576
        print(f"Amostras: {len(amostras)}  ({total_mb:.0f} MB)")
        for a in amostras:
            print(f"          {a.get('file_name')}")

        estados = ((v.get("fine_tuning") or {}).get("state")) or {}
        if not estados:
            print("Treino  : sem informação de treino (voz não é clone profissional?)")
            return 0
        print("\nTreino por modelo:")
        prontos = 0
        for modelo, estado in sorted(estados.items()):
            marca = {"fine_tuned": "PRONTO", "fine_tuning": "treinando",
                     "not_started": "na fila", "failed": "FALHOU"}.get(estado, estado)
            if estado == "fine_tuned":
                prontos += 1
            print(f"  {marca:<10} {modelo}")
        em_uso = cfg["model_id"]
        print(f"\n{prontos} de {len(estados)} modelos prontos.")
        if estados.get(em_uso) == "fine_tuned":
            print(f"O modelo em produção ({em_uso}) já está pronto — pode usar.")
        elif em_uso in estados:
            print(f"O modelo em produção ({em_uso}) ainda não está pronto.")
        return 0

    if args.budget:
        b = word_budget(cfg)
        print(f"WORD_MIN={b['min']}")
        print(f"WORD_TARGET={b['target']}")
        print(f"WORD_MAX={b['max']}")
        print(f"WORDS_PER_MINUTE={b['wpm']}")
        return 0

    if args.list_voices:
        api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
        if not api_key:
            print("ERRO: ELEVENLABS_API_KEY não definida.", file=sys.stderr)
            return 1
        try:
            data = api_get("voices", api_key)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                print("ERRO: a chave não tem o escopo 'Voices (read)'. Habilite em "
                      "https://elevenlabs.io/app/settings/api-keys", file=sys.stderr)
            else:
                print(f"ERRO: HTTP {e.code}.", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"ERRO: {explain_network_error(e)}", file=sys.stderr)
            return 1
        for v in data.get("voices", []):
            labels = v.get("labels") or {}
            extra = ", ".join(f"{k}={v2}" for k, v2 in labels.items())
            print(f"{v.get('voice_id')}  {v.get('name', '?'):<22} "
                  f"[{v.get('category', '?')}]  {extra}")
        print("\nVozes 'premade' funcionam no plano Free; 'professional' e as da "
              "Voice Library exigem plano pago.")
        return 0

    if args.check:
        api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
        if not api_key:
            print("ERRO: ELEVENLABS_API_KEY não definida. Preencha o .env "
                  "(veja .env.example).", file=sys.stderr)
            return 1
        if cfg["voice_id"].startswith("PLACEHOLDER"):
            print("ERRO: config/tts.json ainda tem voice_id de placeholder.",
                  file=sys.stderr)
            return 1
        return check(cfg, api_key)

    if not args.script or not args.out:
        print("ERRO: --script e --out são obrigatórios (ou use --check).",
              file=sys.stderr)
        return 2

    script_path = pathlib.Path(args.script)
    if not script_path.is_absolute():
        script_path = ROOT / script_path
    if not script_path.exists():
        print(f"ERRO: roteiro não encontrado: {script_path}", file=sys.stderr)
        return 1

    body = aplica_pronuncia(
        to_speakable(strip_front_matter(script_path.read_text(encoding="utf-8"))),
        carrega_pronuncia())
    if not body:
        print("ERRO: roteiro vazio depois de remover o front-matter.", file=sys.stderr)
        return 1

    words = len(body.split())
    budget = word_budget(cfg)
    minutes = words / budget["wpm"]
    parts = chunk(body)

    print(f"Roteiro : {script_path.name}")
    print(f"Palavras: {words}  (~{int(minutes)}m{int((minutes % 1) * 60):02d}s a {budget['wpm']} ppm)")
    print(f"Trechos : {len(parts)}  ({sum(len(p) for p in parts)} caracteres)")

    if words > budget["max"]:
        print(f"AVISO: {words} palavras passam do teto de {budget['max']} "
              f"para esta voz ({budget['wpm']} ppm).")
    if words < budget["min"]:
        print(f"AVISO: {words} palavras ficam abaixo do piso de {budget['min']}.")

    if args.dry_run:
        print("DRY-RUN: nenhuma chamada à API. Prévia do trecho 1:")
        print("  " + parts[0][:200].replace("\n", " ") + "…")
        return 0

    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        print("ERRO: ELEVENLABS_API_KEY não definida (veja .env.example).", file=sys.stderr)
        return 1
    if cfg["voice_id"].startswith("PLACEHOLDER"):
        print("ERRO: config/tts.json ainda tem voice_id de placeholder.", file=sys.stderr)
        return 1

    out_path = pathlib.Path(args.out)
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Cota antes da síntese, para medir o custo real do episódio. Best-effort:
    # exige o escopo User (read) e nunca impede a geração do áudio.
    used_before = None
    try:
        used_before = api_get("user/subscription", api_key).get("character_count")
    except Exception:
        pass

    audio = bytearray()
    for i, part in enumerate(parts):
        prev = parts[i - 1] if i > 0 else None
        nxt = parts[i + 1] if i + 1 < len(parts) else None
        print(f"  trecho {i + 1}/{len(parts)} ({len(part)} chars)…", flush=True)
        audio += strip_container(synthesize(part, cfg, api_key, prev, nxt))

    antes = silencio_mp3(bytes(audio), float(cfg.get("silence_start_s", 0) or 0))
    depois = silencio_mp3(bytes(audio), float(cfg.get("silence_end_s", 0) or 0))
    audio = bytearray(antes) + audio + bytearray(depois)

    out_path.write_bytes(bytes(audio))
    try:
        mostrado = out_path.relative_to(ROOT)
    except ValueError:
        mostrado = out_path          # --out fora do projeto, em teste
    print(f"OK {mostrado} {out_path.stat().st_size // 1024} KB")

    caracteres = sum(len(p) for p in parts)
    exato = bool(parts) and len(CUSTOS_TRECHOS) == len(parts)
    spent = sum(CUSTOS_TRECHOS) if exato else None
    if used_before is not None:
        try:
            settled = None
            if spent is None:
                # Sem o cabeçalho, só resta esperar o contador de cota da conta.
                print("Aguardando o contador de cota estabilizar…", flush=True)
                settled = settled_character_count(api_key)
            sub = api_get("user/subscription", api_key)
            limit = sub.get("character_limit", 0)
            if spent is None:
                used_now = settled if settled is not None else sub.get("character_count", 0)
                spent = used_now - used_before
            else:
                used_now = used_before + spent
            left = max(0, limit - used_now)
            if spent > 0:
                rate = spent / caracteres
                origem = "exato" if exato else "estimado pelo contador"
                print(f"Custo: {spent} créditos ({rate:.2f} por caractere, {origem}). "
                      f"Restam {left} — dá para {left // spent} episódios.")
                monthly = spent * BUSINESS_DAYS
                share = monthly / limit if limit else 0
                print(f"       {BUSINESS_DAYS} episódios/mês ≈ {monthly} "
                      f"({share:.0%} da cota de {limit}).")
                if share > 1:
                    print("AVISO: o ritmo atual estoura a cota antes do fim do mês. "
                          "Troque model_id para eleven_flash_v2_5 em config/tts.json "
                          "(metade do custo) ou encurte o roteiro.")
                elif share > 0.8:
                    print("AVISO: acima de 80% da cota. Margem pequena para um mês "
                          "com episódios longos — considere o eleven_flash_v2_5.")
        except Exception:
            pass
    if args.metricas:
        try:
            from publish import mp3_duration_seconds
            duracao = round(mp3_duration_seconds(out_path) or 0) or None
        except Exception:
            duracao = None
        pathlib.Path(args.metricas).write_text(json.dumps({
            "modelo": cfg["model_id"],
            "voz": cfg["voice_id"],
            "caracteres": caracteres,
            "trechos": len(parts),
            "creditos": spent if (spent or 0) > 0 else None,
            "creditos_exatos": exato,
            "audio_s": duracao,
        }, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
