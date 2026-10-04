# ADR 0008 — Memória em camadas: acervo sem fim, leitura com teto

- **Status:** aceito; implementação por etapas (C1 a C7)
- **Data:** 2026-10-03

## Contexto

Em 03/10 a memória do agente foi medida pelas transcrições
(`scripts/memoria_custo.py`): nos dias do Opus 5.5, índice, backlog e
roteiros eram ~42% do cache lido. O índice não cabia mais numa leitura da
ferramenta Read e o agente via só começo, títulos e fim. Os passos A (lista
compacta de pautas no prompt) e B (histórico do backlog fora da leitura
diária) resolveram o imediato; no ensaio de 02/10, o índice foi de 21% para 1%
do cache lido e o backlog de 11% para 6%.

Mas a lista compacta cresce ~110 KB por ano: ~115 KB em um ano, ~340 KB em
três — uns 145 mil tokens relidos a cada chamada. O problema volta, só mais
devagar. E o podcast quer outra coisa que a memória de hoje não dá: falar do
passado com propriedade ("há um ano, a preocupação era esta; hoje está
resolvida").

## Medido em 03/10, depois de 26 episódios

| Item | Hoje | Ritmo |
|---|---|---|
| Pautas | 78 | 3 por episódio, ~750 por ano |
| Roteiro | ~9,5 KB | ~2,4 MB por ano |
| Log de pesquisa | ~14 KB | ~3,5 MB por ano |
| Índice detalhado | 241 KB, ~3,1 KB por pauta | ~2,3 MB por ano |
| Lista compacta | 11,5 KB, 147 B por pauta | ~110 KB por ano |
| Memória lida por dia | ~85 KB | cresce com a lista |

## Decisão

**O acervo cresce para sempre; o que é lido por dia tem teto.** Nada se apaga:
roteiros, logs de pesquisa e índice são a fonte, e tudo o mais é derivado.

| Camada | O que é | Lida todo dia? | Teto lido |
|---|---|---|---|
| 0. Acervo | roteiros, `research/`, `covered-index.json` | não, por busca | — |
| 1. Curto prazo | 5 roteiros na íntegra | sim | ~47 KB |
| 2. Lista de pautas | uma linha por pauta, últimos 90 dias no prompt | sim | ~28 KB |
| 3. Semanas | `memoria/semanas/AAAA-Wnn.md`, ~1,5 KB | as 4 últimas | ~6 KB |
| 4. Meses | `memoria/meses/AAAA-MM.md`, ~3 KB | os 2 últimos | ~6 KB |
| 5. Há um ano | resumo da mesma semana do ano anterior, escolhido pelo orquestrador | sim, desde ago/2027 | ~1,5 KB |
| 6. Trimestres e anos | `memoria/trimestres/`, `memoria/anos/` | não, por busca | — |
| Temas | `memoria/temas.md` | sim | ~5 KB, 10 temas |
| Fios em aberto | `memoria/fios.md` | sim | ~10 KB, 20 fios |
| Backlog | pautas ativas | sim | ~12 KB |

Total lido por dia: ~110 a 120 KB, em qualquer ano. Começa um pouco acima dos
~85 KB de hoje — o C não existe para economizar agora, e sim para impedir o
crescimento linear e dar memória de narrativa.

### Projeção

| | Hoje | 1 ano | 2 anos | 3 anos | 5 anos |
|---|---|---|---|---|---|
| Pautas no acervo | 78 | ~830 | ~1.580 | ~2.330 | ~3.830 |
| Acervo em disco | 0,8 MB | ~8 MB | ~17 MB | ~25 MB | ~42 MB |
| Lista inteira, se sem teto | 11,5 KB | ~120 KB | ~230 KB | ~340 KB | ~560 KB |
| Lido por dia, com o C | ~85 KB | ~115 KB | ~115 KB | ~115 KB | ~115 KB |

### Regras que valem para todas as camadas

- **Resumo aponta para o original.** Cada resumo cita os episódios de onde veio.
  Antes de falar do passado no ar, o agente relê o roteiro original — a regra de
  fonte primária vale para a própria memória. Resumo de resumo perde e inventa
  detalhe.
- **Repetição e narrativa são memórias diferentes.** Para não repetir pauta,
  resumo não serve; serve a linha por pauta e, além dos 90 dias, a busca no
  índice. Os resumos servem à continuidade.
- **Resumo tem conferência determinística** (`confere_resumo.py`): toda pauta do
  período citada, todo episódio citado existe, nenhuma data fora do período,
  tamanho dentro do teto. Se falhar, registra e não grava.
- **Quem escreve os resumos:** um passo do orquestrador depois da publicação,
  que não bloqueia o episódio. Um script decide o que está pendente, como a
  `window.py` decide a janela — semana que fechou sem resumo é feita no dia útil
  seguinte, sem buraco. O texto vem de um `claude -p` com prompt próprio
  (`prompts/memoria.md`), sobre um esqueleto montado do índice. **Se o
  pipeline migrar de máquina ou para a nuvem, este passo vai junto.**
- **Revisão humana no começo:** os resumos das primeiras semanas e o de setembro
  são lidos pelo autor antes de o agente passar a usá-los. Depois, só a
  conferência.

### Temas e fios: perguntas que não fecham e perguntas que fecham

Discutido com o autor em 03/10: "desacelerar a fronteira" foi proposto como
fio e não cabia — vai ganhar notícia por anos e nunca fecha. Daí duas
camadas:

| | Tema | Fio |
|---|---|---|
| Exemplo | Desacelerar a fronteira | Quando acaba a pausa da OpenAI? |
| Fecha? | nunca; no máximo adormece | sim |
| Guarda | estado reescrito, 3 episódios recentes | pergunta, 3 marcos, prazo |
| Quem cria | **o autor** — é linha editorial | o agente, com regras |
| Teto | 10 temas (8 em 03/10) | 20 fios |

O estado do tema é sobrescrito; a evolução fica nos resumos mensais e anuais,
que terão uma seção por tema — matéria-prima do "há um ano" e da linha do
tempo. O fio aponta para os temas; a lista de fios de um tema é calculada, não
armazenada. Fio só para desfecho esperado em até ~6 meses: previsão mais longa
fica no índice e volta pelo "há um ano".

Temas iniciais: desacelerar a fronteira; agentes fora do controle; quem
fiscaliza os laboratórios; EUA e China na IA; acesso restrito a capacidades
perigosas; e dois pedidos do autor — a busca pela AGI, e empregos em massa e
o risco para a humanidade. No mesmo dia, a primeira sugestão do agente,
feita no ensaio — ciência feita por máquina: quem confere? —, foi aprovada e
virou o oitavo tema. Fios iniciais: 10, escolhidos pelo autor entre 17
propostos a partir das notas de desdobramento do índice.

### Sugestões de tema e o relatório do autor

O agente pode perceber uma questão de fundo que merece tema; no futuro, os
ouvintes também. Para a sugestão não se perder no log de pesquisa, ela vai
para `memoria/temas-sugeridos.md` (pendente, aprovado, recusado), e quem decide
é o autor. Até 10 pendentes; recusada fica registrada para não voltar.

Para o autor ver o que pede decisão sem ir procurar, `scripts/relatorio.py`
junta, por semana: episódios e custo, sugestões pendentes, fios vencidos e
fechados, temas que mudaram, fontes que falharam na leitura (das transcrições)
e avisos das conferências. Dois gatilhos: o comando `/relatorio`, a pedido, e
o orquestrador no último episódio da semana — o calendário decide, então é a
quinta quando a sexta é feriado —, que grava `memoria/autor/AAAA-Wnn.md` e
põe um resumo só com contagens no `estado.json` público. O vigia na nuvem lê
esse resumo e avisa no celular.

### Fios em aberto

Preocupações, promessas e previsões que apareceram no ar, no molde do backlog:

```
## F-012 · Agentes da OpenAI que escaparam do sandbox
- aberto: 2026-09-28 (ep. 22)
- pergunta: haverá sanção? a perícia independente confirma?
- marcos:
  - 2026-10-02 (ep. 26) — perícia da Asymmetric reconstrói 55 sites
- situação: aberto
- rever até: 2026-12-31
```

- Situações: aberto, cumprido, desmentido, resolvido, arquivado (esfriou sem
  desfecho).
- O agente do dia acrescenta um marco quando uma notícia mexe num fio, abre um
  fio quando o episódio levanta pergunta concreta e verificável, e fecha quando
  há desfecho — contando a história no ar. Fio fechado vai para
  `memoria/fios-fechados/AAAA.md`, que não é lido no dia a dia.
- **Teto: 20 fios abertos, 3 marcos por fio, ~10 KB.** Um fio com três marcos
  tem uns 500 bytes; 20 fios dão ~10 KB. O caminho completo de um fio fica nos
  roteiros citados e no histórico do git.
- `confere_fios.py` registra, sem bloquear: campos faltando, situação fora da
  lista, fio fechado ainda no arquivo, data de revisão vencida, episódio citado
  inexistente, mais de 3 marcos, mais de 20 fios, arquivo acima do teto.

### Conferência de repetição por link

Depois do roteiro, `confere_repeticao.py` compara os links das pautas do dia com
os de todas as pautas anteriores do índice. Link repetido vira aviso no
registro. Entra já, porque é barata; é a rede de segurança para quando a lista
do prompt tiver teto de 90 dias.

## Etapas

| Etapa | O quê | Quando |
|---|---|---|
| C1 | Temas e fios em aberto, conferência, listas iniciais aprovadas pelo autor | 03/10 |
| C2 | Resumos semanais, passo pós-publicação, conferência; carga das 6 semanas de 24/08 a 02/10 | semana de 12/10 |
| C3 | Resumo mensal: setembro como piloto, outubro no começo de novembro | out/nov |
| C4 | Repetição por link já; teto de 90 dias na lista quando passar de ~30 KB | 03/10; ~jan/2027 |
| C5 | Trimestre e ano | dez/2026 |
| C6 | Há um ano no prompt | desde 24/08/2027 |
| C7 | Linha do tempo da IA, projeto paralelo do acervo | quando houver acervo |

Junto com o C2, medir se 4 resumos semanais permitem ler 3 roteiros na íntegra
em vez de 5 (hoje 16% do cache lido) — decidir pelo custo medido.

## Consequências

- O custo de memória deixa de crescer com o tempo; no primeiro ano fica um pouco
  acima do de hoje.
- O podcast ganha o que hoje não tem: continuidade de semanas e meses, e
  promessas e preocupações acompanhadas até o desfecho.
- Mais um passo de modelo por semana (e por mês), com custo a medir no primeiro.
- As camadas são arquivos portáveis; na Fase 4, vale comparar com o módulo de
  memória do AgentCore.
