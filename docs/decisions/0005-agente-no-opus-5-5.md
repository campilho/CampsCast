# ADR 0005 — Agente no Claude Opus 5.5, com esforço fixado

- **Status:** aceito, provisório — revisão em 03/10/2026, com cinco dias de produção
- **Data:** 2026-09-26

## Contexto

O Claude Opus 5.5 saiu com preço de tabela 20% abaixo do Opus 5: US$ 4 e
US$ 20 por milhão de tokens de entrada e saída, contra US$ 5 e US$ 25. A
pergunta não era se o modelo é melhor em abstrato, e sim quanto custa e como
soa **um episódio do CampsCast** escrito por ele.

Duas pré-condições apareceram antes de qualquer medição.

**O CLI do pipeline não aceitava o modelo.** Atualizar o app desktop não
atualiza o `claude` instalado por npm, que é o que o launchd chama. A versão
2.1.241 respondeu `400 ... version 2.1.280 or newer is required`. Trocar só o
nome do modelo teria derrubado a execução seguinte.

**O esforço mudaria junto, sem ninguém pedir.** O pipeline nunca passou
`--effort`. As transcrições mostram que o Opus 5 rodou em `"effort":"high"` em
todas as 111 chamadas de 25/09 — era o padrão dele. O padrão do Opus 5.5 é
`medium`, um degrau abaixo. Trocar de modelo sem fixar isso trocaria duas
variáveis de uma vez, e qualquer diferença no episódio ficaria sem dono.

## Medição: o episódio de 25/09 refeito

O episódio de 25/09 foi refeito inteiro — pesquisa, roteiro e narração — num
sandbox fora do repositório, sem publicar. O estado anterior foi reconstruído
desfazendo, na ordem inversa, as oito edições que o agente de 25/09 fez em
`covered-index.json` e `saved-items/backlog.md`, com o texto exato registrado
na transcrição. Mesma janela (24/09), mesmo número (21), mesmo esforço medido
(`high` nas 194 chamadas do Opus 5.5).

| | Opus 5 (produção) | Opus 5.5 (sandbox) |
|---|---|---|
| Custo do agente | US$ 6,54 | US$ 7,27 (+11%) |
| Turnos | 77 | 123 |
| Cache lido | 4,9 mi tokens | 12,5 mi tokens |
| Cache escrito | 183 mil | 305 mil |
| Saída | 63 mil | 71 mil |
| WebSearch | 22 | 21 |
| **WebFetch** | **19** | **51** |
| Fontes distintas, segundo a ficha técnica | 17 | 40 |
| Parte do Haiku (leitura de páginas) | US$ 0,66 | US$ 0,90 |
| Tempo do agente | 17,4 min | 16,1 min |
| Palavras / áudio | 1.310 / 8min35s | 1.390 / 8min50s |
| Créditos da ElevenLabs | 4.212 | 4.379 |
| Pautas | as mesmas três | as mesmas três, ângulo diferente na segunda |

Os custos que o CLI reporta fecham com a tabela de preços considerando escrita
de cache de uma hora (2× a entrada) e leitura de cache a US$ 0,50 no Opus 5 e
US$ 0,20 no Opus 5.5.

## Leitura

**Mais barato por token não foi mais barato por episódio.** O Opus 5.5 abriu
2,7 vezes mais páginas para o mesmo número de buscas. Cada página é um turno a
mais, e cada turno relê o contexto inteiro do cache. A leitura de cache ficou
2,5 vezes maior, e o custo dela praticamente empatou: US$ 2,51 contra US$ 2,46.
A queda de preço foi absorvida pelo volume.

**Uma execução contra uma execução não decide.** Nos dez episódios de 14 a
25/09, o Opus 5 custou de US$ 6,54 a US$ 10,77, com mediana de US$ 8,66 — e
25/09 foi justamente o dia mais barato do período. Contra a mediana, os US$ 7,27
do Opus 5.5 ficam 16% abaixo. Com uma amostra de um, não dá para separar o
modelo da variação normal de um dia para o outro.

**O que é comportamento, e não ruído, é a leitura.** Cinquenta e uma páginas
abertas contra dezenove — e quarenta fontes distintas contra dezessete, pela
contagem que o próprio agente declara na ficha — é uma diferença grande demais
para ser acaso, e vai na
direção da regra de fonte primária do projeto. Se isso melhora o episódio é
julgamento de ouvido, feito pelo autor.

Uma segunda rodada do mesmo dia, horas depois e já com a abertura nova do
[ADR 0006](0006-abertura-no-tom-nao-no-texto.md), custou US$ 6,60 em 120
turnos — 9% abaixo da primeira. É a variação entre duas execuções do mesmo
modelo no mesmo dia, e mostra o tamanho do ruído que a revisão de 03/10 vai
ter de enxergar através.

A pesquisa foi feita dois dias depois da original, com mais cobertura de 24/09
disponível na web. Isso pode ter influenciado a escolha das páginas; não
influencia o preço por token.

## Decisão

O agente passa a rodar no `claude-opus-5-5` com `--effort high` a partir de
28/09 (`CLAUDE_MODEL` e `CLAUDE_EFFORT` em `scripts/run_episode.sh`).

Na revisão de 03/10, com cinco episódios em produção, a comparação é contra a
semana do Opus 5, pelo registro em `metricas/execucoes.jsonl`:

- **mediana até 15% acima de US$ 8,66**, ou abaixo: mantém;
- **mais de 15% acima, sem ganho audível**: testar `--effort medium`, que é o
  padrão do próprio modelo e o lugar natural de colher o preço menor.

## Consequências

- O CLI do terminal precisa estar em 2.1.280 ou mais. Atualizar o app desktop
  não basta: é outro binário, instalado como root, que pede `sudo npm install
  -g @anthropic-ai/claude-code@latest`.
- O registro de execução passou a gravar o esforço **lido da transcrição**, não
  o que o orquestrador pediu. Foi lendo a transcrição que se descobriu o `high`
  implícito do Opus 5.
- A ficha técnica falada diz "Claude Opus cinco ponto cinco", por extenso — o
  nome vem de `nomes.py`, derivado do id do modelo, e não precisou de ajuste.
