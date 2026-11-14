# Varredura por feeds (H2)

Proposto em 10/11/2026, quando a linha do Jornalista (subagente que lê as
páginas, [plano](plano-leitura-por-subagente.md)) parou de melhorar: cada versão
mexia no custo de um lado e ele subia do outro. Das três hipóteses levantadas
naquele dia, esta é a que dá para medir sem gastar modelo.

**Hipótese.** Boa parte do trabalho do agente é descobrir o que saiu: abrir
"anthropic.com/news", "blog.google/technology/ai", "huggingface.co/Qwen" e ler a
listagem. Um feed RSS, Atom ou um sitemap diz o mesmo — título, data e
endereço — sem modelo nenhum. Se um script ler os feeds antes e entregar a
lista da janela, o agente começa sabendo o que é novo e abre só o post.

**O que não resolve.** Pauta que nasce fora das fontes (imprensa, governo,
GitHub, X), que é uns 30% do que vai ao ar, e porta fechada: o feed da OpenAI
dá título, data e resumo, mas o post continua dando 403. Para a primeira, a
hipótese H1 (um agente barato que acha pautas) complementa esta.

## Fase 0 — inventário e teste com o passado (12/11, sem custo)

Feito fora do repositório, com urllib e um User-Agent genérico, sem contornar
nada.

**Leituras de listagem.** 32% das leituras de página dos 20 dias de produção
de 14/10 a 11/11 foram de listagem ou feed (282 de 893, 14 por dia; contado em
11/11). Em 10, 11 e 12/11:
25, 22 e 29 listagens por dia, 16, 16 e 20 delas em sites que têm feed ou
sitemap.

**O que existe.** Das 18 fontes do `sources.yaml` e das portas vizinhas que já
deram pauta:

| | Fontes |
|---|---|
| Feed | OpenAI (e as portas: comunidade, alinhamento), Google (quatro seções do blog), DeepMind, Mistral, NVIDIA (blog e sala de imprensa), AWS, YC, Sequoia, Zhipu, Meta newsroom, Apple, Microsoft, Thinking Machines, Cloudflare, Google Cloud, Hugging Face (blog), arXiv, CrowdStrike, NCSC, Tesouro americano |
| API | Qwen, DeepSeek, Moonshot, Zhipu e MiniMax no Hugging Face |
| Sitemap com data | Anthropic (570 de 589 páginas com data), xAI, a16z (sitemap de notícias, com título), Meta research, Cohere |
| Nada | ai.meta.com (sitemap dá 403), Moonshot, Kimi, MiniMax, DeepSeek API, claude.com (sitemap sem data) |

Todos os endereços acima são permitidos pelo robots.txt (dois sites não têm um).
O blog do Google tem feed por seção, e o de IA não traz os posts dos modelos
Gemini: três das pautas de outubro só apareceram no feed da seção de modelos.

**Teste com o passado.** Das 87 pautas que foram ao ar de 01/10 a 12/11:

| | Pautas |
|---|---|
| Estariam na lista | 53 |
| O feed de hoje não volta até a data (numa execução diária, estariam) | 5 |
| O site tem feed e o endereço não veio | 4 |
| O site não tem feed | 25 |

Das que vieram de site com feed e dentro do alcance dele, 53 de 57 (93%). As 4
que faltaram estavam em seções sem feed próprio (Google Research, comunicados
da CrowdStrike, notícias da Thinking Machines, a Reflection no Hugging Face).
As 25 sem feed: 9 de imprensa, 7 de governo ou FMI, 4 de laboratório sem feed,
2 do GitHub, 1 do X, 2 de sites avulsos.

**Os últimos dias.** A execução de 11/11, a do Mac dormindo, deixou passar a fala
do Bessent (feed do Tesouro, 10/11 às 22:15) e o comunicado do conselho da
NVIDIA (sala de imprensa, 10/11 às 16:07); os dois estariam na lista dela. A de
10/11 não viu o Gemini Robotics 2.5 (feed do DeepMind: 09/11). Os TPUs 8tx e 8i
Max foram vistos em 10/11 e descartados; o log de 12/11 os dá como perdidos, com
a data de um resumo do dev.to.

