# CampsCast — orientação para agentes

Podcast diário de IA em português, escrito e narrado por agentes, publicado em
dias úteis. Rodando em produção desde 24/08/2026.

> **Antes de mexer em qualquer coisa:** `bash tests/smoke_test.sh`
> São 146 testes, offline, sem custo. Rode antes e depois de alterar.

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
| `novidades.py` | mudanças no podcast a anunciar na abertura, por janela de datas |
| `chamada.py` | decide se o episódio convida a seguir o podcast (dias em `config/show.json`) |
| `pautas.py` | lista compacta do que já foi ao ar, uma linha por pauta, escrita no prompt |
| `confere_backlog.py` | confere se o backlog guarda só pauta ativa; registra, não bloqueia |
| `confere_fios.py` | confere fios (teto de 20, marcos, datas) e temas (teto de 10); registra |
| `confere_repeticao.py` | avisa pauta do dia com link já usado antes; ignora páginas de listagem |
| `relatorio.py` | relatório semanal do autor: decisões pendentes, temas, fios, fontes que falharam, avisos; `--semana`, `--fecha-semana` |
| `confere_roteiro.py` | confere o que a abertura e a ficha não podem deixar de dizer; registra, não bloqueia |

### Diagnóstico e manutenção
| Script | O que faz |
|---|---|
| `watch_agent.py` | mostra ao vivo o que o agente está pesquisando |
| `research_trail.py` | reconstrói o rastro de pesquisa de um episódio |
| `calibrate_pace.py` | mede o ritmo real de fala e corrige a faixa de palavras |
| `set_base_url.py` | troca o endereço do feed, verificando antes; `--resolve` |
| `install_launchd.sh` | instala o agendamento com os caminhos reais da máquina |
| `registro.py` | registro diário de execução e custo em `metricas/execucoes.jsonl`; `mostra`, `reconstroi` |
| `memoria_custo.py` | reparte o cache lido de cada execução entre prompt, índice, backlog, roteiros e web |
| `estado.py` | publica `estado.json` no S3 dizendo como a execução terminou; é o que o vigia externo lê |

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
| `config/novidades.json` | mudanças a anunciar na abertura, cada uma com data de início e de fim |
| `config/schedule.json` | dias de publicação, feriados, exceções |
| `memoria/temas.md` | temas: questões de fundo que não fecham; criados pelo autor |
| `memoria/temas-sugeridos.md` | sugestões de tema (do agente; no futuro, de ouvintes) que o autor aprova ou recusa |
| `memoria/fios.md` | fios em aberto: promessas, previsões e preocupações à espera de desfecho ([ADR 0008](docs/decisions/0008-memoria-em-camadas.md)) |
| `prompts/master.md` | o agente |

Relatório da semana: comando `/relatorio` (`.claude/commands/relatorio.md`).

Segredos em `.env` (gitignored). Anotações pessoais em `privado/` (gitignored).

## Convenções

- Comentários e documentação em **português**, como o resto do projeto.
- Todo achado não óbvio vira ADR em `docs/decisions/` ou entra em
  `docs/aprendizados.md`. Mensagem de commit explica **por quê**, não o quê.
- Bug encontrado ganha teste no `smoke_test.sh` antes de ser corrigido.
- Nunca commitar `.env`, áudio, ou conteúdo de `privado/`.

## Estado

Fases 1 e 2 concluídas (05/09 e 03/10/2026). Fase 3 a partir de 05/10 — ver `TODO.md` e `PROJETO.md`.
