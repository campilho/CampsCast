# O Editor, versão a versão

O Editor é o agente principal do CampsCast (`prompts/master.md`). Ele lê a
memória, pesquisa, escolhe as pautas e escreve o roteiro e o log. Este arquivo
conta como ele chegou à versão de hoje: o que mudou em cada versão, por quê e o
que se mediu.

O registro oficial é a ficha, em `config/agentes.json`. Ela guarda a impressão
digital do prompt, o modelo, as ferramentas, o que mudou e o que se mediu, e a
suíte falha se o prompt mudar sem ela. Para ver a ficha legível:
`python3 scripts/agentes.py mostra`. Este texto é o resumo para gente; quando
ele e a ficha discordarem, vale a ficha.

## A regra do jogo

Uma mudança por vez. Cada versão nova é ensaiada contra a anterior em dias
passados (`scripts/ensaio.sh`) antes de ir ao ar, e depois fica uma semana na
produção antes de alguém tocar no prompt de novo. Número pequeno (1.1) é
instrução; número grande (2.0) é ferramenta, modelo ou papel.

## Linha do tempo

| Versão | No ar desde | Em uma frase | Por que veio |
|---|---|---|---|
| antes | 24/08 | 14 mudanças no prompt sem número | o programa nascendo |
| 1.0 | 08/11 (prompt de 02/11) | a primeira com ficha; a leitura de páginas fica no próprio agente | a Anthropic trocou a leitura por um subagente sem aviso |
| 1.1 | 16/11 | fonte oficial fechada entra pela cobertura de três veículos; reportagem não | o RSA do DeepMind, que só se lia pela imprensa |
| 1.2 | 23/11 | a certeza é a da fonte, com a frase da fonte ao lado da do roteiro | o verificador achou que metade dos erros era paráfrase |

### Antes da ficha (24/08 a 02/11)

O prompt mudou 14 vezes no git (`git log -- prompts/master.md`), sem número
de versão. Por exemplo: em 30/10, ler fonte fechada por outra porta da própria
fonte antes da imprensa; em 31/10, o log com nota por página e as escolhas.

### 1.0: a versão de partida (ficha em 08/11)

- **O que é:** o prompt como estava desde 02/11. O primeiro episódio com ele
  foi o nº 46, de 03/11.
- **O que fixou:** o agente lê as páginas com o WebFetch dele mesmo
  (`CLAUDE_CODE_WEB_FETCH_AGENT=0`). De 05 a 08/11, um experimento da Anthropic
  tinha passado a leitura para um subagente sem aviso
  ([ADR 0013](decisions/0013-leitura-de-paginas.md)).
- **Medido:** US$ 4,98 e 5,25 por episódio em 03 e 04/11.
- **O que ficou de lição:** sem versão não dá para comparar. A ficha nasceu
  para que cada mudança tenha nome, data e medida.

### 1.1: quando a fonte oficial fecha (desde 16/11)

- **Por que:** em 09/11 o anúncio do RSA do DeepMind estava num post do X que
  recusou a leitura, e a notícia só se lia por cinco coberturas. A regra
  antiga não dizia o que fazer.
- **O que mudou:** publicação oficial fechada por todas as portas (a página,
  outra porta da fonte, a cópia do arquivo) entra pela cobertura de pelo
  menos três veículos de texto próprio, dito no ar. Newsletter, agregador e
  texto de agência repetido não contam. Reportagem de jornal não é publicação
  oficial.
- **Ensaio (09/11, rodado em 12/11):** US$ 6,25 contra 7,88 da 1.0, 14,0
  contra 15,7 min. Descartou quatro furos de reportagem, usou a porta da
  cobertura em três publicações fechadas e achou o RSA, que o primeiro texto
  da regra tinha perdido. O primeiro texto aplicava a regra a uma reportagem
  do New York Times; o escopo foi acertado antes de ir ao ar.
- **Produção (eps. 55 a 58):** US$ 5,08 por episódio. Abertas à mão, as três
  páginas da OpenAI que deram 403 ao agente bateram número a número com o que
  foi ao ar.
- **O que ficou de lição:** em 16/11 uma fala e três revisores vieram de
  newsletter, numa pauta que tinha outra fonte primária. Estava certo, mas por
  sorte: a proibição só valia dentro da porta da cobertura. Isso vai para o
  1.3.

### 1.2: a certeza é a da fonte (desde 23/11)

- **Por que:** o Verificador V1 (14/11, `verificacao/v1/resumo.md`) conferiu os
  episódios 41 a 46 e achou 11,3% de erro, contra 5,9% da linha de base.
  Metade dos erros era o mesmo: o roteiro tirava o "appeared", o "could", o
  "as many as" da fonte, ou trocava a medida por uma vizinha.
- **O que mudou:** o roteiro diz com a mesma certeza que a fonte, e arredondar
  é dizer "cerca de". O passo novo é a "Conferência da certeza" no log: para
  cada número e cada afirmação central, a frase do roteiro ao lado da frase da
  fonte.
- **Ensaio (eps. 41 a 46, 20 e 21/11, verificador nos doze roteiros):**

  | | 1.1 | 1.2 |
  |---|---|---|
  | Erros por afirmação verificável | 12,3% | 8,4% |
  | Paráfrase que acrescenta | 7,1% | 3,2% |
  | Custo do agente por dia | US$ 4,86 | US$ 5,19 |

  A direção é clara, mas com 155 afirmações por lado a queda ainda cabe no
  acaso (z = 1,54). A medida de verdade vem da produção
  ([plano e números](plano-editor-1-2.md)).
- **O que ficou de lição:** a regra solta a 1.1 já tinha ("incerteza é dita
  como incerteza"). O que mudou o texto foi obrigar a comparação com a fonte
  ([aprendizados](aprendizados.md)). Sobra a ligação de causa: o "porque" que a
  fonte não faz, que o agente anota como leitura dele e mantém no ar.

## O que vem

- **1.3, as portas:** a proibição de newsletter e agregador vale para qualquer
  fato tirado de cobertura, e "pela cobertura" no ar diz quantos veículos. A
  cópia do arquivo público sai das portas enquanto o WebFetch não abrir o
  web.archive.org.
- **A ligação de causa:** "porque" que a fonte não diz também é paráfrase que
  acrescenta. Entra numa versão própria ou junto com o 1.3, sempre com ensaio.
- **Fora do Editor:** o verificador diário em sombra mediria cada versão na
  produção de graça, e a redação com vários agentes
  ([ADR 0010](decisions/0010-redacao-com-varios-agentes.md)) tiraria trabalho
  inteiro do Editor. Os dois estão no `TODO.md`.

Ao lançar uma versão nova, acrescente a linha na tabela e a seção, no mesmo
commit da ficha.
