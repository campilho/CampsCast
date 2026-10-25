# Linha de base da verificação de fatos — episódios 1 a 40

Conferência feita em 25/10/2026, numa sessão na nuvem, sobre os 40 episódios
publicados de 24/08 a 23/10/2026 (`prompts/verificador.md`, passo V1 do
[ADR 0010](../../docs/decisions/0010-redacao-com-varios-agentes.md)). Uma linha
por afirmação em [`afirmacoes.jsonl`](afirmacoes.jsonl); a tabela de cada
episódio em `AAAA-MM-DD.md`.

> **Leia isto antes dos números.** A rede desta sessão só abriu `anthropic.com`,
> `claude.com`, `github.com`, `raw.githubusercontent.com`, `pypi.org` e
> `blog.modelcontextprotocol.io`. Todo o resto deu `ENOTFOUND`: openai.com,
> Google, NVIDIA, Mistral, Hugging Face, imprensa, sites de governo. Por isso
> **54% das afirmações ficaram `inacessivel`**. A taxa abaixo mede sobretudo
> fatos com fonte na Anthropic e a memória do programa, não o roteiro inteiro.

## Totais

| Situação | Afirmações | % |
|---|---|---|
| `confirmado` | 373 | 39,3% |
| `impreciso` | 38 | 4,0% |
| `errado` | 8 | 0,8% |
| `nao_verificavel` | 17 | 1,8% |
| `inacessivel` | 513 | 54,1% |
| **Total** | **949** | |

**Taxa de erro**, (`errado` + `impreciso`) sobre o verificável
(`confirmado` + `impreciso` + `errado` = 419): **46 de 419 = 11,0%**
(IC 95% de Wilson: 8,3–14,3%). Contando só `errado`: 8 de 419 = 1,9%
(1,0–3,7%). **Nenhum erro grave**: todos os 46 são `leve`, nenhum muda o
sentido da pauta.

## Por agente

| Recorte | Afirmações | confirmado | impreciso | errado | nao_verif. | inacessível | Verificáveis | Taxa de erro | IC 95% |
|---|---|---|---|---|---|---|---|---|---|
| Episódios 1–21 (Claude Opus 5) | 496 | 188 | 23 | 5 | 13 | 267 | 216 | **13,0%** | 9,1–18,1% |
| Episódios 22–40 (Claude Opus 5.5) | 453 | 185 | 15 | 3 | 4 | 246 | 203 | **8,9%** | 5,7–13,6% |

Os intervalos se sobrepõem. A diferença inteira vem da memória do programa,
não dos fatos de fora:

| Recorte | Verificáveis | Erros | Taxa | IC 95% |
|---|---|---|---|---|
| Memória do programa, Opus 5 | 40 | 12 | **30,0%** | 18,1–45,4% |
| Memória do programa, Opus 5.5 | 58 | 1 | **1,7%** | 0,3–9,1% |
| Fatos de fora, Opus 5 | 176 | 16 | 9,1% | 5,7–14,3% |
| Fatos de fora, Opus 5.5 | 145 | 17 | 11,7% | 7,5–18,0% |
| Só fonte em anthropic.com/claude.com, Opus 5 | 97 | 11 | 11,3% | 6,5–19,2% |
| Só fonte em anthropic.com/claude.com, Opus 5.5 | 121 | 17 | 14,0% | 9,0–21,4% |

- **A memória do programa melhorou de verdade.** O Opus 5 errou 12 de 40 vezes
  ao dizer o que um episódio anterior tinha contado: dia trocado, coisa que nunca
  foi ao ar, frase do log tratada como dita no ar. Depois do episódio 22 foi uma
  vez em 58. Mas a troca de modelo (22, em 28/09) e a memória em camadas
  (ADR 0008, em 03/10, a partir do 27) caíram quase juntas. Nos episódios 22 a
  26, só com o modelo novo, foi 1 erro em 13 (IC 1,4–33,3%); do 27 ao 40, 0 em
  45. A amostra não separa as duas causas.
- **Nos fatos de fora não há melhora mensurável.** No único recorte que a rede
  não enviesou, as fontes da Anthropic, o Opus 5.5 erra tanto quanto o Opus 5.

