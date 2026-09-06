# 🎙️ CampsCast

> Briefing diário de IA (dias úteis), pesquisado, roteirizado, narrado e
> publicado de forma autônoma por agentes de IA.
> Roda localmente num MacBook Pro M3, com Claude Code em modo headless,
> TTS na ElevenLabs e publicação via feed RSS em S3.

**Status:** Fase 1 concluída em 05/09/2026 · Fase 2 em andamento · **Autor:** Camps · Detalhes de arquitetura em [PROJETO.md](PROJETO.md)

---

## Como assinar

```
https://campscast.com.br/feed.xml
```

Cole em qualquer app que aceite URL de RSS. Em breve também pelo nome, nos
diretórios — Spotify, Pocket Casts e Podcast Index receberam a submissão em
06/09/2026 e estão processando. A Apple Podcasts vem em seguida.

> O endereço antigo, `campscast.s3.us-east-1.amazonaws.com/feed.xml`, continua
> funcionando para quem assinou antes da migração de domínio. Os dois servem o
> mesmo feed.

---

## Pipeline

```
launchd (seg–sex, 05:50)
   └─► scripts/run_episode.sh
         ├─ [1] claude -p prompts/master.md   → episodes/YYYY-MM-DD.md
         ├─ [2] scripts/tts.py                → audio/YYYY-MM-DD.mp3
         ├─ [3] scripts/publish.py            → feed/feed.xml + S3
         └─ [4] scripts/notify.py             → e-mail / notificação macOS
```

Cada etapa pode rodar isolada — veja `--only` e `--skip` abaixo.

---

## Primeira execução (Fase 1)

### Pré-requisitos

> Montando num Mac novo? O passo a passo completo, do Homebrew ao launchd, está
> em **[docs/setup-macos.md](docs/setup-macos.md)**.

| Ferramenta | Necessária para | Instalar |
|---|---|---|
| Python 3.11+ | todos os scripts (só stdlib) | já vem no macOS / python.org |
| Claude Code CLI | etapa 1 (pesquisa e roteiro) | `npm i -g @anthropic-ai/claude-code` |
| Conta AWS (só chaves) | etapa 3 (upload S3) | sem CLI: `scripts/s3.py` assina em SigV4 |
| Conta ElevenLabs | etapa 2 (narração) | Starter US$ 5/mês — ver [docs/setup-elevenlabs.md](docs/setup-elevenlabs.md) |

Nenhuma dependência Python externa. Não existe `pip install` neste projeto, e o
upload para o S3 não usa a AWS CLI — a assinatura SigV4 está em
[scripts/s3.py](scripts/s3.py), em biblioteca padrão. Só é preciso um par de
chaves de acesso.

### Passo a passo

```bash
# 1. Valide a estrutura sem gastar um centavo — não chama nenhuma API.
bash tests/smoke_test.sh

# 2. Configure os segredos.
cp .env.example .env && $EDITOR .env

# 3. Configure a ElevenLabs — chave, escopos, voz e plano.
#    Roteiro completo: docs/setup-elevenlabs.md
python3 scripts/tts.py --check

# 4. Ajuste config/show.json (base_url, capa, e-mail) e config/briefing.md.

# 5. Simulação completa: mostra o que cada etapa faria, sem executar.
#    Em dry-run o `claude` nem precisa estar instalado.
scripts/run_episode.sh --dry-run

# 6. Só o roteiro — a etapa mais barata de testar de verdade.
scripts/run_episode.sh --only research

# 7. Leia o roteiro em episodes/ antes de gastar créditos de TTS.

# 8. Narre e gere o feed local, sem subir nada.
scripts/run_episode.sh --only tts
python3 scripts/publish.py --no-upload

# 9. Quando o bucket estiver pronto, o pipeline inteiro:
scripts/run_episode.sh
```

### Flags do orquestrador

| Flag | Efeito |
|---|---|
| `--date YYYY-MM-DD` | data do episódio (default: hoje) |
| `--only research\|tts\|publish\|notify` | roda apenas as etapas listadas |
| `--skip publish,notify` | pula as etapas listadas |
| `--dry-run` | mostra o que faria, sem executar |
| `--overwrite` | regrava um episódio que já existe |
| `--force` | roda em dia sem episódio (fim de semana, feriado) |

Logs por dia em `logs/YYYY-MM-DD.log`.

### Acompanhar a pesquisa ao vivo

A etapa 1 leva vários minutos e o `claude -p` só devolve a saída no fim — o que
faz o terminal parecer travado. O `run_episode.sh` já espelha a atividade do
agente enquanto ele trabalha:

```
[22:20:51]   3. lendo: https://www.anthropic.com/news
[22:21:44]  21. buscando: "OpenAI GPT-5.6 Sol price cut August 2026"
[22:26:02]      ↳ Research done. Three verified primary sources.
[22:26:31]  56. escrevendo: episodes/2026-08-23.md
```

Para acompanhar uma execução que já está rodando, de outro terminal:

```bash
python3 scripts/watch_agent.py
```

Ele lê a transcrição que o próprio CLI grava em `~/.claude/projects/`, e
identifica a sessão do pipeline pelo prompt-mestre — não confunde com uma
sessão interativa aberta no mesmo projeto.

---

## Quando há episódio

Dias de publicação, feriados e exceções vivem em
[config/schedule.json](config/schedule.json):

```json
{
  "weekdays": [1, 2, 3, 4, 5],
  "holidays": "BR",
  "skip_dates": [],
  "force_dates": []
}
```

`holidays: "BR"` pula os feriados nacionais brasileiros — inclusive os móveis,
calculados a partir da Páscoa, para não virar uma lista a manter todo janeiro.
Quem clonar o projeto em outro país usa `null` e a própria lista em
`skip_dates`; quem quiser publicar aos sábados põe `6` em `weekdays`.

O instalador do launchd lê esse mesmo arquivo, então os horários de disparo
nunca divergem da regra que o pipeline aplica.

**Pular um dia não perde notícia.** A janela do episódio seguinte cobre desde o
último dia coberto — depois de um feriado na segunda, a terça cobre sexta,
sábado, domingo e segunda.

```bash
python3 scripts/schedule.py --proximos 14
```

---

## Janela de notícias

O que cada episódio cobre não é uma regra de calendário, é uma invariante:

> **O episódio do dia D cobre do dia seguinte ao último dia já coberto até D−1.
> Hoje nunca entra** — o dia ainda não acabou.

Cada roteiro grava `window_start` e `window_end` no front-matter, e a execução
seguinte lê o `window_end` mais recente para saber onde começar. Consequências
práticas:

- Rodar no sábado ou no domingo é permitido e não precisa de flag nenhuma.
- Uma execução manual no sábado (que cobre a sexta) faz a automática de segunda
  cobrir só sábado e domingo. Nenhuma pauta é vista duas vezes, nenhuma é pulada.
- Rodar duas vezes no mesmo dia não gera episódio vazio: a janela sai como
  vazia e o pipeline encerra sem gastar TTS.
- Depois de uma parada longa, a janela é truncada em 7 dias.
- Se `episodes/<data>.md` já existe, o pipeline se recusa a sobrescrever.
  Use `--overwrite` para regravar, ou `--skip research` para reaproveitar.

Na primeira execução, sem nenhum episódio anterior, vale a partida a frio:
segunda, sábado e domingo começam na sexta-feira mais recente; terça a sexta
cobrem apenas o dia anterior.

Para inspecionar sem rodar nada:

```bash
python3 scripts/window.py --date 2026-08-23 --human
```

---

## Estrutura

```
config/briefing.md      contrato editorial — edite para mudar o rumo da semana
config/sources.yaml     fontes por camada (labs → hardware → investidores)
config/show.json        metadados do podcast (título, capa, URLs do feed)
config/tts.json         voz e modelo da ElevenLabs
prompts/master.md       prompt-mestre do agente
scripts/window.py       calcula a janela de notícias (ver seção abaixo)
scripts/schedule.py     decide se o dia tem episódio (dias úteis, feriados)
scripts/calibrate_pace.py  mede o ritmo real de fala e corrige a faixa de palavras
scripts/audio_metrics.py  métricas de áudio (espectro, reverberação, dinâmica)
scripts/check_recording.py avalia gravação; --sala mede ambiente, --markdown tabela
scripts/prep_voice_samples.py converte gravações para o formato que a ElevenLabs aceita
scripts/s3.py           upload para o S3 (SigV4 em Python puro, sem AWS CLI)
scripts/set_base_url.py troca o endereço público do feed, verificando antes
scripts/watch_agent.py  espelha a atividade do agente ao vivo
episodes/               1 roteiro por dia — é a memória do podcast
research/               log de pesquisa: o que foi considerado e descartado
saved-items/backlog.md  pautas relevantes que não couberam
covered-index.json      dedup barato: o que já foi ao ar
analysis/               [Fase 3] análises escritas pelo Camps
audio/  feed/  logs/    gerados; fora do git
docs/decisions/         ADRs
docs/aprendizados.md    o que quebrou, por quê, e o que ficou de método
docs/benchmarks-audio.md medições comparadas de sala, aparelho e distância
CLAUDE.md               orientação para quem (ou o quê) pegar o projeto
docs/gravacao-voz.md    guia para gravar o material da voz profissional
docs/publicacao-diretorios.md  requisitos de Apple, Spotify e Pocket Casts
docs/dominio-proprio.md  migrar o feed para domínio próprio
docs/dominio-registro-br-route53.md  .com.br + Route 53 + CloudFront, passo a passo
tests/smoke_test.sh     valida tudo offline
```

