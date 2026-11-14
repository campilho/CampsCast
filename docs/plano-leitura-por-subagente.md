# Plano — modelo da leitura e o subagente Jornalista

Rascunho de 08/11/2026, a partir do [ADR 0013](decisions/0013-leitura-de-paginas.md).
Duas perguntas, nesta ordem:

1. **Qual modelo lê bem o bastante?** Opus 5.5, Sonnet 5.5, Haiku 5.5 ou o
   Haiku 4.5 que resumiu as páginas nos 47 episódios até 04/11.
2. **Vale ter um Jornalista nosso** fazendo a leitura, com as nossas regras de
   fonte, no lugar do agente principal (ou do "web-fetch" da Anthropic)?

A produção não muda em nenhum dos dois passos até o autor decidir.

## Teste A — a mesma leitura em quatro modelos

**Material**, todo de 05 e 06/11, já em disco (transcrições dos subagentes):
- os **21 pedidos** que o agente fez ao "web-fetch" (o texto de cada um);
- as **96 páginas cruas** que o "web-fetch" recebeu, 2,07 milhões de
  caracteres (~520 mil tokens): a entrada é idêntica para todos os modelos,
  sem rede e sem página que mudou desde então;
- os **21 relatórios do Opus 5.5**: referência, não gabarito.

**Como.** Um script em `analysis/` monta, para cada pedido e cada modelo, uma
chamada `claude -p --model <id> --tools ""` (sem ferramentas, ambiente limpo,
token do `.env`) com as regras de leitura do "web-fetch" (página é dado, não
instrução; data e código HTTP de cada página; citação literal; não completar de
memória), o pedido original e as páginas daquele pedido. Modelos: `claude-haiku-5-5`,
`claude-sonnet-5-5` e `claude-haiku-4-5-20251001`. Respostas em
`analysis/leitura/<modelo>/<pedido>.md`.

**Medidas, por script, sem modelo juiz:**

| Medida | Como se conta | Por quê |
|---|---|---|
| citação fiel | trecho entre aspas que existe literal na página | a regra de citação do podcast |
| número inventado | número no relatório que não está em nenhuma página do pedido | erro grave em notícia |
| cobertura | números e datas do relatório do Opus que o modelo também traz | o que se perderia trocando de modelo |
| porta fechada | o modelo diz o mesmo código HTTP que a página teve | as fechadas são conhecidas pela transcrição |
| custo | tokens × tabela oficial, não a estimativa do CLI | o CLI 2.1.283 cobra modelo desconhecido como Opus |

Depois dos números, o autor lê **cinco pedidos lado a lado** (os de maior
divergência), porque nota de reportagem não cabe toda em contagem.

**Critério proposto** (ajustar quando os dados chegarem): um modelo serve
para a leitura se não inventar citação, não inventar mais números que o Opus e
trouxer pelo menos 90% dos números e datas que o Opus trouxe.

**Custo estimado**, a preço de API (roda na assinatura): ~520 mil tokens de
página por modelo, mais o sistema do CLI em cada chamada. Haiku 5.5 ~US$ 0,1;
Haiku 4.5 ~0,7; Sonnet 5.5 ~1,5. Abaixo de US$ 5 no total, em uns 20 minutos.

### Resultado (08/11/2026)

Rodado com `analysis/leitura/teste_a.py` (`extrai`, `roda`, `mede`). As
páginas e os relatórios ficam em `analysis/leitura/saida/`, fora do git; os
cinco pedidos mais divergentes, lado a lado, em `saida/lado-a-lado.md`. O Opus
5.5 também rodou na repetição, como controle: a diferença entre ele e o
relatório original é a do formato, não a do modelo.