## Erros graves

Nenhum. Para registro, os oito `errado`, todos leves:

- 35, pauta 2: "Ela só pode exigir cortes em categorias definidas antes: dado de cliente, informação protegida por sigilo jurídico e detalhes da arquitetura dos modelos". Essas são as categorias que os funcionários não repassam à METR; a de corte citada é "reproducing confidential IP". A página tem nota de atualização de 16/10, mesmo dia do episódio.
- 24, pauta 2: "a leitura de cache caiu para dez centavos, metade do que cobram o Sonnet e o Sol anterior". O Sonnet 5.5 já cobra US$ 0,10; os vinte centavos são do Sonnet 5.
- 23, pauta 1: "a mesma tabela do GPT seis Sol [...] inclusive os vinte centavos da leitura de cache". Mesmo erro, um dia antes: o Sonnet 5.5 cobra US$ 0,10.
- 20, pauta 2 (memória): "Anteontem eu contei aqui que o Claude Opus cinco ponto cinco iguala ou supera a capacidade biológica do modelo anterior, e que o acesso passa por credenciamento". Nenhum roteiro do acervo contou isso.
- 14, pauta 2: "o Kimi K três [...] fica atrás do Sonnet cinco". A página põe os modelos de peso aberto entre o Sonnet e o Mythos; o K3 fica acima do Sonnet em entrega de carga e no nível dele no resto.
- 14, pauta 2 (memória): "eu disse no ar que [armas convencionais] tinha ficado de fora por falta de espaço". A frase está no log de pesquisa de 11/09, não no roteiro.
- 11, pauta 1: "É o terceiro de uma série que começou em março do ano passado". O relatório cita três anteriores (março, agosto e novembro de 2025): é o quarto.
- 9, pauta 2 (memória): "Na quarta passada [...] eu mencionei uma trava": a restrição anti-destilação. Nenhum roteiro de 02 a 04/09 a menciona.

Dos 38 `impreciso`, os padrões que se repetem:

- data trocada, em geral data de publicação tomada pela data do fato, ou um dia de diferença na memória do programa (12 casos);
- singular por plural, ou uma parte pelo todo: "um físico", que foram dois; um bilhão "das duas", quando é de cada uma;
- modal mudado: "deve", onde a fonte diz "can"; "foi doada", onde diz "will be donated";
- número arredondado sem aviso: 30 por 31.

## Domínios que não abriram

151 domínios distintos falharam, em 268 tentativas registradas: 253 por
`ENOTFOUND` (política de rede da sessão), 4 por timeout, 4 por 404, 1 por 403
e 6 por outras causas. A coluna "afirmações" conta as que ficaram
`inacessivel` tendo aquele domínio como URL conferida.

