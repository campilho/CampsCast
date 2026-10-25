# Linha de base da verificação de fatos — episódios 1 a 40

Conferência dos 40 episódios publicados de 24/08 a 23/10/2026, passo V1 do
[ADR 0010](../../docs/decisions/0010-redacao-com-varios-agentes.md), feita em
duas rodadas no mesmo dia, 25/10/2026, em sessões na nuvem:

- **Primeira rodada** (`prompts/verificador.md`): escolheu as afirmações e
  conferiu as 949. A rede só abria meia dúzia de domínios, e 513 ficaram
  `inacessivel`.
- **Segunda rodada** (`prompts/verificador-reconferencia.md`): reconferiu só
  essas 513, com a rede aberta. São as linhas com `"rodada": 2` em
  [`afirmacoes.jsonl`](afirmacoes.jsonl); nas tabelas de cada episódio,
  `AAAA-MM-DD.md`, a nota começa com "Rodada 2:".

> **Leia isto antes dos números.** Com a rede aberta, `openai.com` continuou
> barrando o WebFetch com 403, em inglês e em português. Das 71 afirmações
> presas lá, 47 ganharam veredito pela imprensa, 17 delas pela Unite.AI, que
> publica texto gerado por IA. Na segunda rodada inteira, 29% das afirmações
> (148 de 513) foram conferidas na imprensa, não na fonte primária.

## Totais

| Situação | Afirmações | % |
|---|---|---|
| `confirmado` | 833 | 87,8% |
| `impreciso` | 63 | 6,6% |
| `errado` | 8 | 0,8% |
| `nao_verificavel` | 42 | 4,4% |
| `inacessivel` | 3 | 0,3% |
| **Total** | **949** | |

**Taxa de erro**, (`errado` + `impreciso`) sobre o verificável
(`confirmado` + `impreciso` + `errado` = 904): **71 de 904 = 7,9%**
(IC 95% de Wilson: 6,3–9,8%). Contando só `errado`: 8 de 904 = 0,9%
(0,4–1,7%). **Nenhum erro grave**: os 71 são `leve`.

## Por agente

| Recorte | Afirmações | confirmado | impreciso | errado | nao_verif. | inacessível | Verificáveis | Taxa de erro | IC 95% |
|---|---|---|---|---|---|---|---|---|---|
| Episódios 1–21 (Claude Opus 5) | 496 | 428 | 34 | 5 | 26 | 3 | 467 | **8,4%** | 6,2–11,2% |
| Episódios 22–40 (Claude Opus 5.5) | 453 | 405 | 29 | 3 | 16 | 0 | 437 | **7,3%** | 5,2–10,2% |

Os intervalos se sobrepõem quase inteiros. Separando memória do programa e
fatos de fora:

| Recorte | Verificáveis | Erros | Taxa | IC 95% |
|---|---|---|---|---|
| Memória do programa, Opus 5 | 40 | 12 | **30,0%** | 18,1–45,4% |
| Memória do programa, Opus 5.5 | 58 | 1 | **1,7%** | 0,3–9,1% |
| Fatos de fora, Opus 5 | 427 | 27 | 6,3% | 4,4–9,0% |
| Fatos de fora, Opus 5.5 | 379 | 31 | 8,2% | 5,8–11,4% |
| Fonte em anthropic.com/claude.com, Opus 5 | 97 | 11 | 11,3% | 6,5–19,2% |
| Fonte em anthropic.com/claude.com, Opus 5.5 | 121 | 17 | 14,0% | 9,0–21,4% |
| Fatos de fora sem a Anthropic, Opus 5 | 330 | 16 | 4,8% | 3,0–7,7% |
| Fatos de fora sem a Anthropic, Opus 5.5 | 258 | 14 | 5,4% | 3,3–8,9% |

- **A memória do programa melhorou de verdade.** O Opus 5 errou 12 de 40 vezes
  ao dizer o que um episódio anterior tinha contado: dia trocado, coisa que nunca
  foi ao ar, frase do log tratada como dita no ar. Depois do episódio 22 foi uma
  vez em 58. Mas a troca de modelo (22, em 28/09) e a memória em camadas
  (ADR 0008, em 03/10, a partir do 27) caíram quase juntas. Nos episódios 22 a
  26, só com o modelo novo, foi 1 erro em 13 (IC 1,4–33,3%); do 27 ao 40, 0 em
  45. A amostra não separa as duas causas. A segunda rodada não mexeu nesse
  recorte: nenhuma afirmação da memória estava inacessível.
