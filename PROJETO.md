# 🎙️ CampsCast — Briefing diário de IA, gerado por agentes

> Podcast diário (dias úteis) com as principais notícias do mundo de IA do dia anterior,
> pesquisado, roteirizado, narrado e publicado de forma autônoma por agentes de IA.
> Roda localmente em um MacBook Pro M3, com Claude Code em modo headless,
> TTS na ElevenLabs e publicação via feed RSS em S3.

**Status:** Fase 1 concluída em 05/09/2026 · Fase 2 em andamento (voz própria e os quatro diretórios no ar; falta a divulgação) · Fases 3 e 4 planejadas
**Autor:** Camps
**Licença:** MIT para o código, CC BY 4.0 para o conteúdo editorial

---

## 1. Visão

Um pipeline agêntico de ponta a ponta: um trigger determinístico (launchd) acorda o
Claude Code de madrugada; a partir daí o agente decide o que pesquisar, o que é
relevante, o que descartar, o que guardar para depois — e entrega um episódio de
podcast pronto para tocar no carro às 7h da manhã, via Android Auto.

O projeto também é um laboratório público de engenharia de agentes: cada fase
documenta decisões de arquitetura, custos reais e lições aprendidas.

**Tudo é IA, e o episódio diz isso.** Pesquisa, roteiro e voz — e, nas próximas
fases, vídeos, site e agentes com nome e papel — são feitos por IA, e isso é
dito em voz alta em todo episódio. Nenhuma persona finge ser humana, e nada é
publicado em nome do Camps sem a aprovação dele. É o mote do projeto.

