# ADR 0012 — Nota por critério para escolher as pautas

- **Status:** proposto (02/11/2026). Régua v1 em
  [`config/rubrica-pautas.md`](../../config/rubrica-pautas.md); calibração fora
  do ar feita (abaixo); nada na produção
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

1. **Uma régua de cinco critérios, notas de 1 a 5,** cada nota com uma
   descrição curta: fonte, foco (o briefing), impacto, novidade e memória
   (temas e fios). Fonte 1 ou 2 e novidade 1 eliminam, porque já são regras
   do projeto (fonte primária, não repetir).
2. **O agente dá as notas, o código escolhe.** Uma linha por candidata em
   `runs/AAAA-MM-DD/candidatas.json`, cada nota com o seu "por quê". Um
   script determinístico, com teste, elimina, soma (pesos iguais na v1),
   desempata (impacto, foco, novidade, `id`), limita a duas pautas por
   empresa e define "dia fraco" como menos de duas candidatas da janela com
   soma 16 ou mais.
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

**Dois ajustes para a v2.**
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

**Limites.** O dossiê é mais pobre que o de uma execução real; foi uma
chamada com todas as candidatas, não uma por candidata; e quem dá a nota é o
mesmo modelo que escreve o programa. O quarto lugar teve cinco candidatas
entre 17 e 18: num dia assim um ponto decide, e a sombra precisa mostrar se,
com dossiês reais, esse ponto oscila.

**Próximo:** a régua v2 com os dois ajustes, uma rodada de conferência sobre
as mesmas 31 candidatas, e então a sombra.

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
