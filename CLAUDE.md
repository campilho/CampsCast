# CampsCast — orientação para agentes

Podcast diário de IA em português, escrito e narrado por agentes, publicado em
dias úteis. Rodando em produção desde 24/08/2026.

> **Antes de mexer em qualquer coisa:** `bash tests/smoke_test.sh`
> São 93 testes, offline, sem custo. Rode antes e depois de alterar.

## Regra número um

**Meça, não suponha.** Quase todo bug sério deste projeto veio de uma suposição
que parecia óbvia. Estão catalogados em [docs/aprendizados.md](docs/aprendizados.md) —
vale ler antes de propor mudanças, porque várias ideias intuitivas já foram
testadas e caíram.

## Pipeline

```
launchd (seg-sex 05:50, repescagem 06:20 e 07:00)
  └─ scripts/run_episode.sh
       ├─ [1] claude -p prompts/master.md  → episodes/AAAA-MM-DD.md
       │                                   → research/AAAA-MM-DD.md
       ├─ [2] scripts/tts.py               → audio/AAAA-MM-DD.mp3
       ├─ [3] scripts/publish.py           → feed.xml → S3 → CloudFront
       └─ [4] scripts/notify.py
```

Publicado em `https://campscast.com.br/feed.xml`.

## Invariantes que não podem quebrar

**Janela de notícias.** O episódio do dia D cobre do dia seguinte ao último dia
já coberto até D−1. Hoje nunca entra. Sobrevive a execução manual, feriado e
pausa de dias. Vive em `scripts/window.py`; cada roteiro grava `window_start` e
`window_end` no front-matter, e é de lá que a execução seguinte parte.

**Faixa de palavras.** Derivada do ritmo medido da voz (`words_per_minute` em
`config/tts.json`), não fixa no prompt. Trocar de voz, de modelo **ou de velocidade**
(`speed` em `voice_settings`) exige remedir com
`scripts/calibrate_pace.py --apply`.

**Sem dependências.** Nada de `pip install`. Duração de MP3 lendo frames MPEG,
upload ao S3 assinando SigV4, tudo em biblioteca padrão. Quem clona precisa de
Python e do Claude CLI.

**Fonte primária.** Notícia só entra com post oficial, paper ou release.
Agregador serve para descobrir, nunca para citar.

## Ferramentas

### Pipeline
| Script | O que faz |
|---|---|
| `run_episode.sh` | orquestrador; `--only`, `--skip`, `--dry-run`, `--force`, `--overwrite` |
| `window.py` | calcula a janela de notícias |
| `schedule.py` | decide se o dia tem episódio (dias úteis, feriados) |
| `tts.py` | narra; `--check`, `--budget`, `--voice`, `--model`, `--speed`, `--list-voices`, `--voice-status` |
| `publish.py` | gera o feed e sobe |
| `s3.py` | upload SigV4; `--print-policy`, `--print-iam-policy` |
| `notify.py` | avisa que saiu |
| `nomes.py` | nomes falados na ficha técnica e número do episódio |

### Diagnóstico e manutenção
| Script | O que faz |
|---|---|
| `watch_agent.py` | mostra ao vivo o que o agente está pesquisando |
| `research_trail.py` | reconstrói o rastro de pesquisa de um episódio |
| `calibrate_pace.py` | mede o ritmo real de fala e corrige a faixa de palavras |
| `set_base_url.py` | troca o endereço do feed, verificando antes; `--resolve` |
| `install_launchd.sh` | instala o agendamento com os caminhos reais da máquina |

### Clonagem de voz
| Script | O que faz |
|---|---|
| `check_recording.py` | avalia gravação; `--sala`, `--detalhe`, `--markdown` |
| `audio_metrics.py` | métricas reutilizáveis: espectro, reverberação, dinâmica |
| `prep_voice_samples.py` | converte para WAV e valida antes do upload |
| `monitor.py` | medidor ao vivo; separa voz de ruído por banda, não por nível |

## Configuração

| Arquivo | Governa |
|---|---|
| `config/briefing.md` | contrato editorial da semana |
| `config/sources.yaml` | fontes, por camada |
| `config/show.json` | metadados do podcast e do feed |
| `config/tts.json` | voz, modelo, ritmo medido, silêncio no começo e no fim |
| `config/pronuncia.json` | como o sintetizador deve ler nomes que ele erra; só muda o áudio |
| `config/schedule.json` | dias de publicação, feriados, exceções |
| `prompts/master.md` | o agente |

Segredos em `.env` (gitignored). Anotações pessoais em `privado/` (gitignored).

## Convenções

- Comentários e documentação em **português**, como o resto do projeto.
- Todo achado não óbvio vira ADR em `docs/decisions/` ou entra em
  `docs/aprendizados.md`. Mensagem de commit explica **por quê**, não o quê.
- Bug encontrado ganha teste no `smoke_test.sh` antes de ser corrigido.
- Nunca commitar `.env`, áudio, ou conteúdo de `privado/`.

## Estado

Fase 1 concluída. Fase 2 em andamento — ver `TODO.md` e `PROJETO.md`.
