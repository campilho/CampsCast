# ADR 0012 — Nota por critério para escolher as pautas

- **Status:** proposto (02/11/2026). Régua v2 em
  [`config/rubrica-pautas.md`](../../config/rubrica-pautas.md), com os três
  ajustes da calibração da v1 aprovados pelo autor; as duas calibrações fora do
  ar feitas (abaixo); nada na produção
- **Data:** 2026-11-02

## Contexto

Em 02/11, cinco execuções de 29/10 com o mesmo estado (quatro ensaios e a que
foi ao ar; tabela em [aprendizados](../aprendizados.md), "Duas execuções do
mesmo dia escolhem pautas diferentes") repetiram sempre a manchete e
espalharam as outras duas vagas por seis pautas diferentes. Todas as escolhas
estavam justificadas no log e dentro da janela.

A instrução de hoje explica a variação. O passo 5 do `prompts/master.md` diz
"ranqueie as pautas por impacto real", com um único critério escrito
(lançamento de modelo de fronteira de player principal), e manda puxar do
backlog em "dia fraco (menos de 2 pautas fortes)", sem dizer o que é forte. A
pauta do backlog entrou em três das cinco execuções: é a mesma dúvida
decidida de jeitos diferentes.

Há duas fontes de variação, e esta decisão trata da segunda:

1. **O que o agente encontra.** A execução que foi ao ar fez 18 buscas e
   achou a carta dos democratas; a que fez 9 não achou. Pauta que não foi
   encontrada não concorre.
2. **Como ele decide entre as boas.** Com quatro ou cinco candidatas fortes,
   o desempate fica implícito e muda a cada execução.

## Decisão proposta

1. **Uma porteira e quatro notas, de 1 a 5,** cada nota com uma descrição
   curta: foco (o briefing), impacto, novidade e memória (temas e fios). A
   porteira é a fonte primária, conferida por qualquer porta oficial; quem não
   passa sai, e novidade 1 também, porque já são regras do projeto. O caminho
   da fonte (URL, porta, quanto foi lido) fica nos metadados de cada
   candidata, fora da nota. Essa é a v2; a v1 tinha a fonte como quinta nota
   (abaixo, por que mudou).
2. **O agente dá as notas, o código escolhe.** Uma linha por candidata em
   `runs/AAAA-MM-DD/candidatas.json`, cada nota com o seu "por quê". Um
   script determinístico, com teste, elimina, soma (pesos iguais, de 4 a
   20), ordena as da janela e as do backlog juntas, desempata (impacto, foco,
   novidade, `id`) e limita a duas pautas por empresa.
3. **O Editor recebe as três e pode vetar uma,** com o motivo escrito no
   log; o código promove a seguinte. Veto frequente quer dizer régua errada.
4. **Em etapas,** como o resto da Fase 3: calibração fora do ar (feita),
   sombra na produção (o agente grava as notas, o código calcula, mas quem
   decide ainda é o agente; o relatório de sexta compara), e só então a
   troca.

É o contrato entre o Jornalista e o Editor do [ADR 0010](0010-redacao-com-varios-agentes.md),
e vem antes do V4 (pesquisa em paralelo): pesquisa dividida em subagentes
precisa de um formato comum para as candidatas.

## Alternativas consideradas

- **Cobertura mínima fixa antes de escolher** — toda execução lê a mesma
  lista de fontes e faz as mesmas buscas padrão, e um script confere no log.
  Ataca a primeira fonte de variação. Não é alternativa, é complemento: vai
  junto, a partir dos dados de rendimento das fontes.
- **Notas em triplicata** — cada candidata recebe as notas três vezes, em
  chamadas separadas e num modelo mais barato, e vale a mediana. Reduz o
  ruído da nota; fica para se a calibração mostrar que ele é grande.
- **Comparação em pares** ("A ou B?") só para empates de um ponto, que costuma
  ser mais estável que nota absoluta.
- **Baixar a temperatura** — o Claude Code sem interface não oferece; pela
  API reduz mas não zera, e as buscas na web variam de qualquer jeito.

## Calibração (02/11)

**Como.** As 135 entradas dos cinco logs de 29/10 viraram 31 candidatas: 29
da janela e 2 do backlog. As outras 72, fora da janela ou sem data conferida,
saem pelo código antes da nota. Cada candidata foi com um dossiê enxuto
(título, data, fonte com o que foi lido) para três rodadas independentes do
Opus 5.5 (esforço alto, o da produção), cada uma com a ordem embaralhada e com
a memória e a lista de pautas cobertas como estavam antes de 29/10. Uma
chamada por rodada, todas as candidatas juntas, de US$ 0,64 a 0,67 cada.
Arquivos e scripts em `analysis/ensaios-2026-11-02/calibracao/`.

**Resultado.**
- As três rodadas escolheram as mesmas três: Gemini 4 Carbon (soma 24),
  bancos do Canadá (20) e AI for Science da Anthropic (19).
- A nota quase não variou. Foco nunca mudou; fonte e impacto mudaram em 8 e
  7 das 31 candidatas, sempre por um ponto; a soma variou no máximo 3 pontos
  (mediana 1), e 15 candidatas tiveram a mesma soma nas três rodadas.
- Doze eliminadas pela fonte nas três, entre elas a Cathedral, do backlog,
  lida só pela imprensa porque a reportagem original é fechada.

Com o mesmo dossiê, a régua tira quase toda a variação da escolha. O que
sobra nas execuções reais vem do que cada uma encontra e de quem dá a nota ter
dossiês diferentes; a sombra mede essa parte.

**Três ajustes para a v2.**
1. **Foco 4 largo demais.** O AI for Science (créditos e um programa para 20
   instituições) ficou em terceiro com foco 4, "outro anúncio de player
   principal", quando as cinco execuções reais o descartaram como "programa,
   não resultado". Não é o modelo puxando para a Anthropic: o mesmo modelo,
   decidindo livre, descartou nas cinco; foi a descrição. Na outra ponta, o
   Octoverse, que entrou em três das cinco, ficou com foco 2 porque o GitHub
   não está na lista de players. A v2: foco 4 só para anúncio que mude
   modelo, produto central ou política de um player principal; programa,
   parceria, caso de cliente e ensaio ficam em 3. E decidir se a Microsoft,
   com o GitHub, entra na lista do briefing.
2. **O "dia fraco" com soma 16 não separa nada.** De 13 a 16 das 20
   elegíveis passaram de 16, então o backlog nunca entraria; a da Cohere somou
   18, empatada com a carta dos democratas e a lei de Nova York. Proposta: o
   backlog concorre na mesma ordem que as da janela (a novidade já desconta o
   que envelheceu), e a regra do dia fraco sai.
3. **A nota de fonte mede o nosso acesso, não a notícia.** O openai.com deu
   403 em todos os 42 logs de pesquisa, e o x.ai em 37; o anthropic.com, em
   5. Pela régua v1, notícia da OpenAI lida pelo feed ou por outra página da
   empresa leva 4, e só pela imprensa leva 3, onde a mesma notícia da
   Anthropic levaria 5. Na calibração, as da OpenAI tiveram fonte 3 ou 4, e o
   AI for Science, 5. Um a dois pontos de diferença que vêm de quem nos
   bloqueia. Proposta: fonte vira só porteira (tem fonte primária verificável
   por alguma porta oficial — página, feed, outra página da empresa,
   documento — ou é eliminada) e sai da soma, que passa a ir de 4 a 20. O que
   foi lido e por onde continua registrado, para a estatística das fontes.

**Limites.** O dossiê é mais pobre que o de uma execução real; foi uma
chamada com todas as candidatas, não uma por candidata; e quem dá a nota é o
mesmo modelo que escreve o programa. O quarto lugar teve cinco candidatas
entre 17 e 18: num dia assim um ponto decide, e a sombra precisa mostrar se,
com dossiês reais, esse ponto oscila.

## Calibração da v2 (02/11)

Os três ajustes foram aprovados pelo autor no mesmo dia, com dois acréscimos:
a Microsoft entrou na lista de players principais do briefing, e os cinco
laboratórios de peso aberto da China (Alibaba, DeepSeek, Moonshot, Zhipu e
MiniMax) viraram um grupo explícito, com foco 4 para lançamento de modelo de
fronteira deles. Mesmas 31 candidatas, mesmo método, com o briefing novo; de
US$ 0,47 a 0,49 por rodada.

- **De novo as mesmas três nas três rodadas:** Gemini 4 Carbon (19),
  bancos do Canadá (16, 16 e 14) e os créditos de API da OpenAI para
  assinantes Pro e Business (14).
- **Mais estável que a v1:** a soma não variou em 20 das 31 candidatas
  (mediana 0, máximo 2).
- **Os ajustes funcionaram.** O AI for Science caiu para foco 3 e soma 13.
  A porteira deixou 11 de fora nas três rodadas, todas lidas só pela
  imprensa, e passou todas as da OpenAI. O Octoverse subiu para foco 3 com a
  Microsoft na lista. A pauta do backlog (Cohere) concorreu junto e ficou com
  12.

**O ponto novo: a terceira vaga se decide por um ponto.** Os créditos da
OpenAI (14) ficaram um ponto à frente da lei de Nova York sobre chatbots de
companhia e do AI for Science (13 nas três rodadas) e da carta dos democratas
(13 em duas). Os créditos levaram foco 4 por "mexer em preço e
acesso", o que a v2 escreveu para mudança de política; uma promoção de
créditos cabe ali, mas talvez não devesse. Duas saídas, a decidir pelo autor:
- **política mais estreita:** foco 4 só para mudança de preço ou acesso
  duradoura e para todos os clientes; promoção, crédito e teste grátis ficam
  em 3. Com isso, a lei de Nova York vence pelo desempate (impacto 4);
- **impacto com peso 2:** a soma vai de 5 a 25 e quem muda mais coisa sobe.
  Os créditos e a lei empatam em 17, e a lei vence no desempate.

É o caso típico do veto do Editor: com as três escolhidas e as seguintes à
vista, ele trocaria os créditos pela lei, com o motivo no log. Se a sombra
mostrar vetos assim com frequência, a régua muda.

**Decidido em 02/11 pelo autor: a política mais estreita** (régua v2.1).
Corrige a descrição que errou sem mexer no peso de tudo. Pela soma da v2, os
créditos caem para 13 e a lei de Nova York fica com a vaga pelo desempate
(impacto 4); a confirmar na primeira rodada com a v2.1.

**Próximo:** depois de terça, a sombra na produção.

## Adendo de 13/11: porteira v2.2

Com o Editor 1.1 (`config/agentes.json`), a partir do episódio de 16/11,
a publicação oficial fechada por todas as portas passa pela porteira
quando lida pela cobertura de
três veículos com texto próprio, e o roteiro diz isso no ar. Reportagem
continua fora: o escopo foi decidido pelo autor em 12/11, para que jornal
e revista de interesse geral não virem fonte diária.

## Consequências

- A escolha passa a ser auditável e mostrável: a tabela de notas pode ir para
  a ficha do Editor no site, dentro da regra de fidelidade.
- Trocar pesos ou o limite do dia fraco vira rodar o script de novo sobre o
  mesmo arquivo, sem pesquisar de novo.
- A nota continua sendo julgamento do modelo: o ruído muda de lugar e passa a
  ser medido. E a régua precisa de ajuste com casos reais nas primeiras
  semanas.
- Quem pesquisa e gosta de uma pauta tende a dar nota alta a ela. Na v1, a
  instrução de avaliar uma candidata de cada vez; depois, notas dadas por
  quem não pesquisou.