| Domínio | URLs que falharam | Episódios | Afirmações que ficaram inacessíveis | Erro |
|---|---|---|---|---|
| openai.com | 21 | 18 | 71 | ENOTFOUND |
| artificialanalysis.ai | 15 | 13 | 27 | ENOTFOUND |
| cloud.google.com | 8 | 3 | 6 | timeout 4, outro 4 |
| blog.google | 7 | 5 | 26 | ENOTFOUND |
| blogs.nvidia.com | 6 | 5 | 29 | ENOTFOUND |
| alignment.openai.com | 6 | 4 | 11 | ENOTFOUND |
| mistral.ai | 5 | 4 | 21 | ENOTFOUND |
| developers.openai.com | 5 | 5 | 12 | ENOTFOUND |
| huggingface.co | 5 | 5 | 10 | ENOTFOUND |
| axios.com | 4 | 3 | 9 | ENOTFOUND |
| techcrunch.com | 4 | 4 | 8 | ENOTFOUND |
| cisa.gov | 4 | 4 | 7 | ENOTFOUND |
| github.com | 4 | 3 | 4 | 404 |
| aws.amazon.com | 4 | 4 | 3 | ENOTFOUND |
| securityweek.com | 4 | 2 | 1 | ENOTFOUND |
| community.openai.com | 3 | 3 | 17 | ENOTFOUND |
| deepmind.google | 3 | 3 | 13 | ENOTFOUND |
| about.fb.com | 3 | 3 | 5 | ENOTFOUND |
| darioamodei.com | 3 | 3 | 5 | ENOTFOUND |
| en.wikipedia.org | 3 | 3 | 0 | ENOTFOUND |
| www-cdn.anthropic.com | 3 | 3 | 0 | ENOTFOUND |
| whitehouse.gov | 2 | 2 | 12 | ENOTFOUND |
| press.un.org | 2 | 2 | 8 | ENOTFOUND |
| aljazeera.com | 2 | 2 | 4 | ENOTFOUND |
| huawei.com | 2 | 1 | 3 | ENOTFOUND |
| minimax.io | 2 | 1 | 3 | ENOTFOUND |
| blog.cloudflare.com | 2 | 2 | 2 | ENOTFOUND |
| reflection.ai | 2 | 2 | 2 | ENOTFOUND |
| thenextweb.com | 2 | 2 | 2 | ENOTFOUND |
| canberratimes.com.au | 2 | 2 | 1 | ENOTFOUND |
| theregister.com | 2 | 2 | 1 | ENOTFOUND |
| x.com | 2 | 2 | 1 | ENOTFOUND |
| cryptobriefing.com | 2 | 2 | 0 | ENOTFOUND |
| decrypt.co | 2 | 2 | 0 | ENOTFOUND |
| rubyhack.ai | 2 | 2 | 0 | ENOTFOUND |
| the-decoder.com | 2 | 2 | 0 | ENOTFOUND |
| thehackernews.com | 2 | 2 | 0 | ENOTFOUND |
| web.archive.org | 2 | 2 | 0 | bloqueado pela ferramenta |
| wiz.io | 2 | 1 | 0 | ENOTFOUND |
| asymmetricsecurity.com | 1 | 1 | 7 | ENOTFOUND |
| council.nyc.gov | 1 | 1 | 7 | ENOTFOUND |
| fsb.org | 1 | 1 | 7 | ENOTFOUND |
| sakana.ai | 1 | 1 | 7 | ENOTFOUND |
| andonlabs.com | 1 | 1 | 6 | ENOTFOUND |
| euronews.com | 1 | 1 | 6 | ENOTFOUND |
| harvey.ai | 1 | 1 | 6 | ENOTFOUND |
| kpbs.org | 1 | 1 | 6 | ENOTFOUND |
| linkedin.com | 1 | 1 | 6 | ENOTFOUND |
| mikitabalesni.com | 1 | 1 | 6 | ENOTFOUND |
| public-inspection.federalregister.gov | 1 | 1 | 6 | ENOTFOUND |
| un.org | 1 | 1 | 6 | ENOTFOUND |
| bnnbloomberg.ca | 1 | 1 | 5 | ENOTFOUND |
| commerce.senate.gov | 1 | 1 | 5 | ENOTFOUND |
| developer.meta.com | 1 | 1 | 5 | ENOTFOUND |
| fortune.com | 1 | 1 | 5 | ENOTFOUND |
| globaltimes.cn | 1 | 1 | 5 | ENOTFOUND |
| gov.ca.gov | 1 | 1 | 5 | ENOTFOUND |
| ifm.ai | 1 | 1 | 5 | ENOTFOUND |
| imf.org | 1 | 1 | 5 | ENOTFOUND |
| iowaattorneygeneral.gov | 1 | 1 | 5 | ENOTFOUND |
| microsoft.ai | 1 | 1 | 5 | ENOTFOUND |
| pm.gov.au | 1 | 1 | 5 | ENOTFOUND |