Princípio editorial central (inspirado no framework de curadoria de
[Deborah Folloni](https://dfolloni.substack.com/p/como-acompanhar-noticias-de-ia-sem)):
**ir direto à fonte**. A cadeia de valor de IA tem três andares — hardware (NVIDIA),
labs (Anthropic, OpenAI, Google) e apps — e quanto mais embaixo, maior o impacto nos
andares de cima. Notícia de veículo de imprensa já é derivada; o agente prioriza os
blogs oficiais dos labs, anúncios de hardware e a visão dos grandes investidores.
O funil dela — **capturar → filtrar → assimilar → testar** — se traduz aqui em:
o agente automatiza capturar e filtrar; assimilar e testar seguem humanos
(as análises pessoais do Camps, que entram na Fase 3).

---

## 2. Formato editorial do episódio

Regras fixas que o agente deve respeitar:

| Regra | Valor |
|---|---|
| Frequência | 1 episódio/dia, **apenas dias úteis** — dias, feriados e exceções em `config/schedule.json` |
| Janela de notícias | Do dia seguinte ao último já coberto até a véspera (`scripts/window.py`). Na segunda, sexta a domingo |
| Duração | **5 a 10 minutos** (alvo ~8 min; nunca ultrapassar 10) |
| Tópicos por episódio | **Máximo 3 tópicos relevantes** |
| Excedente | Tópico relevante que não coube → vai para o **backlog** (`saved-items/`) |
| Uso do backlog | Em dia fraco de notícias, puxar item do backlog **avisando a data original** ("essa notícia é de 2 dias atrás, mas vale destacar…") |
| Idioma | Português do Brasil, tom de conversa, sem jargão não explicado |
| Prioridade máxima | Lançamento de modelo de fronteira dos principais players |

Estrutura do roteiro. A faixa de palavras não é fixa: sai do ritmo medido da
voz de produção (`words_per_minute` em `config/tts.json`). Em 12/09/2026, a
150 palavras por minuto, a faixa é de 825 a 1.425 palavras, com alvo de 1.200.

> A primeira medição, em 23/08/2026, deu 125 palavras por minuto com a voz da
> época; a estimativa original assumia ~160. Trocar de voz, de modelo ou de
> velocidade exige remedir — ver `docs/aprendizados.md`.

```
[silêncio]     1 s
[COLD OPEN]    Uma frase com a manchete do dia. (15s)
[ABERTURA]     Vinheta verbal com o número do episódio + data. (20s)
[TÓPICO 1]     A notícia mais importante. O que é, por que importa, fonte. (2-3 min)
[TÓPICO 2]     (2-3 min)
[TÓPICO 3]     (1-2 min) — ou item do backlog, com aviso de data
[ENCERRAMENTO] Ficha técnica: páginas lidas, pautas avaliadas, quem escreveu
               e quem narrou. Sem recap e sem "o que observar". (20s)
[silêncio]     3 s — sem folga, o Spotify emenda no episódio anterior
```

---

## 3. Arquitetura

```
 launchd (seg-sex, 05:50)
      │
      ▼
 run_episode.sh ──► claude -p "$(cat prompts/master.md)"   [Claude Code headless]
      │                   │
      │                   ├─ lê config/briefing.md        (foco editorial da semana)
      │                   ├─ lê config/sources.yaml       (fontes confiáveis)
      │                   ├─ lê episodes/*.md + saved-items/  (memória / dedup / backlog)
      │                   ├─ web search + fetch nas fontes
      │                   ├─ escreve episodes/YYYY-MM-DD.md   (roteiro final)
      │                   └─ atualiza saved-items/ e covered-index.json
      │
      ▼
 tts.py ──► ElevenLabs API (Multilingual v2, voz clonada do Camps) ──► audio/YYYY-MM-DD.mp3
      │
      ▼
 publish.py ──► gera/atualiza feed.xml ──► aws s3 sync ──► bucket S3 (público-leitura)
      │
      ▼
 notify.py ──► e-mail "Episódio publicado (9m32s)" (opcional)
```

O feed RSS é o ponto de desacoplamento: qualquer app de podcast que aceite URL
(Pocket Casts, AntennaPod) assina direto; o Spotify entra na fase de publicação.

### Por que trigger determinístico + execução agêntica?

LLMs não "acordam sozinhos" — todo agente de produção segue o padrão
*tick determinístico → autonomia na execução*. O launchd só dá o tick; toda a
inteligência (o que buscar, o que cortar, o que guardar) é decisão do agente.

---

## 4. Estrutura do repositório

```
.
├── PROJETO.md                  # este arquivo
├── README.md                   # visão pública, como assinar, arquitetura
├── config/
│   ├── briefing.md             # contrato editorial editável (foco da semana)
│   └── sources.yaml            # fontes confiáveis, por camada
├── prompts/
│   └── master.md               # prompt-mestre do agente
├── episodes/
│   └── 2026-08-24.md           # 1 roteiro por dia = memória do podcast
├── saved-items/
│   └── backlog.md              # itens relevantes que não couberam (com data)
├── analysis/                   # [Fase 3] visões e pesquisas do Camps
│   └── 2026-09-xx-tema.md
├── audio/                      # MP3 gerados (gitignored; ficam no S3)
├── scripts/
│   ├── run_episode.sh          # orquestrador
│   ├── tts.py                  # ElevenLabs
│   ├── publish.py              # feed.xml + upload S3
│   └── notify.py               # notificação por e-mail
├── covered-index.json          # URLs/títulos já cobertos (dedup barato)
└── docs/
    └── decisions/              # ADRs: Polly vs ElevenLabs, custos, etc.
```

---

## 5. Fontes (`config/sources.yaml`)

Arquivo vivo — cresce com o tempo e com sugestões dos ouvintes (Fase 3).
Estrutura inicial, seguindo a lógica "vá na origem":

```yaml
# Camada 1 — Labs (prioridade máxima; toda notícia nasce aqui)
labs:
  - https://www.anthropic.com/news
  - https://openai.com/news
  - https://blog.google/technology/ai/
  - https://deepmind.google/discover/blog/
  - https://ai.meta.com/blog/
  - https://mistral.ai/news/
  - https://x.ai/news

# Camada 0 — Hardware / infra
hardware:
  - https://blogs.nvidia.com/
  - https://aws.amazon.com/blogs/machine-learning/

# Camada 2 — Investidores (termômetro de mercado)
investors:
  - https://a16z.com/
  - https://www.ycombinator.com/blog
  - https://www.sequoiacap.com/stories/

# Vozes-chave (checar em dias de rumor forte; usar com parcimônia)
people:
  - Dario Amodei, Sam Altman, Andrej Karpathy, Boris Cherny

# Agregadores (apenas para checagem de cobertura, nunca fonte primária)
aggregators:
  - https://news.ycombinator.com/
```

Regra do agente: **notícia só entra no episódio se tiver fonte primária**
(post oficial, paper, release). Agregador serve para descobrir, não para citar.

---

## 6. Dedup e backlog

- **Dedup:** antes de escrever, o agente lê `covered-index.json` (lista de URLs e
  títulos já cobertos) e os últimos 5 roteiros em `episodes/`. Pauta repetida só
  volta se houver desdobramento novo — e dizendo explicitamente o que mudou.
- **Backlog (`saved-items/backlog.md`):** cada item guardado tem data original,
  fonte, resumo de 2 linhas e prazo de validade (default: 5 dias úteis).
  Ao usar um item do backlog, o roteiro **avisa a data** ("notícia de 3 dias atrás,
  mas relevante demais para passar em branco") e o item é removido.
- Ao final de cada execução, o agente reescreve o índice e poda itens vencidos.

---

## 7. Contrato do `config/briefing.md`

Arquivo curto que o Camps edita quando quiser mudar o rumo — o agente lê a cada
execução. Formato:

```markdown
# Briefing editorial — semana de 24/08/2026

## Foco fixo
Principais notícias de IA do dia anterior. Prioridade: lançamentos de modelos
de fronteira (Anthropic, OpenAI, Google, Meta, Mistral, xAI).

## Foco especial da semana (opcional)
Ex.: "Se aparecer algo sobre agentes em seguros/finanças, ganha prioridade."

## Não cobrir
Ex.: rumores sem fonte primária; drama corporativo sem fato novo.

## Tom
Analítico, direto, sem hype. Explicar siglas na primeira ocorrência.
```

---

## 8. Prompt-mestre do agente (rascunho — `prompts/master.md`)

```markdown
Você é o produtor e roteirista do podcast [NOME], um briefing diário de IA
em português do Brasil, de 5 a 10 minutos, publicado em dias úteis.

## Processo (nesta ordem)
1. Leia config/briefing.md (contrato editorial) e config/sources.yaml.
2. Leia covered-index.json e os últimos 5 arquivos de episodes/ — você NÃO
   pode repetir pautas já cobertas, salvo desdobramento novo (e diga o que mudou).
3. Leia saved-items/backlog.md.
4. Pesquisa: percorra as fontes na ordem labs → hardware → investors.
   Janela: notícias de ontem (se hoje é segunda: sexta, sábado e domingo).
   Toda pauta precisa de fonte primária.
5. Seleção: ranqueie por impacto. Critério nº 1: lançamento de modelo de
   fronteira de player principal. Escolha NO MÁXIMO 3 pautas.
   - Sobrou pauta relevante? Adicione ao backlog com data, fonte e resumo.
   - Dia fraco (<2 pautas fortes)? Puxe do backlog, avisando a data original.
6. Roteiro: escreva episodes/YYYY-MM-DD.md com 1.100–1.400 palavras, seguindo
   a estrutura de PROJETO.md §2. Texto para ser FALADO: frases curtas,
   siglas expandidas na primeira menção ("LLM, os grandes modelos de linguagem"),
   números arredondados, zero markdown no corpo do roteiro.
7. Atualize covered-index.json e saved-items/backlog.md (pode os vencidos).
8. Ao final, imprima apenas: OK <caminho-do-roteiro> <duração-estimada>.

## Guardrails
- Nunca invente notícia, número ou citação. Sem fonte primária, não entra.
- Incerteza é dita como incerteza ("a empresa afirma que…").
- Não reproduza trechos longos de artigos: sempre parafraseie.
```

---

## 9. Fases

### ✅ Fase 1 — Pipeline core (MVP)
- [x] Repo criado com esta estrutura
- [x] `briefing.md` e `sources.yaml` iniciais
- [x] `run_episode.sh` + `claude -p` headless funcionando manualmente
- [x] Dedup por `covered-index.json` + leitura de episódios anteriores
- [x] Backlog de itens guardados operante
- [x] TTS ElevenLabs (Flash v2.5, com clonagem Instant da voz do Camps) —
      substituído na Fase 2 pela clonagem profissional no Multilingual v2.
      Polly e Chirp3 seguem pendentes no ADR 0001, sem bloquear
- [x] `feed.xml` + MP3 no S3, feed válido
- [x] launchd seg–sex 05:50, com repescagem às 06:20 e 07:00
      (`com.camps.campscast`), e `pmset` acordando o Mac às 05:45. Na bateria não
      resiste — ver notas operacionais e Fase 3
- [x] Assinatura no Pocket Casts → funciona no celular. No EX30 o app do
      Android Automotive não atualiza de forma confiável; a saída foi o
      diretório, na Fase 2
- [x] URL compartilhada com 4 beta testers — o feedback formal virou conversa
      direta com ouvintes (Fase 2) e formulário no site (Fase 3)

**Critério de saída:** 5 episódios consecutivos publicados sem intervenção
manual. **Encerrada em 05/09/2026 com 4** — 01, 02, 03 e 04/09, todos
disparados às 05:50 sem toque humano. O quinto cairia na segunda 07/09, que é
feriado nacional; com a qualidade já validada nos testes do autor, esperar mais
um dia útil não acrescentaria informação.

### Fase 2 — Voz própria, publicação e divulgação

Entregue:

- [x] **Instant Voice Clone** da voz do Camps narrando o episódio — antecipado
      ainda na Fase 1
- [x] **Domínio próprio** `campscast.com.br`, com Route 53, ACM e CloudFront
- [x] **Alias de e-mail dedicado** `contato@campscast.com.br`
- [x] Capa — `> CC` em conceito de terminal, 1400×1400
- [x] **Diretórios** — os quatro no ar:

      | Diretório | Estado | Desde |
      |---|---|---|
      | Spotify | no ar, testado no carro e no celular | 07/09/2026 |
      | Pocket Casts | no ar | 06/09/2026 |
      | Podcast Index | no ar | 06/09/2026 |
      | Apple Podcasts | no ar, ID 6809631318 | 07/09/2026 |

- [x] **Professional Voice Clone** — 28 minutos gravados em blocos de 2 minutos
      entre pousos de Congonhas, S/R ponderado 33,6 dB, nenhum bloco abaixo de
      30. Adotada em 07/09; obrigou a voltar ao `eleven_multilingual_v2` porque
      o fine-tuning falhou nos modelos Flash e Turbo. Ver adendo ao ADR 0004.
- [x] README público com os links dos diretórios e a seção da voz
- [x] Qualidade de gravação medida e publicada — `docs/benchmarks-audio.md`, com
      os MP3 de referência dos dois clones em `campscast.com.br/referencias/`
- [x] Episódio com silêncio de 1 s no começo e 3 s no fim, número na abertura e
      na tag `<itunes:episode>`, e encerramento só com a ficha técnica (12/09)
- [x] Ficha técnica com nomes derivados dos modelos em uso; modelo do agente
      fixado no orquestrador (12/09)
- [x] Primeira leitura de audiência — Spotify, Apple e CloudFront. Números em
      `privado/`; o método, em `docs/aprendizados.md`
- [x] Registro diário de execução e custo em `metricas/execucoes.jsonl` —
      horários por etapa, sono do Mac, tokens do Claude, créditos exatos da
      ElevenLabs e tamanho da memória que o agente lê. Unidades brutas, não
      dinheiro. Histórico desde 26/08 reconstruído dos logs (13/09)

A fazer:

- [ ] Conversar com quatro ou cinco ouvintes: até onde ouvem, o que os faria
      parar, e se preferem Spotify ou Apple Podcasts
- [ ] **Plano de divulgação** — primário no LinkedIn, com posts frequentes
      sobre a evolução do projeto e sempre com os links; avaliar outros canais
- [ ] **Avaliar o YouTube** como mais um canal, incluindo o YouTube Music para
      o áudio
- [ ] **Avaliar um site simples** em `campscast.com.br` — links para todos os
      diretórios, descrição do projeto e link para o GitHub. Vira a âncora do
      formulário da Fase 3. Hospedar custa quase nada no S3 e no CloudFront que
      já existem; o trabalho é o conteúdo. Hoje a raiz do domínio responde 403
- [ ] ADR de custos reais consolidado — inclui o custo do Claude por token,
      base da decisão de onde rodar na Fase 3

**Critério de saída:** podcast encontrável pelo nome nos principais diretórios,
narrado com voz clonada profissional — **atingido em 07/09** — e divulgação em
andamento: plano publicado, primeiro ciclo de posts no LinkedIn rodando, e
decisão tomada sobre site e YouTube.

### Fase 3 — Presença multicanal, feedback e independência do Mac

Formato e curadoria:

- [ ] **Formato entrevista** — uma segunda voz, de catálogo, apresenta a notícia
      ou pergunta; a voz do Camps analisa. A clonagem profissional já existe
      desde a Fase 2
- [ ] `analysis/` ativo: visões e pesquisas escritas pelo Camps, que o agente
      usa como material de análise nos episódios (o "assimilar" humano do funil)
- [ ] Camps revisa sugestões acumuladas antes de escrever análises novas
- [ ] Sugestões de fontes dos ouvintes → `sources.yaml`

Feedback:

- [ ] **Formulário no site**, responsivo, além do e-mail `contato@`. Site
      estático não recebe envio sozinho: precisa de um backend pequeno — uma
      função na AWS gravando e notificando, por exemplo. O agente lê as
      sugestões antes de gerar o episódio e as marca como processadas
- [ ] **Avaliar WhatsApp e Instagram** como canais de feedback — só se as
      conversas com ouvintes mostrarem demanda: cada canal a mais é mais uma
      caixa para ler

Vídeo:

- [ ] **Instagram do podcast com shorts gerados por IA** — não diário; chamada
      curta para a notícia do dia e para o podcast. É o passo para aprender a
      usar modelos de vídeo, que hoje geram clipes de 5 a 8 segundos
- [ ] **YouTube Shorts** com o mesmo material, no mesmo formato vertical.
      Vídeos longos ficam de fora por enquanto

Site:

- [ ] **Site sofisticado feito com Claude Design**, desktop e mobile — um
      showcase de IA: exemplos das vozes e dos vídeos, como o projeto funciona
      por dentro, e caminho para visitantes técnicos contribuírem com pautas ou
      código. Escopo a detalhar
- [ ] Capa oficial gerada no Midjourney

FinOps:

- [ ] **Relatório de custos** a partir de `metricas/execucoes.jsonl` — custo
      por episódio em dólar e em reais, com a tabela de preços datada, e
      gráficos ao lado do que cresce: índice de pautas, páginas lidas,
      chamadas ao modelo. Versão beta do agente de FinOps da Fase 4

Operação:

- [ ] **Rodar sem depender do Mac do Camps** — o mesmo pipeline da Fase 2, sem
      redesenho; o redesenho em agentes é a Fase 4. Três caminhos em avaliação:

      | | AWS | Mac mini emprestado | Mac mini comprado |
      |---|---|---|---|
      | Custo do Claude | por token, no Bedrock, cobrado pela AWS | assinatura Max, sem custo extra | assinatura Max, sem custo extra |
      | Custo fixo | contêiner agendado, baixo | zero | compra do equipamento e energia |
      | Mudança no pipeline | trocar o que é só do macOS | nenhuma | nenhuma |
      | Disponibilidade | gerenciada | energia, internet e rotina da casa do irmão | energia e internet de casa |
      | Segurança | segredos no cofre da AWS | chaves do projeto em máquina de outra pessoa; usuário macOS separado | máquina própria |
      | Vitrine e Fase 4 | alinhado com o AgentCore | não | não |
      | Reuso | pago por projeto | não é do Camps | agentes do livro 2081 e outros projetos agênticos |

      Bases medidas em 12/09:

      - **Uso do Claude por episódio**, somado dos registros das execuções
        automáticas de 01 a 11/09: de 27 a 68 chamadas ao modelo. A entrada é
        quase toda leitura de cache, de 1,5 a 8,5 milhões de tokens, mais 74 a
        172 mil de cache escrito e 26 a 72 mil de saída. O volume mais que
        dobrou de 01–04/09 para 08–11/09: o agente lê mais memória e mais
        páginas. A conta em dólares fica para o ADR de custos.
      - **Dependência de macOS:** só no orquestrador (5 ocorrências) e na
        notificação (2). Narração, feed, janela, calendário e upload são
        biblioteca padrão.
      - **Cobrança:** a assinatura Max cobre o Claude Code logado na conta; a
        API é cobrada à parte, por token, e o Bedrock é cobrado pela AWS.
        Nenhum dos dois consome a cota do Max. No Mac mini do irmão, rodar com
        a conta do Camps, não com a dele.

      Decisão depois do ADR de custos, com o custo mensal do Claude no Bedrock
      ao lado dos outros dois caminhos. Com o Mac mini, a AWS entra na Fase 4.

**Critério de saída:** dez dias úteis seguidos publicados sem o Mac do Camps ligado;
formulário no ar, com as sugestões chegando ao agente; site novo publicado.

### Fase 4 — Agência de podcast autônoma na AWS

O projeto vira vitrine de agentes de IA em nuvem, com tudo aberto no GitHub.
Se a Fase 3 tiver escolhido o Mac mini, é aqui que a AWS entra.

- [ ] **Rearquitetar em agentes especializados no Amazon Bedrock AgentCore** —
      Runtime para hospedar, Gateway para expor ferramentas, Browser para a
      pesquisa na web, Memory e Observability; conversa entre agentes por A2A.
      O Claude Agent SDK é candidato natural para escrever os agentes que o
      AgentCore hospeda
- [ ] Claude Opus via Amazon Bedrock
- [ ] **Tudo no GitHub:** código, pipelines, infraestrutura como código, prompts
      e configuração dos agentes
- [ ] Banco de dados de estatísticas — Spotify, Apple, downloads — e
      monitoramento dos ouvintes
- [ ] Agente de marketing gerando posts para atrair público, com aprovação
      humana antes de publicar qualquer coisa em nome do Camps
- [ ] Agente de FinOps acompanhando o custo de cada episódio
- [ ] **Agentes com nome e papel:** o roteirista, o editor de vídeo, o de
      marketing, o analista de FinOps, a apresentadora da segunda voz e o Camps
      virtual

**Critério de saída:** a definir quando a Fase 3 fechar.

### Ideias futuras (sem compromisso)
- Episódio da tarde com tema variável (negócios, agentes, seguros)
- Transcrição e show notes publicadas junto ao episódio — alimentam o site
- Vídeos longos no YouTube
- Agência de produção de podcast autônoma oferecida para outros temas

---

## 10. Custos estimados (1 episódio/dia útil)

| Item | Estimativa/mês |
|---|---|
| Claude (Max já contratado; headless usa a assinatura) | ~R$ 0 incremental |
| ElevenLabs Creator — Multilingual v2 desde 08/09, ~4.600 créditos por episódio | US$ 22; 22 episódios usam ~77% da cota |
| S3 + CloudFront (plano gratuito) + Route 53 | poucos dólares |
| **Total incremental** | **~US$ 25/mês** |

Valores reais consolidados ficam para o ADR de custos. Se o pipeline for para a
AWS — na Fase 3 ou na 4 —, o Claude passa a ser cobrado por token no Bedrock, fora
da assinatura: o maior item a medir antes de migrar.

---

## 11. Notas operacionais (Mac como runner)

```bash
# Não dormir na tomada + agendar despertar (seg-sex 05:45)
sudo pmset -c sleep 0
sudo pmset repeat wakeorpoweron MTWRF 05:45:00

# Alternativa agressiva (tampa fechada sem monitor): desabilita sleep de vez
sudo pmset -a disablesleep 1
```

launchd: plist em `~/Library/LaunchAgents/com.camps.campscast.plist` com
`StartCalendarInterval` seg–sex 05:50, repescagem às 06:20 e 07:00, chamando
`scripts/run_episode.sh`.

**Limite medido:** na bateria, o `caffeinate -s` não vale, e o Mac volta a dormir
segundos depois de o launchd acordá-lo. Foi assim nas três falhas de 10 e 11/09.
Na tomada, com a tampa fechada, a execução de 09/09 concluiu com o sistema em
DarkWake a noite toda. Enquanto o pipeline depender do Mac, a regra é **na
tomada** — tampa aberta como margem até mais noites confirmarem. A saída
definitiva está na Fase 3.
Logs em `logs/` com data — o agente pode ler o log da véspera para
autodiagnóstico em caso de falha.
