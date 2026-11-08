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

**Como testar na semana sem arriscar o episódio.** A produção segue como está.
O `scripts/ensaio.sh` roda dias passados com `JORNALISTA=1`, numa cópia fora do
repositório e sem S3, e compara com o episódio publicado daquele dia: pautas
escolhidas, fontes lidas, portas fechadas, custo, tempo e avisos. Dois ou três
ensaios, de ~US$ 5 e 15 minutos cada.

## Fora deste plano, a decidir à parte

- **Atualizar o CLI** (2.1.283): versões novas conhecem o Haiku 5.5 e o Sonnet
  5.5 (apelidos e preço), mas trazem outras mudanças. Testar por ensaio.
- **Modelo pequeno no Haiku 5.5** (`ANTHROPIC_DEFAULT_HAIKU_MODEL`): o resumo
  das páginas e as buscas ficam ~10× mais baratos (cerca de US$ 0,6 por
  episódio). Entra no Teste A como o braço Haiku 5.5.
