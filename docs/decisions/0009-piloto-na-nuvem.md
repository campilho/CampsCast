# ADR 0009 — Piloto na nuvem, em paralelo ao Mac, e plano B na AWS

- **Status:** proposto (04/10/2026); a implementar por etapas
- **Data:** 2026-10-04

## Contexto

O critério de saída da Fase 3 é publicar dez dias úteis seguidos sem o Mac do
autor ligado. O caminho mais curto é o Claude Code na nuvem: o pipeline é o
mesmo e o custo do Claude continua na assinatura Max (ADR 0007). Antes de
trocar, o piloto roda **uma semana em paralelo ao Mac**, publicando num
bucket de testes, para provar que faz tudo igual e para medir o custo — um dia
o Claude pode ser cobrado por token, e a conta precisa estar pronta.

O que foi conferido em 04/10, na documentação oficial e no próprio projeto:

| Fato | Fonte |
|---|---|
| Rotina é uma sessão na nuvem agendada; desconta do uso da assinatura | [Routines](https://code.claude.com/docs/en/routines) — "Routines draw down subscription usage the same way interactive sessions do" |
| O crédito de US$ 250 não vale para rotinas | tela do resgate, 03/10 |
| Sessão na nuvem também se abre pelo terminal: `claude --cloud` | [Cloud environments](https://code.claude.com/docs/en/cloud-environments) |
| Cada execução clona o ramo padrão; o push vai para `claude/...` **a menos que o prompt mande outro ramo** | Routines — "Claude pushes its work to a branch prefixed with `claude/` unless your prompt directs it to push to another branch" |
| O modelo é escolhido na rotina e vale em todas as execuções | Routines — "Claude uses the selected model on every run" |
| Rede: lista "Trusted" por padrão; fora dela, 403 com `host_not_allowed`. A lista padrão inclui `*.amazonaws.com`; dá para usar uma lista própria | Routines e Cloud environments |
| Variável de ambiente é visível a quem usa o ambiente; chave de API vai como **credencial gerenciada**, que o proxy anexa ao cabeçalho — inclusive com nome próprio, como `xi-api-key` | Cloud environments — "For a header like `X-Api-Key` that takes the bare value, change the name and clear the prefix" |
| Login interativo da AWS (SSO) não funciona na nuvem | Cloud environments — "Interactive auth like AWS SSO: Not supported" |
| Só o git persiste entre execuções; a máquina é Ubuntu 24.04 nova a cada vez | Cloud environments |
| Status verde da execução não quer dizer que a tarefa deu certo | Routines — "A green status in the run list means the session started and exited without an infrastructure error" |
| O pipeline já roda em Linux: `caffeinate`, `pmset` e `osascript` são opcionais e pulados fora do Mac | `run_episode.sh`, `registro.py`, `notify.py` |
| O vigia, numa rotina, teve o `curl` barrado com 403 para o S3 e para o domínio em todas as execuções, embora `*.amazonaws.com` esteja na lista padrão | logs das execuções de 29/09 e 02/10 — causa não confirmada |

## Decisão

### 1. O pipeline local passa a versionar o que produz

Hoje o episódio, o índice, o backlog, os fios e o registro só chegam ao
GitHub quando alguém comita à mão. A nuvem começa do zero a cada dia, clonando
o repositório: sem isso, a cópia na nuvem teria a memória atrasada. Além do
piloto, é o que permite trocar de máquina sem perder nada.

Etapa nova no `run_episode.sh`, **versiona**, depois da publicação e do
relatório:

- adiciona **só uma lista explícita** de caminhos — `episodes/<data>.md`,
  `research/<data>.md`, `covered-index.json`, `saved-items/`, `memoria/`,
  `metricas/execucoes.jsonl` — e nunca `git add -A`: áudio, logs, `.env` e
  `privado/` não podem entrar por descuido;
- commit com a identidade do autor e mensagem "Episódio N — título", com uma
  linha dizendo que foi o pipeline;
- `git push` para a `main`; se recusar por ter mudança remota, `pull --rebase`
  e uma nova tentativa; se falhar de novo, aviso no registro e no estado,
  **sem derrubar o episódio**, que já foi publicado;
- conferência no smoke test: o commit nunca contém arquivo fora da lista.

No Mac, o push sai pelo HTTPS com a credencial no Keychain
(`credential.helper osxkeychain`), que o agente do launchd alcança na sessão
do usuário — a confirmar no primeiro dia, olhando o log.

### 2. O piloto: uma rotina, um ramo próprio, um bucket de testes

```
 04:00  Rotina "CampsCast — piloto" (nuvem, Ubuntu)
          │ clona o repositório; git checkout -B piloto origin/main
          │ (a main tem o estado de ontem, comitado pelo Mac)
          ├─ bash scripts/run_episode.sh --perfil piloto
          │     pesquisa e roteiro → narração → feed e MP3 no bucket de testes
          │     → relatório (sexta) → registro e estado no bucket de testes
          └─ commit no ramo piloto; git push --force origin piloto

 05:00  Mac, como hoje: episódio de verdade, publicado, e agora comitado na main

 depois scripts/compara_piloto.py <data>: piloto contra produção
```

- **Por que antes do Mac:** os dois partem do mesmo estado (o de ontem) e
  cobrem a mesma janela. Se o piloto rodasse depois, encontraria o episódio
  do dia já na `main` e pararia, como manda a janela.
- **Ramo `piloto`:** refeito a cada dia a partir da `main` e enviado com
  `--force`. Nunca toca a `main`; uma regra de proteção no GitHub garante
  isso mesmo se o prompt errar.
- **Bucket de testes** `campscast-piloto`, com um usuário da AWS próprio que só
  grava nele. O feed, o MP3, o `estado.json` e o relatório do piloto vão para
  lá; o `estado.json` que o vigia lê continua intocado. `publish.py` ganha uma
  variável para trocar o `base_url` do feed.
- **Segredos:** a chave da ElevenLabs vai como credencial gerenciada para
  `api.elevenlabs.io`, no cabeçalho `xi-api-key` — o código nunca a vê, e o
  `tts.py` ganha um modo que não exige a variável. A chave da AWS vai como
  variável de ambiente, porque a assinatura SigV4 é calculada no código e o
  proxy não assina; quem usa o ambiente é só o autor, e a chave só grava no
  bucket de testes. Para a produção na nuvem, avaliar trocar por um GitHub
  Actions com OIDC, sem chave guardada.
- **Rede:** lista própria com `api.elevenlabs.io`, o bucket de testes e o
  domínio do podcast, além da lista padrão. O primeiro passo do piloto é
  testar a rede, porque o 403 do vigia no S3 ainda não está explicado.
- **Modelo:** Opus 5.5 escolhido na rotina. O esforço (`--effort high`) vem do
  orquestrador.

### 3. Duas formas de rodar o agente dentro da rotina — decidir no primeiro teste

| | **A. O orquestrador de sempre** | **B. A sessão é o agente** |
|---|---|---|
| Como | a rotina roda `run_episode.sh`, que chama `claude -p` como hoje | a rotina prepara o prompt, faz a pesquisa e o roteiro ela mesma, e chama o orquestrador só para o resto |
| Mudança no pipeline | nenhuma | o orquestrador ganha um modo "agente externo" |
| Custo medido | o JSON do `claude -p` já traz custo e tokens, como hoje | somar o uso a partir da transcrição da própria sessão, que está no disco da máquina enquanto ela roda |
| Incerteza | o `claude -p` aninhado consegue se autenticar dentro da sessão? Não está na documentação | nenhuma técnica; muda o desenho |

A primeira execução manual do piloto responde à pergunta de A. Se funcionar,
fica A: é o mesmo pipeline, que é o que se quer provar.

### 4. O que o piloto mede, por dia

| Medida | Como |
|---|---|
| Fez o mesmo trabalho? | roteiro, palavras, pautas, avisos das conferências, edições na memória — `compara_piloto.py` contra a produção |
| Custo do Claude a preço de API | JSON do `claude -p` (forma A) ou transcrição (forma B); vai para o registro do ramo `piloto` |
| Custo da ElevenLabs | cabeçalho `character-cost`, como hoje; o piloto narra de verdade: ~3.300 créditos por dia, cabe no plano (136 mil por mês) |
| Horário e duração | registro de execução |
| Publicação | feed e MP3 no bucket de testes, conferidos por leitura |

**Critério para trocar a produção para a nuvem:** cinco dias úteis seguidos
em que o piloto publica no bucket de testes sem intervenção, com roteiros sem
regra quebrada e custo dentro de ±20% do Mac. Depois disso, inverter: a nuvem
publica de verdade e o Mac vira a reserva por uma semana.

### 5. Onde entra o crédito de US$ 250

Não paga a rotina. Serve às sessões na nuvem que não são rotina: montar e
depurar o piloto, as execuções manuais de teste e o ensaio na nuvem. Uma
alternativa seria o Mac disparar o piloto com `claude --cloud` às 04:00 — gasta
o crédito em vez do Max —, mas aí o piloto depende do Mac para começar, que é
justamente o que ele quer eliminar. Fica como plano de contingência se o uso
do Max apertar.

## Plano B: AWS, e a primeira visão da Fase 4

Não será implementado agora. Serve de estudo e de referência de custo.

```
 EventBridge Scheduler (seg-sex 05:00, America/Sao_Paulo)
      │
      ▼
 ECS Fargate — tarefa com o contêiner do pipeline (Python + Claude Code CLI)
      │  papel IAM da tarefa: sem chave guardada
      ├─ Claude no Amazon Bedrock (CLAUDE_CODE_USE_BEDROCK=1), cobrado por token
      ├─ chave da ElevenLabs e token do GitHub no Secrets Manager
      ├─ MP3 e feed no S3 que já existe
      ├─ git push do estado para o GitHub
      └─ logs no CloudWatch; estado.json como hoje, para o vigia
```

- **Por que Fargate e não Lambda:** a pesquisa e o roteiro levam de 10 a 20
  minutos, e o limite da Lambda é de 15 minutos por execução. O Fargate cobra
  pelo tempo da tarefa.
- **Custo:** o Claude passa a ser cobrado por token no Bedrock — uns US$ 97 por
  mês no Opus 5.5, pela conta do ADR 0007, que é o item que decide. O resto
  (Fargate por ~20 minutos por dia, EventBridge, Secrets Manager, CloudWatch)
  é pequeno; os preços ficam para quando o plano B for escolhido, conferidos
  nas páginas de preço do dia.
- **Fase 4:** o mesmo desenho, com o agente reescrito no Claude Agent SDK e
  hospedado no Bedrock AgentCore (Runtime, Memory, Gateway, Observability). A
  memória em camadas do ADR 0008 é feita de arquivos portáveis justamente para
  poder ser comparada com o AgentCore Memory.

## Acesso do agente à conta da AWS

Hoje a conta da AWS só tem o usuário raiz. Para o agente passar a criar e
conferir recursos direto na conta — o bucket de testes, depois o plano B —, a
ordem é: primeiro tirar o autor da raiz, depois dar ao agente um perfil
próprio e limitado.

**O Agent Toolkit for AWS** (conferido em 04/10 na documentação da AWS) não é
novo: saiu em maio de 2026 e reúne o servidor MCP gerenciado da AWS
(`aws-mcp`, acessado por um proxy local que exige o `uv`), skills e um arquivo
de regras. No Claude Code instala como plugin —
`/plugin install aws-core@claude-plugins-official` — ou pelo assistente
`aws configure agent-toolkit` (AWS CLI 2.35 ou mais nova). O ponto que decide
a segurança, nas palavras da AWS: o servidor "does not define its own IAM
actions" e "your AI agents work with your existing AWS credentials". **O
agente pode tudo o que o perfil logado pode.** Existem chaves de condição
(`aws:ViaAWSMCPService`, `aws:CalledViaAWSMCP`) para negar ações só quando
vêm pelo MCP, mas um `aws ...` no shell com o mesmo perfil não passa por elas
— a defesa de verdade é o perfil. Fontes:
[Getting started](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/quick-start.html),
[How AWS MCP Server works with IAM](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/security_iam_service-with-iam.html).

O arquivo de regras recomendado é para copiar no `CLAUDE.md`. Ler antes: ele
entra nas instruções de toda sessão e manda usar a AWS CLI quando o MCP não
estiver disponível — o que, com um perfil amplo, é a porta que as chaves de
condição não fecham.

**Passo a passo (P0), pelo autor no console:**

1. **MFA no usuário raiz** e nenhuma chave de acesso para ele. A raiz sai do
   uso diário ([boas práticas da raiz](https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html)).
2. **Ativar o IAM Identity Center** e criar o usuário do autor com o conjunto
   de permissões `AdministratorAccess` — é ele que o autor usa daqui em diante
   ([primeiros passos](https://docs.aws.amazon.com/singlesignon/latest/userguide/getting-started.html)).
3. **Criar o conjunto de permissões `CampsCastAgente`** e atribuí-lo ao mesmo
   usuário, com uma política própria: leitura geral (`ViewOnlyAccess`) mais
   escrita só em buckets `campscast-*` e nada de IAM. Criar usuários e
   políticas fica com o autor, porque quem cria política pode se dar
   qualquer permissão. Sessão de 1 a 4 horas.
4. **Perfil na CLI do Mac:** `aws configure sso`, com o perfil
   `campscast-agente`; `aws sso login --profile campscast-agente` antes de cada
   sessão de trabalho ([SSO na CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html)).
5. **Plugin `aws-core` no Claude Code**, apontado para esse perfil
   (`AWS_PROFILE=campscast-agente`), e o arquivo de regras lido antes de entrar
   no `CLAUDE.md`.

**O que não muda:** o pipeline de produção segue sem AWS CLI, com o usuário
que só grava no bucket (ADR 0002). O Agent Toolkit é para as sessões de
desenvolvimento no Mac; na nuvem não funcionaria, porque o login interativo
da AWS não roda numa sessão na nuvem.

Correção a uma anotação de 03/10 no PROJETO.md: o "renovável por 90 dias" não
está na documentação do `aws login`, cuja sessão vai até 12 horas. Noventa
dias é o teto configurável da sessão interativa do IAM Identity Center.

## Etapas

| Etapa | O quê | Quem |
|---|---|---|
| P0 | Credencial da AWS que não é a raiz, para o autor e para o agente (seção acima) | autor, com o passo a passo |
| P1 | Etapa **versiona** no pipeline local, com teste; ensaio; ir ao ar | agente |
| P2 | Bucket `campscast-piloto` (agente, com o perfil da P0) e o usuário que só grava nele (autor, com a política que o agente escreve) | juntos |
| P3 | `tts.py` sem chave (credencial gerenciada), `BASE_URL` no `publish.py`, perfil `piloto` no orquestrador, `compara_piloto.py` | agente |
| P4 | Ambiente na nuvem: rede, credencial da ElevenLabs, variáveis do bucket de testes; proteção da `main` no GitHub | autor, no claude.ai e no GitHub |
| P5 | Execução manual na nuvem: rede, forma A ou B, um episódio completo no bucket de testes | juntos |
| P6 | Rotina às 04:00 por uma semana; comparação diária | rotina; leitura no relatório de sexta |

## Consequências

- O repositório passa a ser a memória oficial, atualizada todo dia útil, e não
  só quando alguém comita. Trocar de máquina deixa de exigir cuidado.
- Durante a semana do piloto, a ElevenLabs narra em dobro (~16 mil créditos a
  mais na semana).
- O piloto gasta uso do Max na rotina; o crédito de US$ 250 fica para o
  desenvolvimento na nuvem.
