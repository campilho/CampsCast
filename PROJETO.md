# 🎙️ [NOME DO PODCAST] — Briefing diário de IA, gerado por agentes

> Podcast diário (dias úteis) com as principais notícias do mundo de IA do dia anterior,
> pesquisado, roteirizado, narrado e publicado de forma autônoma por agentes de IA.
> Roda localmente em um MacBook Pro M3, com Claude Code em modo headless,
> TTS na ElevenLabs e publicação via feed RSS em S3.

**Status:** Fase 1 concluída em 05/09/2026 · Fase 2 em andamento
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
| Janela de notícias | Dia anterior. Na segunda-feira: sexta + sábado + domingo |
| Duração | **5 a 10 minutos** (alvo ~8 min; nunca ultrapassar 10) |
| Tópicos por episódio | **Máximo 3 tópicos relevantes** |
| Excedente | Tópico relevante que não coube → vai para o **backlog** (`saved-items/`) |
| Uso do backlog | Em dia fraco de notícias, puxar item do backlog **avisando a data original** ("essa notícia é de 2 dias atrás, mas vale destacar…") |
| Idioma | Português do Brasil, tom de conversa, sem jargão não explicado |
| Prioridade máxima | Lançamento de modelo de fronteira dos principais players |

Estrutura sugerida do roteiro (~950–1.200 palavras ≈ 8 min de fala):

> Calibrado com medição real em 23/08/2026: a voz de produção fala a **125
> palavras por minuto**, não as ~160 que a estimativa original assumia.
> 1.152 palavras renderam 9min11s. O teto de 10 minutos equivale a 1.250
> palavras — por isso a faixa fecha em 1.200.

```
[COLD OPEN]    Uma frase com a manchete do dia. (15s)
[ABERTURA]     Vinheta verbal + data. (15s)
[TÓPICO 1]     A notícia mais importante. O que é, por que importa, fonte. (2-3 min)
[TÓPICO 2]     (2-3 min)
[TÓPICO 3]     (1-2 min) — ou item do backlog, com aviso de data
[ENCERRAMENTO] Recap em 3 frases + teaser do que observar hoje. (30s)
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
 tts.py ──► ElevenLabs API (modelo Flash v2.5, voz PT-BR) ──► audio/YYYY-MM-DD.mp3
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
- [x] TTS ElevenLabs (Flash v2.5, voz clonada do Camps) — Polly e Chirp3
      seguem pendentes no ADR 0001, sem bloquear
- [x] `feed.xml` + MP3 no S3, feed válido
- [ ] launchd seg–sex 05:50 (Mac configurado: `pmset` para acordar/não hibernar)
- [x] Assinatura no Pocket Casts → funciona no celular. No EX30 o app do
      Android Automotive não atualiza de forma confiável; a saída é o
      diretório, na Fase 2
- [x] URL compartilhada com 4 beta testers — feedback formal fica para a Fase 2

**Critério de saída:** 5 episódios consecutivos publicados sem intervenção
manual. **Encerrada em 05/09/2026 com 4** — 01, 02, 03 e 04/09, todos
disparados às 05:50 sem toque humano. O quinto cairia na segunda 07/09, que é
feriado nacional; com a qualidade já validada nos testes do autor, esperar mais
um dia útil não acrescentaria informação.

### Fase 2 — Voz própria e publicação

- [x] **Instant Voice Clone** da voz do Camps narrando o episódio — antecipado
      ainda na Fase 1
- [x] **Domínio próprio** `campscast.com.br`, com Route 53, ACM e CloudFront
- [x] **Alias de e-mail dedicado** `contato@campscast.com.br`
- [x] Capa — `> CC` em conceito de terminal, 1400×1400
- [x] Submissão ao **Spotify** — enviada em 06/09/2026, em processamento
- [x] Submissão ao **Pocket Casts**
- [x] Submissão ao **Podcast Index**
- [ ] Submissão à **Apple Podcasts** — bloqueada: o Apple ID usa um e-mail em
      domínio expirado, e o Podcasts Connect falha ao enviar a confirmação
- [ ] **Professional Voice Clone** — guia de gravação em `docs/gravacao-voz.md`
- [ ] README público caprichado, com os links dos diretórios
- [ ] Refatorar para subagents do Claude Code (pesquisador / editor / publicador)
- [ ] ADR de custos reais consolidado

**Critério de saída:** podcast encontrável pelo nome nos principais diretórios,
narrado com voz clonada profissional.

### Fase 3 — Formato entrevista, feedback e curadoria humana
- [ ] **Professional Voice Clone** do Camps (guia de gravação em
      `docs/gravacao-voz.md`) + segunda voz de catálogo →
      formato entrevista: a voz de IA apresenta a notícia ou pergunta;
      a voz do Camps analisa
- [ ] `analysis/` ativo: visões e pesquisas escritas pelo Camps, que o agente
      usa como material de análise nos episódios (o "assimilar" humano do funil)
- [ ] Feedback dos ouvintes: alias de e-mail dedicado + Google Form (que
      notifica o mesmo alias); agente lê via Gmail API antes de gerar,
      incorpora sugestões de pauta e marca como processado
- [ ] Camps revisa sugestões acumuladas antes de escrever análises novas
- [ ] Capa oficial gerada no Midjourney
- [ ] Sugestões de fontes dos ouvintes → `sources.yaml`

### Ideias futuras (sem compromisso)
- Episódio da tarde com tema variável (negócios, agentes, seguros)
- Migração do orquestrador para Claude Agent SDK
- Transcrição/show notes publicadas junto ao episódio
- Fallback GitHub Actions para quando o Mac estiver indisponível

---

## 10. Custos estimados (Fase 1, 1 episódio/dia útil)

| Item | Estimativa/mês |
|---|---|
| Claude (Max já contratado; headless usa a assinatura) | ~R$ 0 incremental |
| ElevenLabs Flash (~8 min/dia útil ≈ 176 min/mês) | Starter US$ 5 → Creator US$ 22 conforme uso |
| S3 + transferência (episódios de ~8 MB, poucos ouvintes) | < US$ 1 |
| **Total incremental** | **~US$ 5–25/mês** |

---

## 11. Notas operacionais (Mac como runner)

```bash
# Não dormir na tomada + agendar despertar (seg-sex 05:45)
sudo pmset -c sleep 0
sudo pmset repeat wakeorpoweron MTWRF 05:45:00

# Alternativa agressiva (tampa fechada sem monitor): desabilita sleep de vez
sudo pmset -a disablesleep 1
```

launchd: plist em `~/Library/LaunchAgents/com.camps.podcast.plist` com
`StartCalendarInterval` seg–sex 05:50 chamando `scripts/run_episode.sh`.
Logs em `logs/` com data — o agente pode ler o log da véspera para
autodiagnóstico em caso de falha.