---

## Publicação no S3

Feed e MP3 precisam ser públicos para leitura. O passo a passo — Block Public
Access, bucket policy, credenciais mínimas e teste — está em
**[docs/setup-s3.md](docs/setup-s3.md)**.

Nada a instalar: [scripts/s3.py](scripts/s3.py) assina em SigV4 com a biblioteca
padrão do Python.

---

## Agendamento (launchd)

```bash
scripts/install_launchd.sh
```

Gera o plist com os caminhos reais da máquina — `claude`, `python3`, raiz do
projeto — valida e carrega.

**O projeto não pode ficar em `~/Documents`, `~/Desktop` ou `~/Downloads`.** O
macOS bloqueia agentes do launchd nessas pastas: o erro é `Operation not
permitted` e a execução pelo Terminal continua funcionando, então isso só
aparece de madrugada. O instalador recusa e explica. Detalhes em
[docs/setup-macos.md](docs/setup-macos.md).

Conferir e disparar na hora:

```bash
launchctl list | grep campscast
launchctl kickstart -k gui/$(id -u)/com.camps.campscast
```

O Mac precisa estar acordado às 05:50 em dias úteis:

```bash
sudo pmset -c sleep 0
sudo pmset repeat wakeorpoweron MTWRF 05:45:00
```

---

## Problemas comuns

**`Not logged in · Please run /login`** — instalar o CLI não autentica, e o
login do app desktop não vale para ele: são armazenamentos de credenciais
diferentes. Rode `claude` uma vez no Terminal, use `/login`, saia com `/exit`.
Precisa ser num terminal interativo — não funciona dentro de script.

**`'claude' não encontrado no PATH`** — se instalou com `sudo npm i -g`, o
binário fica em `/usr/local/bin`. O launchd roda com um PATH mínimo, por isso o
plist em `docs/` já declara `EnvironmentVariables > PATH`. Confira se o caminho
do seu `which claude` está lá.

**`CERTIFICATE_VERIFY_FAILED` ao falar com a ElevenLabs** — Python do
python.org no macOS não usa os certificados do sistema. Rode uma vez:
`"/Applications/Python 3.13/Install Certificates.command"`.

**`402 paid_plan_required`** — conta Free não usa vozes da Voice Library pela
API. Veja [docs/setup-elevenlabs.md](docs/setup-elevenlabs.md#3-escolher-o-plano--atenção-aqui).

**Episódio toca só os primeiros minutos** — era um bug de concatenação de MP3,
corrigido ([ADR 0003](docs/decisions/0003-costura-de-mp3.md)). Confira qualquer
episódio com `afinfo audio/AAAA-MM-DD.mp3`, que mostra a duração como um player
a vê — a soma de frames do `publish.py` não pega esse tipo de falha.

**Episódio vazio ou pautas repetidas** — cheque o `window_end` do último
arquivo em `episodes/`. É ele que define onde a próxima execução começa.
`python3 scripts/window.py --date <hoje> --human` mostra o cálculo.

---

## Licença

Duas licenças, porque o repositório tem duas naturezas.

| O quê | Licença |
|---|---|
| Código — `scripts/`, `tests/`, `config/`, `prompts/`, `docs/` | [MIT](LICENSE) |
| Conteúdo editorial — `episodes/`, `research/`, `saved-items/`, `analysis/`, `archive/` e os MP3 | [CC BY 4.0](LICENSE-CONTENT.md) |

Pegue o pipeline e monte o seu podcast, sem dever nada. Se reaproveitar texto ou
áudio de um episódio, cite a fonte.

A MIT foi escrita para software; aplicá-la a roteiro e narração seria ambíguo.
A CC BY é a licença desenhada para obra criativa.

**Licença não é permissão de escrita.** O repositório é público para leitura;
contribuições entram por *pull request*, e nada é mesclado sem revisão do autor.
