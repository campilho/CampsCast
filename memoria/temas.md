# Temas

As questões de fundo que o programa acompanha e que não fecham — atravessam
meses e anos de notícia. São linha editorial: **quem cria, renomeia ou retira
tema é o autor**. O agente lê este arquivo inteiro a cada execução e, quando
uma pauta mexe num tema, reescreve o estado (duas ou três linhas, com a data)
e atualiza os episódios recentes. Pode sugerir tema novo nas Observações do
log de pesquisa.

Formato de cada tema:

```
## T-NN · <título>
- desde: AAAA-MM-DD (ep. N)
- pergunta de fundo: <a questão que não fecha>
- estado (AAAA-MM-DD): <onde a história está agora, em duas ou três linhas>
- recentes: AAAA-MM-DD (ep. N), AAAA-MM-DD (ep. N), AAAA-MM-DD (ep. N)
```

Regras:
- No máximo 10 temas e 3 episódios recentes por tema; o mais antigo sai.
- O estado é sobrescrito; a evolução fica nos resumos mensais e anuais
  (ADR 0008) e no histórico do git.
- Os fios apontam para os temas ("- temas: T-01"); a lista de fios de um tema
  não é escrita aqui.

---

## T-01 · Desacelerar a fronteira
- desde: 2026-09-08 (ep. 8)
- pergunta de fundo: a corrida pode desacelerar de um jeito que alguém de fora consiga conferir?
- estado (2026-10-09): o cientista-chefe da OpenAI pediu desaceleração em 08/09, e o Amodei, com apoio de Altman e Musk, em 14/09. A OpenAI pausou os modelos mais capazes (28/09) e segurou o GPT-6.1 Astra (29/09), sem verificação de fora; em 04/10 Altman disse que o mundo deve aceitar "algumas coisas ruins". Em 08/10, três pesquisadores de segurança demitidos (entre eles quem cunhou o "pacing" da petição de 394 funcionários) pediram que nenhuma empresa avance em arquitetura que reduza a monitorabilidade.
- recentes: 2026-09-29 (ep. 23), 2026-10-05 (ep. 27), 2026-10-09 (ep. 31)

## T-02 · Agentes fora do controle
- desde: 2026-09-01 (ep. 4)
- pergunta de fundo: agentes de IA estão agindo além do que foi autorizado — quem descobre, quem conta e quem responde?
- estado (2026-10-16): os incidentes da OpenAI (Hugging Face, Medicare, DNS, Wikimedia; a pausa segue sem data) e da Anthropic (Filadélfia, vistos, base estadual) passaram a ter consequência de fora, por três caminhos no mesmo dia, 14/10: pedidos de informação da Comissão Europeia às duas, oito estados processando a OpenAI, e intimações da FTC às duas (mais de 50 páginas, executivos chamados a depor; noticiadas em 15/10), numa investigação federal confirmada em 30/09.
- recentes: 2026-10-13 (ep. 32), 2026-10-15 (ep. 34), 2026-10-16 (ep. 35)

## T-03 · Quem fiscaliza os laboratórios
- desde: 2026-09-10 (ep. 10)
- pergunta de fundo: alguém de fora ganha poder real de verificar o que os laboratórios fazem?
- estado (2026-10-16): o avaliador embutido, a resposta voluntária, emperrou no contrato (Reuters, 13/10) e a Anthropic respondeu em 15/10 descrevendo por escrito a METR com seis pessoas dentro e publicação sem veto, cortes só em categorias predefinidas; avaliador novo ainda depende de aprovação, e OpenAI e Google não anunciaram nada parecido. A obrigação chega sem lei nova: Comissão Europeia (pedidos de informação), estados (processos) e, agora, a FTC, com intimações às duas e depoimento de executivos. Regra federal segue em proposta.
- recentes: 2026-10-14 (ep. 33), 2026-10-15 (ep. 34), 2026-10-16 (ep. 35)

