# ADR 0013 — Leitura de páginas: WebFetch no próprio agente, e o experimento vigiado

- **Status:** aceito (08/11/2026); em produção a partir do episódio de 09/11
- **Data:** 2026-11-08

## Contexto

Em 05 e 06/11 o agente não leu nenhuma página com o WebFetch. Chamou 10 e 11
vezes um subagente "web-fetch", e eram os subagentes que liam: 46 e 68
páginas. Nada mudou do nosso lado; o CLI era o 2.1.283 de 03 a 06/11. O custo
do agente foi de US$ 4,98 (03/11) para 7,83 (06/11), +57%, e as medições que
liam só a transcrição principal mostraram zero leituras. Ninguém percebeu por
quatro dias: o achado veio do relatório da semana (aprendizados, "O agente
passou a ler por subagente").

## O que foi medido

**A troca é um experimento da Anthropic, ligado por interruptor remoto.** No
próprio CLI (strings do binário, 2.1.283), o subagente é ligado assim:

```
enabled = CLAUDE_CODE_WEB_FETCH_AGENT ?? interruptor("tengu_clever_orbit", false)
```

O cache local (`~/.claude.json`) tinha `tengu_clever_orbit: true` dentro do
experimento `tengu_clever_orbit_experiment`, variação 1. Às 12:04 de 08/11 o
interruptor voltou a `false` e o experimento sumiu do cache. Minutos depois,
porém, uma sessão interativa aberta recebeu o subagente de novo, com o cache
ainda em `false`. **O cache é indício, não prova.** A documentação oficial não
cita o subagente e ainda descreve o WebFetch antigo, que devolve um resumo.

**O que o subagente embutido é.** O "web-fetch" tem o WebFetch como única
ferramenta, `model: "inherit"` (o mesmo modelo do agente principal), no máximo
15 turnos e não lê o CLAUDE.md. O prompt dele diz que o agente principal "never
sees the page content, only your report" e trata a página como dado não
confiável; o WebFetch de dentro dele devolve a página crua ("Fetched … (HTTP
200 OK, …)"). A leitura é isolamento contra instrução escondida em página —
inferência pelo prompt, sem confirmação da Anthropic.

**Como controlar** (ambiente limpo, como o do launchd; testes de centavos):

| Para | Como | Resultado |
|---|---|---|
| WebFetch direto no agente | `CLAUDE_CODE_WEB_FETCH_AGENT=0` (ou `false`) | o agente tem o WebFetch; o "web-fetch" some |
| Forçar o subagente | `CLAUDE_CODE_WEB_FETCH_AGENT=1` | a variável vence o interruptor |
| "web-fetch" em outro modelo | `CLAUDE_CODE_SUBAGENT_MODEL=claude-haiku-5-5` com `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` | rodou no Haiku 5.5, com página crua; sem o FORCE ele herda o principal |
| Subagente nosso | `--agents` com `prompt`, `model` e `tools: ["WebFetch"]` | funciona; o WebFetch dele vem resumido, no formato antigo |
| Resumo e busca mais baratos | `ANTHROPIC_DEFAULT_HAIKU_MODEL` (ou `ANTHROPIC_SMALL_FAST_MODEL`) `=claude-haiku-5-5` | resumo das páginas e WebSearch passam do Haiku 4.5 ao 5.5; a busca funcionou |

A ordem de escolha do modelo de um subagente, no código do CLI: o parâmetro
`model` da chamada, depois o `model` da definição, depois
`CLAUDE_CODE_SUBAGENT_MODEL`; `inherit` na definição vence a variável, a menos
que o FORCE esteja ligado.

**No CLI 2.1.283, os apelidos são os antigos:** `haiku` é o Haiku 4.5 e
`sonnet` é o Sonnet 5. Os IDs `claude-haiku-5-5` e `claude-sonnet-5-5`
funcionam, mas o CLI não os conhece: avisa `unrecognized_model` e estima o
custo pela tabela do Opus 5.5 (US$ 4 e 20 por milhão). O `custo_estimado_usd`
do registro ficaria errado com esses modelos.

**De onde veio o custo.** A conta de cada dia bate até o centavo com a tabela
oficial (Opus 5.5: US$ 4 entrada, 20 saída, 0,20 leitura de cache), com um
detalhe que só a conta mostrou: **a sessão principal grava cache de 1 hora**
(2×, US$ 8 por milhão) **e os subagentes, de 5 minutos** (1,25×, US$ 5). E
sempre houve um segundo modelo: o Claude Haiku 4.5 resume as páginas do
WebFetch e faz as buscas (US$ 0,87 a 1,05 por dia até 04/11; a busca custa
US$ 0,01 cada).

| 06/11 | US$ |
|---|---|
| principal: cache escrito (191 mil, 1 h) | 1,53 |
| principal: cache lido (4,1 milhões) | 0,83 |
| **subagentes: cache escrito (592 mil, 5 min) — as páginas cruas** | **2,96** |
| subagentes: cache lido | 0,09 |
| saída, dos dois (99 mil) | 1,99 |
| Haiku 4.5: 11 buscas | 0,43 |
| **total** | **7,83** |

Antes, a mesma leitura passava pelo Haiku 4.5 por cerca de US$ 0,75 por dia.
Estimativa para 06/11 com os mesmos tokens (a qualidade não foi medida):

| Leitura feita por | US$ por episódio |
|---|---|
| "web-fetch" no Opus 5.5 (o que rodou) | 7,83 |
| "web-fetch" no Sonnet 5.5 | ~6,0 |
| modo antigo, resumo no Haiku 4.5 (real em 03 e 04/11) | 4,98 a 5,25 |
| "web-fetch" no Haiku 5.5 | ~4,3 |
| modo antigo, resumo e busca no Haiku 5.5 | ~4,4 a 4,6 |

## Decisão

1. **O orquestrador fixa `CLAUDE_CODE_WEB_FETCH_AGENT=0`**, ao lado do modelo
   e do esforço. A produção volta ao modo dos 47 episódios até 04/11 e sai do
   sorteio do experimento. Quem quiser o outro modo (num ensaio, por exemplo)
   passa a variável explícita, que vence o padrão.
2. **O experimento é vigiado em toda execução** (`scripts/confere_claude.py`),
   porque pode voltar com outro nome ou passar por cima da variável:
   - antes do agente, o estado do `tengu_clever_orbit` no cache vai para o
     log, ligado ou desligado; ligado vira aviso no registro, mesmo com a
     variável em 0. Também vai para o log a lista de qualquer interruptor do
     CLI que mudou desde a execução anterior (a foto fica em
     `logs/claude-interruptores.json`, fora do git);
   - depois do agente, a transcrição diz o que a sessão fez: chamada ao
     "web-fetch", página crua no lugar do resumo ou modelo que não seja o
     principal nem o pequeno do CLI viram aviso.
   Os avisos aparecem em "Avisos das conferências" no relatório da semana.
3. As medições já leem os subagentes (`scripts/transcricoes.py`), nos dois
   formatos de resposta do WebFetch.

## Consequências

- O custo deve voltar a ~US$ 5 por episódio. A leitura volta a passar pelo
  resumo do Haiku 4.5, como até 04/11.
- Se o experimento voltar e passar por cima da variável, o aviso sai no mesmo
  dia, no log e no registro, e na sexta no relatório.
- Não fica decidido aqui o modelo da leitura. Baratear com o Haiku 5.5 ou o
  Sonnet 5.5, ou criar um subagente Jornalista nosso, só depois de comparar a
  qualidade com os pedidos reais de 05 e 06/11 (plano em
  `docs/plano-leitura-por-subagente.md`).
- Trocar o modelo pequeno ou usar modelos que o CLI 2.1.283 não conhece exige
  que o registro calcule o custo pela própria tabela de preços.