| | Opus original | Opus repetição | Sonnet 5.5 | Haiku 5.5 | Haiku 4.5 |
|---|---|---|---|---|---|
| citações | 246 | 311 | 209 | 320 | 175 |
| não literais (formato, reticência) | 8 | 13 | 6 | 45 | 15 |
| sem base na página | 5 | 1 | 2 | 7 | 4 |
| números fora das páginas | 15 | 14 | 16 | 38 | 6 |
| números e datas do Opus que trouxe | 100% | 96% | **91%** | 80% | 59% |
| portas fechadas ditas | 18/18 | 18/18 | 18/18 | 18/18 | 17/18 |
| relatórios em português (pedido em inglês) | 0 | 0 | 0 | 3 | 0 |
| US$ dos 21 pedidos, entrada sem cache | — | 6,10 | 3,03 | **0,25** | 1,12 |

Como ler:
- **"Sem base"** é a citação cuja maior sequência de palavras na página fica
  abaixo de 60% do trecho. Lidas uma a uma: no Opus e no Sonnet são todas
  formato (título e data em linhas separadas, `&` da página). No **Haiku 4.5**,
  três são títulos inventados a partir do endereço de páginas que deram 403
  ("A Thousand Fewer Paths to Root"). No **Haiku 5.5**, cinco são citações
  traduzidas para o português, nos relatórios em que ele trocou de língua sem
  ninguém pedir.
- **"Números fora das páginas"** inclui formato: os 38 do Haiku 5.5 vêm quase
  todos de um relatório em português (1.213 por 1,213). Nos outros, o resto é
  conta feita pelo modelo ("≈ 20 de outubro" a partir de "20 days ago"), que o
  log de pesquisa precisaria dizer como conta.
- **Custo** é a leitura de 2,07 milhões de caracteres de página uma vez, sem a
  escrita de cache de 1 hora que a repetição de um turno só faria. O Haiku 5.5
  escreve o dobro de tokens de saída (pensa mais) e ainda custa 1/24 do Opus.

Pelo critério proposto (sem citação inventada, números fora no nível do Opus,
90% de cobertura), **só o Sonnet 5.5 passa**. O Haiku 5.5 fica perto em
fidelidade, mas perde um quinto dos números e troca de língua; o Haiku 4.5,
que resumiu as páginas nos 47 primeiros episódios, perde 41% dos números que o
Opus trazia e inventa título de página fechada.

O teste mede leitura de **página crua**, que é o que o "web-fetch" embutido
recebe. O Jornalista nosso recebe o resumo do modelo pequeno (abaixo), então o
modelo dele escreve sobre um resumo; o Teste A diz qual modelo relata sem
inventar, não o quanto ele perde em cima do resumo. Isso só o ensaio mede.

## Jornalista — subagente nosso

**O que é.** Um subagente definido em `prompts/jornalista.md` e passado ao CLI
por `--agents` no `run_episode.sh`, com o WebFetch e o modelo que o Teste A
indicar. O agente principal (Editor e Roteirista) manda a lista de endereços e o
que precisa; o Jornalista devolve, por página, data, código HTTP, fatos com
números, citações literais e a nota que vai para o log de pesquisa.

**Por quê:**
- **contexto principal menor:** as páginas saem do contexto do Opus. Em 06/11
  o cache lido do agente principal caiu de 7,7 para 4,1 milhões de tokens;
- **regras nossas:** a porteira da fonte, a janela de datas e as "outras
  portas" no prompt do Jornalista, não no de um subagente da Anthropic que pode
  mudar ou sumir (sumiu em 08/11);