- **Nos fatos de fora não há melhora.** Com quase 400 afirmações por agente, o
  Opus 5.5 erra tanto quanto o Opus 5. A estimativa pontual dele é até pior
  (8,2% contra 6,3%), dentro do ruído.
- **As fontes da Anthropic concentram os erros dos dois agentes**: 11–14%,
  contra 5% no resto. Veja a seção seguinte antes de tirar conclusão disso.

## Primeira e segunda rodada

- **O que virou verificável.** Das 513 afirmações inacessíveis, 485 (94,5%)
  ganharam veredito: 460 `confirmado`, 25 `impreciso` (todos leves) e nenhum
  `errado`. Outras 25 ficaram `nao_verificavel` e 3 seguem `inacessivel`.
- **A taxa de erro caiu de 11,0% para 7,9%.** Antes eram 46 de 419 (IC
  8,3–14,3%); com as duas rodadas, 71 de 904 (6,3–9,8%). Só nas 485 da segunda
  rodada, 25 erros, ou 5,2% (3,5–7,5%). O `errado` caiu de 1,9% para 0,9%.
- **A diferença entre o Opus 5 e o Opus 5.5 nos fatos de fora não apareceu.**
  Na segunda rodada, o Opus 5 errou 11 de 251 (4,4%) e o Opus 5.5, 14 de 234
  (6,0%). Somadas as rodadas, 6,3% contra 8,2%. A única melhora mensurável
  continua sendo a memória do programa.
- **Por que a segunda rodada achou menos erro.** As afirmações novas erram
  menos que as de fonte na Anthropic: 5,7% (3,7–8,7%) com veredito em fonte
  primária, contra 12,3% (8,7–17,2%) nas fontes primárias da primeira rodada.
  Há três explicações, e esta verificação não separa uma da outra:
  1. **Verificadores diferentes.** O briefing da segunda rodada escreveu
     critérios que a primeira deixava implícitos: não dizer não é desmentir,
     conta do roteiro que bate é `confirmado`, placar ao vivo que mudou é
     `nao_verificavel`. Isso pode ter deixado a segunda rodada mais branda com
     o `impreciso`.
  2. **Imprensa.** 136 vereditos verificáveis da segunda rodada vêm da
     imprensa, que muitas vezes é de onde o roteiro tirou a frase. Conferir o
     roteiro contra a própria paráfrase é mais fraco que conferir contra o post.
     A diferença medida é pequena: 3,7% (1,6–8,3%) na imprensa, 5,7% na fonte
     primária.
  3. **Assunto.** Nos posts da Anthropic, o roteiro desce a detalhe fino,
     como preço de cache, categoria de corte e nome de variante. É onde o
     `impreciso` aparece.

### Pistas que a primeira rodada deixou

- Comunicado de Iowa (ep. 34): as quatro afirmações foram confirmadas no
  comunicado e na petição de 14/10.
- Prazo de 60 dias da ordem do DHS (ep. 38): `impreciso leve`. O prazo contava
  da emissão, em 24/07, e tinha vencido um mês antes do episódio.
- "Mais de cinquenta idiomas" do Voxtral (ep. 38): `confirmado`. É o
  enquadramento do post, embora o modelo de fala cubra 35 idiomas.
- "Todas as versões desde a 5.4" do PHP (ep. 39): ficou de fora, porque a
  primeira rodada já tinha dado `nao_verificavel`, não `inacessivel`.

## Erros graves

Nenhum, nas duas rodadas. A segunda não achou nenhum `errado`, então os oito
são os da primeira, todos leves:

- 35, pauta 2: "Ela só pode exigir cortes em categorias definidas antes: dado de cliente, informação protegida por sigilo jurídico e detalhes da arquitetura dos modelos". Essas são as categorias que os funcionários não repassam à METR; a de corte citada é "reproducing confidential IP". A página tem nota de atualização de 16/10, mesmo dia do episódio.
- 24, pauta 2: "a leitura de cache caiu para dez centavos, metade do que cobram o Sonnet e o Sol anterior". O Sonnet 5.5 já cobra US$ 0,10; os vinte centavos são do Sonnet 5.
- 23, pauta 1: "a mesma tabela do GPT seis Sol [...] inclusive os vinte centavos da leitura de cache". Mesmo erro, um dia antes: o Sonnet 5.5 cobra US$ 0,10.
- 20, pauta 2 (memória): "Anteontem eu contei aqui que o Claude Opus cinco ponto cinco iguala ou supera a capacidade biológica do modelo anterior, e que o acesso passa por credenciamento". Nenhum roteiro do acervo contou isso.
- 14, pauta 2: "o Kimi K três [...] fica atrás do Sonnet cinco". A página põe os modelos de peso aberto entre o Sonnet e o Mythos; o K3 fica acima do Sonnet em entrega de carga e no nível dele no resto.
- 14, pauta 2 (memória): "eu disse no ar que [armas convencionais] tinha ficado de fora por falta de espaço". A frase está no log de pesquisa de 11/09, não no roteiro.
- 11, pauta 1: "É o terceiro de uma série que começou em março do ano passado". O relatório cita três anteriores (março, agosto e novembro de 2025): é o quarto.
- 9, pauta 2 (memória): "Na quarta passada [...] eu mencionei uma trava": a restrição anti-destilação. Nenhum roteiro de 02 a 04/09 a menciona.

Dos 63 `impreciso`, os padrões que se repetem nas duas rodadas:

- data trocada: data de publicação tomada pela data do fato, fuso trocado
  (a coletiva de Albanese em Nova York foi na quarta, não na quinta de
  Canberra), prazo dado como aberto depois de vencido, um dia de diferença na
  memória do programa;
- parte pelo todo, ou contagem: "um que transcreve", quando são três; "os 51
  vereadores", quando foram uns 40; 53 "imagens", quando são 53 ocorrências;
- paráfrase que acrescenta: "a Anthropic editou", onde a METR diz que ela
  "teve a oportunidade de editar"; "as fontes", onde a Reuters tem uma só;
- modal ou novidade mudada: "deve", onde a fonte diz "can"; a China
  "anunciou" na ONU as 5.000 vagas que Xi já tinha lançado em julho;
- cargo ou papel aproximado: Kavukcuoglu "da arquitetura do DeepMind", quando
  é arquiteto-chefe de IA do Google inteiro;
- número arredondado sem aviso: 30 por 31.

## Domínios que não abriram

Na primeira rodada, 151 domínios falharam, 253 vezes por `ENOTFOUND`: a
política de rede da sessão só deixava passar a Anthropic, o GitHub e mais
quatro. Na segunda, a rede estava aberta, e o que falhou foi bloqueio do site
ou da ferramenta. A coluna "afirmações" conta as notas da segunda rodada que
citam o bloqueio. Quase todas acharam fonte alternativa.

| Domínio | Bloqueio | Afirmações | O que se fez |
|---|---|---|---|
| openai.com | 403 em toda página `/index/`, também em `pt-BR` | 77 | RSS oficial para datas; developers, alignment e community.openai.com, openaifoundation.org; imprensa |
| press.un.org | a página não carrega o texto | 8 | transcrição automática da ONU e UN News; 1 segue `inacessivel` |
| wsj.com | não aberto | 8 | citação literal no blog de Simon Willison e outra imprensa; 2 `nao_verificavel` |
| ifm.ai, mbzuai.ac.ae | 403 | 5 | Hugging Face e imprensa |
| x.com | 403, ou não aberto | 4 | post embutido em matéria; imprensa |
| axios.com | 403 | 3 | texto da Axios republicado no Yahoo Finance; The Next Web |
| help.openai.com | 403 | 2 | imprensa |
| cnbc.com | 403, também AMP | 1 | Anadolu, sem ler a atribuição à CNBC |
| politico.com, theguardian.com, web.archive.org | bloqueado pela ferramenta | 2 | imprensa |
| eur-lex.europa.eu | página vazia para o WebFetch | 1 | reprodução literal do AI Act pelo Future of Life Institute |
| humain.com, pif.gov.sa, alarabiya.net, huaweicentral.com, newsbytesapp.com | 403 | 3 | Argaam, Jon Peddie; 2 `nao_verificavel` |
| itv.com | 503 | 1 | Anadolu |

As três que seguem `inacessivel`: no episódio 3, o "pensada primeiro para
celular" e a projeção de um trilhão de reais, que só o post da OpenAI no
Brasil poderia confirmar; no episódio 20, as "seis reuniões" do Conselho de
Segurança, que só a nota de imprensa da ONU traz.

## O que o orquestrador corrigiu

Cada `errado` e cada `impreciso` foi reaberto pelo orquestrador antes de
aceito, nas duas rodadas.

**Primeira rodada.** Além dos erros, uma amostra de confirmados foi
reconferida. As mudanças:

- **Episódio 38:** a afirmação sobre os especialistas no post do veneno de
  escorpião voltou de `impreciso` para `confirmado`. O verificador tinha lido mal
  a página.
- **Episódio 37:** 22 confirmações tinham vindo só do resumo da WebSearch, sem
  abrir a página. Viraram `inacessivel`, com o veredito anotado como pista.
- **Episódio 18:** "dos nove membros, só um assinou a carta" passou para
  `nao_verificavel`: a TechCrunch e o post de Tao divergem sobre quem assinou.
- **Episódios 15 e 21:** quatro afirmações que só um resumo ou catálogo de
  terceiros sustentava viraram `inacessivel`.

**Segunda rodada.** Os ajustes:

- **Episódio 16:** o único `errado` dos subagentes virou `confirmado`. Um
  veículo tratava Harvey e Legora como clientes da API, e o subagente tomou
  isso como desmentido. A lista de plugins da Artificial Lawyer os inclui.
- **Episódio 8:** "foi ele quem conduziu o projeto" passou de `impreciso` para
  `nao_verificavel`. A fonte não diz quem conduziu, e não dizer não é desmentir.
- **Episódio 29:** o dia em que a OpenAI avisou o governo de Nova Gales do Sul
  passou de `confirmado` para `nao_verificavel`, pelo mesmo critério do
  episódio 18: a ABC diz quinta, a AAP diz sexta.
- **Episódio 34:** a multa de 3% do AI Act passou de `nao_verificavel` para
  `confirmado`. O subagente esgotou a cota antes de abrir o art. 101, e o
  orquestrador o abriu.

## Método e limites

- **Primeira rodada.** Um subagente por episódio, cinco em paralelo, do 40 ao
  1, com o mesmo briefing. Até 8 afirmações por pauta, priorizando número, data
  e citação. A memória do programa foi conferida contra os roteiros do
  repositório.
- **Segunda rodada.** As 513 afirmações agrupadas pelas 147 URLs que a
  primeira tentou abrir, em 16 lotes por domínio. Cinco subagentes em paralelo,
  cada URL aberta uma vez para todas as afirmações que a citam. As pistas da
  primeira rodada foram passadas como pista, não como veredito. Em 109 casos a
  URL tentada não era a fonte da pauta; a orientação foi abrir também a fonte
  da pauta quando ela fosse mais primária.
- **WebFetch.** A evidência sai de páginas abertas pelo WebFetch, que passa o
  texto por um modelo pequeno e limita a citação literal a cerca de 125
  caracteres. Os trechos são literais, mas curtos. O modelo pequeno às vezes
  erra a leitura, e todo `errado` e `impreciso` foi reperguntado.
- **Fonte não citada.** Na segunda rodada, 246 das 460 confirmações (53,5%)
  vêm de uma página que o roteiro não citou: outra página oficial, a imprensa ou
  a fonte primária que a imprensa repercutia.
- **Imprensa e texto de IA.** 148 vereditos da segunda rodada vêm da imprensa,
  e a nota diz qual veículo. 17 se apoiam na Unite.AI, que assina textos
  escritos por agente e revisados pela redação. Uma confirmação só por ela é a
  mais fraca do acervo.
- **Placares ao vivo.** Artificial Analysis, Terminal-Bench e tabelas de preço
  foram lidos em 25/10, semanas depois dos episódios. Onde o número de hoje
  difere do dito no ar, a nota diz de onde veio o valor do dia, ou a afirmação
  ficou `nao_verificavel`.
- **Cópias no GitHub.** Na primeira rodada, para imprensa e posts bloqueados,
  contou como fonte a cópia literal em issue ou gist que traz link e data do
  original (94 afirmações, 89 confirmadas). Nenhum veredito da segunda saiu de
  cópia no GitHub.
- **Seleção.** Até 8 afirmações por pauta, escolhidas pelo verificador, não
  sorteadas. A taxa vale para fatos com número, data ou citação, não para cada
  frase do roteiro. Fontes abertas que divergem viraram `nao_verificavel`.
- **Gravidade é julgamento.** Um único verificador por afirmação, sem segunda
  opinião sobre `leve` e `grave`.
- **Ramos.** A primeira rodada pedia `claude/verificador-linha-de-base` e foi
  para `claude/eager-cerf-xvyd87`. A segunda foi para
  `claude/verificador-reconferencia-prompts-raky57`. Nada foi para a `main`, e
  nada fora de `verificacao/linha-de-base/` mudou.