**Tamanho.** 28 a 37 linhas por dia, sem repetidos; AWS e Google Cloud somam de
4 a 16 delas, quase tudo guia de parceiro. Daí o teto por fonte.

Critério para a fase 1: a lista traz pelo menos 80% das pautas de fontes com
feed (93%) e cabe em umas 40 linhas por dia (28 a 37). Passou.

## Fase 1 — sombra (a partir de 13/11)

`scripts/varredura.py` lê os feeds de `config/varredura.json` e grava
`logs/varredura-AAAA-MM-DD.md` (a lista como entraria no prompt) e `.json`
(tudo, para medir). O orquestrador chama **depois** do agente, e a lista não
entra no prompt.

Decisões, cada uma com o motivo:

- **Depois do agente, não antes.** O agente tem Glob e Grep e já leu arquivo de
  `logs/` (28/10). Rodando depois, a lista do dia nunca existe enquanto ele
  trabalha. Como a janela termina ontem, a lista sai igual à das 05:00.
- **Arquivo próprio, fora do `sources.yaml`.** O agente lê o `sources.yaml`; na
  sombra ele não pode ver nada diferente do que vê hoje.
- **Sitemap: vale a primeira vez que a página foi vista.** A data do sitemap é
  a da última edição; a página do Fable 5.2 voltou em 11/11 porque foi editada,
  e já tinha ido ao ar em 10/11. Comparar com a leitura anterior erraria a
  página publicada entre a meia-noite e a hora da execução. O estado em
  `logs/varredura-vistos.json` guarda quando cada página apareceu; se foi antes
  do começo da janela, ela é antiga e foi editada. Linha de base gravada em
  12/11 às 21:37.
- **Gzip.** O DeepMind passou a mandar o feed comprimido sem que se pedisse
  (12/11, à noite; de manhã veio sem). O limite de 6 MB vale depois de
  descomprimir.
- **Dado de terceiros.** Título e resumo saem sem marcação, sem crase, com 160
  caracteres no máximo; XML que declara entidade é recusado antes do parser.
- **Não bloqueia.** 10 s por feed, 60 s no total, threads que não seguram a saída
  do Python; feed que falha vira linha em "Falharam". Os 36 feeds levam uns 3,5 s.
- **Python do launchd.** O `env -i` com `/usr/bin` na frente pega o Python 3.9 da
  Apple, que não segue redirecionamento 308 (Sequoia) e leva 403 do Cloudflare
  (xAI). A produção roda o 3.13 do PATH do plist; meça com ele.

Ensaio (`scripts/ensaio.sh`) roda com a varredura desligada: num dia passado, os
feeds de agora não são os que a produção teria visto.

**O que medir, todo dia, até 19/11** (20/11 é feriado):

1. Pautas que foram ao ar e estavam na lista (acerto).
2. Pautas de site com feed que não estavam na lista (falha do feed).
3. Itens da lista que o agente não leu nem descartou (descoberta perdida).
4. Data do feed contra a data que o agente leu na página (Gemini Robotics 2.5:
   09/11 no feed, 10/11 na página, segundo o log de 12/11).
5. Linhas por dia e por fonte, e quantas viraram pauta: fonte que só ocupa
   linha sai antes da fase 2.
6. Falhas por feed.

As listas da sombra servem também de entrada para a fase 2: o ensaio de um dia
passado usa a lista gravada naquele dia, e não a dos feeds de agora (o da AWS,
por exemplo, só guarda três dias).

## Fase 2 — ensaio com a lista no prompt

Versão nova do Editor em `config/agentes.json`: a lista entra como seção do
prompt, como "Pautas já cobertas", e o passo 4 do `master.md` diz para partir
dela — para as fontes da lista, não abrir a listagem, só o post candidato;
fontes sem feed seguem como hoje. Ensaio contra o Editor em produção em dois
dias da sombra.

Critério: leituras de listagem de ~20 para menos de 5 por dia; custo e tempo
iguais ou menores; nenhuma pauta da lista perdida.

O Editor 1.1 (porta fechada, três coberturas) também muda o prompt. Uma mudança
por vez: o que chegar pronto primeiro vai ao ensaio primeiro.

## Fase 3 — produção

Com o OK do autor, olhando os números do ensaio.