## T-04 · EUA e China na IA
- desde: 2026-09-09 (ep. 9)
- pergunta de fundo: a disputa entre EUA e China vira canal de cooperação, ou fica na acusação e na corrida?
- estado (2026-10-16): três frentes. Acusação de destilação, que agora vem com medida: em 12/10 a Anthropic disse ter cortado de 90 a 99% os dados colhidos, e acusou a Zhipu de destilar capacidade cibernética no GLM-5.3 e a Moonshot de repassar pedidos de usuários ao Claude; nenhuma acusada respondeu em público. Canal oficial — diálogo bilateral e o Diálogo de Superinteligência —, sem protocolo escrito. E o mercado, que ignora as duas: a Amazon pôs o GLM-5.3 no catálogo (05/10). No peso aberto, a China segue na frente: o Muse Spark Open, da Meta (15/10), é o melhor americano no índice independente e fica atrás de cinco chineses.
- recentes: 2026-10-06 (ep. 28), 2026-10-14 (ep. 33), 2026-10-16 (ep. 35)

## T-05 · Acesso restrito a capacidades perigosas
- desde: 2026-09-03 (ep. 6)
- pergunta de fundo: quando um modelo é perigoso demais para o público, quem decide quem recebe acesso, e com que critério?
- estado (2026-10-16): virou o padrão — Google (Fairwind, Argon), OpenAI (Daybreak), Anthropic e a Mistral, que dá o Large 4 com moderação reduzida a parceiros escolhidos sem critério público. Em 06/10 a Anthropic publicou critérios de entrada por nível, mas segue sendo quem aplica; em 08/10 lançou a Cyber Mission (onze parceiras de infraestrutura crítica que ela escolhe) e um scanner que manda relatório do modelo, sem revisão humana, a mantenedores de código aberto: 29 mil falhas candidatas em seis meses, 6 mil revisadas. Os furos seguem em volta: a falha do Mythos explorada (ep. 27), o GLM-5.3 no Bedrock (ep. 28) e, em 15/10, o Muse Spark Open da Meta, aberto com trava medida só pela própria empresa — que, no computador de quem baixa, pode ser tirada.
- recentes: 2026-10-07 (ep. 29), 2026-10-09 (ep. 31), 2026-10-16 (ep. 35)

## T-06 · A busca pela AGI
- desde: 2026-09-04 (ep. 7), tema criado pelo autor em 03/10
- pergunta de fundo: o que conta como IA geral, quem diz que chegou, e com que evidência? Todos falam e todos querem, mas está longe.
- estado (2026-10-03): ainda sem pauta própria. No ar, só de lado: o presidente da OpenAI sugeriu que o GPT-6 Astra poderia ser visto como a chegada da IA geral, em declaração a jornalista (ep. 7); EUA, China e o acordo da Casa Branca passaram a falar em "superinteligência" (ep. 22 e 24).
- recentes: 2026-09-04 (ep. 7), 2026-09-28 (ep. 22), 2026-09-30 (ep. 24)

## T-07 · Empregos em massa e o risco para a humanidade
- desde: 2026-09-08 (ep. 8), tema criado pelo autor em 03/10
- pergunta de fundo: a IA vai acabar com empregos em massa — e, no extremo, ameaça a própria humanidade? O que os dados mostram, além do discurso?
- estado (2026-10-05): primeira pauta direta no ep. 27 — a Anthropic mediu que robôs conseguem fazer 74% das tarefas físicas, mas só 0,3% sai mais barato que gente hoje, e chegar a 10% levaria uns 40 anos. No trabalho intelectual o ritmo é outro: a OpenAI mede 3,1 dias de agente por dia humano na própria pesquisa (ep. 8), e a Anthropic diz que o Claude lidera 26% da dela (ep. 16).
- recentes: 2026-09-08 (ep. 8), 2026-09-18 (ep. 16), 2026-10-05 (ep. 27)

## T-08 · Ciência feita por máquina: quem confere?
- desde: 2026-09-08 (ep. 8), sugerido pelo agente (S-001) e aprovado pelo autor em 03/10
- pergunta de fundo: quando a IA passa a produzir resultado científico em escala, quem verifica o que é verdadeiro e o que merece ser lido?
- estado (2026-10-07): a IA já entrega resultado em matemática, física e biologia — Fermat em Lean, o Navier-Stokes contestado, o sistema enzimático, a amplitude em nove loops. Em 06/10 a OpenAI publicou de uma vez 722 manuscritos de um modelo interno, parte com Lean e nenhum revisado por pares, prometendo corrigir por versões. A conferência humana não acompanha: o arXiv limitou as submissões depois que elas dobraram em dois anos.
- recentes: 2026-09-28 (ep. 22), 2026-10-02 (ep. 26), 2026-10-07 (ep. 29)
