# 🎙️ CampsCast

<img src="site/capa/capa-1672.jpg" alt="Ilustração em pixel art do estúdio do CampsCast: um prédio em corte ao amanhecer, com São Paulo e a Ponte Estaiada ao fundo, cada agente no seu posto." width="100%">

> Briefing diário de IA (dias úteis), pesquisado, roteirizado, narrado e
> publicado de forma autônoma por agentes de IA.
> Roda localmente num MacBook Pro M3, com Claude Code em modo headless,
> TTS na ElevenLabs e publicação via feed RSS em S3.
> No site, [campscast.com.br](https://campscast.com.br), dá para assistir a
> cada gravação no estúdio, evento a evento.

**Status:** Fase 1 concluída em 05/09/2026 · Fase 2 concluída em 03/10/2026 · Fase 3 em andamento desde 05/10 · **Autor:** Fernando Campilho · Detalhes de arquitetura em [PROJETO.md](PROJETO.md)

---

## Como assinar

<a href="https://open.spotify.com/show/5toSeNQlZxjbCAFPA1gAuJ">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/spotify-badge-branco.svg">
    <img src="assets/spotify-badge-preto.svg" alt="Ouça no Spotify" width="165">
  </picture>
</a>

| Onde | Link |
|---|---|
| **Apple Podcasts** | [podcasts.apple.com/br/podcast/campscast](https://podcasts.apple.com/br/podcast/campscast/id6809631318) |
| **Spotify** | [open.spotify.com/show/campscast](https://open.spotify.com/show/5toSeNQlZxjbCAFPA1gAuJ) |
| **Pocket Casts** | busque por *CampsCast* |
| **Podcast Index** | [podcastindex.org](https://podcastindex.org/search?q=campscast) |
| **RSS direto** | `https://campscast.com.br/feed.xml` |
| **Site** | [campscast.com.br](https://campscast.com.br): o último episódio, o estúdio e como sugerir um tema |

O feed serve qualquer app que aceite URL de RSS.

> O endereço antigo, `campscast.s3.us-east-1.amazonaws.com/feed.xml`, continua
> funcionando para quem assinou antes da migração de domínio. Os dois servem o
> mesmo feed.

---

## Marcos

| Data | |
|---|---|
| 24/08/2026 | Primeiro episódio no ar |
| 06–07/09 | Nos diretórios: Pocket Casts e Podcast Index, depois Spotify e Apple Podcasts |
| 08/09 | Primeiro episódio narrado pela voz clonada profissional do autor |
| 15–25/09 | Nove episódios seguidos publicados sem ninguém em casa |
| 28/09 | O agente passa a ser o Claude Opus 5.5 e anuncia o próprio upgrade no ar: "a partir de hoje, quem escreve este roteiro é o Claude Opus cinco ponto cinco, o modelo que o meu antecessor, o Opus cinco, noticiou aqui no episódio dezenove" |
| 01/10 | O [post de lançamento no LinkedIn](https://www.linkedin.com/posts/fernandocampilho_ontem-o-apresentador-do-meu-podcast-anunciou-share-7510711037797752833-sHT2) é destacado pelo LinkedIn News na matéria ["Novos agentes, modelos e IPOs: as conversas da semana sobre IA"](https://www.linkedin.com/news/story/novos-agentes-modelos-e-ipos-as-conversas-da-semana-sobre-ia-7629556/) |
| 03/10 | Fase 2 concluída. O programa ganha memória em camadas: temas de fundo, fios em aberto à espera de desfecho e um relatório semanal com o que pede decisão do autor ([ADR 0008](docs/decisions/0008-memoria-em-camadas.md)). O custo por episódio fica medido ([ADR 0007](docs/decisions/0007-custo-por-episodio.md)) |
| 25/10 | Linha de base dos fatos: um verificador confere os 40 primeiros episódios contra as fontes primárias — 949 afirmações, 7,9% de erro, todos leves ([ADR 0010](docs/decisions/0010-redacao-com-varios-agentes.md)) |
| 26/10 | A narração passa ao Eleven v4, com o mesmo clone da voz ([ADR 0011](docs/decisions/0011-narracao-no-eleven-v4.md)) |
| 02/11 | O site entra no ar em [campscast.com.br](https://campscast.com.br), com o estúdio em pixel art; desde 04/11 ele se atualiza sozinho no fim de cada episódio |
| 05–08/11 | Um experimento da Anthropic troca, sem aviso nem versão nova, a leitura de páginas do agente por um subagente, e o custo sobe 57%. O relatório da semana pega a mudança, e a leitura é fixada de volta ([ADR 0013](docs/decisions/0013-leitura-de-paginas.md)) |
| 09/11 | Episódio 50 |
| 14/11 | Ensaio do verificador nos 14 episódios mais recentes, com a régua calibrada contra a linha de base. O verificador mais barato concordava com o roteiro; no mais caro, os erros leves dos episódios 41 a 46 sobem para 11,3%, metade por tirar da notícia a cautela da fonte (`verificacao/v1/`) |

## A voz

Os episódios são narrados por uma clonagem profissional da voz do autor,
treinada com 28 minutos gravados no celular, em blocos de dois minutos entre
pousos do aeroporto de Congonhas. Desde 26/10, o modelo é o Eleven v4, com o
mesmo clone ([ADR 0011](docs/decisions/0011-narracao-no-eleven-v4.md)).

O caminho até lá está medido em [docs/benchmarks-audio.md](docs/benchmarks-audio.md):
qual cômodo, qual aparelho, qual distância, com número em vez de impressão. A
conclusão mais útil foi a menos intuitiva — **projeção de voz pesou mais que
sala, aparelho e distância somados**, e aproximar o microfone de 20 para 10 cm
piorou a gravação.

E há a evidência direta de que **clonagem aprende tudo que está na amostra**.
Mesmo roteiro, mesma voz, mesmo modelo; só muda a qualidade do material de
treino:

| | Ouvir | Piso nas pausas |
|---|---|---|
| Amostra curta e limpa | [MP3](https://campscast.com.br/referencias/2026-09-04-instant.mp3) | **−90,4 dBFS** |
| 15 min gravados com a TV ligada na sala | [MP3](https://campscast.com.br/referencias/2026-09-04-professional-quarto-com-tv.mp3) | **−52,2 dBFS** |

Trinta e oito decibéis de diferença, e o pior é o que teve cinco vezes mais
material. Ouça as pausas entre as frases.

---

## O site

[campscast.com.br](https://campscast.com.br) é servido do mesmo bucket do
podcast, pelo CloudFront, e o `run_episode.sh` o atualiza no fim de cada
episódio publicado. Se a publicação do site falhar, o episódio segue.

| Endereço | O que tem |
|---|---|
| `/` | A capa: o que é o CampsCast, como ouvir, o último episódio e os números da última gravação |
| `/estudio/` (ou `/studio`) | O estúdio em pixel art: cada personagem no seu posto conforme o relógio de São Paulo, e o **replay da gravação**, evento a evento |
| `/estudio/roteiros/AAAA-MM-DD.html` | O roteiro do dia, com as fontes |
| `/estudio/pesquisa/AAAA-MM-DD.html` | O log de pesquisa do dia: o que foi lido, o que foi descartado e por quê |
| `/sugestao/` | Sugerir um tema |
| `/privacidade/` | Privacidade: sem cookies e sem rastreamento |

Os personagens (Produtor, Jornalista, Editor, Roteirista, Locutor, Vigia,
Arquivista) são os papéis do pipeline. O que eles dizem nos balões **sai do
registro da gravação, não da imaginação**: o estúdio mostra só o que
aconteceu. Detalhes, elenco e o contrato dos dados em [docs/site.md](docs/site.md).

---

## Pipeline

```
launchd (seg–sex, 05:00; repescagem às 06:00 e 07:00)
   └─► scripts/run_episode.sh
         ├─ [1] claude -p prompts/master.md   → episodes/ e research/ do dia
         │       (lê e atualiza a memória: temas, fios em aberto, backlog)
         ├─ [2] scripts/tts.py                → audio/AAAA-MM-DD.mp3
         ├─ [3] scripts/publish.py            → feed.xml no S3, atrás do CloudFront
         ├─ [4] scripts/notify.py             → e-mail / notificação macOS
         └─ depois: registro de custo e do uso do Max, estado.json, o site,
            e no último episódio da semana o relatório do autor
```

Cada etapa pode rodar isolada — veja `--only` e `--skip` abaixo. Às 07:30, uma
rotina na nuvem confere se o episódio do dia está no ar e avisa no celular.

---

## Quanto custa

O que o CampsCast acrescenta às contas é cerca de **R$ 6,25 por episódio**:
ElevenLabs, domínios e AWS. O agente roda na assinatura Max do Claude, que o
autor já tinha e divide com outros usos. A preço de API, os 21 episódios de
outubro custariam US$ 100,13, quase exatamente o preço do Max. A partir de
16/11, o log de cada episódio diz quanto da janela de 5 horas e da semana do
Max ele gastou.

As contas estão no [ADR 0007](docs/decisions/0007-custo-por-episodio.md) e em
[docs/custos.md](docs/custos.md), com o orçamento de cada experimento.

---

## Primeira execução (Fase 1)

### Pré-requisitos

> Montando num Mac novo? O passo a passo completo, do Homebrew ao launchd, está
> em **[docs/setup-macos.md](docs/setup-macos.md)**.

| Ferramenta | Necessária para | Instalar |
|---|---|---|
| Python 3.11+ | todos os scripts (só stdlib) | python.org (o `/usr/bin/python3` da Apple é 3.9 e não serve) |
| Claude Code CLI | etapa 1 (pesquisa e roteiro) | `npm i -g @anthropic-ai/claude-code` |
| Conta AWS (só chaves) | etapa 3 (upload S3) | sem CLI: `scripts/s3.py` assina em SigV4 |
| Conta ElevenLabs | etapa 2 (narração) | Starter (US$ 5/mês) para vozes prontas; Creator (US$ 22/mês) para clonar a própria voz — ver [docs/setup-elevenlabs.md](docs/setup-elevenlabs.md) |

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
config/tts.json         voz, modelo e ritmo medido da ElevenLabs
config/agentes.json     versão de cada agente, com o que mudou e o que se mediu
prompts/master.md       prompt-mestre do agente
scripts/                o pipeline, as conferências e as medições (tabela no CLAUDE.md)
episodes/               1 roteiro por dia
research/               log de pesquisa: o que foi considerado e descartado
memoria/                temas, fios em aberto e o relatório semanal do autor
saved-items/            backlog de pautas que não couberam, e o histórico dele
covered-index.json      o que já foi ao ar, para não repetir
verificacao/            conferência dos fatos: linha de base e o ensaio v1
metricas/               registro de cada execução: tempo, tokens, custo
site/                   capa e estúdio de campscast.com.br
docs/decisions/         ADRs
docs/aprendizados.md    o que quebrou, por quê, e o que ficou de método
docs/custos.md          o que é pago, créditos, chaves e orçamentos
docs/site.md            o site: páginas, personagens, dados
docs/benchmarks-audio.md medições comparadas de sala, aparelho e distância
docs/setup-*.md         macOS, S3, ElevenLabs
docs/dominio-*.md       domínio próprio: .com.br, Route 53 e CloudFront
CLAUDE.md               orientação para quem (ou o quê) pegar o projeto
tests/smoke_test.sh     valida tudo offline
audio/  feed/  logs/    gerados; fora do git
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

O Mac precisa estar acordado às 05:00 em dias úteis:

```bash
sudo pmset -c sleep 0
sudo pmset repeat wakeorpoweron MTWRF 04:55:00
```

E **na tomada**: durante a gravação, o `caffeinate` impede o Mac de dormir, mas
só com energia externa. Com a tampa fechada e na bateria, ele dorme no meio da
pesquisa — em 11/11, foram 97 minutos de atraso. Se a primeira tentativa
falhar, o launchd tenta de novo às 06:00 e às 07:00.

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

**Episódio saiu muito depois das 05:00** — veja a coluna "dormiu" de
`python3 scripts/registro.py mostra`. Se o Mac dormiu no meio, ele estava fora
da tomada ou com a tampa fechada.

**`AVISO: ANTHROPIC_API_KEY no ambiente`** — com essa variável o Claude CLI
cobraria o episódio na API em vez da assinatura. O orquestrador a remove antes
do agente; uma chave de API para experimentos fica no `.env` com outro nome
(veja [docs/custos.md](docs/custos.md)).

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
