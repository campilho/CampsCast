# Verificação v1 — resumo (14/11/2026, três rodadas)

Os 14 episódios novos (41 a 54, de 26/10 a 13/11) estão conferidos, mas por
dois verificadores diferentes, e as contas ficam separadas:

| Rodada | O quê | Subagentes | Arquivos |
|---|---|---|---|
| etapa 1 | 8 episódios: 04, 05, 06, 09, 10, 11, 12 e 13/11; calibração (35 e 38) | Sonnet | `AAAA-MM-DD.md`, `afirmacoes.jsonl` sem `verificador`, [calibracao.md](calibracao.md) |
| etapa 2a | calibração refeita (35 e 38) | Opus | [opus/](opus/calibracao.md) |
| etapa 2b | 6 episódios: 26, 27, 28, 29 e 30/10 e 03/11 | Opus | `AAAA-MM-DD.md`, linhas com `"verificador": "opus"` no `afirmacoes.jsonl` |

**Que modelos rodaram de fato.** Pelo `modelUsage` das sessões, o apelido
"sonnet" rodou o `claude-sonnet-5` e o "opus" rodou o `claude-opus-5`, não as
versões 5.5. O coordenador das três rodadas foi o Opus 5.5. O roteirista dos
episódios 27 a 40 da linha de base era o Opus 5.5. A linha de base não registra
qual modelo conferiu.

## Calibração: quanto cada verificador pega

Episódios 35 e 38: 47 afirmações e 7 erros na linha de base, conferidos às cegas.

| | Mesma situação da linha de base | Erros marcados | Dos 7 da linha de base, pegou |
|---|---|---|---|
| Sonnet (etapa 1) | 39 de 47 | 1 | **1** |
| Opus (etapa 2a) | 39 de 47 | 8 | **5** |

A versão anterior deste resumo dizia que o Sonnet "deixou passar 5 dos 7".
Está errado: ele pegou 1 e deixou passar 6. O Sonnet é brando, a rubrica não:
com o Opus, ela julga com a mesma dureza da linha de base (8 erros contra 7,
5 em comum), com uma margem de cerca de ±2 erros em 47 afirmações.

## Episódios 41 a 46, no Opus (6 episódios, 188 afirmações)

| Situação | n |
|---|---|
| confirmado | 157 |
| impreciso | 20 (todos leves) |
| errado | 0 |
| nao_verificavel | 9 |
| inacessivel | 2 |

**Taxa de erro: 20 / 177 verificáveis = 11,3%** (IC 95% de Wilson: 7,4% a 16,8%).

| Episódio | Afirmações | Erros / verificáveis |
|---|---|---|
| 41 (26/10) | 37 | 5 / 34 |
| 42 (27/10) | 32 | 3 / 29 |
| 43 (28/10) | 29 | 3 / 29 |
| 44 (29/10) | 31 | 2 / 30 |
| 45 (30/10) | 29 | 4 / 27 |
| 46 (03/11) | 30 | 3 / 28 |

- **Memória do programa:** 3 / 44 = 6,8% (IC 2,3% a 18,2%). São três casos:
  em 27/10, "o caso que eu contei em setembro e de novo no dia treze" (o 13/10
  conta outros casos), e "em nove de setembro, a OpenAI disse" (publicou em
  08/09; regra 6); em 30/10, "eu contei dois relatórios da própria OpenAI"
  (em 22/10 era um relatório com dois casos; regra 7).