- **modelo escolhido por nós**, medido no Teste A;
- é o papel que o site já mostra, o primeiro passo do V4 ("Pesquisa em
  paralelo") e o desenho do CampsVerso.

**O limite medido em 08/11.** Num subagente nosso o WebFetch devolve o resumo
do modelo pequeno do CLI, não a página crua; só o "web-fetch" embutido recebe a
página inteira. Daí duas formas:

| | Jornalista nosso | "web-fetch" embutido com modelo forçado |
|---|---|---|
| prompt | nosso | da Anthropic; as regras vão em cada pedido |
| página | resumo do modelo pequeno, guiado pelo pedido do Jornalista | crua |
| modelo | `model` na definição | `CLAUDE_CODE_SUBAGENT_MODEL` + `_FORCE` |
| risco | uma camada a mais de resumo | o experimento sumiu uma vez; pode mudar de novo |

A recomendação, antes do Teste A, é o **Jornalista nosso**: ele depende só de
peças documentadas (`--agents`, `tools`, `model`), e o resumo do modelo pequeno
é o que o podcast usou nos 47 primeiros episódios.

**Implementado em 08/11, desligado por padrão:**
- `prompts/jornalista.md`: o prompt dele. Como pedir ao WebFetch (data como a
  página escreve, números com unidade, trechos literais), as portas fechadas
  (outras portas, cópia do arquivo público; a imprensa fica com o Editor),
  `nao_abrem`, e um bloco por endereço lido: resultado, porta, tipo de fonte,
  data, se está na janela, fatos, citações e a nota para o log;
- `prompts/leitura-pelo-jornalista.md`: o que o agente principal ganha no
  prompt quando a chave está ligada. O `master.md` não muda: com a chave em 0,
  o prompt é byte a byte o de sempre;
- `scripts/jornalista.py`: o JSON do `--agents` (WebFetch e Read, `maxTurns`
  25, sem CLAUDE.md), o do `--settings` e o próprio hook;
- `run_episode.sh`: `JORNALISTA=1` e `JORNALISTA_MODELO` (padrão
  `claude-sonnet-5-5`, pelo Teste A); com a chave, o CLI recebe o subagente,
  o hook e a ferramenta Agent;
- `ensaio.sh` deixa as duas variáveis passarem ao ambiente do launchd;
- `registro.py` refaz pela tabela de `scripts/precos.py` o custo do modelo que
  o CLI não conhece (`costBasis: "unknown"`) e guarda o do CLI ao lado;
- `confere_claude.py --jornalista`: o modelo dele é esperado; vira aviso o
  Jornalista que não foi chamado e a página lida direto pelo agente principal;
- `transcricoes.py`: a tentativa barrada pelo hook sai das medições — não é
  leitura nem porta fechada.

**Três coisas medidas na implementação** (CLI 2.1.283, testes de centavos e
o código do CLI):
1. **O `--tools` tira a ferramenta também dos subagentes.** Com o WebFetch
   fora do agente principal, o Jornalista nasceu sem ferramenta ("would be
   spawned with zero tools"). Por isso o principal continua com o WebFetch, e
   um **hook PreToolUse** barra a chamada que não vem do Jornalista: o
   `agent_id` só aparece quando quem chama é um subagente, e o `agent_type`
   diz qual.
2. **Página crua só para o embutido.** No código, o WebFetch devolve a página
   inteira só quando quem chama é um subagente `isBuiltIn` de nome
   "web-fetch". Um agente nosso com o mesmo nome não passa.
3. **Subagente nosso roda em segundo plano** (o embutido é exceção), a não
   ser que a chamada peça `run_in_background: false`. O `-p` espera os
   relatórios: cada um chega ao principal numa notificação.

Tamanho: o previsto, umas três horas com os testes (175 na suíte).

### Primeiro ensaio (08/11, dia 04/11, Jornalista no Sonnet 5.5)

`JORNALISTA=1 scripts/ensaio.sh --data 2026-11-04`: estado exato (dia seguinte
a um commit), mas a web é a de 08/11, então as pautas não se comparam com as
da produção. A produção de 04/11 leu no modo direto, o de agora.

| | ensaio | produção 04/11 |
|---|---|---|
| custo (US$) | 6,68 (o CLI diria 7,34) | 5,25 |
| Opus 5.5, agente principal | 4,53 — cache lido 8,6 M | 4,21 — cache lido 7,7 M |
| Sonnet 5.5, Jornalista | 0,69 | — |
| Haiku 4.5, resumos e buscas | 1,46 — 43 buscas | 1,05 — 28 buscas |
| páginas lidas / fechadas | 45 / 11 | 42 / 1 |
| minutos | 10,0 | 11,9 |

O que funcionou: 9 pedidos ao Jornalista, três já no primeiro minuto, em
paralelo, com o Editor buscando enquanto isso; nenhuma tentativa de WebFetch
barrada (o Editor seguiu o prompt); as portas fechadas seguiram a ordem (o RSS
da OpenAI como outra porta, depois a cópia do arquivo); o log de pesquisa saiu
com 45 páginas, cada uma com nota; a citação do post do Google veio literal
do resumo ao relatório, e o Editor a traduziu no roteiro, como sempre.

O que não veio: **o contexto do Editor não encolheu.** O relatório do
Jornalista, com um bloco por página, ocupa no Editor o que o resumo ocupava,
e o Jornalista é custo a mais (US$ 0,69). E **seis das onze fechadas são
429 do arquivo público**: Jornalistas em paralelo batem no archive.org ao
mesmo tempo. Uma amostra, num dia de web diferente: não decide nada sozinha.

Para os próximos ensaios, uma mudança por vez: relatório mais curto (só o que
pesa na decisão, sem fatos de página "nada na janela"), e o arquivo público
consultado um por vez.

**Decisão do autor (08/11): o Jornalista é arquitetura, não economia.** A
conta de onde vai o custo (aprendizados, "Separar em agentes não barateia
sozinho") mostrou que nem ele nem um Roteirista separado baixam o custo por
si: o Editor já recebia resumos, e a escrita acontece em poucas chamadas. O
valor está em cada agente ser especialista no seu papel, com um prompt que
melhora de versão em versão. Paralelismo não é requisito: o pipeline não tem
pressa.

### Jornalista 1.1 — um pedido por vez (ensaio de 04/11, rodado em 09/11)

Mesmo comando, mesmo estado, com a 1.1. A web é a de 09/11, um dia depois
dos outros ensaios. "Base" é o modo direto no mesmo dia, ensaiado em 08/11.

| | 1.1 | 1.0 | base |
|---|---|---|---|
| custo (US$) | 6,98 | 6,68 | 5,05 |
| Opus 5.5, Editor | 5,00 | 4,53 | 4,03 |
| cache escrito / lido do Editor | 305 mil / 10,0 M | 303 mil / 8,6 M | 203 mil / 7,4 M |
| Sonnet 5.5, Jornalista | 0,51 | 0,69 | — |
| Haiku 4.5, resumos e buscas | 1,46 | 1,46 | 1,02 |
| pedidos ao Jornalista | 6, um por vez | 9, em paralelo | — |
| páginas lidas / fechadas | 33 / 1 | 46 / 11 | 46 / — |
| buscas do Editor | 50 | 43 | 23 |
| o que a leitura pôs no Editor | relatórios, 52 mil caracteres | relatórios, 66 mil | resumos, 59 mil |
| o que as buscas puseram no Editor | 172 mil caracteres | 150 mil | 81 mil |
| maior contexto do Editor | 262 mil tokens | 247 mil | 221 mil |
| minutos | 12,5 | 10,0 | 11,2 |

A mudança da 1.1 fez o que devia. Cada pedido saiu depois do relatório do
anterior: 10:09 → 10:10, 10:11 → 10:12, e assim até o sexto. As portas
fechadas caíram de 11 para 1, um 403 da OpenAI, e não houve nenhum 429. O
tempo quase não mudou.

O custo não baixou, e agora se vê onde ele está:

- **O relatório não condensa.** O Jornalista devolve uns 1.600 caracteres por
  página lida, o tamanho do resumo do Haiku que o Editor recebia direto.
- **O Editor busca o dobro.** Sem poder abrir página, ele usa a busca como
  leitura: 50 buscas contra 23, e 172 mil caracteres de resultado contra 81
  mil. A frase "Enquanto espera, pode buscar na web", da própria 1.1,
  convida a isso.
- **Relatório que chega pela fila é cache escrito a mais.** Cada notificação
  entra no contexto como texto novo, e a escrita do Editor custa 2× a entrada
  (cache de 1 hora). Foram 305 mil tokens escritos contra 203 mil no modo
  direto.

As pautas foram XSA-523 do Xen (crédito à Anthropic), o relatório anual do
NCSC e as habilidades de química do Antigravity. Só o NCSC coincide com a
produção, mas a web é outra. O roteiro está em
`analysis/leitura/saida/roteiros-04-11/jornalista-1.1.md`.

Candidatos à 1.2, um de cada vez. O primeiro é o Editor esperar parado:
chamar o Jornalista em primeiro plano, com `run_in_background: false`, para
o relatório voltar como resultado da ferramenta, e tirar o "pode buscar
enquanto espera". Ataca as buscas e a escrita pela fila. O segundo é o
relatório mais curto. O Haiku 5.5 no resumidor vale com ou sem o
Jornalista, e é a mudança de maior efeito medida até aqui.

### Jornalista 1.2 — o Editor espera parado (ensaio de 04/11, rodado em 09/11)

O Editor pede com `run_in_background: false`, e um segundo hook
(`jornalista.py espera`) garante isso. Assim o relatório volta como resposta
da chamada, não por notificação. Saiu do prompt o "enquanto espera, pode
buscar na web". Antes, um teste com um subagente de brinquedo confirmou que o
CLI 2.1.283 respeita o campo, e que o hook vence o `true` pedido pelo modelo.

| | 1.2 | 1.1 | base |
|---|---|---|---|
| custo (US$) | **5,98** | 6,98 | 5,05 |
| Opus 5.5, Editor | **4,00** | 5,00 | 4,03 |
| chamadas do Editor | **39** | 59 | 51 |
| cache escrito / lido do Editor | 281 mil / 6,5 M | 305 mil / 10,0 M | 203 mil / 7,4 M |
| Sonnet 5.5, Jornalista | 0,53 | 0,51 | — |
| Haiku 4.5, resumos e buscas | 1,45 | 1,46 | 1,02 |
| buscas do Editor | 49 | 50 | 23 |
| o que as buscas puseram no Editor | 157 mil caracteres | 172 mil | 81 mil |
| o que a leitura pôs no Editor | relatórios, 53 mil | relatórios, 52 mil | resumos, 59 mil |
| páginas lidas / fechadas | 36 / 6, nenhum 429 | 33 / 1 | 46 / — |
| minutos | 13,6 | 12,5 | 11,2 |

A espera em primeiro plano tirou 20 chamadas do Editor, e o Opus voltou ao
custo do modo direto. O resto do custo a mais é o Jornalista (Sonnet, 0,53)
e as buscas, que continuaram em 49. Quem puxava as buscas não era a espera. O
Editor sem WebFetch descobre pela busca o que no modo direto descobria
abrindo as páginas de listagem, e só depois manda os endereços ao
Jornalista. Por isso a busca é o próximo alvo, e não o relatório: ela põe no
Editor três vezes mais texto que os relatórios.

Nos relatórios da 1.1, 20 dos 33 blocos de página eram de página fora da
janela ou sem data, e ocupavam 57% do texto. Encurtar esses blocos para uma
linha tiraria uns 25 mil caracteres do Editor. Ajuda, mas pesa menos que a
busca.

## Modelo pequeno no Haiku 5.5 — o corte de custo mais provável

O Haiku 4.5 resume as páginas e faz as buscas no modo direto (US$ 1,05 em
04/11). No Teste A, o Haiku 5.5 trouxe 80% dos números do Opus, contra 59% do
4.5, por um quarto do preço. Trocar é uma variável, `ANTHROPIC_DEFAULT_HAIKU_MODEL`,
que o `ensaio.sh` deixa passar; o vigia aceita o modelo pedido. Estimativa:
~US$ 0,40 no lugar de 1,05 (as buscas custam US$ 0,01 cada em qualquer
modelo). O risco medido é a troca de língua.

### Ensaio (08/11, dia 04/11, modo direto)

Dois ensaios do mesmo dia, um depois do outro, com a mesma web (a de 08/11):
o resumidor no Haiku 5.5 e a base, no Haiku 4.5 de sempre. A base saiu perto
da produção de 04/11 (5,05 contra 5,25), então a diferença é do resumidor.

| | Haiku 5.5 | base, Haiku 4.5 |
|---|---|---|
| custo (US$) | **3,75** (o CLI estimaria 7,71) | 5,05 |
| Opus 5.5, o Editor | 3,47 — cache lido 5,4 M | 4,03 — cache lido 7,4 M |
| modelo pequeno | **0,28** — 18 buscas | 1,02 — 23 buscas |
| chamadas do Editor / turnos | 38 / 77 | — / 101 |
| páginas lidas / fechadas | 31 / 2 | 46 / 3 |
| resumos: média por página | 2.091 caracteres, 44 números | 1.361 caracteres, 25 números |
| resumos em português | 0 de 29 | 0 de 43 |
| minutos | 9,7 | 11,2 |

- **A queda não é só do resumidor:** o Editor leu 15 páginas a menos e buscou
  menos. Os resumos do Haiku 5.5 trazem quase o dobro de números por página,
  e o volume total que entra no Editor ficou igual (61 mil contra 59 mil
  caracteres): menos páginas, cada uma com mais. É a explicação provável, mas
  é uma amostra; ensaios do mesmo dia já variaram uns 3% no custo, e aqui a
  diferença é de 26%.
- **Pautas:** duas das três iguais (o parecer do tribunal europeu e a marca
  d'água da Anthropic); a terceira trocou — escolha de pauta varia de ensaio
  para ensaio mesmo com o mesmo código.
- **O registro precisava da tabela própria:** o CLI estimaria US$ 7,71, com o
  Haiku 5.5 a preço de Opus. A conta refeita também esquecia o US$ 0,01 por
  busca; corrigido com teste antes, e a tabela agora bate até o centavo com a
  do CLI no Haiku 4.5.

Falta: o autor ler os dois roteiros de 04/11 lado a lado, e um segundo dia de
ensaio. Se confirmar, vai à produção como versão nova do Editor (o
`modelo_pequeno` da ficha), num dia sem outra mudança.

### Segundo dia (09/11, modo direto, contra a produção do mesmo dia)

Ensaio de 09/11 rodado na noite de 09/11. Partiu do mesmo commit da produção
das 05:00, com a web do mesmo dia: é a comparação mais próxima até aqui.

| | Haiku 5.5 | produção 09/11 |
|---|---|---|
| custo (US$) | **5,09** (o CLI estimaria 11,11) | 7,88 |
| Opus 5.5, o Editor | 4,73 — cache lido 9,2 M | 6,34 — cache lido 14,8 M |
| modelo pequeno | **0,36** | 1,54 |
| chamadas do Editor | 54 | 79 |
| páginas lidas / buscas | 62 / 17 | 71 / 40 |
| resumos: média por página | 1.840 caracteres | 1.130 caracteres |
| minutos | 13,5 | 15,7 |

- **De novo, o corte vem em duas partes.** O resumidor mais barato tira
  US$ 1,18. O Editor que buscou menos tira mais 1,61. A primeira parte é
  certa; a segunda apareceu nos dois dias, mas pode ser variação de execução.
- **Nenhuma pauta em comum com a produção.** O ensaio escolheu a
  investigação do conselho da NVIDIA (pelo comunicado oficial), a memória de
  agentes da Anthropic e o fim do AI Frontiers, contado por John Langford. Não
  achou o RSA do DeepMind, a manchete da produção. Viu a Hacktron e a
  descartou: a página da OpenAI deu 403, e a cópia do arquivo não abriu. Com
  17 buscas em vez de 40, achou menos. É o lado ruim de buscar menos, e
  precisa entrar na conta junto com o custo.

**Como testar na semana sem arriscar o episódio.** A produção segue como está.
O `scripts/ensaio.sh` roda dias passados com `JORNALISTA=1`, numa cópia fora do
repositório e sem S3, e compara com o episódio publicado daquele dia: pautas
escolhidas, fontes lidas, portas fechadas, custo, tempo e avisos. Dois ou três
ensaios, de ~US$ 5 e 15 minutos cada.

## Fora deste plano, a decidir à parte

- **Atualizar o CLI** (2.1.283): versões novas conhecem o Haiku 5.5 e o Sonnet
  5.5 (apelidos e preço), mas trazem outras mudanças. Testar por ensaio.
- **Modelo pequeno no Haiku 5.5**: passou a ser parte do plano (seção acima).