Com uma URL cada e menos de cinco afirmações presas: 9to5google.com, abc.net.au, abcnews.com, akamai.com, alphagenome.google, api.github.com (403), assets.claude.com, bitsight.com, bleepingcomputer.com, blog.arxiv.org, calif.io, cbsnews.com, cdn.openai.com, cert.europa.eu, cims.nyu.edu, cloudblog.withgoogle.com, cloudflare.com, cognition.com, cybernews.com, cybersecuritynews.com, dealroom.co, deploymentsafety.openai.com, devdiscourse.com, docs.cloud.google.com, docs.mistral.ai, ecosistemastartup.com, endorlabs.com, english.aawsat.com, expressandstar.com, federalregister.gov, finance.yahoo.com, fmprc.gov.cn, gizmodo.com, gulfnews.com, hackmd.io, hf.co, horadecodar.com.br, horizon3.ai, ias.edu, insurancebusinessmag.com, investing.com, itdaily.com, jpmorganchase.com, justsecurity.org, kfgo.com, ksl.com, labs.cloudsecurityalliance.org, lesswrong.com, letsdatascience.com, metr.org, minimaxi.com, mlcommons.org, mofcom.gov.cn, morganstanley.com, mustafa-suleyman.ai, news.un.org, news4jax.com, newsroom.accenture.com, newsweek.com, nsa.gov, nvidianews.nvidia.com, officechai.com, olhardigital.com.br, php.net, platform.minimax.io, ppc.land, pressroom.versantmedia.com, pymnts.com, research.meta.ai, sec.gov, siliconangle.com, taiwannews.com.tw, tech-insider.org, tech.ifeng.com, technobezz.com, techzine.eu, thephp.foundation, therecord.media, thestar.com.my, thetechportal.com, tidbits.com, unite.ai, vercel.com, watchtowr.com, webull.com, wikimediafoundation.org, words.filippo.io, x.ai, yahoo.com.

## O que o orquestrador corrigiu

Cada `errado` e cada `impreciso` com fonte aberta foi reaberto pelo
orquestrador antes de aceito. Além disso, uma amostra de confirmados foi
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

## Método e limites

- Um subagente por episódio, cinco em paralelo, do 40 ao 1, com o mesmo
  briefing. Até 8 afirmações por pauta, priorizando número, data e citação. A
  memória do programa foi conferida contra os roteiros do repositório. A
  evidência saiu de páginas abertas pelo WebFetch, que passa o texto por um
  modelo pequeno e limita a citação literal a cerca de 125 caracteres. Os
  trechos são literais, mas curtos.
- **Viés de cobertura.** Com a rede fechada, verificou-se o que tem fonte na
  Anthropic (218 afirmações) ou no GitHub (94), mais a memória do programa (98).
  A OpenAI, fonte citada em 20 das 120 pautas, ficou quase toda de fora (71
  afirmações presas só em openai.com). Comparar com a taxa de outras fontes não é possível.
- **Cópias no GitHub.** Para imprensa e posts bloqueados, contou como fonte a
  cópia literal em issue ou gist que traz link e data do original (94
  afirmações, 89 confirmadas). Resumo, digest ou catálogo de terceiros não
  contou. A cópia pode diferir do original. A técnica foi descoberta pelo
  verificador do episódio 27 e só então entrou no briefing; do 21 para trás,
  todos já começaram com ela. Por isso os episódios antigos têm
  mais checagem por cópia: são 71 dos 176 fatos de fora verificáveis do Opus 5,
  contra 23 de 145 do Opus 5.5.
- **Seleção.** Até 8 afirmações por pauta, escolhidas pelo verificador, não
  sorteadas. A taxa vale para fatos com número, data ou citação, não para cada
  frase do roteiro. Fontes abertas que divergem viraram `nao_verificavel`.
- **Gravidade é julgamento.** Um único verificador por afirmação, sem segunda
  opinião sobre `leve` e `grave`.
- **Segunda passada.** Toda nota de afirmação `inacessivel` começa com `rede:` e
  traz a pista da busca. Com a rede aberta, basta refazer as 513 afirmações
  inacessíveis a partir do `afirmacoes.jsonl`, sem escolher afirmações de novo.
  As pistas que mais pedem conferência: o comunicado de Iowa (ep. 34), "todas as
  versões desde a 5.4" do PHP (ep. 39), o prazo de 60 dias da ordem do DHS
  (ep. 38) e "mais de cinquenta idiomas" do Voxtral (ep. 38).
- O prompt pedia o ramo `claude/verificador-linha-de-base`. A sessão só podia
  enviar para `claude/eager-cerf-xvyd87`, e o trabalho foi para lá. Nada foi
  para a `main`, e nada fora de `verificacao/linha-de-base/` mudou.