- **Sem a memória:** 17 / 133 = 12,8% (IC 8,1% a 19,5%).
- **Por regra:** 8 (paráfrase que acrescenta) decidiu 10 dos 20; a 7 decidiu 4;
  a 9, 3; e a 5, a 6 e a 12, um cada. Um ficou sem regra. O padrão se repete:
  o roteiro tira o "appeared", o "aim", o "could" e o "as many as" da fonte, ou
  troca a medida por outra próxima ("procurou o repositório" virou "começava o
  ataque"; "tempo de revisão humana" virou o tempo do Claude).
- Um dos 20 só é erro pela letra da regra 5: "noventa por cento" por 90,5%, sem
  marcador. Sem ele: 19 / 177 = 10,7% (IC 7,0% a 16,2%).

### Comparação com a linha de base (episódios 27 a 40)

A linha de base achou 19 erros em 321 verificáveis: 5,9% (IC 3,8% a 9,1%).
**Nos episódios 41 a 46, a taxa subiu para 11,3%.** Os intervalos quase não se
cruzam (7,4% a 9,1%), e o teste de duas proporções dá z ≈ 2,1 (p ≈ 0,03).
Tirando o caso da regra 5, dá z ≈ 1,9 (p ≈ 0,05). A calibração diz que a
comparação vale: o Opus marcou 8 onde a linha de base marcou 7. Descontando
essa diferença, a taxa ainda fica perto de 10%. A subida é real, mas está no
limite da significância. Nenhum erro é grave, e todos mudam um detalhe, não a
pauta. São seis episódios, de uma semana e meia só.

## Episódios 47 a 54, no Sonnet (8 episódios, 249 afirmações)

| Situação | n |
|---|---|
| confirmado | 239 |
| impreciso | 5 (todos leves) |
| errado | 0 |
| nao_verificavel | 4 |
| inacessivel | 1 |

**Taxa de erro: 5 / 244 = 2,0%** (IC 0,9% a 4,7%). Memória do programa:
1 / 28 = 3,6% (IC 0,6% a 17,7%). Faltam no jsonl as afirmações de memória de
04 e 06/11, que só estão no `.md`.

**Não dá para comparar com a linha de base nem com o Opus.** Na calibração, o
Sonnet pegou 1 dos 7 erros. Os 2,0% são um piso, não uma taxa. O
erro de 09/11 é este: "cibernético e biológico" foi acrescentado ao que se
disse em 13/10. Os `impreciso` de 04 e 06/11 foram reconferidos pelo
coordenador.

## Por onde se leu

| Via | Opus (41–46) | Sonnet (47–54, jsonl) | Calibração Sonnet |
|---|---|---|---|
| fonte | 90 | 107 | 27 |
| outra_porta | 15 | 0 | — |
| imprensa | 42 | 28 | 16 |
| repositorio | 41 | 51 | 4 |
| arquivo | 0 | 1 (inacessível) | — |

O `web.archive.org` não abre pelo WebFetch. Nenhuma afirmação foi lida pelo
arquivo, mesmo nos casos em que o subagente achou uma cópia do dia pela API
`wayback/available`.

### Pautas da OpenAI

- **26/10, retomada do treino** (`securing-our-frontier-model-training-environment`):
  openai.com deu 403, e as outras portas não têm o texto. Lida pela imprensa
  (Let's Data Science, AI Weekly, GadgetScout). O "sistema que para o treino
  sozinho" ficou `inacessivel`. A data de 03/10 saiu do alignment.openai.com.
- **27/10, ETH, Kakeya e QCD** (`building-scientific-understanding…`): deu 403
  e não está em outra porta. Lida pela imprensa (Let's Data Science,
  Interesting Engineering, Tech Insider, StudyFinds, Wikipedia).
- **27/10, GPT-6.1 Terra:** lida em community.openai.com, a fonte citada. O
  preço saiu do developers.openai.com (`outra_porta`).
- **30/10, regra do desligamento** (`how-we-detect-frontier-model-misalignment`):
  deu 403. Lida no alignment.openai.com e no model-spec.openai.com, nas versões
  de 29/10 e 18/08 (`outra_porta`).
- **03/11, GPT-Rosalind-6:** lida em deploymentsafety.openai.com, a fonte citada.
- **03/11, sprint de segurança** (`preparing-our-next-security-sprint…`): deu
  403. Data, parceria e tipos de bônus saíram do RSS oficial
  (`openai.com/news/rss.xml`, `outra_porta`). Valores e teto só pela imprensa
  (AI TL;DR, Interesting Engineering).
- Na rodada do Sonnet: 04/11, lida pela fonte (alignment.openai.com); 05/11, só
  pela imprensa; 06/11, pela fonte (deploymentsafety); 09/11, pelos posts da
  Hacktron; 10/11, pela imprensa e pela METR; 12/11, em community.openai.com.

Das seis pautas da OpenAI destes seis episódios, duas se leram só pela
imprensa e uma em parte por ela. A razão é sempre a mesma: o 403 do openai.com,
sem cópia em outra porta. O RSS oficial (`openai.com/news/rss.xml`) abriu, e vale entrar nas
`outras_portas` do `sources.yaml` para datas e títulos.

## Erros graves

Nenhum, nas três rodadas.

## Método e limites

- Um subagente no Opus (`claude-opus-5`) por episódio, com a rubrica inteira.
  O coordenador reabriu a fonte de todos os 22 `impreciso` e derrubou dois,
  ambos de 03/11. No primeiro, a página diz "~70-95x" no próprio resumo. No
  segundo, a ficha diz, sem ressalva, "still refusing requests for biological
  weaponization". Os outros 20 se sustentaram.
- Os `confirmado` não foram reconferidos. Na calibração, o Opus deixou passar
  2 dos 7 erros, e por isso a taxa de 11,3% também pode estar baixa.
- Os subagentes não tiveram Bash e escreveram o jsonl à mão. Depois, o
  coordenador validou as 188 linhas com `jq`: todas com as 16 chaves.
- Regra 10: o archive.org fechado transforma placar que muda em
  `nao_verificavel` (6 dos 9). Regra 5: ao pé da letra, ela pune arredondamento
  de meio ponto sem marcador, o que ninguém aplicou na linha de base. As duas
  são candidatas a uma v2.
- O S-1 da Anthropic (mais de 10 MB) não abre pelo WebFetch. A pauta de 27/10
  foi conferida pela imprensa e pelo FWP da própria Anthropic na SEC.
- A etapa 2b custou cerca de US$ 13 do orçamento da sessão, incluindo a
  reconferência e a cópia dos jsonl. Dá mais ou menos US$ 2 por episódio.
