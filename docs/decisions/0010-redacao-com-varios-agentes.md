# ADR 0010 — Redação com vários agentes, para estudar orquestração e aprendizado

- **Status:** proposto (18/10/2026); nada implementado. Primeiro passo descrito
  no fim
- **Data:** 2026-10-18

## Contexto

Hoje um agente só faz tudo numa execução de `claude -p`: lê o briefing e a
memória, pesquisa, escolhe as pautas, escreve o roteiro, atualiza a memória e
escreve o log de pesquisa (os nove passos de `prompts/master.md`). Funciona: são
33 episódios até 16/10, a maior parte sem aviso das conferências.

O objetivo aqui não é consertar nada. É **exercitar orquestração de agentes**,
com etapas em sequência, em paralelo e em outro horário, e medir **quanto um
agente melhora de uma execução para outra** com anotações e memória de curto e
de longo prazo. O podcast é o banco de provas.

O que foi conferido em 14/10, na documentação oficial:

| Fato | Fonte |
|---|---|
| Subagentes funcionam em `claude -p`. Definidos em `.claude/agents/*.md` ou por `--agents` (JSON na linha de comando ou, desde a v2.1.281, num arquivo) | [headless](https://code.claude.com/docs/en/headless), [sub-agents](https://code.claude.com/docs/en/sub-agents) |
| Cada subagente tem modelo, ferramentas, prompt, esforço e limite de turnos próprios | sub-agents |
| Até 20 subagentes em background ao mesmo tempo; um subagente chama outro até 3 níveis | sub-agents |
| Subagente com `memory: project` ganha memória própria em `.claude/agent-memory/<nome>/`, versionável no git; as primeiras 200 linhas ou 25 KB entram no prompt dele | sub-agents, [memory](https://code.claude.com/docs/en/memory) |
| Eventos `SubagentStart` e `SubagentStop` existem em hooks; nenhum traz custo | [hooks](https://code.claude.com/docs/en/hooks) |
| O JSON do `-p` traz o custo total e por modelo, subagentes incluídos; **não por subagente** | [cost-tracking](https://code.claude.com/docs/en/agent-sdk/cost-tracking) |
| `--max-budget-usd` conta o gasto dos subagentes | headless |
| Agent SDK: `pip install claude-agent-sdk` (Python 3.10+); roda o binário do Claude Code | [agent-sdk](https://code.claude.com/docs/en/agent-sdk/overview) |
| Agent SDK: a documentação pede chave de API para quem constrói produto; não diz com todas as letras que uso pessoal pela assinatura é permitido | [legal-and-compliance](https://code.claude.com/docs/en/legal-and-compliance) |
| Rotinas e `claude --cloud` descontam do limite da assinatura, sem cobrança à parte pela máquina | [routines](https://code.claude.com/docs/en/routines) |

Da referência da API da Anthropic (skill `claude-api`, 14/10): Managed Agents é
beta, só na API da Anthropic (não no Bedrock), cobra token a preço de tabela
mais US$ 0,08 por hora de sessão e US$ 10 por mil buscas; tem coordenador com
lista de agentes em paralelo, memória com versões, agenda por cron e
"outcomes" (um avaliador separado itera o trabalho contra uma rubrica). Pela
mesma tabela, **busca e leitura na web do lado do servidor não existem no
Bedrock** — risco para o plano B do ADR 0009, a conferir.

## Os papéis

| Papel | Padrão | Modelo | Observação |
|---|---|---|---|
| Pesquisadores | paralelo, um por camada de `sources.yaml` | Sonnet 5.5 | muita leitura, pouco raciocínio |
| Verificador de fontes | paralelo, um por candidata | Sonnet 5.5 | lê a fonte primária ele mesmo, não o resumo do pesquisador |
| Editor de pauta | sequencial | Opus 5.5 | briefing, temas, fios, lista de pautas, backlog |
| Roteirista | sequencial | Opus 5.5 | |
| Revisor | ciclo com o roteirista, no máximo duas voltas | Opus ou Sonnet | rubrica por critério, mais as conferências de hoje |
| Arquivista | sequencial; e um passo semanal | Sonnet 5.5 | índice, fios, temas, backlog, resumos do C2 |
| Locutor | sequencial | nenhum (`tts.py`) | |
| Editor final | sequencial | nenhum (`publish.py`) | notas do episódio e capítulos podem ganhar modelo depois |
| Vigia | outro horário (07:30) | rotina na nuvem | já existe; pode virar auditor dos fatos depois de publicado |

Locutor e editor final ficam como código. Pôr modelo onde o código já é exato
acrescenta custo e variação sem ganho. O verificador precisa ser
independente: "uma medição que compartilha suposições com o código medido não
é verificação" (`docs/aprendizados.md`).

**Contrato entre agentes é arquivo.** Cada etapa grava JSON em
`runs/AAAA-MM-DD/` (candidatas, verificadas, pauta, roteiro, parecer), e um
`confere_*.py` valida o arquivo antes da etapa seguinte. Passagem de bastão
que falha precisa cair no teste, não ser compensada pelo agente seguinte —
foi assim que as variáveis de ambiente passaram um mês sem chegar ao agente.
A mesma pasta é a fonte do estúdio em miniatura do site.

## Opções de execução

| | Claude Code headless | Agent SDK | Managed Agents | AWS (Bedrock + AgentCore) |
|---|---|---|---|---|
| Dependência nova | nenhuma | `pip install` | nenhuma (REST) | infraestrutura |
| Cobrança | assinatura Max | chave de API (assinatura incerta) | token a preço de API + sessão + busca | token no Bedrock + infraestrutura |
| Paralelo | subagentes em background | igual, em código | linhas de trabalho na mesma sessão | Step Functions ou A2A |
| Memória por agente | `memory: project` | igual | memory stores com versões | AgentCore Memory |
| Agenda | launchd, rotina | por conta própria | cron nativo | EventBridge |
| Revisor com rubrica | montar | montar | nativo (outcomes) | montar |
| Custo por agente | das transcrições | das transcrições | uso por sessão | CloudWatch |
| Tira o Mac do caminho | só com rotina | não | sim | sim |
| Maturidade | em produção | estável | beta | estável, muita montagem |

A preço de API, o agente de hoje sai por US$ 4,41 a 4,87 de mediana por
episódio (registro de 28/09 a 16/10), uns US$ 100 por mês. Vários agentes
releem briefing e memória cada um, o que puxa o custo para cima; workers em
Sonnet ou Haiku puxam para baixo. Só medindo.

## Decisão proposta

1. **Primeiro no Claude Code headless, no Mac**, num desenho híbrido: a
   sequência fica no orquestrador (determinística, testável, cada etapa no
   registro) e o paralelo fica dentro das etapas de pesquisa e de verificação,
   com subagentes. Sem dependência nova e sem custo à parte.
2. **Em sombra**, ao lado da produção, nunca no lugar dela, até a comparação
   mostrar que vale. Depende do `scripts/ensaio.sh` (TODO), que roda um dia
   passado no ambiente do launchd.
3. Os agentes de produção definidos por `--agents` num arquivo do repositório,
   não em `.claude/agents/`, para não vazarem para as sessões de
   desenvolvimento (o isolamento do commit `a038297`).
4. **Fase 4:** os mesmos papéis e contratos levados a Managed Agents ou ao
   AgentCore, para comparar. Como papéis, prompts e contratos são arquivos, a
   troca é de onde roda, não do desenho.

## Aprendizado e memória

- **Curto prazo:** a pasta da execução. É o que um agente entrega ao outro.
- **Longo prazo editorial:** temas, fios, pautas e backlog (ADR 0008).
- **Longo prazo de ofício, por agente:** um caderno de lições por papel. O
  revisor anota por que reprovou; o vigia, o que achou depois de publicado; o
  verificador, as fontes que costumam falhar; o autor, o que quiser.
- **Lição errada vira regra para sempre.** Mesma regra das sugestões de tema:
  o agente propõe, o autor aprova no relatório de sexta. Cada caderno tem teto
  e cada lição tem data.
- **Melhora se mede, não se declara:** reprovações do revisor por motivo,
  voltas até aprovar, candidatas descartadas pelo verificador, avisos das
  conferências, custo por papel. Comparar com e sem as lições, rodando dias
  passados de novo no `ensaio.sh`.

## Primeiro passo

O **verificador, ainda fora da sequência**: um `claude -p` separado, depois do
agente atual, que lê o roteiro do dia e confere cada fato contra a fonte
primária. Registra, não bloqueia, como as conferências de hoje. Em uma semana
dá a linha de base que falta: com que frequência o roteiro erra fato. Depois o
revisor, o arquivista e, por último, a pesquisa em paralelo — uma mudança por
vez.

Em 25/10 o passo ganhou uma versão anterior, sobre o acervo: o
`prompts/verificador.md` roda numa sessão na nuvem, paga com o crédito de
US$ 250 que expira em 05/11, e confere de uma vez os 40 episódios publicados.
Sai a linha de base sem esperar semanas de produção, e o prompt vira o ponto de
partida do verificador diário.

## Consequências

- Mais etapas, mais pontos de falha e mais tempo de relógio. O orquestrador
  precisa de repescagem por etapa, não só por execução.
- Cada agente sabe só o que está no contrato. Fonte, citação literal e data
  precisam viajar no arquivo, ou o roteirista escreve sem ter lido.
- Subagentes em Opus, em paralelo, gastam o limite do Max mais rápido.
